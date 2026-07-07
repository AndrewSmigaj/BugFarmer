#!/usr/bin/env python3
"""Scene — THE MYRMECOLOGY STATION (ant_tunnels_30's main entrance; owner overhaul 2026-07-07).

Owner: the old scene was a bare cabin — "it needs to SCREAM ants (a sign), tunnels open to the
SOUTH into DIRT, an actual myrmecologist camp, not the bare minimum." This is a FIELD-RESEARCH
STATION obsessed with the colony below: everything faces the mouth.

ORIENTATION: HIGH y = NORTH = top. The main tunnel MOUTH opens to the SOUTH (down, toward the
colony); the dirt ROAD arrives from the NORTH. The building sits on the surface between them.

Composable piece: `place_ant_entrance(b, ox, oy)` — lays the station, road, pen, sign, the
observation post and the south-opening mouths onto whatever terrain the caller provides (the
zone supplies the dirt surface + the dirt-block underground; standalone build() fakes a context).

Passes (this file grows): P1 structure+identity · P2 the field-study character · P3 lived-in
richness + ant motifs. Renders under previews/zones/ant_tunnels_30/scenes/.
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.terrain import _vnoise                                 # noqa: E402

PREVIEW = "zones/ant_tunnels_30/scenes"
SCALE = 5


def _occ(b, oid, x, y):
    """Place if the anchor + footprint are free; return success (keeps the scene lint-clean)."""
    if b.in_bounds(x, y) and b.is_free(x, y):
        try:
            b.place_occupant(oid, x, y)
            return True
        except Exception:
            return False
    return False


def _floor_room(b, x0, y0, x1, y1):
    """Wood-walled room shell with a wood floor; returns the interior rect (inclusive)."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.set_ground(x, y, "wood_floor", surface="building")
            if x in (x0, x1) or y in (y0, y1):
                _occ(b, "wall_wood", x, y)
    return (x0 + 1, y0 + 1, x1 - 1, y1 - 1)


def place_ant_entrance(b, ox, oy):
    """The Myrmecology Station compound. (ox,oy) = SW anchor; ~46 wide x 44 tall.
    South (low y) = the mouths into dirt; north (high y) = the road in."""
    mouth_y = oy + 6            # the main mouth throat sits low (south)
    bldg_y0 = oy + 16          # building south wall
    road_y = oy + 43           # road enters from the north edge

    # ============ THE MAIN MOUTH — opens SOUTH into the dirt (dark descending shaft) =======
    def carve_mouth(mx, top_y, width, depth):
        """Dark throat descending SOUTH (decreasing y) from an opening at top_y; flared lip."""
        for d in range(depth):
            flare = 1 if d < 2 else 0
            for w in range(-(width // 2) - flare, width // 2 + 1 + flare):
                x, y = mx + w, top_y - d
                if not b.in_bounds(x, y):
                    continue
                c = b.occ.get((x, y))
                if c and c.get("id") in ("dirt_block", "stone_block"):
                    del b.occ[(x, y)]
                    b.reserved[y][x] = False
                    b.surface[y][x] = "grass"
                b.set_ground(x, y, "cave_floor")
    main_mx = ox + 22
    carve_mouth(main_mx, bldg_y0 - 2, width=4, depth=14)
    carve_mouth(ox + 8, bldg_y0 - 4, width=2, depth=9)
    carve_mouth(ox + 37, bldg_y0 - 3, width=2, depth=10)
    # dirt-block MOUND LIPS framing the main mouth (owner: mounds are made OF dirt blocks)
    for lx, ly in [(main_mx - 4, bldg_y0 - 1), (main_mx - 3, bldg_y0), (main_mx + 4, bldg_y0 - 1),
                   (main_mx + 3, bldg_y0), (main_mx - 5, bldg_y0 - 2), (main_mx + 5, bldg_y0 - 2)]:
        _occ(b, "dirt_block", lx, ly)

    # ============ THE STATION BUILDING — the formicarium-centred ant lab ===================
    bx0, by0, bx1, by1 = ox + 6, bldg_y0, ox + 20, bldg_y0 + 9
    ix0, iy0, ix1, iy1 = _floor_room(b, bx0, by0, bx1, by1)
    # a 1-wide door on the SOUTH wall (faces the mouth — the colony is his focus; C1)
    dcx = bx0 + 4
    b.occ.pop((dcx, by0), None)
    b.reserved[by0][dcx] = False
    b.set_ground(dcx, by0, "wood_floor", surface="building")
    _occ(b, "door_square", dcx, by0)
    # NORTH wall = the display wall: terrarium, ant charts, the FORMICARIUM centrepiece, books
    fcx = (ix0 + ix1) // 2
    _occ(b, "bug_terrarium_big", ix0, iy1)                 # 2x1 live-ant vivarium
    _occ(b, "ant_chart", ix0 + 3, iy1)
    _occ(b, "formicarium", fcx, iy1)                       # the centrepiece
    _occ(b, "ant_chart", ix1 - 3, iy1)
    _occ(b, "bookshelf", ix1 - 1, iy1)                     # 2x1
    # the TRAIL-STUDY table (map_table_big, 2x2) centre; a chair beside it
    _occ(b, "map_table_big", ix0 + 5, iy0 + 3)
    _occ(b, "chair_wood", ix0 + 7, iy0 + 3)
    # the researcher's corner: cot (2x2) NW + writing desk (2x1) NE
    _occ(b, "cot", ix0, iy0 + 1)
    _occ(b, "desk", ix1 - 2, iy0 + 1)
    _occ(b, "specimen_case", ix0, iy0 + 3)
    _occ(b, "specimen_case", ix1, iy0 + 3)
    _occ(b, "lantern", ix1, iy0)

    # ============ THE ANT SIGN + the dirt ROAD from the north =============================
    _occ(b, "sign_ant", bx1 + 2, by1)
    rng = random.Random(43)
    rx = bx0 + 6
    for y in range(road_y, by1, -1):
        for xx in (rx, rx + 1):
            if b.in_bounds(xx, y) and b.is_free(xx, y) and b.surface[y][xx] != "building":
                b.set_ground(xx, y, "mud", surface="path")
        rx += rng.choice((-1, 0, 0, 1))
        rx = max(bx0 + 2, min(bx1 - 2, rx))
    for y in range(by0 - 1, mouth_y, -1):
        for xx in (dcx, dcx + 1):
            if b.in_bounds(xx, y) and b.is_free(xx, y) and b.ground[y][xx] != "cave_floor":
                b.set_ground(xx, y, "mud", surface="path")

    # ============ THE EMPTY PEN — the future outdoor ant-farm plot (owner: pen is empty) ===
    px0, py0, px1, py1 = bx1 + 4, by0 + 1, bx1 + 12, by0 + 8
    for x in range(px0, px1 + 1):
        for y in (py0, py1):
            _occ(b, "gate_wood" if (x == px0 + 4 and y == py0) else "fence_wood", x, y)
    for y in range(py0 + 1, py1):
        for x in (px0, px1):
            _occ(b, "fence_wood", x, y)

    # ===== P2: THE FIELD-STUDY CHARACTER — he WATCHES and BAITS the trails ================
    # OBSERVATION POST at the main mouth: stool + easel of field sketches + a crate of jars + light
    _occ(b, "stool_wood", main_mx - 6, bldg_y0 + 1)
    _occ(b, "easel", main_mx - 7, bldg_y0 + 2)
    _occ(b, "crate", main_mx - 6, bldg_y0 + 3)
    _occ(b, "lantern", main_mx - 4, bldg_y0)
    # BAIT STATIONS staked along the ant trail up from the mouth (he studies what they haul)
    for bxx, byy in [(main_mx + 2, bldg_y0 + 4), (main_mx - 3, bldg_y0 + 8),
                     (main_mx + 5, bldg_y0 + 12), (ox + 8, bldg_y0 + 15)]:
        _occ(b, "bait_station", bxx, byy)
    # SPECIMEN-COLLECTION gear west of the building: a net post + crates
    _occ(b, "net_post", bx0 - 3, by0 + 3)
    _occ(b, "crate", bx0 - 3, by0 + 2)
    _occ(b, "crate", bx0 - 2, by0 + 1)
    # The PEN as an outdoor ant-farm plot IN PROGRESS (still empty of ants — the tease): a
    # started dirt mound + a survey stake, gear staged at the gate.
    _occ(b, "dirt_block", px0 + 3, py0 + 3)
    _occ(b, "dirt_block", px0 + 4, py0 + 3)
    _occ(b, "dirt_block", px0 + 4, py0 + 4)
    _occ(b, "signpost", px0 + 2, py0 + 2)
    _occ(b, "crate", px0 + 4, py0)

    # ===== P3: LIVED-IN RICHNESS + ant motifs =============================================
    # a small field camp beside the building: campfire + a couple of supply crates
    _occ(b, "campfire", bx0 - 4, by1 - 2)
    _occ(b, "crate", bx0 - 4, by1 - 4)
    _occ(b, "crate", bx0 - 5, by1 - 5)
    # nets drying + more light along the road head and the mouth
    _occ(b, "net_pile", bx1 + 2, by1 - 2)
    _occ(b, "lantern", main_mx + 6, bldg_y0)
    # more fungus + windfalls near the mouths (the ants' food, and the trail bait)
    _occ(b, "mushroom_inkcap", main_mx - 8, mouth_y + 3)
    _occ(b, "mushroom_morel", main_mx + 7, mouth_y + 4)
    _occ(b, "mushroom_inkcap", ox + 11, mouth_y + 2)
    _occ(b, "tree_apple", ox + 3, oy + 26)
    _occ(b, "wild_berry_bush", ox + 6, oy + 31)

    # PREVIEW-ONLY: a worker file streaming UP out of the main mouth toward the forage
    for i in range(9):
        t = i / 8.0
        b.place_bug("ant_worker", main_mx - 1 + t * 5, mouth_y + 2 + t * 18, scale=2.2)
    return (bx0, by0)


def build():
    """Standalone vignette: fake a dirt surface (north) over a dirt-block body (south)."""
    b = ZoneBuilder("scene_myrmecology_station", 52, 46, base_tile="dirt",
                    name="Myrmecology Station", biome="dirt")
    ng = _vnoise(47)
    for y in range(0, 15):                       # south third = dirt-block underground body
        for x in range(52):
            b.set_ground(x, y, "cave_floor", surface="grass")
            if ng(0.14 * x, 0.14 * y) > 0.35:
                b.place_occupant("dirt_block", x, y)
    for y in range(14, 46):                       # transitioned surface with grass remnants
        for x in range(52):
            if ng(0.16 * x, 0.16 * y) > 0.6:
                b.set_ground(x, y, "grass")
    place_ant_entrance(b, 2, 1)
    b.spawn = [12, 42]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
