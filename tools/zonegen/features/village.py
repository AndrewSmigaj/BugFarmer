#!/usr/bin/env python3
"""Village/town composites — building-scale features too useful to keep scene-local.

A SHOP is a building shell + a wide shopfront sign + interior shelving rows + a counter with a
shopkeeper behind it. A PLAZA is a paved civic square with a centerpiece, ringed by seating + lamps.
Both coordinate through the builder's occupancy model and reuse the room/house/garden primitives.

Coordinate note (matches place_room + the renderer): low y = SOUTH = camera-near = "front";
high y = NORTH = back. `place_room` door_side "top"=south(front) wall, "bottom"=north(back) wall;
`wall_run` side "bottom"=north(back) wall (where front-facing furniture belongs, per the facing rule).
"""
from .room import place_room
from .house import wall_run
from .garden import flower_patch

PLAZA_FLOWERS = ["flower_red", "flower_yellow", "flower_blue", "poppy", "lavender"]


def shop_building(b, x0, y0, x1, y1, *, sign_id, npc=None, npc_dir="down",
                  door_side="top", wall="wall_stone", floor="wood_floor",
                  shelf_id="shop_shelving", shelf_rows=2, counter_id="counter",
                  extra_fill=None):
    """A shop: a building shell (door on `door_side`) with a wide shopfront SIGN centered on the
    south frontage, rows of SHELVING against the back/side walls (facing rule), a COUNTER across
    the middle, and the shopkeeper NPC behind it facing the customer. `extra_fill(b, I)` adds
    shop-specific props. Returns the interior rect (ix0,iy0,ix1,iy1) or None if too small."""
    I = place_room(b, x0, y0, x1, y1, floor=floor, wall=wall, door="door_square", door_side=door_side)
    if not I:
        return None
    ix0, iy0, ix1, iy1 = I

    # 1) wide shopfront sign — centered on the SOUTH frontage, just outside the wall (faces camera).
    cx = (x0 + x1) // 2
    sw = b.footprint(sign_id)[0]
    b.place_occupant(sign_id, cx - sw // 2, y0 - 1, reserve=False)

    # 2) shelving rows against the BACK (north) wall + one side wall — stocked goods read front-on.
    wall_run(b, [shelf_id] * (ix1 - ix0 + 1), side="bottom", I=I)
    if shelf_rows >= 2 and (iy1 - iy0) >= 3:
        wall_run(b, [shelf_id] * (iy1 - iy0 - 1), side="left", I=(ix0, iy0, ix1, iy1 - 1), start=0)

    # 3) counter across the middle with the shopkeeper behind it (one row north, facing down/south).
    # A workshop (no storefront) passes counter_id=None to skip the counter + NPC.
    if counter_id:
        midy = (iy0 + iy1) // 2
        cfw = b.footprint(counter_id)[0]
        ncount = max(1, (ix1 - ix0 - 1) // cfw)
        wall_run(b, [counter_id] * ncount, side="top", I=(ix0 + 1, midy, ix1 - 1, midy))
        if npc:
            b.place_player(f"{npc}_{npc_dir}", (ix0 + ix1) / 2.0, midy + 1)

    if extra_fill:
        extra_fill(b, I)

    # RESERVE the interior — a finished shop is solid; later passes (roads,
    # scatter) must never paint or place inside it (see place_house step 7).
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            if b.in_bounds(x, y) and not b.reserved[y][x]:
                b.reserved[y][x] = True
    return I


def plaza(b, cx, cy, *, r=4, tile="stone_path", fountain_id="fountain",
          bench_id="bench", lamp_id="lamp_post", statue_id="statue_founder",
          flowers=True, flower_kinds=None, seed=0):
    """A civic square centered at (cx,cy): pave an (2r+1)-square (surface='path'), drop
    a centerpiece (fountain, 2x2) dead-center, FOUR benches in facing pairs, lamp posts
    at the corners, the CIVIC PROPS the intent doc requires — notice_board (SE, the
    village's message hub) + signpost (NW, the wayfinding anchor) + a founder statue
    (NE) — and flower beds in two corners. (These props existed only in
    scene_village's local square() before; composing a core without them shipped a
    poorer civic heart than the blit it replaced.) Returns the paved rect."""
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    b.fill_ground(x0, y0, x1, y1, tile, surface="path")

    def _put(oid, x, y, **kw):                              # place only on free footprint cells
        fw, fh = b.footprint(oid)
        if all(b.is_free(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
            return b.place_occupant(oid, x, y, **kw)
        return False

    # Plaza furniture is DELIBERATELY on the paving: surface=None keeps the cells
    # classified "path" (truthful mask, and no building-over-road warn).
    # centerpiece (2x2) centered on (cx,cy)
    _put(fountain_id, cx - 1, cy - 1, surface=None)
    # benches in facing pairs flanking the fountain (south + north rows)
    for by in (y0 + 1, y1 - 1):
        _put(bench_id, cx - 3, by, reserve=False, surface=None)
        _put(bench_id, cx + 1, by, reserve=False, surface=None)
    # lamp posts at the four corners
    for (lx, ly) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        _put(lamp_id, lx, ly, reserve=False, surface=None)
    # civic props: board SE, signpost NW (one cell in from the corners' lamps),
    # statue NE — all just inside the paving so they read as part of the square
    _put("notice_board", x1 - 1, y0 + 1, surface=None)
    _put("signpost", x0 + 1, y1 - 1, surface=None)
    if statue_id:
        _put(statue_id, x1 - 2, y1 - 2, surface=None)

    # corner flower beds (sub-grid free-floating, off the paving onto the SW/NE grass corners)
    if flowers:
        kinds = flower_kinds or PLAZA_FLOWERS
        flower_patch(b, x0 - 2, y0 - 2, x0, y0, kinds, n=5, seed=seed)
        flower_patch(b, x1, y1, x1 + 2, y1 + 2, kinds, n=5, seed=seed + 1)
    return (x0, y0, x1, y1)


def shop_frontage(b, ox, oy, *, sign_id, sign_x=1, items=()):
    """THE shared shop frontage (2026-06 consistency rule): the sign by the door +
    the goods DISPLAY LINE — one straight row, never sprinkled. `items` =
    [(oid, dx, dy), ...] relative to (ox, oy); keep dy in {-1, -2, -3} (the
    frontage strip) and dx ascending (a line)."""
    fw, fh = b.footprint(sign_id)
    if all(b.is_free(ox + sign_x + dx, oy - 1 + dy) for dx in range(fw) for dy in range(fh)):
        b.place_occupant(sign_id, ox + sign_x, oy - 1, surface="grass")
    for (oid, dx, dy) in items:
        fw, fh = b.footprint(oid)
        if all(b.is_free(ox + dx + ddx, oy + dy + ddy) for ddx in range(fw) for ddy in range(fh)):
            b.place_occupant(oid, ox + dx, oy + dy, surface="grass")
