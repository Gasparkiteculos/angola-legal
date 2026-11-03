#!/usr/bin/env python3
"""Validate rendered Compose settings and proxy trust boundaries."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def rendered_compose(proxy_address: str) -> dict:
    env = os.environ.copy()
    env["ANGOLA_TRUSTED_PROXY"] = proxy_address
    result = subprocess.run(
        ["docker", "compose", "-f", str(ROOT / "docker-compose.yml"),
         "config", "--format", "json"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "docker compose config failed")
    return json.loads(result.stdout)


def check_compose(proxy_address: str) -> None:
    service = rendered_compose(proxy_address)["services"]["angola-legal"]
    actual = service.get("environment", {}).get("ANGOLA_TRUSTED_PROXY")
    if actual != proxy_address:
        raise AssertionError(
            f"Compose did not pass ANGOLA_TRUSTED_PROXY: expected {proxy_address!r}, got {actual!r}"
        )
    ports = service.get("ports", [])
    if not any(
        str(port.get("target")) == "8000"
        and str(port.get("published")) == "8000"
        and port.get("host_ip") == "127.0.0.1"
        for port in ports if isinstance(port, dict)
    ):
        raise AssertionError("Application port must be published on host loopback only.")
    if service.get("read_only") is not True:
        raise AssertionError("Compose must use a read-only root filesystem.")
    if "ALL" not in service.get("cap_drop", []):
        raise AssertionError("Compose must drop all Linux capabilities.")
    if "no-new-privileges:true" not in service.get("security_opt", []):
        raise AssertionError("Compose must enable no-new-privileges.")


def main() -> int:
    try:
        check_compose("")
        check_compose("192.0.2.44")
        nginx = (ROOT / "deploy" / "nginx.conf.example").read_text(encoding="utf-8")
        required = (
            "proxy_set_header X-Forwarded-For $remote_addr;",
            "proxy_set_header X-Forwarded-Proto https;",
            "return 301 https://$server_name$request_uri;",
            "limit_req_status 429;",
        )
        for directive in required:
            if directive not in nginx:
                raise AssertionError(f"Nginx template missing required directive: {directive}")
        if "$proxy_add_x_forwarded_for" in nginx:
            raise AssertionError("Nginx must not append untrusted client-supplied X-Forwarded-For.")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        if "USER 10001:10001" not in dockerfile:
            raise AssertionError("Image must run as a non-root user.")
        ignored = set((ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines())
        for name in (".env", "tests", "docs", ".git"):
            if name not in ignored:
                raise AssertionError(f"Build context should exclude {name}.")
    except (AssertionError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"deployment validation failed: {exc}", file=sys.stderr)
        return 1
    print("deployment configuration checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
