# Structures — the catalog (drafted 2026-06-26)

Placed **built things** that aren't furniture, containers, décor, or crafting stations: fences, walls, doors,
signs, wells, docks, mining rigs, bug-catching infrastructure, beehives. Cost/stations in
[`../crafting.md`](../crafting.md); sellers (e.g. the electric line is **buy-only**) in
[`../merchants.md`](../merchants.md).

**✅ = id exists today** (all rows ✅). `source` is the **proposed** 🔵 obtainment. The **electric/weather** line
(`fence_electric`, `antenna`, `radar_dish`, `weather_console`, `neon_sign`) is the **bought electricity expansion**
(wealth-gated, D14) — not craftable. The **`honey_extractor`** processing station lives in
[`../crafting.md`](../crafting.md), not here.

> **Village subset:** wooden/picket `fence_*` + `gate_*`, a `well`, a few `sign_*` + `notice_board`, a
> `market_stall`. Mining rigs, docks, explosives, and the electric line belong to later zones.

---

## Fences, gates & garden barriers
| id | role | source 🔵 | notes |
|---|---|---|---|
| `fence_wood` ✅ | wood fence | craft@workbench (wood) | village |
| `fence_corner_wood` ✅ | wood fence corner | craft@workbench (wood) | corner piece for `fence_wood` |
| `fence_picket` ✅ | picket fence | craft@workbench (wood) | village — overlap w/ `fence_wood` |
| `fence_picket_weathered` ✅ | weathered picket | craft@workbench / find | aged variant |
| `fence_stone` ✅ | stone fence | craft@stonecutter | sturdier |
| `fence_iron` ✅ | iron fence | craft@anvil (iron_bar) | sturdiest |
| `fence_electric` ✅ | electric fence | **buy** (electricity expansion, D14) | powered barrier |
| `broken_fence` ✅ | broken fence | **find** | ruin/clutter |
| `hedge` ✅ | hedge | craft@workbench (fiber) / grow | living barrier |
| `garden_arch` ✅ | garden arch | craft@workbench (wood) | garden gateway |
| `gate_wood` ✅ | wood gate | craft@workbench (wood) | pairs w/ `fence_wood` |
| `gate_picket` ✅ | picket gate | craft@workbench (wood) | pairs w/ `fence_picket` |
| `gate_iron` ✅ | iron gate | craft@anvil (iron_bar) | pairs w/ `fence_iron` |

## Walls
| id | role | source 🔵 | notes |
|---|---|---|---|
| `wall_wood` ✅ | wood wall | craft@sawmill (plank) | village |
| `wall_wood2` ✅ | log wall | craft@workbench (wood) | rustic variant |
| `wall_brick` ✅ | brick wall | craft@stonecutter (brick) | town |
| `wall_brick2` ✅ | stone-brick wall | craft@stonecutter (brick+stone) | town variant |
| `wall_stone` ✅ | stone wall | craft@stonecutter (stone) | sturdy |
| `wall_sandstone` ✅ | sandstone wall | craft@stonecutter (sandstone) | desert |
| `wall_marble` ✅ | marble wall | craft@stonecutter (marble) | premium |

## Doors & windows
| id | role | source 🔵 | notes |
|---|---|---|---|
| `door_wood` ✅ | wooden door | craft@workbench (wood) | village |
| `door_square` ✅ | simple door | craft@workbench (wood) | overlap w/ `door_wood` |
| `door_iron` ✅ | iron door | craft@anvil (iron_bar) | secure |
| `window_4pane` ✅ | 4-pane window | craft@sawmill (plank+glass) | wall window |

## Signs & notices
| id | role | source 🔵 | notes |
|---|---|---|---|
| `signpost` ✅ | signpost | craft@workbench (wood) | generic directional |
| `sign_plank` ✅ | plank sign | craft@workbench (wood) | generic |
| `notice_board` ✅ | notice board | craft@workbench (wood) | quests/notices (also an occupant variant) |
| `sign_market` / `sign_market_board` ✅ | market signs | craft@workbench (wood) | market dressing |
| `sign_shop` / `sign_inn` / `sign_camp` ✅ | shop/inn/camp signs | craft@workbench (wood) | building markers |
| `sign_anchor` / `sign_fish_board` ✅ | dock/fishing signs | craft@workbench (wood) | dock dressing |
| `sign_weaver` ✅ | weaver/textile shop sign (D26) | craft@workbench (wood) | weaver storefront |
| `sign_anvil` / `sign_leaf` / `sign_crest` ✅ | smith/naturalist/town-crest signs | craft@workbench (wood) | themed markers |
| `sign_weather` / `veg_patch_sign` ✅ | weather/veg-patch signs | craft@workbench (wood) | themed markers |
| `neon_sign` ✅ | neon sign | **buy** (electricity expansion, D14) | powered sign |

*(16 sign variants — kept as a set; many are pure town-dressing. Overlap is intentional flavor; **your** call which the village uses.)*

## Wells, pumps & mills (water/power)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `well` ✅ | well | craft@stonecutter (stone) | village water; breaks → `well` (Terraria self-drop) |
| `hand_pump` ✅ | hand pump | craft@anvil (iron_bar) | water draw |
| `windmill` ✅ | windmill | craft@sawmill (plank) | mill flavor / power |
| `windmill_tall` ✅ | tall windmill | craft@sawmill (plank) | size variant |

## Docks & boats
| id | role | source 🔵 | notes |
|---|---|---|---|
| `dock_plank` ✅ | dock planks | craft@sawmill (plank) | walkable dock |
| `mooring_post` ✅ | mooring post | craft@workbench (wood) | dock fitting |
| `boat` ✅ | rowboat | craft@sawmill (plank) | water traversal flavor |
| `rowboat_beached` ✅ | beached rowboat | **find** (shore) | shore prop (occupant) |

## Mining infrastructure (D13 mining loop)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `mine_rail` ✅ | mine rail | craft@anvil (iron_bar) | cart track (hauling — backlog mechanic) |
| `mine_cart` ✅ | mine cart | craft@anvil (iron_bar) | runs on `mine_rail` |
| `mine_support` ✅ | mine support | craft@workbench (wood) | tunnel beam (structural dressing) |
| `rock_crusher` ✅ | rock crusher | craft station | mining chain step 1: `{metal}_ore` → `{metal}_paydirt` (D13) |
| `ore_sluice` ✅ | ore sluice | craft station | mining chain step 2: `{metal}_paydirt` → `refined_{metal}_ore` (D13) |
| `gem_cutter` ✅ | gem cutter | craft station | cuts raw gems → cut gems (`ruby`→`cut_ruby`, etc.) |
| `coal_bin` ✅ | coal bin | craft@workbench (wood) | fuel store dressing |
| `lumber_rack` ✅ | lumber rack | craft@workbench (wood) | wood store dressing |

## Bug-catching infrastructure (passive collection)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `autonet` ✅ | autonet | craft@anvil (iron_bar+fiber) | placed auto-collector (capacity-capped); see tools.md A3 |
| `net_post` ✅ | net post | craft@workbench (wood) | mounts netting |
| `fly_netting` ✅ | fly netting | craft@loom (fiber) | spans posts; passive catch |
| `bait_station` ✅ | bait station | craft@workbench (wood) | lures bugs |
| `bait_basket` ✅ | bait basket | craft@workbench (fiber) | bait holder — overlap w/ `bait_station` |
| `collection_tray` ✅ | collection tray | craft@workbench (wood) | gathers passive catch |

## Farm & utility
| id | role | source 🔵 | notes |
|---|---|---|---|
| `compost_bin` ✅ | compost bin | craft@workbench (plank) | scraps → fertilizer (a crafting station too — see crafting.md) |
| `wheelbarrow` ✅ | wheelbarrow | craft@workbench (wood) | farm dressing |
| `tool_rack` ✅ | tool rack | craft@workbench (wood) | tool display |
| `ladder` ✅ | ladder | craft@workbench (wood) | vertical access |
| `market_stall` ✅ | market stall | craft@sawmill (plank) | sell point (the merchant layer) |
| `tent` ✅ | tent | craft@loom (cloth) | camp shelter |
| `fireplace` ✅ | fireplace | craft@stonecutter (stone+brick) | hearth (overlap w/ `campfire` décor + `stove`) |

## Explosives (mining)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `tnt` ✅ | TNT | craft@workbench (coal+...) | blast-mining (mechanic — backlog) |
| `powder_keg` ✅ | powder keg | craft@workbench (coal+...) | bigger blast — overlap w/ `tnt` |

## Electric & weather (bought expansion, D14)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `antenna` ✅ | antenna | **buy** (electricity expansion) | powered |
| `radar_dish` ✅ | radar dish | **buy** (electricity expansion) | powered/weather |
| `weather_console` ✅ | weather console | **buy** | reads/controls weather flavor |

## Beekeeping hives (the beekeeping system — backlog mechanic)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `beehive_basic` ✅ | basic hive | craft@workbench (plank) | T1 |
| `beehive_medium` ✅ | medium hive | craft@sawmill (plank+copper_bar) | T2 |
| `beehive_large` ✅ | large hive | craft@sawmill (plank+copper_bar) | T3 |
| `beehive_deluxe` ✅ | deluxe hive | **buy/unlock** | T4 |

*(Harvest with a `bee_smoker` (tools.md); process honeycomb at the `honey_extractor` station (crafting.md).)*

## NPC vendors (shop occupants — category `structure`, `interaction_type:"shop"`)
The village vendors are placed occupants, not crafted — listed here so the registry homes them. Roster +
stock = `../DECISIONS.md` D25/D26 + `merchants.md`; placeholder player-model art until distinct NPC sprites land.
| id | role | source 🔵 | notes |
|---|---|---|---|
| `general_store_merchant` ✅ | General Store (Marjoram) | placed (village) | items: seeds/tools/calm_spray; buys material/food |
| `bug_dealer` ✅ | Bug Dealer | placed (village) | bugs: buy live (`species.sell_price`) + dead; sells a few back |
| *(coming D26)* `blacksmith`/`carpenter`/`weaver`/`stonemason`/`modern_wares`/`fisherman`/`mayor`/`ecologist`/`miners_outpost` | village + mining vendors | placed | see `_village_assignments.md` |

---

**Scope:** 76 — 13 fences/gates, 7 walls, 4 doors/windows, 16 signs, 4 wells/mills, 4 docks/boats, 6 mining rigs,
6 bug-catching, 7 farm/utility, 2 explosives, 3 electric/weather, 4 hives. Material tiers route to
workbench/sawmill/stonecutter/anvil; the **electric line is buy-only** (D14); explosives + mining-haul + beekeeping
are **backlog mechanics** (the placeables exist; the systems aren't wired). Sign/fence/wall variants carry overlap
notes for **your** prune call — nothing cut here.

## Stonemason sign (D26)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `sign_mason` ✅ | stonemason shop sign (2-wide) | craft@workbench (wood) | chisel-and-mallet emblem |
