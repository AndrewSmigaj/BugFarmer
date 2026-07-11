Good sweep across all four angles. Now let me deep-fetch the key sources in parallel, starting with the two open-source implementations and the technique deep-dives.

---

The dual-camera + Gaussian blur approach in the BigDaddyGameDev repo is directly relevant to our rendering question. Now let me pull the ACTUAL source code from both open-source repos, plus the official Terraria wiki and Unity URP docs.

---

The realcoloride example turns out to be a naive inverse-square-law demo, NOT the true Terraria flood-fill — an important discrepancy to flag. The BigDaddyGameDev tree needs the `main` branch. Let me get its actual C# code, plus find a source describing the REAL Terraria multi-pass directional spread, and read the Unity URP 2D docs.

---

Now I have the exact code paths. The key script is `TileFogController.cs`. Let me read the ACTUAL code, plus deep-read the Seed of Andromeda flood-fill tutorial (the canonical BFS + light-removal source) and get a working URP 2D lights doc.

---

`TileFogController.cs` confirms the architecture: it only maintains the solid/air tile data; the darkness is produced entirely by the render pipeline (second camera renders air as white → Gaussian blur → SpriteLightKit blend). Let me read the actual blur + blend shaders to nail the rendering path, get the SoA tutorial from its working mirror, and follow the Unity redirect.

---

I have deep reads across all angles. Two more targeted fetches to firm up the fit analysis: the URP 2D Light component reference (blend styles / Sprite Light / Global Light), and confirmation of Terraria's actual directional-sweep propagation (distinct from BFS).

---

Let me fetch the Unity forum thread on Starbound/Terraria-style lighting (a real implementation discussion) and the URP 2D light blend-styles doc to close the fit analysis.

---

Let me follow the redirect for the Unity thread and get the correct URP blend-styles doc.

---

I have deep-read the sources in full and studied the actual code of two open-source implementations. Here is the complete research report.

---

# Terraria/Starbound-style per-tile lighting — algorithm + real code

## Source table

| Source (url) | Concrete technique | Data structures | Perf / update cost | Fit to OUR constraints (URP 2D, cosmetic, top-down, have solid HashSet) |
|---|---|---|---|---|
| **realcoloride/TerrariaLightEngineExample** — `lightingengine.py` + README (github.com/realcoloride/TerrariaLightEngineExample) | **NOT a flood fill.** Per light: compute bounding box, then `brightness = intensity / distance²` (inverse-square) accumulated per tile. Single pass. README claims final render is "deferred shading: multiply lightmap texture against tile textures, optionally bilinear." | `Tile` objects in `[width][height]` list, each with `identity_brightness` float + `is_light_tile` bool; `Light{x,y,intensity,range}` list. | O(lights × range²). No incremental update logic; recompute all. | **POOR / mislabeled.** Light passes straight through solid tiles — it never reads a wall/solid map, so "buried vs exposed" is impossible. No sky concept. Ignore it as a propagation model; only its "multiply a lightmap texture with bilinear" rendering note is reusable. FLAG: this is not how Terraria actually works. |
| **BigDaddyGameDev/Tile-Light-and-Shadows-Like-Terraria** — real Unity/C# repo. Studied `Assets/TileShadows/Scripts/TileFogController.cs`, `Assets/_GaussianBlur/GaussianBlurFilter.shader`, `Assets/_SpriteLightKit/Shaders/SpriteLightKit-BlendImageEffect.shader` | **No per-cell propagation at all.** Two cameras: camera 2 renders every AIR cell as a solid **white sprite**; a **9-tap separable Gaussian blur** softens the white mask; then a **multiply blit** composites it over the main camera. Light "penetration depth" is tuned by the white sprite's **Pixels-Per-Unit**. | `TileData[,] _tiles` holding `TileType.SOLID`/`AIR` (built from the Tilemap; borders forced solid). Two `Tilemap`s (solid + air). Blur uses a downsampled RT; blend uses `_MainTex`, `_LightsTex`, `_MultiplicativeFactor`. | "Propagation" is just the screen-space blur, recomputed every frame. Digging = flip one cell solid↔air via `SetTiles()`; **zero propagation cost**, blur handles the spread. | **Strong architectural fit, but the code does NOT port.** The blend/blur are **built-in-RP image effects** (`Hidden/…` `CGPROGRAM`, `OnRenderImage`/stencil `Ref 2`) + prime31 **SpriteLightKit** — none of that runs under URP's 2D Renderer; you must reimplement it as a URP ScriptableRendererFeature/Blit or a Sprite Light. See fit notes below — this "render-open-cells-as-light, blur, multiply" model is the best fit for top-down. |
| **Seed of Andromeda — "Fast Flood Fill Lighting" pt.1 & pt.2** (seedofandromeda.com/blogs/29 & /30; readable mirror notverymoe.github.io/md-gamedev-gems/voxel/lighting/soa) | **Canonical BFS flood fill.** Seed source cell at max; FIFO queue; pop node, for each neighbor: if neighbor is transparent AND `neighbor.light + 2 <= current.light`, set `neighbor.light = current.light − 1`, enqueue. **Sunlight** = same BFS but going straight **down** does NOT decrement while at max (sky reaches infinitely down until an opaque block). Colored = 3 separate BFS (R/G/B, 4 bits each). **Removal BFS** (block placed): separate queue seeded with (cell, oldValue); zero cells dimmer than the front, re-queue brighter neighbors into the *add* queue, then re-propagate. | `struct LightNode{ short index; Chunk* }`; `struct LightRemovalNode{ short index; short val; Chunk* }`; light stored as `unsigned short[32³]` packed `SSSS RRRR GGGG BBBB`. Two `std::queue`s. | **Incremental & local**: placing/removing a block only touches the affected radius, not the whole map. Attenuation −1/step → a light of level 15 dies after 15 cells, bounding the work. | **Best algorithm fit** if you want true propagation. Everything ports (it's engine-agnostic). FLAG: its **sunlight/"exposed"** logic is gravity-based (down = sky). That concept is meaningless top-down — you must replace "seed sky at top row, flood down" with a **roof/overhead signal** (see prose). |
| **0fps — "Voxel Lighting"** (0fps.net/2018/02/21/voxel-lighting/) | Same BFS flood fill framed as an AO approximation ("propagate via BFS along the 6 faces, −1 per step, saturate to avoid underflow"). Advanced: pack R/G/B + multi-directional sky into a **32-bit word** and do component-wise max/decrement with **word-level-parallel bit tricks** instead of looping channels; samples sun along ±x and 45° diagonals for softer ambient. | 1 byte (Minecraft: 4-bit torch + 4-bit sky) up to 32-bit packed (`4 R + 4 G + 4 B + 5×4 sky`). BFS queue. | Same local BFS; word-parallel trick removes the per-channel loop. | Good conceptual reference; the 2D reduction is trivial (4 neighbors). Same top-down "sky direction" caveat. The 32-bit packing is overkill for a cosmetic grayscale darkness overlay. |
| **Official Terraria Wiki — Lighting mode** (terraria.wiki.gg/wiki/Lighting_mode) | Confirms the real engine. **New engine (White/Color):** light levels computed on **sub-tile pixel clusters** → smooth transitions + colored light in the source's hue. **Old engine (Retro/Trippy):** per-tile, blocky. All modes **spread with attenuation and decay more through solid tiles than air**. | Per-tile lightmap; new engine adds sub-tile samples. | Recompute only when a light-affecting object changes; multithreaded per-region in the shipped game. | Confirms the target look (smooth, colored, decays faster through solids). The real Terraria engine uses cache-friendly **directional linear sweeps** (L→R, R→L, T→B, B→T; each cell = `max(cell, neighbor − decay)`) rather than a queue — equivalent result, better for a dense rectangular window like ours. |
| **Unity Discussions — "Starbound/Terraria Style Lighting"** (discussions.unity.com/threads/…/325086) | Two techniques in one thread: (a) flood fill — *"starts at 3 and calls all directions decreasingly… when light hits a solid block it decreases the value; when it hits another light it takes the higher of the two"* (= BFS max/−1). (b) The exact **dual-camera Gaussian-blur blend** used by the BigDaddyGameDev repo. Advice: *"recalculate only if a light-casting object changes position."* | Per-tile values (implied array); blurred RT for the camera approach. | Only recompute on change; no metrics given. | Confirms both routes. Same top-down caveat on "sky." |
| **Unity URP 2D docs — Tilemap Renderer / Light 2D / Blend styles** (docs.unity3d.com … urp/2d) | URP 2D Renderer lights are **cookie/shape based**: Global, Freeform, Sprite (arbitrary sprite as the light shape), Spot/Point, each on a **Blend Style** (Multiply or Additive, per mask channel) targeting sorting layers. `Shadow Caster 2D` casts **hard shadows from collider silhouettes**, not per-cell flood. | Light2D components; blend styles; normal/mask maps. | GPU per light. | FLAG: URP's **built-in 2D lights don't propagate through a tile grid** and won't give "buried = dark." Do NOT try to model 160×160 cells as shadow casters. The URP-native way to inject *your own* computed lightmap is a **single Sprite Light 2D whose sprite = your lightmap texture (Multiply blend)**, or a **custom fullscreen Blit ScriptableRendererFeature** — that's the URP replacement for the repo's built-in-RP image effect. |

---

## 1) The multi-pass flood / propagation algorithm

There are two real families in the sources; the naive inverse-square example is a third that you should discard.

**A. Queue BFS flood fill (Seed of Andromeda, 0fps, Minecraft, the Unity thread).** Canonical and engine-agnostic:

- **Seed:** set each light-source cell to its max level (Minecraft 15, SoA 16). Push it to a FIFO queue. Sky-exposed cells are seeded at max on a **separate sky channel**.
- **Spread step (per popped cell, over 4 neighbors in 2D / 6 in 3D):** if the neighbor is transparent **and** `neighbor.light + 2 <= current.light`, then `neighbor.light = current.light − 1` and enqueue it. The `+2` test is the key idempotence guard — it stops cells that are already bright enough from being re-queued, so the BFS terminates quickly.
- **Falloff:** exactly **−1 per cell of air**. A level-15 torch therefore dies after 15 cells, which bounds the work. Terraria/this style decays **faster through solid tiles** than through air, so light only "leaks" a cell or two into a wall.
- **Passes/order:** BFS is inherently correct in a single breadth-first wavefront (nearest cells first). You don't run N fixed passes; you drain the queue once.
- **Colored light when covered:** run the algorithm **once per channel** (R, G, B), each 4-bit, blended by taking per-channel max — so a red torch behind a wall bleeds red; two overlapping colored lights add up per channel. 0fps packs all channels into a 32-bit word and does the max/decrement with bit tricks to avoid three loops.

**B. Directional linear sweeps (the actual shipped Terraria engine; the wiki's "New/Color" mode).** Instead of a queue, scan the visible rectangle in **four ordered passes — left→right, right→left, top→bottom, bottom→top**. In each pass every cell becomes `max(cell, neighbor_along_pass − decay)`, where `decay` is larger for solid/water than for air. Four sweeps propagate light in all directions; a couple of iterations converge. This is more cache-friendly than a queue for a dense window and is why Terraria can multithread it per screen-region. The "Color" engine additionally samples **sub-tile pixel clusters** (smaller than a tile) so transitions are smooth rather than blocky (the "Retro/Trippy" old engine is per-tile → blocky).

**C. (Discard) inverse-square point lights (realcoloride).** `brightness = intensity/distance²` inside a bounding box, summed. It never consults a solid map, so light passes through walls and there is no sky/buried concept. It is mislabeled "Terraria"; use it only as the mental model for the *final* "multiply a lightmap over the scene" step.

## 2) How "buried vs exposed" is decided

In the **side-view** games this is a **sky-light flood on a dedicated channel**: seed the top row of the world (or every cell with open sky above) at max, then flood with the −1 rule — **except straight down does not decrement while at max**, so a vertical shaft of sky reaches arbitrarily deep until an opaque tile stops it. A cell is **exposed** iff sky-light reaches it > 0; **buried** cells receive no sky and go black unless a torch's BFS reaches them. Terraria's decay-more-through-solids means one dirt tile above you already cuts most of the sky, so being "under a roof" reads as dark.

**FLAG — this logic does not survive the move to top-down.** Every source's "exposed" test assumes a gravity/down direction. In your **top-down** 256×256 grid there is no down in the render plane: an open field and a deep tunnel are both "open in 2D," so a sky-flood in the plane cannot distinguish them. You need a **separate overhead/roof signal**, not plane-openness:

- If you have (or can derive) an overhead layer — "is there a ceiling/canopy above this cell?" — seed darkness from roofed cells and treat roofless cells as sky-exposed. Your solid `HashSet` alone does **not** encode this unless a "roof" is a distinct tile type.
- If you have no roof layer, invert the framing (this is exactly what the BigDaddyGameDev repo does and it fits top-down cleanly): **darkness emanates from SOLID cells; open cells are ambient-lit.** Render/seed "light" wherever a cell is AIR, "dark" wherever it is SOLID, then let the blur/flood bleed darkness a cell or two past the walls. Interiors of solid masses (cave rock, inside a building footprint) are buried→dark; open ground is lit; the wall edge gets a soft falloff. This needs only your existing solid map and no notion of "sky."

## 3) Per-cell value → visible darkness on screen (the concrete render path each source uses)

- **realcoloride README:** *deferred/multiply* — build a lightmap texture, one texel per tile, **multiply** it against the tile textures, **bilinear** sample for smoothing. (Texture path.)
- **BigDaddyGameDev repo (actual code I read):** **screen-space blurred mask, multiplied.** Camera 2 renders every AIR cell as a white sprite → `GaussianBlurFilter.shader` (a quarter-res downsample pass + separable **9-tap horizontal** and **9-tap vertical** passes, weights `0.227 / 0.316 / 0.070`) → `SpriteLightKit-BlendImageEffect.shader` whose fragment is literally `return _MultiplicativeFactor * main * lights;` (a multiply; black mask → black scene). Light penetration depth = the white sprite's **Pixels-Per-Unit**. No per-cell array is ever lit — the blur *is* the propagation.
- **Terraria (wiki):** a **per-tile lightmap texture drawn stretched over the world with bilinear filtering** (that's the smooth sub-tile gradient), multiplied into the frame; Color mode adds sub-tile pixel-cluster samples.
- **Seed of Andromeda / voxel:** bakes the per-cell light into **mesh vertex colors** on the chunk mesh; hardware interpolation across triangles gives the smooth gradient (no separate lightmap texture).
- **Unity thread:** same **dual-camera Gaussian-blur multiply**, with one participant mentioning vertex colors and open uncertainty about the shader.

So the field splits into three render paths: **(a) upscaled+bilinear (optionally blurred) lightmap texture, multiplied** (Terraria, realcoloride); **(b) blurred screen-space mask from a second camera, multiplied** (BigDaddyGameDev, Unity thread); **(c) mesh vertex colors** (voxel/SoA).

## 4) Cost of updating when the player DIGS

- **BFS (SoA/0fps):** **incremental and local.** Digging a solid → cell becomes transparent → re-seed from the brightest neighbor / sky and propagate a bounded radius. Placing a solid → run the **removal BFS** (zero the front, re-queue brighter neighbors into the add queue, re-propagate). Work is proportional to the affected radius (≤ max light level), never the whole map.
- **Directional sweeps (Terraria):** recompute the dirty screen-region only, on change ("recalculate only if a light-caster moves").
- **Dual-camera blur (BigDaddyGameDev):** **essentially free per dig** — flip the tile solid↔air; the cameras + blur re-render every frame regardless, so there is no propagation to update.
- **Inverse-square (realcoloride):** re-sum lights overlapping the dug cell — but since it ignores walls, digging changes nothing visually; broken for this use.

---

## Fit to OUR constraints, with mismatches flagged

**Recommended path:** compute your **own** grayscale (or RGB, later) per-cell darkness on the ~160×160 render window from your existing solid `HashSet`, write it into a small `Texture2D` (e.g. R8, 160×160 or the full 256×256), then multiply it over the scene. This keeps darkness cosmetic/client-side and off the network, exactly as required.

- **Algorithm:** use the **BFS or 4-way directional sweep** (Sections 1A/1B), seeded by the **top-down-correct "darkness from solids" inversion** (Section 2), not the gravity sky-flood. At 256×256 = 65k cells a full recompute is sub-millisecond, and the 160×160 window is smaller still, so **you may not even need incremental digging updates** — a full window recompute per dig is fine. Incremental removal/add BFS is a cheap optional optimization if profiling ever demands it.
- **Rendering under URP 17 / 2D Renderer — pick one:**
  1. **Custom fullscreen `Blit` ScriptableRendererFeature** that samples your lightmap texture (point-source, bilinear-upscaled, optional small Gaussian for sub-cell smoothing) and **multiplies** it into the camera color. This is the URP-native re-implementation of the repo's `main * lights` blend.
  2. **One Sprite Light 2D** whose sprite is your lightmap texture, on a **Multiply blend style**, covering the window. Fully URP-native, no custom shader.
  3. A **screen-aligned quad** with a Multiply material carrying the lightmap texture (simplest).
- **FLAG — the BigDaddyGameDev code will not compile/run in URP.** Its blur and blend are **built-in-RP image effects** (`OnRenderImage`, `CGPROGRAM`, stencil `Ref 2`) plus **prime31 SpriteLightKit**; the 2D Renderer has no `OnRenderImage`. Port the *architecture* (render-open-as-light → blur → multiply) as a Renderer Feature; don't lift the files.
- **FLAG — do not use URP's built-in 2D lights for "buried = dark."** Global/Freeform/Sprite/Spot lights and `Shadow Caster 2D` are cookie/collider-silhouette based and do **no per-cell tile propagation**; modeling 160×160 cells as shadow casters is infeasible. Feed your **own** computed lightmap in instead (options above).
- **FLAG — top-down "exposed" mismatch (applies to every propagation source).** All of them equate "exposed" with sky reachable *downward*. You must supply a **roof/overhead signal** or use the **darkness-from-solids inversion**; plane-openness alone will light up deep tunnels as if they were open fields.
- **Colored light:** for cosmetic buried-darkness a **single grayscale channel** suffices (multiply dims uniformly). If you later want colored torches through cover, run the 3-channel (RGB) BFS and store an RGBA lightmap — the multiply blend tints for free.
- **Digging cost:** flip the cell in your `HashSet` → mark the lightmap dirty → recompute (locally via removal/add BFS, or just re-run the cheap window pass) → re-upload the small texture. Trivial at this grid size.

Net: adopt the **flood-fill/directional-sweep propagation** for the per-cell values (SoA/Terraria model), the **darkness-from-solids top-down seeding** (BigDaddyGameDev framing), and a **URP Renderer-Feature multiply of an upscaled, lightly-blurred lightmap texture** (Terraria's texture path, re-implemented for URP) as the on-screen overlay.

Sources: [realcoloride/TerrariaLightEngineExample](https://github.com/realcoloride/TerrariaLightEngineExample), [BigDaddyGameDev/Tile-Light-and-Shadows-Like-Terraria](https://github.com/BigDaddyGameDev/Tile-Light-and-Shadows-Like-Terraria), [Seed of Andromeda flood-fill lighting pt.1](https://www.seedofandromeda.com/blogs/29-fast-flood-fill-lighting-in-a-blocky-voxel-game-pt-1) / [pt.2](http://www.seedofandromeda.com/blogs/30-fast-flood-fill-lighting-in-a-blocky-voxel-game-pt-2) (mirror: [notverymoe archive](https://notverymoe.github.io/md-gamedev-gems/voxel/lighting/soa/index.html)), [0fps Voxel Lighting](https://0fps.net/2018/02/21/voxel-lighting/), [Official Terraria Wiki: Lighting mode](https://terraria.wiki.gg/wiki/Lighting_mode), [Unity Discussions: Starbound/Terraria style lighting](https://discussions.unity.com/threads/starbound-terraria-style-lighting.325086/), [Unity URP 2D Tilemap Renderer lighting docs](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/2d/tilemap-renderer-2d-renderer.html).