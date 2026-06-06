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
