# 2026-08-05 — fire-ant and black-ant built end to end

`CONSISTENCY_bronze_fireant_blackant.png` — the same seven animations across all three outfits. Same
poses, same arcs, same scale; only the armour and each outfit's own gauntlets differ. That is the whole
point of the outfit system, and it now holds for a set built from scratch today.

**14 animations each**, from `motions.py`, using **their own gauntlets** (`hands = outfit`).

## Two pipeline bugs this uncovered — both would have hit every future outfit

**1. The cutter could not read a magenta sheet.** Sheets have been generated on magenta since
2026-07-29; `cut_outfit.background()` still keyed on near-black. Every existing outfit predates the
switch, so nothing had been cut since, and the failure surfaced only now as *"expected 3 rows of 4, got
[1]"*. It now **detects the key from the sheet's own border** and handles both.

**2. Magenta key bleed on the silhouette edge.** The generator anti-aliases the figure against the
background, so the outermost pixels are a blend of art and key. On black sheets that was a dark edge and
invisible; on magenta it is bright pink, and it survives keying because a half-magenta pixel is not
magenta enough to key out.

| | before defringe | after |
|---|---|---|
| fireant | 1.04% of opaque pixels | **0.00%** |
| blackant | 1.32% | **0.00%** |

`defringe()` replaces each tinted pixel with the mean of its clean neighbours, three passes, and drops
any with no clean neighbour rather than guessing.

## Worth flagging

The gauntlets are the same colour as the armour on both, so the hands barely read in the side walk —
same as silver. Not wrong, but if hands need to read against the body, that is a gauntlet-design
decision, not an animation one.
