# 2026-08-18 — does the pixel conversion actually work?

The gate before spending anything on the other 25 outfits. Nothing here cost money.

## Watch these three first

`outfits/<name>/anim/ALL_ANIMATIONS.gif` — **every animation of one outfit in one file**: the three
walks, the three runs, and all seven tool swings, playing together.

- `C:\Users\emily\BugFarmer\tools\_generated\player\outfits\bronze-v2\anim\ALL_ANIMATIONS.gif`
- `C:\Users\emily\BugFarmer\tools\_generated\player\outfits\fireant-v2\anim\ALL_ANIMATIONS.gif`
- `C:\Users\emily\BugFarmer\tools\_generated\player\outfits\blackant-v3\anim\ALL_ANIMATIONS.gif`

Every cell is at 2x native pixels, one whole-number scale for the whole sheet, nothing resampled.

## The answer to "did it pixelize"

### `OLD_vs_NEW_bronze.png`
The bronze `official.py` points at today, next to the pixel one, at the same on-screen height.

| | figure | colours |
|---|---|---|
| OLD `outfits/bronze` | 118x270 | **12,555** — a smooth render |
| NEW `outfits/bronze-v2` | 26x68, shown 4x | **972** — a sprite |

**Bronze did convert.** It was rebuilt on 2026-08-15 at 18:09 — the last thing that happened before
the power went out, which is why you never saw it. The old raw bronze is what has been on screen.

### `PIXEL_PROOF_<outfit>.png`
Front, side and back at 8x for each of the three. What to check: every block the same size, hard
edges. All three pass — 719-1,164 colours at 26-32px wide.

## What I changed to make the gifs pixel

Two things were quietly destroying the grid *after* conversion, so a gif built from pixel frames still
came out looking raw:

1. `render_animations.TARGET_BODY_H = 320` scaled every outfit by a **fractional** factor — 3.678x
   black-ant, 4.156x fire-ant, 4.706x bronze. Fractional NEAREST makes some source pixels 4 screen-px
   wide and the ones beside them 5. Now everything composites at **native size** and is enlarged once,
   by **4x**, at the very end (`build.PIXEL_SCALE`).
2. `gallery_gif.py` resized every cell with **`Image.LANCZOS`** — a blur filter. Now whole-number
   divisors and NEAREST only.

Verified by arithmetic, not by eye: every rendered frame of all 13 animations x 3 outfits is an exact
4x block grid (each 4x4 block a single flat colour).

⚠ **Side effect, intended:** outfits are no longer forced to one on-screen height, because that
normalisation was measured on TOTAL figure height — headgear included — which shrank the *body* of a
tall-helmeted outfit. Black-ant is 87 native px against bronze's 68, so it now genuinely renders
taller. That difference is real and was previously hidden.

## Nothing has been promoted

All three are in `official.PENDING`, pointing at their existing folders. No renames, no archiving,
nothing in `OUTFITS`. `build.py <name>` renders a pending outfit for review only and says so.

## What I need decided

1. Does the pixel conversion hold up?
2. **Bronze** — does it pass, or reroll it with the tighter prompt language?
3. Fire-ant and black-ant — still good now that you can see them animated?

Still open from before, unchanged: black-ant's body is 24% longer than the other two
(shoulders-to-feet 57 vs 45/46), which is an art issue, not a code one.
