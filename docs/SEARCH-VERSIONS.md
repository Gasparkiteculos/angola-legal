# Search, versions and change checks | Pesquisa, versões e alterações

## Search and version reporting
Run `python scripts/catalog.py search "labour"` for case-insensitive search across JSON metadata, or `python scripts/catalog.py versions` to list version and monitoring fields. These local commands make no network requests and do not search full legal texts.

## Version identity and change checks
`record_id` identifies a catalogue record; `versioning.version_label` identifies the represented publication/version. Use `version_of` when the parent record is catalogued. Preserve the formal instrument and Gazette issue in `official_identifier`; record legal relations in `related_identifiers` with evidence. A republication is not automatically a new enactment or consolidated current text.

Run `python scripts/catalog.py diff OLD.json NEW.json` to compare metadata snapshots. A differing `source_sha256` indicates different bytes only when a collector lawfully accessed both artifacts and explicitly recorded their hashes. It does not prove a legal amendment. Website timestamps and unchanged files do not establish legal currentness.

## Collection, provenance and safeguards
1. Treat search hits as discovery leads until institutional identity and the document itself are checked.
2. Prefer Gazette facsimiles and issuing-institution repositories. Verify title, number, series/issue, date and operative relationship from the official item; describe exactly what was inspected.
3. Keep publication, commencement, force, temporal status, verification and reuse rights separate. Leave uncertain values unknown.
4. Store metadata and official links only unless reuse rights permit more. Respect site terms, access controls, rate limits, privacy and security restrictions.
5. Deduplicate by jurisdiction plus formal instrument identifier, corroborated by Gazette series/issue/date. Do not merge distinct versions, republications or corrigenda.
6. For comparison, hash only lawfully accessed artifacts; store digest and check date, and do not retain copies unless permitted. A changed file is not itself a legal change.

Automated metadata checks do not determine legal status. Human review remains necessary; this catalogue is not legal advice.


## Legal relationship graph
Run `python scripts/catalog.py graph --format json` for a machine-readable graph or `python scripts/catalog.py graph --format dot` for Graphviz DOT. Edges retain the record making the assertion, its evidence URL and verification label. Reciprocal `amends`/`amended_by` declarations are normalized and merged without discarding evidence. A reference that does not resolve uniquely to a catalogue record is emitted as an unresolved external node. This is a graph of recorded metadata and evidence, not a legal opinion or an exhaustive statement of the law.


## Integrity report
Run `python scripts/catalog.py check-graph` to review counts, errors and warnings before publishing a graph. Invalid relation labels, self-references, duplicate assertions and missing provenance fail the check; unresolved or ambiguous targets are warnings with explicit nodes. Unit tests for direct/inverse edges, ambiguous/unresolved targets, duplicates, invalid labels, self-references and provenance run through the existing unittest workflow.
