"""showcase.py — the "show people" reel: several armour sets running and swinging. FREE, no API.

  python3 tools/player_sprites/showcase.py                       # five sets, the default pick
  python3 tools/player_sprites/showcase.py bronze silver ranger  # your own pick
  python3 tools/player_sprites/showcase.py --approach 11         # a different swing feel

Writes `tools/_generated/player/SHOWCASE.gif`.

Layout, top to bottom — six bands:
  1  WALK right   (side)      fists past the hip, rolling
  2  WALK down    (front)
  3  RUN  right   (side)      both fists up at the chest, pointing forward, pumping
  4  RUN  down    (front)
  5  SWING side               a different tool per column, so all six motions appear
  6  SWING front

Walk and run are DIFFERENT poses, not one played faster. Getting that wrong once produced fists that
"go crazy like flapping" — the walk's ±55° roll running at running speed. They are separate here, and
each advances off its own clock (150ms vs 90ms) against one shared timeline.

The point of one loop is that a set has to hold up in motion, from every angle, holding a weapon — not
just standing still on a contact sheet. Sets that look fine as a portrait have fallen apart the moment
they moved.

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
CYCLE = [1, 2, 3, 2]              # frame 4 came back a second stride, so it is dropped
APPROACH = 10

# WALK — the approved pose (`demo_swings.py`, signed off as "walk b is fine"). Fists swing fore and aft
# past the HIP, rolling as they go "as if on a wheel"; the side view shows the near fist only and the far
# one is dimmed.
WALK_MS = 150
WALK_SWING = 0.42                 # fore/aft travel, as a fraction of torso width
WALK_ROLL = 55.0                  # how much the fist rolls through the swing

# RUN — a DIFFERENT pose, not the walk played fast. This is the thing the first showcase got wrong: it
# ran the walk's ±55° roll at running speed, which reads as flapping. Owner: "those are absolutely not
# the hand movements we agreed on, they are absolutely crazy going crazy like flapping".
# Matched against the approved `RUN_r75.gif`: BOTH fists visible even side-on, raised to CHEST height,
# rotated to POINT FORWARD, pumping with bigger travel — a runner's fists, not a stroll.
RUN_MS = 90
RUN_SWING = 0.62                  # bigger travel than the walk
RUN_ROT = 75.0                    # fists point forward and hold there
RUN_ROLL = 16.0                   # only a little roll on top of that
RUN_RAISE = 0.05                  # lifted toward the chest, as a fraction of body height. 0.13 put the
                                  # fists over the FACE — the reference keeps them below the helmet.


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

    BANDS = 6                     # walk side · walk front · run side · run front · swing side · swing front
    COLW, ROWH = int(CELL * 2.9), int(CELL * 2.5)
    W, H = COLW * len(sets), ROWH * BANDS
    TS = int(CELL)
    rng = np.random.RandomState(11)
    tiles = [rgba(os.path.join(RES, "Tiles", n)) for n in
             ("grass.png", "grass_v2.png", "grass_v3.png", "grass_v4.png", "grass_v5.png")]
    ground = np.zeros((H, W, 4), np.uint8)
    for gy in range(0, H + TS, TS):
        for gx in range(0, W + TS, TS):
            paste(ground, scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    def gait_pose(sc, s, cx, base, bank_name, beat, running):
        """Walk and run are DIFFERENT poses, not one speed apart.

        Walk: fists past the hip, rolling; side view shows the near fist only.
        Run:  both fists up at the chest, pointing forward, pumping — matched to `RUN_r75.gif`.
        """
        bank = s[bank_name]
        body = bank[CYCLE[beat % len(CYCLE)] - 1]
        cy = base - body.shape[0] // 2
        paste(sc, body, cx, cy)
        row, lx, rx = torso(bank[1])
        mid, halfw = (lx + rx) / 2, (rx - lx) / 2
        dy = cy - body.shape[0] / 2
        ph = math.sin(beat / len(CYCLE) * 2 * math.pi)
        travel = RUN_SWING if running else WALK_SWING
        lift = RUN_RAISE * body.shape[0] if running else 0.0
        for sgn in (+1, -1):
            if bank_name == "side" and sgn < 0 and not running:
                continue                                 # walking side-on shows the near fist only;
                                                         # running shows both, as the reference does
            off = sgn * ph * halfw * 2 * travel
            ang = (RUN_ROT - ph * sgn * RUN_ROLL) if running else (-ph * sgn * WALK_ROLL)
            near = off > 0
            paste(sc, rot(s["hand"], ang),
                  cx - body.shape[1] / 2 + mid + off, dy + row - lift,
                  1.0 if near else (0.75 if running else 0.55))

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
    # One shared timeline. The walk advances at WALK_MS and the run at RUN_MS off the same clock, so
    # the run genuinely reads as faster than the walk instead of both being driven at the frame rate —
    # which is what made the first version flap.
    nsw = max(16, int(0.22 * S.FPS * 4))
    STEP = 30                                            # ms per rendered frame
    frames, ms = [], []
    for f in range(nsw):
        now = f * STEP
        walk_beat = int(now / WALK_MS)
        run_beat = int(now / RUN_MS)
        sc = ground.copy()
        fr = False
        for i, s in enumerate(sets):
            cx = int(COLW * (i + 0.5))
            gait_pose(sc, s, cx, int(ROWH * 0.92), "side",  walk_beat, running=False)
            gait_pose(sc, s, cx, int(ROWH * 1.92), "front", walk_beat, running=False)
            gait_pose(sc, s, cx, int(ROWH * 2.92), "side",  run_beat,  running=True)
            gait_pose(sc, s, cx, int(ROWH * 3.92), "front", run_beat,  running=True)
            tool = TOOLS_FOR[i % len(TOOLS_FOR)]
            t = f / (nsw - 1)
            fr |= swing_pose(sc, s, cx, int(ROWH * 4.92), "side", tool, t)
            swing_pose(sc, s, cx, int(ROWH * 5.92), "front", tool, t)
        im = Image.new("RGBA", (W, H), (28, 34, 28, 255))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        frames.append(im.convert("RGB"))
        ms.append(STEP * (3 if fr else 1))

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
