#!/usr/bin/env python3
"""Shaped-ground tile compositor — the PYTHON mirror of the client TileCompositor.

The client blends `matA~matB~shape` composites on the GPU (TileComposite.shader,
`lerp(matB, matA, mask)`); this reproduces the SAME result on the CPU so we can render
shaped-ground previews and the shovel builder-panel swatches WITHOUT Unity. The mask math
is ported 1:1 from `TileCompositor.MaskAt` — the ONLY subtlety is coordinate space:

    Unity texture pixel (0,0) is BOTTOM-left, y UP.  PIL pixel (0,0) is TOP-left, y DOWN.

So for a PIL pixel (x, y_top) we evaluate the mask at Unity y = (n-1 - y_top). With that flip
the CPU output is pixel-identical to the shader, which is why a preview here is trustworthy.

CLI:
    python3 tools/sprites/composite_tiles.py --sheet shapes      # 13 shapes of grass~dirt
    python3 tools/sprites/composite_tiles.py --sheet materials   # every material pair, diagNE
    python3 tools/sprites/composite_tiles.py --sheet panel       # builder-panel swatch grid
Outputs to tools/_generated/previews/examples/shaped_ground/.
"""
import os
import argparse
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TILES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Tiles")
OUT = os.path.join(ROOT, "tools", "_generated", "previews", "examples", "shaped_ground")

# Mirror TileCompositor.Shapes and the server shovelMaterials (the decorative palette).
SHAPES = [
    "full",
    "diagNE", "diagNW", "diagSE", "diagSW",
    "halfN", "halfS", "halfE", "halfW",
    "quadNE", "quadNW", "quadSE", "quadSW",
]
MATERIALS = ["grass", "dirt", "sand", "mud", "stone_floor", "stone_path", "wood_floor", "cave_floor"]


def mask_at(shape, x, y, n):
    """True where material A shows. (x, y) are UNITY coords (y up), ported 1:1 from MaskAt."""
    t = n - 1
    h = n // 2
    if shape == "full":
        return True
    if shape == "diagNE":
        return (x + y) >= t
    if shape == "diagSW":
        return (x + y) <= t
    if shape == "diagNW":
        return y >= x
    if shape == "diagSE":
        return y <= x
    if shape == "halfN":
        return y >= h
    if shape == "halfS":
        return y < h
    if shape == "halfE":
        return x >= h
    if shape == "halfW":
        return x < h
    if shape == "quadNE":
        return x >= h and y >= h
    if shape == "quadNW":
        return x < h and y >= h
    if shape == "quadSE":
        return x >= h and y < h
    if shape == "quadSW":
        return x < h and y < h
    return True  # unknown -> solid A


_tile_cache = {}


def load_tile(mat):
    if mat not in _tile_cache:
        p = os.path.join(TILES, f"{mat}.png")
        _tile_cache[mat] = Image.open(p).convert("RGBA")
    return _tile_cache[mat]


def composite(matA, matB, shape):
    """Return the composited 32x32 RGBA tile for matA~matB~shape (identical to the GPU path)."""
    a = load_tile(matA)
    b = load_tile(matB)
    n = a.width
    if b.width != n:
        b = b.resize((n, n), Image.NEAREST)
    out = Image.new("RGBA", (n, n))
    ap, bp, op = a.load(), b.load(), out.load()
    for y_top in range(n):
        uy = (n - 1) - y_top  # PIL top-down -> Unity bottom-up
        for x in range(n):
            op[x, y_top] = ap[x, y_top] if mask_at(shape, x, uy, n) else bp[x, y_top]
    return out


def tile_for(tile_id):
    """Render any ground id (plain OR matA~matB~shape) the way the client would."""
    if "~" in tile_id:
        parts = tile_id.split("~")
        if len(parts) == 3:
            return composite(parts[0], parts[1], parts[2])
    return load_tile(tile_id)


# ---- preview sheets ---------------------------------------------------------

def _up(img, scale):
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def _label(draw, xy, text, fill=(235, 235, 235, 255)):
    draw.text(xy, text, fill=fill)


def sheet_shapes(matA="grass", matB="dirt", scale=5):
    cell, pad, gap = 32 * scale, 14, 18
    cols = 5
    rows = (len(SHAPES) + cols - 1) // cols
    W = pad + cols * (cell + gap)
    H = pad + rows * (cell + gap + 14) + 20
    sheet = Image.new("RGBA", (W, H), (40, 40, 46, 255))
    d = ImageDraw.Draw(sheet)
    _label(d, (pad, 6), f"{matA} ~ {matB} — all 13 shapes (matA fills the white region)")
    for i, sh in enumerate(SHAPES):
        r, c = divmod(i, cols)
        x = pad + c * (cell + gap)
        y = 24 + r * (cell + gap + 14)
        sheet.paste(_up(composite(matA, matB, sh), scale), (x, y))
        _label(d, (x, y + cell + 1), sh)
    return sheet


def sheet_materials(matB="dirt", shape="diagNE", scale=5):
    cell, pad, gap = 32 * scale, 14, 18
    cols = 4
    rows = (len(MATERIALS) + cols - 1) // cols
    W = pad + cols * (cell + gap)
    H = pad + rows * (cell + gap + 14) + 20
    sheet = Image.new("RGBA", (W, H), (40, 40, 46, 255))
    d = ImageDraw.Draw(sheet)
    _label(d, (pad, 6), f"every material as A over {matB}, shape {shape}")
    for i, m in enumerate(MATERIALS):
        r, c = divmod(i, cols)
        x = pad + c * (cell + gap)
        y = 24 + r * (cell + gap + 14)
        sheet.paste(_up(composite(m, matB, shape), scale), (x, y))
        _label(d, (x, y + cell + 1), m)
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", choices=["shapes", "materials", "both"], default="both")
    ap.add_argument("--matA", default="grass")
    ap.add_argument("--matB", default="dirt")
    ap.add_argument("--shape", default="diagNE")
    ap.add_argument("--scale", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    made = []
    if a.sheet in ("shapes", "both"):
        p = os.path.join(OUT, "shapes.png")
        sheet_shapes(a.matA, a.matB, a.scale).save(p)
        made.append(p)
    if a.sheet in ("materials", "both"):
        p = os.path.join(OUT, "materials.png")
        sheet_materials(a.matB, a.shape, a.scale).save(p)
        made.append(p)
    print("wrote:\n  " + "\n  ".join(made))


if __name__ == "__main__":
    main()
