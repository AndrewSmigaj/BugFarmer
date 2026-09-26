#!/usr/bin/env python3
"""Mockups of the shovel "Set Materials" panel (S2) — two layout options for the owner to pick.

Uses the REAL composited tiles (composite_tiles.py) as the swatches, so the mockup shows exactly what
the in-game panel would preview. This is a design artifact, not the shipped UI — the panel itself is
built in C# (UI/ShovelBuilderPanel.cs) once a layout is chosen.

    python3 tools/sprites/shovel_panel_mockup.py
Outputs option_a_grid.png / option_b_preview.png to previews/examples/shaped_ground/.
"""
import os
from PIL import Image, ImageDraw
from composite_tiles import composite, load_tile, MATERIALS, OUT as _OUT

OUT = _OUT
# Panel palette (approximate the wood/parchment UI kit).
BG = (44, 38, 32, 255)
PANEL = (58, 49, 40, 255)
INK = (238, 228, 204, 255)
GOLD = (246, 210, 100, 255)
DIM = (150, 140, 120, 255)
RED = (214, 110, 96, 255)
GREEN = (150, 200, 130, 255)
RING = (246, 210, 100, 255)

# A tiny hand-held state for the mockup (what the player currently has selected + holds).
CUR_A, CUR_B, CUR_SHAPE = "sand", "stone_floor", "diagNE"
# pretend inventory (item -> held) so have/need reads realistically
HELD = {"sand": 5, "stone": 1, "grass_turf": 3, "dirt": 8, "plank": 0}
# mirror of ground_recipes.json (for the have/need readout)
RECIPES = {
    "grass": [("grass_turf", 1)], "dirt": [("dirt", 1)], "sand": [("sand", 1)],
    "mud": [("dirt", 1), ("grass_turf", 1)], "stone_path": [("stone", 1)],
    "cave_floor": [("stone", 1)], "stone_floor": [("stone", 2)], "wood_floor": [("plank", 2)],
}


def up(img, s):
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


def recipe_for(matA, matB):
    """Union (summed) of both materials' recipes — mirrors groundRecipeIngredients."""
    merged, order = {}, []
    for m in ([matA, matB] if matA != matB else [matA]):
        for it, c in RECIPES.get(m, []):
            if it not in merged:
                order.append(it)
            merged[it] = merged.get(it, 0) + c
    return [(it, merged[it]) for it in order]


def affordable(matA, matB):
    return all(HELD.get(it, 0) >= c for it, c in recipe_for(matA, matB))


def draw_panel(w, h, title):
    img = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, w - 6, h - 6], fill=PANEL, outline=(96, 80, 62, 255), width=2)
    d.text((18, 14), title, fill=GOLD)
    return img, d


def swatch(img, d, x, y, cell, tile_img, label, selected=False, dim=False, ring_col=RING):
    frame = (30, 26, 22, 255)
    d.rectangle([x, y, x + cell, y + cell], fill=frame, outline=(90, 76, 60, 255))
    s = up(tile_img, max(1, cell // tile_img.width))
    s = s.crop((0, 0, cell - 2, cell - 2))
    if dim:
        ov = Image.new("RGBA", s.size, (30, 26, 22, 150))
        s = Image.alpha_composite(s, ov)
    img.paste(s, (x + 1, y + 1))
    if selected:
        d.rectangle([x - 2, y - 2, x + cell + 2, y + cell + 2], outline=ring_col, width=3)
    if label:
        d.text((x, y + cell + 2), label, fill=DIM if dim else INK)


def have_need(d, x, y, matA, matB):
    d.text((x, y), "Recipe (costs BOTH materials):", fill=INK)
    yy = y + 16
    for it, c in recipe_for(matA, matB):
        have = HELD.get(it, 0)
        col = GREEN if have >= c else RED
        d.text((x + 6, yy), f"{it}: need {c}, have {have}", fill=col)
        yy += 15
    ok = affordable(matA, matB)
    d.text((x, yy + 4), "READY to place" if ok else "Not enough — placing shows 'Need ...'",
           fill=GREEN if ok else RED)


def option_a_grid():
    """Compact grid: material A as composited swatches, material B strip below, controls at the foot."""
    w, h = 470, 400
    img, d = draw_panel(w, h, "SET MATERIALS")
    cell = 46
    # Material A grid (each swatch = the actual composite you'd place)
    d.text((18, 40), "Material A  (fills the shape)", fill=INK)
    x0, y0, cols = 20, 60, 4
    for i, m in enumerate(MATERIALS):
        r, c = divmod(i, cols)
        x = x0 + c * (cell + 26)
        y = y0 + r * (cell + 20)
        tile = composite(m, CUR_B, CUR_SHAPE)
        swatch(img, d, x, y, cell, tile, m, selected=(m == CUR_A), dim=not affordable(m, CUR_B))
    # Material B strip
    by = y0 + 2 * (cell + 20) + 8
    d.text((18, by), "Material B  (the other half)", fill=INK)
    for i, m in enumerate(MATERIALS):
        x = 20 + i * 30
        swatch(img, d, x, by + 18, 26, load_tile(m), "", selected=(m == CUR_B))
    # shape + controls
    d.text((18, by + 58), f"Shape: {CUR_SHAPE}   (mouse wheel to cycle)", fill=GOLD)
    have_need(d, 250, 60, CUR_A, CUR_B)
    d.text((18, h - 34), "LMB place   ·   Shift+LMB dig   ·   wheel = shape", fill=DIM)
    return img


def option_b_preview():
    """Big live preview of the current composite on the left; A/B pickers on the right."""
    w, h = 470, 400
    img, d = draw_panel(w, h, "SET MATERIALS")
    # big preview
    big = up(composite(CUR_A, CUR_B, CUR_SHAPE), 4)
    d.text((18, 40), "Placing:", fill=INK)
    img.paste(big, (24, 60))
    d.rectangle([22, 58, 24 + big.width + 2, 60 + big.height + 2], outline=GOLD, width=2)
    d.text((20, 62 + big.height + 6), f"{CUR_A}~{CUR_B}~{CUR_SHAPE}", fill=GOLD)
    have_need(d, 20, 62 + big.height + 30, CUR_A, CUR_B)
    # pickers on the right
    cell = 34
    d.text((190, 40), "Material A", fill=INK)
    for i, m in enumerate(MATERIALS):
        r, c = divmod(i, 4)
        swatch(img, d, 190 + c * (cell + 24), 58 + r * (cell + 18), cell,
               composite(m, CUR_B, CUR_SHAPE), m, selected=(m == CUR_A), dim=not affordable(m, CUR_B))
    d.text((190, 200), "Material B", fill=INK)
    for i, m in enumerate(MATERIALS):
        r, c = divmod(i, 4)
        swatch(img, d, 190 + c * (cell + 24), 218 + r * (cell + 18), cell,
               load_tile(m), m, selected=(m == CUR_B))
    d.text((18, h - 34), "LMB place   ·   Shift+LMB dig   ·   wheel = shape", fill=DIM)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    a = os.path.join(OUT, "panel_option_a_grid.png")
    b = os.path.join(OUT, "panel_option_b_preview.png")
    option_a_grid().save(a)
    option_b_preview().save(b)
    print("wrote:\n  " + a + "\n  " + b)


if __name__ == "__main__":
    main()
