# Zone & scene authoring — the system

This is the index for **world-building**: how we lay out zones, houses, yards, caves, and the
example scenes that show them off. Read this first; it points at everything else.

The system is **four parts**, each with one home:

| Part | What it is | Lives in |
|------|------------|----------|
| **① The builder** | The Python library you compose zones/scenes with — feature primitives that coordinate through a shared occupancy model (a road routes around a pond; scatter avoids water). | `tools/zonegen/` |
| **② These guides** | How to do each world-building task (build a house, a yard, a cave…). Read & iterate on them as we learn. | `docs/guides/authoring/` |
| **③ Example scenes** | Small curated vignettes built with ①, rendered to preview PNGs. They double as the worked examples for these guides and the visual catalog/QA. | `tools/zonegen/scenes/` |
| **④ The Gallery** | `previews/index.html` — every scene card + zone render in one page. | `tools/zonegen/gallery.py` |

> **Art is separate.** How sprites *look* and get made is `docs/guides/art/` (start with
> `art/object_pipeline.md`). These guides assume art already exists — or use a **placeholder**
> (a labeled colored square) so layout never waits on art.

## The loop (how we actually work)
1. Decide the contents — from a zone doc (`docs/product/zones/<zone>.md`) or the scene's theme.
   Mine `docs/brainstorms/<topic>/` for what to place.
2. Read the **feature guide(s)** for what you're building (below).
3. Build with `ZoneBuilder` + the `features/` primitives. **Author themed buildings as TEXT GRIDS**
   (`features/tilemap.stamp`/`dump`) — reasoned cell-by-cell, not by guessing coordinates.
4. **`b.lint()` is the QA gate** — it returns TEXT defect strings (door blocked, wall/door/window height
   mismatch, fence/wall on path/water, wall/fence on a road TILE, dirt potholes inside stone roads,
   spawn circles mostly over water). `registry.render_one` prints it. `place_occupant` additionally
   warns AT PLACEMENT when a building lands on road surface (lint can't see it later — the mask is
   overwritten). Rule: **verify in TEXT (lint + `dump`), then look at a rendered crop** — never call it
   good off a giant PNG. (`validate()` is the older bare overlap check; `lint()` supersedes it.) The one
   expected lint item now is the wall-32/door-24 height (pending a 1.5-cell re-bake).
5. New object with no art renders as a labeled placeholder — log it in `docs/product/art_needed.md`.

```bash
python3 tools/zonegen/scenes/<scene>.py     # build + render ONE scene to its preview PNG + print lint
python3 tools/zonegen/registry.py <scene>   # render via the canonical registry path (prints lint)
python3 tools/zonegen/gallery.py            # regenerate previews/index.html (the GALLERY)
```

> **THE GALLERY is the visual entry point**: open `tools/_generated/previews/index.html`
> — every scene card with the guide it illustrates. Zone maps live in `previews/maps/`,
> one-off art QA in `previews/art_review/`. The previews root holds only directories.

> (The old Art Lab variant viewer was removed 2026-06 — the gallery + direct renders replaced it.)

## From scenes to a real ZONE (the full pipeline)
A **scene** is a small render-only vignette; a **ZONE** is the 256×256 world the game loads. Composing:
1. **Building pieces** — each themed building is a `place_<thing>(b, ox, oy)` function + a thin `build()`
   wrapper (`scenes/scene_smith.py`, `_carpenter`, `_market`, `_mayor`, `_ecologist`, `_cottage`,
   `_lakeside.place_boat_store`, `player_house.place_player_house`). One source of truth per building.
2. **A composed scene** — `scenes/scene_village.py` drops those pieces along straight roads + a square.
3. **The zone** — `scenes/zone_village.py`: blit the scene into the centre of a 256×256 `ZoneBuilder`,
   add organic terrain (`lake`/`forest`/`rock_patch`), extend roads to the edges, set `Z.bug_spawning`,
   then `Z.save()` → `nakama/data/zones/<id>/` (size must be a multiple of 32; `save()` writes row/col 0,0
   so patch them after for real zones).
4. **View the whole zone** — `python3 tools/view_world.py <zone>` → `tools/_generated/previews/maps/<zone>_detail.png`
   (a north-up colour minimap; it reads the SAVED chunks, so save first).
5. **Test in-game (no Unity needed)** — `run-backend` skill to start the server, then the sync-harness
   joins the zone and verifies it loads + ticks + spawns (see `tools/sync-harness/`).

**Quick mechanic-test zones:** `python3 tools/make_test_zone.py --zone-id <id> --species <s> --occupant 'id@x,y' …`
builds a tiny deterministic zone with a bug spawn + placed occupants — for isolating one mechanic.
**Spawning gotcha:** only species DEFINED in `nakama/data/species.json` spawn (currently
`fly_common`, `butterfly_meadow`, `wasp_common`, `centipede_garden`); `bugs.json` ids that
lack a species spec silently don't spawn.

## The builder — `tools/zonegen/`
- `zonebuilder.py` — `ZoneBuilder(zone_id, W, H, base_tile=…)`: the on-disk grids + the coordination
  masks `surface[]` (`water|path|building|farm|forest|grass`) and `reserved[]`. `place_occupant`
  (writes anchor + footprint cells, **refuses overlaps loudly**), `set_ground`, **`lint()`** (the text
  QA gate), `place_player`/`place_bug` (render-only dressing), `save()`/`load()`.
- `render.py` — `render_builder(b, out, scale, bounds=None)`: builder → full-art preview PNG.
- `registry.py` — the **scene catalog** + canonical render (prints lint).
- `features/` — the primitives (one guide each, below): `tilemap` (text-grid stamp/dump), `terrain`
  (`lake`/`forest`/`pond`/`rock_patch`/`path`/`stream`), `scatter`, `garden`, `yard`, `room`, `house`,
  `village`, `furniture`, `cave`.
- `scenes/` — three kinds: **building pieces** (`place_*` + `build()`), **vignette scenes** (registered
  previews), and **zone builders** (`zone_village.py` → `save()`).
- **Precedence — place HARD features first so later ones route around them:** biome base → water →
  roads → buildings → farms → scatter.

## Feature guides
- [building.md](building.md) — rooms, walls, doors, building shells (`room.place_room`).
- [house.md](house.md) — multi-room houses: the composer, the south-facing facing rule, room
  templates, ⊥/L shapes, furniture **collections** (basic/fancy), and the 3/4/5-room layout generators.
- [village.md](village.md) — composing a believable **town**: road hierarchy, function clusters, the
  `plaza()`/fountain focal point, `shop_building()`, density gradients, and the build-order recipe.
- [yard.md](yard.md) — fenced yards/pens: `fence_rect`, `yard` (gate + path + decor).
- [roads.md](roads.md) — organic roads/paths: `terrain.path` (wander + fray + taper), THE ROAD-ANGLE
  SYSTEM (`smooth_paths` + diagonal tiles — curves on square tiles), junction/adjacency rules.
- [vegetation.md](vegetation.md) — `scatter` (flowers/bushes/grass): density, spacing, **clumping**,
  grove metrics, the no-dead-grass rule.
- [water.md](water.md) — lakes (`terrain.lake` multi-blob shapes), `shore_dress` per-arc banks, docks.
  (Supersedes trees-and-ponds.md; its forest half lives in forest.md.)
- [caves.md](caves.md) — underground space (solid rock carved out).
- [ant-colony.md](ant-colony.md) — a worked underground nest ("creatures shape the underground").
- [blocks.md](blocks.md) — mineable/placeable cube blocks that tile in a grid.
- [biome-feature-map.md](biome-feature-map.md) — which primitives to reach for per biome.
- [research_procgen.md](research_procgen.md) — HOW OTHERS DO IT: the 2026-06 research sweep
  (noise fields, least-cost-path roads, building-footprint grammars) with the adopted/passed-on
  scoreboard — the rationale behind `noise_field`/`route_road`/`sculpt_plan`.

## Orient yourself
- **The whole map:** `docs/product/architecture_world.md` — the 24-zone grid, layout, river/roads,
  per-zone species, coordinates.
- **Per-zone design docs:** `docs/product/zones/<zone>.md` (start from `_TEMPLATE.md`). Current build
  scope: `docs/product/zones/demo_slice.md`.
- **Content to draw from:** `docs/brainstorms/<topic>/` + `ecology_proposal.md`.
- **Operational playbook:** the `author-zone` skill (`.claude/skills/author-zone/`) drives this loop.

> Worked examples to read: `scenes/scene_cottage.py` (a text-grid 2-room home + `property_yard`),
> `scenes/scene_village.py` (composing the building pieces into a town), and `scenes/zone_village.py`
> (a scene → full 256×256 zone: terrain + roads + bug spawning + `save()`).
