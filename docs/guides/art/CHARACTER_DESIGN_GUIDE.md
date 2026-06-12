# Character Design Guide for Bug Farmer

## AS BUILT (2026-06-12): 16x32 region-template paper-doll — READ THIS FIRST
The layered player SHIPPED at the game's existing **16x32** canvas (Andrew's
call: keep the current resolution), not the 32x48 proposed below. How it works
(`tools/player_sprites/`):
- Sprites are **text grids** (char-per-pixel, `pixkit.py` legend); every body
  pixel carries a REGION tag (skin/hair/shirt/pants/boots). ONE hand-authored
  idle master per direction (`body_frames.py`); right = mirrored left.
- **Layers derive from the master by region filtering** (each layer carries the
  outline pixels adjacent to its region) — registration is perfect by
  construction. The body layer substitutes clothing regions to skin + a linen
  shorts band (row-aware), so the unclothed base has no holes.
- **Walk cycle** [contact-L, idle, contact-R, idle] derives mechanically:
  half-row leg shifts (rows 25-31) + 1px head bob (rows 0-13). NO arm swing
  (read as an artifact). Files: `{set}_{dir}.png` (idle, the pre-existing
  names) + `_w1`/`_w3` contacts.
- **Wearables** (`wearables.py`): overlay grids on the same canvas; head items
  are pre-composed with the bob per frame; `HIDES_HAIR` lists full helms.
- **16x32 anchor rows**: hair 1-5 · face 6-12 (eyes 8-9) · neck 13 ·
  shoulders 14 · torso 15-22 · waistband 23 · legs 24-28 · boots 29-31.
- Unity: `CharacterComposer.cs` alpha-blends `Resources/Player/layers/**` into
  cached per-(dir,frame) sprites at runtime (single SpriteRenderer; layer metas
  need `isReadable: 1` — `fix_sprite_ppu.py` sets it). Appearance/equip server
  sync is a backlog follow-up; F6 cycles debug outfits locally.

The sections below are the ORIGINAL 32x48 proposal — kept for the proportions/
perspective/palette guidance, which still applies. Dimensions there are
superseded by the as-built 16x32 above.

## Architecture Decision: LAYERED / Modular Player (2026-06-02)

The player is **composited at runtime from stacked layers**, not a single baked sprite.
This is the only approach that scales to armor + helmets + clothing without a combinatorial
sprite explosion (skin x shirt x pants x chest x helmet). Decided with the user; 4 skin tones
to start.

### Layer stack (back -> front; one SpriteRenderer per layer, ascending sortingOrder)
1. `base_body`  - bare humanoid: skin tone, face, hands, feet. One set per **skin tone** (4).
2. `pants`      - clothing bottom (legs/waist).
3. `shirt`      - clothing top (torso/arms).
4. `chest`      - chest armor, drawn OVER shirt (equipment slot).
5. `hair`       - hair, sits on top of the head; one set per hair style/color.
6. `helmet`     - head equipment, drawn OVER hair (equipment slot).

(`EquippedTool` already renders separately and is out of this stack.)

### Shared anchor template (the thing that makes layers line up)
Every layer is **32x48**, same pivot, same canonical pose per direction. All layers register
to ONE master silhouette so they overlay pixel-perfect. The **`*_down` body is the master**;
up/left/right derive from it. Documented anchor rows (32x48 grid):
- head center column: x=16; head box rows ~0-19
- shoulder/neck line: row ~22
- hand height: row ~32 (arms at side)
- waist line: row ~36
- feet baseline: row ~47
A helmet must occupy the head box; a chest layer the shoulder->waist band; pants waist->feet.

### Registration strategy (CRITICAL - how AI parts align) — PAPER-DOLL (spike-verified 2026-06-02)
gpt-image-1 `generations` produces independent images that will NOT register on their own.

**REJECTED — images/edits inpainting.** Spike result: gpt-image-1's `edits` endpoint does NOT
honor the mask as a hard constraint. Even with a correct head-only mask it regenerated the WHOLE
character (tank top -> armor, arms reshaped, torso drifted). The base body is not preserved, so no
clean layer can be extracted. Do not use edits for layer production.
(Repro: `python3 gen_sprites.py --player-spike` -> `raw_sprites/spike_head_tan_down.png`.)

**CHOSEN — paper-doll with anchor offsets we control.** Spike-verified working:
- **Base bodies**: `generations` against the template prompt (one per skin tone x direction).
- **Equipment / clothing layers**: generate each piece **STANDALONE** (`item_layer_prompt`):
  "draw ONLY the item, no head/body, sized to fit a chibi character, 3/4 top-down, transparent."
  Trim with `getbbox()`.
- **Registration is done by US, not the model:** each layer gets **anchor-offset metadata**
  (where it pins relative to the body's head/torso/waist anchor + a scale factor). Unity stacks
  it over an UNCHANGED body via a SpriteRenderer. Body stays pixel-identical; only the offset/scale
  are tuned per slot.
  (Repro: `python3 gen_sprites.py --paperdoll-spike` -> `raw_sprites/spike_paperdoll_tan_down.png`
  shows the body intact + helmet composited at the head anchor.)
- Anchor knobs live in `paperdoll_spike()` (`scale`, `px`, `py`) — promote these to per-item
  metadata when building the real layer set. Head item ~= head bbox width; sits ~12% above head top.

### Data model (server + network) - prerequisite, NOT yet built
- `PlayerState` (state.go): add `Appearance { SkinTone, Hair, HairColor }` + equipment slots
  `{ Head, Chest, Legs }` holding item_id or empty. `EquippedTool` already exists.
- `items.json`: wearables get `equip_slot` (head/chest/legs) + a layer sprite key.
- `EntityData` / join payload: must carry appearance + visible equipment so REMOTE clients
  render the same stack (today it only sends id/type/x/y/facing).

### Resources layout
```
Resources/Player/body/{tone}_{dir}.png        # e.g. body/tan_down.png   (4 tones x 4 dir)
Resources/Player/hair/{style}_{dir}.png
Resources/Player/wear/{slot}/{item}_{dir}.png # wear/head/iron_helm_down.png, wear/chest/..., wear/legs/...
```
File naming stays `{thing}_{direction}.png` per existing convention.

### Animation / walk frames (spike-verified 2026-06-02)
Spikes (`--walk-sheet` then `--segment-sheet`) established:
- gpt-image-1 **CAN** draw several consistent walk poses of the same chibi in one sheet
  (foot-forward / passing poses read as a walk).
- It will **NOT** honor a requested frame COUNT or even spacing (asked 4, got 3, uneven). So
  fixed-column slicing is wrong.
- **Working extraction:** generate sheet -> `segment_sheet()` splits figures by TRANSPARENT
  column gaps (variable count) -> trim + re-center each onto the fixed 32x48 anchor -> frames.
  Verified: 3 clean figures extracted from `walksheet_medium_down.png`.
- Frame count is nondeterministic -> normalize: pad/loop to a target (a 2-frame alternating
  step-bob is enough at this zoom; 4 is nicer). Re-roll a sheet if it yields too few.

**Animation x layering cost (the expensive combination, needs a decision):**
Full per-frame layered art = every equipment layer redrawn & registered for every walk frame x
direction = explosion. Pragmatic compromise to recommend:
- Animate the **base body** only (legs/arms move) -> a few frames per direction per skin tone
  (skin tones still come from recoloring ONE master frame set).
- Equipment/clothing = a SINGLE overlay per direction that rides the body's torso/head anchor
  each frame (slight bob), NOT redrawn per frame. Cheap, reads fine at game zoom.
- Only redraw equipment per-frame later if a specific item visibly needs it.

### Build order (de-risk before mass-generating)
1. **Registration spike** (cheap, ~2-3 API calls): one base body -> `images/edits` add a
   helmet -> confirm the helmet pixels land on the head box and overlay cleanly. PROVE the
   edits approach before scaling. (If it fails, fall back to hand-registered atlas.)
2. Generate 4 base bodies (4 dir each) = the "variants to choose from".
3. Hair + a couple clothing layers; verify stacking in Unity.
4. Wire the data model (Go + network + multi-SpriteRenderer client) — separate effort,
   C# cannot be compiled here (needs Unity).

---

## Design Philosophy

### Style Reference: Terraria-Cute-Retro
- **Chibi proportions**: Large head relative to body (head is ~40% of total height)
- **Chunky, readable**: 2-3 pixel wide limbs, not thin single-pixel lines
- **Cute over realistic**: Simplified features, big expressive elements
- **Retro pixel art**: Limited palette, clear shapes, no anti-aliasing

### Perspective: 45-Degree Top-Down (NOT Side View)
This is critical. We're looking DOWN at the character from above and in front.

**What this means:**
- You see the TOP of the character's head (hair is prominent oval shape)
- Face is visible BELOW the top of head
- Even when facing left/right, use 3/4 view (NOT pure profile)
- Body is foreshortened (shorter than side-view would show)

**Common mistake to avoid:**
Side-view sprites show a profile (nose sticking out, one eye visible from side).
Our sprites should show the face more frontally even when the body is turned.

---

## Character Specifications

### Base Size: 32x48 pixels (2x3 cells)

Player sprites occupy 2 cells wide by 3 cells tall (where each cell is 16x16).
This allows the player to fit through 2-block-wide doorways.

```
Row breakdown (48 pixels):
  0-5   : Top of head (hair crown, viewed from above)
  6-15  : Hair sides/back + Face (framing face)
  16-23 : Face lower + Upper torso (eyes, shirt top)
  24-35 : Torso (shirt, arms)
  36-47 : Lower body + Legs (waist, pants, feet)
```

### Terraria-Style Proportions

The character uses chunky, blocky shapes similar to Terraria:
- Huge rectangular head (~40% of height)
- White eyes with 2x2 dark pupils
- Blocky rectangular limbs (not organic/rounded)

```
Width distribution (32 pixels):
  - Character body: 18-22 pixels wide (centered)
  - Head: 18-22 pixels wide (huge, rectangular)
  - Shoulders: 20-24 pixels wide
  - Legs: 12-16 pixels wide (gap between)

Height distribution (48 pixels):
  - Head+Hair: ~20 pixels (42%)
  - Body: ~18 pixels (37%)
  - Legs: ~10 pixels (21%)
```

### Relationship to Grid
- Grid cell: 16x16 pixels
- Blocks: 16x20 pixels (3D cubes)
- Player: 32x48 pixels (2 cells wide, 3 cells tall)
- Player can walk through 2-block-wide openings

---

## Direction Sprites

### Down (Facing Camera)
The "hero shot" - most important sprite.

**What we see:**
- Oval top-of-head (hair) - prominent at top
- Full face below - both eyes visible, centered
- Shoulders/chest - symmetrical, arms at sides
- Legs - feet pointing toward camera

```
Visual guide (simplified):
     ████████        <- hair top (oval)
    ██████████       <- hair sides
     ████████        <- face (skin)
    ████  ████       <- eyes
     ██████          <- mouth area
    ██████████       <- shoulders/shirt
    ██████████       <- torso
     ████████        <- waist
      ██  ██         <- legs
      ██  ██         <- feet
```

### Up (Facing Away)
**What we see:**
- Oval top-of-head (hair) - dominant
- Back of head/hair - no face visible
- Back/shoulders
- Legs from behind

### Left (Facing Left, 3/4 View)
**NOT a side profile!** This is a 3/4 view.

**What we see:**
- Oval top-of-head, slightly off-center
- Face turned left BUT one eye still visible (or at least implied)
- Body turned, left shoulder forward
- Legs, left leg forward

### Right (Facing Right, 3/4 View)
Mirror of left.

---

## Color Palette System

### Principle: 3 Colors Per Material
Every material uses exactly 3 shades:
1. **Light** - Hit by light (top-left areas)
2. **Base** - Main color (most surface area)
3. **Dark** - Shadow (bottom-right areas)

### Skin Tones
```python
# Default (warm beige)
SKIN = {
    'light': (240, 200, 170),  # Highlights
    'base':  (220, 175, 140),  # Main skin
    'dark':  (180, 130, 100),  # Shadows
}
```

### Hair Colors
```python
HAIR_BROWN = {
    'light': (120, 85, 65),
    'base':  (90, 60, 45),
    'dark':  (60, 40, 30),
}

HAIR_AUBURN = {
    'light': (170, 95, 70),
    'base':  (140, 65, 45),
    'dark':  (100, 45, 30),
}

HAIR_BLACK = {
    'light': (70, 70, 80),
    'base':  (45, 45, 55),
    'dark':  (25, 25, 35),
}

HAIR_BLONDE = {
    'light': (230, 200, 140),
    'base':  (200, 170, 100),
    'dark':  (160, 130, 70),
}
```

### Clothing Colors
```python
SHIRT_TEAL = {
    'light': (90, 160, 150),
    'base':  (60, 130, 120),
    'dark':  (40, 90, 90),
}

SHIRT_GREEN = {
    'light': (95, 150, 100),
    'base':  (65, 120, 70),
    'dark':  (45, 85, 50),
}

SHIRT_BLUE = {
    'light': (100, 135, 190),
    'base':  (70, 100, 160),
    'dark':  (50, 70, 120),
}

SHIRT_RED = {
    'light': (190, 105, 100),
    'base':  (160, 70, 70),
    'dark':  (120, 50, 50),
}

PANTS_BROWN = {
    'light': (130, 100, 75),
    'base':  (100, 75, 55),
    'dark':  (70, 50, 40),
}

PANTS_DARK = {
    'light': (100, 80, 65),
    'base':  (75, 55, 45),
    'dark':  (50, 35, 30),
}

PANTS_GRAY = {
    'light': (130, 130, 135),
    'base':  (100, 100, 105),
    'dark':  (70, 70, 75),
}

PANTS_TAN = {
    'light': (200, 180, 145),
    'base':  (175, 150, 110),
    'dark':  (140, 115, 80),
}
```

### Eye Color
```python
# Simple dark color for eyes
EYE = (30, 30, 35)  # Near-black, not pure black
```

---

## Lighting Rules

### Light Source: Top-Left
Consistent with all other sprites in the game.

```
Light hits:
  - Top of head (lighter hair)
  - Left side of face
  - Left shoulder
  - Top of any surface

Shadow falls:
  - Bottom-right of head
  - Right side of body
  - Under arms
  - Bottom edges
```

### Application Example
```
For a facing-down sprite:

  Hair row 0-1: Use light shade (crown catching light)
  Hair row 2-4: Left side = light, right side = dark
  Face: Left cheek = light, right cheek = base
  Shirt: Left arm/side = light, right = dark
  Pants: Similar left-right gradient
```

---

## Character Variants

### Farmer (Default)
- Hair: Brown
- Shirt: Teal
- Pants: Brown
- Personality: Friendly, hardworking

### Ranger
- Hair: Auburn
- Shirt: Green
- Pants: Dark Brown
- Personality: Adventurous, nature-focused

### Scholar
- Hair: Black
- Shirt: Blue
- Pants: Gray
- Personality: Studious, curious

### Merchant
- Hair: Blonde
- Shirt: Red
- Pants: Tan
- Personality: Cheerful, entrepreneurial

---

## Iterative Design Process

### Pass 1: Block Out Shape
1. Define the silhouette using base colors only
2. Ensure proportions are correct
3. Check that it's readable as a person

### Pass 2: Add Shading
1. Apply light/dark variants based on lighting
2. Add eyes and facial features
3. Refine edges

### Pass 3: Polish
1. Check silhouette (squint test)
2. Verify lighting consistency
3. Test alongside other sprites
4. Adjust colors if needed

### Review Questions
After each pass, ask:
1. "Does this look cute, not goofy?"
2. "Can I tell which direction they're facing?"
3. "Is the top-of-head visible (45-degree view)?"
4. "Does it match Terraria's chunky charm?"

---

## File Naming Convention

```
{character}_{direction}.png

Examples:
  farmer_down.png
  farmer_up.png
  farmer_left.png
  farmer_right.png
  ranger_down.png
  ...
```

Output directory: `BugFarmerClient/Assets/Sprites/Player/`

---

## Common Mistakes to Avoid

1. **Too thin**: Limbs should be 4-6 pixels wide at 32x48 scale, not single-pixel lines
2. **Pure side view**: Left/right should be 3/4 view, not profile
3. **No top-of-head**: From 45-degrees above, hair crown must be visible
4. **Pure black outlines**: Use dark variant of material color instead
5. **Too realistic**: Use blocky shapes, not organic curves
6. **Wrong proportions**: Head should be ~40% of height for cute look
7. **Inconsistent lighting**: Light always from top-left
8. **Wrong size**: Player is 32x48 (2x3 cells), NOT 16x20
