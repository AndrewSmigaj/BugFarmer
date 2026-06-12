#!/usr/bin/env python3
"""Pipeline B entry point — hand-authored player sprites (NO API).

v2 (2026-06): the real work lives in tools/player_sprites/ — text-grid master
templates (body_frames.py), 3-shade palettes (palettes.py), and the region
renderer (pixkit.py) that derives baked classes, walk frames (_w1/_w3) and
paper-doll layers (Resources/Player/layers/) from ONE master grid per
direction. See docs/guides/art/CHARACTER_DESIGN_GUIDE.md.

Run: python3 tools/generate_player_sprites.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from player_sprites.generate import main  # noqa: E402

if __name__ == "__main__":
    main()
