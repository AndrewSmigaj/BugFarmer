# Playtank — Building Systemic Melee
https://playtank.io/2024/08/12/building-systemic-melee/
Read: 2026-07-29 · systems-design essay on avoiding per-weapon hand-authoring

## What it contributes
The DATA-DRIVEN parent: attacks as parameterised phase windows rather than authored motions. This is the
closest source to the problem we actually have — dozens of tools, one animator, no per-tool animation budget.

## Verbatim
- Phases as frame windows: "maybe frames 78 to 94 are turned 'on' this way, leaving the telegraphing and idle
  return as-is"
- Distinct phases: telegraphing, active damage window, combo window, recovery vulnerability — "each phase has
  specific gameplay rules attached."
- Hitboxes via "intersection tests... based on attack velocity and weapon shape rather than multiple traces";
  traces must be "predicted forward in time" for fast animations.
- Stimulus-response: "the weapon injects state/damage, then other systems determine consequences" — enabling
  "combinatorial variation without animation duplication."

## Techniques, checkable
1. **Four phases with gameplay rules attached, not three visual ones.** We model telegraph / strike /
   recovery visually but attach no rules to them. A COMBO WINDOW and a RECOVERY VULNERABILITY window are both
   free to add and change how the swing plays, not just how it looks.
2. **Weapon properties exposed as data, motion shared.** Exactly our situation: one animator, per-tool
   parameters. Argues for FEWER hand-set numbers and more derived ones — one weight coefficient rather than
   four independent segment tables.
3. **Sweep patterns as a weapon property** — reach and arc are data, not animation. We already do this
   (arc/offset per profile), so we are further along than the article assumes most projects are.
4. Fast attacks need the hit test predicted forward, or a 0.20s swing can tunnel past a target between frames.

## Fit with our constraints
Validates the existing architecture — profile-driven, one animator, no per-tool prefabs — and says the
remaining win is in exposing MORE as data and deriving more from a single weight parameter.

The combo-window idea is the one genuinely new gameplay concept in the sweep. Everything else found so far
improves how a swing LOOKS; this changes how it PLAYS.
