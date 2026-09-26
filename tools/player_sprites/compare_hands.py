"""compare_hands.py — see candidate hand sets IN THE ANIMATIONS. FREE, no API.

  python3 tools/player_sprites/compare_hands.py bronze

Writes `outfits/<outfit>/hands/candidates/COMPARE.gif`.

A sheet of four hands on a magenta background tells you almost nothing. What matters is whether they
read while the character is idle, walking, running, and holding a weapon — which is the only reason
these sprites exist. So every candidate set is rendered through the real motion from `gait.py`, side by
side, on one timeline.

Columns are the states; rows are the candidate sets, plus the currently-approved set at the top as the
control. Judge downward: same state, different hands.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_propagation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import swing_lab as S                                    # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

# The four views each candidate sheet is drawn in, left to right.
RELAXED_BACK, RELAXED_PALM, FIST_BACK, FIST_PALM = 0, 1, 2, 3


def rgba(p):
    return np.asarray(Image.open(p).convert("RGBA"), np.uint8)


def key_magenta(rgb):
    """Figure mask: magenta reachable from the border is background."""
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mag = (R > 140) & (B > 140) & (G < 110) & (np.abs(R - B) < 70)
    seed = np.zeros_like(mag)
    seed[0, :], seed[-1, :] = mag[0, :], mag[-1, :]
    seed[:, 0], seed[:, -1] = mag[:, 0], mag[:, -1]
    return ~binary_propagation(seed, mask=mag)


def cut_hands(sheet_path, want=4):
    """The four hands off a candidate sheet, left to right, each trimmed to its own ink."""
    rgb = np.asarray(Image.open(sheet_path).convert("RGB"), int)
    art = key_magenta(rgb)
    out = np.dstack([rgb.astype(np.uint8), (art * 255).astype(np.uint8)])
    cols = art.any(0)
    idx = np.where(cols)[0]
    gaps, run = [], None
    for i in range(idx.min(), idx.max() + 2):
        if i <= idx.max() and not cols[i]:
            run = i if run is None else run
        elif run is not None:
            gaps.append((i - run, run))
            run = None
    gaps.sort(reverse=True)
    cuts = sorted(g[1] + g[0] // 2 for g in gaps[:want - 1])
    edges = [idx.min()] + cuts + [idx.max() + 1]
    hands = []
    for a, b in zip(edges, edges[1:]):
        m = np.zeros_like(art)
        m[:, a:b] = art[:, a:b]
        if not m.any():
            continue
        ys, xs = np.where(m)
        crop = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        crop[..., 3] = np.where(m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
        hands.append(crop)
    return hands


def idle_into(scene, bx, by, body, neutral, back_hand, palm_hand):
    """STANDING. Just the resting pose — hands hanging at the waist, nothing moving."""
    ny0, ny1, cx, tw = gait.anchor(neutral)
    bh = ny1 - ny0 + 1
    h, w = body.shape[:2]
    ox, oy = bx - w / 2.0, by - h / 2.0
    wy = oy + ny0 + int((ny1 - ny0) * gait.WALK["waist"])
    r = gait.WALK["ratio"]
    rest = tw * 0.42
    gait._paste(scene, gait._sz(gait._dim(palm_hand), bh, r), ox + cx - rest, wy)
    gait._paste(scene, body, bx, by)
    gait._paste(scene, gait._sz(back_hand, bh, r), ox + cx + rest, wy)


def holding_into(scene, bx, by, body, neutral, fist, tool_png):
    """Holding a sword at rest — the real test of whether a hand works on a handle."""
    ny0, ny1, cx, _ = gait.anchor(neutral)
    bh = ny1 - ny0 + 1
    cell = bh / 2.0
    h, w = body.shape[:2]
    ox, oy = bx - w / 2.0, by - h / 2.0
    art = S.scale_h(rgba(tool_png), cell)
    g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]
    a = -20.0
    r = math.radians(a)
    tx = ox + cx + math.cos(r) * 0.62 * cell
    ty = oy + ny0 + (ny1 - ny0) * 0.55 - math.sin(r) * 0.62 * cell
    gait._paste(scene, body, bx, by)
    gait._paste(scene, S.rot(art, a - S.ART_ANGLE), tx, ty)
    rr = math.radians(-(a - S.ART_ANGLE))
    gait._paste(scene, gait._sz(S.rot(fist, a - S.ART_ANGLE + S.HAND_ROT), bh, gait.RUN["ratio"]),
                tx + g[0] * math.cos(rr) - g[1] * math.sin(rr),
                ty + g[0] * math.sin(rr) + g[1] * math.cos(rr))


def build(outfit="bronze"):
    d = os.path.join(PLAYER, "outfits", outfit)
    cand = os.path.join(d, "hands", "candidates")
    sets = []
    for name in sorted(os.listdir(cand)):
        p = os.path.join(cand, name, "result.png")
        if os.path.isdir(os.path.join(cand, name)) and os.path.exists(p):
            sets.append((name, cut_hands(p)))
    if not sets:
        raise SystemExit("no candidate sets")

    side = [rgba(os.path.join(d, f"side_{i}.png")) for i in (1, 2, 3)]
    front = [rgba(os.path.join(d, f"front_{i}.png")) for i in (1, 2, 3)]
    sword = os.path.join(RES, "Items", "sword_bronze_icon.png")
    BH = gait.anchor(side[1])[1] - gait.anchor(side[1])[0] + 1
    CW, CH = int(BH * 1.25), int(BH * 1.30)
    STATES = ["idle side", "walk side", "run side", "walk front", "holding sword"]
    LAB, ROWLAB = 26, 90

    frames, ms = [], []
    for beat in range(len(gait.CYCLE)):
        sheet = Image.new("RGB", (ROWLAB + CW * len(STATES), LAB + CH * len(sets)), (32, 32, 38))
        dr = ImageDraw.Draw(sheet)
        for k, s in enumerate(STATES):
            dr.text((ROWLAB + k * CW + 8, 7), s, fill=(215, 230, 255))
        for ri, (name, hands) in enumerate(sets):
            y = LAB + ri * CH
            dr.text((6, y + CH // 2), name, fill=(255, 225, 140))
            rb, rp = hands[RELAXED_BACK], hands[RELAXED_PALM]
            fb, fp = hands[FIST_BACK], hands[FIST_PALM]
            for k, state in enumerate(STATES):
                sc = np.zeros((CH, CW, 4), np.uint8)
                bx, by = CW / 2, CH / 2
                if state == "idle side":
                    idle_into(sc, bx, by, side[1], side[1], rb, rp)
                elif state == "walk side":
                    b = side[gait.CYCLE[beat] - 1]
                    gait.walk_into(sc, bx, by, b, side[1], rb, rp, beat)
                elif state == "run side":
                    b = side[gait.CYCLE[beat] - 1]
                    gait.run_into(sc, bx, by, b, side[1], fb, fp, beat)
                elif state == "walk front":
                    b = front[gait.CYCLE[beat] - 1]
                    gait.walk_front_into(sc, bx, by, b, front[0], rb, beat)
                else:
                    holding_into(sc, bx, by, side[1], side[1], fb, sword)
                im = Image.new("RGBA", (CW, CH), (150, 160, 150, 255))
                im.alpha_composite(Image.fromarray(sc, "RGBA"))
                sheet.paste(im.convert("RGB"), (ROWLAB + k * CW, y))
        frames.append(sheet)
        ms.append(gait.WALK["ms"])

    out = os.path.join(cand, "COMPARE.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(f"  {len(sets)} sets x {len(STATES)} states -> {out.replace('/mnt/c/', 'C:/')}")
    print(f"  sets: {', '.join(n for n, _ in sets)}")
    return out


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "bronze")
