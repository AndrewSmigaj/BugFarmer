# Feature guide: ant colonies & trails (underground)

How to author an ant nest — a worked example for the "creatures shape the underground too" idea, and the
first **trail-system** guide (other trail/swarm behaviours will reuse the ideas). Worked example:
`tools/zonegen/scenes/scene_ant_colony.py`. Needs nothing but **blocks + ant sprites** (`ant_worker`,
`ant_queen`, `ant_mound` already exist).

## The shape of a nest
An ant nest is a **tree of narrow tunnels descending from a surface entrance into chambers** dug through
soil. Build it as:
- **Soil, not bedrock.** Fill the solid rock mostly with `dirt_block` and a minority of `stone_block`
  (ants dig earth) — no ore veins.
- **Entrance:** an `ant_mound` at the surface (top edge) over the mouth of the main shaft.
- **Main shaft:** a single **narrow (1-cell), meandering** tunnel dropping from the entrance toward the
  deep **queen's chamber**. Narrow + wandering = dug by a creature (same rule as natural cave tunnels,
  but thinner — never straight).
- **Branches:** short narrow tunnels off the shaft to **chambers** — small rounded rooms (2–4 cells
  across). Vary their purpose: the **queen's chamber** (largest, deepest/central), **brood chambers**,
  **food stores**. A nest branches like a root system.

## Trails = files of ants (the key visual)
Ants must read as **marching columns**, not random scatter:
- Place `ant_worker` along a tunnel's **ordered centerline**, evenly spaced (~every 2 cells) with a tiny
  jitter, so they form a **file** following the tunnel. The **main shaft is busy** (a steady column);
  **side branches carry a few**.
- The **`ant_queen`** sits in the queen's chamber; **2–3 workers tend each chamber**.
- Density rule of thumb: a worker roughly every 2 cells on the main trail, every 3–4 on branches.

## Build → render → review — the tells
```bash
python3 tools/zonegen/scenes/scene_ant_colony.py
```
- Ants follow the tunnels as **columns** (you can trace the trail), not a random sprinkle.
- The nest **branches like a tree** from one surface entrance; chambers are distinct rounded rooms.
- Tunnels are **narrow + wandering** (never straight); soil (dirt) dominates over stone.
- `b.lint()` clean (0 defects), 0 placement warnings.

## Iteration learnings (from building the example — keep these)
- **Bug sprites are tiny (≈8×8, sized for in-game swarms).** At scale ≈1 they vanish on the dark tunnel
  floor. In a PREVIEW, place trail ants at `scale≈2.4` (queen ≈3.2) so the column reads. (In-game the
  ants move and are seen close-up, so they don't need this.)
- **A long shaft drifts straight** unless you weaken the goal pull: use `bias≈0.16` + `wobble≈0.7` for the
  main shaft (higher bias = straighter). Branches can use the default.
- Ants on dark floor are still lowish-contrast even scaled up — acceptable for layout review; a future
  lighter "trail ant" preview variant (or a preview highlight) would read better.

## Notes
- Bug *sprites* exist already; this scene places them with `place_bug` (free-floating, sub-grid). A
  proper colony in-game (queen laying, workers pathing the trails) is gameplay for later.
- If the trail/file + branching-tunnel logic settles, promote it to `features/ant.py`
  (`dig_nest`, `ant_file`). For generic cave tunnels/caverns see [caves.md](caves.md).
- Segmented bugs SHIPPED with the predator slice (centipede head/body/tail sprites +
  the CentipedeTrail display chain) — the pattern is reusable for millipedes.
