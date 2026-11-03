#!/usr/bin/env python3
"""Validate production Compose isolation and trusted-proxy invariants."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROXY = "172.29.0.2"


def rendered_config() -> dict:
    env = os.environ.copy()
    env.update({
        "ANGOLA_DOMAIN": "deployment-check.example.invalid",
        "ANGOLA_PUBLIC_BASE_URL": "https://deployment-check.example.invalid",
    })
    result = subprocess.run(
        ["docker", "compose", "-f", str(ROOT / "docker-compose.production.yml"),
         "config", "--format", "json"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "production Compose config failed")
    return json.loads(result.stdout)


def main() -> int:
    try:
        config = rendered_config()
        services = config["services"]
        app = services["angola-legal"]
        proxy = services["caddy"]
        if app.get("ports"):
            raise AssertionError("The application must not publish a host port.")
        if "8000" not in [str(port) for port in app.get("expose", [])]:
            raise AssertionError("The application must expose port 8000 only to its private network.")
        if app.get("read_only") is not True or "ALL" not in app.get("cap_drop", []):
            raise AssertionError("The application must use a read-only root and drop all capabilities.")
        if app.get("environment", {}).get("ANGOLA_TRUSTED_PROXY") != EXPECTED_PROXY:
            raise AssertionError("Waitress must trust only the exact Caddy peer address.")
        networks = config["networks"]
        app_net = networks["app_net"]
        if app_net.get("internal") is not True:
            raise AssertionError("Application network must be internal.")
        caddy_ip = proxy.get("networks", {}).get("app_net", {}).get("ipv4_address")
        app_ip = app.get("networks", {}).get("app_net", {}).get("ipv4_address")
        if (caddy_ip, app_ip) != (EXPECTED_PROXY, "172.29.0.3"):
            raise AssertionError("Production proxy and application network addresses do not match.")
        published = {
            (str(port.get("target")), str(port.get("published")), port.get("protocol"))
            for port in proxy.get("ports", []) if isinstance(port, dict)
        }
        expected = {("80", "80", "tcp"), ("443", "443", "tcp"), ("443", "443", "udp")}
        if published != expected:
            raise AssertionError(f"Caddy must publish only HTTP/HTTPS ports; got {published!r}.")
        caddyfile = (ROOT / "deploy" / "Caddyfile").read_text(encoding="utf-8")
        for required in ("{$ANGOLA_DOMAIN}", "reverse_proxy angola-legal:8000",
                         "Strict-Transport-Security", "-Server"):
            if required not in caddyfile:
                raise AssertionError(f"Caddyfile missing required configuration: {required}")
        if "X-Forwarded-For" in caddyfile:
            raise AssertionError("Do not forward client-controlled X-Forwarded-For explicitly.")
        if "8000:" in str(proxy.get("ports", [])):
            raise AssertionError("Application port must never be public.")
    except (AssertionError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"production deployment validation failed: {exc}", file=sys.stderr)
        return 1
    print("production Compose isolation and proxy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
