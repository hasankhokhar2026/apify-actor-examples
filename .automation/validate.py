"""Validate the exact static artifact before deployment."""
from pathlib import Path
import json
from actor_sync.site import validate_site

root = Path.cwd()
org = json.loads(Path(__file__).with_name("config.json").read_text(encoding="utf-8"))["organizations"][0]
files = {p.relative_to(root / "site").as_posix(): p.read_text(encoding="utf-8")
         for p in (root / "site").rglob("*") if p.is_file()}
print(validate_site(files, org, "/" + org["repository"] + "/"))
