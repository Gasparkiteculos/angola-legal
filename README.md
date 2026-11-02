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

This repository contains the initial project specification, architecture, editorial policy, legal taxonomy, data model, JSON Schema, an illustrative sample record, a metadata validator and contribution guidance.

It does **not** claim to contain a complete or verified corpus of Angolan legal materials. The sample record is illustrative, not a real legal instrument.

## Licensing | Licenciamento

- **Source code:** MIT License.
- **Documents and datasets:** governed separately by `DATA-LICENSE.md`. Third-party materials retain their own copyright, access and reuse conditions. A link or metadata record does not imply permission to redistribute the underlying document.

## Getting started | Primeiros passos

See:

- `docs/SPECIFICATION.md` — initial technical specification;
- `docs/LEGAL-TAXONOMY.md` — broad legal-material taxonomy;
- `docs/DATA-MODEL.md` and `schemas/legal-document.schema.json` — record structure;
- `docs/EDITORIAL-POLICY.md` — verification and editorial rules;
- `docs/ARCHITECTURE.md` — proposed architecture;
- `CONTRIBUTING.md` — how to contribute;
- `DATA-LICENSE.md` — document and dataset rights.

### Validate the illustrative record

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_metadata.py records/examples/illustrative-record.json
```

## Contributing | Contribuir

Contributions are welcome: source discovery, metadata, legal taxonomy, validation, documentation, translations and code. Please read `CONTRIBUTING.md` and the editorial policy before submitting materials.

## Disclaimer | Aviso

Angola Legal is an information and research project, not a legal authority and not a substitute for advice from a qualified legal professional. Always consult authoritative sources and verify the current legal status before relying on a document.

---

**Project:** Angola Legal  
**Repository:** https://github.com/Gasparkiteculos/angola-legal
