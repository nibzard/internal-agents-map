# ABOUTME: Cuts a raw site recording into a launch edit: a browser window over an animated desktop.
# ABOUTME: Zoom motion drives a liquid lens warp; the edit ends on the site address from the address bar.
import math
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---- Project settings: change these for each video. -------------------------------------
SRC = "raw.mp4"
OUT = sys.argv[1] if len(sys.argv) > 1 else "launch-edit.mp4"
FPS = 30
SW, SH = 1600, 900  # source size
OW, OH = 1920, 1080  # output size
PUNCH = 0.03  # extra scale at cuts
PUNCH_OUT_FRAMES, PUNCH_IN_FRAMES = 6, 10

# Browser window on the canvas. The canvas is the output size; site content keeps its native size.
WIN_X, WIN_Y, BAR_H, WIN_R = (OW - SW) // 2, 64, 52, 14
CONTENT_X, CONTENT_Y = WIN_X, WIN_Y + BAR_H
PILL_W, PILL_H, PILL_CY = 560, 32, WIN_Y + BAR_H // 2
FONT = "ABCAreal-Medium.ttf"  # the site's UI font file (copy the .ttf next to this script)
BG_FRAMES = "bg/frame-{:04d}.png"  # desktop background loop from bg-capture.sh
FONT_PX = 15
HOST = "internal-agents.com"  # the address the edit ends on
# Site palette (light theme neutral scale, BGR). Use the site's own colour tokens:
# 2 = window bar, 3 = address pill, 4 = desktop fallback, 5 = window outline, 6 = window dots,
# 9 = muted path text, 12 = ink.
SAND = {
    n: tuple(int(h[i : i + 2], 16) for i in (5, 3, 1))
    for n, h in {
        2: "#f9f9f8",
        3: "#f1f0ef",
        4: "#e9e8e6",
        5: "#e2e1de",
        6: "#dad9d6",
        9: "#8d8d86",
        12: "#21201c",
    }.items()
}

# Each shot: source range (s), playback speed, address bar path, and camera keyframes
# (output seconds, scale, cx, cy) in site content pixels. Negative cy is in the browser bar.
# Optional keys: slow=(src_a, src_b, speed) slows one fast UI moment; xfade=N cross-fades
# N frames into this shot instead of a punch cut; free=True lets the camera leave the canvas.
# path=None marks the ending shot: the address is drawn live and the window fades away.
PILL_Y = PILL_CY - CONTENT_Y  # address bar centre in content pixels
SHOTS = [
    dict(
        name="hero",
        src=(0.2, 2.4),
        speed=1.0,
        path="",
        cam=[(0.0, 1.8, 660, 175), (0.4, 1.8, 660, 175), (1.5, 1.0, 800, 450)],
    ),
    dict(
        name="catalog",
        src=(2.5, 5.2),
        speed=1.6,
        path="",
        cam=[(0.0, 1.0, 800, 450), (1.69, 1.05, 800, 450)],
    ),
    dict(
        name="problem-link",
        src=(8.4, 9.6),
        speed=1.0,
        path="",
        cam=[(0.0, 1.0, 800, 450), (0.1, 1.0, 800, 450), (0.9, 2.0, 1120, 235)],
    ),
    dict(
        name="problem-page",
        src=(9.75, 13.4),
        speed=1.4,
        path="/problems/security-alerts",
        cam=[(0.0, 1.6, 700, 170), (0.35, 1.6, 700, 170), (1.2, 1.0, 800, 450)],
    ),
    dict(
        name="search",
        src=(14.75, 18.7),
        speed=1.3,
        path="/problems/security-alerts",
        slow=(15.0, 15.2, 0.35),  # the search dialog opening animation
        cam=[
            (0.0, 1.0, 800, 450),
            (0.6, 1.0, 800, 450),
            (1.4, 1.75, 800, 330),
            (2.0, 1.75, 800, 330),
            (2.8, 1.5, 800, 470),
        ],
    ),
    dict(
        name="record",
        src=(18.95, 23.0),
        speed=1.3,
        path="/agents/stripe-minions",
        xfade=8,
        cam=[
            (0.0, 1.7, 640, 200),
            (0.35, 1.7, 640, 200),
            (1.25, 1.0, 800, 450),
            (1.5, 1.0, 800, 450),
            (2.5, 1.3, 800, 500),
        ],
    ),
    # The ending zooms into the address bar until only the address stays on screen.
    dict(
        name="outro",
        src=(0.0, 2.4),
        speed=0.6,
        path=None,
        free=True,
        cam=[(0.0, 1.0, 800, 424), (0.7, 1.0, 800, 424), (2.3, 6.0, 800, PILL_Y)],
    ),
]
FADE_IN_FRAMES = 4
END_FADE_SCALES = (
    3.0,
    5.4,
)  # the window fades into the full desktop background across this scale range
# ---- End of project settings. ------------------------------------------------------------


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return (1 - math.cos(math.pi * p)) / 2


def camera(cam, t):
    if t <= cam[0][0]:
        return cam[0][1:]
    for (t0, s0, x0, y0), (t1, s1, x1, y1) in zip(cam, cam[1:]):
        if t <= t1:
            e = ease((t - t0) / (t1 - t0))
            return (
                math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * e),
                x0 + (x1 - x0) * e,
                y0 + (y1 - y0) * e,
            )
    return cam[-1][1:]


def build_timeline():
    """Returns per-output-frame (source frame position, scale, cx, cy, shot, velocity)."""
    frames = []
    for si, shot in enumerate(SHOTS):
        a, b = shot["src"]
        slow_a, slow_b, slow_speed = shot.get("slow", (0, 0, 1))
        positions, pos = [], a
        while pos < b:
            positions.append(pos)
            pos += (slow_speed if slow_a <= pos < slow_b else shot["speed"]) / FPS
        n = len(positions)
        for i in range(n):
            t = i / FPS
            s, cx, cy = camera(shot["cam"], t)
            if si > 0 and i < PUNCH_IN_FRAMES and not shot.get("xfade"):
                s *= 1 + PUNCH * (1 - ease(i / PUNCH_IN_FRAMES))
            if si < len(SHOTS) - 1 and i >= n - PUNCH_OUT_FRAMES and not SHOTS[si + 1].get("xfade"):
                s *= 1 + PUNCH * ease((i - (n - PUNCH_OUT_FRAMES) + 1) / PUNCH_OUT_FRAMES)
            src_idx = positions[i] * FPS  # fractional; blended in main()
            frames.append([src_idx, s, cx + CONTENT_X, cy + CONTENT_Y, si])
    # Zoom velocity in log-scale per second, measured inside each shot.
    for i, f in enumerate(frames):
        lo = i - 1 if i > 0 and frames[i - 1][4] == f[4] else i
        hi = i + 1 if i + 1 < len(frames) and frames[i + 1][4] == f[4] else i
        v = (math.log(frames[hi][1]) - math.log(frames[lo][1])) * FPS / max(hi - lo, 1)
        f.append(v)
    return frames


def load_sources(indices):
    cap = cv2.VideoCapture(SRC)
    cache, i = {}, 0
    need = set(indices)
    last = max(need)
    while i <= last:
        ok, img = cap.read()
        if not ok:
            break
        if i in need:
            cache[i] = cv2.imencode(".png", img)[1]
        i += 1
    return cache


U, V = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))
NX, NY = (U - OW / 2) / (OW / 2), (V - OH / 2) / (OW / 2)
R2 = (NX**2 + NY**2) / (1 + (OH / OW) ** 2)  # 1.0 at the corners
R = np.sqrt(R2)
PX = 1.0  # canvas pixels per output pixel at scale 1


def font(px):
    return ImageFont.truetype(FONT, max(1, int(round(px))))


def draw_url(draw, cx, cy, path, px):
    """Draws HOST plus a muted path, centred on (cx, cy)."""
    f = font(px)
    w_host = draw.textlength(HOST, font=f)
    w = w_host + (draw.textlength(path, font=f) if path else 0)
    x = cx - w / 2
    draw.text((x, cy), HOST, font=f, fill=SAND[12][::-1], anchor="lm")
    if path:
        draw.text((x + w_host, cy), path, font=f, fill=SAND[9][::-1], anchor="lm")


def build_canvas(path, ss=2):
    """Returns window, window alpha, shadow, and content mask layers; drawn at ss times size."""
    W, H = OW * ss, OH * ss

    def rgb(n):
        return SAND[n][::-1]

    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        (WIN_X * ss, (WIN_Y + 18) * ss, (WIN_X + SW) * ss, (CONTENT_Y + SH + 18) * ss),
        WIN_R * ss,
        fill=46,
    )
    shadow = cv2.GaussianBlur(np.array(shadow), (0, 0), 28 * ss)
    img = Image.new("RGB", (W, H), 0)
    d = ImageDraw.Draw(img)
    box = (WIN_X * ss, WIN_Y * ss, (WIN_X + SW) * ss - 1, (CONTENT_Y + SH) * ss - 1)
    d.rounded_rectangle(box, WIN_R * ss, fill=rgb(2), outline=rgb(5), width=ss)
    win_a = Image.new("L", (W, H), 0)
    ImageDraw.Draw(win_a).rounded_rectangle(box, WIN_R * ss, fill=255)
    d.line(
        (WIN_X * ss, CONTENT_Y * ss - ss, (WIN_X + SW) * ss, CONTENT_Y * ss - ss),
        fill=rgb(4),
        width=ss,
    )
    for k in range(3):
        x, y, r = (WIN_X + 24 + 20 * k) * ss, PILL_CY * ss, 6 * ss
        d.ellipse((x - r, y - r, x + r, y + r), fill=rgb(6))
    d.rounded_rectangle(
        (
            (OW - PILL_W) // 2 * ss,
            (PILL_CY - PILL_H // 2) * ss,
            (OW + PILL_W) // 2 * ss,
            (PILL_CY + PILL_H // 2) * ss,
        ),
        PILL_H // 2 * ss,
        fill=rgb(3),
    )
    if path is not None:
        draw_url(d, OW / 2 * ss, PILL_CY * ss, path, FONT_PX * ss)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (box[0] + ss, CONTENT_Y * ss - WIN_R * ss, box[2] - ss, box[3] - ss), WIN_R * ss, fill=255
    )
    ImageDraw.Draw(mask).rectangle((0, 0, W, CONTENT_Y * ss - 1), fill=0)

    def small(a):
        return cv2.resize(a, (OW, OH), interpolation=cv2.INTER_AREA)

    def alpha(a):
        return small(np.asarray(a, np.float32) / 255)[..., None]

    return (
        small(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)).astype(np.float32),
        alpha(win_a),
        alpha(shadow),
        alpha(mask),
    )


def compose(layers, desktop, img):
    win, win_a, shadow, mask = layers
    out = desktop.astype(np.float32) * (1 - shadow)
    out = win * win_a + out * (1 - win_a)
    region = out[CONTENT_Y : CONTENT_Y + SH, CONTENT_X : CONTENT_X + SW]
    m = mask[CONTENT_Y : CONTENT_Y + SH, CONTENT_X : CONTENT_X + SW]
    region[:] = img * m + region * (1 - m)
    return out.astype(np.uint8)


def desktop_frame(i):
    for k in (i, i - 1, 0):  # hold the last frame if the loop is shorter than the edit
        img = cv2.imread(BG_FRAMES.format(max(k, 0)))
        if img is not None:
            return img
    raise FileNotFoundError("run bg-capture.sh first")


def overlay_url(out, s, cx, cy):
    """Draws the address at the size and place the camera gives the address bar text."""
    img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    draw_url(
        ImageDraw.Draw(img),
        (OW / 2 - cx) * s + OW / 2,
        (PILL_CY - cy) * s + OH / 2,
        "",
        FONT_PX * s,
    )
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def sample(img, s, cx, cy, warp, chroma):
    k = PX / s * warp
    mx = (cx + (U - OW / 2) * k * chroma).astype(np.float32)
    my = (cy + (V - OH / 2) * k * chroma).astype(np.float32)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def render(img, s, cx, cy, v, t, free=False):
    if not free:
        cx = min(max(cx, OW / 2 / s), OW - OW / 2 / s)
        cy = min(max(cy, OH / 2 / s), OH - OH / 2 / s)
    a = min(0.06, 0.05 * abs(v))
    if a < 0.003:
        return sample(img, s, cx, cy, 1.0, 1.0)
    sign = 1 if v > 0 else -1
    warp = 1 - sign * a * (1 - R2) + a * 0.12 * np.sin(8 * R - 9 * t)
    taps = 7 if abs(v) > 0.4 else 3
    spread = v / FPS * 0.22
    acc = np.zeros((OH, OW, 3), np.float32)
    for j in range(taps):
        sj = s * math.exp(spread * (j / (taps - 1) - 0.5))
        frame = np.empty((OH, OW, 3), np.uint8)
        for ch, c in ((0, 1 - a * 0.04), (1, 1.0), (2, 1 + a * 0.04)):  # BGR
            frame[..., ch] = sample(img[..., ch], sj, cx, cy, warp, c)
        acc += frame
    return (acc / taps).astype(np.uint8)


def main():
    timeline = build_timeline()
    cache = load_sources([k for f in timeline for k in (int(f[0]), int(f[0]) + 1)])
    canvases = {sh["path"]: build_canvas(sh["path"]) for sh in SHOTS}
    enc = subprocess.Popen(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{OW}x{OH}",
            "-r",
            str(FPS),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            OUT,
        ],
        stdin=subprocess.PIPE,
    )
    n = len(timeline)
    shot_len = [sum(1 for f in timeline if f[4] == k) for k in range(len(SHOTS))]
    held, j = [], 0  # last frames of a shot that cross-fades into the next one
    for i, (src_idx, s, cx, cy, si, v) in enumerate(timeline):
        shot = SHOTS[si]
        j = j + 1 if i > 0 and timeline[i - 1][4] == si else 0
        k, w = int(src_idx), src_idx - int(src_idx)
        site = cv2.imdecode(cache[k], cv2.IMREAD_COLOR)
        if w > 0.01 and k + 1 in cache:
            site = cv2.addWeighted(site, 1 - w, cv2.imdecode(cache[k + 1], cv2.IMREAD_COLOR), w, 0)
        desktop = desktop_frame(i)
        img = compose(canvases[shot["path"]], desktop, site)
        out = render(img, s, cx, cy, v, i / FPS, shot.get("free", False))
        lo, hi = END_FADE_SCALES
        fade = min(
            (i + 1) / FADE_IN_FRAMES,
            1 - ease((s - lo) / (hi - lo)) if shot["path"] is None else 1.0,
        )
        if fade < 1.0:
            out = cv2.addWeighted(out, fade, desktop, 1 - fade, 0)
        if shot["path"] is None:
            out = overlay_url(out, s, cx, cy)
        nxt_xfade = SHOTS[si + 1].get("xfade", 0) if si + 1 < len(SHOTS) else 0
        if j >= shot_len[si] - nxt_xfade:
            held.append(out)
            continue
        if j < len(held):
            w = (j + 1) / (len(held) + 1)
            out = cv2.addWeighted(held[j], 1 - w, out, w, 0)
            if j == len(held) - 1:
                held = []
        enc.stdin.write(out.tobytes())
    enc.stdin.close()
    enc.wait()
    total = n - sum(sh.get("xfade", 0) for sh in SHOTS)
    print(f"{OUT}: {total} frames, {total / FPS:.2f}s")


if __name__ == "__main__":
    main()
