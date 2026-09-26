"""Build the art demo review folder: everything drawn in code, beside the current art.

    python3 tools/sprites/drawn/demo.py

Output: tools/_generated/player/reviews/2026-09-26-art-demo/ (tracked, so the owner can open it on Windows).
Nothing here touches game assets; it only renders previews.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from drawn import canvas as K, tiles as TL, objects as O, bugs as B, items as I, ui as U, player as PL  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "tools", "_generated", "player", "reviews", "2026-09-26-art-demo")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
BG = (40, 42, 48, 255)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size=22):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def cur(path):
    return Image.open(os.path.join(RES, path)).convert("RGBA")


def labelled_row(items, scale, title, bg=BG, pad=24, label_h=40):
    """items: list of (label, image). One row, integer NEAREST scale, 22 pt labels (review-sheet rule)."""
    f = font(22)
    w = pad + sum(im.width * scale + pad for _, im in items)
    h = label_h + max(im.height * scale for _, im in items) + pad * 2 + 30
    sheet = Image.new("RGBA", (max(w, 600), h), bg)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), title, fill=(240, 240, 240), font=font(24))
    x = pad
    for lab, im in items:
        d.text((x, label_h), lab, fill=(220, 220, 220), font=f)
        sheet.alpha_composite(K.upscale(im, scale), (x, label_h + 30))
        x += im.width * scale + pad
    return sheet


def gif(frames, path, scale, ms, bg=(122, 160, 80, 255)):
    big = [K.upscale(f, scale) for f in frames]
    out = []
    for b in big:
        c = Image.new("RGBA", b.size, bg)
        c.alpha_composite(b)
        out.append(c.convert("P", palette=Image.ADAPTIVE))
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, disposal=2)


# ----------------------------------------------------------------------------- the scene
def terrain_map():
    C = [[1] * 13 for _ in range(9)]
    path = [(0, 5), (1, 5), (2, 5), (3, 5), (4, 4), (5, 4), (6, 4), (7, 4), (8, 5), (9, 5), (10, 5), (11, 4), (12, 4)]
    for (x, y) in path:
        for dx in (0, 1):
            for dy in (0, 1):
                if 0 <= y + dy < 9 and 0 <= x + dx < 13:
                    C[y + dy][x + dx] = 0
    return C


def scene_new():
    gv = [TL.grass(s) for s in (1, 2, 3, 4)]
    dv = [TL.dirt(s) for s in (1, 2, 3)]
    wang = TL.wang_set(gv[0], TL.dirt(9, pebbles=False))
    ter = TL.render_terrain(terrain_map(), gv, dv, wang).image()
    sc = ter.copy()
    tree = O.flowering_tree().image()
    chest = O.chest().image()
    beetles = B.beetle_frames()
    player = PL.walk("front", {"helmet", "chest", "legs", "boots", "gauntlets"})[0].image()
    player2 = PL.walk("side", (), "floating")[0].image()
    # y-sorted placement (bottom-anchored), like the game
    placed = [
        (tree, 1 * 32, 3 * 32 + 16 - tree.height + 16),
        (chest, 8 * 32, 2 * 32 + 16 - chest.height + 16),
        (player2, 3 * 32 + 16 - 16, 6 * 32 - 72 + 4),
        (player, 6 * 32 + 16 - 16, 5 * 32 - 72 + 8),
        (beetles[1].image(), 9 * 32, 5 * 32 + 6),
        (I.honey_jar().image(), 10 * 32 + 8, 2 * 32 + 20),
    ]
    placed.sort(key=lambda t: t[2] + t[0].height)
    for (im, x, y) in placed:
        sc.alpha_composite(im, (x, y))
    # HUD: hearts + a hotbar
    hb = [U.heart(1).image()] * 4 + [U.heart(0.5).image()]
    for i, h in enumerate(hb):
        sc.alpha_composite(h, (6 + i * 14, 6))
    slots = [(U.slot(selected=True), I.axe()), (U.slot(), I.honey_jar()), (U.slot(), None)]
    x0 = (sc.width - 3 * 38) // 2
    for i, (s, icon) in enumerate(slots):
        sc.alpha_composite(s.image(), (x0 + i * 38, sc.height - 40))
        if icon is not None:
            sc.alpha_composite(icon.image(), (x0 + i * 38 + 2, sc.height - 38))
    return sc


def scene_current():
    """The same layout with today's game art, as the game draws it at 32 px per cell (a 16-px texture
    fills a whole cell, so it shows 2x magnified — that is what the player sees today)."""
    g = K.upscale(cur("Tiles/grass.png"), 2)
    variants = [K.upscale(cur(f"Tiles/grass{s}.png"), 2) for s in ("", "_v2", "_v3", "_v4", "_v5")]
    d = cur("Tiles/dirt.png")
    C = terrain_map()
    rows, cols = len(C) - 1, len(C[0]) - 1
    sc = Image.new("RGBA", (cols * 32, rows * 32))
    for r in range(rows):
        for q in range(cols):
            corners = (C[r][q], C[r][q + 1], C[r + 1][q], C[r + 1][q + 1])
            tile = d if sum(corners) <= 2 else variants[(q * 73856093 ^ r * 19349663) % len(variants)]
            sc.alpha_composite(tile, (q * 32, r * 32))
    tree = cur("Objects/tree_oak.png")
    chest = cur("Objects/chest_wood.png")
    beetle = K.upscale(cur("Bugs/beetle_carrion.png"), 2)
    player = K.upscale(cur("Player/merchant_down.png"), 2)
    player2 = K.upscale(cur("Player/farmer_right.png"), 1)
    jar = cur("Items/honey_icon.png")
    placed = [
        (tree, 1 * 32, 3 * 32 + 16 - tree.height + 16),
        (chest, 8 * 32, 2 * 32 + 16 - chest.height + 16),
        (player2, 3 * 32 + 16 - player2.width // 2, 6 * 32 - player2.height + 4),
        (player, 6 * 32 + 16 - player.width // 2, 5 * 32 - player.height + 8),
        (beetle, 9 * 32 + 4, 5 * 32 + 10),
        (jar, 10 * 32 + 8, 2 * 32 + 20),
    ]
    placed.sort(key=lambda t: t[2] + t[0].height)
    for (im, x, y) in placed:
        sc.alpha_composite(im, (x, y))
    return sc


def main():
    os.makedirs(os.path.join(OUT, "sprites"), exist_ok=True)
    report = []

    # 1) the scene, new vs current
    new, old = scene_new(), scene_current()
    S = 3
    f = font(26)
    sheet = Image.new("RGBA", (old.width * S + new.width * S + 72, new.height * S + 90), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "TODAY'S ART (as the game draws it)", fill=(240, 240, 240), font=f)
    d.text((old.width * S + 48, 16), "NEW — drawn by Claude in code", fill=(240, 240, 240), font=f)
    sheet.alpha_composite(K.upscale(old, S), (24, 60))
    sheet.alpha_composite(K.upscale(new, S), (old.width * S + 48, 60))
    sheet.save(os.path.join(OUT, "01_scene_today_vs_new.png"))
    K.upscale(new, 3).save(os.path.join(OUT, "01b_scene_new_3x.png"))
    new.save(os.path.join(OUT, "sprites", "scene_new_1x.png"))

    # 2) ground
    gv = [TL.grass(s) for s in (1, 2, 3, 4)]
    dv = [TL.dirt(s) for s in (1, 2, 3)]
    wang = TL.wang_set(gv[0], TL.dirt(9, pebbles=False))
    row = [(f"grass {i + 1}", g.image()) for i, g in enumerate(gv)] + [(f"dirt {i + 1}", t.image()) for i, t in enumerate(dv)]
    labelled_row(row, 6, "Ground tiles, 32x32, seamless; one shared palette").save(os.path.join(OUT, "02_ground_tiles.png"))
    wimgs = [(str(k), wang[k].image()) for k in sorted(wang)]
    labelled_row(wimgs[:8], 5, "The 16 grass/dirt transition tiles (1-8)").save(os.path.join(OUT, "02b_transitions_1.png"))
    labelled_row(wimgs[8:], 5, "The 16 grass/dirt transition tiles (9-16)").save(os.path.join(OUT, "02b_transitions_2.png"))
    for i, g in enumerate(gv):
        g.image().save(os.path.join(OUT, "sprites", f"grass_{i + 1}.png"))
    for i, t in enumerate(dv):
        t.image().save(os.path.join(OUT, "sprites", f"dirt_{i + 1}.png"))

    # 3) chest + tree vs today
    ch, tr = O.chest().image(), O.flowering_tree().image()
    labelled_row([("today: chest_wood", cur("Objects/chest_wood.png")), ("new: chest", ch),
                  ("today: tree_oak", cur("Objects/tree_oak.png")), ("new: flowering tree", tr)], 5,
                 "Objects — today vs new", bg=(92, 140, 70, 255)).save(os.path.join(OUT, "03_chest_and_tree.png"))
    ch.save(os.path.join(OUT, "sprites", "chest.png")); tr.save(os.path.join(OUT, "sprites", "flowering_tree.png"))

    # 4) beetle
    fr = beetle_fr = [f.image() for f in B.beetle_frames()]
    labelled_row([("today", K.upscale(cur("Bugs/beetle_carrion.png"), 2))] + [(f"walk {i + 1}", im) for i, im in enumerate(fr)],
                 7, "Burying beetle (beetle_carrion) — 6-frame tripod walk", bg=(122, 160, 80, 255)).save(
        os.path.join(OUT, "04_beetle.png"))
    gif(fr, os.path.join(OUT, "04_beetle_walk.gif"), 8, 90)
    for i, im in enumerate(fr):
        im.save(os.path.join(OUT, "sprites", f"beetle_walk_{i + 1}.png"))

    # 5) icons
    icons = [("today: copper axe", cur("Items/axe_copper_icon.png")), ("new: copper axe", I.axe().image()),
             ("new: iron axe", I.axe("iron").image()), ("new: gold axe", I.axe("gold").image()),
             ("today: honey", cur("Items/honey_icon.png")), ("new: honey jar", I.honey_jar().image())]
    labelled_row(icons, 7, "Item icons (32x32) — one tool family drawn consistently").save(os.path.join(OUT, "05_icons.png"))

    # 6) player: floating hands vs arms, base vs full bronze set
    full = {"helmet", "chest", "legs", "boots", "gauntlets"}
    cells = []
    for hands in ("floating", "arms"):
        for outfit, oname in (((), "base"), (full, "bronze set")):
            for fac in ("front", "side", "back"):
                fr = [x.image() for x in PL.walk(fac, outfit, hands)]
                cells.append((f"{hands} / {oname} / {fac}", fr))
                gif(fr, os.path.join(OUT, f"06_walk_{hands}_{oname.replace(' ', '_')}_{fac}.gif"), 6, 150)
    S = 5
    cw, chh = 32 * S + 14, 72 * S + 14
    sheet = Image.new("RGBA", (12 * cw + 40, 4 * (chh + 36) + 60), (122, 160, 80, 255))
    d = ImageDraw.Draw(sheet)
    d.text((20, 10), "The player — 3 facings x 4 walk frames. Rows: floating hands (approved) and arms; base and bronze set",
           fill=(20, 20, 24), font=font(24))
    r = 0
    for i in range(0, len(cells), 3):
        y = 50 + r * (chh + 36)
        x = 20
        for (lab, fr) in cells[i:i + 3]:
            d.text((x, y), lab, fill=(20, 20, 24), font=font(20))
            for k, im in enumerate(fr):
                sheet.alpha_composite(K.upscale(im, S), (x + k * cw, y + 28))
            x += 4 * cw
        r += 1
    sheet.save(os.path.join(OUT, "06_player_sheet.png"))

    # 6b) the armour pulled apart: every piece is its own layer, drawn on the same skeleton
    for fac in ("front", "side"):
        p = PL.pose(fac, 0)
        img, layers = PL.compose(p, full, "floating")
        bodyc = layers["body"].copy()
        bodyc.outline(K.P.OUTLINE)
        parts = [("body (hair hidden by helmet)", bodyc.image())]
        for k in ("legs", "boots", "chest", "helmet", "hands_near"):
            parts.append((k.replace("hands_near", "gauntlets"), layers[k].image()))
        parts.append(("all together", img.image()))
        labelled_row(parts, 6, f"Separate armour pieces ({fac}) — each is its own layer; they line up in every frame",
                     bg=(122, 160, 80, 255)).save(os.path.join(OUT, f"06b_armour_layers_{fac}.png"))

    # 7) UI
    p = U.panel().image()
    comp = p.copy()
    comp.alpha_composite(U.slot().image(), (8, 24)); comp.alpha_composite(I.axe().image(), (10, 26))
    comp.alpha_composite(U.slot(selected=True).image(), (48, 24)); comp.alpha_composite(I.honey_jar().image(), (50, 26))
    hearts = Image.new("RGBA", (5 * 15 + 2, 14))
    for i, fl in enumerate((1, 1, 1, 0.5, 0)):
        hearts.alpha_composite(U.heart(fl).image(), (1 + i * 15, 1))
    labelled_row([("panel + slots (selected = gold ring)", comp), ("hearts: full / half / empty", hearts)], 5,
                 "UI pieces", bg=(90, 120, 80, 255)).save(os.path.join(OUT, "07_ui.png"))

    # the lint: every drawn sprite is on the master palette
    for name, im in (("chest", ch), ("tree", tr), ("beetle", beetle_fr[0]),
                     ("axe", I.axe().image()), ("honey jar", I.honey_jar().image()), ("grass", gv[0].image()),
                     ("dirt", dv[0].image()), ("player+bronze", PL.walk("front", full)[0].image()),
                     ("panel", p)):
        report.append(K.lint(im, name))
    with open(os.path.join(OUT, "lint.txt"), "w") as fh:
        for rrow in report:
            fh.write(f"{rrow['name']:<15} {rrow['size']:>7}  colours {rrow['colours']:>3}  off-palette {rrow['off_palette']}\n")
    print("wrote", OUT)
    for rrow in report:
        print(rrow)


if __name__ == "__main__":
    main()
