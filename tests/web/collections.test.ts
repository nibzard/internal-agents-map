// ABOUTME: Collection boundaries preserve full exports without equating infrastructure with agents.
import { describe, expect, it } from 'vitest';
import { catalogSection, collectionCounts, loadCatalog, validateCatalog } from '../../src/lib/catalog';
import { directoryCards, entryView } from '../../src/lib/entry-view';
import { catalogMarkdown, compactIndexJson, recordJson, recordMarkdown } from '../../src/lib/exports';
import { placements } from '../../src/lib/definitions';
const catalog = loadCatalog();

describe('derived collections', () => {
  it('assigns every record exactly once and rejects unknown or conflicting types', () => {
    for (const item of catalog.approaches) expect(item.catalog_section).toBe(catalogSection(item.approach_type));
    expect(() => catalogSection('unreviewed-type')).toThrow('Unknown approach type');
    const copy = structuredClone(catalog) as any;
    copy.approaches[0].catalog_section = copy.approaches[0].catalog_section === 'agents' ? 'infrastructure' : 'agents';
    expect(() => validateCatalog(copy)).toThrow('inconsistent catalog_section');
  });
  it('counts a family once and deduplicates reused source URLs', () => {
    for (const section of ['agents', 'infrastructure'] as const) {
      const records = catalog.approaches.filter((item) => item.catalog_section === section);
      const counts = collectionCounts(catalog, section);
      expect(counts.entries).toBe(records.length);
      const ids = new Set(records.flatMap((item) => item.source_ids));
      expect(counts.sources).toBe(new Set(catalog.sources.filter((source) => ids.has(source.id)).map((source) => source.canonical_url ?? source.url)).size);
    }
    const family = catalog.approaches.find((item) => item.approach_type === 'agent-system')!;
    expect(collectionCounts({ ...catalog, approaches: [family] }, 'agents').entries).toBe(1);
  });
  it('keeps full and compact JSON inclusive and individual exports identifiable', () => {
    const compact = JSON.parse(compactIndexJson(catalog));
    expect(compact.schema_version).toBe(4);
    expect(compact.approaches).toHaveLength(catalog.approaches.length);
    for (const item of catalog.approaches) {
      expect(JSON.parse(recordJson(catalog, item.id)).approaches[0].catalog_section).toBe(item.catalog_section);
      expect(compact.approaches.find((record: any) => record.id === item.id).catalog_section).toBe(item.catalog_section);
    }
  });
  it('prevents infrastructure matching agent supervision or the agent quadrant', () => {
    for (const card of directoryCards(catalog).filter((item) => item.catalogSection === 'infrastructure')) {
      expect(card.boundaries).toEqual([]);
      expect(card.invocation).toEqual([]);
      expect(placements(catalog).some((item) => item.id === card.id)).toBe(false);
    }
  });
  it('keeps collection Markdown separate while preserving every claim across both', () => {
    const agents = catalogMarkdown(catalog);
    const infrastructure = catalogMarkdown(catalog, 'infrastructure');
    expect(agents).not.toContain('## Harvey — Spectre');
    expect(infrastructure).toContain('## Harvey — Spectre');
    for (const claim of catalog.claims) expect(agents + infrastructure).toContain(claim.text.trim());
  });
});

describe('infrastructure reading profile', () => {
  it('preserves Spectre sandboxes ahead of scoped use examples without a disclaimer or autonomy', () => {
    const text = recordMarkdown(catalog, 'harvey-spectre');
    expect(text).not.toContain('This entry describes supporting infrastructure');
    expect(text).not.toContain('- Autonomy:');
    expect(text.indexOf('## Capabilities and architecture')).toBeLessThan(text.indexOf('## Documented uses'));
    const entry = entryView(catalog, 'harvey-spectre');
    expect(text).toContain(entry.architectureClaims.find((claim) => claim.field === 'architecture.sandbox')!.text);
  });
  it('renders inverse uses from authored dependencies, without same-company inference', () => {
    expect(entryView(catalog, 'shopify-internal-agents').relatedEntries.find((item) => item.id === 'shopify-river')?.group).toBe('used-by');
    for (const entry of catalog.approaches) {
      const related = entryView(catalog, entry.id).relatedEntries;
      expect(new Set(related.map((item) => item.id)).size).toBe(related.length);
      for (const link of related.filter((item) => item.group === 'used-by')) {
        expect(catalog.approaches.find((item) => item.id === link.id)?.relationships).toContainEqual({ type: 'built-on', approach_id: entry.id });
      }
    }
    expect(entryView(catalog, 'harvey-spectre').relatedEntries.filter((item) => item.group === 'used-by').map((item) => item.id)).not.toContain('harvey-security-operations');
  });
});
