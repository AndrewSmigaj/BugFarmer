# bronze — current

**Bronze is the reference outfit.** Every animation is designed on bronze, then the same motion is applied
to the other 21 with their own gauntlets. So this folder is where the agreed animations live — not a
review folder, not a scratch render.

**The rule from now on: the moment you say "this one", it is copied here and a row is added below, the
same day.** Everything in `reviews/` is exploration and gets regenerated or thrown away; nothing there is
safe. Losing an agreed animation because it only ever existed in a review folder is what wasted
2026-08-04.

`anim/` here is NOT derived output — the **motion is the decision**. The gif is the record of it, and the
constants that produce it are named in the table so it can be rebuilt from code alone.

## Agreed

| file | motion, in code | agreed | your words |
|---|---|---|---|
| `anim/walk_side.gif` | `gait.WALK` | 2026-07-29 | *"walk b is fine"* |
| `anim/walk_front.gif` | `gait.FRONT` | 2026-07-29 | *"first for walking forward gait_front_d3_bigger.gif is great"* |
| `anim/walk_back.gif` | `gait.FRONT` applied to the back frames | 2026-08-02 | delivered against *"so we have forward and sideways might as well finish with back"* |
| `anim/run_side.gif` | `gait.RUN` | 2026-07-29 | *"RUN_r75.gif is fine, looks the best"* |
| `anim/run_front.gif` | `gait.FRONT` at run speed | — | ⚠ **not designed** — the walk motion played faster |
| `anim/run_back.gif` | `gait.FRONT` at run speed | — | ⚠ **not designed** — the walk motion played faster |
| `anim/swing_sword.gif` | `motions.SWORD_SIDE` via `attack_frames` | 2026-08-04 | *"yes we obviously want the quick candidate"* |
| `anim/swing_sword_down.gif` | `motions.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |
| `anim/swing_sword_up.gif` | `motions.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |
| `anim/swing_net.gif` | `motions.NET_SIDE` | 2026-08-04 | *"this net for the side will work: ...1204_8bfd24e_net_A_sweep_and_lift.gif"* |
| `anim/swing_axe.gif` | `motions.AXE_SIDE` | 2026-08-04 | *"...axe_B_high_chop.gif for the axe"* |
| `anim/swing_hoe.gif` | `motions.HOE_SIDE` | 2026-08-04 | *"...hoe_B_long_drag.gif for the side hoe"* |
| `anim/swing_shovel.gif` | `motions.SHOVEL_SIDE` | 2026-08-04 | *"...shovel_B_deeper.gif for the shovel"* |

## Not here yet

**The SPEAR side motion** is not settled. Its length is (1.9 cells, `motions.SPEAR_SCALE`); the motion is
not. It sits in `archive/2026-08-04-unsettled-tools/`.

**NO TOOL HAS A FACING-DOWN OR FACING-UP VERSION.** Only the sword does. Axe, hoe, net, shovel and spear
exist side-on only — the down/up work was never started for them.

Every agreed motion is defined in `tools/player_sprites/motions.py`, which only ever grows. Lab files
(`swing_tools.py` and friends) are scratch and get overwritten; nothing there is durable.

The superseded 27-frame eased side sword is in `archive/2026-08-04-superseded-side-sword/`. Nothing is
deleted.
