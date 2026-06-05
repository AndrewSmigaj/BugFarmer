# Feature guide: houses (multi-room buildings)

How to compose a **varied multi-room house** with `zonegen`'s house composer. Where
[feature-building.md](feature-building.md) covers a single `place_room` shell, this covers
stitching several differently-sized rooms into **one connected building** (an L, an
upside-down-T) with shared walls, interior doors, windows, and furniture placed against the
walls by reusable room templates.

Module: `tools/zonegen/features/house.py`. Worked example: `tools/zonegen/builds/player_house.py`.

## Orientation (read this first)
The renderer now matches the game: **world +Y is NORTH (up)**, so in a rendered preview
**higher row numbers are toward the TOP** of the image and row 0 is at the bottom. "North wall"
= the high-Y (top) wall; "south wall" = the low-Y (bottom) wall, nearest the camera.

## The facing rule (drives every furniture decision)
Every world sprite is drawn **front-on** — we always see the object's FRONT (it faces south,
toward the camera). Consequences:
- Pieces with an obvious front/back — **fridge, bookshelf, dresser, fireplace, wardrobe, the
  bug-terrarium display** — read correctly only against the **NORTH wall** (back) or the **SIDE
  walls**. On the south wall they'd show their front into the wall and look wrong.
- **Flat / low** pieces — counter, sink, stove, table, chairs, rugs — read fine anywhere, so the
  **south wall** is for those plus the **entry** (front door).
- There are no rotated sprites yet, so don't expect a piece to "turn" to face a wall; place it
  where front-on reads right.

## The composer
```python
from features.house import (place_house, living_template, bedroom_template,
                            kitchen_template, crafting_template)

rooms = [
    {"name": "bedroom",  "rect": (4, 8, 13, 17),   "fill": bedroom_template},
    {"name": "main",     "rect": (13, 8, 24, 17),  "fill": living_template},
    {"name": "kitchen",  "rect": (24, 8, 34, 17),  "fill": kitchen_template},
    {"name": "crafting", "rect": (15, 17, 23, 25), "fill": crafting_template},
]
place_house(b, rooms, front=("main", "top"))   # exterior door on main's south wall
```
- Each `rect` is the inclusive **OUTER-wall** bounds. Adjacent rooms **overlap by exactly one
  shared wall line** (e.g. bedroom `x1 == main x0`); the composer turns each shared segment into
  a wall with a **single interior door** punched through it.
- `front=("room_name", side)` puts the exterior door on that room's wall. **`side` is in
  array-naming**: `"top"` = the low-Y (south) wall, `"bottom"` = the high-Y (north) wall,
  `"left"`/`"right"` = side walls. For a south-facing entrance use `"top"`.
- The composer also scatters **windows** on long exterior walls (`window_4pane`), and computes
  **doorways** (the interior cell just inside each door) which templates keep clear.
- `fill` is the room's furniture template; it receives `(b, interior_rect, doors, doorways)`.

### Shapes
Compose shapes by choosing room rects that share walls:
- **Upside-down-T (⊥):** a horizontal bar of three rooms, plus one room whose south wall sits on
  the middle room's north wall (the stem rising north). See `player_house.py`.
- **L:** two rooms sharing one wall, a third sharing a wall with one of them.
- Vary room **sizes** (different widths/heights) — don't make three equal boxes. Keep rooms
  **cozy** (~8–10 cells/side); fill them with furniture rather than making them cavernous.

## Furniture: templates + `wall_run`
Templates place furniture **against walls** using `wall_run` and a doorway-safe `_safe`:
```python
wall_run(b, ["counter", "sink", "counter", "stove"], side="top", I=I, doorways=doorways)
```
- `side`: `top` = south wall, `bottom` = north wall, `left`/`right` = side walls. Items advance
  along the wall by their footprint; anything that would land in a doorway is skipped.
- Multi-cell footprints anchor at their **top-left** and extend **down-right** (south→…); the
  sprite baselines at the footprint's front edge and rises toward the back, so a deep piece (a
  4-cell bed) fills its footprint instead of poking through a wall.

### The four stock templates (reusable across houses)
- **`living_template`** — hearth + bookshelf + bug-trophy on the **north** wall; sofa, rug,
  armchairs in the middle; plants in the south corners; entry kept clear.
- **`bedroom_template`** — bed along a side wall (foot toward camera); bookshelf + dresser on the
  **north** wall; nightstand, rug, lamp.
- **`kitchen_template`** — flat `counter`/`sink`/`stove` run on the **south** wall; the
  front-facing **`fridge`** + extra counter on the **north** wall; kegs on a side wall; the 2×2
  square `table_wood` + chairs centered.
- **`crafting_template`** — `furnace` + `cauldron` on the **north** wall; `workbench` + `anvil`
  as work surfaces flanking the south entry; storage (chest/barrel/crate) on a side wall.

Write a **new template** as `fn(b, interior, doors, doorways)`: unpack `ix0,iy0,ix1,iy1`, build
a doorway-safe `P = lambda oid,x,y,**k: _safe(b,oid,x,y,doorways,**k)`, and place per the facing
rule (front-facing on north/sides, flat on south). Render and let the builder's overlap warnings
guide you.

## Build → render → review loop
```bash
python3 tools/zonegen/builds/player_house.py     # build + render the preview PNG
```
Read the PNG (and crop with `render_builder(b, out, scale, bounds=(x0,y0,x1,y1))` for detail).
Aim for **0 placement warnings**; the builder refuses overlaps loudly.

## Cross-cutting
- New furniture/appliance sprites are added via the **add-object** skill (gpt-image-1); missing
  ones render as labeled placeholder squares. Track them in [../product/art_needed.md](../product/art_needed.md).
- Single-room shells, doors, and the precedence order: [feature-building.md](feature-building.md).
- Sprite/pipeline rules: [object_pipeline.md](object_pipeline.md).
