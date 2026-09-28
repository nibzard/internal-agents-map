# Contributing to Internal Agents Map

Contributions can add an approach, add a source, correct a claim, or improve the analysis.

The catalog favors broad collection and explicit provenance. Do not invent missing details. Use `unknown` when a required classification or rubric value has not been established. Omit an optional field, such as an architecture field, that no source documents; do not write a placeholder value. Use review states to distinguish missing reporting from unfinished review. Keep commentary and conflicting evidence, but label them.

The catalog is public. Do not add personal contact data, such as e-mail addresses or private notes about people, to any file. Only public sources belong here. CI rejects e-mail addresses in tracked files.

## Inclusion rules

This section is the shared inclusion policy for the catalog and its intake skill.
Include a case when public evidence answers these questions:

1. Which organization uses it, and for what internal work?
2. What did that organization build or materially adapt?
3. What implementation or use does the source describe?

Material adaptation means a documented change for the organization's work, such as internal
tool connections, company context, workflow logic, or controls. Buying licenses or reporting
adoption alone is insufficient. No minimum amount of custom code is required.

An agent or an implemented system that supports agents can qualify. Label its approach type.
General model-serving infrastructure without a documented agent workflow is out of scope.
Research implementations and prototypes can qualify; label their deployment stage accurately.

A system does not need a product name. Use a descriptive label when the workflow is identifiable.
Commercial and open-source systems can qualify, including an organization's own product.
Apply the same evidence requirements to all cases. A product announcement alone is insufficient.

Prefer original sources. Outside reporting can support a case when it answers the questions
above with attributed evidence. Record source provenance and assess support for each claim.
Rumors and unattributed claims do not establish eligibility.

### Intake decisions

- **Add:** The evidence meets the inclusion rules and no record exists.
- **Update:** The system already has a record. Link new evidence to that record.
- **Needs evidence:** A required fact is unclear. Record the missing fact or source.
- **Out of scope:** The documented work does not meet the inclusion rules. State which rule fails.

Classify the submitted case, not every system the organization might have. An adoption-only
story is out of scope as submitted. Use Needs evidence when the source describes a possible
internal build but leaves a required fact unclear. New evidence can reopen either decision.

Keep eligibility separate from execution. A source capture or validation failure blocks the
change; it does not establish that the case is out of scope. Record the blocker without changing
a supported eligibility decision. Do not add a case based on search snippets or remembered text.

### Agent-assisted intake

The [intake skill](.claude/skills/add-agent-from-url/SKILL.md) applies these rules to source URLs.
A request to assess a case produces an assessment. A request to add or update it authorizes the
corresponding local edits. Commit and publication actions follow the user's authorization.

Review whether sources support the claims before adding them. Automated checks validate record
structure, source-file integrity, and links; they do not confirm reported results or interpretations.
Agreement between reviewing agents is not independent evidence.

## Set up the project

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Install the Node.js version in [.node-version](.node-version).
3. Run `uv sync --locked`.
4. Run `npm ci`.
5. Run `uv run python scripts/build.py --check`.
6. Run `uv run python -m unittest discover -s tests`.

uv installs the required Python version and manages the project environment. You do not need to
create or activate a virtual environment yourself. Python validates the research data and writes
the repository documents. Node builds the website.

## Add an approach

1. Copy `templates/agent.yaml` to `data/agents/<id>.yaml`.
2. Give the record a kebab-case ID that matches its file name.
3. Classify structural type and invocation separately. Structural type describes the system;
   invocation describes how work starts or proceeds. Use `unknown` when the sources do not
   document an invocation mode.
4. Add a scoped `operating_models` assessment. Record where human attention normally returns,
   not a company-wide maturity estimate. Keep attention separate from tool authority,
   publication permission, and how long the run can proceed unattended.
5. Add structured source records before you summarize them. Write `canonical_url` only when
   it is different from `url`.
6. Preserve each accepted source while it is still live:
   `uv run python scripts/archive_sources.py --source-id <source-id>`. Review the captured
   Markdown, then add the emitted `capture` field to the source record.
7. Give every primitive, key metric, and lesson a kebab-case `id` that is unique in its list.
   Give each primitive a `role`: `workflow`, `mechanism`, or `validation`. A claim path names
   the item by its ID, such as `primitives.open-a-run` or `key_metrics.weekly-runs`.
8. Link every claim path to evidence. Add a locator when the source has a stable section,
   timestamp, comment ID, commit, or line. When the record has only one source, write
   `source_id` on a link only if the link has no locator. Write `relation` only for `contradicts` or `contextualizes`; the
   default is `supports`.
9. Do not write the values that the build derives: `year`, `catalog_section`, and a `kind` or
   `provenance` that is equal to its default. See [claim evidence](data/schema.md#claim-evidence).
10. Run `uv run python scripts/build.py`.
11. Run all verification commands in the pull request template.

Apply the [inclusion rules](#inclusion-rules) before writing a record.

A new organization also needs a record in `data/companies.yaml`; the build fails until the registry holds it. See the [company registry rules](data/schema.md#company-registry).

## Add a company logo

1. Edit the organization's record in `data/companies.yaml`.
2. Put the asset at `public/logos/<id>.svg` or `public/logos/<id>.png`. The file stem must equal the record `id`.
3. Replace `logo: none` and its `logo_note` with the logo mapping: `file`, `source_url`, and `accessed_at`.
4. Prefer an SVG from the organization's own brand or press page. Keep `logo: none` with a reason in `logo_note` when no usable asset exists or the terms are unclear.
5. Run `uv run python scripts/build.py`. It checks the file limits and the SVG safety rules, then records the derived size, bytes, and hash in the catalog output.

Each logo is the trademark of its owner. The [schema](data/schema.md#company-registry) lists the file limits.

## Add a source or commentary

Sources can include:

- Company articles and documentation
- Source code, repositories, releases, and commits
- Talks, transcripts, podcasts, and papers
- News reports and case studies
- Social posts
- Hacker News threads and material comments
- Other forum discussions

Set `kind` to the source format. Set `provenance_class` to the publisher relationship. These fields do not state whether a claim is true.

Use `first-party` for organization publications. Use `direct-participant` for a statement from a person who worked on the system. Use `independent-secondary` for outside reporting. Use `community` for Hacker News and forum commentary.

A commentary source can contextualize or contradict a claim. It does not need to support one. Use the corresponding evidence relation.

For Hacker News, keep the thread and each material comment as separate source records. Use the permanent item or comment URL. For source code, record a commit and file locator when possible.

### Preserve a source

The original `url` remains the catalog citation. The preservation command creates a reviewed,
append-only Steel Markdown capture. With `--save-wayback`, it also records any existing or
newly created Wayback URL as `external_archive_url` in the capture manifest:

```bash
uv run python scripts/archive_sources.py --source-id <source-id>
```

Add `--pdf` only when visual layout materially supports a claim. Add `--save-wayback` when Save
Page Now credentials are configured in the environment. Never put archive credentials in source
records, command arguments, logs, or pull requests.

The command refuses authenticated/private pages, explicit `noarchive` directives, error pages,
and existing bundles. Review `archive/sources/<source-id>/content.md` before linking the capture
from YAML. See the [source-preservation policy](docs/source-preservation.md) for ownership,
retention, and takedown rules.

When another record already preserves the same source version, set `duplicate_of` to that
source ID. An exact match on the original URL lets the build reuse its capture, with the
original manifest and timestamp intact. Mirrors, translations, and changed versions need
their own captures.

## Write claims and analysis

- Use quotation marks only for exact source text.
- Mark company metrics as self-reported unless an independent source verifies them.
- Include a metric date, scope, denominator, and method when available.
- Mark editorial conclusions as `inferred` or `catalog-judgment`.
- Preserve conflicting reports when they refer to different dates or methods.
- Do not treat an undocumented field as evidence that a feature is absent.
- Assess confidence for each claim, with a reason tied to its evidence. Use `high` for
  direct, specific support, `medium` when a material qualification or inference remains,
  `low` for ambiguous or conflicting support, and `unverified` when support is insufficient.
  Omitted confidence becomes `not-assessed`; publisher identity never supplies a rating.
  Confidence in a report's attribution does not independently verify its outcome.
- Never assign an operating level without naming the workflow scope. Treat it as a dated catalog judgment, not a reported company fact.
- Review each lesson against a specific source passage. Describe a reported practice as
  `fact`/`reported`, attribute a team's preference as `opinion`/`reported`, and reserve
  `inference`/`catalog-judgment` for an actual catalog inference.
- Explain what supports that particular claim in `confidence_reason`, including the
  unresolved step when there is one. Rewording a shared disclaimer is not a review.
  Add a locator to the supporting passage and keep advice bounded to its reported case.
- When adopting `page_content`, read every listed source and give a state to all seven
  reader questions. Use `reported`, `unreported`, `not-applicable`, or `not-reviewed` as
  defined in `data/schema.md`; keep a next action for unfinished review. Write
  `claim_paths` only for `workflow`, `human_involvement`, and `validation`; the build
  derives the paths of the other four questions.
- Review all eight architecture fields against the same sources. The build makes a present
  field `reported` and an absent field `unreported`. Write an `implementation_fields` entry
  only for a note on a present field, or for a `state` and `note` on an absent field.
- Give the headline and each key metric a `category`, `basis`, and `subject` in its
  `claim_metadata`, or list the metric under `page_content.aliases` with `duplicate_of`
  and `reason`. Confirm a duplicate metric manually.

`unknown` means the catalog has not established a classification. Use the review states to
distinguish a question the reviewed sources leave unanswered (`unreported`), unfinished
review (`not-reviewed`), and a question outside the workflow's scope (`not-applicable`).
Shared infrastructure does not need a single supervision level when its workflows differ.

The “In depth” badge requires detailed primary evidence, a supporting source for every
claim, preserved copies of every source, and a completed `page_content` review of all listed
sources, questions, and architecture fields. Purpose and implementation must be reported.
Qualified claims and reviewed gaps can qualify; unfinished review cannot. The badge describes
documentation coverage, not verified outcomes or system quality.

When you edit `docs/patterns.md` or `docs/adoption-lessons.md`, compare similar approach types and deployment stages. State the sample size. Include counterexamples before you call a pattern common.

## Generated files

The build updates these files:

- `README.md`, between the overview markers
- `docs/patterns.md`, between the catalog snapshot markers
- `docs/adoption-lessons.md`, between the catalog snapshot markers
- `docs/landscape.md`
- `data/agents.json`

Do not edit generated content by hand. Commit these files with the source YAML change.

## Verify a change

Run:

```bash
uv run python scripts/build.py
npm run verify
```

The first command regenerates the data and the repository documents. `npm run verify` then runs
every gate in one sequence: the generated-output and archive checks, the type and unit checks,
the website build, the artifact check, the Python tests, lint, format, privacy, local links,
the browser tests, and the whitespace check. Run a single gate directly when you repair a failure.

The scheduled link check tests external URLs. A confirmed 404 or 410 passes with an `archived`
warning when a verified fallback exists and fails otherwise. Blocked and temporarily unreachable
URLs are reported separately as warnings. A pull request does not depend on remote sites being
available.

## Website

The website is an Astro project in `src/`. It reads the same validated catalog as the Markdown
and JSON. Edit `data/agents/*.yaml` for evidence, `src/content/lessons/*.md` for lessons, and the
pages, layouts, components, and styles in `src/` for the presentation.

Run `npm run dev` for a local preview. It regenerates the normalized data and reloads the page
when you edit a record or a lesson. Run `npm run verify` before you open a pull request.

The build writes the website to `dist/`, which Git ignores. Do not commit website output.
Vercel builds and checks the same artifact for every push, and a merge to `main` deploys it to
`https://internal-agents.com/`. See [website maintenance and delivery](docs/site.md) for the
hosting rules, preview deployments, delivery checks, and rollback.

## Agents and infrastructure

The map maintains two collections. Agents perform identifiable work for internal
teams; Infrastructure supplies reusable execution, orchestration, or tool access.
Both retain structured, source-backed records. Lessons compare practices across cases.
Choose the subject before assigning workflow claims or metrics: a task-performing
system remains an agent even when it orchestrates subagents. A family requires
independently useful constituent agents. Sandbox detail alone does not establish a
platform. Attribute downstream agent results to their actual subject and author
`built-on` only when a source establishes the dependency.

The homepage counts agents; the Infrastructure index keeps supporting implementations
discoverable. Full JSON exports include both collections, identified by derived
`catalog_section`. Existing detail URLs and anchors remain stable. See the
[schema migration](docs/changelog.md).
