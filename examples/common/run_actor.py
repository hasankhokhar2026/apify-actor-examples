#!/usr/bin/env python3
"""Validate an Actor input, optionally run it, and download a bounded dataset sample.

Python 3.10+, no dependencies. Default mode makes public GET requests only.
"""

import argparse
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc != "api.apify.com":
            raise ValueError("Refused a cross-host API redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(path, token=None, payload=None):
    headers = {"User-Agent": "apify-actor-examples/1.0", "Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(payload).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request("https://api.apify.com/v2" + path, headers=headers, data=data)
    # No automatic retries of run creation: a lost response could still mean the
    # run was created. Check Apify Console before submitting it a second time.
    try:
        with urllib.request.build_opener(SameHostRedirect()).open(req, timeout=40) as response:
            raw = response.read(32 * 1024 * 1024 + 1)
            if len(raw) > 32 * 1024 * 1024:
                raise ValueError("Response exceeds 32 MiB; lower --download-limit")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise ValueError(f"Apify returned HTTP {exc.code}; inspect the Actor's pricing, input, and permissions") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ValueError("Network request failed; check Console before retrying a run submission") from None


def validate(value, schema, path="input"):
    """Basic JSON Schema checks; Apify performs full validation when a run starts."""
    expected = schema.get("type")
    types = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
             "string": lambda x: isinstance(x, str), "boolean": lambda x: isinstance(x, bool),
             "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
             "number": lambda x: isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x),
             "null": lambda x: x is None}
    if isinstance(expected, str) and expected in types and not types[expected](value):
        raise ValueError(f"{path} must be {expected}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} has an unsupported value")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{path}.{key} is required")
        for key, child in value.items():
            props = schema.get("properties", {})
            if key in props:
                validate(child, props[key], path + "." + key)
            elif schema.get("additionalProperties") is False:
                raise ValueError(f"{path}.{key} is unsupported")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(schema.get("items"), dict):
                validate(child, schema["items"], f"{path}[{index}]")
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")):
            raise ValueError(f"{path} has an invalid number of entries")
    elif isinstance(value, (float, int)) and not isinstance(value, bool):
        if value < schema.get("minimum", -float("inf")) or value > schema.get("maximum", float("inf")):
            raise ValueError(f"{path} is outside its allowed range")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actor", required=True, help="Stable Actor ID")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    parser.add_argument("--execute", action="store_true", help="Start a potentially billable Apify run")
    parser.add_argument("--budget-usd", type=float, default=0.50, help="Apify maxTotalChargeUsd request, not an all-inclusive cost guarantee")
    parser.add_argument("--actor-timeout", type=int, default=120)
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--download-limit", type=int, default=100)
    args = parser.parse_args(argv)
    try:
        if not re.fullmatch(r"[A-Za-z0-9]{8,40}", args.actor):
            raise ValueError("--actor must be a stable Actor ID")
        if not math.isfinite(args.budget_usd) or args.budget_usd <= 0 or not 1 <= args.download_limit <= 10000 or not 1 <= args.actor_timeout <= 3600 or not 1 <= args.wait_seconds <= 3600:
            raise ValueError("Use a positive budget, download limit 1..10000, and timeouts 1..3600")
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Input must be a JSON object")
        build = request(f"/acts/{args.actor}/builds/default")["data"]
        schema = (build.get("actorDefinition") or {}).get("input") or build.get("inputSchema")
        if isinstance(schema, str):
            schema = json.loads(schema)
        if not isinstance(schema, dict):
            raise ValueError("Published input schema is unavailable")
        validate(payload, schema)
        if not args.execute:
            print("Basic input validation passed against the published schema. No run started.")
            print("Review pricing and add --execute to start a billable run. Apify performs full input validation.")
            return 0
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            raise ValueError("Set APIFY_TOKEN before using --execute")
        query = urllib.parse.urlencode({"timeout": args.actor_timeout, "maxTotalChargeUsd": args.budget_usd})
        run = request(f"/acts/{args.actor}/runs?{query}", token, payload)["data"]
        run_id = run["id"]
        if not re.fullmatch(r"[A-Za-z0-9]{8,40}", run_id):
            raise ValueError("Unexpected run identifier")
        print(f"Run: https://console.apify.com/actors/runs/{run_id}", file=sys.stderr)
        deadline = time.monotonic() + args.wait_seconds
        while run["status"] in ("READY", "RUNNING", "ABORTING", "TIMING-OUT") and time.monotonic() < deadline:
            time.sleep(3)
            run = request(f"/actor-runs/{run_id}", token)["data"]
        if run["status"] != "SUCCEEDED":
            raise ValueError(f"Run status: {run['status']}. A nonterminal run may continue; manage it using the Console link above")
        dataset_id = run.get("defaultDatasetId")
        if not isinstance(dataset_id, str) or not re.fullmatch(r"[A-Za-z0-9]{8,40}", dataset_id):
            raise ValueError("The run did not provide a default dataset")
        rows = request(f"/datasets/{dataset_id}/items?clean=true&limit={args.download_limit}", token)
        if not isinstance(rows, list):
            raise ValueError("Unexpected dataset response")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Saved {len(rows)} records to {args.output}. Download is capped at {args.download_limit}; the Actor may have produced more records.")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        message = str(exc)
        if os.environ.get("APIFY_TOKEN"):
            message = message.replace(os.environ["APIFY_TOKEN"], "[REDACTED]")
        print("Error: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
