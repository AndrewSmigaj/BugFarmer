# Research — Broader look-&-feel improvements (beyond lighting)

> **Status:** RESEARCH / working doc. Distilled from 3 parallel deep-read agents (particles + foliage/water ·
> grounding + camera juice · post-FX + parallax/sky), ~29 sources deep-read, multiple real implementations
> studied (Cyanilux 2D water, prime31 2D foliage, ProPixelizer, DOTween, Gobs&Gods shadow shader). Pairs with
> the two lighting docs. Scope: everything that lifts the game's *feel* that ISN'T scene lighting.
> **Engine: Unity 6000.2 / URP 17.2, 2D Renderer; hard pixel art ~16px logical; gpt-image-1 single-frame
> sprites; day/night + weather; multiplayer.**

## The three laws that gate EVERY technique below (read first)

1. **Quantize motion to whole logical pixels, or it looks "wet."** Any effect that *moves or resamples* pixels
   — wind sway, water distortion, camera follow, squash, cloud-shadow scroll, dither — must snap to whole
   logical pixels (Posterize in shaders / `Round(pos/PPU)*PPU` for transforms) or run at logical resolution
   under a Pixel-Perfect Camera. Un-quantized motion on 16px art reads as blurry/mushy. **Corollary — no
   sub-pixel/fractional ROTATION of a pixel sprite** (it nearest-neighbor-crawls the edges): use an angle
   flipbook or snap to discrete angles. This applies everywhere, not just particles — so the lilypad "tiny
   rotation," the arc-toss spin, and the screenshake "fraction of a degree" below must all be flipbook'd,
   snapped, or reserved for soft/overlay elements. This is the single most repeated finding across all agents.
2. **Post that *remaps color* is pixel-safe; post that *resamples space* smears pixels.** LUT grading, vignette,
   tint, hit-flash = safe (per-pixel color). Bloom, chromatic aberration, heat-haze, blur = spatial resample →
   soften hard edges. Keep camera AA = **None**. Prefer color-remap effects; gate resample effects to rare
   moments or high thresholds.
3. **Everything here is presentation → CLIENT-LOCAL → never in the networked sim.** Cameras, shake, shadows,
   tweens, particles are per-client. **The trap: hitstop must freeze the *animation*, never the deterministic
   sim clock** (that would desync/freeze other players). Pickup magnet/arc are cosmetic; the authoritative
   "who collected what" stays a server event. (Consistent with our determinism model — this is all safe.)

Plus the **cozy-restraint rule**: this is a calm farming game, not an action game. Dial every "juice" technique
to ~10-20% of its action-game intensity, make motion effects *optional* (a reduced-motion / screenshake-off
toggle, default-calm), and apply feedback to *reward* moments (harvest, pickup, growth), not fake impacts.

> **Boundary with the lighting docs (avoid double-scheduling).** A few techniques appear in BOTH this doc and
> `research_lighting_look.md` — to keep a single backlog from costing them twice, the **lighting docs OWN**:
> the day/night **sky gradient / colored ambient** (their "#1 lever"), **LUT color grade + vignette**, **bloom
> on emitters**, and **in-beam particles (dust motes / pollen / fireflies-as-light)**. This doc keeps the
> **motion / particle-authoring** half (how the dust/leaves/fireflies actually move, the wind/water shaders,
> grounding, camera juice, transitions, weather-ground). Rows below that overlap are marked *(→ lighting doc
> owns cost)* — reference, don't re-cost.

## The prioritized backlog (the actionable summary)

**CHEAP HIGH-IMPACT WINS (do first — hours each, transform the feel):**
| Technique | Category | Why it's top |
|-----------|----------|--------------|
| **Wind sway shader** on all foliage/crops | motion | One material animates the entire gpt-image-1 flora library for free (no hand-animation) — the core "alive" upgrade |
| **Ambient dust motes / spores** (1 particle system/zone) | particles | Biggest atmosphere-per-hour; sells "cozy" instantly |
| **Tween/easing on pickups & UI** (magnet, arc toss, ease-out-back pop, number roll) | camera/feel | Highest feel-per-hour; pure reward register; DOTween |
| **Blob-shadow sprite + contact darkening** | grounding | The "un-paste" package, pipeline-safe (no baked shadows). *(base-overlap/tufts also help but are an ONGOING per-asset hand-art tax, not a one-time win — see grounding table)* |
| **Per-biome / per-time LUT color grade** (+ light vignette) | post-FX | One Volume, biggest mood delta; pixel-safe *(→ lighting doc owns cost)* |
| **Harvest / crop-pop particle bursts** | particles | Reinforces the core farming loop |
| **Hit-flash material** (lerp-to-white ~0.05s) | post-FX | Trivial; great for chopping/whacking/mining feedback |
| **Day/night sky gradient + drifting cloud-shadow overlay** | sky | The top-down-correct "parallax"; serves day/night+weather *(sky gradient → lighting doc owns cost; cloud-shadow motion here)* |
| **Smooth camera follow + dead zone + small look-ahead** | camera | Reads calm/premium (keep look-ahead small) |
| **Rainy-day wet-ground pass** (darken/desaturate tiles + sheen; driven by existing weather state) | post-FX/weather | Nearly free, highest rain tell; the CHEAP half of weather-grading |
| **Ambient wildlife actors** (birds land/peck/flush, butterflies, frogs) | particles/actors | On-theme for a *bug* farm; the Stardew "alive world" staple; client-local |

**MEDIUM POLISH (do next):** gentle squash-&-stretch (pickups/tool wind-up/growth pop-in), player-parts-the-grass
displacement, **player wading ripple/splash in shallow water** (reuses the grass-displacer pattern), water flow
+ shoreline ripple, fireflies-at-dusk, falling leaves (seasonal) → snow (reskin), reeds/lilypad bob, ordered
dither, sprite outline (selection/hover), dissolve poof, ~40-60ms visual-only tool hitstop, **pixelate scene
transitions** (a Full-Screen-Pass + shader + event wiring — ~a day, not "hours"), **footprint/trail decals in
snow/sand** (snow weather already sets this up), **watered/tilled-soil darkening** (farming readability),
**emote/speech bubbles** (`!`/`…`/heart over NPCs & animals — cheap iconic cozy tell), **seasonal world
recoloring** as a first-class lever (grass green→autumn→snow→spring), zone-edge distant scenery + atmospheric
perspective, star/aurora night sky.

**EXPENSIVE POLISH (only where a hero scene needs it):** render-texture water reflections *(top-down payoff is
LOWER than side-view — you look down at water, so a mirror reflection matters less than the cheap wet-sheen
above; don't over-invest)*, waterfall foam.

**AUTHORING (scope boundary, not a runtime FX — flagged so it isn't silently omitted):** tilemap
auto-transition / terrain edge blending (grass↔dirt↔water) — a huge part of why cozy maps read cohesive; lives
in the zone/tilemap authoring pipeline, not this catalog.

**SKIP / GATE HARD (wrong for this game or engine):**
- **Classic multi-layer horizontal parallax UNDER THE PLAY PLANE** — no *play-plane* horizon to slide the
  world against in top-down, so parallaxing the walkable ground produces sliding-carpet artifacts. (Nuance:
  the top-down-correct variants — cloud-shadow overlays *above* the plane, edge scenery at 0.8-0.95×,
  atmospheric perspective — ARE included below and DO work; only the ground-plane layer stack is the skip.)
  Kingdom Two Crowns' parallax is the side-scroll device — a cautionary reference for the play plane.
- **URP Decal blob shadows** — Decal Projectors/Renderer Feature belong to the **3D** Universal Renderer, **not
  the 2D Renderer**; don't burn a day on them. Use sprite/shader-quad shadows.
- **Chromatic aberration, strong bloom, global heat-haze, hard white flash, big zoom-punch** — anti-pixel and/or
  photosensitivity/motion-sickness risks; tonally wrong for cozy. Homeopathic + optional at most.
- **Heavy screenshake with rotation** — Nuclear-Throne register; at most a tiny rotation-free thud on rare big
  events, behind a default-off toggle.

## Category 1 — Ambient / weather particles

| Technique | Approach (concrete) | Cost | Reference | Fit |
|-----------|---------------------|------|-----------|-----|
| **Dust motes / spores** | 1 Shuriken system/zone, ~5-20 alive, near-zero gravity, tiny 1-2px sprites, Noise module for wander, Color-over-Life fade-twinkle; bias near light shafts | ~1-2h, negligible runtime | Spiritfarer hazy interiors | **High** |
| **Falling leaves / petals** | Emission across top, Noise tumble, Force-over-Life X wind bias, **pre-rendered rotation flipbook** (NOT live rotation), season-swap sprite | ~2-3h | Ori opening, Stardew fall | **High/Med** (season signal) |
| **Harvest / crop-pop bursts** | One-shot burst 5-15 particles, donut shape, size↓ over 0.5-1.5s life; + 1-frame squash + tiny shake | ~1-2h parametric prefab | Forager, Celeste dust | **High** (core loop) |
| **Fireflies at dusk** | Low-emission system, Noise flight, pulsing-alpha blink; glow = crisp in-world sprite OR overlay bloom (decide) — thematically perfect for a *bug* farm | ~2h | Ori forest | **High** (gate to night) |
| **Rain + splashes + puddle ripples** | Stretched-billboard Shuriken (Global sim space); **splashes spawn from a puddle/ground MASK at randomized ground positions** (NOT VFX-Graph *Collide-with-Depth-Buffer* — that's a 3D idiom that's flaky/unsupported on the 2D Renderer, which has no scene depth to collide against); **puddle ripple = flipbook normal-map in the water shader, NOT a particle per drop** | rain ~2-3h; splashes ~½-1d (mask-driven, cheaper than depth collision) | Stardew/Coral Island rain | **Med/High** |
| **Snow** | Reskin of falling-leaves (slower, round flakes, no rotation flipbook needed) + ground overlay tint | ~1h once leaves exist | Stardew winter | **Med** |

*Pixel-art gotcha (whole category):* never live-rotate a shaped pixel sprite (use flipbooks); snap drift to the
grid or float VFX deliberately *above* the pixel grid as a soft overlay — **decide that layer rule once**, globally.

## Category 2 — Foliage & water motion

| Technique | Approach | Cost | Reference | Fit |
|-----------|----------|------|-----------|-----|
| **Wind sway** on grass/crops/trees | Sprite Shader Graph: displace verts by scrolling **world-pos** noise, scaled by **UV-Y** (base planted, tip sways), 2 noise channels (sway+turbulence), global wind dir/strength props. Drop-in start: VOiD1 free URP 2D wind shader. CPU alt = Stardew's top-vertex skew. | ~½-1 day (or minutes w/ VOiD1); cheap runtime | **Stardew** grass/canopy | **High — do first** |
| **Player-parts-the-grass** | Per-quad: trigger detects crossing → offset top-2 verts by distance/dir → spring rebound → sleep when still (prime31/LordNed 2D). Dense fields: render displacers to a RenderTexture the shader samples. | per-quad ~½day; texture ~1-2d | Ori | **High/Med** |
| **Water flow + shoreline ripple** | Cyanilux 2D water: 2 world-pos noise textures scrolled (speed <0.1), summed ×0.05 = distortion (Y=0 to keep vertical attach); shoreline = scrolling Sine faded inward + Square-SDF per-tile; sparkle = Step on noise | ~½-1 day; cheap | Spiritfarer water | **Med/High** |
| **Reeds / lilypad / tall-crop bob** | Reuse the wind shader at higher amp/slower freq; lilypads = vertical Sine bob + tiny rotation, phase-offset by world-pos | ~1-2h once wind exists | pond ambiance | **Med** |
| **Render-texture water reflections** | 2nd camera → RenderTexture, sampled with distortion offset; lerp reflection↔tint | +full extra render | Spiritfarer (hand-crafted) | **Low** (hero ponds only) |
| **Waterfall foam** | Scrolling Sine-offset UVs along tangent (no vert displacement); foam = stepped SDF sides + smoothstep noise at lip/pool; **alpha-clip** for hard pixel edges | ~½day; niche | — | **Low** (only if you have falls) |

*Gotcha:* the wind/water motion is the #1 place pixel-crawl bites — **quantize the displacement to whole pixels**
(Posterize the offset) and cap amplitude to a few logical pixels. gpt-image-1 synergy: shader motion beats
hand-animated sway frames (single-frame sprites get motion for free).

## Category 3 — Grounding (shadows / AO — no baked shadows allowed)

| Technique | Approach | Cost | Reference | Fit |
|-----------|----------|------|-----------|-----|
| **Blob-shadow sprite** | Child SpriteRenderer, soft dark oval ~40-60% alpha, sorted under, anchored at the sprite **base** (feet/trunk), scaled to footprint; shrink/fade on hops | trivial; batches | Stardew, Zelda-likes | **High** |
| **Contact darkening / AO band** | Soft dark gradient multiply where object meets tile (in the blob or a tiny quad) + 1-2px darker band at tall-object base | trivial | ubiquitous cozy | **High** |
| **Base-overlap + contact tufts + Y-sort** | Sink feet/trunk 2-3px below the tile seam; hand-drawn grass/scuff tuft at base; correct occlusion sorting — kills "pasted-on" with **no shadow at all** | art-time only | Stardew/Spiritfarer | **High** (do first, free) |
| **Projected silhouette shadow shader** | Reuse sprite alpha, skew from `_yRoot` base + squash to ground, offset in **pixel space** via `TEXTURE_PIXEL_SIZE`, expand quad, smoothstep edge (Gobs&Gods) | med shader | action-RPG chars | **Med** (hero objects only) |
| ~~URP Decal blob~~ | **NOT on 2D Renderer** (decals = 3D Universal Renderer) — documented so nobody wastes a day | — | — | **Skip** |

*Gotcha:* a soft oval isn't "hard pixel" — decide crisp-dithered blob vs intentionally-soft blob (the one place
soft may be OK). Scale in integer steps.

## Category 4 — Camera juice / game-feel (dial to COZY, keep client-local)

| Technique | Approach | Cost | Reference | Fit |
|-----------|----------|------|-----------|-----|
| **Tween/easing on pickups & UI** | DOTween: pickup **magnet** (items accelerate to player, vanish), **arc toss** on drop, **ease-out-back** pop on collect + panel open, **number roll** on coins/XP | low w/ DOTween | Vampire Survivors magnet, Stardew | **High — do first** |
| **Smooth follow + dead zone + look-ahead** | Lerp/SmoothDamp to player, soft dead-zone box, *small* directional lead (Cinemachine Look-Ahead + Damping) | low (Cinemachine) | Celeste/Hollow Knight | **High** (small lead) |
| **Gentle squash-&-stretch** | Volume-preserving scale on pickup/land/growth pop-in, ease-out-back overshoot; on 16px use **secondary-motion** or **snap-exempt the brief pop** | low (tween) | Celeste (dialed down) | **High** |
| **Visual-only tool hitstop** | ~40-60ms **animation** freeze on axe/hoe bite + hit-spark — **NEVER freeze the sim clock** (MP) | low | Zelda hit emphasis | **Med** |
| **Screenshake** | Trauma float, offset = maxOffset·trauma², + a *fraction of a degree* rotation; **default-off toggle** | low | Nuclear Throne (heavy) | **Low** — tiny thud on rare big events only |
| ~~Hard flash / big zoom-punch~~ | photosensitivity + motion-sickness + fights Pixel-Perfect | — | — | **Skip** (homeopathic max) |

*Pixel-perfect gotcha (whole category):* smooth follow / shake / fractional scale / zoom all shimmer under
Pixel-Perfect. Fixes: **nest the pixel camera under a float-moving "shaker" parent**; snap smoothed positions to
`1/PPU` in a negative-exec-order `LateUpdate`; exempt brief pop-scales from snapping. **All client-local; each
client owns its camera; the authoritative pickup is a server event (don't let a tween decide ownership) — and
if the server awards an item elsewhere mid-flight, cancel/redirect the local magnet (pop it out), never
teleport it back.**

## Category 5 — Post-FX / material shaders

| Technique | Approach | Cost | Reference | Fit |
|-----------|----------|------|-----------|-----|
| **Per-biome / per-time LUT grade** | Volume **Color Lookup**, LUT baked from a graded screenshot, **Contribution ~0.4-0.6**; one LUT/biome, cross-fade Volume weight for dawn→dusk | low; low runtime (color remap) | Eastward (reported) | **High** (cheapest big mood win) |
| **Hit-flash** | Shader Graph `Lerp(color, white, _Flash)`, spike ~0.05-0.1s via per-instance `SetFloat` | trivial | universal | **High** |
| **Pixelate scene transitions** | Full-Screen Pass + `_Progress` (pixelate-out / iris / dither wipe) on zone/sleep/day-rollover | med; low | Pokémon/FF wipe | **High** |
| **Light vignette** | Volume Vignette, Intensity ~0.15-0.25, rounded; up slightly at night/indoors | trivial | cozy framing | **Med** (subtle — bands if strong) |
| **Ordered dither** | Bayer Dither node → Alpha-Clip for screen-door fades; or bake 4×4 dither into a palette LUT | low-med | ProPixelizer | **Med** |
| **Sprite outline / rim** | Sample ±1 texel, outline where opaque borders transparent; use for **selection/hover**, not everything (compute at native res) | med | Apico clarity ethos | **Med** |
| **Dissolve poof** | Simple Noise → Step alpha-clip + offset Step for HDR edge; **quantize noise to the pixel grid** | med | Ilett recipe | **Med** (bug-catch/harvest) |
| **Bloom** | Volume Bloom, high **Threshold**/low Intensity so only emitters (lamps, fireflies, night windows) glow | low; med runtime | hi-bit farming | **Med** (restraint — it blurs) — *overlaps the lighting look doc* |
| ~~Chromatic aberration~~ / ~~global heat-haze~~ | splits/refracts sub-pixels → fringes every hard edge | — | — | **Skip** (or 1-sec rare) |

## Category 6 — Parallax / sky / depth (top-down realities)

| Technique | Approach | Cost | Reference | Fit |
|-----------|----------|------|-----------|-----|
| **Day/night sky gradient** | HDR gradient keyed to the day/night clock → global ambient/tint + visible-sky color at edges; blend with the per-time LUT | low-med; trivial | Kingdom Two Crowns mood | **High** (serves day/night pledge) |
| **Drifting cloud-shadow overlay** | Large soft tiling shadow texture **multiplying** the ground, scrolling slowly in **world space** (integer steps); optional cloud sprites above; gate density to weather. **This is the top-down-correct "parallax"** (the layer lives *above* the play plane) | low-med; low | Stardew cloud-shadow critters | **High** |
| **Zone-edge distant scenery** | Off-map mountains/treeline/ocean past the walkable tiles, scrolling *slightly* slower (0.8-0.95×) as the camera pans; the only defensible parallax top-down | med; low | JRPG borders, Eastward | **Med** |
| **Atmospheric perspective (depth via scale)** | Authoring: recede = lower contrast, **lower saturation**, hue→sky color, less detail per plane; bake into distant-tier palettes (can't runtime-fog a ≤15-color asset) | med (art) | SLYNYRD landscapes | **Med-High** (powers edge scenery) |
| **Star / aurora night sky** | Dark gradient + twinkling **pixel-snapped** star dots (thresholded noise, animated alpha) fading in on the clock; aurora = slow warping additive bands (special biome) | med; low | day-night skybox | **Med** (only where sky shows) |
| ~~Classic multi-layer scrolling parallax~~ | **Side-scroller-only** — no horizon in top-down; sliding-carpet artifacts. Use cloud-shadows + edge scenery | — | Kingdom Two Crowns (cautionary) | **Skip** for the play plane |

## Consolidated source table (deep-read; grouped)

**Particles / motion:** danielilett (six-grass, URP rain, foliage), alanzucconi (interactive grass), prime31 &
LordNed (2D foliage vert+spring), nedmakesgames (URP foliage shader), VOiD1 (free 2D wind), Cyanilux (2D water,
rain, waterfall breakdowns), lmhpoly (falling leaves), edom18 (curl-noise), Unity Learn (particle lights),
gamedevacademy (juice/dust). **Grounding / camera:** Nijman "Art of Screenshake", russmatney (juicy notes),
critpoints/sonichurricane/ssbwiki (hitstop), Gobs&Gods (2D shadow shader), prasetion (URP decal — flags 3D-only),
bugnet (pixel-perfect jitter fix), Cinemachine docs, Vampire Survivors wiki (magnet), madelinemiller +
Death-Must-Die/Disney (motion-sickness → toggles), Unity squash thread, DOTween. **Post-FX / sky:** ProPixelizer
guide (studied), danielilett (dissolve, dither), gamedevbill/lindenreid (heat-haze), URP post-processing docs,
SLYNYRD pixelblog 23 & 62 (parallax + landscapes — flags side-scroller-only), timcoster (day-night skybox),
Stardew CloudySkies/God-Rays mods, wick.works & 80.lv (Apico/Eastward look), TransitionKit, Kingdom Two Crowns
& Dave-the-Diver postmortems.

*Confidence flags (agent-reported):* "Eastward uses LUT grading" is secondary-not-primary; "Celeste renders
distant scenery at coarser pixel scale" is medium-confidence (a design idea, not a cited fact); the
Apico devlog is philosophy (clarity-first, outlines) not tech specs.
*Perspective caveat:* several references (Spiritfarer, Ori, Celeste, Kingdom Two Crowns) are **side-view /
platformer** — most techniques transfer, but **water reflections especially do not** (side-view water reflects
sky/objects easily; top-down you look *down* at water, a different lower-payoff problem — prefer the cheap
wet-sheen). Weigh side-view references for the *technique*, not the *perspective*.

## Owner-taste questions (surface — do NOT guess)

- **VFX layer rule:** do ambient particles/soft shadows live **on** the pixel grid (crisp, snapped) or **above**
  it as a soft overlay (Spiritfarer-style)? Pick once, globally — mixing per-effect looks inconsistent.
- **Effective pixel density:** honest 16×16 (Stardew) or hi-bit (Sun Haven)? Outline/dither/dissolve all key off
  this — decide before layering.
- **Juice intensity:** how much squash/tween/shake feels right for *your* cozy register (and do we ship a
  reduced-motion/screenshake-off toggle from day one — recommended)?
- **Which cheap wins first?** The backlog above is ordered; confirm the top slice (wind + motes + tweens +
  grounding + LUT) is the right first sprint, or reprioritize.
