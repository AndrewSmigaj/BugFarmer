#!/usr/bin/env python3
"""gen_dug_tiles.py - EXPERIMENT (dug-tile spike): generate dug-out ground tile CANDIDATES.

The dug tile is a NORMAL flat 32px floor tile whose pixels are shaded to LOOK indented (a shallow
dug-out depression) - NOT a literal 3D hole. The standard seamless-tile scaffold (gen_sprites
build_tile_prompt) forbids the inner shadow this needs, so this experiment uses CUSTOM prompts but
REUSES the pipeline core: call_api (generate) + save_tile (cache raw + clean/downscale to 32px).
Outputs candidates for the owner to pick from; the winner gets wired in properly (or hand-drawn) after.

    python3 tools/sprites/gen_dug_tiles.py --keys dug_medium   # test ONE first (validates model + look)
    python3 tools/sprites/gen_dug_tiles.py                     # all six

Raw 1024px renders cache to tools/_generated/raw/dug_exp_<key>.png; cleaned 32px tiles land in
tools/_generated/previews/dug_experiment/<key>.png. In-context comparison is rendered separately.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_sprites import call_api, save_tile  # reuse the pipeline core

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(TOOLS_DIR, "_generated", "previews", "dug_experiment")


def api_key():
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k
    envp = os.path.join(TOOLS_DIR, ".env")
    if os.path.exists(envp):
        for line in open(envp):
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("ERROR: OPENAI_API_KEY not found (env or tools/.env)")


# Shared base: a FLAT square tile that only LOOKS recessed via shading (not a real hole).
BASE = (
    "A single 2D pixel-art GROUND TILE for a top-down farming game, viewed straight from directly above "
    "(flat orthographic, NOT isometric, NO perspective). It is a FLAT SQUARE tile that FILLS THE ENTIRE "
    "FRAME edge to edge, fully opaque. Chunky hard pixel edges, NO anti-aliasing, muted natural palette, "
    "light from the TOP-LEFT. The tile must READ AS A SHALLOW DUG-OUT DEPRESSION using SHADING ONLY: the "
    "tile stays a flat square, but a soft shadow along the INNER TOP and LEFT edges plus a lighter INNER "
    "BOTTOM and RIGHT edge make it look pressed-in / scooped-out, like freshly dug ground sitting a little "
    "below the surface. It is NOT a literal 3D hole, NOT a bowl seen from the side - just a flat tile "
    "shaded to look recessed. No text, no border line, no drop shadow outside the tile. "
)

# 3 DEPTHS (shared material = bare dark-brown earth) + 3 MATERIALS (shared shallow-scoop depth).
PROMPTS = {
    "dug_shallow": BASE + "DEPTH: very shallow - only a faint pressed-in look, a thin soft inner shadow on the top/left, the middle barely lower. MATERIAL: bare dark-brown scraped earth.",
    "dug_medium":  BASE + "DEPTH: a clear shallow scoop - a distinct soft inner-shadow rim, a gently darker sunken middle, loose soil crumbs. MATERIAL: bare dark-brown earth.",
    "dug_deep":    BASE + "DEPTH: a deeper scoop - a stronger inner shadow, the middle noticeably darker and lower with soft rounded inner walls. MATERIAL: bare dark-brown earth.",
    "dug_subsoil": BASE + "DEPTH: a clear shallow scoop. MATERIAL: moist DARK SUBSOIL at the bottom - rich cool brown, damp, small crumbly clods and a pebble or two.",
    "dug_bedrock": BASE + "DEPTH: a clear shallow scoop. MATERIAL: the dig has hit grey ROCK - a cracked cool-grey STONE bottom with fine fissures, ringed by a shadowed brown-soil rim.",
    "dug_clay":    BASE + "DEPTH: a clear shallow scoop. MATERIAL: pale dry CLAY / hardpan bottom - light tan-grey with a fine crackle pattern, clearly paler than brown soil.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", help="comma-separated subset (default all six)")
    ap.add_argument("--model", default="gpt-image-1.5")
    ap.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true", help="print prompts, no API call")
    args = ap.parse_args()

    keys = args.keys.split(",") if args.keys else list(PROMPTS)
    if args.dry_run:
        for k in keys:
            print(f"--- {k} ---\n{PROMPTS[k]}\n")
        return

    key = api_key()
    for k in keys:
        print(f"[gen_dug] {k}  ({args.model} / {args.quality}) ...", flush=True)
        raw = call_api(PROMPTS[k], args.quality, key, model=args.model,
                       size="1024x1024", background="opaque")
        dest = os.path.join(OUT_DIR, f"{k}.png")
        save_tile(raw, f"dug_exp_{k}", dest)
        print(f"  -> {dest}  (raw: _generated/raw/dug_exp_{k}.png)")


if __name__ == "__main__":
    main()
