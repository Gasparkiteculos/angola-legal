# Deployment and operations | Publicação e operação

## Scope

Este repositório contém uma configuração de referência preparada para deployment, mas não aloja um serviço público. Não foi escolhido nem verificado domínio, DNS ou certificado TLS. A porta da aplicação não deve ser exposta diretamente à Internet; o Compose liga-a apenas ao loopback do host.

## Run local container

Requirements: Docker Engine with Compose plugin.

```sh
cp .env.example .env
docker compose up --build -d
curl --fail http://127.0.0.1:8000/health/ready
```

O container corre como utilizador não privilegiado, sistema de ficheiros de leitura apenas, capabilities removidas e diretório temporário limitado. Desligar com `docker compose down`. O ficheiro `.env` está ignorado pelo Git; não guardar segredos no exemplo.

## Public deployment / Publicação pública

1. Selecionar e verificar domínio, titularidade, DNS e disponibilidade por meios externos. Não se presume que `angolalegal.ao` esteja disponível.
2. Configurar DNS e certificados TLS. Nunca guardar chaves privadas no Git.
3. Colocar proxy reverso atualizado ou load balancer HTTPS à frente da aplicação. `deploy/nginx.conf.example` é um modelo e contém placeholders.
4. Manter a porta da app numa rede privada. O modelo Nginx substitui `X-Forwarded-For` por `$remote_addr` e `X-Forwarded-Proto` por `https`; não use `$proxy_add_x_forwarded_for` com valores de cliente não verificados. Configure `ANGOLA_TRUSTED_PROXY` com um endereço IPv4 ou IPv6 exato do proxy que o Waitress observa. Compose transmite esse valor; vazio desativa a confiança. Nunca use wildcard.
5. Definir `ANGOLA_PUBLIC_BASE_URL` apenas com a origem HTTPS verificada. Sem ela, o sitemap responde 404 e robots.txt não anuncia sitemap.
6. Ajustar threads, limite de ligações e rate limit com base em métricas e limites de file descriptors. O rate limiter é local ao processo; réplicas horizontais precisam de limites partilhados no proxy.
7. Ativar firewall, atualizações, alertas, backups de configuração e rollback. Verificar HTTPS, redirects, headers, health checks, sitemap, logs e 429 após publicar.

## Nginx validation scope

CI checks the template textually for header replacement, redirect target, and rate-limit status. It does not run `nginx -t`, start Nginx, or test the complete Client → Nginx → Waitress path. The Waitress socket tests exercise Waitress proxy-header handling directly; they are not an Nginx integration test. After adapting the template to a real host, validate the complete Nginx configuration with `nginx -t` when Nginx is available, then verify the live proxy path before exposing the service.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| ANGOLA_HOST | 127.0.0.1 | Endereço de escuta; container usa 0.0.0.0 internamente. |
| ANGOLA_PORT | 8000 | Porta de escuta. |
| ANGOLA_THREADS | 8 | Threads Waitress. |
| ANGOLA_CONNECTION_LIMIT | 128 | Ligações ativas máximas. |
| ANGOLA_CHANNEL_TIMEOUT | 30 | Timeout de ligação inativa em segundos. |
| ANGOLA_RATE_LIMIT_PER_MINUTE | 60 | Reposição de tokens por IP e minuto (1–60 000). |
| ANGOLA_RATE_LIMIT_BURST | 120 | Burst máximo por IP (1–100 000). |
| ANGOLA_TRUSTED_PROXY | vazio | IP IPv4 ou IPv6 exato do proxy visto pelo Waitress; Compose passa o valor ao container. Vazio mantém confiança em proxy desativada. |
| ANGOLA_PUBLIC_BASE_URL | unset | Origem HTTPS verificada para sitemap. |

## Health, monitoring and recovery

- `/health/live`: liveness; `/health/ready`: confirma que registos, cobertura e inventário de fontes podem ser lidos e têm a estrutura principal esperada; não executa validação integral de schemas em cada pedido. `/api/v1/health` mantém compatibilidade.
- Logs JSON contêm request ID, método, caminho, estado e duração; não registam query string nem IP do cliente.
- Cada resposta contém `X-Request-ID`; incluir esse identificador em relatos de suporte.
- Monitorizar falhas de readiness, erros HTTP, 429, reinícios, recursos e expiração TLS. Não há vendor de monitorização integrado.
- O catálogo não usa base de dados nem recolhe conteúdo submetido. Reimplantar uma imagem validada e a configuração guardada é o procedimento de recuperação. Guardar segredos no cofre do provedor; testar rollback.
- Esta configuração é uma baseline operacional, não uma garantia de segurança ou disponibilidade.
