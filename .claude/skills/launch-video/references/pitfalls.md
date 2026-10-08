# Pitfalls

Each item is a trap we hit while making the reference video, and its fix.

## agent-browser

- **`text=` selectors fail** in `click` and `hover` ("Element not found"). Use a CSS
  selector (`a[href='/problems/x']`) or `find text "Label" click`.
- **Duplicate hidden elements.** A site can have a mobile and a desktop copy of one control
  (for example a theme toggle). `click` then hits the 0×0 hidden copy and reports "covered
  by". Find the visible one with `eval` on `getBoundingClientRect()`, then use
  `find last "<selector>" click`.
- **Controls that scroll away.** A sidebar control is not sticky on a long page. Scroll to
  the top before you click it.
- **Relative paths.** `agent-browser screenshot file.png` writes relative to the daemon,
  not to your shell. Always give absolute paths.
- **CSS specificity.** To hide a tool's panel during capture, a plain
  `display:none!important` can lose to the page's own `!important` rule. Use a more
  specific selector, for example `html body[data-screen] #controls#controls`.
- **`let` redeclaration in `eval`.** Each `eval` shares the page scope. Wrap code in
  `{ ... }` blocks so `const` names do not collide.

## Recording

- **The screencast drops frames** during heavy paints (page loads, backdrop blur). Do not
  record a generative background with `record`; step its clock and screenshot each frame.
- **Do not switch theme** in the take. A light-to-dark change reads as a flash.

## Editing

- **Judder from rounding.** Mapping output frames to `round(t × speed × fps)` skips and
  repeats source frames unevenly. Blend the two nearest source frames by the fractional
  part.
- **Cubic easing is too sharp** for short zooms. Use sine ease-in-out and 0.8 s or longer.
- **Too much zoom blur** makes text look doubled and smeared. Keep spread at about
  0.22 × velocity / fps with 7 taps.
- **Cut plus UI change.** If a dialog opens in the first frames of a shot, two jolts stack.
  Start the shot 0.2–0.3 s earlier.
- **Dark-to-light cuts** are the largest jump in a video. Cross-fade them.
- **Camera clamp at the ending.** Clamping the camera to the canvas pushes the address pill
  off-centre at high zoom. The ending shot needs `free=True`.
- **The ending URL blurs** if you zoom a bitmap of it. Draw the text again at each frame at
  `font size × scale`.
- **The ending fades too early** if the fade range starts at a low scale: the screen goes
  flat before the address pill has grown. Fade between scales of about 3.0 and 5.4 on the
  way to 6.

## Generative background (Steel Box generator)

- **Its HERO camera tracks the moving box.** Behind a centred window the box hides for most
  of the video, then overshoots. Override `heroViewBox` with a fixed, magnified view, and
  set `heroCycleAt = () => 1`.
- **Degenerate shapes.** Late in the clock the box can turn edge-on and draw a thick bar.
  Check stills across the clock range and use only a clean range, slowed down.
- **Line build-in.** The first second draws the lines on. That is a good opening; the first
  shot is zoomed on the site, so the build-in mostly shows in the margins.
- **Moiré in thumbnails.** Downscaled hairlines look like a checkerboard in contact sheets.
  Check at full resolution before you change the line settings.

## Review

- **Stills cannot show the feel of motion.** Measure jumps with `qa.py jumps`, look at
  mid-zoom frames at full resolution, and ask the user to watch on a phone.
