"""pixkit — the hand-authored (Pipeline B) pixel toolkit.

Sprites are TEXT GRIDS: one char per pixel, one string row per pixel row.
Every char names a (region, shade) role — see LEGEND. ONE master grid per
(direction x frame) is rendered under TWO rules so layers always register:

  * BODY layer  = all pixels, with clothing-region chars substituted to
                  skin/underclothes (a complete unclothed base — no holes).
  * CLOTHING/HAIR layers = only that region's chars, plus the master outline
                  pixels 4-adjacent to them (each layer carries its own rim).

Baked class sprites (compat with zone NPCs + RemoteEntity fallback) render
ALL regions with the class palette. Overlays (armor/hats) are separate
mostly-transparent grids on the same 16x32 canvas, composed per-frame with
that frame's bob offset — so equipment never needs per-frame redraw.

LEGEND (canonical chars):
  .  transparent          o  outline (24,20,24)
  S/s/z  skin light/base/shadow      e eye   m mouth   w gleam/accent
  H/h/g  hair  light/base/shadow
  T/t/u  shirt light/base/shadow
  L/l/v  pants light/base/shadow
  B/b    boots light/base
Overlay grids may also use M/n/k (metal light/base/dark) and Y/y/x
(secondary material light/base/dark).
"""
import os

from PIL import Image

# ---- region sets -------------------------------------------------------------
SKIN = set("Sszem")
HAIR = set("Hhg")
SHIRT = set("Ttu")
PANTS = set("Llv")
BOOTS = set("Bb")
ACCENT = set("w")
REGIONS = {"hair": HAIR, "shirt": SHIRT, "pants": PANTS}
# body = skin + boots + accents; clothing chars substitute to underclothes
BODY_SUB = {  # what the unclothed body shows where clothing would be
    "T": "S", "t": "s", "u": "z",          # shirt area -> bare skin
}
# pants chars substitute ROW-AWARE in render(): a shorts band at the top of the
# leg rows (warm linen, not grey), bare skin below — not grey trousers.
SHORTS_SUB = {"L": "l2", "l": "l2", "v": "l3"}
SKIN_SUB = {"L": "S", "l": "s", "v": "z"}
SHORTS_MAX_ROW = 26

OUTLINE = (24, 20, 24, 255)
LINEN = (188, 158, 118, 255)
LINEN_DARK = (150, 122, 88, 255)


def make_palette(skin, hair, shirt, pants, boots=((96, 70, 50), (70, 50, 36))):
    """Build char->RGBA from 3-shade ramps. Each ramp = (light, base, dark) RGB."""
    sl, sb, sd = skin
    hl, hb, hd = hair
    tl, tb, td = shirt
    ll, lb, ld = pants
    bl, bb = boots
    a = lambda c: (c[0], c[1], c[2], 255)
    return {
        "o": OUTLINE,
        "S": a(sl), "s": a(sb), "z": a(sd),
        "e": (28, 28, 34, 255), "m": (176, 110, 86, 255), "w": (255, 255, 255, 255),
        "H": a(hl), "h": a(hb), "g": a(hd),
        "T": a(tl), "t": a(tb), "u": a(td),
        "L": a(ll), "l": a(lb), "v": a(ld),
        "B": a(bl), "b": a(bb),
        "l2": LINEN, "l3": LINEN_DARK,
        # overlay materials (used by wearables grids)
        "M": (176, 182, 190, 255), "n": (124, 130, 140, 255), "k": (78, 84, 94, 255),   # iron
        "Y": (228, 202, 130, 255), "y": (200, 172, 96, 255), "x": (160, 130, 64, 255),  # straw
        "C": (220, 140, 92, 255), "c": (184, 110, 66, 255), "q": (134, 76, 44, 255),    # copper
        "R": (158, 112, 66, 255), "r": (128, 88, 52, 255), "p": (94, 62, 36, 255),      # leather
        "F": (84, 154, 74, 255), "f": (52, 116, 52, 255),                               # foliage (charms)
    }


def parse(grid):
    """Multiline text grid -> list of rows (strings). Validates rectangularity."""
    rows = [r for r in grid.strip("\n").split("\n")]
    w = len(rows[0])
    assert all(len(r) == w for r in rows), \
        f"ragged grid: widths {sorted({len(r) for r in rows})}"
    return rows


def mirror(grid_rows):
    """Horizontal mirror (right = mirrored left)."""
    return [r[::-1] for r in grid_rows]


def render(rows, palette, mode="baked", region=None):
    """rows -> RGBA Image.
    mode='baked'  : every char via palette (the full dressed sprite).
    mode='body'   : clothing chars substituted via BODY_SUB (unclothed base).
    mode='region' : only chars in `region` + adjacent master outline pixels."""
    h, w = len(rows), len(rows[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    keep = None
    if mode == "region":
        keep = {(x, y) for y in range(h) for x in range(w) if rows[y][x] in region}
        rim = set()
        for (x, y) in keep:
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < w and 0 <= ny < h and rows[ny][nx] == "o":
                    rim.add((nx, ny))
        keep |= rim
    for y in range(h):
        for x in range(w):
            c = rows[y][x]
            if c == ".":
                continue
            if mode == "region":
                if (x, y) not in keep:
                    continue
            elif mode == "body":
                if c in SKIN_SUB:
                    c = (SHORTS_SUB if y <= SHORTS_MAX_ROW else SKIN_SUB)[c]
                else:
                    c = BODY_SUB.get(c, c)
            px[x, y] = palette[c]
    return im


def compose(base, overlay, dy=0):
    """Alpha-composite overlay onto a copy of base, shifted dy pixels DOWN."""
    out = base.copy()
    shifted = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shifted.paste(overlay, (0, dy), overlay)
    return Image.alpha_composite(out, shifted)


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


# ---- preview cards -----------------------------------------------------------
def contact_sheet(cells, cols, scale=8, pad=4, bg=(58, 58, 64, 255), label_h=0):
    """cells: list of (Image, ...) — lay out left-to-right, top-to-bottom."""
    if not cells:
        return Image.new("RGBA", (8, 8), bg)
    cw = max(im.width for im in cells) * scale + pad
    ch = max(im.height for im in cells) * scale + pad
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw + pad, rows * ch + pad), bg)
    for i, im in enumerate(cells):
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        x = pad + (i % cols) * cw
        y = pad + (i // cols) * ch
        sheet.paste(big, (x, y), big)
    return sheet


def walk_gif(frames, path, scale=8, ms=140):
    """Animated walk preview (nearest-upscaled)."""
    big = [f.resize((f.width * scale, f.height * scale), Image.NEAREST).convert("RGBA")
           for f in frames]
    canvas = [Image.new("RGBA", big[0].size, (58, 58, 64, 255)) for _ in big]
    for c, f in zip(canvas, big):
        c.paste(f, (0, 0), f)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    canvas[0].save(path, save_all=True, append_images=canvas[1:], duration=ms,
                   loop=0, disposal=2)
