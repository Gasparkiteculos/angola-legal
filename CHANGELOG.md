# Changelog

All notable project changes are recorded here.

## [0.8.0] - 2026-11-03

- Added an independent, read-only JSON API for health, search/filtering, facets, document records, graph neighborhoods and coverage.
- Added a small responsive browser interface for filtered catalogue search, provenance-linked relationship exploration and coverage counts.
- Kept similarity hints and unresolved references explicit; API output preserves edge evidence and status dimensions.
- Added API unit tests, CI checks and local run instructions. No HTTP API hosting or public deployment is claimed.


## [0.7.0] - 2026-11-03

- Added verified metadata for Lei n.º 18/21 from an official Assembleia Nacional publication and linked its amendment/republication relationship to the Constitution republication record.
- Recorded the source's express restriction on reproduction; no legal text or PDF is redistributed.
- Added suggestion-only similarity hints that cannot resolve graph references or create confirmed edges.
- Added a scoped catalogue coverage ledger, JSON Schema, validation report, API/UI-ready JSON guidance, and CI checks.
- Distinguished verified, pending-verification, and not-located targets; coverage is explicitly non-exhaustive and temporal legal status remains independent.


## [0.6.0] - 2026-11-03

- Added unit tests for direct/inverse relations, ambiguity, unresolved references, duplicates, invalid labels, self-references and edge provenance.
- Added a graph integrity report and CI check; relation labels are constrained by schema and invalid/self-referential edges fail validation.
- Kept ambiguous and unresolved references visible as review warnings rather than dropping them.


## [0.5.0] - 2026-11-03

- Added deterministic JSON and Graphviz DOT output for the legal relationship graph.
- Normalized inverse legal relations, retained assertion provenance and represented unresolved references explicitly.
- Documented graph interpretation and limits; the graph does not infer legal force, validity or completeness.


## [0.4.0] - 2026-11-03

- Added verified metadata records for the Constitution republication identified by the National Assembly digital library and Lei n.º 12/23 from the MAPTSS LGT portal.
- Added optional version/monitoring metadata, local metadata search, version listing and snapshot comparison.
- Documented identity, deduplication, provenance, change checks and safeguards; no legal text or PDF was copied.
- Civil, commercial, tax, administrative, family and procedure areas remain gaps pending primary-source verification.


## [0.3.0] - 2026-11-03

- Added verified metadata records for Lei n.º 38/20 and its amending Lei n.º 12/24, with source links and a bidirectional amendment relationship.
- Recorded gazette series/issue, dates, issuer, evidence, provenance and reuse restrictions; separated verified publication from current temporal status.
- Added an initial catalogue note. No Gazette text or PDF was copied into the repository.

## [0.2.0] - 2026-11-03

- Added source-level inventory separating confirmed official portals and discovery candidates.
- Added JSON Schema, Python validator and unit tests for the source registry.
- Documented discovery, reliability, collection, provenance, deduplication, versioning and legal/ethical safeguards.
- Updated README and GitHub Actions validation.
- No real legal texts or document records were added.

## [0.1.1] - 2026-11-03

- Reconstructed the initial open-source project structure from the project specification.
- Added bilingual guidance, taxonomy, data model, schema, fictitious example, and metadata validator.
- Added contribution, governance, rights, privacy, and security policies.
- Added repository formatting, issue templates, and GitHub Actions validation.
- No real legal texts or corpus records are included.
