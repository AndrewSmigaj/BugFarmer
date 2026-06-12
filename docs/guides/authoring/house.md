# Feature guide: houses (multi-room buildings)

How to compose a **varied multi-room house** with `zonegen`'s house composer. Where
[building.md](building.md) covers a single `place_room` shell, this covers
stitching several differently-sized rooms into **one connected building** (an L, an
upside-down-T) with shared walls, interior doors, windows, and furniture placed against the
walls by reusable room templates.

Module: `tools/zonegen/features/house.py`. Reusable house: `tools/zonegen/scenes/player_house.py`
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

### VARIETY IS THE RULE (a residential street is never three clone boxes)
Houses are NOT perfect squares, and a street of identical cottages reads as a tech
demo (2026-06 playtest correction). On any street of 3+ homes, mix ALL of:
- **Shape**: at least one non-rectangular plan (⊥/L/+ via the layout generators or
  hand specs) beside the simple cottage/bar.
- **Collection**: at least one `basic` and one `fancy` home (the poor→nice range).
- **Fence**: vary the family — `fence_picket`, `fence_picket_weathered` (+
  `gate_wood_weathered`), hedge lines; the worn yard tells a story.
- **Setback**: stagger ox/oy a few cells; gates land at different lane offsets.

**SLOT SIZES (measured — budget these before placing, footprint + property_yard
side=2/front=4/back=3):** text-grid cottage ≈ **16×21** · `row_house` ≈ **33×18** ·
`t_house`/`plus_house` ≈ **36×26**. The composer bars are 3× wider than the cottage —
a slot sized by eye for the cottage WILL collide (this exact mistake cost an
iteration: interiors landed inside the neighbor's yard and the lint lit up with
fence-on-fence overlaps). Verify with `bbox(specs)` before committing positions, and
keep every slot clear of road corridors (the wobble band is ±2 around the
centerline).

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
python3 tools/zonegen/scenes/player_house.py     # render the house on its own
python3 tools/zonegen/scenes/scene1_player_farm.py  # render the house inside the full farm scene
```
Read the PNG (and crop with `render_builder(b, out, scale, bounds=(x0,y0,x1,y1))` for detail).
Aim for **0 placement warnings**; the builder refuses overlaps loudly.

## Authoring a themed building by TEXT GRID (the verified workflow)
For a **specific, themed building** (smith, carpenter, ecologist, market, boat store) author it as a
**character grid** with `features/tilemap.py`, not by guessing coordinates. This is the method that holds
up because it's **checkable in text** — I cannot reliably spot spatial defects in a big PNG, but I can
read a grid and the lint.

```python
from features.tilemap import stamp, dump
SMITH = """
WWWWWWWWWWWW
Wt........tW
W..F...G..SW
...
WWWWWDWWWWWW
"""
LEG = {"W": ("occ", "wall_stone"), "D": ("occ", "door_square"), "F": ("occ", "furnace"), ...}
stamp(b, SMITH, LEG, ox=ox, oy=oy)        # first line = NORTH/back; bottom = SOUTH/door
print(dump(b, ox, oy, ox+11, oy+9))       # read it back north-on-top to verify
print("LINT:", b.lint() or "0 defects")   # the QA gate — must be clean (bar the known height item)
```
Make each themed building a **`place_<thing>(b, ox, oy)` function** + a thin `build()` wrapper, so the
**village composes the real piece** (one source of truth) instead of a cruder re-creation.

### Full-home / full-building pattern (what "a building" means)
A building is a **home or shop, not a single room**, wrapped in a [`property_yard`](yard.md):
- **Houses** (ecologist, mayor, cottages) → a **main room + bedroom + kitchen + bathroom**, connected by
  interior doors (put internal `W`/`D` right in the grid; the lint checks interior doors too). Bathroom =
  `bathtub`+`vanity`+`sink`+`mirror` (no toilet sprite yet).
- **Shops/workshops** (smith, carpenter, market, boat store) → a **main room + a back SUPPLY room**.
- **Only HOMES are fenced.** A house sits in a `property_yard` (side yards + backyard + trees + front
  garden). A **shop is OPEN-FRONTED — NO fence** — just the building, its sign, and outdoor goods
  (ore/coal, lumber, produce stalls) out front. Fencing a shop reads wrong.
- **Place buildings CLEAR of every road** — a building dropped on a road tile leaves the road running
  visibly *through* it. In a composed scene, keep each footprint+yard off the road columns/rows.
- Compose the village from the `place_*` pieces: shops cluster at the square (commercial), homes line a
  residential street (each fenced), one cottage per NPC. Doors face south onto a street; a short `connect`
  path joins each door/gate to the road. (Side-facing doors are a TODO — grids currently put the door south.)

### Conventions the lint enforces — don't relearn these (each cost a correction)
1. **Doors are 1 cell wide** (`door_square`, 16×24). The cell directly inside the door must be clear
   floor — never run shelving/counters/buckets across the door wall. `lint()` flags blocked doorways.
2. **NPC behind a counter/desk: set them 2 cells back**, not 1. Player sprites draw in a final on-top
   pass, so an NPC one cell behind a (taller) counter renders *on the desk*.
3. **Keep tall decor OFF the row just inside the SOUTH wall.** The 2-tall wall draws over that row and
   clips lamps/vases/signs. Put tall pieces on the back/side walls or interior; leave the south row open.
4. **Multi-cell items: ONE char at the anchor**, dots for the rest of the footprint. The anchor is the
   **SW corner**; the footprint extends **NORTH (up) and EAST (right)** from it. Repeating the char
   places N overlapping copies (loud warnings). A 2×4 bed's char goes at its *south-west* grid cell.
5. **Every grid row must be the same width.** A stray extra char pokes a wall a cell out of the building
   (overlap warnings / fence-on-wall). Count them.
6. **Objects standing in water** (boat, mooring posts) need their footprint **un-reserved** first —
   `safe()`/`is_free()` correctly refuse reserved water, so the object silently doesn't place.
7. **Goods in rows; themed sign out front** (`sign_anvil`, `sign_plank`, `sign_leaf`, `sign_fish_board`).
8. The single intentional lint item right now is the **wall(32)/door(24) height mismatch** — walls are
   temporarily 2 cells tall pending a 1.5-cell re-bake; treat that one as expected.

## Cross-cutting
- New furniture/appliance sprites are added via the **add-object** skill (gpt-image-1); missing
  ones render as labeled placeholder squares. Track them in [art_needed.md](../../product/art_needed.md).
- Fenced **yards** (fence + gate + approach path + exterior decor) around a house:
  [yard.md](yard.md) (`features/yard.py`). Worked multi-house example:
  `tools/zonegen/scenes/scene_houses.py` (room counts × collections, each in a yard).
- Single-room shells, doors, and the precedence order: [building.md](building.md).
- Sprite/pipeline rules: [object_pipeline.md](../art/object_pipeline.md).
