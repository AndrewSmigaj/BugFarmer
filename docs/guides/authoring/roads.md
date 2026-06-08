# Feature guide: roads & paths

How to lay roads/paths with `zonegen`'s `terrain` primitives. Roads come **after water, before
buildings** in the precedence order: water is carved first, the road parts around it, then buildings
reserve their footprints along the road.

## Primitives
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

## Interaction with other features
- `path` writes `surface='path'`; `scatter` then avoids those cells automatically (no flowers on the
  road). Buildings placed after will reserve over/along it. Verify by rendering — the road should bend
  naturally, fray at the edges, and have nothing scattered on it.

## Cross-cutting
Path tiles follow `art/MASTER_STYLE_GUIDE.md`. Missing tiles render as placeholders; track in
`../../product/art_needed.md`.
