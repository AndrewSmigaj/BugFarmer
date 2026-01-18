# GPT-Image Sprite Generation Pipeline

## Terraria/Zelda-Style Game Assets for Bug Farmer

---

## Purpose

This document defines how Claude Code generates sprite images using OpenAI `gpt-image-1`, replacing the existing Python-based sprite drawing step.

- **Claude Code** remains responsible for all reasoning and geometry
- **gpt-image-1** is used only for pixel synthesis
- Claude validates the result

---

## What This Pipeline Replaces

| Replaced | Unchanged |
|----------|-----------|
| Python scripts that draw sprites procedurally | Style guide parsing |
| | Perspective guide parsing |
| | Geometry inference (cells, footprint, height) |
| | Pivot / ground alignment logic |
| | Animation definitions |
| | JSON entity definitions |
| | Unity / Nakama integration |

The old Python scripts in `tools/` are kept as reference and fallback.

---

## Core Principle

> **Claude decides the spatial contract.**
> **GPT-Image fills that contract with pixels.**
> **Claude validates the result.**

The image model does not infer size, footprint, or placement.

---

## Preconditions (Before Image Generation)

Before calling gpt-image-1, Claude reads the object definition from the database:

| DB Field | Description | Example |
|----------|-------------|---------|
| `category` | Object category | "natural", "furniture", "bee" |
| (key) | Asset identifier | "tree_oak", "honeybee" |
| `world.footprint` | [width, height] in cells | [2, 2] |
| `sprite_w` | Target sprite width in pixels | 32 |
| `sprite_h` | Target sprite height in pixels | 48 |
| `world.pivot` | Anchor type (occupants/placeables only, bugs default "c") | "c" or "bc" |

**Important**: GPT-image-1 outputs at fixed sizes (1024x1024, etc). We do NOT resize/downsample the bitmap. Unity scales sprites at runtime via `Transform.localScale` to match the target `sprite_w` × `sprite_h` from the database.

---

## Workflow by Scenario

### Scenario A: Existing Asset (in occupants.json or placeables.json)
1. Look up asset by key
2. Read: category, sprite_w, sprite_h, world.footprint, world.pivot
3. Proceed to prompt construction

### Scenario B: New Asset (not in database)
1. Determine values based on similar existing assets:
   - category: Match to existing DB categories
   - sprite_w/h: Use SIZE STANDARDS (multiples of 16, match similar items)
   - footprint: Visual size / 16 (rounded)
   - pivot: "bc" for grounded, "c" for floating/flying
2. Add entry to appropriate DB file (occupants.json or placeables.json)
3. Proceed to prompt construction

---

## Asset Categories

### Database Categories (occupants.json)

| DB Category | Examples | Bitmap Anchoring | Pivot |
|-------------|----------|------------------|-------|
| `natural` | Trees, bushes, rocks, flowers | BOTTOM (grounded) | "bc" or "c" |
| `block` | Dirt, stone, ore blocks | FULL-FRAME (3/4 view) | "bc" |
| `structure` | Fences, walls, doors, gates | BOTTOM (grounded) | "bc" |
| `crafting` | Workbench, furnace, anvil | BOTTOM (grounded) | "bc" |
| `furniture` | Tables, chairs, beds | BOTTOM (grounded) | "bc" |
| `storage` | Chests, barrels, crates | BOTTOM (grounded) | "bc" or "c" |
| `lighting` | Lamps, torches | BOTTOM or CENTERED | "bc" or "c" |
| `beekeeping` | Beehives, honey extractor | BOTTOM (grounded) | "bc" |

### Database Categories (bugs.json)

| DB Category | Examples | Bitmap Anchoring | Notes |
|-------------|----------|------------------|-------|
| `bee`, `wasp`, `butterfly`, `moth`, `fly` | Flying insects | CENTERED (they float) | Small sprites |
| `ant`, `beetle`, `spider`, `scorpion`, `centipede`, `hopper` | Walking/crawling | CENTERED (for animation) | Ground contact implied |

### Anchoring Rule

**Grounded objects (pivot "bc"):**
- Artwork touches BOTTOM of bitmap frame
- Bottom of sprite aligns with footprint cells in game
- Visual can extend UPWARD beyond footprint (trees, tall furniture)

**Flying/floating (pivot "c"):**
- Artwork CENTERED in bitmap frame
- No implied ground contact

**Code reference** (`TilemapManager.cs` line 585):
```csharp
worldPos.y += pivot.y * spriteHeightCells * cellSize;
// For "bc": pivot.y = 0, no adjustment → bottom at cell
// For "c": pivot.y = 0.5, shifts up → center at cell
```

---

## Base Prompt (Always Included)

```
Create a 2D game sprite that strictly follows the provided style guide and perspective guide.

Asset: {asset_name}

Requirements:
- Transparent background
- Render only the object itself
- No background elements or environment
- Object fully contained within the frame
- No padding, borders, or cropping
- Consistent scale and framing

This image will be used directly as a sprite in a 2D game.
```

---

## Category-Specific Prompt Variants

Claude selects exactly one variant based on asset category.

**Anchoring depends on category - grounded objects are BOTTOM-aligned, flying bugs are CENTERED.**

### 1. Flying Bugs (CENTERED in frame)

```
This asset represents a flying creature.

Additional requirements:
- CENTER the creature in the frame (it floats)
- No implied ground contact
- No bottom anchoring
- Sprite should feel suspended
- Leave breathing room on all edges
- No shadows or ground planes below the creature
```

**Validation focus**: Centered horizontally and vertically, no edge clipping

### 2. Grounded Bugs (BOTTOM-aligned)

```
This asset represents a walking/crawling creature.

Additional requirements:
- Artwork touches BOTTOM of frame (walks on ground)
- Legs contact the bottom edge of the frame
- Horizontal centering OK
- No shadows in the sprite itself
- Creature appears grounded and stable
```

**Validation focus**: Bottom edge contact, horizontally centered

### 3. Natural Objects - Trees, Bushes, Rocks (BOTTOM-aligned)

```
This asset represents a natural world object.

Additional requirements:
- Artwork touches BOTTOM of frame
- Base/trunk/bottom of object at frame bottom
- Object may extend UPWARD beyond footprint size
- Horizontal centering OK
- No shadows extending outside the object
- Ground contact line at bottom via dark base pixels
```

**Validation focus**: Bottom-aligned, can extend upward

**Example**: tree_oak with 2×2 footprint and 32×48 sprite size
- Trunk bottom at frame bottom
- Canopy extends upward beyond the 2×2 footprint area

### 4. Furniture / Props (BOTTOM-aligned)

```
This asset represents a static world object.

Additional requirements:
- Artwork touches BOTTOM of frame
- Object base aligns with footprint cells when placed
- May extend UPWARD (taller than footprint OK)
- TOP SURFACE DOMINATES (55-65%)
- Front face clearly visible but darker (25-35%)
- Horizontal centering OK
```

**Validation focus**: Bottom-aligned, top surface visible

**Example**: Bookshelf with [2,3] footprint
- Bottom of bookshelf at frame bottom
- Height extends upward
- When placed, bottom aligns with footprint cells

### 5. Blocks / Tiles (FULL-FRAME)

```
This asset represents a world tile.

Additional requirements:
- COMPLETELY FILL THE FRAME
- Edges clean and consistent for tiling
- No shadows extending beyond the tile boundary
- For 3/4 blocks: top 55-65%, front 25-35%
```

**Validation focus**: Full-frame occupancy, edge consistency

### 6. Icons (CENTERED)

```
This asset represents a UI icon.

Additional requirements:
- CENTER the icon in the frame
- High visual clarity at small sizes
- Avoid fine detail that will be lost when scaled down
- No implied ground or world lighting
```

**Validation focus**: Centered mass, readability

### 7. Tools (CENTERED)

```
This asset represents a handheld item.

Additional requirements:
- CENTER the object in the frame
- Clearly readable silhouette
- Balanced visual weight
- Angled 45° for dynamic look
- Handle and head clearly separated
```

**Validation focus**: Centered, silhouette clarity

### 8. Effects (CENTERED)

```
This asset represents a visual effect.

Additional requirements:
- CENTER the effect in the frame
- Use transparency intentionally
- No implied physical weight
- Suitable for additive or alpha blending
```

**Validation focus**: Centered, clean alpha

### 9. Players (BOTTOM-aligned)

```
This asset represents a playable character.

Additional requirements:
- Artwork touches BOTTOM of frame (feet on ground)
- Humanoid proportions (Zelda/Terraria style)
- Clear directional facing
- Consistent limb placement for animation
- Character is grounded, feet at bottom edge
```

**Validation focus**: Bottom-aligned, consistent proportions across directions

---

## Master Style Guide (Load Into Context)

This guide must be loaded for every generation. It consolidates `sprite_guidelines.md` and `SPRITE_GENERATION_GUIDE.md`.

---

### 1. CAMERA & PERSPECTIVE (Non-Negotiable)

```
45° overhead (RPG perspective, bird's eye with slight angle)

What player sees:
- Top surfaces of objects (viewed from directly above)
- Front faces of vertical elements (drawn front-on, 1:1)

NEVER show:
- Left/right side faces
- Isometric diamond tops
- True side views

Plane Rules:
- Horizontal planes (tops): squares stay square, circles stay circular
- Vertical planes (fronts): darker than tops, drawn front-on
- Depth comes from CONTRAST, not perspective distortion
```

### 2. THICKNESS RATIOS (Critical for Terraria Feel)

```
Everything has thickness — even if it shouldn't.

Standard Ratios:
- 55–65% top surface (lit)
- 25–35% front face (dark)
- Remaining: trim / edge

Hard Rules:
- No 1-pixel front faces on solid objects
- If front face <2px → looks flat (reject)
- If front face >50% → looks like side view (reject)
- If it feels chunky → correct
```

### 3. LIGHTING (Cheat Aggressively)

```
Light source: TOP-LEFT (always, non-negotiable)
Lighting is STYLIZED, not realistic

Value Rules:
- Top surfaces → LIGHT
- Front faces → DARK
- Plane boundaries → HARD CONTRAST

If lighting feels "too strong," it's probably correct.
```

### 4. THREE-SHADE COLOR SYSTEM

```
Every material uses exactly 3 shades:
- Light: top surfaces, highlights, top-left edges
- Base: main surface
- Dark: front faces, shadows, bottom-right edges, contact edges

Standard Palettes (RGB):

Wood:
  Dark:  (70, 50, 35)
  Base:  (120, 90, 60)
  Light: (160, 130, 95)

Stone:
  Dark:  (85, 85, 90)
  Base:  (120, 120, 125)
  Light: (155, 155, 160)

Metal (Iron):
  Dark:  (60, 65, 70)
  Base:  (100, 105, 110)
  Light: (150, 155, 160)

Foliage (Green):
  Dark:  (40, 85, 40)
  Base:  (55, 120, 55)
  Light: (80, 150, 70)

Dirt:
  Dark:  (110, 75, 40)
  Base:  (140, 95, 50)
  Light: (165, 120, 70)

Rules:
- No pure black
- No pure white (use off-white/cream)
- Slightly muted saturation (not neon)
- Materials should read BEFORE objects do
```

### 5. GROUND CONTACT (Visual, Not Bitmap Position)

```
Every object must VISUALLY sit on the ground.

Use at least one:
- Dark base pixels
- Implied shadow (darker pixels bottom-right)
- Flat contact line

This is about VISUAL DESIGN, not bitmap anchoring.
The sprite bitmap is centered, but the artwork shows ground contact.

Floating sprites are INVALID.
```

### 6. SHAPE DESIGN (Simplify Hard)

```
- Use blocky, orthogonal shapes
- Reduce curves to suggestions
- Remove detail until readability breaks — then stop
- Favor symmetry over realism
- Align major edges to pixel grid

Ask: "What is the minimum shape that still reads?"
Then remove one more thing.
```

### 7. TEXTURE (Patterned, Not Noisy)

```
Use controlled repetition, avoid random dithering.

Examples:
- Wood → horizontal plank bands
- Stone → clustered noise
- Dirt → horizontal strata + speckles

Think fabric, not photograph.
```

### 8. EDGE DEFINITION (Cheated Outlines)

```
Use darker material-relative edges (not black outlines).

Apply selectively to:
- Bottom edges
- Contact points
- Occlusion boundaries

This improves separation in cluttered scenes.
```

### 9. SIZE STANDARDS (from database)

```
Target pixel sizes (sprite_w × sprite_h):
- Bugs: 8×8 to 32×32 (ant_worker 8×8, honeybee 10×10, butterfly 16×16, tarantula 24×24)
- Small natural objects: 16×16 to 16×24 (bushes, flowers, small rocks)
- Trees: 16×32 to 32×52 (tree_dead 16×32, tree_oak 32×48, tree_pine 32×52)
- Furniture/crafting: 16×20 to 32×48 (chair 16×20, table 32×24, bed 32×48)
- Blocks: 16×20 (3/4 view with front face)

Base cell = 16px. Most sprites are multiples of 16.

GPT generates at 1024×1024, we trim whitespace, Unity scales
to target size via Transform.localScale.

NEVER fix design problems with more visual complexity.
If it needs more detail, the design is wrong.
```

### 10. FINAL ACCEPTANCE CHECKLIST

```
☐ Chunky enough (not thin)
☐ Strong plane contrast (top light, front dark)
☐ Material reads instantly (can tell wood/stone/metal)
☐ Anchored to ground VISUALLY (dark base pixels for grounded objects)
☐ Matches existing sprites (style consistency)
☐ Readable at game zoom (not just in editor)
☐ Correct anchoring per category (centered vs bottom-aligned)
☐ Transparent background
☐ No shadows extending outside object
☐ Content not clipped after whitespace trim

Fail any one → regenerate.
```

---

### DESIGN PHILOSOPHY (One Sentence)

> BugFarmer sprites should look **simple, solid, and slightly overbuilt** — because clarity beats correctness.

---

## Prompt Scaffolds (Fill-in Templates)

These scaffolds combine the base prompt + category variant + style guide into ready-to-use templates.

### Flying Bug Scaffold

```
Create a 2D game sprite.

Asset: {BUG_NAME}
Category: flying_bug

STYLE REQUIREMENTS:
- 45° overhead view (bird's eye with slight angle)
- Light source: top-left
- Transparent background
- Three-shade coloring (light/base/dark per material)
- Chunky, slightly overbuilt appearance
- No pure black, no pure white
- Muted saturation

SPATIAL REQUIREMENTS:
- Center the creature around its pivot point
- No ground contact or bottom anchoring
- Sprite should feel suspended
- Do not drift off any edge
- Leave breathing room on all sides

DESIGN REQUIREMENTS:
- Body silhouette is primary identifier
- Wings semi-transparent where applicable
- Eyes as accent color
- Remove detail until readability breaks, then stop
- If it feels chunky, it's correct

This image will be used directly as a sprite in a 2D game.
```

### Grounded Bug Scaffold

```
Create a 2D game sprite.

Asset: {BUG_NAME}
Category: grounded_bug (walking insect)

STYLE REQUIREMENTS:
- 45° overhead view
- Light source: top-left
- Transparent background
- Three-shade coloring
- Chunky appearance
- No pure black, no pure white

SPATIAL REQUIREMENTS:
- Center the sprite around its pivot
- Legs imply ground contact but do NOT anchor to bottom of frame
- Maintain centered vertical framing
- No shadows or ground planes below creature
- Animation states should not cause vertical jumps

DESIGN REQUIREMENTS:
- Body silhouette first
- Legs clearly visible, implying walking posture
- Eyes as accent
- Chunky, simplified shapes
```

### Natural Object Scaffold (Trees, Rocks, Plants)

```
Create a 2D game sprite.

Asset: {OBJECT_NAME}
Category: natural_object

STYLE REQUIREMENTS:
- 45° overhead view
- Light source: top-left
- Top surfaces: 55-65% of sprite height, LIT
- Front faces: 25-35% of sprite height, DARK
- Strong plane contrast at boundaries
- Transparent background
- Three-shade coloring for each material

SPATIAL REQUIREMENTS:
- Center sprite around its pivot point
- Object may extend upward within frame
- Do NOT bottom-anchor
- VISUAL ground contact via dark base pixels (but bitmap centered)
- No floating appearance

DESIGN REQUIREMENTS:
- Blocky, orthogonal shapes
- Reduce curves to suggestions
- Dark material-relative edges on bottom/contact points
- {SPECIFIC_NOTES}
```

### Furniture Scaffold

```
Create a 2D game sprite.

Asset: {FURNITURE_NAME}
Category: furniture

STYLE REQUIREMENTS:
- 45° overhead view
- Light source: top-left
- TOP SURFACE DOMINATES (55-65%)
- Front face clearly visible but darker (25-35%)
- Transparent background
- Three-shade wood/metal coloring
- {MATERIAL} palette: dark {DARK_RGB}, base {BASE_RGB}, light {LIGHT_RGB}

SPATIAL REQUIREMENTS:
- Center sprite around pivot
- May extend upward (taller than footprint OK)
- Do NOT bottom-anchor
- Visual ground contact via dark base pixels

DESIGN REQUIREMENTS:
- Functional silhouette first
- Show TOP of object (table top, chest lid, etc.)
- Wood grain horizontal for tables
- Clear recognizable shape at game zoom
```

### Block/Tile Scaffold

```
Create a 2D game sprite.

Asset: {BLOCK_NAME}
Category: block (world tile)

STYLE REQUIREMENTS:
- 45° overhead view
- Light source: top-left
- For 3/4 blocks: top 55-65%, front 25-35%
- Three-shade coloring
- {MATERIAL} palette: dark {DARK_RGB}, base {BASE_RGB}, light {LIGHT_RGB}

SPATIAL REQUIREMENTS:
- COMPLETELY FILL THE FRAME
- No centering (exception to normal rules)
- Edges clean and consistent for tiling
- No shadows extending beyond tile boundary

DESIGN REQUIREMENTS:
- Must tile seamlessly
- Subtle variation, not busy
- Avoid strong directional patterns
- Texture: {TEXTURE_PATTERN}
```

### Tool/Item Scaffold

```
Create a 2D game sprite.

Asset: {TOOL_NAME}
Category: tool (handheld item)

STYLE REQUIREMENTS:
- 45° overhead view (or angled 45° for dynamic look)
- Light source: top-left
- Transparent background
- Three-shade coloring per material

SPATIAL REQUIREMENTS:
- Center the object around its pivot
- No ground contact implied
- Clear silhouette at all angles

DESIGN REQUIREMENTS:
- Handle and head clearly separated
- Iconic recognizable shape
- Material colors distinct (wood brown, metal gray)
- Readable in inventory at small size
```

### Player Character Scaffold

```
Create a 2D game sprite.

Asset: {CLASS_NAME}_{DIRECTION}
Category: player (playable character)

STYLE REQUIREMENTS:
- 45° overhead view (Terraria player style)
- Light source: top-left
- Transparent background
- Humanoid proportions

SPATIAL REQUIREMENTS:
- Center sprite around pivot
- Feet do NOT touch bottom of frame
- No bottom anchoring
- Animation states must not cause vertical jumps

DESIGN REQUIREMENTS:
- Clear directional facing: {DIRECTION}
- Consistent limb placement for animation
- {CLASS_DESCRIPTION}
- Readable silhouette
```

---

## Animation Scaffolds

### Reference Frame Scaffold (Use First)

```
Create a 2D game sprite - this is the REFERENCE FRAME (frame 0).

Asset: {ASSET_NAME}
Category: {CATEGORY}
Animation: {ANIMATION_TYPE}

[Include all category-specific style/spatial/design requirements from above]

REFERENCE FRAME REQUIREMENTS:
- This is frame 0 / idle pose / base position
- This establishes the canonical appearance
- All future frames will be based on this
- Ensure clear, clean execution
```

### Animation Frame Scaffold (Use After Reference)

```
Create frame {FRAME_NUMBER} of an animation sequence.

Asset: {ASSET_NAME}
Reference: [Attach reference image / frame 0]
Animation: {ANIMATION_TYPE}

CONSISTENCY REQUIREMENTS (CRITICAL):
- Match EXACT colors from reference
- Match EXACT proportions from reference
- Match EXACT bounding box size
- Maintain same centroid position (within 2px)
- Same overall style and shading approach

THIS FRAME SHOWS:
{FRAME_DESCRIPTION}

Example for flying bug frame 2:
"Wings at lowest position (fully down), body in same position as reference"

Example for tree frame 1:
"Canopy shifted slightly left as if by gentle wind, trunk unchanged"
```

---

## Image Generation Call

### API Endpoints

**For static sprites and reference frames:**
```
POST https://api.openai.com/v1/images/generations
```

**For animation frames (with reference image):**
```
POST https://api.openai.com/v1/images/edits
```
Use the edits endpoint to provide the reference frame as input, ensuring style consistency.

### API Parameters

```bash
curl -X POST "https://api.openai.com/v1/images/generations" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-1",
    "prompt": "{BASE_PROMPT}\n\n{CATEGORY_VARIANT}\n\nStyle Guide:\n{STYLE_GUIDE}",
    "size": "1024x1024",
    "background": "transparent",
    "quality": "low",
    "output_format": "png"
  }' | jq -r '.data[0].b64_json' | base64 --decode > "{output_path}"
```

**Note**: gpt-image-1 only supports: 1024x1024, 1024x1536, 1536x1024. Use 1024x1024 for most sprites.

### Post-Processing (ComfyUI)

**DO NOT RESIZE THE BITMAP.** Unity handles scaling at runtime.

Post-processing trims whitespace only:

```
LoadImage → JoinImageWithAlpha → FastAlphaCropper (padding: 0) → SaveImage
```

The output is the trimmed full-resolution image. Unity scales it to the correct game-world size via `Transform.localScale` when spawning objects.

---

## Validation Steps (Mandatory)

### 1. Transparency Check

```python
from PIL import Image
img = Image.open(path).convert('RGBA')
alpha = [p[3] for p in img.getdata()]
assert min(alpha) < 255, "Image has no transparency"
```

**On failure**: Regenerate (max 2 attempts)

### 2. Whitespace Trimmed

After FastAlphaCropper, verify the sprite content is not clipped (all opaque pixels preserved).

### 3. Anchoring Validation

Anchoring depends on the asset's pivot value:

| Pivot | Bitmap Anchoring | Validation |
|-------|------------------|------------|
| "c" | CENTERED | Content centered in trimmed bounds |
| "bc" | BOTTOM-ALIGNED | Content touches bottom of trimmed bounds |

GPT generates at 1024x1024. After trimming:
- "c" assets: Trimmed bitmap has content centered
- "bc" assets: Trimmed bitmap has content at bottom edge

| Check | Description |
|-------|-------------|
| Horizontal centering | Sprite centered horizontally within a few pixels tolerance |
| Vertical positioning | Matches pivot type (centered for "c", bottom for "bc") |
| Breathing room | Transparent padding appropriate for category |
| No shadows | No ground planes or drop shadows in bitmap |
| No clipping | Sprite content fully preserved after trim |

### 4. Category-Specific Checks

| Asset Type | DB Categories | Additional Validation |
|------------|---------------|----------------------|
| Flying bugs | bee, wasp, butterfly, moth, fly | Centered, no hovering off edges |
| Ground bugs | ant, beetle, spider, scorpion, etc. | Centered, legs imply walking |
| Natural objects | natural | Bottom-aligned per pivot |
| Furniture/crafting | furniture, crafting, storage | Bottom-aligned per pivot |
| Blocks | block | Full-frame occupancy |
| Structures | structure | Bottom-aligned per pivot |

### 5. Animation Consistency (If Applicable)

- Generate frame 0 first as reference
- Compare subsequent frames for:
  - Consistent bounding box
  - **No vertical drift** (critical - prevents animation jumps)
  - Stable centroid across all frames

---

## Animation Workflow

### Which Assets Are Animated?

| Category | Animated? | Animation Type |
|----------|-----------|----------------|
| Flying bugs | Yes | Wing flapping, hover motion |
| Grounded bugs | Yes | Leg movement, body motion |
| Trees | Yes | Subtle sway, leaf rustle |
| Plants/flowers | Maybe | Wind sway |
| Furniture | No | Static |
| Blocks/tiles | No | Static |
| Tools | No | Static |
| Players | Yes | Walk cycle (4 directions) |
| Effects | Yes | Particle animation |

### Animation Generation Steps

**Step 1: Generate Reference Image (Frame 0)**
```
Create base pose / idle frame:
- This is the canonical appearance
- All future frames must match this style, proportions, colors
- Save as {asset_name}_frame_00.png
```

**Step 2: Generate Animation Frames**
```
Using the reference image, generate frames 1-N:

Prompt addition for frame generation:
"Based on the provided reference image, create frame {N} of the animation.
Maintain exact same:
- Colors and shading
- Proportions and scale
- Bounding box size
- Centroid position

This frame shows: {ANIMATION_DESCRIPTION}"
```

**Step 3: Validate Frame Consistency**
```
For each frame, verify:
- Same dimensions as reference
- Centroid within 2px tolerance of reference
- No color palette drift
- No style drift
```

### Animation Prompt Variants

**Flying Bug Animation (4-8 frames)**
```
Frame 0: Wings fully up, body centered
Frame 1: Wings at 45° down
Frame 2: Wings fully down
Frame 3: Wings at 45° up
(repeat / reverse for loop)

Each frame: maintain exact body position, only wings move
```

**Tree Sway Animation (4-6 frames)**
```
Frame 0: Neutral position
Frame 1: Slight lean left, foliage shifted
Frame 2: Back to neutral
Frame 3: Slight lean right, foliage shifted
(loop)

Trunk stays fixed, only canopy sways
```

**Player Walk Cycle (4 frames per direction)**
```
Direction: {up/down/left/right}
Frame 0: Idle/stand
Frame 1: Left foot forward
Frame 2: Pass-through (feet together)
Frame 3: Right foot forward
(loop 1-2-3-2 or similar)

Body maintains center position, only limbs animate
```

---

## Output Contract

### File Paths

```
BugFarmerClient/Assets/Resources/
├── Bugs/{sprite_id}.png         (from species.json sprite_id)
├── Objects/{key}.png            (from occupants.json or placeables.json key)
├── Items/{item_id}_icon.png     (inventory icons)
├── Player/{class}_{direction}.png
└── Effects/{effect_name}.png

BugFarmerClient/Assets/Sprites/
└── Terrain/{tile_id}.png        (from tiles.json)
```

**Loading conventions:**
- Bugs: `Resources.Load<Sprite>($"Bugs/{spriteId}")` - spriteId from species.json
- Objects: `Resources.Load<Sprite>($"Objects/{key}")` - key = JSON object key

### Metadata Confirmation

After successful generation, emit:

```json
{
  "asset": "tree_oak",
  "category": "natural",
  "bitmap_size_px": [576, 842],
  "target_size_px": [32, 48],
  "footprint": [2, 2],
  "pivot": "bc",
  "alpha_verified": true,
  "trimmed": true
}
```

**Note**: `bitmap_size_px` is the actual trimmed image dimensions (varies per image). `target_size_px` is `sprite_w`/`sprite_h` from the database - Unity scales the bitmap to this size.

---

## Footprint Guidelines (From Database)

### Example Objects from occupants.json

| Object | sprite_w×h | footprint_w×h | Pivot | Notes |
|--------|------------|---------------|-------|-------|
| tree_oak | 32×48 | 2×2 | bc | Canopy overhangs |
| tree_pine | 32×52 | 2×2 | bc | Tall trunk |
| tree_palm | 32×48 | 2×2 | bc | Single trunk |
| tree_fruit | 32×44 | 2×2 | bc | Standard |
| tree_dead | 16×32 | 1×1 | bc | Bare trunk |
| bush | 16×16 | 1×1 | c | Low vegetation |
| rock_large | 32×32 | 2×2 | c | Solid mass |
| workbench | 32×20 | 2×1 | bc | Crafting station |
| chest_wood | 32×20 | 2×1 | bc | Storage |

**sprite_w×h** is the target pixel size. Unity scales the bitmap to this.

**footprint_w×h** is how many cells the object occupies for collision/placement.

**Bitmap size varies** - after trimming whitespace, each generated sprite has different pixel dimensions. Unity scales to match sprite_w×h.

---

## Failure Policy

- Max 2 regeneration attempts per asset
- Fail fast on repeated violations
- **Never silently accept**:
  - Missing transparency
  - Content clipped by trimming
  - Misaligned grounding (centered vs bottom-anchored)
  - Checkerboard artifacts

---

## Database Reference

### Authoritative Files

| File | Purpose | Loaded By |
|------|---------|-----------|
| `nakama/data/entities/occupants.json` | Natural world objects | Server (entities.go) |
| `nakama/data/entities/placeables.json` | Player-placeable items | Server (entities.go) |
| `nakama/data/species.json` | Bug/species definitions | Server (match.go) |
| `nakama/data/tiles.json` | Tile definitions | Server (match.go) |

### occupants.json / placeables.json Structure

```json
"tree_oak": {
  "name": "Oak Tree",
  "category": "natural",
  "sprite_w": 32,
  "sprite_h": 48,
  "world": {
    "footprint": [1, 1],
    "pivot": "bc",
    "blocks_players": true,
    "blocks_bugs": true,
    "breakable": { ... }
  }
}
```

**Key fields for sprite generation:**
- `sprite_w`, `sprite_h`: Target pixel dimensions
- `world.footprint`: [width, height] in cells
- `world.pivot`: "bc" (bottom-center) or "c" (center)

### species.json Structure (for bugs)

```json
"fly_common": {
  "display_name": "Common Fly",
  "sprite_id": "fly_common",
  "ai": { ... },
  "swarm": { ... }
}
```

**Key fields for sprite generation:**
- `sprite_id`: Used to load sprite from `Resources/Bugs/{sprite_id}.png`
- Bugs default to centered pivot ("c")

**Important**: The `pivot` field determines how Unity positions the sprite. Don't change pivot values without testing.

---

## Agent Instructions

### For Claude Agents Using This Document

**Workflow A: Manual Sprite (no API access)**

1. **User provides raw sprite** to `tools/raw_sprites/{name}.png`

2. **Check if asset exists in DB**
   - Search `nakama/data/entities/occupants.json` or `placeables.json`
   - For bugs: search `nakama/data/species.json`

3. **If asset is NEW:**
   - Add entry to appropriate DB file
   - Occupants: natural objects that can't be picked up
   - Placeables: items player can place/pick up
   - Include: category, sprite_w, sprite_h, world.footprint, world.pivot

4. **Post-process (ComfyUI):**
   - LoadImage → JoinImageWithAlpha → FastAlphaCropper (padding: 0) → SaveImage
   - Output: Trimmed PNG at full resolution

5. **Save to Resources:**
   - Bugs: `BugFarmerClient/Assets/Resources/Bugs/{sprite_id}.png`
   - Objects: `BugFarmerClient/Assets/Resources/Objects/{key}.png`

---

**Workflow B: API-Generated Sprite (when API access available)**

1. **Check if asset exists in DB** (same as above)

2. **If asset is NEW:** Add DB entry first

3. **Construct prompt:**
   - Select scaffold based on category
   - Fill in asset name and any specific notes
   - Include full style guide

4. **Call gpt-image-1:**
   - POST to /v1/images/generations
   - model: "gpt-image-1", size: "1024x1024", background: "transparent"

5. **Post-process (ComfyUI):** Same as Workflow A

6. **Save to Resources:** Same as Workflow A

7. **Emit confirmation** with metadata JSON

---

## Workflow Summary

```
1. Claude reads object definition from database
   ├── Objects: entities/occupants.json or entities/placeables.json
   ├── Bugs: species.json (uses sprite_id)
   ├── Fields: category, sprite_w, sprite_h, world.footprint, world.pivot
   └── Note: bugs default to pivot "c" (centered)

2. Claude constructs prompt
   ├── Base prompt
   ├── + Category variant (based on DB category)
   └── + Style guide

3. Call gpt-image-1
   └── Generate at 1024x1024 with transparent background

4. Post-process (ComfyUI)
   └── Trim whitespace with FastAlphaCropper (NO RESIZE)

5. Validate
   ├── Transparency present
   ├── Content not clipped
   └── Anchoring correct per pivot type

6. Save to Resources folder
   ├── Objects: Resources/Objects/{key}.png
   └── Bugs: Resources/Bugs/{sprite_id}.png

7. Unity loads sprite and scales via Transform.localScale
   └── Scale = sprite_w / bitmap_width, sprite_h / bitmap_height
```

---

## Cost

| Quality | Cost/Image |
|---------|------------|
| Low | ~$0.02 |
| Medium | ~$0.07 |
| High | ~$0.19 |

**Default: Low** for iteration. Use High for final production.

---

## Sources

- [OpenAI Image Generation Guide](https://platform.openai.com/docs/guides/image-generation)
- [OpenAI Images API Reference](https://platform.openai.com/docs/api-reference/images/)
- [GPT Image 1 Model Documentation](https://platform.openai.com/docs/models/gpt-image-1)
