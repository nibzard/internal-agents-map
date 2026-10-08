---
name: launch-video
description: Make a short, elegant product launch video of a live website for x.com (or LinkedIn, Product Hunt, a README) by recording real interactions with agent-browser and editing them in code. The edit puts the site in a browser window over an animated generative desktop, with eased "liquid" zooms, soft cuts, calm pacing, and an ending that zooms into the address bar to show the URL. Use this skill whenever the user wants a launch video, demo video, promo clip, teaser, screen recording, walkthrough video, or "something to share on X/Twitter" for a site or web app, even when they do not say "skill" or name these techniques. Also use it to edit, re-pace, or restyle such a video.
---

# Launch video

This skill makes a 14–20 second launch video of a live site. The video shows real use of the
real site: no mockups, no fake data. The style target is **elegant**: calm motion, sharp text
at every hold, one idea per shot, and the URL at the end.

The pipeline has four steps. Each step has a script in `scripts/`:

| Step | Script | Output |
|---|---|---|
| 1. Record one raw take | `record.sh` (template) | `raw.mp4`, 1600×900, 30 fps, with cursor |
| 2. Capture the desktop background | `bg-capture.sh` | `bg/frame-NNNN.png`, 1920×1080 |
| 3. Edit in code | `edit.py` (template) | final MP4, 1920×1080 H.264 |
| 4. Check | `qa.py` | contact sheets, jump numbers |

Work in a folder outside the project repo (for example `~/Movies/<name>-launch/`). Copy the
scripts there. Do not add video files to the repo.

Read `references/pitfalls.md` before step 1. It lists the traps that cost time.

## Step 1: record one raw take

Use the production URL. Explore the site first with `agent-browser snapshot -i` and
screenshots. Pick 4–6 beats that tell the product story, for example: hero with key numbers,
browse, one entry point, search, one detail page.

Rules for the take:
- Record one continuous take with `--cursor`. Do all cutting in the edit.
- Hold 1.5–2.5 s before and after each beat. The edit removes dead time; a rushed take
  cannot be slowed down without judder.
- Type with `slow_type` (70 ms per key) so viewers can read the query.
- Use the light theme. Do not switch theme during the video; it reads as a flash.
- Keep `record.sh` as a script so a re-take is one command.

## Step 2: find the beats

Before you edit, map the take to exact times:

```bash
uv run --with opencv-python-headless --with numpy python qa.py sheet raw.mp4 --every 0.5 --out timeline.png
uv run --with opencv-python-headless --with numpy python qa.py motion raw.mp4
```

Then make fine sheets (every 0.1 s) around each click, hover, and page change. Write down:
cursor arrival, click, page change, typing start and end. Every camera keyframe depends on
these times.

## Step 3: the style

These values worked. Start from them; change them only for a reason.

### Frame and composition
- **Output:** 1920×1080, 30 fps, H.264 `yuv420p`, CRF 17, `+faststart`. No audio.
- **Browser window:** the site at native 1600×900 inside a window at (160, 64) with a
  52 px bar, 14 px corner radius, 1 px outline, and a soft shadow (blur 28, offset 18,
  about 18% black). Three neutral-grey dots, not macOS colours.
- **Address pill:** centred, 560×32, in the site's UI font. Show the host in ink and the
  path in a muted tone. The path changes per shot to the real URL path, so the address bar
  tells the story.
- **Palette:** take every colour from the site's design tokens (neutral scale). The desktop
  is one step darker than the page colour, so the window lifts off it.

### Desktop background
- Use a slow generative line animation, for example the Steel Box generator
  (`github.com/steel-dev/steel-box-generator`, HERO mode). Lines in a low-contrast tone of
  the same palette: hairlines, not shapes.
- The window covers the centre, so **magnify the art past the frame** (view height about
  0.62 of the drawing) with a **fixed camera**. Then the ruled bands always cross the
  visible margins. Do not use a camera that tracks a moving shape.
- **Step the clock deterministically** (exactly 1/30 s × time scale per frame) and
  screenshot each frame. Do not screen-record the background.
- Play it slowly (time scale about 0.55). Use only a clean clock range: no degenerate or
  edge-on shapes.
- At the end, the window dissolves onto the live background, and the background frames the
  URL.

See `bg-capture.sh` for the camera override and the stepping loop.

### Camera and the "liquid" zoom
- The camera zooms the **whole canvas**: window, bar, and desktop. In a close-up the bar
  leaves the frame; on zoom out it comes back.
- **Easing:** sine ease-in-out, interpolated in log-scale. Do not use cubic; its peak
  speed is about twice as high and reads as jumpy.
- **Durations:** 0.8–1.1 s for a zoom, 1.6 s for the end zoom. Zooms of 0.35–0.45 s were
  too jumpy.
- **Scales:** 1.6–1.8 to open on a headline, 1.75–2.0 on a control (search box, link list),
  1.3 for a gentle push. Keep the zoom inside the window: no slivers of bar text in a corner.
- **Liquid warp:** strength = 0.05 × |zoom velocity| (log-scale per second), capped at
  0.06. It adds a radial bulge, a slow ripple (`sin(8r − 9t)`, 12% of the strength), a
  4% colour fringe, and a zoom blur of 7 taps with spread 0.22 × velocity / fps. When the
  camera stops, all effects are zero, so text is sharp at every hold. If text looks doubled
  in the middle of a zoom, the blur spread is too large.

### Cuts and pacing
- Total length 14–20 s, 6–7 shots, 1.2–3.0 s each. The ending gets 3–4 s.
- **Speed:** 1.0–1.6×. Scrolls at 1.3–1.6×; 2.2× turns a scroll into a flick.
- **Blend source frames** for fractional speeds. Rounding to the nearest source frame
  skips and repeats frames unevenly; viewers feel that as judder.
- **Punch at cuts:** at most 3% scale, eased over 6 frames out and 10 frames in. 7% felt
  jumpy.
- **Hold after a cut:** 0.1–0.4 s before the camera moves. Do not start a shot with a zoom
  on its first frame.
- **Luminance jumps** (dark dialog to light page): cross-fade 8 frames, no punch.
- **Fast UI animations** (a dialog that opens in 5 frames): slow that source window to
  about 0.35× so frame blending turns it into a soft half-second change.
- Do not put a cut and a UI change in the same frames. Start the shot earlier.

### Ending
Hold the full window on the home page for about 0.7 s. Then zoom 1.6 s into the address
pill to scale 6. The window fades into the desktop between scales 3.0 and 5.4. Draw the URL
again at each frame, at the size and position the camera gives the pill text (font size
15 × scale), so the URL stays sharp. Hold the URL about 1.5 s. Do not fade the URL out.

## Step 4: check, then show the user

Do these checks before you report:

```bash
uv run --with opencv-python-headless --with numpy python qa.py jumps final.mp4
uv run --with opencv-python-headless --with numpy python qa.py sheet final.mp4 --every 0.4 --out final-sheet.png
uv run --with opencv-python-headless --with numpy python qa.py frames final.mp4 1.0 8.5 17.9 --prefix check
```

- **Jumps:** the largest frame-to-frame change must sit near the others. In the reference
  video: median about 2.5, max about 20. A single frame at 60–90 is a hard jump; find it
  and fix it with a cross-fade, a slow window, or a later cut.
- **Mid-zoom frames:** look at them at full resolution. The centre must stay readable.
- **Holds:** every text-heavy hold must be sharp.

Static frames cannot show how the motion feels. Tell the user this, and ask them to watch
the video on a phone. Common feedback and the lever to use:

| Feedback | Lever in `edit.py` |
|---|---|
| "Too jumpy" | Longer zoom durations, sine easing, smaller punch, lower speeds, cross-fades |
| "Too slow" | Shot speeds 1.3 → 1.5; trim holds; do not shorten zooms below 0.8 s |
| "More liquid" | Warp coefficient 0.05 → 0.07, cap 0.06 → 0.08 |
| "Too busy" | Blur spread 0.22 → 0.15, ripple 0.12 → 0.08 |
| "Background too faint" | One step darker line colour in `bg-capture.sh` |

## Running the scripts

```bash
./record.sh https://example.com                         # writes raw.mp4 in the current folder
npx serve -l 4317 /path/to/steel-box-generator &        # in another folder
./bg-capture.sh 560 0.55 0.62 '#E9E8E6' '#BCBBB5' .     # frames, time scale, magnify, bg, ink, out
uv run --with opencv-python-headless --with numpy --with pillow python edit.py final.mp4
```

The background needs at least as many frames as the edit (fps × length). `edit.py` holds the
last background frame if the loop is shorter. Copy the site's UI font (`.ttf`) next to
`edit.py` and set `FONT`, `HOST`, the palette, and `SHOTS` at the top of the file. In this
repository, the UI font is `src/og/fonts/ABCAreal-Medium.ttf` and the palette tokens are in
`src/styles/tokens.css`.
