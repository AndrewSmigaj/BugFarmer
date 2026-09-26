#!/usr/bin/env python3
"""gen_sprites.py - reusable gpt-image-1 sprite batch driver for Bug Farmer.

Encodes the ACTUALLY-WORKING pipeline (no jq, no ComfyUI), per our test run:

    read entity JSON  ->  build prompt from category scaffold  ->  call gpt-image-1
    ->  save response to temp file  ->  decode b64 with python  ->  PIL trim (getbbox)
    ->  save to Resources/  ->  patch .meta import settings  ->  validate transparency

Canonical design reference: architecture_new_object_pipeline.md

Examples:
    # Preview prompts only, no API spend:
    python3 gen_sprites.py --category furniture --dry-run

    # Generate all furniture (placeables.json, category=furniture):
    python3 gen_sprites.py --category furniture

    # Generate specific keys:
    python3 gen_sprites.py --keys table_wood,chair_wood

    # Items (inventory icons):
    python3 gen_sprites.py --source items --keys wood,fiber
"""

import argparse
import base64
import io
import json
import glob
import os
import re
import sys
import urllib.request
import urllib.error

from PIL import Image

# --- Paths -------------------------------------------------------------------
TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS_DIR)
ENTITY_DIR = os.path.join(REPO, "nakama", "data", "entities")
RESOURCES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
RAW_DIR = os.path.join(TOOLS_DIR, "_generated", "raw")
TMP_DIR = "/tmp"

SOURCES = {
    "placeables": os.path.join(ENTITY_DIR, "placeables.json"),
    "occupants": os.path.join(ENTITY_DIR, "occupants.json"),
    "items": os.path.join(ENTITY_DIR, "items.json"),
    "terrain": os.path.join(REPO, "nakama", "data", "tiles.json"),
    "bugs": os.path.join(REPO, "nakama", "data", "bugs.json"),
}

API_URL = "https://api.openai.com/v1/images/generations"
PLAYER_DIR = os.path.join(RESOURCES, "Player")
# ---- art data layer ---------------------------------------------------------
# Prompts are DATA: tools/art/style.json = the global look (palettes + per-family art-direction
# blocks); tools/art/catalog/*.json = per-item silhouettes (`look`) + material overrides. This
# module just assembles them (build_prompt). To add art: add a catalog row (see add-object skill).
ART_DIR = os.path.join(TOOLS_DIR, "art")


def _join(v):
    return "\n".join(v) if isinstance(v, list) else v


def _load_style():
    return json.load(open(os.path.join(ART_DIR, "style.json"), encoding="utf-8"))


def _load_catalog():
    """Merge catalog/*.json. Object files contribute `look`/`materials`; tiles.json and
    blocks.json are special-cased by filename (their own fields)."""
    obj, tiles, blocks = {}, {}, {}
    for fp in sorted(glob.glob(os.path.join(ART_DIR, "catalog", "*.json"))):
        name = os.path.splitext(os.path.basename(fp))[0]
        data = json.load(open(fp, encoding="utf-8"))
        if name == "tiles":
            tiles.update(data)
        elif name == "blocks":
            blocks.update(data)
        else:
            for k, e in data.items():
                obj.setdefault(k, {}).update(e)
    return obj, tiles, blocks


_STYLE = _load_style()
_OBJCAT, _TILECAT, _BLOCKCAT = _load_catalog()

PALETTES = _STYLE["palettes"]
STYLE_BLOCK = _join(_STYLE["object"]["style_block"])
NATURAL_ART_DIRECTION = _join(_STYLE["flora"]["art_direction"])
NATURAL_DESIGN = _join(_STYLE["flora"]["design"])
WALL_ART_DIRECTION = _join(_STYLE["block"]["art_direction"])
WALL_BLOCK = _join(_STYLE["block"]["block"])
TILE_STYLE = _join(_STYLE["tile"]["style"])
TILE_VARIANT_HINTS = _STYLE["tile"]["variants"]
CONNECTOR_BLOCK = _join(_STYLE["connector"])
FLAT_NET = _join(_STYLE["net"])
MINERAL_ART_DIRECTION = _join(_STYLE.get("mineral", {}).get("art_direction", ""))
MINERAL_DESIGN = _join(_STYLE.get("mineral", {}).get("design", ""))
CREATURE_ART_DIRECTION = _join(_STYLE.get("creature", {}).get("art_direction", ""))
CREATURE_DESIGN = _join(_STYLE.get("creature", {}).get("design", ""))
ICON_ART_DIRECTION = _join(_STYLE.get("icon", {}).get("art_direction", ""))
ICON_DESIGN = _join(_STYLE.get("icon", {}).get("design", ""))

OBJECT_DESC = {k: e["look"] for k, e in _OBJCAT.items() if "look" in e}
OBJECT_MATS = {k: e["materials"] for k, e in {**_OBJCAT, **_BLOCKCAT}.items() if "materials" in e}
# optional per-item art FAMILY override (e.g. "mineral" so crystals/rubble read as rock, not plants)
OBJECT_FAMILY = {k: e["family"] for k, e in _OBJCAT.items() if "family" in e}
TILE_DESC = {k: e["look"] for k, e in _TILECAT.items() if "look" in e}
BLOCK_SURFACE = {k: e["surface"] for k, e in _BLOCKCAT.items() if "surface" in e}
ORE_FLECK = {k: e["fleck"] for k, e in _BLOCKCAT.items() if "fleck" in e}
# ---- end art data layer -----------------------------------------------------
PLAYER_DIRS = ("down", "up", "left", "right")
DIR_POSE = {
    "down":  "facing the camera (we see the full face, both eyes)",
    "up":    "facing away (back of head and hair, no face)",
    "left":  "facing left in 3/4 view (NOT pure profile - face still mostly visible)",
    "right": "facing right in 3/4 view (NOT pure profile - face still mostly visible)",
}

# Small distinguishing features for tile VARIANTS (index 1+ = v2, v3, ...).
# Variants must read as the SAME tile type with only micro-differences, NOT a
# different-looking tile - otherwise a field of them looks like a patchwork.
_VARIANT_SAMENESS = (
    " IMPORTANT: keep the EXACT SAME base color, hue, saturation and overall "
    "brightness as the standard tile - this is the same ground type, only with a "
    "couple of tiny detail pixels moved. The change must be barely noticeable.")


def build_tile_prompt(key, variant_idx=0):
    desc = TILE_DESC.get(key, key.replace("_", " "))
    hint = TILE_VARIANT_HINTS[variant_idx] if variant_idx < len(TILE_VARIANT_HINTS) else ""
    return "\n".join([
        "Create a seamless 2D game GROUND TILE texture (pixel art).",
        "",
        f"Tile surface: {desc}.{hint}",
        "",
        TILE_STYLE,
        "",
        "This image will tile across the ground in a 2D top-down game; seam-free repetition is essential.",
    ])


def guess_materials(key, name, category):
    """Pick palette lines by keyword so the prompt carries concrete RGBs."""
    if key in OBJECT_MATS:
        return [PALETTES[m] for m in OBJECT_MATS[key]]
    text = f"{key} {name}".lower()
    mats = []
    if any(w in text for w in ("wood", "oak", "plank", "bench", "table", "chair",
                               "shelf", "book", "saw", "planter", "bed", "fence",
                               "barrel", "crate", "chest")):
        mats.append("wood")
    if any(w in text for w in ("stone", "rock", "brick", "cobble")):
        mats.append("stone")
    if any(w in text for w in ("iron", "metal", "anvil", "steel", "gate")):
        mats.append("metal")
    if any(w in text for w in ("bed", "fancy", "rug", "cushion", "blanket")):
        mats.append("fabric")
    if any(w in text for w in ("plant", "leaf", "bush", "flower", "hedge")):
        mats.append("foliage")
    if not mats:
        mats = ["wood"]
    # de-dup, preserve order
    seen, out = set(), []
    for m in mats:
        if m not in seen:
            seen.add(m)
            out.append(PALETTES[m])
    return out


def spatial_block(pivot, category):
    """Anchoring text is driven by pivot, per the guide (bc=bottom, c=centered).
    Blocks are the exception: full-frame tiling."""
    if category == "block":
        return ("SPATIAL REQUIREMENTS:\n"
                "- COMPLETELY FILL THE FRAME (world tile, no centering)\n"
                "- Clean consistent edges for seamless tiling\n"
                "- For 3/4 blocks: top surface 55-65%, front face 25-35%")
    if pivot == "c":
        return ("SPATIAL REQUIREMENTS:\n"
                "- CENTER the object in the frame around its pivot\n"
                "- No bottom anchoring, no implied ground contact\n"
                "- Leave breathing room on all edges; no drop shadow")
    # default: grounded "bc"
    return ("SPATIAL REQUIREMENTS:\n"
            "- Object base/legs touch the BOTTOM of the frame; front face points DOWN toward the viewer\n"
            "- May extend UPWARD beyond footprint (taller than footprint OK)\n"
            "- Horizontal centering OK; ground contact implied by dark base pixels ONLY\n"
            "- Do NOT draw a ground patch, floor tile, dirt mound, or cast shadow beneath the object")


def design_block(category):
    if category == "furniture":
        return ("DESIGN REQUIREMENTS:\n"
                "- FRONT face DOMINATES (~75%) and faces the viewer flat-on; thin lit top band (~20%) along the upper edge only\n"
                "- Face-on, never corner-on; no left/right side faces\n"
                "- Functional, instantly recognizable silhouette at game zoom\n"
                "- Surface texture (plank/grain/seams) runs horizontally")
    if category in ("crafting", "storage", "structure", "beekeeping", "decoration"):
        return ("DESIGN REQUIREMENTS:\n"
                "- Face-on FRONT view dominates; thin lit top band only; never corner-on, no side faces\n"
                "- Strong plane contrast (lighter top band, mid-tone front face)\n"
                "- Blocky orthogonal shapes; minimum detail that still reads")
    if category == "lighting":
        return ("DESIGN REQUIREMENTS:\n"
                "- Light-emitting part as the brightest accent (warm glow)\n"
                "- Simple recognizable silhouette")
    return ("DESIGN REQUIREMENTS:\n"
            "- Blocky orthogonal shapes; reduce curves to suggestions\n"
            "- Remove detail until readability breaks, then stop")


# Pieces that tile horizontally into a continuous run (fences, walls). Their
# horizontal members MUST bleed off the left+right edges so neighbors connect;
# these are trimmed VERTICALLY ONLY (full width preserved) so the rail/wall body
# spans the whole cell in-game.
def is_block_like(key, category):
    """Cube-tiling blocks/walls (ground blocks, ore blocks, wall blocks)."""
    return category in ("block", "ore") or (category == "structure" and key.startswith("wall"))


def is_linear_connector(key, category):
    return category == "structure" and (
        key.startswith("fence") or key.startswith("wall"))


def block_surface(key):
    if key in BLOCK_SURFACE:
        return BLOCK_SURFACE[key]
    if key.startswith("ore_"):
        return f"grey STONE studded with {ORE_FLECK.get(key, 'metallic ore veins')}"
    return "a solid even surface"


def build_wall_prompt(key, ent, mats):
    """Minecraft-style cube prompt (visible top face) shared by walls, ground blocks and ores,
    so a stacked column / tiled grid reads as one continuous surface. NOT the face-on
    STYLE_BLOCK (which forbids cubes and made these look like footstools)."""
    name = ent.get("name", key)
    parts = [
        "Create a 2D game sprite (single tiling BLOCK, pixel art).",
        "",
        WALL_ART_DIRECTION,
        "",
        f"Asset: {name}",
        "Category: cube-tiling building block",
        "",
        WALL_BLOCK,
        f"- SURFACE TEXTURE: {block_surface(key)}.",
        "",
        "COLOR PALETTE:",
        *[f"- {m}" for m in mats],
        "",
        "This image will be used directly as a tiling block sprite in a 2D game.",
    ]
    return "\n".join(parts)


def build_prompt(key, ent):
    name = ent.get("name", key)
    category = ent.get("category", "furniture")
    world = ent.get("world", {}) or {}
    pivot = world.get("pivot", "bc")
    if key == "fly_netting":
        return FLAT_NET
    mats = guess_materials(key, name, category)
    # Walls, ground blocks (dirt/stone/clay) and ore blocks all use the cube-tiling block prompt
    # so they read as one continuous surface when stacked/tiled.
    if category in ("block", "ore") or (category == "structure" and key.startswith("wall")):
        return build_wall_prompt(key, ent, mats)
    desc_lines = [f"\nWHAT IT IS (draw exactly this): {OBJECT_DESC[key]}"] if key in OBJECT_DESC else []
    family = OBJECT_FAMILY.get(key)                  # optional catalog override
    is_natural = family != "mineral" and category in ("natural", "crop")
    if family == "mineral":                          # faceted rock/crystal, not the plant family
        parts = [
            "Create a 2D game sprite (single mineral/rock formation, pixel art).",
            "",
            MINERAL_ART_DIRECTION,
            "",
            f"Asset: {name}",
            f"Category: {category}",
            *desc_lines,
            "",
            spatial_block(pivot, category),
            "",
            MINERAL_DESIGN,
        ]
    elif family == "creature":                       # small bug/insect, top-down
        parts = [
            "Create a 2D game sprite (single small creature, pixel art).",
            "",
            CREATURE_ART_DIRECTION,
            "",
            f"Asset: {name}",
            f"Category: {category}",
            *desc_lines,
            "",
            spatial_block(pivot, category),
            "",
            CREATURE_DESIGN,
        ]
    elif family == "icon":                           # inventory item icon (tools: diagonal contract)
        parts = [
            "Create a 2D game sprite (single inventory ITEM ICON, pixel art).",
            "",
            ICON_ART_DIRECTION,
            "",
            f"Asset: {name}",
            f"Category: {category}",
            *desc_lines,
            "",
            ICON_DESIGN,
        ]
    elif is_natural:
        parts = [
            "Create a 2D game sprite (single plant, pixel art).",
            "",
            NATURAL_ART_DIRECTION,
            "",
            f"Asset: {name}",
            f"Category: {category}",
            *desc_lines,
            "",
            spatial_block(pivot, category),
            "",
            NATURAL_DESIGN,
        ]
    else:
        parts = [
            "Create a 2D game sprite (single object, pixel art).",
            "",
            "ART DIRECTION: 2D pixel-art object in the style of STARDEW VALLEY furniture and "
            "objects. The object is drawn FLAT and FACE-ON: you stand directly in front of it and "
            "look straight at its front, from only slightly above, so you see mostly its FRONT plus "
            "a thin strip of its top edge. NOT isometric, NOT corner-on, NOT a 3D render. Chunky hard "
            "pixel edges, no anti-aliasing, limited muted palette.",
            "",
            f"Asset: {name}",
            f"Category: {category}",
            *desc_lines,
            "",
            STYLE_BLOCK,
            "",
            spatial_block(pivot, category),
            "",
            design_block(category),
        ]
    if is_linear_connector(key, category):
        parts += ["", CONNECTOR_BLOCK]
    parts += [
        "",
        "COLOR PALETTE:",
        *[f"- {m}" for m in mats],
        "",
        "This image will be used directly as a sprite in a 2D game.",
    ]
    return "\n".join(parts)


def dest_path(source, key, ent):
    """Where the trimmed sprite lands, per the output contract."""
    if source == "items":
        return os.path.join(RESOURCES, "Items", f"{key}_icon.png")
    if source == "terrain":
        return os.path.join(RESOURCES, "Tiles", f"{key}.png")
    if source == "bugs":
        return os.path.join(RESOURCES, "Bugs", f"{key}.png")
    # placeables + occupants -> world sprite
    return os.path.join(RESOURCES, "Objects", f"{key}.png")


def save_tile(raw_png_bytes, key, dest):
    """Cache the raw, then CLEAN the tile (devignette + downscale + quantize to TILE_PX) and save the
    FINISHED tile — one pass, so generating a tile touches exactly this one file (no separate
    pixelclean step). The clean transform lives in pixelclean.py and is imported lazily so dry-runs
    don't need scipy/numpy."""
    import numpy as np
    from pixelclean import clean, TILE_PX
    raw_path = os.path.join(RAW_DIR, f"{key}.png")
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(raw_path, "wb") as f:
        f.write(raw_png_bytes)
    img = Image.open(raw_path).convert("RGBA")
    cleaned = clean(np.asarray(img, dtype=np.uint8), TILE_PX, TILE_PX, True, None, 20)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    Image.fromarray(cleaned).save(dest)
    return (TILE_PX, TILE_PX)


def canvas_size_for(ent):
    """Pick the gpt-image-1 canvas whose orientation matches the asset's target
    aspect ratio, so the trimmed sprite comes out close to sprite_w:sprite_h and
    the runtime's per-axis scale barely distorts it. gpt-image-1 supports only
    square / portrait / landscape, so this is a 3-bucket approximation."""
    w = ent.get("sprite_w") or 1
    h = ent.get("sprite_h") or 1
    ar = w / h
    if ar >= 1.25:
        return "1536x1024"   # landscape (tables, benches, planters)
    if ar <= 0.8:
        return "1024x1536"   # portrait (beds, chairs)
    return "1024x1024"       # near-square (bookshelf, etc.)


EDIT_URL = "https://api.openai.com/v1/images/edits"

# --ref mode: the attached sprite is the family template — the model reproduces its exact
# silhouette/angle/pixel style and changes only what the catalog look asks (material, color).
# This is how a FAMILY (metal bars, tool tiers) stays consistent instead of 7 unrelated takes.
REF_FRAMING = (
    "USE THE ATTACHED IMAGE AS THE EXACT TEMPLATE: reproduce the SAME object with the SAME "
    "silhouette, the SAME camera angle, the SAME proportions, outline and pixel-art style, at "
    "the SAME scale and framing, on the same transparent background. Change ONLY what the "
    "description below requires (material / color / small identifying details).\n\n"
)


def call_api_ref(prompt, ref_path, quality, api_key, model="gpt-image-1", size="1024x1024",
                 background="transparent"):
    """images/edits with a reference sprite (multipart). Feed the RAW 1024px cache of the hero
    (tools/_generated/raw/<key>.png), not the 32px cleaned sprite — the model needs the detail."""
    with open(ref_path, "rb") as f:
        ref_bytes = f.read()
    boundary = "----bugfarmer-ref-boundary"
    parts = []

    def field(name, value):
        parts.append((f"--{boundary}\r\nContent-Disposition: form-data; "
                      f"name=\"{name}\"\r\n\r\n{value}\r\n").encode("utf-8"))

    field("model", model)
    field("prompt", prompt)
    field("size", size)
    field("quality", quality)
    field("background", background)
    field("n", "1")
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"image[]\"; "
                  f"filename=\"ref.png\"\r\nContent-Type: image/png\r\n\r\n").encode("utf-8")
                 + ref_bytes + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    req = urllib.request.Request(
        EDIT_URL, data=body,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = resp.read()
    data = json.loads(payload)
    return base64.b64decode(data["data"][0]["b64_json"])


def call_api(prompt, quality, api_key, model="gpt-image-1", size="1024x1024",
             background="transparent"):
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": size,
        "background": background,
        "quality": quality,
        "output_format": "png",
        "n": 1,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        method="POST")
    # Save response to file first (large b64 breaks naive piping), then decode.
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = resp.read()
    data = json.loads(payload)
    b64 = data["data"][0]["b64_json"]
    return base64.b64decode(b64)


def trim_and_save(raw_png_bytes, key, dest, sprite_w, sprite_h, keep_width=False, k=20):
    """Cache the raw, then CLEAN it to the target sprite size (trim + downscale to sprite_w/h*PPC +
    quantize) and save the FINISHED sprite — one pass, so a regen touches exactly this one file (no
    separate pixelclean step + no git-revert dance). keep_width keeps left/right bleed for blocks/walls.
    clean() lives in pixelclean.py; imported lazily so dry-runs don't need scipy/numpy."""
    import numpy as np
    from pixelclean import clean, PPC
    raw_path = os.path.join(RAW_DIR, f"{key}.png")
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(raw_path, "wb") as f:
        f.write(raw_png_bytes)
    img = Image.open(raw_path).convert("RGBA")
    # Transparency validation (objects come on a transparent background)
    if min(p[3] for p in img.getdata()) >= 255:
        raise ValueError("no transparency in generated image (alpha all opaque)")
    tw, th = max(1, int(sprite_w) * PPC), max(1, int(sprite_h) * PPC)
    cleaned = clean(np.asarray(img, dtype=np.uint8), tw, th, False, None, 20, keep_width=keep_width)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    Image.fromarray(cleaned).save(dest)
    return (tw, th)


def patch_meta(dest):
    """Patch an EXISTING .meta to pixel-art settings. Don't fabricate new ones
    (Unity generates a correct guid-bearing meta on import)."""
    meta = dest + ".meta"
    if not os.path.exists(meta):
        return "new (Unity will import; verify filterMode:0 after)"
    with open(meta, "r") as f:
        txt = f.read()
    orig = txt
    txt = re.sub(r"spriteMode:\s*\d+", "spriteMode: 1", txt)
    txt = re.sub(r"filterMode:\s*\d+", "filterMode: 0", txt)
    if txt != orig:
        with open(meta, "w") as f:
            f.write(txt)
        return "patched (spriteMode:1, filterMode:0)"
    return "ok"


def load_entities(source):
    with open(SOURCES[source]) as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if isinstance(v, dict)}


def select_keys(ents, args):
    if args.keys:
        keys = [k.strip() for k in args.keys.split(",") if k.strip()]
        missing = [k for k in keys if k not in ents]
        if missing:
            sys.exit(f"ERROR: keys not in {args.source}.json: {missing}")
        return keys
    keys = list(ents.keys())
    if args.category:
        keys = [k for k in keys if ents[k].get("category") == args.category]
    if args.limit:
        keys = keys[:args.limit]
    return keys


def normalize_frames(frames):
    """Place each trimmed figure on a COMMON transparent canvas, horizontally
    centered and bottom-aligned (feet on a shared baseline) so swapping frames
    doesn't make the character jump. Native resolution preserved (no resize)."""
    if not frames:
        return frames
    cw = max(f.width for f in frames)
    ch = max(f.height for f in frames)
    out = []
    for f in frames:
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        x = (cw - f.width) // 2
        y = ch - f.height            # bottom-align (feet on baseline)
        canvas.alpha_composite(f, (x, y))
        out.append(canvas)
    return out


def force_n_frames(frames, n=4):
    """Coerce a variable segmentation into exactly n frames for a loopable cycle."""
    k = len(frames)
    if k == 0:
        return []
    if k >= n:
        return frames[:n]
    if k == 3:                       # contact,passing,contact -> ping back through passing
        return [frames[0], frames[1], frames[2], frames[1]]
    if k == 2:
        return [frames[0], frames[1], frames[0], frames[1]]
    return [frames[0]] * n           # k == 1


def make_strip(frames, path, pad=8):
    """Horizontal contact sheet of frames for quick visual review."""
    if not frames:
        return
    h = max(f.height for f in frames)
    w = sum(f.width for f in frames) + pad * (len(frames) - 1)
    strip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for f in frames:
        strip.alpha_composite(f, (x, h - f.height))
        x += f.width + pad
    strip.save(path)


def segment_sheet(sheet_path, min_gap=8, min_w=20):
    """Split a sprite sheet into individual figures by TRANSPARENT column gaps,
    not fixed columns (the model won't space frames evenly). Returns list of
    cropped RGBA frames, left-to-right."""
    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    alpha = sheet.split()[3]
    cols = alpha.load()
    # Which columns contain any non-transparent pixel?
    occupied = []
    for x in range(w):
        on = False
        for y in range(0, h, 2):           # subsample rows for speed
            if cols[x, y] > 16:
                on = True
                break
        occupied.append(on)
    # Group consecutive occupied columns, merging runs separated by < min_gap.
    runs, start = [], None
    gap = 0
    for x in range(w):
        if occupied[x]:
            if start is None:
                start = x
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap >= min_gap:
                    runs.append((start, x - gap + 1))
                    start = None
    if start is not None:
        runs.append((start, w))
    frames = []
    for (l, r) in runs:
        if r - l < min_w:
            continue
        cell = sheet.crop((l, 0, r, h))
        cb = cell.getbbox()
        if cb:
            cell = cell.crop(cb)
        frames.append(cell)
    return frames


def resolve_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        env = os.path.join(TOOLS_DIR, ".env")
        if os.path.exists(env):
            for line in open(env):
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY not found (env or tools/.env)")
    return api_key


def main():
    ap = argparse.ArgumentParser(description="gpt-image-1 sprite batch driver")
    ap.add_argument("--source", choices=list(SOURCES), default="placeables")
    ap.add_argument("--category", help="filter by category (e.g. furniture)")
    ap.add_argument("--keys", help="comma-separated entity keys (overrides category)")
    ap.add_argument("--quality", choices=["low", "medium", "high"], default="medium")
    ap.add_argument("--model", default="gpt-image-1.5", help="image model (default gpt-image-1.5). low quality is a lossy dev-only choice; medium is the standing default")
    ap.add_argument("--dry-run", action="store_true", help="print prompts, no API call")
    ap.add_argument("--force", action="store_true", help="overwrite existing sprites")
    ap.add_argument("--ref", metavar="PNG",
                    help="reference sprite (images/edits): every key reproduces this image's exact "
                         "silhouette/angle/style, changing only its look-row material — use the RAW "
                         "1024px cache of a hero sprite to keep a family consistent")
    ap.add_argument("--limit", type=int, help="cap number of assets")
    ap.add_argument("--segment-sheet", metavar="PATH",
                    help="split an existing sheet into figures by transparent gaps")
    ap.add_argument("--variants", type=int, default=1,
                    help="terrain only: number of seamless variants per tile (v1=base, then _v2, _v3...)")
    args = ap.parse_args()

    if args.segment_sheet:
        frames = segment_sheet(args.segment_sheet)
        base = os.path.splitext(args.segment_sheet)[0]
        print(f"segmented {len(frames)} figure(s) from {args.segment_sheet}")
        for i, fr in enumerate(frames):
            out = f"{base}_seg{i}.png"
            fr.save(out)
            print(f"  seg{i}: size={fr.size} -> {os.path.basename(out)}")
        return

    ents = load_entities(args.source)
    keys = select_keys(ents, args)
    if not keys:
        sys.exit("No matching assets.")

    api_key = None
    if not args.dry_run:
        api_key = resolve_api_key()

    print(f"Source={args.source} quality={args.quality} dry_run={args.dry_run}")
    print(f"Assets ({len(keys)}): {', '.join(keys)}\n")

    is_terrain = args.source == "terrain"

    ok, skipped, failed = 0, 0, 0
    for key in keys:
        ent = ents[key]

        # Terrain: seamless opaque tiles, no trim, optional variants.
        if is_terrain:
            for vi in range(max(1, args.variants)):
                suffix = "" if vi == 0 else f"_v{vi + 1}"
                dest = os.path.join(RESOURCES, "Tiles", f"{key}{suffix}.png")
                prompt = build_tile_prompt(key, vi)
                if args.dry_run:
                    print(f"===== {key}{suffix} -> {os.path.relpath(dest, REPO)} =====")
                    print(prompt)
                    print()
                    continue
                if os.path.exists(dest) and not args.force:
                    print(f"SKIP {key}{suffix}: exists (use --force to overwrite)")
                    skipped += 1
                    continue
                try:
                    png = call_api(prompt, args.quality, api_key, args.model,
                                   size="1024x1024", background="opaque")
                    size = save_tile(png, f"{key}{suffix}", dest)
                    meta_status = patch_meta(dest)
                    print(json.dumps({
                        "tile": f"{key}{suffix}",
                        "dest": os.path.relpath(dest, REPO),
                        "size_px": list(size), "meta": meta_status, "trimmed": False,
                    }))
                    ok += 1
                except urllib.error.HTTPError as e:
                    print(f"FAIL {key}{suffix}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}")
                    failed += 1
                except Exception as e:
                    print(f"FAIL {key}{suffix}: {e}")
                    failed += 1
            continue

        dest = dest_path(args.source, key, ent)
        prompt = build_prompt(key, ent)   # blocks/walls route to build_wall_prompt (cube: top + front face)

        if args.dry_run:
            print(f"===== {key} -> {os.path.relpath(dest, REPO)} =====")
            print(prompt)
            print()
            continue

        if os.path.exists(dest) and not args.force:
            print(f"SKIP {key}: exists (use --force to overwrite)")
            skipped += 1
            continue

        try:
            if args.ref:
                png = call_api_ref(REF_FRAMING + prompt, args.ref, args.quality, api_key,
                                   args.model, size=canvas_size_for(ent))
            else:
                png = call_api(prompt, args.quality, api_key, args.model, size=canvas_size_for(ent))
            _cat = ent.get("category", "")               # blocks/walls keep full width so they tile sideways
            keep_width = is_linear_connector(key, _cat) or _cat in ("block", "ore")
            size = trim_and_save(png, key, dest, ent.get("sprite_w") or 16,
                                 ent.get("sprite_h") or 16, keep_width=keep_width,
                                 k=(8 if args.source == "items" else 20))   # item icons quantize to 8 colors
            meta_status = patch_meta(dest)
            print(json.dumps({
                "asset": key, "category": ent.get("category"),
                "dest": os.path.relpath(dest, REPO),
                "bitmap_size_px": list(size),
                "target_size_px": [ent.get("sprite_w"), ent.get("sprite_h")],
                "pivot": (ent.get("world", {}) or {}).get("pivot"),
                "meta": meta_status, "alpha_verified": True,
            }))
            ok += 1
        except urllib.error.HTTPError as e:
            print(f"FAIL {key}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}")
            failed += 1
        except Exception as e:
            print(f"FAIL {key}: {e}")
            failed += 1

    if not args.dry_run:
        print(f"\nDone: {ok} generated, {skipped} skipped, {failed} failed.")
        print("Next: sync entity JSON to client if changed, then check sprites in Unity.")


if __name__ == "__main__":
    main()
