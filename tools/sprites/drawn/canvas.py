"""The drawing toolkit for hand-drawn (code-drawn) pixel art.

Sprites are built from SHAPES (ellipses, polygons, rectangles, lines) on a small canvas, shaded by ONE
consistent light (top-left, toward the viewer) through height fields, then outlined and cleaned. Every
colour comes from `palette.py`. Nothing here resizes art: a sprite is drawn at its final pixel size.

Coordinates: x right, y DOWN (image space). A height field's "up" points toward the viewer.
"""
import math

import numpy as np
from PIL import Image

from . import palette as P

# Light: from the top-left and in front of the screen. Normalised once.
_L = np.array([-0.62, -0.78, 1.05], dtype=np.float64)
LIGHT = _L / np.linalg.norm(_L)


# ----------------------------------------------------------------------------- masks & height fields
def grid(w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    return xs.astype(np.float64) + 0.5, ys.astype(np.float64) + 0.5


def ellipse(w, h, cx, cy, rx, ry):
    xs, ys = grid(w, h)
    return ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0


def dome(w, h, cx, cy, rx, ry, power=1.0):
    """Height of an ellipsoid cap (0 outside). power<1 = flatter top, >1 = pointier."""
    xs, ys = grid(w, h)
    d = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    hgt = np.sqrt(np.clip(1.0 - d, 0, None))
    return hgt ** power


def rect(w, h, x0, y0, x1, y1):
    """Inclusive pixel rectangle mask."""
    m = np.zeros((h, w), bool)
    m[max(0, y0):max(0, y1 + 1), max(0, x0):max(0, x1 + 1)] = True
    return m


def polygon(w, h, pts):
    """Filled polygon mask (pixel centres inside)."""
    xs, ys = grid(w, h)
    inside = np.zeros((h, w), bool)
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        cond = ((yi > ys) != (yj > ys))
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (xj - xi) * (ys - yi) / (yj - yi + 1e-12) + xi
        inside ^= cond & (xs < xint)
        j = i
    return inside


def capsule(w, h, x0, y0, x1, y1, r):
    """Mask of a thick rounded line segment (limbs, handles)."""
    xs, ys = grid(w, h)
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / (L2 + 1e-12), 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    return (xs - px) ** 2 + (ys - py) ** 2 <= r * r


def capsule_height(w, h, x0, y0, x1, y1, r):
    """Cylinder-like height across a capsule (rounded limbs)."""
    xs, ys = grid(w, h)
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / (L2 + 1e-12), 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d2 = ((xs - px) ** 2 + (ys - py) ** 2) / (r * r)
    return np.sqrt(np.clip(1 - d2, 0, None))


def normals(hgt, strength=1.0):
    """Surface normals of a height field (x right, y down, z toward viewer)."""
    gy, gx = np.gradient(hgt * strength)
    nx, ny, nz = -gx, -gy, np.ones_like(hgt)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / ln, ny / ln, nz / ln


def lambert(hgt, strength=1.0, light=LIGHT):
    nx, ny, nz = normals(hgt, strength)
    return np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0, 1)


BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0


def quantize(value, cuts, dither=0.0, ox=0, oy=0):
    """value (0..1 array) -> ramp index array using ascending cut points.
    dither>0 blends ordered (Bayer) dithering into the thresholds — use sparingly, big surfaces only."""
    v = value.copy()
    if dither > 0:
        h, w = v.shape
        b = np.tile(BAYER4, (h // 4 + 2, w // 4 + 2))[oy % 4:oy % 4 + h, ox % 4:ox % 4 + w]
        v = v + (b - 0.5) * dither
    idx = np.zeros(v.shape, np.int32)
    for c in cuts:
        idx += (v >= c)
    return idx


# ----------------------------------------------------------------------------- tileable noise
def value_noise(w, h, cells, seed, octaves=1, wrap=True):
    """Smooth value noise in 0..1. wrap=True makes it periodic over (w, h) -> seamless tiles."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp_total = 0.0
    amp = 1.0
    c = cells
    for _ in range(octaves):
        g = rng.random((c, c))
        xs = (np.arange(w) + 0.5) / w * c
        ys = (np.arange(h) + 0.5) / h * c
        x0 = np.floor(xs).astype(int)
        y0 = np.floor(ys).astype(int)
        fx = xs - x0
        fy = ys - y0
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        if wrap:
            x1, y1 = (x0 + 1) % c, (y0 + 1) % c
            x0, y0 = x0 % c, y0 % c
        else:
            x1, y1 = np.minimum(x0 + 1, c - 1), np.minimum(y0 + 1, c - 1)
        a = g[np.ix_(y0, x0)]
        b = g[np.ix_(y0, x1)]
        cc = g[np.ix_(y1, x0)]
        d = g[np.ix_(y1, x1)]
        top = a + (b - a) * fx[None, :]
        bot = cc + (d - cc) * fx[None, :]
        out += amp * (top + (bot - top) * fy[:, None])
        amp_total += amp
        amp *= 0.5
        c *= 2
    return out / amp_total


# ----------------------------------------------------------------------------- the canvas
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), np.uint8)

    # -- painting
    def fill(self, mask, col):
        self.px[mask] = (*col, 255)

    def shade(self, mask, value, ramp_name, cuts, dither=0.0, lo=0, hi=None):
        """Paint `mask` with ramp colours chosen by `value` (0..1) through `cuts`.
        lo/hi clamp which ramp indices may be used (e.g. keep a dark object out of the brightest step)."""
        r = P.ramp(ramp_name)
        hi = len(r) - 1 if hi is None else hi
        idx = np.clip(quantize(value, cuts, dither) + lo, lo, hi)
        cols = np.array([(*c, 255) for c in r], np.uint8)
        self.px[mask] = cols[idx[mask]]

    def put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y, x] = (*col, 255)

    def line(self, x0, y0, x1, y1, col):
        """Bresenham line (1 px)."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.put(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def erase(self, mask):
        self.px[mask] = 0

    # -- queries
    def alpha(self):
        return self.px[..., 3] > 0

    def colour(self, x, y):
        return tuple(int(v) for v in self.px[y, x, :3])

    # -- finishing passes
    def outline(self, col=P.OUTLINE, light_col=None, diagonal=False):
        """Outline OUTSIDE the drawn shape. light_col (optional) is used where the outline sits on the
        top/left (lit) side — the 'selective outline' that stops sprites looking stickered-on."""
        a = self.alpha()
        pad = np.pad(a, 1)
        n4 = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        ring = n4 & ~a
        if diagonal:
            n8 = n4 | pad[:-2, :-2] | pad[:-2, 2:] | pad[2:, :-2] | pad[2:, 2:]
            ring = n8 & ~a
        if light_col is None:
            self.px[ring] = (*col, 255)
            return
        # lit side = the interior neighbour is to the right or below the outline pixel
        right = pad[1:-1, 2:]
        below = pad[2:, 1:-1]
        lit = ring & (right | below) & ~(pad[1:-1, :-2] | pad[:-2, 1:-1])
        self.px[ring & ~lit] = (*col, 255)
        self.px[lit] = (*light_col, 255)

    def inner_edge(self, mask, col):
        """Recolour the INSIDE border pixels of `mask` (seams between parts, rims)."""
        pad = np.pad(mask, 1)
        edge = mask & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        self.px[edge] = (*col, 255)

    def clean_orphans(self, passes=2):
        """Remove lone pixels: a pixel with no 4-neighbour of its colour that is surrounded (>=3 of 4)
        by one other colour takes that colour. Keeps clusters clean (pixel-art 'orphan' rule)."""
        for _ in range(passes):
            px = self.px
            h, w = self.h, self.w
            key = (px[..., 0].astype(np.int64) << 24) | (px[..., 1].astype(np.int64) << 16) | \
                  (px[..., 2].astype(np.int64) << 8) | px[..., 3].astype(np.int64)
            out = px.copy()
            changed = 0
            for y in range(h):
                for x in range(w):
                    if px[y, x, 3] == 0:
                        continue
                    k = key[y, x]
                    nb = []
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        nb.append(key[ny, nx] if 0 <= nx < w and 0 <= ny < h else -1)
                    if k in nb:
                        continue
                    vals = [v for v in nb if v > 0 and (v & 0xFF) > 0]
                    if not vals:
                        continue
                    best = max(set(vals), key=vals.count)
                    if vals.count(best) >= 3:
                        out[y, x] = [(best >> 24) & 255, (best >> 16) & 255, (best >> 8) & 255, 255]
                        changed += 1
            self.px = out
            if not changed:
                break

    def paste(self, other, dx=0, dy=0):
        """Alpha-paste another canvas (opaque pixels win)."""
        oh, ow = other.h, other.w
        for y in range(oh):
            ty = y + dy
            if not 0 <= ty < self.h:
                continue
            for x in range(ow):
                tx = x + dx
                if 0 <= tx < self.w and other.px[y, x, 3]:
                    self.px[ty, tx] = other.px[y, x]

    def copy(self):
        c = Canvas(self.w, self.h)
        c.px = self.px.copy()
        return c

    def flip_h(self):
        c = self.copy()
        c.px = c.px[:, ::-1].copy()
        return c

    def image(self):
        return Image.fromarray(self.px, "RGBA")


def from_image(im):
    im = im.convert("RGBA")
    c = Canvas(im.width, im.height)
    c.px = np.array(im, np.uint8)
    return c


def upscale(im, s):
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


# ----------------------------------------------------------------------------- the lint
def lint(im, name=""):
    """Palette membership + colour count + orphan count. Returns a dict (printed by the demo)."""
    arr = np.array(im.convert("RGBA"))
    opaque = arr[..., 3] > 0
    cols = {tuple(int(v) for v in c) for c in arr[opaque][:, :3]}
    pal = P.all_colours()
    off = [c for c in cols if c not in pal]
    # orphans: opaque pixels with no 4-neighbour of the same colour
    h, w = arr.shape[:2]
    orphans = 0
    for y in range(h):
        for x in range(w):
            if not opaque[y, x]:
                continue
            c = tuple(arr[y, x, :3])
            same = False
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and opaque[ny, nx] and tuple(arr[ny, nx, :3]) == c:
                    same = True
                    break
            if not same:
                orphans += 1
    return {"name": name, "size": f"{w}x{h}", "colours": len(cols), "off_palette": len(off),
            "orphans": orphans}
