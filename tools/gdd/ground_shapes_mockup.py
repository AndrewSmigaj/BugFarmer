"""Mock-up for the owner: laying shaped ground by hand — what the player sees.

Panels (all in the game's own tiles, drawn big so the details read):
  1  The shape wheel: T opens a small wheel of shape pictures at the cursor — full in the middle, the four diagonals
     at the corners, the four halves at the sides. Click one; it stays selected.
  2  Laying: a see-through ghost shows exactly what will be laid, with a tick and the cost.
  3  Aiming by pointing (an option on big screens): the part of the square under the pointer sets the direction.
  4  A refusal: a cross and the reason, never colour alone.
  5  The shovel's on-screen choice: ground (R) and shape (T).
  6  What it builds: a diagonal road (full squares + diagonals) beside a checkerboard (full squares only).

Every see-through part is drawn on its own layer and composited, so nothing overwrites what is under it.
Free (no image API). Usage: python3 tools/gdd/ground_shapes_mockup.py
Writes tools/_generated/previews/examples/ground-edges/shapes_mockup.png (git-ignored; on disk).
For docs/product/investigations/research-2026-09-29/laying-ground-manual.md.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TILES = f"{ROOT}/BugFarmerClient/Assets/Resources/Tiles"
OUT = f"{ROOT}/tools/_generated/previews/examples/ground-edges/shapes_mockup.png"
P = 32
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_H, F_L, F_S, F_XS = (ImageFont.truetype(BOLD, 30), ImageFont.truetype(BOLD, 24), ImageFont.truetype(REG, 22),
                       ImageFont.truetype(BOLD, 18))
F_NOTE = ImageFont.truetype(REG, 18)
INK, INK2, BG = (34, 24, 32), (74, 68, 82), (236, 240, 227)
HILITE = (255, 214, 64)
SCALE = 4                     # panels 1-4 show three squares across at 4x
N = P * SCALE                 # one square, in panel pixels

def tile(name):
    im = Image.open(f"{TILES}/{name}.png").convert("RGBA")
    return im.resize((P, P), Image.NEAREST) if im.size != (P, P) else im

GRASS, STONE = tile("grass"), tile("stone_path")

def shape_poly(kind, where, n):
    """The part of an n-by-n square the new ground covers (y down). where = ne/nw/se/sw or n/e/s/w."""
    h = n / 2
    if kind == "full":
        return [(0, 0), (n, 0), (n, n), (0, n)]
    if kind == "diagonal":   # the triangle holding the named corner
        return {"ne": [(0, 0), (n, 0), (n, n)], "nw": [(0, 0), (n, 0), (0, n)],
                "se": [(n, 0), (n, n), (0, n)], "sw": [(0, 0), (0, n), (n, n)]}[where]
    if kind == "half":
        return {"n": [(0, 0), (n, 0), (n, h), (0, h)], "s": [(0, h), (n, h), (n, n), (0, n)],
                "e": [(h, 0), (n, 0), (n, n), (h, n)], "w": [(0, 0), (h, 0), (h, n), (0, n)]}[where]

def layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))

def field(w, h, scale):
    img = Image.new("RGBA", (w * P, h * P))
    for x in range(w):
        for y in range(h):
            img.paste(GRASS, (x * P, y * P))
    return img.resize((w * P * scale, h * P * scale), Image.NEAREST)

def lay(img, sx, sy, poly, n, alpha=255):
    """Put stone over part of the square whose top-left pixel is (sx, sy), composited on its own layer."""
    lyr = layer(img.size)
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).polygon(poly, fill=alpha)
    lyr.paste(STONE.resize((n, n), Image.NEAREST), (sx, sy), m)
    return Image.alpha_composite(img, lyr)

def draw_on(img, fn):
    """Draw with fn(ImageDraw) on a separate see-through layer, then composite it, so alpha blends."""
    lyr = layer(img.size)
    fn(ImageDraw.Draw(lyr, "RGBA"))
    return Image.alpha_composite(img, lyr)

def cursor(img, x, y, s=1.4):
    pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
    return draw_on(img, lambda d: d.polygon([(x + a * s, y + b * s) for a, b in pts],
                                            fill=(255, 255, 255, 255), outline=(0, 0, 0, 255)))

def tag(img, x, y, text):
    def f(d):
        w = d.textlength(text, font=F_XS)
        d.rounded_rectangle([x - 6, y - 4, x + w + 6, y + 24], radius=6, fill=(20, 16, 24, 210))
        d.text((x, y), text, font=F_XS, fill=(255, 255, 255, 255))
    return draw_on(img, f)

def icon(kind, where, s):
    """A shape picture: a grass square with the stone part."""
    im = GRASS.resize((s, s), Image.NEAREST).copy()
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).polygon(shape_poly(kind, where, s), fill=255)
    im.paste(STONE.resize((s, s), Image.NEAREST), (0, 0), m)
    return im

def base_panel():
    img = field(3, 3, SCALE)
    return lay(img, 0, N, shape_poly("full", None, N), N)          # a path running in from the left

def outline_ghost(img, ox, oy, kind, where):
    return draw_on(img, lambda d: (d.polygon([(ox + a, oy + b) for a, b in shape_poly(kind, where, N)],
                                             outline=(255, 255, 255, 255), width=3),
                                   d.rectangle([ox, oy, ox + N - 1, oy + N - 1], outline=(0, 0, 0, 255), width=4)))

def panel_wheel():
    img = base_panel()
    cx, cy = int(1.5 * N), int(1.5 * N)
    r, s = 118, 60
    img = draw_on(img, lambda d: d.ellipse([cx - r - 44, cy - r - 44, cx + r + 44, cy + r + 44],
                                           fill=(20, 16, 24, 170), outline=(230, 220, 190, 255), width=3))
    slots = [("full", None, 0.0, 0.0)]
    for where, ang in (("ne", -45), ("nw", -135), ("se", 45), ("sw", 135),
                       ("n", -90), ("s", 90), ("e", 0), ("w", 180)):
        kind = "diagonal" if len(where) == 2 else "half"
        slots.append((kind, where, r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))))
    for kind, where, dx, dy in slots:
        x0, y0 = int(cx + dx - s / 2), int(cy + dy - s / 2)
        img.paste(icon(kind, where, s), (x0, y0))
        chosen = (kind == "diagonal" and where == "sw")
        pad = 5 if chosen else 1
        img = draw_on(img, lambda d, x0=x0, y0=y0, pad=pad, chosen=chosen: d.rectangle(
            [x0 - pad, y0 - pad, x0 + s + pad - 1, y0 + s + pad - 1],
            outline=(HILITE + (255,)) if chosen else (230, 220, 190, 255), width=4 if chosen else 2))
    img = cursor(img, cx - 0.62 * r + 26, cy + 0.62 * r + 26)   # on the chosen slice, beside its picture
    return img, "1. T opens the shape wheel at\n   the cursor; click a shape and\n   it stays selected"

def panel_lay():
    img = base_panel()
    ox = oy = N
    img = lay(img, ox, oy, shape_poly("diagonal", "sw", N), N, alpha=215)          # the ghost: tapers the path's end
    img = outline_ghost(img, ox, oy, "diagonal", "sw")
    img = cursor(img, ox + 0.30 * N, oy + 0.62 * N)
    img = tag(img, ox + 0.05 * N, oy + N + 14, "✓ Stone path · 1 stone")
    return img, "2. The ghost shows exactly\n   what will be laid, with a\n   tick and the cost"

def panel_point():
    img = base_panel()
    ox = oy = N
    h = N / 2
    zones = {"nw": [(0, 0), (h, 0), (h, h), (0, h)], "ne": [(h, 0), (N, 0), (N, h), (h, h)],
             "sw": [(0, h), (h, h), (h, N), (0, N)], "se": [(h, h), (N, h), (N, N), (h, N)]}
    img = lay(img, ox, oy, shape_poly("diagonal", "ne", N), N, alpha=215)          # the ghost first
    def z(d):
        for k, poly in zones.items():
            pts = [(ox + a, oy + b) for a, b in poly]
            d.polygon(pts, outline=(HILITE + (255,)) if k == "ne" else (255, 255, 255, 120), width=4 if k == "ne" else 2)
    img = draw_on(img, z)
    img = outline_ghost(img, ox, oy, "diagonal", "ne")
    img = cursor(img, ox + 0.78 * N, oy + 0.16 * N)
    return img, "3. Option on big screens:\n   point at a corner, and\n   that corner is filled"

def panel_refuse():
    img = field(3, 3, SCALE)
    img = draw_on(img, lambda d: d.rectangle([3, 3, 3 * N - 4, 3 * N - 4], outline=(200, 80, 60, 255), width=6))
    ox = oy = N
    img = lay(img, ox, oy, shape_poly("diagonal", "sw", N), N, alpha=110)
    def x(d):
        d.rectangle([ox, oy, ox + N - 1, oy + N - 1], outline=(200, 60, 50, 255), width=5)
        d.line([ox + 24, oy + 24, ox + N - 24, oy + N - 24], fill=(200, 60, 50, 255), width=10)
        d.line([ox + N - 24, oy + 24, ox + 24, oy + N - 24], fill=(200, 60, 50, 255), width=10)
    img = draw_on(img, x)
    img = cursor(img, ox + 0.62 * N, oy + 0.55 * N)
    img = tag(img, 14, 12, "Someone else's plot")
    img = tag(img, ox + 0.05 * N, oy + N + 14, "✗ Not your plot")
    return img, "4. A refusal shows a cross\n   and the reason, never\n   colour alone"

def panel_hud():
    img = Image.new("RGBA", (3 * N, 3 * N), (46, 40, 52, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([24, 24, 212, 212], radius=14, fill=(70, 62, 80, 255), outline=(230, 220, 190, 255), width=4)
    d.text((36, 34), "Shovel", font=F_L, fill=(240, 236, 220))
    img.paste(STONE.resize((72, 72), Image.NEAREST), (36, 74))
    img.paste(icon("diagonal", "sw", 72), (124, 74))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((58, 160), "R", font=F_L, fill=HILITE)
    d.text((150, 160), "T", font=F_L, fill=HILITE)
    d.text((24, 236), "Stone path · Diagonal", font=F_S, fill=(240, 236, 220))
    d.text((24, 268), "(the same words sit by the", font=F_NOTE, fill=(200, 196, 180))
    d.text((24, 292), "cursor; every key can be", font=F_NOTE, fill=(200, 196, 180))
    d.text((24, 316), "changed in settings)", font=F_NOTE, fill=(200, 196, 180))
    return img, "5. The choice is always on\n   screen: R the ground,\n   T the shape"

def panel_build():
    scale, w, h = 2, 13, 7
    n = P * scale
    img = field(w, h, scale)
    for x in range(0, 7):                       # a stepped road, two squares thick, running up to the right
        y = 6 - x
        for cx in (x, x + 1):
            img = lay(img, cx * n, y * n, shape_poly("full", None, n), n)
    for x in range(0, 7):                       # a diagonal in each step, along both edges
        y = 6 - x
        if y - 1 >= 0:
            img = lay(img, x * n, (y - 1) * n, shape_poly("diagonal", "se", n), n)
        if y + 1 < h:
            img = lay(img, (x + 1) * n, (y + 1) * n, shape_poly("diagonal", "nw", n), n)   # under the right-hand square
    for x in range(9, 13):
        for y in range(2, 6):
            if (x + y) % 2 == 0:
                img = lay(img, x * n, y * n, shape_poly("full", None, n), n)
    return img, "6. A diagonal road (squares\n   + diagonals) beside a\n   checkerboard (squares)"

panels = [panel_wheel(), panel_lay(), panel_point(), panel_refuse(), panel_hud(), panel_build()]
GAP, LABEL_H, TOP = 30, 112, 150
cw = 3 * N
W = max(GAP + 3 * (cw + GAP), GAP + 2 * (cw + GAP) + panels[5][0].width + GAP)
H = TOP + 2 * (cw + LABEL_H + GAP) + 110
sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)
d.text((GAP, 20), "Laying shaped ground by hand", font=F_H, fill=INK)
d.text((GAP, 62), "R picks the ground and T the shape, which stays selected. A see-through ghost shows exactly what",
       font=F_S, fill=INK2)
d.text((GAP, 90), "will be laid, on top of what is there. It works the same on every screen and on a gamepad.",
       font=F_S, fill=INK2)
for i, (img, lab) in enumerate(panels[:3]):
    x = GAP + i * (cw + GAP)
    sheet.paste(img.convert("RGB"), (x, TOP))
    d.multiline_text((x, TOP + cw + 10), lab, font=F_L, fill=INK, spacing=4)
y2 = TOP + cw + LABEL_H + GAP
for i, (img, lab) in enumerate(panels[3:]):
    x = GAP + i * (cw + GAP)
    sheet.paste(img.convert("RGB"), (x, y2))
    d.multiline_text((x, y2 + img.height + 10), lab, font=F_L, fill=INK, spacing=4)
d.text((GAP, H - 78), "Also: a rotate key turns the chosen shape a quarter turn (twice for the other edge of a road), a copy",
       font=F_S, fill=INK2)
d.text((GAP, H - 48), "key sets the shovel to a square's ground and shape, and undo takes back your last laying.",
       font=F_S, fill=INK2)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sheet.save(OUT)
print(OUT, sheet.size)
