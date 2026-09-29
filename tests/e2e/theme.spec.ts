// ABOUTME: Exercises theme selection, persistence, and Astro navigation in real browsers.
// ABOUTME: The light default also works without JavaScript or access to browser storage.
import { expect, test, type Page } from '@playwright/test';

const themeButton = (page: Page) => page.locator('[data-theme-toggle]:visible');

async function followEntry(page: Page): Promise<void> {
  await page.locator('#block-builderbot h3 a').click();
  await expect(page).toHaveURL(/\/agents\/block-builderbot$/);
  await expect(page.locator('h1')).toContainText('Builderbot');
}

test('uses the light theme until the reader makes a choice, whatever the system prefers', async ({ page, javaScriptEnabled }) => {
  for (const colorScheme of ['dark', 'light'] as const) {
    await page.emulateMedia({ colorScheme });
    await page.goto('/');
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
    await expect(page.locator('html')).toHaveCSS('background-color', 'rgb(253, 253, 252)');
    await expect(page.locator('.entries .entry-box').first()).toHaveCSS('background-color', 'rgb(255, 255, 255)');
    if (javaScriptEnabled === false) {
      await expect(themeButton(page)).toHaveCount(0);
    } else {
      await expect(themeButton(page)).toHaveAccessibleName('Switch to dark theme');
    }
  }
});

test.describe('theme controls', () => {
  test.skip(({ javaScriptEnabled }) => javaScriptEnabled === false, 'Theme selection needs JavaScript.');

  test('switches with the keyboard and remembers an override after reload', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/');
    await themeButton(page).focus();
    await page.keyboard.press('Enter');
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'dark');
    await expect(themeButton(page)).toHaveAccessibleName('Switch to light theme');
    await expect(themeButton(page)).toBeFocused();

    await page.reload();
    await expect(page.locator('html')).toHaveCSS('background-color', 'rgb(17, 17, 16)');
    await themeButton(page).focus();
    await page.keyboard.press('Space');
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.reload();
    await expect(page.locator('html')).toHaveCSS('background-color', 'rgb(253, 253, 252)');
    await expect(themeButton(page)).toHaveAccessibleName('Switch to dark theme');
  });

  test('applies a saved theme before the deferred application scripts run', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.addInitScript(() => localStorage.setItem('theme', 'dark'));
    await page.route('**/_astro/*.js', (route) => route.abort());
    await page.goto('/');
    await expect(page.locator('html')).toHaveCSS('background-color', 'rgb(17, 17, 16)');
    await expect(themeButton(page)).toHaveCount(0);
  });

  test('keeps the theme through client navigation, back, and repeated switching', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/');
    await themeButton(page).click();
    await page.evaluate(() => {
      Object.assign(window, { themeAfterSwaps: [] });
      document.addEventListener('astro:after-swap', () => {
        const state = window as unknown as { themeAfterSwaps: string[] };
        state.themeAfterSwaps.push(document.documentElement.dataset.theme ?? 'system');
      });
    });
    await followEntry(page);
    await expect(themeButton(page)).toHaveAccessibleName('Switch to light theme');
    await page.goBack();
    await expect(page.locator('#directory-heading')).toBeVisible();
    expect(await page.evaluate(() => (
      window as unknown as { themeAfterSwaps: string[] }
    ).themeAfterSwaps)).toEqual(['dark', 'dark']);
    await themeButton(page).click();
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
    await followEntry(page);
    await themeButton(page).click();
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'dark');
  });

  test('keeps a manual choice during navigation when storage is blocked', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.addInitScript(() => {
      Object.defineProperty(window, 'localStorage', {
        get() { throw new DOMException('Storage is disabled', 'SecurityError'); },
      });
    });
    await page.goto('/');
    await themeButton(page).click();
    await followEntry(page);
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'dark');
    await themeButton(page).click();
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
  });

  test('ignores invalid saved values and synchronizes choices between tabs', async ({ page, context }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.addInitScript(() => localStorage.setItem('theme', 'invalid'));
    await page.goto('/');
    await expect(themeButton(page)).toHaveAccessibleName('Switch to dark theme');
    const other = await context.newPage();
    await other.emulateMedia({ colorScheme: 'dark' });
    await other.goto('/definitions');
    await expect(themeButton(other)).toHaveAccessibleName('Switch to dark theme');
    await themeButton(page).click();
    await expect(other.locator('html')).toHaveCSS('color-scheme', 'dark');
    await themeButton(other).click();
    await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
    await themeButton(page).click();
    await expect(other.locator('html')).toHaveCSS('color-scheme', 'dark');
    await other.evaluate(() => localStorage.removeItem('theme'));
    await expect(page.locator('html')).toHaveCSS('background-color', 'rgb(253, 253, 252)');
    await other.close();
  });
});
