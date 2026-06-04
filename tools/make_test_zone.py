#!/usr/bin/env python3
"""Generate a small, self-contained test zone for headless / deterministic testing.

A test zone is an ordinary zone (real chunk files, loaded by the normal LoadChunk
path) — just small, and fully described by its zone.json. The zone config is the
single source of truth: `static` disables spawn/merge/split, `swarm_size` fixes the
bug count per swarm, and `seed` pins the world seed for reproducible runs.

This is the knob for "make a test world / change it / scale it up". To grow toward
production-like load (e.g. to reproduce a load-sensitive sync bug), just raise
--initial (swarm count) and re-run.

Examples
--------
  # default: the canonical sim_test zone (3x3 chunks, 1 fly swarm of 2 bugs)
  python3 tools/make_test_zone.py

  # scale up to 39 swarms to approach village_21 load
  python3 tools/make_test_zone.py --initial 39 --max 39

  # a bigger arena with a plant in it
  python3 tools/make_test_zone.py --zone-id sim_farm --chunks-w 4 --chunks-h 4 \
      --occupant compost_pile@70,70

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
    return {
        "zone_id": args.zone_id,
        "name": args.name or f"Test Zone {args.zone_id}",
        "row": 0,
        "col": 0,
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
