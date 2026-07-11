# Visuals research — index & recovery status (topic 4)

*Improving BugFarmer's visual quality in Unity 6000.2 / URP 2D. Extends (does not repeat) the prior
`../../research_look_and_feel.md` + `../../research_lighting_look.md`.*

## Status
| Slice | Clean doc | Strongest recovered raw | Status |
|---|---|---|---|
| **URP-2D lighting & rendering** (project-grounded) | ✅ `01_unity_urp2d_lighting_and_rendering.md` | `../_raw_recovered/visuals/ae56b9b076e43bd1d.md` (8+ Unity docs + our actual project) | **DONE** — actionable, version-pinned |
| **Art-direction reference** (why Stardew/Spiritfarer/Ori/etc. look rich; palette cohesion; making AI-generated sprites cohere) | ⏳ raw only | `a0a7f7d6a45db08cb.md` (Apico devlog + others), `a669498e088defe4d.md` (art direction of games), `a10a417503069e33a.md` (density & composition) | **Raw recovered** — synthesis owed |
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

## Art-direction angle owed (the owner's core concern — "other games look more interesting")
The prior research covered particles/foliage/shadows/camera/post-FX/parallax. The **gap** the overnight run
targeted (and that survived only as raw) is **art direction**, not tech: palette cohesion & contrast, value
structure, focal hierarchy, tile variety/anti-repetition, idle micro-animation density, and — our specific
risk — **making AI-generated sprites cohere** (palette unification, gradient-map recolor, one consistent light
direction, a unifying post-pass). This deserves a clean synthesis doc from the raw art-direction files above,
plus the asset-pack shortlist. Re-run at ≤2 self-contained agents per `no-wide-agent-fanout`.
