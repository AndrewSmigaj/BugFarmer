# 2026-08-04 — sword swing, facing DOWN and facing UP

`ALL_1h.png` / `ALL_2h.png` show one frame near the end of each. Play the gifs to judge.

Same model as the settled side-on swing: the hand travels an arc, the blade sits at a fixed angle behind
the arm, the tool follows the hand. Only the aiming changes.

## Facing down (toward the camera)

| | |
|---|---|
| **F1_across** | down across the front, tip finishing low |
| **F2_high_stop** | stops higher; the blade unwinds harder so the tip still points down |
| **F3_lower** | carries a little further down |

**It stops in front of him — it does not carry through to the hip like the side view does.** Side-on the
arm swings past straight down; do that facing the camera and the blade ends up buried in his own legs.
(*"the hoe in the face down view needs to stop in front of the user not swing all the way down"*.)

## Facing up (away from the camera)

| | |
|---|---|
| **B1_across** | down across, mirror of the front one |
| **B2_over_the_top** | over the shoulder, straight down |
| **B3_shallow** | shallower, stays high |

**The weapon draws BEHIND him** in this view, or it covers his back.

## Two things this pass got right that the first attempt did not

- **The shoulder is in a different place in every view** — `(0.06, 0.40)` side-on, `(0.10, 0.10)` facing
  down, `(0.10, 0.22)` facing away. Reusing the side-on shoulder is what once put the hand at face height
  facing the camera (*"the face down the hand is too high... the hand should be lower"*).
- **The blade-back angle has to unwind further when the arm travels less.** Side-on the arm reaches −104°,
  so a blade held 52° behind it ends at −52°, pointing down. Facing down the arm stops around −34°, and
  52° behind *that* is +18° — the tip finishing **up in the air** at the end of a downward swing, which is
  exactly what the first pass rendered. These end with far less blade-back than the side view.
