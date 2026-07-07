#!/usr/bin/env python3
"""Scene — THE ANT ENTRANCE (ant_tunnels_30's human doorstep; owner spec 2026-07-07):
"the main [tunnel] has the building and the dirt road, with a pen that is empty, and
stuff inside like the ecologist's but ant oriented... wooden wall building on the dirt
(as it has transitioned from grass by this time)."

The vignette: the rock CLIFF FACE runs the east side on a natural curve (stone blocks —
never a ruled line); the MAIN tunnel mouth opens at its foot between two dirt-block
mound forms; the Myrmecologist's wooden STATION sits on the bare dirt beside it, the
dirt ROAD arriving from the north; the EMPTY PEN waits beside the building (its game
reason arrives with ant husbandry); two smaller side-mouths pierce the cliff further
south; real mushrooms (inkcap/morel) grow at the shaded cliff base; a fruit tree on the
west drops the windfalls the first trails will find. Worker-file dressing is preview-
only — live trails come from the sim.

`place_ant_entrance(b, ox, oy)` is the composable piece for the zone build.
Renders to tools/_generated/previews/zones/ant_tunnels_30/scenes/ant_entrance.png.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.tilemap import stamp                                    # noqa: E402
from features.terrain import _vnoise                                  # noqa: E402

# The Myrmecologist's STATION: one wooden room, door WEST onto the road. Ant-oriented
# working interior (the ecologist pattern): cot, work table + chair, specimen shelf +
# case, terrarium, bookshelf, lantern, supply crates. No trade board (owner: objects
# need game reasons).
STATION = """
WWWWWWWWWWW
W...k.j...W
Wu........D
W.......eeW
W...T..a..W
W.q.....X.W
WWWWWWWWWWW
"""
STATION_LEG = {
    "W": ("occ", "wall_wood"), "D": ("occ", "door_square"), ".": ("floor",),
    "u": ("occ", "cot"),                # 2x2, foot anchor row handled by grid position
    "k": ("occ", "bookshelf"),          # 2x1
    "j": ("occ", "specimen_shelf"),     # 2x1
    "T": ("occ", "table_wood"),         # 2x2 (anchor = foot row)
    "a": ("occ", "chair_wood"),
    "e": ("occ", "bug_terrarium"),
    "q": ("occ", "specimen_case"),
    "X": ("occ", "crate"),
}

PREVIEW = "zones/ant_tunnels_30/scenes"
SCALE = 5


def place_ant_entrance(b, ox, oy):
    """The entrance compound (SW anchor ox,oy; ~46 wide × 40 tall). The caller supplies
    the dirt ground; this piece adds the cliff, mouths, station, road stub, and pen."""
    n = _vnoise(41)

    # THE CLIFF FACE (east side): a noise-warped edge — stone fills east of the line.
    # The curve bows westward toward the bottom (the "down and then across" read).
    for y in range(oy, oy + 40):
        t = (y - oy) / 40.0
        edge = ox + 34 - 6.0 * (1 - t) + (n(0.13 * y, 0.0) - 0.5) * 5.0
        for x in range(int(edge), ox + 46):
            if not b.in_bounds(x, y) or not b.is_free(x, y):
                continue
            b.set_ground(x, y, "stone_floor")
            b.place_occupant("stone_block", x, y)

    def carve_mouth(mx, my, depth, width=2):
        """Open a dark throat INTO the cliff: clear blocks, lay cave_floor."""
        for d in range(depth):
            for w in range(width):
                x, y = mx + d, my + w
                if not b.in_bounds(x, y):
                    continue
                c = b.occ.get((x, y))
                if c and c.get("id") == "stone_block":
                    del b.occ[(x, y)]
                    b.reserved[y][x] = False
                    b.surface[y][x] = "grass"
                b.set_ground(x, y, "cave_floor")

    # THE MAIN MOUTH (mid-cliff) flanked by dirt-block mound FORMS (blocks, per owner —
    # never mound objects), plus two smaller side-mouths south of it.
    main_y = oy + 22
    main_x = int(ox + 34 - 6.0 * (1 - 22 / 40.0) + (n(0.13 * main_y, 0.0) - 0.5) * 5.0)
    carve_mouth(main_x, main_y, depth=10, width=3)
    for px, py in [(main_x - 1, main_y + 3), (main_x - 2, main_y + 4),
                   (main_x - 1, main_y - 2), (main_x - 2, main_y - 3)]:
        if b.in_bounds(px, py) and b.is_free(px, py) and b.surface[py][px] == "grass":
            b.place_occupant("dirt_block", px, py)
    for sy, depth in [(oy + 8, 6), (oy + 33, 5)]:
        sx = int(ox + 34 - 6.0 * (1 - (sy - oy) / 40.0) + (n(0.13 * sy, 0.0) - 0.5) * 5.0)
        carve_mouth(sx, sy, depth, width=2)

    # THE STATION on the bare dirt west of the main mouth, door to the road.
    bx, by = ox + 8, main_y - 3
    stamp(b, STATION, STATION_LEG, ox=bx, oy=by)
    if b.is_free(bx + 11, by + 5):
        b.place_occupant("lantern", bx + 11, by + 5)  # by the east door, dusk-lit

    # THE DIRT ROAD: from the north edge down to the station door, then a worn spur to
    # the mouth. Ground-paint on free dirt (the ground here is already dirt).
    rng_r = __import__("random").Random(43)
    ry, rx = oy + 39, bx + 13
    while ry > by + 3:
        for cell in ((rx, ry), (rx + 1, ry)):
            x, y = cell
            if b.in_bounds(x, y) and b.is_free(x, y) and b.surface[y][x] == "grass":
                b.set_ground(x, y, "mud", surface="path")
        ry -= 1
        rx += rng_r.choice((-1, 0, 0, 1))
        rx = max(bx + 12, min(bx + 16, rx))
    for x in range(bx + 11, main_x):
        y = main_y + 1
        if b.in_bounds(x, y) and b.is_free(x, y) and b.surface[y][x] == "grass" \
           and b.ground[y][x] != "cave_floor":
            b.set_ground(x, y, "mud", surface="path")

    # THE EMPTY PEN south of the station (owner: "a pen that is empty" — its game
    # reason arrives with ant husbandry; the emptiness is the tease).
    px0, py0, px1, py1 = bx, by - 9, bx + 8, by - 2
    for x in range(px0, px1 + 1):
        for y in (py0, py1):
            if b.in_bounds(x, y) and b.is_free(x, y) and b.surface[y][x] == "grass":
                b.place_occupant("gate_wood" if (x == px0 + 4 and y == py1) else "fence_wood", x, y)
    for y in range(py0 + 1, py1):
        for x in (px0, px1):
            if b.in_bounds(x, y) and b.is_free(x, y) and b.surface[y][x] == "grass":
                b.place_occupant("fence_wood", x, y)

    # REAL mushrooms in the cliff's shade; the fruit tree + windfall ground west.
    for mx, my, mid in [(main_x - 3, main_y + 6, "mushroom_inkcap"),
                        (main_x - 5, main_y - 5, "mushroom_morel"),
                        (main_x - 2, main_y - 7, "mushroom_inkcap")]:
        if b.in_bounds(mx, my) and b.is_free(mx, my) and b.surface[my][mx] == "grass":
            b.place_occupant(mid, mx, my)
    if b.is_free(ox + 3, oy + 12):
        b.place_occupant("tree_apple", ox + 3, oy + 12)

    # PREVIEW-ONLY dressing: a worker file from the mouth toward the tree (the live
    # trail is the sim's job; this is what the vignette promises).
    for i in range(7):
        t = i / 6.0
        fx = main_x - 2 - t * (main_x - 2 - (ox + 4))
        fy = main_y + 1 - t * (main_y - oy - 13)
        b.place_bug("ant_worker", fx, fy, scale=2.2)
    return (bx, by)


def build():
    b = ZoneBuilder("scene_ant_entrance", 50, 42, base_tile="dirt",
                    name="The Ant Entrance", biome="dirt")
    # "As it has transitioned from grass by this time" — transitioned, not erased:
    # grass REMNANT patches survive on the open ground (and give the dirt road its
    # contrast). The zone build supplies its own transitioned ground; this is the
    # scene-local equivalent.
    ng = _vnoise(47)
    for y in range(42):
        for x in range(38):
            if ng(0.16 * x, 0.16 * y) > 0.63:
                b.set_ground(x, y, "grass")
    place_ant_entrance(b, 2, 1)
    # Scrub the open ground lightly — dry country, not a void.
    rng_s = __import__("random").Random(48)
    for _ in range(26):
        x, y = rng_s.randrange(2, 34), rng_s.randrange(2, 40)
        if b.is_free(x, y) and b.surface[y][x] == "grass" and b.ground[y][x] in ("dirt", "grass"):
            b.place_occupant(rng_s.choice(["tall_grass", "dead_bush", "tall_grass", "mushroom_inkcap"]), x, y)
    b.spawn = [12, 38]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
