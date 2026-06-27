# Item Architecture

## Overview

All items in BugFarmer have a footprint (grid cells for placement) and a sprite size (visual pixels). The base grid unit is 16×16 pixels.

**Reference sizes:**
- Grid cell: 16×16 pixels
- Player: 48×32 pixels (3×2 cells) - bird's eye view, slightly higher angle
- Smallest bugs: 8×8 pixels (don't use grid)

**Perspective:** Top-down / bird's eye with slightly higher angle. Sprites show tops/backs of objects. Tall objects (trees, lamps) have foreshortened height but player walks behind them.

**Item properties:**
- **Footprint**: Cells the item occupies for collision/placement (W×H in grid cells)
- **Sprite**: Recommended visual size (W×H in pixels) - can exceed footprint
- Items with tall sprites: player walks behind them (tree, lamp post, etc.)

---

## 0. Item & inventory model

The kinds of thing in the world, where their data + art live, and how the inventory treats them:

| Kind | Data file | Art | Notes |
|------|-----------|-----|-------|
| **Tile** (ground layer) | tiles config | `Resources/Tiles/{id}.png` (opaque) | grass, dirt, garden_plot, floors, paths — set per cell, not an inventory item. **A rug is NOT a tile.** |
| **Placeable** | `placeables.json` | `Resources/Objects/{id}.png` | occupies a grid **footprint** (1+ cells), ownable/bought, can grant farm bonuses. Includes **flat placeables** (rug: `flat:true`, drawn on top of the floor) and **blocks** (dirt/stone/ore/wood/wall — a placeable subtype that tiles into a grid; breakable). |
| **Plant / flora** (world) | `occupants.json` | `Resources/Objects/{id}.png` | small flora (flowers/herbs/mushrooms/grass) placed **freely anywhere** — sub-cell position, varied scale & shape, NOT grid-locked, NOT one-per-cell, NOT uniform size; blocked only by already-occupied space. Cut → inventory item. |
| **Free / collectible** | `items.json` (+ world occupant) | reuses the world sprite | placed anywhere, picked up: the bobbing drops — broken blocks, tree-drop wood, fallen fruit, **cut flowers/herbs/mushrooms**. |
| **Tool / weapon** | `items.json` | `Items/{id}_icon.png` | held & swung: the SAME icon sprite is animated in-hand by `PlayerToolAnimator` (swing/sweep/stab/pour by `tool_type`) — pipeline A art, NOT pipeline B (only the player body/gear sprites are hand-authored). |
| **Resource / seed / consumable** | `items.json` | `Items/{id}_icon.png` | wood, fiber, bars, crystal, seeds, potions, fish. **Ore CHUNKS** (`iron_ore`, `coal`, …) are the exception: they carry NO authored icon — they **borrow their deposit's world sprite** via `icon_from: "ore_*_block"` (a scaled-down `Objects/{block}.png`), so the bag shows the same art you mined. The mineable deposit **veins** themselves (`ore_iron_block` = "Iron Deposit", 16×20) are **world occupants** (`occupants.json`, cave-gen-spawned, pickaxe-tier-gated), NOT placeables. |
| **Bug** | bug data | bug sprite | free-placed in the world via a later **release mechanic**. |

**Plants (flowers / herbs / mushrooms / small flora) are FREELY placeable — not grid-locked.** The engine
positions them at any sub-cell point (float coords), at **varied scale**, and they can be **different
shapes/sizes** (some ~1 unit, some ~2 units tall, etc.) — they are NOT one-per-grid-square and NOT all the
same size. The ONLY placement constraint is they can't overlap something already occupying that space (a
block, a placeable footprint, deep water). On open ground they sit freely. (Cut plants are still inventory
items — flowerpot / vase / sell / craft.)

> Engine note (free placement vs the frontier-gated sync): this should be fine. Plants are static,
> non-colliding world decor — they don't move, don't path, and don't participate in the bug-swarm
> simulation that the frontier gating exists to throttle. Placement just needs an "is this point free?"
> check (no overlap with occupant footprints / blocks / water); after that a plant is data + a sprite at a
> float position, replicated like any other static occupant. The sync risk in this engine was *moving*
> swarm entities and resync stalls, not static decor count. (Validate with the sync-harness once we wire a
> real place-plant action, but I see no reason it would stress the frontier path.)

**Breaking a block** spawns a floating **mini of the actual block sprite** (not a generic icon) that bobs
until picked up. Trees are destroyed and drop wood blocks the same way.

**Inventory icons — two paths (IMPLEMENTED):** `EntityDatabase.GetItemSprite(id)` resolves every item
display sprite (inventory slots, hotbar, drag cursor, AND floating ground drops) through one chain:
`Objects/{icon_from}` → `Objects/{id}` → `Items/{id}_icon` → `Items/{id}` →
`Bugs/{species sprite_id}` (bug slots store SPECIES ids; the species→sprite_id map comes from
the now-PUBLISHED `Data/species.json` — publish_entities.py copies it beside the entity JSONs).
- **Derived (no art authored):** placeables, blocks, and cut flowers/herbs use a **mini of their world
  sprite** as the icon (same art as the bobbing drop). Scaling is the consumer's job: UI Images use
  `preserveAspect`; ground drops fit-box to ≤0.75 cell (`GroundItemVisual`).
- **Authored (`Items/{id}_icon.png`):** only items with **no world sprite** — raw resources, tools/weapons
  (drawn 16×16 diagonal: grip bottom-left, head top-right, so one sprite serves as icon AND the in-hand
  swing art via `PlayerToolAnimator`), seed packets, potions, fish.
- `icon_from` (optional, items.json) borrows another entity's world sprite when ids mismatch.

**Bonus system & item "type":** decorations/furniture grant small idle farm bonuses with **diminishing
returns keyed off item `id`** ("a second sofa adds less than the first"; `category` is available as a
coarser grouping). The inventory tracks items by `id`, so the "type" the bonus system needs is **already
known — no schema change**. The per-item **bonus value** is a field added *with* that system, not before
(see `game_design.md §11.5`).

---

## 1–15 (retired) → the economy catalogs

The old §1–15 item tables (coin-ITEMS, blueprint-item, ~80 per-bug drops, 9-tier tool/armor ladders) and the
Summary were **aspirational and had drifted from current decisions**. They are retired here (git history
preserves them). The **as-built, reconciled item set now lives in the economy catalogs**, grounded in the real
entity JSON and audited by `tools/data/catalog_coverage.py` (no-orphan gate):

| What | Where |
|---|---|
| Tools / weapons / accessories | [`../economy/catalogs/tools.md`](../economy/catalogs/tools.md) · [`weapons.md`](../economy/catalogs/weapons.md) · [`accessories.md`](../economy/catalogs/accessories.md) |
| Armor | [`../economy/catalogs/armor.md`](../economy/catalogs/armor.md) |
| Materials, blocks & ore deposits | [`../economy/catalogs/materials.md`](../economy/catalogs/materials.md) |
| Consumables | [`../economy/catalogs/consumables.md`](../economy/catalogs/consumables.md) |
| Furniture / containers / decoration / structures / plants | [`furniture.md`](../economy/catalogs/furniture.md) · [`containers.md`](../economy/catalogs/containers.md) · [`decoration.md`](../economy/catalogs/decoration.md) · [`structures.md`](../economy/catalogs/structures.md) · [`plants.md`](../economy/catalogs/plants.md) |
| Crafting stations + recipes | [`../economy/crafting.md`](../economy/crafting.md) |
| Bugs / species drops | [`../economy/species_and_drops.md`](../economy/species_and_drops.md) |

**§0 above is the still-accurate as-built model** (placeable vs free/collectible item; the icon = scaled-down
world sprite; ore deposits ARE occupants). Everything below it was the drift — read the catalogs instead.
