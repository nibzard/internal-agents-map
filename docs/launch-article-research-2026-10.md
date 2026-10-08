# Research dossier: launch article for internal-agents.com (Steel blog)

ABOUTME: Verified research dossier that supports the Steel blog launch article for internal-agents.com.
ABOUTME: Produced by a 102-agent deep-research run on 2026-10-08; all access dates below are 2026-10-08.

Prepared for the article writer. This dossier does not write the article.

## Method and evidence legend

A deep-research workflow decomposed the brief into five search angles, fetched 20 sources,
extracted 99 claims, and ran 3-vote adversarial verification on the top 25 claims. Result:
24 confirmed, 1 refuted. Claims that were extracted but not adversarially verified are kept
and labeled. Verification status tags used throughout:

- **[V]** Verified: survived 3-vote adversarial verification against the primary source (vote counts noted).
- **[E]** Extracted: taken from a fetched source by one extraction agent. Accurate to that fetch, but no adversarial vote ran on it.
- **[U]** Unverified lead: surfaced by search only. Confirm URL, date, and content before any use.

Rules followed: metrics keep their published scope and date; no rounding or combining;
interpretation marked; Steel's own content is not used as evidence. All company metrics are
self-reported, first-party, and unaudited unless stated otherwise.

---

## 1. Summary

- **The article's thesis holds, with one mandatory hedge.** Across four independent
  first-party sources (Stripe, Shopify, Uber, Anthropic), the published hard problems sit in
  the agent's environment: stopping, resuming, tool access, deterministic gates, evaluation.
  The hedge: Anthropic states "every component in a harness encodes an assumption about what
  the model can't do on its own," and its author dropped sprint contracts and context resets
  after moving to Opus 4.5/4.6 — the needed environment shrinks as the model improves. Present
  "much less in the model" as a snapshot tied to current models, not a law. **High.** [V 15-0]
- **Headline scale metrics are confirmed exactly as published, and all are self-reported.**
  Stripe: over 1,300 merged minion PRs per week (2026-02-19). Shopify: one in eight merged
  PRs coauthored by River (2026-05-28; the article itself calls the number "already wrong, in
  the upward direction" — a floor). Uber: uReview analyzes over 90% of the ~65,000 weekly
  diffs (as of 2025-08; the same article elsewhere says 65,000 per month — preserve, do not
  resolve). **High.** [V]
- **Ramp Inspect has moved past the brief's baseline.** The live catalog now headlines
  "75% of Ramp's merged PRs raised by Inspect sessions (May 2026)" with a trajectory of
  roughly 30% (first report, late 2025) → about 60% (January 2026) → 75% (May 2026). A
  Pragmatic Engineer interview (2026-08-25) re-states 75% as of publication. The article must
  not use "60%+" as the current figure. **High.** [V/E]
- **Two new cases outside coding/code review are ready for catalog intake:** Embat "Mr. Batt"
  (support, 2026-07-21) and Ramp "Doer"/"Architect" (finance ops, 2025-10-01 UTC). Both
  predate the mid-September 2026 review cutoff — they are missed cases, not post-cutoff ones.
  GitHub's Qubot (analytics) also surfaced, but it is already in the catalog. **High.** [V]
- **One claim was refuted and must not appear in the article:** that Ramp's Architect agent
  is fully autonomous after intake (an accountant uploads a recording, gets a finished
  process, no human in the loop). Verification found this overreads the source. Record the
  Architect's supervision as unknown. **High.** [refuted 1-2]
- **Independent counterevidence is strong.** METR's randomized controlled trial: experienced
  open-source developers were 19% slower with early-2025 AI tools while believing they were
  20% faster — the perception-versus-measurement gap is the durable finding. Scope discipline:
  METR now banners the result out of date for current tools. **High.** [V 6-0]
- **Vendor research exists but must be labeled.** CodeRabbit's report (2025-12-17) found
  about 1.7x more issues per AI-co-authored PR (10.83 vs 6.45, 470 PRs); authorship was
  inferred, the control group may be contaminated, and CodeRabbit sells AI code review.
  **Medium.** [V as accurate report of a vendor source]
- **"Internal agents" is not yet standardized vocabulary.** Google Cloud's glossary
  (2026-04-02) uses "background agents," defined by interaction mode, and never uses
  "internal agent." Practitioners (Embat, Browsercase-style first-party posts, GitHub) do use
  "internal agent" organically. The catalog's four-part definition (durable identity,
  organizational context, tools, supervision) is more specific than any published vendor
  definition found. **Medium.** [E]
- **No competing catalog covers internal agents.** The closest lists (awesome-ai-agents:
  public agent products, no evidence standard; StackOne map: 120+ agentic tools, vendor
  marketing) catalog products organizations adopt, not agents organizations build for
  themselves. Positioning is "adjacent landscapes, empty niche" — stated as scope difference,
  not superiority. **Medium.** [E]
- **Coverage is thin where the brief most needs it.** Nothing verified on current state of
  Airbnb AirChat, DoorDash, Sentry Junior, Sierra, Dropbox Nova, or Databricks coSTAR; no
  verified post-September-2026 first-party accounts; no systematic reader-demand pass. See
  section 10. **High (as a statement of what was not found).**

## 2. Category timeline

Dated first-party (or clearly labeled secondary) accounts found and checked this round. This
is not a census; it is every dated account the workflow verified or extracted, and it is
consistent with the catalog's 2025–2026 acceleration (1 record from 2024, 20 from 2025, 45
from 2026).

| Date | Company | Agent / system | Source | Source type | Status |
|---|---|---|---|---|---|
| 2025-08-11 | Uber | uReview | uber.com/blog/ureview | Company report | [V] |
| 2025-10-01 (UTC) | Ramp | Doer + Architect (finance) | ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal | Company report | [V] (date corrected from Oct 2) |
| 2025-11-26 | Anthropic | Long-running agent harness | anthropic.com/engineering/effective-harnesses-for-long-running-agents | Company report (model vendor, first-party) | [V] |
| 2026-01-23 | Ramp (covered by InfoQ) | Inspect (~30% of merged frontend/backend PRs) | infoq.com | Press (independent) | [E] |
| 2026-02-09 | Stripe | Minions (1,000+ merged PRs/week) | stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents | Company report | [V] |
| 2026-02-19 | Stripe | Minions Part 2 (1,300+/week, two-CI-round cap, blueprints) | stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2 | Company report | [V] |
| 2026-03-24 | Anthropic | Harness design (resets, evaluator split, model-relativity) | anthropic.com/engineering/harness-design-long-running-apps | Company report (model vendor, first-party) | [V] |
| 2026-05-21 | Uber | Internal agent platform (identity) | uber.com/blog (agent identity post) | Company report | [U] |
| 2026-05-28 | Shopify | River + Aquifer | shopify.engineering/under-the-river | Company report | [V] |
| 2026-06-19 | GitHub | Qubot (internal analytics; already cataloged) | github.blog (canonical URL in Sources) | Company report | [E] |
| 2026-07-21 | Embat | Mr. Batt / Mbatt (support) | embat.io/tech/internal-ai-agent-platform | Company report | [V] |
| 2026-08-25 | Ramp (interviewed) | Inspect (75% of merged PRs) | newsletter.pragmaticengineer.com | Independent secondary relaying Ramp-reported numbers | [E] |

Reading: every dated account clusters between August 2025 and August 2026. Interpretation:
this is consistent with — but does not by itself prove — an accelerating publication cadence;
a dedicated sweep of talks, podcasts, and filings is still needed (section 10).

### Term usage

- Google Cloud glossary (updated 2026-04-02): uses "background agents," defined by
  interaction mode ("event-driven, queued tasks, limited or no human interaction"). Full-text
  search found no use of "internal agent," "internal AI agent," or "in-house agent." Its core
  agent definition (autonomy, reasoning, planning, memory, tools) has no durable-identity,
  organizational-context, or supervision requirement — overlapping with, but not equivalent
  to, the catalog's definition. [E]
- Cognition (Walden Yan, Latent.Space interview): popularized "background agents" with a
  brain-versus-compute framing. Secondary/podcast; prefer primary Cognition posts if used. [U]
- First-party practitioner use of "internal agent": Embat ("internal AI agent platform,"
  2026-07-21) [V]; GitHub Qubot post ("internal data analytics agent," 2026-06-19) [E];
  Browserbase ("How we build Internal Agents," date unverified) [U].

## 3. Positioning

| Catalog / map | Scope | Size | Evidence standard | Last update | Type |
|---|---|---|---|---|---|
| internal-agents.com | Agents organizations build for their own work; agent vs infrastructure records | 66 records, ~1,150 claims, 140 sources | Per-claim URL, date, stated scope; first-party intake rules | Continuous; last full review mid-September 2026 | Public, evidence-backed |
| e2b-dev/awesome-ai-agents | Public agent products, open-source projects, companies | ~30.3k stars, ~100+ entries across ~24 tags | None stated: submissions must only "keep the alphabetical order and in the correct category" | Last commit 2026-08-21 | Community awesome-list |
| StackOne agentic-AI landscape | Tools and platforms organizations adopt (frameworks, observability, memory, coding agents, etc.) | 120+ tools, 11 categories | None disclosed; author's commercial vantage | Published 2026-02-08; quarterly updates claimed | Vendor marketing |
| Master of Code "AI Agents for Internal Operations" | Named internal-ops deployments with claimed ROI | 27 use cases, 56 deployments | None; relays vendor-claimed numbers | Unverified | Consultancy roundup (secondary) |

Key contrasts, from the fetched awesome-list and map content [E]:

- None of the catalog's flagship internal agents (Ramp Inspect, Airbnb AirChat, Stripe
  Minions, Shopify River, Uber uReview, and others) appear in awesome-ai-agents; the README
  never uses "internal agent," "in-house agent," or "background agent." The list predates the
  acceleration (repo created 2023-06-19) and splits by open- vs closed-source, not by domain
  or supervision.
- The StackOne map is adjacent, not overlapping: it maps what you can buy, not what
  organizations built for themselves. It also aggregates vendor-reported adoption metrics
  without verification (for example Salesforce Agentforce at "$540M+ ARR," Claude Code at
  "4% of all GitHub public commits") — a useful foil for the catalog's per-claim sourcing.
- Interpretation: honest positioning is "the existing landscape space is vendor-product
  shaped; no one catalogs evidence-backed first-party accounts of internal agents." State it
  as a scope difference. Avoid superiority claims about list quality.

## 4. New cases

Matched against the live catalog (66 records; company + agent name). GitHub Qubot is already
cataloged (github-qubot.yaml) and is excluded. No verified post-cutoff (after
mid-September 2026) first-party account was found.

| Company | Agent | Domain | Interface | Supervision | Reported metric | Published | Status |
|---|---|---|---|---|---|---|---|
| Embat | Mr. Batt / Mbatt | Support / customer-issue resolution | Slack | Router picks among 10+ specialists; asks the user when unsure (human-in-the-loop at routing) | Team bio: support response times cut ~70% (no scope, baseline, or period stated) | 2026-07-21 | [V 6-0] Ready for intake |
| Ramp | Doer (finance agent) + Architect (prompt generator) | Finance ops (revenue reconciliation, inter-company transfers to ERP) | Doer: prompt/context-file driven; Architect: screen recordings in, prompts out | Unknown (autonomy claim refuted 1-2) | 6-12x speedup self-claimed, no methodology; SpreadsheetBench eval: 49.5% soft-restriction, 32.5% hard-restriction accuracy | 2025-10-01 UTC | [V 3-0] Ready for intake |
| Browserbase | "Internal agents" (unnamed) | Browser-automation knowledge work | Browser as interface | Unknown | None found | Unverified | [U] Lead only |
| Youforce (built by Incentro) | YARA | HR support | Slack | Unknown | None verified | Unverified | [U] Lead; consultancy-promotional provenance |

Intake notes:

- **Embat Mr. Batt.** Correct URL: https://www.embat.io/tech/internal-ai-agent-platform
  (datePublished 2026-07-21; byline Ton Borrell, Senior AI Product Engineer). The search
  index's "Blog%20Tech" URL 404s. Started as a Product Experience support tool, now
  company-wide. Split from one generalist to 10+ specialists after prompt changes in one
  domain degraded others; router in front, with fallback to asking a human. Platform built on
  what the article calls Anthropic's "Claude Managed Agents" (product name warrants
  verification at intake); at least one tool spins up a Google ADK agent. Pre-cutoff
  publication: a missed case, not a post-cutoff one.
- **Ramp Doer + Architect.** Primary source: Ramp Labs Substack
  (https://ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal; canonical mirror
  labs.ramp.com is JS-rendered). JSON-LD datePublished is 2025-10-01T19:24:14+00:00 — use
  October 1, 2025 UTC. The Doer automates monthly revenue reconciliation and month-end
  booking of inter-company fund transfers into the ERP; the Architect generates the Doer's
  prompts and context files from accountant screen recordings. Before the Architect, each
  use needed 30-45 minutes of manual prompt crafting. Do not state the Architect's autonomy
  level (refuted). The catalog currently holds only Ramp Inspect for this company.
- **Browserbase / YARA.** Both need canonical URL, date, and content confirmation before
  intake. YARA's account is written by the consultancy that built it; treat as promotional
  unless a Youforce first-party account exists.

## 5. Fact check

| Claim | Catalog value | Current value | Status | Source |
|---|---|---|---|---|
| Ramp Inspect share of merged PRs | Headline: "75% of Ramp's merged PRs raised by Inspect sessions (May 2026)"; trajectory ~30% (first report; frontend/backend repos) → ~60% (January 2026) → 75% (May 2026); ~90% of PRs merged into the Inspect repo | 75% of merged PRs raised by Inspect as of 2026-08-25 (Ramp-reported, via Pragmatic Engineer interview) | **Confirmed — and already updated in the catalog.** The brief's "60%+" baseline is stale; do not print it. Keep scopes separate: the 30% figure covers frontend and backend repos; later figures cover all Ramp merged PRs | newsletter.pragmaticengineer.com (2026-08-25); ramp-inspect.yaml |
| Airbnb AirChat: ~64% of PRs through agentic coding; internal orchestrator never shipped | Headline: "About 64% of pull requests materialized through agentic coding" (catalog notes the figure comes from a third-party newsletter quoting engineers, DPE.org); orchestrator built from scratch, never shipped | No newer source, change, or contradiction found this round | **Unverifiable this round** — catalog value stands as-is with its existing provenance caveat | airbnb-airchat.yaml; no new source located |
| Stripe Minions: CI run limits and blueprints | Catalog: two-round CI cap; blueprint-directed runs | Confirmed verbatim. "We only have at most two rounds of CI … After the second push and CI run, we send the branch back to its human operator for manual scrutiny"; standard blueprint includes "one iteration against the full CI suite"; more rounds show "diminishing marginal returns." Blueprints are "a state machine that intermixes deterministic code nodes and free-flowing agent nodes." No deprecation or change found through August 2026 | **Confirmed** [V 6-0] | stripe.dev Part 2 (2026-02-19); Part 1 (2026-02-09) |
| Stripe Minions throughput | (context) | Over 1,000 merged PRs/week at Part 1 (2026-02-09), over 1,300/week at Part 2 (2026-02-19), "human-reviewed, but containing no human-written code." Neither part publishes an acceptance or merge-rate percentage | **Confirmed** [V 3-0] | stripe.dev Parts 1-2 |
| Shopify River adoption | Catalog: session-record and coauthorship metrics from the article | "Now, one in eight merged pull requests across Shopify is coauthored by it" (2026-05-28). In "a recent 30 day period": 59,918 River sessions in 5,170 Slack channels; 3,536 River-coauthored PRs merged; work of 7,000+ people touched (~1,200 more than when Tobi Lutke posted in early May 2026). The article itself says the numbers are "already wrong, in the upward direction" — treat 1-in-8 as a floor as of 2026-05-28. A secondary 2026-09-17 report attributes "~10,000 channels" and "~half of PRs agentic" to Lutke; not primary-confirmed | **Confirmed; newer secondary figure unverified** [V 6-0] | shopify.engineering/under-the-river (2026-05-28); shopifreaks.com (2026-09-17) [U] |
| Shopify Aquifer: session record, disposable workers | Catalog: durable session record; disposable workers | Confirmed verbatim. Session: "Durable identity. Append-only event log. Postgres-backed. The canonical truth about what's happened so far" — "Cells die, sandboxes die, machines die. The conversation doesn't." Agent work runs in disposable "session cells" (provisioned, run, suspended, destroyed, re-provisioned); "The harness lives outside the sandbox." Scope caveat: in Job mode (CI/batch) the session log is optional | **Confirmed** [V 6-0] | shopify.engineering/under-the-river |
| DoorDash code reviewer: scout plus two reviewers; soft and hard deadlines | Catalog as stated in the brief | Not re-verified this round; no change, retraction, or contradiction surfaced | **Unverifiable this round** | doordash-code-review.yaml (unchanged) |
| Sentry Junior | Catalog record sentry-junior.yaml | Not re-verified; nothing found | **Unverifiable this round** | sentry-junior.yaml (unchanged) |
| Sierra (Agency) | Catalog record sierra-pinecone.yaml | Not re-verified; nothing found | **Unverifiable this round** | sierra-pinecone.yaml (unchanged) |
| Dropbox Nova | Catalog record dropbox-nova.yaml | Not re-verified; nothing found | **Unverifiable this round** | dropbox-nova.yaml (unchanged) | 
| Uber uReview | Catalog record uber-ureview.yaml | All figures confirmed verbatim against the primary post (2025-08-11): "uReview today analyzes over 90% of the weekly ~65,000 diffs (equivalent of pull requests) landed at Uber" — while a later passage says "given the scale of diffs at Uber (65,000 per month)"; deployed across all six monorepos (Go, Java, Android, iOS, TypeScript, Python); reviews every commit with median 4-minute latency; over 10,000 commits/week excluding configuration files; "Engineers who interact with the tool mark 75% of its comments as useful, and we see over 65% of its posted comments addressed" versus "only 51% of human-written comments are considered as bugs by the author and addressed in the same changeset." Self-reported ~10 minutes saved per commit (~1,500 developer-hours weekly) has no external verification. Attribute all figures "as of August 2025"; keep the weekly-versus-monthly inconsistency, do not resolve it | **Confirmed** [V 9-0] | uber.com/blog/ureview |
| Databricks coSTAR | Catalog record databricks-costar.yaml | Not re-verified; nothing found | **Unverifiable this round** | databricks-costar.yaml (unchanged) |

## 6. Counterevidence

### Failures and retreats

- **AirChat remains the only verified internal-build retreat** in scope (orchestrator built,
  never shipped; cataloged). No second verified case of an internal agent cancelled, shrunk,
  or replaced by vendor tools was found this round. **[V, catalog]**
- **AWS / Kiro, December 2025 outage.** Per Fortune (reporting the Financial Times), an
  outage followed changes made with Amazon's internal Kiro AI coding tool; Amazon disputed AI
  attribution ("user error," "unrelated to AI"), and internal documents that cited "Gen-AI
  assisted changes" had the AI reference deleted before an operations meeting. Kiro is a
  vendor-built tool used internally — adjacent to, not an instance of, the internal-agent
  pattern; also relevant as a transparency caution. **[E]**
- **Grigorev production destruction (Fortune, 2026-03-18).** Alexey Grigorev's Claude Code
  agent destroyed his live production environment (network, services, database) after a setup
  mistake made it unable to distinguish production from a duplicate; recovery via AWS
  support. He attributed it to autonomous end-to-end execution without safeguards. Personal
  tooling, not an organizational internal agent — use as blast-radius evidence, not as an
  internal-agent failure. **[E]**
- **ITK bulk-conversion experiment (2026-03-09).** Maintainer Hans Johnson called his
  AI-driven ctest-to-GoogleTest conversion "mostly a failure (from a human effort
  perspective)": 846 candidates identified, ~36 attempted, the mechanical-management burden
  too high even though conversions introduced no new test failures. Independent, non-vendor. **[E]**

### Metric criticism

- **METR RCT (2025-07-10, independent).** Experienced open-source developers were 19% slower
  with early-2025 tools (Cursor Pro with Claude 3.5/3.7 Sonnet) on their own mature
  repositories (16 developers, 246 real issues, within-developer random assignment, avg.
  22k+ stars, 1M+ lines). They predicted a 24% speedup beforehand and still believed AI had
  sped them up by 20% after the measured 19% slowdown. Scope discipline: METR banners the
  result "out of date"; its 2026-02-24 follow-up restates the original 19% (CI +2% to +39%)
  and weakly estimates late-2025 tools flipped the direction (returning devs -18%, CI -38%
  to +9%; new devs -4%) — data METR itself calls "very weak evidence." The durable finding
  is the perception-versus-measurement gap, and it is the strongest independent ground for
  treating self-reported metrics (including PR-share and time-saved) with caution. **[V 6-0]**
- **uReview's comparison caveat.** The 75%-useful / 65%-addressed versus 51%-human comparison
  does not control for comment severity or type; human reviewers flag more design-level
  issues that are never "addressed in the same changeset." Qualifies Uber's interpretation,
  not the reported numbers. **[E, from commentary checked during verification]**
- **CodeRabbit report (2025-12-17, vendor research).** 470 open-source PRs (320 AI-co-authored,
  150 human-only): ~1.7x more issues per AI PR (10.83 vs 6.45), across logic,
  maintainability, security, performance; no issue category unique to AI code. Limits:
  authorship inferred from disclosure signals; CodeRabbit concedes the human-only label may
  be contaminated; issues measured with its own product; it sells AI code review. Label as
  vendor research. **[V as accurate report; medium for the substantive conclusion]**
- **Practitioner skepticism of PR-share metrics.** An Ask HN thread (2026-05-29) and an
  asadqi.com essay critique PR-count and coauthorship metrics as inflated ("Slop Grenades"-style
  co-authorship attribution arguments also appeared). Forum/essay grade — useful as a signal
  of skepticism, not as evidence. **[U/E]**

### Independent evidence on how well internal agents work

- **arXiv 2607.04697 (AIDev-pop; preprint, unrefereed).** 33,596 agent-authored PRs across
  2,807 repositories, December 2024–July 2025. Merge conflicts in 41.7% of co-active
  cross-agent PR pairs versus 19.8% intra-agent — but cross-agent pairs were rare (0.5% of
  co-active pairs, 122 repositories, N=115). Concurrent agent activity is common (40.2% of
  repositories contain co-active pairs; 79.4% of agent PRs fall in them). Authors explicitly
  bound applicability away from internal enterprise codebases — cite as open-source evidence
  of interaction costs, not as direct evidence about internal agents. **[V 3-0]**
- **ITK maintainer threads (2026-03-09/10, independent).** AI PR volume "overwhelming" and
  hard to review carefully (Niels Dekker); AI review comments useful for details/style, not
  architecture, with misconceptions resurfacing (Bradley Lowekamp); the project's mitigation
  was process rules plus a vendor review agent (Greptile), not reduced AI usage. **[E]**
- **Surveys.** A Fastly survey (July 2025, via Fortune) found senior engineers ship ~2.5x
  more AI-generated code than juniors, but nearly 30% of seniors said fixing AI output ate
  most of the time saved. METR-affiliated work found about half of AI coding solutions graded
  as passing on a prominent industry test would have been rejected by human reviewers. Both
  need their primary sources located before article use. **[E/U]**

## 7. Lessons under new evidence

No verified post-September-2026 source survived verification — every item below predates the
cutoff (as does almost all lesson-grade evidence in the field right now). The article should
not claim fresh 2026-Q4 corroboration. Labels: **supports** (new source agrees), **extends**
(adds a mechanism or boundary), **contradicts** (disagrees).

### Stop a run
- Stripe's two-round CI cap with mandatory return to a human operator (2026-02-19). **Supports** — a shipped stopping rule justified by "diminishing marginal returns." [V]
- Anthropic's premature-completion failure mode: a later agent instance "would look around, see that progress had been made, and declare the job done" (2025-11-26). **Supports** — stopping wrongly is a named production failure mode. [V]
- Anthropic Labs' "context anxiety" (models wrap up prematurely near the context limit; 2026-03-24). **Extends** — adds a model-behavior trigger for premature stopping, scoped to Claude Sonnet 4.5. [V]

### Review noise
- uReview's trust pipeline: generator plus secondary grader (best F1 in Uber's evaluation), confidence pruning, semantic deduplication, category suppression, five re-runs on the final commit (2025-08-11). **Supports** — noise control is engineered, not prompted. [V]
- ITK: AI review comments handle details and style, not architecture; misconceptions persist across rounds (2026-03-09). **Extends** — bounds where agent review helps, from an independent source. [E]
- Ask HN (2026-05-29): organizations moving deterministic checks to automation and keeping the human review signal independent of the generating AI. **Extends** — a practitioner adaptation of the same lesson. [E]

### Split the work
- Embat: one generalist split into 10+ specialists behind a router after cross-domain prompt interference (2026-07-21). **Supports** — independent first-party replication. [V]
- Anthropic: initializer plus coding agents with structured handoff artifacts (2025-11-26); later planner/generator/evaluator (2026-03-24). **Supports** — same pattern at a model vendor. [V]
- Cursor's planner/worker/judge with sub-planners, team attributing most system behavior to orchestration (via Osmani, 2026-04-28). **Extends** — industrial-scale variant. [E]

### Work can continue
- Aquifer: append-only Postgres session log as canonical record; disposable session cells; "Cells die … The conversation doesn't." (2026-05-28). **Supports** — shipped infrastructure for durable continuation. [V]
- Anthropic: full context resets beat in-place compaction when continuing, with handoff files (2025-11-26 and 2026-03-24). **Supports** — with the model-relative caveat that Opus 4.5 let the author drop resets. [V]
- arXiv AIDev-pop: cross-agent concurrent PRs conflict about twice as often as intra-agent (2026-07). **Extends** — continuation across agents collides more than within one agent. [V]
- Osmani: "the agent is amnesiac, but the filesystem is not" — durable state belongs in the environment (2026-04-28). **Extends** — practitioner formulation of the same rule. [E]

### Load tools
- Stripe: context via rule files plus an MCP server (Toolshed) exposing roughly 400-500 tools, on pre-warmed devboxes (2026-02-19). **Supports** — tool provisioning at scale inside the run environment. [V]
- GitHub Qubot: context loaded at runtime via the GitHub MCP Server; automatic routing between Kusto and Trino query engines; a reported 3x speed improvement attributed to curated context rather than model changes (2026-06-19). **Extends** — non-coding-domain replication. [E]
- MCP client best practices (2026-07-28) and Speakeasy's dynamic-tool-discovery guidance (vendor docs; a companion post claims ~100x token reduction for progressive discovery). **Extends** — the ecosystem is standardizing the pattern. [E/U]

### Steps without a model
- Stripe blueprints: state machines intermixing deterministic code nodes (linters, pushes) and agent nodes (2026-02-19). **Supports** — deterministic steps shipped as a primitive. [V]
- uReview: reviews every commit in CI — a deterministic gate around model judgment (2025-08-11). **Supports**. [V]
- Anthropic/Osmani: a test ratchet — agents prohibited from removing or editing tests (2026-04-28). **Extends** — gates that protect the gate. [E]
- arXiv 2603.20449: solver-aided verification of policy compliance — SMT checking with no model in the loop (2026-03-20, independent academic). **Extends** — formal-methods endpoint of the same lesson. [E]

### Test on your work
- Anthropic: unit tests and curl checks passed while end-to-end behavior was broken; reliable verification required prompting the agent to check features with browser automation "as a human user would" (2025-11-26). **Supports**. [V]
- Anthropic: the feature list stored as JSON with `passes: false` fields because the model is less likely to inappropriately alter JSON (2025-11-26). **Extends** — evaluation state made durable and model-resistant. [V]
- Anthropic Labs: standalone skeptical evaluator outperformed making the generator self-critical; out-of-the-box Claude judged a poor QA agent (2026-03-24). **Extends** — separate who builds from who checks. [V]

**Cross-cutting qualifier (must appear wherever the thesis is stated):** harness complexity
is model-relative. "Every component in a harness encodes an assumption about what the model
can't do on its own"; the same author dropped sprint contracts and context resets after
moving to Opus 4.5/4.6, while claiming the space of interesting harness combinations "moves"
rather than shrinks (2026-03-24). [V 9-0] Also, per InfoQ's summary of Ramp's account,
session speed and quality at Ramp were still mainly limited by the model's intelligence —
models "make mistakes, hallucinate, and require human oversight." [E]

## 8. Reader questions

Caveat: the workflow ran no dedicated demand survey. The table below comes from threads and
essays actually fetched (one Ask HN thread, ITK discourse, practitioner essays). Frequency
signals are qualitative; treat "which the catalog answers" as a first-pass editorial mapping.

| Question | Frequency signal | Example | Catalog answers it? |
|---|---|---|---|
| How do we manage PR review load as AI output grows? | Ask HN thread; ITK maintainers | news.ycombinator.com/item?id=48329446 (2026-05-29) | Partly — review-noise lesson; no org-design guidance |
| Should AI review AI-generated code? | Recurring in the same threads | Same Ask HN thread; ITK discourse (2026-03) | Partly — uReview-style gates documented |
| Must maintainers address every AI review comment? | ITK norm-setting discussion | discourse.itk.org (2026-03-10) | No — social norms of agent output are out of scope |
| Can we auto-approve low-risk agent PRs? | Commenter proposals; noted GitHub lacked native support (2026-05-31, hedged) | Same Ask HN thread | No — product mechanics not covered |
| Where should durable agent state live? | Practitioner essays (Osmani), vendor docs | addyosmani.com/blog/long-running-agents/ | Yes — work-can-continue lesson; Aquifer record |
| How do agents discover tools at runtime? | MCP best-practices docs; vendor posts | modelcontextprotocol.io (2026-07-28) | Yes — load-tools lesson |
| How do we stop a runaway run? | Stripe/Anthropic accounts | stripe.dev Part 2 | Yes — stop-a-run lesson |
| How much harness does an agent need (cost/benefit)? | Anthropic Labs cost data (22x multiplier example) | anthropic.com/engineering/harness-design-long-running-apps | Partly — no cost lesson |
| Does individual velocity translate to roadmap delivery? | Ask HN self-reports; METR perception gap | news.ycombinator.com; metr.org | No — org-level outcomes not covered |
| Build in-house or buy a vendor agent? | Ramp's stated reasons; StackOne-style maps on the buy side | Pragmatic Engineer (2026-08-25) | No — the catalog deliberately takes no position |

## 9. Possible openings for the article

1. **Floors, not boasts.** Open on Shopify calling its own numbers "already wrong, in the
   upward direction" — 1-in-8 merged PRs as a floor as of 2026-05-28 — and on Ramp's
   trajectory (roughly 30% → 60% → 75% of merged PRs between late 2025 and May 2026). Frame:
   the catalog tracks self-reported numbers with dates and scopes because they move fast and
   in one direction.
2. **The agent that prompts the agent.** Ramp built a second agent (the Architect) whose only
   job is writing prompts and context files for its finance agent (the Doer). A concrete,
   verified image of environment-work multiplying — and of the catalog's agent-versus-infrastructure
   split appearing in the wild.
3. **Nineteen percent slower, twenty percent "faster."** METR's RCT found experienced
   developers measurably slower while believing they were faster — the cleanest justification
   for why a public catalog should quote metrics exactly as published, with scope and date,
   and nothing more.
4. **The conversation outlives the computer.** Aquifer's session record: "Cells die,
   sandboxes die, machines die. The conversation doesn't." Lead with the infrastructure
   records as the catalog's own answer to where the hard problems live.
5. **The map is thinnest where the mess is.** Coding and code review dominate (35 and 27 of
   66 records); this research had to dig for Embat's support platform and Ramp's finance
   agents to fill the gaps — an honest statement of what the catalog does not yet know.

## 10. Gaps and open questions

- **River's current rate.** A secondary 2026-09-17 report attributes "~10,000 channels" and
  "~half of PRs agentic" to Tobi Lutke; no primary confirmation. Shopify's next update would
  move the article's headline number.
- **Named-agent current states not re-verified:** Airbnb AirChat (64% figure and the
  never-shipped orchestrator), DoorDash, Sentry Junior, Sierra, Dropbox Nova, Databricks
  coSTAR. Nothing suggested change; nothing confirmed it either.
- **No verified post-cutoff first-party accounts.** The lessons test rests on pre-cutoff
  evidence. A dedicated sweep of conference talks, podcasts, SEC filings, and engineering
  blogs published after 2026-09-15 is the highest-value next pass.
- **Positioning is thin.** Only two adjacent catalogs were fetched (awesome-ai-agents,
  StackOne). Analyst maps (Gartner &c.) and newsletters were not systematically collected.
- **Reader demand was a light pass at best.** A real pass would survey HN/Reddit/conference
  Q&A systematically; the table in section 8 is indicative only.
- **Verifier budget caveats.** Several verifier sessions exhausted their search budgets
  before third-party contradiction sweeps, so "no dispute found" findings are weaker than
  they appear. The METR late-2025-tools update and the uReview usefulness figures carry no
  stated time period.
- **Small-print items to pin at intake:** Embat's "Claude Managed Agents" product name;
  Browserbase and YARA canonical URLs and dates; the Fastly survey's and the METR
  half-fail-graded-passing claim's primary sources; the ramp trajectory's differing scopes
  (frontend/backend repos versus all merged PRs).

## 11. Sources

All accessed 2026-10-08. Type: CR = company report (first-party), IND = independent, VM =
vendor marketing, PRESS = press/secondary. Verification status per the legend.

| URL | Title / publisher | Date | Type | Status |
|---|---|---|---|---|
| https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents | Minions: Stripe's one-shot, end-to-end coding agents (Stripe) | 2026-02-09 | CR | [V] |
| https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2 | Minions Part 2 (Stripe) | 2026-02-19 | CR | [V] |
| https://shopify.engineering/under-the-river | Under the River (Shopify Engineering) | 2026-05-28 | CR | [V] |
| https://www.uber.com/blog/ureview | uReview: Scalable, Trustworthy GenAI for Code Review at Uber | 2025-08-11 | CR | [V] |
| https://ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal | We built an agent to prompt our internal finance agent (Ramp Labs) | 2025-10-01 UTC | CR | [V] |
| https://www.embat.io/tech/internal-ai-agent-platform | Agent Mbatt: overall structure / How we built an internal AI agent platform (Embat) | 2026-07-21 | CR | [V] |
| https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | Effective harnesses for long-running agents (Anthropic) | 2025-11-26 | CR (model vendor) | [V] |
| https://www.anthropic.com/engineering/harness-design-long-running-apps | Harness design for long-running application development (Anthropic Labs) | 2026-03-24 | CR (model vendor) | [V] |
| https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ | Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity (METR) | 2025-07-10 | IND | [V] |
| https://metr.org/blog/2026-02-24-uplift-update/ | METR uplift update | 2026-02-24 | IND | [V] |
| https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report | Our new report: AI code creates 1.7x more problems (CodeRabbit) | 2025-12-17 | VM (vendor research) | [V as report] |
| https://www.coderabbit.ai/whitepapers/state-of-ai-vs-human-code-generation-report | Full report (CodeRabbit, gated) | 2025-12-17 | VM | [E] |
| https://arxiv.org/abs/2607.04697 | AI Agent Pull Requests on GitHub: Frequency, Structure, and Merge Conflict Rates | 2026-07-06 (v2 07-07) | IND (unrefereed preprint) | [V] |
| https://arxiv.org/abs/2602.09185 | AIDev-pop dataset provenance | 2026 | IND | [V, provenance check] |
| https://arxiv.org/abs/2603.20449 | Solver-Aided Verification of Policy Compliance in Tool-Augmented LLM Agents (Univ. of Washington) | 2026-03-20 | IND | [E] |
| https://newsletter.pragmaticengineer.com | Why Ramp built its own in-house coding agent, Inspect (The Pragmatic Engineer) | 2026-08-25 | IND (relaying Ramp-reported numbers) | [E] |
| https://www.infoq.com | Ramp builds internal coding agent that powers 30% of merged PRs (InfoQ) | 2026-01-23 | PRESS | [E] |
| https://www.infoq.com | Stripe engineers deploy Minions, autonomous agents (InfoQ) | 2026-03-20 | PRESS | [E] |
| https://www.infoq.com | Anthropic designs three-agent harness (InfoQ) | 2026-04-04 | PRESS | [E] |
| https://news.ycombinator.com/item?id=48329446 | Ask HN: managing PR review load as AI output grows | 2026-05-29 | IND (forum) | [E] |
| https://discourse.itk.org | AI-generated pull requests overwhelming, hard to review (ITK maintainers) | 2026-03-09/19 | IND (forum) | [E] |
| https://fortune.com | An AI agent destroyed this coder's entire database / AWS-Kiro outage reporting (Fortune, citing FT) | 2026-03-18 | PRESS | [E] |
| https://github.com/e2b-dev/awesome-ai-agents | awesome-ai-agents list | created 2023-06-19; last commit 2026-08-21 | Community list | [E] |
| https://cloud.google.com/discover/what-are-ai-agents | What are AI agents? (Google Cloud glossary) | updated 2026-04-02 | VM | [E] |
| https://www.stackone.com | 120+ agentic AI tools mapped across 11 categories (StackOne) | 2026-02-08 | VM | [E] |
| https://github.blog/ai-and-ml/github-copilot/how-we-built-an-internal-data-analytics-agent/ | How we built an internal data analytics agent — Qubot (GitHub) | 2026-06-19 | CR | [E; already cataloged] |
| https://addyosmani.com/blog/long-running-agents/ | Long-running agents (Addy Osmani) | 2026-04-28 | IND (practitioner; Anthropic staff) | [E] |
| https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices | MCP client best practices (progressive discovery) | 2026-07-28 | IND (spec docs) | [E] |
| https://www.speakeasy.com/mcp/tool-design/dynamic-tool-discovery | Dynamic tool discovery in MCP (Speakeasy) | undated | VM | [U] |
| https://blog.bytebytego.com | Minions explainer (ByteByteGo) | 2026-03-16 | PRESS | [corroboration only] |
| https://www.shopifreaks.com | Report of Lutke remarks: ~10,000 channels, ~half of PRs | 2026-09-17 | PRESS | [U] |
| https://www.latent.space | The Age of Async Agents — Cognition (Walden Yan) | undated | PRESS (podcast) | [U] |
| https://browserbase.com | How we build Internal Agents at Browserbase | undated | CR? | [U] |
| https://incentro.com | YARA — Youforce Automated Request Assistant | undated | VM (builder consultancy) | [U] |
| https://masterofcode.com/blog | AI agents for internal operations: 27 use cases | undated | VM | [U; lead sheet only] |

Catalog files referenced (local, current at 2026-10-08): data/agents/ramp-inspect.yaml,
airbnb-airchat.yaml, doordash-code-review.yaml, sentry-junior.yaml, sierra-pinecone.yaml,
dropbox-nova.yaml, uber-ureview.yaml, databricks-costar.yaml, github-qubot.yaml.
