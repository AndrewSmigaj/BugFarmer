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
| `anim/swing_sword.gif` | `render_animations.SWORD_SIDE` via `attack_frames` | 2026-08-04 | *"yes we obviously want the quick candidate"* |
| `anim/swing_sword_down.gif` | `render_animations.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |
| `anim/swing_sword_up.gif` | `render_animations.DOUBLE_BACK` | 2026-08-04 | *"lets do double back for both, the seem good"* |

## Not here yet

The other five tools — axe, hoe, net, shovel, spear — are **still unsettled**, so they are deliberately
NOT in `current/`. They sit in `archive/2026-08-04-unsettled-tools/`, still on the old shoulder-pivot
model. `B_deeper` was picked for the shovel and is **not recorded**, because the wrist geometry underneath
it was wrong and got reverted. They all need redoing once the geometry is right.

The superseded 27-frame eased side sword is in `archive/2026-08-04-superseded-side-sword/`. Nothing is
deleted.
