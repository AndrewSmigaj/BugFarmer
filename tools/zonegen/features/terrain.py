#!/usr/bin/env python3
"""Ground/terrain primitives shared across scenes: paths and an organic pond.
All coordinate through the builder's ground grid + surface mask (paths -> surface 'path',
water -> reserved 'water'), so roads route around water and scatter avoids both."""
import random


def hpath(b, x0, x1, y, tile="stone_path"):
    """Horizontal path strip on row y from x0..x1 (inclusive), surface='path'."""
    for x in range(x0, x1 + 1):
        if b.in_bounds(x, y):
            b.set_ground(x, y, tile, surface="path")


def vpath(b, x, y0, y1, tile="stone_path"):
    """Vertical path strip on column x from y0..y1 (inclusive), surface='path'."""
    for y in range(y0, y1 + 1):
        if b.in_bounds(x, y):
            b.set_ground(x, y, tile, surface="path")


def stream(b, start, end, *, width=1, seed=0, wobble=0.5):
    """A meandering surface WATER channel from start to end (never straight). Sets water tiles +
    reserves; returns the water cells. Reuse the same wander rule as tunnels."""
    import math
    rng = random.Random(seed)
    x, y = start
    ex, ey = end
    heading = math.atan2(ey - y, ex - x)
    cells = set()
    steps = 0
    while abs(x - ex) + abs(y - ey) > 1 and steps < 4 * (abs(ex - x) + abs(ey - y)) + 60:
        steps += 1
        goal = math.atan2(ey - y, ex - x)
        heading += 0.3 * math.atan2(math.sin(goal - heading), math.cos(goal - heading))
        heading += rng.uniform(-wobble, wobble)
        x += int(round(math.cos(heading)))
        y += int(round(math.sin(heading)))
        r = max(0.5, width / 2.0 + rng.choice([-0.5, 0, 0]))
        rr = int(math.ceil(r))
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                if dx * dx + dy * dy <= r * r + 0.5 and b.in_bounds(x + dx, y + dy):
                    deep = dx == 0 and dy == 0 and width >= 2
                    b.set_ground(x + dx, y + dy, "water_deep" if deep else "water_shallow", surface="water")
                    b.reserve(x + dx, y + dy, surface="water")
                    cells.add((x + dx, y + dy))
    return cells


def pond(b, cx, cy, rx, ry, seed=3):
    """An ORGANIC water feature: irregular shallow blob with a smaller deep centre + reeds."""
    rng = random.Random(seed)
    bank = []
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if not b.in_bounds(x, y):
                continue
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            d = (nx * nx + ny * ny) ** 0.5
            if d <= 1.0 + rng.uniform(-0.15, 0.15):
                b.set_ground(x, y, "water_deep" if d <= 0.5 else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
            elif d <= 1.5:
                bank.append((x, y))
    for (x, y) in bank:
        if b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.3:
            b.place_occupant("reeds", x, y)
