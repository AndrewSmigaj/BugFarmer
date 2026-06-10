#!/usr/bin/env python3
"""Normalize Unity sprite import PPU for WORLD sprites.

The world-object convention is spritePixelsToUnits: 16 (1 cell = 16px = 1 world unit —
see TilemapManager cellSize). Unity auto-imports NEW pngs at the default PPU 100, which
renders them at 16% size ("micro" sprites). Everything placed in early zones was set to 16;
the long tail of generated-but-not-yet-placed art (225 of 315 Objects at the time of this
fix) was still at 100 — a latent bug that fires the first time each one is placed.

Run after adding any new sprite under Resources/Objects (or Items):
  python3 tools/fix_sprite_ppu.py            # fix Objects/ + Items/
  python3 tools/fix_sprite_ppu.py --dry-run  # report only
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "BugFarmerClient", "Assets", "Resources")
FOLDERS = ["Objects", "Items", "Bugs"]
PPU = "16"

dry = "--dry-run" in sys.argv
ppu_pat = re.compile(r"(spritePixelsToUnits:\s*)(\d+)")
# Pixel art must import POINT-filtered (filterMode: 0); Unity's default is Bilinear (1),
# which renders new icons/sprites blurry. NOTE: metas only exist after Unity has imported
# the png once — generate → open/focus Unity (import) → run this → Unity reimports on focus.
filt_pat = re.compile(r"(filterMode:\s*)(-?\d+)")

total = fixed = 0
for folder in FOLDERS:
    base = os.path.join(ROOT, folder)
    if not os.path.isdir(base):
        continue
    for name in sorted(os.listdir(base)):
        if not name.endswith(".png.meta"):
            continue
        path = os.path.join(base, name)
        text = open(path).read()
        m = ppu_pat.search(text)
        if not m:
            continue
        total += 1
        f = filt_pat.search(text)
        bad_ppu = m.group(2) != PPU
        bad_filt = f is not None and f.group(2) != "0"
        if bad_ppu or bad_filt:
            fixed += 1
            if dry:
                what = " ".join(filter(None, [
                    f"PPU {m.group(2)}->{PPU}" if bad_ppu else "",
                    f"filterMode {f.group(2)}->0" if bad_filt else ""]))
                print(f"  would fix {folder}/{name}: {what}")
            else:
                if bad_ppu:
                    text = ppu_pat.sub(rf"\g<1>{PPU}", text, count=1)
                if bad_filt:
                    text = filt_pat.sub(r"\g<1>0", text, count=1)
                open(path, "w").write(text)

print(f"{'would fix' if dry else 'fixed'} {fixed}/{total} sprite metas -> PPU {PPU}, filterMode 0")
