"""run_swing_lab.py — SWING WHILE RUNNING. A lab, not a shipped motion. FREE, no API.

  python3 tools/player_sprites/run_swing_lab.py            # bronze
  python3 tools/player_sprites/run_swing_lab.py fireant

Owner, 2026-08-14: *"we need to make sure we can swing while running… when swinging while running the
walk/run hands change."* None of it is implemented — not in the game, not in `build.py` — so this renders
what it would LOOK like, to settle the off-hand before anything is built.

It is a LAB on purpose. `motions.py`: *the labs are for exploring, and nothing in a lab is durable.* A
motion becomes real by being copied into the approved data with the owner's words and rendered by
`build.py`. So nothing here outlives the decision, and it edits neither `gait.py` nor `official.py`.

WHAT IS BEING COMBINED, AND WHAT THE ACTUAL QUESTION IS
-------------------------------------------------------
Today a gait and a swing never overlap, and they hold DIFFERENT HANDS — which is exactly what the owner
named:

  run    `front` (near fist, +dx) and `back` (far fist, -dx, dimmed, drawn behind the body), swinging
         fore-and-aft from the waist at RUN's amplitude, rotated 75 deg.
  swing  `grip_back` welded to the tool, riding the arc. The far hand is not drawn at all, and the body
         is the neutral side frame held still for the whole stroke.

Running while swinging needs all three at once: legs keep the run cycle, the near hand becomes the grip
hand on the arc, the far hand keeps running. The near hand needs no decision — it holds a weapon, so it
goes where the weapon goes. **The far hand is the open question**, hence three variants.

THE TWO CLOCKS
--------------
The sword stroke is 16 poses x 20ms = 320ms; a run cycle is 4 beats x 90ms = 360ms. They do not divide,
so the body is sampled BY TIME against the run's own clock rather than stepped per swing frame — the legs
run through the stroke and come out of it mid-stride, which is the point.

EVERY NUMBER COMES FROM official.py, like build.py's do. `render_animations.py` is NOT used to load
anything: its `frames_dir()` still looks for frames at the outfit root, which predates the 2026-08-06
move into `<outfit>/frames/`, so it silently finds no side bank at all. Only its swing maths is borrowed.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B                                  # noqa: E402  the LIVE loaders (official.py-driven)
import gait                                        # noqa: E402  the APPROVED gait maths, reused as-is
import official as O                               # noqa: E402  the only source of truth
import render_animations as RA                     # noqa: E402  the approved swing rig (maths only)
import review as R                                 # noqa: E402  readable labels

REVIEWS = os.path.join(B.PLAYER, "reviews")
OUT_DIR = "2026-08-14-swing-while-running"

# The far hand, three ways. `amp` scales the approved RUN amplitude for this render only — it does not
# edit official.py's numbers. `hold` freezes the arm at one point of its swing instead of pumping.
VARIANTS = [
    ("A_keeps_running", dict(amp=1.0, hold=None),
     "the off arm keeps its full run pump, unchanged"),
    ("B_half_pump", dict(amp=0.5, hold=None),
     "the off arm pumps at half amplitude - a body bracing against the swing"),
    ("C_held_forward", dict(amp=1.0, hold=1.0),
     "the off arm stops and holds forward for the whole stroke"),
]


def far_fist(sc, body, neutral, hand, beat, cfg, bx, by, p):
    """Just the FAR fist of the run, at beat `beat`.

    Transcribed from `gait.pose_into` — same constants, same helpers, same order (down BEFORE the body,
    dimmed, so it reads as the far side). Only the far one: the near hand is on the weapon.
    """
    ny0, ny1, cx, tw = gait.anchor(neutral)
    bh = ny1 - ny0 + 1
    h, w = body.shape[:2]
    ox, oy = bx - w / 2.0, by - h / 2.0
    wy = ny0 + int((ny1 - ny0) * p["waist"])
    s = cfg["hold"] if cfg["hold"] is not None else math.sin(gait.PHASE[beat % len(gait.PHASE)] * math.pi)
    dx = p["amp"] * cfg["amp"] * tw * s
    dy = -p["ay"] * bh * abs(s)
    far_ang = p["rot"] - p["tilt"] * s             # trailing hand: cuff leans FORWARD (gait.pose_into)
    gait._paste(sc, gait._sz(gait._rot(gait._dim(hand), far_ang), bh, p["ratio"]),
                ox + cx - dx, oy + wy + dy)


def running_swing(bank, hands, tool, cfg):
    """One stroke, swung while running.

    `attack_frames`' inner loop with two changes: the body is resampled per frame off the run cycle, and
    the far fist is drawn behind it. The swing geometry itself is untouched.
    """
    a = O.ANIMATIONS["swing_sword"]
    p = O.GAITS["RUN"]
    neutral = bank[B.NEUTRAL["side"]]
    y0, y1, _, _ = gait.anchor(neutral)
    bh = y1 - y0 + 1
    cell = bh / 2.0
    art0 = RA.S.scale_h(RA.rgba(tool), cell)
    grip = (RA.S.grip_of(art0) + RA.S.DIAG * RA.S.GRIP_EXTRA) * art0.shape[0]
    poses = RA.attack_poses(a["aim"], O.SWINGS[a["motion"]])

    pad = 230
    W, H = neutral.shape[1] + 2 * pad, neutral.shape[0] + 2 * pad
    out, ms = [], []
    for i, (arm, back, reach) in enumerate(poses):
        # BY TIME, not per frame: 20ms swing steps against the run's own 90ms beat.
        beat = int(i * RA.ATK_MS / p["ms"]) % len(gait.CYCLE)
        body = bank[gait.CYCLE[beat] - 1]

        sc = RA.scene(W, H)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        ny0, ny1, cx, _ = gait.anchor(body)
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx = ox + cx + a["shoulder"][0] * cell
        sy = bcy - a["shoulder"][1] * cell

        far_fist(sc, body, neutral, hands["back"], beat, cfg, bx, by, p)
        gait._paste(sc, body, bx, by)

        r = math.radians(arm)
        hx, hy = sx + math.cos(r) * reach * cell, sy - math.sin(r) * reach * cell
        blade = arm + back
        art = RA.S.rot(art0, blade - RA.S.ART_ANGLE)
        rr = math.radians(-(blade - RA.S.ART_ANGLE))
        gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
        gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)
        gait._paste(sc, art, hx - gx, hy - gy)
        gait._paste(sc, gait._sz(RA.S.rot(hands["grip_back"], blade + RA.HAND_PERP), bh,
                                 p["ratio"]), hx, hy)

        out.append(RA.finish(sc))
        ms.append(RA.ATK_MS)
    return RA.crop_union(out), ms


def side_by_side(reels, labels):
    """The three at ONE scale and NATIVE resolution — nothing is downscaled to fit."""
    from PIL import Image, ImageDraw
    font, lh = R.font(R.TITLE_PT), R.text_h(R.TITLE_PT)
    n = max(len(f) for f, _ in reels)
    cw = max(f[0].width for f, _ in reels) + 24
    ch = max(f[0].height for f, _ in reels)
    frames = []
    for i in range(n):
        im = Image.new("RGB", (cw * len(reels), ch + lh + 10), (58, 58, 64))
        d = ImageDraw.Draw(im)
        for k, ((fr, _), lab) in enumerate(zip(reels, labels)):
            d.text((k * cw + 12, 4), lab, fill=R.INK, font=font)
            im.paste(fr[i % len(fr)], (k * cw + 12, lh + 6))
        frames.append(im)
    return frames, reels[0][1]


def build_lab(outfit="bronze"):
    bank = B.load_frames(outfit, "side")
    hands = B.load_hands(outfit)
    tool = os.path.join(B.RES, "Items", O.ANIMATIONS["swing_sword"]["tool"])
    if not os.path.exists(tool):
        raise SystemExit(f"missing tool sprite: {tool}")

    out = os.path.join(REVIEWS, OUT_DIR)
    os.makedirs(out, exist_ok=True)
    reels, labels = [], []
    for name, cfg, note in VARIANTS:
        fr, ms = running_swing(bank, hands, tool, cfg)
        RA.save(fr, ms, os.path.join(out, f"{outfit}_{name}.gif"))
        reels.append((fr, ms))
        labels.append(name.split("_", 1)[1].replace("_", " "))
        print(f"  {name:16s} {note}")

    fr, ms = side_by_side(reels, labels)
    RA.save(fr, ms, os.path.join(out, f"{outfit}_ALL_THREE.gif"))
    print(f"\n  {out.replace('/mnt/c/', 'C:/')}")
    print(f"    {outfit}_ALL_THREE.gif — the three side by side, native size, nothing downscaled")
    print("    a LAB: nothing here is a motion until you pick one and it goes into the approved data")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("outfit", nargs="?", default="bronze")
    build_lab(ap.parse_args().outfit)
