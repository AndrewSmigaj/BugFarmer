# Plants & natural features — the catalog (drafted 2026-06-26)

Everything that **grows or sits in the world and is foraged/harvested/chopped**: trees, flowers, herbs,
mushrooms, grasses, vines, the farmed crops, plus non-plant natural ground features (logs, crystals, bones,
fallen fruit). What each one **drops when foraged/broken** is the point of this page — it feeds cooking, dyes,
alchemy, and building. Ingredient *uses* live in [`materials.md`](materials.md); cooking/dye stations in
[`../crafting.md`](../crafting.md).

**✅ = id exists today** (all rows ✅). Forage = break with hands/sickle (no tool needed unless noted); trees need
an **axe**. **Drop-model:** a plant drops its **own ingredient** (flowers → `flower`; herbs → themselves; berries
→ `berries`), and generic greenery (grass, vines, debris) → `fiber`. This was reconciled 2026-06-26 (see the
**drop-fix note** at the end).

> **Village subset:** oak/apple trees, wild flowers, the culinary herbs, tall grass, and the farmable crops are
> the starting flora. Cacti/desert, glow-mushrooms, and crystals belong to later/biome zones.

---

## Trees (chop for `wood`; fruit trees also bear fruit)
| id | drop (chop) | fruit | notes |
|---|---|---|---|
| `tree_oak` ✅ | `wood` | — | the standard shade tree |
| `tree_pine` ✅ | `wood` | — | conifer |
| `tree_palm` ✅ | `wood` | — | beach/desert |
| `tree_dead` ✅ | `wood` | — | bare/dead |
| `tree_apple` ✅ | `wood` | `apple` | fruit tree (interaction `fruit_tree`) |
| `tree_orange` ✅ | `wood` | `orange` | fruit tree |
| `tree_plum` ✅ | `wood` | `plum` | fruit tree |
| `tree_cherry` ✅ | `wood` | `cherry` | fruit tree |
| `tree_fruit` ✅ | `wood` + `apple` | apple (generic) | generic fruit tree — overlap w/ `tree_apple` (your call) |
| `tree_apple_test` ✅ | `wood` | `apple` | **test asset** — flag for removal (your call) |

## Bushes & berries
| id | forage drop | notes |
|---|---|---|
| `wild_berry_bush` ✅ | `berries` | the berry forage |
| `bush` ✅ | `fiber` | generic leafy bush |
| `bush_flowering` ✅ | `fiber` | flowering bush — overlap w/ `bush` (your call; could drop `flower`) |

## Flowers (bee attractants · dye & cooking)
| id | forage drop | notes |
|---|---|---|
| `flower_wild` ✅ | `flower` | nectar source (bees) |
| `flower_red` / `flower_blue` / `flower_yellow` ✅ | `flower` | colored variants (generic `flower` drop) |
| `flower_aster` / `flower_foxglove` / `flower_bluebell` ✅ | `flower` | **fixed 2026-06-26** (were `fiber`) |
| `sunflower` ✅ | `sunflower_seed` | seed source |
| `poppy` ✅ | `poppy` | red dye; cooking |
| `dandelion` ✅ | `dandelion` | yellow dye; forage |
| `clover` ✅ | `clover` | green dye; clover honey |
| `clover_red` ✅ | `clover` | red clover → `clover` |

## Herbs (culinary & medicinal — each drops its own ingredient)
| id | forage drop | notes |
|---|---|---|
| `chamomile` ✅ | `chamomile` | medicinal/tea |
| `lavender` ✅ | `lavender` | calming/scent |
| `yarrow` ✅ | `yarrow` | medicinal |
| `mint` ✅ | `mint` | **item added 2026-06-26** (was `fiber`) — culinary |
| `sage` ✅ | `sage` | **item added 2026-06-26** — culinary |
| `thyme` ✅ | `thyme` | **item added 2026-06-26** — culinary |
| `fennel` ✅ | `fennel` | **item added 2026-06-26** — culinary |

*(The 6 new herb/succulent items — `mint sage thyme fennel aloe agave` — exist as `resource` items and render via
their world sprite; dedicated inventory icons are an optional art-backlog polish.)*

## Succulents & cacti
| id | forage drop | notes |
|---|---|---|
| `aloe` ✅ | `aloe` | **item added 2026-06-26** — medicinal gel |
| `agave` ✅ | `agave` | **item added 2026-06-26** — syrup/fiber |
| `cactus_saguaro` / `cactus_barrel` / `cactus_prickly` ✅ | self (`cactus_*`) | desert; drop their own id (occupant — no item entry yet → icon-polish candidate) |

## Mushrooms (edible & glow)
| id | forage drop | notes |
|---|---|---|
| `mushroom_red` / `mushroom_brown` ✅ | self | common edibles (have item entries) |
| `mushroom_chanterelle` / `mushroom_puffball` ✅ | self | foraged edibles (have item entries) |
| `mushroom_glow` ✅ | `mushroom_glow` | cave glow (item entry) |
| `mushroom_blue` ✅ | `mushroom_blue` | cave glow — occupant-only drop (icon-polish candidate) |
| `mushroom_cluster` / `mushroom_morel` / `mushroom_bracket` / `mushroom_inkcap` ✅ | self | foraged — occupant-only drops (icon-polish candidates) |

## Grasses, reeds & water plants
| id | forage drop | notes |
|---|---|---|
| `tall_grass` ✅ | `fiber` | grass clump |
| `pampas` ✅ | `fiber` | tall ornamental grass |
| `reeds` ✅ | `reeds` | waterside reed (occupant-id drop) |
| `cattail` ✅ | `reeds` | cattail → `reeds` |
| `marsh_plant` ✅ | — | marsh cattails (a `flora`-category placeable, not an occupant) |
| `water_lily` / `duckweed` / `pondweed` ✅ | `fiber` | floating water plants |

## Vines, ferns & ground cover (generic `fiber`)
| id | forage drop | notes |
|---|---|---|
| `ivy` / `morning_glory` / `grapevine` ✅ | `fiber` | climbing vines |
| `bramble` ✅ | `fiber` | thorny |
| `clubmoss` / `moss_clump` ✅ | `fiber` | mosses |
| `fern` ✅ | `fern` | has its own item |
| `milkweed` / `milkweed_giant` ✅ | `fiber` + seed (designed) | **breeding station** (rooted host plant, D23): chop for material; open to harvest/move the brood; tearing it down while occupied kills the brood. Current data drop is `milkweed` — to change to `fiber`+seed when built. |

## Crops (farmed — plant a seed, water, harvest)
The 7 base crops grow through 4 stages (`plant_X_stage0..3`, config in `crops.json`); the catalog lists the base.
| crop (occupant) | seed item | harvest item | notes |
|---|---|---|---|
| `plant_wheat` ✅ | `seed_wheat` ✅ | `wheat` ✅ | grain |
| `plant_carrot` ✅ | `seed_carrot` ✅ | `carrot` ✅ | root |
| `plant_tomato` ✅ | `seed_tomato` ✅ | `tomato` ✅ | multi-harvest |
| `plant_corn` ✅ | `seed_corn` ✅ | `corn` ✅ | grain |
| `plant_cabbage` ✅ | `seed_cabbage` ✅ | `cabbage` ✅ | leaf |
| `plant_pumpkin` ✅ | `seed_pumpkin` ✅ | `pumpkin` ✅ | large |
| `plant_eggplant` ✅ | `seed_eggplant` ✅ | `eggplant` ✅ | fruiting |

## Natural ground features (non-plant — homed here as world occupants)
| id | drop | notes |
|---|---|---|
| `log_pile` / `log_fallen` ✅ | `wood` | wood without a tree |
| `stump` / `stump_mossy` ✅ | `wood` | tree stumps |
| `crystal_quartz` / `crystal_small` / `crystal_large` ✅ | `crystal` | crystal clusters |
| `geode` ✅ | `geode` | occupant-id drop (icon-polish candidate) |
| `bone_pile` ✅ | `bone` | bones |
| `compost_pile` ✅ | `fiber` | compostable matter |
| `leaf_litter` ✅ | `fiber` | ground litter |
| `fallen_fruit` / `fallen_orange` / `rotten_fruit` ✅ | — (no break-drop) | ground fruit (detritivore food; not foraged) |
| `rubble` ✅ | `stone_block` | break for stone |
| `standing_stone` ✅ | — | landmark (no drop) |
| `ant_mound` ✅ | — | ant colony marker (see species_and_drops.md) |
| `broken_net` ✅ | `fiber` | salvage clutter |
| `wasp_nest` ✅ | — (no material drop) | **breeding station** (portable structure, D23): "chop" = pick it up & move it; open to harvest/move the brood. Current data drop (`paper_nest`+`wasp_larvae`) is the OLD model — to be removed when D23 is built. |

---

**Scope:** ~97 — 10 trees, 3 bushes, 12 flowers, 7 herbs, 5 succulents/cacti, 10 mushrooms, 7 grass/water,
9 vines/moss/fern, 7 crops (+7 seeds, +produce items), 13 natural features. **Drop-fix note (2026-06-26):**
`flower_aster`/`flower_foxglove`/`flower_bluebell` `fiber`→`flower`; `mint`/`sage`/`thyme`/`fennel`/`aloe`/`agave`
got their own `resource` items + drop themselves; 16 genuine fiber plants (grass/vines/debris/water) keep `fiber`;
`wasp_nest` category `nature`→`natural`. Occupant-only drops (cacti, several mushrooms, `geode`, `reeds`) render via
world-sprite fallback — dedicated icons are an optional art-backlog item, flagged not cut. `tree_apple_test` is a
test asset flagged for **your** removal call.
