"""showcase.py — the "show people" reel: several armour sets running and swinging. FREE, no API.

  python3 tools/player_sprites/showcase.py                       # five sets, the default pick
  python3 tools/player_sprites/showcase.py bronze silver ranger  # your own pick
  python3 tools/player_sprites/showcase.py --approach 11         # a different swing feel

Writes `tools/_generated/player/SHOWCASE.gif`.

Layout, top to bottom:
  band 1   each set RUNNING RIGHT   (side frames, fists swinging fore and aft)
  band 2   each set RUNNING DOWN    (front frames, same fists, toward the viewer)
  band 3   each set SWINGING, side view   — a different tool per set
  band 4   the same swings, front view

The point of putting all four bands in one loop is that a set has to hold up in motion, from every angle,
holding a weapon — not just standing still on a contact sheet. Sets that look fine as a portrait have
fallen apart the moment they moved.

The swing comes from `swing_lab` so this reel cannot drift from the designed motion; change the approach
there and this follows.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swing_lab as S                                    # noqa: E402
from demo_swings import rgba, bbox, scale_h, rot, paste, torso   # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFITS = os.path.join(PLAYER, "outfits")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

DEFAULT = ["bronze", "silver", "ranger", "hornet-stinger", "wizard-robe"]
TOOLS_FOR = ["sword", "axe", "net", "spear", "shovel"]   # one per column, so all six get seen
RUN_CYCLE = [1, 2, 3, 2]
RUN_MS = 90                       # running, not walking — same frames, played faster
HAND_SWING = 0.42
HAND_ROLL = 55.0
APPROACH = 10


def load(name):
    d = os.path.join(OUTFITS, name)
    need = [f"{r}_{i}.png" for r in ("front", "side") for i in (1, 2, 3)] + ["gauntlet/front.png"]
    if any(not os.path.exists(os.path.join(d, f)) for f in need):
        return None
    return dict(name=name,
                side=[rgba(os.path.join(d, f"side_{i}.png")) for i in (1, 2, 3)],
                front=[rgba(os.path.join(d, f"front_{i}.png")) for i in (1, 2, 3)],
                hand=rgba(os.path.join(d, "gauntlet", "front.png")))


def build(names, approach=APPROACH):
    sets = [s for s in (load(n) for n in names) if s]
    if not sets:
        raise SystemExit("no usable outfits")

    BH = max(bbox(s["side"][1])[1] - bbox(s["side"][1])[0] + 1 for s in sets)
    CELL = BH / 2.0
    for s in sets:                                       # one height for every set, or they look mismatched
        for k in ("side", "front"):
            s[k] = [scale_h(f, BH) for f in s[k]]
        s["hand"] = scale_h(s["hand"], BH * S.HAND_FRAC)

    COLW, ROWH = int(CELL * 2.9), int(CELL * 2.5)
    W, H = COLW * len(sets), ROWH * 4
    TS = int(CELL)
    rng = np.random.RandomState(11)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H + TS, TS):
        for gx in range(0, W + TS, TS):
            paste(ground, scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    def run_pose(sc, s, cx, base, bank_name, beat):
        """A run is the walk frames played fast with the fists thrown further and rolled harder."""
        bank = s[bank_name]
        body = bank[RUN_CYCLE[beat % len(RUN_CYCLE)] - 1]
        cy = base - body.shape[0] // 2
        paste(sc, body, cx, cy)
        row, lx, rx = torso(bank[1])
        mid, halfw = (lx + rx) / 2, (rx - lx) / 2
        dy = cy - body.shape[0] / 2
        ph = math.sin(beat / len(RUN_CYCLE) * 2 * math.pi)
        for sgn in (+1, -1):
            if bank_name == "side" and sgn < 0:
                continue                                 # side view shows the near fist only
            off = sgn * ph * halfw * 2 * HAND_SWING
            paste(sc, rot(s["hand"], -ph * sgn * HAND_ROLL),
                  cx - body.shape[1] / 2 + mid + off, dy + row, 1.0 if off > 0 else 0.55)

    def swing_pose(sc, s, cx, base, bank_name, tool, t):
        p = S.TOOLS[tool]
        ang, off, freeze, smear = S.motion(approach, p, t)
        aim = 0.0 if bank_name == "side" else -60.0
        body = s[bank_name][1]
        cy = base - body.shape[0] // 2
        paste(sc, body, cx, cy)
        art = scale_h(rgba(os.path.join(RES, "Items", p["icon"])), CELL)
        g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]
        a = ang + aim
        if bank_name == "front":
            a = max(a, -30.0)                            # stop in front, don't bury it in the ground
        r = math.radians(a)
        tx, ty = cx + math.cos(r) * off * CELL, cy - math.sin(r) * off * CELL
        if smear:
            for k, al in ((7, 0.26), (14, 0.13)):
                paste(sc, rot(art, a + k - S.ART_ANGLE), tx, ty, al)
        paste(sc, rot(art, a - S.ART_ANGLE), tx, ty)
        rr = math.radians(-(a - S.ART_ANGLE))
        paste(sc, rot(s["hand"], a - S.ART_ANGLE + S.HAND_ROT),
              tx + g[0] * math.cos(rr) - g[1] * math.sin(rr),
              ty + g[0] * math.sin(rr) + g[1] * math.cos(rr))
        return freeze

    # Every band shares one timeline: the runs loop continuously while the swings play through, so the
    # reel reads as one moment rather than four clips stitched together.
    nsw = max(10, int(0.22 * S.FPS * 3))
    frames, ms = [], []
    for beat in range(nsw):
        sc = ground.copy()
        fr = False
        for i, s in enumerate(sets):
            cx = int(COLW * (i + 0.5))
            run_pose(sc, s, cx, int(ROWH * 0.92), "side", beat)
            run_pose(sc, s, cx, int(ROWH * 1.92), "front", beat)
            tool = TOOLS_FOR[i % len(TOOLS_FOR)]
            t = (beat % nsw) / (nsw - 1)
            fr |= swing_pose(sc, s, cx, int(ROWH * 2.92), "side", tool, t)
            swing_pose(sc, s, cx, int(ROWH * 3.92), "front", tool, t)
        im = Image.new("RGBA", (W, H), (28, 34, 28, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        frames.append(im.convert("RGB"))
        ms.append(RUN_MS * (3 if fr else 1))

    out = os.path.join(PLAYER, "SHOWCASE.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(f"  {len(sets)} sets x {len(frames)} frames -> {out.replace('/mnt/c/', 'C:/')}")
    print(f"  sets: {', '.join(s['name'] for s in sets)}")
    print(f"  tools: {', '.join(TOOLS_FOR[:len(sets)])}")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ap = APPROACH
    if "--approach" in sys.argv:
        ap = int(sys.argv[sys.argv.index("--approach") + 1])
        args = [a for a in args if a != str(ap)]
    build(args or DEFAULT, ap)
