"""Shared building blocks for the AI player-sprite pipeline.

Every function here was proven end-to-end in the refart_spike experiments. Reuses the
tested API wrapper + palette snap from the Pipeline-A tools rather than re-implementing.
"""
import os
import sys
import json
import base64
import urllib.request

import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_dilation, shift as ndshift

# --- reuse the tested Pipeline-A tooling (API wrapper, key resolution, palette snap) ---
_TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # .../tools
sys.path.insert(0, os.path.join(_TOOLS, "sprites"))
import gen_sprites as _gen          # noqa: E402  (call_api_ref/EDIT_URL/resolve_api_key)
import pixelclean as _pc            # noqa: E402  (apply_palette/build_palette)

# --- constants ---
NATIVE_W, NATIVE_H = 64, 128   # owner-chosen: preserves more render detail than 32x64
MODEL = "gpt-image-1.5"
CANVAS = "1024x1536"
QUALITY = "high"

# The mannequin is a shaded dummy in a colour NO gear uses, so extraction is just
# "keep everything that isn't this colour". GREEN is the default; MAGENTA is the
# fallback chroma for gear that is itself green.
CHROMA = {
    # name: (luminance->RGB coefficients (r_k, g_k, g_bias, b_k), detect(rgb)->bool is-mannequin)
    "green": ((0.28, 0.78, 40.0, 0.34), lambda r, g, b: (g - r > 22) & (g - b > 18)),
    "magenta": ((0.80, 0.30, 0.0, 0.80), lambda r, g, b: (r - g > 30) & (b - g > 30)),
}
DEFAULT_CHROMA = "green"

STYLE = ("Simple readable PIXEL ART, LESS DETAIL, big simple shapes, chunky hard pixel edges, no "
         "anti-aliasing, a limited muted palette, soft cel shading with only 3-4 shades, light from "
         "the TOP-LEFT. Fully TRANSPARENT background: render ONLY the character, no ground, no shadow.")


# ---------- io helpers ----------
def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def save_rgba(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(path)


def char_bbox(rgba, thresh=16):
    """Bounding box of the opaque character (rows y0,y1, cols x0,x1)."""
    a = rgba[..., 3]
    ys, xs = np.where(a >= thresh)
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


# ---------- 1. mannequin ----------
def make_mannequin(base_rgba, chroma=DEFAULT_CHROMA):
    """Recolour the base character to a shaded dummy in `chroma`, preserving luminance
    (shading) so gpt still drapes gear correctly. Transparent pixels stay transparent."""
    rk, gk, gbias, bk = CHROMA[chroma][0]
    rgb = base_rgba[..., :3].astype(np.float64)
    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    man = np.zeros_like(base_rgba)
    man[..., 0] = np.clip(L * rk, 0, 255)
    man[..., 1] = np.clip(L * gk + gbias, 0, 255)
    man[..., 2] = np.clip(L * bk, 0, 255)
    man[..., 3] = base_rgba[..., 3]
    man[base_rgba[..., 3] < 16] = 0
    return man


def is_mannequin_colour(rgb, chroma=DEFAULT_CHROMA):
    """Boolean mask: which pixels are the dummy colour (i.e. NOT gear)."""
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    return CHROMA[chroma][1](r, g, b)


# ---------- 2. masked edit (generate gear on the mannequin) ----------
def masked_edit(image_path, mask_path, prompt, ref_path=None,
                model=MODEL, size=CANVAS, quality=QUALITY, input_fidelity="high"):
    """gpt-image edit: image[] = the mannequin, mask = the paint-here region (transparent
    = editable), optional 2nd image[] = a finished view for cross-view consistency.
    Returns decoded PNG bytes. The mask is a soft hint — always composite-in-post after.
    input_fidelity is sent on gpt-image-1/1.5 (keeps the character faithful) but OMITTED on
    gpt-image-2, which rejects the parameter (it has high fidelity built in)."""
    key = _gen.resolve_api_key()
    boundary = "----bf-aipipe"
    parts = []

    def field(name, value):
        parts.append((f"--{boundary}\r\nContent-Disposition: form-data; "
                      f"name=\"{name}\"\r\n\r\n{value}\r\n").encode("utf-8"))

    def filepart(name, path, fn):
        with open(path, "rb") as f:
            b = f.read()
        parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                      f"filename=\"{fn}\"\r\nContent-Type: image/png\r\n\r\n").encode("utf-8") + b + b"\r\n")

    fields = [("model", model), ("prompt", prompt), ("size", size),
              ("quality", quality), ("n", "1")]
    g2 = "gpt-image-2" in model
    if not g2:                                           # gpt-image-2 rejects both of these:
        fields.append(("background", "transparent"))     #   no transparent bg (returns opaque -> clean in post)
        if input_fidelity:
            fields.append(("input_fidelity", input_fidelity))  #   no input_fidelity (built in)
    for k, v in fields:
        field(k, v)
    filepart("image[]", image_path, "base.png")
    if ref_path:
        filepart("image[]", ref_path, "ref.png")   # mask applies to the FIRST image only
    filepart("mask", mask_path, "mask.png")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        _gen.EDIT_URL, data=b"".join(parts),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return base64.b64decode(data["data"][0]["b64_json"])


def region_mask_png(rgba_shape, editable_bool, path):
    """Write a gpt-image mask: transparent (alpha 0) = editable, opaque = protected."""
    H, W = rgba_shape[:2]
    m = np.full((H, W, 4), (0, 0, 0, 255), np.uint8)
    m[editable_bool, 3] = 0
    save_rgba(m, path)


# ---------- 3. auto-align a render to the base (head match) ----------
def measure_shift(base_rgba, edit_rgba, search=18, down=4):
    """Return (dx, dy) that best registers `edit`'s character onto `base`, by matching the
    unmasked HEAD region on a downscaled grayscale (SSD). Robust to the per-render drift."""
    H, W = base_rgba.shape[:2]
    y0, y1, x0, x1 = char_bbox(base_rgba)
    ch = y1 - y0

    def gs(a):
        return np.asarray(Image.fromarray(a[..., :3]).convert("L").resize((W // down, H // down), Image.BOX), float)
    bg, eg = gs(base_rgba), gs(edit_rgba)
    bm = np.asarray(Image.fromarray((base_rgba[..., 3] >= 16).astype(np.uint8) * 255)
                    .resize((W // down, H // down), Image.BOX), float) >= 128
    hy0, hy1, hx0, hx1 = y0 // down, int(y0 + 0.30 * ch) // down, x0 // down, x1 // down
    best = None
    for sy in range(-search, search + 1):
        for sx in range(-search, search + 1):
            er = eg[hy0 - sy:hy1 - sy, hx0 - sx:hx1 - sx]
            br = bg[hy0:hy1, hx0:hx1]
            m = bm[hy0:hy1, hx0:hx1]
            if er.shape != br.shape or m.sum() == 0:
                continue
            d = (((er - br) ** 2) * m).sum() / m.sum()
            if best is None or d < best[0]:
                best = (d, sx, sy)
    return best[1] * down, best[2] * down


def shift_rgba(arr, dx, dy):
    return ndshift(arr, (dy, dx, 0), order=0)


def shift_mask(mask, dx, dy):
    return ndshift(mask.astype(np.uint8), (dy, dx), order=0) > 0


def _gray_small(rgba, sw, sh):
    return np.asarray(Image.fromarray(rgba[..., :3]).convert("L").resize((sw, sh), Image.BOX), float)


def measure_align(base_rgba, edit_rgba, down=4, search=14, match_band=(0.0, 0.32),
                  scales=(0.70, 0.74, 0.78, 0.82, 0.86, 0.90, 0.94, 0.97, 1.0, 1.03, 1.06,
                          1.10, 1.14, 1.18, 1.22, 1.26, 1.30, 1.34, 1.40)):
    """Robust registration: find (scale, dx, dy) by matching an ANCHOR BAND across SCALE and
    position (SSD on a downscaled grayscale) — image similarity, NOT a bbox (which gear+glow
    confound). To land the render on the base: resize edit by `scale` (centred), then shift.

    `match_band` = (lo, hi) as a fraction of character HEIGHT: the region to match on. Default
    (0.0, 0.32) = the HEAD, which is unchanged by body gear so it anchors legs/feet/torso well.
    For HEAD gear (a helmet REPLACES the head's look) pass a TORSO band, e.g. (0.34, 0.64) — the
    torso stays green in both mannequin and render, so it anchors reliably where the head can't."""
    H, W = base_rgba.shape[:2]
    y0, y1, x0, x1 = char_bbox(base_rgba); ch = y1 - y0
    sw, sh = W // down, H // down
    bg = _gray_small(base_rgba, sw, sh)
    bm = np.asarray(Image.fromarray((base_rgba[..., 3] >= 16).astype(np.uint8) * 255).resize((sw, sh), Image.BOX), float) >= 128
    lo, hi = match_band
    hy0, hy1 = int(y0 + lo * ch) // down, int(y0 + hi * ch) // down
    hx0, hx1 = x0 // down, x1 // down
    br = bg[hy0:hy1, hx0:hx1]; mm = bm[hy0:hy1, hx0:hx1]
    if mm.sum() == 0:
        return 1.0, 0, 0
    eg = _gray_small(edit_rgba, sw, sh).astype(np.uint8)
    best = None
    for s in scales:
        nw, nh = max(1, round(sw * s)), max(1, round(sh * s))
        es = np.asarray(Image.fromarray(eg).resize((nw, nh), Image.BILINEAR), float)
        cv = np.zeros((sh, sw), float)
        oy, ox = (sh - nh) // 2, (sw - nw) // 2
        sy, sx = max(0, oy), max(0, ox); ry, rx = max(0, -oy), max(0, -ox)
        hh = min(nh - ry, sh - sy); ww = min(nw - rx, sw - sx)
        cv[sy:sy + hh, sx:sx + ww] = es[ry:ry + hh, rx:rx + ww]
        for dy in range(-search, search + 1):
            for dx in range(-search, search + 1):
                er = cv[hy0 - dy:hy1 - dy, hx0 - dx:hx1 - dx]
                if er.shape != br.shape:
                    continue
                d = (((er - br) ** 2) * mm).sum() / mm.sum()
                if best is None or d < best[0]:
                    best = (d, s, dx * down, dy * down)
    return best[1], best[2], best[3]


def normalize_align(base_rgba, edit_rgba, min_scale=0.02, match_band=(0.0, 0.32)):
    """Resize the render by the measured scale (centred) then translate-align onto the base —
    correcting both gpt's scale drift AND position in one robust step. `match_band` picks the
    anchor region (see measure_align): default HEAD; pass a torso band for head gear."""
    s, dx, dy = measure_align(base_rgba, edit_rgba, match_band=match_band)
    e = edit_rgba
    if abs(s - 1.0) > min_scale:
        H, W = e.shape[:2]
        nw, nh = max(1, round(W * s)), max(1, round(H * s))
        r = np.asarray(Image.fromarray(e, "RGBA").resize((nw, nh), Image.NEAREST), np.uint8)
        cv = np.zeros((H, W, 4), np.uint8)
        oy, ox = (H - nh) // 2, (W - nw) // 2
        sy, sx = max(0, oy), max(0, ox); ry, rx = max(0, -oy), max(0, -ox)
        hh = min(nh - ry, H - sy); ww = min(nw - rx, W - sx)
        cv[sy:sy + hh, sx:sx + ww] = r[ry:ry + hh, rx:rx + ww]
        e = cv
    return shift_rgba(e, dx, dy), s, dx, dy


# ---------- 4. extract the gear as a 32x64 coverage layer ----------
def _small(arr, y0, y1, x0, x1):
    return np.asarray(Image.fromarray(arr[y0:y1 + 1, x0:x1 + 1], "RGBA").resize((NATIVE_W, NATIVE_H), Image.BOX), np.uint8)


def extract_layer(base_rgba, edit_rgba, gen_mask, chroma=DEFAULT_CHROMA,
                  hand_mask=None, palette=None, despeckle_min=3):
    """Cut the gear out of a mannequin render as a 32x64 coverage layer.

    base_rgba : the REAL (skin-coloured) locked base — the layer composites onto this.
    edit_rgba : the aligned mannequin+gear render.
    gen_mask  : the rough paint-here region (bool, full res).
    hand_mask : optional owner-drawn bool mask (full res) — when present it REPLACES the
                colour test as the silhouette (supports editing the mask by hand).
    Returns (layer_rgba_32x64, gear_bool_32x64). Extraction = inside the region AND
    (hand-mask, if given, else 'not the mannequin colour') AND opaque.
    """
    y0, y1, x0, x1 = char_bbox(base_rgba)
    comp = base_rgba.copy()
    comp[gen_mask] = edit_rgba[gen_mask]
    b = _small(base_rgba, y0, y1, x0, x1)
    c = _small(comp, y0, y1, x0, x1)

    def small_bool(m):
        return np.asarray(Image.fromarray((m[y0:y1 + 1, x0:x1 + 1].astype(np.uint8) * 255), "L")
                          .resize((NATIVE_W, NATIVE_H), Image.NEAREST)) >= 128
    region = small_bool(gen_mask)

    if palette is None:
        opq = lambda s: s[..., :3].reshape(-1, 3)[s[..., 3].reshape(-1) >= 128]
        palette = _pc.build_palette(np.concatenate([opq(b), opq(c)], 0), 22)
    csn = _pc.apply_palette(c[..., :3], palette)
    bsn = _pc.apply_palette(b[..., :3], palette)

    opaque = c[..., 3] >= 128
    if hand_mask is not None:
        keep = small_bool(hand_mask)
    else:
        keep = ~is_mannequin_colour(csn, chroma)
    gear = region & opaque & keep

    lbl, n = label(gear, structure=np.ones((3, 3), int))
    if n:
        counts = np.bincount(lbl.ravel()); counts[0] = 0
        gear = np.isin(lbl, np.where(counts >= despeckle_min)[0])

    layer = np.zeros((NATIVE_H, NATIVE_W, 4), np.uint8)
    layer[..., :3] = np.where(gear[..., None], csn, 0)
    layer[..., 3] = np.where(gear, 255, 0)
    return layer, gear, (bsn, b[..., 3])


def recomposite(base_snap_rgb, base_alpha, layer, gear_bool):
    """Stack a coverage layer onto the (palette-snapped) base — for preview/QA."""
    rec = np.dstack([base_snap_rgb, base_alpha]).astype(np.uint8)
    rec[gear_bool] = layer[gear_bool]
    return rec


def compose_layers(base_snap_rgb, base_alpha, layers):
    """Stack coverage layers onto the base in draw order (back->front). Each layer is a
    32x64 RGBA; opaque pixels overwrite. Mirrors CharacterComposer's paint order."""
    out = np.dstack([base_snap_rgb, base_alpha]).astype(np.uint8)
    for layer in layers:
        a = layer[..., 3] >= 128
        out[a] = layer[a]
    return out


def slot_region(base_rgba, slot):
    """A rough 'paint-here' bool region for a slot, from the base bbox. Generous — the
    mannequin extraction does the precise cut; this only bounds where gpt may paint."""
    H, W = base_rgba.shape[:2]
    y0, y1, x0, x1 = char_bbox(base_rgba)
    ch, cw = y1 - y0, x1 - x0
    bands = {          # (row0, row1, x-margin) as fractions of char height / width
        "head":  (0.00, 0.30, 0.06),
        "torso": (0.24, 0.66, 0.10),
        "legs":  (0.56, 1.02, 0.08),
        "feet":  (0.88, 1.04, 0.08),
        "arms":  (0.28, 0.66, 0.16),
    }
    r0, r1, mx = bands[slot]
    m = np.zeros((H, W), bool)
    xa = max(0, x0 - int(mx * cw)); xb = min(W, x1 + int(mx * cw))
    m[int(y0 + r0 * ch):min(H, int(y0 + r1 * ch)), xa:xb] = True
    return m
