#!/usr/bin/env bash
# ABOUTME: Captures the Steel Box HERO animation frame by frame as the desktop background loop.
# ABOUTME: Needs steel-box-generator served on localhost:4317; writes bg/frame-NNNN.png at 30 fps.
# Usage: bg-capture.sh [frames] [time-scale] [magnify] [bg-hex] [ink-hex] [out-dir]
set -euo pipefail
DIR="$(cd "${6:-.}" && pwd)/bg"
FRAMES="${1:-570}"
TIME_SCALE="${2:-0.55}"  # generator seconds per video second
MAGNIFY="${3:-0.62}"     # view height as a fraction of the drawing; < 1 makes the box overflow the frame
BG_HEX="${4:-#E9E8E6}"   # desktop colour: one step darker than the site page colour
INK_HEX="${5:-#BCBBB5}"  # line colour: low contrast against BG_HEX
AB=agent-browser
mkdir -p "$DIR"
$AB set viewport 1920 1080 >/dev/null
$AB open http://localhost:4317/ >/dev/null
$AB wait 1500 >/dev/null
$AB find role tab click --name "HERO ⇧2" >/dev/null
$AB wait 1000 >/dev/null
$AB eval '{
  const st = document.createElement("style");
  st.textContent = "html body[data-screen] #controls#controls, html body[data-screen] #app-tabs#app-tabs {display:none!important}";
  document.head.appendChild(st);
  noLoop();
  applyPaletteColor("'"$BG_HEX"'", 0); applyPaletteColor("'"$INK_HEX"'", 1); applyPaletteColor("'"$BG_HEX"'", 2);
  noLoop();
  // Fixed camera on the drawing centre, magnified so the ruled bands fill the frame margins.
  window.heroCycleAt = () => 1;
  window.heroViewBox = () => {
    const h = canvasHeight() * '"$MAGNIFY"', w = h * 1920 / 1080;
    return { x: canvasWidth() / 2 - w / 2, y: canvasHeight() / 2 - h / 2, w, h };
  };
  beginHero();
  window.__step = () => { window.deltaTime = 1000 / 30 * '"$TIME_SCALE"'; draw(); };
}' >/dev/null
for i in $(seq 0 $((FRAMES - 1))); do
  $AB eval '__step()' >/dev/null
  $AB screenshot "$DIR/$(printf 'frame-%04d.png' "$i")" >/dev/null
done
echo "captured $FRAMES frames to $DIR"
