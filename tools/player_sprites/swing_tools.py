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

# tool -> icon, two-handed, and the variants to explore.
# Each variant: (anticipation, [4 strike poses], rest).
TOOLS = {
    "axe": ("axe_copper_icon.png", False, {
        # heavy, continuous, no hover at the top
        "A_round_behind": ((150, 70, 0.44),
                           [(70, 55, 0.54), (0, 30, 0.62), (-70, 5, 0.60), (-125, -15, 0.50)],
                           (-60, 45, 0.44)),
        "B_over_the_top": ((128, 88, 0.42),
                           [(60, 62, 0.52), (-10, 26, 0.62), (-72, -4, 0.62), (-108, -20, 0.54)],
                           (-50, 50, 0.44)),
        "C_full_circle": ((175, 80, 0.46),
                          [(90, 66, 0.54), (0, 42, 0.62), (-90, 18, 0.58), (-175, 0, 0.48)],
                          (-70, 48, 0.44)),
    }),
    "hoe": ("hoe_copper_icon.png", False, {
        # lift a little, strike the ground, PULL back toward the player
        "A_strike_and_pull": ((70, 60, 0.46),
                              [(10, 30, 0.60), (-58, 0, 0.66), (-72, 6, 0.50), (-80, 14, 0.36)],
                              (-30, 45, 0.42)),
        "B_deeper": ((88, 66, 0.48),
                     [(6, 26, 0.62), (-66, -6, 0.70), (-78, 2, 0.52), (-86, 10, 0.34)],
                     (-30, 45, 0.42)),
        "C_short_chop": ((52, 54, 0.44),
                         [(0, 24, 0.58), (-54, 0, 0.62), (-64, 6, 0.48), (-70, 12, 0.38)],
                         (-28, 44, 0.42)),
    }),
    "net": ("small_net_icon.png", False, {
        # fast and wide, and the HOOP leads — so the tool is carried ahead of the arm, not trailing it
        "A_wide_sweep": ((92, -40, 0.50),
                         [(30, -46, 0.60), (-20, -50, 0.66), (-70, -54, 0.62), (-104, -58, 0.54)],
                         (-40, -30, 0.44)),
        "B_quick_flick": ((66, -44, 0.48),
                          [(6, -50, 0.62), (-48, -54, 0.66), (-84, -56, 0.58), (-96, -52, 0.50)],
                          (-30, -30, 0.44)),
        "C_scoop_up": ((-60, -30, 0.46),
                       [(-20, -44, 0.60), (20, -52, 0.66), (60, -58, 0.62), (92, -60, 0.52)],
                       (30, -34, 0.44)),
    }),
    "shovel": ("shovel_copper_icon.png", False, {
        # JAB DOWN then lift like a scoop. Reach does the digging, not rotation.
        "A_jab_and_scoop": ((-40, 20, 0.40),
                            [(-70, 6, 0.56), (-84, 0, 0.72), (-80, 10, 0.60), (-52, 34, 0.46)],
                            (-30, 45, 0.42)),
        "B_deep_jab": ((-30, 24, 0.38),
                       [(-66, 8, 0.58), (-88, -2, 0.78), (-86, 6, 0.66), (-58, 30, 0.48)],
                       (-30, 45, 0.42)),
        "C_dig_and_toss": ((-44, 18, 0.40),
                           [(-76, 4, 0.58), (-88, 0, 0.74), (-50, 26, 0.58), (18, 52, 0.46)],
                           (-28, 46, 0.42)),
    }),
    "spear": ("spear_bronze_icon.png", True, {
        # stabby: the REACH does the work, the angle barely moves
        "A_thrust": ((16, 6, 0.34),
                     [(4, 2, 0.52), (0, 0, 0.78), (0, 0, 0.82), (2, 2, 0.60)],
                     (18, 30, 0.40)),
        "B_long_thrust": ((22, 8, 0.30),
                          [(6, 2, 0.56), (0, 0, 0.88), (0, 0, 0.92), (2, 2, 0.66)],
                          (20, 32, 0.40)),
        "C_double_jab": ((16, 6, 0.34),
                         [(0, 0, 0.74), (4, 4, 0.46), (0, 0, 0.80), (4, 4, 0.56)],
                         (18, 30, 0.40)),
    }),
}


def main():
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing-tools")
    os.makedirs(d, exist_ok=True)
    for f in sorted(os.listdir(d)):
        os.remove(os.path.join(d, f))

    hands, _ = R.load_hands(OUTFIT)
    body = R.load_bank(OUTFIT, "side", 1)[1]
    bh = gait.anchor(body)[1] - gait.anchor(body)[0] + 1
    made = {}

    for tool, (icon, two, variants) in TOOLS.items():
        p = os.path.join(R.RES, "Items", icon)
        if not os.path.exists(p):
            print(f"  SKIP {tool}: {icon} missing")
            continue
        for name, spec in variants.items():
            frames, ms = R.attack_frames(body, hands, p, bh, SIDE, spec=spec, two_handed=two)
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
