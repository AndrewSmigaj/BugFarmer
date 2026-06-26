# Zone Design: <Name> (<row,col> · `<zone_id>`)

> Copy this file to `docs/product/zones/<zone_id>.md` for a new zone. It's the concise design contract a
> scene author reads before building. The whole-map context lives in `docs/product/architecture/architecture_world.md`;
> the generation how-to in `docs/archive/ZONE_GENERATION_GUIDE.md` (incl. the biome→feature map). Keep this
> short — it's intent, not implementation.

## Overview
- **Zone ID / Grid:** `<zone_id>` · row R, col C
- **Biome / Difficulty:** <biome> · <Easy|Medium|Hard|…> (note if difficulty deepens with depth/distance)
- **The feel (1 paragraph):** what this place *is*, its mood, and the hook that makes it memorable.

## Connections (map)
- N / E / S / W neighbors and how you travel there (road · tunnel · river · cliff). Note river/cliff
  alignment that must line up at the shared edge.

## Key species & ecology
- **Plants** that anchor the food web (e.g. milkweed for butterflies).
- **Pollinators / pests / predators** present and their roles — who needs/eats whom (this is what makes
  the zone an *ecosystem*, not a backdrop). Link to `ecology_proposal.md` relationships.
- **Threats** — the creatures that make it dangerous (and the difficulty knob).

## Landmarks & little features
2–5 named points of interest so the zone isn't a flat map: a ruin, a giant specimen plant, a spring, a
fallen-log bridge, a collapsed mine cart, a shrine. These are the "little features."

## Structures / NPCs (if any)
Buildings, camps, hermits, signage — and what they're for.

## Materials / loot
Ores, blocks, and gatherables found here, with rough rarity.

## Biome composition (for the generator)
Base tile, ground variety, density of trees/flowers/water, and which `features/` primitives to use
(`cave`, `terrain`, `garden`, `yard`, `scatter`, `room/house`). See the biome→feature map in the guide.

## Scenes (showcase)
The 2+ example scene scripts that show this zone off (`tools/zonegen/scenes/...`).

## Not present
Explicit exclusions, so scope stays honest.
