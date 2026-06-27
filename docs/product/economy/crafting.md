# Crafting — the master table

Every station, what it makes, and the cost MODEL. This is the crafting **system** doc — the full item
**enumeration** lives in [`catalogs/`](catalogs/) (armor/weapons/accessories/tools/consumables/materials) and
the per-zone [`zones/`](zones/) sheets; the §4 tables below are representative, not the complete list.
**Pacing** lives in `progression.md`, **shops** in `merchants.md`, **item purpose/bonuses** in
`stats_and_bonuses.md`, **geography/materials** in `../architecture_world.md §1b`, **decisions** in `DECISIONS.md`.

Schema (real, `nakama/data/entities/recipe.go`): `{station, inputs[], output, process_ticks, catalyst,
unlock}`. `process_ticks` @10 Hz (8 ≈ instant, 200 ≈ 20 s, 3000 = 5 min). `unlock` = `craft` (have station+
recipe) / `buy@<shop>` / `find`.

---

## 1. Cost model (so 200 rows are consistent, not arbitrary)
Price by **material tier-value** (rough "points"), not by gut:

| pts | materials |
|---|---|
| 1 | wood, fiber, stone, sand, clay, flower |
| 2 | plank, coal, brick, glass-sand |
| 3 | copper_bar, glass, thread |
| 4 | bronze_bar, cloth, beeswax, chitin |
| 6 | iron_bar, silk, honey |
| 10 | steel_bar, silver_bar, gem (minor), venom |
| 16 | gold_bar, gem (major) |
| 24–40 | platinum_bar, diamond |

Derived numbers:
- **Craft cost** = Σ(input pts). **Sell price** of the output ≈ **0.5×** its craft cost (you lose value vs
  buying inputs raw — pushes players to *use* what they make).
- **Buy price** (when a shop sells the finished good) ≈ **1.6–2×** craft cost — the convenience premium and a
  real coin sink (Lens of Economy).
- **Artisan multiplier:** a processed good sells for **~2–3×** its raw inputs (the money engine).
- **`process_ticks` by station class:** workbench/stonecutter 8–12 · sawmill/loom 12–40 · cooking_pot/cauldron
  50–120 · furnace 100–200 · anvil 30 · forge 60 · keg/preserves 1500–3000 (aging is a pacing lever, Lens of
  Time).

## 2. Target FLOORS (anti-minimalism — these are minimums, tune numbers not counts)
- Each station carries **≥4–6 recipes** (so it earns its footprint).
- **~5 metal tiers**, each a **full tool family + a full armor set**.
- **~6 utility outfits**, **~12–15 accessories**.
- **≥80%** of the 48 existing decorations craftable (split ≈ **70% craft / 20% buy / 10% find**).
- **≥1 artisan chain per farm product**; **≥1 craft use per major bug drop**; **a handful of dye colors**.
- Sprinklers + at least one of {fertilizer, bait, rain-collector} present.

## 3. Station roster — what each makes + how you get it
| Station | Makes | Obtained |
|---|---|---|
| workbench | basic tools, furniture, walls, the *other* stations' frames | **craft** (wood ×8) — or starter-given |
| stonecutter | brick, stone walls/paths, statues | **craft** @ workbench (stone ×10) |
| furnace | ore → bars, sand → glass, wood → charcoal | **craft** @ workbench (stone ×12 + clay ×4) |
| sawmill | wood → planks, fine wood furniture | **craft** @ workbench (wood ×20 + copper_bar ×2) |
| loom | thread/cloth, rope, sacks, cloth gear | **craft** @ workbench (wood ×10 + fiber ×20) |
| anvil | metal tools, weapons, armor | **craft** @ workbench (iron_bar ×5 + stone ×10) |
| forge | steel/alloys, high-tier metal gear | **craft** @ anvil (iron_bar ×10 + brick ×5) |
| cooking_pot | meals (timed buffs) | **craft** @ workbench (copper_bar ×2 + stone ×4) |
| chopping_block | food/ingredient prep — chop produce & butcher carcasses (`dead_*`) into cooking inputs | **craft** @ workbench (wood ×6) |
| `bug_extractor` | processes `dead_<bug>` carcasses → bug materials (chitin/leather/silk) (D18) | **craft** @ workbench — **BUILT (placeholder art)**; chitin recipe live, full dead→material map = design TODO |
| `spinning_wheel` | fiber → thread (the Weaver's thread station, D26) | **craft** @ workbench (recipe **buy@weaver**) |
| `sewing_machine` | cloth → woven goods (the foot-cranked Weaver table, D26) | **craft** @ workbench (recipe **buy@weaver**) |
| `dye_vat` | flora → dyes (basic colours auto; D26) | **craft** @ workbench (recipe **buy@weaver**) |
| cauldron | potions, dyes | **craft** @ anvil (copper_bar ×4 + stone ×6) |
| keg / preserves_jar | artisan goods (wine, mead, pickles, jam) | **craft** @ sawmill (plank ×10 + copper_bar) |
| honey_extractor | honeycomb → honey/beeswax | **craft** @ workbench (plank ×6 + copper_bar) |
| compost_bin | scraps → fertilizer | **craft** @ workbench (plank ×6) |
| jeweler | accessories (gem + metal) | **craft** @ forge (gold_bar ×5 + gem ×3) **or buy@blacksmith** |
| dye_vat | dye baths (recolor) | **craft** @ loom (clay ×6 + copper_bar) |
| **electronics_bench** | power/automation tech | **BUY@blacksmith** (no player recipe — too complex) |

Bootstrap is clean (no circular gate): furnace smelts the first iron → anvil is built at the workbench from
that iron → forge is built at the anvil. The one un-craftable station (electronics) is a **bought** coin sink.

> **As-built reconcile (2026-06-26):** the **10 `crafting`-category placeables in the data today** are
> `workbench`, `stonecutter`, `furnace`, `sawmill`, `loom`, `anvil`, `forge`, `cooking_pot`, `cauldron`,
> `chopping_block`. The other rows above (`keg`/`preserves_jar`, `honey_extractor`, `compost_bin`, `jeweler`,
> `dye_vat`, `electronics_bench`) are **designed** stations not yet `crafting`-category placeables —
> `honey_extractor` exists as a `beekeeping` placeable, `compost_bin` as a `structure`. A station is "live" only
> when `RecipesByStation[id]` is non-empty (see [`../architecture/architecture_crafting.md`](../architecture/architecture_crafting.md)).

---

## 4. Master recipes — by station
Tiered families are shown once with the per-tier formula (expanded by the template in `production.md`).

### workbench (`process_ticks ≈ 8`)
| Output | Inputs | Unlock | Purpose |
|---|---|---|---|
| torch ×3 | wood 3 + coal 1 | craft | light |
| chest_wood | wood 8 | craft | storage |
| bed | plank 10 + cloth 4 | craft | respawn (set home) |
| sign / fence_wood ×3 / gate | wood 3–6 | craft | structure |
| {station} frames | see §3 | craft | builds the other stations |
| basic furniture (chair/table/stool/shelf…) | wood 4–10 | craft (most) / buy / find | décor (bonus-type tag) |

### stonecutter (`≈10`)
brick ×4 (stone 4) · wall_stone ×2 · stone_path ×4 · stone_brick · pillar/statue (décor) · sandstone (sand 4 → sandstone). **craft.**

### furnace (`100–200`)
| Output | Inputs | Catalyst |
|---|---|---|
| copper_bar | copper_ore 2 | coal 1 |
| iron_bar | iron_ore 2 | coal 1 |
| silver/gold/platinum_bar | {ore} 2 | coal 1–2 |
| **glass** | sand 2 | coal 1 |
| charcoal | wood 5 | — |

### sawmill (`12`)
plank ×2 (wood 1) · fine furniture (dresser, bookshelf, desk, wardrobe — plank 6–12) · barrel · crate · wood_floor.

### loom (`40`)
thread (fiber 3) · cloth (thread 2) · rope (fiber 5) · sack/backpack-upgrade (cloth) · cloth armor pieces · **utility-outfit cloth bases**.

### anvil (`30`) — tools / weapons / armor, **per metal tier**
| Family | Formula (tier T) | Tiers |
|---|---|---|
| pickaxe / axe / shovel / hoe / scythe / watering-can | {bar}×2 + wood×2 | copper→platinum |
| sword / spear / dagger | {bar}×2 + wood×1 | copper→platinum |
| helmet / chest / gloves / legs / boots (a **full set**) | {bar}×3–6 | copper→platinum |
| net / shears (bug-catch tools) | {bar}×2 + cloth×1 | copper→iron |

### forge (`60`)
steel_bar (iron_bar 1 + coal 2) · bronze_bar (copper 2 + tin 1) · **steel/silver/gold tools + armor sets** (same formulas, higher tiers) · alloy weapons.

### cooking_pot (`50`) — meals = **timed buffs** (no hunger system; GDD)
veggie stew, berry pie, honey cake, mushroom skewer, etc. — inputs = crops/forage; each grants a short
buff (the bonus TYPE tags to `stats_and_bonuses.md`).

### cauldron (`100`) — potions + dyes
health tonic, swiftness brew, miner's draught (light), night-eye, luck potion, **calm_spray** (✅ exists),
repellent · **dyes** (flower/bug-pigment → color baths). Catalysts often a **bug drop** (venom/stinger).

### keg / preserves_jar (`1500–3000`, aging) — **artisan goods**
fruit→**juice/wine**, honey→**mead**, veg→**pickles**, fruit→**jam**, milk*→cheese (*future livestock),
grain→flour→bread. Sell at the **artisan multiplier** — the mid/late money engine.

---

## 5. Bug-derived crafting (the unique hook — ≥1 use per major drop)
| Drop (from / zone) | Crafts | Station |
|---|---|---|
| **chitin / carapace** (beetles) | chitin armor set (`thorns`), reinforced tool grips | forge |
| **silk** (spiders/webs) | silk cloth → light armor, fine clothing, rope | loom |
| **beeswax** (bees) | candles, sealed preserves, wax polish (furniture bonus) | cooking_pot/cauldron |
| **honey** (bees) | mead (keg), honey cakes, healing salve | keg / cooking_pot / cauldron |
| **venom / stinger** (wasps, scorpions) | venom blade catalyst, potions (poison/antidote), bug-bane weapon | cauldron / forge |
| **bug pigments** (assorted) | dyes (recolor gear/décor) | dye_vat / cauldron |
| **ant_egg / formic acid** (ants) | bait, fertilizer booster, etch/acid recipes | compost_bin / cauldron |
| **rare specimens** (bosses) | trophy décor (mounted case), bug-bane blade (find recipe) | sawmill / forge |

## 6. Farming consumables & automation (incl. sprinklers)
| Item | Effect | Station | Tiers |
|---|---|---|---|
| **sprinkler** | auto-waters tiles in a radius/day (aura; modeled on `compost_bin`/`autonet`) | anvil/forge | basic (3×3) → iron (5×5) → steel (7×7, needs power) |
| rain_collector | refills sprinklers passively | sawmill | — |
| fertilizer | soil speed/quality (compost → fertilizer) | compost_bin | basic → quality → deluxe |
| bait | lure target bug species | cauldron | per family |
| seed maker | crop → seeds | sawmill | — |

*Sprinkler is the one genuinely-new **mechanic** (a watering aura) — flagged as build-phase code; everything
else here is data.*

## 7. Decorations & structures (most craftable; some buy/find)
The full **per-item** catalogs (every id, with proposed source + village subset) live in
[`catalogs/furniture.md`](catalogs/furniture.md), [`catalogs/containers.md`](catalogs/containers.md),
[`catalogs/decoration.md`](catalogs/decoration.md), and [`catalogs/structures.md`](catalogs/structures.md).
This section is just the **split policy**:
- **Craft (~70%)** — the bulk of the furniture / decoration / structure placeables become recipes at
  workbench/sawmill/stonecutter/loom. Each tags a **bonus TYPE** (comfort/light/etc.) for the §11.5 system;
  values authored later.
- **Buy (~20%, @ Carpenter/General Store)** — flavorful or fiddly pieces (fine paintings, fancy lamps, exotic
  rugs) sold finished — a coin sink and a reason to visit town.
- **Find (~10%)** — rare/themed pieces (boss trophies, ruin relics) as exploration rewards.

## 8. Category coverage checklist (proves the floors are met)
| Category | Where | Floor met? |
|---|---|---|
| Material ladders (bars/planks/cloth/glass/brick) | furnace/sawmill/loom/stonecutter | ✅ |
| Tools (5 tiers, full families) | anvil/forge | ✅ |
| Weapons (per tier + bug-bane) | anvil/forge | ✅ |
| Armor sets (per tier + chitin/silk) | anvil/forge/loom | ✅ |
| Utility outfits (~6) | loom (+ `stats_and_bonuses.md`) | ✅ |
| Accessories (~12–15) | jeweler | ✅ |
| Food (timed buffs) | cooking_pot | ✅ |
| Potions + dyes | cauldron / dye_vat | ✅ |
| Artisan goods (≥1/product) | keg/preserves | ✅ |
| Bug-derived (≥1/drop) | §5 | ✅ |
| Farming automation + **sprinklers** | §6 | ✅ |
| Lighting | workbench | ✅ |
| Furniture / Decoration (≥80% craftable) | §7 | ✅ |
| Structures (fences/walls/paths/doors) | workbench/stonecutter/sawmill | ✅ |
| Storage | workbench/sawmill | ✅ |
| Beekeeping | honey_extractor + hives | ✅ |
| **Stations themselves** (craft or buy) | §3 | ✅ |

Bulk authoring (how we actually create all of this) → `production.md`.
