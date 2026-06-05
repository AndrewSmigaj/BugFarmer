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
import os
import re
import sys
import urllib.request
import urllib.error

from PIL import Image

# --- Paths -------------------------------------------------------------------
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
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
}

API_URL = "https://api.openai.com/v1/images/generations"
PLAYER_DIR = os.path.join(RESOURCES, "Player")

# --- Player layered-character system (see CHARACTER_DESIGN_GUIDE.md) ----------
# Base bodies are generated; equipment/clothing layers are EDITS of a base body
# (images/edits) so they register to the real silhouette. 4 skin tones to start.
SKIN_TONES = {
    "light":  "light skin (base 240,205,180; shadow 200,160,135)",
    "medium": "medium warm skin (base 220,175,140; shadow 180,130,100)",
    "tan":    "tan/olive skin (base 190,150,110; shadow 150,110,75)",
    "deep":   "deep brown skin (base 130,90,65; shadow 95,60,40)",
}
# 3-shade ramps (dark, base, light) for recoloring ONE master body -> all tones.
# Base body is SKIN-ONLY (bald, bare) so every opaque pixel maps through the ramp.
SKIN_RAMP = {
    "light":  ((200, 160, 135), (240, 205, 180), (255, 228, 205)),
    "medium": ((180, 130, 100), (220, 175, 140), (245, 205, 175)),
    "tan":    ((150, 110,  75), (190, 150, 110), (220, 185, 145)),
    "deep":   (( 80,  52,  35), (130,  90,  65), (165, 120,  90)),
}


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def recolor_skin(img, tone):
    """Luminance-preserving recolor of a skin-only body to a target tone ramp.
    Preserves shading (per-pixel brightness picks a point on dark->base->light)."""
    dark, base, light = SKIN_RAMP[tone]
    src = img.convert("RGBA")
    px = src.load()
    w, h = src.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            if lum < 0.5:
                rgb = _lerp(dark, base, lum / 0.5)
            else:
                rgb = _lerp(base, light, (lum - 0.5) / 0.5)
            op[x, y] = (rgb[0], rgb[1], rgb[2], a)
    return out
PLAYER_DIRS = ("down", "up", "left", "right")
DIR_POSE = {
    "down":  "facing the camera (we see the full face, both eyes)",
    "up":    "facing away (back of head and hair, no face)",
    "left":  "facing left in 3/4 view (NOT pure profile - face still mostly visible)",
    "right": "facing right in 3/4 view (NOT pure profile - face still mostly visible)",
}

PLAYER_STYLE = (
    "clean 2D pixel-art RPG character in the style of Stardew Valley / classic SNES "
    "top-down RPGs. FLAT front-facing 2D sprite - absolutely NO isometric, NO "
    "voxel, NO 3D tilt, NO angled/overhead perspective. The character faces the camera "
    "straight on. Cute chibi proportions: big rounded head about 40% of total height, "
    "small torso, short stubby limbs. Smooth rounded pixel clusters (not jagged cubes), "
    "soft cel shading with 3-4 shades per color, a clean darker-tone outline (never pure "
    "black). Soft light from top. Readable, charming, polished."
)


def char_sample_prompt(direction, skin_desc, hair, shirt, pants):
    facing = {
        "down":  "standing FACING THE CAMERA (full face, both eyes visible)",
        "up":    "standing with their BACK to the camera (no face, we see hair and back)",
        "left":  "standing turned to face LEFT (3/4 view, most of the face still visible)",
        "right": "standing turned to face RIGHT (3/4 view, most of the face still visible)",
    }[direction]
    return "\n".join([
        "Create a single 2D game character sprite, pixel art.",
        "",
        f"ART DIRECTION: {PLAYER_STYLE}",
        "",
        f"A friendly chibi farmer {facing}.",
        f"Skin: {skin_desc}. Hair: {hair}. Shirt: {shirt}. Pants/overalls: {pants}. "
        "Simple shoes.",
        "Neutral standing pose, arms at sides, centered, full body from head to feet.",
        "ONE character only. Transparent background, NO ground, NO shadow, NO frame, NO text.",
    ])


def body_prompt(tone, direction):
    return "\n".join([
        "Create a 2D game character sprite (single full-body humanoid, pixel art).",
        "",
        f"ART DIRECTION: {PLAYER_STYLE}",
        "",
        f"Character: a chibi person, {DIR_POSE[direction]}.",
        f"Skin: {SKIN_TONES[tone]}.",
        "BALD - completely smooth head, NO hair at all (hair is a separate layer).",
        "Wearing a plain mid-gray short-sleeve shirt and plain mid-gray shorts (a neutral "
        "underlayer; clothing is added as separate layers later). Bare forearms, lower legs, "
        "and feet show skin.",
        "Keep the skin a SINGLE consistent hue across all visible skin (this body gets recolored).",
        "",
        "FRAMING (critical for layer alignment):",
        "- ONE character, standing upright, centered horizontally.",
        "- Feet near the BOTTOM of the frame, top of head near the TOP - fill the vertical space.",
        "- Neutral standing pose, arms straight at sides, legs together. Symmetrical for down/up.",
        "- Transparent background. Render ONLY the character: no ground, no shadow, no props.",
        "",
        "This is the BASE BODY layer of a layered character - clean, uncluttered, skin only.",
    ])


# --- Material palettes (from architecture_new_object_pipeline.md) ------------
PALETTES = {
    "wood": "Wood: dark (70,50,35), base (120,90,60), light (160,130,95)",
    "stone": "Stone: dark (85,85,90), base (120,120,125), light (155,155,160)",
    "metal": "Metal/iron: dark (60,65,70), base (100,105,110), light (150,155,160)",
    "foliage": "Foliage: dark (40,85,40), base (55,120,55), light (80,150,70)",
    "dirt": "Dirt: dark (110,75,40), base (140,95,50), light (165,120,70)",
    "fabric": "Fabric: dark (100,70,100), base (140,100,140), light (180,140,180)",
}

STYLE_BLOCK = """STYLE REQUIREMENTS (the camera angle is the SINGLE MOST important constraint - get it exactly right):
- Reference style: STARDEW VALLEY furniture/objects. The object is a FLAT, FACE-ON 2D sprite. You look at it straight from the FRONT, from only slightly above.
- The FRONT face DOMINATES the sprite (lower ~75%) and faces the viewer dead-on, perfectly flat.
- Only a THIN strip of the top surface is visible as a flat, axis-aligned horizontal BAND along the very top edge (upper ~20%) - just enough to read the object's depth. The top is a thin band, NOT a large surface.
- Show ONLY the front face and that thin top band. NEVER show a left or right side face. NEVER rotate the object corner-on.
- This is NOT isometric, NOT Minecraft, NOT a voxel/3D render. A square top reads as a thin horizontal band, NEVER a tilted diamond or rhombus.
- Every edge is strictly horizontal or vertical. NO 3D corner rotation, NO perspective lines, NO vanishing points, NO converging edges.
- Light source: TOP-LEFT. Depth comes from CONTRAST (lighter top band, mid-tone front face), never from geometric tilt or visible side faces.
- Three-shade coloring per material; no pure black, no pure white; muted saturation.
- Chunky, slightly overbuilt. Transparent background; render ONLY the object - no ground, no floor tile, no cast shadow."""


TILE_STYLE = (
    "Seamless top-down ground TEXTURE tile for a 2D game, viewed straight from directly "
    "above (flat orthographic - NO perspective, NO angle, NOT isometric). "
    "The texture FILLS THE ENTIRE SQUARE FRAME edge to edge and bleeds off all four sides so "
    "many copies tile seamlessly with NO visible seam. "
    "CRITICAL - NO grid lines: absolutely NO border, NO frame, NO outline, NO dark edges, NO "
    "vignette, NO corner shadows, NO drop shadow. Lighting is COMPLETELY FLAT and EVEN across "
    "the whole tile, identical brightness in the center and at every edge and corner, so that "
    "when tiled in a grid you CANNOT see where one tile ends and the next begins. "
    "Chunky pixel-art texture, limited muted natural palette, subtle low-contrast organic "
    "variation spread evenly (no single big feature in the center), hard pixel edges, no anti-aliasing."
)

# Per-tile content hints (face value of the tile surface).
TILE_DESC = {
    "grass": "lush green grass, fine blades with gentle lighter and darker green clumps",
    "dirt": "bare brown soil, fine grain with small pebbles and subtle clods",
    "stone_path": "fitted flat flagstones / cobbles with thin even mortar lines, grey stone",
    "stone_floor": "polished grey stone floor tiles, clean even joints",
    "wood_floor": "wooden plank floor, warm brown planks running horizontally with thin seams",
    "cave_floor": "rough dark grey rocky cave ground with fine rubble",
    "garden_plot": "tilled dark soil in even furrows, ready for planting",
    "garden_plot_wet": "tilled dark soil, damp and darker, in even furrows",
    "mud": "wet brown mud, glossy uneven surface",
    "sand": "fine pale tan sand with gentle ripples",
    "water_shallow": "shallow clear water, light teal with soft ripples",
    "water_deep": "deep water, darker blue with soft ripples",
    "bridge_wood": "wooden bridge planks running horizontally, sturdy brown boards",
    "bridge_stone": "flat stone bridge slabs, grey with even joints",
}

# Small distinguishing features for tile VARIANTS (index 1+ = v2, v3, ...).
# Variants must read as the SAME tile type with only micro-differences, NOT a
# different-looking tile - otherwise a field of them looks like a patchwork.
_VARIANT_SAMENESS = (
    " IMPORTANT: keep the EXACT SAME base color, hue, saturation and overall "
    "brightness as the standard tile - this is the same ground type, only with a "
    "couple of tiny detail pixels moved. The change must be barely noticeable.")
TILE_VARIANT_HINTS = [
    "",  # v1 (base)
    " Nudge two or three tiny blade/speck pixels to slightly different spots." + _VARIANT_SAMENESS,
    " Place one or two tiny accent pixels in different spots." + _VARIANT_SAMENESS,
    " Shift a few single detail pixels very slightly." + _VARIANT_SAMENESS,
]


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


# Concrete per-object descriptions. The generic scaffold only knows the NAME, so
# the model invents the design (a "Wooden Door" became a cabinet, a "Fireplace" a
# grey slab). These spell out WHAT THE OBJECT IS so the silhouette reads right.
OBJECT_DESC = {
    # --- house / furniture ---
    "bookshelf": (
        "a tall wooden BOOKCASE: an upright wooden frame divided into 3-4 horizontal "
        "SHELVES, each shelf packed with a row of upright BOOKS with colorful spines "
        "(muted red, green, blue, ochre, brown), a few books tilted at an angle. The "
        "shelves-with-books fill the whole front face; clearly a bookshelf, NOT a plain "
        "cabinet or dresser."),
    "door_wood": (
        "a single closed WOODEN DOOR standing in a simple wooden door FRAME: a tall "
        "vertical slab made of vertical wood planks, with two or three recessed rectangular "
        "PANELS, a small round brass DOORKNOB near the right edge at mid-height, and a visible "
        "frame/jamb around it. It must read instantly as a DOORWAY you could walk through - "
        "NOT a cabinet, dresser, box, or wardrobe. Taller than it is wide."),
    "fireplace": (
        "a STONE FIREPLACE: a chunky grey stone hearth with a dark arched FIREBOX opening in "
        "the lower-center, warm glowing ORANGE-AND-YELLOW FLAMES burning inside the opening, "
        "and a flat stone MANTEL ledge across the top. Stone surround framing the fire on the "
        "left, right and top; the fire is the bright focal point."),
    "bed_fancy": (
        "an ornate four-poster BED seen front-on from slightly above: wooden frame with tall "
        "carved CORNER POSTS, a plump white PILLOW at the head end (top), and a richly colored "
        "deep-purple QUILT/BLANKET with trim covering the mattress. Clearly a bed."),
    "bed_basic": (
        "a simple BED seen front-on from slightly above: plain wooden frame, a white PILLOW at "
        "the head end (top), and a plain blue BLANKET over the mattress. Modest, no tall posts."),
    "table_wood": (
        "a sturdy rectangular wooden TABLE: a flat plank tabletop on four legs, wood grain "
        "running across the top, empty surface."),
    "table_stone": (
        "a STONE TABLE: a flat grey stone slab tabletop on a chunky stone pedestal/legs, empty "
        "surface."),
    "chair_wood": (
        "a simple wooden CHAIR facing the viewer: a seat, four legs, and an upright BACKREST "
        "with vertical slats. Clearly a chair."),
    "chair_fancy": (
        "a comfy upholstered ARMCHAIR facing the viewer: wooden frame with a padded PURPLE "
        "cushioned seat, a tall padded backrest and small armrests."),
    "bench": (
        "a long wooden BENCH facing the viewer: a horizontal plank seat on legs with a low "
        "back rail; wide enough to seat two."),
    "planter_box": (
        "a low rectangular wooden PLANTER BOX/trough filled with green leafy plants and a few "
        "small flowers poking up above the rim."),
    "sawhorse": (
        "a carpenter's SAWHORSE: an open A-frame wooden trestle - a horizontal top beam with "
        "splayed angled legs forming an A at each end; you can see through the open frame."),
    "chest_wood": (
        "a closed wooden treasure CHEST: a rectangular wooden box with a rounded hinged LID, "
        "dark iron METAL BANDS and a metal latch/lock on the front."),
    "lamp_floor": (
        "a standing FLOOR LAMP: a slim vertical pole on a small round base, topped with a wide "
        "trapezoid LAMPSHADE (wider at the bottom) that GLOWS warm yellow. The shade is a "
        "lampshade, NOT a tent, teepee or pyramid."),
    # --- kitchen ---
    "fridge": (
        "a wide squat retro REFRIGERATOR seen front-on: a rounded-corner cream/white enamel "
        "cabinet, a horizontal seam splitting it into a smaller top FREEZER door and a larger "
        "lower door, a slim vertical chrome HANDLE on each door. Clearly a kitchen appliance, "
        "NOT a cabinet, wardrobe or dresser. Wider than it is tall."),
    "stove": (
        "a kitchen STOVE / oven RANGE seen front-on: an enamel-and-steel cabinet with an OVEN "
        "door (a handle and a small dark window) below, and a flat COOKTOP across the top "
        "showing TWO round black BURNERS. A two-burner cooking range, clearly a stove."),
    "sink": (
        "a kitchen SINK unit seen front-on: a counter-height base cabinet with a rectangular "
        "metal BASIN set into the top and a curved chrome FAUCET/tap rising at the back. Clearly "
        "a sink, NOT a plain cabinet."),
    "counter": (
        "a kitchen COUNTER cabinet seen front-on: a wooden base CABINET with two cupboard doors "
        "and knobs below, and a flat pale stone COUNTERTOP across the top, empty surface. A "
        "section of kitchen counter."),
    "keg": (
        "a wooden brewing KEG/cask standing upright: a fat vertical wooden barrel bound with "
        "dark metal HOOPS, with a small metal TAP/spigot near the bottom front. Clearly a keg "
        "for brewing, taller and chunkier than a plain barrel."),
    # --- living / bedroom furniture ---
    "sofa": (
        "a comfy upholstered SOFA/couch facing the viewer: a long padded fabric couch with two "
        "seat cushions, a padded backrest, and rolled ARMRESTS at each end, in a warm muted "
        "fabric color. Wide enough to seat two or three. Clearly a sofa, NOT a bench or bed."),
    "armchair": (
        "a single cozy upholstered ARMCHAIR facing the viewer: a deep padded fabric seat with a "
        "tall padded backrest and two soft ARMRESTS, on short wooden feet. A lounge chair."),
    "nightstand": (
        "a small wooden BEDSIDE TABLE / nightstand seen front-on: a little cabinet with one "
        "small DRAWER (a round knob) above a tiny open shelf, short legs, flat top. Small."),
    "dresser": (
        "a wooden DRESSER / chest of drawers seen front-on: a low wide cabinet with three "
        "stacked DRAWERS, each with two round knobs, short feet. Clearly a dresser, NOT a "
        "bookshelf or cabinet of doors."),
    "rug": (
        "a rectangular woven floor RUG/carpet seen FROM ABOVE (flat, top-down): a patterned "
        "textile lying flat on the ground with a decorative woven BORDER and a central medallion "
        "motif, warm colors (deep red, ochre, blue). Flat, no thickness, no furniture."),
    "bug_terrarium": (
        "a glass BUG TERRARIUM display case on a wooden stand: a clear glass tank with a wooden "
        "base and corner frame, holding a little greenery and a mounted INSECT specimen on "
        "display inside. A prized-bug display case, clearly made of glass."),
    "vase": (
        "a decorative ceramic VASE seen front-on: a rounded glazed pot with a narrow neck "
        "holding a small arrangement of flowers/stems. A small tabletop vase."),
    "window_4pane": (
        "a closed GLASS WINDOW set in a wooden frame, seen front-on, filling a tall wall-tile "
        "shape: a wooden frame divided by a cross MULLION into FOUR equal glass PANES, the glass "
        "pale blue-white with a soft diagonal reflection. Reads instantly as a window in a wall, "
        "NOT a painting, cabinet or door. The frame fills the tile; transparent outside it."),
    # --- yard structures ---
    "well": (
        "a stone WATER WELL: a round waist-high STONE wall (the well shaft), a wooden POST on "
        "each side holding a small peaked wooden ROOF over the top, and a bucket on a rope. Dark "
        "water in the opening. Reads clearly as a wishing well, NOT a plain hole."),
    "signpost": (
        "a wooden SIGNPOST: a vertical wooden POST with a rectangular wooden SIGN BOARD mounted "
        "near the top (blank, with a faint arrow), like a directional trail sign."),
    "gate_wood": (
        "a wooden fence GATE: a single hinged gate panel matching a wooden fence - a frame of "
        "horizontal rails with a diagonal CROSS-BRACE, slightly shorter, meant to sit in a fence "
        "line as the openable section."),
    "fence_wood": (
        "a section of wooden post-and-rail FENCE: a vertical wooden POST with two horizontal "
        "RAILS running left and right off it; rustic split wood."),
    "fence_iron": (
        "a section of wrought-IRON FENCE: a slim dark metal POST with two horizontal metal "
        "RAILS running left and right off it (same post-and-rail layout as a wooden fence, but "
        "dark wrought iron, slimmer)."),
    "fence_electric": (
        "a section of ELECTRIC FENCE: a slim post with two horizontal taut WIRES running left "
        "and right, small ceramic INSULATORS where the wires meet the post and a tiny warning "
        "spark; same post-and-rail layout as a wooden fence but thin metal wire."),
    # --- decoration ---
    "statue_stone": (
        "a carved STONE STATUE on a pedestal: a small weathered grey stone figure/bust standing "
        "on a square stone BASE/plinth. Clearly a carved statue, NOT a plain rock or pillar."),
    # --- nature (organic) ---
    "tree_oak": (
        "a leafy OAK TREE: a thick brown TRUNK at the bottom widening into a big round, full "
        "CANOPY of green leaves in rounded bumpy clusters, lighter green highlights on top, "
        "darker green underneath. Lush and full."),
    "tree_apple": (
        "an APPLE TREE: a brown trunk and a round green leafy canopy dotted with small RED "
        "APPLES peeking through the leaves."),
    "tree_pine": (
        "a PINE / EVERGREEN tree: a tall layered CONICAL stack of dark-green needled branches "
        "tapering to a point at the top, with a short brown trunk at the base."),
    "bush": (
        "a small round leafy BUSH: a compact mound of green foliage in rounded clusters, lighter "
        "on top, darker at the base. No trunk."),
    "sunflower": (
        "a tall SUNFLOWER: an upright green stem with a couple of leaves, topped by a big round "
        "flower head of bright YELLOW petals around a dark brown center."),
    "flower_red": (
        "a small flowering plant: a short green stem with little leaves and one or two bright "
        "RED blossoms with a yellow center."),
    "flower_blue": (
        "a small flowering plant: a short green stem with little leaves and one or two bright "
        "BLUE blossoms with a yellow center."),
    "flower_yellow": (
        "a small flowering plant: a short green stem with little leaves and one or two bright "
        "YELLOW blossoms with a darker center."),
    "tall_grass": (
        "a tuft of TALL GRASS: a clump of upright thin green grass blades fanning out, wild, "
        "denser at the base. Just grass blades, no flowers."),
}

# Per-object palette overrides where the keyword guesser picks the wrong material
# (e.g. "fireplace"/"oak" miss stone/foliage and default to plain wood).
OBJECT_MATS = {
    # cube-tiling blocks / walls / ores
    "wall_stone": ["stone"],
    "wall_brick": ["stone"],
    "stone_block": ["stone"],
    "dirt_block": ["dirt"],
    "clay_block": ["dirt"],
    "ore_coal_block": ["stone"],
    "ore_copper_block": ["stone", "metal"],
    "ore_iron_block": ["stone", "metal"],
    "ore_silver_block": ["stone", "metal"],
    "ore_gold_block": ["stone", "metal"],
    "ore_platinum_block": ["stone", "metal"],
    "ore_diamond_block": ["stone"],
    # iron / electric fences read as metal, not wood
    "fence_iron": ["metal"],
    "fence_electric": ["metal"],
    "fireplace": ["stone", "wood"],
    "well": ["stone", "wood"],
    "statue_stone": ["stone"],
    "chest_wood": ["wood", "metal"],
    "planter_box": ["wood", "foliage"],
    "tree_oak": ["wood", "foliage"],
    "tree_apple": ["wood", "foliage"],
    "tree_pine": ["wood", "foliage"],
    "bush": ["foliage"],
    "tall_grass": ["foliage"],
    "sunflower": ["foliage"],
    "flower_red": ["foliage"],
    "flower_blue": ["foliage"],
    "flower_yellow": ["foliage"],
}


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
def is_linear_connector(key, category):
    return category == "structure" and (
        key.startswith("fence") or key.startswith("wall"))


CONNECTOR_BLOCK = (
    "HORIZONTAL TILING (CRITICAL - this piece is placed in a continuous row):\n"
    "- The horizontal members (fence rails / the wall body and its top edge) MUST "
    "extend ALL THE WAY to the LEFT edge and ALL THE WAY to the RIGHT edge of the "
    "image and bleed off both sides, so that when identical copies are placed "
    "side-by-side they join into one unbroken fence/wall with NO gap and NO seam.\n"
    "- Do NOT inset, taper, or round off the left/right ends. Do NOT leave any "
    "transparent margin on the left or right side. The rails/wall reach pixel 0 and "
    "the final pixel column.\n"
    "- At most ONE vertical post/support, centered; the rails pass through/behind it "
    "and continue to both edges. Avoid heavy posts at the left/right ends (they would "
    "double up into a thick lump where two pieces meet).\n"
    "- Transparency is allowed only ABOVE and BELOW the rails/wall, never on the sides.")


# Walls are MINECRAFT-STYLE CUBIC BLOCKS, two stacked into a wall unit. This
# gets its OWN prompt (build_wall_prompt) that does NOT use the face-on
# STYLE_BLOCK - here we WANT visible cube top faces, like the clay_block.
WALL_ART_DIRECTION = (
    "ART DIRECTION: 2D pixel-art WALL BLOCK - ONE solid building block viewed "
    "STRAIGHT FROM THE FRONT, from only SLIGHTLY above (orthographic FRONT view, NOT "
    "rotated, NOT angled, NOT isometric). It is DOMINATED by a LARGE flat lit TOP SURFACE, "
    "with only a SHORT front face beneath it. Chunky hard pixel edges, no anti-aliasing, "
    "muted palette.")

WALL_BLOCK = (
    "SOLID BLOCK that TILES IN A GRID (CRITICAL - get the PROPORTIONS exactly):\n"
    "- The block has TWO horizontal regions stacked vertically: a LARGE flat lit TOP "
    "SURFACE filling the upper ~75% of the height, and a SHORT darker FRONT FACE filling "
    "only the lower ~25%. The top surface MUST DOMINATE; the front face is just a thin lip "
    "at the very bottom.\n"
    "- WHY (the whole point): when these blocks are stacked in a vertical column, the big "
    "top surface of the lower block must rise high enough to COMPLETELY COVER the short "
    "front face of the block above it, so the column reads as ONE continuous top surface"
    "with NO repeating dark bands, NO rungs, NO ladder.\n"
    "- CAMERA IS DEAD-ON FRONT, only slightly above. The top surface is a FLAT HORIZONTAL "
    "band (a foreshortened rectangle), NEVER a tilted diamond or parallelogram, NEVER "
    "corner-on. EVERY edge is strictly HORIZONTAL or VERTICAL. NO left or right side face. "
    "NOT isometric, NOT a rotated cube, NOT a 3D render.\n"
    "- FULL-WIDTH for tight horizontal tiling: the top surface AND the front face both span "
    "the ENTIRE WIDTH and BLEED OFF the LEFT and RIGHT edges (reach pixel column 0 and the "
    "last column), NO transparent margin on the sides, so side-by-side copies merge into "
    "ONE unbroken wall with NO gap and NO seam. Do NOT round, inset, bevel or taper the "
    "left/right ends.\n"
    "- FLAT CLEAN BOTTOM: the bottom edge is one straight FULL-WIDTH horizontal line. NO "
    "legs, feet, base strip, plinth, shadow or notch below the front face.\n"
    "- The SURFACE texture (specified below) runs HORIZONTALLY. Keep shading EVEN across the block (no "
    "dark vignette at the edges) so tiles match seam-free. LOW contrast - the front lip is "
    "only SLIGHTLY darker than the top surface, NOT a heavy black band.")


# Surface texture for the cube-tiling block prompt, shared by walls, ground blocks and ores
# (all rendered as one continuous surface when stacked/tiled).
BLOCK_SURFACE = {
    "wall_wood": "horizontal WOOD PLANKS with visible grain",
    "wall_stone": "fitted grey STONE masonry blocks",
    "wall_brick": "rows of warm red-brown BRICKS with pale mortar lines",
    "stone_block": "solid grey STONE with subtle cracks",
    "dirt_block": "packed brown DIRT/soil flecked with a few small pebbles",
    "clay_block": "smooth warm red-brown CLAY",
}
ORE_FLECK = {
    "ore_coal_block": "chunks of black COAL",
    "ore_copper_block": "orange-brown COPPER veins",
    "ore_iron_block": "rusty orange IRON veins",
    "ore_silver_block": "pale silver-white SILVER flecks",
    "ore_gold_block": "bright yellow GOLD nuggets",
    "ore_platinum_block": "pale blue-white PLATINUM flecks",
    "ore_diamond_block": "glinting cyan-white DIAMOND crystals",
}


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


# Nature sprites (trees, flowers, bushes, grass) are ORGANIC - the rigid face-on
# STYLE_BLOCK ("every edge horizontal/vertical, blocky orthogonal") made them read
# as boxy blobs. They get this softer organic direction instead.
NATURAL_ART_DIRECTION = (
    "ART DIRECTION: 2D pixel-art PLANT/TREE in the style of STARDEW VALLEY nature sprites. "
    "Top-down 3/4 view - we see it from the front and slightly above as it stands on the "
    "ground. ORGANIC, rounded, slightly irregular shapes: soft bumpy leaf/petal clusters, "
    "NOT blocky cubes, NOT orthogonal, NOT isometric, NOT a 3D render. Chunky hard pixel "
    "edges, no anti-aliasing, limited muted natural palette.")

NATURAL_DESIGN = (
    "DESIGN REQUIREMENTS:\n"
    "- Organic rounded silhouette (leaves/petals/blades in soft clumps); NOT boxy or "
    "orthogonal, no straight-ruled edges except a slim trunk/stem.\n"
    "- Instantly recognizable as this exact plant even at small size; bold simple masses.\n"
    "- Soft cel shading: lighter where the top-left light hits the canopy, darker underneath; "
    "3-4 shades.\n"
    "- Render ONLY the plant - no ground patch, no pot (unless described), no cast shadow.")


def build_prompt(key, ent):
    name = ent.get("name", key)
    category = ent.get("category", "furniture")
    world = ent.get("world", {}) or {}
    pivot = world.get("pivot", "bc")
    mats = guess_materials(key, name, category)
    # Walls, ground blocks (dirt/stone/clay) and ore blocks all use the cube-tiling block prompt
    # so they read as one continuous surface when stacked/tiled.
    if category in ("block", "ore") or (category == "structure" and key.startswith("wall")):
        return build_wall_prompt(key, ent, mats)
    is_natural = category == "natural"
    desc_lines = [f"\nWHAT IT IS (draw exactly this): {OBJECT_DESC[key]}"] if key in OBJECT_DESC else []
    if is_natural:
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
    # placeables + occupants -> world sprite
    return os.path.join(RESOURCES, "Objects", f"{key}.png")


def save_tile(raw_png_bytes, key, dest):
    """Tiles are opaque and full-bleed: save as-is, NO trim, NO alpha check."""
    raw_path = os.path.join(RAW_DIR, f"{key}.png")
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(raw_path, "wb") as f:
        f.write(raw_png_bytes)
    img = Image.open(raw_path).convert("RGBA")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest)
    return img.size


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


def trim_and_save(raw_png_bytes, key, dest, vertical_only=False):
    raw_path = os.path.join(RAW_DIR, f"{key}.png")
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(raw_path, "wb") as f:
        f.write(raw_png_bytes)
    img = Image.open(raw_path).convert("RGBA")
    # Transparency validation
    alpha_min = min(p[3] for p in img.getdata())
    if alpha_min >= 255:
        raise ValueError("no transparency in generated image (alpha all opaque)")
    bbox = img.getbbox()
    if bbox:
        if vertical_only:
            # Keep full width (left/right bleed) so the piece tiles horizontally;
            # crop only the empty top/bottom bands.
            bbox = (0, bbox[1], img.width, bbox[3])
        img = img.crop(bbox)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    img.save(dest)
    return img.size


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


def walk_sheet_prompt(tone, direction, frames=4):
    return "\n".join([
        f"A horizontal pixel-art SPRITE SHEET: {frames} poses of the SAME chibi character "
        f"WALKING, {DIR_POSE[direction]}, arranged left-to-right with CLEAR EMPTY GAPS between "
        "each pose.",
        "",
        f"ART DIRECTION: {PLAYER_STYLE}",
        f"Skin: {SKIN_TONES[tone]}.",
        "BALD - smooth head, NO hair. Wearing a plain mid-gray short-sleeve shirt and shorts "
        "(neutral underlayer); bare forearms and lower legs show skin.",
        "Keep the skin a SINGLE consistent hue (this body gets recolored).",
        "",
        "EXAGGERATE the walk poses so the cycle is obvious: pose1 LEFT leg striding far forward "
        "(knee lifted), pose2 legs together passing, pose3 RIGHT leg striding far forward (knee "
        "lifted), pose4 legs together passing. Arms swing clearly opposite to the legs.",
        "",
        "STRICT CONSISTENCY:",
        "- IDENTICAL character in every pose: same size, colors, proportions.",
        "- Feet on a common baseline; only the limbs change between poses.",
        f"- Exactly {frames} poses, well separated by transparent gaps so they can be auto-split.",
        "- Transparent background. NO grid lines, NO numbers, NO ground, NO shadow.",
    ])


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


def build_walk_set(api_key, model, direction="down", n_frames=4, max_tries=3,
                   quality="low"):
    """Production slice: generate a walk sheet -> segment by gaps -> force to
    exactly n_frames -> normalize onto a common canvas -> recolor to all tones.
    Master frames + per-tone frames + review strips land in raw_sprites/walk/."""
    wdir = os.path.join(RAW_DIR, "walk")
    os.makedirs(wdir, exist_ok=True)
    best = []
    for attempt in range(1, max_tries + 1):
        print(f"[gen] walk sheet dir={direction} attempt {attempt}/{max_tries}")
        try:
            png = call_api(walk_sheet_prompt("medium", direction, n_frames),
                           quality, api_key, model)
        except urllib.error.HTTPError as e:
            print(f"      HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
            continue
        sheet_path = os.path.join(wdir, f"_sheet_{direction}_{attempt}.png")
        with open(sheet_path, "wb") as f:
            f.write(png)
        figs = segment_sheet(sheet_path)
        print(f"      segmented {len(figs)} figure(s)")
        if len(figs) > len(best):
            best = figs
        if len(figs) >= n_frames:
            break
    if not best:
        print("FAILED: no figures segmented from any attempt")
        return
    frames = normalize_frames(force_n_frames(best, n_frames))
    # Master (medium-gen) frames
    for i, fr in enumerate(frames):
        fr.save(os.path.join(wdir, f"master_{direction}_{i}.png"))
    make_strip(frames, os.path.join(wdir, f"_strip_master_{direction}.png"))
    # Recolor to all tones
    for tone in SKIN_RAMP:
        toned = [recolor_skin(fr, tone) for fr in frames]
        for i, fr in enumerate(toned):
            fr.save(os.path.join(wdir, f"{tone}_{direction}_{i}.png"))
        make_strip(toned, os.path.join(wdir, f"_strip_{tone}_{direction}.png"))
    print(f"\nWalk set done: {len(frames)} frames x {len(SKIN_RAMP)} tones in {wdir}")
    print(f"Review strips: _strip_master_{direction}.png, _strip_<tone>_{direction}.png")


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
    ap.add_argument("--quality", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--model", default="gpt-image-1", help="image model (e.g. gpt-image-1, gpt-image-2)")
    ap.add_argument("--dry-run", action="store_true", help="print prompts, no API call")
    ap.add_argument("--force", action="store_true", help="overwrite existing sprites")
    ap.add_argument("--limit", type=int, help="cap number of assets")
    ap.add_argument("--player-bodies", action="store_true",
                    help="generate the 4 skin-tone base bodies (review batch)")
    ap.add_argument("--master-body", action="store_true",
                    help="generate ONE bald skin-only master, recolor to all 4 tones")
    ap.add_argument("--walk-set", action="store_true",
                    help="production: walk sheet -> 4 normalized frames -> recolor all tones")
    ap.add_argument("--char-sample", action="store_true",
                    help="generate ONE polished flat front-facing character (quality test)")
    ap.add_argument("--segment-sheet", metavar="PATH",
                    help="split an existing sheet into figures by transparent gaps")
    ap.add_argument("--dirs", help="comma dirs for --player-bodies (default: down)")
    ap.add_argument("--variants", type=int, default=1,
                    help="terrain only: number of seamless variants per tile (v1=base, then _v2, _v3...)")
    args = ap.parse_args()

    if args.char_sample:
        direction = (args.dirs or "down").split(",")[0].strip()
        prompt = char_sample_prompt(
            direction,
            skin_desc="warm medium skin",
            hair="short tousled brown hair",
            shirt="teal short-sleeve shirt",
            pants="brown overalls")
        if args.dry_run:
            print(prompt)
            return
        api_key = resolve_api_key()
        os.makedirs(RAW_DIR, exist_ok=True)
        out = os.path.join(RAW_DIR, f"char_sample_{direction}_{args.quality}.png")
        print(f"generating polished char sample dir={direction} quality={args.quality}")
        png = call_api(prompt, args.quality, api_key, args.model)
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        bb = img.getbbox()
        if bb:
            img = img.crop(bb)
        img.save(out)
        print(f"saved {out}  size={img.size}")
        return

    if args.walk_set:
        api_key = resolve_api_key() if not args.dry_run else None
        direction = (args.dirs or "down").split(",")[0].strip()
        if args.dry_run:
            print(walk_sheet_prompt("medium", direction))
            return
        build_walk_set(api_key, args.model, direction, quality=args.quality)
        return

    if args.master_body:
        api_key = resolve_api_key() if not args.dry_run else None
        direction = (args.dirs or "down").split(",")[0].strip()
        if args.dry_run:
            print(body_prompt("medium", direction))
            return
        os.makedirs(RAW_DIR, exist_ok=True)
        master = os.path.join(RAW_DIR, f"master_body_{direction}.png")
        print(f"[1/2] generate bald skin-only master body dir={direction}")
        png = call_api(body_prompt("medium", direction), args.quality, api_key, args.model)
        m = Image.open(io.BytesIO(png)).convert("RGBA")
        mb = m.getbbox()
        if mb:
            m = m.crop(mb)
        m.save(master)
        print(f"[2/2] recolor master -> {len(SKIN_RAMP)} tones (no API)")
        for tone in SKIN_RAMP:
            out = os.path.join(RAW_DIR, f"tone_{tone}_{direction}.png")
            recolor_skin(m, tone).save(out)
            print(f"  {tone} -> {os.path.basename(out)}")
        print(f"\nMaster + 4 recolored tones in {RAW_DIR}. Review: same silhouette, "
              f"only skin hue differs?")
        return

    if args.segment_sheet:
        frames = segment_sheet(args.segment_sheet)
        base = os.path.splitext(args.segment_sheet)[0]
        print(f"segmented {len(frames)} figure(s) from {args.segment_sheet}")
        for i, fr in enumerate(frames):
            out = f"{base}_seg{i}.png"
            fr.save(out)
            print(f"  seg{i}: size={fr.size} -> {os.path.basename(out)}")
        return

    if args.player_bodies:
        api_key = resolve_api_key() if not args.dry_run else None
        dirs = [d.strip() for d in args.dirs.split(",")] if args.dirs else ["down"]
        os.makedirs(RAW_DIR, exist_ok=True)
        for tone in SKIN_TONES:
            for d in dirs:
                if args.dry_run:
                    print(f"=== body {tone}_{d} ===\n{body_prompt(tone, d)}\n")
                    continue
                out = os.path.join(RAW_DIR, f"body_{tone}_{d}.png")
                print(f"body {tone}_{d}")
                png = call_api(body_prompt(tone, d), args.quality, api_key, args.model)
                img = Image.open(io.BytesIO(png)).convert("RGBA")
                img.save(out)
        if not args.dry_run:
            print(f"\nBodies in {RAW_DIR}/body_*.png - review before promoting to Resources/Player/body/")
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
        prompt = build_prompt(key, ent)

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
            png = call_api(prompt, args.quality, api_key, args.model,
                           size=canvas_size_for(ent))
            size = trim_and_save(png, key, dest,
                                 vertical_only=is_linear_connector(
                                     key, ent.get("category", "")))
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
