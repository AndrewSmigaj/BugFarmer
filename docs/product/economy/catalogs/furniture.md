# Furniture — the catalog (drafted 2026-06-26)

Placed décor-with-a-use: seating, tables, beds, kitchen pieces, and indoor lighting for the **home-plot /
build** layer. Cost model + stations in [`../crafting.md`](../crafting.md); who sells what in
[`../merchants.md`](../merchants.md); décor-bonus rules in [`../DECISIONS.md`](../DECISIONS.md) (**D5**: décor
tags a bonus *type*; values deferred. **D19**: the `*_fancy` tier is **buy/unlock**, not early-craftable).

**✅ = id exists in `placeables.json` today** (all rows below are ✅ — this page is the as-built furniture set).
`source` is the **proposed** obtainment (🔵 designed, not yet wired): `craft@station` / `buy@npc` / `unlock`.
Containers (dresser, bookshelf, cabinet…) are **not here** — a container is its own thing → [`containers.md`](containers.md).

> **Village subset (D17/D19):** the two active zones furnish a modest home — `bed_basic`, `chair_wood`/
> `stool_wood`, `table_wood`, a `stove`, `candle`/`lantern`, plus storage. Everything fancy/marble/velvet is
> later-game buy/unlock and listed here for the build layer, not the starting village.

---

## Seating
| id | role | source 🔵 | notes |
|---|---|---|---|
| `stool_wood` ✅ | basic stool | craft@workbench (wood) | village starter |
| `stool_stone` ✅ | stone stool | craft@stonecutter | overlap w/ `stool_wood` — your call which the village uses |
| `log_seat` ✅ | rustic seat | craft@workbench (wood) | camp/outdoor flavor |
| `chair_wood` ✅ | basic chair | craft@workbench (wood) | village starter |
| `chair_cushioned` ✅ | comfy chair | craft@sawmill (plank+cloth) | mid |
| `chair_fancy` ✅ | fancy chair | **buy/unlock** (D19) | parlor set |
| `rocking_chair` ✅ | rocker | craft@sawmill (plank) | cozy bonus candidate (D5) |
| `bench` ✅ | wooden bench | craft@workbench (wood) | 2-seat |
| `bench_padded` ✅ | padded bench | craft@sawmill (plank+cloth) | mid |
| `bench_stone` ✅ | stone bench | craft@stonecutter | garden/outdoor |
| `armchair` ✅ | armchair | craft@sawmill (plank+cloth) | living set |
| `armchair_fancy` ✅ | wingback | **buy/unlock** (D19) | parlor set |
| `loveseat` ✅ | 2-seat sofa | craft@sawmill (plank+cloth) | living set |
| `sofa` ✅ | sofa | craft@sawmill (plank+cloth) | living set |
| `sofa_modern` ✅ | modern sofa | **buy/unlock** | style variant — overlap w/ `sofa` |
| `sofa_fancy` ✅ | velvet sofa | **buy/unlock** (D19) | parlor set |
| `chaise_lounge` ✅ | chaise | **buy/unlock** | lounge |
| `ottoman` ✅ | footstool | craft@sawmill (plank+cloth) | pairs w/ armchair |
| `throne` ✅ | throne | **buy/unlock** (prestige) | trophy seat |

## Tables & surfaces
| id | role | source 🔵 | notes |
|---|---|---|---|
| `table_wood` ✅ | basic table | craft@workbench (wood) | village starter |
| `table_stone` ✅ | stone table | craft@stonecutter | overlap w/ `table_wood` |
| `coffee_table` ✅ | low table | craft@sawmill (plank) | living set |
| `side_table` ✅ | end table | craft@workbench (wood) | pairs w/ seating |
| `dining_table_fancy` ✅ | carved dining table | **buy/unlock** (D19) | dining set |
| `counter` ✅ | kitchen counter | craft@sawmill (plank) | kitchen |
| `counter_fancy` ✅ | marble counter | **buy/unlock** (D19) | kitchen, premium |
| `kitchen_island` ✅ | island bench | craft@sawmill (plank) | kitchen |
| `bar_cart` ✅ | drinks cart | **buy/unlock** | parlor |
| `map_table_big` ✅ | map table | craft@sawmill (plank) | study/HQ flavor |

## Beds (set home — `bed` is the spawn anchor, D-char)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `bed_basic` ✅ | basic bed | craft@workbench (wood+cloth) | **village starter; sets home** |
| `cot` ✅ | camp cot | craft@workbench (wood+cloth) | cheap/temporary bed |
| `bunk_bed` ✅ | bunk | craft@sawmill (plank+cloth) | space-saver |
| `bed_canopy` ✅ | canopy bed | **buy/unlock** | premium |
| `bed_fancy` ✅ | fancy bed | **buy/unlock** (D19) | premium |

## Kitchen & appliances
| id | role | source 🔵 | notes |
|---|---|---|---|
| `stove` ✅ | stove | craft@anvil (iron_bar) | village cooking flavor (cooking_pot is the real station) |
| `stove_wood` ✅ | wood stove | craft@workbench (wood+stone) | rustic — overlap w/ `stove` |
| `range_stove` ✅ | range | **buy/unlock** | premium kitchen |
| `sink` ✅ | kitchen sink | craft@anvil (iron_bar) | kitchen |
| `keg` ✅ | keg | craft@sawmill (plank+copper_bar) | artisan-goods flavor (see crafting keg/preserves) |

## Bath & vanity
| id | role | source 🔵 | notes |
|---|---|---|---|
| `bathtub` ✅ | bathtub | **buy/unlock** | bathroom |
| `vanity` ✅ | vanity table | **buy/unlock** | bedroom (overlap w/ `dresser` container — vanity is décor, dresser stores) |
| `grandfather_clock` ✅ | tall clock | **buy/unlock** (prestige) | hall décor |

## Hobby / work display (the bug-collector flavor)
| id | role | source 🔵 | notes |
|---|---|---|---|
| `sawhorse` ✅ | work trestle | craft@workbench (wood) | workshop flavor |
| `planter_box` ✅ | indoor planter | craft@workbench (wood) | grow herbs/flowers indoors |
| `shop_shelving` ✅ | shop shelves | craft@sawmill (plank) | market-stall display |
| `specimen_shelf` ✅ | specimen shelf | craft@sawmill (plank) | bug-collection display (overlap w/ `specimen_case` décor) |
| `bug_terrarium_big` ✅ | large terrarium | craft@workbench (wood+glass) | living bug display (overlap w/ `bug_terrarium` décor — big vs small) |

## Indoor lighting (the few small sources, D12)
Light is kept deliberately small — a handful of radii. Held/world torches: see [`tools.md`](tools.md) (A2).
| id | role | source 🔵 | notes |
|---|---|---|---|
| `candle` ✅ | candle | craft@workbench (beeswax) | smallest radius |
| `candelabra` ✅ | candelabra | craft@anvil (copper_bar) | table light |
| `lantern` ✅ | lantern | craft@workbench (copper_bar+glass) | portable-look set light |
| `lamp_table` ✅ | table lamp | craft@sawmill (plank+cloth) | mid radius |
| `lamp_floor` ✅ | floor lamp | craft@sawmill (plank+cloth) | mid radius |
| `lamp_floor_fancy` ✅ | brass floor lamp | **buy/unlock** | premium |
| `lamp_post` ✅ | lamp post | craft@anvil (iron_bar) | outdoor/path light |
| `torch` ✅ | torch | craft@workbench (wood+coal) | basic placed light; also a held placer (tools.md) |
| `torch_wall` ✅ | wall torch | craft@workbench (wood+coal) | wall-mounted (occupant variant of `torch`) |

---

**Scope:** 56 pieces — 19 seating, 10 tables/surfaces, 5 beds, 5 kitchen, 3 bath/vanity, 5 hobby-display, 9
lighting. The base (wood/stone) tier crafts at workbench/sawmill/stonecutter; the `*_fancy`/marble/velvet/
premium tier is **buy/unlock** (D19). Décor bonuses are tagged-but-unvalued (D5). Overlap notes flag look-alikes
(`stool_wood`/`stool_stone`, `sofa`/`sofa_modern`, `stove`/`stove_wood`) for **your** prune call — nothing cut here.
