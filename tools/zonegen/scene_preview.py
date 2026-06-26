#!/usr/bin/env python3
"""The ONE place a scene becomes a preview PNG.

A scene file declares `PREVIEW = "<folder>"` (e.g. "examples/buildings" or "zones/village_21_B/scenes")
and optionally `SCALE`. This module computes the output path from that and renders — used by each scene's
`__main__` AND by `tools/world/previews.py` (which discovers + renders them all). No registry, no hand-typed
output paths: the scene declares where it goes, in one place. See docs/guides/authoring/ORGANIZATION.md.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # tools/zonegen
SCENES = os.path.join(HERE, "scenes")


def _root():                                               # repo root = first parent holding .git
    r = HERE
    while not os.path.exists(os.path.join(r, ".git")) and os.path.dirname(r) != r:
        r = os.path.dirname(r)
    return r


PREVIEWS = os.path.join(_root(), "tools", "_generated", "previews")

for _p in (HERE, SCENES):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from render import render_builder                          # noqa: E402


def _clean(stem):                                          # drop the scene_/scene1_ prefix → clean filename
    for pre in ("scene_", "scene1_"):
        if stem.startswith(pre):
            return stem[len(pre):]
    return stem


def out_path(scene_file, preview):
    name = _clean(os.path.splitext(os.path.basename(scene_file))[0])
    return os.path.join(PREVIEWS, preview, f"{name}.png")


def render(builder, scene_file, preview, scale=3):
    out = out_path(scene_file, preview)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render_builder(builder, out, scale=scale)
    print("preview ->", out)
    return out


def discover_and_render():
    """Import every scenes/*.py declaring a PREVIEW global; build() + render it. Returns [(name, status)]."""
    results = []
    for fn in sorted(os.listdir(SCENES)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        mod = fn[:-3]
        try:
            m = importlib.import_module(mod)
        except Exception as e:
            results.append((mod, f"SKIP import: {str(e)[:90]}"))
            continue
        preview = getattr(m, "PREVIEW", None)
        if not preview:                                    # not a previewed scene (zone_*.py, superseded, …)
            continue
        try:
            b = m.build()
            out = render(b, os.path.join(SCENES, fn), preview, getattr(m, "SCALE", 3))
            defects = b.lint() if hasattr(b, "lint") else []
            results.append((mod, f"{os.path.relpath(out, PREVIEWS)}  ({'lint 0' if not defects else str(len(defects)) + ' defects'})"))
        except Exception as e:
            results.append((mod, f"FAIL render: {str(e)[:90]}"))
    return results


if __name__ == "__main__":
    for name, status in discover_and_render():
        print(f"  {name:32} {status}")
