# Catalog data schema

Each YAML file in `data/agents/` describes one reported approach. An approach can be an agent, a platform, an orchestration system, or an implemented supporting pattern.

The build creates four linked collections in `data/agents.json` (schema version 8):

- `approaches` contains the systems and their comparison fields.
- `claims` contains sourced statements derived from authored fields.
- `sources` contains the evidence and commentary records.
- `companies` contains the organization registry with each logo descriptor.

The export also contains `claim_aliases`. It maps each claim ID of schema version 7 to its claim ID in schema version 8. The build reads the map from `data/claim_aliases.json` and fails when a value is not a claim ID of the export. The map stays for one release. [docs/changelog.md](../docs/changelog.md) lists the changes between schema versions.

Copy `templates/agent.yaml` when you add an approach. Omit optional fields when no public source documents them. Use `unknown` for a required rubric field when the sources do not provide an answer.

## Machine-readable schema

`data/agent.schema.json` is a JSON Schema (draft-07). It is the source of truth for the fields, types, and allowed values of one record. This document explains what the values mean.

The build applies the schema to each record first. Then it applies the rules that compare a record with other records and files: unique source IDs, evidence that refers to the sources of the same record, claim paths that exist, capture manifests, and the company registry.

The first line of each record is `# yaml-language-server: $schema=../agent.schema.json`. An editor that uses the YAML language server, such as VS Code or Cursor with the Red Hat YAML extension, then shows the allowed values and the errors while you type. Keep this line when you copy the template.

The build also writes `src/lib/schema-values.ts` from the schema. The website uses its values and types. Do not edit that file by hand.

To add an allowed value, add it to the schema and to this document. A test fails when this document does not name a value of the schema.

## Required approach fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | A kebab-case ID that matches the file name. |
| `company` | string | The organization that built or adapted the approach. |
| `agent_name` | string | The reported name. Use a clear description if no name is public. |
| `approach_type` | enum | The type of approach. See the values below. |
| `deployment_stage` | enum | `research`, `prototype`, `pilot`, `deployed`, `scaled`, or `unknown`. |
| `first_public_evidence` | map | The evidence `date` and its `source_id`. |
| `last_reviewed_at` | date | The last catalog review date. |
| `status` | enum | `internal`, `open-sourced`, `commercialized`, or `mixed` for a combined record. |
| `domains` | list | Work domains, such as `coding`, `support`, or `security`. |
| `autonomy` | enum | The autonomy level. See the values below. |
| `operating_models` | list | Scoped catalog assessments of where human attention returns in a normal successful run. |
| `rubric` | map | Shared comparison fields. |
| `summary` | string | A short, factual description. |
| `sources` | list | Structured public sources. |
| `evidence` | map | A link from each authored claim to one or more sources. |

The build derives `year`, the year of the earliest verified public evidence, from `first_public_evidence.date`. The export always contains `year`. Do not write it. If a record writes `year` and the value does not agree with that date, the build fails.

Set the optional `featured` field to `true` to show a record before all others in the default directory order. Featured records come after the bookmarks of the reader and before the other well-documented records. Give this field only to a record that is well documented. The A–Z order does not use it.

The optional identity field is `aliases`. Use `relationships` to connect records. Each relationship has a `type` and `approach_id`. Types are `component-of`, `built-on`, `successor-of`, and `related-to`.

### Approach types

- `agent`: One task-performing system. It may be invoked interactively, in the
  background, on a schedule, or by an event. Internal subagents do not by themselves
  turn an agent into an agent system.
- `agent-system`: A documented family of related agents with shared infrastructure.
- `platform`: Reusable infrastructure that supports several agents or workflows.
- `orchestration-system`: A system whose primary responsibility is coordinating agents.
- `supporting-pattern`: A narrower implemented component that enables agent operation.

The build derives `catalog_section` from the type: `agent` and `agent-system` become
`agents`; `platform`, `supporting-pattern`, and `orchestration-system` become
`infrastructure`. Do not write this field.

Classify a compound entry by its documented primary responsibility and explain its
components. Invocation is independent of structural type; an event trigger does not
by itself establish unattended execution.

### Autonomy values

- `assistive`: A person drives the work and the system provides help.
- `human-in-loop`: The system acts, but a person participates in each cycle or approval.
- `drafts-reviewed`: The system prepares work that a person reviews before use.
- `autonomous`: The work takes effect without required human review.
- `unknown`: The catalog has not established the review boundary. The review state distinguishes missing reporting from unfinished review or an inapplicable question.

When a record has exactly one operating model, its autonomy must not contradict the
attention boundary of that model. The build refuses any other pair:

| Autonomy | Allowed attention boundaries |
| --- | --- |
| `drafts-reviewed` | `work-product-review`, `outcome-review` |
| `autonomous` | `exception-only` |
| `human-in-loop` | `continuous-steering`, `work-product-review` |
| `assistive` | `continuous-steering` |

The value `unknown` on either side agrees with every value.

### Operating models and derived levels

`operating_models` adapts [Dan Shapiro's five levels of AI-assisted software development](https://www.danshapiro.com/blog/2026/01/the-five-levels-from-spicy-autocomplete-to-the-software-factory/) to a documented internal-agent workflow, not to an organization as a whole. Shapiro's original framework is coding-oriented; this catalog generalizes it by asking whether and when a successful run requires human attention. Each item contains only:

| Field | Description |
| --- | --- |
| `scope` | A short description of the workflow being assessed, preferably from input to output. |
| `attention_boundary` | Whether and when a successful run requires human attention. |

The build derives the level from the attention boundary:

| Attention boundary | Derived level | Meaning |
| --- | ---: | --- |
| `continuous-steering` | 2 | A person pairs with the agent throughout execution. |
| `work-product-review` | 3 | The agent produces a draft or implementation that a person reviews. |
| `outcome-review` | 4 | A person delegates from a specification and evaluates tests, behavior, or outcomes rather than routinely inspecting implementation. |
| `exception-only` | 5 | A person is normally involved only when the system raises an exception. |
| `unknown` | — | The catalog has not established a human attention boundary. |

Never render or interpret a level without its scope. Compound systems can have multiple scoped assessments. Use `unknown` rather than averaging different workflows or guessing from `autonomy`, invocation mode, output volume, or company identity.

For infrastructure that supports different workflows, a single supervision level may not apply.
Record that distinction in `page_content.questions.human_involvement` as `not-applicable`
with a scope-specific reason. An `unknown` operating model can retain the existing claim and
its evidence without asserting a level for the whole platform.

The boundary describes required human attention, not tool authority or elapsed unattended
execution. Record permissions and publication controls in the supported claims. A Level 5
workflow can still be unable to merge, deploy, spend, or act in production without approval.

Each `operating_models.N` item is an evidence-linked inference with `catalog-judgment` provenance. The build fills this `kind` and `provenance`, so do not write them. Any other `kind` or `provenance` fails the build. Its claim metadata must include `confidence`, `confidence_reason`, and `valid_at`. The level itself is generated and is never authored as a reported company fact.

## Comparison rubric

The rubric organizes different definitions and designs. It does not determine whether an approach belongs in the catalog.

| Field | Allowed values |
| --- | --- |
| `invocation` | A list of `interactive`, `background`, `scheduled`, `event-driven`, or `unknown`. |
| `evidence_strength` | `detailed-primary`, `limited-primary`, `secondary-only`, `mixed`, or `unknown`. |

Schema version 8 removed the `state` and `identity` fields; [docs/changelog.md](../docs/changelog.md) gives the reason.

Evidence strength describes the available detail. It does not measure whether a claim is true. A company article can provide detailed architecture and still contain marketing claims.

Structural type and invocation answer different questions. `approach_type` identifies what
kind of system the record describes. `rubric.invocation` identifies how work starts or proceeds.
Do not infer either field from the other, and use `unknown` when the source is silent.

## Optional description fields

`architecture` can contain short strings for `sandbox`, `harness`, `model`, `tool_access`, `knowledge`, `credentials`, and `context_mgmt`. Its `interfaces` field is a list. Omit a field that no reviewed source documents. Do not write `unknown`, `Not specified`, an empty string, or an empty list; the schema rejects them. `page_content.implementation_fields` records that the sources were read and name nothing. An earlier implementation's environment must be labeled as historical, not attributed to its replacement.

Domain values are `coding`, `code-review`, `support`, `on-call`, `research`, `customer-success`, `security`, `finance-ops`, `data`, `ci-triage`, `maintenance`, `ops`, `recruitment`, `migrations`, and `design`.

Interface values are `slack`, `github`, `web`, `cli`, `linear`, `chrome-extension`, `webhook`, `desktop`, `scheduled`, `skill`, `cursor`, `api`, `automation`, `ci`, `intercom`, `jira`, `internal-ui`, `mobile`, and `monday`.

`primitives`, `key_metrics`, and `lessons_learned` are lists of items. Each item has an `id`. The ID is kebab-case, contains at least one letter, and is unique in its list. A claim path names the item by its ID, so a claim keeps its evidence when the list order changes.

- A primitive has `id`, `name`, `desc`, and `role`. The role is `workflow`, `mechanism`, or `validation`. A workflow primitive is a step of the normal run. A mechanism primitive is a part that the steps use. A validation primitive checks the work.
- A key metric and a lesson have `id` and `text`.

`headline_metric` is a short reported result.

```yaml
primitives:
  - {id: open-a-run, name: Open a run, desc: "An issue label starts a run", role: workflow}
key_metrics:
  - {id: weekly-runs, text: "40 runs a week in August 2026"}
lessons_learned:
  - {id: gate-before-review, text: "The team puts the test gate before the human review."}
```

Treat all company metrics as self-reported unless an independent source verifies them. Include the date, scope, denominator, and measurement method when the source provides them.

## Company registry

`data/companies.yaml` holds one record per organization, sorted by `id`. The registry links every approach record to one organization and names the logo asset of each organization.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | A kebab-case ID. It is also the logo file stem. |
| `name` | string | The organization name. It must equal the `company` value of the approach records. |
| `homepage` | string | The organization homepage. It must use HTTPS. |
| `logo` | map or `none` | The logo asset record, or `none` while no asset is collected. A logo map holds exactly `file`, `source_url`, and `accessed_at`. |
| `logo_note` | string | Required with `logo: none`. It states the reason no logo is shown. It is not allowed when a logo file is named. |

The join runs both ways. Every `company` value in `data/agents/` must have a registry record. Every registry record must be used by at least one approach. `public/logos/` may hold only files the registry names.

Logo files live in `public/logos/<id>.svg` or `public/logos/<id>.png`. The build rejects an SVG larger than 64 KiB and a PNG larger than 128 KiB or narrower than 128 pixels. An SVG needs a `viewBox`. It must not hold a DOCTYPE, an ENTITY declaration, a script, a `foreignObject`, an `on*` attribute, a `javascript:` value, or a non-fragment `href`. The intrinsic size comes from the `viewBox` or from the PNG header.

The build derives the `companies` collection into `data/agents.json` and adds `company_id` to every approach. Each company record carries `id`, `name`, `homepage`, and `logo`. The `logo` is `null` when no asset exists. Otherwise it is a descriptor with `path`, `media_type`, `width`, `height`, `bytes`, `sha256`, `source_url`, and `accessed_at`. The build derives the hash, the byte count, and the size from the asset. Never author them.

## Source records

Every source requires these fields:

| Field | Description |
| --- | --- |
| `id` | A repository-wide unique kebab-case ID. |
| `title` | The source title. |
| `url` | The immutable original publisher URL. It must use HTTPS and must never be replaced with an archive URL. |
| `kind` | The source format. |
| `provenance_class` | The relationship between the publisher and the approach. |
| `accessed_at` | The collection date. |
| `last_verified_at` | The last successful check of the source at its original URL. Reading a preserved copy does not advance this date. |
| `role` | `evidence`, `commentary`, or `discovery`. The default is `evidence`. |

`canonical_url` is optional. It is the normalized publisher URL after redirects and tracking removal. The default is `url`, and the export always contains it. Write it only when it is different from `url`.

Optional fields include `publisher`, `authors`, `published_at`, `capture`, and `duplicate_of`. `capture` points to a repository-owned Steel capture manifest:

```yaml
capture:
  manifest_path: "archive/sources/company-agent-source-1/metadata.json"
```

The capture map contains exactly `manifest_path`. Capture bundles use this deterministic layout:

```text
archive/sources/<source-id>/metadata.json
archive/sources/<source-id>/content.md
archive/sources/<source-id>/page.pdf        # optional
```

The version 1 JSON manifest contains `schema_version`, `source_id`, `original_url`, `final_url`, `captured_at`, `http_status`, `tool`, and `artifacts`. It may also contain `external_archive_url`, the external archive that the capture tool found. The `tool` map records `name: steel` and a non-empty version. `artifacts.markdown` is mandatory; `artifacts.pdf` is optional. Each artifact records its repository-relative `path`, exact `bytes`, and a lowercase `sha256:<digest>`. Markdown must be non-empty. PDFs must begin with `%PDF-` and cannot exceed 10 MiB. Paths and hashes are validated during every build.

Captures are append-only evidence snapshots: never overwrite an existing bundle or use a capture to replace the original `url`. Create a new source ID when materially changed source content is needed for new claims.

Use `duplicate_of` to reference an existing source ID. When the original URLs match exactly,
this declares the same source version and allows reuse of the original capture. The build
resolves alias chains and rejects missing targets and cycles. In the export, the alias has
the resolved `capture`; the manifest keeps the original `source_id`, paths, URL, and capture
time. An alias's own capture takes precedence. A mirror or translation with a different URL
needs its own capture, even when it has `duplicate_of`.

Source kinds are `engineering-blog`, `corporate-article`, `documentation`, `source-code`, `repository`, `release`, `social-post`, `talk`, `transcript`, `podcast`, `paper`, `case-study`, `news`, `hn-thread`, `hn-comment`, `forum`, and `other`.

Provenance classes are:

- `first-party`: The organization published the source.
- `direct-participant`: A person who worked on the system published the source.
- `independent-secondary`: An outside publication reported the information.
- `community`: A community member supplied analysis or commentary.
- `aggregator`: The source collects information from other sources.

Use source records for evidence, context, and commentary. A Hacker News thread and each material comment are separate sources. Store item and comment IDs in the URL or optional metadata.

## Claim evidence

Every descriptive field becomes a claim in the generated JSON file. The `evidence` map links its field path to source records.

```yaml
evidence:
  summary:
    - source_id: acme-agent-source-1
      locator: "Architecture, paragraph 3"
  key_metrics.weekly-runs:
    - source_id: acme-agent-source-2
      relation: contextualizes
      locator: "12:40"
```

Each link has these fields:

| Field | Description |
| --- | --- |
| `source_id` | The source of this record that the link refers to. It is optional only when the record has one source; the build then uses that source. When the record has more than one source, every link must name its source, or the build fails. |
| `relation` | `supports`, `contradicts`, or `contextualizes`. The default is `supports`. |
| `locator` | The exact passage in the source. |

A link must contain `source_id`, `locator`, or both. The export always contains `source_id` and `relation` for each link.

The relation is `supports`, `contradicts`, or `contextualizes`. Use a stable locator when one exists. For preserved sources, `Preserved content.md, lines 23–27` refers to the immutable artifact in that source's capture bundle, including its archive header. A locator must identify the supporting passage, not merely a broad topic. For source code, record the commit, path, and line. For a talk, record the timestamp.

For each lesson, use claim metadata to distinguish a reported practice (`fact`,
`reported`), an attributed preference (`opinion`, `reported`), and a catalog inference
(`inference`, `catalog-judgment`). Its `confidence_reason` names the supporting
observation and any missing link in the reasoning. A generic claim that the source
supports the lesson does not explain that reasoning. The lesson text must also carry
its scope: a team's implementation is not a recommendation for every organization.

Use `claim_metadata` when the default classification is not correct. The build gives each claim path a default `kind` and `provenance`:

| Claim path | Default `kind` | Default `provenance` |
| --- | --- | --- |
| `summary`, `architecture.*`, `primitives.<id>` | `fact` | `reported` |
| `headline_metric`, `key_metrics.<id>` | `metric` | `reported` |
| `lessons_learned.<id>` | `inference` | `catalog-judgment` |
| `operating_models.N` | `inference` (fixed) | `catalog-judgment` (fixed) |

Do not write a `kind` or `provenance` that is equal to its default. The export always contains both.

```yaml
claim_metadata:
  key_metrics.weekly-runs:
    confidence: medium
    confidence_reason: "A direct participant reported the number without a method."
    valid_at: 2026-04
    reported_by: Acme
    metric_scope: "Merged agent-authored pull requests"
    denominator: "All merged pull requests"
    measurement_method: "Company dashboard"
    category: adoption-output
    basis: reported-measurement
    subject: "Merged agent-authored pull requests"
```

A claim path uses the item ID: `primitives.<id>`, `key_metrics.<id>`, or `lessons_learned.<id>`. The build refuses an index path, such as `primitives.3`, in `evidence`, `claim_metadata`, and `page_content`. Only `operating_models.N` keeps its index. The public claim ID is the record ID, two dashes, and the claim path with each `.` and `_` changed to `-`, for example `github-qubot--primitives-start-a-qubot-run`.

A metric's `valid_at` can identify a dated reported observation, but does not by itself define a measurement interval. Keep the interval explicit in `metric_scope` or `measurement_method`; never derive it from a capture or review timestamp. If a source says only “last month” or “as of Part 2,” preserve that wording and leave unsupported calendar dates unset.

Claim kinds are `fact`, `metric`, `inference`, and `opinion`. Provenance values are `reported`, `observed`, `inferred`, and `catalog-judgment`.

Confidence describes the support for a particular claim. Every authored `confidence` needs
a `confidence_reason` that identifies the evidence and any qualification. Source provenance
alone never supplies a rating. A well-supported attribution of a company metric remains
self-reported unless independently verified.

| Confidence | Meaning |
| --- | --- |
| `high` | Direct, specific evidence supports the claim as worded and scoped. |
| `medium` | Evidence supports the main point, with a material qualification or inference. |
| `low` | Support is weak, ambiguous, or conflicting. |
| `unverified` | Review has not established enough support for the claim. |
| `not-assessed` | No explicit confidence assessment is recorded. This is the export default. |

The build preserves authored assessments. Changes to a rating require review of its evidence;
they cannot be inferred from a new source type or a successful link check.

Metric metadata can also include `value`, `unit`, `reported_by`, `metric_scope`, `denominator`, and `measurement_method`. The generated export uses the company as `reported_by` when a reported metric does not override it.

When a record has `page_content`, the metadata of the headline and of each key metric has three axes, or the metric is an alias in `page_content.aliases`:

- `category` is `effectiveness`, `adoption-output`, `cost-latency`, `implementation-scale`, or `runtime-capacity`.
- `basis` is `reported-measurement`, `qualitative`, `estimate`, or `target`.
- `subject` is the specific thing that the metric measures.

Only a metric can carry these axes. An alias must not carry them.

In the export, each primitive claim has `item_id`, `display_name`, and `role`. Each key metric and lesson claim has `item_id`. A canonical metric claim has `category`, `basis`, and `subject`. An alias metric claim has `duplicate_of`, the claim ID of its target, and `reason`.

## Optional reviewed page content

`page_content` version 1 records an editorial review. `reviewed_at` is a full
`YYYY-MM-DD` date, and `source_ids` lists the entry sources actually read. `questions`
contains exactly `purpose`, `workflow`, `human_involvement`, `implementation`,
`validation`, `observations`, and `lessons`. Each answer has a `state` and optionally a
`note`.

States are `reported`, `unreported`, `not-applicable`, and `not-reviewed`. A reported
answer requires one or more same-entry claims supported by a reviewed source. The other
states have no claims. A `not-applicable` or `not-reviewed` answer requires a concrete
note; for `not-reviewed`, the note is the next research action. An `unreported` answer
does not require a note: the state already says the captures were read and name nothing.
Leave the note out unless it adds a fact the state does not carry — what the source says
instead, which claim stays in research details, or the scope that limits the answer.

Write `claim_paths` only for `workflow`, `human_involvement`, and `validation`. They are
editorial choices: the workflow lists every `workflow` primitive in reading order, and the
other two cite the claims that answer them. A reported workflow also requires
`workflow_scope`. The build derives the claim paths of the other four questions and
refuses them in the record:

| Question | Derived claim paths when the state is `reported` |
| --- | --- |
| `purpose` | `summary` |
| `implementation` | Every present architecture field, in the order `model`, `harness`, `sandbox`, `tool_access`, `knowledge`, `context_mgmt`, `credentials`, `interfaces` |
| `observations` | `headline_metric`, then every key metric in record order, aliases included |
| `lessons` | Every lesson |

A derived question that is not `reported` has no claim paths in the export. A reported
derived question with nothing to derive fails the build.

`implementation_fields` holds only what the build cannot derive. The build makes a field
`reported` when its architecture field is present and `unreported` when it is absent.
For a present field, an entry may hold only a `note`. For an absent field, an entry has a
`state` (`unreported`, `not-applicable`, or `not-reviewed`) and a `note`. An entry with
`state: reported` or with `claim_paths` fails the build.

`aliases` maps a metric claim path to `duplicate_of` and `reason`. It marks a metric that
repeats another metric of the same entry. The target must be the headline or a key
metric that is not an alias; self references, cycles, and chains are invalid. Confirm
equal subject, statement/value, period, scope, and qualifications before marking a
duplicate. The working criterion: an alias must add nothing the canonical lacks. A
component of a compound observation can alias the compound; an observation carrying an
extra qualification or absence note cannot, however similar its number.

```yaml
page_content:
  version: 1
  reviewed_at: "2026-09-28"
  source_ids: [acme-agent-source-1]
  workflow_scope: "Issue label → reviewed pull request"
  questions:
    purpose: {state: reported}
    workflow: {state: reported, claim_paths: [primitives.open-a-run]}
    human_involvement: {state: reported, claim_paths: [operating_models.0]}
    implementation: {state: reported}
    validation: {state: unreported}
    observations: {state: reported}
    lessons: {state: reported}
  implementation_fields:
    harness: {note: "The talk names the loop but not its version."}
    sandbox: {state: not-applicable, note: "The agent runs no code of its own."}
  aliases:
    key_metrics.weekly-runs: {duplicate_of: headline_metric, reason: "Same count and period."}
```

The export always contains all seven questions with their claim paths, all eight
implementation fields with their states, and `aliases`.

Run `uv run --locked python scripts/content_coverage.py --check` to validate the
coverage view, or add `--output <path>` to write deterministic JSON. Records without
the optional block are reported as `legacy-unassessed`.

## Collection rules

1. Resolve the approach identity before you extract claims.
2. Capture source metadata before you summarize the source.
3. Keep each authored claim short and specific.
4. Link every claim to exact evidence.
5. Preserve supporting, conflicting, and contextual sources.
6. Mark catalog interpretation as `inferred` or `catalog-judgment`.
7. Record unknown values instead of inferring absence.

Normalize URLs and remove tracking parameters. Link mirrors and translations with `duplicate_of`. Do not merge two approaches only because one company built both. Use relationship metadata in a future record revision when systems share a platform or change names.

Run `uv run python scripts/build.py` after each data change. Run
`uv run python scripts/build.py --check` to verify committed output.
