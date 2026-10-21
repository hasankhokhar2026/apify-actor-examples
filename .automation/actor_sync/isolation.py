"""Brand isolation without embedding other brands' identities in public bundles."""

import hashlib
import json
import re
from urllib.parse import urlsplit, unquote

from .http import SyncError


def fingerprint(text):
    return hashlib.sha256(text.casefold().encode()).hexdigest()


def isolation_config(org, organizations):
    blocked = set()
    for other in organizations:
        if other["apify_username"] != org["apify_username"]:
            for term in (other["brand"], other["apify_username"], other["github_owner"], other["brand"].split()[0]):
                blocked.add(fingerprint(term))
    return {"blocked_fingerprints": sorted(blocked)}


def check_brand(text, org):
    """Check raw data too: hidden metadata must not carry foreign identities."""
    blocked = set(org.get("isolation", {}).get("blocked_fingerprints", []))
    words = re.findall(r"[a-z0-9_-]+", unquote(text).casefold())
    for size in (1, 2, 3):
        for index in range(len(words) - size + 1):
            if fingerprint(" ".join(words[index:index + size])) in blocked:
                raise SyncError("Cross-brand content detected; publication blocked")
    for match in re.finditer(r"https?://[^\s<>\"'\)\]]+", text):
        candidate = match.group().replace("&amp;", "&")
        # The public maintenance code includes f-string URL templates. They are
        # source code, not navigable links, and can contain unmatched brackets.
        if "{" in candidate or "}" in candidate:
            continue
        try:
            url = urlsplit(candidate)
        except ValueError:
            continue
        path = unquote(url.path).split("/")
        if url.hostname in ("apify.com", "www.apify.com") and len(path) >= 3 and path[1] not in (org["apify_username"], "platform", "store", "actors", "api", "web-scraping", "use-cases", "integrations"):
            raise SyncError("Actor link outside this brand's Apify organization; publication blocked")
    return True


def check_snapshot(actors, org):
    if len({a["id"] for a in actors}) != len(actors):
        raise SyncError("Duplicate Actor IDs in publication snapshot")
    for actor in actors:
        if actor["username"] != org["apify_username"] or not actor["url"].startswith("https://apify.com/" + org["apify_username"] + "/"):
            raise SyncError("Actor ownership does not match this brand")
        check_brand(json.dumps(actor, ensure_ascii=False), org)
