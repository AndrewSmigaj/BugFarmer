#!/usr/bin/env python3
"""Author a building/area from a TEXT GRID, and dump any region back to text.

Designing in a character grid is reliable: the door, walls and furniture are visible and reasonable
in text (door has a clear floor cell in front; shelves are NOT on the door wall; one wall ring, not
two) BEFORE it becomes pixels. The FIRST text line is the NORTH (top/back) of the piece; the LAST line
is the SOUTH (front, camera-near) where the entrance usually is.

  stamp(b, grid, legend, ox, oy): place the grid. legend maps each non-space char to a spec:
     ('occ', id)            place an occupant (a building floor is laid under it)
     ('npc', sprite_id)     a render-only character standing on a floor cell
     ('decor', id[, scale]) free-floating ground decor
     ('floor',)             just a walkable building floor cell
     ('ground', tile[, surface])  set the ground tile only (no floor default)
   a space ' ' leaves the cell untouched (outside the piece).

  dump(b, x0,y0,x1,y1): return the region as a char grid (north on top) for eyeball-free verification.
"""


def stamp(b, grid, legend, ox=0, oy=0, floor="wood_floor"):
    rows = grid.split("\n")
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    R = len(rows)
    for r, line in enumerate(rows):
        y = oy + (R - 1 - r)                       # first text line = NORTH (high y)
        for c, ch in enumerate(line):
            if ch == " ":
                continue                           # outside the piece
            spec = legend.get(ch)
            if not spec:
                continue
            x, kind = ox + c, spec[0]
            if kind == "ground":
                b.set_ground(x, y, spec[1], surface=(spec[2] if len(spec) > 2 else None))
                continue
            b.set_ground(x, y, floor, surface="building")   # everything else stands on a floor
            if kind == "occ":
                b.place_occupant(spec[1], x, y)
            elif kind == "npc":
                b.place_player(spec[1], float(x), float(y))
            elif kind == "decor":
                b.place_decor(spec[1], float(x), float(y), spec[2] if len(spec) > 2 else 1.0)


def dump(b, x0, y0, x1, y1):
    """North (y1) on top → South (y0) on bottom. D=door/gate, W=wall, #=fence, lowercase initial of any
    other occupant, x=reserved-no-occupant, .=building floor, (space)=open ground."""
    lines = []
    for y in range(y1, y0 - 1, -1):
        s = ""
        for x in range(x0, x1 + 1):
            c = b.occ.get((x, y))
            if c:
                i = c["id"]
                s += ("D" if i.startswith(("door", "gate")) else
                      "W" if i.startswith("wall") else
                      "#" if i.startswith("fence") else i[0].lower())
            elif b.in_bounds(x, y) and b.reserved[y][x]:
                s += "x"
            elif b.in_bounds(x, y) and b.surface[y][x] == "building":
                s += "."
            else:
                s += " "
        lines.append(f"{y:3d} {s}")
    return "\n".join(lines)
