# Zone Design: Ant Colony (4,0 · `ant_colony_40`)

> Authority: owner rulings 2026-07-06 ("they will have their colony in the sw ant zone";
> Queen "scripted like a game is fine"; structures are BLOCK-BUILT from dirt blocks) +
> D2/D3/D9/D18/D21/D22. *(candidate)* items are mined from assistant drafts — cut freely.
> Lighting backlogged: compose readable in full light, glow anchors pre-placed (R5).

## Overview
- **Zone ID / Grid:** `ant_colony_40` · row 4, col 0 · 256×256 · fully underground
- **Biome / Difficulty:** the colony superorganism · **MEDIUM** (D3: the medium tier holds
  the Colony Queen — a mid-game MINI-boss, distinct from the deferred row-5 grand Queen)
- **The feel:** (3,0) was tunnels; THIS is a CITY. The architecture opens up — galleries,
  terraced farms, granaries, nurseries — all of it dug, all of it dirt-block, all of it
  BUSY. The colony reads as one organism: food flows inward along trails, brood outward
  from the nurseries, and everything converges on the deepest room, where the Queen sits
  in a chamber that is — the zone's surprise — BEAUTIFUL: a fungus-garden cathedral, softly
  glowing, tended constantly. You are tolerated here (workers ignore you) until you touch
  what's theirs: brood theft and wall-breaking summon defenders. Steal like a thief, not a
  bulldozer.

## Connections (map)
- **N → ant_tunnels_30**: the MAIN SHAFT arrives from above + 1-2 minor arteries; traffic
  density is the wayfinding (thicker = deeper).
- **E → centipede_cavern_41**: THE RAID SEAM — where colony soil meets cavern rock. 1-2
  breach tunnels; giant centipedes den on the far side and RAID this edge (the colony's
  visible enemy; dirt-vs-rock is the ecological seam, D21).
- **S / W**: world edges (hard). Row 5 is deferred (D2) — the Deep Sump landmark teases
  what returns there someday.

## Key species & ecology (the superorganism web)
- **v1 sim species (DECIDED):** `ant_worker` (the mass — files everywhere, foraging fungus
  gardens + carrion + stores, provisioning many `ant_brood` nests) and `ant_scout`
  (fewer than (3,0) — this zone's food is mostly HOME-grown; scouts matter at the raid
  seam and the shafts). Multiple brood-anchored nests = the colony founds/recovers
  emergently (the built nest machinery).
- **The engine:** FUNGUS GARDENS — dense pool-flagged mushroom chambers, the colony's
  staple; litter + refuse feed the compost pits *(compost = existing detritivore/compost
  systems where applicable)*.
- **The enemy:** giant centipede(s) denned at the east seam, raiding worker files —
  predator pressure the colony visibly answers (defenders converge; a raid aftermath =
  scattered dead_ant = a feast-trail for the survivors. The ecosystem eats its tragedies).
- **The QUEEN (scripted, owner ruling #2):** a mini-boss FIXTURE in the deepest chamber —
  a scripted encounter layered on the nest system (guards + brood piles as the fight's
  adds/objectives), NOT a sim species. Fight design = its own later slice; the zone doc
  reserves the arena.
- **Later candidates** *(owner call)*: soldier caste (the intended defense upgrade),
  harvester ants + seed caches, **aphid livestock pastures** (the ecology_proposal
  mutualism — honeydew ranching, disruptable), parasite flavor (phorid fly, cordyceps),
  replete honeypot larder.

## Landmarks & little features (hooks on every one)
1. **THE GREAT TRUNK TUNNEL** — the colony highway: a wide gallery threaded through an
   ancient ROOT SYSTEM (the root arches are the architecture), two thick worker columns
   streaming opposite directions. *Hook: both directions promise an origin and a
   destination.*
2. **THE FUNGUS GARDEN TERRACES** — stepped chambers of pale cultivated shelves, workers
   tending rows; the colony's breadbasket. *Hook: one terrace is BLIGHTED (black mold) —
   and the ants are quarantining it.*
3. **THE BROOD NURSERIES** — galleries of `ant_brood` piles, nurse traffic, warm color.
   The theft target. *Hook: the deeper nursery glows amber — royal brood?*
4. **THE GRANARIES** — food-store rooms: fruit, seed husks, carrion stores stacked with
   unsettling neatness. Loot rooms guarded by sheer traffic. *Hook: a half-blocked side
   door the ants don't use.*
5. **THE AphID PASTURE** *(candidate — teaser if livestock deferred)* — a root-wall
   chamber: EITHER live aphids being milked, OR (deferred) an empty pen — sap-slick roots,
   honeydew residue, waiting. *Hook: what grazed here?*
6. **THE QUEEN'S CHAMBER** — the deepest, largest dome: the fungus-garden CATHEDRAL. The
   Queen fixture at its heart, guards at the Royal Antechamber gate. *Hook: the approach —
   the Antechamber's giant-soldier silhouettes — is visible one full screen before the
   fight is committed.*
7. **THE ROYAL VAULT** — sealed behind the Queen's chamber: royal jelly + queen-tier loot.
   Opens only after the encounter. *Hook: a glowing seam in the cathedral's back wall.*
8. **THE COMPOST PITS** — the refuse tier below the gardens; midden mounds, bone flecks,
   puffball clutches that BURST. *Hook: things glint in the midden.*
9. **THE DEEP SUMP** — a flooded gallery at the zone's bottom edge, black still water,
   something pale moving under it. *Hook: row 5 will return someday; this is its door.*
10. **THE RAID SCAR (east seam)** — a breach tunnel mid-repair: dirt-block plugs, dead
    ants, shed centipede segments. An active front line. *Hook: the repair is FRESH.*

## Secrets (≥3), surprise, micro-stories
- **Secret — The Ore-Studded Wall:** the ants tunneled AROUND a gem pocket (they don't
  care; you do). Visible as glints through a 1-block window off a minor gallery; dig the
  long way around to reach it. Deep-tier reward, guarded by proximity to the Antechamber.
- **Secret — The Sealed Breach (south):** a plugged tunnel at the SOUTH edge — the ants
  sealed something out (or in) below. Behind the plug: claw-scored walls, one elite-tier
  loot cache, and a cold draft going DOWN. (The row-5 tease made physical.)
- **Secret — The Honeypot Ceiling** *(candidate)* — a hidden larder chamber whose ceiling
  hangs with replete ants (living amphorae). Harvestable honeydew — if you dare tap them.
- **Surprise (the inversion):** the Queen's chamber is not a horror pit — it's the most
  beautiful room in the underground so far: cultivated glow, clean architecture, order.
  The monster is a gardener.
- **Micro-story 1:** the Blighted Terrace — ants carrying infected shelves AWAY in a
  quarantine file, dumping them in a specific compost pit. The colony practices medicine.
- **Micro-story 2:** the Raid Scar's repair plug is layered — dig it open and the strata
  show it's been breached and re-sealed MANY times. This war is old.

## Structures / NPCs (owner decides at review)
- No human structures inside the colony (it IS the structure). *(candidate)*: the
  Myrmecologist (if kept at 3,0) refers the player DOWN here with a quest-shaped rumor
  ("the Queen is the prize"). The Royal Antechamber + Vault are the zone's "buildings".

## Materials / loot (D18-aligned; queen drops flagged)
- **Blocks:** `dirt_block` city; `stone_block` bones of the deep walls; NO ore veins in
  colony soil EXCEPT the Ore-Studded Wall secret pocket *(single authored exception —
  doctrine-placed veins inside its stone pocket, not hand-set cells)*.
- **Gatherables:** `ant_egg` (brood piles — plentiful here, guarded), fungus + glow
  forage, honeydew *(if aphids approved)*.
- **Bug drops:** `dead_ant` only (D18). **Queen-encounter rewards** *(candidate, owner
  prices this)*: royal jelly + a queen trophy/armor material + royal brood eggs — framed
  as ENCOUNTER loot (chest/vault), not bug drops, so D18 stays clean.

## Biome composition (for the generator)
Solid `dirt_block` fill, stone at depth walls; the chamber graph: Trunk Tunnel spine
(wide, root-arched) → terraces/nurseries/granaries clustered by function (the city has
DISTRICTS) → Antechamber → Queen's dome (carve_cavern lobed, size 6-7) → Vault. Many
`ant_brood` nests; dense pool-flagged mushroom gardens; compost pits with litter pools;
the Deep Sump cave_pool at the south; east-seam breach stubs matching (4,1)'s west edge;
north shaft mouths matching (3,0)'s south exits. Traffic = live sim + preview dressing.

## Craft brief (zone-craft quotas)
- **The promise:** a living CITY that tolerates you — awe first, theft at your own risk.
- **Brainstorm (30 kept / 7 categories):** *work:* terraces ×2 tiers, nurseries ×2,
  granaries, compost pits, quarantine file, repair crews; *architecture:* Trunk Tunnel,
  root arches, Pebble Arch gates, Antechamber, dome, vault, ventilation chimneys;
  *nature:* taproot pillars, root curtains, glow gardens, sump; *threat:* raid scar,
  centipede breaches, guard posts, alarm-cloud event *(candidate)*; *loot:* ore wall, egg
  galleries, honeypots, vault; *whimsy:* the medicine file, ants re-stacking a toppled
  store, a worker polishing the Queen's floor; *relics:* sealed south breach, strata plug,
  bone midden glints.
- **Ground variety (4+):** dirt_block mass → stone deep walls → cave_floor chambers →
  garden/compost floor accents → sump water.
- **The deliberate rule-bend:** ONE ore pocket inside ant soil (doctrine says none) —
  as a SECRET with an authored story (the ants went around), placed as doctrine veins
  within its stone pocket. The exception advertises the rule.
- **Interest quotas:** 3 secrets ✓ (wall/breach/honeypots), surprise inversion ✓
  (cathedral queen), hooks all 10 ✓.

## Owner decisions needed (P4 review)
1. Queen encounter shape: scripted fight design scope (adds from brood piles? formic AoE?
   gear gating?) — its own slice; what's the reward list?
2. Aphid livestock: live mutualism now, empty-pasture teaser, or cut?
3. Soldier caste timing: with the zone build, or after the worker/scout loop ships?
4. The Ore-Studded Wall rule-bend: keep or keep colony soil 100% clean?
5. Royal-vault loot list (royal jelly/trophy/etc.) — encounter-loot framing OK under D18?

## Not present
The grand row-5 Ant Queen (deferred, D2) · fire/army/bullet ants + war-colony anything
(that's col-3 Deadly Ants — this colony is ORGANIZED, not militarized) · human structures ·
ant_mound objects · live cross-zone traffic (backlogged).
