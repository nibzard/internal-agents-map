// ABOUTME: Checks the record contribution handoff, including manual clipboard fallback.
// ABOUTME: The preview remains usable on mobile and without JavaScript.
import { expect, test } from '@playwright/test';

test('previews the specific record prompt with keyboard input', async ({ page }) => {
  await page.goto('/agents/stripe-minions');
  const section = page.locator('[data-record-contribution]');
  const preview = section.locator('summary');
  await preview.focus();
  await page.keyboard.press('Enter');
  const prompt = section.getByRole('textbox');
  await expect(prompt).toBeVisible();
  await expect(prompt).toHaveValue(/Record: data\/agents\/stripe-minions.yaml/);
  await expect(prompt).toHaveValue(/ask what I want changed before editing/);
  const issue = new URL((await section.getByRole('link', { name: 'Suggest on GitHub' }).getAttribute('href'))!);
  expect(issue.searchParams.get('agent')).toBe('Minions at Stripe');
  expect(issue.searchParams.get('request')).toBe('Fix an existing entry');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('copies the preview text and announces success', async ({ page, context }, testInfo) => {
  test.skip(testInfo.project.name === 'no-javascript', 'Clipboard copying needs JavaScript.');
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/agents/stripe-minions');
  await page.getByRole('button', { name: 'Copy update prompt' }).click();
  await expect(page.locator('[data-update-status]')).toHaveText('Prompt copied. Paste it into your coding agent.');
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).toBe(await page.locator('#update-prompt').inputValue());
  expect(copied).toContain('https://internal-agents.com/agents/stripe-minions.md');
});

test('selects the prompt when clipboard access fails', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'no-javascript', 'The preview works natively without JavaScript.');
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: () => Promise.reject(new Error('Clipboard denied')) },
    });
  });
  await page.goto('/agents/stripe-minions');
  await page.getByRole('button', { name: 'Copy update prompt' }).click();
  const prompt = page.locator('#update-prompt');
  await expect(prompt).toBeVisible();
  await expect(prompt).toBeFocused();
  expect(await prompt.evaluate((element: HTMLTextAreaElement) => element.selectionEnd - element.selectionStart))
    .toBe((await prompt.inputValue()).length);
  await expect(page.locator('[data-update-status]')).toContainText('Copy the selected prompt');
});

test('keeps the generic invitation on the catalog and wires record navigation', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.locator('.contribution-invite')).toContainText('Know an internal agent?');
  await expect(page.locator('[data-record-contribution]')).toHaveCount(0);
  await page.locator('a[href="/agents/stripe-minions"]').first().click();
  await expect(page.locator('[data-record-contribution]')).toContainText('Improve this record');
  if (testInfo.project.name === 'no-javascript') {
    await expect(page.getByRole('button', { name: 'Copy update prompt' })).toHaveCount(0);
  } else {
    await expect(page.getByRole('button', { name: 'Copy update prompt' })).toBeVisible();
  }
});
