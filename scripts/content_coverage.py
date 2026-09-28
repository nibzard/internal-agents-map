# ABOUTME: Reports editorial question coverage without turning it into a score.
# ABOUTME: Uses the catalog builder's validated authored records as its source.
"""Validate and export the optional page-content review contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build


def coverage(records: list[dict]) -> dict:
    entries = []
    for record in sorted(records, key=lambda item: item["id"]):
        page = record.get("page_content")
        if page is None:
            entries.append({"id": record["id"], "format_status": "legacy-unassessed"})
            continue
        exported = build.page_content_export(record)
        questions = {
            key: {
                "state": value["state"],
                "note": value.get("note"),
                "claim_paths": value["claim_paths"],
            }
            for key, value in exported["questions"].items()
        }
        architecture = {
            key: {
                "state": value["state"],
                "note": value.get("note"),
                "claim_paths": value["claim_paths"],
            }
            for key, value in exported["implementation_fields"].items()
        }
        pending = [
            f"questions.{key}"
            for key, value in questions.items()
            if value["state"] == "not-reviewed"
        ] + [
            f"implementation_fields.{key}"
            for key, value in architecture.items()
            if value["state"] == "not-reviewed"
        ]
        observations = build.metric_paths(record)
        entries.append(
            {
                "id": record["id"],
                "format_status": "page-content-v1",
                "reviewed_at": page["reviewed_at"],
                "reviewed_source_ids": page["source_ids"],
                "unreviewed_source_ids": [
                    source["id"]
                    for source in record["sources"]
                    if source["id"] not in page["source_ids"]
                ],
                "questions": questions,
                "implementation_fields": architecture,
                "next_actions": pending,
                "raw_observation_count": len(observations),
                "canonical_observation_count": sum(
                    path not in exported["aliases"] for path in observations
                ),
            }
        )
    return {"format_version": 1, "entries": entries}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="validate records and coverage metadata"
    )
    parser.add_argument("--output", type=Path, help="write deterministic JSON coverage output")
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error("choose --check and/or --output")
    records = build.load_agents()
    result = coverage(records)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    if args.check:
        print(f"coverage valid for {len(records)} entries")


if __name__ == "__main__":
    main()
