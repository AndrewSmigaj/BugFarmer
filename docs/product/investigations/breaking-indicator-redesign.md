# Design: #17 a better breaking indicator (covers the whole object, looks good)
_status: READY (design) — display-only, reuses the progress hook · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Today `BreakingVisual` swaps a single **crack-overlay sprite** (`break_stage_*.png`) by damage %
  — a small decal that doesn't cover big objects and depends on crack art. Replace it with a **procedural,
  whole-object** treatment: per-hit **flash + shake**, a **progress ring/bar**, a progressive **damage tint**,
  and a **debris burst + pop** on the final hit. No new art required for the core (all procedural); optional
  debris sprites. Reuses the existing `SetProgress(0..1)` hook the server already drives.
- **Certainty:** fits/feasible **90%** (display-only, hook exists). **Needs your decision:** the exact look
  (how juicy: flash+shake minimal, or full flash+shake+ring+debris) + keep or drop crack decals. **Status:** `READY`.

## 1. Issue
> "we need to make a better breaking indicator which covers the whole things getting broken and just looks better, come up with a new solution"

## 2. Current state
`BreakingVisual.SetProgress(progress)` picks a `break_stage_*` crack sprite by `1-progress` and draws it as a
semi-transparent overlay at sortingOrder 1000. One small decal, art-dependent, doesn't scale to the object.

## 3. Proposed design (how good 2D games do it — Stardew shake/flash/debris > Minecraft cracks)
Drive all of it from the existing `SetProgress` (and a `OnHit()` pulse on each strike):
1. **Per-hit flash (whole sprite):** briefly tint the occupant's SpriteRenderer toward white, decaying over
   ~0.1s — covers the whole object, reads as "I hit it."
2. **Per-hit shake/wobble:** a small position/rotation jitter of the whole occupant on each hit, amplitude
   scaling with remaining HP (wobblier as it nears breaking). Stardew-style "it's taking damage."
3. **Progress indicator:** a thin HP bar or a radial ring above the object (or a corner pip), filling down as
   `progress→0`, shown only while actively breaking + a short linger. Clear "how close."
4. **Progressive damage tint:** lerp the sprite slightly darker/desaturated as HP drops (whole-sprite "wear")
   — replaces the crack decal, no art needed.
5. **Break moment:** a debris-particle burst (a few tinted squares sampled from the sprite's palette) + a
   quick scale-up-then-pop/fade of the object, then the drop spawns. The "satisfying break."

Keep it ONE component (`BreakingVisual`) that owns flash/shake/ring/tint, attached to the occupant being
broken, fed by `SetProgress` + an `OnHit`. Drop the `break_stage` sprite dependency (or keep cracks as an
optional layer behind the procedural effects).

## 4. Implementation outline (fix-pass)
- Extend `BreakingVisual` with `OnHit()` (flash+shake pulse) + a coroutine-driven tween; add a small UI/world
  progress ring; add a debris burst on break (reuse the particle/pool pattern used elsewhere). Wire `OnHit`
  from `BreakingController` on each registered hit, and `SetProgress` from the server break-progress message.
- Determinism: none — pure client feedback; the server still owns HP/break authority.
