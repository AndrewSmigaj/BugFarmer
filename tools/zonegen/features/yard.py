#!/usr/bin/env python3
"""Yard / enclosure primitives: a fenced rectangle (optional gate gap) and a full `yard`
(fence + gate + an approach path out of the gate + optional interior ground + exterior decor).
Everything goes through place_occupant / set_ground so reserved[]/surface[] stay coherent:
fences are hard occupants (so scatter routes around them) and the approach path claims
surface='path'."""


def fence_rect(b, x0, y0, x1, y1, gate=None, *, fence="fence_wood", gate_id="gate_wood"):
    """Perimeter fence around the rect; if `gate` (x,y) is given that cell becomes the gate.
    Returns the set of perimeter cells fenced."""
    cells = set()
    for x in range(x0, x1 + 1):
        cells.add((x, y0)); cells.add((x, y1))
    for y in range(y0, y1 + 1):
        cells.add((x0, y)); cells.add((x1, y))
    if gate:
        cells.discard(gate)
    for c in sorted(cells):
        b.place_occupant(fence, *c)
    if gate:
        b.place_occupant(gate_id, *gate)
    return cells


def yard(b, x0, y0, x1, y1, *, fence="fence_wood", gate=None, gate_id="gate_wood",
         ground=None, ground_surface="grass", path_to=None, path_tile="stone_path",
         decor=()):
    """A fenced yard. `ground` optionally fills the enclosed interior (e.g. 'dirt' for a pen).
    If `gate` and `path_to`=(x,y) are given, an L-shaped path is laid from the gate to that
    point (surface='path'). `decor` = [(oid, x, y), ...] exterior/interior dressings placed as
    occupants (planters, benches, lamp_post, hedge). Returns the rect."""
    if ground:
        b.fill_ground(x0 + 1, y0 + 1, x1 - 1, y1 - 1, ground, surface=ground_surface)
    fence_rect(b, x0, y0, x1, y1, gate=gate, fence=fence, gate_id=gate_id)
    if gate and path_to:
        gx, gy = gate
        tx, ty = path_to
        sy = 1 if ty >= gy else -1
        for y in range(gy, ty + sy, sy):
            if b.in_bounds(gx, y):
                b.set_ground(gx, y, path_tile, surface="path")
        sx = 1 if tx >= gx else -1
        for x in range(gx, tx + sx, sx):
            if b.in_bounds(x, ty):
                b.set_ground(x, ty, path_tile, surface="path")
    for (oid, dx, dy) in decor:
        b.place_occupant(oid, dx, dy, surface="grass")
    return (x0, y0, x1, y1)


def property_yard(b, bx0, by0, bx1, by1, door_x, *, side=2, front=5, back=4,
                  fence="fence_picket", gate_id="gate_picket", tree="tree_oak",
                  flowers=("flower_red", "flower_blue", "flower_yellow", "poppy", "lavender"), seed=0):
    """Fence a sensible yard around a BUILDING whose footprint is (bx0,by0)=SW .. (bx1,by1)=NE
    (by0 = the SOUTH/front wall with the door, by1 = the NORTH/back wall). Leaves `side` cells of
    side-yard on each side, a `front`-deep front garden (south) and a `back`-deep BACKYARD (north) —
    the fence never hugs the house walls. Gate sits on the south fence aligned with `door_x`; a stone
    path runs gate->door. Drops `tree`s in the back row + side yards and `flowers` beds either side of
    the path. Place this AFTER stamping the building. Returns the fence rect (fx0, fy0, fx1, fy1)."""
    fx0, fy0, fx1, fy1 = bx0 - side, by0 - front, bx1 + side, by1 + back
    fence_rect(b, fx0, fy0, fx1, fy1, gate=(door_x, fy0), fence=fence, gate_id=gate_id)
    for y in range(fy0 + 1, by0):                        # path: gate -> front door
        if b.is_free(door_x, y):
            b.set_ground(door_x, y, "stone_path", surface="path")

    def _put(oid, x, y):
        fw, fh = b.footprint(oid)
        if all(b.in_bounds(x + dx, y + dy) and b.is_free(x + dx, y + dy)
               for dx in range(fw) for dy in range(fh)):
            return b.place_occupant(oid, x, y)
        return False

    if tree:                                             # a couple of trees in the BACK corners only
        for (tx, ty) in [(fx0 + 1, fy1 - 1), (fx1 - 1, fy1 - 1)]:
            _put(tree, tx, ty)
    if flowers:                                          # front-garden flower beds either side of the path
        from features.garden import flower_patch
        if door_x - 2 >= fx0 + 1:
            flower_patch(b, fx0 + 1, fy0 + 1, door_x - 2, by0 - 1, list(flowers), 8, seed=seed)
        if fx1 - 1 >= door_x + 2:
            flower_patch(b, door_x + 2, fy0 + 1, fx1 - 1, by0 - 1, list(flowers), 8, seed=seed + 3)
    return (fx0, fy0, fx1, fy1)
