"""Smoke test for the source registry schema and status distinctions."""
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

class SourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas/source-registry.schema.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "sources/source-registry.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def test_seed_registry_is_valid_and_ids_unique(self):
        self.assertEqual([], list(self.validator.iter_errors(self.registry)))
        ids = [source["id"] for source in self.registry["sources"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_candidates_are_not_marked_official(self):
        for source in self.registry["sources"]:
            if source["id"].startswith("candidate-"):
                self.assertEqual("candidate_discovery_only", source["verification_status"])

    def test_required_fields_reject_missing_availability(self):
        sample = dict(self.registry["sources"][0])
        sample.pop("observed_availability")
        self.assertTrue(list(self.validator.iter_errors(sample)))

if __name__ == "__main__":
    unittest.main()
