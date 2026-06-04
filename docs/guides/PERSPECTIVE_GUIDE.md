# 3/4 Top-Down Perspective Guidelines

Based on research from SLYNYRD, OpenGameArt, and Lospec tutorials.

## The Core Principle

**3/4 perspective** (also called "RPG perspective") views objects from approximately **45 degrees above**. You see roughly 3/4 of both the **top surface** AND the **front face**.

## Key Rule: Two Types of Planes

| Plane Type | How to Draw | Example |
|------------|-------------|---------|
| **Horizontal** (tops, floors) | Viewed from directly above - circles stay circular, squares stay square | Table top, bed mattress surface, barrel lid |
| **Vertical** (fronts, walls) | Viewed frontally at 1:1 ratio - no foreshortening | Chair back, headboard, chest front |

> "The vertical planes are represented as seen from the front, the same way the horizontal ones are" - OpenGameArt

## Depth Comes From LIGHTING, Not Geometry

> "The satisfying sense of depth comes from contrast in light where sharp angles meet" - SLYNYRD

- **Top surfaces**: Well-lit (top-left light source)
- **Front faces**: Darker/shadowed
- **Sharp edge contrast**: Where top meets front = strong color change

## Uniformity Over Realism

> "When it comes to pixel art, uniformity takes priority over realism" - SLYNYRD

Keep angles clean and consistent. Don't try to simulate "realistic" perspective distortion.

---

## Applied to Sprite Categories

### Beds
```
WRONG (pure top-down):        CORRECT (3/4 view):
┌────────────────┐            ╔════════════════╗ ← Headboard FRONT (vertical, 1:1)
│   PILLOW       │            ║   HEADBOARD    ║   (we see its face, not top)
│                │            ╠════════════════╣
│   BLANKET      │            │    PILLOW      │ ← Top surface (horizontal)
│                │            │    BLANKET     │   (viewed from above)
│                │            ├────────────────┤ ← Edge line
└────────────────┘            │  FRONT FACE    │ ← Front of mattress (darker)
                              └────────────────┘
```

**Bed sprite breakdown:**
- Rows 0-30%: Headboard **standing vertical** (we see its front face)
- Rows 30-70%: Mattress/blanket **top surface** (viewed from above, lit)
- Rows 70-85%: Mattress **front face** (showing thickness, darker)
- Rows 85-100%: Optional footboard or legs

### Tables
```
┌────────────────┐ ← Top surface (viewed from above)
├────────────────┤ ← Front edge (2-4px, shows thickness)
│  FRONT FACE    │ ← Apron/underside (darker)
│   ││      ││   │ ← Legs visible below
└───┘└──────┘└───┘
```

### Chests
```
╭────────────────╮ ← Lid top (curved, lit)
├────────────────┤
│   FRONT FACE   │ ← Box front (darker, has lock)
└────────────────┘
```

### Chairs
```
╔════════╗       ← Chair back FRONT (vertical surface)
║  BACK  ║
╠════════╣
│  SEAT  │       ← Seat top (viewed from above)
├────────┤
│  LEGS  │       ← Front apron + legs
└─┘    └─┘
```

### Blocks (16x20 cubes)
```
┌────────────┐    ← Top face (rows 0-11, ~60%)
│    TOP     │      Viewed from above, well-lit
│            │
├────────────┤    ← Edge where top meets front
│   FRONT    │    ← Front face (rows 12-19, ~40%)
│            │      Darker, shows depth
└────────────┘
```

### Tall Furniture (Bookshelves, Wardrobes)
- Mostly **front-facing** (vertical surface dominates)
- Small **top edge** visible (2-4px at top)
- Shelves/details drawn frontally

### Trees
```
    ████████        ← Canopy TOP (viewed from above)
   ██████████         Large oval/circle shape
    ████████
       ██           ← Trunk visible at bottom
       ██             (we look down past canopy edge)
```

### Fences/Walls (tileable)
- **Top edge** visible (looking down at it)
- **Front face** of posts/rails
- Must tile horizontally

---

## Quick Checklist for Each Sprite

1. ☐ Does it show the **front face** of vertical elements?
2. ☐ Is the **top surface** drawn as viewed from above (not tilted)?
3. ☐ Is there **strong contrast** where top meets front?
4. ☐ Is lighting consistent (top-left light, bottom-right shadow)?
5. ☐ Does it match the style of the **stone_block** (which is correct)?

---

## Color/Lighting Rules

### Light Direction: Top-Left
```
    LIGHT
      ↘
   ┌─────────┐
   │ BRIGHT  │  ← Top-left areas = light color
   │      ···│  ← Bottom-right areas = dark color
   └─────────┘
```

### Three-Shade System (per material)
- **Light**: Highlights, top-left edges, top surfaces
- **Base**: Main color, most surface area
- **Dark**: Shadows, bottom-right edges, front faces

### Edge Contrast
Where planes meet, use contrasting shades:
- Top surface (light) → hard edge → Front face (dark)

---

## Sources

- [SLYNYRD - Top Down Interiors](https://www.slynyrd.com/blog/2021/11/30/pixelblog-35-top-down-interiors)
- [SLYNYRD - Graphical Projections](https://www.slynyrd.com/blog/2018/3/14/pixelblog-3-graphical-projections-1)
- [OpenGameArt - Perspectives](https://opengameart.org/content/chapter-3-perspectives)
- [Lospec - Perspective Tutorials](https://lospec.com/pixel-art-tutorials/tags/perspective)
