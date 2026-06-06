#!/usr/bin/env python3
"""Reusable house FLOOR-PLAN generators — pure geometry, no furniture/collection choice.

Each returns `(specs, front)` where specs = [(name, rect, template_fn), ...] with inclusive
outer-wall rects that SHARE exactly one wall line between adjacent rooms (so place_house punches
an interior door), and front = ("room", side) for the exterior door (always on a south/min-y wall
that is exterior). Compose with house.styled_rooms(specs, collection) -> place_house(b, rooms, front=front).

Shapes: row_house (3 rooms in a bar), t_house (4 = bar + a north stem, the ⊥), plus_house
(5 = bar + two north stems). Rooms are ~10x10 outer (≈8x8 interior) so furniture fits.
"""
from features.house import (living_template, bedroom_template,         # noqa: E402
                            kitchen_template, crafting_template)


def _shift(specs, ox, oy):
    return [(n, (x0 + ox, y0 + oy, x1 + ox, y1 + oy), f)
            for (n, (x0, y0, x1, y1), f) in specs]


def bbox(specs):
    """Overall (x0,y0,x1,y1) covering all room rects in a specs list."""
    xs0 = min(r[1][0] for r in specs); ys0 = min(r[1][1] for r in specs)
    xs1 = max(r[1][2] for r in specs); ys1 = max(r[1][3] for r in specs)
    return (xs0, ys0, xs1, ys1)


def row_house(ox=0, oy=0):
    """3 rooms in a horizontal bar."""
    specs = [
        ("bedroom", (0, 0, 9, 9),  bedroom_template),
        ("main",    (9, 0, 18, 9), living_template),
        ("kitchen", (18, 0, 27, 9), kitchen_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def t_house(ox=0, oy=0):
    """4 rooms: a bar of 3 with a crafting stem rising NORTH off the main room (the ⊥)."""
    specs = [
        ("bedroom",  (0, 0, 9, 9),   bedroom_template),
        ("main",     (9, 0, 20, 9),  living_template),
        ("kitchen",  (20, 0, 30, 9), kitchen_template),
        ("crafting", (11, 9, 19, 17), crafting_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")


def plus_house(ox=0, oy=0):
    """5 rooms: a bar of 3 with two stems rising NORTH (a study off main, a sunroom off kitchen)."""
    specs = [
        ("bedroom", (0, 0, 9, 9),    bedroom_template),
        ("main",    (9, 0, 20, 9),   living_template),
        ("kitchen", (20, 0, 30, 9),  kitchen_template),
        ("study",   (11, 9, 19, 17), bedroom_template),
        ("sunroom", (21, 9, 29, 17), living_template),
    ]
    return _shift(specs, ox, oy), ("main", "top")
