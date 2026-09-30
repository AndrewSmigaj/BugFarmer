# Diagonal / rounded edges on player-laid ground — techniques + interface research

Research date: 2026-09-29. Written incrementally (appended after each technique).
Question: which techniques and interface designs let a 2D square-grid game show nice diagonal or rounded
edges on player-laid ground (paths, roads, floors), and let the player control the shape when they want to,
without confusing them?

Markers: [SRC] = confirmed from a source I read in full (URL given). [CODE] = read in real source code.
[REPO] = verified in our own repo (file:line). [INF] = my inference. [UNSURE] = could not confirm from a source.

## 0. Our starting point (verified in the repo, read-only)
- Unity **6000.2.9f1** (`BugFarmerClient/ProjectSettings/ProjectVersion.txt`); packages include
  `com.unity.2d.tilemap` 1.0.0 and **`com.unity.2d.tilemap.extras` 5.0.1** (`Packages/manifest.json` lines 9-10). [REPO]
- Ground IS drawn on Unity's Tilemap: `TilemapManager.SetGroundTile` -> `groundTilemap.SetTile(tilePos, tile)`
  one cell at a time (`Assets/Scripts/World/TilemapManager.cs` ~line 1011); a second Tilemap mirrors water for the
  animated overlay. **Correction:** the older research note
  `docs/product/investigations/grass-overhaul/techniques_autotiling_transitions.md` says "we are NOT on Unity's
  Tilemap" — that is wrong; we are. [REPO]
- Current shape system: ground id per cell is a string; shaped cell = `matA~matB~shape`, shapes = full,
  diagNE/NW/SE/SW, halfN/S/E/W, quadNE/NW/SE/SW (`World/Rendering/TileCompositor.cs` lines 25-30, masks
  lines 134-148), composited on the GPU into one 32x32 tile and cached by id; server/save treat the id as opaque
  (`docs/product/architecture/architecture_shaped_ground.md`). Grass has 5 hash-picked variants
  (`VariantTileId`). [REPO]
- So "the player picks 1 of 12 shapes + 2 materials per cell" is what the owner found awkward.

## 1. Autotiling families (how a tile is picked, art cost, diagonals)

Sources deep-read: Boris the Brave "Classification of Tilesets" (https://www.boristhebrave.com/2021/11/14/classification-of-tilesets/);
the cr31 blob page mirror (https://www.boristhebrave.com/permanent/24/06/cr31/stagecast/wang/blob.html); Boris
"Quarter-Tile Autotiling" (https://www.boristhebrave.com/2023/05/31/quarter-tile-autotiling/); Wikipedia "Marching squares"
(https://en.wikipedia.org/wiki/Marching_squares); SpriteCook "Dual-grid tilesets, explained"
(https://www.spritecook.ai/blog/dual-grid-tilesets-explained); Excalibur.js "Dual Tilemap Autotiling Technique"
(https://excaliburjs.com/blog/Dual%20Tilemap%20Autotiling%20Technique/).
Weak source noted, NOT relied on: https://www.redblobgames.com/articles/autotile/claude/ says "Written 2026. Inspired by
Red Blob Games" at a /claude/ URL — it reads as an AI-written experiment, not Amit Patel's own article. [SRC]

### 1a. 4-neighbour (cardinal) mask — 16 tiles
- Picks a tile from which of N/E/S/W hold the same material (4 bits -> 16). Boris calls the edge-matched family
  "S-E2" (16 tiles). It cannot tell an inner corner from a full tile (it never looks at diagonals), so fields get
  blocky inner corners. Good for fences / linear things, weak for ground. [SRC Boris classification]
- Diagonal edges: no. [INF]

### 1b. 16-tile corner set (2-corner Wang) = marching squares = the dual grid's tileset
- The value lives on the tile's 4 CORNERS (vertices). Boris: S-V2 = "store a value on each vertex" with "one of two
  things": **16 tiles without symmetry, 6 with rotation**. [SRC Boris classification]
- Marching squares builds the same 4-bit index from the 4 corners ("walk around the cell ... appending the bit") and
  looks the case up in a 16-entry table; cases 5 and 10 (opposite corners) are the ambiguous "saddle" cases, which
  can be resolved by "the average data value for the center of the cell". Without interpolation the contour crosses
  each cell edge at its MIDPOINT. [SRC Wikipedia]
- With 3 terrains on the corners it explodes: S-V3 = **81 tiles (22 with rotation+mirroring)**. [SRC Boris]
- **Diagonals: YES, for free — this is the key finding.** [INF, checked by arithmetic] If the ground value sits on the
  cell and the rendered tile sits on the corner where 4 cells meet (the dual grid), a staircase of filled cells
  {y <= x} crosses the display edges at (i, i+0.5) and (i-0.5, i) for every i — all on the single line y = x + 0.5.
  So when the one-corner and three-corner tiles are drawn as straight 45-degree cuts through edge midpoints, **a
  staircase the player lays reads as one straight 45-degree edge** (each boundary cell shows 7/8, each outside cell
  1/8). If the same tiles are drawn as quarter-circle arcs, the staircase reads as a gently scalloped curve and a
  rectangle gets rounded corners. Straight edges still sit exactly on the cell lines (the midpoint between two cell
  centres is the shared cell edge), so a rectangle keeps its exact size — only its corners are cut, by at most half
  a cell. Boris states the matching limit: "you cannot make swooping curves of radius larger than half the size of a
  tile". [SRC Boris quarter-tile, for the limit]
- Two cells touching only at a corner = the saddle tile (mask 9 / 6). SpriteCook: "Two cells touching at a corner. On
  the dual grid, the rendered tile sitting between them samples one filled cell at its top-left and one at its
  bottom-right." Excalibur gives it its own "diagonal" sprite (index 3, rotated 0 or 90). The ART decides whether a
  diagonal chain of single cells joins into a thin 45-degree band (about 0.7 cell wide) or stays as separate
  diamonds. [SRC SpriteCook, Excalibur]

### 1c. 47-tile blob set
- Looks at all 8 neighbours. cr31 weights: "North edge = 1, NorthEast corner = 2, East edge = 4, SouthEast corner = 8,
  South edge = 16, [SouthWest] corner = 32, West edge = 64, NorthWest corner = 128" (256 combinations); the rule that
  shrinks it: a corner only counts when both edges beside it are filled (cr31: "If either corner is yellow then the
  edge centre is yellow"; Boris: "if either of the edges of a corner are empty, then the corner must also be empty"),
  leaving **47 tiles** (48 with the empty one). [SRC cr31, Boris]
- **Diagonals: effectively no.** [INF, checked by hand] At a staircase cell, N and W are empty while NE and SW are
  filled; at the top-left corner of a rectangle, N, W, NE and SW are all empty. The 47-reduction throws NE and SW
  away whenever N or W is empty, so both cases get the SAME tile. The blob set cannot draw a staircase as a diagonal
  without also chamfering every rectangle corner by a full half-cell triangle; telling them apart needs the full 256.
- Art cost is the highest (47 tiles per material, per pair of materials if they blend).

### 1d. Quarter-tiles (RPG Maker style "mini-tiles")
- Each cell is drawn as 4 quarter pieces; each quarter is chosen from the cell's own material plus the 3 cells at that
  corner (2 sides + the diagonal). Boris: **5 half-size pieces with rotation, 14-20 without**. [SRC Boris]
- Same corner shapes as the dual grid but drawn per cell, so a per-cell setting (e.g. "keep this cell square") can
  still steer its 4 quarters. [INF]
- Boris on several terrains: "There's no obvious extension for quarter tiles"; in practice people either overlap
  separate autotilings with transparency, or draw tiles per terrain pair and pick the two most prominent terrains per
  quarter. [SRC Boris quarter-tile]

## 2. The dual-grid method (Stålberg; jess::codes; open-source implementations)

### 2a. Oskar Stålberg's original argument (primary source: his thread's slides)
- Tweet (https://x.com/OskSta/status/1448248658865049605, text fetched via the fxtwitter API): "More talk prep. Gonna
  have another go at persuading people to cut their tiles along the dual grid instead of the main grid. I genuinely
  don't understand if this is rare because people don't know about it or if there is some drawback I'm not seeing."
  Follow-up (https://x.com/OskSta/status/1448265809269338117): "You should definitely keep both concepts around in
  your code. Most gameplay will still happen on the main grid. The dual grid is mostly for field-like background
  tilesets". [SRC]
- His three slide images (downloaded + viewed, gr_code/osk1-4 in my scratchpad):
  - "Inward blob cut" (the usual per-cell cut): "Concave corners have to be sharp and narrow; convex corners can be
    nice and round."
  - "Outward blob cut": the reverse — concave round, convex sharp.
  - "On the dual": "All corners can be nice and round!!" — the whole square set is 6 tiles with rotation (empty, one
    corner, half, two opposite corners, three corners, full); on a triangle grid "very few permutations needed" (4).
  - "Main grid & dual grid": both grids live together — the material lives on the main-grid cell, the art is cut on
    the dual grid. [SRC]
- Why this matters to us: ground is exactly his "field-like background tileset", and our gameplay (placing, digging,
  walking, crops) stays on the main grid, unchanged. [INF]

### 2b. jess::codes (Jess Hammer) — the Unity reference implementation [CODE]
Repo: https://github.com/jess-hammer/dual-grid-tilemap-system-unity (Unity 2023.1; a Godot twin exists at
https://github.com/jess-hammer/dual-grid-tilemap-system-godot). README: "It does NOT use `RuleTiles` directly ... It uses
a custom script with hard-coded 'rules'"; reasons: "it allows the tiles to have perfectly rounded corners", "a maximum
of only 16 tiles ... as opposed to 47 (and you could cut that number further down to just 6 if your tiles have
symmetry)", "the tiles are not ambiguous for the player, in that each 'dirt' or 'grass' aligns with the world grid";
"I haven't done any performance testing so no promises"; a RuleTile version "did become quite convoluted".
The core tile choice (`Assets/Scripts/DualGridTilemap.cs`, quoted verbatim):
```csharp
protected static Vector3Int[] NEIGHBOURS = new Vector3Int[] {
    new Vector3Int(0, 0, 0), new Vector3Int(1, 0, 0),
    new Vector3Int(0, 1, 0), new Vector3Int(1, 1, 0) };
...
{new (Dirt, Grass, Grass, Dirt), tiles[14]}, // DUAL_UP_RIGHT   (the two saddle cases get their own tiles)
{new (Grass, Dirt, Dirt, Grass), tiles[4]},  // DUAL_DOWN_RIGHT
...
protected Tile calculateDisplayTile(Vector3Int coords) {
    // 4 neighbours
    TileType topRight = getPlaceholderTileTypeAt(coords - NEIGHBOURS[0]);
    TileType topLeft  = getPlaceholderTileTypeAt(coords - NEIGHBOURS[1]);
    TileType botRight = getPlaceholderTileTypeAt(coords - NEIGHBOURS[2]);
    TileType botLeft  = getPlaceholderTileTypeAt(coords - NEIGHBOURS[3]);
    Tuple<TileType, TileType, TileType, TileType> neighbourTuple = new(topLeft, topRight, botLeft, botRight);
    return neighbourTupleToTile[neighbourTuple];
}
protected void setDisplayTile(Vector3Int pos) {
    for (int i = 0; i < NEIGHBOURS.Length; i++) {
        Vector3Int newPos = pos + NEIGHBOURS[i];
        displayTilemap.SetTile(newPos, calculateDisplayTile(newPos));
    }
}
```
So: changing one world cell re-picks exactly 4 display tiles; each display tile reads 4 world cells. Only 2
materials (Grass/Dirt) — a 16-entry dictionary keyed on the 4-tuple.

### 2c. skner.DualGrid (Unity package, RuleTile-based) [CODE]
Repo: https://github.com/skner-dev/skner.DualGrid (80 stars, last push 2026-04-20). One `DualGridTilemapModule` =
a Data Tilemap + a Render Tilemap offset by (-0.5,-0.5); it listens to `Tilemap.tilemapTileChanged` and refreshes the
4 render tiles. The render tile is `DualGridRuleTile : RuleTile<DualGridNeighbor>` with neighbour states
`Filled = 1` / `NotFilled = 2`; its `RuleMatches` override checks the 4 data cells under a render cell
(`Runtime/Tiles/DualGridRuleTile.cs` lines 126-142; positions from `DualGridUtils.GetDataTilePositions`:
`renderTilePosition - (0,0)`, `-(1,0)`, `-(0,1)`, `-(1,1)`). It is binary per module ("filled or not"), so several
materials = several stacked modules. Useful as proof that Unity's RuleTile machinery (incl. Random output) can drive
a dual grid.

### 2d. TileMapDual (Godot addon) [SRC README]
https://github.com/pablogila/TileMapDual — "real-time, in-editor and in-game dual-grid tileset system"; "Only 15
tiles are required for autotiling, instead of 47"; "if your tiles are symmetrical, you can get away with drawing
only 6"; square, isometric and hex grids; for several materials: "To use more than two terrain types, it is highly
encouraged to use multiple TileMapDual layers." Also recommends separate "display" and "world" tiles.

### 2e. How the dual grid handles the three hard cases
- **Corners:** convex AND concave corners can both be round (Stålberg). Radius limit = half a cell (Boris). [SRC]
- **Diagonals:** see 1b — a staircase of cells becomes a straight 45-degree edge if the corner tiles are drawn as
  chamfers through edge midpoints; a corner-to-corner chain uses the saddle tile, whose art decides "joined band" vs
  "separate". This is automatic: the player never picks a shape. [INF from the geometry + SRC for the saddle tile]
- **Several materials:** the dual grid itself is 2-state. Every implementation found handles more materials by
  STACKING one dual-grid layer per material (skner: one module per tile; TileMapDual: "multiple TileMapDual
  layers"; Boris: "overlapping separate autotilings with transparency"), i.e. a priority order decides which edge
  draws over which. Doing it in one tile needs 3+-state corner sets, which explode (3 materials = 81 tiles). [SRC]
- **Tile count:** 15 drawn + empty per material (6 if the material may be rotated). For 6 materials, stacked:
  ~6 x 15 = 90 tiles, versus pairwise transition sets (15 pairs x 15 = 225) or 47-blob per pair. [SRC counts; INF sum]

### 2f. Things to watch
- The display tile at a chunk seam needs cells from BOTH chunks. Our chunks load lazily, so an edge tile must be
  re-picked when the neighbour chunk arrives (same idea as our shore mask's "unloaded" state). [REPO + INF]
- Rotation shortcuts (6 tiles) suit hard man-made materials; organic ground pinwheels visibly if rotated — draw
  all 15. (Carried from the earlier grass note; I did not re-verify a source for the "pinwheel" claim.) [UNSURE]
- Stålberg's own open question ("some drawback I'm not seeing"): the one real one for us is that the rendered
  outline no longer hugs the grid exactly at corners, so where a cell ends at a corner is slightly less obvious. Our
  cursor/ghost must show the CELL, not the rounded art. [INF]

## 3. Unity 6's own tools (we run Unity 6000.2.9f1 + 2D Tilemap Extras 5.0.1)

Sources: Rule Tile manual (https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@5.0/manual/RuleTile.html),
Custom Rules manual (https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@5.0/manual/CustomRulesForRuleTile.html),
`Tilemap.SetTiles` reference (https://docs.unity3d.com/6000.2/Documentation/ScriptReference/Tilemaps.Tilemap.SetTiles.html),
RuleTile source (https://github.com/Unity-Technologies/2d-extras, `Runtime/Tiles/RuleTile/RuleTile.cs`, 829 lines).
- **Rule Tile:** a 3x3 neighbour grid, each neighbour "Don't Care" / "This" / "Not This"; extended neighbours
  possible; rules are tried in order ("the Rule Tile algorithm will check the first Rule first"); a rule can match
  rotated (the 3x3 box "will be rotated 90 degrees each time the Rule fails to match") or mirrored; output Single,
  Random (Perlin noise of the position) or Animation. [SRC manual]
- **The core matching code** (RuleTile.cs, verbatim):
```csharp
public override void GetTileData(Vector3Int position, ITilemap tilemap, ref TileData tileData) {
    ...
    foreach (TilingRule rule in m_TilingRules) {
        if (RuleMatches(rule, position, tilemap, ref transform)) {
            switch (rule.m_Output) {
                case TilingRuleOutput.OutputSprite.Single:
                case TilingRuleOutput.OutputSprite.Animation:
                    tileData.sprite = rule.m_Sprites[0]; break;
                case TilingRuleOutput.OutputSprite.Random:
                    int index = Mathf.Clamp(Mathf.FloorToInt(GetPerlinValue(position, rule.m_PerlinScale, 100000f)
                                * rule.m_Sprites.Length), 0, rule.m_Sprites.Length - 1);
                    tileData.sprite = rule.m_Sprites[index]; ...
            }
            ... break;   // first matching rule wins
        } } }
public virtual bool RuleMatch(int neighbor, TileBase other) {
    if (other is RuleOverrideTile ot) other = ot.m_InstanceTile;
    switch (neighbor) {
        case TilingRuleOutput.Neighbor.This: return other == this;
        case TilingRuleOutput.Neighbor.NotThis: return other != this;
    }
    return true;
}
```
  So out of the box a Rule Tile only knows "same asset or not". Several materials need a subclass
  (`RuleTile<T>` with custom neighbour constants + `RuleMatch` override; the manual's own example is a "siblings"
  list). `RefreshTile` also refreshes neighbours, so a runtime `SetTile` updates the surrounding tiles by itself. [CODE]
- **Runtime placement:** Tilemap `SetTile`/`SetTiles` work at runtime (we already call `SetTile` per cell). The
  `SetTiles` page offers array and `TileChangeData[]` overloads but does NOT state a speed difference [SRC]; that
  batching is faster is common advice only [UNSURE]. Per edit, a dual grid touches 4 display tiles (x layers).
- **Multiplayer:** the Tilemap is purely a client-side picture. Only the per-cell material id travels (as it does
  today); each client derives the art from the ids with a pure function, so every client shows the same edges with
  nothing extra to sync — as long as any random variant uses the cell position (RuleTile's Perlin-of-position does;
  our `VariantTileId` hash does). [CODE + REPO + INF]
- **Fit:** Rule Tile = a good fit for single-material autotiles made in the editor; for a dual grid with 6 materials
  and player overrides, a small custom script (jess-style, ~100 lines) or a custom `TileBase` whose `GetTileData`
  reads OUR cell data is simpler than bending Rule Tile, and it stays on Unity's Tilemap renderer. [INF, echoed by
  jess: RuleTile version "became quite convoluted"]

## 4. Several materials meeting — priority / layering

### 4a. Don't Starve Together (the closest analogue: players dig up turf and lay it tile by tile) [CODE]
Source: DST's shipped Lua scripts, public mirror https://github.com/penguin0616/dst_gamescripts
(`tiledefs.lua`, `tilemanager.lua`, `worldtiledefs.lua`; the C++ renderer itself is closed).
- `tiledefs.lua` line 93: `--these are done in RENDER order` — every ground type is registered in one global list,
  and the list order is the draw order (impassable, then ocean, then land tiles).
- Every ground type MUST name its own edge shape: `assert(ground_tile_def.noise_texture, "ground_tile_def must contain
  a noise_texture")` (`tilemanager.lua` ~line 94). Natural turfs use ragged noise (`noise_texture="Ground_noise_dirt"`,
  `"Ground_noise_marsh"`), the cobblestone ROAD uses `noise_texture = "images/square.tex"` (a hard square edge), and
  WOODFLOOR uses `name="blocky", noise_texture="noise_woodfloor"` with `flooring = true, hard = true`.
- Modders can move one type relative to another: `ChangeRenderOrder(tilegroup, tile_id, target_tile_id, moveafter)`
  removes the entry and re-inserts it before/after the target.
- Lesson: ONE global priority list + a per-MATERIAL edge style (ragged for nature, square for road, "blocky" for
  floors). The player never picks an edge — the material carries it. How exactly the engine blends with the noise
  texture is not visible in Lua. [UNSURE on the renderer internals]

### 4b. Factorio [SRC]
Official prototype docs (https://lua-api.factorio.com/latest/prototypes/TilePrototype.html): `layer` "Specifies
transition drawing priority ... the final layer is computed as `layer_group + layer`"; tiles also define
`transitions` and `transitions_between_transitions` (special art for where transitions themselves meet). Same idea:
a number per material decides whose edge draws over whose.

### 4c. Stardew Valley player floors & paths [SRC]
Stardew modding docs for `Data/FloorsAndPaths` (https://stardewvalleywiki.com/Modding:Floors_and_Paths): the MATERIAL
sets its connection style, the player does not. `ConnectType`: "Default: For normal floors, intended to cover large
square areas. This uses some logic to draw inner corners"; "Path: For floors intended to be drawn as narrow paths.
These are drawn without any consideration for inner corners"; "CornerDecorated: For floors that have a decorative
corner. Use CornerSize to change the size"; "Random: For floors that don't connect". `ShadowType`: None / Square /
Contoured. Whether a Stardew path joins a DIFFERENT path type is not stated. [UNSURE]
Stardew's base maps are painted by hand in a map editor, so their grass/dirt edges are authored, not computed.
[UNSURE — inferred from the map-layer modding model; no page says it outright]

### 4d. Tiled's terrain brush (editor tool, for contrast) [SRC]
https://doc.mapeditor.org/en/stable/manual/terrain/ — Corner set: "A complete set with 2 terrains has 16 tiles"; Edge
set: 16; Mixed set: 256 ("reduced sets like the 47-tile Blob tileset can be used"). With 3+ terrains and a missing
pair: "Because there are no transitions from dirt directly to cobblestone, the Terrain tool first inserts transitions
to sand and from there to cobblestone" — i.e. it CHANGES neighbouring cells. Fine in an editor, wrong for
player-laid ground (it would rewrite other players' cells). [SRC + INF]

### 4e. The rule to use (combining the above) [INF, derived — needs an in-engine check]
- Give each of our materials a priority, e.g. mud < dirt < sand < grass < stone path < wood floor (taste call; the
  owner's). Draw one dual-grid layer per material, lowest first.
- For layer m at a display corner: a world cell counts as FILLED if its material's priority >= m (so lower layers run
  underneath higher ones and no holes appear) — the Red-Blob-style "same or higher priority" rule; and **skip layer m
  entirely unless at least one of the 4 cells is exactly m** (otherwise a lower layer whose shape differs peeks out as
  a thin rim where it doesn't exist).
- The HIGHER material's art defines the boundary shape: stone path over grass = crisp chamfered stone edge; grass over
  dirt = soft organic edge. Decorative grass tufts can still overhang onto a path as a separate decal layer.
- Art: ~15 tiles per material (6 with rotation for hard materials) = ~90 for six, instead of 15 pair-sets.
- Where 3-4 different materials meet at one corner, the stack composes automatically; no special tiles (Factorio's
  "transitions_between_transitions" is the price of NOT stacking).

## 5. Interface patterns for manual shape control

Sources deep-read: Terraria Hammers (https://terraria.wiki.gg/wiki/Hammers); Terraria Smart Cursor
(https://terraria.wiki.gg/wiki/Smart_Cursor); Minecraft Debug Stick (https://minecraft.wiki/w/Debug_Stick); Factorio
Controls (https://wiki.factorio.com/Controls); Cities: Skylines Roads (https://skylines.paradoxwikis.com/Roads);
Townscaper (https://en.wikipedia.org/wiki/Townscaper); Pie menu (https://en.wikipedia.org/wiki/Pie_menu); Game
Accessibility Guidelines, hold buttons
(https://gameaccessibilityguidelines.com/avoid-provide-alternatives-to-requiring-buttons-to-be-held-down/); Xbox
Accessibility Guideline 107, input (https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107,
read in full). Stardew Controls page: right stick used "to exactly place furniture, rugs, windows, etc."
(https://stardewvalleywiki.com/Controls). Fortnite's edit-mode page could not be fetched (HTTP 402) — its details are
[UNSURE] and not used.

### 5.0 "No control at all" — the shape emerges (Townscaper; DST; Stardew)
- Townscaper: players place "coloured blocks"; "Different rules of the game dictate these blocks' appearances ...
  depending on their location and surroundings"; the developer calls it "more of a toy". DST and Stardew likewise put
  the edge style on the MATERIAL (sections 4a, 4c). [SRC]
- Pros: nothing to learn; every placement looks finished; nothing extra to sync. Cons: no way to force a sharp corner
  or keep a jagged staircase; a checkerboard of two soft materials turns into diamonds, not squares. [INF]

### 5.1 A key that cycles the shape, with a preview (Factorio's R-to-rotate-before-placing)
- Factorio: "R ... Rotates the item held in the cursor or the selected entity clockwise" — works both BEFORE placing
  and on an already-placed thing. [SRC]
- Pros: familiar; one key; the ghost shows the result. Cons: our R is already the material cycle; a 12-shape cycle is
  long (up to 11 presses to get back); a hidden mode that silently changes what the next click does unless the
  indicator is always visible. Works if the cycle is SHORT (2 states: Soft / Sharp) and shown next to the material
  indicator. [INF]

### 5.2 A separate reshaping tool used after laying (Terraria's hammer; Minecraft's debug stick)
- Terraria: hammering a block cycles "Full block -> Half-block -> Slope (floor) facing right -> ... facing left ->
  Slope (ceiling) facing right -> ... facing left", the cycle repeats, and "The order of the shapes ... may vary
  depending on whether there are other blocks surrounding the hammered block" (context-aware ordering). [SRC]
- Minecraft debug stick: "Hitting the block allows players to select the block state key", "Using the block allows
  them to cycle through the valid values", "Sneaking while hitting or using cycles ... in reverse order" — and it is
  Creative-only, i.e. deliberately kept out of normal play. [SRC]
- Pros: the main flow (lay ground) stays simple; shaping is opt-in and discovered later; the world itself is the
  preview; clicking again undoes. Cons: one more tool/mode; a long cycle frustrates (Terraria needs up to 5 hits);
  aiming at a corner needs clear highlighting. [INF]

### 5.3 Radial menu
- Pie menus are fast because "selection depends on direction instead of distance"; "Experienced users use muscle
  memory"; "around 3-12 items can be reasonably accommodated". Used in GTA V, Secret of Mana, CS:GO. [SRC]
- Pros: great on gamepad (stick direction = choice); 4 diagonal orientations map naturally to 4 stick directions.
  Cons: usually hold-to-open (accessibility — needs a toggle alternative); covers the world; it IS the "shape
  picker" the owner fears; overkill for 2 states. [SRC + INF]

### 5.4 Drag to draw paths with automatic corners (city builders)
- Cities: Skylines: Straight / Curved / Freeform / Upgrade tools; "click the left mouse button at the starting point,
  then move the mouse cursor to plan the road placement, and click again to build the road"; right mouse cancels;
  roads "automatically snap to other roads, angles, the zoning grid, and road guidelines"; intersections are made
  automatically. [SRC]
- For us: a diagonal drag lays a staircase of cells, and the dual grid then draws it as a straight 45-degree road —
  diagonal roads with zero shape picking. Pros: fast long paths; draws what the player means. Cons: bulk cost must be
  shown before committing; needs a click-start / click-end alternative (XAG 107: content should be operable "without
  path-based gestures ... like ... clicking and dragging"). [SRC + INF]

### 5.5 Ghost previews and undo
- Factorio: "SHIFT + Left mouse button ... Build ghost"; "CTRL + Z ... Undo some actions such as manual entity
  building/removal, placing of blueprints, and usage of the deconstruction planner"; Redo "CTRL + Y". [SRC] Factorio is
  multiplayer; how its undo resolves conflicts with other players' edits is [UNSURE].
- XAG 107: act on the button RELEASE so a wrong press can be cancelled by moving away; "If a mechanism to cancel the
  action isn't available, a simple mechanism to undo the action is provided." [SRC]
- For us: the ghost must show the CELL outline plus the translucent resulting edges of all 4 affected corner tiles
  (placing one cell changes its neighbours' edges too — surprise is the main source of confusion). Undo = refund your
  own last few placements if nobody changed the cell since (server checks). [INF]

### 5.6 Gamepad
- Terraria's Smart Cursor "places a block at the nearest legal space to the cursor"; Stardew uses the right stick
  "to exactly place furniture, rugs". [SRC] Pattern: target the cell in front of the player by default, free cursor on
  the right stick for precision; a 2-state Soft/Sharp toggle fits one face button or a D-pad direction; a corner
  (vertex) target = the corner of the targeted cell nearest the player's facing or the right stick. [INF]
- XAG 107: all functions reachable by single, non-simultaneous digital presses; "Avoid introducing mechanics where a
  player is required to press two buttons simultaneously" — the code today digs with Shift+LMB held
  (`Player/PlayerInputRouter.cs` line 139); the R cycle with its own Dig entry, as described in the brief, removes
  that two-key press. [SRC + REPO]

### 5.7 Accessibility "no hold" setting
- Game Accessibility Guidelines (Motor, Intermediate): "Avoid / provide alternatives to requiring buttons to be held
  down"; alternatives = toggle, automatic activation, or a player setting. [SRC]
- XAG 107: The Long Dark's "accessible interactions" "converts all press and hold actions into press actions";
  Wasteland 2 offers click-to-move beside click-and-hold; avoid long holds "before the input is registered". [SRC]
- Terraria's Smart Cursor is a toggle by default with "an option in General Settings to make it last only while the
  key is held down". [SRC]
- For us: one global "Hold actions -> Toggle" setting covering hold-to-keep-digging, any radial, and drag-to-draw
  (which then becomes click start / click end). [INF]

## 6. Verification I ran myself (scratchpad, no repo edits)
Script: `scratchpad/gr_verify/verify.py`; picture: `scratchpad/gr_verify/sheet.png` (32 px per cell).
- Blob-47 check: a staircase cell and a rectangle's top-left corner cell both get index **28** — confirmed the blob set
  cannot tell a diagonal run from a square corner.
- Midpoint check: every boundary crossing of the staircase region lies on y = x + 0.5 — confirmed.
- Picture, left to right: (1) a 2-wide staircase drawn square = jagged; (2) the SAME cells through a dual grid with
  45-degree corner tiles = one straight diagonal road with parallel edges; (3) single cells touching only at corners,
  saddle tile drawn "joined" = a thin straight diagonal band; (4) a 4x3 rectangle = exact cell-aligned sides, corners
  cut by half a cell. Not yet checked in-engine: the layering "skip absent layer" rule (4e) — derived, not tested.
- Our committed zone saves contain no `~diag/~half/~quad` ids (grep of `nakama/data/zones` found none; the zonegen hits
  were comments), so retiring the 12-shape picker needs no committed-data migration. Dev-server player saves in
  Postgres may still hold some. [REPO]

## 7. Technique table

| Technique | How it works | Art cost (tiles) | Several materials? | Manual override? | Unity 6 support | Fit for us |
|---|---|---|---|---|---|---|
| Today's composite shapes | Player picks 2 materials + 1 of 12 shapes per cell; GPU mask blend | 1 fill texture per material; masks are code | Exactly 2 per cell | It is ONLY manual | Custom, already built | Poor — the awkward flow the owner rejected; hard geometric edges, no rounding |
| 4-neighbour mask | Cell looks at N/E/S/W (16 cases) | 16 per material | Via layers | Per cell | Rule Tile out of the box | Poor — blocky inner corners, no diagonals |
| 47-tile blob | Cell looks at 8 neighbours; a corner counts only if both sides do | 47 per material (more if pairs blend) | Via layers | Per cell | Rule Tile (3x3) out of the box | Low — most art, and cannot draw diagonals (verified) |
| Quarter-tiles (RPG Maker) | Each cell = 4 quarter pieces, each picked from 3 neighbours | 5 half-size (rotated) or 14-20 | "No obvious extension" (Boris) — overlap layers | Per cell, natural | Custom (half-size Tilemap or compositing) | Medium — runner-up |
| **Dual grid, one layer per material, priority order** | Art cut on the corner where 4 cells meet; each display tile reads 4 cells (16 cases); materials stacked low to high | 15 per material (6 if rotatable) ~ 90 for six | Yes — stacking; 3-4 materials at one corner compose automatically | Per corner: a "sharp" flag swaps to a square-cut tile (a square cut is just the fill texture masked by quadrants — code can make it) | Unity Tilemap offset by half a cell; jess-style script or a Rule Tile subclass (skner) | **High — diagonals and round corners for free, least confusing, fits our Tilemap** |
| Dual grid + runtime mask compositing | Same geometry; each material = fill texture + an edge-mask set; our existing GPU compositor bakes and caches the display tiles | 1 fill + ~15 edge masks per material (masks can be shared or code-made) | Yes | Per corner | Our `TileCompositor` + Tilemap | High — an implementation option for the row above; decide in the spike |
| Smooth marching squares / signed-distance shader | Interpolated contour or distance field, rendered as a mesh or shader | No tiles | Yes | Hard | Custom mesh/shader | Low — smooth anti-aliased curves fight 32 px pixel art |

### Scored candidates for the hard choice (1-5, higher = better)
| Candidate | Diagonal & round look | No confusion | Art cost | Several materials | Override | Unity + multiplayer | Dev cost | Verdict |
|---|---|---|---|---|---|---|---|---|
| Today's 12 shapes | 2 | 1 | 5 | 2 | 5 | 4 | 5 | Reject — fails the owner's ease-of-use bar |
| 47 blob | 2 | 5 | 1 | 3 | 3 | 5 | 4 | Reject — no diagonals, most art |
| Quarter-tiles | 4 | 5 | 4 | 2 | 4 | 3 | 3 | Runner-up — same look, weaker for several materials |
| **Dual grid stacked** | 5 | 5 | 4 | 4 | 4 | 4 | 3 | **PICK** |
| Dual grid + compositing | 5 | 5 | 5 | 5 | 5 | 4 | 2 | Pick's build option — cheaper art, more engineering |
| Smooth contour/shader | 4 | 5 | 5 | 4 | 3 | 2 | 2 | Reject — not pixel art |

## 8. Interface patterns — pros and cons, scored for our game
| Pattern | Pros | Cons | Verdict |
|---|---|---|---|
| Automatic only (Townscaper / DST / Stardew) | Nothing to learn; always looks finished; nothing new to sync | Cannot force a sharp corner or keep a jagged step; soft checkerboards become diamonds | **Default** |
| Shape-cycle key + preview (Factorio R) | Familiar; ghost shows result | R is taken; long cycles; a hidden mode unless always shown | Only if cut to 2 states — not needed with the corner tool |
| Reshape tool after laying (Terraria hammer, debug stick) | Main flow untouched; opt-in; the result shows in place; click again = undo | One more mode/tool; aiming at a corner needs clear highlighting | **Pick, as a 2-state per-corner toggle (Soft/Sharp)** |
| Radial menu | Fast for experts; stick direction = choice on gamepad | Usually hold-to-open; covers the world; it is the "shape picker" the owner fears | Reject for ground |
| Drag to draw with automatic corners (city builders) | Fast long paths; a diagonal drag gives a diagonal road automatically | Bulk cost must be previewed; needs click-start/click-end alternative | **Later addition** |
| Ghost preview + undo | Removes surprise (placing one cell changes 4 corner tiles); makes experimenting safe | Undo must refund and respect other players' edits | **Always** |
| Keep the 12-shape picker as an "advanced" option | Keeps half/quarter strips | Two rendering systems; the confusion stays for anyone who finds it | Retire (owner question on half/quarter strips) |

## 9. Recommendation

**Technique — the dual grid, one layer per material, in a fixed priority order, with the edge style owned by the
material.**
1. Keep the ground data exactly as now: one material id per cell, synced and saved as an opaque string. Gameplay
   (placing, digging, walking, crops) stays on the main grid — Stålberg's own advice. [SRC + REPO]
2. Draw the ground on half-cell-offset Tilemaps (offset (-0.5,-0.5), as jess and skner do), one per material, lowest
   priority first. Each display tile reads its 4 cells: filled = "this material or higher"; skip the layer unless one
   of the 4 cells is exactly this material. [CODE for the offset; INF for the rules]
3. The MATERIAL decides the edge look (DST's per-tile edge texture, Stardew's ConnectType): grass, dirt, sand, mud =
   rounded, irregular pixel edge (grass tufts can still overhang); stone path = straight 45-degree chamfer, so a
   staircase of path cells reads as a clean diagonal road (verified); wood floor = square. Style choices are the
   owner's. [SRC for the pattern; INF for the mapping]
4. Art: 15 tiles per material (6 for rotatable hard materials), or 1 fill texture + an edge-mask set baked at load time
   by our existing GPU compositor. A square-cut variant is just the fill masked by quadrants, so code can make it.
   Decide between hand-drawn sets and baked masks in the spike.
5. Every client computes the art from the synced ids with a pure function, so there is nothing new to send over the
   network. Re-pick edge tiles at chunk seams when the neighbouring chunk loads. [INF + REPO]

**Interface — automatic by default, one optional 2-state corner control, ghost and undo always.**
1. Laying ground stays exactly as the owner set it up: R cycles Dig and each ground kind, it is always visible, and
   left click lays one cell. **No shape choice at all in the normal flow.** Diagonals come from laying cells in a
   staircase; round corners come for free.
2. The ghost shows the cell outline plus a see-through preview of the new edges on all 4 affected corners, and the
   material cost, before the click (act on release, so moving away cancels — XAG 107).
3. For the few who want control: a **corner tool with just two states, Soft and Sharp**. Click near a corner of laid
   ground to make it square; click again to round it back (Terraria-hammer style, but 2 states instead of 6).
   Stored as a per-corner flag on one owning cell's id (the string stays opaque to the server). Where it lives — a
   last entry in the shovel's R cycle beside Dig, or its own hotbar item — is the owner's call.
4. Undo: refund your own last few placements, if nobody changed those cells since (server checks). Factorio proves
   build-undo in a multiplayer game; its conflict rules are [UNSURE].
5. Later: drag to draw a path (straight, L-shaped or diagonal staircase), always with a click-start / click-end
   alternative.
6. Gamepad: target the cell in front of the player, right stick for a free cursor, one face button for the corner
   toggle. Accessibility: one "hold -> toggle" setting covering hold-to-dig and drag-to-draw.
7. Retire the 12-shape picker. No committed zone uses composite ids (checked).

**Gate before building (a spike, not a critic):** in a test zone, lay all six materials in staircases, rectangles,
checkerboards and 3-4-material corners at 32 px. Check the diagonals read cleanly, no thin rim artefacts appear, chunk
seams re-pick correctly, and six stacked Tilemaps on a 256x256 zone hold frame time.

### Questions for the owner (taste — not decided here)
1. Edge style per material: natural ground rounded, stone path straight-diagonal, wood floor square?
2. Priority order (whose edge draws over whose), e.g. mud < dirt < sand < grass < stone path < wood floor?
3. Corner tool: the last entry in the shovel's R cycle, or a separate hotbar tool?
4. Are half-cell and quarter-cell strips still wanted? The dual grid can't draw anything thinner than about 0.7 of a
   cell (a corner-to-corner chain).
5. Two cells touching only at a corner: join into a thin diagonal band, or stay as separate diamonds?

## 10. Self-critique and gaps (no critic agent was allowed; this is my own adversarial pass)
- Web quotes came through WebFetch's summariser, so wording may be lightly paraphrased. Code quotes (jess, skner,
  RuleTile.cs, DST Lua) and the Stålberg/XAG texts are verbatim (curl / full page).
- The web-search budget for the session ran out mid-task (200/200). Not covered as a result: Anno 117 / other city
  builders' diagonal road drag, Fortnite's edit-mode details (fetch got HTTP 402), Minecraft stair auto-orientation
  (page truncated), and other top-down 2D games with player-laid diagonal ground (e.g. Core Keeper, Dinkum). [UNSURE]
- Not source-backed: the "rotated organic tiles pinwheel" claim; batching speed of `SetTiles`; Factorio undo conflict
  rules; whether Stardew paths join other path types; DST's renderer internals. All marked [UNSURE] above.
- The layering skip rule (4e) and the per-corner flag storage are my derivations — the spike must test them.
- Correction found: `docs/product/investigations/grass-overhaul/techniques_autotiling_transitions.md` wrongly says
  we are not on Unity's Tilemap (`TilemapManager.cs` calls `groundTilemap.SetTile`). Not edited (read-only task).
