# Nursery Stations — the breeding model

The player-facing breeding system. The server brood *engine* (create → mature → hatch) is built and tested
(`brood.go`, `nests.go`); this describes the **player-facing layer** on top (open / see / take / teardown),
which is the part not yet built. Canonical decisions: **D23** (`economy/DECISIONS.md`) and the nursery model
in `bug_ecology_plan.md`, reconciled with the finalized model below (which supersedes D23's "host holds a
brood" wording — see Reconciliation).

> **Status (2026-07) — the player-facing layer is BUILT into ONE unified station panel.** Compost, wasp
> nest / milkweed nurseries, and the beehive all open the same `CraftingPanel`, dispatched by
> `interaction_type` (`craft` · `storage` · `station`=compost · `nursery` · `beehive`): a deposit grid + fill
> meters, the shared brood region (stage slots + maturation bar + resident adults + take/place-back), and honey
> harvest. The legacy IMGUI `StationController`, the `NurseryPanel` clone, and `BeehiveController` are deleted.
> The **server-side** breeding engine (`brood.go`/`nests.go`/`processStations`) stays server-side for now; its
> correct long-term home is the **authority-client "ecology port"** slice (`BACKLOG.md`), NOT a server-code
> merge with crafting — crafting is player *inventory*, breeding is the bug *ecology*; same surface abstraction,
> different domains. (Assessment 2026-07: porting breeding client-side is a real, determinism-gated project —
> `float32`→fixed-point of the whole satiation/feeding economy — not a now-simplification, so deferred.)

## The core model — a brood IS a nursery station
A **nursery station is where a species breeds, and the brood *is* that station** — one object, not a container
that holds a separate brood. The nursery stations are:
- **Egg brood** — the wild, self-placed nursery a fly (or other free-roamer with no provided station) drops on
  rotten fruit / at its own cell when there's no built station to breed in.
- **Compost bin** — the built/provided fly nursery (also a food source; same breeding model).
- **Milkweed** — the butterfly nursery (a rooted host plant).
- **Wasp nest** — the wasp nursery (a portable structure with residents).

Each nursery station holds a **brood = eggs + larva** (for most bugs), as **counts** with each stage's
**sprite** (never bare text). The larva's *form* is species-specific — a maggot (fly), a grub (wasp/beetle), a
caterpillar (butterfly) — it is only the name of the larva stage, never a merge of egg + larva.

## Opening a nursery — one station panel
Right-click a nursery station → **one panel** (the same panel family as other stations; a compost bin's deposit
panel and its brood view are unified into one). It shows:
- The **eggs** and the **larva** as **inventory-square slots** (hotbar-style) — each with the species' stage
  sprite + a count — so they can be **grabbed like items**.
- The **resident adults hanging out inside**, where the station supports it: wasps in a nest, **flies in a
  compost bin**. (Wild egg broods are transient — no residents.)
- **Conversion bars** — the egg → larva → adult progress over time, like any station that processes over time.

## Conversion (the default lifecycle — built server-side)
Left alone, a nursery converts **eggs → larva → a new adult bug, which hatches in place and is released into
the world.** This engine exists: `BroodState` (egg/larva counts + a maturation timer), `layIntoBrood`,
`processBroods`. Per species, the source is resolved automatically: fly → compost bin if present else a wild
ground brood; butterfly → milkweed; wasp → nest; free-roamers → a wild ground brood at their cell.

## Take (a nursery is a modified station)
A nursery is **just a station**: the way a hive generates units of honeycomb and a furnace generates steel
bars, a nursery generates **units of brood** — its egg / larva / pupa counts ARE its collectable output. You
**take however many you want**, exactly like any other station's item transfer — **no random yield, nothing
perishes on take** (what you leave keeps developing).
- Each stage grants a **per-species item**. Display sprite and take item are **separate**: the panel shows the
  developing stage sprite (`species.<stage>_sprite_id`); the bag gets `species.<stage>_item_id` where the design
  has a dedicated material (e.g. **wasp larva → the `wasp_larvae` material** — the boss-drop / brood-input item,
  so harvest + place-back use that one item; `wasp_grubs` stays display-only), else the stage's own (stackable)
  sprite id. No new items invented — reuses the unified registry.
- **Built:** placing taken brood back onto a **COMPATIBLE nursery** (hold a brood item, click a stage slot in
  the panel → `OpCodeNurseryDeposit` 114). The server reverse-resolves the item's species+stage (`broodItemStage`)
  and accepts it only if the species matches the nursery's (a fly larva can't go in a wasp nest) — it tops up an
  active brood or **seeds an empty nest** (species known via `NestState`; an empty milkweed's species isn't
  knowable from the host alone, so milkweed is top-up-only). Capacity-clamped; not startable on bare ground.

## Teardown / destroy
Destroying a nursery is the **normal occupant-break** (hit it N times → pick up the empty station):
- The **brood (eggs + larva) perishes.**
- Only the **live resident adults** spill out into the world (wasps come out **aggressive**).
- To keep any brood, **harvest it first**, then move it to a compatible nursery.
- **Built:** `onNestOccupantRemoved` now **perishes the brood** (`clearNestBrood`, no bugs minted) and orphans
  the resident patrol — the already-live adults proximity-aggro the breaker. Matches "the brood dies, only
  living adults spill out."

## Stages — egg → larva → pupa → adult (flies pupate too)
The nursery bugs run the real insect life cycle: **egg → larva → pupa → adult**. Flies included — a housefly is
egg → maggot → pupa → adult, so the compost bin shows a pupa lane. This is **built**: a species pupates when it
has a `pupa_sprite_id` (`fly_common` does), which `brood.go`'s `broodPupates` reads for source/compost broods,
not just nests. *(An earlier draft scoped village flies to egg → larva → adult with NO pupa; that was superseded
when the universal pupa stage shipped — corrected here.)* The larva's **form** is a species-specific display
label only — a **maggot** (fly), a **grub** (wasp/beetle), a **caterpillar** (butterfly), or just **young**
(centipede/millipede) — never a merge of egg + larva. These labels are data (`species.json` `larva_name` /
`pupa_name` / `brood_label`); "brood" is used as the section's umbrella word only where it fits a true nest/hive.

## Reconciliation with D23 (this doc supersedes the older wording)
- D23 says "a host that **holds** a brood" (two objects). **Corrected: the brood IS the station** (one object).
  The code already matches this — `brood.go` treats the brood as the nursery; `SourceKind` only records what
  it's attached to.
- D23's "**move a portable host → the brood travels with it**" special case is **removed** — teardown is the
  plain occupant-break (brood perishes, adults released); you repopulate a re-placed station yourself.
- Milkweed teardown = **fiber + a seed chance** (D24), and the brood perishes; there is no larvae "drop."

## Extended realistic lifecycle — SEPARATE, DEFERRED plan (its own plan, after this)
A later design layer adds **real insect life cycles** as optional educational depth (not everyone must engage):
- **Beetles**: full **egg → larva → pupa → adult** out in the world, individual-to-individual; the **pupa
  yields silk**.
- **Butterflies**: milkweed holds eggs + caterpillars, but a caterpillar forms its **chrysalis and wanders off
  the milkweed** to attach it to a tree / branch / bush / fence before becoming an adult. (Caterpillars + the
  wandering chrysalis are synchronized client-deterministic bugs.)
- Centipede / millipede: lay an egg pile and guard it (refined behavior backlogged).
- **Status: decided, but its own plan — deferred until the nursery-station work above is finished.**

## Built vs. not built
- **Built + tested (server):** the brood engine — `BroodState` (egg/larva counts + timer), `layIntoBrood`,
  `processBroods` (mature + hatch in place), nest deposit/re-hatch, milkweed host loop, wasp-nest residents.
  Breeding works; it is just invisible to the player.
- **Built (server foundation for the panel):** the **universal pupa stage** (nests pupate too — wasp/bee),
  the **teardown fix** (`onNestOccupantRemoved` perishes the brood), and **OpCode 104 now carries
  conversion-progress + resident count** (via the shared `broodUpdateMessage`, re-broadcast each slow tick so an
  open panel stays fresh).
- **Built (client, functional placeholder):** the open-station **`NurseryPanel`** — right-click a **wasp nest**
  or **milkweed** (`interaction_type:"nursery"`) → one Canvas panel showing egg/larva/pupa **slots** (stage
  sprite + count), the **resident adults inside** (a slot + count), and a smoothed **conversion bar**, fed by
  the cached OpCode-104 stream. **Take** a stage's units (click a slot → OpCode 113) and **place brood back**
  into a compatible nursery (hold a brood item, click a slot → OpCode 114 deposit; species-validated, tops up an
  active brood or seeds an empty nest). Mirrors `CraftingPanel`; the owner's UI mockup drives the visual polish.
- **Not built (the player-facing layer):** the **compost bin** unified into the panel (it still uses the
  `StationController` deposit UI — its `interaction_type` stays `"station"` until the deposit + brood views
  merge); **residents at the compost bin** (residents exist only for nests today); and a **clickable world
  object for the wild fly brood** (`ground_pile`).

## Suggested staged build (each stage complete + testable)
0. Butterfly caterpillar larva sprite (the one missing brood stage sprite).
1. **Open a nursery → the station panel** (egg/larva sprites + counts + residents + conversion bar). The big
   visible win — the whole invisible breeding system becomes real. *(A UI mockup is owner-provided; a
   functional placeholder panel can be built first so the data/sprites are ready.)*
2. **Take / random-harvest** eggs & larva as items (+ place-on-compatible-host).
3. **Residents at the compost bin** (generalize the nest-resident model to compost).
4. Teardown fix + the wild-brood clickable object.
- **Final step: reconcile every doc this touches** (fix D23's wording, the ecology plan, the backlog, the
  bugs/swarm-sync architecture docs).
