"""Unit tests for legal relationship graph construction and integrity checks."""
import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import catalog

def record(record_id, identifier, relations=None, source_url=None):
    return {
        "record_id": record_id,
        "title": identifier,
        "official_identifier": identifier,
        "related_identifiers": relations or [],
        "verification_status": "verified",
        "temporal_status": "unknown",
        "source_url": source_url or f"https://official.example/{record_id}",
    }

class RelationshipGraphTests(unittest.TestCase):
    def test_direct_and_inverse_relations_merge_and_keep_provenance(self):
        old = record("al:ao:old", "Lei n.º 38/20", [{
            "scheme": "law", "value": "Lei n.º 12/24", "relation": "amended_by"
        }])
        new = record("al:ao:new", "Lei n.º 12/24", [{
            "scheme": "law", "value": "Lei n.º 38/20", "relation": "amends"
        }])
        graph = catalog.build_relationship_graph([old, new])
        self.assertEqual(1, len(graph["edges"]))
        edge = graph["edges"][0]
        self.assertEqual(("al:ao:new", "al:ao:old", "amends"),
                         (edge["source"], edge["target"], edge["relation"]))
        self.assertEqual(
            {("al:ao:old", old["source_url"]), ("al:ao:new", new["source_url"])},
            {(item["record_id"], item["url"]) for item in edge["evidence"]},
        )
        report = catalog.check_graph_integrity([old, new])
        self.assertEqual("pass", report["status"])

    def test_ambiguous_reference_is_explicit_and_reported(self):
        first = record("al:ao:first", "Lei n.º 2/20")
        second = record("al:ao:second", "Lei n.º 2/20")
        citing = record("al:ao:citing", "Lei n.º 3/20", [{
            "scheme": "law", "value": "Lei n.º 2/20", "relation": "amends"
        }])
        graph = catalog.build_relationship_graph([first, second, citing])
        node = next(n for n in graph["nodes"]
                    if n["verification_status"] == "ambiguous_reference")
        self.assertFalse(node["resolved"])
        report = catalog.check_graph_integrity([first, second, citing])
        self.assertIn("ambiguous_reference", {item["code"] for item in report["warnings"]})

    def test_unresolved_reference_is_preserved_as_external_node(self):
        citing = record("al:ao:citing", "Lei n.º 3/20", [{
            "scheme": "law", "value": "Lei n.º 99/99", "relation": "regulates"
        }])
        graph = catalog.build_relationship_graph([citing])
        external = [n for n in graph["nodes"] if not n["resolved"]]
        self.assertEqual(1, len(external))
        self.assertEqual("unresolved_reference", external[0]["verification_status"])
        report = catalog.check_graph_integrity([citing])
        self.assertEqual("pass", report["status"])
        self.assertEqual(1, report["unresolved_reference_count"])

    def test_invalid_relation_self_reference_and_duplicate_are_errors(self):
        item = record("al:ao:self", "Lei n.º 4/20", [
            {"scheme": "record_id", "value": "al:ao:self", "relation": "amends"},
            {"scheme": "record_id", "value": "al:ao:self", "relation": "amends"},
            {"scheme": "law", "value": "Lei n.º 9/20", "relation": "invented"},
        ])
        report = catalog.check_graph_integrity([item])
        codes = {issue["code"] for issue in report["errors"]}
        self.assertTrue({"invalid_relation", "self_reference", "duplicate_assertion"} <= codes)
        self.assertEqual("invalid", report["status"])

    def test_schema_rejects_unknown_relation_term(self):
        schema = json.loads((ROOT / "schemas/legal-document.schema.json").read_text(encoding="utf-8"))
        source = json.loads((ROOT / "records/angola/lei-12-24-2024.json").read_text(encoding="utf-8"))
        invalid = copy.deepcopy(source)
        invalid["related_identifiers"][0]["relation"] = "invented"
        validator = Draft202012Validator(schema)
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_integrity_report_detects_missing_edge_provenance(self):
        item = record("al:ao:unproven", "Lei n.º 5/20", [{
            "scheme": "law", "value": "Lei n.º 6/20", "relation": "amends"
        }], source_url=None)
        # Force a missing link: the graph must report that the edge has no usable provenance URL.
        item["source_url"] = None
        report = catalog.check_graph_integrity([item])
        self.assertIn("invalid_provenance", {issue["code"] for issue in report["errors"]})

    def test_similarity_suggestion_never_resolves_or_confirms_edge(self):
        known = record("al:ao:law-18", "Lei n.º 18/21, de 16 de Agosto")
        citing = record("al:ao:citing", "Constituição", [{
            "scheme": "law", "value": "Lei n.º 18/22 de 16 Agosto", "relation": "amends"
        }])
        graph = catalog.build_relationship_graph([known, citing])
        external = next(node for node in graph["nodes"] if not node["resolved"])
        self.assertEqual("unresolved_reference", external["verification_status"])
        self.assertTrue(external["suggested_matches"])
        self.assertEqual("al:ao:law-18", external["suggested_matches"][0]["record_id"])
        edge = next(edge for edge in graph["edges"] if edge["evidence"][0]["record_id"] == "al:ao:citing")
        self.assertEqual(external["id"], edge["target"])
        self.assertIn("suggestion-only", external["suggested_matches"][0]["method"])

    def test_coverage_schema_accepts_ledger_and_rejects_missing_verified_record(self):
        schema = json.loads((ROOT / "schemas/catalogue-coverage.schema.json").read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "coverage/catalogue-coverage.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        self.assertFalse(list(validator.iter_errors(ledger)))
        invalid = copy.deepcopy(ledger)
        invalid["targets"][0]["record_id"] = None
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_coverage_report_requires_verified_record_and_null_for_other_states(self):
        ledger = {"reviewed_on": "2026-11-03", "scope_note": "bounded", "targets": [
            {"id": "present", "status": "verified", "record_id": "al:ao:law"},
            {"id": "pending", "status": "pending_verification", "record_id": None},
            {"id": "missing", "status": "not_located", "record_id": None},
        ]}
        records = [record("al:ao:law", "Lei n.º 1/20")]
        report = catalog.catalogue_coverage(ledger, records)
        self.assertEqual("pass", report["status"])
        self.assertEqual(1, report["target_counts"]["pending_verification"])
        ledger["targets"][0]["record_id"] = "al:ao:unknown"
        ledger["targets"][1]["record_id"] = "al:ao:law"
        report = catalog.catalogue_coverage(ledger, records)
        self.assertEqual("invalid", report["status"])
        self.assertEqual(1, len(report["errors"]))

if __name__ == "__main__":
    unittest.main()
