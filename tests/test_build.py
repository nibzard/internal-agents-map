from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import shutil
import struct
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "src" / "content" / "lessons"
SPEC = importlib.util.spec_from_file_location("catalog_build", ROOT / "scripts" / "build.py")
build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(build)
# The agent schema checks the shape of a source; validate_source checks its capture.
SOURCE_VALIDATOR = build.Draft7Validator(
    {
        **build.AGENT_SCHEMA["definitions"]["source"],
        "definitions": build.AGENT_SCHEMA["definitions"],
    },
    format_checker=build.FORMAT_CHECKER,
)


class BuildTests(unittest.TestCase):
    def test_environment_count_counts_present_sandbox_values(self) -> None:
        values = [
            None,
            "",
            "  ",
            "AWS EC2 devbox",
            "Docker container",
        ]
        records = [
            {
                "approach_type": "agent",
                "autonomy": "unknown",
                "operating_models": [{"attention_boundary": "unknown"}],
                "architecture": {"sandbox": value},
            }
            for value in values
        ]
        self.assertIn(
            "- 2 entries document a concrete execution environment.",
            build.render_patterns_snapshot(records),
        )

    def test_capture_paths_reject_symlink_boundaries(self) -> None:
        for mode in (
            "content-sibling",
            "manifest-sibling",
            "content-external",
            "manifest-external",
            "source-sibling",
            "source-external",
            "archive-external",
        ):
            with (
                self.subTest(mode=mode),
                tempfile.TemporaryDirectory() as directory,
                tempfile.TemporaryDirectory() as outside,
            ):
                root = Path(directory)
                bundle = root / "archive" / "sources" / "fixture"
                bundle.mkdir(parents=True)
                sibling = bundle.parent / "sibling"
                sibling.mkdir()
                destination = Path(outside) if "external" in mode else sibling
                name = "metadata.json" if mode.startswith("manifest") else "content.md"
                if mode.startswith("source"):
                    bundle.rmdir()
                    bundle.symlink_to(destination, target_is_directory=True)
                elif mode.startswith("archive"):
                    shutil.rmtree(root / "archive")
                    (root / "archive").symlink_to(destination, target_is_directory=True)
                else:
                    (bundle / name).symlink_to(destination / name)
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    build.resolve_capture_path(
                        f"archive/sources/fixture/{name}",
                        "fixture",
                        name,
                        "capture",
                        "fixture.yaml",
                        root=root,
                    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.records = build.load_agents()
        cls.companies = build.load_companies(cls.records)

    def company_fixture(self, **overrides) -> dict:
        company = {
            "id": "fixture-company",
            "name": "Fixture",
            "homepage": "https://www.fixture.example/",
            "logo": "none",
            "logo_note": "No logo asset has been collected yet.",
        }
        company.update(overrides)
        if isinstance(company.get("logo"), dict):
            company.pop("logo_note", None)
        return company

    def fixture_records(self) -> list[dict]:
        return [{"id": "fixture-agent", "company": "Fixture"}]

    def write_registry(self, root: Path, companies: list[dict]) -> None:
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "data" / "companies.yaml").write_text(
            yaml.safe_dump(companies, sort_keys=False), encoding="utf-8"
        )

    def write_logo(self, root: Path, name: str, content: bytes) -> None:
        logos = root / "public" / "logos"
        logos.mkdir(parents=True, exist_ok=True)
        (logos / name).write_bytes(content)

    def assert_registry_invalid(self, records: list[dict], root: Path) -> None:
        with (
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            build.load_companies(records, root=root)

    def logo_svg(self, **overrides) -> bytes:
        attributes = {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 128 40",
            **overrides,
        }
        markup = " ".join(f'{key}="{value}"' for key, value in attributes.items())
        return f'<svg {markup}><path d="M0 0h128v40H0z"/></svg>'.encode("utf-8")

    def logo_png(self, width: int = 128, height: int = 40) -> bytes:
        return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height)

    def source_fixture(self) -> dict:
        return {
            "id": "fixture-source",
            "title": "Fixture source",
            "url": "https://example.com/article",
            "canonical_url": "https://example.com/article",
            "kind": "engineering-blog",
            "provenance_class": "first-party",
            "role": "evidence",
            "accessed_at": "2026-08-31",
            "last_verified_at": "2026-08-31",
        }

    def write_capture(
        self,
        root: Path,
        *,
        source: dict | None = None,
        markdown: bytes = b"# Preserved source\n\nEvidence.\n",
        pdf: bytes | None = None,
    ) -> tuple[dict, dict, Path]:
        source = copy.deepcopy(source or self.source_fixture())
        source_id = source["id"]
        bundle = root / "archive" / "sources" / source_id
        bundle.mkdir(parents=True)
        markdown_path = bundle / "content.md"
        markdown_path.write_bytes(markdown)
        relative_bundle = f"archive/sources/{source_id}"
        artifacts = {
            "markdown": {
                "path": f"{relative_bundle}/content.md",
                "sha256": f"sha256:{hashlib.sha256(markdown).hexdigest()}",
                "bytes": len(markdown),
            }
        }
        if pdf is not None:
            (bundle / "page.pdf").write_bytes(pdf)
            artifacts["pdf"] = {
                "path": f"{relative_bundle}/page.pdf",
                "sha256": f"sha256:{hashlib.sha256(pdf).hexdigest()}",
                "bytes": len(pdf),
            }
        manifest = {
            "schema_version": 1,
            "source_id": source_id,
            "original_url": source["url"],
            "final_url": source["canonical_url"],
            "captured_at": "2026-08-31T12:34:56Z",
            "http_status": 200,
            "tool": {"name": "steel", "version": "0.4.4"},
            "artifacts": artifacts,
        }
        manifest_path = bundle / "metadata.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        source["capture"] = {"manifest_path": f"{relative_bundle}/metadata.json"}
        return source, manifest, manifest_path

    def assert_source_invalid(self, source: dict, root: Path) -> None:
        if not SOURCE_VALIDATOR.is_valid(source):
            return
        with (
            mock.patch.object(build, "ROOT", root),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            build.validate_source(source, "fixture.yaml", set())

    def rewrite_manifest(self, path: Path, manifest: dict) -> None:
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_catalog_has_unique_ids(self) -> None:
        approach_ids = [record["id"] for record in self.records]
        source_ids = [source["id"] for record in self.records for source in record["sources"]]
        self.assertEqual(len(approach_ids), len(set(approach_ids)))
        self.assertEqual(len(source_ids), len(set(source_ids)))

    def test_normalized_export_has_linked_collections(self) -> None:
        export = build.normalize(self.records, self.companies)
        self.assertEqual(export["schema_version"], 8)
        claim_ids = {claim["id"] for claim in export["claims"]}
        source_ids = {source["id"] for source in export["sources"]}
        company_ids = {company["id"] for company in export["companies"]}
        self.assertTrue(
            all(source["role"] in build.schema_values("sourceRole") for source in export["sources"])
        )
        for approach in export["approaches"]:
            self.assertIn(approach["company_id"], company_ids)
            self.assertTrue(set(approach["claim_ids"]).issubset(claim_ids))
            self.assertTrue(set(approach["source_ids"]).issubset(source_ids))
            self.assertTrue(approach["operating_models"])
            for item in approach["operating_models"]:
                expected = build.BOUNDARY_LEVELS[item["attention_boundary"]]
                self.assertEqual(item["level"], expected)
        for claim in export["claims"]:
            self.assertTrue(claim["evidence"])
            self.assertIn(claim["confidence"], build.schema_values("confidence"))
            self.assertTrue({item["source_id"] for item in claim["evidence"]}.issubset(source_ids))
            if claim["field"].startswith("operating_models."):
                self.assertEqual(claim["kind"], "inference")
                self.assertEqual(claim["provenance"], "catalog-judgment")
                self.assertTrue(claim["valid_at"])

    def test_page_content_pilot_is_complete_and_preserves_primitive_names(self) -> None:
        pilot = [record for record in self.records if record.get("page_content")]
        self.assertEqual(len(pilot), len(self.records))
        catalog = build.normalize(self.records, self.companies)
        claims = {
            claim["display_name"]: claim
            for claim in catalog["claims"]
            if claim["approach_id"] == "github-qubot" and "display_name" in claim
        }
        self.assertEqual(
            claims["Start a Qubot run"]["id"], "github-qubot--primitives-start-a-qubot-run"
        )
        self.assertEqual(claims["Start a Qubot run"]["field"], "primitives.start-a-qubot-run")
        for approach in catalog["approaches"]:
            page = approach["page_content"]
            self.assertEqual(list(page["questions"]), list(build.QUESTION_KEYS))
            self.assertEqual(list(page["implementation_fields"]), list(build.ARCHITECTURE_FIELDS))
            self.assertNotIn("primitive_roles", page)
            self.assertNotIn("observations", page)
            self.assertNotIn(
                "not-reviewed",
                [value["state"] for value in page["questions"].values()]
                + [value["state"] for value in page["implementation_fields"].values()],
            )

    def test_every_schema_7_claim_id_resolves_through_the_claim_aliases(self) -> None:
        lines = SCHEMA7_CLAIM_IDS.read_text(encoding="utf-8").splitlines()
        old_ids = {line for line in lines if not line.startswith("#")}
        aliases = build.load_claim_aliases()
        self.assertEqual(set(aliases), old_ids)
        catalog = build.normalize(self.records, self.companies, aliases)
        claim_ids = {claim["id"] for claim in catalog["claims"]}
        self.assertTrue(set(aliases.values()) <= claim_ids)

    def test_page_content_rejects_unsupported_reported_and_duplicate_chains(self) -> None:
        record = copy.deepcopy(
            next(item for item in self.records if item["id"] == "notion-custom-agents")
        )
        sources = {source["id"] for source in record["sources"]}
        for link in record["evidence"]["summary"]:
            link["relation"] = "contextualizes"
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build.validate_page_content(record, "fixture.yaml", sources)

        record = copy.deepcopy(
            next(item for item in self.records if item["id"] == "notion-custom-agents")
        )
        aliases = record["page_content"]["aliases"]
        alias, target = next(iter(aliases.items()))
        aliases[target["duplicate_of"]] = {"duplicate_of": alias, "reason": "Fixture cycle."}
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build.validate_metric_axes(record, "fixture.yaml")

    def test_page_content_accepts_all_four_review_states(self) -> None:
        record = copy.deepcopy(next(item for item in self.records if item["id"] == "github-qubot"))
        questions = record["page_content"]["questions"]
        questions["human_involvement"] = {
            "state": "not-applicable",
            "claim_paths": [],
            "note": "Fixture scope has no human step.",
        }
        questions["lessons"] = {"state": "not-reviewed", "note": "Review the next capture."}
        build.validate_page_content(
            record, "fixture.yaml", {source["id"] for source in record["sources"]}
        )

    def test_a_note_is_optional_for_an_unreported_question_only(self) -> None:
        path = build.AGENTS_DIR / "github-qubot.yaml"

        def record_with(slot: str, key: str, value: dict) -> dict:
            record = copy.deepcopy(
                next(item for item in self.records if item["id"] == "github-qubot")
            )
            record["page_content"][slot][key] = value
            return record

        build.validate_record(
            record_with(
                "questions", "human_involvement", {"state": "unreported", "claim_paths": []}
            ),
            path,
            set(),
        )
        for slot, key, value in (
            ("questions", "human_involvement", {"state": "not-reviewed", "claim_paths": []}),
            ("questions", "human_involvement", {"state": "not-applicable", "claim_paths": []}),
            ("implementation_fields", "sandbox", {"state": "unreported"}),
            ("implementation_fields", "sandbox", {"state": "not-reviewed"}),
            ("implementation_fields", "sandbox", {"state": "not-applicable"}),
        ):
            with (
                self.subTest(slot=slot, value=value),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                build.validate_record(record_with(slot, key, value), path, set())

    def test_architecture_rejects_placeholder_and_empty_values(self) -> None:
        record = next(item for item in self.records if item["id"] == "github-qubot")
        rejected = (
            ("sandbox", "unknown"),
            ("sandbox", "UNKNOWN"),
            ("sandbox", ""),
            ("sandbox", "  "),
            ("model", "Not specified"),
            ("model", "Not named. A template picks the model."),
            ("model", "Not documented by name"),
            ("model", "Sources name no model or provider"),
            ("harness", "Not specified publicly"),
            ("credentials", "n/a"),
            ("credentials", "Undisclosed"),
            ("interfaces", []),
        )
        for key, value in rejected:
            with self.subTest(key=key, value=value):
                fixture = {**record, "architecture": {**record["architecture"], key: value}}
                errors = build.schema_errors(fixture, "github-qubot.yaml")
                self.assertTrue(any(f": architecture.{key}: " in error for error in errors))
        for key, value in (
            ("sandbox", "Docker container"),
            ("model", "Claude; no model version is named"),
            ("credentials", "None of the user's credentials reach the sandbox"),
        ):
            with self.subTest(key=key, value=value):
                fixture = {**record, "architecture": {**record["architecture"], key: value}}
                self.assertEqual(build.schema_errors(fixture, "github-qubot.yaml"), [])

    def test_an_implementation_field_is_reported_if_and_only_if_its_field_is_present(
        self,
    ) -> None:
        path = build.AGENTS_DIR / "github-qubot.yaml"
        base = next(item for item in self.records if item["id"] == "github-qubot")

        present_but_unreported = copy.deepcopy(base)
        present_but_unreported["page_content"]["implementation_fields"]["model"] = {
            "state": "unreported",
            "note": "Fixture.",
        }
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            build.validate_record(present_but_unreported, path, set())
        self.assertIn(
            "implementation_fields.model has a state, but architecture.model is present",
            stderr.getvalue(),
        )
        for approach in build.normalize(self.records, self.companies)["approaches"]:
            architecture = next(
                record.get("architecture") or {}
                for record in self.records
                if record["id"] == approach["id"]
            )
            for key, value in approach["page_content"]["implementation_fields"].items():
                with self.subTest(record=approach["id"], field=key):
                    self.assertEqual(key in architecture, value["state"] == "reported")

    def test_valid_markdown_only_capture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, manifest, _ = self.write_capture(root)
            # A capture test proves nothing when the schema already rejects its source.
            self.assertTrue(SOURCE_VALIDATOR.is_valid(source))
            with mock.patch.object(build, "ROOT", root):
                build.validate_source(source, "fixture.yaml", set())
                self.assertEqual(build.load_capture_manifest(source, "fixture.yaml"), manifest)

    def test_valid_markdown_and_pdf_capture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, manifest, _ = self.write_capture(root, pdf=b"%PDF-1.7\nfixture\n%%EOF\n")
            with mock.patch.object(build, "ROOT", root):
                build.validate_source(source, "fixture.yaml", set())
                loaded = build.load_capture_manifest(source, "fixture.yaml")
            self.assertEqual(loaded, manifest)
            self.assertIn("pdf", loaded["artifacts"])

    def test_capture_requires_exact_authored_shape(self) -> None:
        for capture in ({}, {"manifest_path": "unused", "extra": True}, "unused"):
            with self.subTest(capture=capture):
                source = self.source_fixture()
                source["capture"] = capture
                with tempfile.TemporaryDirectory() as directory:
                    self.assert_source_invalid(source, Path(directory))

    def test_capture_manifest_requires_exact_schema(self) -> None:
        mutations = (
            lambda manifest: manifest.pop("http_status"),
            lambda manifest: manifest.update({"unexpected": True}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                mutate(manifest)
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_timestamp_must_be_rfc3339_utc(self) -> None:
        for value in (
            "2026-08-31",
            "2026-08-31T12:34:56+00:00",
            "2026-02-31T12:34:56Z",
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                manifest["captured_at"] = value
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_source_identity_must_match(self) -> None:
        mutations = (
            lambda manifest: manifest.update({"source_id": "different-source"}),
            lambda manifest: manifest.update({"original_url": "https://example.com/different"}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                mutate(manifest)
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_metadata_values_are_validated(self) -> None:
        mutations = (
            lambda manifest: manifest.update({"schema_version": 2}),
            lambda manifest: manifest.update({"final_url": "http://example.com"}),
            lambda manifest: manifest.update({"http_status": 404}),
            lambda manifest: manifest.update({"tool": {"name": "browser", "version": "1"}}),
            lambda manifest: manifest.update({"tool": {"name": "steel", "version": ""}}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                mutate(manifest)
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_paths_reject_absolute_traversal_and_cross_source_values(self) -> None:
        values = (
            "/archive/sources/fixture-source/metadata.json",
            "archive/sources/fixture-source/../fixture-source/metadata.json",
            "archive/sources/different-source/metadata.json",
            "archive\\sources\\fixture-source\\metadata.json",
        )
        for value in values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, _, _ = self.write_capture(root)
                source["capture"]["manifest_path"] = value
                self.assert_source_invalid(source, root)

    def test_capture_artifact_paths_cannot_escape_or_cross_bundles(self) -> None:
        values = (
            "/archive/sources/fixture-source/content.md",
            "archive/sources/fixture-source/../fixture-source/content.md",
            "archive/sources/different-source/content.md",
        )
        for value in values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                manifest["artifacts"]["markdown"]["path"] = value
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_rejects_missing_and_empty_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, _, _ = self.write_capture(root)
            (root / "archive/sources/fixture-source/content.md").unlink()
            self.assert_source_invalid(source, root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, _, _ = self.write_capture(root, markdown=b" \n\t")
            self.assert_source_invalid(source, root)

    def test_capture_rejects_byte_count_and_sha_mismatches(self) -> None:
        mutations = (
            lambda artifact: artifact.update({"bytes": artifact["bytes"] + 1}),
            lambda artifact: artifact.update({"sha256": f"sha256:{'0' * 64}"}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, manifest, path = self.write_capture(root)
                mutate(manifest["artifacts"]["markdown"])
                self.rewrite_manifest(path, manifest)
                self.assert_source_invalid(source, root)

    def test_capture_rejects_invalid_and_oversized_pdf(self) -> None:
        pdf_values = (
            b"not a PDF",
            b"%PDF-" + b"0" * build.MAX_PDF_BYTES,
        )
        for pdf in pdf_values:
            with self.subTest(size=len(pdf)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, _, _ = self.write_capture(root, pdf=pdf)
                self.assert_source_invalid(source, root)

    def test_normalized_export_resolves_capture_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = copy.deepcopy(self.records[0])
            for existing_source in record["sources"]:
                existing_source.pop("capture", None)
            source, manifest, _ = self.write_capture(root, source=record["sources"][0])
            record["sources"][0] = source
            with mock.patch.object(build, "ROOT", root):
                export = build.normalize([record], [self.company_fixture(name=record["company"])])
            normalized_source = next(
                item for item in export["sources"] if item["id"] == source["id"]
            )
            self.assertEqual(export["schema_version"], 8)
            self.assertEqual(normalized_source["capture"], manifest)
            self.assertNotIn("manifest_path", normalized_source["capture"])

    def test_alias_exports_and_links_to_the_original_capture_without_relabeling_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = copy.deepcopy(self.records[0])
            for source in record["sources"]:
                source.pop("capture", None)
            original, manifest, _ = self.write_capture(root, source=record["sources"][0])
            alias = {
                **original,
                "id": "fixture-alias",
                "duplicate_of": original["id"],
                "accessed_at": "2026-09-28",
            }
            alias.pop("capture")
            record["sources"][0] = original
            record["sources"].append(alias)
            with mock.patch.object(build, "ROOT", root):
                export = build.normalize([record], [self.company_fixture(name=record["company"])])
                citation = build.render_source_reference(
                    alias, {source["id"]: source for source in record["sources"]}
                )
            exported_alias = next(
                source for source in export["sources"] if source["id"] == alias["id"]
            )
            self.assertEqual(exported_alias["capture"], manifest)
            self.assertIn(f"../archive/sources/{original['id']}/content.md", citation)
            self.assertIn("captured 2026-08-31", citation)
            self.assertNotIn("capture", alias)

    def test_source_reference_renders_all_archive_combinations(self) -> None:
        original = "[Fixture source](https://example.com/article)"
        self.assertEqual(build.render_source_reference(self.source_fixture()), original)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local_source, _, _ = self.write_capture(root)
            with mock.patch.object(build, "ROOT", root):
                self.assertEqual(
                    build.render_source_reference(local_source),
                    f"{original} ([snapshot](../archive/sources/fixture-source/content.md), "
                    "captured 2026-08-31)",
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf_source, _, _ = self.write_capture(root, pdf=b"%PDF-1.7\nfixture\n%%EOF\n")
            with mock.patch.object(build, "ROOT", root):
                self.assertEqual(
                    build.render_source_reference(pdf_source),
                    f"{original} ([snapshot](../archive/sources/fixture-source/content.md), "
                    "[PDF](../archive/sources/fixture-source/page.pdf), captured 2026-08-31)",
                )

    def test_the_default_build_writes_the_data_and_the_repository_documents(self) -> None:
        catalog = build.normalize(self.records, self.companies, build.load_claim_aliases())
        outputs = build.data_outputs(self.records, catalog)
        self.assertEqual(
            set(outputs),
            {
                build.README,
                build.PATTERNS,
                build.ADOPTION_LESSONS,
                build.LANDSCAPE,
                build.DATA_JSON,
                build.SCHEMA_VALUES_TS,
            },
        )
        for path, expected in outputs.items():
            with self.subTest(path=path.name):
                self.assertEqual(
                    path.read_bytes(),
                    expected.encode("utf-8") if isinstance(expected, str) else expected,
                )

    def test_two_builds_of_the_same_records_agree(self) -> None:
        first = build.data_outputs(self.records, build.normalize(self.records, self.companies))
        second = build.data_outputs(self.records, build.normalize(self.records, self.companies))
        self.assertEqual(first, second)

    def test_outputs_are_staged_and_a_stale_file_fails_the_check(self) -> None:
        catalog = build.normalize(self.records, self.companies)
        outputs = build.data_outputs(self.records, catalog)
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            relocated = {
                root / path.relative_to(ROOT): content for path, content in outputs.items()
            }
            with mock.patch.object(build, "ROOT", root):
                build.write_outputs(relocated)
                for path, content in relocated.items():
                    self.assertEqual(
                        path.read_bytes(),
                        content.encode("utf-8") if isinstance(content, str) else content,
                    )
                with (
                    mock.patch.object(build, "load_agents", return_value=self.records),
                    mock.patch.object(build, "load_companies", return_value=self.companies),
                    mock.patch.object(build, "normalize", return_value=catalog),
                    mock.patch.object(build, "data_outputs", return_value=relocated),
                    mock.patch.object(sys, "argv", ["build.py", "--check"]),
                ):
                    build.main()
                    for path in relocated:
                        original = path.read_bytes()
                        for replacement in (b"stale", None):
                            if replacement is None:
                                path.unlink()
                            else:
                                path.write_bytes(replacement)
                            with (
                                contextlib.redirect_stderr(io.StringIO()),
                                self.assertRaises(SystemExit),
                            ):
                                build.main()
                            path.write_bytes(original)

    def test_every_claim_and_source_belongs_to_one_approach(self) -> None:
        catalog = build.normalize(self.records, self.companies)
        self.assertEqual(len(catalog["approaches"]), len(self.records))
        self.assertEqual(
            sum(len(a["claim_ids"]) for a in catalog["approaches"]), len(catalog["claims"])
        )
        self.assertEqual(
            sum(len(a["source_ids"]) for a in catalog["approaches"]), len(catalog["sources"])
        )

    def test_routing_manifest_lists_every_page_of_the_catalog(self) -> None:
        manifest = json.loads((ROOT / "routing-manifest.json").read_text(encoding="utf-8"))
        expected = [
            "/",
            "/infrastructure",
            "/definitions",
            "/methodology",
            "/lessons",
            # The problem pages that the homepage offers as entry points.
            "/problems/code-review-load",
            "/problems/security-alerts",
            "/problems/company-data",
            "/problems/operations",
            *(f"/lessons/{path.stem}" for path in LESSONS.glob("*.md")),
            *(f"/agents/{record['id']}" for record in self.records),
            *(
                f"/organizations/{company_id}"
                for company_id in {
                    record["company_id"]
                    for record in build.normalize(self.records, self.companies)["approaches"]
                }
            ),
        ]
        self.assertEqual(
            sorted(manifest["routes"]),
            sorted(expected),
            "Run npm run build to regenerate routing-manifest.json for the current catalog.",
        )

    def test_catalog_contains_source_anchors(self) -> None:
        catalog = build.render_landscape(self.records)
        for record in self.records:
            for source in record["sources"]:
                self.assertIn(f'<a id="{source["id"]}"></a>', catalog)

    def test_catalog_contains_comparison_links(self) -> None:
        catalog = build.render_landscape(self.records)
        for record in self.records:
            self.assertIn(f"[{record['agent_name']}](#{record['id']})", catalog)

    def test_overview_counts_match_export(self) -> None:
        export = build.normalize(self.records, self.companies)
        company_count = len(
            {
                record["company"]
                for record in self.records
                if build.catalog_section(record["approach_type"]) == "agents"
            }
        )
        overview = build.render_overview(self.records, export)
        self.assertIn(
            f"{sum(build.catalog_section(record['approach_type']) == 'agents' for record in self.records)} agents",
            overview,
        )
        self.assertIn(f"{company_count} organizations", overview)
        self.assertIn(
            f"{len({source.get('canonical_url', source['url']) for source in export['sources']})} distinct sources",
            overview,
        )
        self.assertIn(f"{len(export['claims'])} evidence-linked claims", overview)

    def test_readme_overview_contains_every_approach(self) -> None:
        overview = build.render_overview_table(self.records)
        for record in self.records:
            self.assertIn(
                f"[{record['agent_name']}](docs/landscape.md#{record['id']})",
                overview,
            )

    def test_readme_findings_counts_are_current(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(build.render_readme_findings(self.records), readme)

    def test_catalog_statistics_keep_entry_and_workflow_units_separate(self) -> None:
        fixture = [
            {
                "approach_type": "platform",
                "autonomy": "human-in-loop",
                "operating_models": [
                    {"attention_boundary": "work-product-review"},
                    {"attention_boundary": "unknown"},
                ],
                "architecture": {"interfaces": ["slack"]},
            },
            {
                "approach_type": "supporting-pattern",
                "autonomy": "unknown",
                "operating_models": [{"attention_boundary": "unknown"}],
                "architecture": {"sandbox": "Docker container"},
            },
        ]
        stats = build.catalog_statistics(fixture)
        self.assertEqual(stats["entries"], 2)
        self.assertEqual(stats["supporting_entries"], 2)
        self.assertEqual(stats["operating_models"], 0)
        self.assertEqual(stats["multi_workflow_entries"], 0)
        self.assertEqual(stats["attention_boundaries"]["work-product-review"], 0)
        self.assertEqual(stats["attention_boundaries"]["unknown"], 0)
        self.assertEqual(stats["autonomy"]["human-in-loop"], 0)

    def test_analysis_snapshots_match_catalog(self) -> None:
        patterns = build.render_patterns_snapshot(self.records)
        adoption = build.render_adoption_snapshot(self.records)
        autonomy_counts = Counter(
            record["autonomy"]
            for record in self.records
            if build.catalog_section(record["approach_type"]) == "agents"
        )
        self.assertIn(f"contains {len(self.records)} entries", patterns)
        self.assertIn(f"draw on {len(self.records)} catalog entries", adoption)
        self.assertIn(
            f"{autonomy_counts['drafts-reviewed']} `drafts-reviewed`",
            adoption,
        )

    def test_markdown_escapes_table_values(self) -> None:
        self.assertEqual(build.markdown("Acme | Corp\nTeam"), "Acme \\| Corp Team")
        self.assertEqual(build.markdown(["slack", "web"]), "slack, web")

    def test_company_registry_loads_and_joins_both_ways(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_registry(root, [self.company_fixture()])
            registry = build.load_companies(self.fixture_records(), root=root)
            self.assertEqual(registry, [self.company_fixture()])

    def assert_registry_error(self, records: list[dict], root: Path) -> str:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            build.load_companies(records, root=root)
        return stderr.getvalue()

    def test_company_registry_must_join_both_ways(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_registry(root, [self.company_fixture()])
            message = self.assert_registry_error(
                [
                    {"id": "fixture-agent", "company": "Fixture"},
                    {"id": "other-agent", "company": "Other"},
                ],
                root,
            )
            self.assertIn(
                "other-agent.yaml: company 'Other' has no record in data/companies.yaml.", message
            )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_registry(
                root,
                [
                    self.company_fixture(),
                    self.company_fixture(
                        id="unused-company",
                        name="Unused",
                        homepage="https://unused.example/",
                    ),
                ],
            )
            message = self.assert_registry_error(self.fixture_records(), root)
            self.assertIn(
                "data/companies.yaml: company 'unused-company' is not used by any approach record.",
                message,
            )

    def test_company_registry_rejects_invalid_records(self) -> None:
        fixtures = (
            self.company_fixture(id="Fixture"),
            self.company_fixture(name=""),
            self.company_fixture(homepage="http://www.fixture.example/"),
            self.company_fixture(logo_note=None),
            self.company_fixture(logo=None),
            self.company_fixture(
                logo={
                    "file": "fixture-company.gif",
                    "source_url": "https://fixture.example/logo",
                    "accessed_at": "2026-09-15",
                }
            ),
            {**self.company_fixture(), "extra": True},
        )
        for company in fixtures:
            with self.subTest(company=company), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_registry(root, [company])
                self.assert_registry_invalid(self.fixture_records(), root)
        for companies in (
            [self.company_fixture(), self.company_fixture(homepage="https://other.example/")],
            [
                self.company_fixture(),
                self.company_fixture(id="second-company", homepage="https://other.example/"),
            ],
            [self.company_fixture(id="z-company"), self.company_fixture(id="a-company")],
        ):
            with self.subTest(companies=companies), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_registry(root, companies)
                self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_file_rules(self) -> None:
        fixtures = (
            {
                "file": "other.svg",
                "source_url": "https://fixture.example/logo",
                "accessed_at": "2026-09-15",
            },
            {
                "file": "fixture-company.svg",
                "source_url": "http://fixture.example/logo",
                "accessed_at": "2026-09-15",
            },
            {
                "file": "fixture-company.svg",
                "source_url": "https://fixture.example/logo",
                "accessed_at": "2026-9-15",
            },
            {"file": "fixture-company.svg", "source_url": "https://fixture.example/logo"},
        )
        for logo in fixtures:
            with self.subTest(logo=logo), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_logo(root, "fixture-company.svg", self.logo_svg())
                self.write_registry(root, [self.company_fixture(logo=logo)])
                self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_asset_must_exist_and_be_named_by_the_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_registry(
                root,
                [
                    self.company_fixture(
                        logo={
                            "file": "fixture-company.svg",
                            "source_url": "https://fixture.example/logo",
                            "accessed_at": "2026-09-15",
                        }
                    )
                ],
            )
            self.assert_registry_invalid(self.fixture_records(), root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_logo(root, "fixture-company.svg", self.logo_svg())
            self.write_logo(root, "stray.svg", self.logo_svg())
            self.write_registry(root, [self.company_fixture(logo="none")])
            self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_must_not_hold_unsafe_svg(self) -> None:
        payloads = (
            b'<!DOCTYPE svg><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 40"/>',
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 40"><!ENTITY x "y"/></svg>',
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 40"><script>1</script></svg>',
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 40">'
            b"<foreignObject><p>1</p></foreignObject></svg>",
            self.logo_svg(onload="alert(1)"),
            self.logo_svg(viewBox="0 0 128 40", href="https://evil.example/logo"),
        )
        for content in payloads:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_logo(root, "fixture-company.svg", content)
                self.write_registry(
                    root,
                    [
                        self.company_fixture(
                            logo={
                                "file": "fixture-company.svg",
                                "source_url": "https://fixture.example/logo",
                                "accessed_at": "2026-09-15",
                            }
                        )
                    ],
                )
                self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_assets_are_limited_in_size(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_logo(
                root, "fixture-company.svg", self.logo_svg() + b" " * build.MAX_SVG_LOGO_BYTES
            )
            self.write_registry(
                root,
                [
                    self.company_fixture(
                        logo={
                            "file": "fixture-company.svg",
                            "source_url": "https://fixture.example/logo",
                            "accessed_at": "2026-09-15",
                        }
                    )
                ],
            )
            self.assert_registry_invalid(self.fixture_records(), root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_logo(root, "fixture-company.png", self.logo_png(width=127))
            self.write_registry(
                root,
                [
                    self.company_fixture(
                        logo={
                            "file": "fixture-company.png",
                            "source_url": "https://fixture.example/logo",
                            "accessed_at": "2026-09-15",
                        }
                    )
                ],
            )
            self.assert_registry_invalid(self.fixture_records(), root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_logo(
                root, "fixture-company.png", self.logo_png() + b"\x00" * build.MAX_PNG_LOGO_BYTES
            )
            self.write_registry(
                root,
                [
                    self.company_fixture(
                        logo={
                            "file": "fixture-company.png",
                            "source_url": "https://fixture.example/logo",
                            "accessed_at": "2026-09-15",
                        }
                    )
                ],
            )
            self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_assets_need_a_usable_size(self) -> None:
        payloads = (
            ("fixture-company.svg", b'<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'),
            ("fixture-company.svg", self.logo_svg(viewBox="0 0 0 40")),
            ("fixture-company.svg", b"<svg viewBox='0 0 128'>path</svg>"),
            ("fixture-company.svg", self.logo_svg(viewBox="0 0 inf 40")),
            ("fixture-company.svg", self.logo_svg(viewBox="0 0 nan 40")),
            ("fixture-company.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 8),
        )
        for name, content in payloads:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_logo(root, name, content)
                self.write_registry(
                    root,
                    [
                        self.company_fixture(
                            logo={
                                "file": name,
                                "source_url": "https://fixture.example/logo",
                                "accessed_at": "2026-09-15",
                            }
                        )
                    ],
                )
                self.assert_registry_invalid(self.fixture_records(), root)

    def test_company_logo_descriptor_derives_hash_bytes_and_size(self) -> None:
        for name, content, media_type, size in (
            ("fixture-company.svg", self.logo_svg(), "image/svg+xml", (128, 40)),
            ("fixture-company.png", self.logo_png(width=200, height=64), "image/png", (200, 64)),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_logo(root, name, content)
                logo = {
                    "file": name,
                    "source_url": "https://fixture.example/logo",
                    "accessed_at": "2026-09-15",
                }
                self.write_registry(root, [self.company_fixture(logo=logo)])
                registry = build.load_companies(self.fixture_records(), root=root)
                companies = build.normalize_companies(registry, root=root)
                self.assertEqual(len(companies), 1)
                descriptor = companies[0]["logo"]
                self.assertEqual(
                    descriptor,
                    {
                        "path": f"logos/{name}",
                        "media_type": media_type,
                        "width": size[0],
                        "height": size[1],
                        "bytes": len(content),
                        "sha256": f"sha256:{hashlib.sha256(content).hexdigest()}",
                        "source_url": "https://fixture.example/logo",
                        "accessed_at": "2026-09-15",
                    },
                )

    def test_company_without_a_logo_publishes_a_monogram_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_registry(root, [self.company_fixture()])
            companies = build.normalize_companies(
                build.load_companies(self.fixture_records(), root=root), root=root
            )
            self.assertEqual(companies[0]["logo"], None)
        self.assertEqual(
            build.company_summary(
                [self.company_fixture(logo="none"), self.company_fixture(logo="none")]
            ),
            "2 organizations, 0 logos, 2 monograms",
        )

    def test_duplicate_yaml_keys_fail(self) -> None:
        with self.assertRaises(yaml.constructor.ConstructorError):
            yaml.load("id: first\nid: second\n", Loader=build.UniqueKeyLoader)

    def test_invalid_nested_value_fails_before_render(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["architecture"]["sandbox"] = ["not", "a", "string"]
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            path = Path(directory) / f"{record['id']}.yaml"
            build.validate_record(record, path, set())

    def test_operating_model_claim_names_the_boundary_in_words(self) -> None:
        record = {
            "summary": "An agent.",
            "operating_models": [
                {"scope": "coding task → pull request", "attention_boundary": "work-product-review"}
            ],
        }
        text, _, _ = build.claim_fields(record)["operating_models.0"]
        self.assertEqual(
            text,
            "Level 3 for coding task → pull request; human attention boundary: work-product review.",
        )

    def test_invalid_attention_boundary_fails_before_render(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["operating_models"][0]["attention_boundary"] = "sometimes"
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            path = Path(directory) / f"{record['id']}.yaml"
            build.validate_record(record, path, set())

    def test_featured_must_be_a_boolean(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["featured"] = "yes"
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            path = Path(directory) / f"{record['id']}.yaml"
            build.validate_record(record, path, set())

    def assert_record_error(self, record: dict) -> str:
        stderr = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit),
        ):
            build.validate_record(record, Path(directory) / f"{record['id']}.yaml", set())
        return stderr.getvalue()

    def test_primitive_with_an_unexpected_field_fails(self) -> None:
        # An unquoted comma in a flow mapping splits the description into extra keys.
        record = copy.deepcopy(self.records[0])
        record["primitives"] = [
            {"name": "Wake", "desc": "When an incident is detected", "the bot wakes up": None}
        ]
        message = self.assert_record_error(record)
        self.assertIn(f"{record['id']}.yaml: primitives.0:", message)
        self.assertIn("'the bot wakes up' was unexpected", message)

    def test_schema_errors_name_the_field_path(self) -> None:
        record = copy.deepcopy(self.records[0])
        record["rubric"]["invocation"] = ["batch"]
        message = self.assert_record_error(record)
        self.assertIn(f"{record['id']}.yaml: rubric.invocation.0: 'batch' is not one of", message)

    def test_page_content_state_rules_come_from_the_schema(self) -> None:
        record = copy.deepcopy(
            next(record for record in self.records if record.get("page_content"))
        )
        record["page_content"]["questions"]["validation"] = {
            "state": "not-reviewed",
            "claim_paths": [],
        }
        message = self.assert_record_error(record)
        self.assertIn("page_content.questions.validation: 'note' is a required property", message)

    def test_agent_schema_is_a_valid_draft_7_schema(self) -> None:
        build.Draft7Validator.check_schema(build.AGENT_SCHEMA)

    def test_boundary_levels_cover_every_attention_boundary(self) -> None:
        self.assertEqual(set(build.BOUNDARY_LEVELS), build.schema_values("attentionBoundary"))

    def test_generated_typescript_lists_every_schema_value(self) -> None:
        generated = build.render_schema_values()
        self.assertIn(
            "export const RELATION_TYPE_VALUES = "
            "['component-of', 'built-on', 'successor-of', 'related-to'] as const;",
            generated,
        )
        self.assertIn(
            "export type ClaimProvenance = (typeof CLAIM_PROVENANCE_VALUES)[number];", generated
        )

    def test_every_agent_file_declares_the_schema(self) -> None:
        for path in [*sorted(build.AGENTS_DIR.glob("*.yaml")), ROOT / "templates" / "agent.yaml"]:
            with self.subTest(path=path.name):
                self.assertIn(build.SCHEMA_MODELINE, path.read_text(encoding="utf-8").splitlines())

    def test_schema_document_names_every_schema_value(self) -> None:
        guide = (ROOT / "data" / "schema.md").read_text(encoding="utf-8")
        for name, definition in build.AGENT_SCHEMA["definitions"].items():
            for value in definition.get("enum", []):
                with self.subTest(definition=name, value=value):
                    self.assertIn(f"`{value}`", guide)

    def test_featured_reaches_the_export(self) -> None:
        featured = {
            approach["id"]
            for approach in build.normalize(self.records, self.companies)["approaches"]
            if approach.get("featured")
        }
        self.assertEqual(featured, {"linear-agent", "sierra-pinecone", "stripe-minions"})

    def test_impossible_calendar_date_fails(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build.validate_date("2026-02-31", "last_reviewed_at", "example.yaml")

    def test_json_is_serializable(self) -> None:
        json.dumps(build.normalize(self.records, self.companies))

    def shortest_record(self) -> dict:
        """Give a valid record that omits every field the build can fill."""
        return {
            "id": "fixture-agent",
            "company": self.records[0]["company"],
            "agent_name": "Fixture agent",
            "approach_type": "agent",
            "deployment_stage": "deployed",
            "first_public_evidence": {"date": "2025-11-20", "source_id": "fixture-source"},
            "last_reviewed_at": "2026-09-28",
            "status": "internal",
            "domains": ["coding"],
            "autonomy": "unknown",
            "operating_models": [{"scope": "task to output", "attention_boundary": "unknown"}],
            "rubric": {"invocation": ["unknown"], "evidence_strength": "limited-primary"},
            "summary": "A fixture agent.",
            "key_metrics": [{"id": "ten-runs-a-day", "text": "Ten runs a day."}],
            "sources": [
                {
                    "id": "fixture-source",
                    "title": "Fixture source",
                    "url": "https://example.com/article",
                    "kind": "engineering-blog",
                    "provenance_class": "first-party",
                    "accessed_at": "2026-09-28",
                    "last_verified_at": "2026-09-28",
                }
            ],
            "evidence": {
                "summary": [{"locator": "Paragraph 1"}],
                "key_metrics.ten-runs-a-day": [{"source_id": "fixture-source"}],
                "operating_models.0": [{"relation": "contextualizes", "locator": "Paragraph 2"}],
            },
            "claim_metadata": {
                "operating_models.0": {
                    "confidence": "unverified",
                    "confidence_reason": "The source does not locate human attention.",
                    "valid_at": "2025-11",
                }
            },
        }

    def export_of(self, record: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            build.validate_record(record, Path(directory) / f"{record['id']}.yaml", set())
        return build.normalize([record], self.companies)

    def second_source(self) -> dict:
        return {
            **self.shortest_record()["sources"][0],
            "id": "fixture-source-2",
            "url": "https://example.com/second",
        }

    def test_the_shortest_record_is_valid_and_exports_every_default(self) -> None:
        catalog = self.export_of(self.shortest_record())
        approach = catalog["approaches"][0]
        self.assertEqual(approach["year"], 2025)
        keys = list(approach)
        self.assertEqual(keys.index("year"), keys.index("deployment_stage") + 1)
        source = catalog["sources"][0]
        self.assertEqual(source["canonical_url"], "https://example.com/article")
        self.assertEqual(list(source)[:4], ["id", "title", "url", "canonical_url"])
        claims = {claim["field"]: claim for claim in catalog["claims"]}
        self.assertEqual(
            claims["summary"]["evidence"],
            [{"source_id": "fixture-source", "relation": "supports", "locator": "Paragraph 1"}],
        )
        self.assertEqual(
            claims["key_metrics.ten-runs-a-day"]["evidence"],
            [{"source_id": "fixture-source", "relation": "supports"}],
        )
        self.assertEqual(
            claims["operating_models.0"]["evidence"],
            [
                {
                    "source_id": "fixture-source",
                    "relation": "contextualizes",
                    "locator": "Paragraph 2",
                }
            ],
        )
        self.assertEqual(
            (claims["operating_models.0"]["kind"], claims["operating_models.0"]["provenance"]),
            ("inference", "catalog-judgment"),
        )
        self.assertEqual(
            (
                claims["key_metrics.ten-runs-a-day"]["kind"],
                claims["key_metrics.ten-runs-a-day"]["provenance"],
            ),
            ("metric", "reported"),
        )

    def test_headline_metric_defaults_to_a_reported_metric(self) -> None:
        record = self.shortest_record()
        record["headline_metric"] = "Half of all reviews."
        record["evidence"]["headline_metric"] = [{"locator": "Paragraph 3"}]
        claims = {claim["field"]: claim for claim in self.export_of(record)["claims"]}
        self.assertEqual(
            (claims["headline_metric"]["kind"], claims["headline_metric"]["provenance"]),
            ("metric", "reported"),
        )

    def test_source_provenance_never_supplies_a_confidence_rating(self) -> None:
        for provenance in build.schema_values("provenanceClass"):
            with self.subTest(provenance=provenance):
                record = self.shortest_record()
                record["sources"][0]["provenance_class"] = provenance
                claims = {claim["field"]: claim for claim in self.export_of(record)["claims"]}
                self.assertEqual(claims["summary"]["confidence"], "not-assessed")
                self.assertEqual(
                    claims["summary"]["confidence_reason"],
                    "No explicit confidence assessment is recorded for this claim.",
                )
                self.assertEqual(claims["operating_models.0"]["confidence"], "unverified")

    def test_authored_confidence_requires_a_claim_specific_reason(self) -> None:
        for reason in (None, "", "   "):
            with self.subTest(reason=reason):
                record = self.shortest_record()
                record["claim_metadata"]["summary"] = {"confidence": "high"}
                if reason is not None:
                    record["claim_metadata"]["summary"]["confidence_reason"] = reason
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    self.export_of(record)

    def test_an_explicit_assessment_survives_normalization(self) -> None:
        record = self.shortest_record()
        record["claim_metadata"]["summary"] = {
            "confidence": "high",
            "confidence_reason": "Paragraph 1 describes this internal task directly.",
        }
        claims = {claim["field"]: claim for claim in self.export_of(record)["claims"]}
        self.assertEqual(claims["summary"]["confidence"], "high")
        self.assertEqual(
            claims["summary"]["confidence_reason"],
            record["claim_metadata"]["summary"]["confidence_reason"],
        )

    def test_authored_defaults_give_the_same_export_as_omitted_defaults(self) -> None:
        # The records write year after deployment_stage and canonical_url after url.
        fields = list(self.shortest_record().items())
        explicit = dict(fields[:5] + [("year", 2025)] + fields[5:])
        source = list(explicit["sources"][0].items())
        explicit["sources"][0] = dict(
            source[:3] + [("canonical_url", "https://example.com/article")] + source[3:]
        )
        explicit["evidence"] = {
            "summary": [
                {"source_id": "fixture-source", "relation": "supports", "locator": "Paragraph 1"}
            ],
            "key_metrics.ten-runs-a-day": [{"source_id": "fixture-source", "relation": "supports"}],
            "operating_models.0": [
                {
                    "source_id": "fixture-source",
                    "relation": "contextualizes",
                    "locator": "Paragraph 2",
                }
            ],
        }
        explicit["claim_metadata"]["operating_models.0"] = {
            "kind": "inference",
            "provenance": "catalog-judgment",
            **explicit["claim_metadata"]["operating_models.0"],
        }
        explicit["claim_metadata"]["key_metrics.ten-runs-a-day"] = {
            "kind": "metric",
            "provenance": "reported",
        }
        self.assertEqual(
            json.dumps(self.export_of(explicit), indent=2),
            json.dumps(self.export_of(self.shortest_record()), indent=2),
        )

    def test_a_year_that_differs_from_the_first_public_evidence_fails(self) -> None:
        record = self.shortest_record()
        record["year"] = 2026
        message = self.assert_record_error(record)
        self.assertIn("fixture-agent.yaml: 'year' is 2026", message)
        self.assertIn("'2025-11-20'", message)

    def test_a_link_without_a_source_fails_when_the_record_has_several_sources(self) -> None:
        record = self.shortest_record()
        record["sources"].append(self.second_source())
        record["evidence"]["summary"].append({"source_id": "fixture-source-2"})
        message = self.assert_record_error(record)
        self.assertIn(
            "fixture-agent.yaml: evidence.summary.0 must name a source_id, "
            "because the record has more than one source.",
            message,
        )

    def test_links_in_a_record_with_several_sources_can_name_each_source(self) -> None:
        record = self.shortest_record()
        record["sources"].append(self.second_source())
        for links in record["evidence"].values():
            for link in links:
                link["source_id"] = "fixture-source"
        record["evidence"]["summary"].append({"source_id": "fixture-source-2"})
        claims = {claim["field"]: claim for claim in self.export_of(record)["claims"]}
        self.assertEqual(
            claims["summary"]["evidence"][1],
            {"source_id": "fixture-source-2", "relation": "supports"},
        )

    def test_an_empty_or_relation_only_evidence_link_fails(self) -> None:
        for link in ({}, {"relation": "supports"}):
            with self.subTest(link=link):
                record = self.shortest_record()
                record["evidence"]["summary"] = [link]
                message = self.assert_record_error(record)
                self.assertIn("fixture-agent.yaml: evidence.summary.0:", message)

    def test_operating_model_metadata_rejects_another_kind_or_provenance(self) -> None:
        for field, value, expected in (
            ("kind", "fact", "must be an inference"),
            ("provenance", "reported", "must be a catalog judgment"),
        ):
            with self.subTest(field=field):
                record = self.shortest_record()
                record["claim_metadata"]["operating_models.0"][field] = value
                self.assertIn(expected, self.assert_record_error(record))

    def test_operating_model_metadata_still_requires_the_assessment_fields(self) -> None:
        for field in ("confidence", "confidence_reason", "valid_at"):
            with self.subTest(field=field):
                record = self.shortest_record()
                del record["claim_metadata"]["operating_models.0"][field]
                self.assertIn(f"requires '{field}'", self.assert_record_error(record))

    def test_template_matches_schema(self) -> None:
        template = yaml.safe_load((ROOT / "templates" / "agent.yaml").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "company-agent.yaml"
            build.validate_record(template, path, set())

    def test_documented_sample_counts_are_current(self) -> None:
        patterns = (ROOT / "docs" / "patterns.md").read_text(encoding="utf-8")
        labels = {
            "agent": "Agent",
            "platform": "Platform",
            "agent-system": "Agent family",
            "orchestration-system": "Orchestration system",
            "supporting-pattern": "Supporting pattern",
        }
        counts = Counter(record["approach_type"] for record in self.records)
        for value, label in labels.items():
            self.assertIn(f"| {label} | {counts[value]} |", patterns)


SCHEMA8_FIXTURE = ROOT / "tests" / "fixtures" / "schema8" / "fixture-agent.yaml"
SCHEMA7_CLAIM_IDS = ROOT / "tests" / "fixtures" / "schema7" / "claim-ids.txt"


class SchemaEightTests(unittest.TestCase):
    """Check the schema 8 authored form and export with a hand-written fixture record."""

    company = {
        "id": "fixture",
        "name": "Fixture",
        "homepage": "https://www.fixture.example/",
        "logo": "none",
        "logo_note": "No logo asset has been collected yet.",
    }

    def fixture(self) -> dict:
        return yaml.load(SCHEMA8_FIXTURE.read_text(encoding="utf-8"), Loader=build.UniqueKeyLoader)

    def validate(self, record: dict) -> None:
        build.validate_record(record, SCHEMA8_FIXTURE, set())

    def export_of(self, record: dict, claim_aliases: dict | None = None) -> dict:
        self.validate(record)
        return build.normalize([record], [self.company], claim_aliases)

    def error_of(self, record: dict) -> str:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            self.validate(record)
        return stderr.getvalue()

    def claims_of(self, record: dict) -> dict[str, dict]:
        return {claim["field"]: claim for claim in self.export_of(record)["claims"]}

    def test_the_fixture_is_a_valid_schema_8_record(self) -> None:
        export = self.export_of(self.fixture())
        self.assertEqual(export["schema_version"], 8)
        self.assertEqual(
            list(export),
            ["schema_version", "approaches", "claims", "sources", "companies", "claim_aliases"],
        )
        self.assertEqual(export["claim_aliases"], {})
        self.assertEqual(
            export["approaches"][0]["rubric"],
            {"invocation": ["background"], "evidence_strength": "detailed-primary"},
        )

    def test_claim_ids_and_fields_use_item_ids(self) -> None:
        claim_ids = self.export_of(self.fixture())["approaches"][0]["claim_ids"]
        self.assertIn("fixture-agent--primitives-open-a-run", claim_ids)
        self.assertIn("fixture-agent--key-metrics-forty-prs-a-week", claim_ids)
        self.assertIn("fixture-agent--lessons-learned-gate-before-review", claim_ids)

    def test_primitive_claims_carry_item_id_display_name_and_role(self) -> None:
        claim = self.claims_of(self.fixture())["primitives.test-gate"]
        self.assertEqual(claim["id"], "fixture-agent--primitives-test-gate")
        self.assertEqual(claim["text"], "The test suite must pass before review")
        self.assertEqual(list(claim)[-3:], ["display_name", "item_id", "role"])
        self.assertEqual(
            (claim["display_name"], claim["item_id"], claim["role"]),
            ("Test gate", "test-gate", "validation"),
        )

    def test_metric_claims_carry_their_axes_or_their_alias_target(self) -> None:
        claims = self.claims_of(self.fixture())
        headline = claims["headline_metric"]
        self.assertNotIn("item_id", headline)
        self.assertEqual(list(headline)[-3:], ["category", "basis", "subject"])
        self.assertEqual(headline["category"], "adoption-output")
        canonical = claims["key_metrics.half-merged"]
        self.assertEqual(canonical["text"], "Half of the pull requests merge without change")
        self.assertEqual(list(canonical)[-4:], ["item_id", "category", "basis", "subject"])
        self.assertEqual(canonical["item_id"], "half-merged")
        alias = claims["key_metrics.forty-prs-a-week"]
        self.assertEqual(list(alias)[-3:], ["item_id", "duplicate_of", "reason"])
        self.assertEqual(alias["duplicate_of"], "fixture-agent--headline-metric")
        self.assertEqual(alias["reason"], "Same count and period as the headline.")
        self.assertNotIn("category", alias)
        lesson = claims["lessons_learned.gate-before-review"]
        self.assertEqual(list(lesson)[-1], "item_id")
        self.assertEqual(lesson["item_id"], "gate-before-review")

    def test_the_export_derives_every_question_and_implementation_field(self) -> None:
        page = self.export_of(self.fixture())["approaches"][0]["page_content"]
        self.assertEqual(
            list(page),
            [
                "version",
                "reviewed_at",
                "source_ids",
                "workflow_scope",
                "questions",
                "implementation_fields",
                "aliases",
            ],
        )
        questions = page["questions"]
        self.assertEqual(list(questions), list(build.QUESTION_KEYS))
        self.assertEqual(questions["purpose"], {"state": "reported", "claim_paths": ["summary"]})
        self.assertEqual(
            questions["workflow"]["claim_paths"],
            ["primitives.write-the-change", "primitives.open-a-run"],
        )
        self.assertEqual(
            questions["implementation"]["claim_paths"],
            ["architecture.model", "architecture.harness", "architecture.interfaces"],
        )
        self.assertEqual(
            questions["observations"],
            {
                "state": "reported",
                "claim_paths": [
                    "headline_metric",
                    "key_metrics.forty-prs-a-week",
                    "key_metrics.half-merged",
                ],
                "note": "The talk gives the merge share without a denominator.",
            },
        )
        self.assertEqual(
            questions["lessons"]["claim_paths"], ["lessons_learned.gate-before-review"]
        )
        fields = page["implementation_fields"]
        self.assertEqual(list(fields), list(build.ARCHITECTURE_FIELDS))
        self.assertEqual(
            fields["model"], {"state": "reported", "claim_paths": ["architecture.model"]}
        )
        self.assertEqual(
            fields["harness"],
            {
                "state": "reported",
                "claim_paths": ["architecture.harness"],
                "note": "The talk names the loop but not its version.",
            },
        )
        self.assertEqual(
            fields["sandbox"],
            {
                "state": "not-applicable",
                "claim_paths": [],
                "note": "The agent runs no code of its own.",
            },
        )
        self.assertEqual(fields["tool_access"], {"state": "unreported", "claim_paths": []})
        self.assertEqual(
            fields["credentials"]["note"], "The post names a bot account but not its scope."
        )
        self.assertEqual(
            page["aliases"],
            {
                "key_metrics.forty-prs-a-week": {
                    "duplicate_of": "headline_metric",
                    "reason": "Same count and period as the headline.",
                }
            },
        )

    def test_a_derived_question_that_is_not_reported_exports_no_claim_paths(self) -> None:
        record = self.fixture()
        record["page_content"]["questions"]["lessons"] = {
            "state": "unreported",
            "note": "The lesson is the team's own and does not transfer.",
        }
        page = self.export_of(record)["approaches"][0]["page_content"]
        self.assertEqual(page["questions"]["lessons"]["claim_paths"], [])

    def test_a_reported_derived_question_needs_a_derived_claim(self) -> None:
        record = self.fixture()
        del record["lessons_learned"]
        del record["evidence"]["lessons_learned.gate-before-review"]
        self.assertIn(
            "page_content.questions.lessons is reported, but the record has no claim to derive",
            self.error_of(record),
        )

    def test_reordering_primitives_keeps_every_claim_and_its_evidence(self) -> None:
        def evidence(record: dict) -> dict[str, list]:
            return {claim["id"]: claim["evidence"] for claim in self.export_of(record)["claims"]}

        record = self.fixture()
        before = evidence(copy.deepcopy(record))
        for field in ("primitives", "key_metrics", "lessons_learned"):
            record[field].reverse()
        self.assertEqual(evidence(record), before)

    def test_an_index_path_fails_with_a_clear_message(self) -> None:
        def evidence_key(record: dict) -> None:
            record["evidence"]["primitives.0"] = record["evidence"].pop("primitives.open-a-run")

        def metadata_key(record: dict) -> None:
            record["claim_metadata"]["key_metrics.1"] = record["claim_metadata"].pop(
                "key_metrics.half-merged"
            )

        def workflow_path(record: dict) -> None:
            record["page_content"]["questions"]["workflow"]["claim_paths"] = ["primitives.0"]

        def alias_target(record: dict) -> None:
            record["page_content"]["aliases"]["key_metrics.forty-prs-a-week"]["duplicate_of"] = (
                "key_metrics.1"
            )

        for mutate, where, path in (
            (evidence_key, "evidence", "primitives.0"),
            (metadata_key, "claim_metadata", "key_metrics.1"),
            (workflow_path, "page_content.questions.workflow.claim_paths", "primitives.0"),
            (
                alias_target,
                "page_content.aliases.key_metrics.forty-prs-a-week.duplicate_of",
                "key_metrics.1",
            ),
        ):
            with self.subTest(where=where):
                record = self.fixture()
                mutate(record)
                self.assertIn(
                    f"fixture-agent.yaml: {where} uses the index path {path!r}. "
                    "Name the item by its id instead",
                    self.error_of(record),
                )

    def test_items_need_a_kebab_case_id_and_a_primitive_needs_a_role(self) -> None:
        cases = (
            ("primitives", 0, "id", None, "primitives.0: 'id' is a required property"),
            ("primitives", 0, "role", None, "primitives.0: 'role' is a required property"),
            ("primitives", 0, "role", "helper", "primitives.0.role: 'helper' is not one of"),
            ("primitives", 0, "id", "Open_A_Run", "primitives.0.id: 'Open_A_Run' does not match"),
            ("primitives", 0, "id", "3", "primitives.0.id: '3' does not match"),
            ("key_metrics", 0, "id", None, "key_metrics.0: 'id' is a required property"),
            (
                "lessons_learned",
                0,
                "text",
                None,
                "lessons_learned.0: 'text' is a required property",
            ),
        )
        for field, index, key, value, expected in cases:
            with self.subTest(field=field, key=key, value=value):
                record = self.fixture()
                if value is None:
                    del record[field][index][key]
                else:
                    record[field][index][key] = value
                self.assertIn(f"fixture-agent.yaml: {expected}", self.error_of(record))
        record = self.fixture()
        record["key_metrics"][0] = "40 pull requests a week"
        self.assertIn(
            "fixture-agent.yaml: key_metrics.0: '40 pull requests a week' is not of type 'object'",
            self.error_of(record),
        )

    def test_item_ids_are_unique_within_their_list(self) -> None:
        record = self.fixture()
        record["primitives"][1]["id"] = "open-a-run"
        self.assertIn(
            "fixture-agent.yaml: primitives uses the id 'open-a-run' more than once.",
            self.error_of(record),
        )

    def test_removed_fields_fail(self) -> None:
        def rubric_state(record: dict) -> None:
            record["rubric"]["state"] = "unknown"

        def rubric_identity(record: dict) -> None:
            record["rubric"]["identity"] = "unknown"

        def family(record: dict) -> None:
            record["family_id"] = "fixture-family"

        def archived(record: dict) -> None:
            record["sources"][0]["archived_url"] = (
                "https://web.archive.org/web/1/https://example.com/"
            )

        def roles(record: dict) -> None:
            record["page_content"]["primitive_roles"] = {"primitives.open-a-run": "workflow"}

        def observations(record: dict) -> None:
            record["page_content"]["observations"] = {}

        for mutate, expected in (
            (
                rubric_state,
                "rubric: Additional properties are not allowed ('state' was unexpected)",
            ),
            (
                rubric_identity,
                "rubric: Additional properties are not allowed ('identity' was unexpected)",
            ),
            (
                family,
                "(record): Additional properties are not allowed ('family_id' was unexpected)",
            ),
            (
                archived,
                "sources.0: Additional properties are not allowed ('archived_url' was unexpected)",
            ),
            (
                roles,
                "page_content: Additional properties are not allowed ('primitive_roles' was unexpected)",
            ),
            (
                observations,
                "page_content: Additional properties are not allowed ('observations' was unexpected)",
            ),
        ):
            with self.subTest(expected=expected):
                record = self.fixture()
                mutate(record)
                self.assertIn(f"fixture-agent.yaml: {expected}", self.error_of(record))

    def test_authored_claim_paths_on_a_derived_question_fail(self) -> None:
        for question in build.DERIVED_QUESTIONS:
            with self.subTest(question=question):
                record = self.fixture()
                record["page_content"]["questions"][question]["claim_paths"] = ["summary"]
                self.assertIn(
                    f"fixture-agent.yaml: page_content.questions.{question}.claim_paths is derived "
                    "by the build. Remove it.",
                    self.error_of(record),
                )

    def test_authored_implementation_fields_hold_only_what_the_build_cannot_derive(self) -> None:
        def reported(record: dict) -> None:
            record["page_content"]["implementation_fields"]["model"] = {
                "state": "reported",
                "claim_paths": ["architecture.model"],
            }

        def present_with_a_state(record: dict) -> None:
            record["page_content"]["implementation_fields"]["model"] = {
                "state": "unreported",
                "note": "Fixture.",
            }

        def absent_without_a_state(record: dict) -> None:
            record["page_content"]["implementation_fields"]["knowledge"] = {"note": "Fixture."}

        def unreported_without_a_note(record: dict) -> None:
            record["page_content"]["implementation_fields"]["knowledge"] = {"state": "unreported"}

        for mutate, expected in (
            (
                reported,
                "page_content.implementation_fields.model is derived by the build. Write only "
                "a note for a present architecture field, or a state and a note for an absent one.",
            ),
            (
                present_with_a_state,
                "page_content.implementation_fields.model has a state, but architecture.model "
                "is present, so the build derives reported. Keep only the note.",
            ),
            (
                absent_without_a_state,
                "page_content.implementation_fields.knowledge needs a state, because "
                "architecture.knowledge is absent.",
            ),
            (
                unreported_without_a_note,
                "page_content.implementation_fields.knowledge: 'note' is a required property",
            ),
        ):
            with self.subTest(expected=expected):
                record = self.fixture()
                mutate(record)
                self.assertIn(f"fixture-agent.yaml: {expected}", self.error_of(record))

    def test_every_metric_has_axes_or_is_an_alias(self) -> None:
        def no_axes(record: dict) -> None:
            for key in ("category", "basis", "subject"):
                del record["claim_metadata"]["key_metrics.half-merged"][key]

        def partial_axes(record: dict) -> None:
            del record["claim_metadata"]["headline_metric"]["subject"]

        def alias_with_axes(record: dict) -> None:
            record["claim_metadata"]["key_metrics.forty-prs-a-week"] = {
                "category": "adoption-output",
                "basis": "estimate",
                "subject": "Weekly pull requests",
            }

        def axes_on_a_fact(record: dict) -> None:
            record["claim_metadata"]["summary"] = {"category": "effectiveness"}

        for mutate, expected in (
            (
                no_axes,
                "key_metrics.half-merged needs category, basis, and subject in claim_metadata, "
                "or an entry in page_content.aliases.",
            ),
            (
                partial_axes,
                "headline_metric needs category, basis, and subject in claim_metadata, "
                "or an entry in page_content.aliases.",
            ),
            (
                alias_with_axes,
                "key_metrics.forty-prs-a-week is an alias, so its claim_metadata must not "
                "carry category, basis, or subject.",
            ),
            (
                axes_on_a_fact,
                "claim_metadata.summary may carry category, basis, and subject only on a metric.",
            ),
        ):
            with self.subTest(expected=expected):
                record = self.fixture()
                mutate(record)
                self.assertIn(f"fixture-agent.yaml: {expected}", self.error_of(record))

    def test_alias_targets_are_canonical_metrics_of_the_same_record(self) -> None:
        def aliases(record: dict) -> dict:
            return record["page_content"]["aliases"]

        def self_reference(record: dict) -> None:
            aliases(record)["key_metrics.forty-prs-a-week"]["duplicate_of"] = (
                "key_metrics.forty-prs-a-week"
            )

        def unknown_target(record: dict) -> None:
            aliases(record)["key_metrics.forty-prs-a-week"]["duplicate_of"] = "key_metrics.missing"

        def not_a_metric(record: dict) -> None:
            aliases(record)["summary"] = {"duplicate_of": "headline_metric", "reason": "Fixture."}

        def chain(record: dict) -> None:
            aliases(record)["key_metrics.half-merged"] = {
                "duplicate_of": "key_metrics.forty-prs-a-week",
                "reason": "Fixture chain.",
            }
            for key in ("category", "basis", "subject"):
                del record["claim_metadata"]["key_metrics.half-merged"][key]

        for mutate, expected in (
            (
                self_reference,
                "alias 'key_metrics.forty-prs-a-week' has an invalid duplicate target.",
            ),
            (
                unknown_target,
                "alias 'key_metrics.forty-prs-a-week' has an invalid duplicate target.",
            ),
            (not_a_metric, "page_content.aliases may list only metric claims, found 'summary'."),
            (chain, "alias 'key_metrics.half-merged' may not form a chain or cycle."),
        ):
            with self.subTest(expected=expected):
                record = self.fixture()
                mutate(record)
                self.assertIn(f"fixture-agent.yaml: {expected}", self.error_of(record))

    def test_workflow_lists_every_workflow_primitive_and_only_those(self) -> None:
        for paths in (
            ["primitives.open-a-run"],
            ["primitives.open-a-run", "primitives.write-the-change", "primitives.test-gate"],
        ):
            with self.subTest(paths=paths):
                record = self.fixture()
                record["page_content"]["questions"]["workflow"]["claim_paths"] = paths
                self.assertIn(
                    "workflow claim_paths must name exactly the workflow primitives in reading order.",
                    self.error_of(record),
                )

    def test_claim_aliases_are_embedded_and_must_name_real_claims(self) -> None:
        aliases = {
            "fixture-agent--primitives-0": "fixture-agent--primitives-open-a-run",
            "fixture-agent--summary": "fixture-agent--summary",
        }
        self.assertEqual(self.export_of(self.fixture(), aliases)["claim_aliases"], aliases)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            self.export_of(self.fixture(), {"fixture-agent--primitives-9": "fixture-agent--gone"})
        self.assertIn(
            "data/claim_aliases.json: 'fixture-agent--primitives-9' names unknown claim "
            "'fixture-agent--gone'.",
            stderr.getvalue(),
        )

    def test_claim_aliases_file_must_be_a_map_of_strings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claim_aliases.json"
            path.write_text('{"a--primitives-0": "a--primitives-one"}\n', encoding="utf-8")
            self.assertEqual(
                build.load_claim_aliases(path), {"a--primitives-0": "a--primitives-one"}
            )
            for text, expected in (
                ('["a"]', "data/claim_aliases.json: 'claim aliases' must contain a JSON object."),
                ('{"a": 1}', "data/claim_aliases.json must map each old claim ID to a claim ID."),
            ):
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
                        build.load_claim_aliases(path)
                    self.assertIn(expected, stderr.getvalue())

    def test_a_capture_manifest_may_keep_an_external_archive_url(self) -> None:
        source = {
            "id": "fixture-source",
            "title": "Fixture source",
            "url": "https://example.com/article",
            "kind": "engineering-blog",
            "provenance_class": "first-party",
            "accessed_at": "2026-08-31",
            "last_verified_at": "2026-08-31",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "archive" / "sources" / "fixture-source"
            bundle.mkdir(parents=True)
            content = b"# Preserved\n"
            (bundle / "content.md").write_bytes(content)
            manifest = {
                "schema_version": 1,
                "source_id": "fixture-source",
                "original_url": source["url"],
                "final_url": source["url"],
                "captured_at": "2026-08-31T12:34:56Z",
                "http_status": 200,
                "tool": {"name": "steel", "version": "0.4.4"},
                "artifacts": {
                    "markdown": {
                        "path": "archive/sources/fixture-source/content.md",
                        "sha256": f"sha256:{hashlib.sha256(content).hexdigest()}",
                        "bytes": len(content),
                    }
                },
                "external_archive_url": "https://web.archive.org/web/1/https://example.com/article",
            }
            (bundle / "metadata.json").write_text(json.dumps(manifest), encoding="utf-8")
            source["capture"] = {"manifest_path": "archive/sources/fixture-source/metadata.json"}
            with mock.patch.object(build, "ROOT", root):
                self.assertEqual(build.load_capture_manifest(source, "fixture.yaml"), manifest)

    def test_autonomy_must_not_contradict_a_single_operating_model(self) -> None:
        for autonomy, boundary in (
            ("drafts-reviewed", "work-product-review"),
            ("drafts-reviewed", "outcome-review"),
            ("autonomous", "exception-only"),
            ("human-in-loop", "continuous-steering"),
            ("human-in-loop", "work-product-review"),
            ("assistive", "continuous-steering"),
            ("unknown", "exception-only"),
            ("assistive", "unknown"),
        ):
            with self.subTest(autonomy=autonomy, boundary=boundary):
                record = self.fixture()
                record["autonomy"] = autonomy
                record["operating_models"][0]["attention_boundary"] = boundary
                self.validate(record)
        for autonomy, boundary in (
            ("autonomous", "work-product-review"),
            ("assistive", "exception-only"),
            ("drafts-reviewed", "continuous-steering"),
            ("human-in-loop", "outcome-review"),
        ):
            with self.subTest(autonomy=autonomy, boundary=boundary):
                record = self.fixture()
                record["autonomy"] = autonomy
                record["operating_models"][0]["attention_boundary"] = boundary
                self.assertIn(
                    f"fixture-agent.yaml: autonomy {autonomy!r} contradicts the attention "
                    f"boundary {boundary!r} of the only operating model.",
                    self.error_of(record),
                )

    def test_autonomy_is_not_compared_when_a_record_has_several_operating_models(self) -> None:
        record = self.fixture()
        record["autonomy"] = "autonomous"
        record["operating_models"].append(
            {"scope": "second workflow", "attention_boundary": "exception-only"}
        )
        record["evidence"]["operating_models.1"] = [
            {"source_id": "fixture-agent-source-1", "locator": "Paragraph 7"}
        ]
        record["claim_metadata"]["operating_models.1"] = {
            "confidence": "low",
            "confidence_reason": "Fixture.",
            "valid_at": "2026-03",
        }
        self.validate(record)

    def test_generated_typescript_keeps_the_values_the_site_needs(self) -> None:
        generated = build.render_schema_values()
        for constant in (
            "PRIMITIVE_ROLE_VALUES",
            "OBSERVATION_CATEGORY_VALUES",
            "OBSERVATION_BASIS_VALUES",
            "REVIEW_STATE_VALUES",
        ):
            self.assertIn(f"export const {constant} = ", generated)
        for constant in ("RUBRIC_STATE_VALUES", "IDENTITY_VALUES"):
            self.assertNotIn(constant, generated)

    def test_landscape_renders_items_by_id_without_state_or_identity(self) -> None:
        record = self.fixture()
        self.validate(record)
        landscape = build.render_landscape([record])
        self.assertIn(
            "- Open a run: An issue label starts a run <small>Sources: [fixture-agent-source-1]",
            landscape,
        )
        self.assertIn("- 40 pull requests a week <small>Sources:", landscape)
        self.assertNotIn("| State |", landscape)
        self.assertNotIn("| Identity |", landscape)


if __name__ == "__main__":
    unittest.main()
