#!/usr/bin/env python3
"""Variant library + selection + promotion.

  tools/_generated/variants/<key>/<key>_<n>.png   candidate sprites for a key (any art type)
  tools/_generated/variants/selection.json        {key: chosen variant filename}

Promote = copy the chosen variant over the live game sprite (Resources/Objects or /Tiles) + patch .meta.
A key is a TILE (lives under Tiles/) if it has a row in the tiles catalog; otherwise it's an object.
"""
import json
import os
import re
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import gen_sprites as g                                     # noqa: E402

VARIANTS = os.path.join(TOOLS, "_generated", "variants")
SEL_PATH = os.path.join(VARIANTS, "selection.json")
RES = g.RESOURCES


def tile_keys():
    try:
        return set(json.load(open(os.path.join(TOOLS, "art", "catalog", "tiles.json"))))
    except Exception:
        return set()


def library():
    """{key: [variant filenames sorted]} for every variants/<key>/ folder with PNGs."""
    lib = {}
    if os.path.isdir(VARIANTS):
        for key in sorted(os.listdir(VARIANTS)):
            d = os.path.join(VARIANTS, key)
            if os.path.isdir(d):
                pngs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
                if pngs:
                    lib[key] = pngs
    return lib


def load_selection():
    return json.load(open(SEL_PATH)) if os.path.exists(SEL_PATH) else {}


def save_selection(sel):
    os.makedirs(VARIANTS, exist_ok=True)
    json.dump(sel, open(SEL_PATH, "w"), indent=2)


def live_path(key):
    sub = "Tiles" if key in tile_keys() else "Objects"
    return os.path.join(RES, sub, f"{key}.png")


def next_index(key):
    """Lowest free <key>_<n>.png index in variants/<key>/ (so generation appends, never overwrites)."""
    d = os.path.join(VARIANTS, key)
    n = 0
    if os.path.isdir(d):
        for f in os.listdir(d):
            m = re.match(rf"{re.escape(key)}_(\d+)\.png$", f)
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


def promote(key, variant_filename):
    """Copy variants/<key>/<filename> over the live sprite (+meta). Returns the live path or None."""
    src = os.path.join(VARIANTS, key, variant_filename)
    if not os.path.exists(src):
        return None
    dst = live_path(key)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)
    if "new" in str(g.patch_meta(dst)):                     # brand-new sprite: give it a sibling's import settings
        _ensure_meta(dst)
    return dst


def _ensure_meta(dst):
    folder = os.path.dirname(dst)
    sibling = next((os.path.join(folder, f) for f in os.listdir(folder)
                    if f.endswith(".png.meta") and f != os.path.basename(dst) + ".meta"), None)
    if sibling:
        m = re.sub(r"guid: [0-9a-f]{32}", "guid: " + uuid.uuid4().hex, open(sibling).read(), count=1)
        open(dst + ".meta", "w").write(m)


# ---- populating the library (so the lab isn't empty after a _generated wipe) ----
def add_variant(key, src_png):
    """Copy an arbitrary PNG into variants/<key>/ as the next <key>_<n>.png. Returns the dest path."""
    d = os.path.join(VARIANTS, key)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, f"{key}_{next_index(key)}.png")
    shutil.copy(src_png, dst)
    return dst


def seed_live(keys):
    """Seed each key's CURRENT live game sprite as a baseline variant (only if it has none yet).
    Gives the lab something to show and a baseline to compare new candidates against. No API spend."""
    added = []
    for key in keys:
        if library().get(key):                     # already has variants — don't duplicate
            continue
        live = live_path(key)
        if os.path.exists(live):
            added.append(add_variant(key, live))
    return added


BLOCKLAB = os.path.join(TOOLS, "_generated", "blocklab")


def import_blocklab(blocks=None):
    """Bridge the block bake-off (tools/_generated/blocklab/<approach>/<block>_<i>.png) into the lab:
    copy each candidate into variants/<block>/. This is the link blocklab.py never had. No API spend."""
    added = []
    if not os.path.isdir(BLOCKLAB):
        return added
    for approach in sorted(os.listdir(BLOCKLAB)):
        adir = os.path.join(BLOCKLAB, approach)
        if not os.path.isdir(adir):
            continue
        for f in sorted(os.listdir(adir)):
            m = re.match(r"(.+)_(\d+)\.png$", f)
            if not m:
                continue
            block = m.group(1)
            if blocks and block not in blocks:
                continue
            added.append(add_variant(block, os.path.join(adir, f)))
    return added


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Populate the Art Lab variant library (no API spend).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seed", help="seed keys' current live sprite as a baseline variant")
    s.add_argument("keys", nargs="+")
    ib = sub.add_parser("import-blocklab", help="pull block bake-off output into the lab")
    ib.add_argument("blocks", nargs="*", help="limit to these blocks (default: all found)")
    ls = sub.add_parser("list", help="show the current library")
    a = ap.parse_args()
    if a.cmd == "seed":
        for p in seed_live(a.keys):
            print("  seeded", os.path.relpath(p, TOOLS))
    elif a.cmd == "import-blocklab":
        got = import_blocklab(a.blocks or None)
        for p in got:
            print("  imported", os.path.relpath(p, TOOLS))
        if not got:
            print("  (no blocklab output found — run `python3 tools/blocklab.py` first)")
    elif a.cmd == "list":
        for k, v in library().items():
            print(f"  {k}: {len(v)} variant(s)")
