#!/usr/bin/env python3
"""Room / building-shell feature primitive.

place_room draws an enclosed rectangular building shell: a floor interior + a wall
border with a door gap, reserving the walls (they block) but leaving the interior
walkable so furniture can go inside. Returns the interior rect (x0,y0,x1,y1) for
placing furniture. Coordinates are inclusive outer-wall bounds.
"""


def place_room(b, x0, y0, x1, y1, *, floor="wood_floor", wall="wall_wood",
               door="door_wood", door_side="bottom", door_offset=None):
    if x1 - x0 < 2 or y1 - y0 < 2:
        b.warn(f"room {x0,y0,x1,y1} too small")
        return None

    # Interior floor (walkable; surface=building so scatter etc. avoid it).
    b.fill_ground(x0 + 1, y0 + 1, x1 - 1, y1 - 1, floor, surface="building")

    # Door gap (door footprint width along a horizontal wall).
    door_cells, door_anchor = set(), None
    if door:
        if door_side in ("top", "bottom"):
            wy = y0 if door_side == "top" else y1
            dfw = b.footprint(door)[0]
            dx = door_offset if door_offset is not None else (x0 + x1) // 2 - dfw // 2
            door_cells = {(dx + i, wy) for i in range(dfw)}
            door_anchor = (dx, wy)
        else:  # left / right (single-cell gap)
            wx = x0 if door_side == "left" else x1
            dy = door_offset if door_offset is not None else (y0 + y1) // 2
            door_cells = {(wx, dy)}
            door_anchor = (wx, dy)

    # Wall border, minus the door gap.
    for x in range(x0, x1 + 1):
        for y in (y0, y1):
            if (x, y) not in door_cells:
                b.place_occupant(wall, x, y)
    for y in range(y0 + 1, y1):
        for x in (x0, x1):
            if (x, y) not in door_cells:
                b.place_occupant(wall, x, y)

    if door and door_anchor:
        b.place_occupant(door, *door_anchor)

    return (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
