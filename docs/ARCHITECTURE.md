# Architecture | Arquitetura

## Components

1. **Source inventory and discovery:** institutional sources are distinguished from discovery candidates.
2. **JSON metadata catalogue:** version-controlled records retain identifiers, rights, dates, verification and provenance.
3. **Validation:** JSON Schemas, Python validators, graph checks and CI guard changes.
4. **Read-only API v1:** pure route/query logic in `scripts/api.py`; WSGI middleware and operational controls in `scripts/production.py`.
5. **WSGI server:** Waitress supplies bounded worker and connection handling; the app remains framework-free.
6. **Browser client:** static HTML/CSS/JavaScript consumes the same-origin API. It is replaceable without changing the API data contract.
7. **Reverse proxy:** TLS termination, edge rate limits, domain routing and deployment-specific access controls belong to a separately managed proxy/load balancer.

## Rationale

Waitress is a maintained, pure-Python, production-quality WSGI server with Windows support and configurable worker threads, connection limits, channel timeout, header/body size limits and trusted-proxy controls. It is smaller than adding a web framework plus a server. The project uses a WSGI callable directly, so the public API contract remains independent from the browser interface. Current project documentation and package advisories are reviewed during dependency updates. Waitress 3.0.2 is the minimum selected release; it supports Python 3.9 and later. See the [official Waitress documentation](https://docs.pylonsproject.org/projects/waitress/en/latest/) and [PyPI package metadata](https://pypi.org/project/waitress/).

## Request flow

Client → HTTPS reverse proxy → private Waitress listener → WSGI validation, rate limit, error handling, security headers and request ID → versioned read-only route → JSON records and existing catalogue graph/coverage functions.

Static browser files and JSON API share an origin. CORS is not enabled. The proxy must overwrite forwarded headers; Waitress trusts a proxy only when an exact peer IP is configured. No wildcard proxy trust is permitted. In-process throttling is per process and supplements, rather than replaces, shared edge rate limits.

## Data and legal integrity

- Similarity matches remain suggestions and never create confirmed legal edges.
- Record identity, legal force, temporal status, verification and reuse rights are separate.
- Source texts and PDFs are not served or mirrored.
- Coverage is scoped; “not located” does not assert non-existence.

## Deployment boundary and remaining work

Docker/Compose and an Nginx template are references, not an active public deployment. Domain availability/ownership, DNS, certificates, firewall rules, secrets storage, monitoring provider, backups, hosting capacity and incident response require operational setup. No production database or user-submitted content exists.

## English summary

Angola Legal uses version-controlled JSON as its catalogue. A framework-free WSGI application preserves API v1 and is served by Waitress with bounded worker/connection settings. A same-origin static browser client consumes the API. A separately operated reverse proxy provides HTTPS and edge controls. Deployment files are templates; this repository does not claim a live public service.
