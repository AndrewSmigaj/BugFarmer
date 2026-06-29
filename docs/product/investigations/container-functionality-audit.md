# Investigation: #14 containers (basket, etc.) not functional — audit
_status: READY TO IMPLEMENT · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Four containers — **`basket`** (the one you named), **`chest`**, **`trunk`**, **`yarn_basket`** —
  have a `world.container` block but **no `interaction_type`**, so the client's open gate (which requires
  `InteractionType == "storage"`, `CraftingPanel.cs:138-140`) never opens them. Properly-tagged containers
  (chest_wood, barrel, crate, dresser, …) are fine.
- **Fix:** add `"interaction_type": "storage"` to those 4 placeables + `publish_entities.py`. Pure data.
- **Secondary:** all container opens also ride the shared single-`OverlapPoint` click resolution (see index
  cross-cutting note + #5) — a properly-tagged container can still fail to open if it overlaps other occupants.
- **Certainty:** the 4-missing-tag cause **95%** · shared-OverlapPoint contributor **70%**.
  **Needs your decision:** none. **Status:** `READY` (data fix + the shared OverlapPoint fix).

## 1. Issue
> "basket and other containers don't seem functional, do an audit."

## 2. Audit result (every entity with a `world.container` block)
- **Broken — container block but NOT `interaction_type:"storage"` → won't open as storage:**
  `basket` (it=None), `chest` (None), `trunk` (None, 36 slots!), `yarn_basket` (None).
- **Intentional, not bugs:** `mannequin_*` use `interaction_type:"mannequin"` (they route to
  `MannequinController`, the outfit panel — that's #4, a different handler, not a storage container).
- **Working:** chest_wood/chest_iron/chest_mossy, barrel, crate, cabinet, cupboard, dresser(_fancy),
  wardrobe, clothing_rack, coat_rack, desk, nightstand(_fancy), metal_shelf, fridge, fish_crate, wine_rack,
  produce_crate, bookshelf(_fancy) — all have `interaction_type:"storage"`.
- Craft stations (anvil, furnace, dye_vat, loom, …) correctly use `interaction_type:"craft"` (separate panel).

## 3. Root cause (verified)
`CraftingPanel.TryHandleRightClick` (`CraftingPanel.cs:127`) reads `def.World.InteractionType` and only
proceeds when it is `"craft"` or `"storage"` (`:138-140`). The 4 containers above carry a valid
`world.container` (slots etc.) but their `world.interaction_type` is absent → the gate is false → no panel.
Server-side `ContainerState` is fine; the block is purely the missing client-facing tag.

## 4. Recommendation
1. **Data fix:** set `world.interaction_type: "storage"` on `basket`, `chest`, `trunk`, `yarn_basket` in the
   canonical `nakama/data/entities/{placeables,occupants}.json`, then `python3 tools/data/publish_entities.py`.
   (Add a tiny gate to `catalog_coverage.py` later: "every entity with `world.container` must declare
   `interaction_type` storage|mannequin" — would have caught this.)
2. **Shared OverlapPoint fix** (see #5/index) so properly-tagged containers also resolve clicks reliably.
- Determinism: none (display/inventory only).
