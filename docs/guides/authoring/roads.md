# Feature guide: roads & paths

How to lay roads/paths with `zonegen`'s `terrain` primitives. Roads come **after water, before
buildings** in the precedence order: water is carved first, the road parts around it, then buildings
reserve their footprints along the road.

## THE TOWN GRID RULE (the governing rule — read first)
**STONE roads: wherever anything is BUILT (buildings, yards, pens, fields,
orchards), they run STRAIGHT horizontal or vertical**. **DIRT lanes are
informal — diagonals and meander are fine (they're dirt)**, EXCEPT the segment
directly fronting buildings, which stays straight, with L-elbow corners (an H segment meeting a V
segment — `smooth_paths` bevels the corner). Organic meander is for EMPTY wilds
only. This rule exists because THREE successive attempts at organic-roads-meet-
rectangular-architecture each produced clipping (wobble climbing into frontages,
routed meander through yards and pens); straight roads beside rectangular plots is
also simply what the genre's best (Stardew) does. Pair it with:
- `clear_road_margins(b)` once after all scatter — deletes vegetation within 1 cell
  of any road (tall sprites overhang the roadway from adjacent cells), and
- the tall-sprite-overhang lint (a tree directly south of a road cell = defect).

## ROUTED roads — `route_road` (EMPTY-WILDS spines only, per the rule above)
```python
from features.terrain import route_road
route_road(b, (118, 2), (140, 48), width=4, seed=21)          # point-to-point
route_road(b, (140, 30), None, width=2, tile="dirt", seed=9)  # spur → the NETWORK
```
Least-cost-path roads (see research_procgen.md §2): A* over (cell, heading) with a
terrain cost field — water/reserved prohibitive, forest ×2.5, sand ×1.5, EXISTING
ROADS ×0.3 (later roads hug earlier ones; junctions emerge), turn penalties (one
90° > two spaced 45°s → S-curves), MULTIPLICATIVE noise hills for deterministic
meander. `end=None` routes to the whole existing network (spurs/lanes/driveways —
believable T-junctions with no destination guessing).
- **Pin the road through TOWN** (`noise_amp≈0.15` for the core segment) — real
  settlements straighten roads, and your civic block sits at fixed coords; let it
  go wild again past the core (2026-06 correction: a meandering town segment
  walked through the hall's yard).
- Roads are laid BEFORE buildings, so routing can't avoid them — pinning is the
  answer near fixed architecture; cost does the avoiding everywhere else.

## Walked primitives (spurs + deliberate lanes)
```python
from features.terrain import path, hpath, vpath

# ORGANIC road — wanders gently toward the goal, NOT a dead-straight line. Use this for real roads.
path(b, (4, 30), (W-5, 30), width=3, tile="stone_path",
     edge_tile="dirt", wobble=0.16, taper_ends=6, seed=7)

# STRAIGHT strips — only for short, deliberately-straight connectors (a doorway stub, a dock plank).
hpath(b, x0, x1, y, tile="stone_path")     # one row
vpath(b, x, y0, y1, tile="stone_path")     # one column
```
- **`path`** paints a ~`width`-cell band that meanders toward the goal and **skips `reserved` cells**
  (so it flows around water/buildings instead of clobbering them). All cells become `surface='path'`.
  Returns the painted cells.
- **`edge_tile`** frays the road's shoulders into that tile (e.g. `"dirt"`) — the stone core bleeds
  into dirt at the margins instead of a hard rectangular edge.
- **`taper_ends`** narrows the band to 1 cell over the last N cells at each end, so roads *dwindle*
  as they leave town rather than stopping square.
- **`wobble`** ≈ 0.1–0.25. Low = a deliberate road with a slight bend; higher reads as a trail/path.
  Vary `seed` per road so parallel roads don't wobble identically.

## Design rules (avoid the stamped grid)
- **Don't use dead-straight `hpath`/`vpath` for main roads** — a perfect cross reads as a tech demo.
  Use `path` with a little `wobble` and `taper_ends`.
- **WAYPOINT any segment longer than ~40 cells** (cold-grade finding, 2026-07-06, bee_meadow —
  the grader's words: "a ~145-cell dead-straight runway... a 90-cell perfectly vertical brown
  stripe. That is literally a line drawn with a ruler"): `path()`'s goal-pull flattens wobble
  over distance, so one long call ALWAYS irons out straight. Break the route into 25-40-cell
  legs through offset waypoints (drift the intermediate points ±3-6 cells off the axis), keep
  only the last few cells at a zone-edge CONTRACT row dead true, and finish with an edge-wear
  pass (dirt treads bled one cell off the band at ~15%) so the edges aren't knife-cut. A road
  that bends also fixes the Traveler lens for free: bends make sightlines, sightlines promise.
- **Degrade outward:** stone (`stone_path`) in the core → `dirt` shoulders via `edge_tile` → let the
  ends taper and fade into trampled grass at the zone margins. (See the Village zone's road rules.)
- **A road/lane must be GAPLESS end to end** (owner correction 2026-07-06: "the roads are
  not connected... all your paths have huge gaps in them"): `path()` skips reserved cells
  and cell-by-cell traces skip occupied ones — every skip is a HOLE in the walkway. After
  laying all roads, WALK each route in data (flood along path/dirt ground from endpoint to
  endpoint) and treat any break as a build failure: reroute around the blocker or clear it.
  Taper only where a road genuinely dies into wilderness — never between two things it
  claims to connect.
- **Connect logically, not symmetrically:** route roads between the things that matter (gates, the
  square, the docks); let a spur end awkwardly at the orchard rather than mirroring everything.
- **Lay roads before buildings** so building footprints reserve along the finished road, and after
  water so the road parts around the pond.

## THE ROAD-ANGLE SYSTEM (curves on square tiles)
A wobbling `path()` leaves 1-cell stair-steps; on 2-4-wide roads those hard right
angles read as a staircase, not a curve. The fix is `terrain.smooth_paths(b)` — run it
ONCE after ALL roads (before buildings):
- Every stair-step corner (a grass cell whose N/S + E/W neighbors are both road of one
  material) gets a **45° diagonal transition tile** (`stone_path_d_ne` …
  `dirt_path_d_sw` — composited from the two real tile PNGs by
  `tools/sprites/make_diagonal_tiles.py`, so they match both materials by construction).
- It also HEALS POTHOLES: `edge_tile` fraying on a wobbling centerline leaves dirt
  specks that end up interior to the stone band — any dirt path cell with ≥3 stone
  road neighbors is repaved (the checkered-road lint's inverse).
- Test card: `scene_road_angles` (raw vs smoothed, side by side).
- **Player-placed roads (future)**: the same neighbor rule runs as AUTOTILE when a
  tile is placed — the system picks the variant; players never flip through sprites.

## Junctions & building adjacency (learned building village_21_B)
- **Buildings keep their FULL frontage off the roadway**: footprints ≥2 cells from the
  path edge, and frontage props (signs, crates, ore piles at oy-1/oy-2) need their own
  off-road row — set shops BACK from the lane so clutter lands beside the door spur,
  never on it. The place-time warn + the wall/fence-on-road-tile lint catch the hard
  cases; the wobble band is ±2 around the centerline, so budget clearance against the
  CORRIDOR, not the nominal line.
- **`path()` does NOT route around buildings — never aim it across a built-up
  band** (2026-06, the living-room road): the walker skip-paints blocked cells but
  keeps MARCHING toward its goal, so a lane aimed across a residential block
  threads road tiles straight through interiors and yards. House/shop interiors
  now RESERVE at place-time, `path()` warns loudly when its band crosses a
  building or a large reserved area, and lint flags any road cell walled on both
  sides — but the real fix is layout: SCAN for a clear corridor first (dump the
  blocked intervals row by row), lay the lane STRAIGHT inside it, and connect
  gates with short `spur`s. If no clear corridor exists between two rows of
  buildings, the answer is to MOVE a building or connect the street on its open
  side — not to thread the needle.
- **A landmark at every fork** (signpost minimum) — junction legibility is what makes
  a map navigable, not distant sightlines.

## Interaction with other features
- `path` writes `surface='path'`; `scatter` then avoids those cells automatically (no flowers on the
  road). Buildings placed after will reserve over/along it. Verify by rendering — the road should bend
  naturally, fray at the edges, and have nothing scattered on it.

## Cross-cutting
Path tiles follow `art/MASTER_STYLE_GUIDE.md`. Missing tiles render as placeholders; track in
`../../product/art_needed.md`.
