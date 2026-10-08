# LOG

## Instructions
This log tracks all tasks completed in this project. Use one record per task with the following format:
- **Timestamp**: Date in YYYY-MM-DD format
- **Task**: Brief description of what needed to be done
- **Action**: Specific steps taken, including key commands/tools used
- **Result**: Outcome and any relevant metrics/details

Add new entries at the bottom of the table.

## Records
| Timestamp | Task | Action | Result |
|-----------|------|--------|--------|
| 2026-10-08 | Research and write the launch-article dossier for the internal-agents.com Steel blog announcement | Ran the "deep-research" workflow against the launch-article research brief (102 agents, ~34 min, 5 search angles, 20 sources fetched, 99 claims extracted, 25 adversarially verified: 24 confirmed, 1 refuted); wrote docs/launch-article-research-2026-10.md with all 11 sections from the brief (summary, timeline, positioning, new cases, fact check, counterevidence, lessons, reader questions, openings, gaps, sources) | Ramp Inspect fact check: live catalog already headlines 75% of merged PRs (May 2026), so the brief's "60%+" baseline is stale. Verified 2 new catalog-intake candidates outside coding/code review: Embat Mr. Batt (support, 2026-07-21) and Ramp Doer/Architect finance agents (2025-10-01 UTC; supervision unknown because the autonomy claim was refuted 1-2). GitHub Qubot confirmed already cataloged. Stripe Minions, Shopify River/Aquifer, and Uber uReview metrics confirmed verbatim with scope caveats. METR RCT and CodeRabbit vendor report documented as counterevidence. No verified post-mid-September-2026 first-party accounts found. No catalog data files modified; research output only |
| 2026-10-08 | Catalog intake from the verified launch-research dossier: add two new agent records (branch feat/intake-embat-ramp-finance) | Added data/agents/embat-mr-batt.yaml — Embat "Mr. Batt" internal agent platform (support domain, first-party engineering blog 2026-07-21, source captured as archive/sources/embat-mr-batt-source-1; agent-system, deployed, autonomy unknown; excluded the ~70% support-response-time figure from the author bio because it is NOT in the preserved capture). Added data/agents/ramp-finance-agents.yaml — Ramp "Doer and Architect" finance agents (finance-ops, Ramp Labs post dated 2025-10-01 UTC, source captured as archive/sources/ramp-finance-agents-source-1; agent-system, deployed, autonomy recorded as unknown because adversarial verification refuted the "autonomous after intake" reading 1-2, recorded as a catalog-judgment lesson instead: async-intake-not-autonomy). Added Embat registry entry to data/companies.yaml (logo: none, pending brand review). Regenerated generated outputs: README.md, docs/patterns.md, docs/adoption-lessons.md, docs/landscape.md, data/agents.json, src/lib/schema-values.ts, routing-manifest.json | uv build clean; full npm run verify green (829 e2e passed; one earlier e2e run had 5 load flakes that all passed in isolation and in the final full run). routing-manifest.json now covers 68 approaches across 44 organizations. Working-tree changes left pending review |
