# Zone & scene authoring — the system

This is the index for **world-building**: how we lay out zones, houses, yards, caves, and the
example scenes that show them off. Read this first; it points at everything else.

The system is **four parts**, each with one home:

| Part | What it is | Lives in |
|------|------------|----------|
| **① The builder** | The Python library you compose zones/scenes with — feature primitives that coordinate through a shared occupancy model (a road routes around a pond; scatter avoids water). | `tools/zonegen/` |
| **② These guides** | How to do each world-building task (build a house, a yard, a cave…). Read & iterate on them as we learn. | `docs/guides/authoring/` |
| **③ Example scenes** | Small curated vignettes built with ①, rendered to preview PNGs. They double as the worked examples for these guides and the visual catalog/QA. | `tools/zonegen/scenes/` |
| **④ Art Lab** | A local web tool to view art **variants** in real scenes and pick which to keep. Consumes ③. | `tools/artlab/` |

> **Art is separate.** How sprites *look* and get made is `docs/guides/art/` (start with
> `art/object_pipeline.md`). These guides assume art already exists — or use a **placeholder**
> (a labeled colored square) so layout never waits on art.

## The loop (how we actually work)
1. Decide the contents — from a zone doc (`docs/product/zones/<zone>.md`) or the scene's theme.
   Mine `docs/brainstorms/<topic>/` for what to place.
2. Read the **feature guide(s)** for what you're building (below).
3. Build with `ZoneBuilder` + the `features/` primitives.
4. **Render a preview PNG and look at it.** The preview is the test — there's no live game here.
   Run `b.validate()`; aim for 0 placement warnings. Iterate the layout (and the guide).
5. New object with no art? It renders as a placeholder — log it in `docs/product/art_needed.md`.

```bash
python3 tools/zonegen/scenes/<scene>.py     # build + render ONE scene to its preview PNG
python3 tools/zonegen/registry.py           # render ALL registered scenes (canonical previews)
python3 tools/artlab/server.py              # Art Lab → http://localhost:8765
```

### Art Lab — picking sprite variants
Art Lab shows art **variants** (candidates) for a key overlaid in real scenes, so you can pick which
to keep. Variants live in `tools/_generated/variants/<key>/<key>_<n>.png` (gitignored — repopulate
after a clean). Populate the lab (no API spend):
```bash
python3 tools/artlab/library.py seed <key>…          # seed a key's CURRENT live sprite as a baseline
python3 tools/artlab/library.py import-blocklab       # pull block bake-off output (_generated/blocklab/) into the lab
python3 tools/artlab/library.py list                  # show the library
```
Get real alternatives to choose between by generating candidates (costs API): block bake-off is
`python3 tools/blocklab.py` → then `import-blocklab`. In the web UI, pick a variant per key and
**Apply** to promote it over the live game sprite.

## The builder — `tools/zonegen/`
- `zonebuilder.py` — `ZoneBuilder(zone_id, W, H, base_tile=…)`: the on-disk grids + the coordination
  masks `surface[]` (`water|path|building|farm|forest|grass`) and `reserved[]`. `place_occupant`
  (writes anchor + footprint cells, **refuses overlaps loudly**), `set_ground`, `validate()`,
  `save()` (real zones, size multiple of 32) / `load()` (edit an existing zone).
- `render.py` — `render_builder(b, out, scale, bounds=None)`: builder → preview PNG.
- `registry.py` — the **scene catalog** (which scenes exist, their zone + canonical render scale).
- `features/` — the primitives (one guide each, below).
- `scenes/` — every example scene + the reusable `player_house` preset.
- **Precedence — place HARD features first so later ones route around them:** biome base → water →
  roads → buildings → farms → scatter.

## Feature guides
- [building.md](building.md) — rooms, walls, doors, building shells (`room.place_room`).
- [house.md](house.md) — multi-room houses: the composer, the south-facing facing rule, room
  templates, ⊥/L shapes, furniture **collections** (basic/fancy), and the 3/4/5-room layout generators.
- [village.md](village.md) — composing a believable **town**: road hierarchy, function clusters, the
  `plaza()`/fountain focal point, `shop_building()`, density gradients, and the build-order recipe.
- [yard.md](yard.md) — fenced yards/pens: `fence_rect`, `yard` (gate + path + decor).
- [roads.md](roads.md) — organic roads/paths: `terrain.path` (wander + fray + taper), `hpath`/`vpath`.
- [vegetation.md](vegetation.md) — `scatter` (flowers/bushes/grass): density, spacing, **clumping**.
- [trees-and-ponds.md](trees-and-ponds.md) — `terrain.pond` + tree placement.
- [caves.md](caves.md) — underground space (solid rock carved out).
- [ant-colony.md](ant-colony.md) — a worked underground nest ("creatures shape the underground").
- [blocks.md](blocks.md) — mineable/placeable cube blocks that tile in a grid.
- [biome-feature-map.md](biome-feature-map.md) — which primitives to reach for per biome.

## Orient yourself
- **The whole map:** `docs/product/architecture_world.md` — the 24-zone grid, layout, river/roads,
  per-zone species, coordinates.
- **Per-zone design docs:** `docs/product/zones/<zone>.md` (start from `_TEMPLATE.md`). Current build
  scope: `docs/product/zones/demo_slice.md`.
- **Content to draw from:** `docs/brainstorms/<topic>/` + `ecology_proposal.md`.
- **Operational playbook:** the `author-zone` skill (`.claude/skills/author-zone/`) drives this loop.

> Worked example to read: `tools/zonegen/scenes/cottage.py` (a cottage interior + a fenced yard with
> scatter) and `scenes/scene_houses.py` (room counts × collections, yards).
