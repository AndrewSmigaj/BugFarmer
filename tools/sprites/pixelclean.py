#!/usr/bin/env python3
"""Turn 'pixel-art-styled' gpt-image-1 output into actual clean pixel art.

The model gives us fuzzy 1024px images with anti-aliased edges, messy
near-duplicate colors, and a dark vignette toward the borders (which causes
visible grid seams on tiles). This tool fixes all three:

  1. DOWNSCALE to an integer multiple of the asset's in-game size (area-average)
     so anti-aliasing collapses into solid pixels. We clean to 2x the logical
     sprite size (=32px per cell); the scene/game then NEAREST-upscales by a
     whole number, keeping pixels crisp.
  2. PALETTE-QUANTIZE (k-means) per asset (or a shared palette across the set
     with --shared) so colors are clean and limited.
  3. DE-VIGNETTE (flat-field) for opaque tiles so center and edges match in
     brightness and copies tile seam-free.

Cleaned assets are written to tools/pixelclean_out/{Tiles,Objects}/, leaving the
originals untouched. make_scene.py --assets tools/pixelclean_out renders with them.

Usage:
  python3 pixelclean.py                 # clean all tiles + objects (per-asset palette)
  python3 pixelclean.py --shared        # one shared palette across the whole set
  python3 pixelclean.py --compare a,b,c # also write a before/after PNG for these ids
"""
import argparse
import glob
import json
import os
import numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans2
from scipy.ndimage import gaussian_filter, label

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
TILES_IN = os.path.join(RES, "Tiles")
OBJS_IN = os.path.join(RES, "Objects")
ITEMS_IN = os.path.join(RES, "Items")
ENT_DIR = os.path.join(ROOT, "nakama", "data", "entities")
# Clean IN PLACE: overwrite the canonical game sprites under Resources/{Tiles,Objects}
# (single source of truth, no side dir to hand-copy). Re-running is ~idempotent: the
# BOX downscale to the same target size and the k-means re-quantize are stable. Only
# Tiles/ and Objects/ are touched -- Player/ (hand-authored art) is never read here.
OUT = RES
PREV = os.path.join(ROOT, "tools", "_generated", "previews")

PPC = 2          # cleaned pixels per logical cell-unit (16 logical px -> 32 clean px)
TILE_PX = 32     # cleaned tile resolution (square)


def load_meta():
    meta = {}
    for fn in ("occupants.json", "placeables.json", "items.json"):
        p = os.path.join(ENT_DIR, fn)
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p)).items():
            if isinstance(v, dict):
                meta[k] = v
    return meta


def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def devignette(rgb):
    rgb = rgb.astype(np.float32)
    lum = rgb.mean(axis=2)
    sigma = max(rgb.shape[0], rgb.shape[1]) / 6.0
    illum = gaussian_filter(lum, sigma=sigma)
    gain = (illum.mean() / np.clip(illum, 1e-3, None))[..., None]
    return np.clip(rgb * gain, 0, 255).astype(np.uint8)


def downscale(arr, tw, th):
    return np.asarray(Image.fromarray(arr).resize((tw, th), Image.BOX), dtype=np.uint8)


def build_palette(rgb_pixels, k, seed=1):
    if rgb_pixels.size == 0:        # fully-transparent sprite -> nothing to quantize
        return np.zeros((1, 3))     # (caller emits an all-transparent result; batch continues)
    uniq = np.unique(rgb_pixels.reshape(-1, 3), axis=0)
    k = max(2, min(k, len(uniq)))
    centroids, _ = kmeans2(rgb_pixels.astype(np.float64), k,
                           minit="++", seed=seed, missing="warn")
    return np.clip(centroids, 0, 255)


def apply_palette(rgb, palette):
    h, w, _ = rgb.shape
    flat = rgb.reshape(-1, 3).astype(np.float64)
    d = ((flat[:, None, :] - palette[None, :, :]) ** 2).sum(axis=2)
    return palette[d.argmin(axis=1)].reshape(h, w, 3).astype(np.uint8)


def target_size(key, meta, is_tile):
    if is_tile:
        return TILE_PX, TILE_PX
    e = meta.get(key, {})
    w = int(e.get("sprite_w") or 16)
    h = int(e.get("sprite_h") or 16)
    return max(1, w * PPC), max(1, h * PPC)


def drop_detached(arr, thresh=16, keep_frac=0.10):
    """gpt-image-1 often draws a faint cast shadow / foot DETACHED below the object,
    separated by a transparent gap. alpha_trim's bbox would then span object->gap->junk
    and stretch the junk to the bottom of the frame. Keep only opaque blobs that are at
    least keep_frac of the biggest blob; zero out the small detached islands."""
    a = arr[..., 3]
    mask = a >= thresh
    lbl, n = label(mask, structure=np.ones((3, 3), int))  # 8-connectivity
    if n <= 1:
        return arr
    counts = np.bincount(lbl.ravel())
    counts[0] = 0
    biggest = counts.max()
    keep = np.isin(lbl, np.where(counts >= biggest * keep_frac)[0])
    out = arr.copy()
    out[..., 3] = np.where(keep, a, 0)
    return out


def alpha_trim(arr, thresh=16):
    """Crop to the alpha bounding box so the object fills the frame (like the
    game expects a tightly-trimmed sprite). Without this, raw gpt-image-1 output
    keeps a huge transparent margin and the object reads tiny + floats off-anchor."""
    a = arr[..., 3]
    ys, xs = np.where(a >= thresh)
    if len(xs) == 0:
        return arr
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def small_rgba(arr, tw, th, is_tile):
    if not is_tile:
        arr = drop_detached(arr)
        arr = alpha_trim(arr)
    rgb, alpha = arr[..., :3], arr[..., 3]
    if is_tile:
        rgb = devignette(rgb)
    return downscale(np.dstack([rgb, alpha]), tw, th)


def clean(arr, tw, th, is_tile, palette, k, alpha_thresh=128):
    small = small_rgba(arr, tw, th, is_tile)
    rgb_s, alpha_s = small[..., :3], small[..., 3]
    pal = palette if palette is not None else build_palette(
        rgb_s.reshape(-1, 3) if is_tile else rgb_s.reshape(-1, 3)[alpha_s.reshape(-1) >= alpha_thresh], k)
    rgb_q = apply_palette(rgb_s, pal)
    if is_tile:
        out_a = np.full((th, tw), 255, np.uint8)
    else:
        out_a = np.where(alpha_s >= alpha_thresh, 255, 0).astype(np.uint8)
        rgb_q = np.where(out_a[..., None] == 0, 0, rgb_q)
    return np.dstack([rgb_q, out_a])


def nearest_up(arr, box):
    im = Image.fromarray(arr)
    s = max(1, min(box // im.width, box // im.height))
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shared", action="store_true",
                    help="one shared palette across the whole set (more cohesive, less true color)")
    ap.add_argument("--k", type=int, default=20, help="colors per asset (or total if --shared)")
    ap.add_argument("--compare", default="", help="comma ids to also render before/after")
    ap.add_argument("--items", default="",
                    help="comma item ids: ALSO clean Resources/Items/{id}_icon.png (or {id}.png). "
                         "OPT-IN ONLY — never sweeps all of Items/, which holds legacy already-"
                         "clean 16px icons that a re-clean would upscale and mangle. Items have "
                         "no sprite_w/h, so they clean to the 16-logical default = 32px.")
    args = ap.parse_args()

    meta = load_meta()
    os.makedirs(os.path.join(OUT, "Tiles"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "Objects"), exist_ok=True)

    jobs = []  # (key, src, out, tw, th, is_tile)
    if args.items:
        # EXCLUSIVE items mode: clean only the named freshly-generated icons; do not
        # touch Tiles/Objects (or the legacy Items/) in the same run.
        for key in [k.strip() for k in args.items.split(",") if k.strip()]:
            src = os.path.join(ITEMS_IN, key + "_icon.png")
            if not os.path.exists(src):
                src = os.path.join(ITEMS_IN, key + ".png")
            if not os.path.exists(src):
                print(f"  !! no Items png for '{key}' — skipped")
                continue
            tw, th = target_size(key, meta, False)
            jobs.append((key, src, src, tw, th, False))  # clean in place
    else:
        for src in sorted(glob.glob(os.path.join(TILES_IN, "*.png"))):
            key = os.path.splitext(os.path.basename(src))[0]
            base = key.split("_v")[0]
            tw, th = target_size(base, meta, True)
            jobs.append((key, src, os.path.join(OUT, "Tiles", key + ".png"), tw, th, True))
        for src in sorted(glob.glob(os.path.join(OBJS_IN, "*.png"))):
            key = os.path.splitext(os.path.basename(src))[0]
            tw, th = target_size(key, meta, False)
            jobs.append((key, src, os.path.join(OUT, "Objects", key + ".png"), tw, th, False))

    shared_pal = None
    if args.shared:
        pool = []
        for key, src, _, tw, th, is_tile in jobs:
            s = small_rgba(load_rgba(src), tw, th, is_tile)
            px = s[..., :3].reshape(-1, 3)
            if not is_tile:
                px = px[s[..., 3].reshape(-1) >= 128]
            if len(px):
                pool.append(px)
        shared_pal = build_palette(np.concatenate(pool), args.k)
        print(f"Shared palette: {len(shared_pal)} colors")

    for key, src, dst, tw, th, is_tile in jobs:
        cleaned = clean(load_rgba(src), tw, th, is_tile, shared_pal, args.k)
        Image.fromarray(cleaned).save(dst)
    print(f"Cleaned {len(jobs)} assets -> {os.path.relpath(OUT, ROOT)}/")

    ids = [c.strip() for c in args.compare.split(",") if c.strip()]
    if ids:
        BOX, rows = 320, []
        for key, src, dst, tw, th, is_tile in jobs:
            if key not in ids:
                continue
            before = Image.open(src).convert("RGBA"); before.thumbnail((BOX, BOX), Image.LANCZOS)
            after = nearest_up(load_rgba(dst), BOX)
            row = Image.new("RGBA", (BOX * 2 + 30, BOX), (32, 32, 38, 255))
            row.alpha_composite(before, (10, (BOX - before.height) // 2))
            row.alpha_composite(after, (BOX + 20, (BOX - after.height) // 2))
            rows.append(row)
        if rows:
            comp = Image.new("RGBA", (rows[0].width, sum(r.height for r in rows) + 10 * len(rows)), (24, 24, 28, 255))
            y = 5
            for r in rows:
                comp.alpha_composite(r, (0, y)); y += r.height + 10
            out = os.path.join(PREV, "cleanup_compare.png")
            comp.convert("RGB").save(out)
            print(f"Compare -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
