# Bronze hands — decided 2026-08-06, and the two outfits that followed

All settled. Kept because these are the images the decisions were made from.

## What was decided

| | decision |
|---|---|
| **Fist size** | walk stays at **0.17** — the owner kept the current hand sizes. The earlier complaint that the hands were far too big was about the RUN, which has its own larger ratio (0.19) |
| **Wrist direction** | the cuff leans **toward the body**, because that is where the arm comes from |
| **Palms** | turn **in** for the camera-facing walk |

Owner approval (2026-08-06): all three fixes accepted and made official.

## The sheets

**Decision sheets** — what was chosen from:
- `FIX_1_wrist.png` — before/after. Both signs had been inverted, so the forward fist's wrist sat
  *further forward than the fist* and the arm read as reaching around from the far side.
- `FIX_2_palms.png` — before/after.
- `FIX_3_run_size.png` — run at 0.19 / 0.17 / 0.15.
- `PALMS_compare.png` + `PALMS_A..D.gif` — all four mirror combinations.
- `HAND_SIZES.png` — both views at three ratios, with the measurements.
- `WRIST_current.png` — the two hands isolated per beat, which is what made the inverted sign visible.

**Result** — what came out:
- `GAUNTLETS_all_three.png` — bronze, fireant, blackant. Same five poses, different materials.
- `CONSISTENCY_walk_side.png`, `_walk_front.png`, `_swing_sword.png` — the same motion across all three.

## Why the earlier attempt missed

On 2026-08-05 the two hands were changed to tilt in **opposite** directions. That sounds like the same fix
and is not — both directions stayed wrong, so the thing being pointed at never changed. The lesson is in
`CHARACTER_DESIGN_GUIDE.md`: measure which way the cuff actually moves, don't reason about it. Rotating
this sprite by +22° moves the cuff 2.4px left, by −22° moves it 2.0px right.

## State

3 outfits official, 13 animations each, 39 total. `PENDING` is empty.
Open `tools/_generated/player/gallery.html` to see them.
