"""Comparison sheet for the owner: ten ground layouts drawn three ways, in the game's own tile art.

  As laid          — every square exactly as laid.
  Fill the steps   — the zones' rule (tools/zonegen/features/terrain.py smooth_paths, its diagonal part only): a
                     grass square with exactly one road neighbour above/below and one beside, same material, gets a
                     45° half of road. Drawn here from the current grass and road tiles (the zones' pre-made pieces,
                     Resources/Tiles/stone_path_d_*.png, carry an older grass), so only the method differs.
  Cut the corners  — the "dual grid": tiles drawn on the points where four squares meet (marching squares with
                     45° cuts), so outer corners are trimmed as well as inner ones filled.

Every layout is laid out two squares past each panel edge and cropped, so roads that carry on past the edge are
drawn the way the game draws them. Squares touching only at corners join into a band in the "cut" method — one of
its two possible choices.

Free (no image API). Usage: python3 tools/gdd/ground_edges_sheet.py
Writes tools/_generated/previews/examples/ground-edges/methods.png (git-ignored; on disk).
For docs/product/investigations/research-2026-09-29/laying-ground.md.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TILES = f"{ROOT}/BugFarmerClient/Assets/Resources/Tiles"
OUT = f"{ROOT}/tools/_generated/previews/examples/ground-edges/methods.png"
P = 32            # art pixels per square (the game's density for these tiles)
SCALE = 2         # shown at 2x, nearest-neighbour, so the pixels stay crisp
W, H = 9, 6       # squares per panel
M = 2             # extra squares drawn past each edge, then cropped
GW, GH = W + 2 * M, H + 2 * M

def tile(name):
    im = Image.open(f"{TILES}/{name}.png").convert("RGBA")
    return im.resize((P, P), Image.NEAREST) if im.size != (P, P) else im

GRASS, STONE = tile("grass"), tile("stone_path")

def tiled(t):
    img = Image.new("RGBA", (GW * P, GH * P))
    for x in range(GW):
        for y in range(GH):
            img.paste(t, (x * P, y * P))
    return img

def px(x, y):        # panel cell (x, y), +y = north, may lie up to M squares outside -> image top-left
    return (x + M) * P, (GH - 1 - (y + M)) * P

def as_laid(cells):
    img = tiled(GRASS)
    for (x, y) in cells:
        img.paste(STONE, px(x, y))
    return img

def fill_steps(cells):
    img = as_laid(cells)
    road = lambda x, y: (x, y) in cells
    for x in range(-M, W + M):
        for y in range(-M, H + M):
            if road(x, y):
                continue
            vs = [c for c, ok in (("n", road(x, y + 1)), ("s", road(x, y - 1))) if ok]
            hs = [c for c, ok in (("e", road(x + 1, y)), ("w", road(x - 1, y))) if ok]
            if len(vs) == 1 and len(hs) == 1:
                # the road half of the square, cut from the same stone art over the same grass, so only the
                # method differs from the other column (the zones' pre-made pieces carry an older grass)
                tri = {"ne": [(0, 0), (P, 0), (P, P)], "nw": [(0, 0), (P, 0), (0, P)],
                       "se": [(P, 0), (P, P), (0, P)], "sw": [(0, 0), (0, P), (P, P)]}[vs[0] + hs[0]]
                m = Image.new("L", (P, P), 0)
                ImageDraw.Draw(m).polygon(tri, fill=255)
                img.paste(STONE, px(x, y), m)
    return img

def corner_poly(tl, tr, bl, br):
    """Filled part of one dual tile (0..P, y down): marching squares with edge midpoints; the
    two-diagonal 'saddle' joins into a band (the way a chain of corner-touching squares reads as a road)."""
    h = P // 2
    pts = {"tl": (0, 0), "tr": (P, 0), "br": (P, P), "bl": (0, P)}
    mids = {"t": (h, 0), "r": (P, h), "b": (h, P), "l": (0, h)}
    s = {"tl": tl, "tr": tr, "br": br, "bl": bl}
    order = ["tl", "t", "tr", "r", "br", "b", "bl", "l"]
    edge_of = {"t": ("tl", "tr"), "r": ("tr", "br"), "b": ("br", "bl"), "l": ("bl", "tl")}
    n = sum(s.values())
    if n == 0:
        return []
    if n == 4:
        return [[(0, 0), (P, 0), (P, P), (0, P)]]
    poly = []
    for k in order:
        if k in pts:
            if s[k]:
                poly.append(pts[k])
        else:
            a, b = edge_of[k]
            if s[a] != s[b] or (n == 2 and s["tl"] == s["br"]):
                poly.append(mids[k])
    return [poly]

def cut_corners(cells):
    mask = Image.new("L", (GW * P, GH * P), 0)
    d = ImageDraw.Draw(mask)
    for vx in range(-M, W + M + 1):
        for vy in range(-M, H + M + 1):
            tl, tr = (vx - 1, vy) in cells, (vx, vy) in cells
            bl, br = (vx - 1, vy - 1) in cells, (vx, vy - 1) in cells
            ox, oy = (vx + M - 0.5) * P, (GH - (vy + M) - 0.5) * P
            for poly in corner_poly(tl, tr, bl, br):
                d.polygon([(ox + a, oy + b) for a, b in poly], fill=255)
    img = tiled(GRASS)
    img.paste(tiled(STONE), (0, 0), mask)
    return img

def grid(img):       # crop to the panel, then faint lines where the real squares are
    g = img.crop((M * P, M * P, (M + W) * P, (M + H) * P))
    d = ImageDraw.Draw(g, "RGBA")
    for x in range(W + 1):
        d.line([(x * P, 0), (x * P, H * P)], fill=(0, 0, 0, 60))
    for y in range(H + 1):
        d.line([(0, y * P), (W * P, y * P)], fill=(0, 0, 0, 60))
    return g

ALL = [(x, y) for x in range(-M, W + M) for y in range(-M, H + M)]
LAYOUTS = [
    ("One square", {(4, 2)}),
    ("End of a road", {(x, y) for x in range(-M, 6) for y in (2, 3)}),
    ("A paved yard", {(x, y) for x in range(2, 7) for y in range(1, 5)}),
    ("A diagonal road\n(steps two\nsquares thick)", {(x, y) for (x, y) in ALL if x - 2 <= y <= x - 1}),
    ("Stepping stones\ncorner to corner", {(x, y) for (x, y) in ALL if y == x - 1}),
    ("A square dug out\nof a wide road", {(x, y) for x in range(-M, W + M) for y in (1, 2, 3)} - {(4, 2)}),
    ("A road turning\na corner", {(x, y) for x in range(-M, 6) for y in (1, 2)}
                              | {(x, y) for x in (4, 5) for y in range(1, H + M)}),
    ("A square sticking\nout of a road", {(x, y) for x in range(-M, W + M) for y in (1, 2)} | {(4, 3)}),
    ("A narrow path\njoining a road", {(x, y) for x in range(-M, W + M) for y in (1, 2)} | {(4, y) for y in range(3, H + M)}),
    ("A checkerboard\nof paving", {(x, y) for x in range(2, 7) for y in range(1, 5) if (x + y) % 2 == 0}),
]
COLS = [("As laid", as_laid), ("Fill the steps\n(the zones' rule)", fill_steps),
        ("Cut the corners\n(the other method)", cut_corners)]

font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
font_r = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
font_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
pw, ph = W * P * SCALE, H * P * SCALE
LABEL_W, HEAD_H, GAP, TOP = 330, 110, 24, 110
sheet = Image.new("RGB", (LABEL_W + len(COLS) * (pw + GAP) + GAP, TOP + HEAD_H + len(LAYOUTS) * (ph + GAP) + GAP),
                  (236, 240, 227))
d = ImageDraw.Draw(sheet)
d.text((GAP, 24), "Laying ground: three ways to draw the same squares (stone path on grass)", font=font_h, fill=(34, 24, 32))
d.text((GAP, 66), "Faint lines show the real squares; digging, walking and building always work on whole squares. "
       "Roads carry on past the edges.", font=font_t, fill=(74, 68, 82))
for c, (name, _) in enumerate(COLS):
    d.multiline_text((LABEL_W + GAP + c * (pw + GAP), TOP + 10), name, font=font_r, fill=(34, 24, 32), spacing=6)
for r, (label, cells) in enumerate(LAYOUTS):
    y0 = TOP + HEAD_H + r * (ph + GAP)
    d.multiline_text((GAP, y0 + 12), label, font=font_r, fill=(34, 24, 32), spacing=6)
    for c, (_, fn) in enumerate(COLS):
        panel = grid(fn(cells)).convert("RGB").resize((pw, ph), Image.NEAREST)
        sheet.paste(panel, (LABEL_W + GAP + c * (pw + GAP), y0))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sheet.save(OUT)
print(OUT, sheet.size)
