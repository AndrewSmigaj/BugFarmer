"""demo_swings.py — an outfit walking, then swinging each tool, in a scene. PREVIEW ONLY.

  python3 tools/player_sprites/demo_swings.py bronze
  python3 tools/player_sprites/demo_swings.py --all          # every outfit -> outfits/<name>/DEMO.gif

The point is to judge it in context. Cropped to the character the sword leaves frame entirely, and a
swing whose end you can't see tells you nothing.

The swing is the one the design work picked — `swing_lab.py` approach 6, imported rather than copied,
so this preview cannot drift from the design. Its five iterations and the reasoning are in
`docs/product/investigations/swing-design/`. In short: a damped spring drives the pivot toward three
targets in turn (wind back, strike through, return to the rest pose), a heavier tool is given a
FURTHER strike target so weight reads as distance rather than as ringing, and contact holds the
contact pose for a few frames.

The character is armless, so the hands are separate fists that are MOVED rather than drawn. Walking
swings them fore and aft past the hip and rolls them as they go; swinging puts one on the handle at a
grip measured off that tool's own sprite.
"""
import glob
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swing_lab as S                       # the motion, the profiles and the idle pose live there

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFITS = os.path.join(PLAYER, "outfits")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

APPROACH = 6
WALK_MS = 150
WALK_CYCLE = [1, 2, 3, 2]                   # frame 4 came back a second stride, so it is not cut
HAND_SWING = 0.42                           # fore/aft travel, as a fraction of torso width
HAND_ROLL = 55.0                            # the fist rolls as it swings, turning like a wheel


def rgba(p):
    return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def scale_h(a, h):
    s = h / a.shape[0]
    return np.asarray(Image.fromarray(a, "RGBA").resize(
        (max(2, round(a.shape[1] * s)), max(2, round(h))), Image.NEAREST), np.uint8)


def rot(a, d):
    return np.asarray(Image.fromarray(a, "RGBA").rotate(d, resample=Image.NEAREST, expand=True), np.uint8)


def paste(dst, src, cx, cy, alpha=1.0):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0 = max(0, x0), max(0, y0)
    a1, b1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if a1 <= a0 or b1 <= b0:
        return
    s = src[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    m = s[..., 3] > 0
    if alpha >= 1.0:
        dst[b0:b1, a0:a1][m] = s[m]
    else:
        t = dst[b0:b1, a0:a1]
        t[m] = (t[m] * (1 - alpha) + s[m] * alpha).astype(np.uint8)


def torso(frame):
    """Chest row and body edges, measured ONCE from the neutral frame.

    Measuring per frame makes the hands jitter, because the legs change the silhouette underneath
    them and the anchor follows the legs instead of the chest.
    """
    y0, y1, x0, x1 = bbox(frame)
    row = y0 + int((y1 - y0) * 0.46)
    xs = np.where(frame[..., 3][row] > 0)[0]
    return (row, xs.min(), xs.max()) if len(xs) else (row, x0, x1)


def cut_side_dummy():
    from scipy.ndimage import label, binary_dilation
    a = rgba(os.path.join(PLAYER, "props", "practice-dummy", "result.png"))
    solid = binary_dilation(a[..., :3].astype(int).sum(2) > 70, np.ones((7, 7), bool))
    lbl, n = label(solid, structure=np.ones((3, 3), int))
    best = None
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() < 4000:
            continue
        ys, xs = np.where(m)
        if best is None or xs.mean() > best[0]:
            best = (xs.mean(), ys.min(), ys.max(), xs.min(), xs.max(), m)
    _, y0, y1, x0, x1, m = best
    f = np.zeros_like(a)
    f[m] = a[m]
    f[..., 3] = np.where(m, 255, 0)
    return f[y0:y1 + 1, x0:x1 + 1]


def build(name):
    d = os.path.join(OUTFITS, name)
    need = [f"{r}_{i}.png" for r in ("front", "side") for i in (1, 2, 3)] + ["gauntlet/front.png"]
    if any(not os.path.exists(os.path.join(d, f)) for f in need):
        return None

    side = [rgba(os.path.join(d, f"side_{i}.png")) for i in (1, 2, 3)]
    front = [rgba(os.path.join(d, f"front_{i}.png")) for i in (1, 2, 3)]
    BH = bbox(side[1])[1] - bbox(side[1])[0] + 1
    CELL = BH / 2.0                                   # the character is two world cells tall
    hand = scale_h(rgba(os.path.join(d, "gauntlet", "front.png")), BH * S.HAND_FRAC)

    dummy = scale_h(cut_side_dummy(), BH * 0.85)
    tree = scale_h(rgba(os.path.join(RES, "Objects", "tree_apple.png")), CELL * 2.6)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]

    W, H = int(CELL * 6.4), int(CELL * 3.6)
    TS = int(CELL)
    rng = np.random.RandomState(7)
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H + TS, TS):
        for gx in range(0, W + TS, TS):
            paste(ground, scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    BASE = int(H * 0.88)
    SX, DX, FX = int(W * 0.20), int(W * 0.50), int(W * 0.80)
    frames, ms = [], []

    def stage():
        sc = ground.copy()
        paste(sc, tree, int(W * 0.03), BASE - tree.shape[0] // 2 + int(CELL * 0.2))
        paste(sc, dummy, DX, BASE - dummy.shape[0] // 2)
        return sc

    # ---- walking: the fists are MOVED, no walk art is drawn for them ------------------------
    for rep in range(2):
        for beat, fi in enumerate(WALK_CYCLE):
            sc = stage()
            for px, bank in ((SX, side), (FX, front)):
                body = bank[fi - 1]
                cy = BASE - body.shape[0] // 2
                paste(sc, body, px, cy)
                row, lx, rx = torso(bank[1])
                mid, halfw = (lx + rx) / 2, (rx - lx) / 2
                dy = cy - body.shape[0] / 2
                ph = math.sin(beat / len(WALK_CYCLE) * 2 * math.pi)
                for s in (+1, -1):                    # two fists, opposite phase
                    if bank is side and s < 0:
                        continue                      # side view shows the near fist only
                    off = s * ph * halfw * 2 * HAND_SWING
                    near = off > 0
                    paste(sc, rot(hand, -ph * s * HAND_ROLL),
                          px - body.shape[1] / 2 + mid + off, dy + row,
                          1.0 if near else 0.55)
            frames.append(sc)
            ms.append(WALK_MS)

    # ---- swinging each tool -----------------------------------------------------------------
    for tool in ("sword", "axe", "net", "hoe"):
        p = S.TOOLS[tool]
        art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL)
        g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]
        n = max(10, int(p["dur"] * S.FPS * 4))

        def pose(t, idle=False):
            sc = stage()
            ang, off, freeze, _ = S.motion(APPROACH, p, t)
            if idle:
                ang, off = S.IDLE_ANGLE, S.IDLE_OFF
            for px, body, aim in ((SX, side[1], 0.0), (FX, front[1], -60.0)):
                cy = BASE - body.shape[0] // 2
                a = ang + aim
                r = math.radians(a)
                tx = px + math.cos(r) * off * CELL
                ty = cy - math.sin(r) * off * CELL
                _, lx, rx = torso(body)
                bl = px - body.shape[1] / 2 + lx
                br = px - body.shape[1] / 2 + rx
                # DEPTH SORT, from the arc angle per frame rather than from facing. The front view
                # sweeps the tool across the character's own torso, and drawn on top it looks like
                # it is slicing through him. `_behindPlayer` in the game covers only the up-facing
                # case; the artefact is mid-arc, so the test has to be where the tool actually IS.
                behind = bl < tx < br
                tool_img = rot(art, a - S.ART_ANGLE)
                rr = math.radians(-(a - S.ART_ANGLE))
                hx = tx + g[0] * math.cos(rr) - g[1] * math.sin(rr)
                hy = ty + g[0] * math.sin(rr) + g[1] * math.cos(rr)
                hand_img = rot(hand, a - S.ART_ANGLE + S.HAND_ROT)
                if behind:
                    paste(sc, tool_img, tx, ty)
                    paste(sc, hand_img, hx, hy)
                    paste(sc, body, px, cy)
                else:
                    paste(sc, body, px, cy)
                    paste(sc, tool_img, tx, ty)
                    paste(sc, hand_img, hx, hy)
            return sc, freeze

        for reps in (1, 2):
            for _ in range(reps):
                for i in range(n):
                    sc, fz = pose(i / (n - 1))
                    frames.append(sc)
                    ms.append(int(p["dur"] * 1000 / n) * (4 if fz else 1))
        frames.append(pose(1.0, idle=True)[0])
        ms.append(700)

    out = os.path.join(d, "DEMO.gif")
    imgs = []
    for f in frames:
        im = Image.new("RGBA", (W, H), (30, 36, 30, 255))
        im.alpha_composite(Image.fromarray(f, "RGBA"))
        imgs.append(im.convert("RGB"))
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=ms, loop=0)
    return out


def main():
    names = ([os.path.basename(p) for p in sorted(glob.glob(os.path.join(OUTFITS, "*")))
              if os.path.isdir(p)] if "--all" in sys.argv else sys.argv[1:])
    for n in names:
        out = build(n)
        print(f"  {n:16s} {'-> DEMO.gif' if out else 'SKIPPED (frames or gauntlet missing)'}")


if __name__ == "__main__":
    main()
