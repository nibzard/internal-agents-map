# ABOUTME: Resolves shared source captures without changing their original identity.
# ABOUTME: Mirrors and translations keep their own captures even when they cite an original.
"""Resolve explicit source aliases in authored records and normalized exports."""

from collections.abc import Mapping


def validate_source_aliases(sources: Mapping[str, dict]) -> None:
    """Reject missing targets and cycles, including aliases with their own captures."""
    for source_id in sources:
        seen: set[str] = set()
        current = source_id
        while current:
            if current in seen:
                raise ValueError(
                    f"Source {source_id!r}: duplicate_of forms a cycle at {current!r}."
                )
            seen.add(current)
            if current not in sources:
                raise ValueError(f"Source {source_id!r}: unknown duplicate_of source {current!r}.")
            current = sources[current].get("duplicate_of")


def capture_source(source: dict, sources: Mapping[str, dict]) -> dict | None:
    """Find a capture for an explicit alias of the same publisher URL and version.

    An author uses duplicate_of to identify the same source version. A different URL
    can identify a translation or mirror; its text needs its own reviewed capture.
    """
    current = source
    seen: set[str] = set()
    while current["id"] not in seen:
        seen.add(current["id"])
        if current.get("capture"):
            return current
        original = sources.get(current.get("duplicate_of"))
        if original is None or original["url"] != source["url"]:
            return None
        current = original
    return None
