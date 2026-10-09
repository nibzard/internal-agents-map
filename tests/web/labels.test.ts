// ABOUTME: Checks the short labels and date phrases that the entry pages show.
// ABOUTME: An observation date gets the preposition that agrees with its precision.

import { describe, expect, it } from 'vitest';
import { observedPhrase } from '../../src/lib/labels';

describe('observedPhrase', () => {
  it('puts "on" before a full date', () => {
    expect(observedPhrase('2026-02-20')).toBe('on 20 February 2026');
  });

  it('puts "in" before a month or a year', () => {
    expect(observedPhrase('2026-02')).toBe('in February 2026');
    expect(observedPhrase('2026')).toBe('in 2026');
  });

  it('keeps a value that is not a date without a preposition', () => {
    expect(observedPhrase('early 2026')).toBe('early 2026');
  });
});
