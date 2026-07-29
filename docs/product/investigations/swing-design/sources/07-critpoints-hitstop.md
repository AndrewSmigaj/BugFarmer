# Celia Wagar (CritPoints) — Hitstop / Hitfreeze / Hitlag / Hitpause
https://critpoints.net/2017/05/17/hitstophitfreezehitlaghitpausehitshit/
Read: 2026-07-29 · fighting-game design analysis. The dedicated treatment of the technique.

## What it contributes
Why hitstop works PERCEPTUALLY, not just aesthetically — and what its absence costs.

## Verbatim
- It "gives the eyes a few frames to register and confirm it happened."
- Street Fighter 2's hitstop is "like 10 frames".
- Fighting games let players "cancel moves during the hitstop period", cancels taking effect at its end.
- Smash: characters "vibrate during hitstop, either horizontally on the ground, or vertically in the air."
- Dark Souls 2's lack of hitstop "weakens the impact of the hit perceptually, and makes it harder to tell a
  hit occurred."
- Freezes "both characters" — attacker and victim.

## Techniques, checkable
1. **The function is COMPREHENSION, not decoration** — the eye needs frames to register the collision.
   That matters more for us than for most: our swing is 0.20s total, so the contact instant is ~2 frames at
   60fps. Without a pause there is genuinely almost nothing to see.
2. **Both parties freeze**, not just the victim.
3. **A vibration during the freeze** (Smash) adds energy without motion — cheap and effective at small size.
4. Duration varies wildly by genre: SF2 ~10 frames, action games "a few". For a 0.20s swing, 10 frames would
   be half the move; 2-3 frames (~35-50ms) is the sane range for us.
5. Hitstop can be an INPUT window, not just a visual — cancels land at its end.

## Fit with our constraints
Our onContact already fires at a defined instant and MeleeController already hangs a camera shake off it, so
the hook exists. Adding a 2-3 frame freeze of the pivot plus a small vibration is a handful of lines and is
the highest-value-per-effort change identified in the whole sweep.

Caveat for a farming game: hitstop on EVERY hoe till and axe chop, hundreds of times an hour, may become
irritating where it would not in a combat game. Worth differentiating: combat hits freeze, harvesting hits
don't (or much less). That is a genuine design question, not a copy-the-technique question.
