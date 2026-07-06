#!/usr/bin/env python3
"""Building piece — a small NPC COTTAGE (a home): four rooms in a fenced yard.

THE HOUSEHOLD RULE (house.md §Making DIVERSE houses, owner correction 2026-07-06:
"you keep making every single house the same"): the SHELL (walls/doors) is shared;
the FURNISHING comes from a HOUSEHOLD spec — trade room, wealth tier, signature
piece, tidiness. Adding a household = adding a spec below, never editing the shell.

`place_cottage(b, ox, oy, household="farmsteader")` drops the south-door plan;
`place_cottage_north(...)` the north-door plan (doors face CONTEXT). Run directly to
preview all three households side by side.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.tilemap import stamp, dump                              # noqa: E402

# ---------------------------------------------------------------------------
# SHELLS — walls + doors ONLY (furnishing is the household's job).
# South-door plan: BEDROOM (NW) | TRADE ROOM (NE) over KITCHEN (SW) | LIVING (SE).
SHELL_S = """
WWWWWWWWWWWWWWW
W.......W.....W
W.......W.....W
W.......D.....W
W.......W.....W
WWWWWWDWWWWWDWW
W.......W.....W
W.......W.....W
W.......D.....W
W.......W.....W
W.......W.....W
WWWWWWWWWWDWWWW
"""
# North-door plan (a DIFFERENT plan, not a mirror): LIVING (NW, north front door) |
# TRADE ROOM (NE) over BEDROOM (SW) | KITCHEN (SE).
SHELL_N = """
WWWWDWWWWWWWWWW
W.......W.....W
W.......D.....W
W.......W.....W
W.......W.....W
WWWWDWWWWWDWWWW
W.......W.....W
W.......W.....W
W.......D.....W
W.......W.....W
W.......W.....W
WWWWWWWWWWWWWWW
"""
SHELL_LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), ".": ("floor",)}

BW, BH = 15, 12
DOORX = 10        # south-door column (south plan)
DOORX_N = 4       # north-door column (north plan)
# Room interiors (relative to ox,oy): (dx, dy_bottom, width, height)
ROOM_SW = (1, 1, 7, 5)
ROOM_SE = (9, 1, 5, 5)
ROOM_NW = (1, 7, 7, 4)
ROOM_NE = (9, 7, 5, 4)

# ---------------------------------------------------------------------------
# HOUSEHOLDS — each authored for its plan, text-grid per room (top row = north).
# Shared legend chars; households only use what they need. An anchor char is the
# piece's SOUTH-WEST cell (its FOOT row): footprints extend right and UP-page —
# so multi-row pieces (bed 2x4, table/extractor/rug 2x2) anchor on their BOTTOM
# grid row, and everything else on the char itself. Covered cells stay '.'.
LEG = {
    "W": ("occ", "wall_wood"), "D": ("occ", "door_square"), ".": ("floor",),
    # sleep + storage
    "E": ("occ", "bed_basic"), "F": ("occ", "bed_fancy"), "n": ("occ", "nightstand"),
    "d": ("occ", "dresser"), "C": ("occ", "chest"), "u": ("occ", "trunk"),
    # cook + eat
    "V": ("occ", "stove"), "O": ("occ", "counter"), "K": ("occ", "sink"),
    "c": ("occ", "cupboard"), "T": ("occ", "table_wood"), "a": ("occ", "chair_wood"),
    "s": ("occ", "stool_wood"), "G": ("occ", "keg"), "b": ("occ", "basket"),
    # live
    "A": ("occ", "armchair"), "k": ("occ", "bookshelf"), "f": ("occ", "fireplace"),
    "p": ("occ", "potted_plant"), "l": ("occ", "lamp_table"), "L": ("occ", "lantern"),
    "y": ("occ", "vanity"), "m": ("occ", "mirror_standing"),
    "r": ("occ", "rug_sm_rect"), "R": ("occ", "rug_md_rect"), "h": ("occ", "rug_honeycomb"),
    # trades
    "N": ("occ", "net_pile"), "P": ("occ", "lobster_pot"), "Z": ("occ", "drying_rack_fish"),
    "X": ("occ", "crate"), "B": ("occ", "barrel"), "S": ("occ", "seashell_pile"),
    "H": ("occ", "honey_extractor"), "q": ("occ", "wine_rack"), "j": ("occ", "honey_shelf"),
    "e": ("occ", "skep_basket"), "w": ("occ", "candle_beeswax"), "J": ("occ", "honey_jar_shelf"),
    "g": ("occ", "fish_crate"),
}

HOUSEHOLDS = {
    # Grids use ONE anchor char per piece; footprints extend right+down from it
    # (bed 2x4, stove/counter/dresser/vanity/bookshelf/fireplace/rack/trunk 2x1,
    # table/extractor/honeycomb-rug 2x2, rug_sm_rect 3x2). Door-adjacent cells are
    # kept clear per plan (see the shell comments).
    #
    # THE FISHER (south-door plan) — poor, tidy, the sea in every room. Signature:
    # the seashell collection. Trade room: nets, pots, the indoor drying rack.
    "fisher": {
        "plan": "south",
        "npc": "fisher_down",
        ROOM_NW: ["...C.S.",     # the catch-chest; the shells at the sill
                  ".......",
                  ".......",     # east-wall door row kept clear at col6
                  "E......"],    # bed (2x4) anchors at its FOOT row; bottom col5 clear = door
        ROOM_NE: ["Z..N.",       # net room: rack (2x1) + net north, pots mid, net south
                  "..P.P",
                  ".N...",       # col0 row2 clear = west door
                  "....."],      # col3 clear = south door
        ROOM_SW: ["V.O.K..",     # the cook run CONTIGUOUS c0-c4 (stove 2, counter 2, sink)
                  "B......",     # the salt barrel by the run
                  ".....s.",     # the pulled-out stool is the mess
                  ".sT....",     # table (2x2, foot anchor) + stool
                  "......."],    # top col5 clear = the mid door
        ROOM_SE: ["..L..",       # living, front door at col1: bare boards, a lantern,
                  ".....",      # the small rug (3x2, foot anchor), the fish crate
                  ".....",
                  "gr...",
                  "....."],
    },
    # THE FARMSTEADER (north-door plan) — comfortable, house-proud (the vanity
    # corner is the signature). Trade room: the PANTRY — kegs, the winter store.
    "farmsteader": {
        "plan": "north",
        "npc": "farmer_down",
        ROOM_NW: ["k....p.",     # living, front door above col3: bookshelf (2x1), plant
                  ".A.....",     # armchair; col6 row1 clear = east door
                  "...l...",
                  "......."],    # col3 clear = south door
        ROOM_NE: [".G.G.",       # pantry: kegs north, barrel + crate, the basket
                  "..B.X",      # col0 row1 clear = west door
                  "..b..",
                  "....."],      # col1 clear = south door
        ROOM_SW: ["..n..d.",     # nightstand, dresser (2x1); col3 kept clear = north door
                  ".......",
                  "...y.m.",     # THE VANITY (2x1) + standing mirror — house-proud
                  ".......",     # col6 row2 clear = east door
                  "E......"],    # bed (2x4) anchors at its foot row
        ROOM_SE: ["..V.K",       # kitchen: stove(2)+sink run; col1 top clear = north door
                  "...O.",      # counter under the sink corner
                  "...a.",       # chair at the table; col0 row2 clear = west door
                  ".T...",       # table (2x2, foot anchor)
                  "G...b"],      # keg + basket on the south wall
    },
    # MAREN THE BEEKEEPER (south-door plan) — the zone's anchor, comfortable, bee
    # everything. Signature: the honeycomb rug. Trade room: the BREWING BACKROOM —
    # extractor, wine rack, honey shelf, keg (owner: "the brewing stuff should be
    # in a backroom... not just out on the lawn").
    "beekeeper": {
        "plan": "south",
        "npc": None,
        ROOM_NW: ["..n..d.",     # nightstand, dresser (2x1)
                  "..w....",     # the beeswax candle by the bed
                  ".......",     # col6 row2 clear = east door
                  "F..h..."],    # fancy bed + THE HONEYCOMB RUG (2x2), foot anchors; col5 clear = door
        ROOM_NE: ["...qj",       # BREWING BACKROOM: wine rack + honey shelf north
                  ".H...",      # extractor (2x2, foot anchor)
                  "....G",       # the mead keg; col0 row2 clear = west door
                  "....."],      # col3 clear = south door
        ROOM_SW: ["V.O.K.J",     # cook run c0-c4 + the honey-jar shelf in the corner
                  "c......",     # cupboard (2x1)
                  ".....a.",
                  "..T....",     # table (2x2, foot anchor)
                  "......."],    # top col5 clear = the mid door
        ROOM_SE: ["f.e..",       # living: fireplace (2x1) + the skep beside it
                  ".....",
                  "...w.",       # candle; col0 row2 clear = the west door
                  ".A...",       # the armchair pulled toward the fire
                  "....."],      # front door at col1
    },
}


def _furnish(b, ox, oy, household):
    spec = HOUSEHOLDS[household]
    for (dx, dy, w, hgt), grid in ((k, v) for k, v in spec.items() if isinstance(k, tuple)):
        assert len(grid) == hgt and all(len(row) == w for row in grid), \
            f"{household} room at +{dx},+{dy}: grid must be {w}x{hgt}"
        stamp(b, "\n" + "\n".join(grid) + "\n", LEG, ox=ox + dx, oy=oy + dy)


def place_cottage(b, ox, oy, npc="__spec__", yard_style="modest", household="fisher"):
    """South-door cottage (SW corner ox,oy) furnished by `household`, in a styled
    yard WITH a backyard (yard.md: the private life lives behind the house)."""
    from features.yard import styled_yard
    spec = HOUSEHOLDS[household]
    assert spec["plan"] == "south", f"{household} is authored for the {spec['plan']} plan"
    stamp(b, SHELL_S, SHELL_LEG, ox=ox, oy=oy)
    _furnish(b, ox, oy, household)
    resident = spec["npc"] if npc == "__spec__" else npc
    if resident:
        b.place_player(resident, ox + 11.0, oy + 3)
    return styled_yard(b, ox, oy, ox + BW - 1, oy + BH - 1, ox + DOORX,
                       style=yard_style, seed=ox)


def place_cottage_north(b, ox, oy, npc="__spec__", household="farmsteader"):
    """North-door cottage (front door TOP wall at ox+DOORX_N) furnished by
    `household`. No styled yard by default — a context-facing house is dressed by
    its context (a quay, a lane, a shore)."""
    spec = HOUSEHOLDS[household]
    assert spec["plan"] == "north", f"{household} is authored for the {spec['plan']} plan"
    stamp(b, SHELL_N, SHELL_LEG, ox=ox, oy=oy)
    _furnish(b, ox, oy, household)
    resident = spec["npc"] if npc == "__spec__" else npc
    if resident:
        b.place_player(resident, ox + 4.0, oy + 8)
    return (ox, oy, ox + BW - 1, oy + BH - 1)


# Legacy grid names kept for imports that reference the plan constants.
COT = SHELL_S
COT_N = SHELL_N

PREVIEW = "zones/village_21_B/scenes"
SCALE = 6


def build():
    b = ZoneBuilder("scene_cottage", (BW + 4) * 3 + 4, BH + 14, base_tile="grass",
                    name="Cottage households")
    place_cottage(b, 2, 6, household="fisher", yard_style="unfenced")
    place_cottage_north(b, BW + 6, 6, household="farmsteader")
    place_cottage(b, 2 * (BW + 4) + 2, 6, household="beekeeper", yard_style="unfenced")
    b.spawn = [BW + 6 + DOORX_N, 2]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
