# Zone Design: Centipede Cavern (4,1 · `centipede_cavern_41`)

> Authority: the owner grid (architecture_world.md: row 4, **MEDIUM**, "stalactites, side
> caverns"; D2/D3 relocation; D21 species notes; D22 "no rocks/boulders/stalagmites —
> only stone_block + mineral blocks") + owner rulings 2026-07-06. The 30KB economy sheet
> runs HOTTER (HARD/T3→T4) — treat its economy as *(candidate)*, the grid as truth.
> Lighting backlogged; this zone is the future lighting pass's SHOWPIECE, so every glow
> anchor placed now is a promise kept later (R5).

## Overview
- **Zone ID / Grid:** `centipede_cavern_41` · row 4, col 1 · 256×256 · fully underground
- **Biome / Difficulty:** deep karst caverns · **MEDIUM** (the grid's word) with the
  zone's HARD moments living in its den + deep pockets
- **The feel:** the mining camp above is human space — rails, torches, order. Climb down
  its southern shafts and the architecture stops being anyone's: galleries the water
  carved over deep time, hung with glowworm constellations, floored with black pools.
  It is the most beautiful dark in the game and the most dangerous: this is the
  centipedes' country. You hear the zone before you see it — drips, skitters, and the
  0.8-second HISS that is the game's oldest telegraph. Where (4,0) is a city of order,
  (4,1) is wilderness underground: the detritivore web inverted into quiet horror.
- **The light story (the headline):** glowworm colonies + glow mushrooms are the only
  natural light (D21) — placed NOW as composition anchors, they become literal light
  sources when the backlogged lighting ships. Keep most of the zone dark-by-default;
  the glow rooms are the destinations.

## Connections (map)
- **N → underground_passages_31 (the Mining Camp)**: 2+ shafts/tunnels up (architecture
  req) — one is the RAIL STUB story (see secrets), one a natural chimney. Difficulty
  steps up crossing south.
- **W → ant_colony_40**: the dirt-vs-rock seam; centipede dens cluster this side and RAID
  the colony (the shared war both zone docs tell from opposite sides).
- **E → (4,2) Underground River (future)**: the east edge trends WET — flooded galleries,
  a current heard through the wall. Contract reserved: water enters/exits here when (4,2)
  is built.
- **S**: world edge (hard; row 5 deferred).

## Key species & ecology (the detritivore web, inverted)
- **The base:** fungus + litter + `bat_guano`-style nutrient pockets *(candidate name
  pending owner D22 material rulings)* → **cave crickets/beetles** graze it.
  v1 pragmatic roster: tuned variants of EXISTING tech — `millipede` (cave-tuned litter
  detritivore) + `beetle_carrion` variant as the cave beetle *(new sprites queued in
  BACKLOG: cave beetle, cave millipede)*.
- **The light keystone:** **glowworms** *(NEW species candidate — D21 names them + the
  sprite is in BACKLOG; catchable → firefly-style lantern)* — ceiling colonies over the
  grottos; prey for climbers; the reason to look UP.
- **The apex:** **GIANT CENTIPEDE** — the existing centipede tech (individual category,
  carrion-first, hiss→lunge telegraph, gnaws WOOD but stone stops it) re-tuned + the
  segmented giant sprites that already exist in bugs.json, zoned here. Dens in side
  caverns; patrols the galleries; scavenges the web's dead.
- **The ambush layer:** **cave spiders + WEBS** — the BACKLOG's "don't forget!" lands
  HERE (D21: small webbed spiders in the lower underground, NOT the first Mining Camp).
  Web-choked side passages; drop-on-silk. *(Spider SIM is designed-not-built and NOT in
  this plan's scope — the zone doc reserves their caverns; v1 places webs as decor +
  spawn areas ready.)*
- **Mini-boss candidate** *(owner decides)*: the **Centipede Matron** — a den mother in
  the Great Crevice: nest+brood machinery under a scripted-encounter skin (the Queen's
  pattern, hostile flavor). Drops the potent-venom tier.

## Landmarks & little features (hooks on every one)
1. **THE DRIPSTONE HALL** — the signature gallery: a long vaulted cavern, ceiling teeth
   and floor columns BUILT FROM stone_block clusters (D22 — no stalagmite objects; the
   blocks literally form them, same law as the ant mounds). *Hook: the hall runs deeper
   than any light reaches.*
2. **THE GLOWWORM GROTTO** — the ceiling is a star-field; a still pool doubles it. The
   most beautiful room in the underground, in the most dangerous zone. *Hook: stars that
   MOVE.*
3. **THE GREAT CREVICE (the Den)** — a canyon-crack cavern; shed segments, bone drifts,
   the Matron's brood *(candidate)*. The zone's HARD room. *Hook: every skitter echoes
   from it.*
4. **THE FLOODED GALLERY (east)** — black water over a drowned passage toward (4,2);
   albino shapes below. *Hook: the current SOUNDS through the east wall.*
5. **THE RAIL STUB** — man-made straight tunnel w/ mine_rail + supports, ending at a
   collapse... from the CAMP side. They broke through, saw the hall, and RAN — dropped
   tools point back north. *Hook: what made experienced miners abandon a rail line?*
6. **THE HERMIT'S NOOK** *(candidate NPC — owner decides)* — a lamp-lit pocket cave,
   specimen jars, venom-ink notes. The rare-specimen/recipe vendor seam. *Hook: a lit
   window in the dark.*
7. **THE HERMIT'S FIRST CAMP** — abandoned: shredded tent, scattered notes (lore
   breadcrumbs: he mapped the dens the hard way). *Hook: the notes end mid-sentence.*
8. **THE GUANO CHAMBER** — a roost-shaft ecosystem: nutrient heaps → fungus riot →
   cricket swarms. The web's pantry. *Hook: the LOUDEST room — life in the dark.*
9. **THE CRYSTAL GEODE POCKET** — a gem cavity glinting through a 1-block window
   (Terraria tease — dig around, not through, or meet what nests beside it). *Hook: the
   glint itself.*
10. **THE SINKHOLE SHAFT** — one thin column of true daylight from far above, dust
    dancing in it, green moss ring below. *Hook: the only sun in the zone — and something
    suns itself there.*

## Secrets (≥3), surprise, micro-stories
- **Secret — the Geode Pocket** (above): visible-but-gated riches; the approach is the
  puzzle.
- **Secret — the Amber Chunk:** in a wall off the Dripstone Hall, a fist of amber with an
  ANCIENT BUG inside — the game's deep-time wink. Payoff: unique curio/trophy.
- **Secret — the Prospector's Cache:** the rail-stub collapse hides a survivor's stash on
  its far side (dig the bypass): lantern, silver-tier pick, a note that names the Hall.
- **Surprise (the inversion):** a "stone_block cluster" on the Dripstone Hall floor that
  is a SLEEPING giant centipede — the boulder breathes. (The D22 no-boulders rule becomes
  a gameplay gag: the only "boulder" in the game is alive.)
- **Micro-story 1:** the two hermit camps — the abandoned first camp and the lived-in
  nook — chart one researcher's learning curve in furniture.
- **Micro-story 2:** the rail stub's dropped tools all point north; the collapse was
  dropped BEHIND them. Someone bought time.

## Structures / NPCs (owner decides at review)
- **The Hermit researcher** *(candidate — the architecture hub table reserves him)*:
  rare live specimens, light gear, venom/glow recipes, buys venom+lumen high. If cut: the
  nook stays abandoned (both camps become pure lore).
- The rail stub + supports = the only other "structure" (man-made straight tunnels carry
  rails per caves.md doctrine).

## Materials / loot (row-4 doctrine)
- **Ore (the paycheck for surviving):** caves.md §4 veins ONLY, row-4 band: iron/silver
  baseline, **gold + platinum + diamond deep** + crystal clusters — MEASURED (13-16%
  ore-bearing, deep fifth 20-25%). This is the zone where deep-tier ore lives.
- **Gatherables:** glow forage (mushroom_glow, cave_moss), crystal (wall clusters),
  *(candidates pending owner)*: glowworm lumen/silk (light crafting), venom glands
  (two-tier: common → Matron-gated potent).
- **Bug drops:** dead_centipede etc. per D18 (extractor processes); venom/lumen framed as
  gathers/encounter loot, not drops — same D18-clean pattern as the Queen.

## Biome composition (for the generator)
Solid `stone_block` via fill_solid + the row-4 ore table (doctrine veins, probe-measured);
caverns via `carve_cavern` (gallery for the Hall, lobed/rocky for dens — rocky's interior
columns ARE the "stalagmites", D22-legal); `carve_chamber` side pockets; ISOLATION kept
(mining zone law: caverns not tunnel-linked; the player mines between them) EXCEPT the
authored spine: north shafts → Hall → Grotto fork. ONE straight rail tunnel (mine_rail +
supports) ending at the collapse. `cave_pool` in ~half the big rooms (off-center, bayed);
the flooded east gallery reserved for (4,2). Glow anchors: grotto ceiling field, pool
rims, fungus pockets. Webs + spider spawn areas in 2-3 side passages. West-seam breach
stubs matching (4,0); north shafts matching (3,1)'s south.

## Craft brief (zone-craft quotas)
- **The promise:** the beautiful dark — every light is a destination, every sound a
  warning.
- **Brainstorm (27 kept / 7 categories):** *spaces:* dripstone hall, grotto, crevice den,
  flooded gallery, guano chamber, sinkhole shaft, geode pocket, chimney shafts; *light:*
  glowworm fields, glow pools, mushroom pockets, the daylight column; *threat:* matron
  den, web passages, drop-spiders, the sleeping "boulder", patrol routes; *relics:* rail
  stub, dropped tools, two hermit camps, prospector's cache, amber bug; *loot:* row-4
  veins, crystal clusters, venom tiers, lumen; *water:* dripstone pool, black sump,
  east current; *whimsy:* the moving stars, dust in the sunbeam, a cricket chorus that
  goes silent exactly when you stop.
- **Ground variety (4+):** stone_block mass → cave_floor galleries → pool water → guano/
  fungus accents → rail-bed strip.
- **The deliberate rule-bend:** ONE authored connected spine in an isolation-law zone
  (north shafts→Hall→Grotto) — the tourist route that teaches the zone before the
  isolation doctrine makes the player earn everything else.
- **Interest quotas:** 3 secrets ✓, surprise inversion ✓ (the breathing boulder), hooks
  all 10 ✓.

## Owner decisions needed (P4 review)
1. Difficulty label: grid says MEDIUM, sheet says HARD — confirm MEDIUM w/ hard moments?
2. Hermit NPC: live vendor, abandoned-only, or cut?
3. Centipede Matron mini-boss: in, later, or never?
4. Glowworm as a real new species now (sprite + catchable lantern) or glow-decor first?
5. D22 materials check: dripstone/stalactite DECOR ids are drafts — bless a minimal set
   (or stone_block clusters only)?
6. Cave spider timing: webs+spawn-areas now with spider sim later (recommended), or hold
   webs too?

## Not present
Bats/vertebrates (bug game) · the deep-tier horrors (deep_stalker/gem_mimic — deeper
zones' material) · fire/lava anything · the row-5 depths (deferred) · torch-lit safety
(the camp above owns "safe") · stalagmite OBJECTS (D22 — blocks form everything).
