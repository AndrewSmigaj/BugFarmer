# Decoration — the catalog (drafted 2026-06-26)

Pure-cosmetic placeables: statues, rugs, garden ornaments, display pieces, clutter. They carry **no use** beyond
looks + a **décor bonus tag** (D5: décor tags a bonus *type*; values deferred). Cost/stations in
[`../crafting.md`](../crafting.md); sellers in [`../merchants.md`](../merchants.md).

**✅ = id exists today** (all rows ✅). `source` is the **proposed** 🔵 obtainment. Some pieces are **world
clutter** found pre-placed in zones (cave moss, ore piles, tumbleweed) rather than crafted.

> **Backlogged (your call):** the **rock/cave-decor rework** ("leave decor as-is for now") — `sandstone_formation`,
> `cave_moss`, `ore_pile` etc. are catalogued here so nothing is undocumented, but their **art/placement rework is
> deferred** to BACKLOG. No décor is cut or changed by this page.

---

## Statues & trophies
| id | role | source 🔵 | notes |
|---|---|---|---|
| `statue_stone` ✅ | stone statue | craft@stonecutter | generic |
| `statue_bug` ✅ | bug statue | craft@stonecutter | collector trophy |
| `statue_founder` ✅ | founder statue | **unlock** (prestige) | town landmark |
| `cat_statue` ✅ | cat statue | buy/unlock | flavor |
| `suit_of_armor` ✅ | standing armor | **buy/unlock** | hall trophy (overlap w/ armor display) |
| `cow_skull` ✅ | cow skull | find / buy | desert flavor |

## Rugs & soft furnishing
| id | role | source 🔵 | notes |
|---|---|---|---|
| `rug` ✅ | small rug | craft@loom (cloth) | floor |
| `rug_large` ✅ | large rug | craft@loom (cloth) | floor — size variant |
| `rug_round` ✅ | round rug | craft@loom (cloth) | floor — shape variant |
| `room_divider` ✅ | folding screen | craft@sawmill (plank+cloth) | partition |
| `awning` ✅ | awning | craft@loom (cloth) | shopfront/window |
| `laundry_line` ✅ | laundry line | craft@workbench (fiber) | yard flavor |

## Garden & outdoor
| id | role | source 🔵 | notes |
|---|---|---|---|
| `birdbath` ✅ | birdbath | craft@stonecutter | garden |
| `fountain` ✅ | fountain | craft@stonecutter (stone+copper_bar) | centerpiece (overlap w/ `well` structure) |
| `potted_plant` ✅ | potted plant | craft@workbench (wood) + a plant | indoor green |
| `plant_large` ✅ | potted palm | buy/unlock | large indoor green — overlap w/ `potted_plant` |
| `window_box` ✅ | window box | craft@workbench (wood) + flowers | window flowers |
| `garden_border_log` ✅ | log bed edging | craft@workbench (wood) | bed border |
| `garden_border_stone` ✅ | stone bed edging | craft@stonecutter | bed border — material variant |
| `hay_bale` ✅ | hay bale | craft@workbench (fiber) / farm | farm flavor |
| `scarecrow` ✅ | scarecrow | craft@workbench (wood+cloth) | farm flavor (cosmetic) |
| `tumbleweed` ✅ | tumbleweed | **find** (desert) | desert clutter |
| `dead_bush` ✅ | dead bush | **find** (desert/waste) | clutter |
| `lily_pad` ✅ | lily pad | **find** (water) | pond surface deco |

## Display & hobby
| id | role | source 🔵 | notes |
|---|---|---|---|
| `specimen_case` ✅ | specimen case | craft@sawmill (plank+glass) | bug display (overlap w/ `specimen_shelf` furniture) |
| `bug_terrarium` ✅ | bug terrarium | craft@workbench (wood+glass) | small living display (`bug_terrarium_big` is the furniture-size one) |
| `aquarium` ✅ | aquarium | craft@sawmill (glass) | fish display |
| `easel` ✅ | easel | craft@workbench (wood) | studio flavor |
| `globe` ✅ | globe | buy/unlock | study flavor |
| `telescope` ✅ | telescope | buy/unlock | study/observatory |
| `gramophone` ✅ | gramophone | buy/unlock | parlor |
| `vase` ✅ | vase | craft@stonecutter / buy | tabletop |
| `mirror_standing` ✅ | standing mirror | buy/unlock | bedroom |

## Nautical / dock
| id | role | source 🔵 | notes |
|---|---|---|---|
| `anchor_decor` ✅ | anchor | find / buy | dock flavor |
| `ship_wheel` ✅ | ship's wheel | buy | dock flavor |
| `fishing_net` ✅ | drying net | craft@loom (fiber) | dock dressing (overlap w/ `fly_netting`/`net_post` structures) |
| `fishing_pole` ✅ | fishing pole (deco) | craft@workbench (wood) | dock dressing — décor, not the `fishing_rod` tool |

## Camp & misc
| id | role | source 🔵 | notes |
|---|---|---|---|
| `campfire` ✅ | campfire | craft@workbench (wood+stone) | camp light/flavor |
| `campfire_spit` ✅ | campfire spit | craft@workbench (wood) | camp — overlap w/ `campfire` |
| `ant_eggs` ✅ | ant eggs | **find** (ant zones) | bug-themed natural clutter |

## Mining & cave clutter (rework backlogged)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `ore_pile` ✅ | ore pile | **find** (mines) | mining clutter |
| `ore_sack` ✅ | ore sack | **find** / craft@loom | mining clutter (also `backpack`'s icon source) |
| `mining_bucket` ✅ | mining bucket | craft@workbench (wood) | mining clutter |
| `water_bucket` ✅ | water bucket | craft@workbench (wood) | utility clutter |
| `column_marble` ✅ | marble column | craft@stonecutter (marble) | grand-hall pillar |
| `sandstone_formation` ✅ | sandstone formation | **find** (desert) | natural rock decor (rework backlogged) |
| `cave_moss` ✅ | cave moss | **find** (caves) | natural cave dressing (rework backlogged) |

---

**Scope:** 47 cosmetic pieces — statues, rugs, garden, display, nautical, camp, mining/cave clutter. Décor bonuses
are tagged-but-unvalued (D5). Craftables route to workbench/sawmill/stonecutter/loom; trophies + premium pieces
are buy/unlock; natural clutter is world-placed (find). Look-alikes (`rug`/`rug_large`/`rug_round`,
`potted_plant`/`plant_large`, `specimen_case`/`specimen_shelf`, `campfire`/`campfire_spit`) carry overlap notes
for **your** prune call. The rock/cave-decor **rework** stays backlogged — this page only documents.

## Weaver shop décor (D26 — placeholder art)
| id | role | source 🔵 |
|---|---|---|
| `dress_form` ✅ | tailor's mannequin / garment display | buy@weaver · craft@sewing_machine |
| `fabric_bolt` ✅ | stacked bolt of woven cloth | buy@weaver · craft@loom |
| `yarn_basket` ✅ | basket of dyed yarn (a textile container) | buy@weaver · find |

## Rugs, mannequins & yard décor (D26 — Weaver/Stonemason build-out)
| id | role | source 🔵 |
|---|---|---|
| `rug_sm_sq` ✅ | small square rug (2×2, red geometric) | buy@weaver · craft@loom |
| `rug_sm_rect` ✅ | small rug (3×2, blue floral) | buy@weaver · craft@loom |
| `rug_md_sq` ✅ | medium square rug (3×3, green medallion) | buy@weaver · craft@loom |
| `rug_md_rect` ✅ | medium rug (3×4, kilim stripes) | buy@weaver · craft@loom |
| `rug_lg_rect` ✅ | large rug (3×5, ornate persian) | buy@weaver · craft@loom |
| `rug_runner` ✅ | runner rug (2×4, neutral woven) | buy@weaver · craft@loom |
| `mannequin_white` ✅ | plain white display mannequin (blob-form) | display (weaver) · find |
| `mannequin_cream` ✅ | plain cream display mannequin | display (weaver) · find |
| `mannequin_dress_red` ✅ | dressed mannequin (red) | display (weaver) · find |
| `mannequin_dress_teal` ✅ | dressed mannequin (teal) | display (weaver) · find |
| `brick_pile` ✅ | stack of clay bricks (yard clutter) | craft@stonecutter · find |
| `statue_unfinished` ✅ | half-carved WIP statue (storytelling prop) | display (stonemason) · find |
| `electric_heater` ✅ | modern electric heater (showroom display) | **buy** (electricity expansion, D14) |

## Bug life-stage nursery (display-only)
Rendered by the brood system (`BroodManager`, OpCode 104) at a breeding source as the nursery develops
egg → larva → [pupa] → adult. Not obtainable — display-only decorations, one per species stage.
| id | role | source 🔵 | notes |
|---|---|---|---|
| `fly_eggs` ✅ | fly egg clutch | sim (brood nursery) | fly stage 1 |
| `fly_larvae` ✅ | fly maggots | sim (brood nursery) | fly stage 2 |
| `fly_pupa` ✅ | fly pupae | sim (brood nursery) | fly stage 3 |
| `butterfly_eggs` ✅ | butterfly eggs | sim (brood nursery) | butterfly stage 1 (milkweed) |
| `butterfly_caterpillar` ✅ | caterpillars | sim (brood nursery) | butterfly stage 2 (milkweed) |
| `butterfly_chrysalis` ✅ | chrysalis | sim (brood nursery) | butterfly stage 3 (milkweed) |
| `beetle_eggs` ✅ | beetle eggs | sim (brood nursery) | beetle stage 1 |
| `beetle_larvae` ✅ | beetle grubs | sim (brood nursery) | beetle stage 2 |
| `beetle_pupa` ✅ | beetle pupae | sim (brood nursery) | beetle stage 3 |
| `millipede_eggs` ✅ | millipede eggs | sim (brood nursery) | millipede stage 1 |
| `millipede_larvae` ✅ | young millipedes | sim (brood nursery) | millipede stage 2 (no pupa) |
| `centipede_eggs` ✅ | centipede eggs | sim (brood nursery) | centipede (Phase-3 brood) |
| `centipede_larvae` ✅ | young centipedes | sim (brood nursery) | centipede (Phase-3 brood) |
| `wasp_eggs` ✅ | wasp eggs | sim (nest brood) | wasp nest stage 1 |
| `wasp_grubs` ✅ | wasp grubs | sim (nest brood) | wasp nest stage 2 |
