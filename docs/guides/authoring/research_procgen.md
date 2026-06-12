# Research: how others procedurally build terrain, roads & buildings (2026-06)

Digest of a three-track web-research sweep, kept as the paper trail for which
techniques zonegen adopted and which it passed on. Full citations at the end of
each section.

## 1. Terrain — noise density fields

**The standard recipe** (Red Blob Games, the canonical reference): sum 2-4 octaves
of lattice noise, each at double frequency / half amplitude, normalize. Think in
**wavelength (cells per oscillation)**: base wavelength ≈ 1-1.5× the desired clump
diameter. Calibrated empirically on a 256² grid: wavelength 24, 3 octaves,
persistence 0.5, threshold 0.60 → ~25 forest blobs of median ~20-cell diameter
(threshold sets coverage: 0.55→~36%, 0.60→~25%, 0.65→~16%).

**Shipped-game practice**: RimWorld cuts a Perlin field (frequency 0.04 ≈ our
wavelength 24!) into threshold BANDS per terrain, with a separate density-scalar ×
weighted-species table for vegetation ("the field decides how much, the table
decides what"). Dwarf Fortress generates independent scalar fields and derives
biomes from their OVERLAP — more natural than painting biomes directly.

**The ring recipe** (for our forest rim): a distance-to-edge field jittered by
noise — `forest if lo < d + 0.2·(fbm−0.5) < hi` — gives a ragged ring with natural
gaps instead of hand-chained blobs.

**Failure modes**: thresholding HIGH-frequency noise = salt-and-pepper; one octave
= soap bubbles. The 2nd-3rd octaves supply edge raggedness. Don't copy thresholds
across implementations — calibrate by measured coverage. Cellular-automata
smoothing (the 4-5 rule, 1-2 iterations) is a cheap cleanup pass for specks.

**ADOPTED**: `terrain.noise_field()` (numpy value-noise fBm, the tested reference
implementation) drives the forest ring + meadow density gradients. Parameters from
the calibration table. **PASSED ON**: domain warping, midpoint displacement,
full CA cave generation (no caves on the surface map).

Sources: redblobgames.com/maps/terrain-from-noise · RogueBasin CA method ·
gridsagegames.com mapgen posts · RimWorld wiki Modding_Tutorials/Biomes ·
dwarffortresswiki.org World_generation + Tarn Adams GameAIPro2 ch. 41.

## 2. Roads — least-cost-path + the network discount

**The core result** (Galin et al., *Procedural Generation of Roads*, CGF 2010):
a road is a weighted shortest path over a COST FIELD (slope, water, vegetation,
curvature), solved with grid A*. Water/steep = infinite above a threshold —
prohibitive, not just expensive.

**Production constants found**:
- **Azgaar's Fantasy Map Generator** (source read): `existing-road edges cost
  ×0.5` — every finished route writes into a shared set before the next searches,
  so later roads HUG earlier ones and fork near the destination: junctions emerge
  automatically. Water = ∞; settlement cells ×1 vs wilderness ×3 (roads pulled
  through towns).
- **OpenTTD YAPF**: turn penalties ≈ 45° = 1-3 tiles of travel, 90° = 2× that —
  super-linear, so one hard turn costs more than two gentle ones → S-curves.
  Turn penalties require the A* state to be **(cell, heading)**, not just cell.
- **SBGames 2018 village paper**: route a new building TO THE WHOLE ROAD SET
  (multi-target A*, terminate on touching any road) — believable T-junctions
  without choosing a destination.
- Organic wiggle: add a LOW-FREQUENCY NOISE term to the cost grid (invisible
  hills the road bends around) — path stays valid, deterministic per seed; never
  perturb the path afterward.

**Band extraction**: dilate the centerline with a w×w brush; stamp an extra brush
between diagonal steps (no 1-tile waists); wider class wins per cell so a lane
meeting a trunk just merges — junctions need zero special-casing.

**ADOPTED**: `terrain.route_road()` — A* over (cell, heading), 8-dir, integer
costs (grass 10/14 diag; sand ×1.5; forest ×2.5; water/reserved ∞; existing road
×0.3; noise + turn penalties +5/45° +15/90°), multi-target mode for spurs,
dilation band with the diagonal-pinch fix. **PASSED ON**: Galin's Mₖ direction
masks (45° quantization invisible under a 2-4-wide band + smooth_paths bevels),
L-systems, WFC paths (no global connectivity guarantees), Townscaper relaxation
(inseparable from abandoning the square grid).

Sources: perso.liris.cnrs.fr/eric.galin 2010-roads.pdf · sbgames.org 2018 188241 ·
redblobgames.com/pathfinding/a-star · github.com/Azgaar/Fantasy-Map-Generator
routes-generator.ts · OpenTTD YAPF wiki · tmwhere.com city_generation ·
arXiv 2309.10871 (GDMC winner, 256² maps) · Chaikin corner-cutting.

## 3. Building footprints — polyomino wings + the landmark budget

**Watabou's stated algorithms**: Procgen Mansion = "generate a polyomino, split it
into rectangles (wings)"; the city generator cuts the largest inscribed rect from
the lot then subdivides and discards blocks; the Village Generator uses PLAIN
RECTANGLES ONLY and still reads great — proof that footprint complexity is a
garnish, variety comes from size/orientation/yards.

**The two canonical recipes** (Martin Devans): ADDITIVE (seed rect → attach
shapes to walls, each accepted op HALVING the chance of more — no snakes) and
SUBTRACTIVE (bevel/invert corners, shrink). Validity from the literature: shared
walls ≥6 cells (door + jambs), no corner-only rect contact (kills wall junctions),
room aspect ≤2:1, fill ratio ≥0.5, BFS connectivity over shared walls.

**The proportion rule** (synthesis from Stardew/Watabou + level-design sources):
~80-90% of a village's buildings are simple rects (porch ~half the time), L-shapes
the next tier, and only 1-2 buildings EARN T/U/courtyard massing — **complexity
is a landmark budget, not a dice roll**. Stardew's farmhouse is a 9×5 rect whose
only silhouette break is the porch.

**ADOPTED**: `house.sculpt_plan()` (additive attach-with-offset; offsets make the
L/T/Z/U silhouettes; ≥6 shared walls; corner-touch rejection), fixed `l_house` /
`u_house` (dressed courtyard) / `z_house` (annex), `porch()` (wood-floor apron +
posts + bench — the Stardew break), and the LANDMARK BUDGET as a village rule
(house.md). **PASSED ON**: full shape grammars (authoring-heavy; coherence we get
from shared art), BSP (interior-only; footprints stay boring), bite-corner as a
distinct op (rooms are rects here — bites emerge from wing offsets).

Sources: watabou.itch.io procgen-mansion + devlogs · martindevans.me building
footprints · Stiny & Mitchell 1978 Palladian grammar · Müller et al. CGA 2006 ·
Lopes et al. GAMEON 2010 constrained growth · arXiv 1211.5842 · stardewvalleywiki
Farmhouse · slynyrd.com pixelblog-35.

## The scoreboard

| Technique | Verdict | Where |
|---|---|---|
| fBm value-noise density fields | ADOPTED | terrain.noise_field → forest ring, meadows |
| Distance-band ring + noise jitter | ADOPTED | the forest rim |
| CA 4-5 cleanup pass | ADOPTED (optional arg) | noise masks |
| Least-cost-path roads, (cell,heading) A* | ADOPTED | terrain.route_road |
| Existing-road ×0.3 discount + multi-target spurs | ADOPTED | route_road(ROAD_SET) |
| Turn penalties (OpenTTD ratios) | ADOPTED | route_road |
| Cost-grid noise (not path perturbation) | ADOPTED | route_road |
| Dilation band + diagonal-pinch fix | ADOPTED | route_road |
| Additive footprint growth + offsets | ADOPTED | house.sculpt_plan |
| Porch / annex / courtyard idioms | ADOPTED | house.porch, z/u_house |
| Landmark budget (most simple, 1-2 showpieces) | ADOPTED | house.md rule |
| Galin Mₖ masks, L-systems, WFC, Townscaper, BSP, shape grammars, domain warping | PASSED ON | reasons above |
