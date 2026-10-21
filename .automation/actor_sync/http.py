"""Small, bounded HTTP client. Tokens never appear in URLs or error messages."""

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request


class SyncError(Exception):
    """An expected, safe-to-log operation failure."""


class HttpError(SyncError):
    def __init__(self, status, path):
        self.status = status
        super().__init__(f"HTTP {status} for {path.split('?')[0]}")


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
            raise SyncError("Refused a cross-host API redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Api:
    def __init__(self, base, token=None, attempts=4, timeout=40, opener=None, sleep=time.sleep):
        self.base = base.rstrip("/")
        self.token = token
        self.attempts = attempts
        self.timeout = timeout
        self.opener = opener or urllib.request.build_opener(SameHostRedirect())
        self.sleep = sleep

    def request(self, path, method="GET", data=None):
        if not path.startswith("/") or path.startswith("//"):
            raise SyncError("API path must be relative to the configured API host")
        headers = {"User-Agent": "apify-github-documentation-sync/1.0", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.base == "https://api.github.com":
            headers.update({"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
        payload = None if data is None else json.dumps(data).encode("utf-8")
        if payload is not None:
            headers["Content-Type"] = "application/json"
        # Never retry a mutation: an interrupted response may already have created it.
        attempts = self.attempts if method == "GET" else 1
        for attempt in range(attempts):
            req = urllib.request.Request(self.base + path, data=payload, method=method, headers=headers)
            try:
                with self.opener.open(req, timeout=self.timeout) as response:
                    raw = response.read(16 * 1024 * 1024 + 1)
                    if len(raw) > 16 * 1024 * 1024:
                        raise SyncError("API response exceeded 16 MiB")
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as exc:
                retryable = exc.code in (429, 500, 502, 503, 504)
                if not retryable or attempt + 1 == attempts:
                    raise HttpError(exc.code, path) from None
                try:
                    delay = max(2 ** attempt, float(exc.headers.get("Retry-After", "0")))
                except (TypeError, ValueError):
                    delay = 2 ** attempt
                if delay > 60:
                    raise SyncError("API asked for a long retry delay; retry at the next scheduled run") from None
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt + 1 == attempts:
                    raise SyncError(f"Network failure for {path.split('?')[0]}") from None
                delay = 2 ** attempt
            except (ValueError, UnicodeError):
                raise SyncError(f"Invalid JSON response for {path.split('?')[0]}") from None
            logging.warning("Transient API failure; retrying GET in %.0f seconds", delay)
            self.sleep(delay)

    def data(self, path):
        response = self.request(path)
        if not isinstance(response, dict) or not isinstance(response.get("data"), dict):
            raise SyncError("API response is missing its data object")
        return response["data"]
