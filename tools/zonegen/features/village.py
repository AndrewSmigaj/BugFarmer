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
    I = place_room(b, x0, y0, x1, y1, floor=floor, wall=wall, door="door_wood", door_side=door_side)
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
    return I


def plaza(b, cx, cy, *, r=4, tile="stone_path", fountain_id="fountain",
          bench_id="bench", lamp_id="lamp_post", flowers=True, flower_kinds=None, seed=0):
    """A civic square centered at (cx,cy): pave an (2r+1)-square (surface='path'), drop a centerpiece
    (fountain, 2x2) dead-center, ring it with benches at the N/S edges + lamp posts at the corners,
    and tuck flower beds in two corners. Returns the paved rect."""
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    b.fill_ground(x0, y0, x1, y1, tile, surface="path")

    def _put(oid, x, y, **kw):                              # place only on free footprint cells
        fw, fh = b.footprint(oid)
        if all(b.is_free(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
            return b.place_occupant(oid, x, y, **kw)
        return False

    # centerpiece (2x2) centered on (cx,cy)
    _put(fountain_id, cx - 1, cy - 1)
    # benches at the south & north edges (2-wide, just inside the paving), facing the fountain
    for by in (y0 + 1, y1 - 1):
        _put(bench_id, cx - 1, by, reserve=False)
    # lamp posts at the four corners
    for (lx, ly) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        _put(lamp_id, lx, ly, reserve=False)

    # corner flower beds (sub-grid free-floating, off the paving onto the SW/NE grass corners)
    if flowers:
        kinds = flower_kinds or PLAZA_FLOWERS
        flower_patch(b, x0 - 2, y0 - 2, x0, y0, kinds, n=5, seed=seed)
        flower_patch(b, x1, y1, x1 + 2, y1 + 2, kinds, n=5, seed=seed + 1)
    return (x0, y0, x1, y1)
