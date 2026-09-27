# 2026-08-04 — five approaches to the swing, facing DOWN and UP

Ten gifs, nothing else. `ALL_down.png` / `ALL_up.png` show each one mid-arc and at the end of the strike.

## What was wrong before

- **down** — owner review (2026-08-04): it does not need the swing back, and it should swing through farther.
- **up** — owner review (2026-08-04): not a real swing — it runs backwards, with a downward pull-through, a
  stabbing motion going the wrong way.

The up swing dipped the blade **down** and then drove it **up**. That is a reverse stab, not a sword
swing, and I should have seen it.

## The thing I had structurally wrong

A top-down sword attack is a **sweep ACROSS the body** that *passes through* the space being attacked —
it is not a thrust *along* the attack direction. So every approach here is written relative to the
direction attacked (`centre`: −90 for down, +90 for up) and the arc **crosses** it rather than ending on
it. Anticipation is now **one frame**, not a wind-up you can watch.

## The five

| | |
|---|---|
| **A_sweep_across** | the standard — enters one side, sweeps through, exits the other |
| **B_chop_through** | from over the shoulder, carries well past centre — swings through farther |
| **C_thrust** | barely rotates; the **reach** does the work, straight in and back |
| **D_round** | a full circle about the shoulder, passing through the space at speed |
| **E_double_back** | out across, then whipped back through the other way — reads as a fast double |

12 frames @ 20ms = **0.24s**: 1 anticipation, 4 strike (with a blade trail), 2 hold, 5 recovery.

The strike frames **are** the path — no easing inside the arc — so each approach keeps its own shape
instead of being smoothed into the same curve as its neighbours.

## Reference

- [SLYNYRD — Pixelblog 56, Top Down Character Attack Animation](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation)
- [Godot Recipes — melee attacks](https://kidscancode.org/godot_recipes/3.x/animation/melee_attacks/index.html)
