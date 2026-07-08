# Research — Making the lighting LOOK good (overhead 2D sprite game)

> **Status:** RESEARCH / working doc. Distilled from 3 parallel deep-read agents (URP-2D building blocks ·
> why polished pixel lighting reads as polished · cozy case studies), ≥5 full sources + ≥1 studied project
> each, + an adversarial cold-critic pass that reordered the plan spine and caught pipeline/pixel-art gaps.
> Keeper conclusions graduate into `architecture_lighting.md`. Pairs with
> `research_lighting_dark_underground.md`.
> **Scope:** why our lighting looks flat vs good indie 2D games, and the specific, costed techniques that
> close each gap.

## 1. The diagnosis — why ours looks flat today (VERIFIED against the real assets)

Owner, verbatim: *"our lighting looks terrible compared to any other indie game… Even Apico… your approach is
as naive as it can get, just point and spot lights."* Verified against the actual project files:

- **Post-processing is OFF at the camera** — `SampleScene.unity:898` `m_RenderPostProcessing: 0`, and
  `UniversalRP.asset` `m_VolumeProfile: {fileID: 0}` (no scene Volume assigned). No post runs regardless.
- **The default Volume profile is the STOCK one, neutered — not "empty".** `DefaultVolumeProfile.asset` has
  every override present and `active:1` but at no-op values: Bloom `intensity: 0`, Tonemapping `mode: 0`
  (None), ColorLookup `contribution: 0`, Vignette `intensity: 0`, ColorAdjustments all neutral. Enabling the
  look = camera flag ON **and** dial real values in a scene Global Volume.
- **HDR is already ON** — `UniversalRP.asset:26` `m_SupportsHDR: 1`, camera `m_HDR: 1`. Bloom *can* catch HDR
  emission. But **`Renderer2D.asset:31` `m_HDREmulationScale: 1`** — at scale 1, **2D lights won't
  over-brighten past 1**, so bloom on the lamps themselves needs this raised. (And since the sprite pipeline
  authors **no** emissive sprites either — §4 — bloom currently catches essentially *nothing* but the additive
  lightning flash; raising HDR Emulation Scale is required for *any* lamp bloom.) And **`m_ColorGradingMode: 0`
  (LDR)** — clamps HDR before grading,
  blunting tonemapping/bloom; switch to HDR grading if we tonemap.
- **Raw point lights, default falloff, NO flicker.** `LampLight.cs` `Configure()` sets radius/color but
  **never sets Falloff Strength** (`m_FalloffIntensity`) → hard discs; and `Update()` is
  `intensity = _baseIntensity * (1 − Daylight)` with **no noise/flicker term** — dead-static lamps.
- **Flat per-sprite shading.** Every world sprite uses one shared `Sprite-Lit-Default` (`LitMaterials.cs:23`),
  **no normal maps, no emission maps** → flat light, no glow.
- **No grounding.** No contact shadows / baked AO. (`Renderer2D.asset` DOES ship Shadow Caster 2D shaders.)
- **`m_LightRenderTextureScale: 0.5`** — 2D lights render at half-res (a free soft-blur on pools).
- **No Pixel Perfect Camera** anywhere in `Assets/` or `Packages/manifest.json` — relevant to bloom (§3a).
- Good bones exist: `DayNightController.cs` — one Global Light2D, smoothstep day→dusk→night, warm dawn/dusk
  `(1,0.80,0.58)` vs moonlit-blue night `(0.35,0.42,0.75)`, night floor `0.20`, rain/drought/lightning tints.
  The problem is the **missing polish layer**, not the architecture.

> **Integration finding (`LampLight.cs:43`):** lamps fade as `1 − Daylight`, so **underground during the day
> they'd be OFF in a dark world** — the darkness system (other doc) must feed lamps a per-cell *local*
> darkness. `PlayerNightLight` (`:98`) already emits nothing without an equipped torch ("Terraria-style").

## 2. The polished-vs-naive "tells" (what your eye reads) — the acceptance rubric

All three look agents converged on this table. This is the "does it look good" checklist.

| Tell | Naive (us now) | Polished |
|------|----------------|----------|
| **Ambient** | Bright flat fill, neutral | **Dark, *colored* ambient multiplier** (dim cool/biome base), THEN light added back. Darkness is what makes light read *as* light. **← the #1 lever.** |
| **Light edge** | Hard disc (default falloff) | **Soft falloff** (Falloff Strength) or a baked soft-gradient cookie. |
| **Light life** | Dead-static | **Flicker** on fire/lamp lights (layered Perlin) — the cheapest cozy tell. |
| **Color contrast** | One color everywhere | **Warm key vs cool ambient** — temperature contrast = depth. (We half-do this via day/night.) |
| **Glow** | Bright pixels, no spread | **Bloom + HDR emission** — emission map, Bloom threshold ~1 / low intensity, + a Point Light on the emitter. |
| **Grounding** | Sprite floats | **Contact shadow / baked AO** under the sprite; **tinted**, never pure black. |
| **Shadow color** | (none) / black | **Color-shifted** shadows (cool/complementary). |
| **Mood** | Inconsistent | **One LUT grade + vignette** unifies the palette; optionally per-biome / per-weather. |
| **Form on sprites** | Flat | **Normal maps** — but expensive & unsupported by our pipeline; defer (§4). |

## 3. The recipe — the anchor is CONTEXT-SPLIT (day vs night/underground)

> **Correction (two rounds of critique).** Round 1 this led with "turn on Bloom" — wrong (bloom's glow payoff
> is gated behind emission tooling we lack, §4). Round 2 it swung to "dark colored ambient is THE universal
> anchor" — also wrong for a *mostly-daytime outdoor farm* benchmarked on Apico, whose overworld is **bright
> and flat-lit by day** ([APICO wiki: Time](https://wiki.apico.buzz/wiki/Time) — "during day time there's no
> special effects to the overworld"; dawn/dusk add warm glow + **god rays**). The honest answer splits by
> context:
> - **Daytime outdoor** (the dominant state): the cozy read comes from **palette grade + warm/cool contrast +
>   soft glow + light shafts (god rays)** — darkening does almost nothing at noon.
> - **Night / interiors / underground**: **dark colored ambient FIRST** is the anchor (it's what makes light
>   read as light; and it's the sibling darkness doc's whole domain).
>
> Below, Tier 1 is the cheap, always-on foundation; the darkness lever is scoped to the dark contexts, and the
> daytime look is carried by the grade/glow/shaft passes in Tier 2–3.

**Tier 1 — the cheap wins (tuning existing code, both contexts):**
1. **Dark, colored ambient — the anchor for night/interiors/underground.** Push the Global Light ambient
   toward a dim, slightly cool (or biome-tinted) base at night/underground so added lights pop. Pure tuning of
   `DayNightController` (which already creates/adopts one Global Light2D, `:66-89`, and drives it every frame,
   `:132-152`) — no new assets. (Daytime ambient stays bright; its look is Tier 2–3.)
2. **Soften the lights.** Set **Falloff Strength** on the Point Light2Ds, and/or swap to **baked
   soft-gradient cookies** (Orangepixel pre-renders soft radial light sprites — cheapest, most
   pixel-authentic). Layer **warm** placed lights against the **cool** ambient.
3. **Flicker on fire/lamp lights.** A few lines on `LampLight.cs`: layer fast Perlin (flicker) + slow noise
   (breathing) onto intensity. High cozy payoff for near-zero cost; provably absent today (`:43` has no noise
   term). (Pays off at night/underground — lamps fade to 0 by day, `:43`.)

**Tier 2 — turn on post + grounding (needs profile authoring / some tooling):**
4. **Enable post-processing** (camera flag + a scene Global Volume): **Bloom** (subtle — see §3a), gentle
   **Vignette**, subtle **Tonemapping/Color Adjustments**. Reveals the Tier-1 light.
5. **Contact shadows / AO grounding.** A shared **runtime decal ellipse** under grounded sprites (tinted, not
   black). *(NOT baked into sprite art — the pipeline forbids it; see §4.)*
6. **Emission maps** on glowing entities (`mushroom_glow`, lamps, fireflies) — **but re-costed: this needs new
   pipeline tooling** (§4), not "Low."

**Tier 3 — mood, atmosphere & consistency:**
7. **LUT color grading** (per-biome / per-time / **per-weather** — desaturate & cool in rain); vignette tuning.
8. **Atmosphere:** **god-ray / light-shaft overlays** (Apico's signature dawn/dusk tell — cheap additive soft
   beams; [APICO wiki: Time](https://wiki.apico.buzz/wiki/Time)); dappled/moving canopy shadow + drifting
   cloud-shadow overlays (the dominant *outdoor* cozy tell for a farming game); **light-catching particles**
   (dust motes / pollen / fireflies as particles).

**Tier 4 — selective, expensive:** normal maps on hero surfaces only, as an explicit owner decision (§4).

## 3a. Pixel-art integration (a failure mode the earlier draft ignored)

This is hard pixel art (Point filter, ≤8-color quantized, integer NEAREST upscale) and the owner benchmarks a
pixel-art game — yet **there is no Pixel Perfect Camera in the project.** Full-screen bloom haloes and softens
exactly the crisp edges pixel art depends on, and in a **top-down** game risks washing out gameplay
readability (crops/bugs/relevant glows). So:
- Keep bloom **subtle**, and confine what blooms the **native** way: a **high Bloom threshold + HDR emission**
  (>1) so only intended emitters trip it — NOT "scope bloom to a layer" (URP Bloom is a whole-camera Volume
  effect; true layer-scoping needs a custom ScriptableRendererFeature / second-camera composite — *more*
  engineering than the emission tooling, so only if genuinely needed).
- Decide the **Pixel-Perfect-Camera** question explicitly (add the component for crisp/stable upscaling, or
  accept the shimmer trade-off) **before** enabling full-screen post.
- Add **"readability at game zoom"** to the acceptance rubric — a look pass that hurts readability fails.

## 4. Normal maps + emission + grounding — scope against THIS pipeline

- **Defer normal maps** — and the real reasons are stronger than "animation needs a per-frame shader" (moot:
  world objects aren't animated yet). At ~16px logical, ≤8-color, flat sprites under a **single overhead
  light**, normals buy almost nothing; and **the gpt-image-1 pipeline authors no normal channel.** Reserve for
  a few hero surfaces at Fast quality, later, as an explicit owner decision — or defer entirely.
- **Emission maps are NOT "Low cost" here.** Pipeline A is `gen_sprites.py → pixelclean.py → make_scene.py`:
  a single flat RGBA sprite, k-means quantized to ~8 colors, NEAREST-scaled. There is **no emission/normal
  channel and no step that authors a secondary map.** Emission requires **new tooling** (derive an emission
  mask from the brightest quantized pixels in `pixelclean.py`, or a hand-paint pass). Re-cost accordingly.
- **Contact shadows = runtime decal only.** The pipeline's per-sprite acceptance checklist **forbids baked
  shadows** (*"no baked ground patch or cast shadow"*), so "bake AO into the sprite" is off the table for
  Pipeline A — a shared runtime decal is the only compliant path. (Shadow Caster 2D is available for
  *hero-occupant* real cast shadows, but weigh it vs the decal: top-down casts long weird shadows and costs
  more; the decal is cheaper and art-directable. Reason it, don't default silently.)

## 5. Case studies — the SPECIFIC mechanism each game uses (not "bloom + warm/cool")

| Game | The specific tell | Technique to borrow |
|------|-------------------|---------------------|
| **Apico** (owner benchmark) | Soft warm interior glow, gentle bloom, unified cozy palette | Dark ambient + warm point pools + subtle bloom + one grade. *(Could not source that Apico grades on rain — treat rain-grading as a general cozy lever, not an Apico fact.)* |
| **Stardew Valley** | Time-of-day palette shifts; warm window/lamp vs cool night; **dynamic-shadow mods** show the appetite for moving light | Per-time ambient palette (we have the bones) + dappled/cloud shadow overlays. |
| **Necesse** (top-down cave) | Dim readable cave ambient, warm torch pools, dark between | The darkness-doc mechanisms + soft cookies + warm/cool. |
| **Orangepixel titles** | **Pre-baked soft light sprites**, cheap bloom, strong ambient contrast | Baked soft-gradient cookies instead of raw falloff. |
| **Cozy pixel games (campfire/torch)** | **Layered-Perlin flicker** on fire lights | Tier-1 flicker on `LampLight.cs`. |
| **CrossCode / Hyper-Light-adjacent** | Strong emission + bloom, tinted shadows, graded palettes | Emission (once tooled) + bloom + LUT. |

## 6. Source table (deep-read; ⚑ = caveat)

| Source | Technique | Cost | Fit |
|--------|-----------|------|-----|
| Unity URP 2D docs — Light 2D (**Falloff Strength = edge softness**, verified), blend styles, Shadow Caster 2D | The URP-native light kit | Low | Our substrate; add cookies + Falloff + selective Shadow Casters. |
| Unity URP post-processing docs — Bloom, Color Adjustments, LUT (Color Lookup), Vignette, Tonemapping | The Volume stack; **OFF at camera today** | Low–med | Tier-2 win; ⚑ needs profile authoring, not "free." |
| Unity 2D **Pixel Perfect Camera** manual | Crisp/stable upscaling | Low | ⚑ absent here; decide before full-screen bloom (§3a). |
| Unity 6 **HDR Output** manual | ⚑ 2D Renderer + HDR *display* output requires post OFF | — | One-line caveat; not a blocker for SDR. |
| Orangepixel devblog | Pre-baked soft light sprites, cheap bloom, ambient contrast | Very low | Cheapest authentic softening. |
| Torch/campfire flicker roundups (MonoGame community et al.) | Layered Perlin flicker + slow breathing | Very low | Tier-1 flicker. |
| Stardew dynamic-shadow / dappled-light mods | Moving canopy + cloud shadows, evolve with time/weather | Med | Tier-3 outdoor atmosphere. |
| SpriteIlluminator / normal-map-for-2D | Authoring normal+emission maps | ⚑ high; **no pipeline support here** | Hero surfaces only; defer. |
| "Why good pixel lighting looks good" breakdowns | Dark colored ambient → add light; soft falloff; warm/cool; bloom+emission; tinted shadows; grading | Low–med | The rubric (§2). |
| Color-grading / LUT tutorials | Neutral-LUT (1024×32, matches `m_ColorGradingLutSize:32`); ⚑ Read/Write on, compression off, non-sRGB or artifacts | Low | Tier-3 mood; per-biome/weather. |
| Cozy case studies (Apico/Stardew/Necesse) | Palette shifts, warm-on-cool, intentional placed light, soft glow | — | Reference bar. |

## 6a. URP config prerequisites (a checklist the earlier draft omitted)

Before/with the post pass, verify: **(1)** URP-asset HDR on (already — `m_SupportsHDR:1`); **(2)** raise
`Renderer2D.asset` **HDR Emulation Scale** if lamps (not just emissive sprites) should bloom; **(3)** switch
**Color Grading Mode to HDR** if using Tonemapping (currently LDR `m_ColorGradingMode:0`); **(4)** LUT import:
Read/Write on, compression off, non-sRGB/bilinear; **(5)** camera `m_RenderPostProcessing:1` + a scene Global
Volume with real values (the default profile is neutered).

## 7. Recommended direction (reordered → scored candidates in the design doc)

1. **Dark colored ambient pass FIRST** (tune `DayNightController` — the anchor, cheapest, dominates).
2. **Soften + flicker** placed lights (Falloff / cookies; Perlin flicker on `LampLight.cs`).
3. **Enable post** — subtle, pixel-art-safe bloom (§3a) + vignette + tonemapping; resolve Pixel-Perfect-Camera.
4. **Grounding** — runtime contact-shadow decal (not baked); + emission **once the tooling is built** (§4).
5. **Mood + atmosphere** — LUT grade (per-biome/weather); dappled/cloud shadows; in-beam particles.
6. **Defer/scope normals** to hero surfaces as an explicit owner decision.

## 8. Decisions — RESOLVED (owner 2026-07-08; see `architecture_lighting.md`)

- **Mood:** distinct BugFarmer look, broadly like indie norms. **Apico is one example, NOT a target** — owner
  warned against over-matching it; its concentric-ring (stepped radial falloff) is the technique worth noting.
- **Bloom:** subtle. **Pixel Perfect Camera:** add it + subtle bloom, evaluate at game zoom (try-and-see).
- **Emission tooling:** deferred — bloom-on-bright-pixels + point-light-on-emitter for v1.
- **Normal maps:** skipped (flat ~16px top-down barely benefits).
- **Grading:** start with one global grade; per-biome/weather is a later enhancement.
