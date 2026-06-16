# Bug Ecology / Farming — design of record (in progress)

The durable design for the bug-farming + living-ecosystem work (BACKLOG tasks P0–P11). The throwaway plan
doc only covers the active item; THIS is the persistent design. Verify every sim-touching change with the
**`test-changes`** skill (Go tests + sync-harness + the determinism / "all players in sync" checks).

## Premise & core loop
2135: livestock collapsed, humanity farms giant gene-modded BUGS for meat. **Two production channels:**
(1) many bugs **produce goods at species stations** (bees → honey at an apiary, silkworm → silk); (2) bugs
without a distinct product — flies, wasps — are **sold raw as meat at the bug market** (resolves "what do
flies/wasps produce?" — they're the meat). The loop:
**raise bugs (feed + breed + contain) → harvest the PRODUCT (a production station) OR the BUG itself (nets /
autocatchers, before old age claims the meat) → SELL (market) / USE (craft) → reinvest (sprinklers,
autocatchers, more trees, new species/zones) → climb the food-chain tech tree (farm flies → sustain wasps →
premium bugs).** The ecology (death, breeding, predation, detritivores, pollination) is the **husbandry
engine** beneath this — lean, fun, legible; stabilized behind the scenes so it never collapses.

## Food chain = progression
Flies = starter livestock (trees→fruit→rot→compost feeds + breeds them). Wasps = premium livestock but you
must farm a **surplus of flies** to feed them (predator husbandry) → higher market value; pattern climbs to
bigger/rarer bugs. **Sustaining the tier below is the gate.** Wild predators also threaten stock (pens/defense).

## Farming verbs & infrastructure
Harvest (nets + autocatchers, before natural death claims the meat) · Produce (species stations: apiary→honey,
silk frame→silk) · Feed (trees→fruit→rot, compost bins, flowers→nectar+bonuses; sprinklers auto-water trees)
· Breed (nursery stations) · Contain (pens keep livestock IN as much as wild bugs OUT — a closed `blocks_bugs`
pen holds a swarm) · Herd (move large bugs) · Sell (the bug market — align with the existing merchant). Bug
value scales with tier/size/rarity. **Design goal: EVERY bug is farmable** (each gets AI + catch/sell over time).

## Interaction model — everything interactable is a right-click "station"
Right-click → open a panel: **flowers** (nectar + bonuses), **milkweed/host plants** (brood {eggs,larvae};
larvae feed on it; destroy it → no breeding), **compost bin** (compost fill + a **fly-larva slot**), **fruit
tree** (an **egg clutch** when flies breed on its rotting fruit). **Right-click no longer does weapon secondary
moves** (no sword stab) — it's unambiguously "interact/open." Brood management (view + take a larva → place on
another host) happens in these panels (reuses the container-move op; counts only, no clutter). The **magnifying
glass** = research (reveal a bug's hidden foods/hosts → Ecology tab).

## The nursery breeding model
A reproducing swarm at a breeding station deposits eggs into its brood slot **at the breeding site** (same
food cost / cooldown / caps), incubates on the slow clock, and **hatches in place** into new bugs that
join/form a swarm there (`growSwarm`/`SWARM_REPRODUCED`). Larvae feed on the host; destroy/exhaust the host →
brood lost (suppression verb). Hosts (milkweed) lightly regrow so it's never a permanent dead-end.

## Ecology = the husbandry engine
- **Natural death / lifespan** (swarm-cohort `AdultAge`, slow clock): bugs age + die → drop a **species
  carcass** `dead_<species>` (separate from player-kill `bug_parts` loot). Meaning: harvest at peak or lose the
  meat; unharvested deaths feed the recycle loop.
- **Millipede detritivore** (centipede individual chassis, no attack/gnaw): eats carcasses → **compost** →
  feeds trees/soil (recycling).
- **Predation = premium-livestock husbandry + threat** (wasps/centipede eat flies; you over-produce flies to
  sustain farmed wasps; wild predators threaten stock).
- **Pollination & flowers** = bonuses (flowering crops attract pollinators → yield; positive loop).
- **Aphids ↔ ladybugs** = pest ↔ counter on plants/crops (manageable, introduce-the-counter).

## Stabilizers (behind the scenes, gentle guardrails — not autopilot)
Logistic carrying-caps, predator satiation + slow predator breeding, a **neighbor re-seed floor** ("no species
hard-zeros where its host exists" — no permanent dead-ends), and a **slow population clock** (pop dynamics on
minutes, not the 100ms tick). The player stays the main driver; stabilizers only prevent collapse/explosion.

## Determinism (verified — ~93% vs the deterministic tick system)
State hash (`SwarmManager.ComputeStateHash`) = swarm bug positions/velocities ONLY; stations/items/broods/food
registry NOT hashed. Broods are station soft-state (no new world-objects); larva relocation edits counts (a
container move). **Contract:** zero new ledger event types — births→`SWARM_REPRODUCED`, deaths→`BUG_REMOVED`,
edible/food→`ITEM_ROTTED`/`FOOD_CONSUMED`; server-mint+broadcast object IDs; soft state never in the ledger
(resets on authority handoff — accepted, like nests). Brood late-join is **proven safe** (clients never compute
broods — they replay the hatch event). The boundary for farming mechanics: "does a bug's POSITION depend on
it?" — food/host-depletion/pollinator-attraction/catching ride the ledger (deterministic); market/coins/
sprinklers/soil-fertility/crop-yield are ordinary shared state (outside the lockstep hash). Gate each phase
with the `test-changes` skill (drift detector / trace-diff for positions; harness for ledger + reconnect).

## Bug Lab world (the iteration engine — DONE, P1)
`nakama/data/zones/bug_lab/` (zonegen via `tools/make_bug_lab.py`): a fenced pen per AI species
(fly+compost+trees, butterfly+milkweed+flowers, wasp, centipede; millipede/aphid pens added with those
species) + an open arena. WorldMenu "Bug Lab"; F8 "Stock Bug Lab" loadout (100 fruit + 10 of each species);
multi-species F5 graph + F4 markers.

## Phased build order (BACKLOG tasks #49–56)
P0 art+data (lean: `dead_<species>`, aphid; brood/larva-slot fields; host `Depletable` + soil-fertility +
market-price fields; publish) · **P1 Bug Lab DONE** · P2 stabilizer layer · P3 natural death + carcasses · P4
right-click stations + nursery breeding (flies) · P5 harvest + market core loop (autocatchers, sell-as-meat,
sprinklers) · P6 millipede detritivore→compost→fertility · P7 butterfly milkweed host loop + larva-relocate ·
P8 aphids↔ladybugs · P9 pollination/flower bonuses + crop pests · P10 Ecology tab (Apico-style, Ecologist-
unlock) + magnifier research · P11 balance pass + docs. **Deferred to own plans:** ants (nest refactor),
locusts, seasons, breeding-for-rarity.

## Key decisions
Bug = product (meat at market) OR station product (honey/silk) · food chain = progression · death = harvest-or-
lose turnover · everything = a right-click station · no weapon R-click moves · broods = station counts (no
clutter) · magnifier = research · stabilizers = gentle guardrails · Ecology tab = player surface, F5 = dev tool.
