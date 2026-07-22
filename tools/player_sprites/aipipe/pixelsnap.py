"""pixelsnap — recover the TRUE low-res pixel grid from a gpt-image render of pixel art.

gpt-image draws each logical "pixel" as a ~NxN block at 1024px, with anti-aliased cell borders
and a NON-integer cell pitch. Area-downscaling averages across those borders and muddies colours.
This finds the grid (pitch + corner) and samples the MEDIAN of the inner 50% of each cell, which
ignores the AA borders and recovers crisp, near-exact pixels. (Approach per Fable's description.)

    python pixelsnap.py in.png out.png --auto                 # estimate pitch + corner, print them
    python pixelsnap.py in.png out.png --pitch 16.0 --x0 6 --y0 4
    python pixelsnap.py in.png out.png --auto --width 64 --height 128   # force output grid size
    python pixelsnap.py in.png out.png --auto --palette 24    # snap to the 24 most-frequent colours
    python pixelsnap.py in.png out.png --auto --debug         # also write in.grid.png (grid overlay)

Why libraries fail: they assume an integer downscale factor (dead on arrival for a float pitch)
and use nearest/mean (drags in AA borders). The load-bearing bits here: float pitch, median of the
inner 50%, and harmonic-safe pitch detection (a comb at 2x the true pitch also lands on grid lines,
so we take the SMALLEST pitch that scores near-max — the fundamental)."""
import argparse
import numpy as np
from PIL import Image, ImageDraw


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"), float)


def edge_energy(img):
    """Per-boundary edge energy along x (columns) and y (rows). RGB is PREMULTIPLIED by alpha so a
    non-transparent BACKGROUND gradient in the RGB channel (gpt-image often returns one even where
    alpha=0) contributes nothing — only the character's colour edges + its silhouette count.
    Returns (ex length W-1, ey length H-1)."""
    a = img[..., 3:4] / 255.0
    pm = np.concatenate([img[..., :3] * a, img[..., 3:4]], axis=2)   # premult RGB + alpha
    dx = np.abs(np.diff(pm, axis=1)).sum(axis=2).sum(axis=0)         # W-1
    dy = np.abs(np.diff(pm, axis=0)).sum(axis=2).sum(axis=1)         # H-1
    return dx, dy


def _comb_avg(e, p):
    """Best-phase AVERAGE energy per comb tooth at pitch p. True pitch and its multiples score
    ~equal (every tooth on a real boundary); a sub-multiple p/2 scores lower (half the teeth land
    inside cells). So the fundamental = the SMALLEST pitch that scores near the max."""
    best = 0.0
    for phase in np.linspace(0, p, max(4, int(p * 3)), endpoint=False):
        idx = np.round(np.arange(phase, len(e), p)).astype(int)
        idx = idx[(idx >= 0) & (idx < len(e))]
        if len(idx) >= 3:
            best = max(best, float(e[idx].mean()))
    return best


def _best_phase(e, p):
    best_s, best_ph = -1.0, 0.0
    for phase in np.linspace(0, p, max(8, int(p * 6)), endpoint=False):
        idx = np.round(np.arange(phase, len(e), p)).astype(int)
        idx = idx[(idx >= 0) & (idx < len(e))]
        if len(idx) >= 3 and e[idx].mean() > best_s:
            best_s, best_ph = float(e[idx].mean()), float(phase)
    return best_ph


def _ongrid_frac(e, p, tol=1):
    """Best-phase FRACTION of total edge energy that lands within +/-tol px of a grid line at
    pitch p. Robust to flat regions (sparse edges): the true pitch puts ~all edges on lines
    (frac~1); 2x the pitch misses half the edges (frac~0.5); divisors p/2, p/3 also ~1 but are
    smaller. So the fundamental = the LARGEST pitch scoring near-max."""
    total = e.sum() + 1e-9
    best = 0.0
    for phase in np.linspace(0, p, max(8, int(p * 4)), endpoint=False):
        lines = np.round(np.arange(phase, len(e), p)).astype(int)
        mask = np.zeros(len(e), bool)
        for t in range(-tol, tol + 1):
            idx = lines + t
            mask[idx[(idx >= 0) & (idx < len(e))]] = True
        best = max(best, float(e[mask].sum() / total))
    return best


def detect_pitch(signals, pmin=8.0, pmax=90.0, rel=0.9):
    """Fundamental pitch via on-grid energy fraction, summed over the given 1D signals (pass BOTH
    ex and ey to force a SQUARE grid — gpt draws square logical pixels, and using both axes' signal
    is far more robust than either alone). Take the LARGEST pitch scoring >= rel*max (rejects 2x/3x
    harmonics; divisors are smaller so lose the tie), then fine-tune with tooth energy."""
    if not isinstance(signals, (list, tuple)):
        signals = [signals]
    ps = np.arange(pmin, pmax, 0.5)
    fr = np.array([sum(_ongrid_frac(e, p) for e in signals) for p in ps])
    passing = ps[fr >= rel * fr.max()]
    p_coarse = float(passing.max()) if len(passing) else float(ps[fr.argmax()])
    fine = np.arange(max(pmin, p_coarse - 1.5), min(pmax, p_coarse + 1.5), 0.05)
    p = float(fine[np.argmax([sum(_comb_avg(e, q) for e in signals) for q in fine])])
    return p


def sample(img, px, py, x0, y0, nx, ny):
    """Median of the inner 50% of each cell -> (ny, nx, 4) uint8."""
    H, W = img.shape[:2]
    out = np.zeros((ny, nx, 4), np.uint8)
    for gy in range(ny):
        cy = y0 + (gy + 0.5) * py
        ylo, yhi = int(round(cy - 0.25 * py)), int(round(cy + 0.25 * py))
        ylo, yhi = max(0, ylo), min(H, max(ylo + 1, yhi))
        for gx in range(nx):
            cx = x0 + (gx + 0.5) * px
            xlo, xhi = int(round(cx - 0.25 * px)), int(round(cx + 0.25 * px))
            xlo, xhi = max(0, xlo), min(W, max(xlo + 1, xhi))
            win = img[ylo:yhi, xlo:xhi].reshape(-1, 4)
            if win.size:
                out[gy, gx] = np.round(np.median(win, axis=0)).astype(np.uint8)
    return out


def palette_snap(out, k):
    """Mode-based: map every opaque pixel to the nearest of the k MOST FREQUENT colours (not
    centroid quantization, which averages and smears)."""
    op = out[..., 3] > 128
    cols = out[op][:, :3]
    if len(cols) == 0:
        return out
    uniq, counts = np.unique(cols, axis=0, return_counts=True)
    pal = uniq[np.argsort(-counts)[:k]].astype(int)
    flat = cols.astype(int)
    d = ((flat[:, None, :] - pal[None, :, :]) ** 2).sum(2)
    snapped = pal[d.argmin(1)].astype(np.uint8)
    res = out.copy()
    res[op, :3] = snapped
    return res


def debug_overlay(img, px, py, x0, y0, path):
    im = Image.fromarray(img.astype(np.uint8), "RGBA").convert("RGBA")
    d = ImageDraw.Draw(im)
    H, W = img.shape[:2]
    x = x0
    while x < W:
        d.line([(x, 0), (x, H)], fill=(255, 0, 255, 200), width=1); x += px
    y = y0
    while y < H:
        d.line([(0, y), (W, y)], fill=(0, 255, 255, 200), width=1); y += py
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--pitch", type=float); ap.add_argument("--pitchy", type=float)
    ap.add_argument("--x0", type=float); ap.add_argument("--y0", type=float)
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--nonsquare", action="store_true", help="detect x/y pitch independently")
    ap.add_argument("--width", type=int); ap.add_argument("--height", type=int)
    ap.add_argument("--palette", type=int)
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--upscale", type=int, default=0, help="also save out.big.png at this scale")
    a = ap.parse_args()

    img = load(a.inp)
    H, W = img.shape[:2]
    ex, ey = edge_energy(img)

    if a.pitch:
        px = a.pitch; py = a.pitchy if a.pitchy else a.pitch
    elif a.auto:
        if a.nonsquare:
            px, py = detect_pitch([ex]), detect_pitch([ey])
        else:
            px = py = detect_pitch([ex, ey])       # square grid from both axes
    else:
        raise SystemExit("need --pitch (and optionally --pitchy) or --auto")
    x0 = a.x0 if a.x0 is not None else _best_phase(ex, px) % px
    y0 = a.y0 if a.y0 is not None else _best_phase(ey, py) % py

    nx = a.width if a.width else int((W - x0) // px)
    ny = a.height if a.height else int((H - y0) // py)
    print(f"pitch x={px:.3f} y={py:.3f}  corner x0={x0:.2f} y0={y0:.2f}  grid {nx}x{ny}", flush=True)

    out = sample(img, px, py, x0, y0, nx, ny)
    if a.palette:
        out = palette_snap(out, a.palette)
    Image.fromarray(out, "RGBA").save(a.out)
    if a.debug:
        debug_overlay(img, px, py, x0, y0, a.inp.rsplit(".", 1)[0] + ".grid.png")
    if a.upscale:
        Image.fromarray(out, "RGBA").resize((nx * a.upscale, ny * a.upscale), Image.NEAREST).save(
            a.out.rsplit(".", 1)[0] + ".big.png")


if __name__ == "__main__":
    main()
