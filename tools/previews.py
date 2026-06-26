#!/usr/bin/env python3
"""Content CATALOG generator — the ONE command that rebuilds the "what's in the game" previews.

    python3 tools/previews.py            # rebuild the whole catalog

Output (plain PNGs in folders — browse them in a file explorer, no html, no registry):

    tools/_generated/previews/catalog/<group>/<id>.png    one object, rendered at its IN-GAME size
    tools/_generated/previews/catalog/<group>/_sheet.png  every object in that group on one labeled sheet

So `catalog/furniture/` shows the whole furniture set on `_sheet.png` AND every piece as its own
thumbnail beside it. Groups (furniture, blocks, nature, bugs, tiles, tools, armor, …) come straight
from each entity's `category` in nakama/data/entities/*.json + bugs.json + tiles.json, and the sprite
is read live from Resources/. Replace a sprite or add an entity, re-run, and the catalog updates —
nothing is hand-listed, so it can never drift from what's actually in the game.

(Zone + scene previews are produced by the zone/scene build scripts into previews/zones/<zone>/ and
previews/examples/ — this tool only owns the content catalog.)
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
DATA = os.path.join(ROOT, "nakama", "data")
OUT = os.path.join(ROOT, "tools", "_generated", "previews", "catalog")

ZOOM = 4                      # integer NEAREST upscale so the in-game pixels stay crisp + readable
CELL, BOX, LABEL, COLS = 80, 64, 14, 8
BG = (38, 38, 44, 255)

# raw entity `category` -> the catalog folder it lands in. Unknown categories fall through to their own
# name (so nothing is ever dropped); this dict only makes the common ones read nicely.
GROUP = {
    "block": "blocks", "ore": "ore",
    "furniture": "furniture", "decoration": "decorations", "structure": "structures",
    "crafting": "crafting", "lighting": "lighting", "storage": "storage", "beekeeping": "beekeeping",
    "natural": "nature", "nature": "nature", "flora": "nature", "crop": "crops",
    "tool": "tools", "armor": "armor", "resource": "resources", "seed": "seeds",
    "consumable": "consumables", "backpack": "gear",
}

# (json file, default Resources subdir, sprite-name suffix, force-group-override or None)
SOURCES = [
    ("entities/placeables.json", "Objects", "", None),
    ("entities/occupants.json", "Objects", "", None),
    ("entities/items.json", "Items", "_icon", None),
    ("bugs.json", "Bugs", "", "bugs"),
    ("tiles.json", "Tiles", "", "tiles"),
]


def _entries(path):
    d = json.load(open(path))
    items = d.items() if isinstance(d, dict) else [(v.get("id"), v) for v in d]
    for k, v in items:
        if isinstance(k, str) and k.startswith("_"):
            continue
        if isinstance(v, dict):
            yield k, v


def _sprite(eid, v, subdir, suffix):
    """Resolve an entity's sprite PNG. Honours an explicit sprite_path, else <subdir>/<id><suffix>.png."""
    cands = []
    sp = v.get("sprite_path")
    if sp:
        sp = sp.replace("Resources/", "").lstrip("/")
        cands.append(os.path.join(RES, sp if sp.endswith(".png") else sp + ".png"))
    cands.append(os.path.join(RES, subdir, f"{eid}{suffix}.png"))
    cands.append(os.path.join(RES, subdir, f"{eid}.png"))           # fallback: no suffix
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def _ingame(img, v):
    """Render the sprite at its true in-game size: NEAREST-scale to sprite_w x sprite_h (what the runtime
    does), then integer-upscale by ZOOM so it's crisp and readable. No data size -> use the sprite as-is."""
    w, h = v.get("sprite_w"), v.get("sprite_h")
    if w and h:
        img = img.resize((int(w), int(h)), Image.NEAREST)
    return img.resize((img.width * ZOOM, img.height * ZOOM), Image.NEAREST)


def collect():
    """-> {group: [(id, name, PIL.Image|None), ...]} gathered live from data + sprite files."""
    groups = {}
    for jf, subdir, suffix, override in SOURCES:
        path = os.path.join(DATA, jf)
        if not os.path.exists(path):
            continue
        for eid, v in _entries(path):
            group = override or GROUP.get(v.get("category", ""), v.get("category") or "misc")
            sp = _sprite(eid, v, subdir, suffix)
            img = _ingame(Image.open(sp).convert("RGBA"), v) if sp else None
            groups.setdefault(group, []).append((eid, v.get("name", eid), img))
    return groups


def _fit(img, box):
    s = min(box / img.width, box / img.height, 1.0) if img.width and img.height else 1.0
    if s < 1.0:
        img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.NEAREST)
    return img


def write_individual(group, eid, img):
    d = os.path.join(OUT, group)
    os.makedirs(d, exist_ok=True)
    (img if img is not None else Image.new("RGBA", (16, 16))).save(os.path.join(d, f"{eid}.png"))


def write_sheet(group, entries):
    font = ImageFont.load_default()
    entries = sorted(entries, key=lambda e: e[0])
    rows = (len(entries) + COLS - 1) // COLS
    W = COLS * CELL
    H = 30 + rows * (CELL + LABEL)
    sheet = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 9), f"{group}  ({len(entries)})", fill=(235, 235, 235), font=font)
    for i, (eid, _name, img) in enumerate(entries):
        cx, cy = (i % COLS) * CELL, 30 + (i // COLS) * (CELL + LABEL)
        if img is None:
            dr.rectangle([cx + 10, cy + 10, cx + BOX, cy + BOX], outline=(200, 80, 80))
            dr.text((cx + 12, cy + BOX // 2), "no art", fill=(200, 80, 80), font=font)
        else:
            fit = _fit(img, BOX)
            sheet.alpha_composite(fit, (cx + (CELL - fit.width) // 2, cy + (BOX - fit.height) // 2 + 4))
        dr.text((cx + 3, cy + BOX + 4), eid[:13], fill=(205, 205, 205), font=font)
    os.makedirs(os.path.join(OUT, group), exist_ok=True)
    sheet.save(os.path.join(OUT, group, "_sheet.png"))


def main():
    groups = collect()
    total = 0
    for group, entries in sorted(groups.items()):
        for eid, _name, img in entries:
            write_individual(group, eid, img)
            total += 1
        write_sheet(group, entries)
        missing = sum(1 for _, _, im in entries if im is None)
        print(f"  {group:14} {len(entries):3} items"
              + (f"  ({missing} missing art)" if missing else ""))
    print(f"\ncatalog -> {OUT}   ({total} objects across {len(groups)} groups)")


if __name__ == "__main__":
    main()
