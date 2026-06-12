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


def orchard(b, x0, y0, x1, y1, *, tree="tree_apple", row_spacing=4, tree_spacing=3,
            jitter=1, crates=2, ladders=1, fruit=True, seed=0):
    """A worked ORCHARD: rows of fruit trees with human intent but organic variation —
    jittered rows (never a perfect grid), walking lanes between them, crates and a
    ladder at the row ends, fallen fruit under some trees. Restores the village
    intent-doc landmark and feeds the fruit→rot→fly loop visibly.

    Trees plant only on free grass, so the orchard wraps around roads/water instead
    of stamping over them. Post-jitter MIN SPACING of `tree_spacing` is ENFORCED
    (Chebyshev, the forest() rule) — a nominal grid + jitter can otherwise collapse
    two ~2-cell-tall tree sprites into an overlap. NOTE: `fruit_around` decor is
    RENDER-ONLY (previews); live fallen fruit comes from the server fruit-tree sim.
    Returns the planted tree cells."""
    rng = random.Random(seed)
    planted = []

    def spaced(x, y):
        return all(max(abs(x - px), abs(y - py)) >= tree_spacing for (px, py) in planted)

    for row_i, ry in enumerate(range(y0 + 1, y1, row_spacing)):
        # each row starts with its own phase so rows don't align vertically
        x = x0 + 1 + (row_i % 2)
        while x <= x1 - 1:
            jx = x + rng.randint(-jitter, jitter)
            jy = ry + rng.randint(-jitter, jitter)
            if b.in_bounds(jx, jy) and b.is_free(jx, jy) \
                    and b.surface[jy][jx] == "grass" and spaced(jx, jy):
                if b.place_occupant(tree, jx, jy, surface="farm"):
                    planted.append((jx, jy))
                    if fruit and rng.random() < 0.3:
                        fruit_around(b, jx, jy, n=rng.randint(2, 4))
            x += tree_spacing + rng.randint(0, 1)

    # working clutter at the row ends (crates near the first row, ladder mid-orchard)
    props = (["apple_crate"] * crates) + (["ladder"] * ladders)
    for i, prop in enumerate(props):
        for _ in range(12):  # a few tries each; skip quietly if the edge is crowded
            px = x1 - 1 - rng.randint(0, 2) if i % 2 == 0 else x0 + 1 + rng.randint(0, 2)
            py = y0 + 1 + rng.randint(0, max(1, y1 - y0 - 2))
            if b.in_bounds(px, py) and b.is_free(px, py) and b.surface[py][px] == "grass":
                b.place_occupant(prop, px, py)
                break
    return planted


def fruit_around(b, tx, ty, fresh="fallen_fruit", n=6):
    """Fallen/rotting fruit as free-floating decor around a tree base (sub-grid, half scale)."""
    rng = random.Random(tx * 131 + ty)
    for _ in range(n):
        dx, dy = rng.uniform(-1.5, 1.5), rng.uniform(-1.2, 0.3)
        fid = "rotten_fruit" if rng.random() < 0.3 else fresh
        b.place_decor(fid, tx + dx, ty + dy, scale=0.5)
