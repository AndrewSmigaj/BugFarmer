# 2026-08-04 — blade angled back, hand perpendicular to the pommel

Open `ALL_TEN.png`, then play the gifs.

## What changed from `../2026-08-04-swing-arm/`

*"you dont need to have the wrist angle with respect to the pommel of the sword, its awkward, it should
start a little behind the head and swing down, but the sword can be angled back more, similar to far but
the sword is angle back more so that the hand is perpendicular with the pommel"*

- **No wrist articulation.** The blade sits at one fixed angle behind the arm for the whole swing, instead
  of the wrist rotating frame by frame.
- **The fist grips across the handle**, perpendicular to the blade. The old `HAND_ROT = 225` was tuned for
  the shoulder-pivot swing and means nothing once the hand travels, so it is gone.
- **Starts a little behind the head** (128°) and swings down to −74°.
- **Reach 0.60** — B_far's, the one you pointed at.

The only thing that differs between the four is **how far back the blade is held**:

| | blade behind the arm |
|---|---|
| **F1** | 25° |
| **F2** | 45° |
| **F3** | 65° |
| **F4** | 85° — almost square to the arm |

Each in one- and two-handed. Two-handed uses both approved grips, palm hand further up the handle.

## Still open

The gap between shoulder and fist is inherent — there is no arm drawn. It reads as a travelling fist
rather than a floating one because the hand and sword move together, but if it still bothers you at these
reaches, say so and I will bring the whole set closer in.

## Superseded

`../2026-08-04-swing/` (the four "vertical" ones) is dead — it retimed the old shoulder-pivot motion and
never fixed the thing that was wrong. Say the word and I will delete it so it cannot get picked up later.
