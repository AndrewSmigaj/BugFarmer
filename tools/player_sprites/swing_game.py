"""swing_game.py — attack swings built on a FRAME BUDGET, the way a game does it. FREE, no API.

  python3 tools/player_sprites/swing_game.py

Writes into `tools/_generated/player/reviews/<date>-swing-game/` (cleared each run).

WHY THE PREVIOUS ONES READ AS POSING, NOT ATTACKING
---------------------------------------------------
Owner: *"the user has to watch the play pull back the sword the swing the sword, its not a video game
swing"*.

They spread the motion evenly across the runtime with smooth easing, and gave the wind-up a third of it.
So you watch him lift the sword, then watch him lower it. That is a cutscene.

A game attack is not shaped like that. Almost all of the angular travel happens in **two or three
frames**, and the rest of the runtime is spent **holding the end pose** and recovering. The player
pressed a button; the strike has to already be happening.

THE FRAME BUDGET (14 frames @ 20ms = 0.28s)
--------------------------------------------
    f0-f1    ANTICIPATION   2 frames.  A SMALL lift. Not a wind-up you can watch.
    f2-f4    STRIKE         3 frames.  ~90% of the whole arc, in a tenth of a second.
    f5-f7    HOLD           3 frames.  The end pose sits still. This is what reads as impact.
    f8-f13   RECOVERY       6 frames.  Ease back to idle. Slowest part, and nobody is watching it.

The strike frames also draw a short TRAIL — the blade at the two angles it just passed through — because
at three frames of travel the eye needs the smear to read the arc at all.

Angles: 0 = screen right, 90 = up, -90 = straight down. `arm` is the arm's direction from the shoulder;
`back` is how far behind the arm the blade is held. blade = arm + back.
"""
import datetime
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import render_animations as R                            # noqa: E402
import swing_lab as S                                    # noqa: E402
from compare_hands import rgba                           # noqa: E402

OUTFIT, TOOL = "bronze", "sword"
BG = (150, 160, 150)
PAD = 210
# 20ms is the lowest delay gif players reliably honour (below that many clamp to 100ms). 14 frames x
# 20ms = 0.28s, which is an attack. At 33ms it came out 0.46s — half a second of committed animation per
# swing, which is the "watch him pull it back" problem measured rather than eyeballed.
MS = 20

ANTIC, STRIKE, HOLD, REC = 2, 3, 3, 6
N = ANTIC + STRIKE + HOLD + REC


def _ease_out(u):
    return 1 - (1 - u) ** 3


def keyframes(idle, antic, hit, rest=None):
    """(arm, back) per frame from four poses, on the budget above. Each pose is (arm_deg, back_deg)."""
    rest = rest or idle
    out = []
    for i in range(ANTIC):                                   # small lift, linear, fast
        u = (i + 1) / ANTIC
        out.append((idle[0] + (antic[0] - idle[0]) * u, idle[1] + (antic[1] - idle[1]) * u))
    for i in range(STRIKE):                                  # the whole arc, 3 frames, accelerating
        u = ((i + 1) / STRIKE) ** 0.72
        out.append((antic[0] + (hit[0] - antic[0]) * u, antic[1] + (hit[1] - antic[1]) * u))
    out += [hit] * HOLD                                      # sit on the end pose — this is the impact
    for i in range(REC):                                     # ease home, nobody is watching
        u = _ease_out((i + 1) / REC)
        out.append((hit[0] + (rest[0] - hit[0]) * u, hit[1] + (rest[1] - hit[1]) * u))
    return out


# idle -> anticipation -> hit.  The HIT pose is the one that has to cover the tile being attacked.
FRONT = {                                   # facing the camera: the tip must land PAST HIS FEET
    "down": dict(sh=(0.26, 0.12), idle=(-50, 55), antic=(58, 88), hit=(-96, -4)),
}
BACK = {                                    # facing away: the tip must land ABOVE HIS HEAD
    "up": dict(sh=(0.26, 0.22), idle=(-50, 55), antic=(-82, 88), hit=(104, 2)),
}
SIDE = {                                    # for comparison against the settled side swing
    "side": dict(sh=(0.06, 0.40), idle=(-35, 60), antic=(120, 88), hit=(-104, 40)),
}


def build(kind, cfg, two_handed):
    hands, _ = R.load_hands(OUTFIT)
    bank = R.load_bank(OUTFIT, {"down": "front", "up": "back", "side": "side"}[kind],
                       0 if kind != "side" else 1)
    body = bank[0 if kind != "side" else 1]
    ny0, ny1, cx, _ = gait.anchor(body)
    bh = ny1 - ny0 + 1
    cell = bh / 2.0
    art0 = S.scale_h(rgba(os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])), cell)
    grip = (S.grip_of(art0) + S.DIAG * S.GRIP_EXTRA) * art0.shape[0]
    poses = keyframes(cfg["idle"], cfg["antic"], cfg["hit"])
    behind = kind == "up"

    W, H = body.shape[1] + 2 * PAD, body.shape[0] + 2 * PAD
    out = []
    for i, (arm, back) in enumerate(poses):
        sc = np.zeros((H, W, 4), np.uint8)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx, sy = ox + cx + cfg["sh"][0] * cell, bcy - cfg["sh"][1] * cell

        def place(a, b):
            r = math.radians(a)
            hx, hy = sx + math.cos(r) * R.SWORD_REACH * cell, sy - math.sin(r) * R.SWORD_REACH * cell
            blade = a + b
            art = S.rot(art0, blade - S.ART_ANGLE)
            rr = math.radians(-(blade - S.ART_ANGLE))
            gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
            gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)
            return art, hx - gx, hy - gy, hx, hy, blade

        def weapon():
            # TRAIL on the strike frames only: three frames of travel is too fast to read without it.
            if ANTIC <= i < ANTIC + STRIKE and i > ANTIC:
                pa, pb = poses[i - 1]
                for f in (0.34, 0.67):
                    a, b = pa + (arm - pa) * f, pb + (back - pb) * f
                    art, tx, ty, _, _, _ = place(a, b)
                    gait._paste(sc, S.rot(gait._dim(art, 0.55), 0), tx, ty)
            art, tx, ty, hx, hy, blade = place(arm, back)
            gait._paste(sc, art, tx, ty)
            fists = [(hands["grip_back"], 0.0)]
            if two_handed:
                fists.append((hands["grip_palm"], 0.17))
            for fist, up in fists:
                fx = hx + math.cos(math.radians(blade)) * up * art0.shape[0]
                fy = hy - math.sin(math.radians(blade)) * up * art0.shape[0]
                gait._paste(sc, gait._sz(S.rot(fist, blade + R.HAND_PERP), bh, gait.RUN["ratio"]), fx, fy)

        if behind:
            weapon()
            gait._paste(sc, body, bx, by)
        else:
            gait._paste(sc, body, bx, by)
            weapon()

        im = Image.new("RGBA", (W, H), BG + (255,))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        out.append(im.convert("RGB"))
    return R.crop_union(out)


def main():
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing-game")
    os.makedirs(d, exist_ok=True)
    for f in sorted(os.listdir(d)):
        os.remove(os.path.join(d, f))

    made = []
    for group in (FRONT, BACK, SIDE):
        for kind, cfg in group.items():
            for two in (False, True):
                frames = build(kind, cfg, two)
                lbl = "2h" if two else "1h"
                p = os.path.join(d, f"sword_{kind}_{lbl}.gif")
                frames[0].save(p, save_all=True, append_images=frames[1:], duration=MS, loop=0)
                made.append((f"{kind} {lbl}", frames))
                print(f"  {os.path.basename(p):26} {len(frames)} frames @ {MS}ms = {len(frames)*MS/1000:.2f}s")

    # filmstrip of every frame of the 1h down swing, labelled by phase — the budget made visible
    frames = [f for lbl, f in made if lbl == "down 1h"][0]
    W, H = frames[0].size
    tags = (["ANTIC"] * ANTIC) + (["STRIKE"] * STRIKE) + (["HOLD"] * HOLD) + (["rec"] * REC)
    sheet = Image.new("RGB", (len(frames) * W, H + 22), (28, 28, 34))
    dr = ImageDraw.Draw(sheet)
    for k, f in enumerate(frames):
        sheet.paste(f, (k * W, 22))
        dr.text((k * W + 4, 5), f"{k} {tags[k]}", fill=(255, 220, 140) if tags[k] != "rec" else (120, 120, 140))
    sheet.save(os.path.join(d, "FRAME_BUDGET_down.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")


if __name__ == "__main__":
    main()
