# ABOUTME: Checks explicit source reuse without merging different evidence versions.
# ABOUTME: Shared captures retain their owner, while mirrors and new captures stay separate.

import unittest

from scripts.source_refs import capture_source, validate_source_aliases


class SourceAliasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = {
            "id": "original",
            "url": "https://example.com/article",
            "capture": {"manifest_path": "archive/sources/original/metadata.json"},
        }
        self.alias = {
            "id": "alias",
            "url": self.original["url"],
            "duplicate_of": "original",
        }
        self.sources = {"original": self.original, "alias": self.alias}

    def test_alias_chains_resolve_to_the_capture_owner(self) -> None:
        second = {**self.alias, "id": "second", "duplicate_of": "alias"}
        self.sources["second"] = second
        validate_source_aliases(self.sources)
        self.assertIs(capture_source(second, self.sources), self.original)

    def test_identical_urls_without_an_alias_do_not_share_captures(self) -> None:
        self.alias.pop("duplicate_of")
        self.assertIsNone(capture_source(self.alias, self.sources))

    def test_mirrors_and_translations_do_not_inherit_a_capture(self) -> None:
        for url in ("https://mirror.example/article", "https://example.com/article?lang=fr"):
            with self.subTest(url=url):
                self.alias["url"] = url
                self.assertIsNone(capture_source(self.alias, self.sources))

    def test_an_alias_own_capture_takes_precedence(self) -> None:
        self.alias["capture"] = {"manifest_path": "archive/sources/alias/metadata.json"}
        self.assertIs(capture_source(self.alias, self.sources), self.alias)

    def test_missing_alias_targets_fail_validation(self) -> None:
        self.alias["duplicate_of"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown duplicate_of source 'missing'"):
            validate_source_aliases(self.sources)

    def test_cycles_fail_even_when_a_source_has_its_own_capture(self) -> None:
        for target in ("alias", "original"):
            with self.subTest(target=target):
                self.original["duplicate_of"] = target
                with self.assertRaisesRegex(ValueError, "forms a cycle"):
                    validate_source_aliases(self.sources)
