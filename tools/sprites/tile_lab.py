"""tile_lab.py — measure + preview candidate ground TILES (R&D harness).

Judging "is this a good tileable ground tile?" by eye is unreliable and slow, so this scores every
candidate the same way and renders it repeated, which is the only view that reveals seams/repetition.

Metrics (all cheap, no API):
  colors            distinct RGB count (good ground tiles use few)
  base_share        fraction of the single most common color (references sit ~0.45-0.55)
  max_feature_px    largest connected blob of non-base pixels (big features = the eye locks on = visible repeat)
  edge_delta        |mean luminance of the border ring - interior| (vignette/gradient detector; ~0 is good)
  seam_x / seam_y   WRAP-edge percentile: where the wrap edge's difference falls among all interior
                    adjacent-column/row differences. ~50 => the wrap edge is indistinguishable from
                    ordinary interior texture (seamless). >90 => an outlier = a visible seam when tiled.

Usage:
  python3 tools/sprites/tile_lab.py sheet          # contact sheet of every candidate + master comparison
  python3 tools/sprites/tile_lab.py one <png>      # metrics + field render for one tile
"""
import os
import sys
import glob

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TILES = os.path.join(REPO, "tools", "_generated", "tiles")
CAND = os.path.join(TILES, "candidates")
PREV = os.path.join(TILES, "previews")


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def measure(a):
    """Score one tile (H,W,3 uint8). Returns a dict of the metrics documented above."""
    h, w = a.shape[:2]
    flat = a.reshape(-1, 3)
    cols, counts = np.unique(flat, axis=0, return_counts=True)
    base = cols[counts.argmax()]
    base_share = counts.max() / len(flat)

    # largest connected non-base blob
    non_base = ~np.all(a == base, axis=2)
    lbl, n = label(non_base, structure=np.ones((3, 3), int))
    max_feat = 0
    if n:
        sizes = np.bincount(lbl.ravel())
        sizes[0] = 0
        # report as an approximate diameter so it's comparable to "px" intuitions
        max_feat = float(np.sqrt(sizes.max()))

    L = lum(a)
    ring = np.ones((h, w), bool)
    ring[2:h - 2, 2:w - 2] = False
    edge_delta = abs(float(L[ring].mean() - L[~ring].mean()))

    # wrap-seam: is the WRAP edge unusual compared with the DISTRIBUTION of ordinary interior edges?
    # (A ratio-to-mean misfires on sparse textures where most interior pairs are identical, so use a
    # percentile rank: ~50 = the wrap edge looks like any other edge = seamless; ~100 = an outlier = seam.)
    f = a.astype(float)
    col_pairs = np.abs(np.diff(f, axis=1)).mean(axis=(0, 2))      # W-1 values
    row_pairs = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))      # H-1 values
    wrap_x = np.abs(f[:, 0] - f[:, -1]).mean()
    wrap_y = np.abs(f[0, :] - f[-1, :]).mean()
    seam_x = float((col_pairs <= wrap_x).mean() * 100)
    seam_y = float((row_pairs <= wrap_y).mean() * 100)

    return {
        "size": f"{w}x{h}", "colors": int(len(cols)), "base_share": round(float(base_share), 2),
        "max_feature_px": round(max_feat, 1), "edge_delta": round(edge_delta, 2),
        "seam_x": round(float(seam_x), 2), "seam_y": round(float(seam_y), 2),
    }


def verdict(m):
    """Plain-language read of the metrics (heuristic, for triage — the eye still decides)."""
    bad = []
    if m["seam_x"] > 90 or m["seam_y"] > 90:      # wrap edge is an outlier vs interior edges
        bad.append("SEAM")
    if m["edge_delta"] > 6:
        bad.append("vignette")
    if m["max_feature_px"] > 8:
        bad.append("big-feature")
    if m["colors"] > 24:
        bad.append("too-many-colors")
    return "OK" if not bad else "/".join(bad)


def field(a, n=5, scale=3):
    """Render the tile repeated n x n, upscaled `scale`x with NEAREST (the tiling test)."""
    h, w = a.shape[:2]
    big = np.tile(a, (n, n, 1))
    im = Image.fromarray(big, "RGB")
    return im.resize((w * n * scale, h * n * scale), Image.NEAREST)


def card(path, n=5):
    """One candidate: name, the tile zoomed, its 5x5 field, and its metrics."""
    a = load(path)
    m = measure(a)
    name = os.path.splitext(os.path.basename(path))[0]
    tile_img = Image.fromarray(a, "RGB").resize((128, 128), Image.NEAREST)
    fld = field(a, n=n, scale=2)

    pad, header = 10, 34
    W = pad + 128 + pad + fld.width + pad
    H = header + max(128, fld.height) + 26 + pad
    card_im = Image.new("RGB", (W, H), (32, 32, 38))
    d = ImageDraw.Draw(card_im)
    d.text((pad, 8), f"{name}   [{verdict(m)}]", fill=(255, 235, 160))
    card_im.paste(tile_img, (pad, header))
    card_im.paste(fld, (pad + 128 + pad, header))
    txt = (f"{m['size']}  colors={m['colors']}  base={m['base_share']}  "
           f"maxfeat={m['max_feature_px']}px  edge={m['edge_delta']}  "
           f"seam x={m['seam_x']} y={m['seam_y']}")
    d.text((pad, header + max(128, fld.height) + 6), txt, fill=(215, 215, 225))
    return card_im, m


def sheet():
    paths = sorted(glob.glob(os.path.join(CAND, "*.png")))
    if not paths:
        print("no candidates in", CAND)
        return
    os.makedirs(PREV, exist_ok=True)
    cards = []
    for p in paths:
        try:
            c, m = card(p)
            cards.append(c)
            print(f"{os.path.basename(p):32} {verdict(m):16} {m}")
        except Exception as e:
            print(f"SKIP {p}: {e}")
    W = max(c.width for c in cards)
    H = sum(c.height + 8 for c in cards) + 8
    master = Image.new("RGB", (W, H), (18, 18, 22))
    y = 8
    for c in cards:
        master.paste(c, (0, y))
        y += c.height + 8
    out = os.path.join(PREV, "_ALL_CANDIDATES.png")
    master.save(out)
    print("\nwrote", out)


def grid(cols=4, n=3, scale=2):
    """Compact comparison: every candidate as a small n x n tiled field, laid out in a grid.
    This is the view that actually lets you compare 15+ candidates at once."""
    paths = sorted(glob.glob(os.path.join(CAND, "*.png")))
    if not paths:
        print("no candidates in", CAND)
        return
    os.makedirs(PREV, exist_ok=True)
    cells = []
    for p in paths:
        a = load(p)
        m = measure(a)
        fld = field(a, n=n, scale=scale)
        cells.append((os.path.splitext(os.path.basename(p))[0], fld, m))
    cw = max(c[1].width for c in cells) + 12
    ch = max(c[1].height for c in cells) + 40
    rows = (len(cells) + cols - 1) // cols
    im = Image.new("RGB", (cw * cols, ch * rows), (18, 18, 22))
    d = ImageDraw.Draw(im)
    for i, (name, fld, m) in enumerate(cells):
        x, y = (i % cols) * cw, (i // cols) * ch
        d.text((x + 6, y + 4), name[:34], fill=(255, 235, 160))
        d.text((x + 6, y + 16), f"base={m['base_share']} seam=({m['seam_x']:.0f},{m['seam_y']:.0f}) {verdict(m)}"[:44],
               fill=(180, 200, 180))
        im.paste(fld, (x + 6, y + 32))
    out = os.path.join(PREV, "_GRID_COMPARE.png")
    im.save(out)
    print("wrote", out, f"({len(cells)} candidates)")


def one(path):
    a = load(path)
    m = measure(a)
    print(os.path.basename(path), verdict(m), m)
    os.makedirs(PREV, exist_ok=True)
    out = os.path.join(PREV, os.path.splitext(os.path.basename(path))[0] + "_field.png")
    field(a).save(out)
    print("wrote", out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    if cmd == "sheet":
        sheet()
    elif cmd == "grid":
        grid()
    elif cmd == "one":
        one(sys.argv[2])
    else:
        print(__doc__)
