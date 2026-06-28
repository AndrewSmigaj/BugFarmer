#!/usr/bin/env python3
"""Building piece — the WEAVER ("Isolde's Loom"). A warm WEAVING HALL (looms, spinning wheel, a
dress form, rugs, the weaver at work) under two back rooms: a STOREROOM (fabric bolts, yarn, a cloth
chest) and a colourful DYE ROOM (dye vats + drying cloth). Open-fronted with a cloth sign + a line of
dyed laundry out front.

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

# 14 wide x 15 tall. North band = STOREROOM (left) | DYE ROOM (right), split by a vertical wall at
# col 6; each opens to the full-width WEAVING HALL (south, with the front door). Looms are work
# surfaces in the hall; the dress form + spinning wheel sit on the side walls (facing rule).
WEAVER = """
WWWWWWWWWWWWWW
WT.b.bWV...VyW
W.y..yW.V...yW
W.b..bW.....yW
WWWDWWWWWWDWWW
W.P.L...E....W
W...M........W
WC.....bF..C.W
W............W
W....G.......W
W............W
W............W
W............W
W............W
WWWWWWDWWWWWWW
"""
# Three textile STATIONS in the hall: spinner (fiber->thread), loom (thread->cloth), sewing machine
# (the foot-cranked table — cloth->goods). Dye room (NE) has the vats + drying cloth; the dress form
# displays a finished garment, flanked by a fabric bolt + candelabra light.
LEG = {
    "W": ("occ", "wall_wood"), "D": ("occ", "door_square"),
    "P": ("occ", "spinning_wheel"),  # thread station
    "L": ("occ", "loom"),            # cloth station (2-wide: anchor + east dot)
    "E": ("occ", "sewing_machine"),  # goods station (2-wide)
    "V": ("occ", "dye_vat"),         # dye station
    "F": ("occ", "dress_form"), "G": ("occ", "rug_large"),
    "C": ("occ", "candelabra"),      # cozy candle light (not an electric lamp)
    "b": ("occ", "fabric_bolt"), "y": ("occ", "yarn_basket"),  # yarn_basket is a textile container
    "T": ("occ", "trunk"),           # 2-wide storage trunk (more than a chest)
    "M": ("npc", "scholar_down"), ".": ("floor",),
}

BW, BH, DOORX = 14, 15, 6


def place_weaver(b, ox, oy):
    """Drop the weaver's shop (SW corner ox,oy). Open-fronted: building, cloth sign, dyed laundry out
    front. Door faces south at ox+DOORX. Returns the building rect."""
    stamp(b, WEAVER, LEG, ox=ox, oy=oy)
    from features.village import shop_frontage
    shop_frontage(b, ox, oy, sign_id="sign_weaver", sign_x=DOORX - 2,
                  items=[("fabric_bolt", 1, -2), ("fabric_bolt", DOORX + 2, -2),
                         ("yarn_basket", BW - 2, -2)])
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
