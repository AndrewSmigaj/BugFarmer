# Research — Dark underground (buried blocks + roofed tunnels), top-down 2D

> **Status:** RESEARCH / working doc (throwaway-graduating). Distilled from 3 parallel deep-read agents
> (≥5 full sources + ≥1 studied codebase each) + an adversarial cold-critic pass that found and corrected
> three affirmatively-wrong claims (URP render path, roof-mask persistence, perf). Keeper conclusions
> graduate into `docs/product/architecture/architecture_lighting.md`. This doc records the *evidence*; the
> design doc records the *decision*.
> **Scope:** how to make (1) blocks not exposed to the outside read as dark, and (2) underground tunnels dark
> without a placed light — with an **organic, non-straight** boundary. Everything here is **cosmetic →
> client-side → zero sim/determinism impact.**
> **Engine (pinned — do not assume newer capabilities): Unity 6000.2.9f1 / URP 17.2.0** (verified in
> `ProjectVersion.txt` / `manifest.json`). Several URP 2D features cited below (mid-pipeline light-texture
> injection) exist only in **Unity 6.4+** and are therefore OFF the table for us — see §7 option 3.

## 1. The problem, stated precisely

Owner, verbatim: *"any blocks which are not exposed to the outside [should] be dark, like terraria… the
tunnels in the underground [should] be dark without lighting… our boundary between open areas and underground
areas is not a straight line so we can't just easily set up two lighting zones, the zones need to be in the
shape of the underground."*

Two distinct sub-problems needing **two distinct signals** (the crux the research settled):

- **(A) Buried-block darkness.** A solid mass (rock, dirt, inside a building) should be dark in its *interior*;
  digging reveals dark until light reaches. Signal available: our **solid map**.
- **(B) Roofed-tunnel ambient.** An *open* cell that is underground (has a ceiling / no sky) gets no day/night
  sun and stays dark. Signal available: **nothing in the 2D data today** — must be authored (see §6/§6a).

## 2. The target look (owner reference shots)

| Ref | What it shows | Element to reproduce |
|-----|---------------|----------------------|
| `terrdark.png` (Terraria) | Soft radial light bubble; everything beyond → **black**; buried tiles dark. | Smooth radial falloff + hard black floor beyond reach. |
| `neccdark.png` (Necesse, top-down) | Dim cave ambient, warm torch pools, dark between; boundary follows the carved shape. | **Top-down proof** a non-blocky shape-following darkness works in our exact perspective. |
| `minecdark.png` (Minecraft) | **Stepped** falloff from a torch; light decrements per cell. | The per-cell propagation model; we *smooth* the steps (Terraria "Color" mode), not keep them blocky. |

## 3. The load-bearing insight: top-down ≠ side-view (every source flagged this independently)

Shipped propagation algorithms (Terraria, Minecraft, Seed-of-Andromeda, 0fps) decide **"exposed to sky"** by
flooding sky-light **downward** (down doesn't decrement while at max → a vertical shaft reaches deep until an
opaque tile). **Meaningless in our top-down plane:** an open field and a deep tunnel are *both* "open in 2D,"
so plane-openness can't tell them apart. Copying Terraria's sky-flood would light our tunnels like fields —
the exact bug we're avoiding.

**Consequence:** sub-problem (B) needs a real **roof/overhead signal**, authored at generation, *not*
derivable from the 2D solid map. Sub-problem (A) does *not* — the solid map alone suffices via **seed
inversion** (darkness emanates from solids), which is top-down-safe.

## 4. The three mechanisms — and how they COMBINE (corrected)

| # | Mechanism | Solves | Signal | Runs |
|---|-----------|--------|--------|------|
| **1** | **Darkness-from-solids** — dark at every SOLID cell, lit at every OPEN cell, bleeding a cell or two past walls. Solid-mass interiors → dark; open ground → lit; wall edge → soft falloff. | (A) buried blocks | client **solid map** (`_blocksBugsZoneWide`) | client, cosmetic |
| **2** | **Roofed-cell ambient** — a per-cell `roofed`/`sees_sky` value; roofed cells fall to a dark cave floor **regardless of the day/night sun**. Follows the carved organic shape, stored **independent of walls**, so a dug tunnel keeps its roof and stays dark. | (B) tunnels | **new authored roof signal** (§6a) | authored → client |
| **3** | **Carried / placed light** — lamps, torches, player light, fireflies **add light back**, punching a soft bubble through 1&2. | reveal | existing `LampLight.cs` Light2Ds | client, cosmetic |

**How they combine is the crux, but it is LESS exotic than an earlier draft claimed.** The failure to avoid
is a **naive fullscreen multiply of the *finished* frame** — `(scene + torch) × darkness` turns a lit torch
pool black in a roofed cell (`darkness ≈ 0`). But you don't have to do that: **URP 2D already composites blend
styles as separate textures — a Multiply blend darkens, an Additive blend adds *after* the multiply**
([Light Blend Styles](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/LightBlendStyles.html)).
So darkness on the **Multiply** style + torches on the **Additive** style composite correctly *natively* — an
additive torch survives a multiply-darkened cell for free. Mechanisms 1&2 **reduce** (Multiply); mechanism 3
**adds** (Additive). The remaining risk is the *integration* (torches today sit on Multiply, not Additive —
§7a/N-note) and choosing between the native-blend-style path and a self-computed lightmap (§7a). It is the top
design risk, but it is solvable on our engine version without a custom 2D lighting pass.

**A correction from the URP audit:** you **cannot** implement mechanism-2 by "making the day/night Global
Light skip roofed cells." A URP **Global Light2D is uniform across its sorting layer and cannot take a
per-cell mask/cookie** ([Light 2D reference](https://docs.unity3d.com/6000.4/Documentation/Manual/urp/2DLightProperties.html));
only one global is allowed per blend style/sorting layer, and the project already runs exactly one
Multiply-blend global (`DayNightController.cs:68-71`, the fix for the old "night isn't dark" bug). The roofed
darkness must be its own per-cell contribution to the light field, not a global config.

## 5. Propagation algorithm — computing a per-cell darkness/light value

### 5A. Queue BFS flood fill *(Seed-of-Andromeda, 0fps, Minecraft)* — canonical, ports cleanly
Seed source cells at max, FIFO queue; pop a cell, for each 4-neighbor: if transparent **and**
`neighbor.light + 2 <= current.light`, set `neighbor.light = current.light − 1` and enqueue (the `+2` guard
gives fast termination). Falloff = −1/open cell, **decays faster through solids**. A **removal BFS** on
block-place makes digging incremental & local. Colored = per-channel BFS.

### 5B. Directional linear sweeps *(shipped Terraria "Color" engine)* — cache-friendly for a dense window
4 ordered passes L→R, R→L, T→B, B→T; each cell `= max(cell, neighbor − decay)`, decay larger for solids. A
couple iterations converge; Terraria multithreads it per screen-region. The "Color" engine samples **sub-tile
clusters** for smooth (not blocky) transitions — **the look we want**.

### 5C. Inverse-square point lights *(realcoloride example)* — **DISCARD as a propagation model**
`intensity / distance²` summed in a bbox; never consults a solid map → light passes through walls, no
sky/buried concept. Reuse only its final step: *multiply a lightmap over the scene, bilinear-sampled*.

**Choice:** 5A or 5B produce the same soft radial result. **Perf caveat (corrected — see §8):** the recompute
is only cheap on a **flat array**, not on the `HashSet` we currently hold. To be scored in the design doc.

## 6. The roof signal — RimWorld's model (solves the organic boundary)

RimWorld stores an explicit **per-cell roof** grid *separate from walls*, authored at map generation. Sun
applies only to no-roof cells; mining rock **leaves the roof bit**, so a dug tunnel is roofed → dark until you
build a light. The boundary is whatever shape the generator painted — **not tied to wall geometry** — so it
can be as organic as we like (Perlin-jittered, carved-cave-following). Perlin edge jitter + smoothstep
(Lexdev Civ-VI style) softens the mask edge so it isn't a blocky cell boundary.

### 6a. The roof-signal DATA PATH — this is a NEW end-to-end feature, not a free ride

**Correction:** an earlier draft claimed the client "reads the roof mask like the zone collision map via
OpCode 106." That is false and hid real work. Verified against the code:
- The save format writes **only** `{"chunk_x","chunk_y","ground","occupants"}` (`zonebuilder.py` `save()`);
  the builder's `surface`/`reserved` masks are **authoring-only and dropped on save**. There is no third
  per-cell array and no slot for one.
- **OpCode 106 carries a server-*derived* set** (`state.BlocksBugsCells()`, `match.go:2793`), computed from
  occupant `World.BlocksBugs` — **not** authored save data. It is the wrong wire for a roof mask.
- zonegen has **no roof concept**: `cave.carve_tunnel`/`carve_cavern` return a local `carved` set and nothing
  persists "this open cell is roofed."

So a roof signal spans **five real hops** — the design doc must treat it as a feature, not a footnote:
1. **Builder API** to record roofed cells (a third grid, or *derive* `roofed = interior of a carved region /
   an authored underground polygon` at save time).
2. **A new per-cell array** in `chunk_X_Y.json` (e.g. `roof`), OR a sparser encoding (see the alternative).
3. **A Go loader** change to parse it into the chunk struct.
4. **A wire path** — a new OpCode (or fold into chunk sync); **not** 106.
5. **Client hydration/storage** parallel to `_blocksBugsZoneWide`.

**Rejected alternative (kept as a documented dead-end) — derive `roofed` via enclosure flood-fill from a
sparse sky-seed.** The idea: flood OPEN cells reachable from a handful of authored "sky" seeds → "exposed";
unreachable → "roofed"; persist almost nothing. **Why it fails for us:** in a top-down farming game you *enter*
tunnels from the surface, so essentially every reachable tunnel connects to a sky-seed **through its mouth** —
a binary reachability flood therefore lights the *entire* tunnel as exposed (the common case, not an edge
case). The only obvious patch — attenuate the flood by distance from the mouth — is exactly the horizontal
sky-flood **§3 proves is meaningless in a top-down plane**. So the flood alternative reintroduces the precise
bug the whole design exists to avoid. **Conclusion: an authored roof signal is needed; the flood is not a
viable substitute.** (A *scalar* authored roof can still model mouths as a gradient — see below.)

**Scalar vs binary roof (from Core Keeper).** Core Keeper — a genuinely top-down dark-cave game — is
internally 3D and models **"roof lights / ceiling holes"**: natural daylight leaking through gaps in the cave
ceiling. That argues the roof signal might be a **scalar** (0..1 partial roof → shafts of daylight), not a
binary bit, so a cave mouth or a broken ceiling reads as a gradient of daylight rather than a hard edge. Open
question for the owner (§11).

## 7. Render path — putting a per-cell value on screen under URP 17 / 2D Renderer

Three on-screen techniques in the field:

| Technique | Who | How | Fit |
|-----------|-----|-----|-----|
| **(a) Upscaled bilinear lightmap texture, multiplied** | Terraria | 1 texel/cell in a small `Texture2D`, stretched, bilinear → smooth, multiplied. | Compute our own R8/RGBA lightmap; apply via a **Blit feature** (below). |
| **(b) GPU blur-as-propagation** | BigDaddyGameDev, Unity thread | Render solid/roof mask to a RenderTexture → separable Gaussian in a shader → multiply. The blur *is* the propagation. | **Co-primary** — GPU-side, so the CPU-flood perf question (§8) evaporates; it IS the blit feature we need anyway. The *sample C# won't compile under 2D Renderer* (built-in-RP `OnRenderImage`/SpriteLightKit) — port the technique, not the files. |
| **(c) Mesh vertex colors** | Seed-of-Andromeda | Bake per-cell light into chunk-mesh vertex colors; hardware interpolation smooths. | Re-plumbs our tilemap rendering; more invasive. |

**URP-native ways to apply our darkness, ranked by feasibility on OUR engine (Unity 6000.2 / URP 17.2):**
1. **[PRIMARY] Darkness as a Multiply-blend Sprite Light 2D (or Multiply contribution) + torches on the
   Additive blend style.** The native URP 2D path (§4): the Multiply style darkens roofed/buried cells; the
   Additive style adds torch/lamp light *after* the multiply, so lit pools survive dark cells for free. Works
   on 17.2, no custom pass. **Integration cost:** torches today have no `blendStyleIndex` set → they default
   to index 0 = **Multiply** (`Renderer2D.asset:34`), the same style as the global and the proposed darkness,
   where they'd fight it via the Overlap Operation. Moving them to a dedicated **Additive** style is a required
   (currently unmentioned) `LampLight.cs` change. **Caveat:** `m_LightRenderTextureScale: 0.5` → the light
   buffer is **half-res**; a Sprite-light darkness is soft (fine for gradients, not crisp cave-mouth lines).
2. **[FALLBACK] Self-computed *unified* lightmap → fullscreen Multiply Blit at `AfterRenderingTransparents`.**
   Compute one per-cell field that already includes BOTH the darkness AND the torch/lamp bubbles (Don't
   Starve model), upload as a `Texture2D`, and multiply the finished camera color once. Full res; total
   control over edges. **Cost:** this **abandons URP `Light2D` torches** (their light must be baked into the
   lightmap instead), and it's a per-frame carried-light pass (§7a option A). `Renderer2D.asset` has
   `m_RendererFeatures: []` — a clean greenfield add at a *supported* injection point
   ([URP injection points](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/customize/custom-pass-injection-points.html)).
3. **[NOT AVAILABLE on 17.2] Blit that injects darkness INTO the light-accumulation texture before sprite
   lighting.** There is **no injection point between the 2D light-texture phase and the sprite-lighting phase**
   until **Unity 6.4** ([2D lighting is two-phase](https://docs.unity3d.com/6000.4/Documentation/Manual/urp/Lights-2D-intro.html);
   [Unity forum: 2D custom-pass injection "isn't currently supported," added in 6.4](https://discussions.unity.com/t/how-to-inject-a-custom-renderpass-in-urp-2d-that-respects-sorting-layers-and-order/1641674)).
   An earlier draft made this the primary route — it cannot be built on our version. Revisit only if we upgrade.

**Occupant darkening (cave-mouth seam):** occupant sprites (trees, houses with multi-cell footprints) must be
darkened by the **same screen-space bilinear lightmap per-pixel**, not by their anchor cell — otherwise a tree
anchored in a dark cell reads uniformly dark even where its canopy overlaps lit ground. Tall/edge occupants at
a cave mouth are also an authored-placement concern.

**Two hard "don'ts":** (i) do **not** model 160×160 cells as URP 2D lights / Shadow Caster 2D for buried-dark
(cookie/collider based, no per-cell propagation) — feed our own lightmap; (ii) do **not** lift the
BigDaddyGameDev files — port the architecture as a Renderer Feature.

## 7a. Compositing model — order of operations (THE central risk)

The only truly-broken option is a **naive multiply of the *finished* frame** — that turns lit torch pools
black in roofed cells (§4). Everything else is a real candidate; the carried lights are moving `Light2D`s
(`LampLight.cs` `PlayerNightLight`/`LampLight` + the flashlight cone). Candidates, **re-ranked for our engine
version** (an earlier draft had this inverted — it made the unbuildable one primary):

- **(C) [PRIMARY] Native two-blend-style composite.** Darkness on the **Multiply** style, torches on the
  **Additive** style — URP 2D applies additive *after* multiply, so a torch reveals a warm pool in a
  multiply-darkened cell **natively, no custom pass, on 17.2**. The spike should target this first. Integration
  cost: move torches off the default Multiply style onto Additive (`LampLight.cs`; §7 option 1). Edge softness
  is limited by the half-res light buffer.
- **(A) [FALLBACK] Unified self-computed lightmap.** One per-cell field holds BOTH darkness AND the torch/lamp
  bubbles (Don't Starve model: fullscreen darkness with additive light-holes wherever lights exist); one
  Multiply Blit at `AfterRenderingTransparents`. Full res, total edge control, but **abandons `Light2D`
  torches** (bake their bubbles into the field) and is a per-frame carried-light pass. Use if (C)'s half-res
  edges or blend-style behavior prove unacceptable.
- **(B) [NOT ON 17.2] Inject darkness into the light-accumulation texture mid-pipeline.** No injection point
  until Unity 6.4 (§7 option 3). Off the table unless we upgrade.

**This subsection is the acceptance gate for the whole feature** — the spike must demonstrate "a torch reveals
a dark roofed cell to a warm pool while the rest stays black," starting with (C), before the design is called
done. It is solvable on our version; it is not free (the `LampLight.cs` blend-style change is real work).

## 8. Perf & the digging update (corrected)

- **The "sub-millisecond full recompute" claim was unbenchmarked and is likely FALSE on the data we hold.**
  The solid map is a `HashSet<Vector2Int>` (`TilemapManager.cs:40`); a 4-pass sweep over 65,536 cells is
  ~262k updates × neighbor probes ≈ ~1M `HashSet.Contains` per recompute. (`Vector2Int` implements
  `IEquatable`, so `Contains` does **not** box or GC-allocate — the cost is hashing + cache-misses, not GC —
  but it's still realistically **several ms**, not sub-ms.) Terraria ships a dedicated **Multicore Lighting**
  option precisely because tile-light recompute is its heaviest CPU task. **This is an estimate — measure it.**
- **The perf claim is only true with the right data layout.** Convert the HashSet to a flat `byte[65536]`
  (or `NativeArray`) grid **once per zone**, run the sweep/BFS over the array, and keep **Burst/Jobs** as the
  fallback. With that, a full window recompute is plausibly sub-ms — **but must be measured, not asserted.**
- **Or sidestep it entirely with §7's route (b)** — GPU blur-as-propagation moves the whole cost off the CPU.
- **Digging:** flip the cell in the grid → mark the lightmap dirty → recompute (local removal/add BFS, or the
  cheap window pass) → re-upload the small texture. Cheap *on the flat array*; expensive on the HashSet.
- **Memory:** one R8 (later RGBA) texture at cell res (256² = 64 KB) or window-sized. Negligible.
- **Determinism:** untouched — darkness never enters `ComputeStateHash`; it reads the already-synced solid map
  + authored roof data. No new sim input for mechanisms 1&3; the roof mask is authored zone DATA (like
  ground/occupants), not a runtime sim read.

## 9. Source table (deep-read; ⚑ = a flagged caveat / non-fit)

| Source | Concrete technique | Fit to us |
|--------|--------------------|-----------|
| Seed-of-Andromeda "Fast Flood Fill Lighting" pt.1/2 | BFS: seed max, FIFO, `n+2<=cur`→`cur−1`; removal BFS; RGB=3 BFS | Best algorithm fit. ⚑ its sunlight = gravity-down; replace with roof signal / solids-inversion. |
| 0fps "Voxel Lighting" | Same BFS; 32-bit RGBA word + bit-parallel max/decrement | Conceptual ref; packing overkill for grayscale. |
| Official Terraria Wiki — Lighting mode + Multicore Lighting setting | "Color" = sub-tile clusters → smooth + colored; decays more through solids; sweeps, multithreaded | Confirms target smooth look + 5B; ⚑ confirms recompute is CPU-heavy → §8. |
| BigDaddyGameDev/Tile-Light-and-Shadows-Like-Terraria (studied code) | 2-camera render-AIR-as-white → 9-tap Gaussian → multiply; dig = flip tile, blur handles spread | Strong architectural fit (the GPU-blur route + darkness-from-solids). ⚑ built-in-RP + SpriteLightKit → **won't port**; reimplement as a URP Renderer Feature. |
| RimWorld roof system | Explicit per-cell roof grid, separate from walls, authored at gen; sun only on no-roof; mining leaves roof | The model for mechanism 2 / §6a. |
| **Core Keeper** wiki (roof lights / ceiling holes; internally 3D) | Natural daylight leaks through **ceiling gaps** → scalar roof | ⚑ argues **scalar** roof, not a binary bit (§6a, §11). |
| **Don't Starve** light system (Klei) | Fullscreen darkness with **additive light-holes subtracted** where lights exist; a soft radial around the player | The simplest carried-light-in-caves primitive; matches §7a option A. |
| Unity URP 2D docs (Light2D, blend styles, Shadow Caster 2D, HDR emulation) | Global lights are **uniform, no cookie**; lights combine by Overlap Op (Add/Alpha); Multiply = how the accumulated texture applies | ⚑ kills "global skips roofed cells" + "Multiply sprite-light darkens for free" (§4, §7). |
| Unity Discussions "Starbound/Terraria style lighting" | Confirms BFS-max + dual-camera-blur; "recompute only on light-caster change" | Confirms both routes; same top-down caveat. |
| realcoloride/TerrariaLightEngineExample (studied code) | `intensity/distance²` in a bbox; multiply bilinear lightmap | ⚑ discard as propagation (ignores walls); reuse only the render note. |
| Lexdev Civ-VI-style fog-edge shader | Perlin jitter + smoothstep mask edge | Edge-softening for the roof mask. |

## 10. Recommended direction (corrected ranking → scored candidates in the design doc)

1. **Compute one client-side per-cell light field** from: mechanism-1 darkness-from-solids (flat solid array),
   mechanism-2 roofed-ambient (authored roof signal), mechanism-3 additive carried/placed light — via a
   **directional sweep / BFS on a flat `byte[]` grid** (measure the cost) **or GPU blur-as-propagation**.
2. **Author the roof signal in zonegen** as a real feature (§6a) — an **authored per-cell mask** (binary or
   **scalar**, scalar models cave-mouth shafts); the sparse-sky-seed enclosure flood is a **rejected**
   dead-end (§6a). Specify all five data hops.
3. **Composite via the native two-blend-style path (§7a option C, PRIMARY):** darkness on the **Multiply**
   style, torches moved to the **Additive** style — works on our URP 17.2, no custom pass. Fallback: a
   self-computed unified lightmap + fullscreen Multiply Blit (§7a option A) if half-res edges disappoint.
   **Do NOT** target the mid-pipeline light-texture injection (needs Unity 6.4). Spike option C first — that
   spike is the acceptance gate.
4. **Reveal with the `LampLight.cs` lights** — but note two required changes: move them to the **Additive**
   blend style (§7 option 1), and feed them **per-cell local darkness** (not global `Daylight`, which would
   leave lamps off underground during the day). *(If the fallback unified-lightmap route is chosen instead,
   torch light is baked into the lightmap and the `Light2D` torches are retired — pick one, not both.)*

## 11. Open owner-taste questions (surface, do NOT guess)

- **How dark is "dark"?** Terraria **pitch black** beyond the bubble, or a **dim visible floor** (Necesse) so
  the world stays readable while unlit? (Sets the darkness floor + whether unlit caves are navigable.)
- **Scalar vs binary roof / light shafts?** Hard cave-mouth line, or **Core-Keeper-style ceiling holes**
  leaking shafts of daylight (a scalar roof + Perlin gradient)? (Bigger data + render scope if scalar.)
- **Boundary edge feel:** crisp transition, or a soft gradient apron of dimming approaching underground?
- **Colored underground light** now (RGBA lightmap, torches tint) or **grayscale first**?
- **Player light underground:** match the existing "torch required, no free glow" stance (`LampLight.cs:98`),
  or grant a faint always-on player glow so caves are never fully black at the player?
