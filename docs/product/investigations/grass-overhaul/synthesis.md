# Grass overhaul — synthesis (12 games + techniques → our game)

Distilled from: `games_farming_sims.md` (Stardew), `games_sandbox_survival.md` (Terraria, Necesse),
`games_additional.md` (9 more), `techniques_autotiling_transitions.md`, `techniques_wind_color_depth.md`,
`our_current_grass.md`. This is the evidence base for the plan.

## The universal recipe (what ALL 12 games converge on)
**The base grass tile is almost always plain. Lushness comes from VARIETY + SCATTER + MOTION on top of it.**
Every polished example combines:
1. **Variety at the base** — either many base-tile variants picked per cell (Necesse: 7 random/cell) and/or a
   scattered tuft overlay (Stardew, Terraria). A single repeated tile = the flat-carpet look (Forager is the
   deliberate counter-example, and it's exactly what we're leaving).
2. **A dense scatter of taller detail** — tufts/blades/flowers/plants of varied silhouette (all games). This is
   the single biggest "lush" factor.
3. **Color variation** — variants + per-biome recolor + gradient/hue jitter. (Recolor ALONE ≠ enough — Forager.)
4. **Good edges** — connection/transition tiles, and the best-looking ones break the tile grid with organic
   fringes (Don't Starve) rather than a hard stair-step.
5. **Motion** — the detail sways: base-anchored vertex skew, per-instance phase (no unison), pixel-snapped,
   often player-reactive (Stardew, Terraria, Moonlighter converge on this).

## The levers for OUR game — ranked by (impact × how-easy-given-our-tech)
Our current state (verified): ONE flat `grass.png` on every cell (v2/v3 unused), no autotiling, sparse decor,
static. We're on Unity's real `Tilemap`; **`LitWind` foliage sway is already built**; custom tile shaders proven.

| # | Lever | Evidence | Impact | Our feasibility | 
|---|-------|----------|--------|-----------------|
| **A** | **Variant-per-cell base grass** (author 6–8 textured variants, pick per cell) | Necesse (7/cell, dev-confirmed); Unity `WeightedRandomTile` | **HIGH** (kills the repeat) | **EASY** — Unity Tilemap WeightedRandomTile, or extend `TileDatabase`. We have 3 tiles, use 1 |
| **B** | **Dense grass-detail SCATTER layer** (tuft/blade/flower catalog, 3+ variants, tuned density, random rotate/flip, drop-shadow) | ALL games; Stardew 2×2 subgrid tufts; Necesse dense plants; FoM decal *catalog* | **HIGHEST** (biggest lush factor) | **MED** — need good tuft art; scatter system + detail occupants exist; tufts already get `LitWind` sway |
| **C** | **Better base grass ART** (real texture: subtle blades/clumps, few colors, seamless 50%-offset) | SLYNYRD; every game's tiles ≠ flat noise | **MED-HIGH** | **MED** — our gpt-image + pixelclean pipeline; the variants from A are this art |
| **D** | **Organic edges: dual-grid transitions + fringe overlay** | Don't Starve (noise-perturbed off-grid fringe); dual-grid autotiling (modern pick) | **HIGH** (kills the hard seam) | **MED** — dual-grid works on Unity Tilemap; fringe = an alpha-mask overhang sprite at seams; **spike:** per-cell data path in our chunk loader |
| **E** | **Color variation: macro-tint noise + HSV jitter + biome recolor** | IQ texture-repetition; zahni color map; Core Keeper biomes | **MED-HIGH** | **MED** — macro-tint ground shader via the animated-water-tilemap pattern; **spike:** per-cell tint data path |
| **F** | **Wind sway: pixel-snap + player-reactive bend** | Stardew/Terraria/Moonlighter converge | **MED** (alive) | **MOSTLY BUILT** — `LitWind` already sways foliage incl. grass; enhancements = pixel-snap + velocity bend |

## The two genuinely NEW ideas (beyond variants+scatter+sway)
- **Organic noise-perturbed edge fringes (Don't Starve):** an alpha-mask fringe overlay at grass↔dirt/sand/water
  seams so the boundary weaves off-grid instead of a straight stair-step. Highest "not-a-tilemap" win at edges.
- **A seasonal decal CATALOG (Fields of Mistria):** grass detail as a first-class library (2-blades, tuft,
  single flower…), each with seasonal variants — not one tuft sprite. (Only if we do seasons.)

## Recommended direction (cheapest-highest-impact first — the plan will formalize + score options)
1. **Base variety + detail scatter (the 80/20):** variant-per-cell base grass (A) + a proper dense tuft/flower
   scatter layer (B, C). These two alone move us most of the way to the Necesse look; tufts sway for free via
   `LitWind`. Lowest tech risk, highest visual payoff.
2. **Edges:** dual-grid transitions + an organic fringe overlay (D) — removes the hard grass/dirt seam.
3. **Color depth:** macro-tint low-freq color shader + per-instance HSV jitter (E).
4. **Alive polish:** pixel-snap the sway + optional player-reactive bend (F); ambient life (fireflies exist).

## Open questions / spikes / owner-taste (for the plan + certainty)
- **Spike:** can our custom chunk-loaded Tilemap feed per-cell data to a tint/dual-grid shader? (verify before E/D.)
- **Art direction (owner taste):** crisp-pixel (Stardew/Necesse) vs painterly (Don't Starve)? density/lushness level?
- **Scope:** biome variation? seasons (→ decal catalog + seasonal recolor)? which zones first?
- **Resolution:** we're 32×32 already (Necesse-level, good blending room) — keep.

## ⚠ Critic round-1 corrections (VERIFIED in code — these SUPERSEDE the rankings above)
The cold-critic (`critic_round1.md`) caught real, load-bearing issues; I re-verified each against the code:
1. **PERF — the dense-scatter feasibility was WRONG (was "MED, reuse scatter").** Each occupant =
   GameObject + SpriteRenderer + **BlobShadow GO** + **BoxCollider2D** + click target (`TilemapManager.cs:1007-1130`);
   current density 0.08 (`scatter.py:19`). A Necesse-dense carpet (0.5-1.5/cell) = **tens of thousands of
   GameObjects** → perf death (web: Unity 400→35 FPS @ ~1000 grass GObjects; the GO/collider overhead itself is
   the killer). **Dense visual tufts need a NEW batched, collider-FREE renderer** (`DrawMeshInstanced` or a
   combined per-chunk mesh); interactive/gameplay plants stay sparse occupants. Bake contact-AO INTO the tuft
   sprite (not a shadow GO). **This is the #1 spike — resolve before committing a build order.**
2. **RE-RANK — lead with the CHEAP shader/data wins (A + E), not the GameObject carpet.** Per-cell **HSV
   jitter needs NO data path** — just `hash(floor(worldPos))` in the fragment shader; **macro-tint** uses the
   already-proven `_ShoreMask` per-cell data texture; both = **zero GameObjects**. Add **dithering** to the tint
   gradients (they band on 8-bit). Variants (A) via our runtime `SetTile` path = **roll our own
   `hash(x,y,seed)→variant`** (WeightedRandomTile is a Tile-Palette *asset*, doesn't drop into our path).
3. **ADD normal-mapped lighting (omitted; near-free).** `SpriteLitWorld.shader` already has `_NormalMap` +
   a full `NormalsRendering` pass (lines 18, 177+); the game is URP-2D-lit. Author **normal maps** for grass
   tiles + tufts → real depth/AO under day-night + lamps. (Moonlighter's "no normal maps" was imported without
   noticing Moonlighter isn't 2D-lit like us.)
4. **WIND is basic, not "mostly built."** The sway (`SpriteLitWorld.shader:134`) is a **single global sine
   phased by world-X** + a `_HitBend` impulse — no gusts, weak per-instance variation, no walk-through bend.
   The good (Stardew/Terraria) version = **add noise gusts + per-instance hash phase + player-position bend +
   a persistent trampling trail** (cheap via a per-cell shader field). It's an upgrade to LitWind, not free.
5. **TRANSITIONS — bake-off, lean FRINGE not dual-grid.** Dual-grid needs a 2nd offset tilemap and ~60-75
   tiles for our 4-5 terrains (grass/dirt/path/sand/water), and **conflicts with our existing shaped-ground
   `TileCompositor` blend** (one gameplay tilemap). **Fringe-overhang + dither** (our Topic-2 rated it best for
   organic grass edges; Don't Starve's look) works WITH shaped-ground and is likely the better pick. Bake-off in the plan.
6. **Placement mechanism EXISTS:** `scatter.py` already has `clumping` + a gaussian density field (`:43`) for
   organic clumps/clearings — "tuned density" is a config (pass `clumping>0`), not new code.

**Net revised order:** A (hash-variant tiles) + E (in-shader HSV+macro-tint+dither) + normal maps FIRST (cheap,
zero-GO, high impact) → wind upgrade (F) → **spike the batched tuft renderer, then the dense scatter (B)** →
transitions bake-off (D, lean fringe). The plan formalizes this with scored options.
