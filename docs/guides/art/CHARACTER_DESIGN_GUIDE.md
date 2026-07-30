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

## AS BUILT (2026-07-28): whole-outfit sprite sheets, armless character + floating hands
**This supersedes the masked/paperdoll pipeline described in older revisions of this section.**

The character is **armless**; the hands are separate floating fists moved by code. A walk, a run and a weapon
swing therefore need no drawn poses beyond the walk cycle itself, and one animator drives every tool.

Outfits are generated as **whole 12-frame sheets** (3 rows front/back/side x 4 walk phases), one image per
outfit, rather than composed from chest/legs/boots layers. Generating the whole sheet in one render removes
drift by construction; the masked per-slot route needed hand-fixing on every piece and was abandoned
(owner decision, 2026-07-28).

Model **gpt-image-2**, **NO MASK**. Masked runs come back as black boxes. The prompt must state that the
character has no arms, or the model draws them back on.

**Generate on MAGENTA, never on black (2026-07-29).** Black is the one colour the armour also contains, so
"is this pixel background?" stops being answerable. The cutter used to decide by brightness, and deleted the
artwork's own dark pixels: hornet-stinger lost 17% of the figure — every black band — and ant-carapace 17%,
swamp-gear 11%, ranger 10%, with most of the roster losing 6–9%. On a magenta sheet the separation is exact:
measured on ranger, **zero** art pixels test as magenta, against 8.9% of that same sprite being
indistinguishable from a black background. Key by flooding in **from the border**, never per-pixel — a dark
pixel reachable from outside is background, one enclosed by the figure is its own shading.

**Pick the DESIGN before paying for a walk cycle.** `outfits.py explore <set>` draws three designs of one set,
standing still and large, on magenta. The three must have **different parents** — left to themselves they
become three tunings of one idea, the same failure the swing design guarded against. Only the chosen design
gets a 12-frame sheet.

**A design is not judged until it is judged SMALL.** `preview_explore.py <set>` renders each option large and
again shrunk to real game height on grass; the small row is the one that decides. Ranger's third option was
the best-looking design on the page and the worst in the game — its gold linework became noise the instant it
shrank, while the two plainer designs kept working. So:

- **What distinguishes one design from another must be SILHOUETTE** — hat, hood, crest, plume, cape, shoulder
  and hem shape. Never engraving, filigree, trim or inlay: those are exactly what dies at 40px. Platinum's
  three "fancy" options are a plume, wings and a spiked crown for this reason, and all three stayed readable.
- Four or five flat colour areas per figure, in chunky blocks.

**The model will paint the KEY COLOUR onto the figure** if you let it — magenta "glowing eyes" on a beetle,
a magenta halo on a platinum. They survive only because the key floods from the border (an enclosed magenta
pixel counts as art); a per-pixel colour test would punch holes exactly there. The prompt now forbids
magenta/pink/purple anywhere on the figures, but **check each sheet for it anyway**.

Full procedure — the verbatim sheet and gauntlet prompts, the cutting steps, the pixelsnap pitch warning, the
hand-size constant and the per-tool grip measurement — lives in the **`player-sprites` skill**
(`.claude/skills/player-sprites/SKILL.md`). Art lives in `tools/_generated/player/` (`bases/` = the two locked
sprites, `outfits/<name>/` = one folder per outfit).

**Which sets exist is DATA, not prose.** `tools/player_sprites/outfits.py` holds the roster and the single
shared prompt; a new set is a dict entry naming three things — what the set is, its material and colours, and
its headgear — never a new script. **Every set has headgear**; one without it doesn't match the rest and gets
redone. Which sets are *planned* is `docs/product/economy/catalogs/armor.md`.

**A tier reads by COLOUR, not by silhouette.** At sprite size every plate set is the same shape, so a metal
rung that isn't separated in brightness is a wasted tier. Check it by measuring mean luma over the worn
material of `front_1.png`, not by eye — the completed ladder runs iron 66 → steel 90 → silver 113 →
platinum 157, and eyeballing that same comparison once produced a confident *wrong* call (that steel collided
with silver). Warm metals separate by hue instead: copper is pink-orange, bronze brown-gold, gold yellow.

**Design 2026-07-29 (as built, 22 sets).** The base ladder is complete at nine rungs. Cloth sets (padded,
moth-wool) show the face under a hood or coif rather than a full helm, which is what makes them read as T1
cloth and not as pale armour.

The 16x32 region-template system above is the ORIGINAL hand-authored player and is what the game still loads
today; publishing the new sheets is a separate step.

### The swing: the hand needs a SHOULDER (2026-07-29)
The first five swing "approaches" all rotated one rigid tool sprite about the **player's centre** and stuck
the fist to its grip afterwards. They differed only in the easing of that one angle, which is why they looked
identical and why the fist rode up past the chest — a circle around the navel is not a swing, and no amount
of retiming fixes a wrong pivot.

**Drive the HAND, then hang the tool off it** (`swing_lab.py` approaches 8–9). The hand travels an arc from a
shoulder; the arm shortens across the body and extends through contact, which is what an elbow does. Costs no
new art, because the fist is already a separate code-moved sprite.

Two constraints found by getting them wrong:

- **The armless design caps how far the hand may travel.** A drawn character can reach arm's length because
  the arm connects the hand. Ours cannot — at a realistic reach the sword visibly detached and floated beside
  the body. Keep the hand within roughly a third of a cell of the shoulder.
- **`art_rot` must stay 0 unless the grip is recomputed with it.** `grip_of` measures the handle off the
  *unrotated* sprite, so rotating the net 180° left the hand clamped on the hoop with the handle out the far
  side. Fix a "wrong way round" tool by reversing its **sweep**, not its sprite.

**Every facing gets its own shoulder.** Sharing one put the hand at face height in the front view. The front
view also needs a floor angle so a tool stops in front rather than burying itself, and the away-facing view
draws tool and hand **behind** the body. All three are rendered side by side because all three have to work.

### ONE MOTION PER TOOL — do not share an arc
The strongest recurring mistake in this work: writing one arc function and giving each tool different
constants. It looks like reuse and it is actually six copies of the same move. A sword is not an axe; a
thrust is not a slash. If two tools differ only by numbers, they will read as the same animation, which is
exactly the complaint that came back every round.

Each `kind` in `swing_lab.py` owns a function, and they differ in **mechanism**:

| kind | tool | what it actually does |
|---|---|---|
| `slash` | sword | short fast flick, ~120°, 0.11s — a combat slash, **not** a dramatic wheel |
| `wheel` | axe | behind → over the top → down in front, ~265° unbroken; a real axe never stops at the top |
| `sweep` | net | starts **behind the shoulder**, travels ~195° forward |
| `till` | hoe | raise, drive down to the feet, drag back toward the player |
| `thrust` | spear | angle nearly fixed — the **reach** is the whole animation, held at full extension |
| `scoop` | shovel | stab down into the ground, then lift and scoop up and out |

**A swing must START BEHIND the character.** The net ran 55° → −20°: already out in front, only tipping down.
A tool that begins in front has no swing in it, whatever the timing does.

**Every motion starts AND ends at the idle pose.** Swings used to *teleport* to their wind-up pose — 235° for
the axe, 205° for the net — then sit there while the curve eased in. That jump, not the timing, is what read
as "hovering in the cocked-back position". Travel the wind-up and land the recovery on idle; that also closes
the old "the swing has no exit" defect. Arrive at the top **at speed** (`ease_in`), never decelerating into
it, or the tool lingers at the extreme.

**Combat durations are 0.11–0.22s.** Anything slower cannot be held down in a fight.

**Digging tools are REACH-driven, not angle-driven.** The hoe and shovel read as swings while their angle did
the work. A hoe is a small lift, a strike, and a drag; a shovel is a downward jab that holds and lifts a
little. Both keep the angle nearly still and let the reach drive — that is the difference between digging and
swinging.

### When a note keeps coming back, stop theorising and enumerate
The net swing was wrong five rounds running. Each round produced a *theory* about what "backwards" meant,
changed something on the strength of it, and was wrong; the last theory was invented outright and attributed
to the owner. `net_options.py` is the correction: render every combination that could possibly be meant —
sweep direction × sprite transform × which end leads — caption them, and have him point at one. Cheaper than
a sixth wrong guess, and it ends the argument. Reach for this the *second* time a note repeats, not the fifth.
(When transforming a sprite, recompute the grip on the **transformed** art or the fist clamps to the wrong end.)

### Judge a set IN MOTION, holding something
`showcase.py` renders several sets across four bands on one timeline — running right, running down, swinging
side-on, swinging front-on — with a different tool per column so every motion appears. A set that reads well
as a portrait can still fall apart the moment it moves or picks up a weapon, so the reel, not the contact
sheet, is what a set has to survive. It imports the swing from `swing_lab` rather than reimplementing it, so
it cannot drift from the designed motion.

### SUPERSEDED — the body/arm split (abandoned 2026-07-28)
An earlier attempt split each base into a body plus a rotatable weapon ARM. It was abandoned the same day: you
cannot carve animation pieces out of a finished drawing, because a drawn arm only contains the pixels visible
in that one pose — rotate it and you expose a surface that was never drawn. In profile it is worse still, as
the arm overlaps the torso and lifting it out deletes the body behind it.

The armless + floating-hand design replaces it and removes the problem rather than solving it: a fist is
round, self-contained, and reads the same from any angle, so there is nothing to tear and no joint to hide.
`tools/player_sprites/split_base_arm.py` remains only as a record of the attempt.

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
