---
name: author-zone
description: Use when creating or editing a game zone, or building an example scene/vignette for the zone guides. Covers the zonegen builder-library (feature primitives that coordinate through a shared occupancy model), placeholder-first composition, and rendering preview PNGs to review. Does NOT cover sprite generation (that's add-object / object_pipeline.md).
---

# Author a zone / scene

Build zones and example scenes from reusable **feature primitives** that coordinate through a
shared occupancy model, compose with **placeholder squares** (never wait on art), and review by
**rendering a preview PNG and looking at it**. The preview is the test — there's no live game to
watch here.

## The loop
1. Read the zone document (`docs/product/zones/<zone>.md`) or decide the scene's contents.
2. For each feature, read its **feature guide** (below) + the cross-cutting style guide.
3. Build with the `ZoneBuilder` + feature primitives (`tools/zonegen/`).
4. **Render a preview PNG and `Read` it**; iterate the layout (and the guide).
5. Placed a new object with no art yet? It renders as a labeled placeholder — add it to
   `docs/product/art_needed.md`.

## Builder — `tools/zonegen/`
- `ZoneBuilder(zone_id, W, H, base_tile=..., seed=..., name=...)` — the two on-disk grids plus the
  coordination masks `surface[]` (`water|path|building|farm|forest|grass`) and `reserved[]`.
  Key methods: `place_occupant(id, x, y)` (writes anchor + footprint cells; **refuses overlaps
  loudly** — no silent overwrite), `set_ground`/`fill_ground`, `missing_art()`, `validate()`,
  `save()` (chunk-aligned zones) / `load(zone_id)` (edit an existing zone; derives masks).
- `features/` — feature primitives: `room.place_room` (building shells), `scatter.scatter`
  (decor). More are added over time, each with a feature guide.
- `render.render_builder(b, out, scale, bounds=None)` — render a builder straight to a preview PNG
  (for scene vignettes; no zone files written).
- **Precedence — place HARD features first so later ones route around them:** biome base → water →
  roads → buildings → farms → scatter. (`place_road` will pathfind around `reserved`; `scatter`
  only fills free grass.) Out-of-order placement is refused/warned.
- **Always** run `b.validate()` and **look at the render** before calling a scene/zone done.

## Build & render an example scene
```bash
python3 tools/zonegen/builds/<scene>.py    # builds + renders to tools/_generated/previews/<scene>.png
```
`builds/cottage.py` is the worked example (a cottage interior + a fenced yard with scatter).

## Feature guides
- `docs/guides/feature-building.md` — rooms, walls, doors, building shells.
- `docs/guides/house-building.md` — multi-room houses: the composer, the south-facing **facing
  rule**, the room-template library (living/bedroom/kitchen/crafting), ⊥/L shapes.
- `docs/guides/feature-vegetation.md` — scatter (flowers/bushes/grass): density + spacing.
- Cross-cutting style/perspective: `docs/guides/MASTER_STYLE_GUIDE.md` (+ the broader guide set,
  being consolidated — see BACKLOG "Zone-design guides cleanup").

## Notes
- **Scenes are example vignettes** (rendered straight from the builder, no zone files); they double
  as the visual catalog/QA and the worked examples for the guides. One scene usually spans several
  guides. Across all scenes, aim to place **every** world entity at least once (catalog coverage).
- **Real zones** use `save()` (size must be a multiple of 32 cells).
- Sprite generation is out of scope here — placeholders now, real art later via `add-object`.
