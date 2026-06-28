#!/usr/bin/env python3
"""Building piece — the WEAVER ("Isolde's Loom"). A warm WEAVING HALL under two back rooms: a
STOREROOM (consolidated raw materials — trunk, fabric bolts, baskets) and a colourful DYE ROOM
(dye vats). The hall is a tidy SHOWROOM: a left→right PRODUCTION LINE along the back (spinner ->
loom -> sewing machine), a ROW of display MANNEQUINS and CLOTHING RACKS down the sides, and the
weaver's own woven RUGS laid out flat on the floor as the centrepiece. Candelabra light it warmly.

`place_weaver(b, ox, oy)` drops it into any builder; run directly to preview standalone ->
tools/_generated/previews/zones/village_21_B/scenes/weaver.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.tilemap import stamp                                   # noqa: E402

# 12 wide x 15 tall. North band = STOREROOM (left of the col-6 divider) | DYE ROOM (right); each
# opens through a door into the full-width WEAVING HALL below (front door, south). In the hall:
#   - row 5  PRODUCTION LINE: spinning_wheel -> loom -> sewing_machine (all 2-wide), back wall.
#   - col 1  a vertical ROW of display MANNEQUINS (the blob-form clothing display).
#   - col 9  CLOTHING RACKS (2-wide) + candelabra alternating down the right side.
#   - centre two graded RUGS laid flat as the woven-goods showpiece; weaver NPC at the line.
# 2-wide pieces = anchor char at the SW cell + '.' for the rest of the footprint (auto-filled).
WEAVER = """
WWWWWWWWWWWW
WT..byWVV..W
W.k.b.W..V.W
W.....W....W
WWWDWWWWDWWW
WP..L....E.W
W1.......C.W
W....N.....W
W3.......R.W
W..........W
W2.......C.W
W..........W
W4.......R.W
W..........W
WWWWWDWWWWWW
"""
LEG = {
    "W": ("occ", "wall_wood"), "D": ("occ", "door_square"),
    "P": ("occ", "spinning_wheel"),  # thread station (2-wide)
    "L": ("occ", "loom"),            # cloth station (2-wide)
    "E": ("occ", "sewing_machine"),  # goods station (2-wide)
    "V": ("occ", "dye_vat"),         # dye station
    "R": ("occ", "clothing_rack"),   # garment display rail (2-wide)
    "C": ("occ", "candelabra"),      # cozy candle light
    "b": ("occ", "fabric_bolt"),     # bolts of cloth (storeroom)
    "y": ("occ", "yarn_basket"),     # open basket, always full of yarn (textile filter)
    "k": ("occ", "basket"),          # lidded general basket
    "T": ("occ", "trunk"),           # bulk storage (2-wide)
    # mannequins (Pipeline B blob-forms): two plain + two dressed
    "1": ("occ", "mannequin_white"), "2": ("occ", "mannequin_cream"),
    "3": ("occ", "mannequin_dress_red"), "4": ("occ", "mannequin_dress_teal"),
    "N": ("npc", "scholar_down"), ".": ("floor",),
}

BW, BH, DOORX = 12, 15, 5

# Woven RUGS laid flat on the open centre floor (the weaver's showpiece wares). Flat occupants
# render UNDER nothing here (one-occupant-per-cell), so they sit on genuinely open floor. Each is
# (id, local_x, local_y) of its SW anchor; footprints auto-fill north+east.
RUGS = [
    ("rug_lg_rect", 3, 2),   # LARGE ornate persian (3x5) — centre showpiece
    ("rug_md_sq", 6, 4),     # MEDIUM green medallion (3x3) — graded display, right of it
    ("rug_sm_sq", 7, 1),     # SMALL red geometric (2x2) — front, completes small/med/large
]


def place_weaver(b, ox, oy):
    """Drop the weaver's shop (SW corner ox,oy). Open-fronted: building, cloth sign, planters out
    front. Door faces south at ox+DOORX. Returns the building rect."""
    stamp(b, WEAVER, LEG, ox=ox, oy=oy)
    for rid, lx, ly in RUGS:
        b.place_occupant(rid, ox + lx, oy + ly)
    from features.village import shop_frontage
    shop_frontage(b, ox, oy, sign_id="sign_weaver", sign_x=DOORX - 2,
                  items=[("potted_plant", 1, -2), ("potted_plant", BW - 2, -2)])
    return (ox, oy, ox + BW - 1, oy + BH - 1)


PREVIEW = "zones/village_21_B/scenes"
SCALE = 6


def build():
    b = ZoneBuilder("scene_weaver", BW + 8, BH + 12, base_tile="grass", name="Weaver")
    place_weaver(b, 4, 7)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
