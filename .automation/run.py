"""Maintain this repository's own Apify organization only."""
from pathlib import Path
import tempfile
from actor_sync.cli import main

raise SystemExit(main(["--config", str(Path(__file__).with_name("config.json")),
                      "--state-dir", str(Path(tempfile.gettempdir()) / "actor-docs-sync"),
                      "sync", "--push"]))
