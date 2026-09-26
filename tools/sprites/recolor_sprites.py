#!/usr/bin/env python3
"""Derive tool TIER icons by palette-recoloring a family's wood base sprite.

Tool tiers differ only by HEAD MATERIAL (the in-repo legacy tier sets prove it: identical
alpha masks per family, shared handle colors, only a 2-color head ramp swapped). So we
generate ONE base per family (`{family}_wood`, via gen_sprites + pixelclean) and produce
the other tiers here — no API spend, guaranteed same-silhouette families.

How: every opaque pixel is matched (nearest-RGB within --tolerance) against the WOOD head
ramp; matched pixels map to the same INDEX in the target tier's ramp. Handle/grip pixels
(the shared handle colors, and anything unmatched) pass through untouched. The base must be
pixelcleaned first (small quantized palette) or ramp matching will fail — by design.

Ramps are inline data measured from the legacy tier icons in Resources/Items/ (axe_steel,
pickaxe_gold, ...). Scope guard: keep this a flat script — no config files, no plugins; if
a family's ramps stop fitting, fall back to per-tier generation (gen_sprites).

Usage:
  python3 tools/sprites/recolor_sprites.py --family pickaxe --tiers stone,copper,iron   # the trial
  python3 tools/sprites/recolor_sprites.py --family axe,shovel,hoe                      # data-driven tiers
  python3 tools/sprites/recolor_sprites.py --family pickaxe --tiers gold --dry-run      # report only
Without --tiers, tiers come from items.json: every `{family}_{tier}` entry that exists
(beyond wood) gets a recolor.
"""
import argparse
import json
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEMS = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Items")
ITEMS_JSON = os.path.join(ROOT, "nakama", "data", "entities", "items.json")

# Material ramps, dark -> light, measured from the legacy same-shape tier sets.
# WOOD is the SOURCE ramp (3 colors: shadow, base, highlight — the generated bases are
# quantized, so matching is nearest-RGB within tolerance). Metal targets are 2-color
# (base, highlight); the wood SHADOW maps to the target BASE (index clamping).
RAMPS = {
    "wood":     [(70, 50, 35), (120, 90, 60), (160, 130, 95)],
    "stone":    [(90, 90, 95), (120, 120, 125), (155, 155, 160)],
    "copper":   [(140, 80, 50), (180, 110, 70), (210, 150, 100)],
    "iron":     [(75, 80, 85), (100, 105, 110), (150, 155, 160)],
    "steel":    [(90, 95, 105), (120, 125, 135), (170, 175, 185)],
    "silver":   [(140, 140, 150), (180, 180, 190), (220, 220, 230)],
    "gold":     [(190, 150, 40), (230, 190, 60), (255, 220, 100)],
    "platinum": [(160, 165, 175), (200, 205, 215), (235, 240, 250)],
    "diamond":  [(80, 180, 200), (120, 220, 240), (180, 245, 255)],
}

# The handle stays wood on every tier. In an all-wood base, head and handle share the
# palette, so color alone can't separate them — but the DIAGONAL contract makes the head
# a geometric region (top-right): see head_zone()/--head-frac.


def tiers_from_items_json(family):
    data = json.load(open(ITEMS_JSON))
    out = []
    for k in data:
        if k.startswith(family + "_"):
            tier = k[len(family) + 1:]
            if tier != "wood" and tier in RAMPS:
                out.append(tier)
    return out


def head_zone(shape, frac):
    """The diagonal icon contract (grip bottom-left, head top-right) makes the head
    REGION geometric: pixels whose normalized (x - y_down) exceeds frac. This is what
    lets an all-wood base keep a wooden HANDLE while only the head changes material."""
    h, w = shape
    ys, xs = np.mgrid[0:h, 0:w]
    return (xs / max(1, w - 1)) - (ys / max(1, h - 1)) > frac


def recolor(base_arr, src_ramp, dst_ramp, tolerance, head_frac):
    out = base_arr.copy()
    rgb = base_arr[..., :3].astype(np.int32)
    alpha = base_arr[..., 3]
    zone = head_zone(alpha.shape, head_frac)
    # Assign every head-zone pixel to its NEAREST ramp index (within tolerance), then
    # map indices 1:1 into the target ramp. Single pass — no overwrite ambiguity.
    ramp = np.array(src_ramp)  # (k,3)
    dists = np.abs(rgb[..., None, :] - ramp[None, None, :, :]).sum(axis=3)  # (h,w,k)
    nearest = dists.argmin(axis=2)
    within = dists.min(axis=2) <= tolerance
    mask = within & (alpha > 0) & zone
    for i in range(len(src_ramp)):
        j = min(i, len(dst_ramp) - 1)
        out[..., :3][mask & (nearest == i)] = dst_ramp[j]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True,
                    help="comma families (pickaxe,axe,shovel,hoe). Base = Items/{family}_wood_icon.png")
    ap.add_argument("--tiers", default="",
                    help="comma tiers; default = every {family}_{tier} in items.json")
    ap.add_argument("--tolerance", type=int, default=60,
                    help="max |dR|+|dG|+|dB| to count a pixel as a ramp color")
    ap.add_argument("--head-frac", type=float, default=0.0,
                    help="head zone threshold along the diagonal: normalized x−y must exceed "
                         "this. 0.0 = the upper-right half; raise toward 0.3 if handle pixels "
                         "near the head pick up the tier color")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src_ramp = RAMPS["wood"]
    for family in [f.strip() for f in args.family.split(",") if f.strip()]:
        base_path = os.path.join(ITEMS, f"{family}_wood_icon.png")
        if not os.path.exists(base_path):
            print(f"!! {family}: no base at {os.path.relpath(base_path, ROOT)} — generate+clean it first")
            continue
        base = np.asarray(Image.open(base_path).convert("RGBA"), dtype=np.uint8)

        tiers = ([t.strip() for t in args.tiers.split(",") if t.strip()]
                 or tiers_from_items_json(family))
        if not tiers:
            print(f"-- {family}: no non-wood tiers found in items.json")
            continue

        for tier in tiers:
            if tier not in RAMPS:
                print(f"!! {family}_{tier}: no ramp for '{tier}' — add it to RAMPS or generate instead")
                continue
            dst = os.path.join(ITEMS, f"{family}_{tier}_icon.png")
            if args.dry_run:
                print(f"would write {os.path.relpath(dst, ROOT)} (wood -> {tier})")
                continue
            out = recolor(base, src_ramp, RAMPS[tier], args.tolerance, args.head_frac)
            changed = int((out != base).any(axis=2).sum())
            Image.fromarray(out).save(dst)
            print(f"{family}_{tier}: {changed}px remapped -> {os.path.relpath(dst, ROOT)}")


if __name__ == "__main__":
    main()
