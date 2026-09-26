# Research: how great 2D overhead games compose zones that feel alive (2026-07)

Digest of a five-track web-research sweep (Stardew/ALttP/Link's Awakening map dissections,
the BotW GDC talk, Romero's Doom rules, Worch & Smith's GDC 2010 environmental-storytelling
talk), kept as the paper trail for the composition rules zonegen adopts. Citations end each section.

## 1. Region identity & readable map shapes

**The killer anchor**: A Link to the Past's Light World is exactly our zone size — 256×256
tiles (an 8×8 grid of 32×32-tile chunks) — carved into ~11 regions: eight themed CORE
regions, "most of them notably 2×2 chunks" (64×64 tiles), plus connective pathway zones
"with an internal logic and visual consistency all their own" that hold the map together.
Regions are defined by natural borders (trees, rivers, cliffs), each with a unique theme.

**Link's Awakening's seam trick**: the GB overworld is 2×2-screen sections, each with its
own tileset; buffer sections between themes may only use tiles SHARED by both neighbors —
themes never collide raw, and "simpler areas alternate with higher-complexity ones."
**Stardew**: dense, not big — theme-park districts with unique activities in each.
Pixel-art practice (SLYNYRD): walkable ground stays low-contrast; leave real negative space.

**Rules we adopt**
- Carve the 256² zone into 5-9 NAMED regions, core ones ~64-100 tiles across; each answers
  "what is this place?" in one phrase — one job, one dominant ground cover, one signature prop family.
- Compose seams between themed regions only from vocabulary both sides share (grass/dirt/
  scatter), LA-style — never butt two signature palettes edge-to-edge.
- Region borders are natural barriers (forest mass, stream, block mass) pierced by 2-3
  authored gaps; check: the region outline reads on the render without a legend.
- Every region keeps ≥25% plain low-contrast walkable ground; no two maximum-density
  regions adjacent — quiet connective tissue between.

**Counterexample**: a uniform meadow with props sprayed at one global density — every
screenshot looks the same and no place has a name.

Sources: gamedeveloper.com "Overworld Overload" pt 1 · zladx.github.io
links-awakening-overworld-map · pcgamesn.com/stardew-valley/map-design · slynyrd.com pixelblog-20.

## 2. Landmarks, focal points & decision points

**Romero's Doom rule 8**: "create several easily-recognizable landmarks for easier
navigation" — landmark uniqueness is a navigation feature, not decoration. **BotW GDC
2017**: THREE sizes of "triangle" — large = distant landmark, medium = view-blocker hiding
a surprise, small = exploration tempo — plus "gravity": players orbit anchor to anchor,
side-tracked by small stuff placed between. **GB-Zelda screen language**: each screen is
a diorama — "some screens are self-contained objectives, others are built to point you in
the direction of those objectives." With no elevation, our view-blocker is the forest/block
mass you walk around; our sightline is the LEADING LINE (paths, fences, rows, wrack lines).

**Rules we adopt**
- Three-tier landmark budget: 1-2 zone-scale anchors (unique silhouette — nothing else in the
  zone shares their footprint+sprite), one region-scale focal per region, small junction markers.
- Every path junction is a decision point: each branch shows a DIFFERENT tease within one
  screen of the junction (sign text, ground-cover change, edge of a landmark).
- Approach composition: in the final screen before a focal, ≥2 linear elements (path axis,
  fence, rows, stream bank) point their long axis at it.
- Viewport test on the render: a camera-sized crop anywhere on a main route contains
  either a point of interest or a directional cue toward one.

**Counterexample**: three identical windmills in three corners — landmarks that can't be
told apart navigate worse than none.

Sources: doomwiki.org/wiki/John_Romero · gamedeveloper.com "5 design lessons from BotW" ·
nintendolife.com BotW triangles · blog.radiator.debacle.us 2017/10 · derekexmachina.com LA analysis.

## 3. Route rhythm & pacing

**The 40-second rule**: CD Projekt's Witcher 3 guideline — something interesting every
~40s of travel; a thesis measuring Skyrim found ~35.7s average between points of interest.
That's open-world scale; at cozy scale (Stardew) the beat is tighter: "paths are
deliberately crooked and indirect," and errands OVERLAP (berries spotted en route to the
lake) so travel is never dead time. **Romero rule 7**: make levels flow so the player
REVISITS areas — loops over out-and-backs. **LA**: themed sections alternate with generic ones.

**Rules we adopt**
- Main routes are never straight A→B: bend them around masses so the full route is never
  visible in one screen; each bend reveals the next interest point.
- Interest beat: a micro-POI (forage clump, bench, debris story, sign) every 20-40 tiles of
  main route; a major POI every 2-4 screens. Check: no camera-sized stretch of route with nothing in it.
- Prefer loops: every major POI reachable by ≥2 routes. Dead ends ONLY when the terminus
  pays off — count of no-payoff dead ends on the traced path network = 0.
- Alternate density along every route: dense pocket → quiet stretch → dense pocket; never
  two set pieces back-to-back without a breather.

**Counterexample**: one straight road linking every building, the zone's whole content
legible from the spawn screen — nothing left to discover by walking.

Sources: diva-portal.org diva2:1569059 ("The 40 Seconds Rule and POIs in The Witcher 3") ·
resetera.com threads/142132 · pcgamesn.com Stardew map-design · doomwiki.org/wiki/John_Romero.

## 4. Lived-in texture & environmental storytelling

**Worch & Smith (GDC 2010, "What Happened Here?")**: environments do four jobs — constrain
movement, communicate affordances, reinforce player identity, provide narrative context.
The storytelling move is the READABLE CHAIN OF CAUSALITY: arrange 2-3 props so a past event
can be inferred (their goldfish-flood scene). The player is the interpreter — imply, don't
caption. Be SPECIFIC: set dressing must echo THIS world's premise (BioShock's ATMs), never
generic clutter. **SLYNYRD**: detail lives in clusters overlapping tile boundaries (hides the grid).

**Rules we adopt**
- Micro-story quota: 2-4 per region, each ≥2 props in causal arrangement (tipped
  wheelbarrow + spilled compost trail + feeding beetles) answering "what happened here?"
  with no sign text.
- Wear where use: worn-dirt patches at doorsteps, gates, the well, path mouths — traffic
  history in ground tiles (our no-lighting substitute for grime).
- Clutter grammar stays bimodal: rows/right-angles near buildings, clumped density fields
  in the wild, a mixed band only at the seam. (Our rows/clumps rule, now cited.)
- Specificity check: prop clusters reference the bug-farming fiction (jars, nets, hive
  boxes, drying racks) — zero generic barrel-and-crate piles.
- Decorative clusters straddle tile boundaries; plain walkable ground carries no competing detail.

**Counterexample**: barrels and crates evenly scattered "for atmosphere" — clutter with no
cause, no owner, no story to read.

Sources: worch.com/files/gdc/What_Happened_Here_Web_Notes.pdf · gdcvault.com/play/1012647 ·
slynyrd.com pixelblog-20/-21.

## 5. Secrets, teases & rewards for curiosity

**Romero rules 5-6**: be strict about SEVERAL secrets per level; and "if the player can
see outside, he can somehow get there" — visible space is a promise. **Tunic (Shouldice)**:
locked "paths into the darkness" are fun because "curiosity and speculation is fun" — the
tease itself is content. **Animal Well (Basso)**: budget how many mysteries dangle at once —
too many become mental load. Stardew's Secret Woods: the gate (a log) is visible from day
one, the payoff hidden — visible-but-gated beats invisible.

**Rules we adopt**
- Every region hides ≥1 off-path payoff (clearing behind the forest rim, pocket behind a
  block mass) that plain walking off the path can find.
- Tease visibly: show the reward or its gate at the edge of reach — flowers across the stream,
  a chest through a 1-tile forest gap; gates must be legible (mineable plug, log, tool gate).
- Romero's promise: any visible walkable ground is eventually reachable — no painted-on
  fake spaces on the render.
- Dangle budget: 2-4 simultaneously visible-but-not-yet-openable teases zone-wide, not a dozen.
- Cozy-scale rewards: off-path curiosity always pays (forage, cosmetic, shortcut, sign
  lore) and never punishes.

**Counterexample**: a secret clearing with zero exterior cue, findable only by hugging
every forest edge pixel-by-pixel — hidden ≠ interesting.

Sources: doomwiki.org/wiki/John_Romero · gmtk.substack.com/p/the-secret-to-designing-mysterious
· gamerslearn.com curiosity-exploration-and-discovery · stardewvalleywiki.com/Secret_Woods.
