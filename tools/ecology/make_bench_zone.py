#!/usr/bin/env python3
"""make_bench_zone.py — copy a real zone into a throwaway BENCH zone for measurement and tuning runs.

Why: `run_config.py` deletes the tested zone's saved state before every run (run_config.py wipe_zone_state). Run on
the real village, that would erase the village's live save. A bench copy has its own zone id, keeps no save
(`ephemeral_swarms: true`), has no neighbours, and is git-ignored (`nakama/data/zones/bench_*/`), so tests can't
touch real zones or bloat the repo. Regenerate it any time from the authored source zone.

  python3 tools/ecology/make_bench_zone.py                      # village_21_B -> bench_village
  python3 tools/ecology/make_bench_zone.py --source bee_meadow_20 --name bench_meadow
  python3 tools/ecology/make_bench_zone.py --tile 2 --name bench_village512   # the village tiled 2 x 2 -> 512 x 512
  python3 tools/ecology/make_bench_zone.py --tile 2 --bug-scale 0.3 --name bench_village512   # ... with 0.3 x the bugs
  python3 tools/ecology/make_bench_zone.py --tile 2 --bug-scale 0.28 --hold --name bench_village512   # the owner's walk

--tile N (Stage 1.5, docs/plans/village-slice.md) lays the source out N x N: every chunk file is copied into each tile
with its chunk coordinates shifted; the spawn circles and the starting carrion are repeated in every tile; the
per-zone species numbers (starting groups, maximums, population bands, nest count) are multiplied by N x N and the
top-up interval divided by it, so each tile behaves like the source zone. The spawn point stays in the first tile.

--bug-scale F multiplies those species numbers by F as well (and divides the interval by it): the same habitat with
fewer (F < 1) or more bugs, every species in the same proportion. Nest-staffed groups follow the authored nests, not F.

--hold turns on the zone's hold_population switch (zone.go): the starting count is kept — nothing is born after the
start and nothing dies of age or hunger, while hunting, predation and the player's actions still happen. For seeing a
given number of bugs in the zone, without the first day's mass starvation thinning it out.

Only ids starting with "bench_" can be written, and an existing bench folder is replaced only if its zone.json
says it is a bench zone.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "nakama/data/zones"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="village_21_B")
    ap.add_argument("--name", default="bench_village")
    ap.add_argument("--tile", type=int, default=1, help="lay the source out N x N (a 256 village -> 512 with 2)")
    ap.add_argument("--bug-scale", type=float, default=1.0, help="multiply the species numbers by F (fewer or more bugs)")
    ap.add_argument("--hold", action="store_true", help="hold the starting bug count (hold_population)")
    a = ap.parse_args()
    if a.tile < 1:
        sys.exit("--tile must be 1 or more")
    if a.bug_scale <= 0:
        sys.exit("--bug-scale must be above 0")
    if not a.name.startswith("bench_"):
        sys.exit("refusing: bench zone ids must start with 'bench_' (real zones are never written by this tool)")
    src, dst = ZONES / a.source, ZONES / a.name
    if not (src / "zone.json").exists():
        sys.exit(f"no source zone {src}")
    if dst.exists():
        old = json.loads((dst / "zone.json").read_text()) if (dst / "zone.json").exists() else {}
        if not old.get("bench_of"):
            sys.exit(f"refusing: {dst} exists and is not a bench zone")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    z = json.loads((dst / "zone.json").read_text())
    z.update({"zone_id": a.name, "name": f"Bench copy of {z.get('name', a.source)}", "bench_of": a.source,
              "row": 0, "col": 0, "ephemeral_swarms": True})
    z.pop("neighbors", None)
    if a.tile > 1:
        tile_zone(dst, z, a.tile)
    if a.bug_scale != 1.0:
        scale_species(z, a.bug_scale)
        z["bench_bug_scale"] = a.bug_scale
    if a.hold:
        z["hold_population"] = True
    (dst / "zone.json").write_text(json.dumps(z, indent=2))
    chunks = len(list(dst.glob("chunk_*.json")))
    print(f"{a.name}: copied {chunks} chunks from {a.source} (ephemeral, no neighbours, row/col 0,0"
          + (f", tiled {a.tile} x {a.tile} -> {z['width']} x {z['height']}" if a.tile > 1 else "")
          + (f", species numbers x {a.bug_scale}" if a.bug_scale != 1.0 else "")
          + (", count held" if a.hold else "") + ")")


# Per-zone species numbers scale with the area; the top-up interval shrinks with it (so each tile is topped up as often
# as the source zone). spawn_interval is in ticks.
SCALED_COUNTS = ("initial", "max", "max_population", "min_population", "event_low", "event_high", "max_nests")


def scale_species(z, f):
    """Multiply the per-zone species numbers by f (a count that was above 0 stays at least 1) and divide the top-up
    interval by it."""
    for cap in ((z.get("bug_spawning") or {}).get("species_caps") or {}).values():
        for k in SCALED_COUNTS:
            if isinstance(cap.get(k), (int, float)) and cap[k]:
                cap[k] = max(1, round(cap[k] * f)) if isinstance(cap[k], int) else cap[k] * f
        if isinstance(cap.get("spawn_interval"), (int, float)) and cap["spawn_interval"]:
            cap["spawn_interval"] = cap["spawn_interval"] / f


def tile_zone(dst, z, n):
    """Lay the copied zone out n x n in place: chunk files, zone size, spawn circles, starting carrion, species numbers."""
    w, h = z.get("width") or 256, z.get("height") or 256
    if w % 32 or h % 32:
        sys.exit(f"refusing to tile: {w} x {h} is not a whole number of 32-cell chunks")
    cw, ch = w // 32, h // 32
    originals = sorted(dst.glob("chunk_*.json"))
    for f in originals:
        chunk = json.loads(f.read_text())
        cx, cy = chunk["chunk_x"], chunk["chunk_y"]
        for ty in range(n):
            for tx in range(n):
                if tx == 0 and ty == 0:
                    continue
                chunk["chunk_x"], chunk["chunk_y"] = cx + tx * cw, cy + ty * ch
                (dst / f"chunk_{chunk['chunk_x']}_{chunk['chunk_y']}.json").write_text(json.dumps(chunk))
    z["width"], z["height"] = w * n, h * n
    z["bench_tiles"] = n
    scale_species(z, n * n)
    bs = z.get("bug_spawning") or {}
    areas, carrion = [], []
    for ty in range(n):
        for tx in range(n):
            for area in bs.get("spawn_areas") or []:
                if area.get("type") == "zone":
                    # A zone-wide area already covers every tile: kept once, its weight scaled with the circles' (which
                    # are repeated n x n), so the habitat-to-anywhere ratio stays the source zone's.
                    if tx == 0 and ty == 0:
                        a2 = dict(area)
                        a2["weight"] = (area.get("weight") or 1.0) * n * n
                        areas.append(a2)
                    continue
                a2 = dict(area)
                if "cx" in a2:
                    a2["cx"] += tx * w
                if "cy" in a2:
                    a2["cy"] += ty * h
                if tx or ty:
                    a2["id"] = f"{area.get('id', 'area')}_t{tx}{ty}"
                areas.append(a2)
            for c in bs.get("initial_carrion") or []:
                c2 = dict(c)
                c2["x"] = c2.get("x", 0) + tx * w
                c2["y"] = c2.get("y", 0) + ty * h
                carrion.append(c2)
    if bs.get("spawn_areas"):
        bs["spawn_areas"] = areas
    if bs.get("initial_carrion"):
        bs["initial_carrion"] = carrion


if __name__ == "__main__":
    main()
