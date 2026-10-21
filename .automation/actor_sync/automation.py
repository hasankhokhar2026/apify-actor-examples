"""Install an independent maintenance engine and Pages workflow per brand."""

import json
from pathlib import Path

from .render import json_text


def runtime_files(org):
    package = Path(__file__).parent
    files = {}
    for path in package.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo"):
            files[".automation/actor_sync/" + path.relative_to(package).as_posix()] = path.read_text(encoding="utf-8")
    own = dict(org)
    own["token_env"] = "GITHUB_TOKEN"
    own["expected_login"] = org["github_owner"]
    files[".automation/config.json"] = json_text({"schema_version": 1, "workers": 4, "organizations": [own]})
    files[".automation/requirements.txt"] = "markdown-it-py==4.0.0\nmdurl==0.1.2\n"
    files["LICENSE"] = (package / "site_assets/license-template.txt").read_text(encoding="utf-8").format(brand=org["brand"])
    files[".automation/run.py"] = '''"""Maintain this repository's own Apify organization only."""
from pathlib import Path
import tempfile
from actor_sync.cli import main

raise SystemExit(main(["--config", str(Path(__file__).with_name("config.json")),
                      "--state-dir", str(Path(tempfile.gettempdir()) / "actor-docs-sync"),
                      "sync", "--push"]))
'''
    pins = json.loads((package / "site_assets/action-pins.json").read_text(encoding="utf-8"))
    def action(name):
        return name + "@" + pins[name]["sha"] + " # " + pins[name]["tag"]
    cron = org.get("site", {}).get("cron", "17 */6 * * *")
    schedule = "  schedule:\n    - cron: '" + cron + "'\n" if org.get("site", {}).get("scheduler", "github") == "github" else ""
    files[".github/workflows/documentation.yml"] = f'''name: Refresh and publish documentation

on:
  push:
    branches: [{org['branch']}]
{schedule.rstrip()}
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: documentation-pages
  cancel-in-progress: false

jobs:
  documentation:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment:
      name: github-pages
      url: ${{{{ steps.deployment.outputs.page_url }}}}
    steps:
      - uses: {action('actions/checkout')}
        with:
          persist-credentials: false
      - uses: {action('actions/setup-python')}
        with:
          python-version: '3.12'
      - name: Install pinned rendering dependencies
        run: python -m pip install -r .automation/requirements.txt
      - name: Refresh from the public Apify organization
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: python .automation/run.py
      - name: Read the refreshed commit
        run: git pull --ff-only origin {org['branch']}
      - name: Validate the complete static site
        run: python .automation/validate.py
      - uses: {action('actions/upload-pages-artifact')}
        with:
          path: site
      - name: Publish GitHub Pages
        id: deployment
        uses: {action('actions/deploy-pages')}
'''
    files[".automation/validate.py"] = '''"""Validate the exact static artifact before deployment."""
from pathlib import Path
import json
from actor_sync.site import validate_site

root = Path.cwd()
org = json.loads(Path(__file__).with_name("config.json").read_text(encoding="utf-8"))["organizations"][0]
files = {p.relative_to(root / "site").as_posix(): p.read_text(encoding="utf-8")
         for p in (root / "site").rglob("*") if p.is_file()}
print(validate_site(files, org, "/" + org["repository"] + "/"))
'''
    return files
