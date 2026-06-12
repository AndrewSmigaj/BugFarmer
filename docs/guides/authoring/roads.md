# Feature guide: roads & paths

How to lay roads/paths with `zonegen`'s `terrain` primitives. Roads come **after water, before
buildings** in the precedence order: water is carved first, the road parts around it, then buildings
reserve their footprints along the road.

## THE TOWN GRID RULE (the governing rule — read first)
**Wherever anything is BUILT (buildings, yards, pens, fields, orchards), roads run
STRAIGHT horizontal or vertical**, with L-elbow corners (an H segment meeting a V
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
- **Degrade outward:** stone (`stone_path`) in the core → `dirt` shoulders via `edge_tile` → let the
  ends taper and fade into trampled grass at the zone margins. (See the Village zone's road rules.)
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
  `tools/make_diagonal_tiles.py`, so they match both materials by construction).
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
- **A lane can be laid AFTER its buildings**: `path()` skips reserved cells, so a
  residential lane routed past already-placed yards hugs the fences naturally — use
  this when houses define the street, then connect gates with short straight `spur`s.
- **A landmark at every fork** (signpost minimum) — junction legibility is what makes
  a map navigable, not distant sightlines.

## Interaction with other features
- `path` writes `surface='path'`; `scatter` then avoids those cells automatically (no flowers on the
  road). Buildings placed after will reserve over/along it. Verify by rendering — the road should bend
  naturally, fray at the edges, and have nothing scattered on it.

## Cross-cutting
Path tiles follow `art/MASTER_STYLE_GUIDE.md`. Missing tiles render as placeholders; track in
`../../product/art_needed.md`.
