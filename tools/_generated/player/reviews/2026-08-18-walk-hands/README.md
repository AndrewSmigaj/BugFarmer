# 2026-08-18 — the walking hands sit at different widths

**`WALK_HANDS_WIDTH.png`** ← this one. All three drawn at the **same shoulder width** (blue lines).
Red = the outer edge of the hands at full reach.

| | hands span | clears the shoulder by |
|---|---|---|
| bronze-v2 | 1.19x shoulders | 0.09 |
| fire-ant-v2 | 1.17x shoulders | 0.09 |
| **black-ant-v3** | **1.02x shoulders** | **-0.01 — inside the shoulder line** |

Bronze and fire-ant swing their fists clear of the body. Black-ant's are buried against its sides.

## The cause

`gait.walk_front_into` puts each hand on the body's edge measured at **row 0.62 of the whole
figure** — then adds a gap of 3% of *that row's* width.

That row is a different anatomical place on every outfit, and the body's width there is a different
fraction of the shoulders:

| | width at the placement row | shoulders | ratio |
|---|---|---|---|
| bronze | 19 | 26 | 0.73 |
| fire-ant | 16 | 23 | 0.70 |
| black-ant | 19 | 31 | **0.61** |

Black-ant's pauldrons flare wide but its waist doesn't, so the hands get pinned to the narrow part
and end up behind the shoulder line. Nothing in the code knows where an arm should hang — it reads
the silhouette and hopes.

The gap is the same story: 3% of the placement row means 0px on all three (it floors to the `max(2,…)`
minimum), so there is effectively no clearance term at all.

## The same row breaks the height — `WALK_HANDS.png`

The vertical placement uses that identical 0.62 row, so it lands at the hip on bronze (53% up the
body) and at the **armpit on fire-ant (80%)**. And `ratio=0.17` sizes the hand off total figure
height, so a big helmet also makes a bigger hand: 12px / 13px / 15px.

## Side walk is fine

The side view swings the fists through the torso centre by 0.52 x the torso width at the chest row —
an actual landmark. Reach comes out 0.33-0.38 of body width across all three. It is only the
camera-facing walk that is broken.

## Not code: black-ant is a bigger character

Shoulders-to-feet: bronze 45, fire-ant 46, **black-ant 57**. That is an art re-roll.

---

# Fixed — black-ant is now the reference

**`BEFORE_AFTER.png`** — the same three, before on top, after underneath, all at one shoulder width.

| | before | after |
|---|---|---|
| bronze | 1.19x shoulders | **1.09x** |
| fire-ant | 1.17x shoulders | **1.09x** |
| black-ant | 1.02x shoulders | **1.09x** |

Hand height, as a share of shoulders-to-feet: was 35% / 31% / 27%, now **33% on all three**.

## What changed in the code

`gait.shoulder_line()` is new — the widest row across the torso. It is a real feature of the armour,
so it holds still: across all four frames of both camera-facing banks of all three outfits it moves at
most 2px in width and 1px in row.

`gait.walk_front_into` now measures everything against it:

| | was | now |
|---|---|---|
| where the fists hang | 0.62 down the whole figure | `row` — from the shoulders down toward the feet |
| fist size | 0.17 of total figure height | `ratio` — of the shoulder WIDTH |
| how far out | the body edge at that row, +3% of it | the fist's OUTER EDGE on the shoulder edge, +`edge` |
| travel | in units of that row's width | in shoulder widths |

`gap` is gone. It was 3% of an arbitrary silhouette row, which floored to its 2px minimum on every
outfit — there was no clearance term at all.

## Black-ant was the calibration, and it did move slightly

Every new constant was solved from black-ant's front bank so it would render as it did. It is not
byte-identical:

- **front walk 1.9% of the figure**, run_front 1.2% — a 1px shift of the left fist. The old code
  needed a different clearance on the left than the right (0.048 vs 0.016 of a shoulder) because
  black-ant's silhouette is not symmetric at the old row; one number now serves both sides.
- **back walk 5.9%**, run_back 4.0% — larger, because the constants were solved on the FRONT bank and
  black-ant's back view has a wider shoulder line (33px vs 31px). Look at these two and say if the
  back moved somewhere worse.

## The side walk was not touched

It swings the fists through the torso centre by 0.52 x torso width at the chest row, which is already
a landmark. Reach measures 0.33-0.38 of body width across all three.

## ⚠ None of this is in the game

`official.py` still lists the OLD `bronze`, `fireant`, `blackant`. `build.py --check` cannot even
complete: it stops at `fireant: frame side_4.png is missing`, because the registered fire-ant is the
old 3-frame set. The three rebuilds are still wired to nothing.
