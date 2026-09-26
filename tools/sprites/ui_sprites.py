#!/usr/bin/env python3
"""Hand-authored UI sprite kit (pixkit text grids) — warm wood + parchment.

Everything the programmatic UI needs: 9-slice panels, slot frames (item/bug/
equip + selected/hover rings), equipment ghost icons, the keycap-E badge,
magnifier, divider, close button, coin. Borders for 9-slice are NOT stored in
metas — UIFactory passes them to Sprite.Create (see UIFactory.BORDERS).

Outputs -> Resources/UI/*.png ; preview -> tools/_generated/previews/ui/kit.png
Run: python3 tools/sprites/ui_sprites.py
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from player_sprites import pixkit  # noqa: E402

RES = os.path.normpath(os.path.join(HERE, "..", "BugFarmerClient", "Assets",
                                    "Resources", "UI"))
PREVIEW = os.path.join(HERE, "_generated", "previews", "ui")

PAL = {
    "o": (24, 20, 24, 255),          # the game's outline
    # wood frame ramp
    "W": (158, 112, 70, 255), "w": (122, 86, 52, 255),
    "u": (90, 62, 38, 255), "U": (64, 44, 28, 255),
    # panel interior (slightly translucent so the world reads through a hair)
    "K": (40, 34, 31, 238), "k": (52, 45, 41, 238),
    # parchment
    "P": (240, 228, 198, 255), "p": (224, 208, 172, 255), "q": (198, 178, 140, 255),
    # gold / selection
    "G": (246, 210, 100, 255), "g": (214, 170, 58, 255), "d": (162, 120, 34, 255),
    # bug-slot green rim
    "F": (104, 164, 96, 255), "f": (72, 128, 68, 255),
    # ghost silhouettes (faint)
    "1": (214, 214, 224, 115), "2": (164, 164, 178, 85),
    # hover ring
    "H": (255, 255, 255, 95),
    # misc
    "R": (196, 84, 70, 255),         # close-button red
    "e": (52, 44, 38, 255),          # keycap letter / dark detail
    "m": (140, 150, 165, 255), "M": (190, 200, 215, 255),  # magnifier metal/glass
}

# ---- 9-slice panels (24x24, 7px border) ---------------------------------------
PANEL_WOOD = """
.ooooooooooooooooooooo..
oWWWWWWWWWWWWWWWWWWWWWo.
oWwwwwwwwwwwwwwwwwwwwuo.
oWwuuuuuuuuuuuuuuuuuwuo.
oWwuooooooooooooooouwuo.
oWwuoKKKKKKKKKKKKKKouwuo
oWwuoKkkkkkkkkkkkkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkKKKKKKKKKKkKouwuo
oWwuoKkkkkkkkkkkkkKouwuo
oWwuoKKKKKKKKKKKKKKouwuo
oWwuooooooooooooooouwuo.
oWwuuuuuuuuuuuuuuuuuwuo.
oWwwwwwwwwwwwwwwwwwwwuo.
oUUUUUUUUUUUUUUUUUUUUUo.
.ooooooooooooooooooooo..
"""

PANEL_PARCHMENT = """
.oooooooooooooooooooooo.
oqqqqqqqqqqqqqqqqqqqqqqo
oqPPPPPPPPPPPPPPPPPPPPqo
oqPPPPPPPPPPPPPPPPPPPPqo
oqPPppppppppppppppppPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPpPPPPPPPPPPPPPPpPPqo
oqPPppppppppppppppppPPqo
oqPPPPPPPPPPPPPPPPPPPPqo
oqqPPPPPPPPPPPPPPPPPqqqo
oqqqqqqqqqqqqqqqqqqqqqqo
.oooooooooooooooooooooo.
"""

# ---- slot frames (20x20; equip 24x24) ------------------------------------------
SLOT_FRAME = """
.oooooooooooooooooo.
oWwwwwwwwwwwwwwwwwuo
owooooooooooooooooou
owoKKKKKKKKKKKKKKouo
owoKkkkkkkkkkkkkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkKKKKKKKKKKkKouo
owoKkkkkkkkkkkkkKouo
owoKKKKKKKKKKKKKKouo
owooooooooooooooooou
ouuuuuuuuuuuuuuuuuuo
.oooooooooooooooooo.
"""

KEYCAP_E = """
..oooooooooo..
.oPPPPPPPPPPo.
oPPPPPPPPPPppo
oPPeeeeeePPppo
oPPeePPPPPPppo
oPPeePPPPPPppo
oPPeeeeePPPppo
oPPeePPPPPPppo
oPPeePPPPPPppo
oPPeeeeeePPppo
oPPppppppppppo
oppppppppppppo
.oqqqqqqqqqqo.
..oooooooooo..
"""

ICON_MAGNIFIER = """
................
....ooooo.......
...oMMMMMo......
..oMMmmmMMo.....
..oMmPPPmMo.....
..oMmPPPmMo.....
..oMmPPPmMo.....
..oMMmmmMMo.....
...oMMMMMoo.....
....oooooomo....
.........omm o..
..........ommo..
...........ommo.
............oo..
................
................
"""

DIVIDER_H = """
oooooooooooooooo
uWWWWWWWWWWWWWWu
uwwwwwwwwwwwwwwu
oooooooooooooooo
"""

BTN_CLOSE = """
..oooooooooo..
.oWwwwwwwwwuo.
oWwRRwwwwRRwuo
oWwRRRwwRRRwuo
oWwwRRRRRRwwuo
oWwwwRRRRwwwuo
oWwwwRRRRwwwuo
oWwwRRRRRRwwuo
oWwRRRwwRRRwuo
oWwRRwwwwRRwuo
.owwwwwwwwwuo.
.ouuuuuuuuuuo.
..oooooooooo..
..............
"""

ICON_COIN = """
..oooooooo....
.oGGGGGGGGo...
oGGggggggGGo..
oGgGGGGGGgGo..
oGgGGddGGgGo..
oGgGGddGGgGo..
oGgGGddGGgGo..
oGgGGGGGGgGo..
oGGggggggGGo..
.oGGGGGGGGo...
..oooooooo....
..dddddddd....
..............
..............
"""

# ---- equipment ghost icons (16x16, faint silhouettes) --------------------------
GHOSTS = {
    "ghost_head": """
................
.....111111.....
....11111111....
...1111111111...
...1111111111...
...1122222211...
...11.2222.11...
................
................
................
................
................
................
................
................
................
""",
    "ghost_body": """
................
...11......11...
..1111111111 1..
..111111111111..
..211111111112..
..2.11111111.2..
....11111111....
....11111111....
....11111111....
....22222222....
................
................
................
................
................
................
""",
    "ghost_arms": """
................
....1.1.1.1.....
....1111111.....
....1111111.....
...211111112....
...2111111122...
....1111111.2...
....1111111.....
....1111111.....
....2222222.....
................
................
................
................
................
................
""",
    "ghost_legs": """
................
....11111111....
....11111111....
....1111 111....
....111..111....
....111..111....
....111..111....
....111..111....
....211..112....
....222..222....
................
................
................
................
................
................
""",
    "ghost_feet": """
................
................
................
................
......111.......
......111.......
......111.......
......1111......
......11111.....
......111111....
......2222221...
.......222222...
................
................
................
................
""",
    "ghost_accessory": """
................
......1111......
.....112211.....
....11....11....
....11....11....
....11....11....
....11....11....
.....112211.....
......1111......
................
................
................
................
................
................
................
""",
}


def _fixwidth(grid):
    """Pad/validate rows (spaces become transparent)."""
    rows = [r.replace(" ", ".") for r in grid.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    return ["{:.<{w}}".format(r, w=w) for r in rows]


def render(grid):
    return pixkit.render(_fixwidth(grid), PAL, mode="baked")


def main():
    pieces = {
        "panel_wood": PANEL_WOOD, "panel_parchment": PANEL_PARCHMENT,
        "slot_frame": SLOT_FRAME, "keycap_e": KEYCAP_E,
        "icon_magnifier": ICON_MAGNIFIER, "divider_h": DIVIDER_H,
        "btn_close": BTN_CLOSE, "icon_coin": ICON_COIN,
    }
    pieces.update(GHOSTS)

    # derived variants: bug slot (green rim) + equip slot (gold rivets) + rings
    cells = []
    for name, grid in pieces.items():
        im = render(grid)
        pixkit.save(im, os.path.join(RES, f"{name}.png"))
        cells.append(im)

    # slot_frame_bug: recolor the wood rim to green
    bug = render(SLOT_FRAME.replace("W", "F").replace("w", "f"))
    pixkit.save(bug, os.path.join(RES, "slot_frame_bug.png"))
    cells.append(bug)

    # slot_frame_equip: 24x24 — the 20x20 frame with gold rivet corners on a
    # 24 canvas (pad 2 each side, rivets at the corners)
    from PIL import Image
    base = render(SLOT_FRAME)
    eq = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    eq.paste(base, (2, 2), base)
    riv = render("""
.oo.
oGgo
ogdo
.oo.
""")
    for x, y in ((0, 0), (20, 0), (0, 20), (20, 20)):
        eq.paste(riv, (x, y), riv)
    pixkit.save(eq, os.path.join(RES, "slot_frame_equip.png"))
    cells.append(eq)

    # selection ring (gold) + hover ring (white), 20x20 outlines only
    ring = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    px = ring.load()
    for i in range(20):
        for (x, y) in ((i, 0), (i, 19), (0, i), (19, i)):
            px[x, y] = PAL["G"]
        for (x, y) in ((i, 1), (i, 18), (1, i), (18, i)):
            if px[x, y][3] == 0:
                px[x, y] = PAL["g"]
    pixkit.save(ring, os.path.join(RES, "slot_selected.png"))
    cells.append(ring)
    hov = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    px = hov.load()
    for i in range(20):
        for (x, y) in ((i, 0), (i, 19), (0, i), (19, i)):
            px[x, y] = PAL["H"]
    pixkit.save(hov, os.path.join(RES, "slot_hover.png"))
    cells.append(hov)

    pixkit.save(pixkit.contact_sheet(cells, cols=6, scale=6),
                os.path.join(PREVIEW, "kit.png"))
    print(f"UI kit -> {RES} ({len(cells)} sprites); preview -> {PREVIEW}/kit.png")


if __name__ == "__main__":
    main()
