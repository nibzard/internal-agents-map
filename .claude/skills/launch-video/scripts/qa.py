# ABOUTME: Inspection tools for launch video takes and edits: contact sheets, motion profile, jump check.
# ABOUTME: Run with: uv run --with opencv-python-headless --with numpy python qa.py <command> <video> ...
import argparse

import cv2
import numpy as np


def read_frames(path, scale=None):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    while True:
        ok, f = cap.read()
        if not ok:
            break
        yield (cv2.resize(f, scale) if scale else f), fps


def grid(tiles, cols):
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[r : r + cols]) for r in range(0, len(tiles), cols)])


def sheet(a):
    """Timestamped contact sheet: use it to find beats (hover, click, typing) in a raw take."""
    tiles, step = [], None
    for i, (f, fps) in enumerate(read_frames(a.video)):
        step = step or max(1, round(fps * a.every))
        if i % step == 0:
            t = cv2.resize(f, (a.width, a.width * f.shape[0] // f.shape[1]))
            cv2.putText(t, f"{i / fps:.2f}", (5, 22), 0, 0.6, (0, 0, 255), 2)
            tiles.append(t)
    cv2.imwrite(a.out, grid(tiles, a.cols))
    print(f"{a.out}: {len(tiles)} tiles every {a.every}s")


def motion(a):
    """Mean frame change per time bucket: 0 means a static hold, peaks are scrolls and transitions."""
    prev, d, fps = None, [], 30
    for f, fps in read_frames(a.video, (160, 90)):
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(float)
        if prev is not None:
            d.append(np.abs(g - prev).mean())
        prev = g
    b = max(1, round(fps * a.bucket))
    print(
        " ".join(
            f"{k * a.bucket:.1f}:{np.mean(d[k * b : (k + 1) * b]):.1f}" for k in range(len(d) // b)
        )
    )


def jumps(a):
    """Largest frame-to-frame changes. A smooth edit has no single frame far above its neighbours."""
    prev, d = None, []
    for f, _ in read_frames(a.video, (192, 108)):
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(float)
        if prev is not None:
            d.append(np.abs(g - prev).mean())
        prev = g
    d = np.array(d)
    top = sorted(int(k) for k in np.argsort(d)[::-1][: a.top])
    print(f"{len(d) + 1} frames; median {np.median(d):.2f}; max {d.max():.1f}")
    print("largest (frame, change):", [(k + 1, round(float(d[k]), 1)) for k in top])


def frames(a):
    """Writes single frames at the given times (seconds) for a full-resolution look."""
    want = sorted(a.times)
    for i, (f, fps) in enumerate(read_frames(a.video)):
        while want and i >= round(want[0] * fps):
            name = f"{a.prefix}-{want.pop(0):.2f}.png"
            cv2.imwrite(name, f)
            print(name)
        if not want:
            break


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("sheet")
    s.set_defaults(fn=sheet)
    s.add_argument("video")
    s.add_argument("--every", type=float, default=0.5)
    s.add_argument("--cols", type=int, default=6)
    s.add_argument("--width", type=int, default=320)
    s.add_argument("--out", default="sheet.png")
    m = sub.add_parser("motion")
    m.set_defaults(fn=motion)
    m.add_argument("video")
    m.add_argument("--bucket", type=float, default=0.5)
    j = sub.add_parser("jumps")
    j.set_defaults(fn=jumps)
    j.add_argument("video")
    j.add_argument("--top", type=int, default=12)
    f = sub.add_parser("frames")
    f.set_defaults(fn=frames)
    f.add_argument("video")
    f.add_argument("times", type=float, nargs="+")
    f.add_argument("--prefix", default="frame")
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
