# Crafting — design & content

How crafting works and the station/recipe content plan. The *system* architecture (opcodes, state,
determinism boundary) lives in [`architecture_crafting.md`](architecture_crafting.md); this doc is the
**design + content** queue (what to craft, where).

## The model (one system, a speed knob)
There is no "quick vs slow" mode. Every station works the same way:

1. Right-click a station → the crafting panel opens.
2. Pick a recipe → set a quantity → **Craft**. The inputs leave your bag immediately.
3. The station **processes** at the recipe's `process_ticks` (10 Hz): a workbench tool is ~8 ticks
   (≈instant), a furnace smelt is ~200 (≈20 s). A progress bar fills.
4. Output piles into the **output grid**. **"Get all"** sweeps it into your inventory (overflow
   stays); **double-click** a cell to take just that stack.

Storage containers (chests/dressers/racks) share the same panel/opcode plumbing: **double-/shift-click**
a stack to move the whole thing between your bag and the container. Filtered containers (a wardrobe →
`clothing`) reject items that lack the tag.

**Gating (Stage 1):** a recipe is available when you're *at its station* with the inputs — you gate
progression by owning/building the furnace, anvil, etc. Learned/bought recipes (the `unlock` field) wait
on player persistence (see backlog).

## Stations & recipes (the content queue)
Deliberately broad — prune later for fun. **Bold** = an EXISTING sprited item; _italic_ = a NEW item
(see [`art_needed.md`](art_needed.md)). Speed in parens is just a `process_ticks` hint.

- **workbench** (fast) — basics: **torch**, simple **furniture** (**chair_wood**/**table_wood**/
  **fence_wood**), **sword_wood**/wooden tools from **wood** (+ **fiber**). _wood_plank_ later.
- **sawmill** (slow) — **wood** → _wood_plank_ (+ _sawdust_); planks gate better furniture/structures.
- **furnace** (slow) — smelt: **iron_ore** + **coal** → **iron_bar**; **copper/tin/silver/gold/platinum_ore**
  → _*_bar_; **sand** → _glass_; **wood** → _charcoal_.
- **anvil** (fast) — bars → metal **tools/weapons/armor** tiers (**pickaxe_iron**/**axe_iron** today; the
  recolor pipeline already makes tier icons) + _nails_, _fittings_.
- **forge** (slow) — advanced alloys / high-tier metal (_steel_ from _iron_bar_ + _charcoal_), endgame gear.
- **stonecutter** (fast) — **stone_block** → **brick**, **wall_stone**, slabs/paths/statues.
- **loom** (slow) — **fiber** → _thread_ → _cloth_; cloth gates clothing/soft armor/_rug_/sacks.
- **cauldron** (slow) — herbalism: **chamomile/lavender/yarrow/mushrooms** → _dyes_ (recolor),
  _potions_/**calm_spray** — ties to the herbalist NPC.
- **cooking_pot / stove** (fast+slow) — **produce** → _meals_ (food/swarm boosts); _flour_ (**wheat**) → _bread_.
- **chopping_block** (fast) — cheap early **wood**/food prep (no station-build needed).
- **honey_extractor** (slow) — honeycomb → _honey_ → _honey_wine_ (beekeeping; backlog).
- **Future** — dye/tailoring station, jeweler (gems→accessories), electronics bench (when electricity lands).

No **bug-leather** — leather armor exists but has no material source yet (future livestock, or
shop-bought); don't block crafting on it.

### Stage-1 validation set (shipped — existing art only)
`recipes.json` ships these so quick + slow + multi-input + the panel are all exercisable in the
**Crafting Test** zone with no new art:

| Station | Recipe | Inputs | Output | Ticks |
|---|---|---|---|---|
| workbench | torch | 3 wood + 1 coal | 3 torch | 8 |
| workbench | chair_wood / table_wood / fence_wood / sword_wood | wood | the item | 8 |
| stonecutter | brick | 2 stone_block | 4 brick | 10 |
| stonecutter | wall_stone | 2 stone_block | 2 wall_stone | 10 |
| furnace (slow) | iron_bar | 2 iron_ore + 1 coal | 1 iron_bar | 200 |
| anvil | pickaxe_iron / axe_iron | 2 iron_bar + 2 wood | the tool | 30 |

## Storage audit (shipped)
Storage furniture now declares `world.container {slots, filter}` + `interaction_type:"storage"`:
- **Generic:** chest_wood(24), chest_iron(30), chest_mossy(18), barrel/crate(12), cabinet/cupboard(12),
  desk(8), nightstand/nightstand_fancy(6).
- **Filtered:** dresser/dresser_fancy/wardrobe → `clothing`; coat_rack → `clothing`;
  bookshelf/bookshelf_fancy → `book`; wine_rack → `drink`; fridge → `food`; produce_crate/fish_crate → `food`.

Specialized capture/collection devices (bait_basket, collection_tray, bug_terrarium, autonet,
specimen_shelf) are LEFT to their own (bug/fishing) systems — not general item storage.

Items carry `tags` (clothing/food/material/metal/tool/seed/consumable) — a container's filter is a tag.
