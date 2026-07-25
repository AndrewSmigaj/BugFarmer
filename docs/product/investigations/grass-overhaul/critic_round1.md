# Grass overhaul — adversarial cold-critic, round 1

Role: adversarial critic. Job = find what's WRONG or MISSING in the research pack so we don't ship a
shallow/flawed design. Every finding is checked against the REAL code and/or my own web research (cited).
Facts (verified) vs inference are flagged.

## VERDICT

The pack is **broad and mostly sound on the ART / game-survey side** — the core thesis (variant-per-cell
base + scatter + motion) is correct and its single load-bearing external claim (Necesse = 7 random variants
per cell) is **verified**. But it has **one critical, ship-threatening blind spot** and **several genuine
omissions**, and its **ranking is partly wrong**:

- **The #1 error is a performance hand-wave.** The synthesis rates the dense tuft scatter (lever B) as
  "MED feasibility… mostly a data/art task, not new tech" and says tufts "sway for FREE via LitWind." In our
  ACTUAL engine, rendering a dense tuft carpet through the occupant path is the single most expensive, riskiest
  lever — each tuft is a full GameObject with a collider, a second shadow GameObject, and a click target. This
  is not de-risked and it inverts the cost calculus of the whole plan.
- **The ranking over-sells the dense scatter (B) and under-sells the in-shader color/jitter stack (E)**, which
  in OUR engine is the cheapest, zero-GameObject, highest-anti-repeat win and needs no per-cell data plumbing at
  all (contrary to the pack's open "spike").
- **Genuine omissions:** normal-mapped 2D lighting on grass (the shader ALREADY supports it and the game is
  URP-2D-lit), persistent trampling trails, dithering-as-anti-banding, and a real noise-density placement spec.
- **The current "alive" state is overstated:** LitWind is a single global sine phased by world-X only, with no
  gusts, no per-instance phase, and no player-reactive bend — not the Stardew/Terraria effect the pack implies
  is "mostly built."

Bottom line: the design is directionally right but would ship a **flawed build order and a hand-waved perf
risk** if formalized as-is. Fixes below.

---

## FINDINGS (ranked by severity)

### 1. CRITICAL — dense tuft scatter through the occupant GameObject path will not scale (feasibility hand-wave)

**Claim in the pack (WRONG/UNDERSTATED):** synthesis lever B = "HIGHEST impact… **MED** feasibility — scatter
system + detail occupants exist; tufts already get `LitWind` sway"; our_current_grass.md §"Levers we already
have" = "a denser, better-tuned grass-detail pass is a config/data change, **not new tech**."

**What the real code does (verified — `TilemapManager.cs:1007-1130`, `RenderOccupant`):** every occupant is a
pooled **GameObject** carrying:
- a `SpriteRenderer` (individually Y-sorted: `sr.sortingOrder = -cellPos.y`, line 1074),
- a `BoxCollider2D`, enabled + sized to the sprite (lines 1110-1117),
- a **`BlobShadow` = a second child GameObject + SpriteRenderer** (lines 1099-1103) — and grass tufts are
  category **`natural`** (verified in `nakama/data/entities/occupants.json`: `tall_grass`, `fern`, `clover`,
  `flower_wild`, `bush`, `dandelion` all `"category":"natural"`), which is NOT in the `terrainOrWater`
  skip-list, so **every tuft gets a blob-shadow GO**,
- an `OccupantClickTarget`, plus a possible `LampLight` child.

So one "grass tuft" = ~2 GameObjects + 2 SpriteRenderers + 1 collider + 1 click target + individual sort.
Current scatter density is **0.08** (`tools/zonegen/features/scatter.py:19`, `density=0.08`) — i.e. sparse
decor. A Necesse/Stardew-dense carpet is ~0.5–1.5 tufts/cell. In a 256×256 zone even 30% grass = ~20k cells →
**tens of thousands of GameObjects** (culled to loaded chunks, but a player's loaded radius is still thousands).

**Web evidence (verified):** a Unity dev's 2.5D project ran **390–400 FPS with no grass, dropping to 35–40 FPS**
with grass GameObjects, and **even disabling the SpriteRenderers only recovered to 50–70 FPS** — i.e. the
GameObject/collider/transform overhead ALONE (not the draw) is the killer — at only **~1000** grass objects.
The universal recommendation is **`Graphics.DrawMeshInstanced` / `DrawMeshInstancedIndirect`** or a combined-
sprite/mesh layer, NOT individual GameObjects. (Sources: Unity Discussions "2D Grass objects and Performance";
toqoz.fyi "Drawing Thousands of Meshes"; danielilett "Six Grass Rendering Techniques".) Our occupant path is
HEAVIER than that dev's case (we add a collider + a shadow GO + a click target per tuft).

**Why it matters:** the pack's build order leads with a dense scatter as a cheap "data/art" task. In reality a
dense decorative-grass layer needs a **NEW batched, non-interactive render path** — `DrawMeshInstanced(Indirect)`,
a single combined grass mesh per chunk, or baking tuft silhouettes into the tile art — separate from the
interactive-occupant system (which is correctly designed for *breakable/harvestable* objects, not a carpet).
This is the thing to spike FIRST; it changes everything downstream. The blob-shadow-per-tuft and collider-per-
tuft must both be dropped for decorative grass.

---

### 2. WRONG RANKING — the in-shader color/jitter stack (E) beats the dense scatter (B) on cost/impact in OUR engine, and its "spike" is already resolved

**Claim in the pack:** synthesis ranks E (color) at **#3**, behind the dense scatter, and lists as an OPEN
spike: "can our custom chunk-loaded Tilemap feed per-cell data to a tint/dual-grid shader? (verify before E/D)."

**Why the ranking is off:**
- **Per-cell HSV jitter needs NO per-cell data path.** The ground is one Unity `Tilemap` with a single shared
  material (`TilemapManager.cs:135-136`, `LitMaterials.Apply(groundTilemap renderer)`). A custom ground shader
  can derive a stable per-cell value from `hash(floor(worldPos))` **in the fragment shader** — no CPU plumbing,
  no RenderTexture, deterministic across clients by construction. The pack treats per-cell data as a blocking
  unknown; for jitter it's a non-issue.
- **The art-directed macro-tint path is ALREADY PROVEN.** The water material is fed a data texture exactly this
  way: `_waterMat.SetTexture("_ShoreMask", _shoreMask)` (`TilemapManager.cs:962`). A low-freq tint field for
  grass (zahni's "2×2-px-per-tile tint map") drops into the identical pattern. The "spike" is effectively
  answered by code that already ships.
- It adds **ZERO GameObjects** (contrast finding 1). Given our proven GPU tile shaders, the cheapest, safest,
  highest anti-repeat win is: **variant-per-cell (A) + in-shader per-cell HSV jitter + macro tint (E)** — this
  is the true 80/20, not a dense GameObject scatter.

**Corollary omission — dithering as anti-banding.** The pack covers dithered *edges* (zahni) but not dithering
as **anti-banding on the macro-tint / HSV gradients themselves**: a subtle low-freq tint over a near-flat green
will visibly **band on 8-bit** unless you add ordered-dither/blue-noise in the shader. This is a required detail
for E to look good and is missing.

**Fix the ranking to:** A + E (shader color/jitter/tint) as Phase 1 (cheap, zero-GO, proven), THEN the batched
dense-scatter as Phase 2 (gated on the finding-1 render-path spike).

---

### 3. OMITTED LEVER — normal-mapped 2D lighting on grass, and the infrastructure already exists

**The omission:** the pack never mentions normal maps once, for either the base tile or the tufts.

**Why that's a real miss (verified):**
- The game is **URP 2D-lit** — day/night sun sweep + lamp `Light2D`s (grass tiles already `LitMaterials.Apply`
  to receive them). A flat grass sprite stays flat under a moving light; a **normal-mapped** grass tile/tuft
  gains real form as the sun direction sweeps and near lamps — this is the "depth / AO under tufts" the brief
  explicitly asked about.
- **We already have the pipeline for it:** `SpriteLitWorld.shader` declares `_NormalMap` (line 18) and ships a
  full **`NormalsRendering` pass** (lines 177-261). Normal-mapped grass is a texture-authoring task, not new
  shader tech.
- Ready-made top-down **normal-mapped grass/landscape tilesets** and **Aseprite normal-gen plugins**
  (mooosik normal-toolkit, securas Edge Normals; SpriteIlluminator; itch normalmap32) exist. (Sources: Unity
  Learn "2D Lighting for Pixel Art — normal maps"; gamemaker.io normal-map lighting; codeandweb SpriteIlluminator.)
- The pack cites **Moonlighter's "we do NOT use normal maps"** as if it settles the question — but Moonlighter
  fakes light by sprite superposition precisely because it is NOT a 2D-lit game; **we are.** The pack imported
  Moonlighter's conclusion without checking it applies to us.

At minimum this should have been evaluated and scored, not silently dropped. It's a legitimate high-polish lever
for a lit game and it's nearly free on our existing shader.

---

### 4. OMITTED "alive" idea + OVERSTATED current sway

**(a) Persistent trampling / flattened trails is missing.** The pack covers only springs-back player-bend
(Stardew rotational shake, aarthificial displacement mask). It never considers **persistent trampled paths** —
grass that stays flattened where you repeatedly walk, a well-known living-world technique the brief flagged.
Worth at least an evaluate/score pass as a cheap alive-factor (a per-cell "trample" value in the same in-shader
per-cell field from finding 2, decaying over time). (Web note: sparse public write-ups, but it's a real
technique in top-down/3D titles; flag as a candidate, not a must.)

**(b) The pack overstates that the "alive half is mostly done."** synthesis lever F = "MOSTLY BUILT — `LitWind`
already sways foliage." The **actual** shader (`SpriteLitWorld.shader:134`) is:
`posWS.x += sin(originWS.x * 0.6 + _Time.y * _WindSpeed) * _WindStrength * v.uv.y;`
That is a **single global sine phased by world-X only** — NOT the "**scrolling-noise gusts + per-instance phase
from full world position**" that `techniques_wind_color_depth.md` itself calls THE thing that stops a field
"breathing in unison." Tufts sharing an X column sway in lockstep. And there is **no player-reactive bend** —
the only extra term is `_HitBend`, an externally-set per-hit impulse (tree-wobble on being struck), not a
walk-through bend. So the marquee Stardew/Terraria reactive-gusty sway is **NOT built**; it's real new shader
work (a noise texture + per-instance seed + a player-position/velocity uniform). The pack should say "sway
EXISTS but is primitive," not "mostly built."

---

### 5. UNDER-EXPLORED — dual-grid vs. the existing shaped-ground system, and its true multi-terrain cost

**(a) Integration conflict not reconciled.** The ground is ONE Unity `Tilemap` whose per-cell ids also drive
**gameplay** (dig / walkability) and already feed the **`TileCompositor` shaped-ground** blend system
(`matA~matB~shape`, used where the shovel places blended ground — noted in our_current_grass.md). Dual-grid
requires a **second, half-offset render tilemap** while the logical grid stays authoritative, and it must either
**coexist with or replace** shaped-ground. The pack notes shaped-ground exists but never asks whether dual-grid
duplicates it, layers over it, or fights it. That's the load-bearing integration question and it's unanswered.

**(b) The "only 16 tiles!" pitch is for TWO terrains.** Verified: multi-terrain dual-grid "**requires multiple
layers**" (one per terrain in a priority stack) or an advanced 28-tiles-per-terrain variant. With grass / dirt /
path / sand / water that's **~4–5 stacked dual-grid layers = 60–75 authored edge tiles + N offset render
layers** — not the cheap "16 tiles" the ranking implies. (Sources: SpriteCook dual-grid; pablogila/TileMapDual
"use multiple layers for >2 terrains"; Excalibur dual-grid.)

**(c) So the transition-method ranking needs an explicit bake-off.** The pack's OWN Topic-2 finding rates
**overhang-fringe + dither** as the best-looking organic grass edge. Given (a)+(b), "dual-grid everywhere" is
not obviously the right default — a **fringe/overhang overlay + dither drawn over the existing shaped-ground**
may hit the same look with far less plumbing. Dual-grid is ranked as the pick without scoring this cheaper
alternative for OUR specific tilemap.

---

### 6. Density-by-noise placement is named but never turned into a mechanism

Lever B says "tuned density, random rotate/flip." But the lush look (Don't Starve, Necesse) comes from
**noise-driven CLUMPING + clearings + edge-following**, not uniform per-cell probability. Our `scatter.py`
ALREADY has a gaussian "field" density function (`tools/zonegen/features/scatter.py:43`, "blended gaussian bumps
→ patch density") — the pack should have connected to it and specified a real **noise-density spec** (clumps,
sparser near paths, denser in hollows). Leaving it at "tuned density" is exactly the "research doesn't change
pixels" failure — a rule with no code mechanism.

---

### 7. Minor claim caveats (verified — low severity, but fix the wording)

- **Necesse "7 variants/cell" = CONFIRMED.** Independent source confirms the grass sheet is 32×224 (= seven
  32×32 sprites) picked randomly per tile. The load-bearing claim for lever A holds. (Source: Necesse Steam
  grass-texture thread / wiki.)
- **`WeightedRandomTile` exists and IS a deterministic position hash = CONFIRMED** (it seeds RNG from the cell
  position, picks by weight, restores RNG). BUT it is a Unity **Tile ASSET for the Tile-Palette editor
  workflow**; our tiles are built at runtime (`TileDatabase.GetGroundTile` → `groundTilemap.SetTile`, a plain
  `Tile` cached per id — `TilemapManager.cs:976-978`). So we do NOT "drop in `WeightedRandomTile` near-free";
  we implement our own `hash(x,y,zoneSeed)→variant` at SetTile time. The pack's fallback ("or extend
  `TileDatabase`") is the correct path — just stop implying the Unity asset slots into our custom pipeline.
  (Sources: Unity 2d-extras `WeightedRandomTile.cs` / docs; DeepWiki 2d-extras Random Tile Types.)
- **AO/contact-shadow under tufts:** the pack proposes a per-tuft drop-shadow (techniques_wind_color_depth §4)
  and we have `BlobShadow` — but per-tuft that's another GO/SpriteRenderer (feeds finding 1). The cheaper,
  batched alternative — **bake a soft contact-AO darkening into the base of each tuft sprite** (and/or a single
  darkening term in the batched grass shader) — is not mentioned. Prefer baked AO over shadow GameObjects for a
  dense layer.

---

## PRIORITIZED FIX LIST (what the plan MUST change before it's trustworthy)

1. **[BLOCKER] Spike the dense-grass RENDER PATH before anything else.** Prototype `DrawMeshInstanced(Indirect)`
   (or a per-chunk combined grass mesh) for the tuft layer with NO collider / NO shadow-GO / NO click target.
   Budget it at target density in a 256×256 zone. The occupant system is the wrong tool for a decorative carpet.
   Until this is answered, lever B is NOT "MED feasibility."
2. **[RE-RANK] Lead with A + E (variant-per-cell + in-shader per-cell HSV jitter + macro tint + dither), not a
   dense GameObject scatter.** Close the "per-cell data" spike now: jitter = `hash(floor(worldPos))` in-frag (no
   plumbing); macro-tint reuses the proven `_ShoreMask` data-texture path. Add ordered/blue-noise dither to kill
   banding on the tint gradients.
3. **[EVALUATE] Score normal-mapped grass (tile + tufts).** The `_NormalMap` slot + `NormalsRendering` pass
   already exist; the game is 2D-lit. Author normal maps (Aseprite plugin) for the base tile and hero tufts and
   judge the depth win under day/night + lamps. Don't inherit Moonlighter's "no normal maps" — we ARE lit.
4. **[FIX WORDING + SCOPE] Reclassify sway as "primitive, real work remains."** Current LitWind = single global
   X-phased sine, no gusts, no per-instance phase, no walk-bend. Spec the upgrade (noise texture + per-instance
   seed + player pos/velocity uniform) and stop calling F "mostly built." Add persistent-trample as a scored
   candidate (cheap via the same per-cell shader field).
5. **[BAKE-OFF] Score dual-grid AGAINST fringe-overhang+dither-over-shaped-ground for edges, on OUR tilemap.**
   Resolve the shaped-ground/`TileCompositor` coexistence question and count the true multi-terrain tile/layer
   cost (4–5 stacked sets) before declaring dual-grid the transition method.
6. **[MECHANISM] Turn "tuned density" into a real noise-density spec** wired to `scatter.py`'s existing gaussian
   field (clumps, clearings, edge-following, sparser near paths) — a code mechanism, not a comment.
7. **[POLISH] Prefer baked contact-AO in tuft sprites over per-tuft shadow GameObjects** (feeds fix 1's budget).

Load-bearing claims I re-verified against source: Necesse 7-variant (CONFIRMED), WeightedRandomTile determinism
(CONFIRMED, with the asset-vs-runtime caveat), the occupant render cost (code: `TilemapManager.cs:1007-1130`),
the LitWind sway formula (code: `SpriteLitWorld.shader:134`), the water data-texture path
(`TilemapManager.cs:962`), grass occupant categories (`occupants.json`), scatter density
(`scatter.py:19`), and the 2D-grass GameObject perf cliff (Unity Discussions, quantified).
