"""swing_lab.py — render one swing APPROACH as a demo scene. Preview only, nothing ships.

Five approaches are compared, each with a different parent so they cannot quietly converge (see
docs/product/investigations/swing-design/DESIGN.md). This script is the harness: the approach is a parameter,
everything else is held constant so a difference in the output is a difference in the approach.

Each scene shows BOTH the side-facing and the front-facing character, because both have to work, and is
framed so the character and the whole arc fill the frame.

  python3 tools/player_sprites/swing_lab.py 1        # faithful baseline
  python3 tools/player_sprites/swing_lab.py 2        # impact-first
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFIT = os.path.join(PLAYER, "outfits", "bronze")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
DEST = os.path.join(REPO, "docs", "product", "investigations", "swing-design")

ease_out = lambda t: 1 - (1 - t) ** 2
ease_in = lambda t: t ** 3


def ease_out_back(t):
    c1, u = 1.70158, t - 1
    return 1 + (c1 + 1) * u ** 3 + c1 * u ** 2


# Profiles as shipped (PlayerToolAnimator.cs:33-46). `weight` 0..1 drives the derived approaches.
TOOLS = {
    "sword": dict(icon="sword_bronze_icon.png", kind="swing", arc=100.0, dur=0.20, off=0.60, weight=0.25),
    "axe":   dict(icon="axe_copper_icon.png",   kind="chop",  arc=110.0, dur=0.34, off=0.55, weight=1.00),
    "net":   dict(icon="small_net_icon.png",    kind="sweep", arc=90.0,  dur=0.25, off=0.60, weight=0.10),
    "hoe":   dict(icon="hoe_copper_icon.png",   kind="till",  arc=90.0,  dur=0.24, off=0.55, weight=0.65),
}
ART_ANGLE = 45.0
DIAG = np.array([-1, 1]) / math.sqrt(2)
GRIP_EXTRA = 0.16
HAND_FRAC = 0.17          # of BODY height — never off the tool sprite
HAND_ROT = 225
FPS = 30

# The pose the game cuts to the instant a swing ends (PlayerToolAnimator.cs:183-185, RestoreIdle :204).
# It is set directly — no lerp — so the gap between where an approach LEAVES the tool and this pose is a
# visible pop. The lab used to loop straight back to t=0, which hid that cost from every approach.
IDLE_ANGLE, IDLE_OFF, IDLE_SCALE = -35.0, 0.4, 0.75


# ---------------------------------------------------------------- approaches
def motion(approach, p, t):
    """-> (angle, offset, freeze, smear). angle/offset drive the pivot; freeze/smear are presentation."""
    aim, arc, off, half = 0.0, p["arc"], p["off"], p["arc"] / 2
    kind, w = p["kind"], p["weight"]

    if approach in (1, 2):                      # AS SHIPPED — 2 adds impact treatment only
        a, o = _shipped(kind, t, aim, arc, off)
        contact = {"swing": 0.65, "chop": 0.55, "sweep": 0.50, "till": 0.50}[kind]
        freeze = approach == 2 and contact <= t < contact + 0.06 + 0.10 * w
        return a, o, freeze, False

    if approach == 3:                           # STARDEW — half the swing is wind-up
        ant, strike = 0.50, 0.20                # recovery = 0.30, and recovery length is the weight knob
        top = aim + half + half * 0.35
        if t < ant:
            return aim + half + (top - (aim + half)) * ease_out(t / ant), off, False, False
        if t < ant + strike:
            u = (t - ant) / strike
            return top + (aim - top) * ease_in(u), off, False, u > 0.6
        u = (t - ant - strike) / (1 - ant - strike)
        u = min(1.0, u / (0.4 + 0.6 * w))       # heavier -> slower recovery, may not finish
        return aim + ((aim - half) - aim) * ease_out(u), off, False, False

    if approach == 4:                           # COOPER — strike instantly, weight in the follow-through
        strike = 0.12                           # almost no anticipation
        if t < strike:
            u = t / strike
            return (aim + half) + (aim - (aim + half)) * ease_in(u), off, False, u > 0.4
        u = (t - strike) / (1 - strike)
        end = aim - half - half * (0.30 + 0.50 * w)     # exaggerated overshoot, scaled by weight
        return aim + (end - aim) * ease_out_back(u), off, False, False

    if approach == 5:                           # SPRING — no authored segments
        freq = 5.5 - 3.0 * w                    # heavy = lower frequency
        ratio = 0.45 + 0.35 * w                 # heavy = more damped, less ring
        target = (aim + half) if t < 0.18 else (aim - half)
        x, v, dt = aim + half, 0.0, 1 / 240
        k = (2 * math.pi * freq) ** 2
        c = ratio * 2 * math.sqrt(k)
        steps = int(max(1, t * p["dur"] / dt))
        for i in range(steps):
            tt = i * dt / p["dur"]
            g = (aim + half) if tt < 0.18 else (aim - half)
            v += (k * (g - x) - c * v) * dt
            x += v * dt
        return x, off, False, abs(v) > 900
    return 0.0, off, False, False


def _shipped(kind, t, aim, arc, off):
    half = arc / 2
    if kind == "swing":
        top, end, cur = aim + half + half * 0.30, aim - half, aim + half
        ant, strf = 0.15, 0.50
        if t < ant:              a = cur + (top - cur) * ease_out(t / ant)
        elif t < ant + strf:     a = top + (aim - top) * ease_in((t - ant) / strf)
        else:                    a = aim + (end - aim) * ease_out_back((t - ant - strf) / (1 - ant - strf))
        o = off
        if ant <= t < ant + strf:   o = off + 0.2 * ease_in((t - ant) / strf)
        elif t >= ant + strf:       o = off + 0.2 - 0.2 * ease_out((t - ant - strf) / (1 - ant - strf))
        return a, o
    if kind == "chop":
        top, end, cur = aim + half + half * 0.35, aim - half, aim + half
        ant, strf, hold = 0.22, 0.33, 0.28
        if t < ant:                       return cur + (top - cur) * ease_out(t / ant), off
        if t < ant + strf:                return top + (aim - top) * ease_in((t - ant) / strf), off
        if t < ant + strf + hold:         return aim, off
        u = (t - ant - strf - hold) / (1 - ant - strf - hold)
        return aim + (end - aim) * ease_out(u), off
    if kind == "sweep":
        return aim + half - arc * ease_out(t), off
    if kind == "till":
        top, cur = aim + half + half * 0.35, aim + half
        ant, strf = 0.20, 0.30
        if t < ant:        return cur + (top - cur) * ease_out(t / ant), off
        if t < ant + strf: return top + (aim - top) * ease_in((t - ant) / strf), off
        u = (t - ant - strf) / (1 - ant - strf)
        return aim + ((aim - 12.0) - aim) * ease_out(u), off + ((off - 0.55) - off) * ease_in(u)
    return aim, off


# ---------------------------------------------------------------- drawing
def rgba(p): return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


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
        tgt = dst[b0:b1, a0:a1]
        tgt[m] = (tgt[m] * (1 - alpha) + s[m] * alpha).astype(np.uint8)


def grip_of(art):
    o = art[..., 3] > 0
    ys, xs = np.where(o)
    c = np.array([art.shape[1] / 2, art.shape[0] / 2])
    proj = (np.stack([xs, ys], 1) - c) @ DIAG
    return DIAG * (proj.max() - 0.22 * art.shape[0]) / art.shape[0]


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


def build(approach):
    side = rgba(os.path.join(OUTFIT, "side_2.png"))
    front = rgba(os.path.join(OUTFIT, "front_2.png"))
    BH = bbox(side)[1] - bbox(side)[0] + 1
    CELL = BH / 2.0
    hand = rgba(os.path.join(OUTFIT, "gauntlet", "front.png"))
    hand_s = scale_h(hand, BH * HAND_FRAC)
    dummy = scale_h(cut_side_dummy(), BH * 0.85)
    tree = scale_h(rgba(os.path.join(RES, "Objects", "tree_apple.png")), CELL * 2.6)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]

    # framed tight: two characters with arc room, dummy between, tree at the edge
    W, H = int(CELL * 6.4), int(CELL * 3.6)
    TS = int(CELL)
    rng = np.random.RandomState(7)
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H + TS, TS):
        for gx in range(0, W + TS, TS):
            paste(ground, scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    BASE = int(H * 0.88)
    SX, DX, FX = int(W * 0.20), int(W * 0.50), int(W * 0.80)

    def frame(tool, t, idle=False):
        p = TOOLS[tool]
        ang, off, freeze, smear = motion(approach, p, t)
        if idle:                                        # the pose the game snaps to when the swing ends
            ang, off, smear = IDLE_ANGLE, IDLE_OFF, False
        sc = ground.copy()
        paste(sc, tree, int(W * 0.03), BASE - tree.shape[0] // 2 + int(CELL * 0.2))
        paste(sc, dummy, DX, BASE - dummy.shape[0] // 2)
        art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL * (IDLE_SCALE if idle else 1.0))
        g = grip_of(art) + DIAG * GRIP_EXTRA

        for px, body, aim_off in ((SX, side, 0.0), (FX, front, -60.0)):
            cy = BASE - BH // 2
            paste(sc, body, px, cy)
            a = ang + aim_off
            if smear:                                   # subframe ghosts along the arc just travelled
                for k, al in ((6, 0.30), (12, 0.16)):
                    r2 = math.radians(a + k)
                    paste(sc, rot(art, a + k - ART_ANGLE),
                          px + math.cos(r2) * off * CELL, cy - math.sin(r2) * off * CELL, al)
            r = math.radians(a)
            tx, ty = px + math.cos(r) * off * CELL, cy - math.sin(r) * off * CELL
            paste(sc, rot(art, a - ART_ANGLE), tx, ty)
            rr = math.radians(-(a - ART_ANGLE))
            gg = g * art.shape[0]
            paste(sc, rot(hand_s, a - ART_ANGLE + HAND_ROT),
                  tx + gg[0] * math.cos(rr) - gg[1] * math.sin(rr),
                  ty + gg[0] * math.sin(rr) + gg[1] * math.cos(rr))
        im = Image.new("RGBA", (W, H), (30, 36, 30, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        return im.convert("RGB"), freeze

    frames, ms = [], []
    for tool in ("sword", "axe", "net", "hoe"):
        p = TOOLS[tool]
        n = max(8, int(p["dur"] * FPS * 3))
        for reps in (1, 2):
            for _ in range(reps):
                for i in range(n):
                    img, fr = frame(tool, i / (n - 1))
                    step = int(p["dur"] * 1000 / n)
                    frames.append(img)
                    ms.append(step * (4 if fr else 1))     # a freeze is a held frame, purely local + visual
            # hold the IDLE pose, not t=0 — the cut from swing-end to idle is part of what we're judging
            frames.append(frame(tool, 1.0, idle=True)[0]); ms.append(650)
    out = os.path.join(DEST, f"iteration-{approach}.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(f"  approach {approach}: {len(frames)} frames -> {out.replace('/mnt/c/', 'C:/')}")
    return out


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
