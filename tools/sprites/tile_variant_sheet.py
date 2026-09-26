"""tile_variant_sheet.py — variants that actually KEEP the parent's palette.

Generating variants as separate calls lets each one drift to its own shades, and a field of mixed
variants then reads as a patchwork of lighter and darker squares. Three fixes, stacked:

  1. ONE IMAGE  — all four variants are drawn in a single 2x2 sheet, so they share a palette by
     CONSTRUCTION rather than by instruction. (Proven earlier this session: the four quadrants of the
     `SH1` sheet matched perfectly, while four separate reference-fed calls drifted.)
  2. NAMED COLOURS — the parent's exact hex values go in the prompt, instead of "keep the same palette".
  3. FORCED PALETTE — every sliced variant is quantised to the PARENT's palette, not to a freshly
     computed one of its own. Drift becomes impossible regardless of what the model returns.

  python3 tools/sprites/tile_variant_sheet.py               # all four families
  python3 tools/sprites/tile_variant_sheet.py grass_03      # just one
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tile_experiments as T                                   # noqa: E402

TILES = os.path.join(REPO, "tools", "_generated", "tiles")
RAW, C16, REFS = (os.path.join(TILES, "raw"), os.path.join(TILES, "candidates16"),
                  os.path.join(TILES, "refs"))
TILE_PX = 16

# the 1024px source each family came from, so we feed detail rather than a 16px thumbnail
PARENT_RAW = {"grass_01": "A1_baseline", "grass_02": "A4_healed",
              "grass_03": "SH1_sheet_2x2", "grass_04": "V1_recipe_sheet"}


def parent_palette(fam):
    """The parent tile's exact colours, most-common first."""
    a = np.asarray(Image.open(os.path.join(C16, fam + ".png")).convert("RGB"), np.uint8)
    cols, counts = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
    return cols[np.argsort(-counts)]


def force_palette(a, palette):
    """Snap every pixel to the NEAREST parent colour — no per-tile palette, so no drift."""
    flat = a.reshape(-1, 3).astype(int)
    d = ((flat[:, None, :] - palette[None, :, :].astype(int)) ** 2).sum(axis=2)
    return palette[d.argmin(axis=1)].reshape(a.shape).astype(np.uint8)


def sheet_prompt(palette):
    hexes = ", ".join("#%02X%02X%02X" % tuple(int(c) for c in p) for p in palette[:6])
    return (
        "A 2x2 grid of FOUR square grass ground textures, separated by thin black lines. "
        "Each square is a variant of the SAME texture as the attached image, seen from directly above. "
        f"CRITICAL - COLOUR: use ONLY these exact colours in all four squares: {hexes}. Do not "
        "introduce any other colour, do not lighten or darken any square: all four squares must have "
        "IDENTICAL overall brightness and identical proportions of each colour, so that if the four "
        "were placed side by side you could not tell which is which except by the arrangement of the "
        "marks. Keep the same mark size and the same density as the attached image. "
        "The four differ ONLY in where the small grass marks sit. "
        "Each square is flat-lit edge to edge: no vignette, no shading, no darkened corners, no border "
        "inside a square, and its texture runs off its own four edges so it tiles seamlessly. "
        "Crisp PIXEL ART for a 2D top-down farming game. Hard pixel edges, NO anti-aliasing, NO gradients.")


def autotrim(q, thresh=60):
    lum = 0.299 * q[..., 0] + 0.587 * q[..., 1] + 0.114 * q[..., 2]
    r = np.where(lum.mean(axis=1) > thresh)[0]
    c = np.where(lum.mean(axis=0) > thresh)[0]
    return q[r.min():r.max() + 1, c.min():c.max() + 1]


def run(fam):
    ref = os.path.join(REFS, fam + "_sheetref.png")
    os.makedirs(REFS, exist_ok=True)
    src = os.path.join(REFS, {"grass_01": "A1", "grass_02": "A4",
                              "grass_03": "SH1_q4", "grass_04": "V1_q1"}[fam] + "_ref.png")
    if not os.path.exists(src):                                # fall back to the family's raw
        src = os.path.join(RAW, PARENT_RAW[fam] + ".png")
    Image.open(src).convert("RGB").resize((1024, 1024), Image.LANCZOS).save(ref)

    pal = parent_palette(fam)
    png = T.edit(ref, sheet_prompt(pal))
    rp = os.path.join(RAW, f"{fam}_variantsheet.png")
    open(rp, "wb").write(png)
    a = np.asarray(Image.open(rp).convert("RGB"), np.uint8)
    half = a.shape[0] // 2
    for i, (y, x) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        q = autotrim(a[y * half:(y + 1) * half, x * half:(x + 1) * half])[6:-6, 6:-6]
        tile = force_palette(T.grid_sample(q, TILE_PX), pal)    # parent's palette, forced
        Image.fromarray(tile, "RGB").save(os.path.join(C16, f"{fam}_{chr(97 + i)}.png"))
    print(f"  {fam}: 4 variants -> {fam}_a..d, palette forced to parent ({len(pal)} colours)")


if __name__ == "__main__":
    fams = sys.argv[1:] or ["grass_01", "grass_02", "grass_03", "grass_04"]
    for f in fams:
        try:
            run(f)
        except Exception as e:
            print(f"  FAILED {f}: {type(e).__name__}: {e}")
