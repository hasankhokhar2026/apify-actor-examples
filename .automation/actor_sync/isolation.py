"""Brand isolation without embedding other brands' identities in public bundles."""

import hashlib
import html
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


def check_brand(text, org, own_ids=()):
    """Check raw data too: hidden metadata must not carry foreign identities, and no link may
    point at an Actor or account of another Apify user. `own_ids` are this organization's Actor
    IDs, so links that name an Actor by ID (standby hosts, /actors/<id>) can be verified."""
    blocked = set(org.get("isolation", {}).get("blocked_fingerprints", []))
    words = re.findall(r"[a-z0-9_-]+", unquote(text).casefold())
    for size in (1, 2, 3):
        for index in range(len(words) - size + 1):
            if fingerprint(" ".join(words[index:index + size])) in blocked:
                raise SyncError("Cross-brand content detected; publication blocked")
    for match in URL.finditer(text):
        candidate = match.group().replace("&amp;", "&")
        # The public maintenance code includes f-string URL templates. They are
        # source code, not navigable links, and can contain unmatched brackets.
        if "{" in candidate or "}" in candidate:
            continue
        if foreign_actor_link(candidate, org["apify_username"], own_ids):
            raise SyncError("Link to an Actor or account outside this brand's Apify organization; publication blocked: "
                            + candidate[:200])
    return True


URL = re.compile(r"https?://[^\s<>\"'\)\]]+")
# First path segments of apify.com that are platform pages, never an Actor or an account.
APIFY_PAGES = frozenset("""
about affiliates alternatives api blog careers change-log changelog contact cookie-policy customers data-for-generative-ai
docs ecommerce enterprise fair-use-policy features help integrations jobs legal login marketplace mcp partners payouts
platform pricing privacy-policy product-matching-ai professional-services proxy resources sales scheduler security
sign-up solutions startups status storage store success-stories templates terms-of-service use-cases web-scraping
webinars anti-scraping-protection crawlee residential-proxy datacenter-proxy serverless
""".split())


def foreign_actor_link(candidate, username, own_ids=()):
    """True when a URL points at an Apify Actor (or an Apify account) that is not this
    organization's: apify.com/<user>/<actor> and apify.com/<user>, apify.com/actors/...,
    console.apify.com/actors/<actor>, <user>--<actor>.apify.actor, api.apify.com/v2/acts/<actor>
    and mcp.apify.com?tools=<user>/<actor>. Platform pages (APIFY_PAGES, docs, blog, Console
    settings, runs) are fine. An Actor named by ID is ours only if the ID is in `own_ids`;
    any other Actor whose owner cannot be read from the URL counts as foreign."""
    try:
        # Scanned text is HTML (&quot;) or raw JSON (\" \n): a URL ends at a quote, bracket or backslash.
        candidate = re.split(r"[\"'<>\\\s]", html.unescape(candidate), maxsplit=1)[0]
        url = urlsplit(candidate.strip().rstrip(".,;:!?*_`"))
        host = (url.hostname or "").lower()
    except ValueError:
        return False
    own = username.lower()
    ids = {i.lower() for i in own_ids}
    segments = [s for s in unquote(url.path).split("/") if s]
    first = segments[0].lower() if segments else ""
    if host in ("apify.com", "www.apify.com"):
        if not segments or first == own:
            return False
        if first == "actors":
            return len(segments) > 1 and segments[1].lower() not in ids
        return first not in APIFY_PAGES
    if host == "console.apify.com":
        return first == "actors" and len(segments) > 1 and segments[1].lower() not in ("runs", "tasks", *ids)
    if host.endswith(".apify.actor"):
        label = host[:-len(".apify.actor")]
        return not (label.startswith(own + "--") or label in ids)
    if host == "api.apify.com":
        if len(segments) >= 3 and segments[1].lower() in ("acts", "actors"):
            actor = segments[2].lower()
            return not (actor.startswith(own + "~") or actor.startswith(own + "/") or actor in ids)
        return False
    if host == "mcp.apify.com":
        tools = [t for value in re.findall(r"(?:^|&)tools=([^&]*)", url.query) for t in unquote(value).split(",") if "/" in t]
        return any(not t.lower().startswith(own + "/") for t in tools)
    return False


MARKDOWN_LINK = re.compile(r"(!?)\[([^\]\n]*)\]\(\s*<?(https?://[^\s)>]+)>?(?:\s+\"[^\"\n]*\")?\s*\)")


def strip_foreign_links(text, username, own_ids=()):
    """Publisher text with every link to another account's Actor turned into plain text: a
    Markdown link keeps its words, a bare or angle-bracket URL keeps its host and path without
    the scheme (readable, never a link). Returns (text, [rewritten URLs])."""
    rewritten = []

    def link(match):
        if not foreign_actor_link(match.group(3), username, own_ids):
            return match.group(0)
        rewritten.append(match.group(3))
        words = match.group(2).strip()
        return words or match.group(3).split("://", 1)[1]

    text = MARKDOWN_LINK.sub(link, text)

    def bare(match):
        candidate = match.group()
        if "{" in candidate or "}" in candidate or not foreign_actor_link(candidate.replace("&amp;", "&"), username, own_ids):
            return candidate
        rewritten.append(candidate)
        return candidate.split("://", 1)[1]

    text = URL.sub(bare, text)
    text = re.sub(r"<((?:[a-z0-9-]+\.)*apify\.(?:com|actor)/[^>\s]*)>", r"\1", text)
    return text, rewritten


def strip_foreign_actor_links(actor, username, own_ids=()):
    """Apply strip_foreign_links to every string the publisher wrote (README, title,
    description, schemas). Returns (actor, [rewritten URLs]) for the run log."""
    found = []

    def walk(value):
        if isinstance(value, str):
            clean, urls = strip_foreign_links(value, username, own_ids)
            found.extend(urls)
            return clean
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    cleaned = dict(actor)
    for key in ("readme", "title", "description", "input_schema", "output_schema", "dataset_schema", "key_value_schema"):
        if key in cleaned:
            cleaned[key] = walk(cleaned[key])
    return cleaned, found


def check_snapshot(actors, org):
    if len({a["id"] for a in actors}) != len(actors):
        raise SyncError("Duplicate Actor IDs in publication snapshot")
    for actor in actors:
        if actor["username"] != org["apify_username"] or not actor["url"].startswith("https://apify.com/" + org["apify_username"] + "/"):
            raise SyncError("Actor ownership does not match this brand")
        check_brand(json.dumps(actor, ensure_ascii=False), org, {a["id"] for a in actors})
