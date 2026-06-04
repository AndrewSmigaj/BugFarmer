#!/usr/bin/env python3
"""Compose a preview scene PNG from the generated sprites, mirroring the game's
placement rules (ground tiles + bottom-center-anchored occupants, y-sorted, each
occupant stretched to its sprite_w x sprite_h target size like TilemapManager does).

This is a DESIGN PREVIEW so you can eyeball how sprites read together without
opening Unity. It intentionally reproduces the in-game per-axis scaling, so any
distortion you see here is what you'd see in the game.

Usage:  python3 make_scene.py [--scale 6] [--out /tmp/scene.png]
"""
import argparse, glob, json, os, random
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
TILES = os.path.join(RES, "Tiles")
OBJS = os.path.join(RES, "Objects")
PLAYER = os.path.join(RES, "Player")
ENT_DIR = os.path.join(ROOT, "nakama", "data", "entities")
CELL = 16  # logical pixels per cell

# Player sprites are pre-authored at a fixed frame size (no target-stretch).
# (sprite_file, cx, cy) bottom-center anchor; drawn at native frame size scaled by S.
PLAYERS = [
    ("farmer_down", 6, 7),      # standing inside the room
    ("merchant_down", 18, 11),  # over in the yard
]


def load_meta():
    meta = {}
    for fn in ("occupants.json", "placeables.json"):
        p = os.path.join(ENT_DIR, fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for k, v in d.items():
            if isinstance(v, dict) and ("sprite_w" in v or "world" in v):
                meta[k] = v
    return meta


def sprite_size_cells(meta, key):
    e = meta.get(key, {})
    w = e.get("sprite_w") or 16
    h = e.get("sprite_h") or 16
    return w, h


def pivot_of(meta, key):
    return (meta.get(key, {}).get("world", {}) or {}).get("pivot", "bc")


def footprint_of(meta, key):
    """Footprint in CELLS (not the stretched sprite_w). A 2-cell-wide object
    occupies the anchor cell plus cells to its right, so its center sits half a
    cell right of the anchor cell's center — mirror TilemapManager's X shift."""
    fp = (meta.get(key, {}).get("world", {}) or {}).get("footprint")
    if isinstance(fp, (list, tuple)) and len(fp) >= 1 and fp[0]:
        return int(fp[0])
    return 1


def load_png(folder, key):
    p = os.path.join(folder, f"{key}.png")
    if not os.path.exists(p):
        return None
    return Image.open(p).convert("RGBA")


# ---- Scene definition -------------------------------------------------------
# Grid is GW x GH cells. Ground is a fill plus rectangular/explicit overrides.
GW, GH = 26, 16

GROUND_FILL = "grass"
GROUND_RECTS = [
    # (tile, x0, y0, x1, y1) inclusive
    ("wood_floor", 1, 2, 10, 9),    # house interior (enclosed box)
    ("stone_path", 11, 9, 13, 15),  # path from house into yard
    ("stone_path", 11, 9, 20, 10),
]

# Occupants: (id, cx, cy) with (cx,cy) = bottom-center anchor cell (floats OK).
OBJECTS = [
    # --- house back wall + door (row y=2); door footprint=2 occupies cells 5-6 ---
    *[("wall_wood", x, 2) for x in range(1, 11) if x not in (5, 6)],
    ("door_wood", 5, 2),
    # --- house side walls (left x=1, right x=10), full height ---
    *[("wall_wood", 1, y) for y in range(3, 10)],
    *[("wall_wood", 10, y) for y in range(3, 10)],
    # --- house front/bottom wall (row y=9) ---
    *[("wall_wood", x, 9) for x in range(2, 10)],
    # --- house interior furniture (all inside x2..9, y3..8) ---
    ("bed_fancy", 2, 7),       # left wall, head to back (footprint=2; code centers it)
    ("bookshelf", 3, 3),       # back wall, left of door
    ("fireplace", 8, 3),       # back wall, right
    ("chest_wood", 8, 5),      # right side, below fireplace
    ("lamp_floor", 9, 8),      # bottom-right corner of room
    ("table_wood", 4, 8),      # along the bottom wall
    ("chair_wood", 2.5, 8),    # flanking the table
    ("chair_wood", 5.5, 8),
    # --- yard: fence line along the right edge ---
    *[("fence_wood", x, 1) for x in range(11, 21)],
    *[("fence_wood", 20, y) for y in range(2, 8)],
    ("gate_wood", 15, 1),
    # --- yard trees & nature ---
    ("tree_oak", 13, 4),
    ("tree_apple", 17, 5),
    ("tree_pine", 19, 3),
    ("bush", 11, 5),
    ("bush", 18, 7),
    ("sunflower", 12, 6),
    ("flower_red", 14, 7),
    ("flower_blue", 15, 6),
    ("flower_yellow", 16, 7),
    ("tall_grass", 19, 8),
    # --- yard furniture/structures ---
    ("bench", 12, 12),
    ("planter_box", 22, 11),
    ("well", 16, 13),
    ("signpost", 11, 11),
    ("sawhorse", 23, 14),
    ("table_stone", 19, 13),
    ("chair_fancy", 21, 13),
    ("lamp_floor", 14, 11),
    ("statue_stone", 24, 8),
    ("bed_basic", 23, 5),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=int, default=6, help="upscale factor per cell")
    ap.add_argument("--assets", default=None,
                    help="root holding Tiles/ and Objects/ (default: game Resources, "
                         "which already holds the cleaned canonical sprites).")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "_generated", "previews", "scene.png"))
    args = ap.parse_args()
    global TILES, OBJS
    if args.assets:
        root = args.assets if os.path.isabs(args.assets) else os.path.join(os.getcwd(), args.assets)
        TILES = os.path.join(root, "Tiles")
        OBJS = os.path.join(root, "Objects")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    S = args.scale
    cpx = CELL * S  # cell size in output px

    meta = load_meta()
    W, H = GW * cpx, GH * cpx
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # 1) Ground fill
    fill = load_png(TILES, GROUND_FILL)
    ground = [[GROUND_FILL] * GW for _ in range(GH)]
    for tile, x0, y0, x1, y1 in GROUND_RECTS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < GW and 0 <= y < GH:
                    ground[y][x] = tile
    # Variant pools: a tile id maps to itself + any {id}_v2/_v3... files on disk.
    def variant_pool(tid):
        files = sorted(glob.glob(os.path.join(TILES, f"{tid}.png")) +
                       glob.glob(os.path.join(TILES, f"{tid}_v*.png")))
        return [os.path.splitext(os.path.basename(f))[0] for f in files] or [tid]

    pools = {}
    tcache = {}
    rng = random.Random(7)  # fixed seed -> reproducible scene
    for y in range(GH):
        for x in range(GW):
            base = ground[y][x]
            pool = pools.setdefault(base, variant_pool(base))
            tid = rng.choice(pool)
            if tid not in tcache:
                im = load_png(TILES, tid)
                tcache[tid] = im.resize((cpx, cpx), Image.NEAREST) if im else None
            t = tcache[tid]
            if t:
                canvas.alpha_composite(t, (x * cpx, y * cpx))

    # 2) Occupants, y-sorted (lower on screen drawn later = in front)
    missing = []
    for oid, cx, cy in sorted(OBJECTS, key=lambda o: (o[2], o[1])):
        img = load_png(OBJS, oid)
        if img is None:
            missing.append(oid)
            continue
        sw, sh = sprite_size_cells(meta, oid)
        # mirror game: stretch trimmed sprite to (sprite_w x sprite_h) cells
        rw, rh = max(1, sw * S), max(1, sh * S)
        spr = img.resize((rw, rh), Image.NEAREST)
        piv = pivot_of(meta, oid)
        # bottom-center of anchor cell (cx,cy), shifted right for wide footprints
        fp_x = footprint_of(meta, oid)
        anchor_x = cx * cpx + cpx / 2 + (fp_x - 1) * 0.5 * cpx
        anchor_y = (cy + 1) * cpx
        if piv == "c":
            px = int(anchor_x - rw / 2)
            py = int(anchor_y - cpx / 2 - rh / 2)
        else:  # bc
            px = int(anchor_x - rw / 2)
            py = int(anchor_y - rh)
        canvas.alpha_composite(spr, (px, py))

    # 3) Player(s): drawn at native frame size (already authored, no stretch)
    for pid, cx, cy in PLAYERS:
        img = load_png(PLAYER, pid)
        if img is None:
            missing.append(pid)
            continue
        pw, ph = img.size
        spr = img.resize((pw * S, ph * S), Image.NEAREST)
        anchor_x = cx * cpx + cpx / 2
        anchor_y = (cy + 1) * cpx
        canvas.alpha_composite(spr, (int(anchor_x - pw * S / 2), int(anchor_y - ph * S)))

    canvas.convert("RGB").save(args.out)
    print(f"Scene: {GW}x{GH} cells @ scale {S} -> {W}x{H}px  {args.out}")
    if missing:
        print(f"Missing sprites (skipped): {', '.join(sorted(set(missing)))}")


if __name__ == "__main__":
    main()
