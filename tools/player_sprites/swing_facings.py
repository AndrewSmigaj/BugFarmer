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


# ⚠⚠ THIS IS A GAME. THE SWING HAS TO COVER WHAT IT HITS.
# Owner, 2026-08-04: "when you strike something below you while facing down it means being able to strike
# something below you, all your looking down ones are pretty much the same thing as the sideways ones".
#
# Facing DOWN, the player is attacking the tile SOUTH of him — which is straight DOWN THE SCREEN. So the
# blade must travel down-screen and finish with its TIP PAST HIS FEET, covering that tile. A swing that
# sweeps out to the side is cosmetically a front-facing sprite doing the sideways attack; it covers
# nothing below him and is useless as an attack.
#
# Facing UP, the same in reverse: the blade must finish ABOVE HIS HEAD, covering the tile NORTH of him.
#
# This is why the blade ends at 0 behind the arm in these — the blade CONTINUES the arm, pointing straight
# down (or straight up), which is what puts the tip out past the body.

# THESE ARE THEIR OWN MOTIONS, NOT THE SIDE SWING RE-AIMED.
# Owner, 2026-08-04: "you are starting with the sideways swing first and then trying to force it into
# different melds, the swing will be different when facing down and up, and it also needs to finish the
# swing, so its weird you are like so obsessed with the sideways swing".
#
# The side swing is one monotonic sweep from behind the head to the hip. Facing the camera that is the
# wrong shape twice over: the arc happens in a different plane, and a monotonic sweep STOPS DEAD at the
# bottom instead of following through. So each of these is written in three phases:
#
#   RAISE    lift the blade clear, wind up
#   STRIKE   fast, through the tile being attacked
#   FINISH   carry PAST the contact point and settle - the swing finishes rather than freezing
#
# `phase(t, cuts, keys)` interpolates arm angle / blade-behind-arm across those phases.


def phase(t, cuts, arm, back, reach, eases):
    """Piecewise motion. `cuts` are the phase boundaries; arm/back have len(cuts)+1 keyframes."""
    lo = 0.0
    for i, hi in enumerate(list(cuts) + [1.0]):
        if t <= hi or i == len(cuts):
            u = 0.0 if hi <= lo else min(1.0, max(0.0, (t - lo) / (hi - lo)))
            u = eases[i](u)
            return (arm[i] + (arm[i + 1] - arm[i]) * u,
                    reach,
                    back[i] + (back[i + 1] - back[i]) * u)
        lo = hi
    return arm[-1], reach, back[-1]


_OUT, _IN, _IO = R._ease_in_out, R._ease_in, R._ease_in_out


def down_swing(raise_to, strike_to, finish_to, reach, back_hi=85, back_lo=-6, back_end=34):
    """FACING DOWN. Raise beside the head, strike down through the tile below, follow through and settle."""
    def f(t):
        return phase(t, (0.30, 0.64),
                     arm=[-55, raise_to, strike_to, finish_to],
                     back=[back_hi, back_hi, back_lo, back_end],
                     reach=reach, eases=[_OUT, _IN, _OUT])
    return f


def up_swing(wind_to, strike_to, finish_to, reach, back_hi=85, back_lo=4, back_end=30):
    """FACING UP. Wind down in front, strike up through the tile above, carry over and settle.

    ⚠ The FINISH has to move the blade somewhere VISIBLY DIFFERENT from the strike. First pass took the
    arm past vertical while unwinding the blade by the same amount, so blade = arm + back stayed pinned
    near 90 and the last three frames were identical — the swing froze at the top instead of finishing.
    Carrying the arm over AND letting the blade fall past vertical is what makes it read as follow-through.
    """
    def f(t):
        return phase(t, (0.30, 0.64),
                     arm=[20, wind_to, strike_to, finish_to],
                     back=[back_hi, back_hi, back_lo, back_end],
                     reach=reach, eases=[_OUT, _IN, _OUT])
    return f


# FACING DOWN — attacking the tile below. The tip must land PAST HIS FEET, then the swing finishes.
FRONT = [
    ("F1_overhead", (0.26, 0.12), down_swing(112, -84, -52, 0.52)),
    ("F2_high_raise", (0.30, 0.14), down_swing(132, -78, -44, 0.56)),
    ("F3_tight", (0.22, 0.10), down_swing(96, -90, -60, 0.46)),
]

# FACING UP — attacking the tile above. The tip must land ABOVE HIS HEAD, then the swing finishes.
# Weapon draws BEHIND him.
BACK = [
    ("B1_uppercut", (0.26, 0.22), up_swing(-58, 92, 142, 0.52)),
    ("B2_deep_wind", (0.30, 0.22), up_swing(-74, 86, 150, 0.56)),
    ("B3_tight", (0.22, 0.22), up_swing(-44, 96, 136, 0.46)),
]


def render(kind, name, sh, fn, two_handed):
    hands, _ = R.load_hands(OUTFIT)
    bank = R.load_bank(OUTFIT, "front" if kind == "front" else "back", 0)
    body = bank[0]
    bh = gait.anchor(body)[1] - gait.anchor(body)[0] + 1
    icon = os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])
    return R.arm_swing_frames(body, hands, icon, bh, two_handed=two_handed, motion=fn, pad=210,
                              shoulder=sh, behind=(kind == "back"))


def out_dir(tag):
    """A NEW folder per run — timestamped. Nothing is ever overwritten.

    Every lab script used to write to one folder named for the day and clear it each run, so re-running
    destroyed the previous attempt. That means when the owner says "it was mostly ok before you changed
    something", the file he was looking at no longer exists, and I cannot even tell him which version it
    was because the filenames were reused. Owner: "can you please stop overwriting files i cant show you
    the old one".

    A dated batch folder per run is exactly the scratchpad convention already written into the
    player-sprites skill — which I designed and then did not apply to my own output.
    """
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    d = os.path.join(R.PLAYER, "reviews", f"{stamp}-{tag}")
    os.makedirs(d, exist_ok=True)
    return d


def main():
    # A CLEAN FOLDER EVERY RUN. Re-running with renamed variants used to leave every dead attempt on
    # disk beside the live ones — 56 gifs in one folder, of which 12 were current. Owner: "all i see in
    # here is complete crap... so which ones are you talking about". Anything this script wrote last run
    # is regenerable in one command, so it goes; nothing else in the folder is touched.
    d = out_dir("swing-facings")
    made = []
    for kind, variants in (("front", FRONT), ("back", BACK)):
        for name, sh, fn in variants:
            for two in (False, True):
                frames, ms = render(kind, name, sh, fn, two)
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
            im = frames[-1]        # the END pose - does the tip actually reach past him?
            bg = Image.new("RGB", (W, H), BG)
            bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
            sheet.paste(bg, (k * W, 22))
            dr.text((k * W + 6, 6), lbl, fill=(255, 220, 140))
        sheet.save(os.path.join(d, f"ALL_{tag}.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")
    return d


if __name__ == "__main__":
    main()
