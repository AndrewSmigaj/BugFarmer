# Sprite Generation Guide

## Pixel Art Principles for BugFarmer

### Perspective
- **45-degree top-down** (bird's eye with slight angle)
- Player sees tops/backs of objects, not pure side view
- Light source: **top-left** (consistent across all sprites)
- Shadows fall bottom-right

### Color Rules
1. **Limited palette per sprite** (3-5 colors max per material)
   - Base color
   - Light variant (highlights, top-left edges)
   - Dark variant (shadows, bottom-right edges)
   - Optional: mid-tone, accent

2. **No pure black outlines** - use dark variant of the object's color
3. **No pure white** - use off-white/cream for highlights
4. **Saturation**: slightly muted, natural tones (not neon)

### Size Reference
- Grid cell: 16×16 pixels
- Player: 48×32 pixels (3×2 cells)
- Smallest bugs: 8×8 pixels
- Most items: 16×16 to 32×32

### Readability
- Clear silhouette at 100% zoom
- Must be recognizable at game scale
- Avoid 1-pixel details that disappear when scaled
- 2-pixel minimum for important features

### Top-Down Specific
- Show **tops** of things (table top, chest lid, tree canopy)
- Vertical objects show **foreshortened height** (bookshelf shorter than side-view)
- Ground-level items are flatter (rugs, floors)
- Tall items cast implied shadow (optional darker pixels on bottom-right)

---

## Iterative Workflow (Per Sprite)

### Pass 1: Initial Draft
1. State the item name, size, and purpose
2. Define color palette (name each color, RGB values)
3. Describe the visual design in words:
   - What are we looking at from above?
   - Key features that make it recognizable
   - How lighting hits it
4. Create initial pixel grid

### Pass 2: Review & Improve
1. Check silhouette - is it readable?
2. Check colors - consistent lighting direction?
3. Check proportions - fits the footprint?
4. Check style - matches other sprites?
5. Identify specific improvements
6. Create revised pixel grid

### Pass 3 (if needed): Final Polish
1. Fine-tune problem areas
2. Ensure tileable edges (for terrain/floors)
3. Verify transparency is correct
4. Create final grid

### Pass 4: Generate Script
1. Add to appropriate generator file or create new one
2. Include color definitions
3. Test generation
4. Verify output

---

## Prompting Myself: Questions to Ask

Before drawing each sprite:
1. "What does this look like from 45 degrees above?"
2. "What's the ONE feature that makes this recognizable?"
3. "Where does light hit it? Where are shadows?"
4. "What colors does this material have in real life?"
5. "At 16×16 pixels, what details can I actually show?"

During review:
1. "If I squint, can I tell what this is?"
2. "Does the lighting match other sprites?"
3. "Is anything too cluttered or busy?"
4. "Would a player understand this in their inventory?"

---

## Category-Specific Notes

### Terrain (16×16 tileable)
- Must tile seamlessly in all directions
- Avoid strong patterns that create visible grids
- Subtle variation, not busy

### Trees/Plants (various sizes)
- Canopy dominates from above
- Trunk visible at bottom (player walks behind)
- Multiple green shades for depth

### Furniture (16×16 to 32×32)
- Show the TOP surface
- Wood grain horizontal for tables
- Clear functional shape

### Tools (16×16 inventory icons)
- Angled 45° for dynamic look
- Handle and head clearly distinct
- Material colors (wood brown, metal gray)

### Bugs (8×8 to 16×16)
- Body shape is key identifier
- Wings semi-transparent where applicable
- Eyes as accent color

### Fencing/Walls (16×16 or 16×20)
- Top edge visible (looking down at it)
- Posts/rails clear
- Must tile horizontally

---

## Color Palette Reference

### Wood
- Dark: (70, 50, 35)
- Base: (120, 90, 60)
- Light: (160, 130, 95)

### Stone
- Dark: (85, 85, 90)
- Base: (120, 120, 125)
- Light: (155, 155, 160)

### Metal (Iron/Steel)
- Dark: (60, 65, 70)
- Base: (100, 105, 110)
- Light: (150, 155, 160)

### Copper
- Dark: (140, 80, 50)
- Base: (180, 110, 70)
- Light: (210, 150, 100)

### Gold
- Dark: (180, 140, 40)
- Base: (230, 190, 60)
- Light: (255, 220, 100)

### Grass
- Dark: (55, 115, 55)
- Base: (72, 140, 72)
- Light: (95, 165, 85)

### Dirt
- Dark: (110, 75, 40)
- Base: (140, 95, 50)
- Light: (165, 120, 70)

(More palettes to be added as we go)

---

## File Organization

```
tools/
  generate_terrain_sprites.py    # Ground tiles
  generate_object_sprites.py     # World objects (trees, rocks)
  generate_furniture_sprites.py  # Tables, chairs, beds
  generate_tool_sprites.py       # Axes, pickaxes, etc.
  generate_item_sprites.py       # Inventory icons
  generate_bug_sprites.py        # All insect species
  generate_building_sprites.py   # Walls, fences, doors
  generate_station_sprites.py    # Crafting stations
```

Output to:
```
BugFarmerClient/Assets/Sprites/
  Terrain/
  Objects/
  Furniture/
  Tools/
  Items/
  Bugs/
  Buildings/
  Stations/
```
