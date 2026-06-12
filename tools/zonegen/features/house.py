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

Furniture is chosen by COLLECTION (see features/furniture.py): each template takes a `coll`
("basic" | "fancy" | ...) and asks the catalog for the right id per role, so the SAME template
furnishes a plain or an upscale room. Bind the collection per room with `styled_rooms()`.
"""

import random
from functools import partial

from .furniture import pick


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

    # 7. RESERVE the interiors (2026-06: a lane got paved straight through a
    # living room — path() skip-paints reserved cells, but interior FLOOR cells
    # were never reserved, so the road threaded between the furniture). A
    # finished house is SOLID: nothing places or paints inside it afterwards.
    for (x, y) in interiors:
        if b.in_bounds(x, y) and not b.reserved[y][x]:
            b.reserved[y][x] = True
    return rooms


def styled_rooms(specs, collection="basic"):
    """Build a `rooms` list for place_house, binding a furniture collection into each template.
    `specs` = [(name, rect, template_fn), ...]. The collection threads in via the template's
    `coll` kwarg, so place_house's fill(b, I, doors, doorways) contract is unchanged."""
    return [{"name": n, "rect": r, "fill": partial(fn, coll=collection)}
            for (n, r, fn) in specs]


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
def living_template(b, I, doors, doorways, coll="basic"):
    """Main / sitting room (front door on the south wall): hearth + shelves + bug-trophy on
    the NORTH wall (front-facing), a sofa and armchairs around a rug in the middle, plants in
    the south corners, entry kept clear. Furniture per the `coll` collection."""
    ix0, iy0, ix1, iy1 = I
    cx, cy = _center(I)
    F = lambda role: pick(role, coll)

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k) if oid else False

    P(F("hearth"), cx - 1, iy1)            # 2x1 hearth, flush against the north (back) wall
    P(F("bookshelf"), ix0, iy1)            # north wall, west
    P(F("display"), ix1, iy1)              # north wall, east (show off your catches)
    P(F("rug"), cx - 1, cy - 1, reserve=False, surface=None)
    P(F("lounge"), cx - 1, cy)             # centered sofa, facing the camera
    P(F("armchair"), ix0, cy - 1)          # west, by the rug
    P(F("armchair"), ix1, cy - 1)          # east, by the rug
    P(F("light"), ix0, iy1 - 1)            # west wall, by the shelf
    P(F("clock"), ix1, cy + 1)             # east wall (skipped if the collection has none)
    P(F("accent_small"), ix1, iy1 - 1)     # east wall, by the terrarium
    P(F("plant"), ix0, iy0)                # south-west corner
    P(F("plant"), ix1, iy0)                # south-east corner


def bedroom_template(b, I, doors, doorways, coll="basic"):
    """Bed along a side wall, bookshelf + dresser on the NORTH wall (front-facing), a rug,
    plant and lamp. Furniture per the `coll` collection."""
    ix0, iy0, ix1, iy1 = I
    F = lambda role: pick(role, coll)

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k) if oid else False

    P(F("bed"), ix0, iy0)                  # 2x4 along the west wall, foot toward the camera
    P(F("nightstand"), ix0 + 2, iy0)       # beside the foot of the bed
    P(F("dresser"), ix0, iy1)              # north wall, west (front-facing)
    P(F("bookshelf"), ix0 + 2, iy1)        # north wall (front-facing)
    P(F("plant"), ix1, iy1)                # north-east corner
    P(F("rug"), ix0 + 2, iy0 + 2, reserve=False, surface=None)
    P(F("accent_small"), ix1, iy1 - 1)     # east wall
    P(F("light"), ix1, iy0)                # south-east corner


def kitchen_template(b, I, doors, doorways, coll="basic"):
    """Flat appliances (counter/sink/stove) along the SOUTH wall; the fridge (front-facing)
    plus extra counter on the NORTH wall; kegs on a side wall; the 2x2 square table + chairs
    in the middle. Furniture per the `coll` collection."""
    ix0, iy0, ix1, iy1 = I
    F = lambda role: pick(role, coll)

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k) if oid else False

    wall_run(b, [F("counter"), F("sink"), F("counter"), F("stove")],
             side="top", I=I, doorways=doorways)
    wall_run(b, [F("fridge"), F("counter"), F("counter")],
             side="bottom", I=I, doorways=doorways)
    wall_run(b, ["keg", "keg", "barrel"], side="right", I=I, start=1, doorways=doorways)
    cx, cy = _center(I)
    P(F("table"), cx - 1, cy)              # 2x2 square table
    P(F("seating"), cx - 2, cy)
    P(F("seating"), cx + 1, cy)
    P(F("plant"), ix1, iy1)                # north-east corner
    P(F("light"), ix1, iy0)                # south-east corner


def crafting_template(b, I, doors, doorways, coll="basic"):
    """Workshop nook (door on the south wall): furnace + cauldron on the NORTH wall
    (front-facing), workbench + anvil as work surfaces flanking the entry, storage on a side
    wall. Crafting stations are functional (not collection-varied); `coll` is accepted for a
    uniform template signature."""
    ix0, iy0, ix1, iy1 = I

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k) if oid else False

    P("furnace", ix0, iy1 - 1)             # 2x2 north wall, west
    P("cauldron", ix1 - 1, iy1 - 1)        # 2x2 north wall, east
    P("workbench", ix0, iy0)               # south wall, west (work surface)
    P("anvil", ix1 - 1, iy0)               # south wall, east (work surface)
    P("chest_wood", ix0, _center(I)[1])    # west wall storage
    P("barrel", ix1, _center(I)[1])        # east wall
    P("crate", ix1, _center(I)[1] + 1)
    P("torch", ix1, iy0 + 1)                # east wall light, above the entry


def bathroom_template(b, I, doors, doorways, coll="basic"):
    """A BATHROOM (the full-home standard 2026-06: EVERY house has one — no
    toilet sprite yet, per house.md): bathtub along the west wall, vanity + sink
    on the north (back) wall per the facing rule, a standing mirror east, a rug.
    All pieces have art (bathtub 2×1, vanity, sink, mirror_standing)."""
    ix0, iy0, ix1, iy1 = I

    def P(oid, x, y, **k):
        return _safe(b, oid, x, y, doorways, **k) if oid else False

    P("bathtub", ix0, iy1 - 1)                              # west wall, toward the back
    wall_run(b, ["vanity", "sink"], side="bottom", I=I, doorways=doorways)
    P("mirror_standing", ix1, iy1 - 1)                      # east wall
    P("rug", _center(I)[0], _center(I)[1], reserve=False)


# ---- floor-plan layouts -----------------------------------------------------
# Reusable house FLOOR-PLAN generators — pure geometry, no furniture/collection choice.
# Each returns (specs, front) where specs = [(name, rect, template_fn), ...] with inclusive
# outer-wall rects that SHARE exactly one wall line between adjacent rooms (so place_house
# punches an interior door), and front = ("room", side) for the exterior door (a south/min-y
# exterior wall). Compose: styled_rooms(specs, collection) -> place_house(b, rooms, front=front).
# Shapes: row_house (3 in a bar), t_house (4 = bar + a north stem, the ⊥), plus_house
# (5 = bar + two north stems). Rooms are ~10x10 outer (≈8x8 interior) so furniture fits.
def _shift(specs, ox, oy):
    return [(n, (x0 + ox, y0 + oy, x1 + ox, y1 + oy), f)
            for (n, (x0, y0, x1, y1), f) in specs]


def bbox(specs):
    """Overall (x0,y0,x1,y1) covering all room rects in a specs list."""
    xs0 = min(r[1][0] for r in specs); ys0 = min(r[1][1] for r in specs)
    xs1 = max(r[1][2] for r in specs); ys1 = max(r[1][3] for r in specs)
    return (xs0, ys0, xs1, ys1)


def row_house(ox=0, oy=0):
    """3 rooms in a horizontal bar."""
    specs = [
        ("bedroom", (0, 0, 9, 9),  bedroom_template),
        ("main",    (9, 0, 18, 9), living_template),
        ("kitchen", (18, 0, 27, 9), kitchen_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def t_house(ox=0, oy=0):
    """4 rooms: a bar of 3 with a crafting stem rising NORTH off the main room (the ⊥)."""
    specs = [
        ("bedroom",  (0, 0, 9, 9),   bedroom_template),
        ("main",     (9, 0, 20, 9),  living_template),
        ("kitchen",  (20, 0, 30, 9), kitchen_template),
        ("crafting", (11, 9, 19, 17), crafting_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def plus_house(ox=0, oy=0):
    """5 rooms: a bar of 3 with two stems rising NORTH (a study off main, a sunroom off kitchen)."""
    specs = [
        ("bedroom", (0, 0, 9, 9),    bedroom_template),
        ("main",    (9, 0, 20, 9),   living_template),
        ("kitchen", (20, 0, 30, 9),  kitchen_template),
        ("study",   (11, 9, 19, 17), bedroom_template),
        ("sunroom", (21, 9, 29, 17), living_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


# ---- NATURAL shapes (2026-06: "not squares — natural, and mostly square") -----
# Bars-of-rects still read boxy; these outlines are NON-CONVEX — wings attach with
# a perpendicular OFFSET so corners don't align (the offset is what makes an L/Z/U
# silhouette instead of a longer bar). All rectilinear (no diagonal wall art).

def l_house(ox=0, oy=0):
    """A true L: the main room with a kitchen east, and a bedroom wing rising NORTH
    off the main's WEST end only — the outline is an L, not a bar."""
    specs = [
        ("main",    (0, 0, 11, 9),   living_template),
        ("kitchen", (11, 0, 20, 9),  kitchen_template),
        ("bedroom", (0, 9, 9, 18),   bedroom_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def u_house(ox=0, oy=0):
    """A courtyard U (⊓ opening north): a wide south bar with two wings rising
    NORTH at its ENDS; the gap between the wings is a private COURTYARD — dress it
    (flower bed / birdbath) with `courtyard_rect(specs)`."""
    specs = [
        ("main",     (0, 0, 22, 8),   living_template),
        ("bedroom",  (0, 8, 9, 17),   bedroom_template),
        ("kitchen",  (13, 8, 22, 17), kitchen_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def courtyard_rect(specs):
    """The open court of a `u_house` specs list (the gap between the two north
    wings, INSIDE the bbox): returns (x0, y0, x1, y1) in the same coords."""
    ys = sorted({r[1][1] for r in specs})
    bar = next(r for r in specs if r[1][1] == ys[0])
    wings = sorted((r for r in specs if r[1][1] > ys[0]), key=lambda r: r[1][0])
    if len(wings) < 2:
        return None
    return (wings[0][1][2] + 1, bar[1][3] + 1, wings[1][1][0] - 1, wings[0][1][3])


def z_house(ox=0, oy=0):
    """A Z/S offset pair: two rooms sharing a vertical wall but OFFSET along it,
    plus a small annex shed off the back — three corners bitten out of the bbox."""
    specs = [
        ("main",    (0, 0, 11, 10),  living_template),
        ("kitchen", (11, 4, 21, 14), kitchen_template),
        ("annex",   (2, 10, 10, 18), crafting_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def sculpt_plan(ox=0, oy=0, *, seed=0, rooms=4):
    """GENERATIVE floor plans (the research recipe: core rect + grammar ops): start
    from a core room, then attach each new room to a random existing room on a
    random side with a random PERPENDICULAR OFFSET — offsets ≠ 0 make non-convex
    L/T/Z/U outlines naturally. Validity: every attachment shares a ≥5-cell wall
    line (so place_house punches a door), interiors never overlap, all rooms reach
    the core through shared walls (attachment guarantees it). The FRONT room is
    whichever has the longest south exterior. Returns (specs, front)."""
    rng = random.Random(seed)
    temps = [living_template, bedroom_template, kitchen_template, crafting_template,
             bedroom_template]
    names = ["main", "bedroom", "kitchen", "crafting", "study"]

    def dims():
        return rng.randint(9, 12), rng.randint(8, 11)

    w, h = dims()
    placed = [("main", (0, 0, w, h), temps[0])]

    def interiors_clash(rect):
        x0, y0, x1, y1 = rect
        for (_, (a0, b0, a1, b1), _) in placed:
            if x0 + 1 <= a1 - 1 and x1 - 1 >= a0 + 1 and y0 + 1 <= b1 - 1 and y1 - 1 >= b0 + 1:
                return True
            # corner-only touch (rects meeting at exactly one point) makes a weird
            # 4-way wall junction — reject (research: kills wall autotiling reads)
            if ((x0 == a1 or x1 == a0) and (y0 == b1 or y1 == b0)):
                return True
        return False

    for i in range(1, max(2, min(rooms, 5))):
        ok = False
        for _ in range(30):                     # try attachments until one fits
            host = placed[rng.randrange(len(placed))][1]
            hx0, hy0, hx1, hy1 = host
            side = rng.choice(("top", "bottom", "left", "right"))
            nw, nh = dims()
            if side in ("top", "bottom"):
                span = hx1 - hx0
                off = rng.randint(-(nw - 6), span - 6)   # ≥6-cell shared wall (door + jambs)
                x0 = hx0 + off
                rect = (x0, hy1, x0 + nw, hy1 + nh) if side == "top" \
                    else (x0, hy0 - nh, x0 + nw, hy0)
            else:
                span = hy1 - hy0
                off = rng.randint(-(nh - 6), span - 6)
                y0 = hy0 + off
                rect = (hx1, y0, hx1 + nw, y0 + nh) if side == "right" \
                    else (hx0 - nw, y0, hx0, y0 + nh)
            if not interiors_clash(rect):
                placed.append((names[i], rect, temps[i]))
                ok = True
                break
        if not ok:
            break

    # normalize to non-negative coords, then pick the front room: longest exterior
    # south (min-y) wall span.
    minx = min(r[1][0] for r in placed)
    miny = min(r[1][1] for r in placed)
    placed = [(n, (x0 - minx, y0 - miny, x1 - minx, y1 - miny), f)
              for (n, (x0, y0, x1, y1), f) in placed]
    south = min(r[1][1] for r in placed)
    front_room = max((r for r in placed if r[1][1] == south),
                     key=lambda r: r[1][2] - r[1][0])[0]
    return _shift(placed, ox, oy), (front_room, "top")


def porch(b, specs, *, depth=2):
    """A VERANDA outside the front door: a wood-floor apron `depth` deep along the
    front room's south wall, post (fence) at each outer corner, a bench beside the
    door. Zero new art; not reserved (walkable). Call AFTER place_house and AFTER
    property_yard (the apron overwrites the yard path under it)."""
    x0, y0, x1, y1 = bbox(specs)
    south = min(r[1][1] for r in specs)
    fr = max((r for r in specs if r[1][1] == south), key=lambda r: r[1][2] - r[1][0])
    fx0, fy0, fx1, _ = fr[1]
    px0, px1 = fx0 + 1, fx1 - 1
    for y in range(fy0 - depth, fy0):
        for x in range(px0, px1 + 1):
            if b.in_bounds(x, y) and not b.reserved[y][x]:
                b.set_ground(x, y, "wood_floor", surface="building")
    for px in (px0, px1):                       # corner posts
        if b.in_bounds(px, fy0 - depth) and b.is_free(px, fy0 - depth):
            b.place_occupant("fence_wood", px, fy0 - depth, surface=None)
    doorx = (fx0 + fx1) // 2
    if b.is_free(doorx + 2, fy0 - 1):
        b.place_occupant("bench", doorx + 2, fy0 - 1, reserve=False, surface=None)
