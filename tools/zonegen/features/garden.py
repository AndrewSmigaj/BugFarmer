#!/usr/bin/env python3
"""Garden/farm primitives. EVERYTHING snaps to the grid except bugs — flowers and crops are real
grid OCCUPANTS (one per cell, saved to the zone), since the player plants them. (Only `fruit_around`
stays sub-grid: fallen fruit is a dropped pickup, not a planted thing.)"""
import random


def crop_bed(b, x0, y0, x1, y1, crops):
    """A tilled bed with MIXED crops — each column a different crop, cycling `crops`."""
    b.fill_ground(x0, y0, x1, y1, "garden_plot", surface="farm")
    for i, x in enumerate(range(x0, x1 + 1)):
        crop = crops[i % len(crops)]
        for y in range(y0, y1 + 1):
            if b.is_free(x, y):
                b.place_occupant(crop, x, y, surface="farm")


def flower_patch(b, x0, y0, x1, y1, kinds, n, seed=0):
    """Flowers PLANTED on the GRID — one occupant per cell on grass (saved to the zone). Everything
    snaps to the grid except bugs; the player can plant flowers, so they're real grid occupants."""
    rng = random.Random(seed)
    placed = tries = 0
    while placed < n and tries < n * 12:
        tries += 1
        ix, iy = rng.randint(int(x0), int(x1)), rng.randint(int(y0), int(y1))
        if b.in_bounds(ix, iy) and b.is_free(ix, iy) and b.surface[iy][ix] == "grass":
            b.place_occupant(rng.choice(kinds), ix, iy)
            placed += 1


def fruit_around(b, tx, ty, fresh="fallen_fruit", n=6):
    """Fallen/rotting fruit as free-floating decor around a tree base (sub-grid, half scale)."""
    rng = random.Random(tx * 131 + ty)
    for _ in range(n):
        dx, dy = rng.uniform(-1.5, 1.5), rng.uniform(-1.2, 0.3)
        fid = "rotten_fruit" if rng.random() < 0.3 else fresh
        b.place_decor(fid, tx + dx, ty + dy, scale=0.5)
