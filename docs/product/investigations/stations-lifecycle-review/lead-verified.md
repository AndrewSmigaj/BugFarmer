# Lead-verified findings (checked against real code/data myself, not via agents)

These are the load-bearing claims I verified directly, to anchor the synthesis.

## Roster (village_21_B/zone.json `bug_spawning.species_caps`) — DEFINITIVE
6 spawning species: **fly_common** (initial 78), **butterfly_meadow** (30), **wasp_common** (0, nest-only,
max_nests 7), **centipede_garden** (16), **millipede** (16), **beetle_carrion** (12). Bees (bee_honey) are
NOT in the roster despite 4 `beehive_basic` placed → dormant/future hook.

## Verified — the lifecycles are healthier than suspected
- **centipede_garden breeds fine.** Empty `attractions_by_phase` but a COMPLETE predation block
  (species.json: strike_radius 2.3, feed_per_kill 45, hunt_satiation_threshold 50, prey=[fly_common]) → feeds by
  hunting flies → accumulates ReproductionMeter → `layIntoBrood` (brood.go:90-98 fallback) lays a visible
  ground clutch at its own cell. COMPLETE (predation is client-authority; config is present). *(NOTE: home_range=0.0
  — verify that's intentional for a nestless crawler, not a bug.)*
- **millipede breeds fine.** Feeds/breeds on `leaf_litter`, which EXISTS (occupants.json) and IS placed in
  village_21_B (10 instances, NE woods) as a depletable forage pool — the zonegen documents this by design
  (zone_village_21_B.py §10.5). COMPLETE.
- **The nest hijack is FIXED.** hornet_giant now has its own `hornet_nest`; wasp_nest resolves to wasp_common
  (sorted-first over wasp_soldier). village_21_B's 7 wasp nests correctly spawn wasp_common, not hornets.
- **Free-roamer / detritivore breeding is handled** (brood.go:90-98): species with no station/host_plant/ground-
  item source lay a visible `ground_pile` clutch at their own cell (detached lifetime, retires when hatched out).

## Verified — real findings (to confirm/expand via the agents)
1. **`wasp_soldier.nest_occupant="wasp_nest"` is DEAD CONFIG** — unreachable (wasp_common sorts first in
   `speciesForNestOccupant`, nests.go:37-55). Not in the village_21_B roster so no live impact here, but a latent
   data smell (wasp_soldier can never found a nest). Severity: low (data hygiene).
2. **Bees are placed-but-inert in village_21_B** — 4 `beehive_basic` (a `nest_occupants_extra` box → registers
   DORMANT) but bee_honey isn't in the spawn roster → the hives likely do nothing. Half-working / future hook.
3. **Compost/milkweed "resident adults INSIDE" is dead UI** — the shared brood region renders a resident slot,
   but residents are nest-only (architecture_nursery_stations.md says compost residents are "later"; the OpCode-104
   resident count is nests-only per brood.go). So for compost/milkweed the INSIDE area never populates. (Agent B to
   confirm at file:line.)
4. **No clickable world object for wild ground broods** — free-roamer/beetle/wild-fly broods develop as ground
   piles but the player can't open/take from them (no station object). Lifecycle works; player-facing management
   absent. (architecture_nursery_stations.md lists this as not-built.)

Discipline note: two of my own initial suspicions (crawlers can't breed) were WRONG on verification — a reminder
to hold the agents' findings to the same file:line bar before putting them in the assessment.
