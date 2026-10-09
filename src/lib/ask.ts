// ABOUTME: Builds the links that send one catalog page to an outside chat assistant.
// ABOUTME: The assistant reads the published Markdown record; the prompt names the HTML page as a fallback.
import { canonicalUrl, markdownPath } from './routes';

/** The address that opens a ChatGPT conversation with a prompt already in it. */
const CHATGPT_URL = 'https://chatgpt.com/';

/**
 * The prompt that points an assistant at the Markdown record of one page. Some assistant
 * browsers cannot open a URL that they did not find through search, so the prompt also
 * names the HTML page.
 */
export function askPrompt(path: string, title: string): string {
  return (
    `Read ${canonicalUrl(markdownPath(path))} — the Internal Agents Map record of ${title}. ` +
    `If you cannot open it, read ${canonicalUrl(path)} instead. ` +
    'Use only what the record and its cited sources say, and cite them. ' +
    'Say which points come from the catalog record, which from the original sources, and which are your own inference. ' +
    'Then help me understand this system and what I can learn from it.'
  );
}

/** The ChatGPT link that starts a conversation about one page. */
export function askChatGptUrl(path: string, title: string): string {
  const url = new URL(CHATGPT_URL);
  url.searchParams.set('q', askPrompt(path, title));
  return url.toString();
}
