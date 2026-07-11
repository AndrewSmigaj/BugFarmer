# Visuals: Unity URP-2D lighting & rendering levers (project-grounded)

*Topic 4 of the 2026-07 research. Deep-read of 8+ Unity URP docs **plus the actual BugFarmerClient
project** (URP 17.2.0, our `Renderer2D.asset`, `DayNightController`, `LampLight`, `LitMaterials`). Every
lever below is version-verified for Unity 6000.2 / URP 17. Raw transcript:
`../_raw_recovered/visuals/ae56b9b076e43bd1d.md`. Extends the prior `research_look_and_feel.md` /
`research_lighting_look.md`, which this doesn't repeat.*

## Our actual setup (confirmed by reading the project)
- **URP 17.2.0, 2D Renderer.** `Renderer2D.asset`: `LightRenderTextureScale 0.5`, `MaxLightRT 16`,
  `MaxShadowRT 1`, `HDREmulationScale 1`, one **Multiply** blend style used (the perf optimum — docs say use
  only 1–2).
- **One Global Light2D** (Multiply) driven by `DayNightController` — night floor **0.20** → **1.0** day; tints
  moonlit-blue night → warm amber dawn/dusk → white day.
- **`LampLight` Point lights**, warm `(1.0, 0.97, 0.85)`, `Inner = 0.25×Outer` — **but no Falloff Strength set**
  → *this is the "hard falloff" ring you flagged.*
- **One shared `Sprite-Lit-Default` material** (`LitMaterials.Lit`) on every renderer — correct for batching;
  do **not** make per-sprite material variants.
- **HDR ON, post-processing OFF** (`m_RenderPostProcessing: 0`) → **no bloom can run today** even though HDR is on.

## The highest-leverage levers (ranked by uplift/effort)

| # | Lever | What it does | Effort | Perf | Notes |
|---|---|---|---|---|---|
| **1** | **Lamp Falloff Strength** (`m_FalloffIntensity` ≈ 0.6–0.9) | Feathers the hard lamp ring into a soft pool — **directly fixes the flagged "hard disc" look** | Trivial (one field) | Free | Pair with a slightly larger Outer + small Inner radius |
| **2** | **Turn on Bloom** (camera `RenderPostProcessing = 1` + a Global Volume with a Bloom override) | Lamps/emissive glow; the single biggest "cozy night" upgrade. HDR already on → only the camera flag + Volume are missing | Low | Downscale=Quarter, Max Iter cap = cheap | Threshold ~0.8–1.0, Intensity ~0.3–1, Scatter ~0.7. Bump key lights >Intensity 1 to make them bloom |
| **3** | **Warm-key / cool-ambient contrast** (already partly done) | Warm lamps against cool night ambient = the #1 "looks good" trick; lean into it more | Trivial | Free | Multiply-global (cool) + point lamps (warm) is exactly the right combo |
| **4** | **Sprite "cookie" lights** for lamps/lanterns | A soft radial-gradient sprite as a `Sprite`-type Light2D → art-directed soft pool / lantern teardrop / window rectangle shapes | Low | Same as point | Use when you want a *specific shape* or extra-soft edge beyond Falloff Strength |
| **5** | **Emissive accents** (additive HDR overlay sprites) | Make a *specific* part glow (flame, glowing eyes, fireflies) regardless of scene light — `Sprite-Lit-Default` has no emission channel, so overlay an additive over-1 sprite (or a Shader-Graph Lit sub-target with HDR Emission) | Med | Cheap per accent | This is how fireflies/torches self-glow into the bloom |
| **6** | **Shadow Caster 2D** on hero props | Real cast shadows (we set Global Shadow Strength 0.75 but nothing casts yet) | Med | +1 shadow RT | Use sparingly on landmark objects, not every sprite |
| **7** | **Normal maps** (Secondary Texture `NormalMap`) on a few hero sprites | Fake 3D relief that reacts to light direction | **High cost** | **Depth pre-pass per layer batch** | The expensive lever — restrict to ONE sorting layer / few hero sprites, use Light **Normal Map Quality = Fast** on small lamps, and measure |

## ≥4 scored candidates for "biggest visual uplift per effort" (lighting/render slice)
Axes: **visual impact · effort · perf on low-end · fits pixel-art** (1–5).

| Candidate | Impact | Effort | Perf | Pixel-fit | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Falloff Strength + Bloom + push warm/cool contrast** | 5 | 5 | 4 | 5 | **PICK — do first.** Near-zero cost, fixes the flagged hard lamps, adds glow; all three are config, not code. |
| **B. Sprite-cookie lamps + emissive accents (fireflies/torches)** | 4 | 4 | 4 | 5 | **PICK #2.** Art-directable soft light + real self-glow into the bloom. |
| C. Shadow Caster 2D on landmarks | 3 | 3 | 3 | 4 | Keep for hero props only; grounding for key objects. |
| D. Normal maps across sprites | 4 | 2 | 2 | 3 | REJECT as a blanket — depth-prepass-per-batch cost; only a few hero sprites, measured. |
| E. Per-sprite custom lit materials | 2 | 2 | 1 | 3 | REJECT — breaks the SRP/dynamic batching we rely on with many pooled renderers. |

## Anti-patterns (verified against our setup)
- **Adding blend styles** — each new blend style = a new full-screen light render texture every frame; stay at 1–2 (we're at 1).
- **Per-sprite material variants** — kills batching with our many pooled `SpriteRenderer`s.
- **Two enabled Globals** — both accumulate into the Multiply texture and pin the world bright (the "night isn't dark" bug our controller guards against).
- **Blanket normal maps** — the depth-prepass-per-layer-batch cost; not per-sprite-cheap.
- **Bloom that eats pixel art** — keep Threshold above mid-tones and Intensity modest so it glows lamps, not everything (the classic "bloom destroyed my pixel art" mistake).

## Open questions (owner taste — not guessed)
1. **How far off pure pixel-art are we willing to go?** Bloom + soft cookie lights + normal-map relief each
   nudge toward a "lit modern 2D" look rather than crisp flat pixels. Where's the line?
2. **Night mood target** — how dark/cozy? The night floor (0.20) + bloom intensity together set this.
3. **Which props deserve cast shadows / normal-map relief** (the expensive levers) — name the hero objects.

---
### Other visuals research recovered (see `README.md` in this folder)
This doc is the **lighting/rendering** slice. The **art-direction reference** (what makes Stardew/Spiritfarer/
Ori/etc. look rich; palette cohesion; making AI-generated sprites cohere) and the **Unity asset-packs survey**
were also researched overnight and survived as raw files — indexed in `visuals/README.md`, synthesis owed.
