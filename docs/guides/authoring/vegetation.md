# Feature guide: vegetation / decoration scatter

How to fill open ground with weighted decor using `zonegen`'s `scatter` primitive. (New modular
guide — the per-biome scatter weights currently in `BIOME_PALETTES.md` are being folded in here;
see BACKLOG "Zone-design guides cleanup".)

## Primitive
```python
from features.scatter import scatter
scatter(b, x0, y0, x1, y1,
        {"flower_red": 3, "flower_blue": 3, "bush": 2, "sunflower": 1, "tall_grass": 2},
        density=0.10, min_spacing=2, seed=7, surfaces=("grass",),
        clumping=0.0, cluster_radius=4)
```
- Places weighted decor on FREE cells of an allowed surface (default `grass`), keeping at least
  `min_spacing` between items, and **avoiding anything `reserved`** (water, roads, buildings, farms).
- `density` is the fraction of eligible cells to fill. Decor is NOT reserved (it's not an obstacle),
  so it never blocks other features — which is why **scatter runs LAST** in the precedence order.
- **`clumping`** (0 = uniform/even; 0.7–0.95 = natural): gathers decor into PATCHES with bare ground
  between, and each patch leans toward one species — how real wildflowers/bushes grow. Same total
  count, distributed organically instead of evenly. `cluster_radius` sets patch size (cells).
  **Default to `clumping≈0.85` for meadow/forest ground** — even scatter reads as stamped.

## Design rules
- **Run scatter last**, after all hard features, so it just fills the leftover ground and can't
  displace anything.
- **Avoid the confetti look:** keep density modest (~0.05–0.15), vary weights so a few species
  dominate and others accent, and **use `clumping`** so it patches instead of sprinkling evenly.
- **Clump for ecology/mood:** `clumping` makes organic patches in one pass; layer it with
  sub-region passes (a denser flower patch near a pond, sparser toward paths) for extra control.
- **Match the biome:** meadow → flowers + tall grass; forest understory → bushes + mushrooms;
  near water → reeds/flowers. (Per-biome weight tables: `art/BIOME_PALETTES.md`, being consolidated.)

## EVERYTHING snaps to the grid except BUGS
- **One grid cell per placed thing.** Trees, plants, flowers, crops — the player plants/places them, so
  they are real grid OCCUPANTS (`place_occupant`, integer cells), and they're saved to the zone. Only
  **bugs** are free-floating/sub-grid (they move). `flower_patch` plants flowers on the grid;
  `place_decor` (sub-grid) is for non-grid dressing only (fallen fruit pickups, lily pads on water).
- **Trees are grid-aligned but their sprite is ~2 cells tall** — scatter them with **`min_spacing` ≥ 3**
  (modest `density`, ~0.15) so the tall sprites don't overlap into a solid mass. Put trees in **clumps in
  the open, where there are no houses** (a yard gets at most a couple of back-corner trees).

## Interaction with other features
- Reads `reserved`/`surface`, so it inherently skips fences, paths, water, and building footprints —
  no trees in the pond, none on the road. Verify by rendering: scattered decor should sit only on
  open grass.

## Cross-cutting
Decor sprites follow `art/MASTER_STYLE_GUIDE.md`. Missing ones render as placeholders; track in
`art_needed.md`.
