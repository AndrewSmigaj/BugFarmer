#!/usr/bin/env python3
"""THROWAWAY — ant_colony_40 (4,0) LAYOUT options (zone-craft OPTIONS step; owner picks).

3 schematic arrangements of the colony's spine + districts + rock field + coast. Fast block-paint
(no 8k render). North = top; coast = west; rock = bottom+SE; queen = deep south. Brown=dirt soil,
grey=rock, blue=sea, dark=trunk/chambers, coloured=districts, gold=Queen dome.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from features.terrain import _vnoise                                         # noqa: E402
from PIL import Image, ImageDraw

N = 256
SHAFTS = [60, 104, 150, 182]


def paint(layout):
    seam = _vnoise(42); coast = _vnoise(43)
    img = Image.new("RGB", (N, N), (150, 100, 60)); px = img.load()
    for y in range(N):
        cx = 16 + 8 * (1 - y / 255.) + (coast(0.06*y,0.0) - 0.5) * 10
        for x in range(N):
            # sea west
            if x < cx:
                px[x, N - 1 - y] = (55, 105, 180); continue
            # rock: full-width bottom band + NE->SW SE intrusion (one field)
            botrock = y < 44 + (seam(0.04*x,0.04*y) - 0.5) * 30
            serock = (x - y) + (seam(0.05*x,0.05*y) - 0.5) * 200 > 150
            if botrock or serock:
                px[x, N - 1 - y] = (120, 122, 130)
            elif x < cx + 3:
                px[x, N - 1 - y] = (150, 130, 90)          # rocky shore hint
    d = ImageDraw.Draw(img)

    def line(a, b, w=4, col=(40, 34, 30)):
        d.line([(a[0], N - 1 - a[1]), (b[0], N - 1 - b[1])], fill=col, width=w)

    def room(c, r, col):
        d.ellipse([c[0] - r, N - 1 - c[1] - r, c[0] + r, N - 1 - c[1] + r], fill=col)

    QUEEN = (118, 32)
    KIND = {"fungus": (90, 160, 90), "nursery": (170, 120, 90), "granary": (200, 180, 110),
            "compost": (110, 90, 70)}
    if layout == "A":  # CENTRAL SPINE — trunk straight down centre, districts flank in pairs
        for sx in SHAFTS:
            line((sx, 255), (118, 205), 4)
        line((118, 205), QUEEN, 7)
        dist = [(62, 176, "fungus"), (174, 176, "fungus"), (58, 128, "nursery"), (180, 128, "nursery"),
                (74, 84, "granary"), (152, 84, "compost")]
        for (cx, cy, k) in dist:
            line((118, cy), (cx, cy), 3); room((cx, cy), 12, KIND[k])
    elif layout == "B":  # SWITCHBACK — trunk zig-zags down; districts nest in the bends
        pts = [(118, 205), (70, 168), (168, 130), (66, 92), (150, 60), QUEEN]
        for sx in SHAFTS:
            line((sx, 255), (118, 205), 4)
        for i in range(len(pts) - 1):
            line(pts[i], pts[i + 1], 7)
        for (cx, cy, k) in [(70, 168, "fungus"), (168, 130, "nursery"), (66, 92, "granary"),
                            (150, 60, "compost"), (110, 150, "nursery"), (180, 176, "fungus")]:
            room((cx, cy), 12, KIND[k])
    else:  # C  ROOT BRANCHES — trunk splits like roots from a gathering gallery; districts at tips
        room((118, 208), 10, (60, 50, 42))
        for sx in SHAFTS:
            line((sx, 255), (118, 208), 4)
        tips = [(56, 150, "fungus"), (186, 150, "fungus"), (78, 96, "granary"), (168, 100, "nursery"),
                (116, 120, "nursery"), (150, 176, "compost")]
        for (cx, cy, k) in tips:
            line((118, 208), (cx, cy), 5); room((cx, cy), 12, KIND[k])
        line((118, 208), QUEEN, 7)
    # the Queen dome + secrets marks
    room(QUEEN, 18, (215, 180, 70))
    d.rectangle([206, N - 1 - 40 - 3, 212, N - 1 - 40 + 3], fill=(230, 210, 120))   # ore-wall (SE rock)
    d.rectangle([116, N - 1 - 12 - 3, 122, N - 1 - 12 + 3], fill=(60, 130, 200))    # deep sump
    return img.resize((512, 512), Image.NEAREST)


if __name__ == "__main__":
    out = "/tmp/claude-1000/-mnt-c-Users-emily-BugFarmer/00dda8ea-1149-4f3a-a6cd-e947771ae3c3/scratchpad"
    imgs = [paint(L) for L in ("A", "B", "C")]
    canvas = Image.new("RGB", (512 * 3 + 40, 542), (20, 20, 20))
    for k, im in enumerate(imgs):
        canvas.paste(im, (k * 522 + 10, 20))
    canvas.save(out + "/colony_layout_options.png")
    repo = os.path.join(ZG, "..", "_generated", "previews", "zones", "ant_colony_40", "_layout_options")
    os.makedirs(repo, exist_ok=True)
    canvas.save(os.path.join(repo, "ALL_options.png"))
    print("ok")
