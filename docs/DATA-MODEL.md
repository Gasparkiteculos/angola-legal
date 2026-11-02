# Data model

A record describes an item and its evidence, not necessarily the item’s full text. The JSON Schema is normative for the initial metadata format.

## Identity and description

- `record_id`: stable project identifier.
- `title`, optional language-specific titles.
- `document_nature`: type/category of the item, independent of effect.
- `document_nature_detail`: local explanatory label.

## Independent legal and editorial dimensions

- `legal_force`: binding, non-binding, persuasive, informational, or unknown.
- `temporal_status`: in force, partially in force, amended, repealed, expired, not yet in force, historical, not applicable, or unknown.
- `verification_status`: verification state of record assertions.
- `reuse_rights.status`: project metadata, confirmed public domain, license granted, link only, restricted, or unknown.

These values are not interchangeable. A verified record may have unknown temporal status and unknown reuse rights.

## Context and relationships

Optional fields include issuer, territorial scope, subject matter, language, dates, jurisdiction, official identifier, and `related_identifiers`. Relations may connect amendments, repeals, consolidations, implementing measures, cases, treaty instruments, or source catalogue IDs. Record the identifier scheme and value; add a relation when known.

## Provenance and reuse

`provenance` describes the evidence source and collection method. `reuse_rights` describes permission for the project’s proposed publication. A source URL is not a license. See `DATA-LICENSE.md`.

## Example

`records/examples/illustrative-record.json` is intentionally fictitious and contains no real legal text.


## Legal relationship graph

`python scripts/catalog.py graph --format json` builds a deterministic graph from `related_identifiers` and any explicit `versioning.version_of` links. Use `--format dot` to produce Graphviz DOT. Edges carry the asserting record, source URL and verification label. Inverse pairs such as `amended_by`/`amends` are normalized to a consistent action direction and duplicate reciprocal assertions are combined while retaining both evidence references. Ambiguous or unrepresented targets appear as dashed/external nodes with `resolved: false`; they are not silently discarded or treated as verified documents. The graph represents catalogued assertions and coverage only; it does not infer legal effects, validity or current force.
