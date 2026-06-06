# Feature guide: houses (multi-room buildings)

How to compose a **varied multi-room house** with `zonegen`'s house composer. Where
[feature-building.md](feature-building.md) covers a single `place_room` shell, this covers
stitching several differently-sized rooms into **one connected building** (an L, an
upside-down-T) with shared walls, interior doors, windows, and furniture placed against the
walls by reusable room templates.

Module: `tools/zonegen/features/house.py`. Reusable house: `tools/zonegen/houses/player_house.py`
(`place_player_house(b, ox, oy)` drops it into any scene). Worked use: `tools/zonegen/scenes/scene1_player_farm.py`.

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
from features.house import (place_house, styled_rooms, living_template, bedroom_template,
                            kitchen_template, crafting_template)

# (name, rect, template) specs; styled_rooms binds a FURNITURE COLLECTION (see below).
rooms = styled_rooms([
    ("bedroom",  (4, 8, 13, 17),  bedroom_template),
    ("main",     (13, 8, 24, 17), living_template),
    ("kitchen",  (24, 8, 34, 17), kitchen_template),
    ("crafting", (15, 17, 23, 25), crafting_template),
], collection="fancy")
place_house(b, rooms, front=("main", "top"))   # exterior door on main's south wall
```
(You can still pass a raw `rooms` list of `{"name","rect","fill"}` dicts; `styled_rooms` is the
terse form that also binds the collection. For ready-made shapes use the layout generators below.)
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

### Room-count layouts (`houses/layouts.py`)
Ready-made shared-wall floor plans so you don't hand-place every rect — each returns
`(specs, front)` for `styled_rooms(specs, collection)` → `place_house(b, rooms, front=front)`:
- `row_house(ox, oy)` — 3 rooms in a bar.
- `t_house(ox, oy)` — 4 rooms (bar + a crafting stem north; the ⊥).
- `plus_house(ox, oy)` — 5 rooms (bar + study & sunroom stems north).
`bbox(specs)` returns the overall rect (handy for wrapping the house in a yard).

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

Each stock template takes a trailing `coll=` (the collection) and asks the catalog for the right id
per **role** (`pick(role, coll)`), so the SAME template furnishes a plain or an upscale room.

Write a **new template** as `fn(b, interior, doors, doorways, coll="basic")`: unpack `ix0,iy0,ix1,iy1`,
`F = lambda role: pick(role, coll)`, build a doorway-safe `P` that skips `None`
(`lambda oid,x,y,**k: _safe(b,oid,x,y,doorways,**k) if oid else False`), and place `F("bed")`,
`F("lounge")`, etc. per the facing rule. Render and let the builder's overlap warnings guide you.

## Furniture collections (`features/furniture.py`)
A **collection** is a self-contained look/feel set mapping a **role** (bed, seating, lounge, table,
light, rug, plant, hearth, display, counter, stove, …) to a concrete entity id. A house picks a
collection; any role it doesn't define falls back to `basic`. Two exist now — `basic` (plain/cheap) and
`fancy` (upscale) — and they're **modular: add or remove a collection as a unit** (later: `tropical`,
`modern`, `rustic` — ideally each its own module). The "which is fancy / appropriate for wealth"
knowledge lives HERE, in the scaffolding — never in the game's entity data (the game treats every
placeable as an independent item).
- Use it via `styled_rooms(specs, collection="fancy")` (binds `coll` into each template).
- `pick(role, collection)` resolves the id (returns `None` for a role a collection intentionally omits,
  e.g. `basic` has no clock → templates skip it).
- **Members of a role across collections should share a footprint** (so swapping doesn't shift
  `wall_run` placement); flat decor (rug) is the allowed exception.
- To add a collection: define a new `role -> id` dict listing only the roles where it differs from
  `basic`, and register it in `COLLECTIONS`. New ids are added via the **add-object** skill.

## Build → render → review loop
```bash
python3 tools/zonegen/houses/player_house.py     # render the house on its own
python3 tools/zonegen/scenes/scene1_player_farm.py  # render the house inside the full farm scene
```
Read the PNG (and crop with `render_builder(b, out, scale, bounds=(x0,y0,x1,y1))` for detail).
Aim for **0 placement warnings**; the builder refuses overlaps loudly.

## Cross-cutting
- New furniture/appliance sprites are added via the **add-object** skill (gpt-image-1); missing
  ones render as labeled placeholder squares. Track them in [../product/art_needed.md](../product/art_needed.md).
- Fenced **yards** (fence + gate + approach path + exterior decor) around a house:
  [feature-yard.md](feature-yard.md) (`features/yard.py`). Worked multi-house example:
  `tools/zonegen/scenes/scene_houses.py` (room counts × collections, each in a yard).
- Single-room shells, doors, and the precedence order: [feature-building.md](feature-building.md).
- Sprite/pipeline rules: [object_pipeline.md](object_pipeline.md).
