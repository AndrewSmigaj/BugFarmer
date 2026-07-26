"""gen_tiles_handauthored.py — Pipeline-B (no API) ground-tile candidates.

Writes explicit RGBA pixel grids, the same hand-authored approach as the player sprites. Every tile is
built with WRAP-AROUND stamping, so it is seamless BY CONSTRUCTION (no seam-healing needed, ever).

The palette is derived from our EXISTING grass tile so candidates stay in our game's colour family:
one dominant base + a readable light accent + a readable dark accent + two near-base tones — the
structure the reference games use (our current tile's flaw is 20 near-identical greens with no
dominant base, measured by tile_lab).

  python3 tools/sprites/gen_tiles_handauthored.py        # writes H1/H2/H3 into _generated/tiles/candidates
"""
import os
import colorsys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources", "Tiles", "grass.png")
OUT = os.path.join(REPO, "tools", "_generated", "tiles", "candidates")
N = 32


def shift(rgb, dv=0.0, ds=0.0, dh=0.0):
    """Nudge a colour in HSV space (keeps it in the same family)."""
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + dh) % 1.0
    s = min(1.0, max(0.0, s + ds))
    v = min(1.0, max(0.0, v + dv))
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s, v))


def base_palette():
    """base, light, dark, near1, near2 — anchored on our existing grass tile's average colour."""
    a = np.asarray(Image.open(SRC).convert("RGB"), dtype=float)
    base = tuple(int(round(c)) for c in a.reshape(-1, 3).mean(axis=0))
    return {
        "base":  base,
        "light": shift(base, dv=+0.09, ds=+0.04, dh=+0.010),   # sunlit blade (subtle: high contrast reads as static)
        "dark":  shift(base, dv=-0.08, ds=-0.03, dh=-0.012),   # shadowed clump (subtle)
        "near1": shift(base, dv=+0.035),
        "near2": shift(base, dv=-0.04),
    }


def put(img, x, y, rgb):
    img[y % N, x % N] = rgb                      # modulo = wrap-around = seamless by construction


def hook(img, x, y, rgb, h=2, over=1):
    """A small blade glyph: `h` px up, then `over` px across at the top (the reference 'hook')."""
    for i in range(h):
        put(img, x, y - i, rgb)
    for j in range(1, over + 1):
        put(img, x + j, y - (h - 1), rgb)


def wrapped_noise(rng, cells, smooth=1):
    """Low-res random field upsampled to NxN as large soft blobs that WRAP.

    A plain bilinear resize is NOT wrap-aware (its edges don't meet), which puts a real seam in the
    tile. So tile the low-res grid 3x3, upsample that, and take the centre — the result is periodic.
    """
    g = rng.random((cells, cells))
    g3 = np.tile(g, (3, 3))
    big3 = np.asarray(Image.fromarray((g3 * 255).astype(np.uint8)).resize((N * 3, N * 3), Image.BILINEAR),
                      float) / 255.0
    big = big3[N:2 * N, N:2 * N]
    for _ in range(smooth):                      # cheap wrap-safe blur
        big = (big + np.roll(big, 1, 0) + np.roll(big, -1, 0) + np.roll(big, 1, 1) + np.roll(big, -1, 1)) / 5.0
    return (big - big.min()) / (np.ptp(big) + 1e-9)


def h1_stardew_informed(seed=7):
    """Dominant base + sparse small hook glyphs in a light and a dark accent."""
    p = base_palette()
    rng = np.random.default_rng(seed)
    img = np.zeros((N, N, 3), np.uint8)
    img[:, :] = p["base"]
    # Density is calibrated against the reference: ~50% of the tile carries a non-base tone
    # (on 32x32 that is ~500 px, NOT the ~90 a naive sparse scatter gives).
    for _ in range(210):                         # quiet near-base speckle (most of the texture)
        put(img, rng.integers(N), rng.integers(N), p["near1"] if rng.random() < 0.5 else p["near2"])
    for _ in range(55):                          # the readable light blades
        x, y = int(rng.integers(N)), int(rng.integers(N))
        hook(img, x, y, p["light"], h=int(rng.integers(2, 4)), over=1)
    for _ in range(34):                          # dark blades for depth
        x, y = int(rng.integers(N)), int(rng.integers(N))
        hook(img, x, y, p["dark"], h=int(rng.integers(2, 3)), over=1)
    return img


def h2_necesse_informed(seed=11):
    """Soft mottle: large wrapped blobs quantised to a few tones (calm, low contrast)."""
    p = base_palette()
    rng = np.random.default_rng(seed)
    f = wrapped_noise(rng, cells=8, smooth=2)
    img = np.zeros((N, N, 3), np.uint8)
    img[:, :] = p["base"]
    img[f < 0.38] = p["near2"]
    img[f > 0.62] = p["near1"]
    img[f > 0.90] = p["light"]
    for _ in range(6):                           # a few darker specks so it isn't pure gradient
        put(img, rng.integers(N), rng.integers(N), p["dark"])
    return img


def h3_ours(seed=3):
    """Ours: mottled base (H2 idea) PLUS denser blade glyphs (H1 idea) — texture with a calm ground."""
    p = base_palette()
    rng = np.random.default_rng(seed)
    f = wrapped_noise(rng, cells=7, smooth=2)
    img = np.zeros((N, N, 3), np.uint8)
    img[:, :] = p["base"]
    img[f < 0.35] = p["near2"]
    img[f > 0.72] = p["near1"]
    for _ in range(22):
        x, y = int(rng.integers(N)), int(rng.integers(N))
        hook(img, x, y, p["light"], h=int(rng.integers(1, 3)), over=1)
    for _ in range(13):
        x, y = int(rng.integers(N)), int(rng.integers(N))
        hook(img, x, y, p["dark"], h=2, over=1)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    p = base_palette()
    print("palette:", {k: v for k, v in p.items()})
    for name, fn in [("H1_handauthored_stardew_informed", h1_stardew_informed),
                     ("H2_handauthored_necesse_mottle", h2_necesse_informed),
                     ("H3_handauthored_ours", h3_ours)]:
        img = fn()
        dest = os.path.join(OUT, name + ".png")
        Image.fromarray(img, "RGB").save(dest)
        print("wrote", os.path.relpath(dest, REPO))


if __name__ == "__main__":
    main()
