# Feature guide: vegetation / decoration scatter

How to fill open ground with weighted decor using `zonegen`'s `scatter` primitive. (New modular
guide — the per-biome scatter weights currently in `BIOME_PALETTES.md` are being folded in here;
see BACKLOG "Zone-design guides cleanup".)

## Primitive
```python
from features.scatter import scatter
scatter(b, x0, y0, x1, y1,
        {"flower_red": 3, "flower_blue": 3, "bush": 2, "sunflower": 1, "tall_grass": 2},
        density=0.10, min_spacing=2, seed=7, surfaces=("grass",))
```
- Places weighted decor on FREE cells of an allowed surface (default `grass`), keeping at least
  `min_spacing` between items, and **avoiding anything `reserved`** (water, roads, buildings, farms).
- `density` is the fraction of eligible cells to fill. Decor is NOT reserved (it's not an obstacle),
  so it never blocks other features — which is why **scatter runs LAST** in the precedence order.

## Design rules
- **Run scatter last**, after all hard features, so it just fills the leftover ground and can't
  displace anything.
- **Avoid the confetti look:** keep density modest (~0.05–0.15) and `min_spacing` ≥ 2; vary weights
  so a few species dominate and others accent, rather than an even sprinkle.
- **Clump for ecology/mood** by scattering in sub-regions with different weights (e.g. a denser
  flower patch near a pond, sparser toward paths) rather than one uniform pass over the whole zone.
- **Match the biome:** meadow → flowers + tall grass; forest understory → bushes + mushrooms;
  near water → reeds/flowers. (Per-biome weight tables: `BIOME_PALETTES.md`, being consolidated.)

## Interaction with other features
- Reads `reserved`/`surface`, so it inherently skips fences, paths, water, and building footprints —
  no trees in the pond, none on the road. Verify by rendering: scattered decor should sit only on
  open grass.

## Cross-cutting
Decor sprites follow `MASTER_STYLE_GUIDE.md`. Missing ones render as placeholders; track in
`art_needed.md`.
