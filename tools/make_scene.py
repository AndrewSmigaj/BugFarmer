#!/usr/bin/env python3
"""Compose a preview-scene PNG from sprites, mirroring the game's placement rules
(ground tiles + bottom-center/centered occupants, y-sorted, each occupant stretched
to its sprite_w x sprite_h target like TilemapManager does).

This is the DESIGN-PREVIEW / VISUAL-QA tool for zone authoring: build a small grid
(a "scene") and render it to a focused PNG so you can eyeball how items read together
without opening Unity. Missing sprites render as labeled PLACEHOLDER squares (colored
by category), so layout/composition can be iterated before any art exists.

It can render either:
  * a built ZONE on disk:  python3 make_scene.py --zone sim_test [--bounds x0,y0,x1,y1]
  * the built-in demo scene: python3 make_scene.py            (a house + yard vignette)

It also exposes render_scene()/load_zone() as a library for build scripts (tools/zonegen).

Usage: python3 make_scene.py [--zone <id>] [--bounds x0,y0,x1,y1] [--scale 6] [--out PATH]
"""
import argparse, glob, json, os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
TILES = os.path.join(RES, "Tiles")
OBJS = os.path.join(RES, "Objects")
PLAYER = os.path.join(RES, "Player")
BUGS = os.path.join(RES, "Bugs")
ENT_DIR = os.path.join(ROOT, "nakama", "data", "entities")
ZONES_DIR = os.path.join(ROOT, "nakama", "data", "zones")
CELL = 16        # logical pixels per cell
CHUNK = 32       # cells per chunk side (matches world.ChunkSize)

# Placeholder fill color (RGBA) by entity category, so a missing-sprite square reads
# as roughly the right kind of thing. Anything unmapped uses DEFAULT_PH.
CATEGORY_COLORS = {
    "block":       (140, 140, 145, 255),
    "wall":        (150, 120, 90, 255),
    "structure":   (165, 125, 85, 255),
    "furniture":   (200, 170, 120, 255),
    "natural":     (95, 160, 90, 255),
    "tree":        (70, 130, 70, 255),
    "plant":       (120, 185, 95, 255),
    "flower":      (210, 140, 180, 255),
    "crop":        (130, 195, 100, 255),
    "decoration":  (200, 160, 200, 255),
    "container":   (180, 150, 110, 255),
    "storage":     (180, 150, 110, 255),
    "crafting":    (170, 130, 110, 255),
    "light":       (235, 215, 130, 255),
    "lighting":    (235, 215, 130, 255),
    "beekeeping":  (225, 200, 110, 255),
}
DEFAULT_PH = (195, 195, 195, 255)
MISSING_TILE = (60, 80, 60, 255)   # ground placeholder

# Built-in demo scene (used when --zone is not given): a cottage + yard vignette.
PLAYERS = [("farmer_down", 6, 7), ("merchant_down", 18, 11)]
DEMO_GW, DEMO_GH = 26, 16
DEMO_GROUND_FILL = "grass"
DEMO_GROUND_RECTS = [
    ("wood_floor", 1, 2, 10, 9),
    ("stone_path", 11, 9, 13, 15),
    ("stone_path", 11, 9, 20, 10),
]
DEMO_OBJECTS = [
    *[("wall_wood", x, 2) for x in range(1, 11) if x not in (5, 6)],
    ("door_wood", 5, 2),
    *[("wall_wood", 1, y) for y in range(3, 10)],
    *[("wall_wood", 10, y) for y in range(3, 10)],
    *[("wall_wood", x, 9) for x in range(2, 10)],
    ("bed_fancy", 2, 7), ("bookshelf", 3, 3), ("fireplace", 8, 3), ("chest_wood", 8, 5),
    ("lamp_floor", 9, 8), ("table_wood", 4, 8), ("chair_wood", 2.5, 8), ("chair_wood", 5.5, 8),
    *[("fence_wood", x, 1) for x in range(11, 21)], *[("fence_wood", 20, y) for y in range(2, 8)],
    ("gate_wood", 15, 1),
    ("tree_oak", 13, 4), ("tree_apple", 17, 5), ("tree_pine", 19, 3), ("bush", 11, 5), ("bush", 18, 7),
    ("sunflower", 12, 6), ("flower_red", 14, 7), ("flower_blue", 15, 6), ("flower_yellow", 16, 7),
    ("tall_grass", 19, 8),
    ("bench", 12, 12), ("planter_box", 22, 11), ("well", 16, 13), ("signpost", 11, 11),
    ("sawhorse", 23, 14), ("table_stone", 19, 13), ("chair_fancy", 21, 13), ("lamp_floor", 14, 11),
    ("statue_stone", 24, 8), ("bed_basic", 23, 5),
]


# ---- entity metadata --------------------------------------------------------
def load_meta():
    meta = {}
    for fn in ("occupants.json", "placeables.json", "crops.json"):
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
    return e.get("sprite_w") or 16, e.get("sprite_h") or 16


def pivot_of(meta, key):
    return (meta.get(key, {}).get("world", {}) or {}).get("pivot", "bc")


def footprint_of(meta, key):
    """Footprint (width, height) in CELLS. Multi-cell-wide objects sit half a cell right
    of the anchor cell's center (TilemapManager's X shift); multi-cell-DEEP objects (beds,
    tables) have the anchor at the footprint's TOP-LEFT, so the sprite's baseline is the
    BOTTOM of the footprint, not of the anchor cell."""
    fp = (meta.get(key, {}).get("world", {}) or {}).get("footprint")
    if isinstance(fp, (list, tuple)) and len(fp) >= 2:
        return (int(fp[0]) or 1), (int(fp[1]) or 1)
    if isinstance(fp, (list, tuple)) and len(fp) == 1 and fp[0]:
        return int(fp[0]), 1
    return 1, 1


def category_of(meta, key):
    return (meta.get(key, {}) or {}).get("category", "")


def is_flat(meta, key):
    """Flat floor coverings (rugs): lie on the ground, drawn before furniture sits on them."""
    return bool((meta.get(key, {}).get("world", {}) or {}).get("flat"))


def load_png(folder, key):
    p = os.path.join(folder, f"{key}.png")
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None


def placeholder_img(meta, key, rw, rh):
    """A labeled colored square standing in for a missing sprite."""
    color = CATEGORY_COLORS.get(category_of(meta, key), DEFAULT_PH)
    img = Image.new("RGBA", (rw, rh), color)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, rw - 1, rh - 1], outline=(25, 25, 25, 255))
    if rw >= 24 and rh >= 12:
        d.text((2, 2), key[:12], fill=(20, 20, 20, 255))
    return img


def _variant_pool(tid):
    files = sorted(glob.glob(os.path.join(TILES, f"{tid}.png")) +
                   glob.glob(os.path.join(TILES, f"{tid}_v*.png")))
    return [os.path.splitext(os.path.basename(f))[0] for f in files] or [tid]


# ---- core renderer (library) ------------------------------------------------
def render_scene(ground, occupants, meta, scale, out_path, players=None, seed=7, bugs=None,
                 decor=None, record_tiles=None):
    """Render a scene to PNG.
      ground:    GH x GW grid of tile-id strings.
      occupants: list of (id, cx, cy) ANCHOR cells in local cell coords (floats OK).
      players:   optional list of (sprite_id, cx, cy) drawn at native size.
      bugs:      optional list of (sprite_id, cx, cy) from Resources/Bugs, centered, on top.
      decor:     optional list of (id, cx, cy, mult) free-floating ground decor (fruit, etc.) —
                 NOT grid-aligned: drawn from Objects at sprite_size*mult, centered on (cx,cy).
    Returns a report dict (size, placeholders used, missing tiles)."""
    GH = len(ground)
    GW = len(ground[0]) if GH else 0
    cpx = CELL * scale
    canvas = Image.new("RGBA", (GW * cpx, GH * cpx), (0, 0, 0, 0))

    pools, tcache, missing_tiles = {}, {}, set()
    rng = random.Random(seed)
    block_rects = []                       # draw rects of swappable blocks/walls (+ requested ground tiles)
    record_tiles = record_tiles or set()   # ground-tile ids to also record (e.g. {"cave_floor"}) for the viewer
    _blockcells = set()                    # cells with a block on top — their ground tile is hidden, skip it
    for (_oid, _cx, _cy) in occupants:
        _c = (meta.get(_oid, {}) or {}).get("category", "")
        if _c in ("block", "ore") or (_c == "structure" and _oid.startswith("wall")):
            _blockcells.add((int(round(_cx)), int(round(_cy))))
    for y in range(GH):
        for x in range(GW):
            base = ground[y][x]
            tid = rng.choice(pools.setdefault(base, _variant_pool(base)))
            if tid not in tcache:
                im = load_png(TILES, tid)
                tcache[tid] = im.resize((cpx, cpx), Image.NEAREST) if im else None
            t = tcache[tid]
            iy = (GH - 1 - y) * cpx   # flip vertically: zone row 0 at image BOTTOM (game +Y up)
            if t:
                canvas.alpha_composite(t, (x * cpx, iy))
                if base in record_tiles and (x, y) not in _blockcells:
                    block_rects.append({"key": base, "cx": x, "cy": y,
                                        "x": x * cpx, "y": iy, "w": cpx, "h": cpx})
            else:
                missing_tiles.add(base)
                ph = Image.new("RGBA", (cpx, cpx), MISSING_TILE)
                canvas.alpha_composite(ph, (x * cpx, iy))

    # Flat floor coverings (rugs) are drawn FIRST, at ground level over their footprint, so
    # furniture placed on them sits on top.
    for oid, cx, cy in [o for o in occupants if is_flat(meta, o[0])]:
        img = load_png(OBJS, oid)
        if img is None:
            continue
        fw, fh = footprint_of(meta, oid)
        spr = img.resize((fw * cpx, fh * cpx), Image.NEAREST)
        canvas.alpha_composite(spr, (cx * cpx, (GH - cy - fh) * cpx))

    # Occupants AND free-floating decor (fruit) share ONE back-to-front pass, sorted by cy:
    # higher cy (north, away) first, lower cy (south, near) last. So fruit BEHIND a tree (higher
    # cy than the trunk) draws before it and is correctly occluded; fruit in front draws on top.
    placeholders = []
    items = [("occ", oid, cx, cy, 1.0) for (oid, cx, cy) in occupants if not is_flat(meta, oid)]
    items += [("decor", did, cx, cy, mult) for (did, cx, cy, mult) in (decor or [])]
    for kind, oid, cx, cy, mult in sorted(items, key=lambda t: (-t[3], t[2])):
        img = load_png(OBJS, oid)
        sw, sh = sprite_size_cells(meta, oid)
        if kind == "decor":
            if img is None:
                continue
            rw, rh = max(1, int(sw * scale * mult)), max(1, int(sh * scale * mult))
            spr = img.resize((rw, rh), Image.NEAREST)
            ax = cx * cpx + cpx / 2
            cyc = (GH - cy - 0.5) * cpx
            canvas.alpha_composite(spr, (int(ax - rw / 2), int(cyc - rh / 2)))
            continue
        rw, rh = max(1, sw * scale), max(1, sh * scale)
        if img is None:
            spr = placeholder_img(meta, oid, rw, rh)
            placeholders.append(oid)
        else:
            spr = img.resize((rw, rh), Image.NEAREST)
        fp_x, _ = footprint_of(meta, oid)
        anchor_x = cx * cpx + cpx / 2 + (fp_x - 1) * 0.5 * cpx
        # Anchor is the FRONT (south) cell of the footprint; in the flipped image its front
        # edge is the bottom of its band. The sprite baselines there and rises toward the back,
        # filling the footprint (matches TilemapManager's center-pivot placement).
        if pivot_of(meta, oid) == "c":
            cell_center_y = (GH - cy - 0.5) * cpx
            px, py = int(anchor_x - rw / 2), int(cell_center_y - rh / 2)
        else:  # bc
            front_edge_y = (GH - cy) * cpx
            px, py = int(anchor_x - rw / 2), int(front_edge_y - rh)
        canvas.alpha_composite(spr, (px, py))
        _cat = (meta.get(oid, {}) or {}).get("category", "")
        if _cat in ("block", "ore") or (_cat == "structure" and oid.startswith("wall")):
            block_rects.append({"key": oid, "cx": cx, "cy": cy, "x": px, "y": py, "w": rw, "h": rh})

    for pid, cx, cy in (players or []):
        img = load_png(PLAYER, pid)
        if img is None:
            continue
        pw, ph = img.size
        spr = img.resize((pw * scale, ph * scale), Image.NEAREST)
        ax = cx * cpx + cpx / 2
        front_edge_y = (GH - cy) * cpx
        canvas.alpha_composite(spr, (int(ax - pw * scale / 2), int(front_edge_y - ph * scale)))

    # Bugs: small free-floating sprites (flies, butterflies) from Resources/Bugs, sub-grid
    # (cx,cy floats) and scaled by `mult`, drawn last so they sit on top of everything.
    for bid, cx, cy, mult in (bugs or []):
        img = load_png(BUGS, bid)
        if img is None:
            continue
        bw, bh = img.size
        rw, rh = max(1, int(bw * scale * mult)), max(1, int(bh * scale * mult))
        spr = img.resize((rw, rh), Image.NEAREST)
        ax = cx * cpx + cpx / 2
        cyc = (GH - cy - 0.5) * cpx
        canvas.alpha_composite(spr, (int(ax - rw / 2), int(cyc - rh / 2)))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.convert("RGB").save(out_path)
    return {"w": GW * cpx, "h": GH * cpx, "gw": GW, "gh": GH,
            "placeholders": sorted(set(placeholders)), "missing_tiles": sorted(missing_tiles),
            "block_rects": block_rects}


# ---- load a built zone from disk into (ground, occupants) -------------------
def load_zone(zone, bounds=None):
    zdir = zone if os.path.isdir(zone) else os.path.join(ZONES_DIR, zone)
    cfg = json.load(open(os.path.join(zdir, "zone.json")))
    W, H = cfg.get("width") or 256, cfg.get("height") or 256
    x0, y0, x1, y1 = bounds or (0, 0, W - 1, H - 1)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W - 1, x1), min(H - 1, y1)
    gw, gh = x1 - x0 + 1, y1 - y0 + 1
    ground = [["grass"] * gw for _ in range(gh)]
    occupants = []
    for cy in range(y0 // CHUNK, y1 // CHUNK + 1):
        for cx in range(x0 // CHUNK, x1 // CHUNK + 1):
            cf = os.path.join(zdir, f"chunk_{cx}_{cy}.json")
            if not os.path.exists(cf):
                continue
            ch = json.load(open(cf))
            for ly in range(CHUNK):
                for lx in range(CHUNK):
                    gx, gy = cx * CHUNK + lx, cy * CHUNK + ly
                    if not (x0 <= gx <= x1 and y0 <= gy <= y1):
                        continue
                    ground[gy - y0][gx - x0] = ch["ground"][ly][lx]
                    occ = ch["occupants"][ly][lx]
                    if isinstance(occ, dict) and occ.get("anchor"):
                        occupants.append((occ["id"], gx - x0, gy - y0))
    return ground, occupants


def _demo_ground():
    g = [[DEMO_GROUND_FILL] * DEMO_GW for _ in range(DEMO_GH)]
    for tile, x0, y0, x1, y1 in DEMO_GROUND_RECTS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < DEMO_GW and 0 <= y < DEMO_GH:
                    g[y][x] = tile
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone", default=None, help="render a built zone on disk (id or path)")
    ap.add_argument("--bounds", default=None, help="x0,y0,x1,y1 cell viewport (zones only)")
    ap.add_argument("--scale", type=int, default=6, help="upscale factor per cell")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "_generated", "previews", "scene.png"))
    args = ap.parse_args()
    meta = load_meta()

    if args.zone:
        bounds = tuple(int(v) for v in args.bounds.split(",")) if args.bounds else None
        ground, occupants = load_zone(args.zone, bounds)
        players = None
        label = f"zone {args.zone}" + (f" bounds {args.bounds}" if args.bounds else "")
    else:
        ground, occupants, players = _demo_ground(), DEMO_OBJECTS, PLAYERS
        label = "demo"

    r = render_scene(ground, occupants, meta, args.scale, args.out, players)
    print(f"Scene ({label}): {r['gw']}x{r['gh']} cells @ scale {args.scale} -> {r['w']}x{r['h']}px  {args.out}")
    if r["placeholders"]:
        print(f"Placeholders (no sprite yet): {', '.join(r['placeholders'])}")
    if r["missing_tiles"]:
        print(f"Missing ground tiles: {', '.join(r['missing_tiles'])}")


if __name__ == "__main__":
    main()
