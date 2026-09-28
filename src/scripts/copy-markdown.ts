// ABOUTME: Copies the Markdown record behind a copy link to the clipboard instead of opening it.
// ABOUTME: If the clipboard is not available, the link opens the Markdown as it does without JavaScript.

/** How long the link says "Copied" before it shows its own label again. */
const CONFIRM_MS = 2000;

let started = false;

/** Copy the record of each copy link that a reader clicks. */
export function startCopyMarkdown(): void {
  if (started) return;
  started = true;
  // The router swaps the document, so one listener on the document serves every page.
  document.addEventListener('click', (event) => {
    const link = (event.target as Element | null)?.closest?.<HTMLAnchorElement>('a[data-copy-markdown]');
    if (!link || !navigator.clipboard || !window.ClipboardItem) return;
    event.preventDefault();
    // Safari keeps the click's permission only when the write starts in the handler.
    const text = fetch(link.href).then((response) => {
      if (!response.ok) throw new Error(`${response.status} ${link.href}`);
      return response.blob();
    });
    navigator.clipboard
      .write([new ClipboardItem({ 'text/plain': text.then((blob) => new Blob([blob], { type: 'text/plain' })) })])
      .then(() => showState(link, 'Copied'))
      .catch(() => { location.href = link.href; });
  });
}

/** Show a short state on the link, then its own label again. */
function showState(link: HTMLAnchorElement, state: string): void {
  const label = link.querySelector('[data-copy-label]');
  if (!label) return;
  const text = link.dataset.copyText ?? label.textContent ?? '';
  link.dataset.copyText = text;
  label.textContent = state;
  window.setTimeout(() => { label.textContent = text; }, CONFIRM_MS);
}
