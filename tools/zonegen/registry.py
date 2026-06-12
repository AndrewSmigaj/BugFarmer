#!/usr/bin/env python3
"""Scene registry + canonical preview rendering — the SINGLE source of truth for scenes.

This is authoring metadata and lives WITH the authoring system (zonegen). It defines which
scenes exist, what ZONE each belongs to, and the ONE canonical render scale per scene. Scene
modules under tools/zonegen/scenes/ only define build(); they do NOT pick output paths or
scales. The Art Lab (tools/artlab/) imports this registry to know what to render.

  python3 tools/zonegen/registry.py                 # render all canonical previews
  python3 tools/zonegen/registry.py scene_desert    # render one
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # tools/zonegen
TOOLS = os.path.dirname(HERE)                              # tools
for p in (TOOLS, HERE, os.path.join(HERE, "scenes")):
    if p not in sys.path:
        sys.path.insert(0, p)
from render import render_builder                           # noqa: E402

PREVIEWS = os.path.join(TOOLS, "_generated", "previews")

# scene module -> (zone, canonical scale). scale = px-per-cell / 16; kept LOW so the lab stays snappy
# (a big scene at scale 5+ is a 25-megapixel PNG that's slow to render + ship). Bump a scene's scale
# only if its detail is genuinely hard to read at this size.
REGISTRY = {
    "scene1_player_farm":            ("surface", 3),
    "scene_houses":                  ("surface", 2),
    "scene_beefarm_woods":           ("surface", 3),
    "scene_village":                 ("surface", 2),
    "scene_butterfly_meadow":        ("surface", 3),
    "scene_meadow_forest_edge":      ("surface", 3),
    "scene_underground_caverns":     ("underground", 3),
    "scene_underground_house":       ("underground", 3),
    "scene_underground_mining_camp": ("underground", 3),
    "scene_ant_colony":              ("underground", 2),
    "scene_desert":                  ("desert", 3),
    "scene_road_angles":             ("tests", 4),
    "scene_shore_arcs":              ("tests", 3),
    "scene_orchard":                 ("surface", 3),
    "scene_fly_farm":                ("surface", 4),
    # building PIECES (each is one themed building + its build() wrapper)
    "scene_smith":                   ("pieces", 6),
    "scene_carpenter":               ("pieces", 6),
    "scene_market":                  ("pieces", 6),
    "scene_mayor":                   ("pieces", 5),
    "scene_cottage":                 ("pieces", 6),
    "scene_ecologist":               ("pieces", 5),
    "scene_lakeside":                ("pieces", 4),
    "scene_block_house":             ("tests", 4),
    "scene_block_mine":              ("tests", 4),
    "scene_block_tiling":            ("tests", 4),
    "scene_catalog":                 ("tests", 3),
}


def zone_of(name):
    return REGISTRY[name][0]


def preview_path(name):
    return os.path.join(PREVIEWS, REGISTRY[name][0], f"{name}.png")


def render_one(name, lint=True):
    """Render scene `name` to its canonical preview path; returns the make_scene report (w,h,block_rects).
    Also prints the spatial LINT (text defects) — the QA gate that doesn't depend on eyeballing pixels."""
    zone, scale = REGISTRY[name]
    mod = __import__(name)
    b = mod.build()
    out = preview_path(name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rep = render_builder(b, out, scale=scale)
    if lint:
        defects = b.lint()
        print(f"  LINT {name}: {'0 defects ✓' if not defects else str(len(defects)) + ' defects:'}")
        for d in defects:
            print(f"      - {d}")
    return rep


def render_all(only=None):
    """Renders every registered scene, then regenerates the gallery (index.html)."""
    reports = {}
    for name in (only or REGISTRY):
        try:
            reports[name] = render_one(name)
        except Exception as e:
            print(f"  SKIP {name}: {str(e)[:140]}")
    try:
        from gallery import generate as _gallery
        _gallery()
    except Exception as e:
        print(f"  gallery skipped: {e}")
    return reports


if __name__ == "__main__":
    names = sys.argv[1:] or None
    for n in render_all(only=names):
        print(f"  {zone_of(n)}/{n}.png")
