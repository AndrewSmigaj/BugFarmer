# Creating New Objects in Bug Farmer

## Entity Types

| Type | JSON File | Description | Example |
|------|-----------|-------------|---------|
| **item** | `items.json` | Inventory-only | `wood`, `pickaxe_wood` |
| **occupant** | `occupants.json` | World-only (can't be placed by player) | `tree_oak`, `ore_iron_block` |
| **placeable** | `placeables.json` | Inventory + world (player places) | `dirt_block`, `chest_wood` |
| **bug** | `bugs.json` | Spawned creatures | `butterfly_common`, `honeybee` |

---

## File Locations

### JSON (Server = authoritative, copy to client)
```
nakama/data/entities/
├── items.json
├── occupants.json
└── placeables.json

BugFarmerClient/Assets/Resources/Data/entities/
├── items.json      (copy from server)
├── occupants.json  (copy from server)
└── placeables.json (copy from server)
```

### Sprites
```
BugFarmerClient/Assets/Resources/
├── Items/    → Inventory icons (*_icon.png)
├── Objects/  → World sprites
└── Bugs/     → Bug sprites ({bug_id}.png)
```

---

## Sprite Naming Convention

### Inventory Icons (Items/ folder)
**All inventory icons use `{id}_icon` suffix:**

| Item ID | Inventory Sprite |
|---------|------------------|
| `wood` | `Items/wood_icon.png` |
| `dirt_block` | `Items/dirt_block_icon.png` |
| `chest_wood` | `Items/chest_wood_icon.png` |
| `pickaxe_iron` | `Items/pickaxe_iron_icon.png` |

### World Sprites (Objects/ folder)
**Use the item ID directly:**

| Item ID | World Sprite |
|---------|--------------|
| `dirt_block` | `Objects/dirt_block.png` |
| `tree_oak` | `Objects/tree_oak.png` |
| `chest_wood` | `Objects/chest_wood.png` |

### Bug Sprites (Bugs/ folder)
**Bug sprites use the bug ID directly:**

| Bug ID | Bug Sprite |
|--------|------------|
| `butterfly_common` | `Bugs/butterfly_common.png` |
| `honeybee` | `Bugs/honeybee.png` |

### Summary by Entity Type

| Entity Type | Inventory Sprite | World Sprite |
|-------------|------------------|--------------|
| item (inventory-only) | `Items/{id}_icon.png` | N/A |
| occupant (world-only) | N/A | `Objects/{id}.png` |
| placeable (both) | `Items/{id}_icon.png` | `Objects/{id}.png` |
| bug (spawned) | N/A | `Bugs/{id}.png` |

**Simple rule:** Icon is always `{id}_icon.png`, world/bug sprite is always `{id}.png`.

---

## Footprint and Sprite Sizes

Each grid cell = 16×16 pixels.

| Footprint | Pixels | Examples |
|-----------|--------|----------|
| `[1, 1]` | 16×16 | blocks, fences, chairs |
| `[1, 1]` tall | 32×48 | trees (footprint is trunk base only) |
| `[1, 2]` | 16×32 | doors, bookshelves |
| `[2, 1]` | 32×16 | workbench, chest, anvil |
| `[2, 2]` | 32×32 | beds, tables |

Sprites can be taller than footprint × 16 for objects that extend upward visually.
Trees have a [1, 1] footprint (narrow trunk) but a 32×48 sprite (trunk + canopy).

---

## JSON Examples

### Item (inventory-only)
```json
"wood": {
  "name": "Wood",
  "category": "resource",
  "stackable": true,
  "max_stack": 99,
  "sell_price": 2
}
```

### Occupant (world-only)
```json
"tree_oak": {
  "name": "Oak Tree",
  "category": "natural",
  "world": {
    "footprint": [1, 1],
    "pivot": "bc",
    "blocks_players": true,
    "breakable": {
      "hp": 5,
      "required_tool_type": "axe",
      "required_tool_tier": 1,
      "drops": [{"item_id": "wood", "count": 4, "chance": 1.0}]
    }
  }
}
```

### Placeable Block
```json
"dirt_block": {
  "name": "Dirt Block",
  "category": "block",
  "stackable": true,
  "max_stack": 99,
  "sell_price": 1,
  "world": {
    "footprint": [1, 1],
    "pivot": "bc",
    "blocks_players": true,
    "breakable": {
      "hp": 4,
      "required_tool_type": "shovel",
      "drops": [{"item_id": "dirt_block", "count": 1, "chance": 1.0}]
    }
  }
}
```

### Placeable Furniture
```json
"chest_wood": {
  "name": "Wooden Chest",
  "category": "storage",
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

## World Properties

| Property | Type | Description |
|----------|------|-------------|
| `footprint` | `[w, h]` | Grid cells: width × height |
| `pivot` | string | `"bc"` (bottom-center) or `"c"` (center) |
| `blocks_players` | bool | Player collision |
| `blocks_bugs` | bool | Bug collision |
| `rotatable` | bool | Can rotate when placing |
| `interactable` | bool | E key interaction |
| `interaction_type` | string | `"storage"`, `"crafting"`, `"door"` |

### Breakable Properties

| Property | Type | Description |
|----------|------|-------------|
| `hp` | int | Hit points |
| `required_tool_type` | string | `"pickaxe"`, `"axe"`, `"shovel"` |
| `required_tool_tier` | int | Minimum tier (1-5) |
| `drops` | array | What drops when broken |

---

## Sprite Generation (Python Pixel Grids)

### Core Principle

Sprites are created using Python scripts that define pixel grids as 2D arrays of RGBA colors. This approach gives precise control over every pixel and ensures consistent style across all sprites.

### Generation Scripts (in `tools/`)

| Script | What it generates | Output location |
|--------|-------------------|-----------------|
| `generate_bug_sprites.py` | All bugs/insects | `Assets/Resources/Bugs/` |
| `generate_object_sprites.py` | Trees, rocks, plants | `Assets/Resources/Objects/` |
| `generate_block_sprites.py` | Terrain blocks | `Assets/Resources/Objects/` |
| `generate_furniture_sprites.py` | Furniture, chests | `Assets/Resources/Objects/` |
| `generate_item_sprites.py` | Resource icons | `Assets/Resources/Items/` |
| `generate_tool_sprites.py` | Tool icons | `Assets/Resources/Items/` |
| `generate_player_sprites.py` | Player characters | `Assets/Resources/Player/` |
| `generate_terrain_sprites.py` | Terrain tiles | `Assets/Resources/Terrain/` |

### Pattern for Adding New Sprites

1. **Define color constants** (RGBA tuples):
```python
T = (0, 0, 0, 0)  # Transparent
WING_O = (240, 140, 40, 255)   # Orange
BODY_B = (40, 40, 45, 255)     # Body black
```

2. **Create a build function** returning a pixel grid:
```python
def build_butterfly_monarch():
    """Monarch butterfly: 16×16 (orange with black edges)"""
    grid = [[T] * 16 for _ in range(16)]

    # Left wing (upper)
    for y in range(2, 8):
        for x in range(1, 7):
            dist = abs(x - 4) + abs(y - 5)
            if dist < 5:
                grid[y][x] = WING_O if dist < 3 else BLACK

    # Body (center)
    for y in range(3, 14):
        grid[y][7] = BODY_B
        grid[y][8] = BODY_B

    return grid
```

3. **Add to the sprites list** in main():
```python
sprites = [
    ("butterfly_monarch.png", build_butterfly_monarch()),
    # ... other sprites
]
```

4. **Run the script**:
```bash
python tools/generate_bug_sprites.py
```

### Helper Function

All scripts use this to convert grids to images:
```python
def create_sprite_from_grid(grid):
    """Create an image from a pixel grid."""
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img
```

### Design Principles

- **45-degree top-down perspective** (seeing top/back of bugs)
- **Body shape is key identifier** - silhouette should be recognizable
- **Wings semi-transparent** where applicable (alpha < 255)
- **Eyes as accent color** for visual interest
- **Sizes**: 8×8 (ants, flies), 10-12×12 (bees, beetles), 14-16×16 (butterflies, spiders), 24-32×32 (bosses)

### Color Strategy

- **Base color**: Main body/shell color
- **Dark variant**: Shadows, edges (lower/right sides)
- **Light variant**: Highlights (upper/left sides)
- **Accent**: Eyes, markings, special features

### Reference Documents
- `MASTER_STYLE_GUIDE.md` - Visual rules (perspective, lighting, anchoring, sizes)

---

## Adding a New Object

1. **Add JSON** to `nakama/data/entities/{file}.json`

2. **Create sprites:**
   - Icon: `Items/{name}_icon.png`
   - World: `Objects/{id}.png`

3. **Sync to client:**
   ```bash
   cp nakama/data/entities/*.json BugFarmerClient/Assets/Resources/Data/entities/
   ```

4. **Rebuild server:**
   ```bash
   cd nakama && docker compose up --build -d
   ```

5. **Test** - give yourself the item in `state.go` `AddPlayer()`
