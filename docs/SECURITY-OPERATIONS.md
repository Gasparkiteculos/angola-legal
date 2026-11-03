# Security operations | Operações de segurança

- Keep application ports private; TLS belongs at a maintained reverse proxy/load balancer.
- Never commit secrets, private keys, production .env files, logs with personal data, or legal-source files without rights review.
- Waitress proxy trust is opt-in and exact-IP only. The proxy must overwrite forwarded headers. Do not set a wildcard.
- Same-origin UI/API means CORS remains disabled. A separate client origin requires a reviewed allowlist.
- Rate limiting is bounded and process-local; use shared edge controls before horizontal scaling.
- Apply security updates and review advisories; CI runs pip-audit for runtime dependencies.
- App errors do not return tracebacks or filesystem paths. Request IDs link client errors to JSON logs; query strings and client IPs are excluded from app logs.
- Use /health/live and /health/ready for monitoring. Configure alerts and retention in the hosting environment.
- Catalogue/configuration backups are source-controlled; protect non-Git deployment secrets in the provider's secret manager. Test rollback and restore.
- Report vulnerabilities privately through GitHub Security Advisories where enabled; do not publish exploit details or sensitive data in public issues.

These controls reduce common risks but do not constitute a formal penetration test or a guarantee of service security.
