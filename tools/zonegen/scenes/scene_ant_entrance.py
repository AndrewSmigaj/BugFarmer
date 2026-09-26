#!/usr/bin/env python3
"""Scene — THE MYRMECOLOGY STATION (ant_tunnels_30's main entrance; owner overhaul 2026-07-07).

A field-research station obsessed with the colony below. Owner corrections applied: the tunnel
MOUTH is a single CLEAN natural throat (not stiff rectangular shafts); the building sits clearly
to the WEST of the mouth with a gap (never over it); the mouth + compound are cleared of trees.

ORIENTATION: HIGH y = NORTH = top. The MOUTH opens SOUTH (down, toward the colony); the dirt ROAD
arrives from the NORTH; the building sits on the surface to the WEST.

Composition contract (so it drops into the zone without messing it up):
  `place_ant_entrance(b, mx, my)` places ONLY the SURFACE compound around a mouth whose opening is
  at (mx, my) — it does NOT carve the tunnel (the ZONE owns the tunnel network). It clears a
  clearing first, so trees never end up in the throat. The standalone `build()` carves one clean
  natural tunnel itself so the preview shows the entrance.
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.terrain import _vnoise                                 # noqa: E402
from features.cave import carve_tunnel                               # noqa: E402

PREVIEW = "zones/ant_tunnels_30/scenes"
SCALE = 5


def _occ(b, oid, x, y):
    if b.in_bounds(x, y) and b.is_free(x, y):
        try:
            return b.place_occupant(oid, x, y) or True
        except Exception:
            return False
    return False


def _clear_surface(b, x0, y0, x1, y1):
    """Remove surface vegetation (trees/scrub) in a rect — keeps blocks/ore and building cells."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not b.in_bounds(x, y):
                continue
            c = b.occ.get((x, y))
            if not c:
                continue
            cid = c.get("id", "")
            if cid in ("dirt_block", "stone_block") or "ore_" in cid:
                continue                                  # keep terrain blocks; clear trees/scrub
            del b.occ[(x, y)]
            b.reserved[y][x] = False


def _room(b, x0, y0, x1, y1, door_side="e"):
    """Wood-walled room + floor; a 1-wide door on door_side. Returns interior rect."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.set_ground(x, y, "wood_floor", surface="building")
            if x in (x0, x1) or y in (y0, y1):
                _occ(b, "wall_wood", x, y)
    dcx, dcy = {"e": (x1, (y0 + y1) // 2), "w": (x0, (y0 + y1) // 2),
                "s": ((x0 + x1) // 2, y0), "n": ((x0 + x1) // 2, y1)}[door_side]
    b.occ.pop((dcx, dcy), None)
    b.reserved[dcy][dcx] = False
    b.set_ground(dcx, dcy, "wood_floor", surface="building")
    _occ(b, "door_square", dcx, dcy)
    return (x0 + 1, y0 + 1, x1 - 1, y1 - 1)


def place_ant_entrance(b, mx, my):
    """Surface compound around the MOUTH at (mx, my). Building sits WEST; the caller carves the
    tunnel descending SOUTH from (mx, my)."""
    # 1. CLEARING — no trees in the mouth or the compound (owner: trees were in the throat)
    _clear_surface(b, mx - 34, my - 3, mx + 6, my + 22)

    # 2. dirt-block MOUND LIPS hugging the mouth's shoulders (a natural low rim, not a box)
    for lx, ly in [(mx - 3, my + 1), (mx + 3, my + 1), (mx - 4, my + 2),
                   (mx + 4, my + 2), (mx - 2, my), (mx + 2, my)]:
        _occ(b, "dirt_block", lx, ly)

    # 3. THE BUILDING — clearly WEST of the mouth (a ~10-cell gap), on the surface.
    bx1, by0 = mx - 10, my + 4
    bx0, by1 = bx1 - 14, by0 + 9
    for yy in range(by0, by1 + 1):                      # force-clear the footprint (any stray tree)
        for xx in range(bx0, bx1 + 1):
            if b.in_bounds(xx, yy) and b.occ.get((xx, yy)) is not None:
                del b.occ[(xx, yy)]
                b.reserved[yy][xx] = False
    ix0, iy0, ix1, iy1 = _room(b, bx0, by0, bx1, by1, door_side="e")   # door faces the mouth
    fcx = (ix0 + ix1) // 2
    # north display wall (iy1): terrarium · chart · FORMICARIUM · chart · books
    _occ(b, "bug_terrarium_big", ix0, iy1)
    _occ(b, "ant_chart", ix0 + 3, iy1)
    _occ(b, "formicarium", fcx, iy1)
    _occ(b, "ant_chart", ix1 - 2, iy1)
    _occ(b, "bookshelf", ix1 - 1, iy1)
    # trail-study table + chair, centre
    _occ(b, "map_table_big", ix0 + 5, iy0 + 2)
    _occ(b, "chair_wood", ix0 + 7, iy0 + 2)
    # researcher corner: cot SW, desk NE, specimens, lantern
    _occ(b, "cot", ix0, iy0)
    _occ(b, "desk", ix1 - 2, iy0)
    _occ(b, "specimen_case", ix0, iy0 + 3)
    _occ(b, "specimen_case", ix0 + 3, iy0 + 3)
    _occ(b, "lantern", ix0 + 9, iy0)

    # 4. THE ANT SIGN at the door/road head; the PEN north of the building.
    _occ(b, "sign_ant", bx1 + 1, by1 + 1)
    px0, py0 = bx0 + 1, by1 + 2
    px1, py1 = px0 + 8, py0 + 6
    for x in range(px0, px1 + 1):
        for y in (py0, py1):
            _occ(b, "gate_wood" if (x == px0 + 4 and y == py0) else "fence_wood", x, y)
    for y in range(py0 + 1, py1):
        for x in (px0, px1):
            _occ(b, "fence_wood", x, y)
    _occ(b, "dirt_block", px0 + 3, py0 + 2)             # the ant-farm-in-progress (empty pen tease)
    _occ(b, "dirt_block", px0 + 4, py0 + 2)
    _occ(b, "signpost", px0 + 2, py0 + 3)

    # 5. OBSERVATION POST in the gap between the building and the mouth (he watches the trails).
    _occ(b, "stool_wood", mx - 6, my + 3)
    _occ(b, "easel", mx - 7, my + 4)
    _occ(b, "crate", mx - 6, my + 5)
    _occ(b, "lantern", mx - 4, my + 2)
    for bxx, byy in [(mx - 4, my + 6), (mx - 7, my + 9), (mx - 3, my + 12)]:
        _occ(b, "bait_station", bxx, byy)               # bait staked along the trail up from the mouth

    # 6. FIELD CAMP west of the building + specimen gear.
    _occ(b, "campfire", bx0 - 3, by0 + 2)
    _occ(b, "crate", bx0 - 3, by0 + 3)
    _occ(b, "net_post", bx0 - 2, by0 + 5)
    _occ(b, "net_pile", bx1 + 2, by0 + 1)

    # 7. fungus + windfalls at the shaded mouth (the ants' food).
    _occ(b, "mushroom_inkcap", mx - 5, my - 1)
    _occ(b, "mushroom_morel", mx + 5, my - 2)
    _occ(b, "tree_apple", bx0 - 4, by1)

    # 8. a short worn spur from the door across to the mouth.
    for x in range(bx1 + 1, mx):
        if b.in_bounds(x, by0 + 4) and b.is_free(x, by0 + 4) and b.surface[by0 + 4][x] == "grass":
            b.set_ground(x, by0 + 4, "mud", surface="path")
    return (mx, my)


def build():
    """Standalone vignette: fake terrain + carve ONE clean natural tunnel, then the compound."""
    W, H = 56, 46
    b = ZoneBuilder("scene_myrmecology_station", W, H, base_tile="dirt",
                    name="Myrmecology Station", biome="dirt")
    ng = _vnoise(47)
    MY = 24                                              # surface/underground boundary
    for y in range(H):
        for x in range(W):
            if y <= MY:                                 # underground dirt body
                b.set_ground(x, y, "dirt", surface="grass")
                b.place_occupant("dirt_block", x, y)
            elif ng(0.16 * x, 0.16 * y) > 0.6:
                b.set_ground(x, y, "grass")
    MX = 36
    # ONE clean natural tunnel descending SOUTH from the mouth (carve = remove blocks, dirt floor)
    for (cx, cy) in carve_tunnel(b, (MX, MY), (MX - 3, 2), width=3, seed=7, wobble=0.55):
        if b.occ.get((cx, cy)):
            del b.occ[(cx, cy)]
            b.reserved[cy][cx] = False
        b.set_ground(cx, cy, "dirt", surface="grass")
    # preview-only worker file up out of the mouth
    for i in range(9):
        t = i / 8.0
        b.place_bug("ant_worker", MX - 1 - t * 3, MY - 2 - t * 16, scale=2.2)
    place_ant_entrance(b, MX, MY)
    b.spawn = [12, 42]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
