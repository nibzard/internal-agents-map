from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "content_coverage", ROOT / "scripts/content_coverage.py"
)
coverage_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(coverage_module)


class ContentCoverageTests(unittest.TestCase):
    def test_legacy_record_is_unassessed(self) -> None:
        result = coverage_module.coverage([{"id": "fixture"}])
        self.assertEqual(
            result["entries"], [{"id": "fixture", "format_status": "legacy-unassessed"}]
        )

    def test_counts_canonical_observations_and_source_gaps(self) -> None:
        disposition = {"state": "unreported", "claim_paths": [], "note": "Checked."}
        record = {
            "id": "fixture",
            "sources": [{"id": "one"}, {"id": "two"}],
            "page_content": {
                "reviewed_at": "2026-09-17",
                "source_ids": ["one"],
                "questions": {"purpose": disposition},
                "implementation_fields": {"model": disposition},
                "observations": {
                    "headline_metric": {"category": "effectiveness"},
                    "key_metrics.0": {"duplicate_of": "headline_metric"},
                },
            },
        }
        entry = coverage_module.coverage([record])["entries"][0]
        self.assertEqual(entry["unreviewed_source_ids"], ["two"])
        self.assertEqual(entry["raw_observation_count"], 2)
        self.assertEqual(entry["canonical_observation_count"], 1)

    def test_implementation_field_is_reported_iff_its_architecture_field_is_present(self) -> None:
        for record in coverage_module.build.load_agents():
            page = record.get("page_content")
            if page is None:
                continue
            architecture = record.get("architecture") or {}
            for key, value in page["implementation_fields"].items():
                with self.subTest(record=record["id"], field=key):
                    present = architecture.get(key) not in (None, "", [])
                    self.assertEqual(present, value["state"] == "reported")


if __name__ == "__main__":
    unittest.main()
