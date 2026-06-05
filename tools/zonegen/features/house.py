#!/usr/bin/env python3
"""House composer + furniture templates.

`place_house()` takes a list of room rects (inclusive OUTER-wall bounds) that may SHARE
wall lines, and draws ONE connected building: floors, the merged wall border, interior
doors between adjacent rooms, an exterior front door, and windows on the outside walls —
then runs each room's furniture template. This is what gives VARIED multi-room shapes
(an L, an upside-down-T) instead of one box split into equal thirds.

A room is a dict:
    {"rect": (x0, y0, x1, y1), "name": "kitchen", "fill": kitchen_template}
Adjacent rooms overlap by exactly ONE shared wall column/row; that shared line becomes a
wall with a single door punched through it. Templates place furniture AGAINST the walls
(via `wall_run`) so nothing floats in the middle of a room.

Reuse: import the templates into any house build script, or write new ones — the composer
doesn't care which template fills a room.
"""


# ---- geometry helpers -------------------------------------------------------
def _border(rect):
    x0, y0, x1, y1 = rect
    cells = set()
    for x in range(x0, x1 + 1):
        cells.add((x, y0))
        cells.add((x, y1))
    for y in range(y0, y1 + 1):
        cells.add((x0, y))
        cells.add((x1, y))
    return cells


def _interior_cells(rect):
    x0, y0, x1, y1 = rect
    return {(x, y) for x in range(x0 + 1, x1) for y in range(y0 + 1, y1)}


def _side_cells(rect, side):
    """Non-corner cells of one OUTER wall side, in order."""
    x0, y0, x1, y1 = rect
    if side == "top":
        return [(x, y0) for x in range(x0 + 1, x1)]
    if side == "bottom":
        return [(x, y1) for x in range(x0 + 1, x1)]
    if side == "left":
        return [(x0, y) for y in range(y0 + 1, y1)]
    if side == "right":
        return [(x1, y) for y in range(y0 + 1, y1)]
    return []


def _segment_interior(cells):
    """Drop the two endpoints (corners) of a straight wall segment."""
    s = sorted(cells)
    return s[1:-1] if len(s) > 2 else s


# ---- the composer -----------------------------------------------------------
def place_house(b, rooms, *, floor="wood_floor", wall="wall_wood",
                interior_door="door_square", front_door="door_square",
                front=None, window="window_4pane", windows=True):
    """Build a connected multi-room house from `rooms`. `front` is ("room_name", side)
    for the exterior door. Returns the rooms list (with interiors filled)."""
    # 1. floors
    interiors = set()
    for r in rooms:
        x0, y0, x1, y1 = r["rect"]
        b.fill_ground(x0 + 1, y0 + 1, x1 - 1, y1 - 1, floor, surface="building")
        interiors |= _interior_cells(r["rect"])

    borders = [(_border(r["rect"]), r) for r in rooms]
    wallcells = set()
    for cells, _ in borders:
        wallcells |= cells
    wallcells -= interiors  # a junction that is floor of a room is an opening, not a wall

    # 2. shared (room-to-room) segments vs exterior walls
    shared_all = set()
    doors = {}  # cell -> door id
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            shared = borders[i][0] & borders[j][0] & wallcells
            if len(shared) >= 3:  # a real shared wall, not a single corner touch
                shared_all |= shared
                inner = _segment_interior(shared)
                if inner:
                    doors[inner[len(inner) // 2]] = interior_door
    exterior = wallcells - shared_all

    # 3. exterior front door
    if front:
        name, side = front
        r = next(rr for rr in rooms if rr["name"] == name)
        cand = [c for c in _side_cells(r["rect"], side) if c in exterior and c not in doors]
        if cand:
            doors[cand[len(cand) // 2]] = front_door

    # 4. windows on long exterior sides (skip corners + doors + the front wall span)
    win = {}
    if windows:
        for r in rooms:
            for side in ("top", "bottom", "left", "right"):
                cand = [c for c in _side_cells(r["rect"], side)
                        if c in exterior and c not in doors]
                if len(cand) >= 9:
                    for idx in (len(cand) // 4, 3 * len(cand) // 4):
                        win[cand[idx]] = window
                elif len(cand) >= 3:
                    win[cand[len(cand) // 2]] = window
    for c in doors:  # doors win any tie
        win.pop(c, None)

    # 5. place walls (skipping openings), then doors, then windows
    for (x, y) in sorted(wallcells):
        if (x, y) in doors or (x, y) in win:
            continue
        b.place_occupant(wall, x, y)
    for (x, y), did in doors.items():
        b.place_occupant(did, x, y)
    for (x, y), wid in win.items():
        b.place_occupant(wid, x, y)

    # 6. fill each room. Templates keep `doorways` (the interior cells just inside a door)
    # clear so furniture never blocks a doorway.
    doorways = set()
    for (dx, dy) in doors:
        for nx, ny in ((dx + 1, dy), (dx - 1, dy), (dx, dy + 1), (dx, dy - 1)):
            if (nx, ny) in interiors:
                doorways.add((nx, ny))
    for r in rooms:
        x0, y0, x1, y1 = r["rect"]
        interior = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        fill = r.get("fill")
        if fill:
            rdoors = [c for c in doors if c in _border(r["rect"])]
            fill(b, interior, rdoors, doorways)
    return rooms


# ---- placement helpers ------------------------------------------------------
# FACING RULE: every world sprite is drawn front-on (south-facing — we see its front).
# So pieces with an obvious front/back — fridge, bookshelf, dresser, fireplace, the bug
# display — read correctly only against the NORTH wall (iy1, back) or the SIDE walls; on
# the SOUTH wall (iy0, nearest the camera) they'd show their front into the wall and look
# wrong. Flat/low pieces (counter, sink, stove, table, chairs) read fine anywhere, so the
# south wall is reserved for those plus the entry. In interior-rect coords here, iy0 is the
# SOUTH (front) wall and iy1 is the NORTH (back) wall.

def _cells(b, oid, x, y):
    fw, fh = b.footprint(oid)
    return {(x + dx, y + dy) for dy in range(fh) for dx in range(fw)}


def _safe(b, oid, x, y, doorways, **kw):
    """place_occupant, but refuse if the footprint would fall in a doorway (keep it clear)."""
    if _cells(b, oid, x, y) & doorways:
        return False
    return b.place_occupant(oid, x, y, **kw)


def wall_run(b, items, *, side, I, start=0, gap=0, reserve=True, doorways=()):
    """Place a row of items hugging one wall of interior rect I=(ix0,iy0,ix1,iy1).
    side: top=south wall, bottom=north wall, left/right=side walls. Items advance by their
    footprint (+gap); items that would fall in a doorway are skipped (the slot still advances).
    Returns [(item, x, y, ok), ...]."""
    ix0, iy0, ix1, iy1 = I
    dw = set(doorways)
    placed, pos = [], start
    for it in items:
        fw, fh = b.footprint(it)
        if side == "top":
            x, y = ix0 + pos, iy0
        elif side == "bottom":
            x, y = ix0 + pos, iy1 - (fh - 1)
        elif side == "left":
            x, y = ix0, iy0 + pos
        elif side == "right":
            x, y = ix1 - (fw - 1), iy0 + pos
        else:
            break
        ok = False if (_cells(b, it, x, y) & dw) else b.place_occupant(it, x, y, reserve=reserve)
        placed.append((it, x, y, ok))
        pos += (fw if side in ("top", "bottom") else fh) + gap
    return placed


def _center(I):
    ix0, iy0, ix1, iy1 = I
    return (ix0 + ix1) // 2, (iy0 + iy1) // 2


# ---- room templates (reusable across houses) --------------------------------
def living_template(b, I, doors, doorways):
    """Main / sitting room (front door on the south wall): hearth + shelves + bug-trophy on
    the NORTH wall (front-facing), a sofa and armchairs around a rug in the middle, plants in
    the south corners, entry kept clear."""
    ix0, iy0, ix1, iy1 = I
    cx, cy = _center(I)

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k)

    P("fireplace", cx - 1, iy1)            # 2x1 hearth, flush against the north (back) wall
    P("bookshelf", ix0, iy1)               # north wall, west
    P("bug_terrarium", ix1, iy1)           # north wall, east (show off your catches)
    P("rug", cx - 1, cy - 1, reserve=False, surface=None)
    P("sofa", cx - 1, cy)                   # centered, facing the camera
    P("armchair", ix0, cy - 1)             # west, by the rug
    P("armchair", ix1, cy - 1)             # east, by the rug
    P("lamp_floor", ix0, iy1 - 1)          # west wall, by the shelf
    P("grandfather_clock", ix1, cy + 1)    # east wall
    P("vase", ix1, iy1 - 1)                # east wall, by the terrarium
    P("potted_plant", ix0, iy0)            # south-west corner
    P("potted_plant", ix1, iy0)            # south-east corner


def bedroom_template(b, I, doors, doorways):
    """Bed along a side wall, bookshelf + dresser on the NORTH wall (front-facing), a rug,
    plant and lamp."""
    ix0, iy0, ix1, iy1 = I

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k)

    P("bed_fancy", ix0, iy0)               # 2x4 along the west wall, foot toward the camera
    P("nightstand", ix0 + 2, iy0)          # beside the foot of the bed
    P("dresser", ix0, iy1)                 # north wall, west (front-facing)
    P("bookshelf", ix0 + 2, iy1)           # north wall (front-facing)
    P("potted_plant", ix1, iy1)            # north-east corner
    P("rug", ix0 + 2, iy0 + 2, reserve=False, surface=None)
    P("vase", ix1, iy1 - 1)                # east wall
    P("lamp_floor", ix1, iy0)              # south-east corner


def kitchen_template(b, I, doors, doorways):
    """Flat appliances (counter/sink/stove) along the SOUTH wall; the fridge (front-facing)
    plus extra counter on the NORTH wall; kegs on a side wall; the 2x2 square table + chairs
    in the middle."""
    ix0, iy0, ix1, iy1 = I

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k)

    wall_run(b, ["counter", "sink", "counter", "stove"], side="top", I=I, doorways=doorways)
    wall_run(b, ["fridge", "counter", "counter"], side="bottom", I=I, doorways=doorways)
    wall_run(b, ["keg", "keg", "barrel"], side="right", I=I, start=1, doorways=doorways)
    cx, cy = _center(I)
    P("table_wood", cx - 1, cy)            # 2x2 square table
    P("chair_wood", cx - 2, cy)
    P("chair_wood", cx + 1, cy)
    P("potted_plant", ix1, iy1)            # north-east corner
    P("lamp_floor", ix1, iy0)              # south-east corner


def crafting_template(b, I, doors, doorways):
    """Workshop nook (door on the south wall): furnace + cauldron on the NORTH wall
    (front-facing), workbench + anvil as work surfaces flanking the entry, storage on a side
    wall."""
    ix0, iy0, ix1, iy1 = I

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k)

    P("furnace", ix0, iy1 - 1)             # 2x2 north wall, west
    P("cauldron", ix1 - 1, iy1 - 1)        # 2x2 north wall, east
    P("workbench", ix0, iy0)               # south wall, west (work surface)
    P("anvil", ix1 - 1, iy0)               # south wall, east (work surface)
    P("chest_wood", ix0, _center(I)[1])    # west wall storage
    P("barrel", ix1, _center(I)[1])        # east wall
    P("crate", ix1, _center(I)[1] + 1)
    P("torch", ix1, iy0 + 1)                # east wall light, above the entry
