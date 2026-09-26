# PRUNE — Village vendors (`village_21_B`): what each NPC sells

> **REVIEWED 2026-06-27 →** Andrew's calls are recorded in `DECISIONS.md` **D26** and turned into concrete
> assignments in **`_village_assignments.md`** (station · recipe/collection · vendor/find · unlock). This file
> is the original input; the two above are the live source of truth.

> **Working decision doc (scratch).** Source = [`village.md`](village.md) + D20. Mark **KEEP / CUT /
> LATER / NEW-ok** per row. `✅` exists today · `🆕` must be created · `⚠️` exists as a different thing.
> **In scope:** Merchant (General Store)✅, **Blacksmith** ("some metal"), **Carpenter** (furniture
> recipes). Bug Dealer✅ already live. **Fisherman + Mayor = BACKLOGGED** (fishing unbuilt; land deeds
> separate). **Tools/weapons recipes AUTO-unlock (never gated)** — the store just *also sells* them.

---

## 1. GENERAL STORE — Merchant (`general_store_merchant` ✅ live, currently sells seeds/tools)
Designed: *general goods, seeds, supplies, decorations, recipes, basic equipment; rotating stock + rare teases.*
| Decision | Item | Status | Note |
|:--:|---|:--:|---|
| ☐ | seeds: `seed_tomato/corn/carrot/cabbage/pumpkin/wheat/eggplant` | ✅ (eggplant: `seed_eggplant`✅) | already sold |
| ☐ | `small_net` ✅ / `large_net` ✅ | ✅ | net (start + sold) |
| ☐ | `watering_can_basic` ✅ | ✅ | |
| ☐ | `magnifying_glass` (inspect bugs, starter) | 🆕 | designed starter tool — missing |
| ☐ | `gardener_gloves` | 🆕 | craftable + sold |
| ☐ | `straw_hat` (sun hat) | 🆕 | craftable + sold |
| ☐ | storage: small sack → large basket | 🆕 (`backpack`✅ is the 3rd tier) | sack/basket missing |
| ☐ | `calm_spray` ✅ | ✅ | keep |
| ☐ | basic tools also on shelf: `pickaxe_/axe_/hoe_/shovel_/scythe_` wood→copper | mostly ✅ (scythe only `scythe_wood`✅; `shovel_copper`🆕) | sold convenience |
| ☐ | basic weapons: `sword_wood`✅ `spear_wood`✅ → `sword_copper`🆕 `spear_copper`🆕 | mixed | sold + a few rare teases |
| ☐ | a few **decorations** (sold finished) | from §3 list | pick which |
| ☐ | a few **recipes / rare teases** (buy@general) | TBD | "peek at high-end gear" |
| ☐ | **rotating/randomized stock** | ⏸ feature | adds shared state → backlog or build? |

## 2. BLACKSMITH (`blacksmith` 🆕) — "sells SOME metal; real mining gear is at the Mining Camp"
| Decision | Item | Status | Note |
|:--:|---|:--:|---|
| ☐ | `iron_bar` ✅ | ✅ | metal restock |
| ☐ | `copper_bar` | 🆕 | bar ladder missing (only iron_bar exists) |
| ☐ | basic metal tools (copper/iron pickaxe/axe) | ✅ (`pickaxe_copper/iron`,`axe_copper/iron`) | "some metal" |
| ☐ | copper/iron armor pieces | ✅ (`copper_helmet`,`iron_*`,`leather_*`) | |
| ☐ | accessories (`bee_charm`✅/`lucky_clover`✅) | ✅ | "accessories" |
| ☐ | buys: ores + bars | ✅ ids | over-mine sink |
> Note: the deep mining gear/recipes deliberately live at the **Miner's Outpost** (see the underground
> prune doc), NOT here. Blacksmith stays light.

## 3. CARPENTER (`carpenter` 🆕) — "furniture / wood / building recipes" — THE BIG PRUNE
The placeables below **already exist as art** but have **NO recipes** (not obtainable yet). Per
crafting.md §7: **~70% craft (auto) / ~20% buy-finished / ~10% find**, and "fancy = needs dyes/advanced
mats, not buildable yet." Mark each: **C**=craft-recipe(auto) · **B**=buy-finished(carpenter/store) ·
**R**=find-only · **L**=later(needs dyes/mats) · **CUT**=drop the piece.

### Furniture (59 exist)
| Set per item (C/B/R/L/CUT) | Placeables |
|---|---|
| ☐… | `chair_wood` `table_wood` `stool_wood` `bench` `log_seat` `sawhorse` `shop_shelving` `counter` `bookshelf` `dresser` `desk` `cabinet` `cupboard` `wardrobe` `nightstand` `side_table` `coffee_table` `bed_basic` `cot` `bunk_bed` `bench_padded` `bench_stone` `stool_stone` `table_stone` `planter_box` `specimen_shelf` `bug_terrarium_big` `keg` `wine_rack` `sink` `stove` `stove_wood` `range_stove` `fridge` `bathtub` `vanity` `loveseat` `sofa` `sofa_modern` `armchair` `rocking_chair` `chaise_lounge` `ottoman` `chair_cushioned` `kitchen_island` `map_table_big` `bar_cart` `throne` `grandfather_clock` `bed_canopy` |
| ☐ **L (fancy → needs dyes/adv mats)** | `bed_fancy` `sofa_fancy` `dresser_fancy` `counter_fancy` `dining_table_fancy` `armchair_fancy` `bookshelf_fancy` `chair_fancy` `nightstand_fancy` |

### Decoration (48 exist)
| Set | Placeables |
|---|---|
| ☐… | `rug` `rug_large` `rug_round` `potted_plant` `plant_large` `window_box` `vase` `mirror_standing` `statue_founder` `statue_bug` `statue_stone` `cat_statue` `fountain` `birdbath` `aquarium` `bug_terrarium` `specimen_case` `telescope` `globe` `easel` `gramophone` `coat_rack` `room_divider` `column_marble` `suit_of_armor` `ship_wheel` `anchor_decor` `laundry_line` `scarecrow` `hay_bale` `campfire` `campfire_spit` `water_bucket` `mining_bucket` `ore_pile` `ore_sack`(prop) `garden_border_log` `garden_border_stone` `lily_pad` `cow_skull` `dead_bush` `tumbleweed` `sandstone_formation` `awning` `fishing_net`(prop) `fishing_pole`(prop) |
| ☐ lighting (8) | `torch` `lantern` `candle` `candelabra` `lamp_post` `lamp_table` `lamp_floor` `lamp_floor_fancy` |

### Structure / building (walls/fences/gates/doors — mostly auto @ workbench/stonecutter/sawmill)
| ☐ | `wall_wood/wood2/stone/brick/brick2/marble/sandstone` · `fence_wood/picket/picket_weathered/iron/stone/corner_wood` · `gate_wood/picket/iron` · `door_wood/square/iron` · `well`✅ · `ladder` · `garden_arch` · `hedge` |

## 4. DYES (all 🆕) — "sold by the appropriate vendor"
| Decision | Id | Status | Source |
|:--:|---|:--:|---|
| ☐ | `red_dye` `yellow_dye` `blue_dye` `green_dye` | 🆕 | from local flowers/poppy (needs a dye recipe + dye_vat/cauldron) |

## 5. PREREQUISITE GAPS (eyes-open before keeping)
- **No furniture/décor recipes exist at all** — KEEPing "Carpenter sells furniture recipes" = authoring a
  recipe batch (inputs from wood/plank/cloth; **`plank`/`cloth` themselves are 🆕**).
- **Bug Extractor station 🆕** + its outputs (`leather`/`chitin`/`silk` raw mats 🆕) gate the leather/cloth armor the store/blacksmith reference.
- **`copper_bar` + the bar ladder 🆕** (only `iron_bar` exists) — furnace recipes for them missing.
- **Dyes need a dye recipe + station** (dye_vat designed-not-built; cauldron ✅ exists as fallback).
- **Rotating store stock** = shared mutable state (coordination/determinism note) → decide build-now vs backlog.

## 6. BACKLOGGED (your call — not this pass)
- **Fisherman** (`fishing_pole`✅/`fishing_net`✅/`boat`✅ exist) — **deferred with the fishing mechanic** (no fishing code yet).
- **Mayor** — land deeds (separate system).
- **`bridge_wood`** 🆕 (only `dock_plank`✅ exists) — fishing/docks dressing.

## 7. AFTER PRUNE
KEEP base-mats/stations → KEEP items → KEEP furniture/décor recipes (auto vs `shop:carpenter`/`shop:general_store_merchant`) →
recipe-unlock mechanism → NPC sprites + dialogue → place blacksmith@smith bldg + carpenter@carpenter bldg
(`zone_village_21_B.py`) + booths → verify + commit.
