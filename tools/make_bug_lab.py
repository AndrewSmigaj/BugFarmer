#!/usr/bin/env python3
"""Generate the Bug Lab — a single-zone sandbox: a fenced pen per AI species
(+ feed/breed stations) and an open arena to stage cross-species interactions.

The iteration engine for the bug-ecology work: tune one species' AI in isolation,
or drop predators into a prey pen in the arena. Re-run to regenerate.

  python3 tools/make_bug_lab.py
Output: nakama/data/zones/bug_lab/zone.json + chunk_X_Y.json
"""
import json, os

CHUNK = 32
CW, CH = 6, 6                 # 6x6 chunks -> 192x192 cells
W, H = CW * CHUNK, CH * CHUNK

occ = {}                      # (gx, gy) -> occupant id

def place(gx, gy, oid):
    if 0 <= gx < W and 0 <= gy < H:
        occ[(gx, gy)] = oid

def fence_rect(x0, y0, x1, y1, fid, gap=None):
    """Perimeter fence of [x0..x1] x [y0..y1] inclusive; `gap`=(gx,gy) cell left
    open as a player entrance (no occupant -> always passable)."""
    cells = set()
    for x in range(x0, x1 + 1):
        cells.add((x, y0)); cells.add((x, y1))
    for y in range(y0, y1 + 1):
        cells.add((x0, y)); cells.add((x1, y))
    if gap:
        cells.discard(gap)
    for (x, y) in cells:
        place(x, y, fid)

# --- pens across the top band (y 8..40) ---
pens = []          # (label, species, spawn_cx, spawn_cy, radius) — sets the species cap + a spawn area
extra_spawns = []  # extra spawn areas for an already-capped species (prey/detritivore co-spawns in a pen)

# Fruit-tree MIX (different rates -> overlapping fruit waves -> a steadier fly-food supply than one
# boom-bust apple cycle). plum is fast (grow 600/drop 3000/5 fruit), cherry mid-fast (720/3600/6),
# apple slow (840/4200/4). All rain-gated; the Director's extra-rain keeps them watered when flies dip.
TREE_MIX = ["tree_plum", "tree_cherry", "tree_apple", "tree_cherry", "tree_plum", "tree_apple",
            "tree_cherry", "tree_plum"]

def tree_ring(cx, cy):
    """A compost bin (center) ringed by 8 fruit trees of mixed rates + 4 inner trees — the dense fly-food
    pattern. Flies have vision 8 in a 32-wide pen, so food must be DENSE or they wander hungry and never
    top off to the breed point. 12 trees of overlapping rates keep rotten fruit within a fly's vision
    almost everywhere and lift the prey base enough to feed the predators."""
    place(cx, cy, "compost_bin")
    ring = [(-10, -10), (0, -10), (10, -10), (-10, 0), (10, 0), (-10, 10), (0, 10), (10, 10)]
    for i, (dx, dy) in enumerate(ring):
        place(cx + dx, cy + dy, TREE_MIX[i % len(TREE_MIX)])
    for i, (dx, dy) in enumerate([(-5, -5), (5, -5), (-5, 5), (5, 5)]):  # inner ring, denser canopy
        place(cx + dx, cy + dy, TREE_MIX[(i + 1) % len(TREE_MIX)])

# Fly pen: prey + recycle loop. Flies eat rotten fruit (compost bin + tree ring). The MILLIPEDE here eats
# its OWN food — leaf_litter piles (a depletable detritus pool, like flower nectar) — so it does NOT
# compete with the flies for rotten fruit. The carrion BEETLE eats dead_<bug> corpses.
fence_rect(8, 8, 40, 40, "fence_wood", gap=(24, 40))
tree_ring(24, 24)
for (x, y) in [(16, 16), (32, 16), (16, 24), (32, 24), (16, 32), (32, 32)]:
    place(x, y, "leaf_litter")  # millipede detritus food (separate from the flies' rotten fruit)
pens.append(("fly_pen", "fly_common", 24, 22, 7))

# Butterfly pen: milkweed (host) + nectar flowers
fence_rect(48, 8, 80, 40, "fence_wood", gap=(64, 40))
# Butterflies were pinning their hard cap (food too rich -> they out-bred the cull). Fewer milkweed
# (breeding host) + fewer flowers (nectar) makes them FOOD-LIMITED so they oscillate below the cap and
# the Director's drought tier can engage. (The "remove some flowers, spread them less" lever.)
for (x, y) in [(64, 24)]:
    place(x, y, "milkweed")  # 1 host plant (breeding bottleneck — holds butterflies below the cap)
for (x, y) in [(54, 14), (74, 34)]:
    place(x, y, "flower_wild")  # 2 nectar flowers — nectar-scarce so butterflies food-limit at ~30-40
pens.append(("butterfly_pen", "butterfly_meadow", 64, 24, 7))

# Wasp arena: a predator–prey loop. Flies (prey) feed on the fruit-tree ring; a wasp_nest anchors the
# resident patrol (its HomePos/homing-breed loop AND seeds Phase 3 nest-splitting). Wasps hunt + EAT flies
# (prey consumed, no corpse). Stone walls (predator pen).
fence_rect(88, 8, 120, 40, "fence_stone", gap=(104, 40))
tree_ring(104, 24)
place(104, 16, "wasp_nest")
pens.append(("wasp_pen", "wasp_common", 104, 16, 5))
extra_spawns.append(("wasp_pen_prey", "fly_common", 104, 30, 8))

# Centipede arena: predator + prey. The centipede is a pure hunter (hunts flies; breeds via the well-fed
# timer). Stone walls (it gnaws wood).
fence_rect(128, 8, 160, 40, "fence_stone", gap=(144, 40))
tree_ring(144, 24)
pens.append(("centipede_pen", "centipede_garden", 144, 16, 6))
extra_spawns.append(("centipede_pen_prey", "fly_common", 144, 30, 8))

# Arena = the open lower two-thirds (no fence) for staging drops.

# HARD per-species BUG cap (max_population) = the crash-guard. The server mints ZERO bugs past it,
# no matter how much food a player supplies — food only paces how fast a pen climbs to the cap, and
# death/predators turn it over there. Without this, a renewable food source (milkweed) explodes a pen
# (butterflies hit 932 in the first long run). These are the test-pen ceilings; real zones set their own.
MAX_POP = {"fly_common": 150, "butterfly_meadow": 100, "wasp_common": 40, "centipede_garden": 30}
# Ecology Director — THREE-TIER bands per species (ecology_director.go). Natural dynamics own the middle
# [event_low..event_high]; the Director only acts at the edges, gentlest-first: re-seed (extreme low) /
# extra-rain (moderate low) / DROUGHT (moderate high) / hard cull (extreme high). Rain is one global, so
# relief beats suppression. The prey species (fly) carry the event bands; predators/detritivore get just
# a re-seed FLOOR (the "come back" guarantee) + a ceiling — their food is prey/carrion, governed by the
# fly bands. Invariant: min < event_low < event_high < cull_at < max_population.
DIRECTOR = {
    # Prey base: thin fly food is rain-gated, so below event_low the Director makes it RAIN (more fruit
    # -> more fly food -> flies + predators recover). A fly boom past cull_at releases wasps.
    "fly_common":       {"min_population": 8,  "event_low": 25, "event_high": 90, "cull_at": 120, "cull_with": "wasp_common"},
    # Nectar/host-driven: bounded by FOOD, not the cull. 1 milkweed limits births; few flowers limit nectar
    # feeding; and a DROUGHT slashes nectar/host regen (droughtFoodRegenMult) so butterflies ebb naturally.
    # event_high 45 → intermittent drought when they spike; cull_at 80 is a far last resort (rarely fires).
    "butterfly_meadow": {"min_population": 12, "event_low": 18, "event_high": 45, "cull_at": 80},
    # Predators + detritivore: re-seed floor (anti-extinction "come back") + ceiling. The wasp can also
    # SPLIT into new hives (max_nests). Raised ceilings/floors to grow the predator + decomposer numbers.
    "wasp_common":      {"min_population": 6,  "cull_at": 32, "max_nests": 3},
    "centipede_garden": {"min_population": 5,  "cull_at": 24},
    "millipede":        {"min_population": 3,  "cull_at": 24},
    "beetle_carrion":   {"min_population": 2,  "cull_at": 16},
}
species_caps, spawn_areas = {}, []
for label, sp, cx, cy, r in pens:
    species_caps[sp] = {"initial": 2, "max": 12, "max_population": MAX_POP[sp], "spawn_interval": 999999.0, "swarm_size": 6}
    species_caps[sp].update(DIRECTOR.get(sp, {}))
    spawn_areas.append({"id": label, "species": [sp], "type": "circle", "cx": cx, "cy": cy, "radius": r})

# Decomposer guild, co-located in the FLY pen (densest food for each). The MILLIPEDE is a plant
# detritivore — it eats the rotten fruit under the tree ring (competes a little with the flies). The
# carrion BEETLE eats dead_<bug> corpses — flies dying of OLD AGE here are its steady supply (predation
# elsewhere consumes prey, so old-age/starvation deaths are the only carrion). Beetle composts corpses →
# fly food, closing the recycle loop. Spawn areas come from extra_spawns below.
species_caps["millipede"] = {"initial": 2, "max": 8, "max_population": 30, "spawn_interval": 999999.0, "swarm_size": 1}
species_caps["millipede"].update(DIRECTOR.get("millipede", {}))
species_caps["beetle_carrion"] = {"initial": 2, "max": 4, "max_population": 20, "spawn_interval": 999999.0, "swarm_size": 1}
species_caps["beetle_carrion"].update(DIRECTOR.get("beetle_carrion", {}))
extra_spawns.append(("fly_pen_millipede", "millipede", 24, 20, 6))
extra_spawns.append(("fly_pen_beetle", "beetle_carrion", 24, 28, 6))

# Extra prey/detritivore spawn areas inside the predator arenas (species already capped above — these
# add spawn points without touching the cap): flies as wasp/centipede prey, the millipede on carrion.
for label, sp, cx, cy, r in extra_spawns:
    spawn_areas.append({"id": label, "species": [sp], "type": "circle", "cx": cx, "cy": cy, "radius": r})

zone = {
    "zone_id": "bug_lab", "name": "Bug Lab", "row": 0, "col": 0,
    "width": W, "height": H, "spawn_point": [W // 2, H - 20],
    "biome_type": "test", "seed": 4242,
    # Always start fresh from the `initial` spawns (don't restore the prior run's saved population) so
    # tuning runs are reproducible + comparable. Test zone only.
    "ephemeral_swarms": True,
    # Run the sim 6x faster in wall-clock (sim-time fixed by SimRate) so a many-game-day ecology run
    # finishes in minutes. Balance-neutral; test zone only. Set 10 to compare at normal speed.
    "call_rate": 60,
    # Advance 8 sim-ticks per Nakama call → 48× wall-clock total (call_rate is capped at 60). A 120s
    # harness run now covers ~7 game-days. Test zone only; balance-neutral (same tick sequence, faster).
    "sim_batch": 8,
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

print(f"wrote {out}/  ({W}x{H}, {len(pens)} pens, {len(occ)} occupants)")
print("  pens:", ", ".join(f"{l}={sp}" for l, sp, *_ in pens))
