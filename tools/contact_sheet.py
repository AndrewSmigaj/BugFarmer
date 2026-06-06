#!/usr/bin/env python3
"""Labeled contact sheet — a grid of individual sprites with their ids, grouped by kind, so you can
eyeball a zone's whole art set and flag which sprites are stale / need a redo. Sprites are loaded from
Resources/{Objects,Tiles} and NEAREST-scaled up. Output goes to a per-zone previews folder.

Usage: python3 tools/contact_sheet.py --zone underground
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources")
PREV = os.path.join(ROOT, "tools", "_generated", "previews")

# Per-zone sprite sets, grouped. Add zones as we build them.
SHEETS = {
    "underground": [
        ("Blocks & walls", ["dirt_block", "stone_block", "clay_block", "hard_stone_block",
                            "wall_stone", "wall_wood", "wall_brick"]),
        ("Ore / resource blocks", ["ore_coal_block", "ore_copper_block", "ore_iron_block",
                                   "ore_tin_block", "ore_silver_block", "ore_gold_block",
                                   "ore_platinum_block", "ore_diamond_block"]),
        ("Tiles", ["cave_floor", "stone_floor", "stone_path", "water_shallow", "water_deep",
                   "bridge_stone"]),
        ("Cave features", ["crystal_small", "crystal_large", "crystal_quartz", "geode", "rubble",
                           "bone_pile", "cave_moss"]),
        ("Cave mushrooms", ["mushroom_glow", "mushroom_blue", "mushroom_cluster", "mushroom_morel",
                            "mushroom_bracket", "mushroom_inkcap", "mushroom_red", "mushroom_brown"]),
        ("Mining gear", ["tnt", "powder_keg", "mine_cart", "mine_rail", "mine_support", "ore_sack",
                         "tool_rack", "wheelbarrow", "mining_bucket", "ore_pile", "chest_mossy"]),
        ("Lighting", ["torch", "torch_wall", "lantern", "lamp_post"]),
    ],
    "bugs": [
        ("Flies", ["fly_house", "fly_horse", "fly_bot", "fruitfly_common", "fruitfly_vinegar", "fruitfly_spotwing"]),
        ("Mosquitoes", ["mosquito_common", "mosquito_tiger", "mosquito_malaria"]),
        ("Bees & wasps", ["honeybee", "bumblebee", "bee_carpenter", "wasp_paper", "wasp_yellowjacket", "hornet"]),
        ("Beetles & ladybugs", ["beetle_common", "beetle_rhino", "beetle_stag", "ladybug", "ladybug_orange", "ladybug_giant"]),
        ("Moths & butterflies", ["moth_brown", "moth_luna", "moth_atlas", "butterfly_common", "butterfly_swallowtail", "butterfly_emperor"]),
        ("Spiders", ["jumping_spider", "spider_wolf", "spider_huntsman", "spider_orb", "black_widow", "spider_funnel"]),
        ("Scorpions", ["scorpion_bark", "scorpion_desert", "scorpion_emperor"]),
        ("Hoppers & cicadas", ["grasshopper", "locust", "locust_swarm", "cricket", "cicada_annual", "cicada_periodical"]),
        ("Roaches & fireflies & dragonflies", ["roach_common", "roach_hisser", "roach_giant", "firefly", "firefly_blue", "firefly_great", "dragonfly", "dragonfly_emperor", "dragonfly_hawker"]),
        ("Centipede/millipede segments", ["centipede_head_a", "centipede_head_b", "centipede_body_a", "centipede_body_b", "centipede_tail_a", "centipede_tail_b", "millipede_head_a", "millipede_body_a", "millipede_tail_a"]),
        ("Water bugs", ["strider_common", "strider_giant", "dytiscid_small", "dytiscid_great", "dytiscid_giant", "backswimmer_common", "mayfly_common", "mayfly_giant", "leech_common", "leech_giant", "snail_pond", "snail_apple"]),
    ],
    "plants": [
        ("Wildflowers", ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "poppy", "chamomile", "lavender", "clover", "dandelion", "flower_aster", "flower_foxglove", "flower_bluebell", "sunflower"]),
        ("Mushrooms", ["mushroom_brown", "mushroom_red", "mushroom_glow", "mushroom_blue", "mushroom_chanterelle", "mushroom_puffball", "mushroom_cluster", "mushroom_morel", "mushroom_bracket", "mushroom_inkcap"]),
        ("Herbs", ["mint", "sage", "thyme", "fennel", "yarrow"]),
        ("Grass / reed", ["tall_grass", "reeds", "cattail", "pampas"]),
        ("Fern / moss / bush", ["fern", "cave_moss", "clubmoss", "moss_clump", "bush", "bush_flowering", "bramble", "wild_berry_bush"]),
        ("Aquatic", ["lily_pad", "water_lily", "duckweed", "pondweed"]),
        ("Vines & succulents", ["ivy", "morning_glory", "grapevine", "aloe", "agave", "cactus_saguaro", "cactus_barrel", "cactus_prickly"]),
    ],
}

CELL, SPRITE, LABEL, COLS = 64, 52, 12, 8
BG = (40, 40, 46, 255)


def load_sprite(key):
    for sub in ("Objects", "Tiles", "Bugs"):
        p = os.path.join(RES, sub, f"{key}.png")
        if os.path.exists(p):
            return Image.open(p).convert("RGBA"), (sub == "Tiles")
    return None, False


def fit(img, box):
    w, h = img.size
    s = min(box / w, box / h)
    return img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.NEAREST)


def build(zone):
    groups = SHEETS[zone]
    font = ImageFont.load_default()
    rows = sum(1 + (len(ids) + COLS - 1) // COLS for _, ids in groups)  # header + sprite rows
    W = COLS * CELL + 16
    H = rows * (CELL + LABEL) + 40
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((8, 8), f"{zone} — sprite contact sheet", fill=(235, 235, 235), font=font)
    y = 28
    for label, ids in groups:
        d.text((8, y), f"== {label} ==", fill=(170, 200, 255), font=font)
        y += 16
        for i, key in enumerate(ids):
            col = i % COLS
            if i and col == 0:
                y += CELL + LABEL
            cx = 8 + col * CELL
            sp, _ = load_sprite(key)
            if sp is None:
                d.rectangle([cx + 6, y + 6, cx + SPRITE, y + SPRITE], outline=(200, 80, 80))
                d.text((cx + 8, y + 22), "MISSING", fill=(200, 80, 80), font=font)
            else:
                sp = fit(sp, SPRITE)
                img.alpha_composite(sp, (cx + (CELL - sp.width) // 2, y + (SPRITE - sp.height) // 2 + 4))
            d.text((cx + 2, y + SPRITE + 2), key[:11], fill=(210, 210, 210), font=font)
        y += CELL + LABEL + 8
    out_dir = os.path.join(PREV, zone)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "contact_sheet.png")
    img.save(out)
    return out


def build_ab(keys, name):
    """A vs B comparison: A = live sprite in Resources, B = tools/_generated/ab/{key}_B.png."""
    font = ImageFont.load_default()
    ab_dir = os.path.join(ROOT, "tools", "_generated", "ab")
    rowh = SPRITE + LABEL + 6
    W = 2 * CELL + 90
    H = 28 + len(keys) * rowh + 16
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((8, 8), f"A/B pick — {name}", fill=(235, 235, 235), font=font)
    d.text((90 + (CELL - 16) // 2, 22), "A (live)", fill=(170, 200, 255), font=font)
    d.text((90 + CELL + (CELL - 16) // 2, 22), "B (alt)", fill=(170, 200, 255), font=font)
    y = 36
    for key in keys:
        d.text((6, y + SPRITE // 2), key[:13], fill=(210, 210, 210), font=font)
        a, _ = load_sprite(key)
        bp = os.path.join(ab_dir, f"{key}_B.png")
        b = Image.open(bp).convert("RGBA") if os.path.exists(bp) else None
        for i, sp in enumerate((a, b)):
            cx = 90 + i * CELL
            if sp is None:
                d.text((cx + 6, y + 16), "—", fill=(150, 150, 150), font=font)
            else:
                sp = fit(sp, SPRITE)
                img.alpha_composite(sp, (cx + (CELL - sp.width) // 2, y + (SPRITE - sp.height) // 2))
        y += rowh
    out_dir = os.path.join(PREV, "ab_review")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.png")
    img.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone", choices=list(SHEETS))
    ap.add_argument("--ab", help="comma-separated keys for an A/B comparison sheet")
    ap.add_argument("--name", default="ab", help="output name for --ab sheet")
    args = ap.parse_args()
    if args.ab:
        print("wrote", build_ab([k.strip() for k in args.ab.split(",")], args.name))
    else:
        print("wrote", build(args.zone or "underground"))
