# Architecture | Arquitetura

## Components

1. **Source inventory and discovery:** institutional sources are distinguished from discovery candidates.
2. **JSON metadata catalogue:** version-controlled records retain identifiers, rights, dates, verification and provenance.
3. **Validation:** JSON Schemas, Python validators, graph checks and CI guard changes.
4. **Read-only API v1:** pure route/query logic in `scripts/api.py`; WSGI middleware and operational controls in `scripts/production.py`.
5. **WSGI server:** Waitress supplies bounded worker and connection handling; the app remains framework-free.
6. **Browser client:** static HTML/CSS/JavaScript consumes the same-origin API. It is replaceable without changing the API data contract.
7. **Production edge:** a Caddy reverse proxy terminates TLS and routes to Waitress on a private Docker network. CORS stays disabled.

## Rationale

Waitress is a maintained, pure-Python, production-quality WSGI server with Windows support and configurable worker threads, connection limits, channel timeout, header/body size limits and trusted-proxy controls. It is smaller than adding a web framework plus a server. The project uses a WSGI callable directly, so the public API contract remains independent from the browser interface. Current project documentation and package advisories are reviewed during dependency updates. Waitress 3.0.2 is the minimum selected release; it supports Python 3.9 and later. See the [official Waitress documentation](https://docs.pylonsproject.org/projects/waitress/en/latest/) and [PyPI package metadata](https://pypi.org/project/waitress/).

## Request flow

Client → Caddy HTTPS reverse proxy → private Waitress listener → WSGI validation, rate limit, error handling, security headers and request ID → versioned read-only route → JSON records and existing catalogue graph/coverage functions.

The production Compose stack publishes only Caddy on ports 80/443. The application has no host port; its private internal network gives Caddy the fixed peer address `172.29.0.2`. Waitress trusts that one exact proxy address and accepts its forwarded client address and HTTPS scheme. The app and proxy run as non-root where supported, use read-only filesystems, drop capabilities, and use bounded temporary storage. The public Caddy certificate state is kept in named Docker volumes.

The application rate limiter is bounded and process-local. With the single production instance it receives the true client IP from the configured Caddy proxy. Horizontal replicas would each have separate limiter state and require shared rate controls before scaling.

## Data and legal integrity

- Similarity matches remain suggestions and never create confirmed legal edges.
- Record identity, legal force, temporal status, verification and reuse rights are separate.
- Source texts and PDFs are not served or mirrored.
- Coverage is scoped; “not located” does not assert non-existence.
- The API is read-only; non-GET/HEAD methods remain rejected.

## Deployment boundary and remaining work

The production files are a tested template, not an active hosting account or public deployment. Server purchase, verified domain, DNS, provider firewall rules, SSH access, alerting and external HTTPS/API smoke checks require owner configuration. Caddy obtains and renews certificates automatically when the verified DNS and firewall prerequisites are in place. There is no production database or user-submitted content.

## English summary

Angola Legal uses version-controlled JSON as its catalogue. A framework-free WSGI application preserves API v1 and is served by Waitress with bounded worker/connection settings. A same-origin static browser client consumes the API. The production profile uses Docker Compose and Caddy on a single Linux VPS; TLS terminates at Caddy, and Waitress is reachable only on a private network. The repository does not claim a live public service.
