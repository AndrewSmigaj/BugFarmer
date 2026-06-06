#!/usr/bin/env python3
"""Garden/farm primitives + free-floating collectible decor (flowers, fallen fruit).
Crop beds claim surface='farm'; flowers/fruit are sub-grid `place_decor` (NOT grid occupants),
so they read as gatherable ground dressing rather than blocking furniture."""
import random


def crop_bed(b, x0, y0, x1, y1, crops):
    """A tilled bed with MIXED crops — each column a different crop, cycling `crops`."""
    b.fill_ground(x0, y0, x1, y1, "garden_plot", surface="farm")
    for i, x in enumerate(range(x0, x1 + 1)):
        crop = crops[i % len(crops)]
        for y in range(y0, y1 + 1):
            if b.is_free(x, y):
                b.place_occupant(crop, x, y, surface="farm")


def flower_patch(b, x0, y0, x1, y1, kinds, n, seed=0, scale=0.8):
    """Flowers as free-floating COLLECTIBLE decor — sub-grid (not snapped to cells), on grass."""
    rng = random.Random(seed)
    placed = tries = 0
    while placed < n and tries < n * 10:
        tries += 1
        fx, fy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ix, iy = int(round(fx)), int(round(fy))
        if b.in_bounds(ix, iy) and b.is_free(ix, iy) and b.surface[iy][ix] == "grass":
            b.place_decor(rng.choice(kinds), fx, fy, scale=scale)
            placed += 1


def fruit_around(b, tx, ty, fresh="fallen_fruit", n=6):
    """Fallen/rotting fruit as free-floating decor around a tree base (sub-grid, half scale)."""
    rng = random.Random(tx * 131 + ty)
    for _ in range(n):
        dx, dy = rng.uniform(-1.5, 1.5), rng.uniform(-1.2, 0.3)
        fid = "rotten_fruit" if rng.random() < 0.3 else fresh
        b.place_decor(fid, tx + dx, ty + dy, scale=0.5)
