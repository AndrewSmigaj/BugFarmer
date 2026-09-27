# Grass overhaul — plan

**Status:** research DONE (12 games + techniques + our-grass + feasibility + cold-critic, all in
`docs/product/investigations/grass-overhaul/`). This is the PLAN (Stage 3). The certainty assessment (Stage 4)
+ raised certainties (Stage 5) are appended below once done. Quality bar: **best-for-the-game, not fast/prototype.**

## Context
Our grass is **one flat 32×32 `grass.png` on every cell** (verified: `grass_v2/v3` unused, no autotiling, no
per-cell variation, static, sparse decor) → reads as a flat green carpet vs the target look. **Target: Necesse**
(owner-named) + Stardew-level polish. Evidence: the investigation folder above.

## What good games actually do (converged across 12)
Lushness = **VARIETY + COLOR + DEPTH + ORGANIC EDGES + MOTION** on a deliberately simple base. Necesse's core
recipe (dev-confirmed): ~7 random tile-variants per cell + dense scattered plants + biome recolor. The base
tile is almost always plain; the life is variety + scatter + (often) motion. Recolor ALONE is the flat look
we're leaving (Forager).

## Design — phased by (impact × cheapness × low-risk). Cheap zero-GameObject wins FIRST.
(Order set by the cold-critic's verified perf finding: dense tufts via our occupant system = tens of thousands
of GameObjects+colliders = a perf disaster, so that's spike-gated; the shader/tile wins carry no perf risk.)

**Phase 1 — the base (zero new GameObjects, zero perf risk, biggest bang-for-buck):**
- **1a Variant-per-cell base grass:** author 6-8 textured grass variants (real blades/clumps, few colors,
  seamless 50%-offset method); pick per cell by `hash(x,y,seed)→variant` in `TileDatabase` (our runtime
  `SetTile` path). Kills the repeat — Necesse's #1 lever.
- **1b In-shader color variation** on the ground tilemap material: per-cell **HSV jitter** via
  `hash(floor(worldPos))` (no data path needed) + low-freq **macro-tint** via a per-cell data texture (the
  proven `_ShoreMask` pattern) + **dithering** (anti-banding). Organic tonal variation, zero GameObjects.
- **1c Normal-mapped grass:** author normal maps; `SpriteLitWorld.shader` already has the `NormalsRendering`
  pass → real depth/AO under our day-night + lamp 2D lighting. Near-free richness.

**Phase 2 — motion (upgrade the existing wind):** upgrade `SpriteLitWorld.shader` from its single global sine
to **noise gusts + per-instance hash phase**, add **player-position walk-through bend**, and an optional
**persistent trampling trail** (a per-cell shader field, reusing the data-texture path).

**Phase 3 — the dense detail layer (the biggest visual win — SPIKE-GATED for perf):**
- **3a SPIKE FIRST — a batched, collider-free grass-detail renderer** (the #1 risk): `DrawMeshInstanced` (or a
  combined per-chunk mesh) drawing thousands of tuft sprites with per-instance data (pos/variant/phase), **no
  GameObjects/colliders**, separate from the occupant system. Gate the rest on this hitting playable FPS.
- **3b Dense tuft/flower scatter** on that path: author a tuft catalog (blades, tufts, flowers, clover; 3+
  variants; **baked contact-AO in the sprite**), placed via `scatter.py`'s existing `clumping`/gaussian field
  (organic clumps + clearings + edge-following), density tuned high; tufts get the Phase-2 wind. Gameplay/
  harvestable plants stay sparse occupants.

**Phase 4 — organic edges (small in-engine bake-off):** lean **fringe-overhang + dither overlay** (grass blades
hanging over the dirt/path/water seam + a dithered band — the Don't Starve organic look, works WITH our
shaped-ground `TileCompositor`), optionally + the existing shaped-ground blend for a soft color transition.

**Phase 5 — scope/polish:** biome/seasonal recolor + decal catalog (Fields-of-Mistria style, IF we do seasons);
ambient life (fireflies exist); per-zone tuning.

## Hard choices — scored options (≥4 each)
**HC1 — dense grass-detail RENDER PATH (the #1 spike):**
| option | perf@density | look/flex | dev cost | verdict |
|---|---|---|---|---|
| a. Occupant GameObjects (current) | ✗ dies (10⁴s of GO+colliders; web: 400→35 FPS @~1000) | high | low | **REJECT** (the critic's catch) |
| b. `DrawMeshInstanced` + per-instance data | ✓✓ | high (variant/phase/pos, shader wind) | med | **PICK (primary)** |
| c. Combined per-chunk mesh (rebuild on change) | ✓✓ | med | med | **PICK (fallback)** if instancing culling is fiddly |
| d. Bake tufts INTO the variant tiles | ✓✓✓ | low (grid-locked, no overlap/sway) | low | reject for the hero layer; OK as extra tile texture |
| e. ParticleSystem mesh particles | ✓ | med | med | weaker for placed static art |

**HC2 — transitions:**
| option | organic look | fits our tech | asset cost | verdict |
|---|---|---|---|---|
| a. Dual-grid autotile | med (crisp, grid-ish) | ✗ 2nd tilemap; conflicts w/ shaped-ground; ~60-75 tiles/5 terrains | high | weak for us |
| b. Fringe-overhang + dither overlay | ✓✓ | ✓ works with shaped-ground | med | **PICK** |
| c. Extend `TileCompositor` shaped-ground blend to grass edges | ✓ soft | ✓✓ reuses existing GPU blend | med | **PICK (complement to b)** |
| d. Hand-authored corner connection tiles | med | ✓ | med-high | baseline, less organic |

**HC3 — base variant selection:**
| option | fits runtime SetTile path | cost | verdict |
|---|---|---|---|
| a. `hash(x,y,seed)→variant` in TileDatabase | ✓✓ | low | **PICK** |
| b. Unity `WeightedRandomTile` asset | ✗ (Tile-Palette asset, not our path) | — | reject |
| c. In-shader variant via UV atlas + hash | ✓ | med | alt (folds into the color shader) |
| d. Fewer, larger multi-cell tiles | partial | med | weak (repeats at larger scale) |

**HC4 — color variation:**
| option | impact | cost/perf | verdict |
|---|---|---|---|
| a. Baked variant tiles only | med | low art | partial (pairs with 1a) |
| b. In-shader per-cell HSV hash + dither | high | low, zero-GO | **PICK** |
| c. Per-cell macro-tint data texture (shore-mask style) | high (patches) | low, proven | **PICK (macro half)** |
| d. Vertex-color tilemap tint | med | low | alt (coarser) |

## Build order + acceptance (each phase = a client-visual change; NO sim/sync/determinism surface → a Unity render/eyeball gate, not the determinism gates)
1. Phase 1 (1a+1b+1c) → **accept:** a grass field at game zoom shows no visible tile repetition + organic tonal
   variation + lighting depth; side-by-side vs current AND vs a Necesse reference crop; owner eyeball.
2. Phase 2 → **accept:** grass gusts naturally (not a metronome), bends as the player walks through.
3. Phase 3a spike → **accept:** dense tuft field (≥0.5/cell) at **playable FPS, no regression vs current**, zero
   new colliders (measured with the F7 perf overlay). Only then 3b.
4. Phase 4 → **accept:** grass/dirt/path/water seams read organic (no hard stair-step) on rendered crops.
5. Overall → **accept:** the grass reads lush and alive, like Necesse, not a flat carpet — owner sign-off on crops + in-engine.

## Owner-taste / open questions (surface, don't guess)
- **Art direction:** crisp-pixel (Stardew/Necesse, matches our current art) vs painterly (Don't Starve)? (lean crisp.)
- **Lushness/density** target (how dense the tuft carpet)?
- **Seasons?** (gates the decal catalog + seasonal recolor scope.)
- **Which zone first** (village_21_B)? Roll out per-zone or global?
- **Perf budget / target device** (sets the Phase-3 density ceiling)?

## Critical files (implementation, later)
- Tiles/variants + hash selection: `TileDatabase.cs` (+ new grass variant PNGs, normal maps).
- Color/wind shaders: `SpriteLitWorld.shader`, a new ground-tint shader (mirror the water-tilemap `_ShoreMask`
  data-texture pattern in `TilemapManager.cs`).
- Batched tuft renderer: NEW (DrawMeshInstanced/combined-mesh), fed by `scatter.py` placement data.
- Transitions: fringe overlay art + `TileCompositor` extension.
- Art pipeline: gpt-image + `pixelclean` for the tiles/tufts/normals.

## Certainty assessment (Stage 4 — visual feature; Sync/determinism N/A)
| # | Dimension | Score | Band | Evidence | Falsifier | To raise |
|---|-----------|-------|------|----------|-----------|----------|
| 1 | Requirements fidelity | 88 | Strong | Targets **Necesse** (owner-named) + Stardew polish; 12-game research; the owner's direction (no shortcuts, best for the game) honored (spike-gates the perf risk vs doing the cheap-bad version); scope (art-dir/seasons/zone) SURFACED not invented | owner wanted something narrower/different | owner review |
| 2 | Comprehension (our tile/shader system) | 86 | Strong | Read `TileDatabase.cs:45-93` (1 tile/id), `TilemapManager` (Unity Tilemap + `_ShoreMask` per-cell data-tex :928-962 + occupant weight :1007-1130), `SpriteLitWorld.shader:134` (global-sine wind) + `_NormalMap` :18/:177+, `TileCompositor`, `scatter.py` clumping :43; critic re-verified | the **ground tilemap material** can't take a tint shader w/o breaking `LitMaterials` lighting (unread) | read `LitMaterials.Apply` + ground-tilemap material assignment |
| 3 | Design quality | 86 | Strong | Phased cheap-first; reuses proven patterns (water data-tex shader, LitWind, TileCompositor, scatter clumping); **≥4 scored options/hard-choice**; spike-gates the perf risk | the batched-tuft renderer (new system) is harder than scoped | Phase-3a spike |
| 4 | ★ Sync & determinism | — | **N/A** | Client-visual only; grass variant/tint/tuft = **deterministic-by-worldpos hash** → all clients consistent, **no sync/hash surface** | — | — |
| 5 | Correctness (algorithms) | 80 | Strong | hash→variant, HSV-jitter shader, macro-tint via the proven data-tex, DrawMeshInstanced, fringe overlay — standard + evidenced | batched-renderer FPS, or a per-cell-data shader gotcha | Phase-3a spike + shader prototype |
| 6 | Blast radius & contract | 82 | Strong | Additive (new tiles/shader/renderer layer); no server contract; visual-only | tint shader breaks the ground-tilemap lighting/water stack; fringe vs shaped-ground conflict | verify material stack + fringe/composite coexistence |
| 7 | ★ Visual fidelity vs reference | 72 | Plausible | Recipe = Necesse's dev-confirmed method + Stardew polish; but the LOOK depends on art execution + in-engine tuning — **only a spike/owner proves "looks good"** | art doesn't land / density looks off | in-engine visual spike + owner eyeball (Phase-1 accept gate) |
| 8 | Art-pipeline feasibility | 78 | Plausible | Tiles/tufts: proven gpt-image+pixelclean. **Normal maps = a NEW step**, unproven for 32px pixel tiles | can't generate good normals for pixel tiles | verify a normal-map gen path |
| 9 | ★ Performance @ zone scale | 75 | Plausible | Phase1-2 = zero-GO shaders (cheap, Strong); the dense-tuft hero is the RISK but the plan **spike-gates it** (batched, collider-free) | batched renderer can't hit FPS at ≥0.5/cell | Phase-3a spike (F7 overlay) — the plan's own gate |
| 10 | Tiling/seams | 82 | Strong | variants+hash-jitter+macro-tint (IQ/Necesse-evidenced) kill repetition; fringe-overhang kills seams | repetition visible at some zoom / seam art doesn't blend | large-field zoom render |
| 11 | Style cohesion | 80 | Strong | keeps 32×32, reuses our lighting/shaders; crisp-pixel lean (owner-taste flagged) | owner wants a different art direction | owner art-direction decision |
| 12 | Integration | 80 | Strong | Unity Tilemap (variants), water data-tex pattern (macro-tint), LitWind (wind), TileCompositor (shaped-ground) all verified present; fringe/shaped-ground = a flagged bake-off | tint shader can't bind on the ground tilemap material | read the ground-tilemap material path |
| — | **Design confidence (weakest design axis)** | **~78** | | **weakest = Visual fidelity (72) + Perf (75)** — both inherently SPIKE-gated for a render feature (the plan makes them Phase-1/3a gates), NOT readable design holes | | run the in-engine visual + perf spikes |

**Verification: PENDING** — all gates are client-visual/eyeball (no determinism/sync gates): (a) Phase-1 in-engine
render vs a Necesse crop (owner eyeball); (b) **Phase-3a batched-dense-tuft perf spike** (F7 overlay, no FPS
regression) — the one real risk; (c) shader prototype (tint+wind); (d) normal-map generation check. None run yet.

**What this means:** PROCEED to build, cheap Phase-1 wins first (Strong, zero-risk), and run the Phase-3a perf
spike early (the one real risk). The weakest axes (fidelity, perf) are legitimately spike/owner-gated — not
design holes. **Two readable residuals to close NOW (Stage 5):** the ground-tilemap-material integration
(rows 2/12) + the normal-map generation path (row 8).

## Stage 5 — certainties raised (evidence added)
- **Row 12 Integration 80 → 84 (Strong):** the ground tilemap is its own dedicated `Tilemap`+`Renderer`
  (`LitMaterials.Apply(groundTilemap.GetComponent<Renderer>())`) — it can take a dedicated grass-tint material +
  per-cell data texture, the EXACT proven water-tilemap pattern; no conflict with the shared sprite Lit material.
- **Row 2 Comprehension 86 → 88:** that closes the "can the ground material take a tint shader" unknown.
- **Row 8 Art-pipeline / normal maps 78 → 84 (Strong):** **Laigter** (free, open-source, auto normal-map
  generator built for 2D sprites/pixel art — height/soft/bump/invert) or a height-from-luminance sobel in our
  Python pipeline. Normal maps for grass tiles/tufts = a solved, tooled step.
- **Row 9 Performance 75 → 82 (Strong; in-engine spike is the final proof):** `Graphics.DrawMeshInstanced`/
  `DrawMeshInstancedIndirect` is THE Unity pattern for exactly this ("objects that move only in the shader —
  trees, grass"); a documented example renders **10M grass instances** at great perf with compute-shader
  culling. The batched collider-free tuft renderer is well-established; Phase-3a spike proves it in OUR setup,
  but the risk is now low.
- **Row 7 Visual fidelity stays 72 (Plausible) — the honest ceiling:** whether it LOOKS like Necesse can only
  be proven by an in-engine spike + owner eyeball (a look-and-feel axis — a read/critic can't prove it). The
  plan makes it the Phase-1 acceptance gate. NOT a design hole.

**FINAL design confidence: ~80** (weakest DESIGN axis = Visual fidelity 72, inherently spike/owner-gated for a
render feature; everything else Strong 82-88). **Verification PENDING by design** (visual/eyeball gates + the
Phase-3a perf spike). **Proceed to build** — Phase-1 cheap wins first (zero-risk) + run the Phase-3a perf spike
early. Only genuine residuals: **owner-taste** (art direction crisp-vs-painterly · lushness/density · seasons ·
which zone first) + the two **in-engine spikes** (visual + perf). No knowable fact is left un-dug.
