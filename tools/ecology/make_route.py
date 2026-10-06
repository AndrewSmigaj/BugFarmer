#!/usr/bin/env python3
"""Make a walking route for the headless test player through a zone's busiest feeding spots
(docs/plans/village-slice.md, Stage 1.0b: the wanderer when headless, the camera tour when windowed).

    python3 tools/ecology/make_route.py bench_village                  # -> tools/_generated/routes/bench_village.route
    python3 tools/ecology/make_route.py bench_village --stops 8 --png  # also a picture of the route

How: the zone's food sources (fruit trees, flowers, milkweed, nests, leaf litter, compost) are counted in 16x16-cell
bins; the busiest bins, at least 24 cells apart, become the stops; the stops are visited in nearest-neighbour order
from the zone's spawn point; each leg is pathed (A*, 8 directions) on the PLAYER-blocking grid — the server's own rule
(`IsBlockedForPlayers`, state.go): an object whose entity data says `blocks_players`, or water / lava ground — kept a
cell away from anything blocked and 6 cells from the zone's edge. The file lists the path's points, one "x,y" cell per
line (the player walks from point to point), with the stops in the header.
"""
import argparse
import glob
import heapq
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHUNK = 32
PLAYER_BLOCKING_GROUND = {"water_shallow", "water_deep", "lava"}  # state.go IsBlockedForPlayers
FRUIT_TREES = {"tree_apple", "tree_plum", "tree_cherry", "tree_orange", "tree_pear", "tree_peach"}


def is_food(oid):
    return (oid in FRUIT_TREES or oid.startswith("flower_") or oid in ("poppy", "lavender", "milkweed")
            or "nest" in oid or "litter" in oid or "compost" in oid)


def load(zone):
    zdir = os.path.join(ROOT, "nakama", "data", "zones", zone)
    cfg = json.load(open(os.path.join(zdir, "zone.json")))
    W, H = cfg.get("width") or 256, cfg.get("height") or 256
    blocks = set()
    for f in ("occupants", "placeables"):
        p = os.path.join(ROOT, "nakama", "data", "entities", f + ".json")
        for k, v in json.load(open(p)).items():
            if isinstance(v, dict) and (v.get("world") or {}).get("blocks_players"):
                blocks.add(k)
    blocked = [[False] * W for _ in range(H)]
    food = []
    for path in glob.glob(os.path.join(zdir, "chunk_*.json")):
        d = json.load(open(path))
        cx, cy = d["chunk_x"], d["chunk_y"]
        for ly, row in enumerate(d.get("ground", [])):
            for lx, t in enumerate(row or []):
                gx, gy = cx * CHUNK + lx, cy * CHUNK + ly
                if t and 0 <= gx < W and 0 <= gy < H and t.split("~")[0] in PLAYER_BLOCKING_GROUND:
                    blocked[gy][gx] = True
        for ly, row in enumerate(d.get("occupants", [])):
            for lx, c in enumerate(row or []):
                if not (isinstance(c, dict) and c.get("id")):
                    continue
                gx, gy = cx * CHUNK + lx, cy * CHUNK + ly
                if not (0 <= gx < W and 0 <= gy < H):
                    continue
                if c["id"] in blocks:
                    blocked[gy][gx] = True
                if c.get("anchor") and is_food(c["id"]):
                    food.append((gx, gy))
    spawn = cfg.get("spawn_point") or [W // 2, H // 2]
    return W, H, blocked, food, (int(spawn[0]), int(spawn[1]))


def walkable_grid(W, H, blocked, edge=6, clearance=1):
    ok = [[True] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if x < edge or y < edge or x >= W - edge or y >= H - edge:
                ok[y][x] = False
                continue
            for dy in range(-clearance, clearance + 1):
                for dx in range(-clearance, clearance + 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and blocked[yy][xx]:
                        ok[y][x] = False
    return ok


def reachable_from(ok, start, W, H):
    """The walkable cells a player at `start` can actually reach (a stop inside a closed building is not)."""
    seen = [[False] * W for _ in range(H)]
    stack = [start]
    seen[start[1]][start[0]] = True
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and ok[ny][nx] and not seen[ny][nx]:
                seen[ny][nx] = True
                stack.append((nx, ny))
    return seen


def nearest_walkable(ok, x, y, W, H, radius=12):
    best, bd = None, math.inf
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < W and 0 <= yy < H and ok[yy][xx]:
                d = dx * dx + dy * dy
                if d < bd:
                    best, bd = (xx, yy), d
    return best


def astar(ok, a, b, W, H):
    """8-direction A* on walkable cells; diagonal moves only when both side cells are walkable (no corner cutting)."""
    if a == b:
        return [a]
    openq = [(0.0, a)]
    came, g = {a: None}, {a: 0.0}
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == b:
            path = [cur]
            while came[path[-1]] is not None:
                path.append(came[path[-1]])
            return path[::-1]
        x, y = cur
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < H and ok[ny][nx]):
                continue
            if dx and dy and not (ok[y][nx] and ok[ny][x]):
                continue
            ng = g[cur] + (1.4142 if dx and dy else 1.0)
            if ng < g.get((nx, ny), math.inf):
                g[(nx, ny)] = ng
                came[(nx, ny)] = cur
                heapq.heappush(openq, (ng + math.hypot(b[0] - nx, b[1] - ny), (nx, ny)))
    return None


def thin(path, every=5):
    """Keep turns and a point every few cells, so the player walks short straight legs that follow the path."""
    if len(path) <= 2:
        return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        d0 = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        d1 = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        if d0 != d1 or i % every == 0:
            out.append(path[i])
    out.append(path[-1])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("zone")
    ap.add_argument("--stops", type=int, default=8)
    ap.add_argument("--out")
    ap.add_argument("--png", action="store_true", help="also draw the route over the zone (north up)")
    a = ap.parse_args()

    W, H, blocked, food, spawn = load(a.zone)
    ok = walkable_grid(W, H, blocked)
    start = nearest_walkable(ok, spawn[0], spawn[1], W, H, radius=20)
    if start is None:
        sys.exit("the zone's spawn point has no walkable cell nearby")
    ok = reachable_from(ok, start, W, H)  # from here on, only ground the player can reach counts
    bins = {}
    for x, y in food:
        bins.setdefault((x // 16, y // 16), []).append((x, y))
    ranked = sorted(bins.items(), key=lambda kv: -len(kv[1]))
    stops = []
    for (bx, by), pts in ranked:
        cx = sum(p[0] for p in pts) // len(pts)
        cy = sum(p[1] for p in pts) // len(pts)
        if any(math.hypot(cx - s[0], cy - s[1]) < 24 for s, _ in stops):
            continue
        w = nearest_walkable(ok, cx, cy, W, H)
        if w:
            stops.append((w, len(pts)))
        if len(stops) >= a.stops:
            break
    if not stops:
        sys.exit("no reachable food clusters found")

    order, cur, left = [], start, list(stops)
    while left:
        i = min(range(len(left)), key=lambda k: math.hypot(left[k][0][0] - cur[0], left[k][0][1] - cur[1]))
        order.append(left.pop(i))
        cur = order[-1][0]

    points, legs_failed, at = [], 0, start
    for (stop, n) in order + [order[0]]:  # close the loop so the route repeats cleanly
        leg = astar(ok, at, stop, W, H)
        if leg is None:
            legs_failed += 1
            continue
        points.extend(thin(leg)[1:] if points else thin(leg))
        at = stop

    out = a.out or os.path.join(ROOT, "tools", "_generated", "routes", f"{a.zone}.route")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(f"# route for {a.zone}: {len(order)} stops at the busiest feeding spots, pathed around player-blocking cells\n")
        f.write(f"# from tools/ecology/make_route.py; legs that couldn't be pathed: {legs_failed}\n")
        for (s, n) in order:
            f.write(f"# stop {s[0]},{s[1]} ({n} food sources within its 16-cell bin)\n")
        for x, y in points:
            f.write(f"{x},{y}\n")
    length = sum(math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]) for i in range(len(points) - 1))
    print(f"{out}: {len(order)} stops, {len(points)} points, ~{length:.0f} cells per lap "
          f"(~{length / 5:.0f} s at the player's 5 cells/s), unpathable legs: {legs_failed}")

    if a.png:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (W, H), (110, 160, 90))
        px = img.load()
        for y in range(H):
            for x in range(W):
                if blocked[y][x]:
                    px[x, H - 1 - y] = (60, 60, 70)
        d = ImageDraw.Draw(img)
        for x, y in food:
            d.point((x, H - 1 - y), fill=(240, 220, 80))
        d.line([(x, H - 1 - y) for x, y in points], fill=(220, 40, 40), width=1)
        for (s, n) in order:
            d.ellipse((s[0] - 3, H - 1 - s[1] - 3, s[0] + 3, H - 1 - s[1] + 3), outline=(255, 255, 255))
        img = img.resize((W * 3, H * 3), Image.NEAREST)
        png = out.rsplit(".", 1)[0] + ".png"
        img.save(png)
        print(f"picture (north up): {png}")
    return 0 if legs_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
