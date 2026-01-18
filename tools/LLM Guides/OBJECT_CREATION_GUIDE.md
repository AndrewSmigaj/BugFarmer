# Object Creation Guide

Complete step-by-step workflow for adding new objects to Bug Farmer.

---

## Overview

```
1. Define entity in JSON (with sprite_w/sprite_h)
2. Construct image generation prompt
3. User generates image and places in tools/raw_sprites/
4. Trim whitespace (Python or ComfyUI - no resize)
5. Save to correct Resources folder (use absolute paths)
6. Fix Unity .meta file (if replacing existing sprite)
7. Sync JSON: server → client
8. Rebuild Nakama server
```

---

## Step 1: Define Entity in JSON

### File Locations

| Entity Type | JSON File | Description |
|-------------|-----------|-------------|
| **occupant** | `nakama/data/entities/occupants.json` | World-only (trees, rocks, ores) |
| **placeable** | `nakama/data/entities/placeables.json` | Inventory + world (furniture, blocks) |
| **item** | `nakama/data/entities/items.json` | Inventory-only (resources, tools) |
| **bug** | `nakama/data/species.json` | Spawned creatures |

### Required Fields

Every occupant/placeable MUST have:

```json
"object_id": {
  "name": "Display Name",
  "category": "natural|block|structure|furniture|crafting|storage|lighting",
  "sprite_w": 32,
  "sprite_h": 48,
  "world": {
    "footprint": [2, 2],
    "pivot": "bc"
  }
}
```

| Field | Description | Examples |
|-------|-------------|----------|
| `sprite_w` | Target width in pixels | 16, 32 |
| `sprite_h` | Target height in pixels | 16, 20, 24, 32, 48 |
| `footprint` | [width, height] in grid cells | [1,1], [2,1], [2,2] |
| `pivot` | Anchor point | "bc" (bottom-center), "c" (center) |

### Size Standards

| Object Type | Typical sprite_w×h | Footprint |
|-------------|-------------------|-----------|
| Small plants/flowers | 16×16 | [1,1] |
| Blocks/fences | 16×20 | [1,1] |
| Tall plants/chairs | 16×24 | [1,1] |
| Trees | 32×48 or 32×52 | [1,1] |
| Workbench/chest | 32×20 or 32×24 | [2,1] |
| Tables/furnace | 32×32 | [2,2] |
| Beds | 32×64 | [2,4] |

Base cell = 16px. Sprites can extend upward beyond footprint.

### JSON Examples

**Occupant (world-only):**
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
    "breakable": {
      "hp": 5,
      "required_tool_type": "axe",
      "required_tool_tier": 1,
      "drops": [{"item_id": "wood", "count": 4, "chance": 1.0}]
    }
  }
}
```

**Placeable (inventory + world):**
```json
"chest_wood": {
  "name": "Wooden Chest",
  "category": "storage",
  "sprite_w": 32,
  "sprite_h": 20,
  "stackable": false,
  "sell_price": 15,
  "world": {
    "footprint": [2, 1],
    "pivot": "bc",
    "interactable": true,
    "interaction_type": "storage",
    "breakable": {
      "hp": 2,
      "required_tool_type": "axe",
      "drops": [{"item_id": "chest_wood", "count": 1, "chance": 1.0}]
    }
  }
}
```

---

## Step 2: Construct Image Generation Prompt

### Base Prompt (always include)

```
Create a 2D game sprite.

Asset: {ASSET_NAME}
Category: {CATEGORY}

STYLE REQUIREMENTS:
- 45° overhead view (bird's eye with slight angle)
- Light source: top-left
- Transparent background
- Three-shade coloring (light/base/dark per material)
- Chunky, slightly overbuilt appearance
- No pure black, no pure white
- Muted saturation

This image will be used directly as a sprite in a 2D game.
```

### Category-Specific Additions

**For grounded objects (pivot "bc") - trees, furniture, blocks:**

```
SPATIAL REQUIREMENTS:
- Artwork touches BOTTOM of frame
- Object base at frame bottom
- May extend upward (taller than footprint OK)
- Horizontal centering OK
- Visual ground contact via dark base pixels

THICKNESS RATIOS:
- Top surface: 55-65% (lit)
- Front face: 25-35% (dark)
- Strong contrast at plane boundaries
```

**For centered objects (pivot "c") - bushes, small items:**

```
SPATIAL REQUIREMENTS:
- CENTER the object in the frame
- No bottom anchoring
- Leave breathing room on all edges
```

**For flying bugs:**

```
SPATIAL REQUIREMENTS:
- CENTER the creature in the frame (it floats)
- No ground contact
- Sprite should feel suspended
- No shadows below creature
```

### Material Palettes (RGB)

Include relevant palette in prompt:

```
Wood:
  Dark:  (70, 50, 35)
  Base:  (120, 90, 60)
  Light: (160, 130, 95)

Stone:
  Dark:  (85, 85, 90)
  Base:  (120, 120, 125)
  Light: (155, 155, 160)

Foliage:
  Dark:  (40, 85, 40)
  Base:  (55, 120, 55)
  Light: (80, 150, 70)
```

### Example Complete Prompt

```
Create a 2D game sprite.

Asset: tree_maple
Category: natural (tree)

STYLE REQUIREMENTS:
- 45° overhead view (bird's eye with slight angle)
- Light source: top-left
- Transparent background
- Three-shade coloring (light/base/dark per material)
- Chunky, slightly overbuilt appearance
- No pure black, no pure white

SPATIAL REQUIREMENTS:
- Artwork touches BOTTOM of frame
- Trunk base at frame bottom
- Canopy extends upward
- Horizontal centering OK
- Visual ground contact via dark base pixels at trunk

THICKNESS RATIOS:
- Top surface (canopy top): 55-65% visible, lit
- Front face (canopy front): 25-35% visible, darker

COLOR PALETTE:
Trunk (wood): dark (70,50,35), base (120,90,60), light (160,130,95)
Foliage: dark (40,85,40), base (55,120,55), light (80,150,70)

This image will be used directly as a sprite in a 2D game.
```

---

## Step 3: User Generates Image

**Tell the user:**

```
Please generate this sprite using gpt-image-1 (or your preferred image generator) with:
- Size: 1024x1024
- Transparent background
- The prompt above

Save the result to: tools/raw_sprites/{object_id}.png
```

Wait for user confirmation that the image is ready.

---

## Step 4: Trim Whitespace with ComfyUI

**DO NOT RESIZE.** Unity handles scaling at runtime.

### ComfyUI Workflow (trim only)

```
LoadImage → FastAlphaCropper (padding: 0) → SaveImage
```

### ComfyUI API Call

```bash
curl -X POST "http://localhost:8188/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "load": {
        "class_type": "LoadImage",
        "inputs": {"image": "raw_sprites/{object_id}.png"}
      },
      "crop": {
        "class_type": "FastAlphaCropper",
        "inputs": {
          "image": ["load", 0],
          "padding": 0
        }
      },
      "save": {
        "class_type": "SaveImage",
        "inputs": {
          "images": ["crop", 0],
          "filename_prefix": "{object_id}"
        }
      }
    }
  }'
```

Output appears in ComfyUI output folder.

### If ComfyUI Not Available

Use Python:

```python
from PIL import Image

def trim_whitespace(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    img.save(output_path)

trim_whitespace('tools/raw_sprites/tree_maple.png',
                'BugFarmerClient/Assets/Resources/Objects/tree_maple.png')
```

---

## Step 5: Save to Correct Folder

| Entity Type | Sprite Location |
|-------------|-----------------|
| Occupant | `Resources/Objects/{id}.png` |
| Placeable (world) | `Resources/Objects/{id}.png` |
| Placeable (icon) | `Resources/Items/{id}_icon.png` |
| Bug | `Resources/Bugs/{id}.png` |
| Item (icon only) | `Resources/Items/{id}_icon.png` |

Move trimmed sprite to correct location:

```bash
# For occupants/placeables (world sprite)
cp /mnt/c/Users/emily/BugFarmer/tools/raw_sprites/{object_id}_trimmed.png \
   /mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Objects/{object_id}.png
```

**IMPORTANT: Use absolute paths.** Relative paths may fail silently.

---

## Step 6: Fix Unity .meta File (If Replacing Existing Sprite)

When replacing an existing sprite, Unity's `.meta` file may have incorrect import settings from the old image.

### Check the .meta file

```bash
cat BugFarmerClient/Assets/Resources/Objects/{object_id}.png.meta
```

### Required Settings for Pixel Art

| Setting | Required Value | Description |
|---------|----------------|-------------|
| `spriteMode` | `1` | Single sprite (NOT 2 = sprite sheet) |
| `filterMode` | `0` | Point filtering (NOT 1 = Bilinear) |
| `spritePixelsToUnits` | `16` | Matches game grid |

### Fix spriteMode (if set to 2)

If the sprite shows as missing or wrong size, the .meta file may have `spriteMode: 2` (sprite sheet) with old sub-sprite definitions.

```bash
# Change spriteMode from 2 to 1
sed -i 's/spriteMode: 2/spriteMode: 1/' \
    BugFarmerClient/Assets/Resources/Objects/{object_id}.png.meta
```

Or edit the .meta file and change:
```yaml
spriteMode: 1      # Single sprite (was 2)
filterMode: 0      # Point filtering for pixel art
```

### For New Sprites

New sprites get a fresh .meta file with default settings. Unity should import correctly, but verify `filterMode: 0` for crisp pixel art.

---

## Step 7: Sync JSON to Client

```bash
cp /mnt/c/Users/emily/BugFarmer/nakama/data/entities/occupants.json \
   /mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Data/entities/
cp /mnt/c/Users/emily/BugFarmer/nakama/data/entities/placeables.json \
   /mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Data/entities/
```

---

## Step 8: Rebuild Nakama Server

```bash
cd /mnt/c/Users/emily/BugFarmer/nakama && docker compose up --build -d
```

---

## Validation Checklist

Before marking complete:

- [ ] JSON has `sprite_w` and `sprite_h` fields
- [ ] JSON has `world.footprint` and `world.pivot`
- [ ] Sprite has transparent background
- [ ] Sprite saved to correct Resources folder (use absolute paths!)
- [ ] Unity .meta file has `spriteMode: 1` and `filterMode: 0`
- [ ] Client JSON synced from server
- [ ] Server rebuilt with `docker compose up --build -d`

### Verify Transparency

```python
from PIL import Image
img = Image.open(path).convert('RGBA')
alpha = [p[3] for p in img.getdata()]
assert min(alpha) < 255, "No transparency - regenerate"
```

---

## Runtime Scaling (How It Works)

Unity scales sprites automatically based on `sprite_w`/`sprite_h`:

```csharp
// In TilemapManager.cs
var targetSize = EntityDatabase.GetSpriteSize(occupantId);
float scaleX = targetSize.x / sprite.rect.width;
float scaleY = targetSize.y / sprite.rect.height;
go.transform.localScale = new Vector3(scaleX, scaleY, 1f);
```

A 1024×1024 sprite with `sprite_w: 32, sprite_h: 48` renders identically to a native 32×48 sprite.

---

## Quick Reference

### Pivot Types

| Pivot | Meaning | Used For |
|-------|---------|----------|
| `"bc"` | Bottom-center | Trees, furniture, blocks (grounded) |
| `"c"` | Center | Bushes, flying bugs, small items |

### Common Categories

| Category | Examples |
|----------|----------|
| `natural` | Trees, bushes, rocks, flowers |
| `block` | Dirt, stone, ore blocks |
| `structure` | Fences, walls, doors |
| `furniture` | Tables, chairs, beds |
| `crafting` | Workbench, furnace, anvil |
| `storage` | Chests, barrels, crates |
| `lighting` | Torches, lamps |

### File Naming

| Type | Inventory | World |
|------|-----------|-------|
| Occupant | N/A | `Objects/{id}.png` |
| Placeable | `Items/{id}_icon.png` | `Objects/{id}.png` |
| Item | `Items/{id}_icon.png` | N/A |
| Bug | N/A | `Bugs/{id}.png` |
