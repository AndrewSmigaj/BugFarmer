BugFarmer Sprite Guide
Terraria-Style Pixel Art for 45° Overhead View

This guide defines the visual rules, constraints, and workflow for all BugFarmer sprites.
It prioritizes readability, consistency, and production speed over realism.

1. Camera & Perspective (Non-Negotiable)

45° overhead (RPG perspective)

Player sees:

Top surfaces of objects

Front faces of vertical elements

Never show:

Left/right faces

Isometric diamond tops

True side views

Plane Rules

Horizontal planes (tops):

Viewed from directly above

Squares stay square, circles stay circular

Vertical planes (fronts):

Drawn front-on (1:1)

Darker than tops

Depth comes from contrast, not perspective distortion.

2. Lighting Rules (Cheat Aggressively)

Light source: top-left

Lighting is stylized, not realistic

Value Rules

Top surfaces → light

Front faces → dark

Plane boundaries → hard contrast

If lighting feels “too strong,” it’s probably correct.

3. Thickness & Chunkiness (Critical)

Everything has thickness — even if it shouldn’t.

Thickness Ratios (Guideline)

55–65% top surface

25–35% front face

Remaining: trim / edge

Rules:

No 1-pixel front faces on solid objects

Thin objects are exaggerated

Flat sprites are rejected

If it feels chunky → good.

4. Grid Discipline

The tile grid is a feature, not a limitation.

Align major edges to pixel grid

Favor symmetry over realism

Avoid off-grid diagonals unless iconic (tools, bugs)

Sprites that “almost fit” the grid will look wrong in-game.

5. Shape Design (Simplify Hard)

Use blocky, orthogonal shapes

Reduce curves to suggestions

Remove detail until readability breaks — then stop

Ask:

“What is the minimum shape that still reads?”

Then remove one more thing.

6. Color & Materials
Palette Rules

3–5 colors per material

No pure black

No pure white

Slightly muted saturation

Three-Shade System

Light – top surfaces, highlights

Base – main surface

Dark – front faces, shadows, contact edges

Materials should read before objects do.

7. Texture Strategy (Patterned, Not Noisy)

Use controlled repetition

Avoid random dithering

Examples:

Wood → plank bands

Stone → clustered noise

Dirt → horizontal strata + speckles

Think fabric, not photograph.

8. Edge Definition (Cheated Outlines)

Use darker material-relative edges

Apply selectively:

Bottom edges

Contact points

Occlusion boundaries

This improves separation in cluttered scenes.

9. Ground Contact (Mandatory)

Every object must visually sit on the ground.

Use at least one:

Dark base pixels

Implied shadow

Flat contact line

Floating sprites are invalid.

10. Category Rules
Terrain (16×16, tileable)

Seamless tiling

Subtle variation

No strong directional patterns

Furniture

Top surface dominates

Front face clearly visible

Functional silhouette first

Tools

Angled for clarity

Handle + head clearly separated

Iconic shapes only

Bugs

Body silhouette first

Eyes as accent

Wings implied, not detailed

Walls / Fences

Top edge visible

Front face dark

Horizontal tiling required

11. Workflow (Single Sprite)
Pass 1 – Blockout

Define size, footprint, material

Draw top + front planes only

No texture yet

Pass 2 – Material

Apply 3-shade palette

Enforce plane contrast

Snap to grid

Pass 3 – Terraria Bias Pass (Required)

Thicken thin areas

Increase contrast

Remove 10–20% detail

Darken front face

Strengthen base contact

Pass 4 – Validation

Readable at game zoom?

Works next to other sprites?

Recolorable?

Feels slightly chunky?

If yes → ship it.

12. Final Acceptance Checklist

☐ Chunky enough

☐ Strong plane contrast

☐ Grid-aligned

☐ Material reads instantly

☐ Anchored to ground

☐ Matches existing sprites

Fail any one → revise.

Design Philosophy (One Sentence)

BugFarmer sprites should look simple, solid, and slightly overbuilt — because clarity beats correctness.

Choosing the Right Sprite Size (Terraria-Style, 45° Overhead)
1. Pick a Single Base Tile Size First (Everything Depends on This)

This is the root decision. Everything else scales from it.

Strong Recommendation

Base world tile: 16×16 pixels

Why:

Proven (Terraria, Starbound, Core Keeper)

Easy to scale cleanly (×2, ×3, ×4)

Forces good simplification

Keeps memory + draw calls sane

If you pick 24×24 or 32×32 as your base tile, you:

Encourage over-detailing

Increase art cost

Lose the “chunky” Terraria feel

Rule: If a tile isn’t readable at 16×16, the design is wrong — not the resolution.

2. Separate World Footprint From Sprite Canvas

This is where many teams get confused.

Definitions

Footprint: How many tiles the object occupies in the world

Sprite size: Pixel dimensions of the image

These are not the same thing.

Example
Object	Footprint	Sprite Size
Stone block	1×1 tile	16×16
Table	2×1 tiles	32×24 or 32×28
Tree	1×1 tile	32×48
Player	3×2 tiles	48×32

Sprites are often taller than their footprint to show height.

Rule:
Footprint controls gameplay. Sprite size controls readability.

3. Vertical Budget Rule (Critical for 45° Overhead)

In your camera, height is shown downward (front face).

Safe Vertical Budget

Front face height: 25–40% of sprite height

Top surface: 55–65%

Trim: remaining pixels

Practical Guidance

If front face is <2px → looks flat

If front face >50% → looks like side view

This ratio matters more than exact pixel counts.

4. Category-Based Size Standards (Recommended)

Lock these in early and do not drift.

Terrain

16×16 (always)

Tileable

Zero overhang

Small Objects (rocks, stumps, stations)

Footprint: 1×1 or 2×1

Sprite: 16×16 to 32×24

Furniture

Footprint: 2×1, 2×2

Sprite:

Tables: 32×24

Chests: 16×16 or 16×20

Beds: 32×32

Trees

Footprint: 1×1

Sprite: 32×48 or 32×64

Trunk must touch tile base

Player / NPCs

Footprint: 3×2

Sprite: 48×32

Must visually match furniture scale

Bugs

8×8 (small)

16×16 (large / flying)

Rule:
If two objects interact (sit on, walk past, craft at), their sprite sizes must reinforce that relationship.

5. Avoid “Resolution Inflation”

A very common trap.

Warning Signs

“This needs more pixels”

“It feels cramped”

“We can just scale it down later”

These usually mean:

Shape is unclear

Contrast is too weak

Thickness is missing

Do not fix design problems with more pixels.

Terraria sprites look good because they are designed for 16×16, not despite it.

6. Test at Game Zoom — Not in the Editor
Mandatory Test

View sprites at:

Actual camera zoom

With 5–10 other objects nearby

On moving background

If it only looks good at 400% zoom:
→ It is not good.

7. Scaling Strategy (Future-Proofing)

If you ever upscale:

Use integer scaling only (×2, ×3, ×4)

Never resample or smooth

Design at native resolution

Designing at 16×16 lets you:

Ship pixel-perfect now

Go HD later without re-authoring

8. The “Goldilocks Check”

Ask this before finalizing a size:

☐ Does it read instantly?

☐ Does it feel chunky?

☐ Does it overpower nearby tiles?

☐ Does it underwhelm interactables?

☐ Does it match player scale intuitively?

If it feels slightly bigger than you expected → correct.

9. One Hard Rule (Worth Highlighting)

Never mix multiple “implicit scales.”

If:

Tables are drawn as if 1 tile = 1 meter

Trees are drawn as if 1 tile = 3 meters

Players are drawn as if 1 tile = 0.5 meters

Your world will feel wrong, even if sprites are good individually.

Pick a mental scale and stick to it.

Bottom Line Recommendation

Base tile: 16×16

Design everything to read at that scale

Use sprite height to imply verticality

Err on chunkier, not thinner

Lock category size standards early