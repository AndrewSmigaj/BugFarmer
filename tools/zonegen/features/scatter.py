#!/usr/bin/env python3
"""Vegetation/decoration scatter primitive.

scatter() drops weighted decor onto FREE cells of an allowed surface (default grass),
respecting a minimum spacing so it doesn't look like confetti, and avoiding anything
already `reserved`. It runs LAST in the precedence order, so it never displaces water,
roads, buildings, or farms — it just fills the leftover ground. Decor isn't reserved
(it's not a hard obstacle), but spacing keeps it tidy.

By default placement is UNIFORM (even, blue-noise-ish). Pass `clumping` > 0 for an ORGANIC
look: decor gathers into PATCHES (with bare ground between), and each patch leans toward one
species — the way real wildflowers/bushes actually grow. Same total count (density), just
distributed naturally instead of evenly.
"""
import math
import random


def scatter(b, x0, y0, x1, y1, weights, *, density=0.08, min_spacing=2, seed=0,
            surfaces=("grass",), clumping=0.0, cluster_radius=4):
    rng = random.Random(seed)
    cells = [(x, y)
             for y in range(max(0, y0), min(b.H, y1 + 1))
             for x in range(max(0, x0), min(b.W, x1 + 1))
             if not b.reserved[y][x] and b.surface[y][x] in surfaces]
    ids = list(weights)
    wts = [weights[i] for i in ids]
    placed = []
    target = int(density * len(cells))
    if not cells or target <= 0:
        return placed

    if clumping <= 0:
        # ---- uniform (original behaviour) ----
        rng.shuffle(cells)
        order, centers = cells, None
    else:
        # ---- patchy: seed cluster centres, each with a dominant species, then visit cells
        # in weighted order so high-density patches fill first (Efraimidis–Spirakis sampling) ----
        n_clusters = max(1, round(target / max(3.0, math.pi * cluster_radius)))
        centers = [(*rng.choice(cells), rng.choices(ids, wts)[0]) for _ in range(n_clusters)]

        def field(x, y):                                   # blended gaussian bumps -> patch density
            w = 0.0
            for cx, cy, _sp in centers:
                w += math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * cluster_radius ** 2))
            return w

        spread = max(0.0, min(1.0, clumping))              # 1 = tight patches, ~0 = nearly uniform
        keyed = []
        for (x, y) in cells:
            w = field(x, y) * spread + (1 - spread)
            keyed.append((rng.random() ** (1.0 / max(w, 1e-9)), x, y))
        keyed.sort(reverse=True)
        order = [(x, y) for _k, x, y in keyed]

    for (x, y) in order:
        if len(placed) >= target:
            break
        if any(max(abs(x - px), abs(y - py)) < min_spacing for px, py in placed):
            continue
        if centers:                                        # patch's dominant species most of the time
            cx, cy, sp = min(centers, key=lambda c: (x - c[0]) ** 2 + (y - c[1]) ** 2)
            oid = sp if rng.random() < 0.7 else rng.choices(ids, wts)[0]
        else:
            oid = rng.choices(ids, wts)[0]
        if b.place_occupant(oid, x, y, surface=None, reserve=False):
            placed.append((x, y))
    return placed
