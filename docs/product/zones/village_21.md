# Zone Design: Starting Village (2,1 · `village_21`)

The single source of truth for the Village zone — its intent, contents, ecology, and the scene(s)
that show it off. Players spawn here; it's the safe hub and the game's first impression.

## Overview
- **Zone ID / Grid:** `village_21` · row 2, col 1
- **Biome / Difficulty:** Meadow (fly-ecology) · Easy — the safe hub; no dangerous bugs.
- **The feel:** A small but real **town** in a wide meadow — a handful of distinct shops around a civic
  square, a pond with a fishing dock in the southwest, and working farms/orchard at the edges. *Lived-in
  and characterful*: each building unmistakable by its signage and props, the rest open meadow to explore
  and (later) buy land in.

## Design principles (read before building)
- **The meadow is primary; the village is a human interruption, not a replacement.** Grass, flowers,
  flies, predators, rot and decay exist *inside and around* town, not just outside it.
- **Boundaries are made of density, materials, and clutter — not walls.** The five regions (civic core →
  residential → orchard → fly farm → meadow) blend with no hard borders. Roads degrade as they leave town
  (stone → dirt → trampled grass); flower density rises and structures fade as you go outward.
- **Ecology emerges from layout + time, never from props.** There are no "rot plant" objects — rot comes
  from *fruit aging* on the ground. Don't place artificial ecology triggers; place the *causes* (fruit
  trees, compost, fallen fruit) and let the systems do the rest.
- **Decorations must imply use, wear, intent, or failure** — prefer broken/used variants and slight
  disorder over pristine props. Avoid perfect symmetry and decorative clutter with no story. If a spot
  feels empty, add physical *evidence*, not a new system.

## Connections (map)
- **N →** Butterfly Meadow (`butterfly_meadow_11`), by road. **S →** the cave mouth down to the Mining Caves
  (`underground_passages_31`). **W →** Bee Meadow (2,0). **E →** Wasp Thicket (2,2). 3-cell stone roads to
  each edge, fraying to dirt/trampled grass at the margins.
- **Roads:** grid-aligned, no rotation. A N–S road through town + an E–W connector, with spurs to the
  orchard and fly farm. Connect buildings logically; avoid perfect symmetry; let roads occasionally fade
  out awkwardly at the meadow.

## Key species & ecology
- The village is the **fly-ecology showcase**: fruit trees → fallen fruit → rot → **flies** → predators
  (frogs/spiders, migrant wasps). The Orchard + Fly Farm make this legible. (See `ecology_proposal.md`.)
- No threats; pollinators (bees/butterflies drifting in from the north) and flies only.

## The town — buildings (each made distinct by signage + props)
| Building | Style | Purpose | Signature props / sign |
|----------|-------|---------|------------------------|
| **Town Hall** | Largest, **fancy** (marble accents) | Mayor; buy land plots; records & notices | Banner/crest sign, columns, a statue out front; fancy interior (marble walls, fancy mirror, big map table). Functional, not grand. |
| **Market** | A shop **building** with a wide shopfront board | Produce/goods trade | a **3-wide `sign_market_board`** out front, awnings + produce crates, rows of `shop_shelving` inside, a **merchant behind the counter** |
| **General Store** | Standard shop, open frontage | Tools, seeds, sundries, food | Barrels/sacks, delivery clutter, shelves visible through the open front, a painted shop sign |
| **Carpenter / Furniture** | Workshop + showroom | Furniture & wood goods (also the woodcutter) | Log piles, sawhorse, chopping block, stumps, **furniture on display** out front, sawn-plank sign; fewer trees + uneven regrowth nearby |
| **Smith** | Stone, soot-stained | Tools, metal goods, pen upgrades | Exterior **forge + anvil**, coal bin, tool rack, a horseshoe/anvil sign, glow of the fire |
| **Boat & Fishing Store** | On the **SW lake**, on **docks** | Fishing & boat gear | A moored **boat**, **anchor sign**, nets, crates of fish, lanterns on the dock posts |
| **Ecologist's House** | Cozy cottage | Ecology interpretation (only when engaged) | Specimen jars, charts, a small test garden, a bug terrarium, tagged plants. A knowledgeable resident, not a quest hub by default. |
| **NPC Cottages** (2–4) | Varied (comfy / rustic / tidy) | Villagers live here | Each themed differently — window boxes, a cat statue, laundry line, a chimney, a vegetable patch |

## Landmarks & little features
- **Civic square** (center, the visual anchor): ONE central element (well / old tree with a stone ring /
  monument), plus benches (unevenly placed), a notice board, a signpost (fast travel), flower beds, and a
  small **statue**. It should imply waiting, gathering, announcements, conversation.
- **SW lake**: a pond with the **fishing docks + boat**, reeds, lily pads, a frog or two.
- **Orchard** (edge, intentionally ordered): grid-aligned apple/orange rows with clear walking lanes,
  ladders, crates at row ends, **compost piles**, fallen fruit under the trees. *Apples fall fresh, age,
  then rot and draw flies — no placed rot props.*
- **Fly Farm** (edge, a landscape system not a building): compost piles, concentrated fallen apples,
  darkened soil, shallow puddles; net posts, hanging bait baskets, collection trays, simple wooden frames.
  Show failure too — broken nets, overrun patches, predator signs. It teaches fly farming by existing.
- **Lighting (non-protective):** lamps near doors and roads, sparse and uneven, removable. Some bugs
  dislike light; if players remove lamps, consequences are allowed. Lights are not safety.

## Materials / loot
- None mined here; the village is where you *spend* and *craft*. The Smith sells/upgrades pen materials
  (wood → iron → …) used for bug-farming.

## Biome composition (for the generator)
- Base **grass**, dirt patches, the stone road network laid first; buildings reserved along the roads;
  the lake (`terrain.pond`) carved SW with docks bridging onto it; orchard via `garden`, farms via
  `yard`/`garden`; meadow filled last with `scatter` (flowers, tall grass, bushes, tree clusters).
- **Meadow gradient:** keep flowers/flies/uneven grass active *inside* town; thin flowers and increase
  dirt/trampling near buildings; raise flower density and fallen-fruit/rot outside town.

## Scenes (showcase)
- `tools/zonegen/scenes/scene_village.py` — the full town (roads, all buildings, civic square, lake/docks,
  NPC cottages, decor). The worked vignette for this zone.
- (Optional) `scene_village_interiors.py` — the fancy Town Hall + a couple themed NPC interiors.

## Hard constraints (locked)
- ❌ No player housing (land is bought later, elsewhere) · ❌ no safe zones · ❌ no scripted events ·
  ❌ no artificial rot props (rot emerges from fruit age) · ❌ no dangerous bugs here.
- No advanced dungeon crafting (that's the Smith's shop, not a player furnace yet).

## Build / review checklist
- [ ] Village reads clearly; each building identifiable by sign + props.
- [ ] Orchard is structured; fallen apples present (rot emerges, not placed).
- [ ] Fly farm exists *outside* town as a landscape, with failure evidence.
- [ ] Roads connect logically and fade at the margins (no perfect symmetry).
- [ ] Decorations imply use/wear; meadow ecology stays active inside the village.
- [ ] `b.validate()` passes, 0 placement warnings; rendered preview looked right.
