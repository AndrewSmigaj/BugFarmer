"""swing_tools.py — axe / hoe / net / shovel / spear on the settled attack model. FREE, no API.

  python3 tools/player_sprites/swing_tools.py

Writes into `tools/_generated/player/reviews/<date>-swing-tools/` (cleared each run).

The sword is settled: the HAND travels an arc, the blade sits at an angle behind the arm, the tool
follows the hand, and the whole thing runs on a frame budget (1 anticipation / 4 strike with a trail /
2 hold / 5 recovery = 0.24s). The other five tools still run the OLD shoulder-pivot motion — the one
where the fist parks beside the shoulder and spins in place. These rebuild them on the new model.

ONE MOTION PER TOOL. They are not one arc with different constants — that was the code smell the owner
caught: *"sword is not an axe swing"*. His notes on each, from `APPROVED/DECISIONS.md` and the sessions:

  AXE     "swing behind over then down in front ... like a real axe", "literally swing all the way
          around", and it must NOT hover in the cocked-back position.
  HOE     "lift a little, strike the ground and PULL" — not "someone whipping the ground with a stick".
  NET     the hoop is the OPENING and it should LEAD; faster, and swing across more.
  SHOVEL  "downward stabbing then up like a scoop" — it must JAB DOWN, not wave around.
  SPEAR   "stabby", two-handed, and the reach does the work rather than the rotation.

Poses are (arm offset from centre, blade behind arm, reach in cells); `centre` is 0 for the side view,
so an offset of 0 points straight forward. The arc must pass THROUGH the space being worked.
"""
import datetime
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import render_animations as R                            # noqa: E402
import swing_lab as S                                    # noqa: E402

OUTFIT = "bronze"
BG = (150, 160, 150)
SIDE = dict(centre=0.0, sh=(0.06, 0.40), behind=False)

# tool -> (icon, two-handed, LENGTH relative to a cell, variants)
#
# ⚠ THESE ARE NOT SWINGS WITH DIFFERENT ARCS. Owner: "you arent thinking of the tools right - you are
# treating them all like swords you swing in different ways... do you sit there bashing the ground with
# a shovel? do you?"  No. Each tool has a VERB, and the verb decides which channel carries the motion:
#
#   axe     CHOP    - a big arc that BITES AND STOPS. A real axe does not follow through past the wood.
#   hoe     TILL    - chop in, then DRAG back toward you. The drag is the working stroke, not the chop.
#   net     CATCH   - sweep hoop-first, then LIFT to enclose. It ends by scooping up, not by passing through.
#   shovel  DIG     - push the blade IN, LEVER the handle back while the blade stays planted, lift, toss.
#                     Not a strike at all. Nothing about digging is a swing.
#   spear   THRUST  - cocked back at the body, then driven forward. REACH is the whole motion.
#
# Reach shrinking while the tool stays low IS the drag/lever. Reach growing with a still angle IS the
# thrust. Rotation is the wrong channel for both, which is why they read as waving before.

TOOL_SCALE = {"spear": 1.9}
# pivot: where along the shaft the tool sits on the driving hand (0 = the butt, like a sword).
# second: where the other fist sits relative to that, along the shaft. NEGATIVE = behind, toward the butt.
TOOL_PIVOT = {"shovel": 0.34}
TOOL_SECOND = {"shovel": -0.22}     # A SPEAR IS NOT A SWORD LENGTH. Asked for three times; never applied.

TOOLS = {
    "axe": ("axe_copper_icon.png", False, {
        "A_bite_and_stick": ((150, 70, 0.44),
                             [(80, 50, 0.54), (10, 20, 0.62), (-28, 0, 0.62), (-32, 2, 0.60)],
                             (60, 55, 0.44)),
        "B_high_chop": ((172, 78, 0.42),
                        [(95, 56, 0.52), (16, 22, 0.62), (-34, -2, 0.64), (-38, 0, 0.62)],
                        (70, 58, 0.44)),
    }),
    "hoe": ("hoe_copper_icon.png", False, {
        # chop in, then DRAG: the reach shrinks while the tool stays low
        "A_chop_and_drag": ((70, 55, 0.46),
                            [(-50, 10, 0.62), (-62, 0, 0.66), (-70, 5, 0.50), (-78, 10, 0.34)],
                            (40, 50, 0.44)),
        "B_long_drag": ((78, 58, 0.46),
                        [(-46, 12, 0.64), (-60, 2, 0.68), (-72, 6, 0.46), (-84, 12, 0.26)],
                        (40, 50, 0.44)),
    }),
    "net": ("small_net_icon.png", False, {
        # Hoop LEADS (negative back). START LOW AND END LOW — you scoop a bug up off the ground, your
        # hand does not finish beside your face. Owner: "when you sweep up a bug does your hand end up
        # near your face?" The hand stays below the shoulder line for the whole motion, and the hoop is
        # angled UP more so the opening faces where the bug is.
        "A_low_scoop": ((-78, -34, 0.46),
                        [(-64, -52, 0.60), (-46, -62, 0.68), (-34, -58, 0.64), (-38, -48, 0.58)],
                        (-74, -32, 0.44)),
        "B_wider": ((-84, -30, 0.44),
                    [(-66, -50, 0.62), (-42, -64, 0.72), (-26, -60, 0.68), (-34, -50, 0.60)],
                    (-78, -30, 0.44)),
    }),
    "shovel": ("shovel_copper_icon.png", True, {
        # HOW A SHOVEL IS ACTUALLY HELD AND USED. Two corrections, both mine:
        #
        # 1. YOU DO NOT HOLD IT UP NEAR YOUR FACE. The hands stay LOW — waist to hip — with the blade
        #    below them. Mine had the hands at chest height because the arm aimed near horizontal from a
        #    shoulder that sits at 30% down the body.  Now the ARM aims steeply down (about -55 deg) so
        #    the hands sit at 50-57% down, and the BLADE is brought back up to a shallow forward angle by
        #    a large `back` — that is what "hands low, blade forward into the block" looks like.
        #
        # 2. IT IS A LEVER, NOT A BATTERING RAM. Two hands at two points on the shaft; the LOWER hand
        #    barely moves and the top hand swings. So the strike drives the blade in with reach, and then
        #    the last frames change the ANGLE with almost no hand travel — that rotation about the low
        #    hand IS the lever. `pivot` puts the tool on the driving hand partway up the shaft and
        #    `second` (negative) puts the other fist BEHIND it, toward the butt, where the top hand goes.
        "A_lever_dig": ((-58, 42, 0.34),
                        [(-56, 38, 0.50), (-54, 32, 0.68), (-50, 55, 0.66), (-46, 70, 0.62)],
                        (-58, 44, 0.34)),
        "B_deeper": ((-60, 44, 0.32),
                     [(-58, 38, 0.52), (-56, 28, 0.76), (-50, 56, 0.74), (-44, 74, 0.68)],
                     (-60, 46, 0.32)),
    }),
    "spear": ("spear_bronze_icon.png", True, {
        # COCKED BACK at the body, then driven forward. Reach is the entire motion.
        #
        # ⚠ AIM IT BELOW HORIZONTAL. The shoulder pivot sits at ~30% down the body, which IS the shoulder
        # line — measured off the sprite's width profile, where the helmet ends and the torso starts. But
        # thrusting horizontally FROM there leaves the hands at shoulder height, up by his head. A spear
        # held two-handed sits at chest/waist. -20 deg drops the hands to about 45% down the body, which
        # is where they belong. Owner: "the hands need to come down a bunch more they are near the head".
        "A_thrust": ((-14, 0, 0.15),
                     [(-18, 0, 0.40), (-20, 0, 0.80), (-20, 0, 1.00), (-20, 0, 0.94)],
                     (-14, 10, 0.28)),
        "B_lower": ((-18, 0, 0.12),
                    [(-24, 0, 0.42), (-26, 0, 0.84), (-26, 0, 1.06), (-26, 0, 0.98)],
                    (-18, 12, 0.26)),
    }),
}


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
    d = out_dir("swing-tools")

    hands, _ = R.load_hands(OUTFIT)
    body = R.load_bank(OUTFIT, "side", 1)[1]
    bh = gait.anchor(body)[1] - gait.anchor(body)[0] + 1
    made = {}

    for tool, (icon, two, variants) in TOOLS.items():
        scale = TOOL_SCALE.get(tool, 1.0)
        p = os.path.join(R.RES, "Items", icon)
        if not os.path.exists(p):
            print(f"  SKIP {tool}: {icon} missing")
            continue
        for name, spec in variants.items():
            frames, ms = R.attack_frames(body, hands, p, bh, SIDE, spec=spec, two_handed=two,
                                         scale=scale, pivot=TOOL_PIVOT.get(tool, 0.0),
                                         second=TOOL_SECOND.get(tool, 0.17))
            out = os.path.join(d, f"{tool}_{name}.gif")
            frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0)
            made.setdefault(tool, []).append((name, frames))
            print(f"  {os.path.basename(out):30} {len(frames)}f")

    for tool, rows in made.items():
        W = max(f[0].size[0] for _, f in rows)
        H = max(f[0].size[1] for _, f in rows)
        mid = R.ATK_ANTIC + R.ATK_STRIKE // 2
        sheet = Image.new("RGB", (len(rows) * W, 2 * (H + 22)), (28, 28, 34))
        dr = ImageDraw.Draw(sheet)
        for k, (name, frames) in enumerate(rows):
            for r, (idx, tag) in enumerate(((mid, "mid"), (min(R.ATK_ANTIC + R.ATK_STRIKE,
                                                              len(frames) - 1), "end of strike"))):
                bg = Image.new("RGB", (W, H), BG)
                im = frames[min(idx, len(frames) - 1)]
                bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
                sheet.paste(bg, (k * W, r * (H + 22) + 22))
                dr.text((k * W + 6, r * (H + 22) + 5), f"{tool} {name} {tag}", fill=(255, 220, 140))
        sheet.save(os.path.join(d, f"ALL_{tool}.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")


if __name__ == "__main__":
    main()
