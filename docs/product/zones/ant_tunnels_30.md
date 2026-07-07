# Zone Design: Ant Tunnels (3,0 · `ant_tunnels_30`) — rev 2 (owner review 2026-07-07)

> Rev 2 incorporates the owner's line-item review verbatim. Authority: those rulings +
> D2/D3/D9/D18/D21/D22. *(candidate)* = cut freely. Lighting backlogged (compose in full
> light, glow anchors pre-placed). Objects need GAME REASONS — no decorative-only props.

## Overview
- **Zone ID / Grid:** `ant_tunnels_30` · row 3, col 0 · 256×256
- **Biome / Difficulty:** HALF OUTSIDE, half soil-and-stone underground · **EASY**
- **The layout (owner):** "make half of the easy ant zone outside so ants can form
  trails to food sources. The rock CLIFF FACE will start where it is in the next zone
  over, near the top, then in a natural way curve down and then across, letting ants
  have more room to do stuff." So: the cliff line enters at the EAST edge matching the
  mining zone's cliff height, curves naturally DOWN and then ACROSS toward the west —
  everything above/west of it is OPEN GROUND (grass long since transitioned to dirt,
  scrub, SPREAD-OUT forest, food sources); below/east of it is the rock-and-soil
  underground with the tunnel systems. Tunnel MOUTHS open along the cliff base.
- **The feel:** an outdoor ant country under a big sky, with the underground close
  enough to touch. Worker files run trails ANYWHERE food appears — a windfall under a
  fruit tree, a dead beetle in the scrub, a fungus patch in a tunnel room — and every
  trail eventually bends toward a dark mouth in the cliff. Inside: soil tunnels and
  small chambers against honest stone.
- **Scouts (owner):** "the scouts are going to be based in the lower part but cross
  zones — we have not implemented that yet, so that part is BACKLOGGED (ants heading up
  and out)." In-zone, scouts range the outside half and light the trails; the
  cross-zone foraging waits for real bug transfer. The old thin "surface strip" concept
  is superseded by the half-outside layout.

## Connections (map)
- **N → bee_meadow_20**: a plain edge into the meadow's southern gradient (which stays
  as built). Ant presence in the bee zone waits for cross-zone transfer (backlogged).
- **E → underground_passages_31**: THE STONE SEAM — "there should be a natural boundary
  like with the beginning mining zone all along the ant area and the rocky area." Rock
  runs the whole shared edge; the cliff line continues the mining zone's; the committed
  burrow stubs at y ≈ 96/124/138/158/168/200 remain the tunnel-level contract. Stray
  ore + stone in the seam (owner: "stray ore and stone is great").
- **S → ant_colony_40**: the main tunnel arteries descend; traffic thickens downward.
- **W**: world edge.

## Key species & ecology
- **v1 sim species:** `ant_worker` (files/trails — the zone's living signature) +
  `ant_scout` (ranges the outside; based lower per owner; cross-zone later). Nests =
  `ant_brood` piles (HAND-harvestable — no shovel; drops ant_egg). 2-3 small nests.
- **Food, inside and out (owner: "some food sources and ecosystem"):** OUTSIDE —
  rotting fruit under 2-3 wild fruit trees (flies aren't spawned here but may find it —
  fine), berry bushes, surface carrion as it happens. INSIDE — fungus gardens of REAL
  mushrooms (`mushroom_inkcap`, `mushroom_morel` — pool-flagged staples; owner: "actual
  mushrooms, not just 'cluster'"), litter drifts. Trails form to whichever is
  currently worth hauling.
- **Food stores are REAL ITEMS (owner):** granary chambers hold actual ground items
  (fruit, rotten fruit, dead bugs) — never decoration props. *(The ants-carry-items-to-
  chambers mechanic is a backlogged candidate; v1 stores are authored caches.)*
- **Tension:** one cave centipede den near the stone seam (owner-approved for EASY).
- **Drops:** `dead_ant` ONLY (D18) → the Bug Extractor yields **chitin** and **formic
  acid** (owner decision — recipes shipped).

## Landmarks & little features
1. **THE MAIN ENTRANCE** — the largest tunnel mouth at the cliff base, and beside it
   the zone's one human place: see Structures. A dirt ROAD runs from the north edge to
   it. Several smaller side-mouths open along the cliff elsewhere.
2. **THE CLIFF LINE** — the zone's spine: stone entering high at the east, curving
   down-and-across; mouths, scree, and stray ore along its foot.
3. **THE FORAGE GROUNDS (outside)** — spread-out forest stands, fruit trees with
   windfall rings, berry scrub — the trail destinations. Watching a file form to a
   fresh windfall IS the zone's show.
4. **THE CROSSROADS CHAMBER (inside)** — the first junction; three tunnels, three
   traffic streams.
5. **THE FUNGUS TERRACES (inside)** — inkcap and morel gardens tended by workers.
6. **THE GRANARY (inside)** — a chamber cached with real fruit/rotten-fruit/dead-bug
   items. Steal at your own pace; the colony restocks what it can.
7. **THE ABANDONED DIG (at the stone seam)** — a half-collapsed side tunnel from the
   mining tier, IN STONE (owner): bent rails, a crushed mine cart, timbers.
8. **THE CENTIPEDE DEN (stone seam)** — shed segments outside a rock pocket; the hiss
   before the sight.
9. **BROOD CHAMBERS (inside, lower)** — ant_brood piles and nurse traffic; the
   colony proper thickens below toward (4,0).

## Secrets (game-reasoned)
- **The Lost Miner's Pack** — off the Abandoned Dig, in stone: a rucksack cache
  (lantern, tools, loot). Reason: loot + mining-camp lore thread.
- **The Sealed Breach** — a dirt-block plug where the ants walled off the miners'
  breakthrough; diggable; a cache behind it. Reason: dig gameplay + the seam's story.
- **The Blocked Side-Run** *(candidate)* — a collapsed side tunnel at the seam that can
  be dug open to a small stray-ore pocket (owner-approved ore). Reason: rewards
  players who probe the cliff base.
- *(Cut by owner: the shiny hoard, the daylight inversion, both micro-stories, the
  ventilation chimney, the taproot.)*

## Structures / NPCs (owner-decided)
- **THE MYRMECOLOGIST'S STATION — a live vendor in a WOODEN BUILDING near the main
  entrance** (owner: "a wood building... the main [tunnel] has the building and the
  dirt road, with a pen that is EMPTY, and stuff inside like the ecologist's but ant
  oriented — wooden wall building on the dirt"). Interior: cot, table, chair, specimen
  shelf/case + terrarium (ant-study gear), lantern, crates — every object with a game
  reason; NO trade board. The EMPTY PEN outside sits ready (its game reason arrives
  with ant husbandry — a deliberate tease that becomes real). Sells/buys: ant-line
  goods (ant_egg trade, light gear, fungus-farm starter — exact stock at economy pass).
- **A new SCENE is required:** `scene_ant_entrance.py` — the building + dirt road +
  empty pen + main mouth + side mouths + cliff face. (Owner: "need to create a scene
  for the entrance.")

## Materials / loot
- Blocks: `dirt_block` soil; STONE along the whole east seam + under the cliff line
  (the natural boundary), with stray ore + stone in the seam (owner-approved); no ore
  in pure colony soil otherwise.
- Gatherables: ant_egg (hand, from brood piles), real mushrooms, windfalls, moss/glow.
- Extractor: dead_ant → chitin / formic_acid (shipped).

## Biome composition (for the generator)
Outside half (N/W): dirt-transitioned ground with grass remnants, SPREAD-OUT forest
stands (village recipe, generous clearings), 2-3 fruit trees + berry scrub, the dirt
road north-edge → main entrance. The CLIFF LINE: a natural curve (noise-warped, C13 —
never a ruled arc) of stone_block face from the east edge's mining-zone height, down
and across; scree + stray-ore veins (doctrine) at its foot; mouths = dirt-block mound
forms + dark openings. Underground (S/E): dirt_block soil tunnels + chambers against
stone walls (ant-colony.md doctrine), fungus terraces (inkcap/morel pools), granary
item caches, brood chambers, the stone-seam features; south arteries to (4,0); the
east burrow stubs at the contract rows.

## Backlogged from this review (owner)
- Scouts based in the lower colony CROSSING ZONES up/out — waits for real bug transfer.
- Ants CARRYING real items to chambers (the transport mechanic).
- The ant BROOD system deep pass ("backlog the entire brood testing").

## Owner decisions recorded (2026-07-07)
Live vendor ✓ · formic/chitin via extractor ✓ · stray ore + stone at the seam ✓ ·
centipede den in EASY ✓ · half-outside layout ✓ · real mushrooms ✓ · brood = hand ✓ ·
stores = real items ✓ · no board/chimney/taproot/hoard/inversion/micro-stories ✓.

## Not present
Ant mounds as objects (blocks form everything) · the Queen (below) · soldiers/castes
v1 · aphids (teased at 4,0) · cross-zone ant traffic (backlogged) · new decoration
props without game reasons.
