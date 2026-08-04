"""swing_facings.py — sword swings for FACING DOWN (toward camera) and FACING UP (away). FREE, no API.

  python3 tools/player_sprites/swing_facings.py

Writes options into `tools/_generated/player/reviews/<date>-swing-facings/`.

The side-on swing is settled (`render_animations.sword_motion`, 2026-08-04). These two are the same
model — the hand travels an arc, the blade sits at a fixed angle behind the arm, the tool follows —
re-aimed for the other two views.

WHAT IS DIFFERENT PER FACING, and why it is not just the side swing rotated
--------------------------------------------------------------------------
* THE SHOULDER MOVES. `FACINGS` in `swing_lab.py` has it at (0.06, 0.40) side-on but (0.10, 0.10)
  front and (0.10, 0.22) away. Pretending it is in the same place put the hand at face height in the
  front view — owner: "the face down the hand is too high, it holds it like face height with the tool
  straight down the hand should be lower".
* FACING AWAY, THE WEAPON IS BEHIND HIM. Drawn in front it covers his back.
* FACING DOWN, THE SWING MUST STOP IN FRONT of him rather than carry all the way through — owner: "the
  hoe in the face down view needs to stop in front of the user not swing all the way down". Side-on the
  arm carries past straight down to the hip; here that would bury the blade in his own legs.

Angle convention, as everywhere else: 0 = screen right, 90 = up, -90 = straight down.
"""
import datetime
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import render_animations as R                            # noqa: E402
import swing_lab as S                                    # noqa: E402

OUTFIT, TOOL = "bronze", "sword"
BG = (150, 160, 150)

# From swing_lab.FACINGS — cell units offset from body centre, +x forward / +y up.
SH_FRONT = (0.10, 0.10)
SH_BACK = (0.10, 0.22)


def _mk(start, end, back_start, back_end, reach):
    def f(t):
        th = start + (end - start) * R._ease_in_out(t)
        back = back_start + (back_end - back_start) * R._ease_in(t)
        return th, reach, back
    return f


# ⚠ THE BLADE-BACK ANGLE MUST UNWIND FURTHER WHEN THE ARM TRAVELS LESS.
# Side-on the arm carries to -104, so a blade held 52 behind it ends at -52 — pointing down, correct.
# Facing down the arm stops around -34 (it must not carry through into his own legs), and 52 behind that
# is +18 — the tip ends UP IN THE AIR at the end of a downward swing. First pass did exactly that.
# So these end with far less blade-back than the side view.

# FACING DOWN — he faces us. The blade comes down across the front of his body and STOPS in front,
# never carrying through to the hip the way the side view does.
FRONT = [
    ("F1_across", _mk(118, -34, 85, 5, 0.52)),      # down across, tip finishing low
    ("F2_high_stop", _mk(110, -20, 85, -15, 0.48)),  # stops higher, blade unwinds harder to point down
    ("F3_lower", _mk(125, -50, 85, 20, 0.55)),       # carries a little further down
]

# FACING AWAY — his back to us, weapon drawn BEHIND him.
BACK = [
    ("B1_across", _mk(118, -40, 85, 10, 0.52)),
    ("B2_over_the_top", _mk(140, -70, 85, 30, 0.50)),  # over the shoulder, straight down
    ("B3_shallow", _mk(96, -20, 85, -10, 0.46)),       # shallower, stays high
]


def render(kind, name, fn, two_handed):
    hands, _ = R.load_hands(OUTFIT)
    bank = R.load_bank(OUTFIT, "front" if kind == "front" else "back", 0)
    body = bank[0]
    bh = gait.anchor(body)[1] - gait.anchor(body)[0] + 1
    icon = os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])
    return R.arm_swing_frames(body, hands, icon, bh, two_handed=two_handed, motion=fn, pad=210,
                              shoulder=SH_FRONT if kind == "front" else SH_BACK,
                              behind=(kind == "back"))


def main():
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing-facings")
    os.makedirs(d, exist_ok=True)
    made = []
    for kind, variants in (("front", FRONT), ("back", BACK)):
        for name, fn in variants:
            for two in (False, True):
                frames, ms = render(kind, name, fn, two)
                lbl = "2h" if two else "1h"
                p = os.path.join(d, f"sword_{kind}_{lbl}_{name}.gif")
                frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0)
                made.append((f"{kind} {lbl} {name}", frames))
                print(f"  {os.path.basename(p):40} {len(frames)}f")

    for tag in ("1h", "2h"):
        rows = [m for m in made if f" {tag} " in m[0]]
        W = max(f[0].size[0] for _, f in rows)
        H = max(f[0].size[1] for _, f in rows)
        sheet = Image.new("RGB", (len(rows) * W, H + 22), (28, 28, 34))
        dr = ImageDraw.Draw(sheet)
        for k, (lbl, frames) in enumerate(rows):
            im = frames[int(len(frames) * 0.78)]
            bg = Image.new("RGB", (W, H), BG)
            bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
            sheet.paste(bg, (k * W, 22))
            dr.text((k * W + 6, 6), lbl, fill=(255, 220, 140))
        sheet.save(os.path.join(d, f"ALL_{tag}.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")
    return d


if __name__ == "__main__":
    main()
