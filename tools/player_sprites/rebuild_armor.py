"""rebuild_armor.py — re-split the armour masks and redraw the fit preview, in one step.

The masking loop is: edit `suit.png` (the armour art) or the mask layers in the .ase, then look at the
character wearing it. This does the second half so the loop is a single command.

  1. splits every layer of the masking .ase into pieces/<set>_<layer>.png   (Aseprite CLI)
  2. paints those masked areas of suit.png onto the base character
  3. writes armor_combinations.png — the same character in several gear combinations

Whenever a combination includes the HELMET the BALD base is used, otherwise hair pokes out around it.

  python3 tools/player_sprites/rebuild_armor.py                # copper
  python3 tools/player_sprites/rebuild_armor.py silver-armor   # another set
"""
import os
import sys
import glob
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
REFS = os.path.join(PLAYER, "references")
ASEPRITE = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Aseprite/Aseprite.exe"

SLOTS = ["helmet", "chest", "legs", "boots", "arms"]     # every wearable slot we mask
COMBOS = [
    ("bare", []),
    ("all BUT helmet", ["chest", "legs", "boots", "arms"]),
    ("chest + legs", ["chest", "legs"]),
    ("chest+legs+boots", ["chest", "legs", "boots"]),
    ("arms only", ["arms"]),
    ("helmet only", ["helmet"]),
    ("helmet + chest", ["helmet", "chest"]),
    ("boots only", ["boots"]),
    ("FULL SET", SLOTS),
]


def win_path(p):
    """WSL path -> the Windows path Aseprite.exe needs."""
    p = os.path.abspath(p)
    return p.replace("/mnt/c/", "C:/") if p.startswith("/mnt/c/") else p


def attempt_dir(item):
    """Newest dated attempt folder for this item (they sort by date)."""
    dirs = sorted(glob.glob(os.path.join(PLAYER, "in-progress", item, "*")))
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        sys.exit(f"no attempt folder under in-progress/{item}")
    return dirs[-1]


def split_layers(work):
    """Aseprite CLI: one PNG per layer. Named from the layer, so the .ase layer names ARE the slot names."""
    ase = glob.glob(os.path.join(work, "pieces", "*.ase")) + glob.glob(os.path.join(work, "pieces", "*.aseprite"))
    if not ase:
        print("  (no .ase found — using the existing piece PNGs)")
        return
    if not os.path.exists(ASEPRITE):
        print("  (Aseprite not found — using the existing piece PNGs)")
        return
    prefix = os.path.basename(work.rstrip("/")).split("_")[0]
    out = os.path.join(work, "pieces", "copper_{layer}.png")
    subprocess.run([ASEPRITE, "-b", "--all-layers", "--split-layers", win_path(ase[0]),
                    "--save-as", win_path(out)], capture_output=True)
    # drop exports of helper/reference layers — only real slots are pieces
    for f in glob.glob(os.path.join(work, "pieces", "copper_*.png")):
        stem = os.path.basename(f)[len("copper_"):-4]
        if stem not in SLOTS:
            os.remove(f)
    print(f"  split {len(glob.glob(os.path.join(work, 'pieces', 'copper_*.png')))} slot masks from {os.path.basename(ase[0])}")


def build(work):
    haired = np.asarray(Image.open(os.path.join(REFS, "base.png")).convert("RGBA"), np.uint8)
    bald = np.asarray(Image.open(os.path.join(REFS, "bald.png")).convert("RGBA"), np.uint8)
    suit = np.asarray(Image.open(os.path.join(work, "suit.png")).convert("RGBA"), np.uint8)

    masks = {}
    for s in SLOTS:
        p = os.path.join(work, "pieces", f"copper_{s}.png")
        if os.path.exists(p):
            masks[s] = np.asarray(Image.open(p).convert("RGBA"), np.uint8)[..., 3] > 0

    def dress(which):
        which = [w for w in which if w in masks]
        out = (bald if "helmet" in which else haired).copy()
        for s in which:
            take = masks[s] & (suit[..., 3] > 0)     # only where the suit actually drew armour
            out[take] = suit[take]
        return out

    Z, pad, labelh = 6, 16, 46
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    cw, ch = haired.shape[1] * Z, haired.shape[0] * Z
    sheet = Image.new("RGB", (pad + (cw + pad) * len(COMBOS), labelh + ch + pad), (38, 40, 46))
    d = ImageDraw.Draw(sheet)
    x = pad
    for name, which in COMBOS:
        img = Image.fromarray(dress(which), "RGBA").resize((cw, ch), Image.NEAREST)
        bg = Image.new("RGBA", (cw, ch), (150, 160, 150, 255))
        bg.alpha_composite(img)
        sheet.paste(bg.convert("RGB"), (x, labelh))
        w = name.split()
        d.text((x, 8), w[0], fill=(255, 235, 160), font=font)
        d.text((x, 26), " ".join(w[1:]), fill=(255, 235, 160), font=font)
        if "helmet" in which:
            d.text((x + cw - 32, 8), "bald", fill=(140, 220, 255), font=font)
        x += cw + pad
    out = os.path.join(work, "armor_combinations.png")
    sheet.save(out)
    print("  wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    item = sys.argv[1] if len(sys.argv) > 1 else "copper-armor"
    work = attempt_dir(item)
    print(f"{item}: {os.path.relpath(work, REPO)}")
    split_layers(work)
    build(work)
