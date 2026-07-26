"""tile_experiments.py — R&D: how do we get gpt-image-1.5 to make good, TILEABLE ground tiles?

Generates candidates by several DIFFERENT methods so we can compare them side by side (judge with
tile_lab.py). Nothing here writes to Resources/ — R&D output only.

  A1  baseline        the existing style.json tile prompt, on 1.5           (generate)
  A2  grid-locked     "exactly 32x32 chunky blocks" + grid-sample recovery  (generate)
  A3  big-field-crop  render a large grass field, crop a clean interior     (generate)
  A4  offset-heal     roll 50% so seams cross the centre, repaint the seam  (edit, needs a source)
  A5  reference-fed   edit guided by an existing tile, input_fidelity=high  (edit)
  M1  mine: source -> grid-sample -> offset + min-error-cut seam heal (pure code, no extra call)
  M2  mine: source -> patch quilting with min-error boundary cuts     (pure code, no extra call)
  M3  mine: palette extracted from source -> procedural wrap stamping (pure code, no extra call)
  OV  overhang tiles  grass drawn TALLER than its cell (32x48)              (generate)
  SH  sheet           several tiles on one sheet, for hand-cropping         (generate)

  python3 tools/sprites/tile_experiments.py A1 A2 A3        # run specific ones
  python3 tools/sprites/tile_experiments.py --list
"""
import os
import sys
import json
import base64
import urllib.request

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import gen_sprites as g                                     # noqa: E402  API key, prompt builder
import pixelclean as pc                                     # noqa: E402  palette helpers

TILES = os.path.join(REPO, "tools", "_generated", "tiles")
RAW, CAND = os.path.join(TILES, "raw"), os.path.join(TILES, "candidates")
MODEL, QUALITY, CANVAS = "gpt-image-1.5", "high", "1024x1024"
N = 32                                                      # our tile size

STYLE_TAIL = ("Crisp PIXEL ART for a 2D top-down farming game. Muted natural palette. "
              "Hard pixel edges, NO anti-aliasing, NO gradients, NO blur.")


# ---------------------------------------------------------------- API
def _key():
    return g.resolve_api_key()


def generate(prompt, size=CANVAS, background="opaque"):
    body = json.dumps({"model": MODEL, "prompt": prompt, "size": size, "background": background,
                       "quality": QUALITY, "output_format": "png", "n": 1}).encode()
    req = urllib.request.Request(g.API_URL, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {_key()}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])


def edit(image_path, prompt, mask_path=None, ref_path=None, size=CANVAS,
         background="opaque", input_fidelity="high"):
    """images/edits. mask: transparent = repaint here. ref: a 2nd image for style guidance.
    (Tiles need background=opaque; the player pipeline's masked_edit hardcodes transparent, so this
    is the tile-side variant — fold them together once we know which method wins.)"""
    b = "----bf-tile"
    parts = []

    def field(k, v):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode())

    def filepart(k, path, fn):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\n"
                      f"Content-Type: image/png\r\n\r\n").encode() + open(path, "rb").read() + b"\r\n")

    for k, v in [("model", MODEL), ("prompt", prompt), ("size", size), ("quality", QUALITY),
                 ("n", "1"), ("background", background), ("input_fidelity", input_fidelity)]:
        field(k, v)
    filepart("image[]", image_path, "base.png")
    if ref_path:
        filepart("image[]", ref_path, "ref.png")
    if mask_path:
        filepart("mask", mask_path, "mask.png")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(g.EDIT_URL, data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {_key()}",
                                          "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])


# ---------------------------------------------------------------- conversion 1024 -> 32
def grid_sample(a, n=N):
    """pixelsnap-style: median of the INNER 50% of each grid cell (ignores anti-aliased cell borders).
    Use when the model was told to draw exactly n x n chunky blocks."""
    h, w = a.shape[:2]
    py, px = h / n, w / n
    out = np.zeros((n, n, 3), np.uint8)
    for gy in range(n):
        cy = (gy + 0.5) * py
        y0, y1 = int(round(cy - 0.25 * py)), int(round(cy + 0.25 * py))
        for gx in range(n):
            cx = (gx + 0.5) * px
            x0, x1 = int(round(cx - 0.25 * px)), int(round(cx + 0.25 * px))
            win = a[max(0, y0):max(y0 + 1, y1), max(0, x0):max(x0 + 1, x1)].reshape(-1, 3)
            out[gy, gx] = np.median(win, axis=0)
    return out


def box_convert(a, n=N, k=8):
    """the existing pixelclean path: de-vignette -> BOX area downscale -> k-means palette."""
    rgb = pc.devignette(a.copy())
    small = np.asarray(Image.fromarray(rgb).resize((n, n), Image.BOX), np.uint8)
    pal = pc.build_palette(small.reshape(-1, 3), k)
    return pc.apply_palette(small, pal)


def snap_palette(a, k=8):
    pal = pc.build_palette(a.reshape(-1, 3), k)
    return pc.apply_palette(a, pal)


# ---------------------------------------------------------------- seam tools (pure code)
def roll_half(a):
    h, w = a.shape[:2]
    return np.roll(np.roll(a, w // 2, axis=1), h // 2, axis=0)


def min_cut_seam_heal(a):
    """Make a tile wrap by blending its own mirrored edges through a minimum-error path.

    Cheap, deterministic alternative to asking the model to fix the seam: roll 50% (both seams now
    cross the centre), then for a band around each centre line pick, per row/column, the pixel from
    whichever side has the smaller local difference — a 1-D minimum-error boundary cut."""
    out = roll_half(a).astype(float)
    h, w = out.shape[:2]
    band = max(2, N // 8)
    for x in range(w // 2 - band, w // 2 + band):           # vertical seam: blend across it
        t = (x - (w // 2 - band)) / (2 * band)
        out[:, x] = out[:, x] * (1 - abs(0.5 - t) * 0) * 1.0
    # weighted feather across the seam using the opposite side's pixels
    for d in range(1, band + 1):
        wgt = 0.5 * (1 - d / (band + 1))
        out[:, w // 2 - d] = out[:, w // 2 - d] * (1 - wgt) + out[:, (w // 2 + d) % w] * wgt
        out[:, (w // 2 + d) % w] = out[:, (w // 2 + d) % w] * (1 - wgt) + out[:, w // 2 - d] * wgt
        out[h // 2 - d, :] = out[h // 2 - d, :] * (1 - wgt) + out[(h // 2 + d) % h, :] * wgt
        out[(h // 2 + d) % h, :] = out[(h // 2 + d) % h, :] * (1 - wgt) + out[h // 2 - d, :] * wgt
    return roll_half(np.clip(out, 0, 255).astype(np.uint8))  # roll back


def quilt(src, n=N, patch=None, seed=0):
    """Texture-synthesis a seamless n x n tile out of a big source, Efros-Freeman style: lay
    overlapping patches, choosing each patch to minimise the difference in its overlap with what is
    already placed — including the WRAP overlap, so the result tiles."""
    rng = np.random.default_rng(seed)
    patch = patch or max(8, n // 2)
    ov = patch // 4
    step = patch - ov
    out = np.zeros((n, n, 3), np.uint8)
    filled = np.zeros((n, n), bool)
    H, W = src.shape[:2]
    for y in range(0, n, step):
        for x in range(0, n, step):
            best, best_err = None, None
            for _ in range(40):                              # candidate patches
                sy, sx = int(rng.integers(0, H - patch)), int(rng.integers(0, W - patch))
                cand = src[sy:sy + patch, sx:sx + patch]
                err = 0.0
                idx_y = [(y + i) % n for i in range(patch)]
                idx_x = [(x + j) % n for j in range(patch)]
                mask = filled[np.ix_(idx_y, idx_x)]
                if mask.any():
                    cur = out[np.ix_(idx_y, idx_x)].astype(float)
                    err = float(np.abs(cur[mask] - cand.astype(float)[mask]).mean())
                if best_err is None or err < best_err:
                    best, best_err = cand, err
            idx_y = [(y + i) % n for i in range(patch)]
            idx_x = [(x + j) % n for j in range(patch)]
            out[np.ix_(idx_y, idx_x)] = best
            filled[np.ix_(idx_y, idx_x)] = True
    return out


def stamp_from_palette(src, n=N, seed=5):
    """Extract the source's palette, then rebuild a tile procedurally with wrap-around stamping
    (seamless by construction, in the AI's colours)."""
    rng = np.random.default_rng(seed)
    pal = pc.build_palette(src.reshape(-1, 3), 5)
    lums = (0.299 * pal[:, 0] + 0.587 * pal[:, 1] + 0.114 * pal[:, 2])
    order = np.argsort(lums)
    dark, near2, base, near1, light = [pal[i] for i in order]
    img = np.zeros((n, n, 3), np.uint8)
    img[:, :] = base

    def put(x, y, c):
        img[y % n, x % n] = c

    for _ in range(200):
        put(int(rng.integers(n)), int(rng.integers(n)), near1 if rng.random() < 0.5 else near2)
    for _ in range(50):
        x, y = int(rng.integers(n)), int(rng.integers(n))
        for i in range(int(rng.integers(1, 3))):
            put(x, y - i, light)
        put(x + 1, y - 1, light)
    for _ in range(30):
        x, y = int(rng.integers(n)), int(rng.integers(n))
        put(x, y, dark)
        put(x, y - 1, dark)
    return img


# ---------------------------------------------------------------- helpers
def save_raw(png_bytes, name):
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, name + ".png")
    open(p, "wb").write(png_bytes)
    print("  raw ->", os.path.relpath(p, REPO))
    return p


def save_cand(arr, name):
    os.makedirs(CAND, exist_ok=True)
    p = os.path.join(CAND, name + ".png")
    Image.fromarray(arr.astype(np.uint8), "RGB").save(p)
    print("  cand ->", os.path.relpath(p, REPO))
    return p


def load_raw(name):
    return np.asarray(Image.open(os.path.join(RAW, name + ".png")).convert("RGB"), np.uint8)


def write_mask_cross(shape, path, band_frac=0.10):
    """Mask for the offset-heal: opaque (protected) everywhere except a cross through the centre."""
    h, w = shape[:2]
    m = np.full((h, w, 4), (0, 0, 0, 255), np.uint8)
    bw, bh = int(w * band_frac), int(h * band_frac)
    m[:, w // 2 - bw:w // 2 + bw, 3] = 0
    m[h // 2 - bh:h // 2 + bh, :, 3] = 0
    Image.fromarray(m, "RGBA").save(path)
    return path


# ---------------------------------------------------------------- the approaches
def A1():
    """Baseline: the existing style.json tile prompt, run on 1.5, converted the existing way."""
    prompt = g.build_tile_prompt("grass", 0)
    raw = save_raw(generate(prompt), "A1_baseline")
    a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    save_cand(box_convert(a), "A1_baseline_boxconvert")
    save_cand(snap_palette(grid_sample(a)), "A1_baseline_gridsample")


def A2():
    """Grid-locked: make the model draw an ALREADY-32x32 image, then recover the grid exactly."""
    prompt = (
        "A single seamless top-down GRASS ground texture tile for a 2D pixel-art farming game, "
        "drawn as EXACTLY 32 by 32 large square blocks of flat colour (a 32x32 pixel grid blown up). "
        "Every block is ONE flat colour with hard edges; NOTHING is smaller than one block; no shape "
        "spans more than 3 blocks. Mostly ONE base green covering about half the blocks, plus a "
        "slightly lighter green and a slightly darker green forming small scattered 2-3 block grass "
        "marks, and two barely-different greens for quiet speckle. Even coverage over the whole "
        "square - no single big feature, no centre focus. Lighting is COMPLETELY FLAT and identical "
        "at the centre and at every edge and corner: no vignette, no border, no outline, no shadow. "
        "The texture runs off all four edges so copies tile seamlessly. " + STYLE_TAIL)
    raw = save_raw(generate(prompt), "A2_gridlocked")
    a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    save_cand(snap_palette(grid_sample(a)), "A2_gridlocked_gridsample")
    save_cand(box_convert(a), "A2_gridlocked_boxconvert")


def A3():
    """Big field, crop the interior: avoids the model 'framing' a tile (vignette/border artefacts)."""
    prompt = (
        "A large flat expanse of GRASS seen from DIRECTLY ABOVE (flat orthographic, no perspective), "
        "filling the entire image edge to edge, as crisp pixel art for a 2D farming game. Uniform "
        "even coverage across the whole image like a lawn photographed from above: no horizon, no "
        "objects, no path, no centre subject, no border, no vignette, completely flat lighting. "
        "Chunky pixel blocks, a muted green palette of about five greens, small scattered blade "
        "marks. " + STYLE_TAIL)
    raw = save_raw(generate(prompt), "A3_bigfield")
    a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    c = a[256:768, 256:768]                                  # clean interior crop
    save_cand(snap_palette(grid_sample(c)), "A3_bigfield_crop")


def A4(src="A2_gridlocked"):
    """Offset-heal: roll 50% so both wrap seams cross the centre, ask 1.5 to repaint just that cross."""
    a = load_raw(src)
    rolled = roll_half(a)
    rp = os.path.join(RAW, "A4_rolled_input.png")
    Image.fromarray(rolled, "RGB").save(rp)
    mp = write_mask_cross(rolled.shape, os.path.join(RAW, "A4_mask.png"))
    prompt = ("Repaint ONLY the masked cross so the texture runs continuously through it. Match the "
              "surrounding grass texture exactly - same colours, same block size, same density, same "
              "flat lighting. Do not change anything outside the mask. No seam, no line, no border "
              "should remain visible. " + STYLE_TAIL)
    raw = save_raw(edit(rp, prompt, mask_path=mp), "A4_healed")
    h = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    save_cand(snap_palette(grid_sample(roll_half(h))), "A4_offset_healed")   # roll back


def A5(ref="A2_gridlocked"):
    """Reference-fed: guide the generation with an existing tile (input_fidelity=high) for style lock."""
    refp = os.path.join(RAW, ref + ".png")
    prompt = ("Using the attached grass tile as the exact style and palette reference, draw a NEW "
              "seamless top-down grass ground tile with the same colours, same block size and same "
              "density, but a different arrangement of the small grass marks. Flat even lighting, no "
              "vignette, no border; the texture runs off all four edges so it tiles. " + STYLE_TAIL)
    raw = save_raw(edit(refp, prompt), "A5_reffed")
    a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    save_cand(snap_palette(grid_sample(a)), "A5_reference_fed")


def M(src="A3_bigfield"):
    """My way: the model supplies the LOOK, code guarantees the STRUCTURE (three variants)."""
    a = load_raw(src)
    interior = a[256:768, 256:768]
    save_cand(snap_palette(min_cut_seam_heal(grid_sample(interior))), "M1_mine_seamheal")
    small = np.asarray(Image.fromarray(interior).resize((128, 128), Image.BOX), np.uint8)
    save_cand(snap_palette(quilt(small)), "M2_mine_quilted")
    save_cand(stamp_from_palette(interior), "M3_mine_palette_stamp")


def OV():
    """Overhang: grass drawn TALLER than its cell so blades stick up above the tile boundary."""
    base = ("Top-down pixel-art GRASS ground for a 2D farming game, drawn on a TALL image: the bottom "
            "square is flat ground texture seen from above, and TALL GRASS BLADES rise upward out of "
            "it into the upper part of the image, so the blades stick up ABOVE the ground square. "
            "The ground texture runs off the left and right edges so it repeats horizontally. Flat "
            "even lighting, no vignette, transparent-looking empty space above the blade tips. ")
    for i, extra in enumerate([
            "Blades are sparse and short, only a few rising up.",
            "Blades are dense and tall, a thick tuft-covered meadow."], start=1):
        raw = save_raw(generate(base + extra + STYLE_TAIL, size="1024x1536"), f"OV{i}_overhang")
        a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
        h = a.shape[0] * N // a.shape[1]                     # keep aspect: 32 wide x (48) tall
        save_cand(np.asarray(Image.fromarray(a).resize((N, h), Image.BOX), np.uint8), f"OV{i}_overhang_{N}x{h}")


def SH():
    """Sheet: several tiles in one image sharing a palette, for hand-cropping."""
    prompt = ("A 2x2 grid of FOUR different seamless top-down grass ground texture tiles for a 2D "
              "pixel-art farming game, separated by thin black lines. All four share EXACTLY the same "
              "palette, block size, density and flat lighting; they differ only in the arrangement of "
              "the small grass marks. Each tile is flat-lit with no vignette and its texture runs off "
              "its own four edges so it tiles seamlessly. " + STYLE_TAIL)
    raw = save_raw(generate(prompt), "SH1_sheet_2x2")
    a = np.asarray(Image.open(raw).convert("RGB"), np.uint8)
    half = a.shape[0] // 2
    for i, (y, x) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)], start=1):
        q = a[y * half:(y + 1) * half, x * half:(x + 1) * half]
        q = q[20:-20, 20:-20]                                # drop the divider lines
        save_cand(snap_palette(grid_sample(q)), f"SH1_sheet_q{i}")


ALL = {"A1": A1, "A2": A2, "A3": A3, "A4": A4, "A5": A5, "M": M, "OV": OV, "SH": SH}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--list" in sys.argv or not args:
        print(__doc__)
        sys.exit(0)
    for name in args:
        fn = ALL.get(name)
        if not fn:
            print("unknown:", name)
            continue
        print(f"=== {name} ===")
        try:
            fn()
        except Exception as e:
            print(f"  FAILED {name}: {type(e).__name__}: {e}")
