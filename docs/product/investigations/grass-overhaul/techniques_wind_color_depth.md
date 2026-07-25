# Grass techniques — wind sway, color variation, tufts/depth

Concrete, implementable techniques (verified against real shader tutorials/repos). Focus: making grass feel
ALIVE (wind, react-to-player) and LUSH (color variation, tuft overlays), mapped to our 2D top-down tile game
(Unity, custom tile renderer + we already run a GPU tile-composite shader, so custom shaders are on the table).

## Source table
| # | source | technique | cost | fits us? |
|---|--------|-----------|------|----------|
| 1 | github.com/aarthificial/pixelgraphics (shaders.md) | Pixel-art wind: noise-scaled sway, `WindVelocity` (2D dir+speed) + `WindStrength`; UV-displacement variant (mesh/sprite bigger than art to avoid clipping); **velocity reactivity** via a `_DisplacementMask` (R=velocity weight, G=wind weight) so entities push foliage | Med (shader) | YES — the tuft sprites, not the ground tile |
| 2 | halisavakis.com — "Grass Shader Part I" | Wind = sample a scrolling displacement texture at `worldPos.xz*ST + time*speed`, remap [0,1]→[-1,1], ×`WindStrength`, apply to the TIP only; **height weight via vertex color** (base=0, tip=1); **per-instance random** seeded by `random(worldPos.xz*(i+1))` so blades don't move in unison; tint via a gradient map (base→tip) | Med (shader) | YES — same idea in a 2D canvas shader weighting by sprite-local Y |
| 3 | (Stardew `Grass.cs`, from the farming-sims doc) | The reference for tufts: per-tuft rotational SWAY on player collision (maxShake π/8, decay), 3 blade variants, 2×2 sub-grid, seasonal recolor by sheet-row | Low-med | YES — the canonical top-down approach |

## 1. Wind sway (the "alive" factor)
The recipe (portable to a Unity **2D sprite/canvas shader** on the grass-tuft sprites):
- **Displace the TOP of the tuft, keep the base planted.** Weight the horizontal offset by sprite-local Y
  (top rows move, bottom rows don't) — the vertex-color trick becomes a UV.y weight in 2D.
- **Drive it by scrolling noise, not a single sine.** Offset = `noise(worldPos * scale + time*windSpeed) * windStrength * heightWeight`, in the wind direction. A scrolling noise texture (or 2 layered) gives gusts, not a metronome.
- **Per-instance offset by WORLD POSITION** (`random(worldPos)`) so neighbouring tufts sway out of phase — this is what stops the "whole field breathing in unison" look.
- **Two options for us:** (a) a shader on the tuft sprites (best look, needs a custom 2D material + the tufts as their own renderer layer); (b) cheap CPU/animation: a few pre-baked sway frames per tuft with a per-instance phase (Stardew-style rotation). Shader = smoother + reactive; frames = simplest.

## 2. Player-reactive bend (grass parts as you walk)
- Feed entity positions/velocity into the tuft shader as a displacement (aarthificial `_DisplacementMask` R
  channel / a "player position + radius" uniform); tufts near the player bend away, spring back.
- Stardew's cheaper version: on player-collision, add a decaying rotational shake per tuft (no shader) + a
  "grassyStep" sound. Great feel for low cost. **Recommended baseline; shader-bend as the premium upgrade.**

## 3. Color variation (the "not a flat carpet" factor) — see also the anti-tiling doc
- **Per-instance hue/value jitter** on tuft sprites (small ±HSV shift seeded by position) — cheap, breaks
  sameness.
- **Large-scale color modulation across the map:** multiply the ground/tufts by a low-frequency Perlin/noise
  field (subtle lighter/darker/warmer patches) so a big lawn has organic tonal variation instead of one green.
  A shader `tint = base * (1 + noise(worldPos*lowFreq)*amount)`.
- **A gradient base→tip tint** on tufts (darker root, lighter tip) reads as real blades (Alisavakis gradient map).
- Multiple base-tile variants + weighted random (we HAVE grass_v2/v3 unused — wire them in) is the first cheap win.

## 4. Tufts / detail layer + depth
- Grass = **flat base ground tile + a scattered TUFT/BLADE overlay layer** (the single biggest lush-factor;
  every reference game does this). Tufts are small sprites (Stardew 15×20px, up to 4/tile in a 2×2 sub-grid),
  3+ variants, random rotation/flip/variant, density-controlled, avoiding paths.
- **Depth:** a tiny soft drop-shadow under each tuft (1-2px, semi-transparent) grounds it; taller tufts overlap
  the player slightly (sort by Y) for a layered field. Optional flowers/clover mixed into the scatter for accent.

## Top recommendations for us (2D tile game)
1. **Base:** author better grass tiles with real texture (subtle blades/clumps, not flat noise) + wire in
   variant selection (weighted random per cell across grass/v2/v3 → more variants). Add low-freq color noise.
2. **Detail layer:** a proper scattered TUFT overlay (new small tuft sprites, 3+ variants, dense-but-tuned,
   random rotate/flip, drop-shadow) — the biggest visual win.
3. **Alive:** wind sway on the tuft layer (start CPU/animation or a simple 2D shader) + player-reactive bend
   (Stardew rotational-shake baseline, shader-bend premium).
4. **Edges:** proper grass↔dirt/path transitions (see anti-tiling/autotiling doc: dual-grid) + fringe/overhang.
