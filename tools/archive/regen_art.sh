#!/bin/sh
# ART PASS (gpt-image-1 — API spend, user-approved):
#   1. CROP STAGE sprites (11 keys: tomato/corn stage0-3, wheat stage0-2)
#   2. ALL ITEM ICONS regenerated (the floating drop images use the same sprites)
#   3. pixelclean -> PPU normalize -> publish
set -e
cd "$(dirname "$0")/.."

STAGES="plant_tomato_stage0,plant_tomato_stage1,plant_tomato_stage2,plant_tomato_stage3,plant_corn_stage0,plant_corn_stage1,plant_corn_stage2,plant_corn_stage3,plant_wheat_stage0,plant_wheat_stage1,plant_wheat_stage2"

echo "=== 1. crop stage sprites (11) ==="
python3 tools/sprites/gen_sprites.py --source occupants --keys "$STAGES" --force

echo "=== 2. ALL item icons (regen with current style) ==="
python3 tools/sprites/gen_sprites.py --source items --force

echo "=== 3. clean + normalize + publish ==="
python3 tools/sprites/pixelclean.py
python3 tools/sprites/fix_sprite_ppu.py
python3 tools/data/publish_entities.py | tail -1

echo "=== done — review: ls Items/ + Objects/plant_*stage* ; rebuild server for entity data ==="
