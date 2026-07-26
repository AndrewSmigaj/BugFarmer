"""tile_scene.py — preview candidate ground tiles WITH a character and a tree on them, at true scale.

A bare tiled field says nothing about whether a tile reads well in the actual game, because what
matters is how it sits under the things you look at. This composites the real player sprite and a real
tree onto each candidate at the game's true size relationship.

Everything is 16 PPU — one CELL is 16 pixels, for ground and entities alike:
  * ground tile   16x16  = 1x1 cell   (our candidates were authored 32x32 by mistake = 2x2 cells)
  * player        16x32  = 1x2 cells  (used at native size)
  * tree_oak      sprite 32x48 = 2x3 cells (the 64x96 PNG is halved to 32x48)
The whole scene is then upscaled uniformly with NEAREST just so it is visible on screen.

  python3 tools/sprites/tile_scene.py            # all 32x32 candidates -> previews/_SCENES.png
"""
import os
import glob

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
TILES = os.path.join(REPO, "tools", "_generated", "tiles")
CAND, PREV = os.path.join(TILES, "candidates16"), os.path.join(TILES, "previews")

CELL = 16                      # 16 PPU: one cell is 16 px, ground and entities alike
COLS, ROWS = 11, 7             # field size of each scene, in cells
ZOOM = 4                       # final upscale for viewing
LABEL_PX = 30                  # label height — small default-font text was unreadable on these sheets


def _font(size=LABEL_PX):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _fitted(draw, text, max_w):
    """Largest readable font that still fits the card width — big labels were being cut off."""
    for size in range(LABEL_PX, 9, -2):
        f = _font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
    return _font(10)


def load_rgba(path):
    return Image.open(path).convert("RGBA")


def player_sprite():
    """Compose the default character from its layers (16x32), then upscale 2x to tile-pixel space."""
    layers = ["body/default_down", "pants/farmer_down", "shirt/farmer_down", "hair/brown_down"]
    out = None
    for name in layers:
        p = os.path.join(RES, "Player", "layers", name + ".png")
        if not os.path.exists(p):
            continue
        im = load_rgba(p)
        out = Image.new("RGBA", im.size, (0, 0, 0, 0)) if out is None else out
        out.alpha_composite(im)
    if out is None:
        return None
    return out                                    # 16x32 = 1x2 cells at 16 PPU; no rescale


def tree_sprite(name="tree_oak"):
    """entity data says tree_oak renders at 32x48 = 2x3 cells; the PNG is 64x96, so halve it."""
    p = os.path.join(RES, "Objects", name + ".png")
    if not os.path.exists(p):
        return None
    im = load_rgba(p)
    return im.resize((im.width // 2, im.height // 2), Image.NEAREST)


def scene(tile_rgb, player, tree, label):
    """One field of this tile with a tree and the character standing on it."""
    W, H = COLS * CELL, ROWS * CELL
    field = Image.new("RGBA", (W, H))
    t = Image.fromarray(tile_rgb, "RGB").convert("RGBA")
    for cy in range(ROWS):
        for cx in range(COLS):
            field.paste(t, (cx * CELL, cy * CELL))
    if tree is not None:                       # bottom-anchored on its cell, like the game does
        field.alpha_composite(tree, (2 * CELL - (tree.width - CELL) // 2, 2 * CELL - (tree.height - CELL)))
    if player is not None:
        field.alpha_composite(player, (6 * CELL, 3 * CELL - (player.height - CELL)))
    big = field.convert("RGB").resize((W * ZOOM, H * ZOOM), Image.NEAREST)
    bar = LABEL_PX + 14
    card = Image.new("RGB", (big.width, big.height + bar), (24, 24, 28))
    card.paste(big, (0, bar))
    d = ImageDraw.Draw(card)
    d.text((8, 6), label, fill=(255, 235, 160), font=_fitted(d, label, card.width - 16))
    return card


def main():
    os.makedirs(PREV, exist_ok=True)
    player, tree = player_sprite(), tree_sprite()
    print(f"16 PPU  cell={CELL}px   player={player.size if player else None} (1x2 cells)   tree={tree.size if tree else None} (2x3 cells)")
    cards = []
    for p in sorted(glob.glob(os.path.join(CAND, "*.png"))):
        a = np.asarray(Image.open(p).convert("RGB"), np.uint8)
        if a.shape[0] != CELL or a.shape[1] != CELL:
            continue                                   # skip the non-32x32 (overhang) sprites
        cards.append(scene(a, player, tree, os.path.splitext(os.path.basename(p))[0]))
    if not cards:
        print("no 32x32 candidates found")
        return
    cols = 3
    rows = (len(cards) + cols - 1) // cols
    cw, ch = cards[0].width + 8, cards[0].height + 8
    sheet = Image.new("RGB", (cw * cols, ch * rows), (14, 14, 18))
    for i, c in enumerate(cards):
        sheet.paste(c, ((i % cols) * cw + 4, (i // cols) * ch + 4))
    out = os.path.join(PREV, "_SCENES.png")
    sheet.save(out)
    print(f"wrote {out}  ({len(cards)} scenes)")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------- mixed-variant fields
def mixed_scene(tiles, player, tree, label):
    """A field where EACH CELL randomly picks one of the family's variants.

    This is the only test that matters for a variant set: a single tile repeated shows its own
    repetition, but variants exist to break that up, and they only work if they also blend with each
    other (same palette/density) rather than reading as patchwork."""
    import hashlib
    W, H = COLS * CELL, ROWS * CELL
    field = Image.new("RGBA", (W, H))
    ims = [Image.fromarray(t, "RGB").convert("RGBA") for t in tiles]
    for cy in range(ROWS):
        for cx in range(COLS):
            h = int(hashlib.md5(f"{cx},{cy}".encode()).hexdigest()[:8], 16)   # deterministic per cell
            field.paste(ims[h % len(ims)], (cx * CELL, cy * CELL))
    if tree is not None:
        field.alpha_composite(tree, (2 * CELL - (tree.width - CELL) // 2, 2 * CELL - (tree.height - CELL)))
    if player is not None:
        field.alpha_composite(player, (6 * CELL, 3 * CELL - (player.height - CELL)))
    big = field.convert("RGB").resize((W * ZOOM, H * ZOOM), Image.NEAREST)
    bar = LABEL_PX + 14
    card = Image.new("RGB", (big.width, big.height + bar), (24, 24, 28))
    card.paste(big, (0, bar))
    d = ImageDraw.Draw(card)
    d.text((8, 6), label, fill=(255, 235, 160), font=_fitted(d, label, card.width - 16))
    return card


# which experiment each family came from — shown in the label so no separate map file is needed
ORIGIN = {"grass_01": "A1 baseline prompt", "grass_02": "A4 seam-healed",
          "grass_03": "SH1 q4, from the 4-up sheet", "grass_04": "V1 q1, recipe sheet"}


def families():
    """Render each grass family twice: the single tile repeated, and all 4 variants mixed per cell."""
    player, tree = player_sprite(), tree_sprite()
    cards = []
    for fam in ["grass_01", "grass_02", "grass_03", "grass_04"]:
        paths = [os.path.join(CAND, f"{fam}.png")] + [
            os.path.join(CAND, f"{fam}_{s}.png") for s in "abc" if os.path.exists(os.path.join(CAND, f"{fam}_{s}.png"))]
        paths = [p for p in paths if os.path.exists(p)]
        if not paths:
            continue
        tiles = [np.asarray(Image.open(p).convert("RGB"), np.uint8) for p in paths]
        cards.append(scene(tiles[0], player, tree, f"{fam} ({ORIGIN.get(fam, '?')}) — ONE tile repeated"))
        cards.append(mixed_scene(tiles, player, tree, f"{fam} ({ORIGIN.get(fam, '?')}) — {len(tiles)} VARIANTS mixed"))
    cols = 2
    rows = (len(cards) + cols - 1) // cols
    cw, ch = cards[0].width + 8, cards[0].height + 8
    sheet = Image.new("RGB", (cw * cols, ch * rows), (14, 14, 18))
    for i, c in enumerate(cards):
        sheet.paste(c, ((i % cols) * cw + 4, (i // cols) * ch + 4))
    out = os.path.join(PREV, "_FAMILIES.png")
    sheet.save(out)
    print(f"wrote {out}  ({len(cards)} scenes: each family single vs mixed)")
