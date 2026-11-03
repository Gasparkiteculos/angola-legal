# Deployment and operations | Publicação e operação

## Current status

The repository contains a production profile for one Linux VPS using Docker Compose, a private Waitress service and Caddy for HTTPS. No provider account, domain, DNS, TLS endpoint, monitoring vendor or public deployment is configured. The `.invalid` values in `.env.example` are reserved placeholders and must be replaced with a domain the project owner controls.

See `HOSTING-DECISION.md` for the provider choice and dated price estimate. No paid service or domain was purchased.

## Requirements

- Linux VPS with Docker Engine and the Docker Compose plugin.
- A domain registered and controlled by the owner.
- Provider firewall access: allow TCP 80/443 and UDP 443 from the Internet; allow SSH only from an authorized administrator address. Do not open TCP 8000.
- DNS A record pointing to the VPS public IPv4. The baseline stack does not publish IPv6 listeners; do not add an AAAA record until explicit IPv6 host bindings and firewall rules have been configured and tested.
- Git access to the repository and an owner-managed SSH key.

## First activation

1. Provision an Ubuntu or Debian server in Germany and enable a provider-level firewall before opening public traffic. Apply OS updates and restrict SSH to key authentication.
2. Verify domain ownership and configure DNS to the allocated server IP. Do not assume any particular Angola domain is available.
3. Clone the reviewed repository branch/commit on the host. Do not deploy an unreviewed branch.
4. Copy `.env.example` to `.env`, then set `ANGOLA_DOMAIN` and `ANGOLA_PUBLIC_BASE_URL` to the verified hostname and its exact HTTPS origin. The file is Git-ignored; do not commit it. No application secret is required.
5. Confirm that the private subnet `172.29.0.0/24` does not conflict with an existing Docker network. If it does, change the subnet and both fixed container addresses together, then adjust the trusted proxy address in production Compose to the exact Caddy address.
6. Check the rendered config and start the stack:
   ```sh
   docker compose --env-file .env -f docker-compose.production.yml config --quiet
   docker compose --env-file .env -f docker-compose.production.yml up --build -d
   docker compose --env-file .env -f docker-compose.production.yml ps
   ```
7. Caddy obtains and renews the public certificate automatically after DNS points to the server and inbound ports 80/443 are reachable. Do not repeatedly test against a production certificate authority before DNS and firewall are ready.
8. Verify externally: `https://<verified-domain>/health/ready`, `/api/v1/health`, `/api/v1/search?limit=1`, and the home page. Confirm HTTP redirects to HTTPS, browser certificate validity, `X-Request-ID`, the security headers, and that POST returns 405.
9. Add an external uptime check for `/health/ready` and an alert for availability failures. Keep alerts free of query-string content and personal data.

The application service has no published host port. It joins only the private internal network; Caddy has the fixed private peer address `172.29.0.2`, which is the sole configured trusted proxy. Caddy overwrites forwarded-client headers by default. The UI and API share one origin, so CORS remains disabled.

## Logs and monitoring

- Application logs are structured JSON on stdout with request ID, method, route, status and duration. They omit the client IP and query string.
- Inspect service output with `docker compose -f docker-compose.production.yml logs --since=1h angola-legal caddy`. Set host journal/log rotation and retention to a bounded period.
- Monitor the external readiness URL, container restarts, disk use, CPU, memory, and certificate issuance/renewal errors. Provider dashboards offer infrastructure-level signals; configure a separate uptime alert.
- `/health/live` is a liveness check. `/health/ready` confirms core JSON data can be read and has the expected primary structure. Neither certifies legal completeness or current legal force.

## Updates, backups and recovery

The application stores no mutable catalogue state in the container. Legal metadata, source inventory and configuration templates are versioned in Git; third-party legal texts and PDFs are not copied by deployment. Recovery is to provision a clean host, apply firewall and OS updates, check out the last approved commit, restore the owner-managed `.env`, and run Compose again.

Caddy's named `caddy_data` volume stores certificates and private TLS material; `caddy_config` stores runtime state. Persist these Docker volumes across container replacement. Back up the Compose configuration and owner-managed environment file in an encrypted secret store. If backing up Caddy volume contents, encrypt them, restrict access and retention, and never put them in Git. Certificates can be reissued if the volume is lost, provided the domain and ports are correctly configured. Test restoration and rollback after first activation and after major configuration changes.

There is no database backup, because the current service has no database or writable application data. Backups of source-controlled catalog data follow the repository's normal GitHub backup policy; they do not confer additional copyright or redistribution rights.

## Rollback

Keep the previous approved Git commit available. To roll back, check out that commit, verify its production Compose configuration, rebuild the image, and run `docker compose ... up --build -d`. Confirm readiness and the public smoke checks. Do not change legal metadata in response to an operational rollback.

## Image base and dependency updates

The application base is `python:3.12-slim-bookworm`, not a manifest digest. The Python minor version and Debian suite are explicit; patch layers can receive upstream fixes as images are rebuilt. A digest would improve repeatability but can freeze old security layers unless routinely refreshed. Introduce digest pinning only with a verified digest and a recurring reviewed update mechanism. Runtime Waitress remains version-pinned; CI audits it with pip-audit.

## CI/CD approval

GitHub Actions runs on relevant pull requests and commits: metadata/source validation, tests, graph and coverage checks, syntax and dependency audit, Compose and Caddy validation, Docker build, and application smoke checks. It does not hold production credentials and does not deploy. Production deployment is a manual owner-operated step after reviewing and accepting the pull request; no automatic production release is configured.

## Local container

The existing local profile is unchanged:

```sh
docker compose up --build -d
curl --fail http://127.0.0.1:8000/health/ready
docker compose down
```

## Limitations

This single VPS has a single point of failure and no managed failover. The rate limiter is process-local, appropriate to the current single instance; scaling to multiple app replicas needs shared edge limiting. CI validates the production Compose shape and Caddy syntax but cannot establish the actual DNS, firewall, TLS certificate, provider availability or public health endpoint. Do not describe the service as publicly available until external HTTPS and API checks pass.
