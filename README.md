# Angola Legal

**Acesso aberto, organizado e rastreável ao conhecimento jurídico de Angola.**  
**Open, structured, and traceable access to Angolan legal knowledge.**

Angola Legal is an open-source initiative to build a comprehensive, searchable and verifiable repository of legal materials related to Angola. Its scope goes beyond legislation and includes jurisprudence, administrative and regulatory acts, international instruments, legislative history, doctrine, research and practical legal documentation.

O Angola Legal é uma iniciativa open source para construir um repositório abrangente, pesquisável e verificável de materiais jurídicos relacionados com Angola. O âmbito vai além da legislação e inclui jurisprudência, atos administrativos e regulatórios, instrumentos internacionais, processo legislativo, doutrina, investigação e documentação jurídica prática.

## Scope | Âmbito

The project may catalogue, subject to provenance, access, privacy and reuse-rights checks:

- Constitution and constitutional instruments;
- Laws, codes, statutes, decrees, regulations and administrative acts;
- Sectoral regulatory instruments and technical standards;
- Court decisions and other publishable jurisprudence;
- Treaties, conventions and international instruments;
- Legislative proposals, reports, opinions, debates and preparatory works;
- Public procurement, public administration and publishable contracts;
- Collective agreements, professional statutes and codes of conduct;
- Legal doctrine, academic research, theses and reports;
- Forms, manuals, guides, fee schedules and practical materials;
- Historical versions, amendments, corrigenda, repeals and consolidated texts.

A taxonomia é aberta: a inclusão não depende de o documento ser uma lei, mas da sua relevância jurídica e da possibilidade legítima de o catalogar.

## Core principles | Princípios

1. **Source provenance:** record where each item came from and when it was collected.
2. **No false certainty:** distinguish verified facts from inferred, pending or unknown information.
3. **Separate dimensions:** document type, legal force, temporal status, verification status and reuse rights are independent fields.
4. **Respect rights and privacy:** public availability does not automatically grant redistribution rights.
5. **Traceability:** preserve identifiers, versions, relationships and change history.
6. **Bilingual documentation:** project documentation is maintained in Portuguese and English.
7. **No completeness claims without evidence:** coverage must be measured and qualified.

## Repository status | Estado do repositório

Version **0.4.0** adds verified metadata records for the Constitution republication identified by the Assembleia Nacional digital library and Lei n.º 12/23 (General Labour Law), alongside the initial Penal Code instruments. Local tools search metadata, list version links and compare snapshots. They do not fetch source documents or establish current legal status; the repository stores links and metadata only.

The repository does **not** claim a complete or current consolidated corpus of Angolan legal materials. Legal-document verification records the evidence checked; temporal status remains separate and may be unknown. The earlier illustrative sample is fictional, not a real legal instrument.

## Licensing | Licenciamento

- **Source code:** MIT License.
- **Documents and datasets:** governed separately by `DATA-LICENSE.md`. Third-party materials retain their own copyright, access and reuse conditions. A link or metadata record does not imply permission to redistribute the underlying document.

## Getting started | Primeiros passos

- `docs/SOURCE-DISCOVERY.md` — verification, reliability, collection workflow and safeguards;
- `sources/source-registry.json` and `schemas/source-registry.schema.json` — source inventory and schema;
- `docs/RECORD-CATALOG.md` and `records/angola/` — catalogue, provenance and document records;
- `docs/SEARCH-VERSIONS.md` and `scripts/catalog.py` — local metadata search, version reporting and snapshot comparison;
- `docs/SPECIFICATION.md`, `docs/LEGAL-TAXONOMY.md`, `docs/DATA-MODEL.md`;
- `docs/EDITORIAL-POLICY.md`, `docs/ARCHITECTURE.md`, `CONTRIBUTING.md`, `DATA-LICENSE.md`.

### Validate records and sources

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_metadata.py records/examples/illustrative-record.json records/angola/*.json
python scripts/validate_sources.py
python -m unittest discover -s tests
```

## Contributing | Contribuir

Contributions are welcome: source discovery, metadata, legal taxonomy, validation, documentation, translations and code. Please read `CONTRIBUTING.md`, the editorial policy and source discovery guidance before contributing.

## Disclaimer | Aviso

Angola Legal is an information and research project, not a legal authority and not a substitute for advice from a qualified legal professional. Always consult authoritative sources and verify the current legal status before relying on a document.

---

**Project:** Angola Legal  
**Repository:** https://github.com/Gasparkiteculos/angola-legal
