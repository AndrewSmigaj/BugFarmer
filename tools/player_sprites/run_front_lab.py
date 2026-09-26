"""run_front_lab.py — a REAL pose for the camera-facing run. A lab. FREE, no API.

  python3 tools/player_sprites/run_front_lab.py [outfit]

Owner, 2026-08-14: *"the only thing I don't like is run_front, it should have more of a fist pumping (so
higher, with fists that get bigger and smaller)… that's just not running with hands down by the side."*

He is describing a defect that is in the data: `official.GAITS["FRONT_RUN"]` is byte-identical to
`FRONT` apart from `ms` — the front run IS the front walk played faster. That is the same mistake the
side run already fixed ("running the walk pose fast reads as flapping"); the camera-facing one never got
its own pose.

TWO THINGS THE OWNER ASKED FOR
------------------------------
  HIGHER   the fists pump around chest/shoulder height, not down at the hip (`row` 0.62 today).
  DEPTH    "fists that get bigger and smaller" — the fist coming toward the camera grows and the one
           going back shrinks. Nothing else in the pipeline does this; it is what sells a run TOWARD
           the viewer, where the arms travel mostly in Z and a purely up-down motion reads as flapping.

⚠ THIS IS A LAB, AND THE PLACEMENT MATHS IS TRANSCRIBED FROM `gait.walk_front_into` ON PURPOSE.
`gait.py` says there is exactly ONE camera-facing walk implementation and not to copy it — correct, and
this must not survive as a second one. If a variant is picked, the pulse goes INTO `gait.walk_front_into`
and its numbers into `official.GAITS`; this file is then dead. Two live copies is what put palms-out in
the game for a week.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B                                  # noqa: E402  the live loaders
import gait                                        # noqa: E402  approved helpers + phase
import official as O                               # noqa: E402  the only source of truth
import render_animations as RA                     # noqa: E402  scene/finish/save
import review as R                                 # noqa: E402  readable labels

OUT_DIR = "2026-08-14-run-front-pump"

# row  height of the pump, as a fraction down the figure (0.62 = today's hip, 0.42 = chest)
# gap  distance out from the body edge; NEGATIVE puts the fists over the torso, in front of the body
# dx/dy travel per beat, as a fraction of body span      pulse  how much the fists grow/shrink in Z
# Owner picked BIG REACH as the closest, 2026-08-14, and asked for three variants of it plus three
# fresh ideas. The reach three each move ONE axis off the original so the comparison stays legible.
BIG_REACH = dict(row=0.46, gap=0.04, dx=0.08, dy=0.30, pulse=0.22)

# Owner, 2026-08-14, on the first six: *"they cant go that high, it clips into the shoulders… they should
# be slightly wider than big reach and slightly lower - the other ones are just ridiculous."* So the high
# and the exotic ones are gone. These three sit around big reach, wider and lower, and differ only in how
# much of the travel is trimmed off the TOP of the arc — which is what was hitting the pauldron.
VARIANTS = [
    ("BIG_REACH", BIG_REACH, "the anchor, unchanged", "reach"),
    ("W1_wider_lower", dict(BIG_REACH, row=0.50, gap=0.07),
     "wider and lower, same travel", "reach"),
    ("W2_wider_lower_short", dict(BIG_REACH, row=0.50, gap=0.07, dy=0.24),
     "same, with the top of the arc trimmed so it clears the shoulder", "reach"),
    ("W3_widest_lowest", dict(BIG_REACH, row=0.53, gap=0.09, dy=0.26),
     "a touch further again in both directions", "reach"),
]

PICKED = "W3_widest_lowest"                        # owner, 2026-08-14: "we will go with wisdest lowest"


def pump_frames(bank, hands, cfg):
    """One 4-beat cycle. Transcribed from `gait.walk_front_into`, plus the depth pulse.

    Draw order is deliberate: the SHRINKING fist goes down before the body so it can pass behind the
    torso when `gap` is negative, and the GROWING one after it. That is what makes the size change read
    as an arm travelling in depth instead of a sprite being scaled.
    """
    p = O.GAITS["FRONT_RUN"]
    neutral = bank[B.NEUTRAL["front"]]
    ny0, ny1, _, _ = gait.anchor(neutral)
    bh = ny1 - ny0 + 1
    hand = hands["side"]                                    # the profile fist, as the front walk uses
    W, H = bank[0].shape[1] + 2 * RA.PAD, bank[0].shape[0] + RA.PAD
    out = []
    for beat in range(len(gait.CYCLE)):
        body = bank[gait.CYCLE[beat] - 1]
        sc = RA.scene(W, H)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2
        row, lx, rx = gait._edges(body, cfg["row"])
        span = rx - lx
        s = gait.FRONT_PHASE[beat % len(gait.FRONT_PHASE)]
        gap = span * cfg["gap"]

        # right hand forward when s > 0: it rises, and grows as it comes at the camera
        pairs = [
            (1.0 - cfg["pulse"] * s, hand[:, ::-1],         # LEFT is the mirrored one (gait.py)
             ox + lx - gap - s * span * cfg["dx"] * cfg.get("cross", 1.0),
             oy + row - s * span * cfg["dy"]),
            (1.0 + cfg["pulse"] * s, hand,
             ox + rx + gap + s * span * cfg["dx"], oy + row + s * span * cfg["dy"]),
        ]
        # BOTH fists go in FRONT of the body, as `gait.walk_front_into` draws them. Putting the smaller
        # one behind the body instead lost it entirely at chest height, where the torso is widest — the
        # size change has to carry the depth on its own.
        gait._paste(sc, body, bx, by)
        pairs.sort(key=lambda t: t[0])                      # smaller first, so the near fist is on top
        for scale, art, hx, hy in pairs:
            gait._paste(sc, gait._sz(art, bh, p["ratio"] * scale), hx, hy)
        out.append(RA.finish(sc))
    return out, p["ms"]


def side_by_side(reels, labels):
    """All of them at ONE scale and NATIVE resolution — nothing downscaled."""
    from PIL import Image, ImageDraw
    font, lh = R.font(R.TITLE_PT), R.text_h(R.TITLE_PT)
    cw = max(f[0].width for f in reels) + 24
    ch = max(f[0].height for f in reels)
    frames = []
    for i in range(len(reels[0])):
        im = Image.new("RGB", (cw * len(reels), ch + lh + 10), (58, 58, 64))
        d = ImageDraw.Draw(im)
        for k, (fr, lab) in enumerate(zip(reels, labels)):
            d.text((k * cw + 12, 4), lab, fill=R.INK, font=font)
            im.paste(fr[i % len(fr)], (k * cw + 12, lh + 6))
        frames.append(im)
    return frames


def back_check(outfit, bank, hands, out, picked):
    """The picked pose on the BACK bank, which shares `FRONT_RUN` with the front one.

    The pulse sign is the open question. Facing the camera, the arm swinging forward comes TOWARD you and
    grows. Running away, that same arm is going away from you, so it should shrink — the depth cue
    inverts even though the numbers are shared. Both are rendered rather than assumed.
    """
    reels, labels = [], []
    now = B._gait_front_frames(bank, bank[B.NEUTRAL["back"]], hands, O.GAITS["FRONT_RUN"])
    RA.save(now, O.GAITS["FRONT_RUN"]["ms"], os.path.join(out, f"{outfit}_back_CURRENT.gif"))
    reels.append(now)
    labels.append("current")
    for tag, cfg in (("same_pulse", picked),
                     ("flipped_pulse", dict(picked, pulse=-picked["pulse"]))):
        fr, ms = pump_frames(bank, hands, cfg)
        RA.save(fr, ms, os.path.join(out, f"{outfit}_back_{tag}.gif"))
        reels.append(fr)
        labels.append(tag.replace("_", " "))
    RA.save(side_by_side(reels, labels), ms, os.path.join(out, f"{outfit}_BACK.gif"))
    print(f"    {outfit}_BACK.gif — current, then the picked pose with the pulse both ways")


def build_lab(outfit="bronze"):
    bank = B.load_frames(outfit, "front")
    hands = B.load_hands(outfit)
    out = os.path.join(B.PLAYER, "reviews", OUT_DIR)
    os.makedirs(out, exist_ok=True)

    # today's run_front, unchanged, so the options are judged against what is actually in the game
    ms = O.GAITS["FRONT_RUN"]["ms"]
    now = B._gait_front_frames(bank, bank[B.NEUTRAL["front"]], hands, O.GAITS["FRONT_RUN"])
    RA.save(now, ms, os.path.join(out, f"{outfit}_CURRENT.gif"))

    groups = {}
    for name, cfg, note, group in VARIANTS:
        groups.setdefault(group, ([now], ["current"]))
        fr, ms = pump_frames(bank, hands, cfg)
        RA.save(fr, ms, os.path.join(out, f"{outfit}_{name}.gif"))
        groups[group][0].append(fr)
        groups[group][1].append(name.split("_", 1)[-1].replace("_", " "))
        print(f"  {name:18s} {note}")

    for group, (reels, labels) in groups.items():
        RA.save(side_by_side(reels, labels), ms, os.path.join(out, f"{outfit}_{group.upper()}.gif"))

    picked = next(cfg for name, cfg, _, _ in VARIANTS if name == PICKED)
    back_check(outfit, B.load_frames(outfit, "back"), hands, out, picked)
    print(f"\n  {out.replace('/mnt/c/', 'C:/')}")
    for group, (reels, _) in groups.items():
        print(f"    {outfit}_{group.upper()}.gif — current, then {len(reels) - 1} options")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("outfit", nargs="?", default="bronze")
    build_lab(ap.parse_args().outfit)
