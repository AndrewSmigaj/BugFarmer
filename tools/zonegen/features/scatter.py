#!/usr/bin/env python3
"""Vegetation/decoration scatter primitive.

scatter() drops weighted decor onto FREE cells of an allowed surface (default grass),
respecting a minimum spacing so it doesn't look like confetti, and avoiding anything
already `reserved`. It runs LAST in the precedence order, so it never displaces water,
roads, buildings, or farms — it just fills the leftover ground. Decor isn't reserved
(it's not a hard obstacle), but spacing keeps it tidy.
"""
import random


def scatter(b, x0, y0, x1, y1, weights, *, density=0.08, min_spacing=2, seed=0,
            surfaces=("grass",)):
    rng = random.Random(seed)
    cells = [(x, y)
             for y in range(max(0, y0), min(b.H, y1 + 1))
             for x in range(max(0, x0), min(b.W, x1 + 1))
             if not b.reserved[y][x] and b.surface[y][x] in surfaces]
    rng.shuffle(cells)
    ids = list(weights)
    wts = [weights[i] for i in ids]
    placed = []
    target = int(density * len(cells))
    for (x, y) in cells:
        if len(placed) >= target:
            break
        if any(max(abs(x - px), abs(y - py)) < min_spacing for px, py in placed):
            continue
        oid = rng.choices(ids, wts)[0]
        if b.place_occupant(oid, x, y, surface=None, reserve=False):
            placed.append((x, y))
    return placed
