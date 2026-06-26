#!/usr/bin/env python3
"""Normalize Unity sprite import PPU for WORLD sprites.

The world-object convention is spritePixelsToUnits: 16 (1 cell = 16px = 1 world unit —
see TilemapManager cellSize). Unity auto-imports NEW pngs at the default PPU 100, which
renders them at 16% size ("micro" sprites). Everything placed in early zones was set to 16;
the long tail of generated-but-not-yet-placed art (225 of 315 Objects at the time of this
fix) was still at 100 — a latent bug that fires the first time each one is placed.

Run after adding any new sprite under Resources/Objects (or Items):
  python3 tools/sprites/fix_sprite_ppu.py            # fix Objects/ + Items/
  python3 tools/sprites/fix_sprite_ppu.py --dry-run  # report only
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
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

# ---- Player/ (recursive: covers layers/ subfolders) -------------------------
# Same PPU/point rules; ADDITIONALLY layer sprites must be CPU-readable
# (isReadable: 1) — CharacterComposer blends them with GetPixels32 at runtime.
read_pat = re.compile(r"(isReadable:\s*)(\d+)")
player_base = os.path.join(ROOT, "Player")
for dirpath, _dirs, names in os.walk(player_base):
    needs_read = f"{os.sep}layers" in dirpath or dirpath.endswith("layers")
    for name in sorted(names):
        if not name.endswith(".png.meta"):
            continue
        # TRIAL (2026-06): the vector-Scout farmer_* sprites are 36x44 at
        # PPU 28 (~1.3x1.6 cells) — don't force them back to 16.
        if name.startswith("farmer_"):
            continue
        path = os.path.join(dirpath, name)
        text = open(path).read()
        m = ppu_pat.search(text)
        if not m:
            continue
        total += 1
        f = filt_pat.search(text)
        r = read_pat.search(text)
        bad_ppu = m.group(2) != PPU
        bad_filt = f is not None and f.group(2) != "0"
        bad_read = needs_read and r is not None and r.group(2) != "1"
        if bad_ppu or bad_filt or bad_read:
            fixed += 1
            rel = os.path.relpath(path, player_base)
            if dry:
                what = " ".join(filter(None, [
                    f"PPU {m.group(2)}->{PPU}" if bad_ppu else "",
                    f"filterMode {f.group(2)}->0" if bad_filt else "",
                    "isReadable->1" if bad_read else ""]))
                print(f"  would fix Player/{rel}: {what}")
            else:
                if bad_ppu:
                    text = ppu_pat.sub(rf"\g<1>{PPU}", text, count=1)
                if bad_filt:
                    text = filt_pat.sub(r"\g<1>0", text, count=1)
                if bad_read:
                    text = read_pat.sub(r"\g<1>1", text, count=1)
                open(path, "w").write(text)

# ---- UI/ (point filter only — Unity's bilinear default blurs pixel-art UI;
# PPU is irrelevant: UI Images scale by RectTransform, and 9-slice borders are
# passed in code via Sprite.Create, never stored in metas)
ui_base = os.path.join(ROOT, "UI")
if os.path.isdir(ui_base):
    for name in sorted(os.listdir(ui_base)):
        if not name.endswith(".png.meta"):
            continue
        path = os.path.join(ui_base, name)
        text = open(path).read()
        f = filt_pat.search(text)
        total += 1
        if f is not None and f.group(2) != "0":
            fixed += 1
            if dry:
                print(f"  would fix UI/{name}: filterMode {f.group(2)}->0")
            else:
                open(path, "w").write(filt_pat.sub(r"\g<1>0", text, count=1))

print(f"{'would fix' if dry else 'fixed'} {fixed}/{total} sprite metas -> PPU {PPU}, filterMode 0 (+isReadable on Player/layers, point on UI)")
