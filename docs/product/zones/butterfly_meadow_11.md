# Zone Design: Butterfly Meadow (1,1 · `butterfly_meadow_11`)

## Overview
- **Zone ID / Grid:** `butterfly_meadow_11` · row 1, col 1 (directly **north** of the village)
- **Biome / Difficulty:** Flowering meadow → forest edge · **Medium** (a gentle step up from the village)
- **The feel:** A bright, drifting meadow thick with **milkweed** and wildflowers, clouds of **butterflies**
  overhead — beautiful, but the first place that bites back: **wasps** hunt here, and the cooler **forest
  edge** to the north leaks **millipedes and centipedes**. The pollination-vs-predation balance is on full
  display; this is the player's first real ecosystem to read and (optionally) tip.

## Connections (map)
- **S →** Village (`village_21`) by road (you arrive from the south). **N →** the harder forest zones
  (millipede/centipede country) — the meadow shades into trees at the top edge. **W/E →** other meadows.

## Key species & ecology
- **Plants:** **milkweed** (the keystone — butterflies breed only on it), plus nectar flowers (aster,
  foxglove, clover, lavender) feeding pollinators.
- **Pollinators:** 2–3 **butterflies** (monarch-like on milkweed, a swallowtail, a small common) + drifting
  **bees**. They pollinate flowers (heuristic, swarm-proximity) — visible payoff for keeping flowers up.
- **Pests/Predators:** **2 wasps** — an *easier* paper wasp and a *harder* yellowjacket (wasps get nastier
  in zones further out). Wasps prey on the caterpillars/butterflies and on bees → the predation pressure.
- **Edge threats:** **millipede** (slow, armored, mostly defensive) and **centipede** (fast, venomous) seep
  in from the northern forest edge — the danger ramps as you go north.
- **Out of balance:** kill all milkweed → butterflies age out; kill all wasps → butterflies/caterpillars
  boom (and may strip flowers); over-collect butterflies → pollination drops → fewer flowers/seeds. (See
  `ecology_proposal.md`.)

## Landmarks & little features
- **The Great Milkweed Stand** — an oversized milkweed cluster swarming with monarchs (the iconic spot).
- **Flower-clock glade** — a ring of flowers of different colors, like a sundial of blooms.
- **The broken fence line** — an old split-rail fence half-swallowed by the meadow (failed farm; story prop).
- **A mossy boulder / butterfly basking rock** in a sunbeam.
- **Forest-edge gloom** (north strip) — darker grass, stumps, a fallen log "bridge," where centipedes lurk.

## Structures / NPCs
- Optional: a **lepidopterist's tent/blind** (a bug-watcher's camp — net posts, specimen jars, a folding
  stool) as a small point of interest and a future quest hook.

## Materials / loot
- Gatherables: milkweed pods/floss, flower nectar, butterfly/wasp specimens; no ores. Forest edge drops
  the odd log/stump wood.

## Biome composition (for the generator)
- Base **grass** (lush), few dirt patches; **heavy `scatter`** of flowers + milkweed + tall grass + bushes;
  scattered tree **clusters** thickening into a **forest band** along the north edge (stumps, fallen log,
  ferns); butterflies/bees/wasps as `place_bug` (sub-grid, scaled) drifting; a boulder + the broken fence as
  occupants. Little water (maybe a small puddle/spring).

## Scenes (showcase) — BUILT (placeholders; `tools/_generated/previews/`)
- `scene_butterfly_meadow.py` — the meadow proper (milkweed stand, flower-clock glade, pollinator swarm,
  a wasp or two, the broken fence, basking rock, lepidopterist's blind). 64×52, 0 warnings, validate OK.
- `scene_meadow_forest_edge.py` — the northern transition (grass darkening to dirt, tree band, stumps,
  fallen-log bridge, a centipede + millipede from segment parts) showing the difficulty ramp + forest
  props. 60×46, 0 warnings, validate OK. Both are north-up (village road enters from the south/bottom).
- New placeholder entities added for these scenes (see `art_needed.md`): `milkweed_giant`, `clover_red`,
  `stump_mossy`, `log_fallen`, `broken_fence`, `boulder`, `specimen_case`.

## Not present
- No buildings/town, no mining, no deep-forest density (that's the zones further north).
