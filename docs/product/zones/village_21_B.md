# Zone Design: Starting Village, Natural Rebuild (`village_21_B`)

The candidate replacement for `village_21`: the SAME functional content and macro-
geography (spatial memory transfers — big lake SW, mining S, farms + predators N, core
at center), rebuilt so it reads natural instead of stamped. `village_21` stays on disk
and joinable; this zone is judged side-by-side against it. If it wins, it becomes THE
village.

## Overview
- **Zone ID / Grid:** `village_21_B` · row 2, col 1 (same world slot as its sibling)
- **Biome / Difficulty:** Meadow (fly-ecology) · Easy-with-edges — the safe hub, but
  the wild north carries the predator showcase (see Constraints: this is a RECORDED
  CHANGE from the original "no dangerous bugs" rule).
- **The feel:** a real town that grew along ONE bending road, in a meadow that was
  here first. No ruler lines, no stamped square, no two lake banks alike.

## What the rebuild fixes (the named tells in `village_21`)
1. Ruler-straight `+` roads → ONE organic main road (S→quarry→plaza→farms→tapers out
   N) + dirt lanes, with the **road-angle system** (diagonal transition tiles +
   `smooth_paths`) so curves render as bevels, not staircases.
2. The blitted 120×116 core square → composed in place along the road's bend, reusing
   the REAL building pieces; upgraded `plaza()` (notice board, signpost, founder
   statue, benches) at the bend.
3. Uniform lake shores → `shore_dress` arcs (no two banks alike).
4. Grid crop beds → three irregular fields (wheat/corn/tomato) with hedgerows.
5. Missing orchard → `garden.orchard()` restores the intent-doc landmark.
6. Confetti scatter → clumping ≈0.85 everywhere with a density gradient to the rim.

## Connections (map)
Four exits KEPT (the world doc commits to them; no transition system exists yet, so
these are taper-outs, not gates): **N** main road tapers out ≈(100,255) toward
Butterfly Meadow · **S** main road start, toward the cave mouth / Mining ·
**W** dirt lane tapers ≈(0,~130) toward Bee Meadow · **E** dirt lane past the
ecologist tapers ≈(255,~148) toward Wasp Thicket.

**THE RIVER IS DEFERRED to the neighbor-zone slice** (Emily's call; the world doc's
river system runs through the adjacent zones). For that slice, the reviewed geometry
is recorded here: a stream at gx≈40-50 needs TWO bridges or it walls off the west
third — W-lane bridge ≈(44,130) + farm footbridge ≈(47,182); `terrain.bridge` is
engine-free (walkability is the hardcoded tile-id switch; bridge tiles replacing
water are walkable on both sides with zero Go/C# change).

## Key species & ecology (same numbers as village_21 after the knot update)
- fly_common 40/75 (pop 400): zone-wide + the fly farm circle (~120,205).
- butterfly_meadow 15/50 (pop 300): meadow_se → the **beehive meadow** circle
  (210,78 r26 — re-centered off the rocks/pond); meadow_w (28,134 r32 — nudged off
  the lake's lobed shore); meadow_sw (30,205 r28).
- wasp_common 0/3 (pop 12, nest-driven): nest №1 ≈(98,225) — ≥15 and ≤40 cells from
  BOTH the fly farm and the orchard (vision 14 / home_range 40: the wild-fly buffer
  absorbs raids); nest №2 deep in the NE gloom.
- centipede_garden: knots (1-3 per swarm) — initial 2×2, max 3, pop 8, circle in the
  NE forest-edge gloom.
- **Predator caps make orchard-adjacency safe**: fly 400 / wasp 12 are hard ceilings
  regardless of prey density; more fruit just reaches the ceilings sooner — the
  legible fruit→rot→fly→wasp chain, faster.

## The town — buildings (reusing the REAL `place_*` pieces)
| Building | Piece | Placement notes |
|----------|-------|-----------------|
| Town Hall | `place_mayor` (marble accents read civic) | W of the plaza, the largest silhouette |
| Market | `place_market` | across the plaza from the hall |
| General Store | NEW composed via `shop_building` (barrels, sacks, open frontage, basket sign) | beside the market — the intent doc lists it separately; no piece existed |
| Carpenter + Smith | `place_carpenter`, `place_smith` | the production cluster SE of the plaza, adjacent |
| Boat & Fishing Store | `place_boat_store` | ON the big lake's E shore; **docks are `bridge_wood` ground tiles** (walkable, art exists — `dock_plank` has no art) + lanterns + nets |
| Ecologist's Cabin | `place_ecologist` (unfenced — the documented exception) | E side in its grove, on the E lane |
| Cottages ×4 | `place_cottage`/`place_house` + `property_yard` | a curving residential lane N of the plaza; varied setbacks, collections, door spurs |
| Farmhouse | cottage variant + farm clutter | at the fields, NW |

Spacing constants ported from `scene_village`: shop gaps 2-4, 2-wide door spurs to
the road, footprints ≥2 cells off the path edge. Orientation variety via
`place_house front=` + setbacks (text-grid side doors stay a TODO).

## Landmarks & wayfinding (landmark AT every fork — the "couldn't find things" fix)
| Fork / place | Landmark + props |
|--------------|------------------|
| The plaza (spawn) | fountain + founder statue + notice board + signpost; spawn = paved S-edge plaza cell within ±10 of (126,123) |
| Farm-lane fork (N of core) | **WINDMILL** + signpost; the wheat field beside it |
| Quarry fork (S) | mine_support timber frame + parked mine_cart + signpost |
| W lane | signpost at the plaza end; standing_stone (new art) on the meadow knoll |
| E lane junction | signpost + the ecologist's sign_leaf |
| The lake | dock lanterns visible from the S road bend |
| Lighting plan (night slice) | lamps line the MAIN road through town only + one per shop door + dock lanterns; the orchard/nest walk N is deliberately dark |

## Per-region content lists (the brainstorm step — what dresses each region)
- **Plaza & civic core:** fountain, statue_founder, notice_board, signpost, benches
  ×4, lamp corners, flower beds, market_stall + awning + produce crates at the
  market front, barrels/sacks delivery clutter at the general store, banner on the
  hall. Wear: one bench placed crooked (off-row), a wheelbarrow parked off the road.
- **Production cluster:** exterior forge + anvil + coal_bin + tool rack (smith);
  log_pile, sawhorse, chopping_block, stumps + furniture-on-display row (carpenter);
  sawdust read = dirt patch under the sawhorse.
- **Residential lane:** picket yards (one weathered — the poor→nice range), window
  boxes (planter_box), laundry_line, cat_statue, birdbath, a vegetable patch
  (crop_bed 3×4), mailboxes, one cottage with a campfire_spit out back.
- **Farms NW:** three irregular fields — wheat (by the windmill), corn, tomato —
  hedgerow bush-lines between, scarecrow (exists!) in the wheat, hay_bale clusters
  (new art), water_bucket + wheelbarrow at the field edge, the farmhouse with a
  compost_bin.
- **Orchard:** `orchard()` rows + crates/ladder + compost_pile pair on the fly-farm
  side; fallen fruit (live, from the server sim).
- **Fly farm (a landscape, not a building):** compost piles, net_post pairs +
  fly_netting, bait_basket hangs, collection_tray rows, darkened soil (dirt),
  shallow puddle (2-3 water_shallow cells), **failure evidence**: broken_net ×2 +
  one overrun patch (dense flies + rotten fruit decor).
- **Wasp pen (the observation vignette, kept):** wood fence ring + flowers + the
  wild nest — wood deliberately (the "fences don't stop wings" lesson made visible).
- **Big lake SW:** shore_dress arcs — sand beach S (with the beached rowboat, new
  art), docks+nets E (boat store), reeds N, forested bank W; the island blob
  placeholder offshore.
- **NE forest-edge gloom (centipede home):** pine-heavy density gradient, stumps +
  log_fallen + ferns + mushroom clusters, the carrion gully (bone_pile + dirt),
  nest №2 deep in, the reedy pond KEPT (dragonfly future), a ruined stone pen
  (stone_block L-shapes — the "stone is the answer" lesson as environmental story).
- **Mining S:** rock_patch terraces, mine_rail run + mine_cart + mine_support
  timbers, the camp (tent + campfire + crate + lantern), ore sacks by the track.
- **Meadows:** clumped flower species per region (poppy/clover W, lavender/aster SE
  by the beehives, chamomile/yarrow N), tall grass ribbons along roads, beehive_basic
  row at the SE pond meadow (the future-bees hook).

## Materials / loot
Same as village_21 (the village is where you spend/craft; mining intro at the S
quarry feeds the Smith).

## Biome composition (generator recipe — locked precedence)
base grass → lakes (`lake` ×3 + shore_dress) → roads (`path` + `smooth_paths`) →
buildings (pieces + plaza at the bend) → farms (`crop_bed` irregular + `orchard`) →
scatter LAST (clumping ≈0.85, density gradient up toward the rim, forest ring with
3 clearings).

## Scenes
- `zone_village_21_B.py` — the zone builder (this doc is its spec).
- Test cards already shipped: `scene_road_angles`, `scene_shore_arcs`,
  `scene_orchard` (the primitives' guides point at them).
- New piece: the general store (composed `shop_building`), the mining camp + NE ruin
  as text-grid `place_*` functions if they outgrow inline composition.

## Hard constraints
- ❌ No player housing · ❌ no safe zones · ❌ no scripted events · ❌ no artificial
  rot props (rot emerges from fruit age).
- ⚠ **CHANGED from village_21.md:** "no dangerous bugs" is RETIRED — the predator
  slice made wasps + centipedes the north side's intentional content (the danger
  gradient: safe core → wild edges). Recorded here so the docs don't contradict.
- village_21 is NOT regenerated or touched (its chunk files carry hand-edits).

## Build / review checklist (each V3 iteration)
- [ ] `b.lint()` 0 new defects (wall/door height = the known exception).
- [ ] The main road BENDS and its curves are bevelled (no staircases); lanes are
      dirt; tapers at all four edges.
- [ ] Plaza at the bend with all civic props; spawn on its paving (±10 of 126,123).
- [ ] Each building identifiable by sign + props; clusters legible (civic W,
      production SE, residential N, lake SW).
- [ ] No two lake banks read alike; the docks sit ON the water.
- [ ] Orchard structured + fly farm with failure evidence + the wasp buffer
      geography (nest ≥15 from prey sites).
- [ ] Vegetation patchy (clumped), density rising to the rim; forest ring with
      clearings; the NE gloom reads darker/denser.
- [ ] Wayfinding: a signpost at EVERY fork, a landmark within a screen of each.
- [ ] view_world render compared against THIS doc's map before calling it done.
