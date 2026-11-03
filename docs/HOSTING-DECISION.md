# Hosting decision | Decisão de hosting

**Decision date: 2026-11-03.** This is a deployment recommendation, not evidence that an account, domain, service or public URL exists.

## Selected platform

Use one Hetzner Cloud CX23 server in a Germany location, Docker Compose, and Caddy as the reverse proxy. At the official listed rate, CX23 is €5.49/month excluding VAT, and a primary IPv4 costs €0.50/month excluding VAT: approximately **€5.99/month before applicable taxes**, plus the separately purchased domain. The EU CX plan includes 20 TB outgoing traffic. Actual billing currency, tax and current availability are set by the provider at checkout.

This is a single-server, single-region deployment. It has no automatic failover, managed database or included application-level monitoring. It suits the current static JSON catalogue and read-only API while keeping the monthly baseline low. Caddy obtains and renews HTTPS certificates automatically; Docker Compose keeps the application port private. A fixed Caddy address on the private Docker network allows Waitress to trust only the known proxy and rate-limit actual client addresses.

Sources, checked 2026-11-03:

- Hetzner Cloud prices, including CX23: <https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/>
- Primary IPv4 price: <https://docs.hetzner.com/cloud/servers/primary-ips/overview/>
- EU included traffic: <https://docs.hetzner.com/robot/general/traffic/>
- Hetzner data center locations and backbone: <https://docs.hetzner.com/general/infrastructure-and-availability/data-centers-and-connection/>
- Caddy automatic HTTPS behavior and requirements: <https://caddyserver.com/docs/automatic-https>

## Competitive alternative and contingency

Render paid Web Service is the managed contingency. Its current pricing page lists the smallest paid web service at **US$7/month**; it supports Docker, Frankfurt deployment, custom domains and managed TLS. This is easier to operate, but the app currently trusts a reverse proxy only by one exact peer IP. A managed provider's proxy address behavior must be verified and the client-IP/rate-limit boundary adapted before moving there. We will not infer an upstream proxy IP or trust forwarded headers from arbitrary clients.

Sources, checked 2026-11-03:

- Render pricing: <https://render.com/pricing>
- Render regions: <https://render.com/docs/regions>
- Render custom domains/TLS: <https://render.com/docs/custom-domains>
- Render health checks: <https://render.com/docs/health-checks>

## Image pinning decision

The application image uses `python:3.12-slim-bookworm`: Python minor line and Debian suite are explicit, while upstream security patch rebuilds remain available. A manifest digest is not pinned in this release because no digest was independently verified here and a static digest would require an explicit recurring update process to avoid retaining vulnerable layers. The exact runtime Python dependency remains pinned in `requirements.txt`. CI builds and smoke-tests the image for each relevant pull request. Review and rebuild base images regularly; digest pinning can be introduced with an automated update and review process.

## Cost and approval boundary

No account, server, DNS record, paid service, domain or public deployment was created. Server activation and any domain purchase require the owner's approval. Estimate excludes applicable VAT/taxes, domain registration, optional backups/snapshots, and operator time. Hetzner lists €5.49/month for CX23 plus €0.50/month for IPv4, both excluding VAT; prices and availability can change.
