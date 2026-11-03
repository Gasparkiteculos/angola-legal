"""Socket-level tests for Waitress proxy trust and client identity."""
import http.client
import socket
import sys
import threading
import time
import unittest
from pathlib import Path
from waitress import create_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import production


class RecordingLimiter:
    def __init__(self):
        self.clients = []

    def allow(self, address):
        self.clients.append(address)
        return True


class WaitressProxyIntegrationTests(unittest.TestCase):
    def test_without_proxy_trust_uses_direct_socket_peer(self):
        observations = []

        def capture(environ, start_response):
            observations.append((
                environ.get("REMOTE_ADDR"),
                environ.get("wsgi.url_scheme"),
                environ.get("HTTP_X_FORWARDED_FOR"),
            ))
            return production.application(environ, start_response)

        old_limiter = production.LIMITER
        limiter = RecordingLimiter()
        production.LIMITER = limiter
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = create_server(capture, host="127.0.0.1", port=port, threads=2)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 5
            while True:
                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                    conn.request("GET", "/api/v1/health", headers={
                        "X-Forwarded-For": "203.0.113.10",
                        "X-Forwarded-Proto": "https",
                    })
                    response = conn.getresponse()
                    response.read()
                    conn.close()
                    self.assertEqual(200, response.status)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
            self.assertEqual("127.0.0.1", observations[-1][0])
            self.assertEqual("127.0.0.1", limiter.clients[-1])
        finally:
            server.close()
            thread.join(timeout=3)
            production.LIMITER = old_limiter

    @unittest.skipUnless(socket.has_ipv6, "IPv6 sockets are unavailable")
    def test_ipv6_trusted_proxy_peer_and_forwarded_client(self):
        observations = []

        def capture(environ, start_response):
            observations.append((environ.get("REMOTE_ADDR"), environ.get("wsgi.url_scheme")))
            return production.application(environ, start_response)

        try:
            with socket.socket(socket.AF_INET6) as probe:
                probe.bind(("::1", 0))
                port = probe.getsockname()[1]
        except OSError:
            self.skipTest("IPv6 loopback is unavailable")
        old_limiter = production.LIMITER
        production.LIMITER = RecordingLimiter()
        server = create_server(
            capture, host="::1", port=port, threads=2, ipv6=True,
            trusted_proxy="::1",
            trusted_proxy_headers={"x-forwarded-for", "x-forwarded-proto"},
            clear_untrusted_proxy_headers=True,
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 5
            while True:
                try:
                    conn = http.client.HTTPConnection(
                        "::1", port, timeout=1, source_address=("::1", 0)
                    )
                    conn.request("GET", "/api/v1/health", headers={
                        "X-Forwarded-For": "2001:db8::25",
                        "X-Forwarded-Proto": "https",
                    })
                    response = conn.getresponse()
                    response.read()
                    conn.close()
                    self.assertEqual(200, response.status)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
            self.assertEqual(("2001:db8::25", "https"), observations[-1])
        finally:
            server.close()
            thread.join(timeout=3)
            production.LIMITER = old_limiter

    def test_trusted_and_untrusted_forwarded_headers_and_rate_limit_identity(self):
        observations = []

        def capture(environ, start_response):
            observations.append((
                environ.get("REMOTE_ADDR"),
                environ.get("wsgi.url_scheme"),
                environ.get("HTTP_X_FORWARDED_FOR"),
            ))
            return production.application(environ, start_response)

        old_limiter = production.LIMITER
        limiter = RecordingLimiter()
        production.LIMITER = limiter
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = create_server(
            capture,
            host="127.0.0.1",
            port=port,
            threads=2,
            trusted_proxy="127.0.0.1",
            trusted_proxy_headers={"x-forwarded-for", "x-forwarded-proto"},
            clear_untrusted_proxy_headers=True,
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 5
            while True:
                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                    conn.request("GET", "/api/v1/health", headers={
                        "X-Forwarded-For": "198.51.100.25",
                        "X-Forwarded-Proto": "https",
                    })
                    response = conn.getresponse()
                    response.read()
                    conn.close()
                    self.assertEqual(200, response.status)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)

            self.assertEqual(("198.51.100.25", "https", "198.51.100.25"), observations[-1])
            self.assertEqual("198.51.100.25", limiter.clients[-1])

            conn = http.client.HTTPConnection(
                "127.0.0.1", port, timeout=2, source_address=("127.0.0.2", 0)
            )
            conn.request("GET", "/api/v1/health", headers={
                "X-Forwarded-For": "203.0.113.77",
                "X-Forwarded-Proto": "https",
            })
            response = conn.getresponse()
            response.read()
            conn.close()
            self.assertEqual(200, response.status)
            self.assertEqual(("127.0.0.2", "http", None), observations[-1])
            self.assertEqual("127.0.0.2", limiter.clients[-1])
        finally:
            server.close()
            thread.join(timeout=3)
            production.LIMITER = old_limiter


if __name__ == "__main__":
    unittest.main()
