"""swing_five.py — five diverse attack approaches, facing DOWN and UP. FREE, no API.

  python3 tools/player_sprites/swing_five.py

Writes into `tools/_generated/player/reviews/<date>-swing-five/` (cleared each run).

WHAT THE PREVIOUS PASS GOT WRONG
--------------------------------
Owner, 2026-08-04:
  down — *"it really does not need that swing back, and it really should swing through farther"*
  up   — *"not even a real swing, its backwards and also down pull through, its a backwards stabby
          motion as in going the wrong way"*

The up swing dipped the blade DOWN and then drove it UP. That is a reverse stab, not a sword swing.

WHAT REFERENCE SAYS
-------------------
A top-down sword attack is a **sweeping motion ACROSS the body**, giving a wide attack area, and the
anticipation / follow-through / recover frames are kept minimal so it stays quick (SLYNYRD, Pixelblog 56,
"Top Down Character Attack Animation"). The direction being attacked is the space the arc **passes
through** — it is not a thrust along that direction.

So every approach here is expressed relative to `centre`, the direction being attacked:

    facing DOWN  -> centre = -90  (the tile below him, straight down the screen)
    facing UP    -> centre = +90  (the tile above him)

and the arc sweeps THROUGH `centre` rather than ending at it.

BUDGET — 12 frames @ 20ms = 0.24s
    f0      ANTICIPATION   ONE frame. He said the down swing does not need the pull-back.
    f1-f4   STRIKE         the whole arc, four frames, with a blade trail
    f5-f6   HOLD           sits on the exit pose
    f7-f11  recovery
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
PAD = 230
MS = 20
ANTIC, STRIKE, HOLD, REC = 1, 4, 2, 5

FACINGS = {                       # centre = the direction attacked; sh = shoulder; behind = draw first
    "down": dict(centre=-90.0, sh=(0.26, 0.12), bank="front", behind=False),
    "up":   dict(centre=+90.0, sh=(0.26, 0.22), bank="back",  behind=True),
}


def _ease_out(u):
    return 1 - (1 - u) ** 3


# Each approach: (anticipation pose, [strike path poses...], rest pose).
# A pose is (arm_offset_from_centre, blade_behind_arm, reach). The arc must PASS THROUGH offset 0.
APPROACHES = {
    # 1 — the standard. Blade enters from one side, sweeps across the attacked space, exits the other.
    "A_sweep_across": (
        (+82, 70, 0.52),
        [(+40, 62, 0.56), (0, 50, 0.60), (-46, 40, 0.58), (-86, 34, 0.52)],
        (-86, 55, 0.46),
    ),
    # 2 — chop through. Comes from over the shoulder and carries well past centre. "swing through farther".
    "B_chop_through": (
        (+112, 88, 0.44),
        [(+50, 60, 0.54), (0, 20, 0.62), (-58, -6, 0.60), (-104, -18, 0.52)],
        (-70, 45, 0.46),
    ),
    # 3 — thrust. Barely rotates; the REACH does the work, straight into the tile and back.
    "C_thrust": (
        (+26, 8, 0.34),
        [(+8, 2, 0.48), (0, 0, 0.70), (0, 0, 0.76), (-4, 2, 0.62)],
        (+30, 40, 0.42),
    ),
    # 4 — round. A full circle about the shoulder, passing through the attacked space at speed.
    "D_round": (
        (+150, 80, 0.46),
        [(+70, 70, 0.54), (0, 55, 0.60), (-80, 40, 0.58), (-150, 30, 0.50)],
        (-120, 55, 0.44),
    ),
    # 5 — two-beat. Out across, then whipped back through centre the other way. Reads as a fast double.
    "E_double_back": (
        (+70, 66, 0.50),
        [(0, 44, 0.60), (-64, 30, 0.56), (-10, 46, 0.58), (+34, 58, 0.54)],
        (+34, 60, 0.46),
    ),
}


def poses_for(centre, spec):
    """Per-frame (arm, blade-behind-arm, reach) on the budget above.

    Each approach's strike path has exactly STRIKE poses, so the strike frames ARE the path — no
    resampling, no easing inside the arc. The path itself carries the acceleration, which keeps each
    approach's shape readable instead of smoothed into the same curve as its neighbours.
    """
    antic, path, rest = spec
    assert len(path) == STRIKE, f"{len(path)} strike poses, budget is {STRIKE}"

    def at(p):
        return (centre + p[0], p[1], p[2])

    out = [at(antic)] * ANTIC
    out += [at(p) for p in path]
    hit = out[-1]
    out += [hit] * HOLD
    r = at(rest)
    for i in range(REC):
        u = _ease_out((i + 1) / REC)
        out.append(tuple(hit[k] + (r[k] - hit[k]) * u for k in range(3)))
    return out


def build(facing, name, two_handed=False):
    cfg = FACINGS[facing]
    hands, _ = R.load_hands(OUTFIT)
    bank = R.load_bank(OUTFIT, cfg["bank"], 0)
    body = bank[0]
    ny0, ny1, cx, _ = gait.anchor(body)
    bh = ny1 - ny0 + 1
    cell = bh / 2.0
    art0 = S.scale_h(rgba(os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])), cell)
    grip = (S.grip_of(art0) + S.DIAG * S.GRIP_EXTRA) * art0.shape[0]
    poses = poses_for(cfg["centre"], APPROACHES[name])

    W, H = body.shape[1] + 2 * PAD, body.shape[0] + 2 * PAD
    out = []
    for i, (arm, back, reach) in enumerate(poses):
        sc = np.zeros((H, W, 4), np.uint8)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx, sy = ox + cx + cfg["sh"][0] * cell, bcy - cfg["sh"][1] * cell

        def place(a, b, rc):
            r = math.radians(a)
            hx, hy = sx + math.cos(r) * rc * cell, sy - math.sin(r) * rc * cell
            blade = a + b
            art = S.rot(art0, blade - S.ART_ANGLE)
            rr = math.radians(-(blade - S.ART_ANGLE))
            gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
            gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)
            return art, hx - gx, hy - gy, hx, hy, blade

        def weapon():
            if ANTIC < i < ANTIC + STRIKE:                       # trail on the strike frames
                pa, pb, pr = poses[i - 1]
                for f in (0.34, 0.67):
                    art, tx, ty, _, _, _ = place(pa + (arm - pa) * f, pb + (back - pb) * f,
                                                 pr + (reach - pr) * f)
                    gait._paste(sc, gait._dim(art, 0.5), tx, ty)
            art, tx, ty, hx, hy, blade = place(arm, back, reach)
            gait._paste(sc, art, tx, ty)
            fists = [(hands["grip_back"], 0.0)]
            if two_handed:
                fists.append((hands["grip_palm"], 0.17))
            for fist, up in fists:
                fx = hx + math.cos(math.radians(blade)) * up * art0.shape[0]
                fy = hy - math.sin(math.radians(blade)) * up * art0.shape[0]
                gait._paste(sc, gait._sz(S.rot(fist, blade + R.HAND_PERP), bh, gait.RUN["ratio"]), fx, fy)

        if cfg["behind"]:
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
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing-five")
    os.makedirs(d, exist_ok=True)
    for f in sorted(os.listdir(d)):
        os.remove(os.path.join(d, f))

    made = {}
    for facing in FACINGS:
        for name in APPROACHES:
            frames = build(facing, name)
            p = os.path.join(d, f"{facing}_{name}.gif")
            frames[0].save(p, save_all=True, append_images=frames[1:], duration=MS, loop=0)
            made[(facing, name)] = frames
            print(f"  {os.path.basename(p):28} {len(frames)}f @ {MS}ms = {len(frames)*MS/1000:.2f}s")

    for facing in FACINGS:
        rows = [(n, made[(facing, n)]) for n in APPROACHES]
        W = max(f[0].size[0] for _, f in rows)
        H = max(f[0].size[1] for _, f in rows)
        mid = ANTIC + STRIKE // 2
        sheet = Image.new("RGB", (len(rows) * W, 2 * (H + 22)), (28, 28, 34))
        dr = ImageDraw.Draw(sheet)
        for k, (n, frames) in enumerate(rows):
            for r, (idx, tag) in enumerate(((mid, "mid-arc"), (ANTIC + STRIKE - 1, "end of strike"))):
                bg = Image.new("RGB", (W, H), BG)
                im = frames[min(idx, len(frames) - 1)]
                bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
                sheet.paste(bg, (k * W, r * (H + 22) + 22))
                dr.text((k * W + 6, r * (H + 22) + 5), f"{n}  {tag}", fill=(255, 220, 140))
        sheet.save(os.path.join(d, f"ALL_{facing}.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")


if __name__ == "__main__":
    main()
