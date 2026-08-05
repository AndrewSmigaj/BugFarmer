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
| `anim/swing_sword_down.gif` | `render_animations.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |
| `anim/swing_sword_up.gif` | `render_animations.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |

## ⚠ UNRESOLVED — the side sword swing

Two candidates are sitting in `anim/`, both named `..._CANDIDATE_...` so neither can be mistaken for
settled. **This needs one word from you.**

| file | what it is |
|---|---|
| `anim/swing_sword_side_CANDIDATE_slow_27f.gif` | 27 frames / 270 ms. `arm_swing_frames` + `sword_motion` — arm 128°→−104°, blade 85°→52°, reach 0.60. This is what *"do sword_1h_f4_back85 as the official one, but have it pull back a tad more at the end"* produced. |
| `anim/swing_sword_side_CANDIDATE_quick_12f.gif` | 12 frames / 280 ms. The **frame-budget** version — 1 anticipation, 3 strike with a blade trail, hold on the hit, recovery. What you meant by *"we had clearly switched to a video game much quicker one"*. |

**What happened:** when the quick frame-budget model was adopted, only **facing down and up** were wired
up to it. The side swing was left on the old eased model and I kept describing it as settled. The numbers
show it plainly — down/up are 11f/240ms, the side one is 27f/270ms.

## Not here yet

The other five tools — axe, hoe, net, shovel, spear — are still unsettled. `B_deeper` was picked for the
shovel and is **not yet recorded**, because the wrist geometry underneath it was wrong and got reverted.
They all need redoing once the geometry is right.
