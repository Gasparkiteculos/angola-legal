# Coverage ledger and API readiness

## Coverage is scoped

`coverage/catalogue-coverage.json` is a reviewed list of target instruments, not a census or completeness claim. Each target is `verified`, `pending_verification`, or `not_located`. A verified target must point to a catalogue record whose document identity is verified. Pending and not-located targets cannot carry record IDs. “Not located” reports the result of a bounded search; it does not assert non-existence.

The ledger and report expose counts so a future API or interface can show coverage without implying that the catalogue is complete. Keep the reviewed date and scope note visible whenever publishing the report.

## Resolution and legal relationships

The catalogue resolver creates an edge only for a unique exact identifier match. Normalized similarity is a review hint with a score and method; it remains attached to an unresolved node and never creates a confirmed legal relationship. Editors must inspect primary documentary evidence and record the source URL on the asserting document before confirming an edge.

Relationship edges retain the asserting record, source URL, and verification status. The graph is a deterministic JSON contract suitable for later API/UI consumption, but this release does not provide an HTTP API or visual interface. Consumers must preserve unresolved nodes, evidence, and independent legal-force and temporal-status fields.

## Version identity

Use distinct records for originals, amendments, corrigenda, and republications when evidence establishes distinct publication events or documentary forms. Use `versioning.version_of` only when the parent/version relationship is supported. A republication is not automatically a new enactment, and a republication does not establish current force. Deduplicate only when stable identifiers and documentary evidence show that records represent the same item; do not merge merely similar titles.

## Coverage report

Run:

```bash
python scripts/catalog.py coverage
```

The report validates references against verified catalogue records and returns counts by status. CI also validates the coverage JSON Schema. No legal text or PDF is redistributed by the ledger.
