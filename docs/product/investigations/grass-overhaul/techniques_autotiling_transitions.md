# Grass Overhaul — Techniques: Autotiling, Transitions, Anti-Repetition

Deep research on making 2D top-down grass look good in a Unity 2D top-down farming game.
Context: tiles are ~16-32px PNGs rendered per-cell via a custom runtime TileDatabase; we already
have a runtime GPU tile-composite shader system, so custom shaders + runtime tile generation are
on the table.

Status: IN PROGRESS (research being appended per source/topic as it is read).

---

## Source table

| # | Source URL | Concrete technique | Cost / complexity | Fits our Unity custom-tile + shader game? |
|---|-----------|--------------------|-------------------|-------------------------------------------|
| 1 | boristhebrave.com/2023/05/31/quarter-tile-autotiling/ | Quarter-tile / marching-squares / blob tile-count comparison; corner methods = 16 (or 5–6 w/ rotation) vs blob 48 | Low–med | Yes — port the corner logic; confirms dual-grid = 16 tiles |
| 2 | excaliburjs.com/blog/Dual Tilemap Autotiling Technique/ | Dual-grid impl: 2 tilemaps, half-offset, 4-corner lookup, **5 tiles + rotation** | Low | Yes (algorithm); rotation bad for organic grass |
| 3 | spritecook.ai/blog/dual-grid-tilesets-explained | Dual-grid: 15+empty tiles, 4-bit corner mask, ready lookup table, diagonal handling | Low | Yes — cleanest explanation + lookup table to port |
| 4 | boristhebrave.com/permanent/24/06/cr31/.../2corn.html | cr31 2-corner Wang = the terrain/corner method, 16 tiles, corner affects 3 tiles → patches | Low | Yes — the theory behind dual-grid |
| 5 | github.com/jess-hammer/dual-grid-tilemap-system-unity | Canonical Unity dual-grid (custom script, NOT RuleTile), 2 Tilemaps, 16 tiles | Med | Read for algorithm; built on Unity Tilemap (we port) |
| 6 | github.com/skner-dev/skner.DualGrid | Productized Unity dual-grid, **RuleTile-compatible**, auto-setup, free | Low (if on Tilemap) | Reference; needs Unity Tilemap (we're custom → port) |
| 7 | redblobgames.com/articles/autotile/claude/ | Master comparison of all methods + **multi-terrain PRIORITY-OVERLAY** + perf caching | Low | Yes — priority-overlay is our multi-terrain model |
| 8 | iquilezles.org/articles/texturerepetition/ | Shader de-repetition; **technique 3 = low-freq index blend, 2 fetches** | Med (shader) | Yes — drops into our GPU composite shader |
| 9 | zahni.itch.io/overworld/devlog/809069/... | Overflow/fringe overhang, dithered grass edges, full-tile transitions, **2×2-px-per-tile tint map** | Low | Yes — best practical transition + macro-tint tricks |
| 10 | docs.unity3d.com .../WeightedRandomTile | Weighted variants, **deterministic per cell position** (position hash) | Low | Yes — mirror as hash(x,y,seed) for our determinism |
| 11 | sprite-ai.art/blog/seamless-pixel-art-tiles | Seamless tile authoring, 32×32 sweet spot, scatter detail across whole tile, 3×3 test | Low | Yes — art-side rules for our PNG tiles |

---

## Topic 1 — Autotiling methods

### Source: BorisTheBrave — "Quarter-Tile Autotiling" (2023) — boristhebrave.com
Boris the Brave is one of the canonical autotiling references (author of the widely-cited
autotiling/wave-function-collapse writeups). Key facts extracted:

- **Quarter-tile / "sub-tile" autotiling**: divide each grid cell into 4 sub-cells (half width
  & half height). Each quarter-tile is chosen from the terrain of its own cell + the 3 cells it is
  adjacent/diagonal to (i.e. the 2×2 neighborhood around that corner). This is functionally the
  same family as the dual-grid / marching-squares idea.
- **Tile-count comparison (his table)**:
  | Method | With rotation | Without rotation |
  |--------|--------------|------------------|
  | Quarter-tiles | 5 half-size tiles | 14–20 half-size |
  | Marching Squares (dual grid) | 6 tiles | 16 tiles |
  | Blob pattern | — | 48 (i.e. 47+1) full tiles |
- **Relationship to dual-grid / marching squares**: marching squares stores terrain on the grid
  *vertices* (a "dual grid" offset by half a cell) and needs **16 tiles** (or 6 with rotation);
  quarter-tiling stores terrain on the *cells* and reconstructs the same 4-corner logic from
  sub-tiles. Both reduce the blob 47/48 down to ~16.
- **The key limitation of all corner/2×2 methods**: with only 16 (or fewer) tiles you "cannot
  produce swooping curves larger than half a tile" and borders can't locally shrink/grow one
  terrain — the edge geometry is coarser than a hand-authored 47-blob. Trade fidelity of the edge
  silhouette for a ~3× smaller tileset.
- **Takeaway for us**: the 47-blob gives the richest hand-authored edge silhouette; the
  dual-grid/marching-squares 16-tile approach is the modern sweet spot (smooth, tiny tileset) but
  the raw edge is only as curvy as half a tile — you compensate with *overhang/fringe decals* (see
  Topic 2) rather than more autotile tiles.

### Source: SpriteCook — "Dual-grid tilesets, explained" — spritecook.ai
The clearest statement of the modern dual-grid method. CONFIRMED facts:
- **The offset grid**: tiles are NOT placed on the painted cells. A second "display" grid is offset
  by **half a tile** so each *rendered* tile sits over the corner where **four painted cells meet**
  — each display tile overlaps exactly 4 world cells at its corners.
- **16 tiles (15 + empty)**: "Two options [grass/not], four corners, 2^4 = 16 cases. One case is
  'all four empty' → draws nothing. The other 15 are the 15-piece tileset."
- **4-bit bitmask** from the 4 cells the display tile touches: TL=bit1, TR=bit2, BL=bit4, BR=bit8.
- **Direct comparison**: "the single-grid blob needs 8 neighbors and 47 tiles to handle what dual
  grid covers with 4 cells and 15 tiles."
- **Why dual-grid beats edge/corner matching**: diagonal-corner touching (two same-terrain cells
  meeting only at a corner) resolves *naturally* — a display tile between diagonal cells just has
  two opposite filled corners; no special-case logic needed. (This is the classic failure mode of
  naive 4-neighbor edge autotiling.)
- **Ready-to-use lookup table** (4-bit mask → tile frame index):
  `[-1, 15, 8, 9, 0, 11, 14, 7, 13, 4, 1, 10, 3, 2, 5, 6]` — index by the bitmask, `-1` = empty.

### Source: Excalibur.js — "Dual Tilemap Autotiling Technique" — excaliburjs.com
A concrete TypeScript implementation of dual-grid, with an important OPTIMIZATION: use **5 tiles +
runtime rotation** instead of 15 distinct tiles.
- **Two tilemaps**: a *world* map (logic only: soil vs grass) and a *graphics/mesh* map (the visible
  overlay). The mesh map is positioned at a **half-tile offset** (`vec(-8,-8)` for 16px tiles) so
  "the corners of each mesh tile align with the centers of four world tiles."
- **4-corner lookup**: each mesh tile samples the 4 world tiles at its corners (TL, TR, BL, BR).
- **Only 5 unique sprites, rotated** (grass-neighbor count drives the choice; rotation drives
  orientation):
  - 0 grass → draw nothing
  - 1 grass → sprite 1 (outer/edge corner), rotated 0/90/-90/180 by which corner is grass
  - 2 grass → sprite 2 (straight edge) for *adjacent* pair, sprite 3 for *diagonal* pair
  - 3 grass → sprite 4 (inner corner), rotated
  - 4 grass → sprite 5 (fully filled)
- So a **symmetric** grass tileset can be as small as **~5–6 authored tiles** (matches Boris's "6
  with rotation"). For ORGANIC grass you usually DON'T rotate (rotation makes the noise/blades
  visibly pinwheel), so you author the full 15 — rotation-free variants read better for nature.
- Gotcha noted: `sprite.clone()` before setting rotation, or every instance rotates.

**Design note for organic grass**: rotation-based 5-tile packs are perfect for hard-edged man-made
materials (paths, stone) but for GRASS the rotational symmetry is visible as pinwheeling blade
directions — author the 15 distinct tiles (or add per-tile variants) instead of rotating 5.

### Source: cr31 (Stagecast) — "2-Corner Wang Tiles" (via boristhebrave permanent mirror)
cr31.co.uk is THE classic autotiling reference (the origin of most modern writeups). The original
domain is gone; boristhebrave hosts a permanent mirror. CONFIRMED facts:
- **2-corner Wang tiles = the corner-matching method** (the Stardew/RPG-Maker family). Each corner
  has 2 possible types (e.g. grass / not-grass). 4 corners × 2 types = **2^4 = 16 tiles** (index
  0–15). This IS the same 16-tile set as dual-grid — dual-grid is just the *rendering* trick that
  places a 2-corner Wang tileset on an offset grid so it aligns visually.
- **Corner bitmask**: NE=1, SE=2, SW=4, NW=8; sum the corners that are the "filled" terrain → index.
  (Note: bit assignment is arbitrary; each implementation picks its own — dual-grid tutorials use
  TL=1,TR=2,BL=4,BR=8. Same 16 tiles.)
- **Why corner-matching (Wang 2-corner) is the terrain method**: "an edge only affects one adjacent
  tile, while matching a corner affects three adjacent tiles" → corner matching produces large
  contiguous *patches* of terrain (grass fields) with clean borders, which is exactly what terrain
  wants. Edge-matching (2-edge Wang, 16 tiles) is for walls/fences/paths (linear things), not fields.
- **This unifies the whole topic**: blob-47 = 8-neighbor per-cell; 2-corner Wang / marching-squares
  / dual-grid = 4-corner, 16-tile, and are the SAME tileset rendered three ways. Dual-grid is the
  cleanest rendering because the display tile literally sits on the 4-cell corner.

### Source: jess-hammer/dual-grid-tilemap-system-unity (GitHub, the canonical Unity impl)
The most-referenced Unity dual-grid implementation (Jess Hammer; inspired by Oskar Stålberg's dual
grid concept + a ThinMatrix video). CONFIRMED:
- **Two Unity Tilemaps**: a *world* Tilemap (logic: which cells are grass/dirt) and a *display*
  Tilemap offset by half a cell. A custom `MonoBehaviour` reads the world grid and paints the
  display grid.
- **Does NOT use RuleTile** — "a custom script with hard-coded 'rules' to control the placement of
  regular tiles." Each display tile checks its **4** world-neighbors (vs 8) → picks 1 of **16**.
- Advantages stated: "perfectly rounded corners", "tiles are not ambiguous… each dirt/grass aligns
  with the world grid", 4-neighbor efficiency, only 16 tiles vs 47.
- Built on Unity 2023.1; author notes performance not formally profiled (fine for our scale).

### Source: skner-dev/skner.DualGrid (Unity package, the "productized" dual-grid)
A polished, Asset-Store + GitHub Unity package (free). CONFIRMED:
- **Data Tilemap** (tile types) + **Render Tilemap** (half-offset visual). Paint the Data map, the
  Render map updates automatically.
- **RuleTile-COMPATIBLE**: "full integration with Unity's Tilemap and Rule Tiles" + "streamlined
  rule tile creation." Automatic setup ("takes seconds"). Requires Unity 2021.3+, 2D Tilemap Extras
  3.1.2, 2D Tilemap Editor 1.0.0. Only 16 tiles for all combinations; "fully round corners not
  possible with traditional tilemap structures."
- **Relevance to us**: this is the reference to READ for how to wire dual-grid, but it is built on
  Unity's *Tilemap component*. We render per-cell via a custom TileDatabase, so we'd port the
  *algorithm* (offset grid + 4-corner→16 lookup), not drop in the package.

### Source: Red Blob Games — "Autotiling: Interactive Guide" (redblobgames.com/articles/autotile/claude/)
Red Blob Games is a top-tier reference. This guide's comparison table is the single best summary:

| Technique | Tiles needed | Handles corners? | Art complexity | Best for |
|-----------|-------------|------------------|----------------|----------|
| 4-bit bitmask (cardinal N/E/S/W only) | 16 | **No** (can't tell inner vs outer corner → awkward) | Low | prototyping |
| 8-bit **blob / 47** | **47** (of 256) | **Yes** (smooth inner+outer) | Medium | polished 2D games |
| **Dual grid** | **16** | **Yes** | Low ("easier to create art") | smooth transitions |
| Mini-tile / 2×2 (RPG Maker) | 5 shapes (×rotation) | Yes | Low | RPG-Maker style |

Load-bearing details CONFIRMED from this source:
- **Blob-47 bitmask trick**: with 8 neighbors you'd have 256 combos, but a diagonal neighbor only
  matters when *both* its adjacent cardinals are also filled → collapses to **47** meaningful tiles.
  Code: `if (n && e && ne) mask |= NE_bit;` (diagonal counts only if both cardinals present).
- **Dual grid = marching squares with sprites**: "essentially the same concept as Marching Squares
  but substitutes pre-drawn sprites for vector line segments." 4 corners × 2 states = 16 cases.
  Terrain boundary passes through *tile centers* → visually smoother than cell-aligned edges.
- **MULTI-TERRAIN (grass↔dirt↔sand↔water) — the priority method** (important for us): assign each
  terrain a **priority level**; a cell matches neighbors of "same or higher priority," and **each
  terrain draws its own tileset as an overlay** on top of the lower-priority terrain. So you don't
  make an N×N matrix of pairwise transition tiles — you stack: water (base) < sand < dirt < grass,
  each higher layer autotiled with its own 16/47 set, its transition edge overhanging the layer
  below. This is how you get grass-over-dirt-over-sand-over-water without combinatorial explosion.
- **Perf insight**: recompute bitmasks only for cells whose neighbors changed; cache tile indices.
  (Relevant since our world is largely static grass — compute once at zone load.)

---

## Topic 2 — Transitions / edge blending

### Source: zahni — "Tricks for tile-based terrain" (Overworld devlog, itch.io)
A working commercial 2D overworld's actual tricks. This is the single most practical transitions
source. CONFIRMED tricks:
1. **Overflow / spillage (THE key one for organic edges)**: objects and grass are "allowed to spill
   out beyond the edge of the tile boundary." Grass blades / forest edges partially overlap the row
   above → individually-drawn tiles merge into one continuous mass, and the hard cell grid vanishes.
   This is the "overhang/fringe sprite" technique: the transition isn't a flat border tile, it's
   grass geometry drawn OVER the neighbor tile.
2. **Faux perspective from directional overhang** (from the related result): grass overhangs the
   BOTTOM (south) of a dirt/mud bank MORE than the sides → reads as grass leaning toward camera.
   Asymmetric overhang sells a slight 3/4 look on a top-down map.
3. **Full-tile transition sprites** for SHARP color boundaries (beach↔ocean): a transition sprite
   covering an entire tile, drawn as a SQUARE with exact alignment (no seam). Use when a soft blend
   won't do (water/dirt edges are "solid/smooth" so dithering looks wrong there).
4. **Multi-tile-wide transition patterns**: 2–3-tile-wide shoreline/edge sprites mixed in so "every
   horizontal shoreline is not just the same shape repeating." Directly attacks edge repetition.
5. **Dithering suits GRASS specifically**: a stippled/dithered grass→dirt edge "suggests little
   blades of grass," but the SAME dither looks wrong on water/dirt (those edges are solid). → Use
   dithered/stippled transitions for grass edges, hard/overhang transitions for water & stone.
6. **Depth-sort via parallelogram footprints** so overflowing sprites never draw a far object atop
   a near one.

**Synthesis for grass↔X transitions (best-looking approach):**
- grass↔dirt/path/soil → **dithered/stippled** edge + **overhanging grass-blade fringe** drawn over
  the dirt (soft, organic; the hard checker edge disappears).
- grass↔water/stone → **hard autotile border** or a **full-tile transition sprite** (crisp), maybe
  with a thin overhang of grass but not a dither.
- This matches the multi-terrain PRIORITY-OVERLAY model (Red Blob): grass is a high-priority layer
  whose autotiled edge tiles include hanging fringe, composited over the lower layer.

---

## Topic 3 — Anti-tiling / breaking repetition

### Source: Inigo Quilez — "Texture Repetition" (iquilezles.org) — the DEFINITIVE shader method
IQ (Shadertoy/Pixar) is the canonical reference for killing texture repetition in a shader. Three
techniques, in ascending cost:
- **Technique 1 — per-tile hash transform + border blend**: hash each tile's integer coords to a
  random offset + orientation (mirror/rotate), sample the texture transformed per tile. Naively this
  seams at tile borders, so near a border (`smoothstep(0.25,0.75,fuv)`) you sample the up-to-4
  neighboring tiles' transforms and blend. Cost: up to 4 texture fetches near borders. Great for
  a tiling grass texture where you want each repeat to look different.
- **Technique 2 — Voronoi/Gaussian blend**: over a 3×3 neighborhood, each cell has a random feature
  point; sample the texture offset per cell, weight by `w = exp(-5*d)`, normalize. 9 fetches; highest
  quality but expensive.
- **Technique 3 — low-frequency index blend (BEST cost/quality, recommended for us)**: sample a
  low-frequency "variation" noise → `float k`, map to an index across N virtual patterns; hash gives
  each pattern a UV offset; sample TWO patterns and `smoothstep`-blend by k. Only **2 texture
  fetches**, variation noise stays cache-resident. This is the cheap, high-quality way to make one
  grass texture read as endlessly varied — a big-scale noise picks which "flavor" of grass each
  region shows, blended smoothly.
- Directly implementable in our runtime GPU tile-composite shader: technique 3 = one extra low-freq
  noise sample + a second offset tap.

### Source: zahni devlog — the "2×2-px-per-tile color map" trick (large-scale color modulation)
- **Low-resolution colored background**: a very low-res image with "2×2 pixels per tile" TINTS the
  identical grass sprite differently across the map (grassland vs desert vs marsh) WITHOUT drawing
  new tile variants. This is macro color modulation done as data, not shader noise — you hand-paint
  or noise-generate a tiny per-region tint map and multiply it into the grass tile at draw. Cheap,
  art-directable, and kills the "one flat carpet color" look at zone scale.
- Combine with per-tile variants + IQ technique-3 micro-variation for a full anti-repetition stack.

### Source: Unity 2D Tilemap Extras — WeightedRandomTile / RandomTile (Unity docs + GitHub)
The standard "multiple variants, weighted-random per cell" primitive, and its determinism property:
- **WeightedRandomTile**: pick a sprite from a weighted pool; higher weight = more likely. Crucially
  the choice "is randomized based on its location and remains fixed for that particular location" —
  i.e. it is a **deterministic hash of the cell coordinate**, not a per-frame RNG. Same cell → same
  variant on every client/run.
- **CRITICAL for our deterministic multiplayer game**: variant selection MUST be a pure function of
  (cell x, cell y, zone seed) — a position hash — so every client renders the identical grass. This
  is display-only (not sim state), so it doesn't need a ledger event, but it must not use
  frame/time/`Random` — use `hash(x,y)`. (Matches how WeightedRandomTile is deterministic-by-design.)
- **RandomBrush** paints sets; **RandomTile** is the unweighted version.

### Source: sprite-ai "Pixel art tiles that don't look terrible" — authoring recipe
Concrete tile-authoring rules to reduce repetition at the ART level:
- **Seamless authoring**: rightmost pixel column must match the leftmost of the neighbor; same top/
  bottom. Author via the 50%-offset method (shift 50% h+v, fix the seams that appear in the center).
- **Tile size**: 16×16 hardest (every pixel critical), **32×32 = sweet spot**, 64+ easiest. (We're
  16–32px — lean to 32 for grass to get blending room.)
- **Distribute detail across the WHOLE tile**, not the center — center-biased detail (pebbles/
  flowers clumped mid-tile) creates a visible repeating "dot" grid + vignette. Scatter small pebbles/
  wildflowers edge-to-edge.
- **Test with a 3×3 grid** + a 50%-offset check + zoomed-out inspection to expose seams and hidden
  periodicity before shipping a tile.

**Anti-repetition RECIPE (concrete, layered — the full stack):**
1. **3–5 base grass variants**, weighted-random per cell by `hash(x,y,seed)` (common flat + rarer
   detailed). Deterministic.
2. **Scattered detail decals** (flowers, pebbles, clover, dry patches) placed sparsely by a second
   position-hash pass, drawn OVER the base — breaks the grid without multiplying base tiles.
3. **Per-tile hue/value jitter in the shader**: `hash(cell)`→ small ±HSV offset (esp. value ±3–6%,
   hue ±2–4°) so no two cells are the identical color. Cheap, kills the "flat carpet".
4. **Macro color modulation**: a low-freq Perlin field (or zahni's 2×2-px-per-tile tint map) tints
   grass by region (lush hollow vs dry rise) — large scale, art-directable.
5. **Optional micro-variation** via IQ technique-3 in-shader for the base grass texture itself.
6. Keep the autotiled EDGES (dual-grid) separate from this — variation/jitter applies to interior
   fill tiles; edges get the fringe/overhang treatment from Topic 2.

---

## Topic 4 — Unity-specific

### What Unity gives you out of the box (2D Tilemap Extras package)
- **RuleTile**: scriptable tile with neighbor rules; Output can be Single / **Random** (weighted-ish
  variant pool) / Animation. Good for autotiling on Unity's Tilemap component. Needs `com.unity.2d.
  tilemap.extras`.
- **WeightedRandomTile / RandomTile / RandomBrush**: multi-variant weighted random, deterministic by
  cell position (see Topic 3). The built-in anti-repetition primitive.
- **Dual-grid packages**:
  - `jess-hammer/dual-grid-tilemap-system-unity` — reference implementation, custom script (NOT
    RuleTile), 2 Tilemaps + half-offset, 16 tiles. Best to READ for the algorithm.
  - `skner-dev/skner.DualGrid` — productized package, **RuleTile-compatible**, auto-setup, Asset
    Store + GitHub free. Data Tilemap + Render Tilemap.
  - Forks: `DualGrid-Hex` (hex), `Dual-Grid-without-Null-Tiles` (base tile instead of null).

### What needs Unity's Tilemap component vs a custom renderer (OUR situation)
- All the above packages are built on Unity's **Tilemap component + Tile Palette**. Our game renders
  each cell via a **custom runtime TileDatabase** (PNGs, dynamic `Sprite.Create`) + a **runtime GPU
  tile-composite shader** — we are NOT on Unity's Tilemap. So:
  - We **port the ALGORITHMS**, not the assets: (a) dual-grid = maintain our logical grass/dirt grid,
    render an offset display layer where each display cell samples its 4 logical corners → 16-entry
    lookup (use the ready table `[-1,15,8,9,0,11,14,7,13,4,1,10,3,2,5,6]` or author our own 15).
  - Variant selection + hue/value jitter + macro tint = **all shader-side**, which we already do —
    feed the shader `cell_xy`, a `hash(cell)`, and a low-freq tint map; this is squarely in our
    existing GPU tile-composite system's wheelhouse.
  - Multi-terrain = **priority-overlay layers** (Red Blob): render water<sand<dirt<grass, each its
    own autotiled pass with fringe, composited by the shader — fits a GPU composite far better than
    Unity's single-Tilemap-per-layer model.
- **Determinism constraint (ours, not Unity's)**: every per-cell random (variant, jitter, decal
  scatter) must be `hash(x,y,zoneSeed)` so all networked clients agree. Display-only → no ledger
  event, but no time/frame RNG.

### Shader-based tinting/variation (fits us best)
- Per-tile HSV jitter from `hash(cell)`; macro Perlin/2×2-tint multiply; IQ technique-3 texture
  de-repetition — all fragment-shader work on the grass layer. This is the highest-leverage, lowest-
  art-cost path given we already have the runtime composite shader. (Contrast: on vanilla Unity
  Tilemap you'd need per-tile material property blocks or baked variants — clunkier than our setup.)

---

## Top recommendations for us

Confidence: HIGH on the technique landscape (11 deep-read sources, cross-confirmed). Facts vs
inference are flagged. The one thing to verify against OUR code before building: how the runtime
GPU tile-composite shader currently receives per-cell data (so we know where to inject hash/offset/
tint) — not covered by these external sources.

**1. Autotiling method: DUAL-GRID (offset display grid, 16-tile corner set). [FACT-backed]**
   - It is the modern consensus (Boris, Red Blob, spritecook, jess-hammer, skner all converge): 16
     tiles vs 47, only 4 corners checked, diagonals resolve for free, boundary runs through tile
     centers → smoothest edges, least art. It IS 2-corner Wang tiles rendered on a half-offset grid.
   - Port the ALGORITHM into our custom renderer (we're not on Unity's Tilemap): keep a logical
     grass/dirt grid; render an offset layer where each display cell samples its 4 logical corners →
     index a 16-entry table. Ready table: `[-1,15,8,9,0,11,14,7,13,4,1,10,3,2,5,6]` (or author 15).
   - For ORGANIC grass, author the full 15 distinct edge tiles — do NOT use the 5-tiles+rotation
     shortcut (rotation makes blades pinwheel visibly). [INFERENCE from excalibur's rotation note.]
   - Reserve blob-47 only if we later want richer hand-drawn edge silhouettes; dual-grid is the
     right default and lets edge richness come from fringe overhang instead.

**2. Multi-terrain (grass/dirt/path/sand/water): PRIORITY-OVERLAY layers, not pairwise tiles. [FACT]**
   - Stack water < sand < dirt/path < grass; each higher terrain autotiled with its own dual-grid
     set and composited over the one below (Red Blob). Avoids the N² transition-tile explosion and
     fits a GPU composite shader naturally.

**3. Transitions: dithered fringe + overhang for grass; hard/full-tile for water & stone. [FACT]**
   - grass↔dirt/path: dithered/stippled edge (reads as blades) + grass-blade FRINGE that overhangs
     onto the dirt tile (zahni's overflow trick) — this is what kills the hard checker edge.
   - Overhang the SOUTH edge more than sides for faux-perspective on our top-down map.
   - grass↔water/stone: hard autotile border or full-tile transition sprite (dither looks wrong on
     solid materials).

**4. Anti-repetition ("flat carpet" fix): the layered stack (the big win). [FACT + INFERENCE]**
   a. 3–5 weighted-random base grass variants per cell, chosen by `hash(x,y,zoneSeed)` (deterministic).
   b. Sparse scattered detail decals (flowers/pebbles/clover/dry patch) via a 2nd position-hash pass,
      drawn over the base — breaks the grid cheaply.
   c. Per-cell shader HSV jitter from `hash(cell)` (value ±3–6%, hue ±2–4°) — no two cells identical.
   d. Macro color modulation: low-freq Perlin field OR a 2×2-px-per-tile tint map → regional grass
      color (lush hollow vs dry rise). Art-directable, large scale.
   e. Optional: IQ technique-3 in-shader de-repetition of the base grass texture (2 texture fetches).
   - Do (a)–(d) first; they're cheap and give ~90% of the result. (e) is polish.

**5. Determinism guardrail (ours). [FACT — from our multiplayer model + WeightedRandomTile]**
   - Every per-cell "random" (variant, jitter, decal) = pure `hash(x,y,zoneSeed)`. It's display-only
     (no ledger event / no sim state) but MUST NOT use time/frame/`Random`, or clients diverge visually.

**6. Art authoring. [FACT]**
   - Prefer 32×32 grass tiles (blending room) over 16; author seamless (50%-offset method); scatter
     detail edge-to-edge (not center) to avoid a repeating dot grid; validate every tile on a 3×3 +
     offset test before use.

**Suggested build order**: dual-grid interior+edges (1) → priority-overlay for dirt/path/water (2) →
fringe/overhang + dither on grass edges (3) → variant+decal+HSV-jitter+macro-tint anti-repetition
stack (4), all under the hash-determinism rule (5). Verify the shader's per-cell data path in our
code first.
