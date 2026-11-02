# Architecture

## Initial model

The initial repository is a version-controlled specification and metadata catalogue. JSON records follow `schemas/legal-document.schema.json`; validation is performed locally and in GitHub Actions. Source documents are not required in the repository: records may point to an authoritative location.

## Logical components

1. **Discovery:** identify candidate material and record source provenance.
2. **Metadata:** describe nature, identifiers, dates, subject, authority, territorial scope, status, and relationships.
3. **Verification:** preserve the assertion, evidence, reviewer state, and time of review.
4. **Rights and privacy review:** determine what metadata, link, or document content may be published.
5. **Presentation and search (future):** expose records with filters and clear uncertainty indicators.

These are conceptual responsibilities; no production service or complete corpus is implied.

## Data flow

Candidate → provenance and rights screening → metadata entry → schema validation → editorial review → versioned publication → periodic or event-triggered recheck. Corrections should be additive and traceable where practical.

## Design constraints

- Stable project record IDs distinct from official identifiers.
- Preserve original source links and source dates; do not silently replace them.
- Handle unavailable sources and conflicting versions explicitly.
- Keep source text separate from project-authored metadata.
- Minimize personal data and avoid collecting credentials or access-restricted content.
- Support multiple document forms and relationships without assuming a simple law/amendment model.

## Future considerations

A database, full-text indexing, OCR, APIs, or document storage require separate design and rights/privacy review. This specification does not authorize collection of restricted materials.
