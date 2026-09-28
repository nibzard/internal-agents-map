# Plan 018: Simplify the record schema without losing the evidence chain

Status: PROPOSED on 2026-09-28. No execution requested.

## Why this plan exists

Three independent reviews of the catalog data model reached the same conclusion:
the research standard is sound, and the record format around it repeats one fact
in several places. This plan checks their claims against the 66 records on `main`
and turns the parts that hold into a sequenced change.

## What the reviews got right (checked against the data)

| Claim | Result |
| --- | --- |
| `page_content.questions.purpose` always equals `[summary]` | 66 of 66 |
| `questions.lessons` always equals every `lessons_learned.*` | 66 of 66 |
| `questions.observations` equals the headline and every key metric | 64 of 66 |
| Reported `implementation_fields.<k>` always points to `architecture.<k>` | 314 of 314 |
| `relation: supports` on evidence links | 1257 of 1299 |
| Records with a single source | 40 of 66 |
| `operating_models.*` metadata is always `inference` / `catalog-judgment` | 84 of 84 |
| `rubric.state` unknown / `rubric.identity` unknown | 39 and 50 of 66 |
| Nothing in `src/` reads `rubric.state` or `rubric.identity` | confirmed; only `evidence_strength` and `invocation` are read |
| `canonical_url` equals `url` | 138 of 138 |
| `archived_url`, `family_id` used | 0 and 0 |
| `year` differs from the year of `first_public_evidence.date` | 2 (`openai-sevbot`, `openai-software-factory`); both look like errors |
| Architecture fields set to `unknown` or `Not specified` | 19 and 5 |
| Architecture fields with a value and state `unreported` at the same time | 34 |
| Observation entries that only say `duplicate_of` | 33 |
| Placeholder architecture values become claims with a confidence | 26 (6 `high`, 19 `medium`, 1 `low`) |

## Where the reviews overstate

- `questions.workflow` is not always the list of workflow primitives. In 6 records
  (`block-builderbot`, `linear-agent`, `openai-sevbot`, `openai-software-factory`,
  `posthog-stamphog`, `uber-ureview`) the question reorders the primitives into
  reading order. That order is real editorial content and must survive.
- The page states `not-applicable` and `unreported` on `human_involvement` (14 and 14
  records) carry information that no other field holds. The seven-question view is not
  pure duplication; only its `claim_paths` are.
- The third review wants observations split into typed values with comparators and
  units. `claim_metadata` already allows `value`, `unit`, `denominator`, and
  `measurement_method`. The gap is authoring discipline, not schema. Do not add a
  second metric model.
- The second review reports placeholder claims at `high` confidence. Most are
  `medium`. The defect is that a placeholder becomes a claim at all.

## The one structural defect worth a schema bump

Positional claim paths (`primitives.3`, `key_metrics.2`) are used by `evidence`,
`claim_metadata`, and `page_content`, and they form the public claim IDs
(`<record>--primitives-3`). Reordering a list keeps every reference valid while
attaching evidence to the wrong statement. No validator can catch that. This is the
only change below that alters the public export shape, so it sets the schema bump.

## Changes, in order

Each step is a separate pull request with its own verification. Steps 1 and 2 leave
`data/agents.json` byte-identical. Step 3 bumps the catalog schema to 8.

### Step 1: defaults the build can fill (no export change)

- `relation` defaults to `supports`.
- `source_id` on an evidence link defaults to the record's only source when it has
  one; the build refuses the omission when a record has several sources.
- `claim_metadata.operating_models.*` needs only `confidence`, `confidence_reason`,
  and `valid_at`; `kind` and `provenance` are fixed by the schema and filled in.
- `claim_metadata.key_metrics.*` and `headline_metric` default to `kind: metric`,
  `provenance: reported`, which `claim_fields()` already assumes.
- `year` is derived from `first_public_evidence.date`. Fix the two records that
  disagree in the same change; check each against its capture first.
- `canonical_url` becomes optional and defaults to `url`.
- Add a migration script that rewrites every record to the shortest form and prove
  with `scripts/build.py --check` that the export does not change.

### Step 2: one way to say unknown (no export change)

- An architecture field is either present with a reported value or absent. Delete the
  strings `unknown`, `Not specified`, and their variants (24 values across 66
  records); the schema forbids them afterwards. The `sandbox: unknown` convention in
  `data/schema.md` goes with them.
- The build stops creating a claim for an absent field, so the 26 placeholder claims
  and their default confidence disappear.
- `implementation_fields.<k>` may be `reported` only when `architecture.<k>` exists,
  and `unreported` only when it does not. Today 34 records violate this. The
  coverage checker enforces it.

### Step 3: stable IDs and inline roles (schema 8)

- Every `primitives`, `key_metrics`, and `lessons_learned` item gets an `id`
  (kebab-case, unique within the record). `key_metrics` and `lessons_learned` change
  from lists of strings to lists of `{id, text}` maps.
- Evidence, claim metadata, and page-content paths use the ID: `primitives.pr-babysitting`,
  `key_metrics.sessions-created`. The public claim ID becomes `<record>--primitives--pr-babysitting`.
- The migration script assigns an ID from the current name or first words, writes the
  old claim ID into a `claim_aliases` map in the export for one release, and the site
  keeps the old anchors as redirect targets.
- `role` (`workflow`, `mechanism`, `validation`) moves onto each primitive.
  `page_content.primitive_roles` is deleted.
- `category`, `basis`, and `subject` move into `claim_metadata` of each metric.
  `page_content.observations` keeps only the `duplicate_of` entries, renamed
  `aliases`.
- `page_content.questions` keeps `state`, `note`, and `workflow_scope`. `claim_paths`
  are allowed only where they add information: the workflow reading order, and a
  `human_involvement` or `validation` answer that cites specific items. The build
  derives `purpose`, `implementation`, `observations`, and `lessons` paths.
- `page_content.implementation_fields` keeps only entries whose state is not derivable:
  `not-applicable` and `not-reviewed`, plus `unreported` entries that carry a note.
- Delete `rubric.state`, `rubric.identity`, `family_id`, and `archived_url` from the
  schema and the records. Record the reason in `data/schema.md`.
- Keep `autonomy` for now. It is shown on every entry page and in the Markdown
  export. Add a build check that a record with one operating model does not
  contradict it (the 27 `drafts-reviewed` / `work-product-review` pairs agree; the
  16 `unknown` / `unknown` pairs agree). Deriving it is a later decision.

### Step 3 export contract (schema 8)

Authored record:

- `primitives[]`: each item has `id` (kebab-case, unique in the record), `name`, `desc`,
  and `role` (`workflow`, `mechanism`, or `validation`).
- `key_metrics[]` and `lessons_learned[]`: lists of `{id, text}` maps.
- Claim paths everywhere (`evidence`, `claim_metadata`, `page_content`) use
  `primitives.<id>`, `key_metrics.<id>`, `lessons_learned.<id>`. Index paths are
  rejected.
- `claim_metadata.<metric path>` may carry `category`, `basis`, and `subject`
  (the values that `page_content.observations` carried). Every headline and key
  metric must carry them, or be listed as an alias.
- `page_content.aliases`: map of metric path to `{duplicate_of, reason}`. Replaces
  `page_content.observations`. `page_content.primitive_roles` is removed.
- `page_content.questions.<q>.claim_paths` is authored only for `workflow`,
  `human_involvement`, and `validation`, and may be omitted when it is empty. The
  build derives `purpose` (summary), `implementation` (every present architecture
  field, in the entry-page field order), `observations` (headline, then every key
  metric in record order, aliases included), and `lessons` (every lesson). A derived
  question gets these paths only when its authored state is `reported`; otherwise its
  paths are empty. Authoring a `claim_paths` on those four is rejected.
- `page_content.implementation_fields` lists only what the build cannot derive: a
  `note` alone for a present architecture field, or a `state` (`unreported`,
  `not-applicable`, or `not-reviewed`) and a `note` for an absent one. The build
  derives `reported` for every present architecture field and `unreported` for the
  rest. An authored `state: reported` or `claim_paths` is rejected.
- `rubric.state`, `rubric.identity`, `family_id`, and source `archived_url` are
  removed from the schema.

Export (`data/agents.json`, `schema_version: 8`):

- Claim `id` keeps the shape `<record>--<path with dots and underscores as dashes>`,
  so `github-qubot--primitives-start-a-qubot-run`. Claim `field` is the ID path.
- Primitive claims carry `item_id`, `display_name`, and `role`. Metric and lesson
  claims carry `item_id`. Metric claims carry `category`, `basis`, and `subject`
  when they are canonical, or `duplicate_of` (a claim ID) and `reason` when they
  are aliases.
- Top-level `claim_aliases`: map of every schema 7 claim ID to its schema 8 claim
  ID. Kept for one release. The site resolves an old anchor through it.
- `page_content` in the export carries all seven `questions` with their full
  derived `claim_paths`, all eight `implementation_fields` with derived states,
  and `aliases`. It carries no `primitive_roles` and no `observations`.
- `approaches[].rubric` has only `invocation` and `evidence_strength`.
- The compact index (`/agents/index.json`) becomes schema 4 with the same rubric
  change.

### Step 4: documentation

- Move the migration paragraphs ("Schema 6 replaces…", "catalog 7 / compact index 3")
  from `data/schema.md` into `docs/changelog.md`.
- Update `templates/agent.yaml`, `CONTRIBUTING.md`, and the add-agent skill to the
  shortest form.

## What this plan does not do

- It does not replace YAML, add a knowledge graph, or introduce a second metric model.
- It does not drop claim-to-source-to-locator links or the append-only captures.
- It does not change `deployment_stage` or `status`, even though `deployment_stage`
  is `deployed` or `scaled` in 65 of 66 records. Low variance is not a defect.

## Expected effect

The median record is 279 lines. Steps 1 and 2 remove the repeated defaults and
placeholder values. Step 3 removes `primitive_roles`, most of `observations`, and
most `claim_paths`. The estimate from the review tables is a 30 to 40 percent
reduction in lines with no loss of evidence, and one place to edit when a statement
changes.

## Verification gates

- After each step: `uv run python scripts/build.py --check`,
  `uv run --locked python scripts/content_coverage.py --check`, the Python and web
  test suites, and the e2e entry-page spec.
- Step 3 adds a test that reorders the primitives of a fixture record and asserts
  that every claim keeps its evidence.
- Step 3 adds a test that every pre-migration claim ID resolves through
  `claim_aliases`.

## STOP conditions

- Stop before Step 3 if any consumer of `data/agents.json` outside this repository
  is identified. None is documented today.
- Stop if the migration script cannot assign a unique ID to an item without a
  hand-written override for more than 10 percent of items.
