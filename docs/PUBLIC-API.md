# Public API v1 | API pública v1

Base path: `/api/v1`. API exclusivamente de leitura. Todos os endpoints são GET; HEAD é suportado para assets web. Não há endpoints de escrita, upload, proxy ou texto integral das fontes. Respostas preservam proveniência, direitos, verificação, estado temporal e referências não resolvidas.

- `GET /api/v1/health` — compatibilidade.
- `GET /api/v1/search` — `q`, `nature`, `institution`, `subject`, `date_from`, `date_to`, `legal_force`, `temporal_status`, `verification_status`, `limit` (1–100) e `offset` (>=0).
- `GET /api/v1/facets` — valores de filtros atuais.
- `GET /api/v1/sources` — inventário ao nível da fonte.
- `GET /api/v1/documents/{record_id}` — registro completo de metadados.
- `GET /api/v1/graph` — grafo inteiro ou vizinhança através de `record_id` e `depth` (0–3).
- `GET /api/v1/coverage` — cobertura delimitada e respetivos estados.
- Health operacional: `GET /health/live`, `GET /health/ready`.

Erros usam JSON com `error.code`, `error.message` e `request_id`; o mesmo identificador segue no header `X-Request-ID`. Parâmetros desconhecidos, repetidos ou inválidos são rejeitados. Limites de URL e rate limiting são aplicados na camada WSGI/Waitress.

```sh
curl 'http://127.0.0.1:8000/api/v1/search?q=Lei&verification_status=verified&limit=10&offset=0'
```

A API é independente da interface. Não certifica vigência atual, completude do catálogo ou aconselhamento jurídico.
