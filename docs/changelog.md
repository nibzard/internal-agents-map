# Catalog schema changelog

This document records the changes to the published catalog (`data/agents.json`,
`/agents.json`) and to the compact index (`/agents/index.json`). [data/schema.md](../data/schema.md)
describes the current schema.

## Catalog schema 8 / compact index 4

Methodology updates within schema 8:

- Missing claim confidence now exports as `not-assessed`, with an explicit reason, instead
  of receiving a rating from source provenance. Authored ratings require a reason and retain
  their value until their evidence is reviewed.
- A source alias with the same original URL can inherit the capture of its `duplicate_of`
  target. The resolved manifest retains its original identity and timestamp.
- The “In depth” badge requires a completed source and page-content review. Low confidence,
  reviewed gaps, and questions that do not apply no longer disqualify a record by themselves.

Schema 8 gives each list item a stable ID, so that a claim keeps its evidence when a list
changes order. Before schema 8, a claim path such as `primitives.3` used the position of
the item. A reordered list kept every reference valid but attached the evidence to a
different statement.

Changes to the authored record (`data/agents/*.yaml`):

- `primitives[]` items require `id` and `role` (`workflow`, `mechanism`, or `validation`).
- `key_metrics[]` and `lessons_learned[]` change from lists of strings to lists of
  `{id, text}` maps.
- Claim paths in `evidence`, `claim_metadata`, and `page_content` use the item ID:
  `primitives.<id>`, `key_metrics.<id>`, and `lessons_learned.<id>`. The build refuses an
  index path.
- `claim_metadata` of a metric carries `category`, `basis`, and `subject`.
- `page_content.observations` is renamed `page_content.aliases` and keeps only the
  `duplicate_of` entries. The `category`, `basis`, and `subject` of the other entries
  move to `claim_metadata`.
- `page_content.primitive_roles` is removed. The role is on each primitive.
- `page_content.questions.<q>.claim_paths` is removed for `purpose`, `implementation`,
  `observations`, and `lessons`. The build derives them.
- `page_content.implementation_fields` keeps only a note for a present field, or a state
  and a note for an absent field. The build derives `reported` and `unreported`.
- `rubric.state` and `rubric.identity` are removed. The site did not read them, and 39 and
  50 of the 66 records had the value `unknown`.
- `family_id` is removed. No record used it.
- Source `archived_url` is removed. No record used it, and the capture bundle keeps the
  preserved copy. The build no longer compares a manifest `external_archive_url` with it.

Changes to the export:

- `schema_version` is 8.
- A claim `field` uses the item ID, and the claim `id` follows it, for example
  `github-qubot--primitives-start-a-qubot-run` instead of `github-qubot--primitives-0`.
- Primitive claims carry `item_id`, `display_name`, and `role`. Key metric and lesson
  claims carry `item_id`. A canonical metric claim carries `category`, `basis`, and
  `subject`. An alias metric claim carries `duplicate_of` (a claim ID) and `reason`.
- The top-level `claim_aliases` maps every schema 7 claim ID to its schema 8 claim ID. It
  stays for one release.
- `approaches[].page_content` carries all seven questions with derived claim paths, all
  eight `implementation_fields` with derived states, and `aliases`. It carries no
  `primitive_roles` and no `observations`.
- `approaches[].rubric` carries only `invocation` and `evidence_strength`.
- The compact index is schema 4, with the same rubric change.

## Catalog schema 7 / compact index 3

The build derives `catalog_section`: `agent` and `agent-system` become `agents`;
`platform`, `supporting-pattern`, and `orchestration-system` become `infrastructure`.
Do not author this field. Unknown structural types fail validation. Existing fields,
IDs, claim anchors, and detail URLs remain available. `/agents.json` and
`/agents/index.json` retain their historical names and include both collections.
Consumers must select `catalog_section` explicitly for agent counts or comparisons.
One agent family counts once, not as an estimated number of constituent agents.

`/` and `/index.md` represent Agents. `/infrastructure` and `/infrastructure.md`
represent Infrastructure. `/?collection=all` shows two labeled groups. Legacy
infrastructure type queries on `/` switch to All while retaining OR filters.
Seven `page_content.questions` keys remain the common evidence contract; HTML and
Markdown apply collection profiles without changing evidence or hiding unknowns.

## Catalog schema 6 / compact index 3

Schema 6 replaces the old `task-agent` and `background-agent` approach types with
`agent`. Consumers that used those values should filter structural type with
`approach_type: agent` and use `rubric.invocation` to distinguish interactive,
background, scheduled, and event-driven operation. The compact index schema is 3.
