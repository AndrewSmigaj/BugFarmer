# Our current grass — how it works today + why it reads worse (verified)

Stage-2 study of our own grass (companion to the external research). All claims verified against the real code
/ assets this pass.

## The assets
- `BugFarmerClient/Assets/Resources/Tiles/grass.png`, `grass_v2.png`, `grass_v3.png` — all **32×32 RGBA**.
- Viewed: all three are **near-uniform flat green with faint speckle noise** — NO blades, tufts, clumps,
  directional detail, or internal structure. `grass.png` = mid-green speckle; `v2` = flatter darker; `v3` =
  brighter/yellower. They read as a flat green fill, not "grass."

## How a ground tile renders (verified — `TileDatabase.cs:45-93`)
`GetGroundTile(tileId)` → `Resources.Load<Texture2D>("Tiles/{tileId}")` → one `Sprite.Create` → one `Tile`
(`color = Color.white`), **cached by id**. So:
- **Every cell with id `grass` gets the SAME single sprite.** No per-cell variation.
- **No variant selection** — `grass_v2`/`grass_v3` are never chosen (only ref is a stray comment in
  `LitMaterials.cs:85`). We have 3 variants and use 1.
- **No autotiling** — it's a plain `Tile`, not a Unity `RuleTile`; no context-aware edges.
- The only tile sophistication is the **composite shaped-ground** system (`matA~matB~shape`,
  `TileCompositor` / `architecture_shaped_ground.md`) — used where the shovel places blended ground; plain
  grass fields don't use it.

## Detail layer today
- Grass-detail OCCUPANTS exist: `tall_grass`, `fern`, `bush`, `flower_wild/red/blue/yellow/aster`, `clover`,
  `dandelion`, `mushroom_*` (`nakama/data/entities/occupants.json`).
- Placed by `tools/zonegen/features/scatter.py` — drops weighted decor onto free grass cells. But in practice
  it's **sparse** (e.g. `scene1_player_farm.py`: density ~0.25-0.28 mixed mostly with trees/bushes), so there's
  no dense grass-blade/tuft carpet — just occasional props on a flat field.
- **No wind/animation on ground grass** (the `LitMaterials` "wind-swaying foliage" path is for occupant
  sprites like trees, not the ground tile).

## Why ours reads worse than Stardew / Necesse (the diagnosis)
1. **One flat tile, repeated identically** → obvious tiling, a green carpet. (No variation.)
2. **The tile art has no grass texture** — flat noise, no blades/clumps to catch the eye.
3. **No transitions** — grass meets dirt/path/water at hard tile edges (except shovel composites); no fringe/
   overhang of grass into neighbors.
4. **No dense detail layer** — tufts/flowers are sparse decor, not a lush overlay.
5. **Static** — no wind sway, no react-to-walk, nothing alive.

## Levers we already have (reuse, don't reinvent)
- Runtime tile creation from PNGs (`TileDatabase`) — easy to extend to variant selection.
- The composite/shader tile pipeline (`TileCompositor`, `TileComposite.shader`) — proof we can do runtime GPU
  tile work + custom shaders (a wind/color shader is feasible here).
- The scatter system (`scatter.py`) + existing detail occupants — a denser, better-tuned grass-detail pass is a
  config/data change, not new tech.
- The art pipeline (gpt-image + `pixelclean`) to author better grass tiles + tuft/detail sprites.

_(This is the "our side." The external research — `games_*.md`, `techniques_*.md` — provides how good games
solve 1-5; the `synthesis.md` + the plan combine them.)_
