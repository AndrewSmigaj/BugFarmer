# Containers — the catalog (drafted 2026-06-26)

Things that **hold items**: chests, wardrobes, shelves, the worn backpack. A placeable is a container when its
`world.container` block is set (`slots`, optional `filter`) — that's what opens a storage grid in-game (the
container system is as-built; see [`../../architecture/architecture_inventory.md`](../../architecture/architecture_inventory.md)).
Cost/stations in [`../crafting.md`](../crafting.md); sellers in [`../merchants.md`](../merchants.md).

**✅ = id exists today.** `source` is the **proposed** 🔵 obtainment. A filtered container only accepts items
tagged to match (`clothing`/`food`/`book`/`drink`) — a design hook for themed storage, already in the data.

> **Village subset:** a `chest_wood` (or `crate`/`barrel`) + a `dresser` cover the starting home. Backpack is an
> early **buy** that grows carry capacity (`slot_bonus`). Fancy/themed pieces are the build-out layer.

---

## General chests & crates (no filter)
| id | slots | source 🔵 | notes |
|---|---|---|---|
| `crate` ✅ | 12 | craft@workbench (wood) | cheapest box; village starter |
| `barrel` ✅ | 12 | craft@workbench (wood) | overlap w/ `crate` — your call |
| `chest_wood` ✅ | 24 | craft@workbench (wood ×8) | the standard home chest |
| `chest_mossy` ✅ | 18 | **find** (ruins/cave loot) | found variant — flavor |
| `chest_iron` ✅ | 30 | craft@anvil (iron_bar) | biggest; mid-game upgrade |
| `cabinet` ✅ | 12 | craft@sawmill (plank+glass) | display cabinet (glass front) |

## Clothing & wardrobe (filter: clothing)
| id | slots | source 🔵 | notes |
|---|---|---|---|
| `dresser` ✅ | 12 | craft@sawmill (plank) | village clothing storage |
| `dresser_fancy` ✅ | 12 | **buy/unlock** (D19) | carved variant |
| `wardrobe` ✅ | 12 | craft@sawmill (plank) | tall clothing store — overlap w/ `dresser` |
| `coat_rack` ✅ | 8 | craft@workbench (wood) | small clothing rack |

## Kitchen & food (filter: food)
| id | slots | source 🔵 | notes |
|---|---|---|---|
| `cupboard` ✅ | 12 | craft@sawmill (plank) | dry goods (no filter in data — general) |
| `fridge` ✅ | 12 | **buy/unlock** | keeps food (flavor); premium |
| `produce_crate` ✅ | 8 | craft@workbench (wood) | farm produce |
| `fish_crate` ✅ | 8 | craft@workbench (wood) | catch storage — overlap w/ `produce_crate` |

## Study, bedroom & themed
| id | slots | source 🔵 | notes |
|---|---|---|---|
| `bookshelf` ✅ | 12 (book) | craft@sawmill (plank) | books only |
| `bookshelf_fancy` ✅ | 12 (book) | **buy/unlock** (D19) | mahogany variant |
| `desk` ✅ | 8 | craft@sawmill (plank) | writing desk w/ drawers |
| `nightstand` ✅ | 6 | craft@workbench (wood) | bedside |
| `nightstand_fancy` ✅ | 6 | **buy/unlock** | ornate variant |
| `wine_rack` ✅ | 8 (drink) | craft@sawmill (plank) | drinks only |

## Worn capacity
| id | effect | source 🔵 | notes |
|---|---|---|---|
| `backpack` ✅ | `slot_bonus` +10 carry slots (equips to the backpack slot) | **buy@trader** | per the design: backpack is **bought**; a cheaper craftable **`sack`** is 🔵 designed (not yet an item) |

## Loot prop (not a storage UI)
| id | behavior | notes |
|---|---|---|
| `apple_crate` ✅ | breakable occupant — drops `apple` ×2 + `wood` (needs an axe) | category `storage` but it has **no `world.container`** — it's a *break-for-loot* prop, not a player chest. Documented here so it isn't orphaned; **your call** whether to recategorize it as décor. |

---

**Scope:** 20 placed containers (6 general, 4 clothing, 4 food, 6 study/bedroom/themed) + the worn `backpack` +
the `apple_crate` loot prop. Filters (`clothing`/`food`/`book`/`drink`) are a themed-storage hook already in the
data. Look-alikes (`crate`/`barrel`, `dresser`/`wardrobe`, `produce_crate`/`fish_crate`) carry overlap notes for
**your** prune call — nothing cut. The designed `sack` (cheap craftable backpack) is the one 🔵 not-yet-built id.

## Storage chests (D26 — Weaver pass)
| id | role | slots | source 🔵 |
|---|---|---|---|
| `chest` ✅ | small 1×1 storage chest | 12 | craft@workbench (wood) |
| `trunk` ✅ | wide 2×1 storage trunk (more than a chest) | 36 | craft@sawmill (plank) · buy |
| `yarn_basket` ✅ | textile basket (a real container, filter:textile) | 4 | buy@weaver · find |
