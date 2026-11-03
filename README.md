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

## Repository status | Estado do repositório

Version **0.10.0** adds a production deployment profile for a small Linux VPS using Docker Compose, Caddy-managed HTTPS, a private application network, persistent TLS state, and an exact trusted-proxy address. The API remains read-only. CI validates metadata and source data, runs tests and dependency auditing, builds and smoke-tests the application image, and validates the production Compose and Caddy configuration.

The project is **prepared for deployment but is not hosted publicly**. Hosting, a verified domain, DNS records, provider firewall rules, monitoring alerts, and production credentials still require owner configuration. This release does not certify current legal status or catalogue completeness.

O projeto está preparado para deployment, mas ainda não está publicado na Internet. O hosting, um domínio verificado, DNS, regras de firewall, alertas de monitorização e credenciais de produção dependem de configuração pelo titular.

The repository does **not** claim a complete or current consolidated corpus of Angolan legal materials. Legal-document verification records the evidence checked; temporal status remains separate and may be unknown. The earlier illustrative sample is fictional, not a real legal instrument.

## Licensing | Licenciamento

- **Source code:** MIT License.
- **Documents and datasets:** governed separately by `DATA-LICENSE.md`. Third-party materials retain their own copyright, access and reuse conditions. A link or metadata record does not imply permission to redistribute the underlying document.

## Getting started | Primeiros passos

- `docs/SOURCE-DISCOVERY.md` — verification, reliability, collection workflow and safeguards;
- `sources/source-registry.json` and `schemas/source-registry.schema.json` — source inventory and schema;
- `docs/RECORD-CATALOG.md` and `records/angola/` — catalogue, provenance and document records;
- `coverage/catalogue-coverage.json`, `schemas/catalogue-coverage.schema.json` and `docs/COVERAGE-AND-API-READINESS.md` — scoped coverage and API/UI data contract;
- `scripts/api.py`, `scripts/production.py` and `web/` — read-only JSON API and browser interface;
- `docs/DEPLOYMENT.md`, `docs/PUBLIC-API.md`, `deploy/`, `docker-compose.production.yml` and `Dockerfile` — deployment, API, container and proxy reference;
- `docs/HOSTING-DECISION.md` — hosting selection, dated cost estimate and contingency;
- `docs/SEARCH-VERSIONS.md`, `docs/DATA-MODEL.md` and `scripts/catalog.py` — graph, local metadata search, version reporting and snapshot comparison;
- `docs/SPECIFICATION.md`, `docs/LEGAL-TAXONOMY.md`, `docs/DATA-MODEL.md`;
- `docs/EDITORIAL-POLICY.md`, `docs/ARCHITECTURE.md`, `CONTRIBUTING.md`, `DATA-LICENSE.md`.

### Validate records and sources

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_metadata.py records/examples/illustrative-record.json records/angola/*.json
python scripts/validate_sources.py
python -m unittest discover -s tests
python scripts/catalog.py check-graph
python scripts/catalog.py coverage
python scripts/api.py
# open http://127.0.0.1:8000
# local container: docker compose up --build
```

For production deployment, follow `docs/DEPLOYMENT.md`. Do not put credentials, private keys, or production environment files in Git. A custom domain must be owned and verified before setting its DNS or public base URL.

## Contributing | Contribuir

Contributions are welcome: source discovery, metadata, legal taxonomy, validation, documentation, translations and code. Please read `CONTRIBUTING.md`, the editorial policy and source discovery guidance before contributing.

## Disclaimer | Aviso

Angola Legal is an information and research project, not a legal authority and not a substitute for advice from a qualified legal professional. Always consult authoritative sources and verify the current legal status before relying on a document.

---

**Project:** Angola Legal  
**Repository:** https://github.com/Gasparkiteculos/angola-legal
