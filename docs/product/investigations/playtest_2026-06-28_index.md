# Playtest 2026-06-28 — investigation campaign (index / morning landing page)

Source: Andrew's 22-item playtest list. Each **INVESTIGATE/DESIGN** item gets its own
`deep-investigate` run → a doc in this folder (investigate-only, NO fixes applied; max rigor; backend
may be spun up; every sub-agent claim re-verified in source). **BACKLOG** items go straight to
`BACKLOG.md`. **KNOWN-FIX** items are captured for the eventual fix-pass with no investigation (the user
said they're obvious / don't investigate). Status fills in as each completes.


## ★ MORNING SUMMARY — campaign complete (read this first)
All 17 investigations done (one doc each in this folder); 3 backlogged; 2 known-fixes captured. **No game code
was changed — these are findings + recommendations to approve.**

**The single highest-value finding — one cross-cutting bug:** every right-click occupant interaction (shop,
break, container, compost, mannequin, bed) resolves its target via a single `Physics2D.OverlapPoint` with **no
topmost-wins rule** → overlapping occupants steal the click. **One shared fix** (`OverlapPointAll` + pick the
topmost interactable) directly de-risks **#5, #18, #8, #14, #4, #12**. Do this first.

> **✅ BUILT 2026-07-01** — `InteractionResolver.TopmostInteractable` (front-most INTERACTABLE occupant via
> `OverlapPointAll`; front-most = lowest `AnchorCell.y` = highest render sortingOrder), routed through all 8
> handlers; **Unity batchmode build compiles clean**. **Corrected scope after re-reading each doc:** it fixes
> **#18** + the overlap-stolen-click *flakiness class*, and **de-risks** the rest — but it does NOT by itself fix
> **#5** (your live-confirm: the shop opens; it's the sell-flow), **#14** (data tag), **#10** (station-state
> keying), **#4** (render never built), **bed-2** (respawn/optimistic-message). Each keeps its own fix. Pending:
> a short in-Editor click-feel pass.

**Clean, high-certainty fixes (mostly data / small code):**
- #14 containers — basket/chest/trunk/yarn_basket missing `interaction_type:"storage"` (data).
- #2 placement preview — ghost lacks the render's pivot-Y baseline; one shared position helper.
- #1 doors — inconsistent sizes; standardize to 16×32 / footprint [1,2] (data).
- #15 watering — `handleWatering` rejects bare tilled soil; water → `garden_plot_wet` (small code).
- #3 zone transition — **REGRESSION**: commit ce4102a dropped village_21_B's `neighbors`; restore + teach the
  builder to emit them (data + builder).
- #10 compost-on-move — compost StationState only made at chunk-load; add lazy find-or-create (server; sim gate).

**Needs a 2-minute live confirm before the fix is certain:** #5 (does the NPC dialogue open on right-click?),
#8 bed-2 (set home → faint → wake at bed?).

**Not bugs / features to build:** #6 NPCs are correctly authored (non-issue; only fisherman placement-skip).
#4 mannequin outfit render was never built (feature). #16 dye-making station (design). #17 break-indicator
(design). #13 apples → breakable ground occupant (design). #22 corpses ARE generated for starvation/old-age
(predation excepted); the scarcity was missing dead_* sprites — **already fixed this session (commit 9b61b95)**
— plus they're eaten fast. #20 phantom = strike has no LOS; designed attack-indicator + corpse-feeding-pause.

**Suggested fix order:** (1) the shared OverlapPoint resolver; (2) the data fixes #14/#1/#3/#9; (3) #2/#15/#10;
(4) the designs #13/#16/#17/#4/#20-A; (5) the sim features #20-B/#10/#22-predation-carcass (each through
`frontier-sync` + the determinism gate).

## Disposition table
| # | Issue (user's words, condensed) | Disposition | Doc slug | Status |
|---|---|---|---|---|
| 6 | Missing NPCs (market person, bug salesperson) not in their store — village_21_B; verify all NPCs target the right zone | INVESTIGATE | `missing-npcs-village21b` | ✅ RESOLVED — NPCs correctly authored (9/10 in saved chunks; user confirmed); only `fisherman` placement-skipped (optional fix). No NPC-authoring bug. |
| 5 | Unable to sell items (tried clicking different ways); can't test buying (no money) | INVESTIGATE | `cannot-sell-items` | ✅ FIXED (2026-07-02, the Apico **barter sell**: stage into a basket from your REAL inventory → one atomic `sell_batch`; "Buys:" header + stage filter; OpCode-40 errors finally surfaced in a shop status line — both confirmed feedback gaps closed). Go tests green; in-Editor CONFIRMED (Andrew, 2026-07-02). |

> **★ Cross-cutting root cause (found during #5):** every right-click occupant interaction resolves its target via a **single `Physics2D.OverlapPoint`** with **no topmost-wins rule** (`PlayerInputRouter.cs:152-178`; `ShopPanel/BreakingController` etc. each call it). Overlapping occupants (NPC at storefront, item under a tree, container behind decor) can steal the click → the intended interaction silently fails. **One shared fix** (`OverlapPointAll` + pick topmost-interactable) de-risks #5, #18, #14, #10, #4, #12. Each still gets its own distinct-cause check.
| 14 | Basket + other containers don't seem functional — audit | INVESTIGATE | `container-functionality-audit` | ✅ FIXED (2026-07-01, `interaction_type:storage` on the 4 + publish) — **basket/chest/trunk/yarn_basket** have a container block but **no `interaction_type:"storage"`** → never open (gate `CraftingPanel.cs:138`). Fix = add the tag + publish. (+shared OverlapPoint.) |
| 10 | Moving the compost container broke it — could no longer load compost | INVESTIGATE | `compost-broke-on-move` | ✅ FIXED (2026-07-01, `resolveStation` lazy find-or-create; go test + sync IDENTICAL) — compost `StationState` is created only by the chunk-load scan; runtime-placed bins get none and `handleStationDeposit:958` requires one → "No station there". Fix = lazy find-or-create like `resolveCraftStation`. Sim-touching → determinism gate. |
| 4 | Mannequins don't visually show items put on them | INVESTIGATE | `mannequin-outfit-not-showing` | ✅ READY (feature, not bug) — outfit STORAGE works; the worn-item compose-onto-sprite render was **never built** (deferred per `MannequinController.cs:19`). Build it reusing the player paper-doll. |
| 2 | Placing a block (not everything) — preview is LOWER than where it actually lands | INVESTIGATE | `block-place-preview-offset` | ✅ READY — ghost uses raw `CellToWorld` (`PlacementController:174`); render adds the bottom-pivot Y baseline (`RenderOccupant:868`) → tall bottom-pivot blocks render higher than the ghost. Fix = one shared position helper. |
| 1 | Door is not 2 blocks high | INVESTIGATE | `door-not-2-high` | ✅ READY (data) — doors inconsistent: door_square=1.5 tall, door_wood=2-wide (footprint transposed), door_iron=correct 1×2. Standardize to 16×32 / [1,2]. (Also: doors have `blocks_players:null` → tie to #9.) |
| 13 | Apples shouldn't hover — should be placeable on the ground & hit to pick up; investigate how | INVESTIGATE+DESIGN | `apples-hover-vs-ground` | ✅ READY (design) — 'hover' = `GroundItemVisual` bob; fruit already falls to ground. Recommend: fallen fruit → small **breakable ground occupant** (flat, hit-to-collect). Pick approach A vs B. |
| 18 | Someone couldn't break something behind a tree — did the tree intercept the click? (user unsure) | INVESTIGATE | `click-intercept-behind-tree` | ✅ FIXED (front-most-interactable resolver, 2026-07-01; compile-gated, in-Editor feel pending) — was: `BreakingController:68` single `OverlapPoint`; a tree's tall sprite-bounds collider overlaps cells in front → steals the click. Same fix as #5 (topmost-interactable). |
| 12 | Picking up bugs/other things inconsistent — some work, some don't | INVESTIGATE | `pickup-inconsistent` | ✅ READY — 3 mechanics: walk-over auto (most), **E-required** for the 4 fruit + bug food, net/hand catch for bugs (#11). Mostly discoverability; no hard bug. Ties to #13/#11. |
| 15 | Can't water ground without a seed/plant in it (watering garden beds) | INVESTIGATE | `cannot-water-empty-bed` | ✅ FIXED (2026-07-01, bare `garden_plot`→`garden_plot_wet`) — `handleWatering` rejects bare tilled soil ('No crop here'); only crops/trees waterable. Fix = water `garden_plot`→`garden_plot_wet` (wet tile exists). |
| 3 | Zone transition broke — intermittent; leads to a black area, not the north mining camp; used to work | INVESTIGATE | `zone-transition-black-area` | ✅ READY — REGRESSION: commit ce4102a dropped village_21_B's `neighbors` (south→underground) on the ecology rebuild; builder never emits neighbors. Restore it + teach the builder. (village_21/underground links survive → 'sometimes'.) |
| 8 | Bed not working — one showed no message; other said "setting bed" but put the user back in the square | INVESTIGATE | `bed-not-working` | ⚠ BLOCKED ON 1 confirm — beds are 2×4; bed1 'no message' = shared OverlapPoint (overlapping bedroom occupant). Server set/respawn code is correct → bed2 needs a live respawn test (optimistic msg vs HomeZone mismatch). |
| 22 | Are wasps/flies dying of starvation & old age? Chart plummets but barely any corpses — are corpses generated on those deaths? | INVESTIGATE | `death-corpse-accounting` | ✅ READY — corpses ARE generated for starvation/old-age/cull (`killBugsNaturally→spawnCarcass`); only **predation** skips it. Scarcity = invisible sprites (FIXED commit 9b61b95) + eaten fast. Optional: predation→carcass (ties #20). |
| 20 | Phantom wasp attack (attacker unseen) + improve wasp attack indicators + corpse-feeding pause when killing flies; plan it | INVESTIGATE+DESIGN | `wasp-attack-indicators-phantom` | ✅ READY (design) — phantom = strike has **no LOS** (kills through the compost bin) + occluded attacker. Design: (A) attack indicator [display]; (B) corpse-on-kill + feeding-pause [sim/frontier-sync]. |
| 16 | Dye vats = dyeing CLOTH; making dyes needs a separate station — design it | DESIGN | `dye-station-design` | ✅ READY (design) — new 'mortar/pigment' station makes dyes (move the 4 flower→dye recipes); dye_vat dyes cloth (cloth+dye→colored_cloth). All data, zero code. |
| 17 | Better breaking indicator — covers the whole object being broken, looks better; new solution | DESIGN | `breaking-indicator-redesign` | QUEUED |
| 11 | Can't catch centipede with small nets but currently can | BACKLOG (net dynamics) | — | ✅ BACKLOGGED |
| 19 | Sleep | BACKLOG | — | ✅ BACKLOGGED |
| 21 | At least one night critter + fireflies | BACKLOG | — | ✅ BACKLOGGED |
| 7 | Rain doesn't reach the bottom of the screen | KNOWN-FIX | — | ✅ CAPTURED (BACKLOG fix queue) |
| 9 | Flies go through doors — just need to make them block | KNOWN-FIX | — | ✅ CAPTURED — doors need `blocks_bugs:true` (+ re-save/determinism); they also have `blocks_players:null`. See #1/#9 in BACKLOG. |

## Likely-shared root causes (investigate in clusters so one finding informs the next; each still gets its own doc, cross-linked)
- **Economy/NPC:** 6 → 5 (if the NPCs aren't placed / target the wrong zone, that likely *is* why selling fails).
- **Containers/stations:** 14 → 10 → 4 (basket/compost/mannequin may share one container-or-station-state defect, esp. around placement/move).
- **Placement/render:** 2 → 1 → 13 → 18 (pivot / footprint-Y / z-order-click clusters).
- **Interaction:** 12 → 15 (pickup + watering = the interact/right-click routing).
- **Movement/char:** 3 → 8 (cross-zone + respawn-to-home).
- **Ecology/combat:** 22 → 20 (death→carcass accounting + wasp strike visibility/feeding).

## Execution order (front-loads high-impact + shared causes; survives interruption)
1. NPC/economy: **6, 5**
2. Containers/stations: **14, 10, 4**
3. Placement/render: **2, 1, 13, 18**
4. Interaction: **12, 15**
5. Movement/char: **3, 8**
6. Ecology/combat: **22, 20**
7. Design: **16, 17**
8. Backlog adds (**11, 19, 21**) + KNOWN-FIX capture (**7, 9**)

## Scale note
17 deep investigations at max rigor (sub-agents + certainty loops + selective backend repro) is a large
overnight run. Worth it per "don't rush," but flagging the cost. Each doc ends with a one-line debrief that
will be copied back into this table's Status column as `READY TO IMPLEMENT` / `BLOCKED ON: …` so this page is
the single thing to read in the morning.
