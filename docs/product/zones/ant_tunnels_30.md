# Zone Design: Ant Tunnels (3,0 · `ant_tunnels_30`)

> Authority: owner rulings 2026-07-06 + D2/D3/D9/D17/D18/D21/D22 are the floor; everything
> labeled *(candidate)* is mined from assistant-drafted sheets/brainstorms and needs no
> permission to CUT, only to keep. Lighting is BACKLOGGED — the zone must read composed in
> full light AND be dark-ready (glow anchors are placed where the future lighting pass
> will want them, so it never rearranges rooms).

## Overview
- **Zone ID / Grid:** `ant_tunnels_30` · row 3, col 0 · 256×256
- **Biome / Difficulty:** underground soil tunnels + a LIT surface strip · **EASY** (the
  gentle introduction to the underground and to ants)
- **The feel:** you walk south out of Bee Meadow's dirtying gradient and the ground simply
  wins — scrub, windfall fruit, and then dark mouths in low dirt-block mounds. Below: a
  branching world of narrow soil tunnels the ANTS dug, alive with purpose. Files of workers
  stream between fungus rooms and food caches; scouts pop up into the daylight strip and
  drag windfalls down. Nothing here wants to hurt you (this is the EASY zone) — the place
  itself is the fascination: follow any file of ants and it TAKES you somewhere. The
  signature image: **a line of ants hauling fruit down a sunlit shaft.**
- **Owner anchor (2026-07-06):** "above that [colony] tunnel systems scouts use which lead
  outside (south of the bee zone)"; D21: "Scout ants = top of the western ant zone (3,0,
  range far/forage out)."

## Connections (map)
- **N → bee_meadow_20**: the LIT SURFACE STRIP (normal day/night, owner ruling) — the top
  ~20-30 rows are outdoor ground continuing Bee Meadow's C12 gradient southward (dirt,
  scrub, berry bushes, 1-2 fruit trees, dry grass). Crossing the edge lands mid-gradient,
  exactly as C12 demands. The strip holds the **2+ tunnel mouths** (architecture req).
- **E → underground_passages_31 (the Mining Camp)**: THE BURROW SEAM CONTRACT — the built
  camp already emits ant burrows out its WEST edge at **y ≈ 96, 124, 138, 158, 168, 200**
  ("the colony continues into the zone to the WEST", zone_underground_passages.py). Our
  EAST edge must present matching dirt-seam burrow stubs at those rows. (Live ants do NOT
  cross until real cross-zone bug transfer ships — backlogged, owner ruling #1.)
- **S → ant_colony_40**: the MAIN SHAFT descends off our south edge into the colony
  proper; darkness and traffic both thicken toward it. 1-2 additional minor tunnels also
  exit south (the colony has more than one artery).
- **W**: world edge (hard).

## Key species & ecology (the food web)
- **v1 sim species (DECIDED):** `ant_worker` (tiny swarms 2-5 — files read as LINES;
  forager: fungus pools + carrion + rotten windfalls; provisions brood) and `ant_scout`
  (1-2, ranges far, pure sensor — registers food into colony memory; the trails follow
  scout routes). Nests anchor on **`ant_brood`** piles in small chambers (2-3 nests here —
  outposts of the true colony below).
- **The staple:** FUNGUS — existing mushroom entities (`mushroom_cluster`/`mushroom_brown`,
  pool-flagged so they deplete and regrow) in tunnel-side gardens + leaf-litter drifts
  blown down the shafts. **The bonanzas:** windfall fruit rotting on the strip (the
  `rotten_fruit` wildcard) and surface bug carrion — these are what the visible trails
  chase.
- **Ambience/prey (surface strip):** flies + butterflies low (windfalls), a firefly or two
  at dusk near the mouths.
- **Tension without danger:** ONE cave centipede den near the east (mining-camp) seam —
  heard hissing before seen, avoidable, an EASY-zone preview of what lives deeper.
- **Later candidates** *(candidate — owner call at review)*: garden/black/harvester ant
  castes, aphid teaser pasture, antlion pit, cordyceps flavor. None in v1.

## Landmarks & little features (curiosity hook per entry)
1. **THE SUNLIT SHAFT** — the widest surface mouth: a dirt-block mound form with daylight
   pouring down its throat; workers haul fruit DOWN it in a visible file. *Hook: the file
   itself — where are they taking it?*
2. **THE FORAGE TRAIL** (surface) — a worn line across the strip from a fruit tree to a
   mouth, petals + chewed-leaf scraps along it. *Hook: follow it either direction.*
3. **THE CROSSROADS CHAMBER** — the first junction underground; three tunnels, three
   traffic streams, one chewed-smooth pillar. *Hook: three ways down, each sounding
   different.*
4. **THE FUNGUS TERRACES (intro-scale)** — a chamber of pale shelf-fungus rows tended by
   workers; the zone's larder. *Hook: a side alcove glows faintly (mushroom_glow).*
5. **THE FORAGER'S GRANARY** — a food-store chamber: seed husks, fruit stores, a neat
   refuse rim. Steal here and the room notices. *Hook: the tidy hoard implies an owner.*
6. **THE VENTILATION CHIMNEY** — a hollow root-husk shaft breathing cool air, faint light
   far above. *Hook: a draft in a dead end says "this connects."*
7. **THE ABANDONED DIG (east seam)** — a half-collapsed side tunnel from the mining tier:
   bent rail stubs, a **crushed mine cart**, timbers. The miners came THIS far west.
   *Hook: the rails point east — toward the camp.*
8. **THE CENTIPEDE DEN (east seam)** — a rock pocket where the soil meets stone; shed
   segments outside. *Hook: the hiss, before you ever see it.*
9. **THE TAPROOT DESCENT** — a chamber threaded by a massive living root running DOWN past
   the floor. *Hook: the nest continues beneath — (4,0) is calling.*
10. **THE MYRMECOLOGIST'S CAMP** *(candidate NPC — owner decides)* — a lamp-lit tent at the
    safest surface mouth: field notes, specimen jars, an ant-egg trade board.

## Secrets (≥3), surprise, micro-stories
- **Secret — The Lost Miner's Pack:** in a pinched crawl off the Abandoned Dig: a rucksack,
  a STILL-LIT lantern, bones under bone-white fungus. Payoff: loot + the question nobody
  answers.
- **Secret — The Sealed Breach:** a patch of wall where the ants bricked up (dirt-block
  plug, different texture) whatever the miners opened. Diggable. Behind it: a cache and
  scratch marks on the FAR side. *(What sealed it — them, or the ants?)*
- **Secret — The Shiny Hoard:** ants collect glitter — a hidden alcove of coins, a copper
  nugget, glass beads, one gem, guarded by nothing but traffic. Found only by following a
  worker that ISN'T carrying food.
- **Surprise (the inversion):** the first long trail a player follows underground leads UP
  — out a hidden mouth under a berry bush into full daylight. The underground breathes out.
- **Micro-story 1:** the crushed mine cart under the collapse — the dig broke into ant
  tunnels, and the ants patched THEIR side neatly while the human side still gapes.
- **Micro-story 2:** one fruit tree on the strip is ringed by a worn circle of forage
  trail — the ants got there first, every season, forever.

## Structures / NPCs (owner decides at review)
- **Myrmecologist's Camp** *(candidate)* — vendor/tutorial NPC (ant lore, first light gear,
  fungus-farm starter, buys ant_egg/fungus). The architecture hub table reserves this slot.
  If cut: the camp stays as an ABANDONED research nook (tent + jars + notes = free lore).
- No other structures — the zone's architecture IS the nest (block-built, owner ruling #4).

## Materials / loot (D18-aligned)
- **Blocks:** `dirt_block` everywhere (shovel tier; the whole zone digs), minority
  `stone_block` pockets. **NO ore veins in ant soil** (ant-colony.md doctrine); the east
  seam MAY carry 1-2 stray copper/coal veins as the mining camp bleeds in *(candidate)*.
- **Gatherables:** `ant_egg` from `ant_brood` piles (shovel), mushrooms + `cave_moss` +
  `mushroom_glow` (light forage), windfall fruit on the strip.
- **Bug drops:** `dead_ant` ONLY (D18 — the Bug Extractor does the rest). The sheets'
  formic/chitin per-caste drop ladders CONFLICT with D18 → **owner question**, not data.

## Biome composition (for the generator)
Surface strip (top ~24 rows): outdoor grass/dirt continuing bee_meadow's gradient_field
southward (same warp/noise vocabulary), scrub scatter, 1-2 fruit trees + berry bushes,
2-3 dirt-block mound FORMS (blocks, never objects) over shaft mouths. Below: solid
`dirt_block` fill via `fill_solid` (stone pockets, no ore); `carve_tunnel(style="natural")`
main shaft (proven tuning: wobble≈0.7, bias≈0.16) + branch tunnels (wobble≈0.55);
`carve_chamber`/`carve_cavern(blob, 3-5)` rooms; 2-3 `ant_brood` nests in brood chambers;
mushroom pools in garden chambers; litter drifts under shafts; east-edge burrow stubs at
the CONTRACT rows (y ≈ 96/124/138/158/168/200); south-edge shaft exits. Files of ants =
live sim (the trails), NOT placed decor — plus a few `place_bug` dressing ants for the
preview renders only.

## Craft brief (zone-craft; quotas: 25+ brainstorm / 6 categories · 3+ landmarks · 2+
## micro-stories · 3+ ground materials · edges · 1 rule-bend · owner questions)
- **The promise:** "follow the ants" — every file is a signpost, every mouth a question.
- **Brainstorm (28 kept across 7 categories):** *activity/work:* fungus terraces, granary,
  brood outposts, forage trail, milking teaser *(cut → 4,0)*, compost rim; *people & wear:*
  myrmecologist camp/nook, miner's pack, abandoned dig, sealed breach, rail stubs;
  *nature:* taproot descent, ventilation chimney, glow alcove, litter drifts, root curtains
  *(cut: root arch — save for 4,0's Trunk Tunnel)*; *ground/water:* dirt-block mound forms,
  stone pockets, damp sump puddle, the strip's gradient; *loot:* shiny hoard, ant eggs,
  windfalls, moss/glow forage; *whimsy:* the up-into-daylight trail, a worker carrying an
  absurdly large petal, the not-carrying-food worker who leads to the hoard; *threat:*
  centipede den, antlion pit *(cut — MEDIUM material)*.
- **Ground variety (4+):** outdoor gradient dirt/grass/scrub → dirt_block soil → stone
  pockets → cave_floor chamber floors (+ glow/moss accents).
- **The deliberate rule-bend:** an EASY zone with a (single, avoidable) predator den — the
  hiss teaches "deeper = danger" better than any sign, and C-rules say guides bend when
  the context earns it.
- **Interest quotas:** 3 secrets ✓, 1 surprise inversion ✓, hooks on all 10 landmarks ✓.

## Owner decisions needed (P4 review)
1. Myrmecologist NPC: live vendor, abandoned nook, or cut?
2. D18 vs the sheets' formic/chitin ladder — dead_ant-only confirmed, or new mats?
3. Stray ore in the east seam: yes (mining bleeds in) or keep ant soil 100% clean?
4. The centipede den in an EASY zone: keep the rule-bend or move it to (3,1)'s side?
5. Zone id `ant_tunnels_30` and the surface-strip depth (~24 rows) — confirm.

## Not present
Ore veins in ant soil · soldiers/castes beyond worker+scout (later) · aphid livestock
(teased only at (4,0)) · the Queen (she's below) · ant_mound OBJECTS (deprecated — blocks
form the mounds) · live cross-zone ant traffic (backlogged: real transfer).
