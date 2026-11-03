"""Integration and security-boundary tests for the production WSGI app."""
import io
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import production


def request(path, method="GET", remote="192.0.2.1"):
    environ = {
        "REQUEST_METHOD": method, "PATH_INFO": path.split("?", 1)[0],
        "QUERY_STRING": path.partition("?")[2], "REMOTE_ADDR": remote,
        "wsgi.input": io.BytesIO(b""), "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost", "SERVER_PORT": "8000",
    }
    captured = {}
    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)
    body = b"".join(production.application(environ, start_response))
    captured["body"] = body
    return captured


class ProductionWsgiTests(unittest.TestCase):
    def setUp(self):
        self.old_limiter = production.LIMITER
        production.LIMITER = production.TokenBucketLimiter(rate=60, capacity=10)

    def tearDown(self):
        production.LIMITER = self.old_limiter

    def test_health_checks_and_security_headers(self):
        live = request("/health/live")
        ready = request("/health/ready")
        self.assertEqual("200 OK", live["status"])
        self.assertEqual("200 OK", ready["status"])
        self.assertIn("X-Request-ID", live["headers"])
        self.assertIn("Content-Security-Policy", live["headers"])
        self.assertEqual("nosniff", live["headers"]["X-Content-Type-Options"])
        self.assertEqual("no-store", live["headers"]["Cache-Control"])

    def test_errors_have_uniform_json_and_do_not_expose_exception_details(self):
        not_found = request("/missing")
        self.assertEqual("404 Error", not_found["status"])
        payload = json.loads(not_found["body"])
        self.assertEqual("Resource not found.", payload["error"]["message"])
        self.assertIn("request_id", payload)
        method = request("/api/v1/health", method="POST")
        self.assertEqual("405 Method Not Allowed", method["status"])
        self.assertEqual("GET, HEAD", method["headers"]["Allow"])

    def test_repeated_and_unknown_parameters_are_rejected(self):
        repeated = request("/api/v1/search?q=law&q=code")
        unknown = request("/api/v1/search?unexpected=x")
        long = request("/api/v1/search?q=" + "x" * 201)
        self.assertEqual("400 Bad Request", repeated["status"])
        self.assertEqual("400 Bad Request", unknown["status"])
        self.assertEqual("400 Bad Request", long["status"])

    def test_rate_limit_returns_429_and_health_is_exempt(self):
        production.LIMITER = production.TokenBucketLimiter(rate=0, capacity=1)
        first = request("/api/v1/facets", remote="198.51.100.9")
        limited = request("/api/v1/facets", remote="198.51.100.9")
        health = request("/health/live", remote="198.51.100.9")
        self.assertEqual("200 OK", first["status"])
        self.assertEqual("429 Too Many Requests", limited["status"])
        self.assertEqual("200 OK", health["status"])

    def test_head_static_and_live_catalogue_search(self):
        head = request("/", method="HEAD")
        self.assertEqual("200 OK", head["status"])
        self.assertEqual(b"", head["body"])
        search = request("/api/v1/search?q=Lei")
        self.assertEqual("200 OK", search["status"])
        self.assertGreater(json.loads(search["body"])["total"], 0)

    def test_routes_cover_search_facets_sources_document_graph_and_coverage(self):
        paths = ["/api/v1/health", "/api/v1/search", "/api/v1/facets",
                 "/api/v1/sources", "/api/v1/coverage", "/api/v1/graph",
                 "/api/v1/documents/al:ao:lei-18-21-2021"]
        for path in paths:
            response = request(path)
            self.assertEqual("200 OK", response["status"], path)
            self.assertTrue(response["body"], path)

    def test_sitemap_is_disabled_without_verified_public_origin_and_built_when_set(self):
        with patch.dict("os.environ", {"ANGOLA_PUBLIC_BASE_URL": ""}):
            self.assertEqual("404 Error", request("/sitemap.xml")["status"])
        with patch.dict("os.environ", {"ANGOLA_PUBLIC_BASE_URL": "https://legal.example"}):
            sitemap = request("/sitemap.xml")
            robots = request("/robots.txt")
        self.assertEqual("200 OK", sitemap["status"])
        self.assertIn(b"https://legal.example/documents/al%3Aao%3Alei-18-21-2021", sitemap["body"])
        self.assertIn(b"Sitemap: https://legal.example/sitemap.xml", robots["body"])

    def test_document_page_is_server_rendered_and_escaped(self):
        page = request("/documents/al:ao:lei-18-21-2021")
        self.assertEqual("200 OK", page["status"])
        self.assertIn(b"<title>Lei n.", page["body"])
        missing = request("/documents/not-found")
        self.assertEqual("404 Error", missing["status"])

    def test_limiter_storage_is_bounded(self):
        limiter = production.TokenBucketLimiter(rate=60, capacity=5, max_clients=3)
        for index in range(10):
            limiter.allow(str(index), now=1.0)
        self.assertLessEqual(len(limiter._buckets), 3)


if __name__ == "__main__":
    unittest.main()
