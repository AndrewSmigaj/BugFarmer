"""motions.py — THE AGREED MOTIONS. This file only ever grows.

Every motion the owner has picked lives here, permanently, with the date and his decision stated in clean
prose (never his words). `render_animations` imports from here; the labs (`swing_tools.py` and friends)
are for exploring, and nothing in a lab is durable.

WHY THIS FILE EXISTS
--------------------
The gifs were being overwritten by each render run, which was fixed with timestamped review folders. The
**specs** — the numbers that define a motion — had exactly the same problem and it went unnoticed: each
new variant was written over the last one in the lab file, so when the owner picked one, the code that
produced it no longer existed and had to be dug out of git history.

Owner direction, 2026-08-04: while the game's animations are being chosen, the candidate motions must be
kept, not thrown away as work moves on.

THE RULE
--------
**A motion that has been picked is COPIED HERE, NEVER EDITED IN PLACE.** Superseding one means adding the
replacement next to it and marking the old one superseded — the numbers behind a shipped animation are not
scratch. Lab variants may be overwritten freely; anything in this file may not.

POSE FORMAT
-----------
`(arm offset from centre, blade angle behind the arm, reach in cells)`, and a spec is
`(anticipation, [4 strike poses], rest)`. `centre` is the direction being attacked — 0 side-on, −90 facing
down, +90 facing up. A cell is half the character's body height.
"""

# ── SWORD ────────────────────────────────────────────────────────────────────────────────────────────
# 2026-08-04 — owner's pick: the quick (frame-budget) candidate.
# Behind the head, past straight down, hand finishing at the hip; the blade unwinds so the tip keeps
# dropping after the arm stops.
SWORD_SIDE = ((120, 88, 0.60),
              [(60, 76, 0.62), (-10, 62, 0.64), (-70, 48, 0.62), (-104, 40, 0.60)],
              (-35, 60, 0.58))

# 2026-08-04 — owner's pick: double-back for both facings, judged good.
# Out across, then whipped back through the other way. Used for facing down AND facing up.
DOUBLE_BACK = ((+70, 66, 0.50),
               [(0, 44, 0.60), (-64, 30, 0.56), (-10, 46, 0.58), (+34, 58, 0.54)],
               (+34, 60, 0.46))

# ── TOOLS, side-on ───────────────────────────────────────────────────────────────────────────────────
# 2026-08-04 — picked by path, from reviews/2026-08-04-swing-tools/
# Owner's pick for the side net: ...1204_8bfd24e_net_A_sweep_and_lift.gif
# Recovered from commit 8bfd24e — it had already been overwritten in the lab file by later variants.
NET_SIDE = ((80, -40, 0.50),
            [(30, -48, 0.62), (-20, -54, 0.66), (-50, -40, 0.62), (-30, -10, 0.58)],
            (40, -30, 0.46))

# Owner's pick for the axe: ...axe_B_high_chop.gif
AXE_SIDE = ((172, 78, 0.42),
            [(95, 56, 0.52), (16, 22, 0.62), (-34, -2, 0.64), (-38, 0, 0.62)],
            (70, 58, 0.44))

# Owner's pick for the side hoe: ...hoe_B_long_drag.gif
HOE_SIDE = ((78, 58, 0.46),
            [(-46, 12, 0.64), (-60, 2, 0.68), (-72, 6, 0.46), (-84, 12, 0.26)],
            (40, 50, 0.44))

# Owner's pick for the shovel: ...shovel_B_deeper.gif
SHOVEL_SIDE = ((-60, 44, 0.32),
               [(-58, 38, 0.52), (-56, 28, 0.76), (-50, 56, 0.74), (-44, 74, 0.68)],
               (-60, 46, 0.32))

# The shovel is gripped partway up the shaft and levered; the second fist sits BEHIND the first, toward
# the butt, which is where the top hand goes.
SHOVEL_PIVOT, SHOVEL_SECOND = 0.34, -0.22

# ── THE LOOKUP `render_animations.build()` READS ─────────────────────────────────────────────────────
# A tool absent from TOOL_SIDE is NOT RENDERED and is reported as a gap. That is deliberate: shipping a
# superseded motion silently is how the agreed tool swings were overwritten by every re-render on
# 2026-08-05, because the picks lived here and `build()` never looked at them.
TOOL_SIDE = {
    "net": NET_SIDE,
    "axe": AXE_SIDE,
    "hoe": HOE_SIDE,
    "shovel": SHOVEL_SIDE,
}
TOOL_TWO_HANDED = {"shovel": True}
TOOL_PIVOT = {"shovel": SHOVEL_PIVOT}
TOOL_SECOND = {"shovel": SHOVEL_SECOND}
TOOL_SCALE = {"spear": 1.9}      # SPEAR_SCALE, defined below; the motion is still unsettled


# ── NOT YET AGREED ───────────────────────────────────────────────────────────────────────────────────
# spear (side)                  — length is settled at 1.9 cells, the motion is not
# axe / hoe / net / shovel      — FACING DOWN and FACING UP do not exist at all; only the sword has them
SPEAR_SCALE = 1.9
