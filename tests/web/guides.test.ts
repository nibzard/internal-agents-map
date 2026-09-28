// ABOUTME: Checks that each guide export carries every heading and link of its page.
// ABOUTME: Page and export read one source, so a change to the text reaches both.

import type { APIContext, APIRoute } from 'astro';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { beforeAll, describe, expect, it } from 'vitest';
import Definitions from '../../src/pages/definitions.astro';
import Methodology from '../../src/pages/methodology.astro';
import { GET as definitionsMarkdown } from '../../src/pages/definitions.md';
import { GET as methodologyMarkdown } from '../../src/pages/methodology.md';
import { canonicalUrl, guidePath } from '../../src/lib/routes';
import { SUPERVISION_DEFINITIONS } from '../../src/lib/guide-content';

describe('the supervision definitions', () => {
  it('maps each attention boundary to one scoped level', () => {
    expect(SUPERVISION_DEFINITIONS.rows.map(({ id, level }) => [id, level])).toEqual([
      ['continuous-steering', '2'],
      ['work-product-review', '3'],
      ['outcome-review', '4'],
      ['exception-only', '5'],
      ['unknown', '—'],
    ]);
  });
});

/** The part of the page the export represents. The layout is not in the export. */
function article(html: string): string {
  return html.slice(html.indexOf('<main'), html.indexOf('</main>'));
}

/** The words of an HTML fragment, without markup and without extra spaces. */
function words(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ')
    .trim();
}

function headings(html: string): string[] {
  return [...html.matchAll(/<h[1-3][^>]*>([\s\S]*?)<\/h[1-3]>/g)].map((match) => words(match[1]!));
}

function links(html: string): { href: string; text: string }[] {
  return [...html.matchAll(/<a href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/g)].map((match) => ({
    href: match[1]!,
    text: words(match[2]!),
  }));
}

/** The address the export writes for a link of the page. */
function exported(href: string, page: string): string {
  if (href.startsWith('#')) return `${page}${href}`;
  if (href.startsWith('/')) return canonicalUrl(href);
  return href;
}

async function markdown(route: APIRoute): Promise<string> {
  const response = await route({} as APIContext);
  return await (response as Response).text();
}

const guides = [
  { name: 'Definitions', component: Definitions, route: definitionsMarkdown, page: 'definitions' },
  { name: 'Methodology', component: Methodology, route: methodologyMarkdown, page: 'methodology' },
];

for (const guide of guides) {
  describe(`the ${guide.name} export`, () => {
    let html = '';
    let text = '';
    /** The words of the export, without the Markdown bold marks. */
    let prose = '';
    let page = '';

    beforeAll(async () => {
      const container = await AstroContainer.create();
      html = article(await container.renderToString(guide.component));
      text = await markdown(guide.route);
      prose = words(text).replace(/\*\*/g, '');
      page = canonicalUrl(guidePath(guide.page));
    });

    it('carries every heading of the page', () => {
      const found = headings(html);
      expect(found.length).toBeGreaterThan(5);
      for (const heading of found) expect(prose).toContain(heading);
    });

    it('carries every table definition of the page', () => {
      const bodies = [...html.matchAll(/<tbody[^>]*>([\s\S]*?)<\/tbody>/g)].map((match) => match[1]).join('');
      const cells = [...bodies.matchAll(/<(?:th|td)\b[^>]*>([\s\S]*?)<\/(?:th|td)>/g)];
      expect(cells.length).toBeGreaterThan(0);
      for (const cell of cells) expect(prose).toContain(words(cell[1]!));
    });

    it('carries every link of the page, with its address', () => {
      const found = links(html);
      expect(found.length).toBeGreaterThan(3);
      for (const link of found) {
        // A marker link also carries the reason as a Markdown link title.
        const target = `](${exported(link.href, page)}`;
        const cited = text.includes(`${target})`) || text.includes(`${target} "`);
        expect(cited, link.href).toBe(true);
        expect(prose, link.href).toContain(link.text.replace(/ ↗$/, ''));
      }
    });
  });
}
