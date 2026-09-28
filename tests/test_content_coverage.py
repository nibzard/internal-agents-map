from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "content_coverage", ROOT / "scripts/content_coverage.py"
)
coverage_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(coverage_module)
build = coverage_module.build
FIXTURE = ROOT / "tests" / "fixtures" / "schema8" / "fixture-agent.yaml"


class ContentCoverageTests(unittest.TestCase):
    def test_legacy_record_is_unassessed(self) -> None:
        result = coverage_module.coverage([{"id": "fixture"}])
        self.assertEqual(
            result["entries"], [{"id": "fixture", "format_status": "legacy-unassessed"}]
        )

    def test_counts_canonical_observations_and_source_gaps(self) -> None:
        record = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        record["page_content"]["source_ids"] = ["fixture-agent-source-1"]
        entry = coverage_module.coverage([record])["entries"][0]
        self.assertEqual(entry["unreviewed_source_ids"], ["fixture-agent-source-2"])
        self.assertEqual(entry["raw_observation_count"], 3)
        self.assertEqual(entry["canonical_observation_count"], 2)

    def test_coverage_reports_the_derived_questions_and_fields(self) -> None:
        record = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        entry = coverage_module.coverage([record])["entries"][0]
        self.assertEqual(
            entry["questions"]["observations"]["claim_paths"],
            ["headline_metric", "key_metrics.forty-prs-a-week", "key_metrics.half-merged"],
        )
        self.assertEqual(list(entry["implementation_fields"]), list(build.ARCHITECTURE_FIELDS))
        self.assertEqual(entry["implementation_fields"]["sandbox"]["state"], "not-applicable")
        self.assertEqual(entry["implementation_fields"]["tool_access"]["state"], "unreported")
        self.assertEqual(entry["next_actions"], [])

    def test_output_is_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "coverage.json"
            record = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
            with (
                mock.patch.object(coverage_module.build, "load_agents", return_value=[record]),
                mock.patch.object(sys, "argv", ["content_coverage.py", "--output", str(output)]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                coverage_module.main()
                first = output.read_bytes()
                coverage_module.main()
            self.assertEqual(output.read_bytes(), first)
            self.assertEqual(json.loads(first), coverage_module.coverage([record]))

    def test_implementation_field_is_reported_iff_its_architecture_field_is_present(self) -> None:
        for record in coverage_module.build.load_agents():
            if record.get("page_content") is None:
                continue
            architecture = record.get("architecture") or {}
            entry = coverage_module.coverage([record])["entries"][0]
            for key, value in entry["implementation_fields"].items():
                with self.subTest(record=record["id"], field=key):
                    self.assertEqual(key in architecture, value["state"] == "reported")


if __name__ == "__main__":
    unittest.main()
