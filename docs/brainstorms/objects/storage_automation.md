# Storage & Automation — Brainstorm

Storage furniture (poor→fancy) plus the simple, slow, capacity-capped automation the plot allows.
Design only.

Read alongside:
- `docs/product/design/game_design.md` §11 in full — especially §11.1 hard constraints (no fast/free
  automation), §11.2 NPC workers, §11.4 autonet, §11.5 furniture idle boosts, §11.6 power/linked
  placement, §11.7 stove capacity.
- Existing ids: `chest_wood`, `chest_iron`, `chest_mossy`, `barrel`, `crate`, `apple_crate`,
  `ore_sack`, `ore_pile`, `cupboard`, `wardrobe`, `cabinet`, `bookshelf`, `autonet`, `mine_cart`,
  `mine_rail`, `hopper`-adjacent (`mining_bucket`), `windmill` (power), `wheelbarrow`.

## Rules this file follows
- **Automation is slow, capped, and plot-only.** Every "auto" object below: deliberately slow, fills
  a capacity and STOPS until emptied, never out-produces hands-on play (§11.1, §11.4). It eases
  tedium, it does not play the game for you.
- **Containment is never automated/bought** — none of this provides bug containment (§11.1, §11.3).
- Power is **opt-in** (§11.6): a coverage aura, linked placement by drawn line, machines are
  fuel-fed OR electric. Don't add a schema power flag ahead of the feature.
- Storage varies poor→fancy; capacity/quality is the value axis.

---

## 1. STORAGE — containers (poor→fancy)

### 1.1 Chests & boxes
| id | one-line | tier | capacity feel |
|----|----------|------|---------------|
| `crate` *(exists)* | a plain wooden crate | poor | small bulk store |
| `chest_wood` *(exists)* | banded wooden chest | common | the baseline chest |
| `chest_iron` *(exists)* | reinforced iron chest | mid | bigger, sturdier |
| `chest_mossy` *(exists)* | a found mossy chest | mid | flavor/loot chest |
| `chest_steel` | a heavy steel strongbox | high | large capacity |
| `chest_ornate` | a carved hardwood chest with brass | fancy | large + showpiece (idle boost) |
| `lockbox` | a small lockable cash/valuables box | poor | secure small items |
| `toolbox` | a carry tote for tools | poor | tool-specific store |

### 1.2 Barrels, sacks, baskets
| id | one-line | tier | use |
|----|----------|------|-----|
| `barrel` *(exists)* | a hooped wooden barrel | poor | bulk liquids/dry goods |
| `barrel_iron` | an iron-banded heavy barrel | mid | sturdier bulk store |
| `sack` | a tied burlap sack | poor | grain/seed bulk |
| `ore_sack` *(exists)* | an ore-filled sack | poor | mining bulk (cave set) |
| `basket_storage` | a large woven storage basket | poor | produce/harvest |
| `harvest_bin` | a big slatted produce bin | common | farm output buffer |
| `apple_crate` *(exists)* | a fruit crate | poor | produce flavor |

### 1.3 Shelves, racks, cabinets (display + store)
| id | one-line | tier | use |
|----|----------|------|-----|
| `shelf_wall` | a simple wall shelf | poor | small items on display |
| `shelf_unit` | a freestanding shelving unit | common | general storage |
| `bookshelf` *(exists)* | a books bookcase | common | books/decor store |
| `cupboard` *(exists)* | a kitchen cupboard | common | dishes/ingredients |
| `cabinet` *(exists)* | a glass-front display cabinet | mid | show valuables (idle boost) |
| `wardrobe` *(exists)* | a clothes wardrobe | mid | gear/clothes store |
| `tool_rack` *(exists)* | a wall tool rack | poor | hang tools (cave/shop set) |
| `pantry_cabinet` | a tall food pantry | mid | bulk food store |
| `display_case` | a glass museum case | fancy | prized specimens/fish (bug crossover, idle boost) |

### 1.4 Bulk / large-scale storage
| id | one-line | tier | use |
|----|----------|------|-----|
| `silo` | a tall grain silo | high | huge grain/feed capacity (plot) |
| `grain_bin` | a metal grain hopper-bin | mid | medium bulk grain |
| `water_tank` | a big water storage tank | mid | feeds irrigation/sprinklers |
| `warehouse_shelving` | tall industrial racking | high | big general store (plot/industrial) |
| `cold_store` | an insulated cold room cabinet | high | keeps perishables long |

---

## 2. AUTOMATION — movement & collection (slow, capped)

### 2.1 Conveyance (move items between machines/storage)
| id | one-line | role |
|----|----------|------|
| `conveyor_belt` | a slow powered belt segment | carries items in a line toward an output (§11.6 electric) |
| `chute` | a passive gravity slide | drops items down to a chest/hopper, no power |
| `hopper` | a funnel that pulls items into the thing below | feed/buffer between machines; capacity-capped |
| `pipe_segment` | a pipe for liquids (water/oil/honey) | route fluids; linked-placement line (§11.6) |
| `mine_cart` *(exists)* + `mine_rail` *(exists)* | rail cart + track | move bulk ore (cave set); rail uses linked placement |
| `wheelbarrow` *(exists)* | a push barrow | manual bulk move (the non-automated baseline) |

### 2.2 Collectors & sorters
| id | one-line | role |
|----|----------|------|
| `collector_basic` | a slow pickup that gathers nearby drops into itself | eases pickup tedium; fills then stops |
| `auto_harvester` | a slow arm/collector that picks ripe crops in range | plot crop automation; capped output (farming_tools.md §8) |
| `egg_collector` | a slow tray that gathers bug egg piles in range | bug-farm chore relief; capped |
| `sorter` | a single-output filter that routes one item type | sort a mixed stream into the right chest |
| `sorter_multi` | a multi-lane sorting bench | sorts several types; bigger, electric |
| `output_chest` | a chest flagged as a machine's drop target | where slow automation deposits |
| `intake_bin` | a bin machines/NPCs pull inputs from | feed buffer for a production chain |

### 2.3 The sanctioned auto-catcher & kin (bug crossover)
| id | one-line | role |
|----|----------|------|
| `autonet` *(exists)* | a fan + tank that slowly sucks nearby flies into an internal net | THE allowed auto-catcher (§11.4): slow, capacity-capped, empties manually |
| `auto_collector_zone` | a slow zone-specific passive collector (in the autonet spirit) | other zones/bugs may get their own; same slow/capped rules |
| `bait_dispenser` | a slow hopper that re-baits a trap | keeps a placed trap stocked; doesn't speed the catch |

---

## 3. POWER & DISTRIBUTION (opt-in, §11.6)

Hints only — the system isn't built; don't add schema flags yet.
| id | one-line | role |
|----|----------|------|
| `windmill` *(exists)* | a tall windmill | wind power source |
| `waterwheel` | a river/stream waterwheel | hydro power source |
| `generator_fuel` | a fuel-burning generator | burns wood/coal for power |
| `power_unit` | a generator/battery distribution box | energizes cells within a radius (coverage aura) |
| `battery_bank` | a bank of batteries | stores power, smooths supply |
| `power_pole` | a pole the linked-placement line snaps to | extend coverage; drawn line (§11.6) |
| `rail_track` | track laid by linked placement | machines that need rail (carts, some processors) |

Power UX recap (from §11.6, for whoever builds it): linked placement draws a LINE start→end,
rejected if it clips an occupied cell, shows a ghost while dragging; coverage is a highlighted aura;
electric machines must sit inside it; it must be obvious at a glance which objects need power vs fuel.

---

## 4. NPC WORKER hooks (§11.2 — physical entities, never fully solve)

Not objects per se, but they pair with this set:
- **Lumberjack** — fells trees → drops into a nearby `output_chest`.
- **Miner** — processes ore at a station; feeds `ore_*` storage.
- **Bug Handler** — repairs fences, resets traps, calms escapees (containment upkeep, NOT catching).
- **Farmhand** (proposed) — waters/weeds slowly.
- **Hauler** (proposed) — carries between `intake_bin`/`output_chest` (a walking conveyor; slow).

---

## Open questions / follow-ups
- Per-object capacity numbers + automation tick rates belong in the economy/automation proposal.
- Which storage/display pieces also grant §11.5 idle boosts (cabinet, display_case, chest_ornate) —
  flag when these reach the catalog.
- Power flags + fuel-vs-electric tagging are deferred to the §11.6 feature; this doc only labels intent.
