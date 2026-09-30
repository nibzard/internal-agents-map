// ABOUTME: Copies the record update prompt and announces the result.
// ABOUTME: Clipboard failures expose and select the prompt for manual copying.
let started = false;

export function startCopyUpdate(): void {
  document.querySelectorAll<HTMLButtonElement>('[data-copy-update]').forEach((button) => {
    button.hidden = false;
  });
  if (started) return;
  started = true;
  document.addEventListener('click', async (event) => {
    const button = (event.target as Element | null)?.closest?.<HTMLButtonElement>('[data-copy-update]');
    const section = button?.closest('[data-record-contribution]');
    const prompt = section?.querySelector<HTMLTextAreaElement>('textarea');
    const preview = section?.querySelector('details');
    const status = section?.querySelector('[data-update-status]');
    if (!button || !prompt || !preview || !status) return;
    status.textContent = '';
    try {
      await navigator.clipboard.writeText(prompt.value);
      status.textContent = 'Prompt copied. Paste it into your coding agent.';
    } catch {
      preview.open = true;
      prompt.focus();
      prompt.select();
      status.textContent = 'Copy the selected prompt, then paste it into your coding agent.';
    }
  });
}
