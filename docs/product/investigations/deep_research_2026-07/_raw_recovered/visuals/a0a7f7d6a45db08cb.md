Good hits. wick.works is the Apico developer's own devlog. Let me sweep more angles in parallel.

---

Rich source set. Now let me deep-read the highest-value sources in full and sweep remaining angles in parallel.

---

Deep-reads landing well. Now the implementation study (a real URP pixel-art post asset), atmospheric-perspective depth, and top-down-specific parallax confirmation.

---

I have deep-read 8 sources in full (including a real implementation study, ProPixelizer) and swept 10+ search angles. I have enough to synthesize. Here is the finished report.

---

# BugFarmer Look-and-Feel Research — Post-FX/Shaders & Parallax/Sky/Depth

**Scope:** Top-down cozy pixel farming/bug game, Unity 6 / URP 17.2, 2D Renderer, ~16px logical pixel art, day/night + weather. Excludes scene lighting (covered separately). Two categories: (A) Post-FX / material shaders, (B) Parallax / sky / depth.

**Bottom line up front — the honest priority verdict:**

- **Cheap high-impact wins (do first):** per-biome **LUT color grading** (Volume `Color Lookup`), **hit-flash material**, **screen-space scene transitions**, and an **animated day/night sky gradient** with **drifting cloud-shadow overlays**. All are low dev cost, low runtime cost, and directly serve "cozy + mood + time-of-day."
- **Tasteful-but-restrained (subtle or bust):** vignette (very light), sprite outline/rim, dissolve, ordered dithering, star/aurora night sky, distant scenery at zone edges.
- **Usually hurts pixel art — mostly skip:** chromatic aberration, strong bloom, heavy heat-haze as a global effect.
- **Side-scroller trick that does NOT translate to top-down (flagged in detail below):** classic **multi-layer horizontal parallax scrolling**. In top-down the camera looks down at the ground plane, so there is no receding horizon to slide layers against. The top-down substitutes are cloud-shadow overlays and off-map distant scenery at zone edges.

**The one tension that governs everything (crisp-pixel rule):** Any full-screen post that *spatially resamples* (blur, chromatic aberration, bloom, heat-haze) will smear your hard 16px pixels, especially if it runs on the pre-upscale high-res target with bilinear filtering. Effects that are *per-pixel color remaps* (LUT grading, vignette-as-darkening, tint) are safe because they don't move pixels. Keep camera anti-aliasing = **None** (ProPixelizer's guide is explicit: "None, for nice, crisp pixel edges"), and be deliberate about whether post runs before or after Pixel-Perfect upscaling.

---

## Source Table (URL → technique → cost → reference → fit)

| # | Source (URL) | Technique it informs | Cost (dev / runtime) | Reference game | Fit for cozy top-down pixel farm |
|---|---|---|---|---|---|
| 1 | wick.works/devlog/pixel-art | Art philosophy: outlines + transparency-animation over "fancy lighting" | Low / Low | **Apico (owner benchmark)** | High — validates clarity-first, restraint |
| 2 | slynyrd.com/…/pixelblog-23-parallax-scrolling | Parallax layers, integer scroll rates, "depth must exist statically" | Med / Low | Celeste (cited) | Low for gameplay plane; Med at zone edges |
| 3 | slynyrd.com/…/pixelblog-62-landscape-backgrounds | Atmospheric perspective / depth via scale | Med (art) / Low | — | Med–High for distant scenery |
| 4 | danielilett.com/…tut5-4-urp-dissolve | Dissolve material FX (Shader Graph) | Med / Low | — | Med (harvest/despawn poof) |
| 5 | danielilett.com/…tut5-5-urp-dither-transparency | Ordered dithering / screen-door transparency | Low–Med / Low | — | Med (retro fades) |
| 6 | gamedevbill.com/heat-haze-shader-graph | Heat-haze/refraction via Scene Color + noise UV offset | Med / Med | — | Low (situational only) |
| 7 | lindenreidblog.com/…heat-distortion-shader-tutorial | Grab/scene-color distortion mechanics | Med / Med | — | Low |
| 8 | sites.google.com/view/propixelizer/user-guide | **Implementation study:** appearance/outline pass, palette-LUT, dither, emission flash, Volume integration, AA=None warning | Med / Low–Med | — | High as a reference architecture |
| 9 | gamedeveloper.com/art/eastward-…pixel-art-adventures | Fog layers, sunbeams, bump maps, "3D game with 2D top-down perspective" | High / Med | **Eastward** | Ref only (their pipeline is heavier than yours) |
| 10 | 80.lv/articles/eastward-charming-chinese-pixel-art-adventure | LUT grading for storytelling + CRT/blur filters (secondary source) | Med / Low | Eastward | High for the LUT idea |
| 11 | docs.unity3d.com/6000.4/…urp/integration-with-post-processing | URP Volume overrides (Color Lookup, Vignette, Bloom, CA) | Low / varies | — | High (this is your delivery mechanism) |
| 12 | github.com/prime31/TransitionKit | Pixelate/wipe scene transitions | Med / Low | — | High (cheap polish) |
| 13 | forum.unity.com/threads/screen-wipe-in-urp.868615 | URP fullscreen wipe (0→1 param) | Med / Low | Pokémon/FF style | High |
| 14 | gameworldobserver.com/2023/…dave-the-diver-unity-2d-3d | 2D pixel + 3D env in URP + Shader Graph | High / Med | **Dave the Diver** | Ref only (hybrid scope) |
| 15 | gamedeveloper.com/design/kingdom-two-crowns…roguelike-design | Modern pixel art, day→night scenery, side-scroll parallax | Med / Low | **Kingdom Two Crowns** | Ref — but its parallax is the side-scroller trick |
| 16 | github.com/KhloeLeclair/StardewMods/CloudySkies | Weather/cloud/tint layering data model | Med / Low | **Stardew (mod)** | High for weather tinting |
| 17 | nexusmods.com/stardewvalley/mods/40483 (God Rays) | Moving sun-angle god rays | Med / Med | Stardew (mod) | Med |
| 18 | discussions.unity.com/…flashes-the-sprite-white/909679 | Hit-flash via lerp-to-white float | Low / Low | — | High (cheap win) |
| 19 | timcoster.com/…procedural-skybox…day-night-cycle | Animated sky gradient + star/cloud fade via HDR gradient + C# | Med / Low | — | High |
| 20 | steamcommunity/forums (Sun Haven vs Stardew) | Hi-bit vs 16px density tradeoff | — | **Sun Haven / Stardew** | Ref (sets your density bar) |

Confidence notes: rows 1–8, 11–13, 18–19 are primary technical/dev sources (high confidence). Row 10 (Eastward LUT/CRT) is a **secondary** claim — the primary Game Developer interview (row 9) confirmed fog/sunbeams/bump maps but did **not** explicitly confirm LUT or CRT, so treat "Eastward uses LUT grading" as reported-not-primary-verified. The "Celeste renders distant mountains at a coarser pixel scale" claim appeared in a secondary search summary only — **medium confidence**, use as a design idea, not a cited fact.

---

# CATEGORY A — Post-FX / Material Shaders

### A1. LUT color grading for per-biome/time-of-day mood — **Priority: HIGH (cheapest big win)**
- **Approach (concrete):** Add a global URP `Volume` with a **Color Lookup** override. Grade a representative screenshot in an image editor (or Photoshop/Aseprite), bake to a strip LUT (e.g. 32×1024 or a 256×16 2D LUT), assign it, and set **Contribution ≈ 0.4–0.6** so it tints without nuking your art's own palette. Author one LUT per biome (forest = cool green, desert = warm), and cross-fade LUTs / blend two Volumes for dawn→noon→dusk→night by driving `weight` from your day/night clock. This is exactly the "color grading for storytelling" approach attributed to Eastward (source 10) and shipped as pre-built device LUTs in ProPixelizer (source 8: NES/PAL/GameBoy LUTs generated in RGB-, HSV-, or value-space).
- **Cost:** Dev low (make LUTs from screenshots, wire one Volume). Runtime very low — it's a per-pixel texture lookup, no spatial resampling.
- **Reference game:** Eastward (LUT-for-mood, per source 10); ProPixelizer ships this as its core color-reduction stage.
- **Pixel-art gotcha:** LUT is **safe** for pixel art (no blur — it only remaps color). The real trap is over-grading: a heavy LUT can collapse two adjacent palette entries into one identical color, destroying pixel-cluster readability. Keep contribution moderate and eyeball that shadow/edge colors stay distinct. Also make sure grading runs on the final composited color, not per-sprite.

### A2. Vignette — **Priority: MED (use very lightly)**
- **Approach:** URP `Volume → Vignette`, **Intensity ~0.15–0.25, Smoothness high, rounded**. Optionally raise intensity slightly at night/indoors to cozy-up the frame. Works in all pipelines and is trivially cheap (docs, source 11).
- **Cost:** Dev trivial / runtime trivial (edge darkening multiply, no blur).
- **Reference game:** Common cozy-game framing; ProPixelizer explicitly supports vignette via Volume (source 8).
- **Pixel-art gotcha:** Because it darkens by multiply, at 16px a strong vignette *quantizes* — you'll see visible banded rings where the low-res palette can't represent the gradient. Keep it subtle; if banding shows, that's your cue you've gone too strong.

### A3. Chromatic aberration — **Priority: LOW (usually hurts — mostly skip)**
- **Approach:** URP `Volume → Chromatic Aberration`. If used at all, keep **Intensity ≤ 0.05** and gate it to transient moments (taking damage, dream/hallucination), never as an always-on look.
- **Cost:** Dev trivial / **runtime meaningful** — it's multi-tap and "expensive on mobile due to multiple texture samples" (source 1/11).
- **Reference game:** Common in hi-fi/action games, rare in cozy farming.
- **Pixel-art gotcha:** This is the archetypal anti-pixel effect. It deliberately splits R/G/B by sub-pixel offsets, which fringes every hard edge into colored blur — directly fighting the crisp 16px aesthetic. For a cozy farm, **flag as skip** unless it's a deliberate 1-second effect.

### A4. Bloom — **Priority: MED (restraint)**
- **Approach:** URP `Volume → Bloom`, low **Threshold** with low **Intensity (~0.1–0.3)**, applied so only genuinely emissive things (lamps, fireflies/bugs, night windows) glow. Pair with HDR emission on those sprites' materials.
- **Cost:** Dev low / runtime moderate (downsample/blur chain).
- **Reference game:** Hi-bit farming/adventure games use gentle bloom on light sources; ProPixelizer supports bloom via Volume (source 8).
- **Pixel-art gotcha:** Bloom is a blur pass — it *will* soften pixel edges around bright areas. Keep threshold high so it only catches intended emitters, and consider running it after upscaling so it blooms whole logical pixels rather than sub-pixels. Great for fireflies (fits a *bug* farm thematically); bad as a global glow.

### A5. Ordered dithering / palette reduction (retro authenticity) — **Priority: MED**
- **Approach:** Two uses. (1) *Retro shading:* Unity's built-in **Dither** node produces a 16×16 Bayer matrix; feed `Screen Position ÷ DitherSize` into it and into **Alpha Clip Threshold** for screen-door transparency (source 5) — gives authentic gradient-free shading/fades. (2) *Palette lock:* the ProPixelizer approach bakes a **4×4 ordered-dither pattern** (values 0–16) into a palette LUT so shading quantizes to your palette (source 8).
- **Cost:** Dev low–med / runtime low.
- **Reference game:** Retro-authentic pixel titles; ProPixelizer's appearance pass ships exactly this.
- **Pixel-art gotcha:** The Dither node keys off *screen* position, so if the camera moves the pattern can "crawl" on sprites. Anchor the dither to the sprite/UV or the pixel grid, and snap `DitherSize` to your integer pixel scale, or the dither dots won't line up with your 16px cells.

### A6. Sprite outline / rim shader — **Priority: MED (High if world reads muddy)**
- **Approach:** A Sprite-Lit/Unlit Shader Graph that samples neighboring texels (±1 texel in UV) and, where an opaque texel borders a transparent one, writes an outline color — or ProPixelizer's dedicated **outline pass** (draws an exterior outline "whenever two adjacent pixels have a different ID," 8-bit ID buffer, optional depth-tested to avoid overlap artifacts — source 8). Use for selectable/interactable objects and pop-out on hover rather than everything.
- **Cost:** Dev med / runtime low–med (extra samples or an extra pass).
- **Reference game:** Apico's benchmark note (source 1) praises Knytt's "solid black pixel outlines" that "clearly distinguish the ground from the background" — outline = readability, which is on-brand for the owner's taste.
- **Pixel-art gotcha:** A shader-generated 1px outline is measured in *screen* pixels, not *logical* pixels — at your upscale factor it can render as a fractional/blurry line. Either compute the outline in texel space at native res (before upscale) or hand-author outlines into the sprites (what Apico-style art usually does). Runtime outlines shine for dynamic selection highlights, not baked art.

### A7. Hit-flash material FX — **Priority: HIGH (cheap win, feels great)**
- **Approach:** Minimal Shader Graph on the sprite material: `Lerp(spriteColor, flashColor, _FlashAmount)`, expose `_FlashAmount` (0–1) and `_FlashColor` (usually white), spike it to 1 for ~0.05–0.1s via a coroutine `material.SetFloat` (source 18). ProPixelizer does the equivalent through `_EmissionColor` ("great for damage flashes," source 8).
- **Cost:** Dev trivial / runtime trivial.
- **Reference game:** Ubiquitous action/beat-em-up feedback; relevant here for chopping trees, catching/whacking bugs, hitting rocks.
- **Pixel-art gotcha:** Use a **material-property block or per-instance float** so flashing one bug doesn't flash all sharing the material. Flash by lerping to a flat color (no blur) so it stays pixel-crisp. Keep it to 1–3 frames — cozy games want a gentle "tick," not a bright strobe.

### A8. Dissolve material FX — **Priority: MED**
- **Approach:** Shader Graph: **Simple Noise → Step(threshold)** on alpha clip, plus a second offset Step to make a thin **HDR emissive edge** (Edge Width + Edge Color), driven by a `_Cutoff` float over time via `SetFloat` (source 4). Use for bug-catch "poof," crop harvest, or item despawn.
- **Cost:** Dev med / runtime low.
- **Reference game:** Common VFX pattern (the Ilett tutorial is the canonical URP recipe).
- **Pixel-art gotcha:** The tutorial targets 3D PBR; for your sprites, **quantize the noise to the pixel grid** (snap noise UVs to 16px cells) or the dissolve will erode in smooth sub-pixel curves that clash with hard pixels. A blocky, pixel-aligned dissolve reads far more "authentic" than a smooth one — this matches the community advice to dissolve "pixel by pixel."

### A9. Heat-haze / refraction — **Priority: LOW (situational only)**
- **Approach:** Sample the **URP Scene Color** node and offset its UVs by animated **Voronoi/sine** noise (`Strength ~0.001–0.005`, `Speed ~0.125–0.25`); clamp to a region with a smoothstep mask so only e.g. a campfire/desert-heat/water-surface zone wobbles (sources 6, 7). Requires Scene Color enabled on the 2D renderer (the modern replacement for old GrabPass).
- **Cost:** Dev med / runtime med (scene-color copy + per-pixel offset; a blur variant is "the most expensive," source 6).
- **Reference game:** 2D games use it on flames/desert/underwater; Dave the Diver-style water shimmer (source 14) is the closest cozy analog.
- **Pixel-art gotcha:** Refraction resamples the framebuffer with sub-pixel offsets — it *inherently* blurs and de-grids your pixels in the distorted area. For 16px art, **quantize the UV offset to whole logical pixels** so the wobble jumps in pixel steps (reads as intentional retro shimmer) instead of smearing. Reserve for small, rare zones (a single campfire, a hot-spring biome), not a global effect.

### A10. Screen-space scene transitions — **Priority: HIGH (cheap polish, big cozy feel)**
- **Approach:** A URP **Full Screen Pass Renderer Feature** driving a Shader Graph fullscreen material with a single `_Progress` (0→1) uniform: pixelate-out (TransitionKit's PixelateTransition, source 12), diamond/iris wipe, or Bayer-dither fade (reuse A5's Dither node). Trigger on door/zone entry, sleep, and day-rollover (source 13 — the classic Pokémon/FF wipe).
- **Cost:** Dev med / runtime low (one fullscreen pass while transitioning).
- **Reference game:** Pokémon/Final Fantasy style wipes; ideal for farm→mine→shop and the "go to sleep, next day" beat.
- **Pixel-art gotcha:** Make the transition itself pixelated (chunky diamond/iris or dither) rather than a smooth alpha crossfade — a smooth blend momentarily shows blurred half-opacity pixels. A pixelate-down transition is on-aesthetic *and* hides load hitches. Snap the effect's cells to your logical pixel size.

---

# CATEGORY B — Parallax / Sky / Depth (top-down realities)

> **Read this first — the side-scroller trap.** Classic multi-layer horizontal parallax scrolling (the SLYNYRD Pixelblog-23 technique, source 2) is fundamentally a **side-view** device: it works by sliding a distant *horizon/background wall* behind the play field, and its author explicitly notes the tutorial "focuses exclusively on horizontal side-scrolling parallax" and that "parallax may not be convincing if your scene doesn't already convey depth when static." In a true top-down farm the camera looks straight down at the ground plane — there is **no horizon and no background wall** to parallax against, so a full 3-layer scrolling parallax reads as a floating error, not depth. **Kingdom Two Crowns' gorgeous parallax (source 15) is a side-scroller trick — do not copy its layer model.** What *does* translate to top-down is below: cloud-shadow overlays (a "parallax" layer that lives *above* the ground), off-map distant scenery at zone edges, and painterly atmospheric-perspective depth. Everything in B is scoped to what actually works looking down.

### B1. Animated day/night sky gradient — **Priority: HIGH (core to your day/night pledge)**
- **Approach:** Drive a global ambient/tint from an **HDR gradient** keyed to your day/night clock (dawn/noon/dusk/night stops), the pattern in the ShaderGraph day-night tutorial (source 19: rotate sun value, animate star/cloud fade, expose to C#). In top-down you rarely *show* much sky, so this manifests mainly as (a) a global color multiply/ambient shift and (b) the color of any visible sky at zone edges (B4). Blend it with the per-time LUT (A1) so grading + sky agree.
- **Cost:** Dev low–med (one gradient + a clock hookup) / runtime trivial.
- **Reference game:** Kingdom Two Crowns' day→night scenery shift (source 15) is the mood target; Stardew mods (sources 16/17) smooth the transitions.
- **Pixel-art gotcha:** A smooth 24-bit gradient will **band** hard when the world is 16px. Either (a) quantize the gradient to your palette, (b) add ordered dither (A5) to the sky band, or (c) key only a handful of discrete tint steps across the day so transitions feel authored, not floaty.

### B2. Drifting clouds + cloud shadows on the ground — **Priority: HIGH (this IS your "parallax" for top-down)**
- **Approach:** A large, soft, tiling **cloud-shadow texture** rendered as a semi-transparent overlay that **multiplies** the ground, scrolling slowly across the map at a fixed world-space velocity (independent of the player) — plus optional brighter cloud sprites drifting above. This is the top-down-correct depth cue: the shadow layer lives *above* the play plane and its motion parallax vs. the static ground sells "sky above." Stardew's ecosystem models exactly this ("cloud shadow critters… occasional shadows moving around," and CloudySkies' weather/tint layering, source 16). Gate density/opacity to weather (thicker/faster on overcast).
- **Cost:** Dev low–med / runtime low (one scrolling multiply overlay).
- **Reference game:** Stardew Valley (cloud-shadow critters + weather mods, sources 16/17).
- **Pixel-art gotcha:** Scroll the overlay in **whole logical-pixel increments** in world space (integer step, same rule as SLYNYRD's "you can't move a half pixel," source 2) or the shadow edge shimmers/crawls against the pixel grid. Keep the shadow soft-but-quantized (dither its edge) so it doesn't read as a hi-res blob over pixel ground. This is a **cheap high-impact win** — it adds life to a static farm without any camera-parallax machinery.

### B3. Multi-layer scrolling parallax (classic) — **Priority: LOW for top-down (side-scroller trick)**
- **Approach (if ever used):** Camera-relative layers at integer speed ratios — SLYNYRD starts the furthest layer at 1px/frame and steps each nearer layer to the next divisor of the canvas width (1,2,3,4,6,8… for a 96px canvas), with seamless looping tiles (source 2). In top-down, the *only* defensible use is a thin off-map band at a zone edge (folds into B4), never under the walkable farm.
- **Cost:** Dev med (a ParallaxController + looping art) / runtime low.
- **Reference game:** Kingdom Two Crowns, Celeste — **both side-scrollers**; do not port their full layer stack.
- **Pixel-art gotcha / trap flag:** **Explicitly a side-scroller-only technique.** Under a top-down ground plane it produces sliding-carpet artifacts and breaks the "camera is directly overhead" contract. Sub-pixel layer speeds also shimmer. If you catch yourself parallaxing the ground, stop — use B2 (cloud shadows) and B4 (edge scenery) instead.

### B4. Distant parallax scenery at zone edges — **Priority: MED (the acceptable slice of parallax)**
- **Approach:** At the borders of a zone (past the walkable tiles) show off-map scenery — distant mountains, treeline, ocean, a far town — as 1–2 layers that scroll *slightly* slower than the world as the camera pans (a small camera-relative offset, e.g. 0.8–0.95× world speed). Because this sits beyond the play area and is viewed at a shallow implied angle, mild parallax reads correctly even top-down. Combine with B6 atmospheric perspective so it recedes convincingly (source 3).
- **Cost:** Dev med (edge art + a light offset script) / runtime low.
- **Reference game:** JRPG/adventure zone borders; Eastward's layered distant environments (source 9).
- **Pixel-art gotcha:** Keep the parallax factor gentle and integer-stepped; too much and the "ground" appears to detach from the "distance." Render distant layers at a **coarser effective pixel scale** if you want the "far things use chunkier pixels" look (Celeste is cited for this — *medium confidence*, treat as a stylistic option, not verified fact).

### B5. Star / aurora night sky — **Priority: MED (mood polish for night)**
- **Approach:** For the sky visible at zone edges / when looking up: a dark gradient with a **twinkling star** layer (scrolling noise thresholded to sparse dots, opacity animated) that fades in via the day/night clock — same HDR-gradient + star-fade rig as source 19. Aurora = a couple of soft, slowly-warping colored bands (Simple/Voronoi noise scrolling, additive, low opacity) reserved for a special biome/season.
- **Cost:** Dev med / runtime low.
- **Reference game:** Night-sky moments in cozy/adventure pixel games; the day-night skybox tutorial's animated stars (source 19).
- **Pixel-art gotcha:** Stars should be **pixel-snapped points**, not sub-pixel Gaussian dots, or they'll twinkle as blurry smudges. Aurora bands must be dithered/quantized to avoid smooth-gradient banding against the 16px world. Only meaningful if the player can actually see sky (edges/overlook), which top-down often hides — hence Med, not High.

### B6. Depth via scale + atmospheric perspective — **Priority: MED–High (art technique, powers B4)**
- **Approach:** Mostly an **authoring** technique, not a shader: for anything meant to read as distant (edge scenery, background hills), reduce contrast, **reduce saturation**, and **shift hue toward the sky/horizon color** with each receding plane; reduce texture detail and blade/cluster size with distance (SLYNYRD's rules, sources 2–3: "saturation reduces with each receding plane… hue shifts more to the color of the sky"). Optionally reproduce it cheaply at runtime with a distance-tinted material (lerp sprite color toward sky color by depth) so it tracks your day/night sky color automatically.
- **Cost:** Dev med (art discipline) / runtime trivial (a color lerp if done in-shader).
- **Reference game:** Eastward's fog layers / dawn-dusk atmosphere (source 9); standard hi-bit landscape practice.
- **Pixel-art gotcha:** With a tight palette (SLYNYRD's landscapes use **≤15 colors**, source 3), atmospheric perspective must be baked into the sprite palettes — you can't "fog" a 16px asset at runtime without muddying its few colors. Author distant tiers as separate, pre-desaturated palette ramps. This is what actually makes B4 convincing, so it earns the higher priority even though it's low-tech.

---

## Reference-game cheat sheet (what each actually teaches you)

- **Apico (owner benchmark, source 1):** The dev's own writing champions **clarity over effects** — "solid black pixel outlines" for figure/ground separation and "transparency + animation rather than lighting effects." Takeaway: your owner will prefer crisp readability (A6 outlines, restrained post) over showy shaders. The devlog is philosophy, not tech specs — it lists no resolution/palette numbers.
- **Eastward (sources 9, 10):** A **3D-rendered game with a 2D top-down perspective**, hand-painted bump maps, fog layers, dawn/dusk sunbeams; LUT-for-storytelling and CRT/blur are reported (secondary). Aspirational mood target, but its pipeline is far heavier than a URP 2D pixel farm — borrow the **LUT-for-mood** idea, not the whole engine.
- **Kingdom Two Crowns (source 15):** Beautiful modern pixel art with day→night scenery — but its parallax is the **side-scroller device**; a cautionary reference, not a blueprint for you.
- **Stardew Valley (sources 16, 17):** The realistic bar for a top-down farm — cloud-shadow critters, weather tints, god-ray/ambient mods. Your **B2 cloud shadows + A1 per-time LUT** essentially reproduce the beloved Stardew-mod look natively.
- **Sun Haven vs Stardew (source 20):** Density decision — Stardew is honest 16×16; Sun Haven spent 40%+ of its budget on more detailed "hi-bit" art. Pick your effective pixel density before layering effects, because outline/dither/dissolve all key off it.
- **Dave the Diver (source 14):** 2D pixel characters over 3D URP environments with Shader Graph — proof that URP + Shader Graph is the right toolchain, but its 2D/3D hybrid is out of scope for a pure-2D farm.
- **Celeste / Owlboy (sources 2, 9):** Side-scroller parallax + hi-bit polish; useful for atmospheric-perspective and "distant = chunkier pixels" ideas, but their depth model is side-view.

## Final prioritized build order (cheap→expensive)
1. **Per-time/per-biome LUT (A1)** + **light vignette (A2)** — one Volume, an afternoon of work, biggest mood delta.
2. **Hit-flash (A7)** and **pixelate scene transitions (A10)** — trivial code, huge "juice."
3. **Day/night sky gradient (B1)** + **drifting cloud-shadow overlay (B2)** — this is your top-down "parallax," and it directly serves the day/night + weather systems you already have.
4. **Sprite outline/selection (A6)**, **dissolve (A8)**, **ordered dither (A5)** — targeted polish.
5. **Zone-edge distant scenery (B4)** with **atmospheric-perspective art (B6)** + **star/aurora nights (B5)** — the expensive, art-heavy tier.
6. **Skip / gate hard:** chromatic aberration (A3), strong bloom (A4), global heat-haze (A9), and full-plane scrolling parallax (B3, side-scroller-only).