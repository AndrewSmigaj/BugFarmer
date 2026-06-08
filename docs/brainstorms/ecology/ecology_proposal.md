# Ecology Proposal — emergent relationships for BugFarmer

> **Status: proposal for discussion.** The user wants to revisit ecology with their own ideas — this doc
> reiterates what's already designed (so we're aligned), critiques the thin spots, and proposes a coherent,
> *emergent* model to react to. Nothing here is committed. Grounded in `game_design.md §9/§13/§18` and
> `architecture_farming.md`.

## 0. The pillar (don't lose this)
The GDD commits to **"emergent systems over scripts"** and **"readable cause-and-effect."** Two modes:
- **Shared world** — bugs migrate, hunt, compete; events arise from spatial + ecological conditions; *no
  timer-based disasters, no forced invasions.*
- **Private plot** — controlled, deterministic, **paused while offline** (no random invasions / offline loss).

So ecology must be **a few local rules that compose into emergent outcomes the player can read and influence**
— never a scripted event tree. The litmus test for any mechanic below: *can the player see why it happened
and act on it?*

## 1. What's already designed (reiterated, close to source)
The **village fly chain** (the "chain" the user remembers), from `architecture_farming.md` + `§9.3`:

> Fruit tree → produces fruit → fruit falls → **rots** (`rotten_apple`/`rotten_orange`) → **flies** attracted
> (feed, will breed) → **predators** (frogs, spiders) hunt flies; **wasps migrate in** when prey is available.

Other documented pieces:
- **Butterfly ↔ milkweed** (`§9.1`): butterflies breed *only* on milkweed; *"if milkweed reaches zero,
  butterflies stop reproducing, population ages out naturally."*
- **Wasp ↔ bee** (`§9.2`): *"wasps prey on bees; wasp reproduction requires successful predation."* Bees
  reproduce when a hive + sufficient food exist.
- **Pollination** (`§9.2`): *"triggered when swarm centers pass near flowers. Heuristic-based, not per-bug."*
- **Future crop pests** (aphid/caterpillar/locust): the plant-HP/damage system exists but is **inactive**
  until those bugs ship.
- **Population aging**: food → 0 ⇒ reproduction stops ⇒ population ages out.
- **Emergent bosses from overgrowth** (`§14.2`): *"not scripted, telegraphed visually."*
- **The Ecologist** (`§13`): the *only* NPC that interprets ecology; offers **optional, world-state-driven**
  quests with multiple solutions; *"never create artificial problems."*

## 2. Where it's thin (the gaps to fill)
1. **Predator mechanics are named, not defined** (frogs/spiders/wasps "hunt flies" — but at what rate, range,
   satiation, reproduction tie?).
2. **Pollination has no observable payoff** ("swarm passes flower" → ??). What does pollination *do*?
3. **No infestation rules** — "out of balance" is gestured at but there's no rule for when a boom tips into a
   problem, or what the problem looks like.
4. **No recovery path** — you can collapse an ecosystem (harvest all fruit, kill all predators) but nothing
   says how it comes back.
5. **Butterfly/bee breeding under-specified** (lifecycle timing, caps).
6. **The Ecologist is a stub** — no detection model, no concrete quests, no player tools.

## 3. Proposed model — one small rule-set, applied to every species
Treat each species as a **population** (tracked per-zone, at the swarm/heuristic level the GDD already uses —
NOT per-bug) with a tiny rule block:

```
population P of species S in zone Z:
  food:        [resources S eats]            # e.g. flies ← rotten_fruit; aphids ← root_sap; wasps ← (bees|flies|caterpillars)
  breeds_on:   [requirement to reproduce]    # e.g. butterflies ← milkweed; bees ← hive+food; wasps ← successful predation
  predators:   [species that eat S]          # pressure DOWN
  capacity:    f(food available, space)      # soft cap; readable
  growth:      up if (food ok AND breed ok AND below capacity), else decline/age-out
  signals:     visual telegraphs of its state # swarm size, color, sound, damage
```

Everything emergent falls out of these four couplings: **food, breeding-requirement, predator, capacity.**
No event scripts — booms/busts/infestations are just these rules interacting.

### Relationship types (the web)
- **Food → consumer:** rotten fruit → flies; crops → pests (aphid/caterpillar/locust); leaves → leafcutters.
- **Host → breeder:** milkweed → butterflies; hive → bees; carrion/rot → flies.
- **Predator → prey:** frog/spider → flies; wasp → bees/caterpillars; mantis/dragonfly → many; antlion → ants.
- **Pollinator ↔ plant (mutualism):** bees/butterflies pollinate → plants set **seed/fruit** (the payoff,
  §3.1) → more flowers next cycle. Lose pollinators → flowering/yield declines.
- **Tended mutualism:** ants ↔ aphids (ants protect aphids, harvest honeydew) — a self-reinforcing loop that
  *spreads* if unchecked (great emergent pressure + a farmable trick the player can learn).

### 3.1 Make pollination *do* something (fills gap #2)
Pollinated flowers/crops → higher **seed set / fruit yield / spread**; unpollinated → sparse yield. Now the
player has a readable reason to keep pollinators alive (and a reason wasps-eating-bees matters to the farm).

### 3.2 Booms, infestations, recovery (fills gaps #3–4)
- **Boom:** remove a predator (or over-provide food) → prey grows past capacity → **infestation** state
  (telegraphed: dense swarm, crop damage, discolored ground). An **"emergent boss from overgrowth"** is just a
  population that blew way past capacity (e.g. a locust swarm, a bloated queen) — kill it / cut the food / let
  predators catch up.
- **Bust:** remove the food/host → population ages out (already designed).
- **Recovery (new):** populations **re-seed from neighbors** — a depleted species drifts back in from adjacent
  zones over time *if* its food/host exists again. So the player (or the Ecologist) restores by **replanting
  the host / reintroducing a predator**, not by a magic reset. Readable, emergent, reversible.

## 4. The demo-slice ecosystems (concrete webs)
- **Village (easy, legible):** fruit→rot→**flies**→(frogs, spiders, migrant wasps). Player levers: harvest
  timing, compost, nets, releasing/encouraging predators. The teaching ecosystem.
- **Butterfly Meadow (medium):** **milkweed→butterflies**, flowers↔(bees/butterflies) pollination, **wasps**
  prey on bees+caterpillars, edge **centipedes/millipedes** as roaming predators/threats. Lever-rich: tip it
  toward pollinators (more flowers/yield) or toward wasps (fewer bugs, safer, but poorer blooms).
- **Mining Caves (sparse detritivore web):** fungus/detritus → springtails/isopods/crickets →
  centipedes/cave-spiders (predators). Glow bugs as a gentle keystone (light). Thin but real.
- **Ant Colony (mutualism showcase):** ants ↔ **aphid livestock** (honeydew), ants farm **fungus** (leaf
  input), **soldiers** defend, **queen** drives growth; parasites (parasitoid wasp, phorid fly, raider
  beetles) prey on the colony. Disrupt aphids/fungus/queen → colony destabilizes (and you can learn to ranch
  aphids yourself).

## 5. The Ecologist (system + NPC) (fills gap #6)
A **balance reader**, not a quest-dispenser of artificial problems:
- **Detection:** reads the per-zone population states (§3). Surfaces them to the player as a readable
  **field journal / "ecosystem health"** view (which species are booming/busting, what's missing).
- **Quests = real imbalances only:** offered *when world-state shows one*, with **multiple solutions** and
  never forced — e.g. "the wasps have collapsed the bee population — restore pollination" (solve by: planting
  flowers to re-seed bees from a neighbor zone, culling wasps, or relocating a hive). Solving it is optional;
  the world keeps running either way.
- **Player tools the Ecologist teaches:** identify species + their couplings; transplant host plants;
  capture+release predators/pollinators; read telegraphs. (These reuse bug-farming gear — nets, lures, pens.)
- **Tone:** curiosity + stewardship, not pest-extermination. Balance is a dial the player *can* leave alone.

## 6. Player levers → consequences (the readable loop)
| Player action | Emergent consequence (readable signal) |
|---|---|
| Leave fruit to rot | Fly swarm grows (visible cloud) → predators arrive |
| Harvest everything | Flies starve → predators leave (quiet zone) |
| Remove predators | Prey booms → infestation/crop damage → maybe an overgrowth boss |
| Plant flowers / keep pollinators | Better yields & spread (lusher zone) |
| Plant milkweed | Butterflies return (from neighbor zones) |
| Encourage ants↔aphids | Honeydew yield, but the loop spreads / attracts predators |

## 7. Open questions (for the user to weigh in)
- Granularity: per-zone population counters vs. a coarser "state" enum (boom/stable/bust)? (Lean coarse +
  readable.)
- How fast should re-seeding from neighbors be (minutes? in-game days?) — pacing of recovery.
- Should pollination yield be a multiplier on existing crops, or gate *new* wild-flower spread, or both?
- How visible should the "ecosystem health" view be — always-on HUD, the Ecologist's journal, or in-world
  reading only (most emergent)?
- Which mutualisms become **player-farmable tricks** (ant/aphid honeydew ranching seems the standout)?
- Do "overgrowth bosses" drop unique materials (incentive to *let* things tip occasionally)?
