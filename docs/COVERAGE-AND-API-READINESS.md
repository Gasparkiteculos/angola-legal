# Coverage ledger and API readiness

## Coverage is scoped

`coverage/catalogue-coverage.json` is a reviewed list of target instruments, not a census or completeness claim. Each target is `verified`, `pending_verification`, or `not_located`. A verified target must point to a catalogue record whose document identity is verified. Pending and not-located targets cannot carry record IDs. “Not located” reports the result of a bounded search; it does not assert non-existence.

The ledger and report expose counts so a future API or interface can show coverage without implying that the catalogue is complete. Keep the reviewed date and scope note visible whenever publishing the report.

## Resolution and legal relationships

The catalogue resolver creates an edge only for a unique exact identifier match. Normalized similarity is a review hint with a score and method; it remains attached to an unresolved node and never creates a confirmed legal relationship. Editors must inspect primary documentary evidence and record the source URL on the asserting document before confirming an edge.

Relationship edges retain the asserting record, source URL, and verification status. The graph is a deterministic JSON contract suitable for later API/UI consumption, the HTTP API and browser interface are implemented separately. Consumers must preserve unresolved nodes, evidence, and independent legal-force and temporal-status fields.

## Version identity

Use distinct records for originals, amendments, corrigenda, and republications when evidence establishes distinct publication events or documentary forms. Use `versioning.version_of` only when the parent/version relationship is supported. A republication is not automatically a new enactment, and a republication does not establish current force. Deduplicate only when stable identifiers and documentary evidence show that records represent the same item; do not merge merely similar titles.

## Coverage report

Run:

```bash
python scripts/catalog.py coverage
```

The report validates references against verified catalogue records and returns counts by status. CI also validates the coverage JSON Schema. No legal text or PDF is redistributed by the ledger.

## Read-only API v1

Start the local development server with `python scripts/api.py`; it binds to `127.0.0.1:8000` by default. The server is read-only and serves the browser client separately from its JSON routes. This is a local reference implementation, not a hosted production service.

- `GET /api/v1/health` — API version and health.
- `GET /api/v1/search?q=lei&nature=legislation&institution=Assembleia%20Nacional&legal_force=binding&temporal_status=unknown&verification_status=verified&subject=constitucional&date_from=2021-01-01&date_to=2026-12-31&limit=20&offset=0` — search/filter and paginated metadata.
- `GET /api/v1/facets` — available filter values.
- `GET /api/v1/documents/{record_id}` — one complete metadata record.
- `GET /api/v1/graph?record_id={record_id}&depth=1` — graph neighborhood (depth capped at three); omit record ID for the full graph.
- `GET /api/v1/coverage` — scoped counts and target states.

Responses are JSON. Unknown routes/documents return 404; invalid pagination/depth returns 400. The API exposes source URLs and relationship evidence, and does not serve or proxy source texts/PDFs. It offers no write endpoints. The browser interface consumes this API and may be replaced without changing the route/data contract. Before public deployment, place it behind a production-grade server and review operational security, availability, rate limits and cross-origin policy.


## Deployment status

Version 0.9.0 provides a read-only WSGI API and browser client. See [deployment operations](DEPLOYMENT.md) and [API v1](PUBLIC-API.md). A domain, DNS, TLS certificate and public hosting are not configured. Catalogue coverage remains scoped and explicitly non-exhaustive.
