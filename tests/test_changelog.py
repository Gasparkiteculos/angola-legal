"""Release heading consistency checks for CHANGELOG.md."""
from datetime import date
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^## \[(\d+)\.(\d+)\.(\d+)\] - (\d{4}-\d{2}-\d{2})$")


class ChangelogIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        cls.version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        cls.headings = [line for line in cls.text.splitlines() if line.startswith("##")]
        cls.parsed = []
        for line in cls.headings:
            match = HEADING.fullmatch(line)
            if match:
                major, minor, patch, release_date = match.groups()
                cls.parsed.append(((int(major), int(minor), int(patch)),
                                   f"{major}.{minor}.{patch}",
                                   date.fromisoformat(release_date)))

    def test_all_release_headers_have_version_and_iso_date(self):
        self.assertTrue(self.headings, "No release headings were found.")
        self.assertEqual(
            len(self.headings), len(self.parsed),
            "Every level-two heading must use '## [X.Y.Z] - YYYY-MM-DD'.",
        )

    def test_each_version_occurs_once(self):
        versions = [version for _, version, _ in self.parsed]
        self.assertEqual(len(versions), len(set(versions)),
                         "A release version appears more than once.")

    def test_versions_are_in_descending_order(self):
        versions = [parts for parts, _, _ in self.parsed]
        self.assertEqual(versions, sorted(versions, reverse=True),
                         "Release versions must be ordered newest to oldest.")

    def test_release_dates_are_in_descending_order(self):
        dates = [release_date for _, _, release_date in self.parsed]
        self.assertEqual(dates, sorted(dates, reverse=True),
                         "Release dates must be ordered newest to oldest.")

    def test_version_file_has_a_matching_changelog_section(self):
        versions = [version for _, version, _ in self.parsed]
        self.assertIn(self.version, versions,
                      "VERSION must have a matching CHANGELOG.md section.")


if __name__ == "__main__":
    unittest.main()
