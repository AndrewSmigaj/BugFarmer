# Investigation: #13 apples hover — want them on the ground, hit to pick up
_status: READY (design) — needs your pick of approach · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Fruit already **falls to the ground** (server `dropFruitFromTree` drops an `apple`/`orange` item
  beside/in-front of the trunk, `handlers_farming.go:763`). The "hover" is the **`GroundItemVisual` bob
  animation** (`bobAmplitude 0.08`, `bobFrequency 2` — every drop floats to read as a pickup), rendered at the
  raw fractional drop Y with no ground baseline. Apples are already `no_auto_pickup:true` (E-key today).
- **What you want = a design change:** fruit should sit FLAT on the ground and be **hit (any tool) to
  collect** — i.e., behave like a tiny resource node, not a floating pickup.
- **Recommended approach (A):** make fallen fruit a small **breakable ground occupant** instead of a bobbing
  ground item — sits flat (occupant render baselines it, no bob), and a hit runs the existing break→drop path
  to give you the apple. Reuses `BreakingController` + the occupant/breakable system; minimal new code.
- **Certainty:** hover-cause (bob) **90%** · the design is a proposal. **Needs your decision:** approach A
  (breakable ground occupant) vs B (no-bob flag + click-pickup on the existing ground item)? **Status:** `READY`.

## 1. Issue
> "I think apples should not hover like that but be placeable on the ground and hit with whatever to pick them up, please investigate how we can do that."

## 2. Why it hovers (verified)
- `GroundItemVisual` (class comment "Handles bob animation and highlight feedback") bobs every drop by
  `bobAmplitude 0.08` around `basePosition = worldPosition` (the server's fractional drop position,
  `worldY = tree.GridY + 0.2 − rng·1.2`). No ground baseline → it floats at a fractional height + bobs.
- Pickup: `apple`/`orange` are `no_auto_pickup:true` → E-key, not a hit.

## 3. Design options
- **A — fallen fruit = a tiny breakable ground occupant (recommended).** On drop, place a 1×1 ground occupant
  (`fallen_apple`, pivot bc → baselined flat, no bob) with `breakable{hp:1, drops:[apple]}`. Hitting it with
  any tool runs the normal break→drop. Pros: exactly "sits on the ground, hit to collect"; reuses break +
  occupant systems; y-sorts correctly. Cons: a new occupant type + the server drop path switches from
  ground-item to occupant placement (small).
- **B — keep the ground item, change its feel.** Add a per-item `grounded` flag → `GroundItemVisual` skips the
  bob + baselines to the cell floor; and route fruit pickup through a left-click/hit instead of E. Pros:
  smaller data change. Cons: ground items aren't built to be "hit"; you'd special-case the pickup path.

## 4. Recommendation
Go with **A**. It matches the intent ("placeable on the ground and hit with whatever"), reuses the breakable
pipeline, and fixes the hover for free (occupants don't bob and are baselined). Scope: a `fallen_<fruit>`
occupant family (art = the existing `fallen_fruit`/`fallen_orange` sprites) + switch `dropFruitFromTree` to
place that occupant. Determinism: fruit drop is server-authoritative display/inventory; a non-blocking ground
occupant doesn't touch the bug-sim collision (set `blocks_bugs:false`).
