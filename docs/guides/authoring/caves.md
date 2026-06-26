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
- **Cave mouth** = a cavern positioned so it **clips the zone edge** (opens to the outside world); a
  cave is just a cavern that touches the surface. Put the entrance there.
Dress cavern **low spots with water** (§3), scatter crystals/mushrooms/rubble/bones, and leave a few
rock columns so the space isn't an empty bowl.

## 3. Underground water features
- **Still pools** in cavern low areas: `water_deep` core, `water_shallow` rim; reserve as `water`.
- **Underground stream**: a thin (1–2 cell) **meandering** water channel following a tunnel — same
  wander rule as tunnels, never straight.
- Keep water OFF the man-made rail tunnel (built routes drain/avoid water).

## 4. Ore placement — rarity + gameplay
Ore is placed as **VEINS, not single specks**, so striking one gives a worthwhile haul.
`fill_solid(b, carved, ore_table, seed=, substrate=)` fills every non-carved cell with a block — ore in short
**random-walk veins**, `pockets` as clusters, the rest the base block. Pass **`substrate(x, y) -> block_id`**
to paint **dirt-left / rock-right / hard-stone-deep regions** (the dirt↔rock interface): e.g. the mining camp
makes the left third `dirt_block` (where the ant tunnels reach in) blending into `stone_block`, and
`hard_stone_block` deep. *(History note: this was once `scatter_ore`; the carve→fill flow is now one call.)*
- **Veins are runs of ~3–6 cells.** Commons get more (and slightly longer) veins; rares get few short ones.
- **Rarity tiers** (relative vein counts): **common** (copper, coal) — frequent; **uncommon** (iron) —
  fewer; **rare** (tin, silver) — sparse, short, scattered deeper.
- **Gameplay tuning:** aim for roughly **12–18 % of the solid rock** ore-bearing — enough that a player
  mining a tunnel keeps hitting commons (no 10-minute dig for one patch), but with plain stone between
  veins so it isn't ore-everywhere. Tune by eye in the render; we can rebalance.
- **Dirt pockets**: soft clustered patches (easy to mine), more common near the top/entrance.

### Per-zone ore table (the spatial nudge — pass this to `scatter_ore`)
Each zone has its OWN table; an LLM should read it, not guess. `clay` is **by design only in some zones,
NOT the beginning mining zone.**

`underground_passages_31` — beginning mining zone:

| material | role | rarity |
|----------|------|--------|
| `dirt_block` | soft pockets | common (near entrance) |
| `stone_block` | base rock | everywhere (the default) |
| `ore_copper_block` | common ore | common |
| `ore_coal_block` | common ore/fuel | common |
| `ore_iron_block` | mid ore | uncommon |
| `ore_tin_block` | minor ore | rare (tiny bits) |
| `ore_silver_block` | minor precious | rare (tiny bits) |
| `hard_stone_block` | tougher rock (needs better pick) | uncommon, more to the south/deep |

(No `clay_block` here. Deeper zones add iron→silver→gold→platinum→diamond and clay where designed.)

## 5. Build → render → review — the "tells" to check
```bash
python3 tools/zonegen/scenes/scene_underground_caverns.py
```
Read the PNG and verify:
- **No straight natural tunnels** (only the man-made one is straight, and it has rail + supports).
- **Caverns vary in shape** (not all round); rocky ones have interior columns; one clips the edge (mouth).
- **Ore is in findable veins**, not lone specks, at a density that looks minable-but-not-everywhere.
- **Water reads as pools** (deep core, shallow rim), not stray puddles, and avoids the rail tunnel.
- `b.lint()` clean, **0 placement warnings**.

Cross-cutting: minerals/crystals use the **mineral** art family (set `"family": "mineral"` on the catalog
row) so they render as faceted rock, not plants — see `object_pipeline.md`. New objects: **add-object** skill.
Surface roads (the natural-vs-built distinction for ROADS) get their own guide later.
