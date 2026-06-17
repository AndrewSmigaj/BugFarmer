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

# --- pens across the top band (y 8..40), 4 AI species ---
pens = []  # (label, species, spawn_cx, spawn_cy, radius)

# Fly pen: compost bin (center) ringed by fast apple trees. Flies have vision 8 in a 32-wide pen, so
# food must be DENSE or they wander hungry and never top off to the breed point (the meadow needed the
# same density fix). An 8-tree ring keeps rotten fruit within a fly's vision almost everywhere.
fence_rect(8, 8, 40, 40, "fence_wood", gap=(24, 40))
place(24, 24, "compost_bin")
for (x, y) in [(14, 14), (24, 14), (34, 14),
               (14, 24), (34, 24),
               (14, 34), (24, 34), (34, 34)]:
    place(x, y, "tree_apple")  # REAL slow tree (rain-gated, ~7min/fruit) — not the fast test tree
pens.append(("fly_pen", "fly_common", 24, 22, 7))

# Butterfly pen: milkweed (host) + nectar flowers
fence_rect(48, 8, 80, 40, "fence_wood", gap=(64, 40))
for (x, y) in [(58, 18), (70, 20), (64, 30)]:
    place(x, y, "milkweed")
# A dense nectar meadow — butterflies feed on diffuse flowers, so they need several to reliably
# find one while foraging (a single sparse flower starves the pen).
for (x, y) in [(52, 12), (60, 14), (68, 14), (76, 12),
               (54, 22), (74, 22),
               (52, 34), (60, 36), (68, 36), (76, 34)]:
    place(x, y, "flower_wild")
pens.append(("butterfly_pen", "butterfly_meadow", 64, 24, 7))

# Wasp pen: stone walls (predator)
fence_rect(88, 8, 120, 40, "fence_stone", gap=(104, 40))
pens.append(("wasp_pen", "wasp_common", 104, 24, 7))

# Centipede pen: stone walls (it gnaws wood)
fence_rect(128, 8, 160, 40, "fence_stone", gap=(144, 40))
pens.append(("centipede_pen", "centipede_garden", 144, 24, 6))

# Arena = the open lower two-thirds (no fence) for staging drops.
# (millipede + aphid pens reserved; added when those species land.)

# HARD per-species BUG cap (max_population) = the crash-guard. The server mints ZERO bugs past it,
# no matter how much food a player supplies — food only paces how fast a pen climbs to the cap, and
# death/predators turn it over there. Without this, a renewable food source (milkweed) explodes a pen
# (butterflies hit 932 in the first long run). These are the test-pen ceilings; real zones set their own.
MAX_POP = {"fly_common": 150, "butterfly_meadow": 100, "wasp_common": 30, "centipede_garden": 20}
species_caps, spawn_areas = {}, []
for label, sp, cx, cy, r in pens:
    species_caps[sp] = {"initial": 2, "max": 12, "max_population": MAX_POP[sp], "spawn_interval": 999999.0, "swarm_size": 6}
    spawn_areas.append({"id": label, "species": [sp], "type": "circle", "cx": cx, "cy": cy, "radius": r})

# Millipede detritivore co-located in the FLY pen (compost bin at 24,24): the recycle loop —
# flies die of old age → carcasses → millipede eats them → compost bin fills → flies feed.
species_caps["millipede"] = {"initial": 2, "max": 4, "max_population": 20, "spawn_interval": 999999.0, "swarm_size": 1}
spawn_areas.append({"id": "fly_pen_millipede", "species": ["millipede"], "type": "circle", "cx": 24, "cy": 24, "radius": 6})

zone = {
    "zone_id": "bug_lab", "name": "Bug Lab", "row": 0, "col": 0,
    "width": W, "height": H, "spawn_point": [W // 2, H - 20],
    "biome_type": "test", "seed": 4242,
    # Run the sim 6x faster in wall-clock (sim-time fixed by SimRate) so a many-game-day ecology run
    # finishes in minutes. Balance-neutral; test zone only. Set 10 to compare at normal speed.
    "call_rate": 60,
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
