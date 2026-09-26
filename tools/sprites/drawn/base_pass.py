"""A cleanup pass on the player base (tools/_generated/player/bases/armless_front.png, armless_side.png).

Same character, same 36x71 canvas, same pixel scale, same outline — every edge pixel stays where it was, so
everything aligned to the base (hand anchors, outfits) still lines up. What changes is how it is drawn:

  1. material map  — every pixel is sorted into hair / skin / top / shorts / eye;
  2. snap          — the original's own light-to-dark shading, softened among neighbours of the SAME material
                     (so speckle merges into clumps but edges between materials stay sharp), then snapped onto
                     that material's ramp in base_palette.py — the painted forms survive, 800 colours don't;
  3. clean-up      — lone speckles folded into their neighbours; silhouette pixels darkened into an outline;
  4. by hand       — the face (both views), the side profile, strap and legs, and all of the hair: explicit
                     pixel tables below (FRONT_HAIR, SIDE_HAIR, SIDE_HEAD, face_front, face_side).

    python3 tools/sprites/drawn/base_pass.py   # -> tools/_generated/player/reviews/2026-09-26-base-pass/

The originals are never written to. Making these the bases is the owner's call.
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from base_palette import PAL, RAMPS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[3]
BASES = ROOT / "tools/_generated/player/bases"
OUT = ROOT / "tools/_generated/player/reviews/2026-09-26-base-pass"


def load(view):
    im = Image.open(BASES / f"armless_{view}.png").convert("RGBA")
    return im, im.load()


def hsv(c):
    r, g, b = (v / 255 for v in c[:3])
    mx, mn = max(r, g, b), min(r, g, b)
    v, d = mx, mx - mn
    s = 0 if mx == 0 else d / mx
    if d == 0:
        h = 0
    elif mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60, s, v


def luma(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255

# ------------------------------------------------------------------ 1. material map

def colour_class(c):
    h, s, v = hsv(c)
    if v < 0.16:
        return "dark"
    if s < 0.20 and v > 0.86:
        return "white"
    if s < 0.36 and v > 0.55:
        return "cream"
    if s < 0.42 and v <= 0.55:
        return "creamdark"
    if 34 <= h < 52 and s < 0.62:
        return "khaki"
    if h < 24 or v < 0.5:
        return "red"      # hair, or a skin edge
    return "skin"


# Horizontal bands per view (rows, inclusive), read off the original.
BANDS = {
    "front": {"hair_bottom": 17, "face_bottom": 25, "face_left": 12, "face_right": 23,
              "top_bottom": 42, "shorts_bottom": 49},
    "side": {"hair_bottom": 17, "face_bottom": 25, "face_left": 18, "face_right": 99,
             "top_bottom": 41, "shorts_bottom": 49},
}


def material_map(view):
    """Sort every solid pixel (alpha >= 128) into a material; the hand tables below correct the rest."""
    im, px = load(view)
    W, H = im.size
    band = BANDS[view]
    mat = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            if c[3] < 128:
                continue
            k = colour_class(c)
            if y <= band["hair_bottom"] and k in ("red", "dark"):
                mat[y][x] = "hair"
            elif y <= band["face_bottom"]:
                if k == "red" and (x <= band["face_left"] or x >= band["face_right"]):
                    mat[y][x] = "hair"
                elif k in ("dark", "white"):
                    mat[y][x] = "eye"
                else:
                    mat[y][x] = "skin" if k in ("skin", "red") else "hair"
            elif y <= band["top_bottom"]:
                mat[y][x] = "top" if k in ("cream", "white", "creamdark", "khaki") else "skin"
            elif y <= band["shorts_bottom"]:
                mat[y][x] = "shorts"
            else:
                mat[y][x] = "skin"
    return mat

# ------------------------------------------------------------------ 2. snap the original's shading

QUANTILES = {  # share of each material's pixels (darkest first) given to each ramp step
    "hair": (0.13, 0.33, 0.55, 0.77, 0.92),   # -> 1 2 3 4 5 6
    "skin": (0.08, 0.20, 0.40, 0.72, 0.93),   # -> a b c d e f
    "top": (0.10, 0.24, 0.50, 0.82),          # -> T U V W X
    "shorts": (0.10, 0.28, 0.58, 0.86),       # -> K L M N P
}
SMOOTH = {"hair": 0.55, "skin": 0.35, "top": 0.45, "shorts": 0.35}   # how much a pixel takes from its neighbours
ITERS = {"hair": 2, "skin": 1, "top": 1, "shorts": 1}               # how many times


def smoothed_luma(view, mat):
    """The original's brightness, softened only among neighbours of the same material: speckle merges into
    clumps, the forms stay, and the edge between hair and face (or top and shorts) stays sharp."""
    im, px = load(view)
    H, W = len(mat), len(mat[0])
    L = [[luma(px[x, y]) for x in range(W)] for y in range(H)]
    for it in range(max(ITERS.values())):
        nxt = [row[:] for row in L]
        for y in range(H):
            for x in range(W):
                m = mat[y][x]
                if m in (None, "eye") or it >= ITERS.get(m, 0):
                    continue
                ns = [L[y + dy][x + dx] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if (dx or dy) and 0 <= x + dx < W and 0 <= y + dy < H and mat[y + dy][x + dx] == m]
                if ns:
                    a = SMOOTH[m]
                    nxt[y][x] = (1 - a) * L[y][x] + a * sum(ns) / len(ns)
        L = nxt
    return L


def snap(view, mat):
    """Each pixel keeps its place in the light-to-dark order of its material and takes the ramp step that
    place earns."""
    L = smoothed_luma(view, mat)
    H, W = len(mat), len(mat[0])
    out = [["."] * W for _ in range(H)]
    for name in ("hair", "skin", "top", "shorts"):
        ramp = RAMPS[name]
        cells = [(L[y][x], x, y) for y in range(H) for x in range(W) if mat[y][x] == name]
        vals = sorted(v for v, _, _ in cells)
        cuts = [vals[min(len(vals) - 1, int(q * len(vals)))] for q in QUANTILES[name]]
        for v, x, y in cells:
            out[y][x] = ramp[sum(1 for t in cuts if v > t)]
    for y in range(H):
        for x in range(W):
            if mat[y][x] == "eye":
                out[y][x] = "@"
    return out

# ------------------------------------------------------------------ 3. clean-up

def denoise(grid, mat, keep, passes=2):
    """Speckle only: a pixel that differs from ALL eight neighbours of its material, where at least five of
    them agree, takes their value. Strokes (two or more pixels in a line) survive."""
    H, W = len(grid), len(grid[0])
    for _ in range(passes):
        out = [row[:] for row in grid]
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                m = mat[y][x]
                if (x, y) in keep or m in (None, "eye"):
                    continue
                ns = [grid[y + dy][x + dx] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if (dx or dy) and mat[y + dy][x + dx] == m]
                if len(ns) < 6 or grid[y][x] in ns:
                    continue
                best = max(set(ns), key=ns.count)
                if ns.count(best) >= 5:
                    out[y][x] = best
        grid = out
    return grid


def darken_edges(grid, mat):
    """Silhouette pixels are at most the material's second-darkest step, the darkest on the far side (bottom,
    right) — an outline that holds the shape."""
    H, W = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for y in range(H):
        for x in range(W):
            m = mat[y][x]
            if m in (None, "eye"):
                continue
            if all(0 <= x + dx < W and 0 <= y + dy < H and mat[y + dy][x + dx] is not None
                   for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                continue
            ramp = RAMPS[m]
            if ramp.index(out[y][x]) > 1:
                lit = (x > 0 and mat[y][x - 1] is None) or (y > 0 and mat[y - 1][x] is None)
                out[y][x] = ramp[1] if lit else ramp[0]
    return out

# ------------------------------------------------------------------ 4. by hand

def apply(grid, edits):
    for (x, y), ch in edits.items():
        grid[y][x] = ch
    return grid


def rows_to_edits(rows):
    """{y: (x0, "letters")} -> {(x, y): letter}; '.' clears a pixel, ' ' leaves it alone."""
    out = {}
    for y, (x0, s) in rows.items():
        for i, ch in enumerate(s):
            if ch != " ":
                out[(x0 + i, y)] = ch
    return out


def face_front(grid, mat):
    """Eyes that look at you (the original's pupils both sat on the inner side — slightly cross-eyed), a
    highlight on the same side of each, a small mouth, a nose shadow."""
    edits = {}
    for x in (14, 15, 20, 21):            # clear the old eyes back to skin
        for y in (18, 19, 20, 21):
            mat[y][x] = "skin"
            edits[(x, y)] = "e"
    for ex in (14, 20):                    # 2x3 eyes, highlight top-left
        for dy in range(3):
            for dx in range(2):
                mat[18 + dy][ex + dx] = "eye"
                edits[(ex + dx, 18 + dy)] = "@"
        edits[(ex, 18)] = "w"
    edits[(17, 23)] = edits[(18, 23)] = "m"
    edits[(18, 21)] = "d"
    return edits


def face_side(grid, mat):
    """The side eye had no pupil, and two of its pixels were see-through: a dark eye with a highlight."""
    edits = {}
    for (x, y) in ((20, 19), (21, 19), (20, 20), (21, 20), (20, 21), (21, 21)):
        mat[y][x] = "skin"
        edits[(x, y)] = "e"
    for (x, y) in ((21, 19), (21, 20), (20, 20), (21, 21)):
        mat[y][x] = "eye"
        edits[(x, y)] = "@"
    mat[19][21] = "eye"
    edits[(21, 19)] = "w"
    return edits


FACE = {"front": face_front, "side": face_side}

# The side head in profile (facing right): fringe over the brow, eye with a pupil and a white in front of it,
# ear, nose bump, mouth, chin, neck in the jaw's shadow; then the shoulder strap as a clean two-pixel band.
SIDE_HEAD = {
    18: (19, "cdddca.2"),
    19: (19, "deeea"),
    20: (15, "2cdeee@wb"),
    21: (15, "2bdefe@eed"),
    22: (15, "2ccefffedb"),
    23: (15, "bdeeeeemb"),
    24: (14, "1bcddddca"),
    25: (15, "acccbaa"),
    26: (14, "bdWVda"),
    27: (13, "bdddWVdb"),
    28: (13, "bddddWVb"),
    29: (13, "bdeeddWVb"),
}
SIDE_MAT = {  # which material each redrawn pixel belongs to (so later passes treat it right)
    **{(x, y): "skin" for y in range(18, 26) for x in range(16, 25)},
    (26, 18): "hair", (15, 20): "hair", (15, 21): "hair", (15, 22): "hair",
    (21, 20): "eye", (21, 21): "eye", (22, 20): "eye",
    (16, 26): "top", (17, 26): "top", (17, 27): "top", (18, 27): "top", (18, 28): "top", (19, 28): "top",
    (19, 29): "top", (20, 29): "top",
}

# The hair, drawn by hand inside the original outline. Front: locks sweeping out from the crown, a sheen across
# the top, dark gaps between locks, a fringe ending in points (one tip between the eyes), and side locks kept
# DARKER than the face beside them (light side locks read as a wider face). Side: volume on the back and top,
# locks sweeping back from the crown, the fringe's dark lower edge over the brow.
FRONT_HAIR = {
    7: (10, "1 1  1223221"),
    8: (10, "212123455443211"),
    9: (11, "134566556543321"),
    10: (8, "1234554564356543321"),
    11: (8, "13454345432454343221"),
    12: (9, "144323432344323321"),
    13: (8, "1343443244323432321"),
    14: (8, "13345433543345323221"),
    15: (8, "12344323442344222321"),
    16: (8, "12334323432234223221"),
    17: (9, "123321232112321221"),
    18: (9, "2233    2     2221"),
    19: (9, "1343          2321"),
    20: (9, "1343          2321"),
    21: (10, "13           311"),
    22: (11, "12          1"),
    23: (12, "1"),
}
SIDE_HAIR = {
    8: (15, "123321"),
    9: (11, "1 12345543221"),
    10: (10, "123456545654321"),
    11: (10, "1345454345543321"),
    12: (8, "1234543443234434321"),
    13: (9, "1344323432343223432"),
    14: (8, "1243343234323433321"),
    15: (8, "1332343223322343221"),
    16: (8, "12332332232233233221"),
    17: (8, "11222322322123212211"),
    18: (9, "1123223221"),
    19: (8, "11233233221"),
    20: (10, "123322"),
    21: (9, "1123222"),
    22: (11, "12222"),
    23: (12, "112"),
    24: (14, "1"),
}


def by_hand(view, grid, mat):
    if view == "front":
        for y in (33, 34):                  # the top's right edge, mis-sorted as skin
            mat[y][23] = "top"
            grid[y][23] = "T"
        for y in range(34, 42):             # lit (left) side of the top: one outline, not two
            if grid[y][12] == "U":
                grid[y][12] = "V"
        hair = rows_to_edits(FRONT_HAIR)
    else:
        for (x, y), m in SIDE_MAT.items():
            mat[y][x] = m
        grid = apply(grid, rows_to_edits(SIDE_HEAD))
        for y in range(55, 64):             # a dark line where the far leg meets the near one
            if mat[y][18] == "skin":
                grid[y][18] = "b"
        hair = rows_to_edits(SIDE_HAIR)
        hair[(26, 18)] = "1"
    for (x, y), ch in hair.items():
        if ch in "123456":
            mat[y][x] = "hair"
    return apply(grid, hair)


def build(view):
    mat = material_map(view)
    grid = snap(view, mat)
    face = FACE[view](grid, mat)
    grid = apply(grid, face)
    grid = denoise(grid, mat, keep=set(face))
    grid = darken_edges(grid, mat)
    grid = apply(grid, {k: v for k, v in face.items() if mat[k[1]][k[0]] == "eye" or v == "m"})
    return by_hand(view, grid, mat), mat


def render(grid):
    H, W = len(grid), len(grid[0])
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = im.load()
    for y in range(H):
        for x in range(W):
            c = PAL[grid[y][x]]
            if c is not None:
                p[x, y] = c + (255,)
    return im


def grid_text(grid):
    return "\n".join("".join(r) for r in grid) + "\n"

# ------------------------------------------------------------------ review sheets + numbers

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GRASS = (78, 132, 60)


def checker(w, h, s):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            d.rectangle([x, y, x + s - 1, y + s - 1], fill=(222, 222, 222) if (x // s + y // s) % 2 else (246, 246, 246))
    return im


def sheet(pairs, path, scale=8):
    """pairs: [(view, today, new)] -> for each view, today | new at `scale`x on a checker, and each at 1x and 3x
    on grass (how the game shows them). Labels at 22pt."""
    f = ImageFont.truetype(FONT, 22)
    fs = ImageFont.truetype(FONT, 18)
    w0, h0 = pairs[0][1].size
    col = w0 * scale + 40
    out = Image.new("RGBA", (len(pairs) * 2 * col + 40, 70 + h0 * scale + 60 + h0 * 3 + 80), (250, 250, 247, 255))
    d = ImageDraw.Draw(out)
    x = 20
    for label, a, b in pairs:
        for tag, im in (("today", a), ("new", b)):
            d.text((x, 16), f"{label} — {tag}", fill=(34, 24, 32), font=f)
            bg = checker(w0 * scale, h0 * scale, scale)
            bg.alpha_composite(im.resize((w0 * scale, h0 * scale), Image.NEAREST))
            out.paste(bg, (x, 56))
            gy = 56 + h0 * scale + 30
            g = Image.new("RGBA", (w0 * 4 + 20, h0 * 3 + 20), GRASS + (255,))
            g.alpha_composite(im, (4, 10))
            g.alpha_composite(im.resize((w0 * 3, h0 * 3), Image.NEAREST), (w0 + 14, 10))
            out.paste(g, (x, gy))
            d.text((x + w0 * 4 + 30, gy + 10), "1x and 3x\non grass", fill=(90, 90, 90), font=fs)
            x += col
    out.save(path)


def compare(columns, path, s=8):
    """columns: [(label, im)] side by side at s x on a checker, labels at 22pt."""
    f = ImageFont.truetype(FONT, 22)
    w0, h0 = columns[0][1].size
    col = w0 * s + 30
    out = Image.new("RGBA", (len(columns) * col + 30, h0 * s + 80), (250, 250, 247, 255))
    d = ImageDraw.Draw(out)
    for i, (label, im) in enumerate(columns):
        x = 20 + i * col
        d.text((x, 16), label, fill=(34, 24, 32), font=f)
        bg = checker(w0 * s, h0 * s, s)
        bg.alpha_composite(im.resize((w0 * s, h0 * s), Image.NEAREST))
        out.paste(bg, (x, 56))
    out.save(path)


def lint(orig, new):
    """Colours, half-see-through pixels, lone pixels, and whether the outline moved."""
    def solid(im):
        return {(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3] >= 128}
    o, n = solid(orig), solid(new)
    lone = 0
    for (x, y) in n:
        c = new.getpixel((x, y))
        ns = [new.getpixel((x + dx, y + dy)) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)) if (x + dx, y + dy) in n]
        if len(ns) == 4 and all(v != c for v in ns) and len(set(ns)) == 1:
            lone += 1
    return {
        "colours": (len([c for c in orig.getcolors(100000) if c[1][3] > 0]),
                    len([c for c in new.getcolors(100000) if c[1][3] > 0])),
        "semi_transparent_pixels": (sum(1 for c in orig.getdata() if 0 < c[3] < 255),
                                    sum(1 for c in new.getdata() if 0 < c[3] < 255)),
        "silhouette_added": len(n - o), "silhouette_removed": len(o - n),
        "lone_pixels": lone, "size": new.size,
    }


def main():
    (OUT / "sprites").mkdir(parents=True, exist_ok=True)
    pairs, report = [], {}
    for view in ("front", "side"):
        grid, _ = build(view)
        im = render(grid)
        im.save(OUT / "sprites" / f"armless_{view}.png")
        (OUT / "sprites" / f"armless_{view}.txt").write_text(grid_text(grid))
        orig = load(view)[0]
        pairs.append((view, orig, im))
        report[view] = lint(orig, im)
    sheet(pairs, OUT / "01_today_vs_new.png")
    compare([(f"{v} today", a) for v, a, _ in pairs] + [(f"{v} new", b) for v, _, b in pairs],
            OUT / "02_side_by_side_8x.png")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
