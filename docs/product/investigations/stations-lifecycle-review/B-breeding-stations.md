# B — Breeding Stations lifecycle audit (village_21_B)

Assessment only, no code changed. Every claim is anchored at `file:line` in the real source as of this
branch. Scope: the five breeding-station types the player can interact with, audited for OPEN / CREATE-
MATURE-HATCH / TAKE / DEPOSIT-BACK / TEARDOWN / RESIDENTS / DETERMINISM.

The panel is ONE unified `CraftingPanel` dispatched by `interaction_type`
(`craft` · `storage` · `station`=compost · `nursery`=wasp-nest/milkweed · `beehive`) —
`CraftingPanel.cs:178` gates the five accepted types; `BuildContent` fans out at `CraftingPanel.cs:291-295`.

## Occupants actually in the committed save
Scanned all 64 `nakama/data/zones/village_21_B/chunk_*.json`: **7 compost_bin, 29 milkweed, 7 wasp_nest,
4 beehive_basic** — and **NO literal `nest` occupant, no hornet_nest, no bee_hive_wild**. The zone bug
roster (`zone.json` → `bug_spawning.species_caps`) is `fly_common, butterfly_meadow, wasp_common,
centipede_garden, millipede, beetle_carrion` — **no `bee_honey`**.

## Per-station verdict table

| Station | interaction_type | Opens? | Auto-breed engine | Take (113) | Deposit-back (114) | Teardown | Residents shown | Verdict |
|---|---|---|---|---|---|---|---|---|
| **compost_bin** | `station` | Yes | Yes — flies lay `kind:"station"` brood, egg→maggot→**pupa**→fly | Yes (fly_eggs/larvae/pupa sprites) | Top-up only (can't seed empty) | Brood cleared; **StationState + food level NOT cleared** | Never (dead "INSIDE" header) | **COMPLETE** w/ 2 smells |
| **wasp_nest** | `nursery` | Yes | Yes — resident provisions nest brood, egg→grub→**pupa**→resident grows | Yes (grub→`wasp_larvae` dedicated item) | Yes — **seeds empty nest** or tops up | Brood perishes, resident spills **aggressive** | Yes (real resident count) | **COMPLETE** (reference impl) |
| **milkweed** | `nursery` | Yes | Yes — butterfly lays `kind:"host_plant"`, egg→caterpillar→chrysalis→butterfly | Yes (butterfly sprites) | **Cannot seed empty milkweed** (top-up only) | Brood cleared; HostPlantState leaks (harmless) | Never (dead "INSIDE" header) | **HALF-WORKING** (place-back + residents) |
| **beehive_basic** | `beehive` | Yes | Mechanism complete, but **inert in this zone** (no bee colony to claim the box) | n/a (bee has no stage sprites) | n/a | Harvest returns "no honeycomb" | Only if a bee colony claims it — never here | **HALF-WORKING** (zone-content dead) |
| **ground brood** (`ground_pile`) | — (no occupant) | **No — not clickable** | Yes server-side (fly on rotten fruit / free-roamer clutch) | Unreachable | Unreachable | Auto-retires when hatched out | n/a | **MISSING** (player surface) |

---

## Detailed findings

### 1. Compost bin — COMPLETE, richest station, two real smells

**Open / deposit / process — all working.**
- Right-click → `station` mode (`CraftingPanel.cs:178,199`), `BuildStationContent` (`CraftingPanel.cs:485`):
  description, COMPOST block (deposit grid + green fill bar + "Take compost"), divider, then the shared brood
  region. Fed by cached `StationUpdate(86)` + `BroodUpdate(104)` echoes — NO open request
  (`CraftingPanel.cs:222-224`), so state is shown from the pushed stream.
- Deposit: `StationDeposit(85)` → `handleStationDeposit` (`handlers_farming.go:1291`) validates against the
  rich `accepts` list (`placeables.json:4870-4904`), `InputCount++`, capacity 10.
- Process: `processStations` (`handlers_farming.go:1479`) converts one input→one `Fill` per `process_ticks`
  (300) and emits a deterministic `InfluenceFoodConsumed` level event (`:1517-1520`).

**Fly nursery — REAL.** `fly_common` (category `swarm`, no `predation`) lists `compost_bin` in both
feeding + reproducing attractions (`species.json:12-20`). A reproducing fly at a filled bin →
`reproduceSwarm` takes the visible-brood path (`match.go:90-97`) → `layIntoBrood` resolves
`kind:"station"` (`brood.go:76-77`) → `processBroods` climbs egg→maggot→**pupa**→adult (fly pupates, it has
`fly_pupa`: `species.json:62`, `broodPupates` at `brood.go:250-253`) → `hatchFromBrood` grows/mints a fly
swarm (`brood.go:302-367`).

**Take / take-compost — working.** `NurseryTake(113)` → `handleNurseryTake` grants the stage sprite id
(fly has no dedicated `*_item_id`, so `itemID = spriteID`: `handlers_nursery.go:56-58`). "Take compost" →
`CompostHarvest(115)` → `handleCompostHarvest` (`handlers_farming.go:1411`) take-all into `compost`, zeros
`Fill`+`FoodFrac`, and drops the deterministic food level to 0 with the SAME `AddFoodEvent` the feed loop
uses (`:1466-1468`).

**SMELL 1 (dead resident UI, severity: low-moderate).** `broodUpdateMessage` only sets `Residents` for
`SourceKind=="nest"` (`brood.go:417-424`); a compost brood is `"station"` → residents **always 0**. But the
shared `BuildBroodRegion` creates the **"INSIDE" header (`resHead`) unconditionally** (`CraftingPanel.cs:620-622`)
and `RefreshBrood` only toggles `_residentSlot`/`_residentLbl`, never `resHead` (`CraftingPanel.cs:666-674`).
Result: the compost (and milkweed) panel always shows an "INSIDE" header with nothing beneath it — visible
dead UI. Matches the doc's "residents at the compost bin: later" (`architecture_nursery_stations.md:126`).

**SMELL 2 (teardown doesn't zero the food, severity: moderate).** `breakOccupantAt` runs
`onBroodSourceRemoved` to clear the brood (`handlers_world.go:594`, `brood.go:388-396`) — good — **but never
deletes `state.Stations[key]` and never emits a food=0 event.** `FindNearbyFood` iterates `state.Stations`
directly and yields any bin with `Fill>0` as depletable food WITHOUT re-checking the occupant exists
(`resource_query.go:91-102`). So breaking a filled compost bin leaves a **phantom invisible food source**
(flies keep pathing to a bin that's gone) plus a soft-state leak, until bugs drain `Fill` or the server
restarts. Inconsistent with harvest, which DOES zero it. Deterministic-consistent across clients (no
desync), so this is a gameplay bug, not a sync bug.

Minor: the doc still calls compost "not built into the panel" (`architecture_nursery_stations.md:124`) —
**stale**, it IS in `station` mode now. And `Items/compost_icon.png` is still missing (doc `:27`).

### 2. Wasp nest — COMPLETE, the reference implementation

- Opens as `nursery` (`occupants.json:2472-2473`). Residents founded at chunk-load: `initNestsInChunk` →
  `speciesForNestOccupant` → `registerNestAt(dormant=false)` → `nestSpawnResident` (`nests.go:61-138`);
  the zone caps `wasp_common` at `max_nests:7`, matching the 7 placed nests.
- Breed loop: sated resident homes → `depositBrood` lays one nest egg (`nests.go:223-245`) → `processBroods`
  matures (wasp pupates: `wasp_pupa` `species.json:178`) → `hatchFromBrood` "nest" case grows the resident
  patrol (`brood.go:331-344`). `residents` field renders (`brood.go:417-424`).
- Take: eggs→`wasp_eggs`, grubs→**`wasp_larvae`** (the dedicated `larva_item_id`, `species.json:179`),
  pupae→`wasp_pupa` (`handlers_nursery.go:46-52`).
- Deposit-back: the ONE case that **seeds an empty station** — an empty nest's species is known via
  `NestState`, so `handleNurseryDeposit` creates the brood (`handlers_nursery.go:152-158`).
- Teardown: `onNestOccupantRemoved` perishes the brood + orphans the still-alive resident, which proximity-
  aggros the breaker (`nests.go:247-266`). Correct per doc.

**Smell (severity: low):** two species map `nest_occupant:"wasp_nest"` — `wasp_common` (`species.json:198`)
and `wasp_soldier` (`species.json:754`). `speciesForNestOccupant` iterates `sortedStringKeys`, so
`wasp_common` (alphabetically first) wins ALL wasp nests (`nests.go:37-55`). This is the known nest-hijack
shape (MEMORY: nest-occupant-hijack). Harmless here (only `wasp_common` is in the roster) but a latent trap
if `wasp_soldier` were ever wanted in a wasp_nest.

**Smell (severity: low):** `wasp_nest` breakable `drops:[]` (`occupants.json:2478`) while `hornet_nest`
drops `paper_nest`+`wasp_larvae` (`occupants.json:2499-2510`). Inconsistent teardown yield — breaking a
wasp nest gives nothing (you must harvest the brood via the panel first, which is the intended design, but
the asymmetry with hornet_nest is a content inconsistency).

### 3. Milkweed — HALF-WORKING (auto-breed fine; place-back + residents are holes)

- Opens as `nursery`, `host_plant:true` (`occupants.json:806-808`). `initHostPlantsInChunk`
  (`handlers_farming.go:1665`) registers a `HostPlantState`; `processHostPlants` regrows capacity
  (`:1691`).
- Auto-breed REAL: `butterfly_meadow` reproducing attraction is `milkweed` (`species.json` butterfly block).
  A breeding butterfly → `layIntoBrood` `kind:"host_plant"` (`brood.go:78-79`) → matures egg→caterpillar→
  **chrysalis**→butterfly (butterfly pupates: `butterfly_chrysalis` `species.json:135`). Take grants the
  butterfly stage sprites (`handlers_nursery.go`).

**GAP #3 confirmed — cannot seed an empty milkweed (severity: moderate).** `handleNurseryDeposit`: with no
active `BroodState` it falls to `NestStates[key]`, and a milkweed has NO NestState (it's a HostPlantState),
so the deposit is **rejected** (`handlers_nursery.go:151-158`). This is the doc-acknowledged limitation
(`architecture_nursery_stations.md:71`). Practical impact: 29 milkweed, most sitting empty most of the time
→ a player holding caterpillars can only place them into a milkweed that ALREADY has an active brood. The
rejection is silent (see UX gap below). This makes milkweed place-back effectively unusable in practice.

**GAP #1 (dead resident UI)** — same as compost: `host_plant` broods report `residents:0`, so the "INSIDE"
header is dead here too.

**Teardown:** brood cleared via `onBroodSourceRemoved`. The `HostPlantState` is **never swept** (no delete
anywhere — verified: no `delete(state.HostPlantStates…)` exists), so it leaks — but harmlessly:
`FindNearbyResources` reads the chunk anchor index (`resource_query.go:164-177`), so with the occupant gone
there's no food hit, no phantom. Pure soft-state leak, self-heals on restart.

**Doc-vs-data content gap (severity: low):** doc says milkweed teardown = "fiber + a seed chance (D24)"
(`architecture_nursery_stations.md:98`); the actual breakable drops `milkweed` ×1 only
(`occupants.json:816-822`). Not implemented.

### 4. Beehive_basic — HALF-WORKING (mechanism complete; inert in THIS zone) — GAP #2

- Opens as `beehive` (`placeables.json:1425`), `BuildBeehiveContent` = brood region + Harvest button
  (`CraftingPanel.cs:307-312`).
- Registered as a **dormant box**: `beehive_basic` ∈ `bee_honey.nest_occupants_extra`
  (`species.json:456-464`), so `speciesForNestOccupant` returns it as an EXTRA → `registerNestAt(dormant=true)`
  → empty NestState, no resident (`nests.go:92-104`).
- **GAP #2 confirmed:** `bee_honey` is NOT in the village_21_B roster and no `bee_hive_wild` is placed, so
  **no bee colony exists** to daughter-found into the box (`findClaimableBox` / `processNestFounding`,
  `nests.go:353,410-445`). The 4 boxes stay dormant **forever**: no residents, no brood, no honey. They are
  decorative. Harvest → `handleHiveHarvest` finds the dormant NestState, `Honey==0` → "No honeycomb in this
  hive yet" (`handlers_hive.go:49-52`).
- The MECHANISM is complete — a LIVE bee colony would claim a box, provision it, and make honey
  (`depositBrood` honey path `nests.go:231-241`). `bee_honey` has **no stage sprites** (`species.json`: none
  of `egg/larva/pupa_sprite_id`), so even a live bee nest deliberately hides the stage slots — the client
  handles that (`CraftingPanel.cs:655` `show = has && !empty(id)`). So the beehive is a **zone-content bug,
  not a code bug**: either add a bee source (a `bee_hive_wild` or `bee_honey` in the roster) or don't place
  bare boxes the player can't populate.

### 5. Ground brood (`ground_pile`) — MISSING player surface — GAP #5

- Server engine REAL: flies breeding on rotten fruit → `kind:"ground_pile"`, area-snapped shared pile
  (`brood.go:80-98`); free-roamers/detritivores lay an own-cell clutch via the same path (`brood.go:90-98`).
  Matures + hatches + auto-retires when emptied (`brood.go:148-153`, `broodSourceGone` returns false for a
  pile: `:169-172`).
- **No player surface:** a ground pile has NO occupant/collider (`SourceID:""`). `InteractionResolver`
  only finds occupant `Collider2D`s (`InteractionResolver.cs:36-51`), so a pile is **not right-clickable**.
  And the **only** consumer of `BroodUpdate(104)` client-side is `CraftingPanel` (verified: the other grep
  hits are `BroodMessages.cs` itself and a false `-104` coordinate in `MannequinController.cs`) — there is
  **no world-sprite renderer for OpCode 104**. So wild breeding is entirely invisible and unmanageable.
  Matches doc "Not built: a clickable world object for the wild fly brood" (`architecture_nursery_stations.md:127`).

### GAP #4 — the "generic nest" — REFUTED
There is **no `nest` occupant in the committed save** (all 64 chunks scanned) and **no `nest` entity defined**
in `occupants.json`. The only nest-class occupants are the 7 `wasp_nest`. A "1 generic nest" seen in a live
zone is a **runtime-founded daughter wasp NestState** (`processNestFounding` places a `wasp_nest` occupant,
`nests.go:382-403`) or a miscount — not an orphaned placed occupant. (If a raw id `"nest"` ever WERE placed
it would have no `EntityDef` → inert: not a station, not a nest, not interactable.)

---

## Determinism — clean
- Broods are **server-only soft state**: never hashed, never in the late-join snapshot
  (`entities/brood.go:8-12`, `brood.go:11-16`). `BroodUpdate(104)` is display-only.
- Births ride the deterministic `SWARM_REPRODUCED` ledger via `growSwarm`/`spawnSwarmAt`
  (`brood.go:340,351,360`), so a dropped/late brood update only delays an on-screen sprite, never a bug
  position (`BroodMessages.cs:43-46`).
- `NurseryTake`/`NurseryDeposit` touch only soft brood state + player inventory, not the hashed sim
  (`handlers_nursery.go:10-11`).
- The compost food coupling is correct: process, feed, harvest all move the compost's food level via the
  SAME frontier-gated `AddFoodEvent`/`InfluenceFoodConsumed` (`handlers_farming.go:1467,1519,1586`) — clients
  stay in sync. The ONE asymmetry is teardown (Smell 2): break doesn't emit the food=0 event that harvest
  does — still deterministic-consistent (all clients read the same un-zeroed ledger), so a phantom, not a
  desync.

## Cross-cutting design / refactor smells
1. **Dead resident header for non-nest stations** (compost + milkweed): `resHead` "INSIDE" is built
   unconditionally and never hidden (`CraftingPanel.cs:620-622` vs `RefreshBrood` `:666-674`). Either hide
   it when `residents==0` or gate it on `kind=="nest"`. (Sev: low-moderate — visible.)
2. **Inconsistent soft-state lifecycle:** `NestStates` are swept when their occupant vanishes
   (`processNests` `nests.go:159-163`), but `Stations` and `HostPlantStates` are **never** swept (no
   `delete` exists for either). Stations leak into a phantom food source (Smell 2); host plants leak
   harmlessly. Give stations/host-plants the same occupant-gone sweep, and zero the station food on break.
   (Sev: moderate for stations, low for host plants.)
3. **Two "seed-empty" behaviors, silently:** only a nest can be seeded from empty (species known via
   `NestState`); compost + milkweed silently reject (`handlers_nursery.go:151-161`). Inconsistent, and the
   rejection is invisible to the player.
4. **No client feedback on server rejection:** `handleNurseryTake` (bag full) and `handleNurseryDeposit`
   (wrong species / empty-seed / capacity) just `return` with no ack (`handlers_nursery.go:67-69,145-161`);
   the client fires-and-forgets and force-clears the cursor on deposit (`CraftingPanel.cs:685-687`). A
   rejected deposit looks like the item vanished until the next inventory sync. (Sev: low-moderate — UX.)
5. **beehive_basic placed with no bee source** — zone content bug (Gap #2).
6. **wasp_nest empty drops vs hornet_nest loot drops** — teardown-yield inconsistency (Sev: low).
7. **Stale doc lines**: `architecture_nursery_stations.md:124` still lists compost as "not built into the
   panel" and residents as "not built"; the panel + universal pupa ARE built. The Status block at the top
   (`:9-27`) is current; the older "Built vs not built" section (`:110-127`) has drifted.

## Verdicts (most severe first)
1. **ground_pile — MISSING player surface** (wild breeding invisible + unclickable). GAP #5.
2. **beehive_basic — HALF-WORKING / inert in village_21_B** (no bee colony to populate the 4 boxes). GAP #2 — zone content.
3. **milkweed — HALF-WORKING** (auto-breed COMPLETE; can't seed an empty one so place-back is unusable in practice; dead resident area). GAP #3 + GAP #1.
4. **compost_bin — COMPLETE** with two real smells: dead "INSIDE" header (GAP #1) + teardown leaves a phantom food source / leaked StationState (Smell 2).
5. **wasp_nest — COMPLETE** (the reference); minor latent species-hijack + drop-yield asymmetry.
