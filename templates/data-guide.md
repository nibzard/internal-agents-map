# Reading the Internal Agents Map programmatically

No account, API key, or agent registration is required. These are public static files.

1. Fetch [the compact index](https://internal-agents.com/agents/index.json).
2. Select `catalog_section` (`agents` or `infrastructure`), then match `company`, `agent_name`, `approach_type`, `domains`, or `rubric.invocation`
   to your question. Structural type and invocation are independent; invocation is an agent facet.
3. Follow an entry's `json_url` or `markdown_url` to retrieve its evidence.
4. Cite original publisher URLs and retain relevant dates and qualifications.

The compact index has its own `schema_version: 3` and an `approaches` array. Each
entry includes identification and filter fields, `last_reviewed_at`, a human-readable
`url`, and links to the individual JSON and Markdown representations.

[The complete dataset](https://internal-agents.com/agents.json) and individual JSON
records use the catalog schema version below. Individual records retain the same
`approaches`, `claims`, `sources`, and `companies` collections, limited to one approach,
its evidence, and its organization. Join each approach's `company_id` to a company `id`
for the name, homepage, and logo descriptor. Join `claim_ids` and `source_ids` by `id`;
do not infer facts from an agent's name or fill in unknown fields.

Markdown is also available by sending `Accept: text/markdown` to a published HTML
page. HTML is the default; an explicit `.md` URL always returns Markdown, with the
`text/plain` media type because some assistant browsers refuse `text/markdown`.
Negotiated responses use `text/markdown` and `Vary: Accept`. Filters and URL fragments do not reduce the exported
collection; use individual records for selective retrieval. `/index.md` holds Agents and `/infrastructure.md` holds Infrastructure. The historical `/agents.json` and `/agents/index.json` endpoints retain both collections.

Distinguish reported facts from catalog judgments. Keep provenance, confidence,
metric scopes, denominators, dates, and all evidence relations, including
`contradicts` and `contextualizes`. An unknown value is not a negative finding.
Company-reported results are not independently verified unless a source says so.

Source `url` and `canonical_url` refer to the publisher, not this website. Capture
paths remain repository-relative: resolve them against
https://github.com/steel-experiments/internal-agents-map/blob/main/.
Preserved source files are not hosted under this website's `/archive/` path.

These files are regenerated on publication. Revalidate cached responses rather than
assuming an unchanged URL contains unchanged data. The sitemap lists canonical HTML
pages; `llms.txt` links to the reading formats. Crawl permission does not replace
the repository license or the rights of cited publishers.

---
