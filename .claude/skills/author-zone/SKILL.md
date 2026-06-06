---
name: author-zone
description: Use when creating or editing a game zone, or building an example scene/vignette for the zone guides. Covers the zonegen builder-library (feature primitives that coordinate through a shared occupancy model), placeholder-first composition, and rendering preview PNGs to review. Does NOT cover sprite generation (that's add-object / object_pipeline.md).
---

# Author a zone / scene

Build zones and example scenes from reusable **feature primitives** that coordinate through a
shared occupancy model, compose with **placeholder squares** (never wait on art), and review by
**rendering a preview PNG and looking at it**. The preview is the test — there's no live game to
watch here.

## Make it RICH — brainstorm, don't do the bare minimum (read this first)
A scene is a crafted vignette, not a checklist. When asked for a new scene you are EXPECTED to
**brainstorm interesting content yourself**, not just place the few things named:
- Start by **brainstorming a content list** for the scene's theme/situation: the named things PLUS
  the supporting props, decorations, clutter, and variety that make the place feel real and lived-in
  (e.g. a mining camp isn't just tents — it's crates, barrels, pickaxes leaning on rocks, ore sacks,
  a stew pot over the fire, lanterns, tool racks, a wash line, scattered rubble). Aim for diversity
  (several variants, a poor→nice range where it fits) — we have AI artists, so content is cheap
  (`game_design.md §19`). Too sparse reads as a tech demo; fill it with character.
- **Most of that content will be NEW entities** — that's expected. Add each via the **add-object**
  skill (lean entity row + a catalog `look` row). It renders as a placeholder immediately, so layout
  never waits on art.
- **Write the brainstorm down and sanity-check it** against the theme before building — did you cover
  the activity, the people, the wear-and-tear, the lighting, the surroundings? Present the plan/brainstorm
  for review rather than silently doing the minimum.

## Go slow; check before you call it done
This is an iterative craft loop, not a one-shot. Deliberately:
- Plan → build a first pass with placeholders → **render and actually LOOK at the PNG** → adjust
  composition → repeat. Crop regions (`render_builder(..., bounds=...)` to `/tmp`) to inspect detail.
- Before declaring a scene (or a plan) good: re-read the render with a critical eye, run `b.validate()`,
  confirm **0 placement warnings**, and check the brainstorm actually landed (is it rich, on-theme,
  readable?). Don't rubber-stamp your own work — verify it.

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
- `features/` — feature primitives: `room.place_room` (building shells), `house.place_house` +
  `styled_rooms` (multi-room houses), `furniture` (collection catalog: `pick(role, coll)`),
  `yard.{fence_rect,yard}` (fenced enclosures), `terrain.{hpath,vpath,pond}`,
  `garden.{crop_bed,flower_patch,fruit_around}`, `scatter.scatter` (decor). `houses/layouts.py`
  has ready-made 3/4/5-room floor plans (`row_/t_/plus_house`). Each has a feature guide.
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
  rule**, room templates, ⊥/L shapes, **furniture collections** (basic/fancy), and the 3/4/5-room
  layout generators.
- `docs/guides/feature-yard.md` — fenced yards/pens: `fence_rect`, `yard` (gate + path + decor).
- `docs/guides/feature-vegetation.md` — scatter (flowers/bushes/grass): density + spacing.
- Worked multi-feature scene: `tools/zonegen/scenes/scene_houses.py` (room counts × collections, yards).
- Cross-cutting style/perspective: `docs/guides/MASTER_STYLE_GUIDE.md` (+ the broader guide set,
  being consolidated — see BACKLOG "Zone-design guides cleanup").

## Notes
- **Scenes are example vignettes** (rendered straight from the builder, no zone files); they double
  as the visual catalog/QA and the worked examples for the guides. One scene usually spans several
  guides. Across all scenes, aim to place **every** world entity at least once (catalog coverage).
- **One preview file per scene.** A build script renders to a single canonical PNG and overwrites
  it in place (e.g. `scene1_player_farm.png`). Don't spawn `_crop`/`_v2` variants in the previews
  dir; render transient crops to `/tmp` and delete them.
- **Collectible / free-floating decor is NOT placeable like furniture.** Fruit, FLOWERS, and bugs
  are things you collect; they don't occupy or line up with cells. Place them with
  `place_decor`(fruit/flowers, sub-grid float coords, scaled down) / `place_bug` (float coords,
  scaled) — scattered, NOT snapped to a grid. Only structures, furniture, fences, walls and crops
  are grid occupants (`place_occupant`). Design note: a future "collectible decor" layer in the
  game should treat these the same way (sub-grid, pickup-able).
- **Real zones** use `save()` (size must be a multiple of 32 cells).
- Sprite generation is out of scope here — placeholders now, real art later via `add-object`.
