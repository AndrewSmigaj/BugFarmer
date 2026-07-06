# Feature guide: tunnels, caves, water & ore (underground)

How to author UNDERGROUND space. Underground is the inverse of the surface: the world is **solid rock
you carve into**. The ground layer is `cave_floor` (revealed where rock is removed); the occupant layer
is mostly **blocks** (stone/dirt/ore) that the player mines. Module: `tools/zonegen/features/cave.py`.
Worked example: `tools/zonegen/scenes/scene_underground_caverns.py`.

> **Why this guide exists:** spatial reasoning is a weak spot — left alone an LLM carves a perfectly
> straight tunnel and a clean elliptical cavern, which read as artificial. The rules below are the
> nudges. Build with the primitives, then **look at the render and check against the "tells" in §5.**

## 1. Tunnels — natural MEANDER vs man-made STRAIGHT
- **Natural / burrowed / water-worn tunnels MEANDER.** Never a straight line. The primitive
  `carve_tunnel(b, start, end, style="natural")` walks from start toward end with **momentum**: it
  mostly keeps its heading, adds a small random **wobble** each step, and occasionally turns; width
  varies **1–3 cells**; it carves a little disk at each step so edges are organic. Burrowed tunnels
  (by creatures) wander MORE and may branch; water-worn ones are smoother but still curve.
  - **Tell:** if a "natural" tunnel runs straight for more than ~4 cells, it's wrong — re-seed or
    raise the wobble.
- **Man-made tunnels are STRAIGHT — and must SHOW why.** Straightness only reads as *intentional* when
  it carries infrastructure: a **rail track** (`mine_rail`) down the centre, **support timbers**
  (`mine_support`) at intervals, even width. Use `carve_tunnel(..., style="straight")` then lay the
  rail + supports. A straight bare tunnel just looks like a mistake.
- **Contrast them in the same scene** so the difference is legible (the demo scene runs a straight
  rail tunnel across the map past wandering burrowed tunnels).

## 2. Caverns & cave mouths
`carve_cavern(b, cx, cy, shape=..., size=N)` — carves a cavern of radius ≈ `size`, **never a clean circle**.
**(2026-06 rewrite)** It blends a soft radial mask with an **fBm noise field** (`noise_field`), thresholds it,
then runs a **cellular-automata smoothing** pass (the 4-5 rule) — the same recipe as the fixed lakes. The old
version unioned overlapping circles and read as **symmetric lobes**; this reads as a natural irregular void.
`shape` tunes elongation + edge roughness:
- **blob** — round-ish but noise-irregular (the default).
- **long / gallery** — an elongated, slightly curved chamber (a fat meander; delegates to `carve_tunnel`).
- **rocky / jagged** — a rougher edge **plus a few interior rock columns** left standing automatically.
- **lobed** — stretched on the x-axis into a peanut/clover outline.
Tune `size` + `seed` and re-render; the per-shape `rough` weight (in code) sets how irregular the outline is.
- **`carve_chamber(b, cx, cy, size, seed=)`** — when a single `carve_cavern` still reads too round, this
  unions **2–3 offset organic blobs along a random long axis** (kidney/peanut/lumpy voids). Prefer it for
  the caverns a player explores; `carve_cavern` is the building block.
- **Cave mouth** = a cavern positioned so it **clips the zone edge** (opens to the outside world); a
  cave is just a cavern that touches the surface. Put the entrance there.
- **Isolation is the point.** In a MINING zone, caverns are **not** tunnel-linked — the player mines to
  them. Only the man-made rail shaft is a pre-dug path. (Ant burrows through soft dirt are the exception —
  that's the colony's habitat.) Don't auto-connect caverns "for walkability"; that defeats mining.
Dress cavern **low spots with water** (§3), scatter crystals/mushrooms/rubble/bones, and leave a few
rock columns so the space isn't an empty bowl.

## 3. Underground water features
- **`cave_pool(b, cx, cy, size, carved, seed=)`** — the quality primitive (cf. `terrain.lake`): an
  IRREGULAR pool = a union of tilted blobs + concave **bays**, **clipped to the cavern's carved cells** so
  the waterline bows along the rock. `water_deep` core → `water_shallow` rim → a **shoreline re-derived by
  adjacency** dressed as a wet-rock bank (damp `mud` with gaps + scattered pebbles/moss). Seat it
  **off-centre** in a low corner, not dead-centre. NEVER a clean ellipse — the old `place_pool` (single
  ellipse) is deprecated for caverns.
- About **half** the caverns get a pool; vary `size` + `seed` so no two read alike.
- **Underground stream**: a thin (1–2 cell) **meandering** water channel following a tunnel — same
  wander rule as tunnels, never straight.
- Keep water OFF the man-made rail tunnel (built routes drain/avoid water).

## 4. Ore placement — rarity + gameplay
Ore is placed as **VEINS, not single specks**, so striking one gives a worthwhile haul.
`fill_solid(b, carved, ore_table, seed=, substrate=)` fills every non-carved cell with a block — ore in
random-walk veins **seeded on a jittered grid** (even coverage, no dead walls), `pockets` as clusters, the
rest the base block. Each vein tuple is `(id, count, lo, hi[, band])` with `band` in
`surface|top|mid|bottom|deep|any` (`deep` = the bottom FIFTH, the richest seam). Pass **`substrate(x, y) ->
block_id`** to paint the **Terraria depth model** (dirt at the surface → stone deep, with stone chunks IN the
dirt) — there is **one rock** you mine (`stone_block`); going deeper changes the floor tile + ore, not the
block. *(History: `hard_stone_block` was removed — a flat sprite AND a redundant idea.)*
- **Veins are runs of ~3–6 cells.** Commons get more veins; rares few short ones, concentrated `deep`.
- **Density + value RAMP with depth.** A baseline `any` tier keeps every band fed; the deep fifth is richest.
- **Gameplay tuning — MEASURE IT, don't eyeball.** Target **~13–16 % of solid rock** ore-bearing overall, the
  deep fifth **~20–25 %**, and — the metric that decides whether mining feels like a grind — **mean
  distance-to-nearest-ore ≈ 3–4 cells, ~75 % of rock within 5** (a 1-wide miner must keep striking ore). The
  ore-distribution probe in the zone work computes per-band % + a BFS dist-to-ore histogram; re-run it after
  any ore change. Long dead runs (p90 > ~10) = players quit.
- **Dirt pockets**: soft clustered patches (easy to mine), more common near the top/entrance.
- **The doctrine applies to SURFACE rock too — never hand-set ores, even "special" rares**
  (owner correction 2026-07-06, bee_meadow_20's gorge: "we have ore placement guides, you don't
  need to spread them out in such a linear fashion" — a hand-placed silver/gold/ruby line and a
  stepped row of bank stones both read as authored, not geological). Surface masses
  (`terrain.rock_mass`) take vein specs like `fill_solid`; texture banks with the mass's own
  apron/spill, not hand steps.
- **"Dirt areas" means DIRT-BLOCK MASSES, not painted ground** (owner correction 2026-07-06:
  "dirt areas actually mean dirt blocks"). A dirt AREA a player meets on the surface is a
  mineable body — `dirt_block` shell (shovel) around a `stone_block`/ore core (pickaxe) — with
  painted dirt only as the apron/lanes between masses. Terrain that only looks diggable but
  isn't is a broken promise.

### Per-zone ore table — `underground_passages_31` (beginning mining zone)
Each zone has its OWN table; read it, don't guess. `clay` is **by design only in some zones, NOT here.**

| material | role | placement |
|----------|------|-----------|
| `dirt_block` | soft surface soil (stone-speckled) | the surface band + the SW ant seam |
| `stone_block` | the one base rock | everywhere below the dirt |
| `ore_copper_block` / `ore_coal_block` | common ore/fuel | frequent, all depths |
| `ore_iron_block` | mid ore | frequent (the `any` baseline) |
| `ore_tin_block` | minor ore | mid band, sparse |
| `ore_silver_block` | precious | bottom + deep |
| `ore_gold_block` / `ore_platinum_block` / `ore_diamond_block` | rich/rare | **deep only** (bottom fifth) |

(No `clay_block`, no `hard_stone_block`. Deeper zones add more of the precious tiers + clay where designed.)

## 5. Build → render → review — the "tells" to check
```bash
python3 tools/zonegen/scenes/scene_underground_caverns.py
```
Read the PNG and verify:
- **No straight natural tunnels** (only the man-made one is straight, and it has rail + supports).
- **Caverns vary in shape** (not all round); rocky ones have interior columns; one clips the edge (mouth).
- **Ore is in findable veins**, not lone specks, at the measured density above (don't eyeball — run the probe).
- **Pools read irregular** (`cave_pool`: bayed waterline, deep core → shallow rim → wet-rock shore), never
  a clean ellipse, seated off-centre in the cavern; about half the caverns have one. Off the rail tunnel.
- `b.lint()` clean, **0 placement warnings**.

Cross-cutting: minerals/crystals use the **mineral** art family (set `"family": "mineral"` on the catalog
row) so they render as faceted rock, not plants — see `object_pipeline.md`. New objects: **add-object** skill.
Surface roads (the natural-vs-built distinction for ROADS) get their own guide later.
