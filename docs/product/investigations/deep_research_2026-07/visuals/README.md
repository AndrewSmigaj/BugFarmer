# Visuals research — index & recovery status (topic 4)

*Improving BugFarmer's visual quality in Unity 6000.2 / URP 2D. Extends (does not repeat) the prior
`../../research_look_and_feel.md` + `../../research_lighting_look.md`.*

## Status
| Slice | Clean doc | Strongest recovered raw | Status |
|---|---|---|---|
| **URP-2D lighting & rendering** (project-grounded) | ✅ `01_unity_urp2d_lighting_and_rendering.md` | `../_raw_recovered/visuals/ae56b9b076e43bd1d.md` (8+ Unity docs + our actual project) | **DONE** — actionable, version-pinned |
| **Art-direction & cohesion** (why Stardew/Spiritfarer/Ori/etc. look rich; palette cohesion; making AI-generated sprites cohere) | ✅ `02_art_direction_and_cohesion.md` | `a0a7f7d6a45db08cb.md`, `a669498e088defe4d.md`, `a10a417503069e33a.md` (+ own web research) | **DONE** — cohesion pipeline, look-target (Stardew), asset shortlist, scored picks |
| **Unity asset-packs survey** (shaders/VFX/tween/lighting packs; free-first) | ⏳ scattered | check `a03253260bc73bf44.md`, `a8ee28390764d697b.md`, `ac6d8eadc55b5bc59.md` (some may be mis-bucketed) | **Partial** — the dedicated asset-pack agent died early; verify from raw + a low-concurrency re-run |
| **Other URP techniques** (post-FX beyond bloom, shaders, tilemap variety, parallax, VFX Graph) | ⏳ raw | `a2d8849a583c18e92.md`, `ad9a4a7f01a437995.md`, `af590b9766eea606a.md` | **Raw recovered** — synthesis owed |

> The `visuals/` raw bucket has ~30 files, some **mis-bucketed prior-session work** (the keyword sort isn't
> perfect). Treat the IDs above as the vetted starting points; the rest of `../_raw_recovered/visuals/` is a
> pile to mine, not a clean split.

## Highest-confidence uplifts already captured (from the lighting doc — do these first)
1. **Set lamp Falloff Strength (~0.6–0.9)** — fixes the flagged hard-disc lamp look. One field, free.
2. **Enable Bloom** (camera post-processing flag + a Global Volume; HDR is already on) — the biggest cozy-night upgrade.
3. **Lean into warm-key / cool-ambient contrast** — the #1 "looks good" trick, already half-done.
4. **Sprite-cookie lights + additive emissive accents** (fireflies/torches self-glow into the bloom).

## Art-direction angle (the owner's core concern — "other games look more interesting") — DONE
Synthesized in `02_art_direction_and_cohesion.md`: why the best 2D games look rich (source table), the
**AI-sprite cohesion pipeline** (master palette → LUT proof → prompt anchoring → post-gen palette clamp → one
light direction → gradient-map rescue), tile variety/anti-repetition, motion-density budget, a single
**look-target (Stardew, + Eastward LUT-mood + Coromon per-biome variety)**, a **Unity asset-pack shortlist**
(Cinemachine/PrimeTween/URP Color Lookup free; All-In-1 Sprite Shader ~$22; Feel ~$25), and scored candidates
with the pick order **LUT → palette-lock → tile-variety+motion on the grass pass**. Owner questions: pixel-art
purity line, look-target confirm, lock one light direction, pixel density, palette scope.
