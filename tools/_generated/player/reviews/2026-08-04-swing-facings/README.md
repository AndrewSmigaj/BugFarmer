# 2026-08-04 — sword swing, facing DOWN and facing UP

`FILMSTRIP_front.png` and `FILMSTRIP_back.png` show one swing broken into its phases. `ALL_1h.png` /
`ALL_2h.png` show the end pose of each option. Then play the gifs.

## These are their own motions, not the side swing re-aimed

> *"you are starting with the sideways swing first and then trying to force it into different melds, the
> swing will be different when facing down and up, and it also needs to finish the swing"*

The side swing is **one monotonic sweep** from behind the head to the hip. Facing the camera that is the
wrong shape twice over — the arc is in a different plane, and a monotonic sweep **stops dead** at the
bottom instead of following through. So each of these is written in three phases:

| | |
|---|---|
| **RAISE** | lift the blade clear, wind up |
| **STRIKE** | fast, through the tile being attacked |
| **FINISH** | carry **past** the contact point and settle — the swing ends, it does not freeze |

## It has to cover what it hits

> *"when you strike something below you while facing down it means being able to strike something below
> you, all your looking down ones are pretty much the same thing as the sideways ones"*

**Facing down, the blade lands with its tip past his feet** — covering the tile south of him. **Facing up,
past his head** — the tile north. A swing that sweeps out to the side is a front-facing sprite doing the
sideways attack: it covers nothing in the direction he is actually attacking, so it is useless as an
attack however good it looks.

## The options

| facing down | | facing up | |
|---|---|---|---|
| **F1_overhead** | raise beside the head | **B1_uppercut** | wind low, drive up |
| **F2_high_raise** | bigger raise, more travel | **B2_deep_wind** | deeper wind-up |
| **F3_tight** | tighter and faster | **B3_tight** | tighter and faster |

Each one- and two-handed. Facing up, the weapon draws **behind** him.

The arm is offset to the side so the blade comes down **beside** him rather than through his own torso —
swinging from a shoulder at his centre reads as impaling, not striking.

## Two things I got wrong on the way here, recorded

- **The blade-back angle must unwind further when the arm travels less.** Side-on the arm reaches −104°,
  so 52° behind it ends at −52°, pointing down. Facing down the arm stops higher, and 52° behind *that*
  points the tip **up in the air** at the end of a downward swing.
- **A follow-through has to move the blade somewhere visibly different from the strike.** The first up
  swing took the arm past vertical while unwinding the blade by the same amount, so `blade = arm + back`
  stayed pinned near 90° and the last three frames were identical.
