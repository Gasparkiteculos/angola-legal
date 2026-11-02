# Source discovery and collection | Descoberta e recolha de fontes

## Purpose and limits

The registry at `sources/source-registry.json` inventories portals, not legal documents. It contains no inferred document records. A source-level verification says only that the portal/institution and the stated access observation were checked on the recorded date; it does not authenticate every item hosted there or establish that a corpus is complete.

## Method | Método

1. Start with institutional links and primary official domains; use search only to discover candidate URLs.
2. Open the portal and confirm institutional identity from the portal itself, a government domain, or an official institutional page. Record the exact URL and the date checked.
3. Confirm what it actually publishes and how a visitor can access it. Record observed availability, including timeouts, login/paywall restrictions, and incomplete listings.
4. Keep source roles separate: official publication, court decision portal, ministry/regulator portal, international treaty repository, or discovery index.
5. Seed only source-level facts that were observed. Never infer document names, dates, enactment, publication, legal force, or current status from search snippets or third-party mirrors.
6. Recheck sources periodically and after redirects, host changes, prolonged outages, or conflicting records. Preserve prior observations in version history rather than silently rewriting history.

The initial inventory was checked on 2026-11-03. Search engines aided discovery; cited evidence URLs point to the institution or repository page where possible. The DRON portal says II and III Series remain available through Imprensa Nacional channels, but the specific publisher portal timed out during checking. No unverified Imprensa Nacional URL is seeded; that access route remains an open discovery task. The Angolex entry is a third-party lead only, not an authoritative source.

## Reliability tiers | Níveis de fiabilidade

- **Tier 1 — official primary publication:** the competent official gazette or issuing institution's own portal for materials it publishes. The DRON entry is limited to I Série as its own page states; other series require separate confirmation. Court portals are primary for their published decisions, not for legislation.
- **Tier 2 — official institutional copy or status register:** official parliament, ministry, regulator, court, treaty depositary, or regional organization portal. It is authoritative for its own records and remit, but may not be complete and may not prove domestic promulgation or legal effect.
- **Tier 3 — discovery only:** commercial indexes, libraries, search engines, mirrors, and unverified publisher links. Use to find leads; corroborate each material fact against a Tier 1 or Tier 2 source.
- Reliability is contextual, not a numeric quality score. Authority of the institution does not remove the need to check version, provenance, and scope.

## Collection workflow | Fluxo de recolha

1. Select a registered source and record its current verification state.
2. Retrieve politely through documented public browsing or a documented API. Respect terms, robots directives, access controls, rate limits, and site stability; no login circumvention or bulk collection without permission.
3. Capture a source URL, retrieval timestamp (UTC), retrieval method, response/availability note, and a cryptographic hash for any lawfully retained file. Keep the original URL even when a stable local identifier is assigned.
4. Transcribe metadata independently from the item. Preserve the publisher's title/date/number exactly as displayed, but record uncertain values as unknown and cite the page/PDF location used.
5. Have a second reviewer confirm source identity, key identifiers, series/edition, and evidence of publication before marking an item verified. Source verification and document verification are separate.
6. Store only metadata and links by default. Do not redistribute source PDFs, scans, or extracted full text unless documented permission or a clear applicable licence has been reviewed. Minimize personal data in court materials.

## Provenance, deduplication and versioning

Each future document record should point to one or more source IDs and retain the exact source URL, retrieved-at timestamp, retrieval method, observed availability, and evidence supporting each field. Never replace the source URL with a search result or an aggregator link.

Deduplicate using official publication identifiers where available (series, issue, number, publication date, instrument number), then compare stable URLs and file hashes. A matching title alone is insufficient. Preserve distinct editions, corrigenda, amended/consolidated versions, and duplicate scans as relationships; do not collapse them into one record.

Treat every retrieval as an immutable version event. Store retrieval timestamp, hash, and collector/tool version; record HTTP validators or portal identifiers when available. New content creates a new version, never overwrites prior provenance. Keep version history and corrections reviewable in Git.

## Legal and ethical safeguards

Public availability is not a grant of copyright or database rights. Record the access method and rights caveat; link out unless reuse terms expressly permit a local copy. Do not defeat paywalls, authentication, technical barriers, CAPTCHA, or rate limits. Avoid collecting sealed, sensitive, or unnecessary personal information. Respect court anonymization and correction requests and escalate uncertain privacy/right questions for human review. A portal listing does not itself prove legal force, currentness, or validity; verify legal status from the official publication and applicable amendment/repeal history.
