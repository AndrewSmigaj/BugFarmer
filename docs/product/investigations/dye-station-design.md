# Design: #16 dye vat → dye cloth; add a station to MAKE dyes
_status: READY (design) — all data, zero code · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Today the **dye_vat MAKES dyes** (poppy→red_dye, dandelion→yellow_dye, flower→blue_dye,
  clover→green_dye) and nothing dyes cloth. You want the split: a new **dye-making** station turns
  flowers→dye, and the **dye_vat dyes cloth** (cloth + dye → colored cloth).
- **All data, no code:** the craft-station system is generic (a placeable + recipes naming it via `station` +
  `interaction_type:"craft"` = a working station). So this is: 1 new station placeable + sprite, move the 4
  dye recipes onto it, add `cloth + dye → <color>_cloth` recipes on the dye_vat, add 4 colored-cloth items +
  icons, publish.
- **Certainty:** fits the system **95%** (reuses the proven pattern). **Needs your decision:** the new
  station's name/theme + whether colored cloth feeds clothing/decor recipes. **Status:** `READY`.

## 1. Issue
> "die vats should be for dying cloth, to make dyes we need another station, feel free to design it"

## 2. Current state (verified)
- `recipes.json`: `red_dye←poppy`, `yellow_dye←dandelion`, `blue_dye←flower`, `green_dye←clover` — all
  `station: "dye_vat"`. Items: `red/yellow/blue/green_dye`, `cloth`. No colored cloth, no dyeing recipe.
- `dye_vat` placeable: `interaction_type:"craft"`, breakable — a normal craft station.

## 3. Proposed design
**New station — "Mortar & Pestle" (or "Pigment Grinder"; pick the name):** crush/steep flora into pigment.
- Placeable `mortar_pestle` (or `dye_pot`): `interaction_type:"craft"`, 1×1, breakable, a small bowl/mortar
  sprite (Pipeline A). Craftable at workbench/stonecutter (`stone_block + plank`).
- **Move** the 4 dye recipes here (`poppy→red_dye`, etc.); broaden sources (any red flower→red_dye, etc.) so
  it's not one-flower-per-color. Add more colors later (purple from lavender, orange from marigold…).

**dye_vat → dyeing cloth:**
- New items `red_cloth`, `yellow_cloth`, `blue_cloth`, `green_cloth` (tag `textile`/`material`; icons via
  recolor of `cloth` — cheap, `recolor_sprites.py` style).
- Recipes on `dye_vat`: `cloth + <color>_dye → <color>_cloth` (process_ticks for a slow steep).
- Colored cloth then feeds dyed clothing/rugs/decor recipes (the weaver/loom chain) — the payoff.

## 4. Implementation outline (for the fix-pass)
1. Add `mortar_pestle` placeable (canonical JSON) + its catalog art-row + craft recipe; gen the sprite.
2. Re-`station` the 4 dye recipes from `dye_vat` → `mortar_pestle`.
3. Add 4 colored-cloth items (+ recolor icons) + the 4 `cloth+dye→cloth` recipes on `dye_vat`.
4. `publish_entities.py`; run `recipe_graph.py` + `catalog_coverage.py` (no dangling, no half-ladder); stock
   the crafting test zone.
- Determinism: none (crafting is outside the sim hash). See the `economy` skill + `architecture_crafting.md`.
