# Shaped ground: controls, precision and data model — research notes

Research for Bug Farmer's shaped-ground placement (full squares, 4 diagonal halves, possibly 4 straight
halves and 4 quarters, laid on top of the ground already in a square). Written incrementally, 2026-09-29.
Nothing in the repo was edited. "unsure" = not confirmed from a source.

## 0. What the game has today (read from the repo, not guessed)

- Camera: `SampleScene.unity` has an orthographic camera, `orthographic size: 7.7` (line 954). No script
  assigns `orthographicSize` and there is no Cinemachine, so the view is 15.4 squares tall, fixed.
  Pixels per square on screen = screen height / 15.4:
  - 1280x720 -> 46.8 px; 1280x800 (Steam Deck) -> 51.9 px; 1366x768 -> 49.9 px;
  - 1920x1080 -> 70.1 px; 2560x1440 -> 93.5 px; 3840x2160 -> 140.3 px.
  (Physical size: a 24-inch 1080p monitor is ~0.277 mm/px, so a square is ~19 mm; a 15.6-inch 1080p laptop
  is ~0.18 mm/px -> ~12.6 mm; Steam Deck 7-inch 1280x800 is ~0.118 mm/px -> ~6.1 mm.)
- Shapes already defined: `TileCompositor.Shapes` (BugFarmerClient/Assets/Scripts/World/Rendering/TileCompositor.cs:25):
  `full, diagNE, diagNW, diagSE, diagSW, halfN, halfS, halfE, halfW, quadNE, quadNW, quadSE, quadSW` (13).
- A shaped square today is ONE string in the ground layer: `matA~matB~shape` (e.g. `grass~dirt~diagNE`);
  server `ChunkData.Ground [][]string` (nakama/modules/world/zone.go:137-141), 32x32 per chunk, JSON.
  `PrimaryMaterial()` (tiles.go:~95) makes matA govern all gameplay. There is no separate undiggable base.
- Current shape input (spike, `ShapedGroundSpike.cs`): the mouse wheel cycles the shape while a shovel is held,
  `[`/`]` also cycle it, M/N cycle materials (temporary). The brief says the wheel is now reserved for the
  hotbar, so this must move.
- `PlacementController.cs:64` already uses R to rotate a placeable's direction (`_placementDirection+1 % 4`).
  The brief says R also switches the shovel between Dig and each ground kind.

## 1. Pointing precision for small targets

### 1a. What the guidelines say (read in full, 2026-09-29)

| Source | Size rule | Notes that matter to us |
|---|---|---|
| WCAG 2.2 SC 2.5.8 Target Size (Minimum), AA — w3.org/WAI/WCAG22/Understanding/target-size-minimum | **24 x 24 CSS px**; "it must be conceptually possible to draw a solid 24 by 24 CSS pixel square ... completely within the target". Smaller is allowed if a 24 px circle centred on each target does not touch another target. | Beneficiaries: tremor, spasticity, fine-motor difficulty. **Essential exception for maps / dense data where position carries meaning** — our world grid is exactly that kind of target, so WCAG does not strictly bind world cells, but it is the best published floor for "can people with motor limits hit this". A CSS px is a density-independent unit (~0.0213 degrees of visual angle). |
| WCAG 2.2 SC 2.5.5 Target Size (Enhanced), AAA — .../target-size-enhanced | **44 x 44 CSS px** | "Touch is particularly problematic ... coarse precision"; mouse/stylus are finer. |
| Apple HIG, Accessibility (JSON backing of the HIG page) | iOS/iPadOS **44x44 pt default, 28x28 min**; macOS **28x28 default, 20x20 min**; tvOS 66/56; visionOS 60/28; watchOS 44/28 | "Consider spacing between controls as important as size" — ~12 pt padding around bezelled controls, ~24 pt around bezel-less ones. |
| Google / Android accessibility help (answer 7101858) | **48 x 48 dp, about 9 mm**, spaced 8 dp | Research cited: 7-10 mm for touch. The TOUCH area may be bigger than the drawn icon (24 dp icon inside a 48 dp target, TouchDelegate). |
| Microsoft Windows "Targeting" (learn.microsoft.com, updated 2026-09-28) | **7.5 mm ~ 40x40 px at 135 PPI** for touch | Make frequently pressed targets larger; targets whose mistakes are costly need more padding. |
| Xbox Accessibility Guideline 107 (Input) | Mobile touch targets: **15 mm phone, 24 mm tablet** (59 px at 100 DPI ...) | Also: UI must work with **single, non-simultaneous digital presses**; **don't require two sticks**; avoid long holds and simultaneous presses; offer toggles; act on the **up event** and give a **cancel before release or an undo**; The Long Dark's "accessible interactions" turns every hold into a press (same idea as our "no holds" setting). Sensitivity adjustable by at least +-50%. |
| Xbox Accessibility Guideline 112 (UI navigation) | — | Every UI fully usable by keyboard/controller digital input alone; linear menus should loop (last -> first); consistent prompts. |
| Game Accessibility Guidelines, "Ensure interactive elements / virtual controls are large and well spaced" (Basic) | touch: 2.4 cm ideal, 0.96 cm on phones — **use as a minimum**, larger if close together | Says it applies to cursor-driven interfaces too, for players with motor impairments. |
| Game Accessibility Guidelines, "Avoid / provide alternatives to requiring buttons to be held down" (Intermediate, motor) | — | Toggle / automatic / player's choice; "toggle is marginally slower than hold ... provide player choice". |

**Take-away for Bug Farmer.** For a mouse on PC the published floors are 24 px (WCAG AA; Apple's macOS minimum is 20 pt,
default 28 pt) and the comfortable size is ~44 px. For touch it is 7.5-9 mm (40-48 dp). A sub-target inside a square
should be judged against these, measuring the **hit area**, not the drawn triangle (Google's 24-in-48 point).

### 1b. Fitts's law — the numbers we can use

| Source | What it gives us |
|---|---|
| Soukoreff & MacKenzie 2004, "Towards a standard for pointing device evaluation" (IJHCS 61; full PDF, 39 pp, read via text extraction) | Shannon form `MT = a + b*log2(D/W + 1)`. **Effective width We = 4.133 x SD of the click end-points** = the width that contains ~96% of clicks (a 4% miss rate). ISO 9241-9 mouse studies agree on **throughput 3.7-4.9 bits/s** (older non-standard studies range 2.3-12.5). |
| NN/g, "Fitts's Law and Its Applications in UX" | Bigger targets = faster AND fewer errors; padding the hit area around a small target helps (but users still slow down if they don't know the padding is there); pop-up/pie menus at the cursor give equal short distances; screen edges are "infinite" for a mouse but not for touch. Movement = fast ballistic phase + slow correction phase, and small targets lengthen the correction phase. |

**Worked numbers for us (my arithmetic from the formula above; throughput 3.7-4.9 bit/s, intercept ignored):**
- Square on screen at 1080p = 70 px; a quarter-square hit area = 35 px.
- Moving the cursor 5 squares (350 px) to a **whole square**: ID = log2(350/70+1) = 2.58 bits -> ~0.53-0.70 s.
- Same move to a **quarter of the square**: ID = log2(350/35+1) = 3.46 bits -> ~0.71-0.93 s. So aiming at a sub-part
  costs roughly **+0.9 bit, about +0.2 s per placement** on a long move.
- Adjusting within the square you are already on (move half a square to the next quarter): ID = log2(1+1) = 1 bit -> ~0.2-0.27 s.
- Miss rate: to keep misses near 4%, click scatter SD must be <= W/4.133 -> <= 8.5 px for a 35 px quarter, <= 5.7 px for
  a 23.5 px quarter (720p). Unsure: I found no study measuring click scatter for triangles specifically.

### 1c. (continued below in section 6 — the target-size estimate is worked out there, after the control designs)

## 2. Speed of selecting a command: cycling vs pie/radial vs palette + hotkeys

| Source (read in full) | Finding |
|---|---|
| Callahan, Hopkins, Weiser & Shneiderman, "An Empirical Comparison of Pie vs. Linear Menus", CHI '88 (6-page PDF from cs.umd.edu, text-extracted) | 8-item menus, 33 subjects, 1,980 selections (pilot: 16 subjects). **Pie ~15% faster** than linear, errors fewer (only marginally significant, p = 0.087). Pie seek time is **flat across item positions**; linear seek time **grows with the item's distance** from the cursor. Pie activation regions were 3,500-6,000 px^2 vs 1,000-2,000 px^2 for linear, at a fixed 10 px distance vs 13-200 px. Caveats: only exactly 8 items; covers screen; subjects split on preference; the most mouse-naive found linear easier at first. (Exact seek-time means are in a table image I could not extract — unsure of the seconds.) |
| Kurtenbach & Buxton, "User learning and performance with marking menus", CHI '94 (full HTML on billbuxton.com) | Real app (ConEd), 2 users, 18 h, 5,237 selections. Users **start with the visible menu and move to blind marks**: User A reached 93.4% marks, User B 55%. **Marks 0.18 s vs menu 1.10 s (User A, ~7x); 0.40 s vs 1.54 s (User B, ~4x)**; still 3-4.2x faster after removing the ~1/3 s press-and-wait delay. After a lay-off, mark use drops and users pop the menu up again to relearn — **being able to switch back and forth between the menu and the fast path matters**. Design rules: even numbers of items up to 12; **match the direction of an item to the spatial meaning of what it does**. |
| Kurtenbach & Buxton, "The limits of expert performance using hierarchic marking menus", INTERCHI '93 (full PDF, text-extracted) | Error rate is the limit, not time. **4-item menus: < 10% errors even 4 levels deep; 8-item: < 10% up to 2 levels**; 12-item gets error-prone. **On-axis directions (N/S/E/W) are faster and more accurate than off-axis (diagonals)**; put frequent items on-axis. Acceptable error rate depends on the cost of undoing an error. |
| Wikipedia "Pie menu" + "Marking menu" (checked against the papers above) | 3-12 items is the practical range for a radial layout; games that use them: The Sims (pie menus), Secret of Mana (ring menu), GTA V (weapon/radio wheel), CS:GO buy menu, Monkey Island verb coin. |

**What this means for choosing a shape (5-13 choices):**
- A **linear cycle** (press R / a button N times) costs time proportional to how far the wanted item is in the list:
  with 4 diagonal orientations the average is 1.5 presses forward (or ~1 press with forward+back keys); with all 13
  shapes it is ~6 presses. Cycling is the easiest to learn and to do on any device, but it is the slowest for experts
  once the list is long, and each press must be checked on screen.
- A **radial menu** keeps every choice one short flick away (flat time for all items, Callahan), and experts
  flick without looking (4-7x faster than reading a menu, Kurtenbach & Buxton). 4 or 8 items is the sweet spot;
  **our 4 diagonals map to the 4 diagonal directions and the 4 straight halves map to N/E/S/W — the menu direction
  can literally BE the shape direction** (Kurtenbach's "spatial commonality" rule). Cost: needs a hold (or a
  press-to-open / press-to-close under "no holds"), covers the screen, and on the 8-way layout the diagonal items are
  the "off-axis" ones that are slightly less accurate.
- A **palette with hotkeys** is the fastest expert path for many items (one key per item), but keys must be learned;
  users often fail to switch from menus to hotkeys (see 2b below).

## 4. Layered ground data (read ahead of topic 3 because the sources came in first)

| Game / source (read) | How a cell stores base + shaped piece | How removal works |
|---|---|---|
| **Terraria** — tModLoader source `patches/tModLoader/Terraria/TileData.Default.cs` (branch 1.4.5, read in full) + `Tile.TML.cs` + tModLoader `Tile` docs | Each tile has SEPARATE arrays: `TileTypeData { ushort Type }` (the block), `WallTypeData { ushort Type }` (the wall behind), `LiquidData { byte Amount; byte typeAndFlags }`, and a 32-bit bit-packed `TileWallWireStateData` whose layout comment reads `wwwwsssh YYYXXXXN NnnCCCCC cccccait`: **bit 24 = IsHalfBlock, bits 25-27 = Slope (3 bits)**, bit 0 HasTile, paint colours, frame numbers, 4 wire bits; plus `short TileFrameX/Y`. `SlopeType` = Solid, SlopeDownLeft, SlopeDownRight, SlopeUpLeft, SlopeUpRight; `BlockType` = Solid, HalfBlock, then the 4 slopes (6 shapes). | Hammering cycles the shape; mining removes the block and reveals the wall behind. The wiki (Hammers page) states each tile holds only ONE block: "impossible to have ... a Stone Block and a Dirt Block with opposite-facing slopes within the same tile" — the empty part of a slope shows the wall layer. **So Terraria = 2 material layers per cell (block + wall) + a 3-bit shape on the top one.** |
| **Terraria hammer** — terraria.wiki.gg/wiki/Hammers (read) | — | Hammer cycles: full -> half -> 4 slopes -> full ("the cycle repeats infinitely"). **"The order ... may vary depending on whether there are other blocks surrounding the hammered block"** — i.e. the cycle is context-aware: it offers the likely shape first. |
| **Minecraft** — minecraft.wiki Slab + Stairs (raw wikitext, read) | Block states are small enums on the block: slab `type = bottom/top/double` (+ `waterlogged`); stairs `facing = N/E/S/W`, `half = bottom/top`, `shape = straight/inner_left/inner_right/outer_left/outer_right` (Bedrock: `weirdo_direction 0-3`, `upside_down_bit`; slab `minecraft:vertical_half`). | Placement rule = **where you point + which way you face**: placing a slab on the bottom part of a block's side makes a bottom slab (the wiki, paraphrased); "... the top half of the side surface creates a top slab"; a top + bottom slab of the same kind merge into a double slab. Stairs `facing` "matches the direction the player faces"; `shape` is derived automatically from neighbouring stairs. |
| **Factorio** — Lua API `LuaTile` (read) + wiki Landfill, Concrete (read) | Each tile position has the visible tile + **`hidden_tile`** + (2.0) **`double_hidden_tile`**. "During normal gameplay, only non-mineable or foundation tiles can become hidden"; "only non-mineable tiles can become double hidden." e.g. concrete over landfill over water = 3 layers. | Mining the top tile restores the hidden one. Placing concrete over another player path "automatically mines the previous path" (player paths REPLACE each other; only natural/foundation ground is kept underneath). Landfill became mineable in 2.0.7. Brush size +/- on Numpad. |
| **Don't Starve** — dontstarve.wiki.gg Turfs (read) | One turf type per tile; turfs are dug with a Pitchfork and replaced. Visual blending between neighbouring tiles uses a **priority ("dominance") order — "Turfs with higher priority ... will partly cover other turfs"**. | What is left after digging: not stated on that page (unsure; I believe a plain undiggable ground, not confirmed). |

### 4b. Rendering in Unity (read: Unity Manual "Tilemap Renderer" reference; ScriptReference TilemapRenderer.Mode)

- Modes: **Chunk** "renders multiple tiles together in single batches" (other objects can't sort between its tiles);
  **Individual** sorts each tile with other sprites ("can reduce performance"); **SRP Batch** batches with the SRP batcher.
  Sorting Layer + Order in Layer decide which tilemap draws first. The page does not discuss multiple tilemaps as layers
  or atlases — the claim that Chunk mode only batches tiles whose sprites share one texture/atlas is **unsure** (widely
  repeated, not confirmed in what I read).

## 3. Gamepad selection of sub-cell shapes (how console/controller building games do it)

| Game (source read) | How the target square is picked | How a sub-cell shape / orientation is picked |
|---|---|---|
| **Terraria** (terraria.wiki.gg Hammers, Controls, Smart Cursor) | Gamepad: right stick moves a cursor (Switch Pro D-pad moves it by tile); Smart Cursor (toggle on R3) auto-targets "the nearest legal space to the cursor"; the quick-use button acts "in the direction the analog stick is held". | **A single cycling action**: each hammer hit steps full -> half -> 4 slopes -> full, and the order "may vary depending on ... surrounding" blocks (context-aware cycle). No way to pick a slope directly was documented. |
| **Minecraft** (Slab, Stairs wikitext) | Crosshair (mouse, or right stick on console — console detail unsure). | **Facing + pointed sub-face**: stairs face the way the player faces; top/bottom half = which half of the face the crosshair hits; stair corner shapes are automatic from neighbours. |
| **Animal Crossing: New Horizons** (Nookipedia Island Designer) | The square in front of the player; "Press A while on grassy areas to create or remove paths"; the same tool removes. | Corner rounding is **automatic**: "Paths can also be rounded if the path is on the edge of a perpendicular pathway." (The widely described trick of changing a corner's shape by pressing A again on it — **unsure**, not in the page I read.) |
| **Stardew Valley** (Controls wiki) | Right stick moves a cursor; very sensitive but used "to exactly place furniture, rugs, windows"; tools also act on the tile in front. | Rotation of the few rotatable items by a face button: "use A to Rotate the rug". Flooring has no sub-cell shapes. |
| **Factorio** (Controls wiki) | Mouse cursor; controller scheme exists (Switch listed, e.g. "ZR + A" ghost build). | **R rotates, Shift+R rotates back; Q "pipette" copies the thing under the cursor**; Ctrl+Z undo, Ctrl+Y / Ctrl+Shift+Z redo; tile brush size Numpad +/-. |
| Dragon Quest Builders 2, The Sims 4 console, Minecraft Bedrock controller specifics | — | **Unsure — not read.** (Search budget was exhausted mid-session; I did not reach reliable pages for these.) |

**Pattern across the games that were read:** apart from Minecraft's first-person crosshair (whose console details I did
not confirm), no controller game I read asks the player to aim at a *part* of a square with a stick. They use (a) the square in front / a stick cursor for WHERE, and (b) for WHICH SHAPE either a single
cycling button (Terraria hammer, Stardew rotate, Factorio R), the player's facing (Minecraft stairs), or automatic shaping
from the neighbours (Minecraft stair corners, ACNH path rounding, Terraria's context-aware hammer order).
The accessibility rules agree: XAG 107 — single non-simultaneous presses, never require two sticks, no long holds.

## 5. Preview and error feedback

| Source (read) | Finding |
|---|---|
| NN/g "10 Usability Heuristics" | #1 keep users informed with feedback in reasonable time; #3 "a clearly marked emergency exit" — Undo and Redo; #5 prevent errors (slips vs mistakes; constraints; confirm before committing); #6 recognition rather than recall (make options visible); #7 accelerators "hidden from novice users" so one design serves novices and experts; #9 plain-language errors that suggest a fix. |
| NN/g "Preventing User Errors: Avoiding Unconscious Slips" | Constraints, good defaults, suggestions while acting — e.g. propose the likely choice first (our auto-shape from neighbours is exactly a "good default"). |
| Factorio wiki "Ghost" + "Controls" | A ghost = "a semi-transparent marker" at the spot; "Any tile that can be placed by the player is valid as a ghost". Undo/redo on Ctrl+Z / Ctrl+Y. (The red/green validity colouring is not on that page — unsure from source, though I know it from play.) |
| XAG 107 | Act on the **up** event so a mis-press can be cancelled by moving away before release; if no cancel, provide a simple undo. |

## 6. How big must a square be on screen for pointing at part of it? (worked from sections 1a-1b)

Only one shape family is active at a time, so the square is split into 4 hit regions, never 13:
- **Corner shapes** (diagonal halves "point at the corner", quarters "point at the quarter"): the 4 **quadrants**.
  The largest upright square that fits in a region (the WCAG 2.5.8 test) is **S/2**.
- **Straight halves** ("point at the side"): the 4 **triangles between the two diagonals** (nearest side). The largest
  upright square that fits is **S/3** (width at height a is S-2a, so a = S/3); the largest circle is 0.414*S.
  (Using the drawn half-rectangle as the hit area does not work: the N and E halves overlap in the NE quadrant.)
- The hit area is the whole region, never the drawn triangle (Google's 24-in-48 rule; NN/g on padded targets).

| Sub-target | fits a square of | S for 24 px (WCAG AA floor) | S for 28 px (Apple macOS default) | S for 44 px (WCAG AAA / iOS, "comfortable") |
|---|---|---|---|---|
| Whole square | S | 24 | 28 | 44 |
| Quadrant (diagonal, quarter) | S/2 | **48** | **56** | **88** |
| Side triangle (straight half) | S/3 | **72** | **84** | **132** |

Against the game's fixed camera (S = screen height / 15.4):

| Screen | S | Quadrant | Side triangle | Verdict for pointing at parts |
|---|---|---|---|---|
| 1280x720 | 47 px | 23 px | 16 px | below the floor — must not rely on it |
| Steam Deck 1280x800 (~0.118 mm/px) | 52 px | 26 px (~3 mm) | 17 px | floor only; Deck players mostly use sticks anyway |
| 1920x1080 | 70 px | 35 px (~9.7 mm on a 24-inch) | 23 px | corners OK (above 24 and 28), halves just under the floor |
| 2560x1440 | 93.5 px | 47 px | 31 px | corners comfortable, halves OK |
| 3840x2160 | 140 px | 70 px | 47 px | all comfortable |

**Conclusion:** pointing at a corner is acceptable from ~56 px squares (1080p and up) and comfortable from ~88 px;
pointing at a side needs ~84 px. So part-pointing can be a mouse accelerator on 1080p+, never the only way. A build
zoom would lift this (1.5x at 1080p -> 105 px squares, 52 px quadrants), but the camera is fixed today and the wheel is
taken, so it would need a key or an automatic zoom while shaping (owner's taste call: you see less of the world).
Side note (noticed, not investigated): 70 px per square is a non-integer 2.19x scale of 32-px art; I found no
pixel-perfect camera component in the scene or scripts. Unsure whether this is intended.

Techniques that make part-pointing work (from the sources): (1) hit region = whole quadrant/triangle, not the drawn
shape; (2) a live ghost of the exact result + outline of the filled part (NN/g #1); (3) hysteresis — only switch to a
new quadrant after the cursor is clearly past the line (my suggestion ~12% of S, about 8 px at 70 px; unsure, tune in
playtest) so the ghost does not flicker at the centre; (4) act on button-up so a wrong aim can be cancelled by moving
off before release (XAG 107); (5) an undo.

## 7. Control designs for Bug Farmer, scored

Fixed for all of them: **R keeps choosing Dig or the ground kind (the material)**; the wheel stays on the hotbar; the
gamepad target is the square in front of the player. Keys named below (F, C) are placeholders: F, C, Q, T, V, X, Z and Tab
show no `KeyCode` use in the client scripts (grep, 2026-09-29; no string-key, `InputAction` or `Gamepad.current` use
either — so there are no gamepad bindings in the scripts yet, and which buttons will be free is still open).
Scores 1 (bad) - 5 (good). "Expert time" numbers come from sections 1b and 2.

| # | Design | Novice ease | Expert speed | Small squares | Gamepad | Accessibility | Fits R + wheel | Discoverable | Keep / reject |
|---|---|---|---|---|---|---|---|---|---|
| D1 | **One cycle key** through every shape (Terraria-hammer style): F steps full -> 4 diagonals -> 4 halves -> 4 quarters; Shift+F back | 4 | 2 | 5 | 5 | 5 | 3 | 4 | **Keep as a part** (rotate within one family = 4 steps, avg 1-1.5 presses). Reject as the whole control: with 13 shapes the average is ~3.25 presses (bidirectional), each needing a look; a second full cycle next to R invites mixing the two up. |
| D2 | **Point at the part** (Minecraft-slab style): the quadrant / side under the cursor sets the direction; family chosen elsewhere | 3 | 5 | 2 | 1 | 2 | 5 | 3 | **Keep as a mouse accelerator only, on when squares >= 56 px.** One click = square + direction; costs ~+0.2 s aiming vs a whole square but saves 1-2 key presses. Reject as the only way: fails 720p/Deck sizes, fails gamepad, demands fine motor control. |
| D3 | **Painter panel + rotate key**: a strip of shape icons on the HUD, click (or hotkey) + F to turn | 5 | 3 | 5 | 3 | 4 | 4 | 5 | **Reject as the main path, keep its visibility.** Each trip to a screen-edge panel is ~4.3 bits (800 px to a 44 px icon) = ~0.9-1.15 s; gamepad needs a focus mode. Its good part (see every option, NN/g #6) survives as the HUD shape icon + the wheel's pictures. |
| D4 | **Shape wheel** (marking menu): hold C, flick; 4 diagonals on the diagonal directions, 4 halves on N/E/S/W, full in the centre; under "no holds" C opens and a click/confirm closes | 4 | 5 | 5 | 4 | 4 | 4 | 4 | **Keep — the main chooser.** Direction of the flick = the side that gets filled (Kurtenbach's spatial rule, easy to remember). 8 items at depth 1 stays under 10% errors; blind flicks 0.18-0.40 s vs 1.1-1.5 s reading a menu; flat time for every item (Callahan). Minus: covers part of the screen; diagonals are the slightly less accurate "off-axis" slots. |
| D5 | **Auto-shape from neighbours**: the ghost proposes the diagonal that joins the two neighbouring edges of the same ground (like Minecraft stair corners, ACNH path rounding, Terraria's neighbour-aware hammer order) | 5 | 4 | 5 | 5 | 5 | 5 | 3 | **Keep as the default suggestion.** Zero extra input when right (road corners — the required use); the ghost shows it before you commit. Reject as the only way: it cannot guess when there are no neighbours or you want something unusual. |
| D6 | **Drag toward the corner** on the square (a gesture) | 2 | 5 | 4 | 1 | 1 | 5 | 1 | **Reject.** Hidden, path-based gesture (XAG 107: never required); the wheel's blind flick gives the same speed openly. |
| D7 | **Aim by facing / movement direction** (Minecraft-stairs style) | 3 | 3 | 5 | 4 | 4 | 5 | 2 | **Reject.** Four-way facing cannot name four diagonals without an arbitrary rule (whether the player sprite has 8-way facing is unsure). |
| D8 | **Recommended hybrid** = D5 default + D4 wheel + D1 rotate (within the family) + D2 pointer-aim when big enough + HUD icon | 5 | 5 | 5 | 5 | 5 | 4 | 4 | **Keep.** Every shape reachable with single presses, no holds, no precision; experts get blind flicks or one-click aiming. Cost: two new bindings (rotate, wheel) and a clear priority rule (below). |

## 8. Recommended design (D8) with the numbers

**The player's model: "R picks the ground. The ghost shows exactly what you will get. F turns it. C shows all shapes."**

1. **Materials stay on R** (Dig -> ground kinds), unchanged.
2. **The shape = family + direction**, shown as an icon beside the shovel's material and as a ghost on the target square.
3. **Where the direction comes from — "last input wins":**
   - **Auto** (default on): whenever the target moves to a new square, the ghost takes the direction that joins the
     neighbouring edges of the same ground (road corners). No neighbours -> keep the current direction.
   - **F / Shift+F** (gamepad: one face button or D-pad left/right — unsure which are free): turn 90 degrees within the
     family; 4 states loop (XAG 112), avg 1 press with both directions. With Auto on, F overrides only this square;
     with Auto off, the chosen direction sticks across squares (for repeated edges).
   - **Pointer-aim** (mouse): when on, the quadrant under the cursor sets a corner shape's direction, the nearest side
     sets a straight half's. **Default on for corner shapes when a square is >= 56 px (quadrant >= 28 px — Apple's macOS
     default, above WCAG's 24 px), for straight halves only at >= 84 px; otherwise off.** 1080p = 70 px -> corners on,
     halves off; 720p/Deck -> off. A settings toggle overrides. With hysteresis (~12% of a square, tune).
4. **The shape wheel on C** (gamepad: a bumper; stick direction picks). Pictures drawn with the current materials.
   Slots: diagonal halves at NE/NW/SE/SW, straight halves at N/E/S/W (flick toward the side you want filled),
   **full in the centre** (release/confirm without moving), plus small centre-ring toggles for **Auto** and — only if
   quarters ship — a **Quarters** page (4 corner slots again). Normal mode: hold, flick, release (appears after ~1/3 s;
   an early flick selects blind, as in Kurtenbach & Buxton). "No holds": C opens, stick/mouse/WASD highlights, click or
   C confirms, Esc/B cancels. No simultaneous presses required anywhere (XAG 107).
5. **Scope suggestion (owner's call):** ship full + 4 diagonals first (the required road set: a 4-slot wheel + centre is
   the most accurate layout, every slot 90 degrees wide); add straight halves as the N/E/S/W slots when wanted; put
   quarters on a second page only if the owner wants them — they are the least readable at 32 px (16x16 art pixels).
6. **Feedback:** ghost of the exact result at partial opacity with an outline of the filled part; can't-place shown by
   colour **and** a symbol + short reason ("Needs 1 sand", "Something is standing here", "Base ground can't be dug") —
   not colour alone (the colour-only rule is from the Game Accessibility Guidelines as I know them, not re-read today:
   unsure); in Dig mode, outline the piece that will come off (shaped piece first, then the ground); place on
   button-up (move off to cancel); **Ctrl+Z / Ctrl+Y** undo/redo of the player's own last N shovel actions, done by the
   server with refunds, refused if someone else changed that square since (multiplayer). Gamepad undo: an entry in the
   wheel's centre ring (mapping unsure).
7. **Why this over the single best alternative (pure wheel):** the wheel alone costs a hold+flick on every change; with
   Auto most road corners need zero input, and F gives 1-press fixes without covering the screen. **Over pure
   pointing:** pointing fails below 56 px and on gamepad; here it is an optional accelerator where the numbers allow it.

## 9. Recommended data model: base + ground + one shaped piece

**Three slots per square, two of them diggable:**

| Slot | Holds | Set by | Dug? |
|---|---|---|---|
| `base` | the undiggable bottom (one kind per chunk by default, exceptions allowed) | world generation | never — digging stops here with "Base ground can't be dug" |
| `ground` | a full-square material, or empty (base shows) — natural grass/sand AND player-laid floors live here | world gen / shovel "full" | yes, second |
| `overlay` | at most ONE shaped piece: material + shape (12 non-full shapes; 4 bits) | shovel shaped placement | yes, first |

**Why 3 (not 2, not a free stack):** Terraria keeps 2 material layers (block + wall) and a 3-bit shape on the block;
Factorio keeps at most 3 (visible + hidden + double-hidden) and player paths REPLACE each other ("Placing it over another
type of path automatically mines the previous path"). A second shaped layer would put 3 materials in one 32-px square
(unreadable), multiply rules and art, and make the dig order ambiguous. No source I read needed more.

**Rules:**
- Place **full** M: an overlay there is removed and refunded; a different ground is refunded and replaced by M (Factorio
  rule). Same M already -> nothing happens, with a message.
- Place **shaped** (M, shape): costs 1 M. Same material as the ground -> refused ("already that ground"). An existing
  overlay of the same M in the **complementary** shape -> the two halves merge into ground = M (Minecraft's
  top + bottom slab = double slab), old ground refunded. Any other existing overlay -> replaced and refunded.
- **Dig:** overlay first, then ground, then refuse at base; each piece refunds the 1 item it cost. This keeps the
  owner's rule that a two-material square costs both materials (each layer is paid when laid) — check it against the
  decision log wording before building.
- **Gameplay** (walking, planting, water) keeps ONE hook like today's `PrimaryMaterial()`; which layer it reads (ground,
  or the overlay when present — today's behaviour, see Migration) is a design decision — **owner's call**. If the bug simulation
  reads ground cells (walkability, food), that rule is a **determinism change** and goes through the frontier-sync recipe.
- Migration (verified in `TileCompositor.cs` header: "material A fills the shape mask's 1-region, material B the
  0-region"): today's `A~B~shape` becomes **overlay = (A, shape), ground = B**. Because `PrimaryMaterial()` returns A,
  **today the shaped piece already governs gameplay** — so "the overlay governs when present" is the no-behaviour-change
  choice. Existing plain ids become `ground`; `base` gets a zone default. Water and other special tiles need a decision
  (base or ground).

**Size and network for a 256x256 zone (65,536 squares; 64 chunks of 1,024) — my arithmetic:**

| Encoding | Per square | Per chunk | Per zone | Notes |
|---|---|---|---|---|
| Today: JSON string per square (`"grass",` ~8 B; `"stone_path~grass~diagNE",` 26 B) | ~8-10 B | ~9 KB | ~0.55-0.65 MB | shaped squares cost 2-3x a plain one |
| **Layered, JSON-compatible (recommended first step):** keep `ground [][]string`; add `base` per chunk; add a SPARSE `overlay` list `{"i":517,"m":"stone_path","s":"diagNE"}` | ground as today + ~40 B per shaped square | ~9 KB + 40 B x shaped | +80 KB for 2,000 shaped squares (3% of the zone) | backward compatible (`omitempty`); nothing extra when unused |
| Layered binary (later, only if profiling says so): u8 base, u8 ground, u8 overlay material, u8 shape (or 12 bits) | 3.5-4 B | 3.5-4 KB | 224-256 KB raw | mostly-empty overlay compresses well (ratio **unsure**) |
| One edit on the wire | binary ~5 B payload (x u8, y u8, slot, material, shape); JSON ~60-90 B | — | — | 8 players x 3 edits/s x 100 B = ~2.4 KB/s: negligible |

Chunk size matters mainly for late-join/subscription snapshots (the project already hit Nakama's 256 KB read cap once;
now raised) — the sparse overlay adds little, so the JSON-compatible step is safe.

**Drawing it in Unity — recommended: three Tilemaps under the existing Grid** (`Base` order 0, `Ground` 1, `Overlay` 2),
Chunk or SRP-Batch mode. An overlay tile = that material's texture cut by the shape mask (reuse TileCompositor's
hard-edged procedural masks and its GPU `Graphics.Blit` path — the tile PNGs import with `isReadable:0`, so the cut must
stay on the GPU; blit with transparency where material B used to go) plus a 1-px darker rim along the cut so the edge
reads at 32 px. Sprites needed =
materials x 12 (8 x 12 = **96**) instead of every ordered pair (8 x 7 x 12 = **672**); build them at load and pack them
into one runtime texture so batching holds (the atlas-batching point is **unsure** — check with the Frame Debugger).
Digging = clear one tilemap cell; the data slots and the drawn layers match 1:1.
Alternative kept on file: today's runtime composite per (A, B, shape) on one tilemap — better if the seam must blend both
materials, but its textures grow with the pairs in use and digging must parse ids. Blending between NEIGHBOURING
squares (Don't Starve's priority/"dominance" overlap) is a separate, later feature.

## 10. Cold-critic pass (what could be wrong) and open questions

- **Tap vs hold on one key** was considered (Kurtenbach's press-and-wait) and rejected: a press-length distinction is a
  timing demand (XAG 107 "speed/duration"). Rotate and wheel are two separate, remappable bindings.
- **Auto can surprise.** Mitigation: the ghost always shows the result before commit; Auto is a visible toggle; F
  overrides. Measure in a playtest how often Auto guesses road corners right (**unsure**, no data).
- **Pointer-aim fighting F:** resolved by "last input wins" + hysteresis; still worth a playtest.
- **Wheel covers the world:** keep it small (radius ~2 squares), semi-transparent, centred on the cursor (mouse) or the
  target square (gamepad).
- **Not confirmed from sources:** Dragon Quest Builders 2, The Sims 4 console, Minecraft console controls, ACNH's
  "press A again on a corner" trick, Factorio's red/green ghost colours, Chunk-mode atlas batching, the colour-only
  accessibility rule (not re-read), gamepad buttons free in Bug Farmer, 8-way player facing.
- **Owner's calls (taste/scope):** whether straight halves and quarters ship; whether a build zoom exists; which layer
  governs gameplay; what the base looks like.

## Sources actually read (full page / full paper / full file)

1. W3C, Understanding WCAG 2.2 SC 2.5.8 Target Size (Minimum) — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
2. W3C, Understanding SC 2.5.5 Target Size (Enhanced) — https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html
3. Apple HIG Accessibility (JSON of the page) — https://developer.apple.com/design/human-interface-guidelines/accessibility
4. Android Accessibility Help, touch target size — https://support.google.com/accessibility/android/answer/7101858
5. Microsoft, Targeting (Windows apps) — https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-targeting
6. Xbox Accessibility Guideline 107 (Input) — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
7. Xbox Accessibility Guideline 112 (UI navigation) — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/112
8. Game Accessibility Guidelines: large and well-spaced controls; alternatives to holding buttons — gameaccessibilityguidelines.com
9. Soukoreff & MacKenzie 2004, IJHCS 61 (PDF, 39 pp) — https://www.yorku.ca/mack/ijhcs2004.pdf
10. NN/g, Fitts's Law and Its Applications in UX — https://www.nngroup.com/articles/fitts-law/
11. Callahan, Hopkins, Weiser, Shneiderman, CHI '88 (PDF) — https://www.cs.umd.edu/~ben/papers/Callahan1988empirical.pdf
12. Kurtenbach & Buxton, CHI '94, User learning and performance with marking menus — http://www.billbuxton.com/MMUserLearn.html
13. Kurtenbach & Buxton, INTERCHI '93, The limits of expert performance using hierarchic marking menus — http://www.billbuxton.com/MMExpert.pdf
14. tModLoader source, `TileData.Default.cs` + `Tile.TML.cs` (branch 1.4.5) and docs `struct_tile` — github.com/tModLoader/tModLoader
15. Terraria wiki: Hammers, Controls, Smart Cursor — terraria.wiki.gg
16. Minecraft wiki: Slab, Stairs (raw wikitext) — minecraft.wiki
17. Factorio: Lua API LuaTile; wiki Landfill, Concrete, Ghost, Controls — lua-api.factorio.com, wiki.factorio.com
18. Don't Starve wiki: Turfs — dontstarve.wiki.gg
19. Nookipedia: Island Designer — nookipedia.com; Stardew Valley wiki: Controls — stardewvalleywiki.com
20. Unity Manual: Tilemap Renderer reference; ScriptReference TilemapRenderer.Mode — docs.unity3d.com
21. NN/g: 10 Usability Heuristics; Preventing User Errors (slips) — nngroup.com
(MacKenzie 1992 PDF was fetched but is a scan with no text layer — not used. Pie/Marking menu Wikipedia pages used only
as cross-checks.)
