#!/usr/bin/env python3
"""Exercise a running local Compose deployment using only the Python stdlib."""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def get(path: str, method: str = "GET"):
    request = Request(BASE + path, method=method)
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, response.headers, response.read()
    except HTTPError as response:
        return response.code, response.headers, response.read()


def main() -> int:
    for _ in range(30):
        try:
            status, _, _ = get("/health/ready")
            if status == 200:
                break
        except OSError:
            time.sleep(1)
    else:
        raise SystemExit("container did not become ready")

    for path in ("/health/live", "/health/ready", "/api/v1/health",
                 "/api/v1/facets", "/api/v1/sources", "/api/v1/coverage",
                 "/api/v1/graph", "/api/v1/search?limit=1", "/"):
        status, headers, body = get(path)
        assert status == 200, (path, status)
        assert headers.get("X-Request-ID"), path
        assert headers.get("X-Content-Type-Options") == "nosniff", path
        if path.startswith("/api/") or path.startswith("/health/"):
            json.loads(body)

    status, _, body = get("/", method="HEAD")
    assert status == 200 and body == b""
    status, headers, body = get("/api/v1/health", method="POST")
    assert status == 405
    assert headers.get("Allow") == "GET, HEAD"
    assert json.loads(body)["error"]["code"] == "405"
    print("container smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
