#!/usr/bin/env python3
"""Diagonal road-transition tiles — composited, never generated.

A 45° transition tile is half road / half grass split along a tile diagonal. We build
it by MASKING the two EXISTING tile PNGs together (so it matches both materials by
construction — zero gpt-image spend, seam-free against either neighbor), with a 2px
dithered band along the diagonal so the edge reads hand-pixelled, not vector-cut.

Naming: `<road>_d_<corner>` where <corner> is the corner the ROAD triangle points
into (the road wraps that corner of the cell):
    stone_path_d_ne  = road fills the NE half (grass keeps the SW half)
    dirt_path_d_ne   = same split, dirt road over grass
`terrain.smooth_paths()` picks these per stair-step corner; the ids contain "path" so
ZoneBuilder._tile_surface classifies them as roads on load().

IMAGE vs GAME orientation: PNG y runs DOWN; the game's +y is NORTH (up). So the
image's top edge is the cell's NORTH edge — "NE corner" = image top-right.

Writes: BugFarmerClient/Assets/Resources/Tiles/<road>_d_<corner>.png (32×32, opaque
full-bleed like every ground tile). Run tools/fix_sprite_ppu.py after Unity imports.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Tiles")

# (road tile id, output base name). dirt's diagonal gets a path-flavored name so
# surface classification on zone load stays correct.
MATERIALS = [
    ("stone_path", "stone_path_d"),
    ("dirt", "dirt_path_d"),
]
GRASS = "grass"
DITHER_BAND = 1  # +/- pixels around the diagonal that checker between materials


def road_side(corner, x, y, n):
    """True if pixel (x,y) [image coords, y down] is on the ROAD side for `corner`,
    None if inside the dither band."""
    if corner in ("ne", "sw"):
        d = x - y                      # main diagonal TL->BR; NE half is d > 0
        road = d > 0 if corner == "ne" else d < 0
    else:
        d = (x + y) - (n - 1)          # anti-diagonal TR->BL; SE half is d > 0
        road = d > 0 if corner == "se" else d < 0
    if abs(d) <= DITHER_BAND:
        return None
    return road


def composite(road_img, grass_img, corner):
    n = road_img.width
    out = Image.new("RGBA", (n, n))
    rp, gp, op = road_img.load(), grass_img.load(), out.load()
    for y in range(n):
        for x in range(n):
            side = road_side(corner, x, y, n)
            if side is None:  # dither band: checker the two materials
                side = (x + y) % 2 == 0
            op[x, y] = rp[x, y] if side else gp[x, y]
    return out


def main():
    grass = Image.open(os.path.join(TILES, f"{GRASS}.png")).convert("RGBA")
    made = []
    for road_id, base in MATERIALS:
        road = Image.open(os.path.join(TILES, f"{road_id}.png")).convert("RGBA")
        if road.size != grass.size:
            road = road.resize(grass.size, Image.NEAREST)
        for corner in ("ne", "nw", "se", "sw"):
            img = composite(road, grass, corner)
            out = os.path.join(TILES, f"{base}_{corner}.png")
            img.save(out)
            made.append(os.path.basename(out))
    print(f"wrote {len(made)} diagonal tiles: {', '.join(made)}")


if __name__ == "__main__":
    main()
