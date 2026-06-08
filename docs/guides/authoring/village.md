# Feature guide: villages & towns

How to compose a believable, lived-in **town** with `zonegen` — not a rigid grid of identical
buildings. This guide pairs design **principles** (why) with the **methods** (which primitive does the
job), and gives the **build-order recipe** the script follows. The worked example is
`tools/zonegen/scenes/scene_village.py`; the zone intent is `docs/product/zones/village_21.md`.

## Principles (what makes a town read as real)
Distilled from how good 2D top-down games lay out towns (Stardew's Pelican Town) and level-design /
urban-design writing on settlement form:

| # | Principle | How it shows up here |
|---|-----------|----------------------|
| 1 | **One focal point per area** | a fountain `plaza()` at the town centre; the docks at the lake |
| 2 | **Density gradients are the boundary** (not walls) | buildings/props dense at centre → `scatter` density rises toward the forest rim |
| 3 | **Road hierarchy: main → side → path** | `path()` main road (width 4) → connector (3) → side lanes (2) |
| 4 | **Cluster buildings by function** | civic (hall·market·grocer·store) by the square; production (carpenter+smith) adjacent; cottages on a side lane; boat store at the lake |
| 5 | **Contrast for legibility** | the tended town floor vs the wild meadow; a tall hall vs low cottages |
| 6 | **Curves beat the grid** | `path()` `wobble` + offset endpoints so roads bend, never rule a straight column |
| 7 | **Signage + props signal function** | 3-wide `sign_market_board`, the smith's forge/anvil, the docks/boat |
| 8 | **Worn over pristine** | `fence_picket_weathered` on the poor cottage; `edge_tile="dirt"` road shoulders |
| 9 | **Emergence via systems, not props** | orchard fruit → `fruit_around` fresh→rot → fruit-flies; no "rot" objects |
| 10 | **Vegetation clumps** | `scatter(..., clumping≈0.85)` — patches with bare ground, never confetti |
| 11 | **Orchard rows with variation** | alternating species rows + jittered `fruit_around` |
| 12 | **A cozy civic heart** | the plaza: fountain + benches + lamps + corner flower beds |
| 13 | **Imply variety** | mix building orientations (doors on different sides), mix cottage collections |

## Methods (principle → primitive)
| Job | Call |
|-----|------|
| Lake (carve first, reserves water) | `terrain.pond(b, cx, cy, rx, ry, seed)` |
| All roads (organic, route around reserved) | `terrain.path(b, start, end, width=, edge_tile="dirt", wobble=, taper_ends=, seed=)` |
| A shop (shell + wide sign + shelf rows + counter + NPC) | `village.shop_building(b, x0,y0,x1,y1, sign_id=, npc=, door_side=, shelf_rows=, extra_fill=)` |
| The civic square (paving + fountain + seats + lamps + beds) | `village.plaza(b, cx, cy, r=)` |
| Cottages (2–3 rooms, varied orientation) | `house.place_house(b, styled_rooms(specs, coll), front=(room, side))` + `row_/t_/plus_house` |
| Generic building shell (door any side) | `room.place_room(b, x0,y0,x1,y1, door_side∈{top,bottom,left,right})` |
| Interior rows of furniture/goods | `house.wall_run(b, items, side=, I=)` (`side="bottom"`=back/north wall, per the facing rule) |
| Fenced yards / picket gardens | `yard.fence_rect(b, ..., fence="fence_picket", gate_id="gate_picket")`, `yard.yard(...)` |
| Garden beds + free-floating flowers/fruit | `garden.crop_bed`, `garden.flower_patch` (sub-grid), `garden.fruit_around` (sub-grid) |
| Clumped meadow | `scatter.scatter(b, ..., clumping≈0.85, density=, seed=)` |
| NPCs / shopkeepers (render-only) | `b.place_player("merchant_down", x, y)` (sprites: merchant/farmer/scholar/ranger × dir) |
| Bugs facing either way (render-only) | `b.place_bug(sprite_id, x, y, scale, flip=)` |

> **Doors on any side already work** — vary `front=(room, side)` / `door_side` for orientation variety
> (Principle 13). **Plants are NOT grid-locked** — `flower_patch`/`fruit_around`/`place_decor` place at
> sub-grid float coords. **Bugs** take `flip=True` to mirror their facing.

## The build-order recipe (and why this order)
Each step coordinates through `reserved[]`/`surface[]`, so later features route around earlier ones:
1. **Base grass** — `ZoneBuilder(...)`.
2. **Lake first** — `pond()` reserves `surface='water'` so roads/scatter avoid it.
3. **Main road → connector → side lanes** — `path()` (widths 4→3→2); paints `surface='path'`, parts
   around the lake. Offset endpoints + `wobble` so it bends.
4. **Building clusters** — `shop_building`/`place_house`/`place_room` reserve footprints (refuse-on-
   overlap keeps it warning-free) and sit beside the roads. Vary door sides for orientation.
5. **Plaza + fountain** — `plaza()` at the road crossing = the focal point; set `b.spawn` on its paving.
6. **Yards & gardens** — picket `fence_rect` + `crop_bed`/`flower_patch`/`garden_border_*`.
7. **Orchard + fly farm (edges)** — `fence_rect` + tree rows + `fruit_around` (the fly-emergence loop).
8. **Clumped meadow scatter (LAST)** — only fills free grass; density **rises toward the rim** (forest
   edge = the town's boundary). Distinct `seed` per region.
9. **Free-floating decor** — `flower_patch` ribbons along roads/meadow gaps; `place_decor` lily pads.
10. **Bugs** — `place_bug(..., flip=…)` with mixed facing/scale: butterflies/bees at the plaza,
    dragonflies over the lake, flies at orchard/fly-farm.

## Review checklist (run each iteration)
- `b.validate() == []` and **0 placement warnings**.
- Lake is **big**; the **main road bends** (not a ruled line); the **plaza is centred** with the
  fountain dead-centre; the **4 clusters** are legible and separated.
- Per building, ask **"is this good quality?"** — the market reads as a market (wide sign, shelf rows,
  NPC behind the counter); the carpenter's sawmill is **indoors** with goods in tidy **rows**; smith is
  **adjacent** to carpenter; the civic three are near each other; **orientations vary**; the
  picket-fenced cottage is enclosed with its garden.
- Vegetation is **patchy** (clumping, not confetti/grid); free-floating flowers sit **off-grid**; bugs
  **face different ways**; the density gradient walls the town with forest at the rim; worn variants
  present; the orchard fly loop is visible.

## Cross-references
`house.md` (composer, facing rule, collections, layouts) · `roads.md` (`path` wander/fray/taper) ·
`yard.md` (fences/pens) · `vegetation.md` (`scatter` clumping). Content ideas:
`docs/brainstorms/{decorations,flora,landmarks}/village.md`. Zone intent: `../../product/zones/village_21.md`.
New entities render as placeholders until art lands — track in `../../product/art_needed.md`.
