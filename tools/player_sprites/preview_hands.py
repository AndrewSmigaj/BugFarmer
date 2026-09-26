"""preview_hands.py — see what the floating fists look like. PREVIEW ONLY, nothing ships.

The character is armless, so the hands are two little fists that float beside the body with a gap. Walking
and swinging are done by MOVING them, which means we can check how they read without drawing a single new
frame — composite the one fist sprite onto the outfit frames we already have and animate it.

Positions are MEASURED from each frame, not hardcoded: the hip row is found from the figure's own bbox and
the fists are placed just outside the body edges at that row. So it adapts to a beekeeper's smock and a
knight's pauldrons without per-outfit numbers.

Swing motion uses the REAL profile numbers from the game (`PlayerToolAnimator.cs:33-46`) so the preview is
honest about what a swing would actually look like.

  python3 tools/player_sprites/preview_hands.py walk bronze
  python3 tools/player_sprites/preview_hands.py walk --all
  python3 tools/player_sprites/preview_hands.py swing bronze sword
"""
import os
import sys
import math
import glob

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFITS = os.path.join(PLAYER, "outfits")
FIST = os.path.join(PLAYER, "hands", "fist.png")

# The fist was drawn on a figure 63px tall at its native grid; keep that ratio whatever size a frame is.
FIST_RATIO = 9.0 / 63.0

# Straight from PlayerToolAnimator.cs:33-46 — same arcs, same durations, so the preview matches the game.
PROFILES = {
    "sword": dict(kind="swing", duration=0.20, arc=100.0, offset=0.60),
    "axe":   dict(kind="chop",  duration=0.34, arc=110.0, offset=0.55),
    "net":   dict(kind="sweep", duration=0.25, arc=90.0,  offset=0.60),
    "spear": dict(kind="stab",  duration=0.22, arc=0.0,   offset=0.45, reach=1.10),
}
SPRITE_ART_ANGLE = 45.0          # PlayerToolAnimator.cs:50


def load_rgba(p):
    return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def scaled_fist(frame_h):
    """The fist at the right size for a frame this tall, NEAREST so it stays crisp."""
    f = load_rgba(FIST)
    target_h = max(3, round(frame_h * FIST_RATIO))
    s = target_h / f.shape[0]
    im = Image.fromarray(f, "RGBA")
    return np.asarray(im.resize((max(3, round(f.shape[1] * s)), target_h), Image.NEAREST), np.uint8)


def hip_edges(a, frac=0.56):
    """Row at `frac` down the figure, and the body's left/right edge on that row."""
    y0, y1, x0, x1 = bbox(a)
    row = y0 + int((y1 - y0) * frac)
    xs = np.where(a[..., 3][row] > 0)[0]
    if not len(xs):
        return row, x0, x1
    return row, xs.min(), xs.max()


def paste(dst, src, cx, cy):
    """Centre `src` at (cx, cy), clipped to dst."""
    h, w = src.shape[:2]
    x0, y0 = int(cx - w // 2), int(cy - h // 2)
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if xs1 <= xs0 or ys1 <= ys0:
        return
    sub = src[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
    m = sub[..., 3] > 0
    dst[ys0:ys1, xs0:xs1][m] = sub[m]


def with_fists(frame, view, beat, gap=0.06):
    """One frame with its fists. `beat` 0-3 drives the bob; fists swing opposite the legs."""
    out = frame.copy()
    fist = scaled_fist(bbox(frame)[1] - bbox(frame)[0] + 1)
    row, lx, rx = hip_edges(frame)
    g = max(2, int((rx - lx) * gap))

    # beats: 0 and 2 are strides (fists opposed), 1 and 3 are passing (fists level)
    swing = [1, 0, -1, 0][beat % 4]
    lift = [0, -1, 0, -1][beat % 4]
    reach = max(1, int((rx - lx) * 0.10))

    if view == "side":
        # one visible fist, swinging fore and aft past the hip
        paste(out, fist, rx + g + swing * reach, row + lift)
    else:
        # both fists, one forward one back — mirrored between the two stride beats
        paste(out, fist, lx - g, row + lift - swing)
        paste(out, fist, rx + g, row + lift + swing)
    return out


def walk(outfit):
    d = os.path.join(OUTFITS, outfit)
    made = []
    for row, view in [("front", "front"), ("back", "back"), ("side", "side")]:
        frames = []
        for beat, n in enumerate([1, 2, 3, 2]):
            p = os.path.join(d, f"{row}_{n}.png")
            if not os.path.exists(p):
                return []
            frames.append(with_fists(load_rgba(p), view, beat))
        h, w = frames[0].shape[:2]
        gif = []
        for f in frames:
            im = Image.new("RGBA", (w, h), (150, 160, 150, 255))
            im.alpha_composite(Image.fromarray(f, "RGBA"))
            gif.append(im.convert("RGB"))
        out = os.path.join(d, f"HANDS_walk_{row}.gif")
        gif[0].save(out, save_all=True, append_images=gif[1:], duration=150, loop=0)
        strip = Image.new("RGB", (4 * (w + 8), h), (38, 40, 46))
        for k in range(4):
            strip.paste(gif[k], (k * (w + 8), 0))
        strip.save(os.path.join(d, f"HANDS_walk_{row}_strip.png"))
        made.append(out)
    return made


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "walk"
    if mode != "walk":
        raise SystemExit("only `walk` implemented so far")
    names = ([os.path.basename(p) for p in sorted(glob.glob(os.path.join(OUTFITS, "*")))]
             if "--all" in sys.argv else [sys.argv[2]])
    for n in names:
        made = walk(n)
        print(f"  {n}: {len(made)} walk gifs" if made else f"  {n}: SKIPPED (frames missing)")


if __name__ == "__main__":
    main()
