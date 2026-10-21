"""Publish one atomic commit per repository using Git without persisted credentials."""

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .http import Api, HttpError, SyncError
from .render import apply_files, example_status, render
from .isolation import check_snapshot, check_brand


class Git:
    def __init__(self, token=None, email="actor-sync@users.noreply.github.com"):
        self.token = token
        self.env = dict(os.environ)
        # Never allow inherited Git tracing to write authentication headers to logs.
        for key in list(self.env):
            if key.startswith("GIT_TRACE") or key.startswith("GIT_CONFIG_") or key.startswith("GITHUB_TOKEN") or key in ("GIT_CURL_VERBOSE", "GIT_ASKPASS", "SSH_ASKPASS", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
                self.env.pop(key, None)
        self.env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_COUNT": "1",
                         "GIT_CONFIG_KEY_0": "credential.helper", "GIT_CONFIG_VALUE_0": "",
                         "GIT_AUTHOR_NAME": "Actor documentation sync", "GIT_COMMITTER_NAME": "Actor documentation sync",
                         "GIT_AUTHOR_EMAIL": email, "GIT_COMMITTER_EMAIL": email})
        self.encoded = ""
        if token:
            self.encoded = base64.b64encode(("x-access-token:" + token).encode()).decode()
            self.env.update({"GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_1": "http.https://github.com/.extraheader",
                             "GIT_CONFIG_VALUE_1": "Authorization: Basic " + self.encoded})

    def run(self, args, cwd=None):
        try:
            result = subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=180)
        except (OSError, subprocess.TimeoutExpired):
            raise SyncError("Git could not complete; check installation, network, and repository access") from None
        if result.returncode:
            error = result.stderr[-2000:]
            for secret in (self.token, self.encoded):
                if secret:
                    error = error.replace(secret, "[REDACTED]")
            raise SyncError(f"Git {args[0]} failed: {error.strip()}")
        return result.stdout.strip()


def verify_identity(org, token):
    if not token:
        raise SyncError(f"Set {org['token_env']} before publishing")
    api = Api("https://api.github.com", token)
    repository = org["github_owner"] + "/" + org["repository"]
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if os.environ.get("GITHUB_REPOSITORY", "").lower() != repository.lower():
            raise SyncError("Workflow repository does not match this brand")
        api.request("/repos/" + repository)
        return api, "41898282+github-actions[bot]@users.noreply.github.com"
    user = api.request("/user")
    expected = org.get("expected_login", org["github_owner"])
    if user.get("login", "").lower() != expected.lower():
        raise SyncError(f"GitHub token does not belong to the expected account for {org['apify_username']}")
    return api, f"{user['id']}+{user['login']}@users.noreply.github.com"


def ensure_repository(org, api):
    path = f"/repos/{org['github_owner']}/{org['repository']}"
    try:
        repo = api.request(path)
    except HttpError as exc:
        if exc.status != 404:
            raise
        # Bootstrap supports user-owned repositories. Organization ownership can be
        # added by creating the repository separately and setting expected_login.
        if org.get("expected_login", org["github_owner"]).lower() != org["github_owner"].lower():
            raise SyncError("Create the organization-owned repository before bootstrapping") from None
        repo = api.request("/user/repos", "POST", {
            "name": org["repository"], "description": f"Runnable Apify Actor examples and reference documentation from {org['brand']}.",
            "homepage": "https://apify.com/" + org["apify_username"], "private": False, "auto_init": False,
        })
    if repo.get("private"):
        raise SyncError("Target repository is private; refusing to change visibility")
    return repo


def publish(org, actors, state_dir, templates, push=False, bootstrap=False):
    check_snapshot(actors, org)
    token = os.environ.get(org["token_env"])
    email = "actor-sync@users.noreply.github.com"
    api = None
    if push:
        api, email = verify_identity(org, token)
    if bootstrap:
        if not push:
            raise SyncError("Bootstrap creates public repositories; use bootstrap --publish")
        ensure_repository(org, api)
    git = Git(token, email)
    remote = f"https://github.com/{org['github_owner']}/{org['repository']}.git"
    state_dir.mkdir(parents=True, exist_ok=True)
    # Background desktop Git integrations can recreate .git metadata on Windows
    # during cleanup. Cleanup must not turn a successful remote push into failure.
    with tempfile.TemporaryDirectory(prefix="work-" + org["apify_username"] + "-", dir=state_dir, ignore_cleanup_errors=True) as temp:
        checkout = Path(temp) / "repo"
        heads = git.run(["ls-remote", "--heads", remote])
        target = "refs/heads/" + org["branch"]
        if any(line.split()[-1] == target for line in heads.splitlines()):
            git.run(["clone", "--quiet", "--depth", "1", "--branch", org["branch"], remote, str(checkout)])
        elif not heads and bootstrap:
            checkout.mkdir()
            git.run(["init", "--quiet", "--initial-branch", org["branch"]], checkout)
            git.run(["remote", "add", "origin", remote], checkout)
        else:
            raise SyncError("Target branch does not exist; run bootstrap for an empty repository")
        if bootstrap:
            for source in [templates / "common", templates / "brands" / org["apify_username"]]:
                if not source.is_dir():
                    raise SyncError("Bootstrap template directory is missing")
                for file in source.rglob("*"):
                    if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc":
                        destination = checkout / file.relative_to(source)
                        if not destination.exists():
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(file, destination)
        previous_path = checkout / "actors.json"
        previous = json.loads(previous_path.read_text(encoding="utf-8"))["actors"] if previous_path.exists() else []
        files = render(org["brand"], actors, previous)
        files["EXAMPLE_STATUS.md"] = example_status(checkout, actors)
        enabled = org.get("site", {}).get("enabled", False)
        if enabled:
            from .site import Site
            from .automation import runtime_files
            files.update({"site/" + path: text for path, text in Site(org, actors).build(previous).items()})
            files.update(runtime_files(org))
            project_readme = checkout / "README.md"
            if project_readme.is_file():
                readme_text = project_readme.read_text(encoding="utf-8")
                site_url = org["site"]["url"]
                if site_url not in readme_text:
                    project_readme.write_text(readme_text.rstrip() + "\n\n## Documentation website\n\n[Browse the Actor catalog, schemas, and Python guides](" + site_url + ").\n", encoding="utf-8", newline="\n")
        changed = apply_files(checkout, files, repair=enabled, prune=enabled)
        if enabled:
            # Scan the whole public technical surface, including hand-maintained
            # guides, before committing; one brand may never point to another.
            for name in set(git.run(["ls-files"], checkout).splitlines()) | set(files):
                path = checkout / name
                if path.is_file() and (path.suffix in (".md", ".json", ".py", ".yml", ".yaml", ".css", ".js", ".txt") or name == "LICENSE"):
                    check_brand(path.read_text(encoding="utf-8"), org)
        status = git.run(["status", "--porcelain"], checkout)
        result = {"organization": org["apify_username"], "repository": remote.removesuffix(".git"),
                  "public_actors": len(actors), "changed_files": len(changed), "dry_run": not push}
        if not status:
            return {**result, "status": "unchanged"}
        if not push:
            return {**result, "status": "would-update", "paths": changed}
        git.run(["add", "--all"], checkout)
        git.run(["commit", "--quiet", "-m", "Sync public Actor documentation and catalog"], checkout)
        # Normal fast-forward push only. If someone pushes concurrently, reject the
        # update instead of overwriting their work. The next run starts fresh.
        git.run(["push", "--quiet", "origin", "HEAD:refs/heads/" + org["branch"]], checkout)
        return {**result, "status": "published", "commit": git.run(["rev-parse", "HEAD"], checkout)}
