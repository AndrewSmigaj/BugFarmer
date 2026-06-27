# Village — recipe / vendor / station ASSIGNMENTS (for review)

> **Working doc.** Andrew reviews; I author (per D26). Every village-relevant placeable/item →
> **{station · recipe-or-collection · sold-by/find · unlock}**. `(review)` = my sensible default where you
> didn't specify — correct freely. `🆕` = item/material must be created. Existing-but-no-recipe items just
> need a recipe authored. **Rule:** tools/weapons/armor recipes **auto-unlock**; furniture/décor/advanced are
> **books or individual gated recipes**; structures (walls/fences) mostly **default-unlock**.

## A. RECIPE COLLECTIONS (the "books") — buy the book → learn the whole set
| Collection | Sold by (book) | Station(s) | Members |
|---|---|---|---|
| `basic_furniture` | **Carpenter** | workbench/sawmill | chair_wood, table_wood, stool_wood, bench, log_seat, rocking_chair, bookshelf, dresser, desk, cabinet, cupboard, wardrobe, nightstand, side_table, coffee_table, bed_basic, cot *(review: cot/bunk_bed basic?)* |
| `advanced_furniture` | **Carpenter** | sawmill | loveseat, sofa, sofa_modern, armchair, chaise_lounge, ottoman, chair_cushioned, kitchen_island, map_table_big *(review: bar_cart, chaise here)* |
| `stone_works` | **Stonemason** | stonecutter | bench_stone, stool_stone, table_stone, planter_box *(review: planter_box wood?)*, statue_stone, column_marble *(review)* |
| `woven_goods` | **Weaver** | loom | rug, rug_large, rug_round, laundry_line, room_divider *(review)* |
| `structures_wood` | **Carpenter** (or default-unlock) | sawmill/workbench | wall_wood, wall_wood2, fence_wood, fence_picket, fence_corner_wood, gate_wood, gate_picket, door_wood, door_square *(review: default-unlock vs book)* |
| `structures_stone` | **Stonemason** | stonecutter | wall_stone, wall_brick, wall_brick2, wall_sandstone, fence_stone, brick paths *(review)* |

> *Naming TBD (D26 "name collections better") — these are working slugs.*

## B. INDIVIDUAL RECIPES (sold/learned one-off)
| Output | Station | Sold by / source | Unlock |
|---|---|---|---|
| keg (basic) | sawmill *(review)* | **Carpenter** (also sells finished) | `shop:carpenter` |
| grandfather_clock | sawmill | Carpenter | `shop:carpenter` |
| bed_canopy | sawmill | Carpenter | `shop:carpenter` |
| throne | sawmill | **found — chest in Mayor's house** | `find` |
| candle 🆕recipe | workbench | **General Store** | `shop:general_store_merchant` |
| candelabra | anvil/forge | **Blacksmith** (iron) | `shop:blacksmith` |
| reed_hat 🆕 | workbench | **Fisherman** | `shop:fisherman` |
| wall_wood | sawmill (wood station) | Carpenter | **default** (auto) |
| fence_wood/picket | workbench | **buy finished @ General Store** + **recipe @ Carpenter** | `shop:carpenter` |
| stove_wood ("wood stove") | anvil | **Blacksmith** (it's metal) | `shop:blacksmith` |
| garden_arch | — | **another town** (defer) | `find`/elsewhere |
| wine_rack | — | **bee zone** (defer) | elsewhere |

## C. PER-VENDOR STOCK
### General Store / Merchant (`general_store_merchant`)
Sells (finished): seeds (all village), `small_net`/`large_net`, `watering_can_basic`, `calm_spray` (costs a
bit), `torch`, `lantern` (pricier), **fence (finished)**, `magnifying_glass`🆕, `gardener_gloves`🆕 (decent
price), a curated few **decorations** *(review list: potted_plant, vase, rug, window_box)*. Sells (recipe/
book entries): **candle recipe**, a couple **rare-tease recipes** *(review)*. **Rotating:** random
higher-level teases. Buys: material/food tags (crops/forage). **NOT** metal tools/weapons.
### Blacksmith (`blacksmith` 🆕)
Sells: `iron_bar`✅ + `copper_bar`🆕, copper/iron tools (`pickaxe_/axe_copper/iron`✅), **weapons beyond wood**
(`sword_copper`🆕/`spear_copper`🆕 + iron), armor (copper/iron/leather✅), **stove_wood**, **candelabra
recipe**. Buys: **metal BARS** (not ore). Remove bee_charm/lucky_clover. Accessories → backlog.
### Carpenter (`carpenter` 🆕)
Sells: **basic_furniture book**, **advanced_furniture book**, individual recipes (keg/grandfather_clock/
bed_canopy/fence/wall_wood), maybe finished **loveseat** + **keg**. Station: workbench/sawmill.
### Ecologist (`ecologist` 🆕 — building exists)
Sells/has recipes: telescope, specimen_shelf, specimen_case, bug_terrarium, bug_terrarium_big, globe
*(review)*, easel *(review)*. (Science/collection décor.)
### Weaver (`weaver` 🆕 — NEW shop scene)
Sells: **woven_goods book/recipes** (rugs, laundry_line, room_divider), cloth🆕, **dyes** (dye station; basic
red/yellow/blue/green default-unlocked; special colors = recipes elsewhere).
### Stonemason (`stonemason` 🆕 — NEW building scene)
Sells: **stone_works book**, **structures_stone**, birdbath, fountain, statues (statue_stone/statue_bug/
statue_founder/cat_statue), column_marble, garden_border_stone.
### Modern Wares (`modern_wares` 🆕 — NEW building scene: glass blocks/modern floors/shelves)
Sells: fridge, range_stove, sofa_modern *(review: here vs advanced_furniture)*, lamp_floor/lamp_floor_fancy
(**electricity → backlog**), modern décor. (Mostly buy-only finished; electronics never craftable.)
### Fisherman (`fisherman` 🆕) — placed; **fishing mechanic deferred**
Sells: fishing_pole, fishing_net, boat (inert until fishing), **reed_hat recipe**.
### Mayor (`mayor` 🆕 — building exists) — land deeds DEFERRED
Add a **chest** in his house → **throne recipe** (find).

## D. NEW ITEMS / MATERIALS TO CREATE (with icons via gpt-image-1)
- **Bars:** `copper_bar`, `silver_bar`, `gold_bar`, `platinum_bar`, `steel_bar`, `bronze_bar` (furnace/forge).
- **Base mats:** `plank` (sawmill), `thread`+`cloth` (loom), `glass` (furnace: sand→glass).
- **Bug Extractor outputs:** `leather`, `chitin`, `silk` (+ the `bug_extractor` station itself 🆕).
- **Dyes:** `red_dye`/`yellow_dye`/`blue_dye`/`green_dye` (dye station 🆕 — or cauldron fallback).
- **New goods:** `magnifying_glass` (tool), `gardener_gloves` (armor/accessory slot — bonus backlog),
  `reed_hat` (head), `copper_bar`-tier weapons `sword_copper`/`spear_copper`.
- **Modern Wares mats:** `glass_block`🆕, `modern_floor`🆕, shelving (for the scene).

## E. TAXONOMY RECLASSIFY — DO NOW (pure data/role; no mechanic needed)
| Id | From | To | Action |
|---|---|---|---|
| `lily_pad` | decoration | **flora/plant** | move to plants; plantable in water *(placement mechanic backlog)* |
| `dead_bush` | decoration | **CUT** | remove from village stock/placement |
| `cow_skull` | decoration | **find-only** | one in this zone's NE forest; no recipe/sale |
| `tumbleweed` | decoration | **find (drier zones)** | not village |
| `campfire`,`campfire_spit` | decoration | **cook-station** | add `interaction_type:"craft"` + cooking recipes (station id) ; built @ workbench |
| `keg` | furniture (already craft) | keep cook/artisan station | author keg recipes |

## F. TAXONOMY RECLASSIFY — RIDES WITH A BACKLOG MECHANIC (mark intent now)
- `water_bucket`/`mining_bucket` → **container** (1-slot, water/contents) — needs fill-display.
- `ore_sack` → **`ore_bin` container** (filter:block, high cap) — needs fill-display.
- `fishing_pole`/`fishing_net` → **tools** (placeable form) — rides with fishing.

## G. SNEAK-PEEK / FIND / DEFER (not sold here)
- **Stays in zone (sneak-peek), recipe elsewhere:** garden_arch (another town), wine_rack (bee zone),
  fancy furniture (`bed_fancy`/`sofa_fancy`/`dresser_fancy`/`counter_fancy`/`dining_table_fancy`/
  `armchair_fancy`/`bookshelf_fancy`/`chair_fancy`/`nightstand_fancy` → a later zone; maybe one `sofa_fancy`
  recipe). **straw_hat** → later zone.
- **Find-only:** throne (mayor chest), cow_skull (NE forest), boss/relic décor later.
- **Backlog mechanics:** player-plots/décor-on-farm, lighting finish, electricity, fishing, land deeds,
  fill-state containers, water-tile placement.

## H. OPEN CALLS for Andrew (the `(review)` flags above)
1. cot/bunk_bed → basic_furniture or individual?  2. planter_box → wood (carpenter) or stone (stonemason)?
3. sofa_modern → advanced_furniture (carpenter) or Modern Wares only?  4. Which decorations does the General
Store carry vs Weaver/Stonemason/Ecologist?  5. gardener_gloves slot — accessory vs hand armor?
6. Collection names (basic_furniture/advanced_furniture/… → your preferred labels).
