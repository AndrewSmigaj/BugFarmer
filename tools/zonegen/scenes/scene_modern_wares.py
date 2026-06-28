#!/usr/bin/env python3
"""Building piece — MODERN WARES ("Pim's Modern Wares"). The clean, bright CONTRAST shop: a sleek
marble SHOWROOM of appliances staged like a store (a kitchen-island hero, fridge, range stove, modern
sofa) on metal shelving, with GLASS-BLOCK windows in the front wall and a neon sign — over a small
STOCKROOM of crates and shelving. Buy-only (electronics are never craftable, D26).

`place_modern_wares(b, ox, oy)` drops it; run directly to preview ->
tools/_generated/previews/zones/village_21_B/scenes/modern_wares.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.tilemap import stamp                                   # noqa: E402

# Building 14 wide x 13 tall (bigger & sleeker, marble). STOCKROOM (N: crates + metal shelving) over
# a large SHOWROOM. Front wall carries GLASS-BLOCK windows around the door. 2-wide/2x2 pieces = anchor
# char (SW cell) + '.' for the rest of the footprint.
BUILDING = """
WWWWWWWWWWWWWW
Wc..M...M..c.W
W.....c......W
WWWDWWWWWDWWWW
WF...M....R..W
W............W
W............W
W.....I......W
W...h........W
WS...L...O...W
W.......N....W
W.......T....W
WWGGWWDWWGGWWW
"""
LEG = {
    "W": ("occ", "wall_marble"), "D": ("occ", "door_square"), "G": ("occ", "glass_block"),
    "F": ("occ", "fridge"), "R": ("occ", "range_stove"), "I": ("occ", "kitchen_island"),
    "S": ("occ", "sofa_modern"), "O": ("occ", "ottoman"), "T": ("occ", "counter"),
    "M": ("occ", "metal_shelf"), "h": ("occ", "electric_heater"),
    "L": ("occ", "lamp_floor"), "c": ("occ", "crate"),
    "N": ("npc", "merchant_down"), ".": ("floor",),
}

BW, BH, DOORX = 14, 13, 6


def place_modern_wares(b, ox, oy):
    """Drop the showroom (SW corner ox,oy). Open-fronted: building, neon sign, planters out front."""
    stamp(b, BUILDING, LEG, ox=ox, oy=oy, floor="stone_floor")
    from features.village import shop_frontage
    shop_frontage(b, ox, oy, sign_id="neon_sign", sign_x=DOORX - 2,
                  items=[("potted_plant", 1, -2), ("potted_plant", BW - 2, -2)])
    return (ox, oy, ox + BW - 1, oy + BH - 1)


PREVIEW = "zones/village_21_B/scenes"
SCALE = 6


def build():
    b = ZoneBuilder("scene_modern_wares", BW + 8, BH + 8, base_tile="grass", name="Modern Wares")
    place_modern_wares(b, 4, 6)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
