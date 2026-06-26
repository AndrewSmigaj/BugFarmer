#!/usr/bin/env python3
"""Top-down bug-distribution map per game-day, over the ACTUAL zone terrain — WHERE the bugs are.

Orientation: NORTH is UP (y increases northward in this zone: rocks at small y = south, lake SW). We do NOT
invert the axis. Background = the zone's ground tiles (lake/water, roads, fields) + faint tree & rock
occupant overlays + the spawn-area circles, so a bug dot has real geographic context.

Parses `SWARMSNAP day=.. sp=.. x=.. y=.. count=..` (server emitSwarmSnapshot) → one PNG per game-day +
a contact-sheet grid. Also a `--reference` mode that draws just the backdrop (+ optional proposed points).

Usage:
  python3 tools/ecology/plot_bugmap.py --log <nakama.log> --zone village_21_B --out <dir>
  python3 tools/ecology/plot_bugmap.py --reference --zone village_21_B --out file.png --mark "label:x,y" ...
"""
import argparse
import glob
import json
import math
import os
import re

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SP = {  # species -> (colour, label)
    "fly_common": ("#d62728", "fly"), "butterfly_meadow": ("#ff7f0e", "butterfly"),
    "wasp_common": ("#111111", "wasp"), "centipede_garden": ("#2ca02c", "centipede"),
    "millipede": ("#8c564b", "millipede"), "beetle_carrion": ("#1f77b4", "beetle"),
}
TILE_RGB = {  # ground tile -> colour (lightened; it's a backdrop)
    "grass": (0.80, 0.88, 0.72), "dirt": (0.80, 0.71, 0.55), "mud": (0.66, 0.58, 0.45),
    "garden_plot": (0.74, 0.62, 0.43), "sand": (0.92, 0.86, 0.66),
    "water_deep": (0.33, 0.52, 0.72), "water_shallow": (0.55, 0.74, 0.88), "bridge_wood": (0.66, 0.52, 0.34),
    "wood_floor": (0.72, 0.60, 0.42), "stone_floor": (0.72, 0.72, 0.74),
    "stone_path": (0.78, 0.74, 0.66),
}
DEFAULT_RGB = (0.82, 0.88, 0.74)
SNAP = re.compile(r"SWARMSNAP day=(\d+) sp=(\S+) x=([\d.]+) y=([\d.]+) count=(\d+)")


def _tile_rgb(t):
    if t in TILE_RGB:
        return TILE_RGB[t]
    for k, v in TILE_RGB.items():  # prefix match (stone_path_d_se -> stone_path)
        if t.startswith(k):
            return v
    return DEFAULT_RGB


def load_zone(zone):
    """Return (terrain RGB array [H,W,3], tree pts, rock pts, spawn circles, W, H)."""
    zdir = os.path.join(ROOT, "nakama", "data", "zones", zone)
    z = json.load(open(os.path.join(zdir, "zone.json")))
    W, H = z.get("width", 256), z.get("height", 256)
    terr = np.full((H, W, 3), DEFAULT_RGB, dtype=float)
    trees, rocks = [], []
    for f in glob.glob(os.path.join(zdir, "chunk_*.json")):
        d = json.load(open(f))
        cx, cy = d["chunk_x"], d["chunk_y"]
        for ly, row in enumerate(d.get("ground", [])):
            if not isinstance(row, list):
                continue
            gy = cy * 32 + ly
            for lx, t in enumerate(row):
                gx = cx * 32 + lx
                if t and 0 <= gx < W and 0 <= gy < H:
                    terr[gy][gx] = _tile_rgb(t)
        for ly, row in enumerate(d.get("occupants", [])):
            if not isinstance(row, list):
                continue
            for lx, cell in enumerate(row):
                if not (isinstance(cell, dict) and cell.get("id")):
                    continue
                oid, gx, gy = cell["id"], cx * 32 + lx, cy * 32 + ly
                if oid.startswith("tree_"):
                    trees.append((gx, gy))
                elif any(k in oid for k in ("stone_block", "boulder", "rock", "ore", "stone_rubble")):
                    rocks.append((gx, gy))
    circles = [a for a in z.get("bug_spawning", {}).get("spawn_areas", []) if a.get("type") == "circle"]
    return terr, trees, rocks, circles, W, H


def backdrop(ax, terr, trees, rocks, circles, W, H, title):
    ax.imshow(terr, origin="lower", extent=(0, W, 0, H), interpolation="nearest")  # origin lower = NORTH up
    if trees:
        tx, ty = zip(*trees)
        ax.scatter(tx, ty, s=3, c="#3a7d34", alpha=0.5, edgecolors="none")
    if rocks:
        rx, ry = zip(*rocks)
        ax.scatter(rx, ry, s=4, c="#666666", alpha=0.6, edgecolors="none")
    for a in circles:
        sp = (a.get("species") or [""])[0]
        ax.add_patch(Circle((a["cx"], a["cy"]), a.get("radius", 6), fill=False,
                            ec=SP.get(sp, ("#999", ""))[0], alpha=0.35, lw=1.0))
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("← W   x   E →", fontsize=7); ax.set_ylabel("← S   y   N →", fontsize=7)
    ax.tick_params(labelsize=6)


def parse(log):
    days = {}
    for line in open(log, errors="ignore"):
        m = SNAP.search(line)
        if m:
            days.setdefault(int(m.group(1)), []).append(
                (m.group(2), float(m.group(3)), float(m.group(4)), int(m.group(5))))
    return days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log"); ap.add_argument("--zone", default="village_21_B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reference", action="store_true", help="just draw the backdrop (+ --mark points)")
    ap.add_argument("--mark", action="append", default=[], help="label:x,y points to mark (reference mode)")
    args = ap.parse_args()
    terr, trees, rocks, circles, W, H = load_zone(args.zone)

    if args.reference:
        fig, ax = plt.subplots(figsize=(11, 11))
        backdrop(ax, terr, trees, rocks, circles, W, H, f"{args.zone} — reference map (north up)")
        # coordinate grid every 32 (= one chunk) for reading off x,y
        for g in range(0, W + 1, 32):
            ax.axvline(g, color="k", alpha=0.12, lw=0.6); ax.axhline(g, color="k", alpha=0.12, lw=0.6)
        ax.set_xticks(range(0, W + 1, 32)); ax.set_yticks(range(0, H + 1, 32))
        # label each spawn circle with its id (so "what the circles mean" is on the map)
        for a in circles:
            ax.annotate(a["id"], (a["cx"], a["cy"]), fontsize=6, ha="center", va="center",
                        color=SP.get((a.get("species") or [""])[0], ("#555", ""))[0], alpha=0.8)
        for mk in args.mark:
            lbl, xy = mk.split(":"); x, y = (float(v) for v in xy.split(","))
            ax.scatter([x], [y], marker="X", s=170, c="red", edgecolors="k", zorder=5)
            ax.annotate(lbl, (x + 2, y + 2), fontsize=8, fontweight="bold", color="darkred", zorder=5)
        fig.tight_layout(); fig.savefig(args.out, dpi=110); print(f"wrote {args.out}")
        return

    days = parse(args.log)
    if not days:
        raise SystemExit(f"no SWARMSNAP in {args.log}")
    os.makedirs(args.out, exist_ok=True)
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=lbl) for c, lbl in SP.values()]
    daylist = sorted(days)
    for d in daylist:
        fig, ax = plt.subplots(figsize=(7, 7))
        backdrop(ax, terr, trees, rocks, circles, W, H, f"{args.zone} — game-day {d}")
        for sp, x, y, count in days[d]:
            ax.scatter([x], [y], s=10 + count * 2, c=SP.get(sp, ("#999", "?"))[0], alpha=0.8, edgecolors="white", lw=0.3)
        ax.legend(handles=handles, fontsize=6, loc="upper left", framealpha=0.7)
        fig.tight_layout(); fig.savefig(os.path.join(args.out, f"day_{d:02d}.png"), dpi=100); plt.close(fig)

    cols = min(4, len(daylist)); rows = math.ceil(len(daylist) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 4.2 * rows), squeeze=False)
    for i, d in enumerate(daylist):
        ax = axes[i // cols][i % cols]
        backdrop(ax, terr, trees, rocks, circles, W, H, f"day {d}")
        for sp, x, y, count in days[d]:
            ax.scatter([x], [y], s=6 + count * 1.5, c=SP.get(sp, ("#999", "?"))[0], alpha=0.8, edgecolors="none")
    for j in range(len(daylist), rows * cols):
        axes[j // cols][j % cols].axis("off")
    fig.suptitle(f"{args.zone} — bug distribution by game-day (north up)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.98)); fig.savefig(os.path.join(args.out, "_contact_sheet.png"), dpi=90)
    print(f"wrote {len(daylist)} day maps + _contact_sheet.png to {args.out}")


if __name__ == "__main__":
    main()
