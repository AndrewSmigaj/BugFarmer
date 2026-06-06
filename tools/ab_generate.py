#!/usr/bin/env python3
"""A/B sprite generation — generate each key TWICE (the model is stochastic, so two calls give two
candidates). A goes LIVE (Resources/…, cleaned) so scenes render; B goes to tools/_generated/ab/{key}_B.png
(also cleaned) for later picking. Reuses gen_sprites (prompt/API/trim) + pixelclean (clean). Build an
A/B comparison contact sheet afterward with: python3 tools/contact_sheet.py --ab <keys...>.

Usage: python3 tools/ab_generate.py --source placeables --keys stone_block,wall_wood
"""
import argparse
import io
import os

from PIL import Image

import gen_sprites as g
import pixelclean as pc

AB_DIR = os.path.join(g.REPO, "tools", "_generated", "ab")


def _clean_inplace(path, key, is_tile):
    meta = pc.load_meta()
    tw, th = pc.target_size(key, meta, is_tile)
    arr = pc.load_rgba(path)
    cleaned = pc.clean(arr, tw, th, is_tile, None, 20)
    Image.fromarray(cleaned).save(path)


def gen_one(key, ent, source, quality, api_key, model, dest):
    cat = ent.get("category", "")
    is_tile = (source == "terrain")
    if is_tile:                                          # seamless opaque ground tile (its OWN prompt)
        png = g.call_api(g.build_tile_prompt(key, 0), quality, api_key, model, size="1024x1024", background="opaque")
        g.save_tile(png, key, dest)
        _clean_inplace(dest, key, True)
    else:                          # objects AND blocks/walls: build_prompt (blocks -> build_wall_prompt cube) + crop
        png = g.call_api(g.build_prompt(key, ent), quality, api_key, model, size=g.canvas_size_for(ent))
        keep_width = g.is_linear_connector(key, cat) or cat in ("block", "ore")
        g.trim_and_save(png, key, dest, vertical_only=keep_width)
        _clean_inplace(dest, key, False)


def main():
    ap = argparse.ArgumentParser(description="A/B sprite generation")
    ap.add_argument("--source", choices=list(g.SOURCES), default="placeables")
    ap.add_argument("--keys", required=True, help="comma-separated entity keys")
    ap.add_argument("--quality", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--model", default="gpt-image-1")
    ap.add_argument("--only", choices=["A", "B", "AB"], default="AB", help="which candidates to (re)gen")
    args = ap.parse_args()

    ents = g.load_entities(args.source)
    keys = [k.strip() for k in args.keys.split(",") if k.strip() in ents]
    missing = [k.strip() for k in args.keys.split(",") if k.strip() not in ents]
    if missing:
        print("WARN unknown keys:", missing)
    os.makedirs(AB_DIR, exist_ok=True)
    api_key = g.resolve_api_key()

    ok = fail = 0
    for key in keys:
        ent = ents[key]
        live = g.dest_path(args.source, key, ent)
        b_dest = os.path.join(AB_DIR, f"{key}_B.png")
        for tag, dest in (("A", live), ("B", b_dest)):
            if tag not in args.only:
                continue
            try:
                gen_one(key, ent, args.source, args.quality, api_key, args.model, dest)
                if tag == "A":
                    g.patch_meta(live)
                print(f"OK {key} [{tag}] -> {os.path.relpath(dest, g.REPO)}")
                ok += 1
            except Exception as e:
                print(f"FAIL {key} [{tag}]: {str(e)[:200]}")
                fail += 1
    print(f"\nA/B done: {ok} ok, {fail} failed. B candidates in tools/_generated/ab/")


if __name__ == "__main__":
    main()
