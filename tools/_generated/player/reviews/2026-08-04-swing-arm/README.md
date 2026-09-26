# 2026-08-04 — swings where the HAND TRAVELS

**These replace `../2026-08-04-swing/`, which was wrong in the same way everything before it was wrong.**

Open `ALL_TEN.png` for one frame of each, then play the gifs — the motion is the whole point here and a
still frame cannot show it.

## What was wrong with every previous swing, including this morning's

*"do people take a sword in their fist, hold their fist up to their shoulder and rotate their fist to
swing it? ever?"* — no, and that is exactly what the old code did.

`swing_frames` computed **one angle**, placed the **tool** at a fixed small radius from the body centre,
and then stuck the hand onto the tool's grip. The tool led and the hand was downstream of it, so the fist
stayed parked beside the shoulder and **rotated in place** while the blade swept round it like a clock
hand bolted to his chest. Changing the timing curve — which is all four of this morning's "vertical
swings" did — cannot fix that, because the timing was never the problem.

`DESIGN.md` already said *"Drive the HAND, then hang the tool off it"*. The renderer did the opposite.

## What these do instead

```
shoulder    fixed point on the body
hand        shoulder + reach(t) x direction(t)      <- THE HAND TRAVELS
blade       points along the arm, plus a wrist offset  <- pivots at the WRIST
tool        positioned so its grip lands on the hand   <- the tool FOLLOWS
```

Reach is in **cells** (half the body height). His half-width is only about 0.28 of a cell, so 1.0 is a
whole torso away — the first attempt used 0.6–1.15 and produced a sword floating in space beside a man.
These run 0.26–0.66.

## The five

| | what varies |
|---|---|
| **A_short** | hand travels, but stays close to the body |
| **B_far** | same path, hand as far out as it can go and still read as his |
| **C_elbow** | tucked on the wind-up, **extends through contact**, folds back after — what an arm does |
| **D_overhead** | up and behind first, then all the way down in front |
| **E_wrist_snap** | moderate travel; the blade **lags** the arm on the way down and whips past at the bottom |

Each in one- and two-handed. Two-handed uses both approved grips — back of the hand on one arm, palm on
the other, palm further up the handle.

## What I can see, from the stills only

- **A** and **E** keep the fist closest to the body and read as most attached to him.
- **B**, and **C** at full extension, leave a visible gap between shoulder and fist. With no arm drawn
  that gap is the risk — it starts to read as a sword floating alongside rather than held.
- **C** is the only one where the reach itself carries the impact, which is the thing that usually sells a
  swing. Whether that beats the gap it opens is a judgement call, and it is yours.

## Two errors I made building this, recorded so they are not repeated

- `FACINGS` gives the shoulder in **cell units offset from body centre**, `+x` forward and `+y` up. I read
  the y as a fraction of body height, which put the shoulder in the wrong place and the whole arm with it.
- Reach in cells is much larger than it sounds. Sanity-check any reach against his half-width (~0.28 cell)
  before rendering ten of them.
