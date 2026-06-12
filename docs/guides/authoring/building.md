# Feature guide: buildings / rooms

How to place building shells in a zone with `zonegen`'s `room` primitive. (New modular guide —
the older `BUILDING_TEMPLATES.md` registry of specific layouts is being folded in here; see BACKLOG
"Zone-design guides cleanup".)

## Primitive
```python
from features.room import place_room
interior = place_room(b, x0, y0, x1, y1, floor="wood_floor", wall="wall_wood",
                      door="door_wood", door_side="bottom", door_offset=None)
```
- `(x0,y0,x1,y1)` are the inclusive OUTER-wall bounds. It fills the interior floor (surface
  `building`), draws the wall border with a door gap, reserves the walls, and **returns the interior
  rect** `(ix0,iy0,ix1,iy1)` for placing furniture.
- The interior is left walkable (not reserved), so you place furniture into it with `place_occupant`.

## Design rules
- **Precedence:** place buildings AFTER water and roads so they don't land in a pond and so a door
  can face an existing path. Buildings reserve their footprint, so later farms/scatter avoid them.
- **Size:** rooms read best at ~8–12 cells per side; bigger rooms want internal structure (not one
  empty box). Doorways are 2 cells wide (the `door_wood` footprint) so the player fits.
- **Footprint awareness:** multi-cell furniture (beds, tables, fireplaces, chests are 2-wide or 2×2)
  must be placed so their footprint stays off the walls — keep their anchor ≥1 cell inside the wall
  on the wide/tall axis, or `place_occupant` will refuse it (loudly). Let the warnings guide you.
- **Furniture against walls:** beds/bookshelves/fireplaces along the back wall, table+chairs toward
  the center/front, a light in a corner — see `scenes/scene_cottage.py` for a worked layout.
- **Door + path:** put the door on the side facing the approach, and lay a `stone_path` from the
  door outward so the building connects to the rest of the zone.

## Interaction with other features
- Walls are reserved → roads route around them, scatter never lands on them.
- Don't place a building on `water`/`path`/another building; the builder refuses overlaps.

## Cross-cutting
Sprites must follow `MASTER_STYLE_GUIDE.md` (3/4 overhead, top-left light, footprint anchoring).
Missing building/furniture sprites render as placeholders; track them in `art_needed.md`.
