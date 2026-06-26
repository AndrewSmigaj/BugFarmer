#!/usr/bin/env python3
"""Block prompt BAKE-OFF.

Three prompt APPROACHES (P1/P2/P3), each a different way of asking for the SAME 3D block
(wide lit TOP + short darker FRONT face, tops lined up in a grid, fronts showing). They share
the STYLE block (for consistency) and differ only in technique. For each approach we render N
random VARIANTS of each test block into tools/_generated/blocklab/P{n}/{block}_{i}.png.

The deliverable never changes (a 3D block). Only the prompt wording is iterated. See
docs/guides/art/block_prompts.md. Generation reuses gen_sprites (build_wall_prompt + transparent + crop)
and pixelclean — NOT opaque, NOT flat.

Usage:
  python3 tools/sprites/blocklab.py                         # P1,P2,P3 x 3 variants x the 4 test blocks
  python3 tools/sprites/blocklab.py --approaches P2 --blocks stone_block --variants 3
"""
import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites as g          # noqa: E402
import pixelclean as pc          # noqa: E402
from PIL import Image            # noqa: E402

LAB = os.path.join(g.REPO, "tools", "_generated", "blocklab")
TEST_BLOCKS = ["stone_block", "dirt_block", "wall_wood", "wall_stone"]

# Shared across ALL approaches (consistency). Goes into WALL_ART_DIRECTION.
SHARED_STYLE = (
    "ART DIRECTION: 2D pixel-art BLOCK for a 2.5D top-down game, viewed STRAIGHT FROM THE FRONT and only "
    "SLIGHTLY from above (orthographic; NOT isometric, NOT a rotated cube, NOT a 3D render). It reads as a "
    "solid cube: a WIDE flat lit TOP surface with a SHORT, only-slightly-darker FRONT face beneath it. "
    "Material colors natural and muted; for STONE use NEUTRAL GREY (no green or blue tint). Crisp hard pixel "
    "edges, no anti-aliasing. The top and the front BOTH span the FULL WIDTH and bleed off the left and right "
    "edges (no side margin) so blocks abut with no gap."
)

# The three techniques (go into WALL_BLOCK). Same goal, different wording.
# Keys are the (descriptive, no-abbreviation) folder names under blocklab/.
APPROACHES = {
    # plain description (what we already had)
    "01_described": (
        "BLOCK SHAPE (described): the block is dominated by its big flat TOP; the FRONT face is a short band "
        "at the bottom, only slightly darker than the top. Stacked in a column the tops line up and the short "
        "fronts show as the wall face, reading as one tidy grid of blocks - no thick black seam lines, no dark "
        "outline around each block, and no bevel that narrows the top."
    ),
    # explicit pixel dimensions
    "02_explicit_dimensions": (
        "BLOCK SHAPE (exact proportions): in the sprite the TOP surface occupies the upper ~80% of the height "
        "and the FRONT face the lower ~20%. The top is a WIDE flat band reaching the full width; any bevel at "
        "its lit edge is at most 1px. The front face is only ~15% darker than the top - NOT a black band - and "
        "there is NO dark outline between blocks. Goal: stacked in a vertical grid, the wide tops align "
        "edge-to-edge into a continuous surface broken only by thin front-face lines."
    ),
    # grid self-check
    "03_grid_check": (
        "BLOCK SHAPE (verify by tiling): picture 9 copies laid out in a 3x3 grid, each in one cell, every "
        "block's TOP meeting the next block directly above and its FRONT face just below. Design the block so "
        "that grid reads as a SEAMLESS wall: the tops connect with no offset and no gap, the fronts show as "
        "thin even bands, and there is NO thick black seam line and NO dark border around any block. Check "
        "yourself: would the tops line up perfectly? If a thick dark line or a narrow/bevelled top would break "
        "the grid, widen the top and lighten the seam."
    ),
}


def gen_variant(key, ent, dest, api, save_raw=None):
    cat = ent.get("category", "")
    keep_width = g.is_linear_connector(key, cat) or cat in ("block", "ore")
    tw, th = ent.get("sprite_w", 16), ent.get("sprite_h", 16)
    png = g.call_api(g.build_prompt(key, ent), "low", api, "gpt-image-1", size=g.canvas_size_for(ent))
    if save_raw:
        Image.open(io.BytesIO(png)).convert("RGBA").save(save_raw)   # for the blur check
    g.trim_and_save(png, key, dest, vertical_only=keep_width)
    Image.fromarray(pc.clean(pc.load_rgba(dest), tw, th, False, None, 16)).save(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--approaches", default="01_described,02_explicit_dimensions,03_grid_check")
    ap.add_argument("--blocks", default=",".join(TEST_BLOCKS))
    ap.add_argument("--variants", type=int, default=3)
    args = ap.parse_args()

    api = g.resolve_api_key()
    ents = g.load_entities("placeables")
    blocks = [b.strip() for b in args.blocks.split(",")]
    ok = fail = 0
    for apk in [a.strip() for a in args.approaches.split(",")]:
        g.WALL_ART_DIRECTION = SHARED_STYLE
        g.WALL_BLOCK = APPROACHES[apk]
        outdir = os.path.join(LAB, apk)
        os.makedirs(outdir, exist_ok=True)
        for key in blocks:
            ent = ents[key]
            for i in range(1, args.variants + 1):
                dest = os.path.join(outdir, f"{key}_{i}.png")
                raw = os.path.join(LAB, f"_raw_{apk}_{key}.png") if (i == 1 and key == "stone_block") else None
                try:
                    gen_variant(key, ent, dest, api, save_raw=raw)
                    print("OK", apk, key, i)
                    ok += 1
                except Exception as e:
                    print("FAIL", apk, key, i, str(e)[:120])
                    fail += 1
    print(f"BAKEOFF DONE: {ok} ok, {fail} failed -> {os.path.relpath(LAB, g.REPO)}")


if __name__ == "__main__":
    main()
