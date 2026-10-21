"""Read only public metadata and documentation; never fetch Actor source files."""

import concurrent.futures
import json
import re
import urllib.parse

from .http import Api, SyncError

SAFE_ID = re.compile(r"^[A-Za-z0-9]{8,40}$")
SAFE_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,150}$")


def schema_object(value, name):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            raise SyncError(f"Invalid {name} JSON") from None
    if not isinstance(value, dict):
        raise SyncError(f"Invalid {name}: expected an object")
    return value


class Apify:
    def __init__(self, api=None):
        self.api = api or Api("https://api.apify.com")

    def listing(self, username):
        items, seen = [], set()
        expected_total = None
        for _ in range(1000):
            query = urllib.parse.urlencode({"username": username, "limit": 100, "offset": len(items)})
            page = self.api.data("/v2/store?" + query)
            rows, total = page.get("items"), page.get("total")
            if not isinstance(rows, list) or not isinstance(total, int) or total < 0:
                raise SyncError("Invalid Store pagination response")
            if expected_total is not None and total != expected_total:
                raise SyncError("Store listing changed during pagination; retry later")
            expected_total = total
            for row in rows:
                actor_id, slug = row.get("id", ""), row.get("name", "")
                if row.get("username") != username or not SAFE_ID.fullmatch(actor_id) or not SAFE_SLUG.fullmatch(slug):
                    raise SyncError("Store returned an unexpected organization or Actor identifier")
                if actor_id in seen:
                    raise SyncError("Store pagination returned a duplicate Actor")
                seen.add(actor_id)
                items.append(row)
            if len(items) == total:
                return items
            if not rows or len(items) > total:
                raise SyncError("Incomplete Store listing; refusing to publish a partial catalog")
        raise SyncError("Store pagination exceeded its safety limit")

    def actor(self, listing):
        actor_id = listing["id"]
        actor = self.api.data(f"/v2/acts/{actor_id}")
        if (actor.get("id") != actor_id or actor.get("username") != listing["username"]
                or not actor.get("isPublic") or not SAFE_SLUG.fullmatch(actor.get("name", ""))):
            raise SyncError(f"Actor {actor_id} is no longer public or changed ownership; retry listing")
        # Always fetch the default build, even if build IDs are unchanged. Hash the text,
        # not modifiedAt; README changes must not depend on timestamp semantics.
        build = self.api.data(f"/v2/acts/{actor_id}/builds/default")
        if build.get("actId") != actor_id or build.get("status") != "SUCCEEDED":
            raise SyncError(f"Actor {actor_id} has no successful default build")
        definition = build.get("actorDefinition") or {}
        readme = definition.get("readme")
        if (not isinstance(readme, str) or not readme.strip()
                or re.fullmatch(r"(?:[\w.-]+/)*[\w.-]+\.md", readme, re.I)):
            readme = build.get("readme")
        if not isinstance(readme, str) or not readme.strip():
            raise SyncError(f"Actor {actor_id} has no published README")
        readme = readme.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"
        input_schema = schema_object(definition.get("input") or build.get("inputSchema"), "input schema")
        if input_schema is None:
            raise SyncError(f"Actor {actor_id} has no published input schema")
        output_schema = schema_object(definition.get("output"), "output schema")
        storages = definition.get("storages") or {}
        if not isinstance(storages, dict):
            raise SyncError(f"Actor {actor_id} has invalid storage definitions")
        dataset_schema = schema_object(storages.get("dataset"), "dataset schema")
        key_value_schema = schema_object(storages.get("keyValueStore"), "key-value store schema")
        # Explicit allowlist: do not serialize builds, environment variables, versions,
        # deployment settings, source files, or the raw Actor API response.
        return {
            "id": actor_id,
            "name": actor["name"],
            "username": actor["username"],
            "title": actor.get("title") or actor["name"],
            "description": actor.get("description") or "",
            "categories": sorted(actor.get("categories") or []),
            "status": "deprecated" if actor.get("isDeprecated") else "public",
            "url": f"https://apify.com/{actor['username']}/{actor['name']}",
            "build_id": build["id"],
            "readme": readme,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "dataset_schema": dataset_schema,
            "key_value_schema": key_value_schema,
        }

    def snapshot(self, username, workers=4):
        listings = self.listing(username)
        # Actor GET and build GET are independent across Actors; bound concurrency.
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            actors = list(pool.map(self.actor, listings))
        return sorted(actors, key=lambda a: a["id"])
