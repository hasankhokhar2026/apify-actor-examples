#!/usr/bin/env python3
"""Process downloaded or synthetic datasets locally. No network requests."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re


def csv_cell(value):
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        value = "'" + value
    return value


def write_csv(rows, output):
    fields = sorted({key for row in rows for key in row})
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: csv_cell(v) for k, v in row.items()} for row in rows)


def dedupe(rows, keys):
    seen, result = set(), []
    for row in rows:
        # Include the field name so an ID cannot collide with an unrelated URL.
        identity = next(((key, str(row[key])) for key in keys if row.get(key) is not None and row.get(key) != ""), None)
        if identity is None:
            identity = ("record", json.dumps(row, sort_keys=True, ensure_ascii=False))
        if identity not in seen:
            seen.add(identity)
            result.append(row)
    return result


def transform(rows, mode, output, keys):
    if mode in ("csv", "dedupe"):
        result = dedupe(rows, keys) if mode == "dedupe" else rows
        write_csv(result, output)
        return {"input_records": len(rows), "output_records": len(result)}
    if mode == "ratings":
        counts = Counter()
        for row in rows:
            if row.get("recordType") not in (None, "review", "authorReview"):
                continue
            value = row.get("rating", row.get("stars", row.get("starRating")))
            if isinstance(value, (float, int)) and not isinstance(value, bool) and 1 <= value <= 5:
                counts[str(value)] += 1
        report = {"input_records": len(rows), "rated_reviews": sum(counts.values()), "rating_counts": dict(sorted(counts.items()))}
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report
    if mode == "markdown":
        output.mkdir(parents=True, exist_ok=True)
        manifest = []
        for index, row in enumerate(rows):
            content = row.get("markdown") or row.get("text")
            if not isinstance(content, str) or not content.strip():
                continue
            url = str(row.get("url") or row.get("loadedUrl") or "")
            # Names depend on source URL and position, never an untrusted title/path.
            name = f"{index:04d}-{hashlib.sha256(url.encode()).hexdigest()[:10]}.md"
            (output / name).write_text(f"Source: {url}\n\n{content}\n", encoding="utf-8")
            manifest.append({"file": name, "url": url, "title": row.get("title", "")})
        (output / "sources.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {"input_records": len(rows), "markdown_files": len(manifest)}
    if mode == "transcript":
        chunks = []
        for row in rows:
            title = str(row.get("title") or row.get("videoTitle") or "Video transcript")
            url = str(row.get("url") or row.get("videoUrl") or row.get("inputUrl") or "")
            text = row.get("text") or row.get("transcript") or row.get("fullText") or row.get("full_text")
            segments = row.get("segments") or row.get("timedSegments") or []
            lines = ["# " + title, "", "Source: " + url, ""]
            if isinstance(segments, list) and segments:
                for segment in segments:
                    if isinstance(segment, dict) and isinstance(segment.get("text"), str):
                        lines.append(f"- [{segment.get('start', segment.get('startTime', 0))}s] {segment['text']}")
            elif isinstance(text, str):
                lines.append(text)
            else:
                continue
            chunks.append("\n".join(lines))
        output.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
        return {"input_records": len(rows), "transcripts": len(chunks)}
    raise ValueError("Unsupported processing mode")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["csv", "ratings", "dedupe", "markdown", "transcript"])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keys", default="placeId,id,url", help="Comma-separated ID fields for dedupe, in priority order")
    args = parser.parse_args(argv)
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        parser.error("Expected a JSON array of record objects")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps(transform(rows, args.mode, args.output, args.keys.split(","))))


if __name__ == "__main__":
    main()
