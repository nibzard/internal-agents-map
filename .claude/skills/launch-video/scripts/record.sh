#!/usr/bin/env bash
# ABOUTME: Records one raw walkthrough take of a live site with agent-browser (cursor on, 30 fps).
# ABOUTME: Template: keep the helpers and setup, replace the example beats with the site's own story.
set -euo pipefail

OUT_DIR="$(pwd)"
AB=agent-browser
SITE="${1:?usage: record.sh https://site.example}"

smooth_scroll() { # $1 = y position, $2 = hold ms
  $AB eval "window.scrollTo({top: $1, behavior: 'smooth'})" >/dev/null
  $AB wait "$2" >/dev/null
}

slow_type() { # types text one key at a time so viewers can follow it
  local text="$1" i
  for ((i = 0; i < ${#text}; i++)); do
    $AB keyboard type "${text:i:1}" >/dev/null
    $AB wait 70 >/dev/null
  done
}

cleanup() { $AB record stop >/dev/null 2>&1 || true; }
trap cleanup EXIT

$AB set viewport 1600 900 >/dev/null
$AB set media light >/dev/null
$AB open "$SITE/" >/dev/null
$AB wait 2500 >/dev/null

$AB record start "$OUT_DIR/raw.mp4" --cursor --fps 30
$AB mouse move 800 450 >/dev/null

# ---- Example beats (internal-agents.com). Replace with the site's own story. ----
# Give every beat a hold before and after it. The edit cuts the dead time later;
# a rushed take cannot be slowed down without judder.

# 1. Hero: headline and key numbers.
$AB wait 2500 >/dev/null

# 2. Browse: one scroll down, one back up.
smooth_scroll 700 1600
smooth_scroll 1500 1600
smooth_scroll 0 1500

# 3. Click one entry point. Use CSS selectors or `find`, not `text=`.
$AB hover "a[href='/problems/security-alerts']" >/dev/null
$AB wait 500 >/dev/null
$AB click "a[href='/problems/security-alerts']" >/dev/null
$AB wait 2200 >/dev/null
smooth_scroll 500 1600
smooth_scroll 0 900

# 4. Search: open the palette, type slowly, pick a result.
$AB click ".search-launcher" >/dev/null
$AB wait 700 >/dev/null
slow_type "code review"
$AB wait 1500 >/dev/null
$AB find text "Stripe · Minions" hover >/dev/null
$AB wait 500 >/dev/null
$AB find text "Stripe · Minions" click >/dev/null
$AB wait 2500 >/dev/null

# 5. Read one detail page.
smooth_scroll 520 2200
smooth_scroll 1100 2200
smooth_scroll 0 1400
# ---- End of example beats. ----

$AB record stop
