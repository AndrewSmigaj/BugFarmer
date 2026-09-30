# Shaped-piece placement on a grid: how games and tools do it (research notes)

Research date: 2026-09-29. Written incrementally (one section appended per game/tool as it is finished).
Question: how do well-liked games/tools let players place SHAPED pieces on a grid by hand (full squares,
diagonal halves in 4 rotations, straight halves, quarters) quickly and without confusion; what do players
praise / complain about.

Legend: "DEEP-READ" = I fetched and read the full page. "unsure" = a claim I could not confirm from a source.
For each: (a) shapes; (b) how shape + orientation are chosen; (c) preview/feedback; (d) gamepad/console;
(e) praise/complaints with source; (f) fit for Bug Farmer.

Bug Farmer constraints (from the brief): shovel R key already cycles Dig + each ground type (shown on screen);
mouse wheel = hotbar; "no holds" accessibility setting (every hold -> press); gamepad targets the square in front
of the player; squares can be small on screen (laptop / Steam Deck); a shape is laid ON TOP of the existing ground
(only one material chosen). Ideas on table: (1) point at the part of the square (corner = diagonal, side = half,
quarter = quarter), no rotate step; (2) small painter-style panel: pick a shape, press a key to rotate.

---

> METHOD NOTE (important caveat): the session's WebSearch budget was already used up (200 of 200 calls) before this
> research started, so NO search-engine queries were possible. Every source below was reached by fetching a page
> whose address I already knew (official wikis, manuals, mod pages, forum threads) or by following links inside
> fetched pages. I did not route searches through other sites. "DEEP-READ" means the whole page was fetched: for
> wikis reached through their raw/API text (Sims, Valheim, Fortnite, Space Engineers, Mario, Nookipedia, Steam Workshop)
> and for source code (Tweakeroo/malilib, OpenTTD) I read the text myself; for the other pages the fetch tool read the
> full page and returned quoted extracts to my questions. Coverage of player feedback is therefore narrower
> than a normal search would give; where I could not find a source, the claim is marked "unsure".


## 1. Minecraft (vanilla) + the Tweakeroo mod's "Flexible Block Placement"

Sources (DEEP-READ): Minecraft Wiki "Slab" wikitext (https://minecraft.wiki/w/Slab?action=raw), "Stairs" wikitext
(https://minecraft.wiki/w/Stairs?action=raw), "Controls" wikitext (https://minecraft.wiki/w/Controls?action=raw);
Tweakeroo mod page (https://modrinth.com/mod/tweakeroo) and its SOURCE CODE on GitHub (branch pre-rewrite/fabric/1.20.x:
config/FeatureToggle.java, config/Hotkeys.java, tweaks/PlacementTweaks.java; malilib util/PositionUtils.java and
render/RenderUtils.java) — read directly, so the Tweakeroo facts below are from code, not from a description.

(a) Shapes: full block; slab = top half or bottom half ("Slabs cannot be oriented vertically"); two slabs of the same
    type in one block merge into a double slab; stairs (an L-shape) in 4 facings x upright/upside-down, and stairs
    auto-reshape into inner/outer corners when next to other stairs.
(b) How chosen — vanilla uses TWO implicit signals, never a rotate key:
    - POINTER POSITION inside the face picks the HALF: (paraphrasing the wiki) placing a slab on top of a block, or on the bottom part of a
      block's side, makes a bottom slab. / "Placing a slab on the underside of a block or on
      the top half of the side surface creates a top slab." Stairs: "Pointing at a block bottom or the top half of a
      block side places the stairs upside-down."
    - PLAYER'S BODY FACING picks the ROTATION of stairs: "When placed in-game by a player, this matches the direction
      the player faces." (History: before Alpha 1.2.0 the orientation came from surrounding blocks; changed to player
      facing in Alpha 1.2.0; the "top half of a side" rule for upside-down stairs came in snapshot 12w30a.)
    - NEIGHBOURS pick the corner shape automatically (inner/outer stair corners) — no player input at all.
    Tweakeroo (client mod) adds a POINT-INSIDE-THE-FACE rotation tool: while HOLDING a hotkey (default Left Alt =
    "placing the block with a rotation/facing"; Left Ctrl = "offset or diagonal position"), the targeted face is split
    into 5 zones by malilib's getHitPart(): a CENTRE square (the middle half of the face, |offset| <= 0.25 on both axes)
    and 4 edge zones divided by the face's diagonals (if horizontal offset > vertical offset -> LEFT/RIGHT, else
    TOP/BOTTOM). The zone under the crosshair picks the block's facing. A config option (Java constant Configs.Generic.REMEMBER_FLEXIBLE) keeps the FIRST
    click's mode for the rest of a drag/fast-placement run. There is also a simpler "Accurate Block Placement" (facing
    INTO or OUT OF the clicked face only, with two hotkeys).
(c) Preview/feedback: vanilla shows only the block outline under the crosshair — NO ghost of the result, so which half
    you get is learned, not shown (unsure whether Bedrock differs). Tweakeroo draws an OVERLAY on the targeted face:
    the centre square plus the lines to the corners, and it FILLS the zone the crosshair is in with a highlight colour
    (RenderUtils.renderBlockTargetingOverlay draws quads at +/-0.25 and the hovered HitPart in a highlight colour).
(d) Controller/console: Bedrock places with the Left Trigger; the right stick aims a centre-screen crosshair, so the
    same "which half of the face is the crosshair on" rule applies (inference from the rule + controls page; exact
    console behaviour otherwise unsure). Touch: without split controls you "tap the desired area to place the block";
    with split controls you aim the crosshair and tap anywhere.
(e) Players: Tweakeroo has 7.5M downloads / 2.7K followers on Modrinth and lists flexible + accurate block placement
    among its headline features (the download count covers the whole mod, not just this feature). The mod page warns
    many servers ban these features. Direct player complaints about vanilla stair/slab placement: none fetched ("unsure"
    — searching was not possible; the long-standing "vertical slabs" request is widely known but I did not confirm it).
(f) Fit for Bug Farmer: STRONG precedent for idea (1). Minecraft already proves "which part of the target you point at
    picks the half" is learnable with no rotate key, and Tweakeroo shows the professional version: an on-cell overlay
    that shows the zones and highlights the one under the pointer. Two lessons: (i) without a visible zone overlay the
    rule is invisible (vanilla), so draw the zones; (ii) Tweakeroo's centre-square + diagonal-split geometry is exactly
    a "centre = full square, edge = half" map. The body-facing rule (stairs) maps onto our gamepad case: the square in
    front of the player is chosen by facing, so facing cannot ALSO pick rotation without a second input.


## 2. Terraria (hammer cycles shapes)

Sources (DEEP-READ): Terraria Wiki "Hammers" (https://terraria.wiki.gg/wiki/Hammers), "Smart Cursor"
(https://terraria.wiki.gg/wiki/Smart_Cursor), "Controls" (https://terraria.wiki.gg/wiki/Controls).

(a) Shapes (6): full block; half-block ("approximately the upper half of the tile is air"); floor slope facing right;
    floor slope facing left; ceiling slope facing right; ceiling slope facing left (the 4 diagonal halves). So: full,
    ONE straight half (bottom only), and all 4 diagonal halves. No quarters, no left/right/top halves.
(b) How chosen: a CYCLING TOOL applied AFTER placing. The block is always placed full; you then hit it with a hammer
    and "Each subsequent press advances through the cycle ... The cycle repeats infinitely, so a sloped or half-block
    can be returned to the full-block shape eventually." Order: full -> half -> slope R -> slope L -> ceiling R ->
    ceiling L -> full, BUT "The order of the shapes listed below may vary depending on whether there are other blocks
    surrounding the hammered block" (the wiki gives no detail on how; so the first hit is context-sensitive — details
    unsure). Up to 5 hits to reach a shape; you cannot pick a shape directly in vanilla.
    History: slopes + half-blocks arrived in Desktop 1.2; upside-down (ceiling) slopes in 1.2.3.
(c) Preview/feedback: none before the hit — you see the result after each hit (the result IS the preview). Smart
    Cursor (toggle or hold Left Ctrl, a setting) shows the target tile in "a yellow box"; with a hammer, Smart Cursor
    targets the nearest WALL to remove, not a slope.
(d) Gamepad: right stick aims; on Switch the Pro Controller gives "by-tile movement" of the cursor vs smooth movement;
    use item = RT/ZR; smart cursor = press/hold left stick "(based on Smart Cursor Mode setting)" — i.e. Terraria
    itself already offers the hold-vs-toggle accessibility choice. Hammer shaping is the same repeated-press cycle on
    every platform (the wiki documents no platform differences).
(e) Players: the Smart Cursor page itself warns "Smart Cursor can backfire unexpectedly, especially if the player has
    not realized it is active." Direct complaints about hammer cycling (too many hits, overshooting the wanted slope,
    wanting to pick a shape directly) — "unsure": I could not reach forum threads or the "Hammer Mode" radial-menu mod
    named in the brief without a search engine. (The existence of such mods would itself be evidence of the pain,
    but I have not confirmed it.)
(f) Fit: Terraria is the closest 2D precedent and it shows the cheapest possible control (one button, cycle) works and
    shipped to a huge audience — but it only works because Terraria slopes are placed rarely, one tile at a time, on
    blocks you can SEE large on screen. Painting a diagonal ROAD tile-by-tile with 1-5 hits per tile would be slow and
    you overshoot (no reverse step documented). Lesson for us: a cycle is acceptable as a FALLBACK (gamepad), not as
    the main way to lay many shaped tiles. Also note Terraria's own hold-vs-toggle setting for Smart Cursor, which
    matches our "no holds" rule.


## 3. OpenTTD / Transport Tycoon Deluxe (rail pieces: "Autorail" vs per-direction buttons)

Sources (DEEP-READ): OpenTTD wiki "Railway construction" (https://wiki.openttd.org/en/Manual/Railway%20construction),
"Building tracks" tutorial (https://wiki.openttd.org/en/Manual/Building%20tracks); OpenTTD SOURCE CODE
src/table/autorail.h (the `_autorail_piece` table) and src/viewport.cpp (`GetAutorailHT`), fetched from GitHub master.

(a) Shapes: per tile, a straight track along X or along Y (full-width pieces) or one of FOUR diagonal half-tile pieces
    (upper, lower, left, right corners) — "diagonal tracks ... occupy only half a square - meaning you can put two
    diagonal pieces into one square." This is exactly our "4 diagonal halves" set, on a grid, top-down (isometric).
(b) How chosen — the game ships BOTH approaches side by side, which makes it a natural experiment:
    - Per-direction buttons: "4 directioned track buttons (easy but quite slow)"; pick the direction button, then
      click/drag. (hotkeys 1-4)
    - AUTORAIL (hotkey A or 5): the piece is chosen by WHERE THE POINTER IS INSIDE THE TILE. Code: "Maps each pixel of a
      tile (16x16) to a selection type" — the four 6x6 CORNER regions select the four diagonal half-pieces (HU, VR,
      VL, HL), the central cross-shaped band selects the straight X or Y piece. So: point at a corner -> the diagonal
      that cuts off that corner; point at the middle -> straight. No rotate step. Dragging then extends the line in
      the drag direction, including long diagonals.
(c) Preview: live highlight of the exact piece under the pointer before clicking; while dragging, "white lines
    represent your future tracks"; "You can click in a square and move your mouse in different directions to see how
    new tracks would be placed." Ctrl while dragging removes instead of builds.
(d) Gamepad: none (PC game; the mobile port exists but I did not check it — unsure).
(e) Player/official verdict: the manual itself calls Autorail "A very efficient tool to build tracks in any direction
    (while might be difficult to use at first)" and says the basic per-direction tool is "Not as efficient as Autorail
    tool" / "easy but quite slow". So: the point-inside-the-tile approach is the one the community recommends for speed,
    with an admitted learning curve that the live highlight pays down.
(f) Fit: VERY STRONG precedent for idea (1) "point at the corner = the diagonal that cuts that corner". It is a
    30-year-old, still-played, grid-based design where the corner-region map is proven and the fix for "hard at first"
    is the live piece highlight. It also shows the value of keeping an explicit fallback (the direction buttons) for
    people who find pointing fiddly. Differences from us: TTD tiles are drawn large enough to aim at a 6/16 corner zone
    with a mouse; on a Steam Deck or a small laptop square that zone could be only a few pixels (see the geometry
    notes in the recommendation).


## 4. Super Mario Maker 2 (slopes in a 2D tile editor)

Sources: Super Mario Wiki "Slope" and "Course Maker" wikitext (https://www.mariowiki.com/Slope,
https://www.mariowiki.com/Course_Maker) — DEEP-READ (raw wikitext); "Super Mario Maker 2" article (grepped the parts
table rows for slopes; that article is 260k characters so it was NOT read in full).

(a) Shapes: two slope pieces, Steep (45 degrees, 1:1) and Gentle (2:1), in every style; ground tiles are full squares.
(b) How chosen: slopes are a separate PART picked from the parts menu; the parts menu in SMM2 is "several scroll wheels
    organized into categories instead of rows" (a radial/wheel palette). After placing, "The direction and length of
    the slope can be changed" (the SMM2 parts table). The exact gesture (dragging an end handle; whether the drag
    direction flips the slope) — unsure, the wiki does not say.
(c) Preview: the editor is WYSIWYG — the piece is drawn in place as you place/stretch it (standard for the series;
    specific slope-handle visuals unsure).
(d) Controller: "Touch controls can still be used, but button controls can also be used to place course elements and
    navigate the UI" (docked play). Quality of the docked controls — unsure (the review page I tried was a 404).
(e) Players: no feedback source reached (unsure).
(f) Fit: WEAK for our case. A slope in Mario Maker is a multi-tile ramp that joins terrain automatically, not a
    half-square of paint. Useful ideas only: (i) shape = its own palette entry chosen once, then direction adjusted in
    place; (ii) a wheel-style palette works on a controller. Its drag-to-stretch model is relevant to OUR diagonal
    ROADS: a road is really a line, so "drag a line and the edge tiles become the right diagonals" (see Approach F).


## 5. Factorio (rotate key before placing)

Source (DEEP-READ): Factorio Wiki "Controls" (https://wiki.factorio.com/Controls).

(a) Shapes: buildings/belts have 4 facings (plus mirror); floor TILES (stone path, concrete, landfill) are full squares
    only — no shaped tiles.
(b) How chosen: a ROTATE KEY that works both BEFORE and AFTER placing: R "Rotates the item held in the cursor or the
    selected entity clockwise"; Shift+R "counterclockwise"; H / V flip horizontally / vertically. The chosen rotation
    stays on the cursor for the next placements (standard behaviour; not quoted by the page — unsure). Tile BRUSH SIZE:
    Numpad + / Numpad - "Increases/Decreases the size of the placement area for tiles". Q = pipette (copy what is under
    the cursor into the hand).
(c) Preview: the item in hand is drawn as a ghost at the cursor, already rotated; Shift+click places a construction
    "ghost" plan.
(d) Controller: the Switch version builds with A and ZR+A for ghosts; the page does not list a controller rotate button
    (unsure).
(e) Players: no direct feedback source fetched (unsure). Factorio's controls are widely cited as a model of keyboard
    efficiency, but I did not fetch a source for that claim (unsure).
(f) Fit: the "rotation lives on the thing in hand, is visible in the ghost, and persists until changed" model is the
    right model for idea (2). Two useful extras: reverse-rotate (Shift+R) so you never have to go 3 steps forward, and
    PIPETTE (point at an existing shaped tile and copy its shape+material into the hand) — pipette is the fastest way
    to continue a pattern. For us R is already taken by the ground-type cycle, so a rotate key must be a different key.


## 6. Tile editors: Unity's Tile Palette and Tiled (LDtk not reached)

Sources (DEEP-READ): Unity Manual "Painting on Tilemaps" (https://docs.unity3d.com/2022.3/Documentation/Manual/Tilemap-Painting.html);
Tiled manual "Editing Tile Layers" (https://doc.mapeditor.org/en/stable/manual/editing-tile-layers/). LDtk docs index
fetched but the relevant pages were not reached (unsure).

(a) Shapes: whatever tiles are in the set; rotation/flip turn one drawn tile (e.g. one diagonal half) into all 4
    orientations — the classic way to get 4 diagonal halves from 1 piece of art.
(b) How chosen: PALETTE + ROTATE/FLIP KEYS on the brush, before painting.
    Unity: "[" "Rotate the active Brush clockwise", "]" "anti-clockwise", "Shift+[" / "Shift+]" flip along x / y.
    Tools: Select S, Move M, Paintbrush B, Box Fill U, Picker I, Eraser D, Flood Fill G.
    Tiled: flip X / Y, rotate Z (left) / Shift+Z (right); right mouse button captures a stamp from the map (pipette);
    Random mode; Shape Fill tool (rectangles, ellipses); Terrain Fill mode / Terrain Brush that automatically "match
    edge and corner terrains" — i.e. AUTO-SHAPING from neighbours as an alternative to hand-picking each piece.
(c) Preview: Unity — "a preview of the picked Tile(s) is shown at the cursor location"; Tiled shows the stamp under the
    cursor (standard; not quoted).
(d) Gamepad: not applicable (desktop editors).
(e) Players/users: no feedback source fetched (unsure).
(f) Fit: this is the professional-tool convention for idea (2): the shape lives on the brush, rotate/flip keys
    (a forward AND a reverse key), a preview at the cursor, and a pipette. The part that matters most for us is the
    second model these editors ship — terrain/auto-tile brushes — because for ROADS the player's intent is "a diagonal
    road", not "these 14 triangles". Note Unity's own keys ([ and ]) are what our developer already knows, but players
    won't; they need on-screen prompts.


## 7. Paint / pixel-art tools: Aseprite (MS Paint not reached)

Sources (DEEP-READ): Aseprite docs "Brushes" (https://www.aseprite.org/docs/brushes/), "Keyboard Shortcuts"
(https://www.aseprite.org/docs/keyboard-shortcuts/), "Drawing" (https://www.aseprite.org/docs/drawing/).
MS Paint's shape gallery: not fetched (unsure).

(a) Shapes: three brush TYPES — round (default), square, line — "The square and line types have a context bar option
    that changes the angle, in degrees"; plus CUSTOM brushes made from any selection ("Edit > New Brush" / Ctrl+B).
    Brush settings (type, size, angle, colours, ink, opacity, pixel-perfect) can be SAVED as named brush presets.
(b) How chosen: a small PANEL (the brush-type popup on the context bar, a strip above the canvas) — pick once, it stays
    until changed. Tool keys use a CYCLING convention: "Two or more tools can share the same key. In this case pressing
    the key multiple times will switch/go through all the tools that have the same key assigned" (e.g. U cycles
    Rectangle / Filled Rectangle). Hold-to-use QUICK tools: Alt = eyedropper while held; Space = hand while held.
    Selection rotation snaps with Shift.
(c) Preview: the current brush's outline is drawn under the cursor (standard Aseprite behaviour; the docs pages I read
    did not describe it — unsure).
(d) Gamepad: n/a.
(e) Users: no feedback source fetched (unsure).
(f) Fit: this is the literal model for idea (2) — a compact shape strip that stays selected, plus a cycling key. Two
    transferable conventions: (i) "same key pressed again steps to the next item in the group" (we already do this
    with R for ground types — so a SECOND cycling key for shape is consistent with our own UI); (ii) Aseprite's
    hold-to-use quick tools would conflict with our "no holds" setting and need a press-to-toggle twin.


## 8. Animal Crossing: New Horizons (paths, cliffs, rivers — one tile in front, auto corners)

Source (DEEP-READ): Nookipedia "Island Designer Construction Permit" wikitext
(https://nookipedia.com/w/index.php?title=Island_Designer_Construction_Permit&action=raw).

(a) Shapes: paths are full tiles whose visible corners/edges are drawn automatically; cliffs and rivers have
    diagonal/rounded corner states.
(b) How chosen: TARGET = the tile in front of the player (press A); SHAPE = mostly AUTOMATIC from neighbours ("Paths can
    also be rounded if the path is on the edge of a perpendicular pathway"), plus "HIT IT AGAIN TO ROUND IT" for
    corners: "The player can round out a cliff by hitting its edge"; "round out a river by hitting the land where two
    waterways collide". Tool guide text: "Press A to create cliffs, round the edges of existing cliffs, or destroy
    existing cliffs." Whether path corners can also be toggled by hand (e.g. facing a corner diagonally) — unsure; the
    page only says paths "can be rounded".
    Material picked from an app menu, then placing: "the player will wipe the ground and immediately place down a path"
    — i.e. one material chosen, laid over what was there (like our ground-on-top rule).
(c) Preview: the target tile is marked in front of the player (standard; not quoted — unsure). Result appears at once.
(d) Console-only (Switch); everything is "face a tile, press A". No pointer, no rotate.
(e) Players: terraforming being slow/tedious one tile at a time is a widely repeated complaint, but I could not fetch a
    source for it (unsure).
(f) Fit: ACNH is the gamepad precedent for our "square in front of the player" mode. Its answer to shapes on a
    controller is NOT a rotate key: it is (1) automatic corner shaping from neighbours and (2) "act on the same edge
    again to change its corner". For a controller player laying a diagonal road, auto-shaping is far faster than
    choosing each triangle's rotation by hand.


## 9. Valheim (+ the Gizmo rotation mod)

Sources (DEEP-READ): Valheim Wiki "Building" and "Controls" wikitext via the Fandom API
(https://valheim.fandom.com/wiki/Building, https://valheim.fandom.com/wiki/Controls); Gizmo mod page on Thunderstore
(https://thunderstore.io/c/valheim/p/ComfyMods/Gizmo/).

(a) Shapes: 3D build pieces incl. 26/45-degree roof and wedge pieces; rotation around the vertical axis only in vanilla.
(b) How chosen: piece from a build menu; ROTATION on the MOUSE WHEEL ("Scroll the mouse to rotate the Building
    Blocks"); SNAP to neighbouring pieces is automatic ("Most building components can snap to each other"), disabled
    while holding Shift (controller: LT+LB); PIPETTE: "Hold [Shift] then [Middle Mouse Button] to select Building
    Blocks you are looking at."
(c) Preview: a ghost of the piece at the aim point, green/red for valid/invalid (standard; not quoted — unsure).
(d) Controller: snap toggle = Left Bumper per the Controls table; the rotate binding on controller is not in the table
    (unsure).
(e) Players: the Gizmo mod — "Configurable modifier hot-keys" to rotate around the other axes, snap angles
    "Configurable from 2-256 divisions per 180 degrees" — has 295.8K downloads on Thunderstore: evidence that players
    want finer/extra rotation control than vanilla gives, and accept modifier keys to get it.
(f) Fit: LOW for the mechanism (3D; our wheel is the hotbar; our shapes are only 4 rotations). Transferable: snap-to-
    neighbour defaults do most of the work, plus a pipette to copy an existing piece.


## 10. Fortnite (edit grid on each build piece, and the newer "Simple Edit")

Sources (DEEP-READ): Fortnite Wiki "Building" wikitext via the Fandom API (https://fortnite.fandom.com/wiki/Building);
"Update v33.00" wikitext, which reproduces Epic's patch notes (https://fortnite.fandom.com/wiki/Update_v33.00).

(a) Shapes: four base pieces (wall, floor, stair, pyramid); each is EDITED into sub-shapes — "Walls and Floors have a
    3x3 grid which allows for the removal or inclusion of various shapes"; "Stairs have a specific direction based
    grid"; "Pyramids can have each corner raised in a 2x2 grid". Corner/triangle and half shapes come from which
    sub-cells you keep.
(b) How chosen — two systems:
    - Classic edit: enter edit mode, PAINT the sub-cells of the piece's grid with the pointer/crosshair (drag across
      them), confirm. Fully free, skill-heavy.
    - SIMPLE EDIT (v33.00, Chapter 6 Season 1): "allows for editing builds with a single button press. The resulting
      edit is based on the part of the building you're looking at rather than being painted manually — it
      automatically executes building edits immediately, removing the step of selecting tiles altogether." Epic:
      "it should also prove helpful for players who are new to building ... Simple Edit allows for a smaller subset of
      edits to choose from, and masters of the current edit system will have more edit options available."
      (A "Simple Build" setting followed in v39.00.)
(c) Preview: in classic edit the selected sub-cells are highlighted on the piece before confirming (the grid is shown
    on the piece — wiki image caption "The 3x3 grid for editing Walls or Floors").
(d) Controller: an "Edit Mode Aim Assist" existed and was "Previously auto-enabled for controller users", later made a
    toggle — i.e. Epic had to add aim help for picking sub-cells with a stick.
(e) Player/developer evidence: Epic's own notes present "point at the part you want, one press, no tile selection"
    as the easier path for new players, kept alongside the full grid editor for experts. (Direct player reception of
    Simple Edit — unsure; not fetched.)
(f) Fit: STRONG. This is the most direct modern precedent for idea (1): a big studio shipped "the part of the piece you
    are looking at decides the shape, one press" specifically to make shaped editing accessible, and kept a richer
    manual mode for experts. It also shows the controller cost: sub-part aiming on a stick needed aim assist.


## 11. Don't Starve Together — the "Geometric Placement" mod (player-feedback source: subscriber numbers)

Source (DEEP-READ): Steam Workshop page (https://steamcommunity.com/sharedfiles/filedetails/?id=351325790), full
description + stats.

Numbers: 7,515,884 current subscribers; 7,151,608 unique visitors; 236,632 favourites; 50,208 ratings. It is one of
the most-subscribed placement mods on Steam — strong evidence that players of a top-down grid game care intensely about
placement precision and a visible grid.
(a) Shapes: not about shapes — about WHERE things go on/inside the tile grid (turf tiles, walls, sub-tile points).
(b) How chosen: "Snaps objects to a grid when placing and displays a build grid around it (unless you hold ctrl)"; a
    "Snap Grid Button" moves the grid to "key points of a tile (center, edge, corner; technically a 5x5 grid of points
    within a tile)" — i.e. named SUB-TILE POINTS (centre / edge / corner) are the vocabulary players use. A "Toggle
    Button" (V) flips between the most recently used geometries.
(c) Preview/feedback — the heart of the mod: a grid of candidate points coloured for "can place" vs "can't place",
    with colour-scheme options Red/Green, Red/Blue, Black/White ("A bit easier to see at night") and the default
    "Outlined" ("black-with-white-outline and white-with-black-outline for the best visibility"). "Hide Cursor Item" can
    hide the held object "so it doesn't cover up the grid". A setting makes "CTRL" either show or hide the grid (a
    hold, with the inverse as a toggle-by-default).
(d) Controller: "Controller Offset — On uses the normal offset, which rotates with the player. Off (default) keeps the
    object at the player's feet, making it easier to place it right where you want to." — i.e. the mod's author made
    the DEFAULT for controller players "place at a predictable spot", because the vanilla facing-based offset was
    imprecise. Options menu on controller via left-stick click on the scoreboard.
(e) Players: the subscriber count is the praise; the mod exists because vanilla placement gave no grid and no
    valid/invalid preview.
(f) Fit: HIGH for the FEEDBACK layer, whatever input we choose: (i) show the sub-cell zones on the targeted square;
    (ii) make the overlay high-contrast with an outline style that reads on any ground and at night (our grounds are
    dirt/grass/sand/stone/wood — very different brightness); (iii) do not let the held-item ghost hide the grid;
    (iv) on controller, a predictable target beats a clever one.


## 12. The Sims series (floor tool: full / quarter / triangle)

Sources (DEEP-READ): The Sims Wiki "Floor" and "Build mode" wikitext via the Fandom API (https://sims.fandom.com/wiki/Floor,
https://sims.fandom.com/wiki/Build_mode), "Build mode (The Sims 4)" (https://sims.fandom.com/wiki/Build_mode_(The_Sims_4)).
The Sims 4's floor-tool mode buttons are NOT described on any page I could reach (Carl's guide and EA help were blocked or
timed out; no search engine) — so the Sims 4 specifics below are marked unsure.

(a) Shapes: full floor tile; quarter tiles; triangular (diagonal-half) tiles; each tile can hold two different
    triangles (a second tile can be added in the remaining part of the same grid tile, paraphrased). Floors are laid over terrain.
(b) How chosen (confirmed for The Sims 2 and 3):
    - The Sims 2: "Floor tiles can be rotated with the use of the , and . keys, and the rotation can be applied to all
      consecutive tiles by pressing Shift." Diagonal floor could also be made by building a diagonal wall first and
      flooring one side of it.
    - The Sims 3: "triangular title [sic] placement can be simplified by pressing CTRL + F to change the current tile to a
      triangular shape", and optionally a second tile can fill the remaining part of the same grid tile (paraphrased) — i.e. a
      MODIFIER KEY switches the brush to triangle mode, and the triangle drawn depends on the part of the tile under the
      cursor (the "which side" part is my reading of that sentence — unsure).
    - Series-wide floor modifiers: Shift+drag "will place flooring in the selected area"; Shift in a closed room fills
      the whole room; Ctrl removes a single floor tile; Ctrl+Shift removes all of that flooring in the room.
    - The Sims 4 (unsure, from memory, not sourced): after picking a floor pattern, the panel offers placement-mode
      buttons Full Tile / Quarter Tile / Triangle; in quarter or triangle mode the sub-part under the cursor is filled.
      Sims 4 has an Eyedropper (E): "Clicking on a wall or floor covering will switch to the appropriate area of build mode
      and select that covering so it can be applied" (sourced).
(c) Preview: object placement shows a green/red footprint and marks the object's front (TS2/TS3, sourced); for floors the
    painted tile preview under the cursor is standard (unsure).
(d) Console: The Sims 4 on PS4/Xbox One exists; how its controller picks quarter/triangle floor parts — unsure.
(e) Players: could not reach forum threads (unsure). The fact that each generation added a faster or more explicit way
    to get triangles (TS2 build-a-diagonal-wall workaround -> TS3 Ctrl+F -> TS4 dedicated mode buttons, the last unsure)
    suggests triangle floors were a persistent request.
(f) Fit: the Sims is the closest match in PURPOSE (painting floor patterns including quarters and triangles over the
    ground). Its lessons: a mode switch (panel button or modifier) chooses the SIZE CLASS (full / quarter / triangle),
    and the pointer position inside the tile chooses WHICH part — a hybrid of our ideas (2) and (1). Plus: a drag-to-fill
    area, fill-the-room, and an eyedropper. Two triangles of different materials in one square is allowed in the Sims;
    for us that corresponds to "lay a triangle over existing ground" (the other half is whatever was there).


## 13. Space Engineers (six rotate keys) and Satisfactory (build-mode wheel on R) — short entries

Sources (DEEP-READ): Space Engineers Wiki "Key Bindings" + "Building" wikitext via the Fandom API
(https://spaceengineers.fandom.com/wiki/Controls, https://spaceengineers.fandom.com/wiki/Building);
Satisfactory Wiki "Controls" (https://satisfactory.wiki.gg/wiki/Controls).

Space Engineers:
(a) Blocks incl. slopes, corners, half blocks, in all 24 orientations of a cube.
(b) SIX dedicated rotate keys on the block preview: Page Down / Delete (vertical axis +/-), Home / End (horizontal axis
    +/-), Insert / Page Up (depth axis +/-); B toggles free vs gravity-aligned placement; N/M symmetry mode.
(c) The game ships a HUD diagram just to explain the six rotations ("Nodding your head up/down (green), shaking your head
    left/right (red), tilting your head left/right (blue)") — the need for a diagram is itself the lesson.
(d) Separate Xbox/PlayStation control pages exist (not read — unsure).
(e) Player complaints about the six-key rotation cluster are widely known but NOT sourced here (unsure).
(f) Fit: a cautionary example. Explicit per-axis rotate keys scale badly and need teaching; with only 4 rotations of a
    flat triangle we must not need anything like this.

Satisfactory:
(b) Rotation on the MOUSE WHEEL ("Scroll Up rotates right ... Down rotates left", Ctrl for finer foundation steps); R =
    "Change Build Mode", which opens a SELECTION WHEEL of modes (the fetched page did not list the mode names; "zoop" =
    lay a whole line of foundations in one drag is from general knowledge — unsure); Snap toggle Ctrl / RB tap; Hologram lock H / long-press RT;
    Nudge with arrow keys; SAMPLE (middle click / X or Square) copies an existing structure "with settings" (pipette).
(d) Controller: "Hold right/left on D-pad to rotate"; long-press RT/R2 = hologram lock; D-pad nudges while locked.
(f) Fit: MEDIUM. Two transferable ideas: (i) a mode key that opens a small wheel (radial) is Satisfactory's answer
    for many modes on one key — relevant if our shape set grows; (ii) "zoop" = drag a line to lay many pieces at once,
    the analogue for laying a diagonal road in one gesture. Its D-pad-left/right rotate is a clean controller mapping.
    (Satisfactory uses HOLD for rotate on the D-pad and long-press for lock — both need press-to-toggle twins under our
    "no holds" rule.)


## 14. RimWorld (baseline: floors are full tiles over kept terrain) — short entry

Source (DEEP-READ): RimWorld Wiki "Floors" (https://rimworldwiki.com/wiki/Floors).
(a) Full tiles only (the page lists no partial shapes; that there are none at all is from general knowledge — unsure).
(b)/(c) Placement mechanics are not described on that page (drag-a-rectangle designation is standard RimWorld — unsure).
Relevant confirmed rule: "After floors are removed, the tile will retain its old terrain type" and "Floors do not prevent
other constructions to be built on top of them" — floor is a LAYER over the terrain, like our "shape laid on top of the
existing ground".
(f) Fit: a reminder that many acclaimed colony/farm games ship NO shaped floors; shaped ground is a differentiator for
us, not table stakes — worth doing well, but it must not slow down the common case (laying full squares).

## Not reached / skipped (and why)
- Dragon Quest Builders 2, Enshrouded, Core Keeper, Palia, Dinkum, Starbound, Planet Zoo, LDtk, MS Paint: not researched
  in depth — no search engine, and their wiki pages either lacked control details (Enshrouded "Building" page) or I did
  not have a reliable address. Any claim about them would be "unsure", so none is made.
- Terraria "Hammer Mode" radial-menu mod named in the brief: could not locate without search (unsure it exists as named).
- Forum/Reddit threads about Sims 4 triangles and Terraria slope-cycling: not reachable without search (unsure).


---
# SUMMARY TABLE (one row per game/tool)

| # | Game / tool | Shapes | How the SHAPE is chosen | How the ORIENTATION is chosen | Preview | Gamepad / console | Player evidence | Fit for us |
|---|---|---|---|---|---|---|---|---|
| 1 | Minecraft (vanilla) | full, top/bottom slab, stairs (4 facings x up/down) | separate item per shape | slab half + upside-down stairs: WHICH HALF OF THE FACE you point at; stair facing: player's body facing; corners: automatic from neighbours | outline only — no ghost (rule is invisible) | same crosshair rule; LT places | none fetched (unsure) | half-by-pointer = proof idea (1) is learnable; lack of preview = what to avoid |
| 1b | Tweakeroo mod (Minecraft) | any block facing | — | point at a ZONE of the face: centre square (middle half) or one of 4 edge zones split by the diagonals; activated by HOLDING Alt/Ctrl; first click's mode kept for a drag | overlay drawn on the face, hovered zone highlighted | n/a | 7.5M downloads (Modrinth) | closest mechanism to idea (1), incl. the overlay |
| 2 | Terraria | full, bottom half, 4 diagonal slopes | hammer hits after placing | fixed cycle, 1-5 hits; order "may vary depending on ... surrounding blocks" | none before the hit | same repeated press; Smart Cursor hold/toggle setting | wiki: Smart Cursor "can backfire unexpectedly" | cycle OK as fallback, too slow as main tool |
| 3 | OpenTTD / TTD | straight X/Y + 4 diagonal half-tile pieces | Autorail tool, or one button per direction | Autorail: POINTER REGION inside the tile (16x16 map: 4 corner regions -> 4 diagonals, middle band -> straights); drag extends | live highlight of the piece; white lines while dragging | none (PC) | manual: Autorail "very efficient ... might be difficult to use at first"; buttons "easy but quite slow" | STRONG precedent for "corner = diagonal" |
| 4 | Super Mario Maker 2 | steep + gentle slopes | parts from category "scroll wheels" | direction + length changed after placing (gesture unsure) | WYSIWYG | button controls when docked | none fetched | weak (slopes are ramps); wheel palette idea |
| 5 | Factorio | 4 facings + mirror (tiles full only) | item in hand | R / Shift+R rotate item in hand OR hovered entity; H/V flip; tile brush size Numpad +/- | rotated ghost at cursor | Switch: A builds (rotate button unsure) | none fetched | the rotate-key model done right (+ reverse, + pipette Q) |
| 6 | Unity Tile Palette / Tiled | any tile; rotate/flip make 4 diagonals from 1 | palette | Unity [ ] rotate, Shift+[ ] flip; Tiled Z/Shift+Z rotate, X/Y flip; Tiled terrain brush auto-picks edge/corner tiles | tile preview at cursor | n/a | none fetched | tool convention for idea (2); auto-terrain brush for roads |
| 7 | Aseprite | round / square / line brush (+angle), custom brushes | small brush-type panel; saved presets; same key pressed again cycles a tool group | angle field | brush outline (unsure) | n/a | none fetched | panel + cycling-key convention; hold-to-use quick tools clash with "no holds" |
| 8 | Animal Crossing NH | paths with auto corners; cliff/river rounded corners | app menu picks material | automatic from neighbours; "round out a cliff by hitting its edge" (act again on the edge) | tile in front | Switch only: face a tile, press A | complaints about slowness widely known, not sourced | gamepad precedent: auto-shape + "act again to change the corner" |
| 9 | Valheim (+Gizmo) | 3D pieces incl. wedges | build menu | MOUSE WHEEL rotates; snap to neighbours automatic; Shift+MMB copies a piece | ghost (unsure) | snap toggle LB | Gizmo rotation mod: 295.8K downloads | low (wheel is our hotbar); pipette + snap ideas |
| 10 | Fortnite | 4 base pieces edited on 3x3 / 2x2 sub-grids | edit mode | classic: paint sub-cells; SIMPLE EDIT (2024): "based on the part of the building you're looking at ... one button press ... removing the step of selecting tiles" | sub-grid highlight | "Edit Mode Aim Assist" was auto-on for controllers | Epic: Simple Edit "helpful for players who are new to building" | STRONG: modern big-studio version of idea (1) |
| 11 | Don't Starve Together — Geometric Placement mod | (placement points, not shapes) | — | snaps to sub-tile key points "center, edge, corner" | grid coloured can/can't place; "Outlined" high-contrast default; option to hide the held item | default puts objects at the player's feet instead of a facing-based offset "making it easier to place it right where you want to" | 7,515,884 subscribers, 50,208 ratings | HIGH for the preview/overlay design |
| 12 | The Sims 2 / 3 / 4 | full, quarter, triangle (two triangles per tile) | TS3: Ctrl+F switches to triangle; TS4: Full/Quarter/Triangle mode buttons (unsure) | TS2: , and . keys rotate floor tiles; TS3/TS4: part of the tile under the cursor (partly unsure) | painted preview (unsure) | TS4 console exists (method unsure) | not reached (unsure) | closest in PURPOSE: mode picks the size class, pointer picks the part |
| 13 | Space Engineers | 24 cube orientations, slopes, corners | toolbar block | SIX keys: PgDn/Del, Home/End, Ins/PgUp (one pair per axis) | HUD rotation diagram needed | separate pages (unsure) | complaints not sourced | cautionary: too many rotate keys |
| 13b | Satisfactory | 3D buildings | build menu; R opens a build-mode WHEEL | mouse wheel rotates (Ctrl finer) | hologram, lockable (H / long-press RT) | D-pad left/right rotate | none fetched | radial for modes; "zoop" line-laying (unsure) |
| 14 | RimWorld | full floors only | architect menu | — | — | — | — | baseline: floors are a layer over kept terrain |

# THE DISTINCT APPROACHES (7), with pros, cons and who uses them

A. POINT AT THE PART (the zone of the cell under the pointer decides the shape/orientation; no rotate step)
   Used by: OpenTTD Autorail (corner regions -> diagonal pieces), Minecraft vanilla (upper/lower half of a face),
   Tweakeroo (centre + 4 edge zones), Fortnite Simple Edit (part you look at, one press), The Sims triangle/quarter
   (partly unsure), Don't Starve Geometric Placement (centre/edge/corner points).
   + Fastest: one action per square, no rotation state to remember or forget; "paint goes where you point".
   + Recommended by the people who know the tools best (OpenTTD manual: "very efficient"); Epic chose it as the EASY mode.
   - A learning curve ("difficult to use at first") that only a live preview pays down; with no overlay the rule is
     invisible (Minecraft vanilla).
   - Needs aim: zones shrink with the square. And one zone map cannot hold every shape: a CORNER could mean "diagonal
     half" OR "quarter" — they are both anchored on a corner — so a single map for 13 shapes needs tiny nested zones.
   - No pointer on a gamepad (Fortnite had to add aim assist for sub-part aiming on a stick).
   - Pointer wobble during a multi-square stroke flips shapes (Tweakeroo's answer: keep the first square's choice).

B. ROTATE KEY ON THE BRUSH (orientation is a setting on the thing in hand; persists; visible in the ghost)
   Used by: Factorio (R / Shift+R, H / V flip), Unity Tile Palette ([ ] and Shift+[ ]), Tiled (Z / Shift+Z, X / Y),
   The Sims 2 (, and . keys; Shift applies to consecutive tiles), Satisfactory on controller (D-pad), Space Engineers.
   + Independent of aim and square size; identical on keyboard and gamepad; a row of identical pieces needs no extra
     presses because the rotation persists.
   - Extra presses, and the player must predict which way it turns (needs reverse key + ghost); needs a free key (our R
     and wheel are taken); explodes with more axes (Space Engineers needs a diagram for six keys).

C. CYCLE ON THE PLACED TILE (place full, then hit it to step through shapes)
   Used by: Terraria hammer; ACNH cliffs/rivers ("round out a cliff by hitting its edge").
   + One button, no UI, discoverable, works on any controller.
   - Slow for many tiles (up to 5 hits in Terraria), overshoot with no reverse, and the order is context-dependent
     ("may vary depending on ... surrounding blocks"); no preview before the hit.

D. PALETTE / PANEL / WHEEL OF EXPLICIT SHAPES
   Used by: OpenTTD per-direction buttons, Aseprite brush-type strip + saved brushes, Mario Maker 2 part wheels,
   Satisfactory build-mode wheel, The Sims 4 mode buttons (unsure).
   + Discoverable, state always visible, easy with a mouse click; wheels suit controllers.
   - Every change is a trip to the panel: OpenTTD's own manual calls the per-direction buttons "easy but quite slow";
     radial wheels are usually hold-to-open (needs a press-to-open twin for "no holds").

E. AUTOMATIC SHAPE FROM NEIGHBOURS
   Used by: Minecraft stair corners, ACNH path rounding, Tiled terrain brush, Valheim snapping, Terraria's first hit.
   + Zero input; great for the common patterns (road edges, rounded corners); ideal on gamepad.
   - Takes control away (the owner wants checkerboards and free patterns); surprises ("Smart Cursor can backfire
     unexpectedly"); needs a manual override.

F. DRAG A LINE OR AREA, THE TOOL FILLS IT
   Used by: OpenTTD Autorail drag (long diagonals), The Sims Shift-drag / fill room, Tiled shape fill, Factorio tile
   brush size, Satisfactory "zoop" (unsure).
   + Enormous speed for roads and fields; a diagonal road becomes one gesture.
   - Drags are holds (need click-start / click-end under "no holds"); needs a preview of the whole stroke.

G. BODY FACING DECIDES
   Used by: Minecraft stairs; Don't Starve's vanilla controller offset "rotates with the player".
   + No extra input.
   - Clashes with gamepad targeting (facing already picks the square in front); only 4 (or 8) directions; the most
     popular DST placement mod made the non-facing option the DEFAULT because facing was imprecise.

Supporting feature seen almost everywhere: a PIPETTE / sample key that copies what is under the pointer into the hand
(Factorio Q, Tiled right-click, Sims eyedropper E, Valheim Shift+middle-click, Satisfactory sample, Unity picker I).

# RECOMMENDATION FOR BUG FARMER

Build a HYBRID of the two ideas on the table: "pick the kind of shape, then point at where it goes".

1. SHAPE KIND is a second visible setting on the shovel, shown next to the ground type: Full / Diagonal half /
   Straight half / Quarter. It is changed by ONE key that cycles (pressing again steps on; Shift steps back) — the same
   convention as our R key and Aseprite's "press again to go through the group" — and it can also be clicked on screen
   (that on-screen strip is the "small painter-style panel"). Full stays the default, so laying ordinary ground does not
   change at all. Why a kind setting at all: a corner can mean a diagonal half OR a quarter, so pointing alone cannot
   tell them apart without tiny nested targets (the Sims solves exactly this with mode buttons plus the pointer).

2. WITH A MOUSE, THE POINTER PICKS THE ORIENTATION — no rotate step. Rule, the same for every kind: "the new ground
   covers the part of the square you are pointing at".
   - Diagonal half: the square is cut into 4 quadrants; pointing in the north-east quadrant lays the triangle that fills
     the north-east corner.
   - Straight half: the square is cut by its two diagonals into 4 triangles; pointing near the north side lays the north
     half.
   - Quarter: 4 quadrants; pointing in one lays that quarter.
   Each kind only needs 4 zones, so every target is HALF the square — about twice the size of a 3x3 map's zones and far
   bigger than OpenTTD's corner regions. (Arithmetic, not a source: on a square drawn 24 pixels wide, a 4-zone target is
   about 12 px; a 3x3 zone map gives 8 px; a map with nested corner zones for quarters gives about 6 px.) This follows
   OpenTTD Autorail (efficient, the expert choice), Fortnite Simple Edit (look at the part, one press — Epic's choice for
   new players), Minecraft (half by pointer) and the Sims (part under the cursor).

3. ALWAYS SHOW THE RESULT BEFORE IT HAPPENS: a ghost of the exact shape in the chosen ground on the targeted square, plus a
   faint outline of that kind's 4 zones with the active one highlighted (Tweakeroo's face overlay). Use a high-contrast
   outlined style that reads on dirt, grass, sand, stone, wood and at night (Geometric Placement's default "Outlined"
   scheme, chosen "for the best visibility"). The cursor or held item must not cover the square. This is what turns
   OpenTTD's "difficult at first" into "obvious", and what vanilla Minecraft lacks.

4. STROKES: when one press-and-drag (or, with "no holds", click-start / click-end) lays several squares, keep the
   orientation chosen on the first square for the whole stroke (Tweakeroo's REMEMBER_FLEXIBLE option), so pointer wobble
   cannot flip triangles halfway along a row.

5. GAMEPAD (square in front of the player): there is no pointer, so use a ROTATE button: each press turns the shape a
   quarter turn, the ghost shows it, and the rotation STAYS for the next squares (Factorio model) so a row of the same
   triangle needs no extra presses. A second button (or Shift equivalent) turns the other way. The kind cycles on its
   own button, mirroring the keyboard key. Do NOT use the player's facing for orientation (facing already chooses the
   square; Don't Starve's top placement mod had to switch facing-based placement off by default). Everything is a
   press, never a hold. The same rotate key should exist on keyboard as an accessibility option ("rotate with a key
   instead of the pointer") for trackpads and unsteady hands.

6. PIPETTE: one key copies ground + kind + orientation from the square under the pointer (or in front) into the shovel —
   every serious building tool has it, and it is the fastest way to continue a checkerboard or a diagonal edge.

7. LATER, NOT NOW: a road/line tool that lays a whole diagonal road in one stroke and puts the right triangles on both
   edges automatically (OpenTTD drag, Tiled terrain brush, Satisfactory "zoop"). It is an accelerator on top of manual
   freedom, never a replacement for it.

WHAT TO AVOID (each seen to hurt elsewhere): Terraria-style "hit it again to cycle" as the main method (slow, overshoot,
unpredictable order); hidden rules with no overlay (vanilla Minecraft); held modifier keys to switch modes (Tweakeroo's
Alt/Ctrl, the Sims' Shift/Ctrl) because of "no holds"; mouse-wheel rotation (Valheim, Satisfactory) because the wheel is
the hotbar; many rotate keys (Space Engineers); orientation from body facing on gamepad.

OPEN QUESTIONS for the owner / playtest (taste, not research-answerable): (i) whether "straight half" and "quarter" are
wanted at launch or only full + diagonal (Terraria and OpenTTD both ship without quarters); (ii) which free key becomes
the shape-kind key (R is taken; key map not checked — unsure which keys are free); (iii) whether the diagonal zone rule
should be "fills the corner you point at" (recommended, matches the paint metaphor) or "cuts off the corner you point at"
(OpenTTD's track reading) — the preview makes either learnable, but it must be one rule for all kinds.

Confidence: high that pointer + preview + a kind setting is the best-supported combination (4 independent precedents
for pointing: OpenTTD, Minecraft, Tweakeroo, Fortnite; 3 for rotate keys as the no-pointer fallback: Factorio, Unity,
Tiled). Weak spot: direct player-forum feedback on shape placement could not be gathered (no search available) — the
player evidence here is download/subscriber counts of placement mods (Tweakeroo 7.5M, Geometric Placement 7.5M
subscribers, Gizmo 295.8K) plus developer and community-manual verdicts (Epic's Simple Edit notes, OpenTTD manual).
