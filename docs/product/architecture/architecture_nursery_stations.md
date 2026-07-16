# Nursery Stations — the breeding model

The player-facing breeding system. The server brood *engine* (create → mature → hatch) is built and tested
(`brood.go`, `nests.go`); this describes the **player-facing layer** on top (open / see / take / teardown),
which is the part not yet built. Canonical decisions: **D23** (`economy/DECISIONS.md`) and the nursery model
in `bug_ecology_plan.md`, reconciled with the finalized model below (which supersedes D23's "host holds a
brood" wording — see Reconciliation).

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

## Take / harvest
- You take eggs/larva out **as items** (per-species egg/larva items, which already have sprites).
- You harvest a **random amount** — the remainder **perish**. (A "harvesting skill" that raises the yield is
  backlogged.)
- Only **living** egg/larva are items; there are **no dead-brood items** — "perish" simply means they died and
  returned to the soil (dead-object modeling stays for adult carcasses only). *[resolved: streamlined]*
- Taken brood can only be **placed on a COMPATIBLE nursery** — butterfly → milkweed, fly → compost, wasp → nest
  (mirrors real host-specificity). Brood cannot be started on bare ground. *[resolved]*

## Teardown / destroy
Destroying a nursery is the **normal occupant-break** (hit it N times → pick up the empty station):
- The **brood (eggs + larva) perishes.**
- Only the **live resident adults** spill out into the world (wasps come out **aggressive**).
- To keep any brood, **harvest it first**, then move it to a compatible nursery.
- **Built:** `onNestOccupantRemoved` now **perishes the brood** (`clearNestBrood`, no bugs minted) and orphans
  the resident patrol — the already-live adults proximity-aggro the breaker. Matches "the brood dies, only
  living adults spill out."

## Stages in this scope — egg → larva → adult (NO pupa)
The village nursery bugs (flies etc.) are **egg → larva → adult**. Do **not** add a pupa stage here — pupae are
part of the deferred extended lifecycle below.

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
  the cached OpCode-104 stream. Mirrors `CraftingPanel`; the owner's UI mockup drives the visual polish later.
- **Not built (the player-facing layer):** **take/random-harvest** + egg/larva items; the **compost bin** unified
  into the panel (it still uses the `StationController` deposit UI — its `interaction_type` stays `"station"`
  until the deposit + brood views merge); **residents at the compost bin** (residents exist only for nests
  today); and a **clickable world object for the wild fly brood** (`ground_pile`).

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
