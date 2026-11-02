"""Tests for the read-only JSON API."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import api


def sample(record_id, title, **fields):
    return {
        "record_id": record_id, "title": title, "official_identifier": title,
        "document_nature": "legislation", "issuing_authority": "Assembleia Nacional",
        "date_published": "2021-08-16", "legal_force": "binding",
        "temporal_status": "unknown", "verification_status": "verified",
        "subject_matter": ["constitutional law"],
        "source_url": "https://official.example/doc",
        **fields,
    }


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            sample("al:ao:one", "Lei n.º 18/21"),
            sample("al:ao:two", "Lei n.º 12/23", date_published="2023-12-27",
                   subject_matter=["labour law"]),
        ]

    def test_search_filters_and_paginates(self):
        status, _, body = api.dispatch(
            "/api/v1/search?q=lei&nature=legislation&limit=1",
            records=self.records, coverage={"targets": []})
        self.assertEqual(200, status)
        self.assertEqual(2, body["total"])
        self.assertEqual(1, len(body["results"]))
        status, _, body = api.dispatch(
            "/api/v1/search?subject=labour&date_from=2022-01-01",
            records=self.records, coverage={"targets": []})
        self.assertEqual(1, body["total"])
        self.assertEqual("al:ao:two", body["results"][0]["record_id"])

    def test_search_rejects_invalid_pagination(self):
        status, _, body = api.dispatch("/api/v1/search?limit=bad",
                                       records=self.records, coverage={"targets": []})
        self.assertEqual(400, status)
        self.assertIn("error", body)

    def test_search_rejects_out_of_range_pagination_and_invalid_dates(self):
        for query in ("/api/v1/search?limit=0", "/api/v1/search?offset=-1",
                      "/api/v1/search?date_from=not-a-date"):
            status, _, body = api.dispatch(query, records=self.records, coverage={"targets": []})
            self.assertEqual(400, status, query)
            self.assertIn("error", body)

    def test_document_endpoint_and_unknown_document(self):
        status, _, body = api.dispatch("/api/v1/documents/al:ao:one",
                                       records=self.records, coverage={"targets": []})
        self.assertEqual(200, status)
        self.assertEqual("al:ao:one", body["record_id"])
        status, _, body = api.dispatch("/api/v1/documents/nope",
                                       records=self.records, coverage={"targets": []})
        self.assertEqual(404, status)

    def test_graph_neighborhood_keeps_unresolved_nodes_and_provenance(self):
        records = [sample("al:ao:one", "Lei n.º 18/21", related_identifiers=[{
            "scheme": "law", "value": "Lei n.º 99/99", "relation": "amends"
        }])]
        status, _, body = api.dispatch("/api/v1/graph?record_id=al:ao:one&depth=1",
                                       records=records, coverage={"targets": []})
        self.assertEqual(200, status)
        self.assertEqual(2, len(body["nodes"]))
        self.assertEqual("unresolved_reference", next(
            node["verification_status"] for node in body["nodes"] if not node["resolved"]))
        self.assertTrue(body["edges"][0]["evidence"])

    def test_unknown_graph_focus_and_coverage_route(self):
        status, _, body = api.dispatch("/api/v1/graph?record_id=unknown",
                                       records=self.records, coverage={"targets": []})
        self.assertEqual(404, status)
        status, _, body = api.dispatch("/api/v1/coverage",
                                       records=self.records, coverage={"reviewed_on": "2026-11-03",
                                                                      "scope_note": "test", "targets": []})
        self.assertEqual(200, status)
        self.assertEqual("pass", body["status"])

    def test_facets_and_health_are_json(self):
        status, mime, body = api.dispatch("/api/v1/facets",
                                          records=self.records, coverage={"targets": []})
        self.assertEqual(200, status)
        self.assertEqual("application/json; charset=utf-8", mime)
        self.assertIn("document_nature", body["facets"])
        self.assertEqual("ok", api.dispatch("/api/v1/health", self.records, {})[2]["status"])


if __name__ == "__main__":
    unittest.main()
