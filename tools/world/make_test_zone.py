#!/usr/bin/env python3
"""Generate a small, self-contained test zone for headless / deterministic testing.

A test zone is an ordinary zone (real chunk files, loaded by the normal LoadChunk
path) — just small, and fully described by its zone.json. The zone config is the
single source of truth: `static` disables spawn/merge/split, `swarm_size` fixes the
bug count per swarm, and `seed` pins the world seed for reproducible runs.

This is the knob for making a test world, changing it, and scaling it up. To grow toward
production-like load (e.g. to reproduce a load-sensitive sync bug), just raise
--initial (swarm count) and re-run.

Examples
--------
  # default: the canonical sim_test zone (3x3 chunks, 1 fly swarm of 2 bugs)
  python3 tools/world/make_test_zone.py

  # scale up to 39 swarms to approach village_21 load
  python3 tools/world/make_test_zone.py --initial 39 --max 39

  # a bigger arena with a plant in it
  python3 tools/world/make_test_zone.py --zone-id sim_farm --chunks-w 4 --chunks-h 4 \
      --occupant compost_pile@70,70

  # the saves test pair (tools/harness_crash_test.sh, tools/run_crosstest.sh): two linked bug-free zones, a bed in
  # the first, test-only save knobs set with --set. Each holds back a departing player's save: persist_a 3 s (the next
  # zone is asked for first, so the server must wait), persist_b 10 s (past the server's 8 s wait, so the game is
  # told "busy" and must retry)
  python3 tools/world/make_test_zone.py --zone-id persist_a --name "Persistence test A" --chunks-w 2 --chunks-h 2 \
      --initial 0 --max 0 --row 0 --col 10 --neighbor east=persist_b --occupant bed_basic@48,50 \
      --set autosave_seconds=5 --set debug_leave_delay_ms=3000
  python3 tools/world/make_test_zone.py --zone-id persist_b --name "Persistence test B" --chunks-w 2 --chunks-h 2 \
      --initial 0 --max 0 --row 0 --col 11 --neighbor west=persist_a \
      --set autosave_seconds=5 --set debug_leave_delay_ms=10000

Output: nakama/data/zones/<zone-id>/zone.json + chunk_X_Y.json (one per chunk).
The Nakama server loads it via world_create {"zone_id": "<zone-id>"}.
"""
import argparse
import json
import os

CHUNK_SIZE = 32  # cells per chunk side; must match nakama world.ChunkSize


def build_chunk(cx, cy, base_tile, occupants_by_cell):
    """One chunk: 32x32 ground of base_tile, 32x32 occupants (null unless placed)."""
    ground = [[base_tile for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
    occupants = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
    for (gx, gy), occ_id in occupants_by_cell.items():
        if gx // CHUNK_SIZE == cx and gy // CHUNK_SIZE == cy:
            lx, ly = gx % CHUNK_SIZE, gy % CHUNK_SIZE
            occupants[ly][lx] = {"id": occ_id, "dir": 0, "anchor": True}
    return {"chunk_x": cx, "chunk_y": cy, "ground": ground, "occupants": occupants}


def build_zone_config(args, width, height):
    cx = args.spawn_cx if args.spawn_cx >= 0 else width // 2
    cy = args.spawn_cy if args.spawn_cy >= 0 else height // 2
    config = {
        "zone_id": args.zone_id,
        "name": args.name or f"Test Zone {args.zone_id}",
        "row": args.row,
        "col": args.col,
        "width": width,
        "height": height,
        "spawn_point": [cx, cy],
        "biome_type": "test",
        "seed": args.seed,
        "bug_spawning": {
            "static": not args.dynamic,
            "species_caps": {
                args.species: {
                    "initial": args.initial,
                    "max": max(args.max, args.initial),
                    "spawn_interval": 999999.0,
                    "swarm_size": args.swarm_size,
                }
            },
            "spawn_areas": [
                {
                    "id": "center",
                    "species": [args.species],
                    "type": "circle",
                    "cx": cx,
                    "cy": cy,
                    "radius": args.spawn_radius,
                }
            ],
        },
    }
    if args.neighbor:
        config["neighbors"] = parse_neighbors(args.neighbor)
    for key, value in parse_sets(args.set).items():
        config[key] = value
    return config


def parse_neighbors(specs):
    """['east=persist_b', ...] -> {'east': 'persist_b'}. A link must be added on BOTH zones, from opposite edges,
    and the two zones must sit next to each other on the world grid (--row/--col) — zone_links_test.go checks it."""
    out = {}
    for spec in specs:
        direction, _, zone_id = spec.partition("=")
        if direction not in ("north", "south", "east", "west") or not zone_id:
            raise SystemExit(f"--neighbor wants dir=zone_id with dir north/south/east/west, got {spec!r}")
        out[direction] = zone_id
    return out


def parse_sets(specs):
    """['autosave_seconds=5', ...] -> {'autosave_seconds': 5}. The value is JSON (a bare word becomes a string). For
    test-only zone.json fields the server reads, e.g. the saves crash test's autosave_seconds and debug_leave_delay_ms."""
    out = {}
    for spec in specs or []:
        key, _, raw = spec.partition("=")
        if not key:
            raise SystemExit(f"--set wants key=value, got {spec!r}")
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError:
            out[key] = raw
    return out


def parse_occupants(specs):
    """['compost_pile@70,70', ...] -> {(70,70): 'compost_pile'}. Single-cell only."""
    out = {}
    for spec in specs or []:
        occ_id, _, coords = spec.partition("@")
        gx, gy = (int(v) for v in coords.split(","))
        out[(gx, gy)] = occ_id
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--zone-id", default="sim_test", help="zone id / folder name (default: sim_test)")
    p.add_argument("--name", default="", help="display name (default: derived from zone-id)")
    p.add_argument("--chunks-w", type=int, default=3, help="chunks wide (default: 3 -> 96 cells)")
    p.add_argument("--chunks-h", type=int, default=3, help="chunks tall (default: 3 -> 96 cells)")
    p.add_argument("--base-tile", default="grass", help="ground tile id for every cell (default: grass)")
    p.add_argument("--species", default="fly_common", help="species id to spawn (default: fly_common)")
    p.add_argument("--initial", type=int, default=1, help="number of swarms spawned at init (default: 1)")
    p.add_argument("--max", type=int, default=1, help="zone-wide swarm cap (clamped >= initial)")
    p.add_argument("--swarm-size", type=int, default=2, help="fixed bugs per swarm (default: 2)")
    p.add_argument("--seed", type=int, default=1234, help="fixed world seed, 0 = random (default: 1234)")
    p.add_argument("--spawn-cx", type=int, default=-1, help="spawn-area center X in cells (default: zone center)")
    p.add_argument("--spawn-cy", type=int, default=-1, help="spawn-area center Y in cells (default: zone center)")
    p.add_argument("--spawn-radius", type=int, default=12, help="spawn-area radius in cells (default: 12)")
    p.add_argument("--dynamic", action="store_true", help="allow continuous spawn/merge/split (default: static)")
    p.add_argument("--occupant", action="append", default=[], help="place a single-cell occupant 'id@gx,gy' (repeatable)")
    p.add_argument("--row", type=int, default=0, help="world-grid row (row 0 is the north-most; default 0)")
    p.add_argument("--col", type=int, default=0, help="world-grid column (default 0)")
    p.add_argument("--neighbor", action="append", default=[], help="an edge link 'dir=zone_id' (repeatable)")
    p.add_argument("--set", action="append", default=[], help="an extra zone.json field 'key=json_value' (repeatable)")
    p.add_argument("--zones-dir", default=os.path.join("nakama", "data", "zones"), help="zones root directory")
    args = p.parse_args()

    width, height = args.chunks_w * CHUNK_SIZE, args.chunks_h * CHUNK_SIZE
    occupants_by_cell = parse_occupants(args.occupant)

    out_dir = os.path.join(args.zones_dir, args.zone_id)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "zone.json"), "w") as f:
        json.dump(build_zone_config(args, width, height), f, indent=2)

    for cy in range(args.chunks_h):
        for cx in range(args.chunks_w):
            chunk = build_chunk(cx, cy, args.base_tile, occupants_by_cell)
            with open(os.path.join(out_dir, f"chunk_{cx}_{cy}.json"), "w") as f:
                json.dump(chunk, f)

    n_chunks = args.chunks_w * args.chunks_h
    print(f"Wrote {out_dir}/: zone.json + {n_chunks} chunk(s), {width}x{height} cells")
    print(f"  static={not args.dynamic} seed={args.seed} "
          f"{args.species}: initial={args.initial} swarm_size={args.swarm_size}")
    print(f"Use it: world_create {{\"zone_id\": \"{args.zone_id}\"}}")


if __name__ == "__main__":
    main()
