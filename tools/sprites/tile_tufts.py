"""tile_tufts.py — generate grass TUFT sprites and scatter them over a base tile.

Every reference game gets its lushness from a scattered detail layer, not from the base tile: the base
stays quiet and the tufts carry the "grass" read. This generates a set of small tufts and previews them
over the chosen bases.

Two tricks reused from earlier in this session:
  * all four tufts are drawn in ONE image, so they share a palette by construction;
  * each tuft is then snapped to the palette of whichever base tile it is being scattered on, so one
    generated set matches every grass family without regenerating it.

  python3 tools/sprites/tile_tufts.py gen           # 1 API call: the tuft sheet
  python3 tools/sprites/tile_tufts.py scene         # preview tufts over grass_01 and grass_02
"""
import os
import sys
import hashlib

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tile_experiments as T                                   # noqa: E402
import tile_scene as S                                         # noqa: E402

TILES = os.path.join(REPO, "tools", "_generated", "tiles")
RAW, C16, PREV = (os.path.join(TILES, "raw"), os.path.join(TILES, "candidates16"),
                  os.path.join(TILES, "previews"))
TUFTS = os.path.join(TILES, "tufts")
CELL = 16


def base_palette(fam="grass_01"):
    a = np.asarray(Image.open(os.path.join(C16, fam + ".png")).convert("RGB"), np.uint8)
    cols, counts = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
    return cols[np.argsort(-counts)]


def gen():
    """One call: four tufts on a transparent background, sharing the grass palette."""
    pal = base_palette()
    hexes = ", ".join("#%02X%02X%02X" % tuple(int(c) for c in p) for p in pal[:6])
    prompt = (
        "FOUR different small clumps of grass, seen from DIRECTLY ABOVE (flat top-down, no perspective), "
        "arranged in a 2x2 layout with a LOT of empty space between them and around them. "
        "The background is COMPLETELY TRANSPARENT and empty — no ground, no tile, no square behind the "
        "clumps, no drop shadow, no outline. Only the grass clumps themselves are drawn. "
        f"Use ONLY these colours: {hexes}. "
        "Each clump is a small tuft of a few upright blades — chunky pixel-art blades, roughly as tall as "
        "it is wide, a simple readable silhouette, NOT a bush and NOT a whole field. The four differ in "
        "shape and blade count: one sparse with 2-3 blades, one fuller, one leaning, one low and wide. "
        "Crisp PIXEL ART for a 2D top-down farming game. Hard pixel edges, NO anti-aliasing, NO gradients.")
    png = T.generate(prompt, background="transparent")
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, "tufts_sheet.png")
    open(p, "wb").write(png)
    print("raw ->", os.path.relpath(p, REPO))
    slice_tufts(p)


def slice_tufts(path, scale_div=12):
    """Cut the sheet into individual tufts, trimmed to the drawn pixels.

    All four are divided by the SAME factor, so each keeps its true proportions and their relative
    sizes survive. (Forcing every tuft to one fixed height stretched the wide, low clumps sideways —
    one of them came out 34px, over two cells wide.)"""
    os.makedirs(TUFTS, exist_ok=True)
    a = np.asarray(Image.open(path).convert("RGBA"), np.uint8)
    half = a.shape[0] // 2
    n = 0
    for i, (y, x) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)], start=1):
        q = a[y * half:(y + 1) * half, x * half:(x + 1) * half]
        ys, xs = np.where(q[..., 3] > 40)
        if len(ys) < 50:
            print(f"  tuft {i}: nothing drawn, skipped")
            continue
        cut = q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h = max(4, int(round(cut.shape[0] / scale_div)))
        w = max(3, int(round(cut.shape[1] / scale_div)))
        small = np.array(Image.fromarray(cut, "RGBA").resize((w, h), Image.BOX), np.uint8)  # writable
        small[..., 3] = np.where(small[..., 3] > 110, 255, 0)      # hard alpha, no soft edge
        Image.fromarray(small, "RGBA").save(os.path.join(TUFTS, f"tuft_{i}.png"))
        print(f"  tuft_{i}: {w}x{h}")
        n += 1
    print(f"{n} tufts -> {os.path.relpath(TUFTS, REPO)}")


def snap_to(tuft, palette):
    """Recolour a tuft to a base tile's palette so it belongs on that grass."""
    out = tuft.copy()
    rgb = out[..., :3].reshape(-1, 3).astype(int)
    d = ((rgb[:, None, :] - palette[None, :, :].astype(int)) ** 2).sum(axis=2)
    out[..., :3] = palette[d.argmin(axis=1)].reshape(out[..., :3].shape)
    return out


def scene(fam, density=0.30, seed=7):
    """A field of `fam` with tufts scattered on it, plus the tree and character for scale."""
    tufts = sorted(f for f in os.listdir(TUFTS) if f.endswith(".png")) if os.path.isdir(TUFTS) else []
    if not tufts:
        print("no tufts yet — run `gen` first")
        return None
    pal = base_palette(fam)
    imgs = [Image.fromarray(snap_to(np.asarray(Image.open(os.path.join(TUFTS, t)).convert("RGBA"), np.uint8), pal),
                            "RGBA") for t in tufts]
    tile = np.asarray(Image.open(os.path.join(C16, fam + ".png")).convert("RGB"), np.uint8)
    variants = [tile] + [np.asarray(Image.open(os.path.join(C16, f"{fam}_{s}.png")).convert("RGB"), np.uint8)
                         for s in "abcd" if os.path.exists(os.path.join(C16, f"{fam}_{s}.png"))]

    W, H = S.COLS * CELL, S.ROWS * CELL
    field = Image.new("RGBA", (W, H))
    for cy in range(S.ROWS):
        for cx in range(S.COLS):
            h = int(hashlib.md5(f"{cx},{cy}".encode()).hexdigest()[:8], 16)
            field.paste(Image.fromarray(variants[h % len(variants)], "RGB").convert("RGBA"), (cx * CELL, cy * CELL))
    for cy in range(S.ROWS):                                   # scattered tuft layer
        for cx in range(S.COLS):
            h = int(hashlib.md5(f"t{cx},{cy},{seed}".encode()).hexdigest()[:8], 16)
            if (h % 1000) / 1000.0 > density:
                continue
            t = imgs[(h >> 12) % len(imgs)]
            ox = (h >> 4) % max(1, CELL - t.width // 2)
            oy = (h >> 8) % 6
            field.alpha_composite(t, (cx * CELL + ox - t.width // 4, cy * CELL + CELL - t.height + oy - 2))
    tree, player = S.tree_sprite(), S.player_sprite()
    if tree is not None:
        field.alpha_composite(tree, (2 * CELL - (tree.width - CELL) // 2, 2 * CELL - (tree.height - CELL)))
    if player is not None:
        field.alpha_composite(player, (6 * CELL, 3 * CELL - (player.height - CELL)))
    return field.convert("RGB").resize((W * S.ZOOM, H * S.ZOOM), Image.NEAREST)


def scenes():
    cards = []
    for fam in ["grass_01", "grass_02"]:
        for dens, tag in [(0.0, "no tufts"), (0.30, "tufts"), (0.55, "dense tufts")]:
            im = scene(fam, density=dens)
            if im is None:
                return
            bar = 34
            card = Image.new("RGB", (im.width, im.height + bar), (24, 24, 28))
            card.paste(im, (0, bar))
            d = ImageDraw.Draw(card)
            label = f"{fam} — {tag}"
            d.text((8, 6), label, fill=(255, 235, 160), font=S._fitted(d, label, card.width - 16))
            cards.append(card)
    cols = 3
    cw, ch = cards[0].width + 8, cards[0].height + 8
    sheet = Image.new("RGB", (cw * cols, ch * ((len(cards) + cols - 1) // cols)), (14, 14, 18))
    for i, c in enumerate(cards):
        sheet.paste(c, ((i % cols) * cw + 4, (i // cols) * ch + 4))
    out = os.path.join(PREV, "_TUFTS.png")
    sheet.save(out)
    print("wrote", out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scene"
    if cmd == "gen":
        gen()
    elif cmd == "slice":
        slice_tufts(os.path.join(RAW, "tufts_sheet.png"))
    else:
        scenes()
