// ABOUTME: Animates foreground exchanges, background handoffs, and mode changes on the Definitions guide.
// ABOUTME: The figures reuse the site's dash, with transparent tips and a soft arrival and departure.

import { animate } from 'motion';

import { DASH, fadingDash } from './dash';

const FOREGROUND_SECONDS = 7;
const BACKGROUND_SECONDS = 8;
const SWITCH_SECONDS = 14;
const TO_AGENT = [0.06, 0.21] as const;
const WORKING = [0.21, 0.7] as const;
const TO_YOU = [0.7, 0.85] as const;
const BACKGROUND_RUN = [0.06, 0.84] as const;
const SWITCH_RUN = [0.04, 0.92] as const;
/** The two vertical guides bound the background part of the mode-change figure. */
const SWITCH_BACKGROUND = [163, 357] as const;
const ORBITS = 2;

/** A phase's progress, or null while another part of the exchange is happening. */
function within(progress: number, [from, to]: readonly [number, number]): number | null {
  if (progress < from || progress > to) return null;
  return (progress - from) / (to - from);
}

/** The same gentle arrival and departure as the existing diagram signals. */
function pulse(along: number, rise = 0.18, fall = 0.18): number {
  const value = Math.min(1, along / rise, (1 - along) / fall);
  return 1 - (1 - value) ** 3;
}

/** Keep the spatial gradient on the dash as it moves along each leg. */
function carrier(signal: SVGPathElement) {
  const dash = fadingDash(signal);
  return (link: SVGPathElement, along: number, returning = false): void => {
    dash.place(returning ? 1 - along : along, link);
    signal.setAttribute('opacity', String(pulse(along)));
  };
}

let running: { stop: () => void }[] = [];
let preference: MediaQueryList | undefined;

/** Stop the old page's timelines before wiring the diagrams on the current page. */
export function startParticipation(): void {
  for (const timeline of running) timeline.stop();
  running = [];
  preference?.removeEventListener('change', startParticipation);
  preference = undefined;

  const exchange = document.querySelector<SVGSVGElement>('.exchange-scene');
  const handoff = document.querySelector<SVGSVGElement>('.handoff-scene');
  const switching = document.querySelector<HTMLElement>('.mode-switch-scene');
  if (!exchange && !handoff && !switching) return;

  preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  preference.addEventListener('change', startParticipation);
  if (exchange) startExchange(exchange, preference.matches);
  if (handoff) startHandoff(handoff, preference.matches);
  if (switching) startSwitch(switching, preference.matches);
}

/** A message travels out, circles the working agent, and returns to the conversation. */
function startExchange(scene: SVGSVGElement, reduced: boolean): void {
  const link = scene.querySelector<SVGPathElement>('.exchange-link');
  const orbit = scene.querySelector<SVGPathElement>('.exchange-orbit');
  const signal = scene.querySelector<SVGPathElement>('.exchange-signal');
  if (!link || !orbit || !signal) return;

  signal.setAttribute('opacity', '0');
  if (reduced) return;

  const carry = carrier(signal);
  running.push(animate(0, 1, {
    duration: FOREGROUND_SECONDS,
    ease: 'linear',
    repeat: Infinity,
    onUpdate: (progress: number) => {
      const outbound = within(progress, TO_AGENT);
      const working = within(progress, WORKING);
      const inbound = within(progress, TO_YOU);
      if (outbound !== null) {
        carry(link, outbound);
      } else if (working !== null) {
        carry(orbit, (working * ORBITS) % 1);
      } else if (inbound !== null) {
        carry(link, inbound, true);
      } else {
        signal.setAttribute('opacity', '0');
      }
    },
  }));
}

/** A single path leaves your row, runs on the agent's row, and brings a result back. */
function startHandoff(scene: SVGSVGElement, reduced: boolean): void {
  const route = scene.querySelector<SVGPathElement>('.handoff-route');
  const signal = scene.querySelector<SVGPathElement>('.handoff-signal');
  const you = scene.querySelector<SVGCircleElement>('.handoff-you-active');
  if (!route || !signal || !you) return;

  signal.setAttribute('opacity', '0');
  you.setAttribute('opacity', '1');
  if (reduced) return;

  const carry = carrier(signal);
  const span = route.getTotalLength();
  const yourRail = Number(you.getAttribute('cy'));
  running.push(animate(0, 1, {
    duration: BACKGROUND_SECONDS,
    ease: 'linear',
    repeat: Infinity,
    onUpdate: (progress: number) => {
      const work = within(progress, BACKGROUND_RUN);
      if (work !== null) carry(route, work);
      else signal.setAttribute('opacity', '0');

      // Light your node when the head of the dash rejoins your rail, before
      // it finishes crossing the short stretch at the end of that rail.
      const returned = work !== null && work > 0.5 &&
        Math.abs(route.getPointAtLength(Math.min(span, work * (span + DASH))).y - yourRail) < 0.5;
      const withYou = progress < BACKGROUND_RUN[0] || progress >= BACKGROUND_RUN[1] || returned;
      you.setAttribute('opacity', withYou ? '1' : '0');
    },
  }));
}

/** The same agent keeps working as human participation leaves and returns. */
function startSwitch(scene: HTMLElement, reduced: boolean): void {
  const route = scene.querySelector<SVGPathElement>('.mode-switch-route');
  const signal = scene.querySelector<SVGPathElement>('.mode-switch-signal');
  const you = scene.querySelector<HTMLElement>('.mode-switch-you-active');
  if (!route || !signal || !you) return;

  signal.setAttribute('opacity', '0');
  you.style.opacity = '1';
  if (reduced) return;

  const carry = carrier(signal);
  const span = route.getTotalLength();
  running.push(animate(0, 1, {
    duration: SWITCH_SECONDS,
    ease: 'linear',
    repeat: Infinity,
    onUpdate: (progress: number) => {
      const work = within(progress, SWITCH_RUN);
      if (work === null) {
        signal.setAttribute('opacity', '0');
        you.style.opacity = '1';
        return;
      }

      carry(route, work);
      const head = route.getPointAtLength(Math.min(span, work * (span + DASH)));
      const inBackground = head.x >= SWITCH_BACKGROUND[0] && head.x < SWITCH_BACKGROUND[1];
      you.style.opacity = inBackground ? '0' : '1';
    },
  }));
}
