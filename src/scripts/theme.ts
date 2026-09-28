// ABOUTME: Remembers an explicit light or dark theme and otherwise follows the system.
// ABOUTME: Carries the choice through Astro swaps, including when storage is blocked.
import type { TransitionBeforeSwapEvent } from 'astro:transitions/client';

type Theme = 'light' | 'dark';

function parseTheme(value: string | null | undefined): Theme | null {
  return value === 'light' || value === 'dark' ? value : null;
}

const systemTheme = matchMedia('(prefers-color-scheme: dark)');
let preference = parseTheme(document.documentElement.dataset.theme);

function applyTheme(target: Document): void {
  if (preference) target.documentElement.dataset.theme = preference;
  else delete target.documentElement.dataset.theme;
}

function updateControls(): void {
  const current = preference ?? (systemTheme.matches ? 'dark' : 'light');
  const next = current === 'dark' ? 'light' : 'dark';
  document.querySelectorAll<HTMLButtonElement>('[data-theme-toggle]').forEach((button) => {
    button.setAttribute('aria-label', `Switch to ${next} theme`);
    button.title = `Switch to ${next} theme`;
    button.querySelectorAll<HTMLElement>('[data-theme-icon]').forEach((icon) => {
      icon.hidden = icon.dataset.themeIcon !== next;
    });
    button.hidden = false;
  });
}

// Match the incoming document before the router takes its next snapshot.
document.addEventListener('astro:before-swap', (event) => {
  applyTheme((event as TransitionBeforeSwapEvent).newDocument);
});
systemTheme.addEventListener('change', updateControls);
window.addEventListener('storage', (event) => {
  if (event.key !== 'theme' && event.key !== null) return;
  preference = parseTheme(event.newValue);
  applyTheme(document);
  updateControls();
});

export function startTheme(): void {
  applyTheme(document);
  updateControls();
  document.querySelectorAll<HTMLButtonElement>('[data-theme-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const current = preference ?? (systemTheme.matches ? 'dark' : 'light');
      preference = current === 'dark' ? 'light' : 'dark';
      applyTheme(document);
      updateControls();
      try {
        localStorage.setItem('theme', preference);
      } catch {
        // The in-memory choice still survives client navigation.
      }
    });
  });
}
