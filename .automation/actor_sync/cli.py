"""Command-line entry point for Oracle/systemd and manual execution."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys
import tempfile

from .apify import Apify
from .gitrepo import publish
from .http import SyncError
from .render import apply_files, json_text, render
from .isolation import check_snapshot

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,100}$")
ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")


def load_config(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if config.get("schema_version") != 1 or not isinstance(config.get("organizations"), list) or not config["organizations"]:
        raise SyncError("Configuration must use schema_version 1 and contain organizations")
    workers = config.get("workers", 4)
    if not isinstance(workers, int) or not 1 <= workers <= 8:
        raise SyncError("workers must be between 1 and 8")
    seen, targets = set(), set()
    for org in config["organizations"]:
        for key in ("apify_username", "github_owner", "repository", "branch"):
            if not isinstance(org.get(key), str) or not IDENTIFIER.fullmatch(org[key]):
                raise SyncError(f"Invalid organization configuration field: {key}")
        if not isinstance(org.get("brand"), str) or not org["brand"].strip():
            raise SyncError("brand must be a non-empty string")
        if not ENV_NAME.fullmatch(org.get("token_env", "")):
            raise SyncError("token_env must name an environment variable, not contain a token")
        if org.get("expected_login") and not IDENTIFIER.fullmatch(org["expected_login"]):
            raise SyncError("Invalid expected_login")
        target = (org["github_owner"].lower(), org["repository"].lower())
        if org["apify_username"] in seen or target in targets:
            raise SyncError("Duplicate organization or repository target")
        seen.add(org["apify_username"])
        targets.add(target)
    return config


@contextmanager
def process_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0)
        # Windows byte-range locks prevent even reading an already locked byte.
        # File size can be inspected without touching another process's lock.
        if os.fstat(stream.fileno()).st_size == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError):
            raise SyncError("Another sync process holds the state-directory lock") from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(json_text(value))
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synchronize public Apify READMEs and schemas into useful GitHub example libraries.")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--state-dir", default="state")
    parser.add_argument("--only", help="Sync only this configured Apify username")
    sub = parser.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="Check live Apify sources; dry-run unless --push is set")
    modes = sync.add_mutually_exclusive_group()
    modes.add_argument("--push", action="store_true")
    modes.add_argument("--dry-run", action="store_true")
    bootstrap = sub.add_parser("bootstrap", help="Create public repositories and publish examples plus reference docs")
    bootstrap.add_argument("--publish", action="store_true", required=True)
    export = sub.add_parser("export", help="Render public Actor reference files locally, without GitHub writes")
    export.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        config_path = Path(args.config).resolve()
        config = load_config(config_path)
        orgs = [o for o in config["organizations"] if not args.only or o["apify_username"] == args.only]
        if not orgs:
            raise SyncError("--only does not match a configured organization")
        state = Path(args.state_dir).resolve()
        results = []
        with process_lock(state / "sync.lock"):
            for org in orgs:
                logging.info("Reading published documentation for %s", org["apify_username"])
                try:
                    actors = Apify().snapshot(org["apify_username"], config.get("workers", 4))
                    check_snapshot(actors, org)
                    if args.command == "export":
                        destination = Path(args.output).resolve() / org["apify_username"]
                        previous_file = destination / "actors.json"
                        previous = json.loads(previous_file.read_text(encoding="utf-8"))["actors"] if previous_file.exists() else []
                        files = render(org["brand"], actors, previous)
                        enabled = org.get("site", {}).get("enabled", False)
                        if enabled:
                            from .site import Site
                            files.update({"site/" + path: text for path, text in Site(org, actors).build(previous).items()})
                        changed = apply_files(destination, files, repair=enabled, prune=enabled)
                        result = {"organization": org["apify_username"], "status": "exported", "public_actors": len(actors), "changed_files": len(changed)}
                    else:
                        result = publish(org, actors, state, config_path.parent / "templates",
                                         push=args.command == "bootstrap" or args.push,
                                         bootstrap=args.command == "bootstrap")
                    results.append(result)
                    logging.info("%s: %s (%d public Actors)", org["apify_username"], result["status"], len(actors))
                except (SyncError, ValueError, KeyError, TypeError, OSError) as exc:
                    # Never print API response bodies, environment variables, or a traceback.
                    message = str(exc) if isinstance(exc, SyncError) else f"Invalid data or local filesystem error ({type(exc).__name__})"
                    logging.error("%s: %s", org["apify_username"], message)
                    results.append({"organization": org["apify_username"], "status": "failed", "error": message})
            failed = any(r["status"] == "failed" for r in results)
            report = {"completed_at": datetime.now(timezone.utc).isoformat(), "success": not failed, "results": results}
            name = "last-export.json" if args.command == "export" else "last-dry-run.json" if not (args.command == "bootstrap" or args.push) else "last-run.json"
            atomic_json(state / name, report)
            print(json.dumps(report, ensure_ascii=True))
            return 1 if failed else 0
    except (SyncError, ValueError, OSError) as exc:
        logging.error("%s", str(exc) if isinstance(exc, SyncError) else "Cannot read configuration or state directory")
        return 2


if __name__ == "__main__":
    sys.exit(main())
