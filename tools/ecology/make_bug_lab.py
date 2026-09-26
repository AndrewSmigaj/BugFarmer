#!/usr/bin/env python3
"""Generate the Bug Lab — a single-zone sandbox: a fenced pen per AI species
(+ feed/breed stations) and an open arena to stage cross-species interactions.

The iteration engine for the bug-ecology work: tune one species' AI in isolation,
or drop predators into a prey pen in the arena. Re-run to regenerate.

  python3 tools/ecology/make_bug_lab.py                  # build with the DEFAULT_LAB quantities
Output: nakama/data/zones/bug_lab/zone.json + chunk_X_Y.json

GEOMETRY (where pens/trees/flowers sit) is code; QUANTITIES (caps, Director bands, sim_batch,
per-species initial/max/swarm_size) are the `lab` config dict so the Phase-4c config sweep can vary
them without editing this file — `build_lab(lab)` takes that dict, `DEFAULT_LAB` is the baseline, and
`tools/ecology/run_config.py` deep-merges a delta over it. See docs/product/ecology/ecology_parameters.md.
"""
import json, os, copy

CHUNK = 32
CW, CH = 6, 6                 # 6x6 chunks -> 192x192 cells
W, H = CW * CHUNK, CH * CHUNK

# Fruit-tree MIX (different rates -> overlapping fruit waves -> a steadier fly-food supply than one
# boom-bust apple cycle). plum is fast (grow 600/drop 3000/5 fruit), cherry mid-fast (720/3600/6),
# apple slow (840/4200/4). All rain-gated; the Director's extra-rain keeps them watered when flies dip.
TREE_MIX = ["tree_plum", "tree_cherry", "tree_apple", "tree_cherry", "tree_plum", "tree_apple",
            "tree_cherry", "tree_plum"]

# ---------------------------------------------------------------------------
# DEFAULT_LAB — the baseline QUANTITIES. tools/bug_lab_configs/00_baseline.json mirrors these; a sweep
# config overrides individual keys (deep-merge). Keep this in sync with 00_baseline.json's "lab" block.
# ---------------------------------------------------------------------------
DEFAULT_LAB = {
    "call_rate": 60,   # 6x wall-clock (sim-time fixed by SimRate). Test zone only.
    "sim_batch": 8,    # 8 sim-ticks/Nakama call -> 48x total. Balance-neutral; test zone only.
    # seal_pens: close the player-entrance gap in every pen → each pen is a CLOSED ecosystem (no bugs
    # leak into the foodless open arena). Sweep-1 proved the predator FLOOR is structural: flies + wasps
    # leak out the gaps, so predator pens hold no sustained prey (centipede→fly = 0 kills even at fly=100
    # global). Sealing contains each predator with its own prey. Headless tuning only (no player needs in).
    "seal_pens": False,
    # HARD per-species BUG cap (max_population) = the crash-guard. The server mints ZERO bugs past it;
    # food only paces how fast a pen climbs. Without it a renewable food source explodes a pen.
    "max_pop": {"fly_common": 150, "butterfly_meadow": 100, "wasp_common": 40,
                "centipede_garden": 30, "millipede": 30, "beetle_carrion": 20,
                "bee_honey": 40},
    # Ecology Director — THREE-TIER bands per species (ecology_director.go). Natural dynamics own the
    # middle [event_low..event_high]; the Director acts only at the edges, gentlest-first: re-seed
    # (extreme low) / extra-rain (moderate low) / DROUGHT (moderate high) / hard cull (extreme high).
    # Invariant: min < event_low < event_high < cull_at < max_population. cull_at:0 disables the cull.
    "director": {
        "fly_common":       {"min_population": 8,  "event_low": 25, "event_high": 90, "cull_at": 120, "cull_with": "wasp_common"},
        "butterfly_meadow": {"min_population": 12, "event_low": 18, "event_high": 45, "cull_at": 80},
        "wasp_common":      {"min_population": 6,  "cull_at": 32, "max_nests": 3},
        "centipede_garden": {"min_population": 5,  "cull_at": 24},
        "millipede":        {"min_population": 3,  "cull_at": 24},
        "beetle_carrion":   {"min_population": 2,  "cull_at": 16},
        # Bees: min_population 0 = the Director NEVER reseeds — the D-phase gate is that the
        # colony is SELF-maintained via the nest economy (b_nest births only, b_reseed 0).
        "bee_honey":        {"min_population": 0,  "cull_at": 0, "max_nests": 4},
    },
    # Per-species spawn-cap fields (merged onto every species_cap). swarm_size/initial/max only.
    "caps": {
        "fly_common":       {"initial": 2, "max": 12, "swarm_size": 6},
        "butterfly_meadow": {"initial": 2, "max": 12, "swarm_size": 6},
        "wasp_common":      {"initial": 2, "max": 12, "swarm_size": 6},
        "centipede_garden": {"initial": 2, "max": 12, "swarm_size": 6},
        "millipede":        {"initial": 2, "max": 8,  "swarm_size": 1},
        "beetle_carrion":   {"initial": 2, "max": 4,  "swarm_size": 1},
        "bee_honey":        {"initial": 0, "max": 12, "swarm_size": 4},  # nest-founded only, never free-spawned
    },
}


def build_lab(lab):
    """Build the bug_lab zone from a `lab` quantities dict (DEFAULT_LAB shape). Geometry is fixed here;
    only the caps/bands/sim_batch come from `lab`. Writes zone.json + chunk_X_Y.json under
    nakama/data/zones/bug_lab/. Returns the zone dict."""
    occ = {}  # (gx, gy) -> occupant id
    seal = lab.get("seal_pens", False)

    def pen_gap(x, y):
        return None if seal else (x, y)  # sealed → no entrance gap (closed-ecosystem pens)

    def place(gx, gy, oid):
        if 0 <= gx < W and 0 <= gy < H:
            occ[(gx, gy)] = oid

    def fence_rect(x0, y0, x1, y1, fid, gap=None):
        """Perimeter fence of [x0..x1] x [y0..y1] inclusive; `gap`=(gx,gy) left open as an entrance."""
        cells = set()
        for x in range(x0, x1 + 1):
            cells.add((x, y0)); cells.add((x, y1))
        for y in range(y0, y1 + 1):
            cells.add((x0, y)); cells.add((x1, y))
        if gap:
            cells.discard(gap)
        for (x, y) in cells:
            place(x, y, fid)

    def tree_ring(cx, cy):
        """A compost bin (center) ringed by 8 fruit trees of mixed rates + 4 inner trees — the dense
        fly-food pattern. Flies have vision 8 in a 32-wide pen, so food must be DENSE or they wander
        hungry and never top off to the breed point."""
        place(cx, cy, "compost_bin")
        ring = [(-10, -10), (0, -10), (10, -10), (-10, 0), (10, 0), (-10, 10), (0, 10), (10, 10)]
        for i, (dx, dy) in enumerate(ring):
            place(cx + dx, cy + dy, TREE_MIX[i % len(TREE_MIX)])
        for i, (dx, dy) in enumerate([(-5, -5), (5, -5), (-5, 5), (5, 5)]):  # inner ring, denser canopy
            place(cx + dx, cy + dy, TREE_MIX[(i + 1) % len(TREE_MIX)])

    pens = []          # (label, species, spawn_cx, spawn_cy, radius) — sets the species cap + spawn area
    extra_spawns = []  # extra spawn areas for an already-capped species

    # Fly pen: prey + recycle loop. Flies eat rotten fruit (compost bin + tree ring). The MILLIPEDE eats
    # its OWN food — leaf_litter piles — so it does NOT compete with the flies. The carrion BEETLE eats
    # dead_<bug> corpses.
    fence_rect(8, 8, 40, 40, "fence_wood", gap=pen_gap(24, 40))
    tree_ring(24, 24)
    for (x, y) in [(16, 16), (32, 16), (16, 24), (32, 24), (16, 32), (32, 32)]:
        place(x, y, "leaf_litter")  # millipede detritus food (separate from the flies' rotten fruit)
    pens.append(("fly_pen", "fly_common", 24, 22, 7))

    # Butterfly pen: milkweed (host) + nectar flowers. Fewer milkweed/flowers makes them FOOD-limited so
    # they oscillate below the cap and the Director's drought tier can engage.
    fence_rect(48, 8, 80, 40, "fence_wood", gap=pen_gap(64, 40))
    for (x, y) in [(64, 24)]:
        place(x, y, "milkweed")  # 1 host plant (breeding bottleneck)
    for (x, y) in [(54, 14), (74, 34)]:
        place(x, y, "flower_wild")  # 2 nectar flowers — nectar-scarce
    pens.append(("butterfly_pen", "butterfly_meadow", 64, 24, 7))

    # Wasp arena: predator-prey loop. Flies feed on the fruit-tree ring; a wasp_nest anchors the resident
    # patrol (HomePos/homing-breed + seeds nest-splitting). Stone walls.
    fence_rect(88, 8, 120, 40, "fence_stone", gap=pen_gap(104, 40))
    tree_ring(104, 24)
    place(104, 16, "wasp_nest")
    pens.append(("wasp_pen", "wasp_common", 104, 16, 5))
    extra_spawns.append(("wasp_pen_prey", "fly_common", 104, 30, 8))

    # Centipede arena: pure hunter (hunts flies; breeds via the well-fed timer). Stone walls.
    fence_rect(128, 8, 160, 40, "fence_stone", gap=pen_gap(144, 40))
    tree_ring(144, 24)
    pens.append(("centipede_pen", "centipede_garden", 144, 16, 6))
    extra_spawns.append(("centipede_pen_prey", "fly_common", 144, 30, 8))

    # Decomposer guild, co-located in the FLY pen (densest food). Millipede on leaf_litter; beetle on
    # dead_<bug> corpses (old-age fly deaths here are its steady supply).
    extra_spawns.append(("fly_pen_millipede", "millipede", 24, 20, 6))
    extra_spawns.append(("fly_pen_beetle", "beetle_carrion", 24, 28, 6))

    # BEE ARENA (second row): the beekeeping loop under observation. A wild hive auto-founds its
    # colony (initial spawns 0 — the nest IS the population source); a dense flower cluster on the
    # west side is the nectar economy; a raider WASP NEST sits just OUTSIDE the east wall, across
    # the pen gap — wasps don't fly over fences, so the gap at (56,68) is their raid corridor into
    # the colony (their prey list includes bee_honey). Gate bands: bees self-maintained via b_nest
    # (b_reseed 0 — the Director can't reseed bees), honey accrues on deposits, raids don't extinct.
    fence_rect(8, 48, 56, 88, "fence_wood", gap=pen_gap(56, 68))
    for (x, y) in [(14, 58), (20, 58), (26, 60), (14, 66), (20, 66),
                   (26, 70), (14, 76), (20, 76), (26, 78)]:
        place(x, y, ["flower_wild", "flower_red", "flower_blue", "flower_yellow"][(x + y) % 4])
    place(34, 68, "bee_hive_wild")
    place(64, 68, "wasp_nest")  # the raiders' base, outside the wall, facing the gap

    # --- assemble species_caps from the lab quantities ---
    max_pop, director, caps = lab["max_pop"], lab["director"], lab["caps"]
    species_caps, spawn_areas = {}, []
    for label, sp, cx, cy, r in pens:
        c = {"max_population": max_pop[sp], "spawn_interval": 999999.0}
        c.update(caps.get(sp, {}))
        c.update(director.get(sp, {}))
        species_caps[sp] = c
        spawn_areas.append({"id": label, "species": [sp], "type": "circle", "cx": cx, "cy": cy, "radius": r})
    # decomposers + bees (no free-spawn pen of their own — decomposers spawn via extra_spawns;
    # bees are founded entirely by their nest, so they get a cap entry and NO spawn area)
    for sp in ("millipede", "beetle_carrion", "bee_honey"):
        c = {"max_population": max_pop[sp], "spawn_interval": 999999.0}
        c.update(caps.get(sp, {}))
        c.update(director.get(sp, {}))
        species_caps[sp] = c
    for label, sp, cx, cy, r in extra_spawns:
        spawn_areas.append({"id": label, "species": [sp], "type": "circle", "cx": cx, "cy": cy, "radius": r})

    zone = {
        "zone_id": "bug_lab", "name": "Bug Lab", "row": 0, "col": 0,
        "width": W, "height": H, "spawn_point": [W // 2, H - 20],
        "biome_type": "test", "seed": 4242,
        # Always start fresh from `initial` (don't restore the prior run) so tuning runs are comparable.
        "ephemeral_swarms": True,
        "call_rate": lab["call_rate"],
        "sim_batch": lab["sim_batch"],
        "bug_spawning": {"static": False, "species_caps": species_caps, "spawn_areas": spawn_areas},
    }

    out = os.path.join("nakama", "data", "zones", "bug_lab")
    os.makedirs(out, exist_ok=True)
    json.dump(zone, open(os.path.join(out, "zone.json"), "w"), indent=2)
    for cy in range(CH):
        for cx in range(CW):
            ground = [["grass"] * CHUNK for _ in range(CHUNK)]
            occs = [[None] * CHUNK for _ in range(CHUNK)]
            for (gx, gy), oid in occ.items():
                if gx // CHUNK == cx and gy // CHUNK == cy:
                    occs[gy % CHUNK][gx % CHUNK] = {"id": oid, "dir": 0, "anchor": True}
            json.dump({"chunk_x": cx, "chunk_y": cy, "ground": ground, "occupants": occs},
                      open(os.path.join(out, f"chunk_{cx}_{cy}.json"), "w"))

    print(f"wrote {out}/  ({W}x{H}, {len(pens)} pens, {len(occ)} occupants, sim_batch={lab['sim_batch']})")
    print("  pens:", ", ".join(f"{l}={sp}" for l, sp, *_ in pens))
    return zone


if __name__ == "__main__":
    build_lab(copy.deepcopy(DEFAULT_LAB))
