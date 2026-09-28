// ABOUTME: Checks that the site reads the schema 8 export: item ID paths, inline roles and metric fields.
// ABOUTME: A one-record fixture keeps these checks independent of the committed catalog.

import { readFileSync } from 'node:fs';
import { describe, expect, it, vi } from 'vitest';
import { validateCatalog } from '../../src/lib/catalog';
import { entryView } from '../../src/lib/entry-view';
import { recordJson, recordMarkdown } from '../../src/lib/exports';

// The lessons read the committed catalog. This fixture is a different catalog.
vi.mock('../../src/lib/lessons', () => ({ lessonsForApproach: () => [] }));

const ID = 'doordash-code-review';
const TEXT = readFileSync(new URL('../fixtures/catalog/schema-8.json', import.meta.url), 'utf8');

// The fixture is plain JSON, so the tests can change any field of it.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function fixture(): any {
  return JSON.parse(TEXT);
}

function claimAt(catalog: ReturnType<typeof fixture>, field: string) {
  const claim = catalog.claims.find((item: { field: string }) => item.field === field);
  if (!claim) throw new Error(`the fixture has no claim at "${field}".`);
  return claim;
}

describe('schema 8 validation', () => {
  it('accepts the fixture', () => {
    expect(() => validateCatalog(fixture())).not.toThrow();
  });

  it('rejects a claim path that uses a list index', () => {
    const broken = fixture();
    claimAt(broken, 'primitives.lead-scout').field = 'primitives.2';
    expect(() => validateCatalog(broken)).toThrow(/field "primitives\.2"\) uses a list index/);
  });

  it('rejects a primitive claim without a valid role', () => {
    const broken = fixture();
    claimAt(broken, 'primitives.lead-scout').role = 'decoration';
    expect(() => validateCatalog(broken)).toThrow(/field "primitives\.lead-scout"\) has no valid role/);
  });

  it('rejects an item ID that does not match the claim path', () => {
    const broken = fixture();
    claimAt(broken, 'primitives.lead-scout').item_id = 'deep-reviewers';
    expect(() => validateCatalog(broken)).toThrow(/field "primitives\.lead-scout"\) has item_id "deep-reviewers"/);
  });

  it('rejects an alias metric whose target claim does not resolve', () => {
    const broken = fixture();
    const [path] = Object.keys(broken.approaches[0].page_content.aliases);
    claimAt(broken, path).duplicate_of = `${ID}--key-metrics-ghost`;
    expect(() => validateCatalog(broken)).toThrow(/is a duplicate of unknown claim "doordash-code-review--key-metrics-ghost"/);
  });

  it('rejects a canonical metric without its observation fields', () => {
    const broken = fixture();
    delete claimAt(broken, 'headline_metric').subject;
    expect(() => validateCatalog(broken)).toThrow(/field "headline_metric"\) lacks category, basis, or subject/);
  });

  it('rejects a page alias that no claim carries', () => {
    const broken = fixture();
    broken.approaches[0].page_content.aliases['key_metrics.ghost'] = { duplicate_of: 'headline_metric', reason: 'None.' };
    expect(() => validateCatalog(broken)).toThrow(/alias "key_metrics\.ghost" does not resolve/);
  });

  it('rejects an old claim ID that maps to an unknown claim', () => {
    const broken = fixture();
    broken.claim_aliases[`${ID}--primitives-9`] = `${ID}--primitives-ghost`;
    expect(() => validateCatalog(broken)).toThrow(
      /claim alias "doordash-code-review--primitives-9" names unknown claim "doordash-code-review--primitives-ghost"/,
    );
  });
});

describe('the entry of a schema 8 record', () => {
  const catalog = validateCatalog(fixture());
  const entry = entryView(catalog, ID);
  const fields = (claims: readonly { field: string }[]) => claims.map((claim) => claim.field);

  it('takes the section of a primitive from its role', () => {
    expect(fields(entry.mechanismClaims)).toEqual(['primitives.grounded-findings']);
    expect(fields(entry.validationClaims)).toEqual(['primitives.disprove-it-pass', 'primitives.evaluation-loop']);
    expect(fields(entry.workflowClaims)).toEqual([
      'primitives.automatic-review-trigger',
      'primitives.lead-scout',
      'primitives.deep-reviewers',
      'primitives.optional-fixer',
    ]);
  });

  it('takes the category, basis, and subject of a metric from its claim', () => {
    const headline = entry.observationItems.find((item) => item.claim.field === 'headline_metric')!;
    expect(headline.categoryLabel).toBe('Adoption output');
    expect(headline.basisLabel).toBe('Reported measurement');
    expect(headline.subject).toBe('Typical weekly reviews across 56 repositories');
  });

  it('keeps an alias metric out of the observations and names its target', () => {
    expect(fields(entry.aliasObservationClaims)).toEqual(['key_metrics.prs-reviewed-typical-week-repositories']);
    expect(fields(entry.canonicalObservationClaims)).not.toContain('key_metrics.prs-reviewed-typical-week-repositories');
    expect(entry.aliasObservationRelations.map((item) => [item.target.id, item.reason])).toEqual([
      [`${ID}--headline-metric`, 'Same review count, repository population, period, and qualification as the headline observation.'],
    ]);
  });

  it('gives every old claim ID an anchor on the entry page', () => {
    const anchors = new Set(entry.claims.flatMap((claim) => [claim.anchor, ...claim.aliasAnchors]));
    for (const old of Object.keys(catalog.claim_aliases ?? {})) expect(anchors, old).toContain(`claim-${old}`);
    const primitive = entry.claims.find((claim) => claim.field === 'primitives.lead-scout')!;
    expect(primitive.aliasAnchors).toEqual([`claim-${ID}--primitives-2`]);
    // An ID that did not change needs no second anchor.
    expect(entry.summary!.aliasAnchors).toEqual([]);
  });

  it('keeps the evidence and the section of every claim when the primitives are reordered', () => {
    const reordered = fixture();
    reordered.claims.reverse();
    reordered.approaches[0].claim_ids.reverse();
    const after = entryView(validateCatalog(reordered), ID);
    const before = new Map(entry.claims.map((claim) => [claim.id, claim]));
    for (const claim of after.claims) {
      expect(claim.citations, claim.id).toEqual(before.get(claim.id)!.citations);
      expect(claim.text, claim.id).toBe(before.get(claim.id)!.text);
    }
    expect(fields(after.mechanismClaims)).toEqual(fields(entry.mechanismClaims));
    expect(fields(after.workflowClaims)).toEqual(fields(entry.workflowClaims));
  });

  it('shows no rubric state or identity in the Markdown record', () => {
    const markdown = recordMarkdown(catalog, ID);
    expect(markdown).not.toMatch(/^- (State|Identity):/m);
    expect(markdown).toContain('- Evidence strength:');
  });

  it('carries the old claim IDs of the record in its JSON export', () => {
    const record = JSON.parse(recordJson(catalog, ID));
    expect(record.claim_aliases).toEqual(catalog.claim_aliases);
    expect(() => validateCatalog(record)).not.toThrow();
  });
});
