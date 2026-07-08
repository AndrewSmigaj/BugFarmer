---
name: economy
description: Read FIRST for any crafting / item / drop / forage / NPC / shop / recipe work. The verified entity + obtainability model, where current design vs as-built live, and the hard-won decisions that keep getting dropped — so you stop reading one file and guessing.
---

# Economy / items / crafting — read this before touching anything

This exists because the assistant keeps re-deriving the system wrong (reading one JSON file, trusting
unverified sub-agents, "consolidating" without consolidating). **Verify every claim against the real entity
def before relying on it.** Don't invent items/materials; don't delete design; surface conflicts as decisions.

## 1. The entity registry is UNIFIED (the #1 thing I get wrong)
The server merges **`items.json` + `occupants.json` + `placeables.json`** into ONE `Entities` map
(`nakama/modules/world/entities.go`, func `LoadAllEntities` — grep it); the client `EntityDatabase` does the same.
So a carryable / drop / recipe id is **valid if it exists in ANY of the three** — never conclude "missing"
from `items.json` alone (that error has happened repeatedly: `ore_copper_block` is an occupant; `chair_wood`/
`stone_block` are placeables; mushrooms/flowers are occupants).
- `occupants.json` — world-placed: ore **deposits** (`category:"ore"`), bugs, trees, **flora/forage**, decor.
- `placeables.json` — player-placed: furniture, **plain blocks** (stone/dirt/clay), **stations**, structures.
- `items.json` — resources, tools, armor, seeds, consumables (sell/buy price, tool stats).
- `crops.json` — crops (`harvest_item`). `recipes.json` — recipes (`station`, `inputs`, `output`, `unlock`).

## 2. How you OBTAIN things (verified)
- **Mine**: ore deposits (occupants) `breakable.drops` → the ore item. **Blocks/placeables drop THEMSELVES**
  (Terraria: break a `well` → get `well`; `stone_block`→`stone_block`). Drops are EXPLICIT — `breakOccupantAt`
  rolls `def.GetDrops()` (`handlers_world.go` ~L547), no self-fallback, so each entity lists its own drop.
- **Forage**: a plant drops its **own ingredient** — `chamomile`→`chamomile`, mushrooms→themselves,
  `reeds`/`cattail`→`reeds`, `bush`/`tall_grass`→`fiber`. (Plants do NOT drop crop seeds — that was junk,
  removed.)
- **Harvest**: crops (`crops.json harvest_item`); fruit trees (`fruit_type` on the tree occupant).
- **Kill**: a bug drops **ONLY `dead_<species>`** (`carcass_item`; `spawnCarcass`, `handlers_combat.go`).
- **Craft**: a recipe output (`recipes.json`). **Buy/Sell**: an NPC vendor — **BUILT v1** (D25):
  a `shop` occupant (`world.shop{kind,sells,buys}`) on `OpCodeAction(2)` → `handlers_shop.go`; currency live.
  Two village vendors (general store + bug dealer). More shops/recipe-selling still designed.

## 3. Decisions that keep getting dropped — DO NOT re-litigate
- **D18 — bugs drop only `dead_<bug>`.** No per-bug ground parts. A **Bug Extractor** (a normal station,
  NOT built yet) turns dead bugs → materials (chitin/silk/venom/leather — these don't exist as items yet).
  `wasp_stinger`/`centipede_parts` are kept as future Extractor outputs, NOT bug drops.
- **No rocks / boulders / stalagmites** (decided 3×) — the world is `stone` + mineral blocks only.
  (`boulder`/`rubble`/`standing_stone` cave-decor cleanup is a deferred task — see backlog.)
- **Nests are breeding stations** (`brood.go`): a wasp nest is a station; larvae are removed *from* it.
  Nothing "drops" `paper_nest`/`wasp_larvae`.

## 4. Where the truth lives
- **Current DESIGN** (intent, the brainstormed catalog): `docs/product/economy/` — `DECISIONS.md` (read first),
  `crafting.md`, `merchants.md`, `progression.md`, `catalogs/*`, `zones/*`. `architecture_items.md` §1-15 was
  **RETIRED 2026-06-26** (the stale ~300-item tables) → now just a pointer; **§0 is the accurate as-built model**.
- **AS-BUILT**: `architecture_crafting.md` (the crafting system) + `architecture_items.md` §0 (the entity/
  obtainability model). Drift between design and code = a decision for the USER (the code may be the bug).
- **Obtainability check**: validate every `items.json`/occupant/placeable drop target resolves in the unified
  registry; a drop to a non-entity (e.g. the old `boulder → stone`) is a bug.

## 5. After editing canonical entity JSON
`python3 tools/data/publish_entities.py` (publishes to the client). Go tests: `bash tools/run_go_tests.sh`
(the local Go toolchain is too old; tests run in the Docker builder). For sim-touching changes, the
`test-changes` skill (determinism gate). Data-only drop/forage edits are determinism-safe (non-edible drops
don't hit the food ledger) but still publish + run go tests.

## 6. The catalogs + the coverage audit (where every entity is homed)
`docs/product/economy/catalogs/` is the per-item enumeration. The 11 pages: tools, weapons, accessories, armor,
materials, consumables (existing) + **furniture, containers, decoration, structures, plants** (the 5 as-built
pages added 2026-06-26). Each entity has ONE **primary** catalog by the homing rule:
- **placeables**: `world.container`→containers; `crafting`→crafting.md; `furniture`+`lighting`→furniture;
  `structure`+`beekeeping` hives→structures; `decoration`→decoration; `block`+`boulder`→materials.
- **occupants**: `natural`/`crop`/`flora`→plants; `ore`→materials; lighting/storage/structure→their page.
- **items**: `resource`→materials (but the **13 dual forageables** that are ALSO `natural` occupants →
  **plants**); `tool`→tools/weapons by `tool_type`; `armor`→armor/accessories by `armor_slot`; `seed`→plants;
  `backpack`→containers.
- **GOTCHA — 14 dual ids** live in two files (13 forageables = item+occupant; `notice_board` = occupant+placeable):
  home them ONCE. Catalogs are curated DESIGN docs, so functional cross-references are fine.
- **Audit**: `python3 tools/data/catalog_coverage.py` — GATE: every entity documented in ≥1 catalog (no orphan)
  + every ✅ id is real; REPORTS double-homes, suspicious ✅ (designed-not-built), and occupant-only drops. Run it
  after adding/renaming any entity; it's the drift gate that replaces eyeballing.
