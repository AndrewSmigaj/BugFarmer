#!/usr/bin/env python3
"""UI MOCKUPS (PIL) — paint the proposed in-game panels with REAL data + real item icons, in the
target Apico-style theme, so we can iterate on the look BEFORE writing the Unity C#. Not shipped; a
design surface. Outputs -> tools/_generated/previews/ui/mock_*.png  (+ a contact sheet).

Style = the game's UIFactory palette (cream #eee4cc text, gold #f6d264 headers, warm wood border, dark
translucent interior) enriched toward Apico: rounded panels, a header strip, beveled item-square slots
with counts + gold selection ring, a coin pill, framed progress bar — and a PER-PURPOSE accent tint
(crafting=amber, dialogue=parchment, shop=green-gold, mannequin=violet, sign=wood).

Run: python3 tools/ui_mock.py
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
OUT = os.path.join(ROOT, "tools", "_generated", "previews", "ui")
os.makedirs(OUT, exist_ok=True)

# ---- palette ----------------------------------------------------------------
INK = (24, 20, 24, 255)
CREAM = (238, 228, 204, 255)
GOLD = (246, 210, 100, 255)
GOLD_D = (214, 170, 58, 255)
WHITE = (250, 250, 250, 255)
RED = (224, 102, 102, 255)
DIM = (150, 140, 126, 255)
INTERIOR = (44, 38, 34, 252)
INTERIOR_HI = (56, 49, 44, 255)
SLOT_BG = (34, 29, 26, 255)
SLOT_RIM = (120, 86, 54, 255)
WOOD = (150, 108, 66, 255)
WOOD_D = (96, 68, 42, 255)

# per-purpose accent (header strip + section tint)
ACCENT = {
    "craft":  (196, 138, 60),    # amber/wood
    "dialog": (170, 150, 110),   # parchment
    "shop":   (120, 156, 86),    # green-gold
    "mann":   (150, 112, 170),   # violet
    "sign":   (138, 102, 64),    # wood
}


def font(sz, bold=True):
    p = "/usr/share/fonts/truetype/ubuntu/Ubuntu-%s.ttf" % ("B" if bold else "R")
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()


F_TITLE = font(22)
F_HEAD = font(15)
F_BODY = font(14, bold=False)
F_BODYB = font(14)
F_COUNT = font(13)
F_SMALL = font(12, bold=False)


# ---- icon loading (mirrors EntityDatabase.GetItemSprite order) ---------------
_icon_cache = {}


def load_icon(item_id, size):
    key = (item_id, size)
    if key in _icon_cache:
        return _icon_cache[key]
    img = None
    for rel in ("Objects/%s.png" % item_id, "Items/%s_icon.png" % item_id,
                "Items/%s.png" % item_id, "Bugs/%s.png" % item_id):
        p = os.path.join(RES, rel)
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            break
    if img is None:
        _icon_cache[key] = None
        return None
    # aspect-preserve fit (letterbox in the square), nearest for pixel art
    w, h = img.size
    s = min(size / w, size / h)
    img = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.NEAREST)
    _icon_cache[key] = img
    return img


# ---- primitives -------------------------------------------------------------
def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def panel(im, x, y, w, h, accent, title):
    """A rounded wood-bordered dark panel with a coloured header strip + title."""
    d = ImageDraw.Draw(im, "RGBA")
    # drop shadow
    rrect(d, (x + 3, y + 4, x + w + 3, y + h + 4), 12, fill=(0, 0, 0, 80))
    # wood border
    rrect(d, (x, y, x + w, y + h), 12, fill=WOOD_D, outline=INK, width=2)
    rrect(d, (x + 2, y + 2, x + w - 2, y + h - 2), 10, fill=WOOD)
    # interior
    rrect(d, (x + 6, y + 6, x + w - 6, y + h - 6), 8, fill=INTERIOR, outline=INK, width=1)
    # header strip (accent-tinted)
    a = accent
    rrect(d, (x + 8, y + 8, x + w - 8, y + 34), 6, fill=(a[0], a[1], a[2], 235))
    d.line((x + 8, y + 34, x + w - 8, y + 34), fill=INK, width=1)
    d.text((x + 16, y + 12), title, font=F_HEAD, fill=INK)
    d.text((x + 15, y + 11), title, font=F_HEAD, fill=CREAM)
    return d


def slot(im, x, y, size, item_id=None, count=0, selected=False, ghost=None, dim=False):
    d = ImageDraw.Draw(im, "RGBA")
    rrect(d, (x, y, x + size, y + size), 5, fill=SLOT_BG, outline=SLOT_RIM, width=2)
    rrect(d, (x + 2, y + 2, x + size - 2, y + 4), 2, fill=(255, 255, 255, 22))  # top bevel
    if item_id:
        ic = load_icon(item_id, size - 8)
        if ic is not None:
            if dim:
                ic = ic.copy()
                a = ic.split()[3].point(lambda v: int(v * 0.35))
                ic.putalpha(a)
            im.alpha_composite(ic, (x + (size - ic.width) // 2, y + (size - ic.height) // 2))
        else:
            d.text((x + 6, y + size // 2 - 6), item_id[:4], font=F_SMALL, fill=DIM)
    elif ghost:
        d.text((x + size // 2 - 9, y + size // 2 - 9), ghost, font=font(16), fill=(120, 120, 132, 150))
    if count > 1:
        s = str(count)
        tw = d.textlength(s, font=F_COUNT)
        d.text((x + size - tw - 4, y + size - 18), s, font=F_COUNT, fill=INK)
        d.text((x + size - tw - 5, y + size - 19), s, font=F_COUNT, fill=WHITE)
    if selected:
        rrect(d, (x - 1, y - 1, x + size + 1, y + size + 1), 6, outline=GOLD, width=2)


def text(d, x, y, s, f=F_BODY, color=CREAM, shadow=True):
    if shadow:
        d.text((x + 1, y + 1), s, font=f, fill=(0, 0, 0, 150))
    d.text((x, y), s, font=f, fill=color)


def button(im, x, y, w, h, label, accent=None, primary=False):
    d = ImageDraw.Draw(im, "RGBA")
    base = GOLD_D if primary else (78, 62, 48, 255)
    top = GOLD if primary else (104, 82, 62, 255)
    rrect(d, (x, y, x + w, y + h), 6, fill=base, outline=INK, width=2)
    rrect(d, (x + 2, y + 2, x + w - 2, y + 2 + (h - 4) // 2), 4, fill=top)
    tw = d.textlength(label, font=F_BODYB)
    text(d, x + (w - tw) / 2, y + (h - 16) / 2, label, F_BODYB,
         color=INK if primary else CREAM, shadow=not primary)


def coin_pill(im, x, y, count):
    d = ImageDraw.Draw(im, "RGBA")
    w = 54 + len(str(count)) * 8
    rrect(d, (x, y, x + w, y + 24), 12, fill=(28, 24, 20, 235), outline=GOLD_D, width=1)
    d.ellipse((x + 5, y + 5, x + 19, y + 19), fill=GOLD, outline=GOLD_D, width=1)
    d.text((x + 9, y + 6), "c", font=F_COUNT, fill=(120, 90, 20))
    text(d, x + 24, y + 4, str(count), F_BODYB, color=GOLD)


def progress(im, x, y, w, h, frac, label, accent):
    d = ImageDraw.Draw(im, "RGBA")
    rrect(d, (x, y, x + w, y + h), h // 2, fill=(20, 17, 15, 255), outline=INK, width=2)
    fw = int((w - 4) * max(0.0, min(1.0, frac)))
    if fw > 4:
        rrect(d, (x + 2, y + 2, x + 2 + fw, y + h - 2), (h - 4) // 2, fill=(242, 178, 64, 255))
        rrect(d, (x + 2, y + 2, x + 2 + fw, y + 2 + (h - 4) // 2), (h - 4) // 4, fill=(255, 214, 120, 200))
    tw = d.textlength(label, font=F_SMALL)
    text(d, x + (w - tw) / 2, y + (h - 13) / 2, label, F_SMALL, color=CREAM)


# ---- data -------------------------------------------------------------------
OCC = json.load(open(os.path.join(ROOT, "nakama/data/entities/occupants.json")))
RECIPES = json.load(open(os.path.join(ROOT, "nakama/data/entities/recipes.json")))
ITEMS = json.load(open(os.path.join(ROOT, "nakama/data/entities/items.json")))
PLACE = json.load(open(os.path.join(ROOT, "nakama/data/entities/placeables.json")))


def nm(idv):
    for src in (ITEMS, PLACE, OCC):
        if idv in src and isinstance(src[idv], dict) and src[idv].get("name"):
            return src[idv]["name"]
    return idv.replace("_", " ").title()


# ---- panels -----------------------------------------------------------------
def m_dialogue():
    im = Image.new("RGBA", (460, 250), (60, 64, 72, 255))
    d = panel(im, 14, 14, 432, 222, ACCENT["dialog"], "Wynn — Carpenter")
    # portrait
    rrect(d, (30, 56, 110, 150), 8, fill=(36, 31, 28, 255), outline=SLOT_RIM, width=2)
    pic = load_icon("carpenter", 72)
    if pic:
        im.alpha_composite(pic, (34 + (72 - pic.width) // 2, 60 + (72 - pic.height) // 2))
    text(d, 128, 60, '"Fine joinery and honest', F_BODY)
    text(d, 128, 80, ' planks. After a furniture', F_BODY)
    text(d, 128, 100, ' book, are you?"', F_BODY)
    button(im, 128, 150, 130, 32, "Trade", primary=True)
    button(im, 270, 150, 130, 32, "Goodbye")
    coin_pill(im, 330, 18, 412)
    return im


def m_shop():
    im = Image.new("RGBA", (560, 430), (60, 64, 72, 255))
    d = panel(im, 14, 14, 532, 402, ACCENT["shop"], "Wynn — Carpenter   ·   Trade")
    coin_pill(im, 430, 18, 412)
    s = OCC["carpenter"]["world"]["shop"]
    known = {"fence_wood"}  # pretend one recipe is already known (greyed)
    y = 50
    text(d, 28, y, "BUY", F_HEAD, GOLD); y += 22
    for i, off in enumerate(s["sells"][:4]):
        slot(im, 28 + i * 52, y, 44, off["id"], 1)
        text(ImageDraw.Draw(im), 28 + i * 52, y + 46, "%dc" % off["price"], F_SMALL, GOLD)
    y += 74
    text(d, 28, y, "LEARN  (recipes)", F_HEAD, GOLD); y += 22
    for i, off in enumerate(s["recipes"][:6]):
        kn = off["id"] in known
        slot(im, 28 + i * 52, y, 44, off["id"], 1, dim=kn)
        lab = "known" if kn else "%dc" % off["price"]
        text(ImageDraw.Draw(im), 28 + i * 52, y + 46, lab, F_SMALL, DIM if kn else GOLD)
    y += 74
    text(d, 28, y, "RECIPE BOOKS", F_HEAD, GOLD); y += 22
    for i, off in enumerate(s.get("books", [])[:3]):
        ry = y + i * 50
        slot(im, 28, ry, 44, "bookshelf", 1)
        text(ImageDraw.Draw(im), 80, ry + 4, nm(off["id"]), F_BODYB, CREAM)
        text(ImageDraw.Draw(im), 80, ry + 24, "%dc  —  teaches the whole set" % off["price"], F_SMALL, GOLD)
    # SELL strip (right)
    text(d, 360, 50, "SELL", F_HEAD, GOLD)
    for i, it in enumerate(["plank", "wood", "apple"]):
        slot(im, 360 + (i % 3) * 52, 72, 44, it, [12, 8, 3][i])
    return im


def m_station():
    im = Image.new("RGBA", (560, 300), (60, 64, 72, 255))
    d = panel(im, 14, 14, 532, 272, ACCENT["craft"], "Furnace")
    r = RECIPES["iron_bar"]
    # recipe list (left)
    text(d, 28, 48, "RECIPES", F_HEAD, GOLD)
    for i, rid in enumerate(["iron_bar", "copper_bar", "glass", "steel_bar"]):
        slot(im, 28 + (i % 2) * 52, 70 + (i // 2) * 52, 44, rid, 1, selected=(rid == "iron_bar"))
    # I/O (middle): inputs -> output
    text(d, 170, 48, "iron_bar  ·  20s", F_HEAD, CREAM)
    dd = ImageDraw.Draw(im)
    text(dd, 170, 72, "Inputs", F_SMALL, DIM)
    for i, io in enumerate(r["inputs"]):
        have = [4, 9][i]
        slot(im, 170 + i * 52, 90, 44, io["item"], 0)
        ok = have >= io["count"]
        text(dd, 170 + i * 52, 136, "%d/%d" % (have, io["count"]), F_SMALL, CREAM if ok else RED)
    text(dd, 170 + len(r["inputs"]) * 52, 100, "->", font(20), GOLD)
    slot(im, 170 + len(r["inputs"]) * 52 + 26, 90, 44, r["output"]["item"], 0)
    text(dd, 170 + len(r["inputs"]) * 52 + 26, 136, "x%d" % r["output"]["count"], F_SMALL, GOLD)
    # qty + craft
    button(im, 170, 162, 28, 26, "-")
    rrect(dd, (202, 162, 240, 188), 5, fill=SLOT_BG, outline=SLOT_RIM, width=2)
    text(dd, 216, 166, "3", F_BODYB, CREAM)
    button(im, 244, 162, 28, 26, "+")
    button(im, 280, 162, 100, 26, "Craft", primary=True)
    # progress bar + queue (slow station)
    progress(im, 170, 200, 250, 18, 0.45, "Smelting  —  11s left", ACCENT["craft"])
    text(dd, 170, 224, "Queue:  iron_bar  x3", F_SMALL, CREAM)
    # output grid (right)
    text(d, 430, 48, "OUTPUT", F_HEAD, GOLD)
    for i in range(4):
        slot(im, 430 + (i % 2) * 52, 70 + (i // 2) * 52, 44, "iron_bar" if i == 0 else None, 2 if i == 0 else 0)
    return im


def m_mannequin():
    im = Image.new("RGBA", (380, 320), (60, 64, 72, 255))
    d = panel(im, 14, 14, 352, 292, ACCENT["mann"], "Mannequin — Outfit")
    # preview (left) — the dressed figure
    rrect(d, (30, 56, 150, 290), 8, fill=(32, 28, 26, 255), outline=SLOT_RIM, width=2)
    fig = load_icon("mannequin_dress_red", 110)
    if fig:
        im.alpha_composite(fig, (50, 110))
    # equip slots (right, head/body/arms/legs/feet)
    cells = [("head", "leather_cap", 250, 56), ("body", "leather_chest", 250, 108),
             ("arms", None, 200, 108), ("arms2", None, 300, 108),
             ("legs", "leather_pants", 250, 160), ("feet", None, 226, 212), ("feet2", None, 274, 212)]
    ghosts = {"head": "H", "body": "B", "arms": "A", "arms2": "A", "legs": "L", "feet": "F", "feet2": "F"}
    for key, item, x, y in cells:
        slot(im, x, y, 44, item, 1 if item else 0, ghost=ghosts[key] if not item else None)
    text(ImageDraw.Draw(im), 196, 264, "Drag clothing from your bag", F_SMALL, DIM)
    return im


def m_sign():
    im = Image.new("RGBA", (340, 200), (60, 64, 72, 255))
    d = panel(im, 14, 14, 312, 172, ACCENT["sign"], "Signpost")
    # carved board
    rrect(d, (34, 56, 306, 168), 8, fill=(120, 86, 54, 255), outline=INK, width=2)
    rrect(d, (40, 62, 300, 162), 6, fill=(150, 110, 70, 255))
    lines = [("SW", "the Lake"), ("S", "the Mines"), ("W", "Honeyford")]
    yy = 74
    for arr, dest in lines:
        text(d, 56, yy, arr + " ->", F_BODYB, (60, 44, 28))
        text(d, 110, yy, dest, F_BODYB, (44, 32, 20))
        yy += 30
    return im


def main():
    panels = {
        "dialogue": m_dialogue(), "shop": m_shop(), "station": m_station(),
        "mannequin": m_mannequin(), "sign": m_sign(),
    }
    for name, im in panels.items():
        p = os.path.join(OUT, "mock_%s.png" % name)
        im.convert("RGB").save(p)
        print("wrote", p, im.size)
    # contact sheet
    pad = 16
    W = max(im.width for im in panels.values()) * 2 + pad * 3
    H = sum(im.height for im in list(panels.values())[:3]) + pad * 4
    sheet = Image.new("RGBA", (W, H), (46, 50, 58, 255))
    # left column: dialogue, shop ; right column: station, mannequin, sign
    x1, y = pad, pad
    for n in ("dialogue", "shop"):
        sheet.alpha_composite(panels[n], (x1, y)); y += panels[n].height + pad
    x2, y = pad * 2 + max(panels["dialogue"].width, panels["shop"].width), pad
    for n in ("station", "mannequin", "sign"):
        sheet.alpha_composite(panels[n], (x2, y)); y += panels[n].height + pad
    sp = os.path.join(OUT, "mock_ALL.png")
    sheet.convert("RGB").save(sp)
    print("wrote", sp, sheet.size)


if __name__ == "__main__":
    main()
