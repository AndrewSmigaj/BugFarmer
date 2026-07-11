# Visuals: Art direction & cohesion (the owner's core concern)

*Topic 4, doc 2 of the 2026-07 visuals research. This is the **art-direction** slice — WHY the best 2D
games read as rich, and (our specific risk) **how to make AI-generated sprites cohere** into one world.
It builds on `01_unity_urp2d_lighting_and_rendering.md` (lighting/render mechanics — not repeated here;
that doc OWNS bloom, LUT-as-a-lighting-lever, warm/cool ambient) and does NOT repeat
`../../research_look_and_feel.md` (particles, foliage, water, shadows, camera, post-FX, parallax — the
motion/FX catalog). Raw sources mined: `../_raw_recovered/visuals/a0a7f7d6a45db08cb.md`,
`a669498e088defe4d.md`, `a10a417503069e33a.md`. Owner benchmark: Apico. Engine: Unity 6000.2.9f1, URP 17.2,
2D Renderer; ~16px logical pixel art; gpt-image-1 single-frame sprites; a grass/wind pass is planned.
Verified project state: a `DefaultVolumeProfile.asset` exists but has NO LUT/color-grading, and
post-processing is currently OFF.*

## Bottom line up front
The owner's complaint ("other games look a lot more interesting than ours") is, on the evidence, **less about
missing effects and more about COHESION + DENSITY + MOTION**:
1. **Cohesion** — our sprites are generated in separate gpt-image passes, so their palettes, contrast, and
   implied light direction don't agree. The richest-looking 2D games force everything into **one value key,
   one temperature, one light direction** (Eastward's global LUT, Graveyard Keeper's tone-lock, Hollow
   Knight's near-monochrome). We have none of these unifiers today.
2. **Density** — a static AI tileset shouts equally everywhere and has zero motion. Rich games budget
   contrast (brightest pixels reserved for player/interactables), compose in **hero-prop vignettes over ~70%
   calm ground**, and layer "1000 tiny motions."
3. **The single cheapest cohesion lever we lack is a global color-grade LUT** — and the single biggest
   richness lever we lack is a **weighted-variant + scatter tile system** plus a **pervasive ambient-motion
   pass**. These three, not more shaders, are the recommendation.

---

## 1. Why the best 2D games look RICH — source table

*(Sources actually deep-read in the overnight research; confidence flagged. Perspective flagged because
several key tricks are side-view-only and DON'T transfer to our top-down pipeline.)*

| Game (source) | View | The art-direction TELL | Transfers to our AI top-down pipeline? |
|---|---|---|---|
| **Stardew Valley** (mentalnerd, anuflora — search-surfaced) | Top-down 3/4 | Cohesion from **constraint**: tiny fixed 16×16 grid + tight per-sprite palette = automatic family resemblance. Strong **outlines** do double duty (readability + meaning). Community itself calls the art a "mish-mash" — cohesion came from the constraint + outline discipline, NOT per-sprite fidelity. | HIGH — enforce the constraint GLOBALLY (pin resolution, palette, outline, light angle), don't chase per-sprite beauty. |
| **Eastward** (gamedeveloper.com; 80.lv) | Top-down 3/4 | **Global LUT color-grade** "makes the colors so much softer"; **split-by-material** construction (each object authored in parts by "natural structure" so each material takes its own value/light); "thousands of little touches." | HIGH — LUT is the cheapest cohesion win for a heterogeneous AI tileset; split-by-material is promptable. (Full 3D-bump rebuild is too heavy — approximate with baked directional shading + one light angle.) |
| **Sea of Stars** (megavisions) | Iso / near-top-down | Ambient life is the tell: animate "lights, fauna, and mechanisms," not just heroes → "come alive even when you can count every pixel." Permits a **wider-than-16bit palette** + colored highlights. | HIGH — "1000 tiny motions" = animate ambient PROPS. Wider palette permission fits AI output. |
| **Moonlighter** (80.lv) | Top-down dungeon | Light is **FAKED by sprite superposition** (layered translucent glow sprites), not lit. Richness = brute detail investment "here and there" (Ghibli-referenced) on a simple base. | HIGH (direct analog) — fake light pools with additive glow sprites; pipeline-agnostic. |
| **Graveyard Keeper** (cbr/paste — search-surfaced) | Top-down 3/4 | Praised as MORE cohesive than Stardew precisely because it **commits to one dark desaturated medieval palette**. Tone-lock = instant cohesion even with a mixed asset set. | HIGH — a tone-locked master palette is exactly what an AI mix needs. |
| **Coromon** (coromon.com/twinfinite — search-surfaced) | Top-down | "Modernized retro": keep 16-bit charm + add modern lighting/smooth animation + **varied vibrant biomes**. Per-biome palette variety prevents sameness while a consistent sprite "hand" holds it together. | HIGH (monster-farming-adjacent) — vary palette PER BIOME, hold the hand constant. |
| **Sun Haven** (review — search-surfaced) | Top-down | Richness = **clutter density**: "a lot of little clutter that just looks so cute," super-detailed chibi props + consistent proportion system. | HIGH — decoration density + a consistent proportion system. |
| **Spiritfarer** (radioactivesugar/medium) | Side-view | Interactables pop via **well-defined silhouettes** reading subtly against painted backgrounds; **pastel band carries EMOTION**. | MED-HIGH — silhouette-first readability transfers to any view; palette-as-emotion transfers. |
| **Ori & the Blind Forest** (Xbox Wire) | Side-view | Hero = near-pure-**white silhouette** against hyper-detailed high-chroma backgrounds → always instantly findable. Depth via 7,000 hand-painted layers (side-view parallax). | MED — the "reserve brightest value + highest chroma for player/interactables" rule transfers; the parallax depth does not. |
| **Hollow Knight** (Ari Gibson / Wikipedia) | Side-view | Near value-**monochrome** muted bluey-grey palette IS the cohesion device — one value key, a few saturated accents carry all focus. Hand-drawn scanned line = one authored "hand." | MED — the single-value-key idea + single-hand idea transfer; parallax does not. |
| **Wylde Flowers** (studiodrydock/supergenius — search-surfaced) | 3/4 (3D-rendered) | Not pixel art — cohesion from hand-painting **tileable textures with one unified brush/hand**. | Idea only — consistency of the "hand" matters more than the rendering tech. |

**Confidence:** Eastward (gamedeveloper primary; 80.lv secondary), Sea of Stars, Moonlighter, Spiritfarer, Ori
are primary deep-reads. Stardew, Graveyard Keeper, Coromon, Sun Haven, Wylde Flowers are search-surfaced
summaries (medium confidence — treat as design ideas). "Eastward uses a LUT grade" is reported, primary-ish
via 80.lv; the gamedeveloper interview confirmed fog/sunbeams/bump-maps but not the LUT explicitly.

### The five cross-cutting laws (why these beat a flat AI tileset)
1. **A global grade / master palette is the cheapest cohesion an AI pipeline lacks.** AI sprites arrive with
   mismatched palettes + lighting; the richest games force EVERYTHING into one value key + temperature (Eastward
   LUT, Graveyard Keeper tone-lock, Hollow Knight monotone). Do it once over the whole scene, not per-sprite.
2. **Contrast is BUDGETED, not uniform.** Reserve the brightest, highest-chroma pixels for the player +
   interactables; keep the world busy-but-lower-contrast (Ori's white silhouette, Spiritfarer's silhouette-pop).
   A flat AI tileset fails because every tile shouts equally — nothing leads the eye.
3. **"1000 tiny motions" separates a living place from a diorama — and it's mostly AMBIENT PROPS.** Fully
   top-down-compatible, and our biggest richness lever since a static tileset has zero motion by default.
4. **Material readability = split objects by material, each with its own value range** (Eastward's "natural
   structure" split). Prompt for objects lit from ONE consistent angle with distinct material values, not a
   flat blob — that's what makes brick read as brick next to tin.
5. **Cohesion is bought with CONSTRAINT + a single "hand," not per-asset fidelity.** Pin resolution, palette,
   outline treatment, and light angle as HARD global constraints; then vary palette per-biome and pile on prop
   density for richness. Cohesion from the constraint, richness from the density + per-biome variety.

---

## 2. Making our AI-generated sprites COHERE (our specific risk) — the concrete pipeline

This is the heart of the doc. Our sprites come out of separate gpt-image passes, so they disagree on palette,
contrast, and implied light direction — which reads as "a pile of assets," not "one world." The fix is a
**cohesion sandwich**: constrain the INPUT (prompt), clamp the OUTPUT (palette), and unify at the END
(engine LUT). No single lever is enough alone; together they are decisive. Cohesion comes from CONSTRAINT +
a single hand, not per-sprite fidelity (§1, law 5).

**The core principle (why palette-lock works).** "A game looks cohesive when the mathematical distance between
colors is strictly regulated… if [assets] are mathematically clamped to the exact same 8-color palette, the
human eye will instantly group them together as belonging to the same universe." *(pixie.haus, "Engineering
Cohesion in AI Pixel Art" — deep-read.)* The brain reads style primarily through color math, so forcing every
sprite onto ONE limited master palette is the strongest, cheapest unifier we can add.

### The pipeline (ordered — do the cheap engine lever first to PROVE it, then the durable input/output fixes)

**Stage 0 — Author a master palette FIRST (the shared color law).** Build one limited palette of hue-shifted
ramps up front (SLYNYRD: a ramp shifts value AND hue ~+20° per step, saturation peaks mid-ramp, avoid
high-sat+high-bright together; a full master palette ≈ 8 ramps × ~9 swatches, plus desaturated neutrals — but
*start smaller*). "Because of the hue shift every color is surrounded by colors that can work together"
(SLYNYRD pixelblog-1 — deep-read). Host it on Lospec/in `style.json`. This is what every later stage snaps to.

**Stage 1 — Global engine LUT (the one-day cohesion PROOF — do this first).** Add a URP **Color Lookup**
override to the existing `DefaultVolumeProfile` (verified present, currently no grading) and flip camera
post-processing on. Bake ONE LUT from a graded screenshot; set Contribution ~**0.4–0.6** so it tints without
collapsing adjacent palette entries. This pulls every on-screen sprite — however mismatched — through ONE color
response in a single pass. It is near-free, reversible, and (per the lighting doc's independent conclusion) the
single biggest cohesion return available. **Recommendation: prove cohesion with a LUT + before/after zone
render before investing in the harder input/output fixes.** *(This lever is co-owned with
`01_unity_urp2d_lighting_and_rendering.md`; it's listed here because it is ALSO the cheapest cohesion lever.)*

**Stage 2 — Prompt anchoring (constrain the INPUT).** Treat the gpt-image prompt as **80% static architecture +
20% variable subject** (pixie.haus). The static 80% — kept byte-identical across every asset — pins:
perspective (top-down 3/4), the **outline rule**, the **shading/lighting type**, and **ONE light direction**
(see Stage 4). The variable 20% is only `[subject]` + `[primary material/color]`. This is exactly our
`tools/art/style.json` (global) + `catalog/*.json` (per-item) split — so we already have the machinery; the
work is making the static block strict and complete. Optionally **seed-lock**: "if you find a sprite… that has
the exact shading technique and line weight you want, copy its seed" to reuse the same computational "hand."

**Stage 3 — Post-generation palette clamp (clamp the OUTPUT — the mathematical unifier).** After generation,
snap every sprite's colors to the Stage-0 master palette (nearest-color quantization / palette index map).
This is the "mathematically forces every pixel to snap to a pre-approved list of hex codes" step. It belongs
as a **new stage in `pixelclean.py`** (which already owns downscale/cleanup), applied targeted (per the
"regen tools clobber art" memory — never bare). This is the step that makes two sprites from two different
generations read as one universe.

**Stage 4 — Enforce ONE light direction.** Pick a single light direction and reject/regenerate any sprite that
disagrees — "the overall visual cohesion that makes work look professional is more important than individual
asset quality… decide on a light source direction before shading; mark an arrow on the canvas." Convention is
**upper-left**; pure top-down often uses **straight-top** (top of objects lighter, bases darker). *We must
lock ONE* (surfaced as an owner question, but recommend **upper-left** — the pixel-art default, and it reads
as gentle sun rather than flat noon). Bake it into the Stage-2 static prompt block so the AI shades
consistently, and it also agrees with our lamp/point-light setup.

**Stage 5 — Gradient-map rescue for stubborn sprites.** When an individual sprite's palette still fights the
set, a **gradient map** remaps it by LUMINANCE (ignoring its original hue/sat) onto the master ramp: darkest
value → darkest palette color, midtones → mid, highlights → brightest, with stops at 1/4-1/2-3/4 (3–5 stops
typical). "This unifies disparate sprites to one palette while preserving detail better than automatic color
conversion." *(Cage's Corner gradient-map tutorial — deep-read.)* Use per-material (a green ramp for foliage,
a brown ramp for wood) as a targeted fix, not a blanket pass.

### Engine levers vs pipeline levers (both halves of the sandwich)

| Cohesion lever | Where it lives | Effort | Why it works |
|---|---|---|---|
| **Global Color Lookup LUT** (Contribution 0.4–0.6) | Engine — URP Volume | Very low | One color response over the whole scene; hides palette mismatch in one pass |
| **Warm/cool day-night global tint** (already half-done) | Engine — `DayNightController` Global Light2D | Trivial (lean in) | A second global unifier that compounds with the LUT |
| **Master palette + post-gen quantization** | Pipeline — `pixelclean.py` + `style.json` | Med | The mathematical clamp: every pixel snaps to shared hex codes |
| **Prompt anchoring (80/20) + seed-lock** | Pipeline — `style.json` / `catalog/*.json` | Low–med | Constrains the AI to one stylistic region + one "hand" |
| **One light direction** | Pipeline — static prompt block + QA reject | Low | Aligns implied lighting so surfaces read as one world |
| **Gradient-map per-material rescue** | Pipeline — manual/targeted | Low per-asset | Forces an off-palette sprite onto the master ramp by value |

The engine LUT is the fastest *proof*; the pipeline palette-clamp + prompt-anchor is the durable *cure*. Do
the LUT this week; fold the palette clamp into `pixelclean.py` as the structural investment.

---

## 3. Tile variety / anti-repetition (the #1 "AI prototype" tell)
*[from a10a417503069e33a.md — draft below, may supplement]*

The "samey grid" is the single biggest tell of an AI-generated prototype and the cheapest to fix.
1. **Weighted variant tiles.** Author each base material as a *set* of 3–6 interchangeable variants; the zone
   builder resolves each cell to a variant by weight (e.g. 85% plain, 15% split across detail variants). Kills
   the checkerboard. (Tilesetter behavior model — search-surfaced.)
2. **A separate scatter / decal layer** over the base (pebbles, tufts, wildflowers, cracks) as a sparse overlay
   pass, NOT baked into the fill. (sprite-ai; Tilesetter.)
3. **Autotiled transitions between materials.** Adopt a defined autotile contract — a **47-tile blob** set for
   organic masses (grass/dirt/water/sand), 16-tile marching-squares only where blockiness is acceptable.
   Richness lives at the **edges/transitions**, not the fills — invest generation budget there (BorisTheBrave
   tileset classification; Lumisteria Stardew tilesheets — the eye lives at material boundaries).
4. **Fix the AI generation itself:** prompt for *evenly scattered detail* and describe the **surface not the
   scene** ("cobblestone texture" > "cobblestone street") to defeat the model's center-focus bias; prefer
   *organic noisy* surfaces (grass/dirt/sand) that hide seams; **preview every tile in a 3×3 grid** before
   accepting. (sprite-ai.art seamless-tiles — deep-read.)

**Density discipline (avoid the opposite failure — uniform clutter):** keep ~**70% calm/negative ground**,
cluster detail in GROUPS with rest space between, and give each zone **one grid-breaking, useful landmark**
(height/orientation/shape contrast + an interactable). (Level Design Book composition + Jim Brown "Importance
of Nothing" GDC 2014.) This dovetails with our existing `zone-craft` hero-prop-vignette discipline.

---

## 4. Motion density — "1000 tiny motions" with a rough budget

Cheap short loops on MANY objects beat a few elaborate ones (SLYNYRD pixelblog-8: subtle 1–2px bob / "bouncy
breathing" reads as alive; **loop cleanliness > frame count** — one orphan pixel in a loop is glaring).
Because our sprites are single-frame gpt-image output, most of this motion should come from **SHADER motion**
(one wind material animates the whole flora library for free) rather than hand-animated frames — this is the
gpt-image synergy already flagged in the look-&-feel doc's wind-sway lever.

**Rough motion budget (per visible screen), cheapest first:**
| Tier | What moves | How | Rough count on screen |
|---|---|---|---|
| 1 (do first) | The ambient FIELD: grass/crops/foliage sway, water shimmer | ONE wind shader + ONE water shader (planned grass pass) | Every foliage/water tile — hundreds, ~free |
| 2 | Atmosphere: dust motes / spores / drifting cloud-shadow | 1 particle system + 1 scrolling overlay per zone | ~5–20 motes; 1 cloud layer |
| 3 | Hero props: a 2–4 frame bob/breathe/flicker on signposts, lanterns, machines | short clean loops (shader or flipbook) | ~5–15 hero props |
| 4 | Wandering critters: birds land/peck/flush, butterflies, frogs, fireflies-at-dusk | client-local ambient actors | ~3–8 actors |

On-theme bonus: this is a **bug** farm — fireflies, butterflies, crawling ambient bugs are both the "1000
motions" lever AND thematic. (Detailed motion mechanics live in `../../research_look_and_feel.md`; this doc
owns only the *density argument* — that many cheap loops is the richness lever.)

---

## 5. Look-target recommendation — measure against ONE game

**PICK: Stardew Valley as the primary look-target,** with Eastward's global-LUT mood and Coromon's per-biome
palette variety as the two "reach" differentiators layered on top.

Why Stardew and not the flashier options:
- **It is our exact perspective and resolution.** Top-down 3/4 oblique, honest ~16px — the same frame we
  render. Eastward (the richness ceiling) is a **3D-rendered game with hand-painted bump maps** (gamedeveloper);
  its pipeline is far heavier than AI sprites can reach, so it's aspirational-for-mood, not a measurable target.
- **Its cohesion strategy is exactly ours.** Stardew's cohesion comes from **constraint + outline discipline**,
  not per-sprite beauty — the community itself calls the art a "mish-mash." That is precisely the AI-sprite
  play: enforce the constraint globally (master palette, one light direction, outline rule), don't chase
  per-asset fidelity. We are betting on the same engine of cohesion Stardew proved.
- **It's achievable and gives a concrete bar.** "Does our farm read as cohesively as a Stardew screenshot?" is
  a question we can hold a before/after render against. Eastward-as-target would always read as "we fell short."

So: **measure cohesion against Stardew; borrow the LUT-for-mood from Eastward and per-biome palette variety
from Coromon** to end up a notch richer than Stardew without leaving our pipeline. (Graveyard Keeper is the
proof that a tone-locked palette out-coheres Stardew — validation for the master-palette bet, not a separate
target.)

---

## 6. Unity asset-pack shortlist (free-first; every row from a page I opened)

*Compatibility verified against the actual store/GitHub pages, July 2026. Our engine: Unity 6000.2.9f1, URP
17.2, 2D Renderer, pixel-art. "Fit" notes the pixel-art / URP-2D caveats.*

| Pack | What it gives us | Free / Paid | URP-2D + Unity-6 fit | Pixel-art fit |
|---|---|---|---|---|
| **Cinemachine 3** (Unity UPM pkg) | Smooth camera follow + dead-zone + look-ahead; **Pixel Perfect extension** snaps ortho size for crisp sprites | **Free** (UPM) | **v3.1.5 released for 6000.2** ✓; Pixel-Perfect extension is URP-2D-aware | High — the Pixel-Perfect extension exists precisely for this; keep look-ahead small |
| **PrimeTween** (Asset Store slug 252960 + GitHub) | Zero-allocation tweens/shakes/sequences for pickup magnet, arc-toss, ease-out-back pop, number-roll | **Free** (PRO paid) | Unity 2020.1+; modern-Unity; WebGL-safe; **0 bytes/frame** on 100 tweens | High — cosmetic, client-local; drives the "juice" tier |
| **DOTween** (Demigiant) | Same tween use-cases; the incumbent, huge ecosystem | **Free** (Pro paid) | Unity 6 → 2020.3 per its page | High — but PrimeTween is safer (no crash if object destroyed mid-tween) + zero-alloc; **prefer PrimeTween for new code** |
| **All In 1 Sprite Shader** (Seaside Studios) | Per-sprite **outline, hit-flash, glow, gradient/colour overlay, dissolve, fade** in one stackable material — directly serves selection-pop + a per-material colour nudge toward the master palette | **Paid ~$22.47** (50% off $44.95) | Min **2021.3.45**; "works out of the box with Built-in, URP and HDRP" + **URP 2D Renderer lights support** ✓ | High — explicitly 2D/sprite; a fast route to outline+flash without hand-writing shaders |
| **Feel** (More Mountains, MMFeedbacks) | 150+ stackable feedbacks: screen-shake, squash, flash, plus **URP post feedbacks** (bloom/vignette/CA/DoF) wired to events (harvest, hit, pickup) | **Paid ~$25** (50% off $50) | Verified **6000.0.23f1 (Unity 6)** ✓; URP/Built-in/HDRP | Med-High — powerful but heavy (301 MB); dial to cozy (10-20% intensity); overlaps PrimeTween — pick ONE juice system |
| **URP built-in Color Lookup** (no pack) | The **LUT color-grade** for our cohesion Stage 1 — bake our own LUT from a graded screenshot | **Free** (in URP 17.2) | Native URP 6000.2 Volume override ✓ | High — pixel-safe (color remap, no resample) |
| **Color Grading Pack [LUT]** / Cinema Themes 2 (Asset Store) | 100+ ready cinema LUTs as *starting points* to bake our biome LUTs from | **Paid** | URP + Built-in | Optional — we mostly want our OWN baked LUT; a pack is inspiration, not required |

**Shortlist verdict:** **Cinemachine (free) + PrimeTween (free) + URP's built-in Color Lookup (free)** cover
camera, juice, and the cohesion LUT at **zero cost**. **All In 1 Sprite Shader (~$22)** is the one paid pick
worth it — it collapses outline + hit-flash + per-material colour overlay + dissolve into one 2D-native
material and accelerates both the polish tier and the per-material palette nudge. **Feel** is only worth it if
we want a large pre-built feedback library and are willing to manage its weight; otherwise PrimeTween + a few
hand-wired effects is leaner. Avoid running **DOTween and PrimeTween both** — choose PrimeTween for new code.

*(No prices/compat invented — each is from the page cited in §Sources. Asset-store prices shown are the
discounted values seen July 2026; treat the struck base price as the norm.)*

---

## 7. Scored candidates — biggest look uplift we can actually do

*Axes (1–5): **impact** on the owner's "looks more interesting" concern · **effort** (5 = cheap) · **fits our
AI-sprite workflow** · **complements the planned grass/wind pass**.*

| Candidate | Impact | Effort | Fits-AI | Grass-synergy | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Global Color Lookup LUT + lean into warm/cool day-night** (cohesion Stage 1) | 5 | 5 | 5 | 3 | **PICK — do first (this week).** One-day, reversible, engine-only; the cheapest cohesion proof and biggest mood delta. Independently the top pick of the lighting doc too. |
| **B. Master-palette lock + post-gen quantization + one light direction** (cohesion Stages 0/2/3/4) | 5 | 3 | 5 | 3 | **PICK — the durable cure.** Fixes the ROOT of our incoherence (separate AI passes). Med effort (a `pixelclean.py` stage + strict `style.json`), perfectly fits our pipeline. Do right after A proves the direction. |
| **C. Weighted-variant + scatter/decal tile system** (anti-repetition) | 4 | 3 | 4 | 5 | **PICK #3 — ride the grass pass.** Kills the "samey grid" AI tell; the variant/scatter resolver is best built alongside the grass/wind pass (same tile+builder work). |
| **D. Pervasive ambient-motion pass** (wind shader + dust motes + a few critters) | 4 | 3 | 5 | 5 | **STRONG — folds into the grass pass.** "1000 tiny motions" is our biggest richness lever; one wind material animates single-frame AI sprites for free. Largely the grass pass itself + a particle system. |
| E. All In 1 Sprite Shader for outline/hit-flash/glow polish | 3 | 4 | 4 | 2 | Adjunct — low-effort per-object polish + a per-material colour nudge; buy it, but it's polish, not the core uplift. |
| F. Chase Eastward-level per-material 3D-bump richness | 5 | 1 | 1 | 2 | **REJECT** — needs a hand-painted bump/3D pipeline AI sprites can't produce; wrong target (see §5). |

**Recommended sequence: A (LUT proof, this week) → B (palette-lock cure) → C+D together on the grass/wind
pass.** A+B are the cohesion fix the owner's concern actually points at; C+D are the richness/anti-samey layer
and are cheapest built into the grass work already planned. E is a cheap polish buy; F is the trap.

---

## 8. Owner questions (taste — surface, do NOT guess)

1. **How far off pure pixel-art are we willing to go?** A cohesion LUT + gentle bloom + soft lights nudge
   toward "lit modern 2D" rather than crisp flat pixels. Stardew stays honest-flat; Coromon/Sun Haven go
   "hi-bit." Where's our line? (Sets LUT contribution, bloom intensity, and whether we allow soft overlay VFX
   on vs above the pixel grid.)
2. **Confirm the look-target.** Recommendation is **Stardew (cohesion bar) + Eastward LUT-mood + Coromon
   per-biome variety**. Is Stardew the right measuring stick, or do you want to aim at a different game?
3. **Lock ONE light direction.** Recommend **upper-left**; pure top-down "straight-top" is the alternative.
   This bakes into every future sprite prompt, so it should be decided once, now.
4. **Effective pixel density** — honest 16×16 (Stardew) or hi-bit (Sun Haven)? Outline/dither/scatter all key
   off this; decide before the master palette is finalized.
5. **Palette scope** — do we commit to a single global master palette (Graveyard-Keeper tone-lock, strongest
   cohesion) or per-biome sub-palettes sharing a spine (Coromon variety, slightly weaker cohesion)? Recommend
   a shared spine + per-biome accent ramps.

---

## Sources

**My own deep-reads (WebFetch, July 2026):**
- pixie.haus — "Engineering Cohesion: The Science of Art Direction in AI Pixel Art" (palette-lock, 80/20 prompt
  anchoring, seed control, I2I trees) — *primary for our AI-cohesion section.*
- SLYNYRD pixelblog-1 "Color Palettes" (hue-shifted ramps, master palette, cohesion via overlap).
- Cage's Corner "Colorizing and remapping with gradient maps" (luminance→ramp gradient-map recolor, 3–5 stops).
- Unity Asset Store — All In 1 Sprite Shader (Seaside Studios): price, min Unity 2021.3.45, URP+2D-lights.
- Unity Asset Store — Feel (More Mountains): price, Unity 6000.0.23f1, URP feedbacks.
- GitHub — KyryloKuzyk/PrimeTween (free, zero-alloc, DOTween adapter).

**Search-surfaced (medium confidence, corroborating):** Unity docs (Cinemachine 3.1.5 for 6000.2; Pixel Perfect
extension; URP Color Lookup override); Omitram/DreDyson DOTween-vs-PrimeTween; sandromaglione + generalistprogrammer
(one-light-direction cohesion rule); jenova.ai / sprite-ai.art (AI palette-lock). Asset-store LUT packs (Color
Grading Pack [LUT], Cinema Themes 2) noted as optional inspiration only.

**Mined from the recovered overnight raw research** (`../_raw_recovered/visuals/`): `a669498e088defe4d.md`
(per-game art-direction tells — Eastward/Sea of Stars/Moonlighter/Ori/Spiritfarer deep-reads),
`a10a417503069e33a.md` (density & composition — BorisTheBrave tilesets, LDB composition/storytelling, 80.lv
Cuban Kitchen set-dressing, SLYNYRD animation, sprite-ai seamless tiles), `a0a7f7d6a45db08cb.md` (Apico/Eastward
look philosophy).

*Confidence flags: Eastward's LUT is reported (80.lv) not primary-confirmed; Stardew/Graveyard Keeper/Coromon/
Sun Haven/Wylde Flowers per-game tells are search-surfaced summaries — design ideas, not cited facts. Asset
prices are the discounted values seen July 2026. Project state (DefaultVolumeProfile exists, no LUT, post OFF,
style.json/catalog split, pixelclean.py) is from `01_unity_urp2d_lighting_and_rendering.md` + CLAUDE.md, not
re-verified against the live project in this pass — mark before implementing.*
