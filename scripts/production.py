"""Production WSGI application, operational middleware, and controlled errors."""
from __future__ import annotations

import json
import html
import ipaddress
from urllib.parse import urlsplit
import logging
import os
import threading
import time
from urllib.parse import quote
import uuid
from collections import OrderedDict
from pathlib import Path
from urllib.parse import parse_qs

from api import API_PREFIX, WEB, dispatch

LOGGER = logging.getLogger("angola_legal.http")
MAX_QUERY_STRING = 2048
MAX_PATH_INFO = 512
MAX_RATE_CLIENTS = 10000


class TokenBucketLimiter:
    """Bounded, process-local token bucket limiter keyed by remote address."""
    def __init__(self, rate=60, window=60, capacity=120, max_clients=MAX_RATE_CLIENTS):
        self.rate = rate
        self.window = window
        self.capacity = capacity
        self.max_clients = max_clients
        self._buckets = OrderedDict()
        self._lock = threading.Lock()

    def allow(self, key, now=None):
        now = time.monotonic() if now is None else now
        with self._lock:
            if self.rate > 0:
                full_refill_seconds = self.window * self.capacity / self.rate
                expiry = now - full_refill_seconds
                while self._buckets:
                    oldest_key, (_, updated) = next(iter(self._buckets.items()))
                    if updated > expiry:
                        break
                    self._buckets.pop(oldest_key)
            tokens, updated = self._buckets.pop(key, (float(self.capacity), now))
            tokens = min(float(self.capacity), tokens + (now - updated) * self.rate / self.window)
            if tokens < 1:
                self._buckets[key] = (tokens, now)
                return False
            self._buckets[key] = (tokens - 1, now)
            while len(self._buckets) > self.max_clients:
                self._buckets.popitem(last=False)
            return True


def _bounded_int(env, name, default, minimum, maximum):
    try:
        value = int(env.get(name, str(default)))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return value


LIMITER = TokenBucketLimiter(
    rate=_bounded_int(os.environ, "ANGOLA_RATE_LIMIT_PER_MINUTE", 60, 1, 60000),
    window=60,
    capacity=_bounded_int(os.environ, "ANGOLA_RATE_LIMIT_BURST", 120, 1, 100000),
)


class ApiError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _error(status, message, request_id):
    return status, {"error": {"code": str(status), "message": message}, "request_id": request_id}


def _validate_query(raw, request_id):
    if len(raw) > MAX_QUERY_STRING:
        raise ApiError(414, "Query string is too long.")
    try:
        params = parse_qs(raw, keep_blank_values=True, strict_parsing=False, max_num_fields=24)
    except ValueError:
        raise ApiError(400, "Invalid query parameters.")
    if any(len(values) != 1 for values in params.values()):
        raise ApiError(400, "Repeated query parameters are not supported.")
    if any(len(values[0]) > 200 for values in params.values()):
        raise ApiError(400, "A query parameter exceeds the allowed length.")
    return params


def _route(environ, request_id):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")
    if len(path) > MAX_PATH_INFO:
        raise ApiError(414, "Path is too long.")
    if method not in ("GET", "HEAD"):
        raise ApiError(405, "This service is read-only.")
    if path == "/robots.txt":
        origin = os.getenv("ANGOLA_PUBLIC_BASE_URL", "").rstrip("/")
        text = "User-agent: *\nAllow: /\n" + (f"Sitemap: {origin}/sitemap.xml\n" if origin.startswith("https://") else "")
        return 200, text.encode("utf-8"), "text/plain; charset=utf-8", "public, max-age=300"
    if path == "/sitemap.xml":
        origin = os.getenv("ANGOLA_PUBLIC_BASE_URL", "").rstrip("/")
        parsed_origin = urlsplit(origin)
        if parsed_origin.scheme != "https" or not parsed_origin.hostname or parsed_origin.username or parsed_origin.password or parsed_origin.query or parsed_origin.fragment:
            raise ApiError(404, "Resource not found.")
        from api import load_records
        urls = [origin + "/", *[origin + "/documents/" + quote(r["record_id"], safe="") for r in load_records()]]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{html.escape(u)}</loc></url>" for u in urls) + "</urlset>"
        return 200, xml.encode("utf-8"), "application/xml; charset=utf-8", "public, max-age=300"
    if path.startswith("/documents/"):
        from api import load_records
        record_id = path[len("/documents/"):]
        record = next((item for item in load_records() if item.get("record_id") == record_id), None)
        if record is None:
            raise ApiError(404, "Resource not found.")
        title = html.escape(str(record.get("title") or "Documento jurídico"))
        description = html.escape(str(record.get("official_identifier") or "Metadados jurídicos com fonte e estado de verificação."))
        origin = os.getenv("ANGOLA_PUBLIC_BASE_URL", "").rstrip("/")
        canonical = f'<link rel="canonical" href="{html.escape(origin + path, quote=True)}">' if origin.startswith("https://") else ""
        try:
            payload = (WEB / "index.html").read_text(encoding="utf-8")
        except OSError:
            raise ApiError(404, "Resource not found.")
        payload = payload.replace("<title>Angola Legal — pesquisa jurídica de Angola</title>",
                                  f"<title>{title} — Angola Legal</title>")
        payload = payload.replace('name="description" content="Pesquise metadados jurídicos angolanos com fontes, proveniência e estado de verificação."',
                                  f'name="description" content="{description}"')
        payload = payload.replace('property="og:title" content="Angola Legal — conhecimento jurídico rastreável"',
                                  f'property="og:title" content="{title}"')
        if origin.startswith("https://"):
            canonical_tag = f'<link rel="canonical" href="{html.escape(origin + path, quote=True)}">'
            payload = payload.replace('  <link rel="stylesheet" href="/styles.css">', f'  {canonical_tag}\\n  <link rel="stylesheet" href="/styles.css">')
        marker = '<section class="section" id="document-view" hidden aria-labelledby="document-title"><a href="#pesquisa" id="back-search">← Voltar à pesquisa</a><div id="document-content"></div></section>'
        summary = f'<section class="section" id="document-view" aria-labelledby="document-title"><a href="/" id="back-search">← Voltar à pesquisa</a><div id="document-content"><p class="eyebrow">ANGOLA LEGAL · REGISTRO DOCUMENTAL</p><h1 id="document-title">{title}</h1><p>{description}</p><p>Verificação: {html.escape(str(record.get("verification_status") or "desconhecida"))} · estado temporal: {html.escape(str(record.get("temporal_status") or "desconhecido"))}</p><p>Projeto informativo; consulte a fonte e confirme a situação jurídica atual.</p></div></section>'
        payload = payload.replace(marker, summary)
        payload = payload.replace('<section class="section" id="grafo" hidden>', '<section class="section" id="grafo">')
        return 200, payload.encode("utf-8"), "text/html; charset=utf-8", "public, max-age=300"
    if path in ("/", "/app.js", "/styles.css"):
        file_name = {"/": "index.html", "/app.js": "app.js", "/styles.css": "styles.css"}[path]
        file_path = WEB / file_name
        try:
            payload = file_path.read_bytes()
        except OSError:
            raise ApiError(404, "Resource not found.")
        mime = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".txt": "text/plain; charset=utf-8",
                ".xml": "application/xml; charset=utf-8"}[file_path.suffix]
        return 200, payload, mime, "public, max-age=300"
    if path in ("/health/live", "/health/ready"):
        if path.endswith("ready"):
            try:
                from api import load_coverage, load_records, load_sources
                records = load_records()
                coverage = load_coverage()
                sources = load_sources()
                if (not isinstance(records, list) or not records
                        or any(not isinstance(record, dict)
                               or not record.get("record_id")
                               or not record.get("title") for record in records)
                        or not isinstance(coverage, dict)
                        or not isinstance(coverage.get("target_counts"), dict)
                        or not isinstance(sources, dict)
                        or not isinstance(sources.get("sources"), list)):
                    raise ValueError("Core catalogue data has an invalid shape.")
            except (OSError, ValueError, TypeError, KeyError):
                raise ApiError(503, "Service is not ready.")
        return 200, _json_bytes({"status": "ok", "request_id": request_id}), "application/json; charset=utf-8", "no-store"
    if not path.startswith(API_PREFIX + "/"):
        raise ApiError(404, "Resource not found.")
    params = _validate_query(query, request_id)
    allowed = {
        API_PREFIX + "/health": set(),
        API_PREFIX + "/search": {"q", "nature", "institution", "legal_force", "temporal_status",
                                 "verification_status", "subject", "date_from", "date_to", "limit", "offset"},
        API_PREFIX + "/facets": set(),
        API_PREFIX + "/sources": set(),
        API_PREFIX + "/coverage": set(),
        API_PREFIX + "/graph": {"record_id", "depth"},
    }
    if path.startswith(API_PREFIX + "/documents/"):
        allowed_params = set()
    else:
        allowed_params = allowed.get(path)
    if allowed_params is None:
        raise ApiError(404, "Resource not found.")
    if set(params) - allowed_params:
        raise ApiError(400, "Unsupported query parameter.")
    status, _, body = dispatch(path + (("?" + query) if query else ""))
    if status >= 400:
        msg = body.get("error", "Request failed.")
        if status == 400 and path == API_PREFIX + "/search":
            raise ApiError(400, msg)
        raise ApiError(status, msg)
    return status, _json_bytes(body), "application/json; charset=utf-8", "no-store"


def application(environ, start_response):
    request_id = uuid.uuid4().hex
    started = time.monotonic()
    remote = environ.get("REMOTE_ADDR", "unknown")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    route = environ.get("PATH_INFO", "/")
    try:
        if not route.startswith("/health/") and not LIMITER.allow(remote):
            status, body = _error(429, "Request rate limit exceeded.", request_id)
            payload, content_type, cache_control = _json_bytes(body), "application/json; charset=utf-8", "no-store"
            status_line = "429 Too Many Requests"
        else:
            code, payload, content_type, cache_control = _route(environ, request_id)
            status_line = {200: "200 OK", 400: "400 Bad Request", 404: "404 Not Found", 405: "405 Method Not Allowed", 414: "414 URI Too Long", 429: "429 Too Many Requests", 503: "503 Service Unavailable"}.get(code, "500 Internal Server Error")
    except ApiError as exc:
        status_line = {400: "400 Bad Request", 404: "404 Not Found", 405: "405 Method Not Allowed",
                       414: "414 URI Too Long", 429: "429 Too Many Requests",
                       503: "503 Service Unavailable"}.get(exc.status, "400 Bad Request")
        _, body = _error(exc.status, exc.message, request_id)
        payload, content_type, cache_control = _json_bytes(body), "application/json; charset=utf-8", "no-store"
    except Exception as exc:
        LOGGER.error(json.dumps({"event": "request_error", "request_id": request_id,
                                 "error_type": type(exc).__name__}, separators=(",", ":")))
        status_line = "500 Internal Server Error"
        _, body = _error(500, "An internal error occurred.", request_id)
        payload, content_type, cache_control = _json_bytes(body), "application/json; charset=utf-8", "no-store"

    elapsed = round((time.monotonic() - started) * 1000, 2)
    LOGGER.info(json.dumps({"event": "http_request", "request_id": request_id, "method": method,
                            "path": route, "status": int(status_line.split()[0]),
                            "duration_ms": elapsed}, separators=(",", ":")))
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(payload))),
        ("Cache-Control", cache_control),
        ("X-Request-ID", request_id),
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
        ("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"),
        ("Cross-Origin-Resource-Policy", "same-origin"),
        ("Vary", "Accept-Encoding"),
    ]
    if status_line.startswith("405"):
        headers.append(("Allow", "GET, HEAD"))
    start_response(status_line, headers)
    return [b"" if method == "HEAD" else payload]


def waitress_options(env=None):
    """Build validated Waitress settings; proxy trust is exact-IP and opt-in."""
    env = os.environ if env is None else env
    options = {
        "host": env.get("ANGOLA_HOST", "127.0.0.1"),
        "port": _bounded_int(env, "ANGOLA_PORT", 8000, 1, 65535),
        "threads": _bounded_int(env, "ANGOLA_THREADS", 8, 1, 64),
        "connection_limit": _bounded_int(env, "ANGOLA_CONNECTION_LIMIT", 128, 1, 4096),
        "channel_timeout": _bounded_int(env, "ANGOLA_CHANNEL_TIMEOUT", 30, 1, 300),
        "max_request_header_size": 8192,
        "max_request_body_size": 0,
        "expose_tracebacks": False,
        "ident": "AngolaLegal",
    }
    trusted_proxy = env.get("ANGOLA_TRUSTED_PROXY", "").strip()
    if trusted_proxy:
        try:
            trusted_proxy = str(ipaddress.ip_address(trusted_proxy))
        except ValueError as exc:
            raise ValueError("ANGOLA_TRUSTED_PROXY must contain one exact IPv4 or IPv6 address.") from exc
        options.update(
            trusted_proxy=trusted_proxy,
            trusted_proxy_headers={"x-forwarded-for", "x-forwarded-proto"},
            clear_untrusted_proxy_headers=True,
        )
    return options


def main():
    from waitress import serve
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    serve(application, **waitress_options())
