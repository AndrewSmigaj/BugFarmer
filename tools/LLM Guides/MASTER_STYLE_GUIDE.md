# BugFarmer Master Style Guide

Single source of truth for all sprite generation. Use this document with ComfyUI and PROMPT_SCAFFOLDS.md.

---

## 1. Camera & Perspective

**45-degree overhead (RPG perspective)**

Player sees:
- Top surfaces of objects
- Front faces of vertical elements

Never show:
- Left/right faces
- Isometric diamond tops
- True side views

**Plane Rules:**
- Horizontal planes (tops): viewed from directly above, squares stay square
- Vertical planes (fronts): drawn front-on (1:1), darker than tops
- Depth comes from contrast, not perspective distortion

---

## 2. Thickness Ratios (Critical)

Everything has visible thickness, even when it shouldn't.

| Zone | Percentage | Description |
|------|------------|-------------|
| Top surface | 55-65% | Light, visible from above |
| Front face | 25-35% | Dark, shows height |
| Trim/edge | Remaining | Accent pixels |

**Rules:**
- No 1-pixel front faces on solid objects
- Thin objects are exaggerated
- Flat sprites are invalid
- If it feels chunky, it's correct

---

## 3. Lighting

**Light source: top-left, shadows bottom-right**

Lighting is stylized, not realistic.

| Surface | Value |
|---------|-------|
| Top surfaces | Light |
| Front faces | Dark |
| Plane boundaries | Hard contrast |

If lighting feels "too strong," it's probably correct.

---

## 4. Three-Shade Color System

Each material uses exactly 3-5 colors:

| Shade | Usage |
|-------|-------|
| Light | Top surfaces, highlights |
| Base | Main surface color |
| Dark | Front faces, shadows, contact edges |

**Palette Rules:**
- No pure black (#000000)
- No pure white (#FFFFFF)
- Slightly muted saturation
- Materials should read before objects do

---

## 5. Bitmap Anchoring (Per Category)

Different categories have different anchoring rules:

| Category | Examples | Bitmap Anchoring | JSON Pivot |
|----------|----------|------------------|------------|
| flying_bug | Bees, butterflies, dragonflies | CENTERED (they float) | "c" |
| grounded_bug | Ants, beetles, spiders | BOTTOM (walk on ground) | "bc" |
| natural_object | Trees, bushes, rocks | BOTTOM (grounded) | "bc" |
| furniture | Chests, tables, chairs | BOTTOM (grounded) | "bc" |
| blocks | Dirt, stone, ore | FILL ENTIRE FRAME | "bc" |
| tools | Axes, pickaxes, nets | CENTERED | "c" |
| player | All 4 directions | BOTTOM (feet grounded) | "bc" |

**Key Concept:**
- "BOTTOM" = Artwork touches bottom edge of PNG frame
- "CENTERED" = Artwork centered in PNG frame with breathing room on all sides
- "FILL" = Artwork fills entire PNG frame (seamless tiles)

---

## 6. Size Standards

Base tile: 16x16 pixels

| Category | Footprint | Sprite Size | Notes |
|----------|-----------|-------------|-------|
| Terrain tiles | 1x1 | 16x16 | Tileable, zero overhang |
| Small objects | 1x1 | 16x16 to 16x24 | Rocks, stumps |
| Trees | 1x1 | 32x48 | Trunk at bottom, canopy above |
| Small bugs | n/a | 8x8 | Ants, flies |
| Large bugs | n/a | 16x16 | Beetles, butterflies |
| Furniture | 1x1 to 2x2 | 16x16 to 32x32 | Scale with footprint |
| Player | 1x2 | 16x32 | Humanoid proportions |

**Footprint vs Sprite Size:**
- Footprint: How many tiles the object occupies in the world
- Sprite size: Pixel dimensions of the image
- Sprites are often taller than their footprint to show height

---

## 7. Ground Contact (For Grounded Objects)

Every grounded object must visually sit on the ground.

Use at least one:
- Dark base pixels at bottom
- Implied shadow
- Flat contact line

Floating sprites are invalid.

---

## 8. Shape Design

- Use blocky, orthogonal shapes
- Reduce curves to suggestions
- Remove detail until readability breaks, then stop
- Favor symmetry over realism
- Align major edges to pixel grid

Ask: "What is the minimum shape that still reads?"
Then remove one more thing.

---

## 9. Texture Strategy

Use controlled repetition, not random dithering.

| Material | Pattern |
|----------|---------|
| Wood | Horizontal plank bands |
| Stone | Clustered noise |
| Dirt | Horizontal strata + speckles |
| Metal | Smooth gradients |
| Leaves | Irregular clusters |

Think fabric, not photograph.

---

## 10. Edge Definition

Use darker material-relative edges selectively:
- Bottom edges
- Contact points
- Occlusion boundaries

This improves separation in cluttered scenes.

---

## 11. Acceptance Checklist

Every sprite must pass ALL:

- [ ] Chunky enough (not thin or delicate)
- [ ] Strong plane contrast (top light, front dark)
- [ ] Grid-aligned (no off-pixel edges)
- [ ] Material reads instantly
- [ ] Anchored correctly for category
- [ ] Matches existing sprites in style
- [ ] Correct dimensions after resize
- [ ] Has transparency (PNG with alpha)
- [ ] No ground shadows in bitmap

Fail any one = revise.

---

## 12. What NOT to Include in Sprites

- Drop shadows (handled by game engine)
- Ground planes or surfaces
- Background colors (use transparency)
- Glow effects (handled by game engine)
- Animation blur

---

## 13. Design Philosophy

> BugFarmer sprites should look simple, solid, and slightly overbuilt - because clarity beats correctness.

- Terraria-style chunky pixel art
- 45-degree overhead view
- Readable at game zoom
- Consistent with existing assets
