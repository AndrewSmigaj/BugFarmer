# Creating New Objects in Bug Farmer

## Entity Types

| Type | JSON File | Description | Example |
|------|-----------|-------------|---------|
| **item** | `items.json` | Inventory-only | `wood`, `pickaxe_wood` |
| **occupant** | `occupants.json` | World-only (can't be placed by player) | `tree_oak`, `ore_iron_block` |
| **placeable** | `placeables.json` | Inventory + world (player places) | `dirt_block`, `chest_wood` |

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
└── Objects/  → World sprites
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

### Summary by Entity Type

| Entity Type | Inventory Sprite | World Sprite |
|-------------|------------------|--------------|
| item (inventory-only) | `Items/{id}_icon.png` | N/A |
| occupant (world-only) | N/A | `Objects/{id}.png` |
| placeable (both) | `Items/{id}_icon.png` | `Objects/{id}.png` |

**Simple rule:** Icon is always `{id}_icon.png`, world sprite is always `{id}.png`.

---

## Footprint and Sprite Sizes

Each grid cell = 16×16 pixels.

| Footprint | Pixels | Examples |
|-----------|--------|----------|
| `[1, 1]` | 16×16 | blocks, fences, chairs |
| `[1, 2]` | 16×32 | doors, bookshelves |
| `[2, 1]` | 32×16 | workbench, chest, anvil |
| `[2, 2]` | 32×32 | beds, tables |
| `[2, 2]` tall | 32×48 | trees |

Sprites can be taller than footprint × 16 for objects that extend upward visually.

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
    "footprint": [2, 2],
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

## Sprite Generation

### Generator Scripts (in `tools/`)

| Script | What it generates |
|--------|-------------------|
| `generate_object_sprites.py` | Trees, rocks, plants |
| `generate_block_sprites.py` | Terrain blocks |
| `generate_furniture_sprites.py` | Furniture, chests |
| `generate_item_sprites.py` | Resource icons |
| `generate_tool_sprites.py` | Tool icons |

### How Generators Work

```python
from PIL import Image

T = (0, 0, 0, 0)           # Transparent
Wd = (70, 50, 35, 255)     # Wood dark
W  = (120, 90, 60, 255)    # Wood base
Wl = (160, 130, 95, 255)   # Wood light

def build_sprite():
    grid = [[T] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if x < 5:
                grid[y][x] = Wl   # Left = lit
            elif x < 11:
                grid[y][x] = W    # Center
            else:
                grid[y][x] = Wd   # Right = shadow
    return grid

def save_grid(grid, path):
    h, w = len(grid), len(grid[0])
    img = Image.new('RGBA', (w, h), T)
    px = img.load()
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            px[x, y] = c
    img.save(path)
```

### Design Rules
- Light from top-left, shadows bottom-right
- 3 shades per material (dark, base, light)
- 45° top-down perspective

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
