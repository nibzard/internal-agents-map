// ABOUTME: Checks the link that opens a ChatGPT conversation about one catalog page.
// ABOUTME: The prompt must point at the published Markdown record, not at the HTML page.
import { describe, expect, it } from 'vitest';
import { askChatGptUrl, askPrompt } from '../../src/lib/ask';

describe('ask ChatGPT link', () => {
  it('points the prompt at the Markdown record of the page', () => {
    const prompt = askPrompt('/agents/stripe-minions', 'Minions at Stripe');
    expect(prompt).toContain('https://internal-agents.com/agents/stripe-minions.md');
    expect(prompt).toContain('Minions at Stripe');
  });

  it('asks the assistant to keep the record, the sources, and its own inference apart', () => {
    const prompt = askPrompt('/agents/stripe-minions', 'Minions at Stripe');
    expect(prompt).toContain('which from the original sources, and which are your own inference');
  });

  it('carries the prompt as the q parameter of a ChatGPT URL', () => {
    const url = new URL(askChatGptUrl('/agents/stripe-minions', 'Minions at Stripe'));
    expect(url.origin + url.pathname).toBe('https://chatgpt.com/');
    expect(url.searchParams.get('q')).toBe(askPrompt('/agents/stripe-minions', 'Minions at Stripe'));
  });
});
