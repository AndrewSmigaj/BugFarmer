"""tile_variants.py — make VARIANTS of a chosen ground tile by feeding the tile back to gpt-image-1.5.

Variants of a ground tile must share the palette, mark size and density of the original, or a field of
mixed variants reads as patchwork. Asking the model for "the same but different" in words does not hold
a style; feeding the actual image back (images/edits with input_fidelity=high) does — the same
reference trick the player-wearable pipeline uses.

The reference fed in is the RAW 1024px render, never the finished 16px tile: the model needs the detail
to copy the look (a 16px input gives it almost nothing to work from).

  python3 tools/sprites/tile_variants.py            # 3 variants of each chosen tile
  python3 tools/sprites/tile_variants.py A1 SH1_q4  # only these
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tile_experiments as T                                    # noqa: E402  API + conversion helpers

RAW = os.path.join(REPO, "tools", "_generated", "tiles", "raw")
REFS = os.path.join(REPO, "tools", "_generated", "tiles", "refs")
OUT16 = os.path.join(REPO, "tools", "_generated", "tiles", "candidates16")
TILE_PX = 16                                                    # one cell at the game's 16 PPU

VARIANT_HINTS = [
    "Rearrange the small grass marks into different positions, and change nothing else.",
    "Use a different scattering of the same marks — some areas slightly barer, some slightly denser.",
    "Shift the marks to new spots and let a few cluster into small tufts, keeping overall density equal.",
]


def autotrim(q, thresh=60):
    lum = 0.299 * q[..., 0] + 0.587 * q[..., 1] + 0.114 * q[..., 2]
    r = np.where(lum.mean(axis=1) > thresh)[0]
    c = np.where(lum.mean(axis=0) > thresh)[0]
    return q[r.min():r.max() + 1, c.min():c.max() + 1]


def build_references():
    """The four chosen tiles, as full-resolution references to feed back to the model."""
    os.makedirs(REFS, exist_ok=True)
    def rawimg(n):
        return np.asarray(Image.open(os.path.join(RAW, n + ".png")).convert("RGB"), np.uint8)

    refs = {}
    refs["A1"] = rawimg("A1_baseline")
    refs["A4"] = T.roll_half(rawimg("A4_healed"))               # roll back to the un-offset texture
    sh = rawimg("SH1_sheet_2x2"); half = sh.shape[0] // 2
    refs["SH1_q4"] = autotrim(sh[half:, half:])[6:-6, 6:-6]     # bottom-right quadrant
    v1 = rawimg("V1_recipe_sheet"); half = v1.shape[0] // 2
    refs["V1_q1"] = autotrim(v1[:half, :half])[6:-6, 6:-6]      # top-left quadrant

    for k, a in refs.items():
        im = Image.fromarray(a, "RGB")
        if im.size != (1024, 1024):                             # edits endpoint wants a square canvas
            im = im.resize((1024, 1024), Image.LANCZOS)
        p = os.path.join(REFS, f"{k}_ref.png")
        im.save(p)
        refs[k] = p
    return refs


PROMPT = (
    "This is the SAME grass ground texture, redrawn as a different variant of itself. "
    "Keep EXACTLY the same colour palette, the same size of the individual grass marks, the same "
    "density and the same completely flat even lighting as the attached image — a player must not be "
    "able to tell the two apart except by the arrangement of the marks. {hint} "
    "The texture fills the whole square and runs off all four edges so copies tile seamlessly: no "
    "border, no outline, no vignette, no darkened corners, no centre focus. "
    "Crisp PIXEL ART for a 2D top-down farming game. Hard pixel edges, NO anti-aliasing, NO gradients.")


def make_variants(key, ref_path, count=3):
    for i in range(count):
        name = f"{key}_var{i + 1}"
        try:
            png = T.edit(ref_path, PROMPT.format(hint=VARIANT_HINTS[i % len(VARIANT_HINTS)]))
        except Exception as e:
            print(f"  FAILED {name}: {type(e).__name__}: {e}")
            continue
        rp = os.path.join(RAW, name + ".png")
        open(rp, "wb").write(png)
        a = np.asarray(Image.open(rp).convert("RGB"), np.uint8)
        tile = T.snap_palette(T.grid_sample(a, TILE_PX), 6)
        os.makedirs(OUT16, exist_ok=True)
        Image.fromarray(tile, "RGB").save(os.path.join(OUT16, name + ".png"))
        print(f"  {name}")


def main():
    want = [a for a in sys.argv[1:]] or ["A1", "A4", "SH1_q4", "V1_q1"]
    refs = build_references()
    print("references:", ", ".join(refs))
    for k in want:
        if k not in refs:
            print("unknown:", k)
            continue
        print(f"=== {k} ===")
        make_variants(k, refs[k])


if __name__ == "__main__":
    main()
