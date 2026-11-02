# Initial legal document catalogue | Catálogo jurídico inicial

## Coverage

The first catalogue records two real instruments from the Diário da República, I Série, that establish a directly verifiable amendment relationship:

- Lei n.º 38/20, approving the Angolan Penal Code, published in I Série n.º 179 on 11 November 2020.
- Lei n.º 12/24, amending Lei n.º 38/20, published in I Série n.º 126 on 4 July 2024.

Machine-readable records are in `records/angola/`. They contain metadata and links only; no Gazette text is copied into this repository.

## Evidence and verification

For Lei n.º 38/20, the Government of Angola legislation portal lists “Novo Código Penal Angolano” and links to a PDF facsimile whose masthead identifies the official gazette issue; the law text contains its repeal and commencement clauses. For Lei n.º 12/24, the Tribunal Supremo official portal hosts a Gazette facsimile that identifies the issue, date, amendment, repeal and commencement provisions.

The records store the issuing authority, instrument/publication identifiers, source URL, access date and provenance notes. The relation `amended_by` / `amends` is supported by the later law's title and operative provisions.

## Temporal status and limits

Publication and legal force are separate from present-day temporal status. Lei n.º 38/20 states that it enters into force 90 days after publication; the dataset does not calculate a normalized commencement date. Lei n.º 12/24 expressly enters into force on publication, recorded as 2024-07-04. The Penal Code is marked `amended` because the 2024 amending law is verified; Lei n.º 12/24 is marked `unknown` because a complete currentness audit has not been done. Neither status is legal advice or a guarantee that all later amendments, corrigenda or repeals have been found.

## Rights

The source facsimiles remain with their host institutions. The repository stores no facsimile, OCR or full legal text. Each record is marked `link_only` because no explicit redistribution licence was established for the source copy.
