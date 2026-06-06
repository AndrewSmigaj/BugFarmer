# Feature guide: yards & fences

Fenced enclosures around a house (or a pen/garden): a perimeter fence with an optional gate, an
approach path out of the gate, optional interior ground fill, and exterior decor. Module:
`tools/zonegen/features/yard.py`. Worked use: `tools/zonegen/scenes/scene_houses.py` (each house wrapped
in a yard) and `scene1_player_farm.py` (the fly pen / orchard use `fence_rect`).

Everything coordinates through the builder's occupancy model: fences are hard occupants (so later
`scatter` routes around them) and the approach path claims `surface="path"` (so scatter won't drop decor
on it).

## `fence_rect`
```python
from features.yard import fence_rect
fence_rect(b, x0, y0, x1, y1, gate=(15, 14))   # perimeter; that cell becomes a gate
```
Perimeter fence around the inclusive rect; if `gate=(x,y)` is given that cell is left open and a
`gate_wood` is placed there. `fence=`/`gate_id=` override the sprites. Returns the perimeter cells.

## `yard`
```python
from features.yard import yard
yard(b, x0, y0, x1, y1, gate=(gx, y0), path_to=(gx, y0 - 3),
     ground="dirt", decor=[("planter_box", x0+1, y0+1)])
```
- `gate` / `path_to`: leave a gate gap and lay an **L-shaped path** from the gate to `(x,y)`
  (`surface="path"`).
- `ground`: optional tile fill for the enclosed interior (e.g. `"dirt"` for a pen; omit for grass).
- `decor`: `[(oid, x, y), …]` occupants placed inside/around (planters, benches, lamp_post, hedge).

## Gotchas
- **Place dressing AFTER the fence**, and check `b.is_free(x, y)` then — checking *before* the fence is
  placed sees stale state and you'll drop lamps/signs onto the fence line (loud overlap warnings). In a
  scene, place flanking lamps/signs just OUTSIDE the south fence beside the path, or strictly inside.
- Wrap a house with `bbox(specs)` from `houses/layouts.py`: `yard(b, bx0-1, by0-1, bx1+1, by1+1, …)`.
- A rectangular yard around a ⊥/+ house encloses some empty grass corners — that's fine (it's a yard).

## Related primitives
- Paths/ponds: `features/terrain.py` (`hpath`, `vpath`, `pond`).
- Garden beds / collectible flowers / fallen fruit: `features/garden.py` (`crop_bed`, `flower_patch`,
  `fruit_around`).
- Houses + collections: [house-building.md](house-building.md). Scatter (vegetation): [feature-vegetation.md](feature-vegetation.md).
