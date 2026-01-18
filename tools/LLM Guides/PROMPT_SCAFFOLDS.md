# BugFarmer Prompt Scaffolds

Fill-in templates for sprite generation. Replace `{PLACEHOLDERS}` with asset-specific values.

Reference: MASTER_STYLE_GUIDE.md for full style rules.

---

## How to Use

1. Select the appropriate scaffold for your asset category
2. Replace all `{PLACEHOLDER}` values
3. Generate in ComfyUI (SDXL 1.0 + Pixel Art XL LoRA)
4. Post-process: Pixelate → Rembg → Scale to target size (Point filter)
5. Validate against acceptance checklist

---

## Flying Bug Scaffold

**Output:** 16x16 or 8x8 PNG, centered composition

```
Create a pixel art {BUG_NAME} sprite for a 2D farming game.

Physical constraints:
- {OUTPUT_SIZE} pixel canvas with transparent background
- Bug CENTERED in frame with breathing room on all sides
- Viewed from 45-degree overhead angle

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- Top surfaces lit (55-65%), front/bottom dark (25-35%)
- {PRIMARY_COLOR} body with {ACCENT_COLOR} accents
- {WING_STYLE} wings (if applicable)
- Simple segmented body: head, thorax, abdomen
- {EYE_COUNT} small dark eyes as accent

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, ground plane, background, glow effects
```

**Example fills:**
- BUG_NAME: honeybee
- OUTPUT_SIZE: 16x16
- PRIMARY_COLOR: golden yellow
- ACCENT_COLOR: black stripes
- WING_STYLE: small translucent
- EYE_COUNT: 2
- MATERIAL_DESCRIPTION: fuzzy yellow-orange body with black bands

---

## Grounded Bug Scaffold

**Output:** 16x16 or 8x8 PNG, bottom-aligned

```
Create a pixel art {BUG_NAME} sprite for a 2D farming game.

Physical constraints:
- {OUTPUT_SIZE} pixel canvas with transparent background
- Bug positioned at BOTTOM of frame (walks on ground)
- Viewed from 45-degree overhead angle, seeing top and front

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- Top surfaces lit (55-65%), front/sides dark (25-35%)
- {PRIMARY_COLOR} body with {ACCENT_COLOR} details
- {LEG_COUNT} visible legs, simplified
- Body segments clearly defined
- Dark contact pixels at bottom edge

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, ground plane, background, glow effects
```

**Example fills:**
- BUG_NAME: ant worker
- OUTPUT_SIZE: 8x8
- PRIMARY_COLOR: dark brown
- ACCENT_COLOR: reddish-brown
- LEG_COUNT: 6
- MATERIAL_DESCRIPTION: hard chitinous shell, segmented body

---

## Natural Object Scaffold (Trees, Rocks, Plants)

**Output:** Variable size PNG, bottom-aligned

```
Create a pixel art {OBJECT_NAME} sprite for a 2D farming game.

Physical constraints:
- {OUTPUT_SIZE} pixel canvas with transparent background
- Object positioned at BOTTOM of frame (grounded)
- Footprint base: {FOOTPRINT_WIDTH}x{FOOTPRINT_HEIGHT} tiles (each tile = 16px)
- Viewed from 45-degree overhead angle

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- Top surfaces lit (55-65%), front faces dark (25-35%)
- {PRIMARY_COLOR} main color with {ACCENT_COLOR} details
- {SHAPE_DESCRIPTION}
- Dark base pixels showing ground contact

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, ground plane, background, glow effects
```

**Example fills (Tree):**
- OBJECT_NAME: oak tree
- OUTPUT_SIZE: 32x48
- FOOTPRINT_WIDTH: 1
- FOOTPRINT_HEIGHT: 1
- PRIMARY_COLOR: brown trunk, green canopy
- ACCENT_COLOR: darker brown bark, lighter green highlights
- SHAPE_DESCRIPTION: thick trunk at bottom, rounded leafy canopy above
- MATERIAL_DESCRIPTION: rough bark texture, clustered leaf masses

**Example fills (Rock):**
- OBJECT_NAME: large boulder
- OUTPUT_SIZE: 32x32
- FOOTPRINT_WIDTH: 2
- FOOTPRINT_HEIGHT: 2
- PRIMARY_COLOR: gray
- ACCENT_COLOR: darker gray shadows, lighter gray highlights
- SHAPE_DESCRIPTION: irregular rounded mass, chunky blocky form
- MATERIAL_DESCRIPTION: rough stone with clustered noise texture

---

## Furniture Scaffold

**Output:** Variable size PNG, bottom-aligned

```
Create a pixel art {FURNITURE_NAME} sprite for a 2D farming game.

Physical constraints:
- {OUTPUT_SIZE} pixel canvas with transparent background
- Furniture positioned at BOTTOM of frame (grounded)
- Footprint: {FOOTPRINT_WIDTH}x{FOOTPRINT_HEIGHT} tiles (each tile = 16px)
- Viewed from 45-degree overhead angle, seeing top and front

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- Top surface visible and lit (55-65%)
- Front face visible and dark (25-35%)
- {PRIMARY_COLOR} main material
- {ACCENT_COLOR} accents or hardware
- {FUNCTIONAL_ELEMENTS}
- Dark base pixels showing ground contact

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, ground plane, background, glow effects
```

**Example fills (Chest):**
- FURNITURE_NAME: wooden chest
- OUTPUT_SIZE: 16x16
- FOOTPRINT_WIDTH: 1
- FOOTPRINT_HEIGHT: 1
- PRIMARY_COLOR: warm brown wood
- ACCENT_COLOR: gold/brass metal fittings
- FUNCTIONAL_ELEMENTS: visible lid seam, metal clasp at front
- MATERIAL_DESCRIPTION: horizontal wood plank texture, metal hinges

**Example fills (Workbench):**
- FURNITURE_NAME: crafting workbench
- OUTPUT_SIZE: 32x24
- FOOTPRINT_WIDTH: 2
- FOOTPRINT_HEIGHT: 1
- PRIMARY_COLOR: natural wood tones
- ACCENT_COLOR: darker wood edges
- FUNCTIONAL_ELEMENTS: flat work surface on top, sturdy legs
- MATERIAL_DESCRIPTION: smooth wood planks, visible grain

---

## Block/Tile Scaffold

**Output:** 16x16 PNG, fills entire frame, tileable

```
Create a pixel art {BLOCK_NAME} tile for a 2D farming game.

Physical constraints:
- 16x16 pixel canvas, NO transparency (fills entire frame)
- Must tile seamlessly in all directions
- Viewed from 45-degree overhead angle

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left (subtle for tiles)
- {PRIMARY_COLOR} main color
- {SECONDARY_COLOR} variation
- {PATTERN_DESCRIPTION}
- Subtle variation, no strong directional patterns

Material: {MATERIAL_DESCRIPTION}

DO NOT include: borders, edges, shadows, directional elements
```

**Example fills:**
- BLOCK_NAME: dirt
- PRIMARY_COLOR: brown
- SECONDARY_COLOR: darker brown
- PATTERN_DESCRIPTION: horizontal strata with scattered speckles
- MATERIAL_DESCRIPTION: packed earth with small pebbles

---

## Tool/Item Scaffold

**Output:** 16x16 PNG, centered composition

```
Create a pixel art {ITEM_NAME} icon for a 2D farming game inventory.

Physical constraints:
- 16x16 pixel canvas with transparent background
- Item CENTERED in frame with breathing room
- Angled for clarity (handle bottom-left, head top-right typical)

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- {PRIMARY_COLOR} main material
- {ACCENT_COLOR} secondary material
- Clear separation between {PART_1} and {PART_2}
- Iconic silhouette, instantly readable

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, background, glow effects
```

**Example fills:**
- ITEM_NAME: iron pickaxe
- PRIMARY_COLOR: gray iron
- ACCENT_COLOR: brown wood
- PART_1: metal head
- PART_2: wooden handle
- MATERIAL_DESCRIPTION: polished metal pick head, worn wood handle

---

## Player Character Scaffold

**Output:** 16x32 PNG, bottom-aligned, 4 directions needed

```
Create a pixel art {CHARACTER_CLASS} character sprite for a 2D farming game.

Physical constraints:
- 16x32 pixel canvas with transparent background
- Character positioned at BOTTOM of frame (feet grounded)
- Facing: {DIRECTION} (down/up/left/right)
- Viewed from 45-degree overhead angle

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- {SKIN_TONE} skin
- {OUTFIT_DESCRIPTION}
- {HAIR_DESCRIPTION}
- Simple facial features (2 dot eyes, no mouth visible)
- Dark base pixels at feet

Character details:
- Class: {CHARACTER_CLASS}
- Outfit colors: {PRIMARY_OUTFIT_COLOR}, {ACCENT_COLOR}
- Distinguishing feature: {UNIQUE_ELEMENT}

DO NOT include: drop shadows, ground plane, background, accessories in hand
```

**Example fills:**
- CHARACTER_CLASS: farmer
- DIRECTION: down
- SKIN_TONE: light peach
- OUTFIT_DESCRIPTION: overalls with short-sleeve shirt
- HAIR_DESCRIPTION: short brown hair
- PRIMARY_OUTFIT_COLOR: blue denim overalls
- ACCENT_COLOR: white shirt
- UNIQUE_ELEMENT: straw hat

---

## Ore/Deposit Scaffold

**Output:** 16x16 or 32x32 PNG, bottom-aligned

```
Create a pixel art {ORE_NAME} deposit sprite for a 2D farming game.

Physical constraints:
- {OUTPUT_SIZE} pixel canvas with transparent background
- Deposit positioned at BOTTOM of frame (embedded in ground)
- Viewed from 45-degree overhead angle

Visual style:
- Terraria-style chunky pixel art
- Light source: top-left
- Rock base: gray stone
- Ore veins: {ORE_COLOR} crystalline/metallic patches
- Top surface lit, front face dark
- {VEIN_PATTERN} ore distribution
- Dark base pixels showing ground contact

Material: {MATERIAL_DESCRIPTION}

DO NOT include: drop shadows, ground plane, background, glow effects
```

**Example fills:**
- ORE_NAME: copper ore
- OUTPUT_SIZE: 16x16
- ORE_COLOR: orange-brown copper
- VEIN_PATTERN: scattered patches across surface
- MATERIAL_DESCRIPTION: gray stone with exposed copper veins, slight metallic sheen on ore

---

## Validation Checklist

After generating, verify:

- [ ] Correct dimensions
- [ ] Transparent background (except blocks)
- [ ] Correct anchoring for category
- [ ] Top surfaces lighter than front faces
- [ ] Chunky, not thin
- [ ] Material reads instantly
- [ ] No forbidden elements (shadows, backgrounds, glow)
- [ ] Matches existing BugFarmer sprites in style

---

## ComfyUI Generation

### Setup
```bash
cd ~/ComfyUI && source venv/bin/activate && python main.py --listen 0.0.0.0
# Open http://localhost:8188
```

### Settings
- **Model:** SDXL 1.0 + Pixel Art XL LoRA (strength 0.8-1.0)
- **Size:** 256x256 or 512x512
- **Sampler:** DPM++ 2M Karras, 20-30 steps
- **CFG:** 7-8

### Post-processing
1. Pixelate (factor 8 or 16 depending on desired detail)
2. Rembg (remove background)
3. Scale to target size using Nearest Neighbor / Point filter
4. Validate against checklist
5. Save as PNG with transparency
