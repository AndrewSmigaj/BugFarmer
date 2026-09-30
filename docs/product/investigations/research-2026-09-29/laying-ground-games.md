# How games let players lay ground on a grid and still get nice shapes

Research for Bug Farmer (2026-09-29). Question: players lay ground (dirt, grass, sand, mud, stone path,
wooden floor) one grid square at a time with a shovel (R cycles Dig / each ground kind). The owner wants
diagonal edges (roads look better) but worries a shape-picking system would confuse players.

Method: web search + deep reads of wiki pages, developer posts, guides and player threads. Every claim
not confirmed from a source is marked "unsure". Findings are appended game by game as they are finished.

Legend for (a) "what the player controls":
- SQUARES = player places whole squares only, nothing else
- SHAPE-ITEM = the shape is a separate item/block (slab, stair, triangle tile)
- RESHAPE-TOOL = a tool changes an already-placed square's shape afterwards
- AUTO = the game draws corners/edges by itself from the neighbours

---

## 1. Animal Crossing: New Horizons (Nintendo, 2020)

Sources deep-read:
- Nintendo Life guide, "Diagonal Rivers And Cliffs - How To Build Bridges At An Angle"
  https://www.nintendolife.com/guides/animal-crossing-new-horizons-diagonal-rivers-and-cliffs-how-to-build-bridges-at-an-angle
- Game8, "How to Create Paths Guide" https://game8.co/games/Animal-Crossing-New-Horizons/archives/290278
- Nookipedia, "Island Designer" https://nookipedia.com/wiki/Island_Designer
- TheGamer, "You Can Wrap Paths With Custom Designs Using This Simple Trick"
  https://www.thegamer.com/animal-crossing-new-horizons-wrap-paths-custom-designs-simple-trick/
- Player thread (Bell Tree forums), "How can I make rounded edge paths?"
  https://www.belltreeforums.com/threads/how-can-i-make-rounded-edge-paths.507616/
- (GameFAQs board thread "Why can't I make a rounded path with a custom design?" returned 403 - not read.)

(a) What the player controls: SQUARES + RESHAPE-TOOL, with the reshape done by the SAME button and the
SAME tool. You lay a whole square ("press A on the ground to construct one path tile", Game8). Then you
press A on an already-laid tile to round its edge: "To round path edges, press A on the tile to round the
edge. To do so, there must be an adjacent tile of the same path type" (Game8). A lone square cannot be
rounded ("You must have at least two path squares together", Bell Tree, user tolisamarie). Rivers and
cliffs work the same way: there is "no 'diagonal cut tool'"; you first build a stepped, jagged edge, then
"work your way along the steps and press 'A' to cut each one off at a 45° angle"; "the pointed edge is
carved into a smooth diagonal line" (Nintendo Life). The game refuses some shapes: it "won't allow you to
have two opposing diagonals next to each other" (Nintendo Life).
Which exact corner gets rounded, and whether a further A-press removes the tile or cycles to another
shape: unsure (Game8 says removal is "Press A using the same path permit"; the exact cycle order is not
stated in any source I read).

(b) How the good look is achieved: the game draws it. "Tiles of the same path will automatically merge,
while paths of different types will have little space between them" (Game8) - i.e. same-material
neighbours join seamlessly with no seams; different materials are kept apart by a grass gap (so the game
never has to draw a stone-to-brick transition). In every source I read, one press gives one result (paths:
a rounded edge; rivers and cliffs: a 45-degree cut) - the player chooses WHERE, not from a list of shapes.
Whether further presses cycle through other shapes: unsure (see above).
Custom-design paths (player-drawn 32x32 patterns) CANNOT be rounded ("you cannot round the edges of Custom
Design paths", Game8). Players worked around it by drawing separate corner and curve designs, which "can
take up a large number of save slots", until Reddit found that a design with one transparent pixel laid
over a built-in path "wraps" to that path's rounded shape (TheGamer).

(c) Controls and interface: Island Designer app; "+" opens a menu of path types (Nookipedia, Game8);
A places, A on an existing tile rounds, A with the same path again (or the Grass option) removes (Game8,
Nookipedia). Facing matters for rivers/cliffs (face the water/cliff). There is no separate undo and no
shape menu. Holding L faces the nearest cardinal direction, and holding L while moving keeps your facing
(Nookipedia) - a tool mainly for lining up these edits.

(d) Player feedback:
- Bell Tree thread: the OP's confusion was simply not knowing the feature existed ("Whenever I push A, I
  always put down a square path") - the rounding is hidden (no on-screen hint), but once told, it is a
  one-line answer and the player was happy. No one in the thread found the rule itself confusing.
- Custom paths not rounding was a real, widespread complaint (TheGamer; the GameFAQs thread title "Why
  can't I make a rounded path with a custom design?"); the community had to find a trick.
- The Nintendo Life guide frames the diagonal-cut as needing to be learned ("it's easy when you know how")
  but a single rule.

(e) Fit for Bug Farmer: VERY GOOD model for the control side. It is the closest match to our need: the
player only ever lays squares with the one tool they already hold, and "hit an existing corner again to
cut it" adds shapes without any new key, menu or picker. The game decides round-vs-diagonal from the
neighbours. Two cautions: (1) it is invisible - ACNH players had to be told; we should show a hint (e.g.
the cursor preview shows the cut corner when hovering a cuttable corner). (2) A one-button "cut this
corner" works because ACNH is a console game with facing; we have a mouse cursor, so the cursor position
inside the square (which quarter of the square) can pick the corner - no facing needed.

---

## 2. Terraria (Re-Logic, 2011; 1.4 "Journey's End" 2020)

Sources deep-read:
- Official Terraria Wiki, "Hammers" https://terraria.wiki.gg/wiki/Hammers
- Official Terraria Wiki, "Cursor modes" https://terraria.wiki.gg/wiki/Cursor_modes
- Player thread (Terraria Community Forums), "Needed solid block shapes + Hammer mechanic" (June 2020)
  https://forums.terraria.org/index.php?threads/needed-solid-block-shapes-hammer-mechanic.94197/
- Steam Workshop mod page + comments, "Hammer My Terrain" https://steamcommunity.com/sharedfiles/filedetails/?id=3675752840
- Steam Workshop mod page + comments, "Hammer Mode" (tModLoader) https://steamcommunity.com/sharedfiles/filedetails/?id=2808846469
  (first attempt was rate-limited; read in full on the second attempt)

Note: Terraria is side-view, so its shapes are for walking up hills, not for top-down roads. It is still the
best-known example of a RESHAPE-TOOL, and the player feedback about it is directly useful.

(a) What the player controls: SQUARES + RESHAPE-TOOL (a separate tool, the hammer). You place full blocks,
then hit a block with a hammer; each hit steps it through a fixed cycle: "Full block -> Half-block ->
Slope (floor) facing right -> Slope (floor) facing left -> Slope (ceiling) facing right -> Slope (ceiling)
facing left", and "The cycle repeats infinitely" (wiki). "The order of the shapes ... may vary depending on
whether there are other blocks surrounding the hammered block" (wiki) - so there is a little neighbour
awareness in which shape comes first. One tile holds one block: you cannot have "a Stone Block and a Dirt
Block with opposite-facing slopes within the same tile" (wiki).

(b) How the good look is achieved: each shape is a real, separately drawn state of the tile. Every block
also draws itself joined to its neighbours of the same kind (tile framing) - unsure: I did not read a
source on framing this session; it is general knowledge.

(c) Controls and interface: one button (use/attack) with the hammer held; no menu, no preview of the next
shape, no undo except hitting again round the whole cycle. Smart Cursor with a hammer targets walls
("Removes the wall nearest the cursor", wiki) - it does not pick slopes for you.

(d) Player feedback:
- Forum suggestion (GG Cannon, 2020): "No one really wants to click 10 times to get to that shape you want
  for each and every block when you are building something." Proposed: left click cycles the SHAPE
  (square > triangle > rectangle), right click / Alt ROTATES it. Replies agreed ("Would love this",
  Travlordian01); another noted the engine only has room for two more block states (Dapling).
- The "Hammer My Terrain" mod (20,323 subscribers, 484 ratings when read) removes the manual step entirely:
  "while mining, nearby blocks get hammered into slopes and half-blocks to smooth out the terrain"; the
  author: "I can't stand looking at these blocky edges afterwards". A commenter: "how is this not in
  normal terraria". Another ranks it with Magic Storage (one of the most-used mods) as mandatory.
- The "Hammer Mode" mod (35,088 subscribers, 328 ratings, 61 comments when read) goes the other way - a
  direct picker: "Tired of having to hammer blocks multiple times just to get the slope or half block you
  want? ... Hammer Mode allows you to select which slope a block should be hammered to." Right-click with a
  hammer opens a radial ("grand design-like") menu; the chosen shape then STAYS selected, and "An icon will
  be shown next to your cursor to show which mode is currently selected"; picking the active mode again
  returns to vanilla behaviour.
  => Players value the smooth LOOK a lot and find the blind one-at-a-time cycle a chore. The two popular
  fixes split by purpose: AUTOMATIC shaping for natural terrain (Hammer My Terrain), and a sticky, visible
  shape mode for deliberate building (Hammer Mode). Nobody defends the blind cycle.

(e) Fit for Bug Farmer: the LESSON fits, the scheme does not. A blind cycle of 6 states per square is
exactly the "confusing shape picking" the owner fears, and Terraria's own players call it tedious. What we
take: (1) if we ever offer manual shaping, the next shape must be chosen from the neighbours (Terraria
already varies the order by neighbours; ACNH goes all the way and has only one sensible choice), and (2)
a preview of the result before clicking. What we skip: a separate hammer tool - our shovel already
carries the mode on R.

---

## 3. Stardew Valley (ConcernedApe, 2016; data format from 1.6, 2024)

Sources deep-read:
- Stardew Valley Wiki (modding), "Modding:Floors and Paths" (the Data/FloorsAndPaths format)
  https://stardewvalleywiki.com/Modding:Floors_and_Paths
- Stardew Valley Wiki, "Flooring" (interior floors - only confirms interior flooring is a whole-room
  wallpaper-style item, not tiles) https://stardewvalleywiki.com/Flooring
- Search snippets only (not deep reads): the wiki path pages (+0.1 speed on the farm, starter recipes).

(a) What the player controls: SQUARES + AUTO. Outdoor floors and paths are crafted items placed one square
at a time. The player never picks a shape. There are no diagonal or corner pieces for the player (unsure:
no source states "no diagonals"; none of the pages lists any).

(b) How the good look is achieved: each floor TYPE declares how it joins its neighbours, and the game picks
the edge/corner pieces automatically. The data field ConnectType has four values (quoted from the wiki):
- Default: "For normal floors, intended to cover large square areas."
- Path: "For floors intended to be drawn as narrow paths."
- CornerDecorated: "For floors that have a decorative corner."
- Random: "For floors that don't connect." (e.g. stepping stones - unsure which floors use it)
plus CornerSize: "The pixel size of the decorative border when the ConnectType field is set to
CornerDecorated or Default", and ShadowType None / Square / Contoured, where Contoured means "Draw a shadow
that follows the lines of the path sprite". There is a separate WinterTexture. So the "nice shape" in
Stardew is not diagonal at all: it is a border that wraps the outside of the laid area, plus a soft shadow
that follows the outline, which makes a blob of squares read as a designed paved area. The per-material
connect style is data, chosen by the artist, never by the player.

(c) Controls and interface: place like any item - hold the item, click a square (a green/red square shows
where it will go - unsure, general knowledge). Removal: hit it with a tool; RemovalDebrisType says what
drops (wiki). No undo, no shape menu.

(d) Player feedback: thin in what I could read. Search results point to players finding the mix of
straight and diagonal routes on a farm an "eyesore" (Stardew forums "What's your approach on decorations?",
snippet only - unsure) and to a Nexus mod "Diagonal Paths of Doom" that gives MAP MAKERS diagonal path
tiles (snippet only) - i.e. the base game has no diagonal paths and some players and modders want them.

(e) Fit for Bug Farmer: GOOD for the look, and zero control cost. The takeaway is "per-material connect
style as data": stone path = "Path"-style border, wooden floor = "Default" plank field with a trim,
stepping stones = "Random" (no joining). That alone makes squares look designed. But it does not give the
diagonal road edges the owner wants, so on its own it is not enough.

---

## 4. Minecraft (Mojang; corner stairs since 1.4.2, 2012)

Sources deep-read (full page source downloaded and read):
- Minecraft Wiki, "Stairs" https://minecraft.wiki/w/Stairs
- Minecraft Wiki, "Slab" https://minecraft.wiki/w/Slab
- Minecraft Wiki, "Dirt Path" https://minecraft.wiki/w/Dirt_Path
- Player thread (Minecraft Forum, Java suggestions), "Something needs to be done to corner stairs to enable
  them to be placed on their own" (with a poll)
  https://www.minecraftforum.net/forums/minecraft-java-edition/suggestions/2961958-something-needs-to-be-done-to-corner-stairs-to
- (Minecraft Feedback post "Isolated corner stairs" returned 403 - not read.)

(a) What the player controls: SHAPE-ITEM + AUTO. The shape is a separate item (a slab is a half block, a
stair is its own block), and the fine shape (the corner) is automatic. "Stairs change their shape to join
with adjacent stairs (of any material)": a stair's high side next to another stair "wraps into an 'L'
shape ... (it creates an 'inner corner')", and a low side next to another stair "shortens ... (it creates
an 'outer corner')" (wiki). The block state "shape" is one of straight / inner_left / inner_right /
outer_left / outer_right - never chosen by the player. Direction comes from where the player is looking:
"a stair orients itself with the half-block side closest to the player"; top or bottom half comes from
where on a block face you point: "Pointing at a block top or the bottom half of a block side places the
stairs right side up" (wiki). Slabs likewise: pointing at the top half of a side makes a top slab; two
slabs of the same kind in one space merge into a double slab (wiki).
The shovel detail: "Dirt paths can be created by using any type of shovel on the side or top of dirt, grass
block ..." - one click turns a square into a path; the path is 15/16 of a block high (wiki). Shovel = path
maker is the same idea as ours.

(b) How the good look is achieved: the game rebuilds the corner model from the neighbours every time one
is placed or removed ("Stairs now automatically change shape into corner stairs depending on location",
history, 1.4.2). Bedrock in 2026 (26.40-26.50) even exposes the auto-chosen corner as a readable state and
added a "cornerable_stairs" tag so custom stairs join too (wiki history) - the auto rule is treated as the
core behaviour, extended, not removed, 14 years on.

(c) Controls and interface: no menu, no preview of the corner, no undo (break and replace). The only
input is where you stand and where you point. Direct control over the auto state exists only in creative
("debug stick", which cycles a block's states - snippet source, sportskeeda; unsure beyond that).

(d) Player feedback (Minecraft Forum suggestion thread with poll): the complaint is that a corner cannot
exist on its own and disappears when the stair that caused it is removed. Poll results: "persistent corner
formation" - "corner stairs should keep being a corner when the stairs forcing them so are removed" -
65.5%; a right-click toggle 20.7% (the author rejected it: it needs sneaking to avoid accidental
activation); dedicated corner blocks 3.4%; command-only 6.9%. One reply (DuhDerp) said "there's also no
reason to have stairs form corners at all". So: most players accept the automatic corner; the wish is
to KEEP a shape they got, not to pick shapes from a list.

(e) Fit for Bug Farmer: partial. "Shape as a separate item" (a half-slab of ground, a triangle of path)
would add inventory items and choices - the confusion the owner fears. The part that fits: auto corners
from neighbours, with the direction read from the cursor/player (no menu). And the feedback lesson: if
our auto-shape changes a square when a neighbour changes, players may want a way to keep a shape.

---

## 5. Don't Starve / Don't Starve Together (Klei, 2013 / 2016)

Sources deep-read:
- Don't Starve Wiki (wiki.gg), "Turfs" https://dontstarve.wiki.gg/wiki/Turfs
- Steam Workshop mod page (full description + stats), "Geometric Placement" (for DST)
  https://steamcommunity.com/sharedfiles/filedetails/?id=351325790

(a) What the player controls: SQUARES + AUTO. Turf is an item; you dig a tile up with a Pitchfork ("Turfs
are floor and ground-tile items. They can be dug up with a Pitchfork", wiki) and lay it one whole tile at a
time. No shapes of any kind for the player.

(b) How the good look is achieved: art blending by PRIORITY. Every turf type has a rank; where two meet,
the higher-ranked one draws over the lower with an irregular, organic edge: "Turfs with higher priority or
'dominance' will partly cover other turfs. For example, a Carpeted Flooring turf will always partly cover a
Checkerboard Flooring turf" (wiki). The wiki's pictures: one marsh turf surrounded by eight sand turfs looks
SMALLER than a tile; one sand turf surrounded by eight marsh turfs looks LARGER than a tile - so the visible
shape of a tile is not its real square. This gives soft, hand-drawn-looking borders with zero player effort.

(c) Controls and interface: hold the turf, click the ground; the game shows a tile indicator when digging
(wiki picture caption: "tile digging indicator"). No undo (dig it back up).

(d) Player feedback: the strongest signal is the Geometric Placement mod - 7,515,763 current subscribers,
50,208 ratings, 1,866 comments when read. It "Snaps objects to a grid when placing and displays a build
grid around it (unless you hold ctrl)", with a "Turf Grid Size" option ("How many tiles in each direction
the grid should go when placing turf. Defaults to 2") and several grid color schemes for visibility
(red/green, black/white "easier to see at night", outlined). Caution: the mod is mostly about snapping
structures and walls to a grid; the turf grid is one of its options, so its size is not a measure of turf
complaints alone. What it does show: a very large share of players want to SEE the grid while placing
things. For turf in particular, the blended edges hide where the real squares are (my inference from
the wiki's "smaller / larger" pictures, not a quoted complaint).
(Unsure: I could not read a Klei forum thread on turf-edge complaints - the web-search budget ran out.)

(e) Fit for Bug Farmer: the LOOK technique fits (priority overlay is already the recommended multi-terrain
method in our own grass research, techniques_autotiling_transitions.md). The control lesson matters even
more: if the art rounds or blends edges, the player must still see the real square while placing - a clear
square outline under the cursor (and ideally the neighbouring grid) while the shovel is in a laying mode.
Our cursor already shows "a square of the chosen ground" (GDD P12) - keep it a crisp square even when the
laid result looks round.

---

## 6. RimWorld (Ludeon, 2018)

Sources deep-read:
- RimWorld Wiki, "Floors" https://rimworldwiki.com/wiki/Floors
- RimWorld Wiki (modding), "TerrainDef" (full page source) https://rimworldwiki.com/wiki/TerrainDef

(a) What the player controls: SQUARES only. Floors are built per tile from the Architect/Floors tab and
removed with the "Remove floor" order (wiki); "After floors are removed, the tile will retain its old
terrain type" (wiki). Dragging out a rectangle of floor to be built by colonists: unsure (general
knowledge; not stated on the pages I read).

(b) How the good look is achieved: two data fields per terrain, set by the artist, never by the player
(TerrainDef page): "renderPrecedence - Render importance of terrain ... higher values take higher priority
(Sand = 350, Soil = 340, Gravel = 330, Carpet = 300-298)", and "edgeType - Gives the terrain a fade effect
towards the edges - Hard, Fade, FadeRough, Water (default: Hard)". So natural ground (sand, soil, gravel)
fades raggedly into its neighbours by priority, while built floors keep a hard square edge. Built floors
are allowed to look square because they ARE built things; natural ground is made to look natural.

(c) Controls and interface: designate, colonists build it over time (workToBuild ticks, costList per
tile; TerrainDef page). The player paints intent, not tiles - unsure beyond the fields quoted.

(d) Player feedback: none read for floors (not searched - budget spent on higher-value games).

(e) Fit for Bug Farmer: the per-material "edge type" idea fits exactly: our wooden floor and stone path are
BUILT things and can keep crisp edges (or a neat trim), while dirt, grass, sand and mud are NATURAL and
should blend raggedly by priority. RimWorld shows that mixing the two treatments in one world reads well.
It gives no diagonals.

---

## 7. Factorio (Wube, 2020; tile system current in 2.0 / Space Age 2024)

Sources deep-read (full page sources):
- Factorio Wiki, "Concrete" https://wiki.factorio.com/Concrete
- Factorio Wiki, "Stone brick" https://wiki.factorio.com/Stone_brick
- Factorio Wiki, "Controls" (tile rows) https://wiki.factorio.com/Controls
- Factorio modding API, "TilePrototype" https://lua-api.factorio.com/latest/prototypes/TilePrototype.html
- Factorio modding API, "TileTransitions" https://lua-api.factorio.com/latest/types/TileTransitions.html

(a) What the player controls: SQUARES only, with a resizable square BRUSH. "Concrete is placed using LMB
and can be removed by using RMB while holding any kind of path. The area in which concrete is placed can
be increased and decreased by using numpad-plus and numpad-minus. Placing it over another type of path
automatically mines the previous path" (wiki). Controls page: "Larger tile building area - Increases the
size of the placement area for tiles" / "Smaller tile building area".

(b) How the good look is achieved: fully automatic, layered transitions. Each tile has a "layer" that
"Specifies transition drawing priority" (API). The higher-layer tile draws its own transition pieces over
the lower one - the piece set is side, inner corner, outer corner, double side, U-transition (each with
random-variation weights: inner_corner_weights, outer_corner_weights, side_weights ...), built from
overlay + mask + background layers (API, TileTransitions). History: "All terrains, including stone path
and concrete, have transitions with water" (0.16). So the concrete edge is a designed kerb drawn by the
engine; the player only ever lays squares.

(c) Controls and interface: hold the tile item; the ghost shows the brush square under the cursor (unsure:
ghost appearance not described in the pages read); LMB lay, RMB remove, numpad +/- brush size; laying over
another path replaces it. Blueprints can include tiles (unsure: not read this session).

(d) Player feedback: none read (not searched).

(e) Fit for Bug Farmer: two ideas fit well. (1) The engine-drawn edge set (side / inner corner / outer
corner / U) by priority is the professional standard for "squares that don't look like squares" - we
already recommend the same thing (dual-grid + priority overlay) in our grass research. (2) Right-click
with ground in hand = remove, and "laying over a different ground replaces it" - fewer mode switches.
(Our right-click is reserved for doors/beds/stations, so only the replace-on-lay idea transfers.)
A brush-size key is useful for big fields but is extra control surface; not needed at first.

---

## 8. Townscaper (Oskar Stålberg, 2020) - the "automatic shapes" extreme

Sources deep-read:
- Game Developer, "How Townscaper works: a story four games in the making"
  https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making
- Wikipedia, "Townscaper" https://en.wikipedia.org/wiki/Townscaper

(a) What the player controls: AUTO only. Stålberg: "you can decide where a block is added or removed, and
you can customise the colour of the blocks you place. That's it. Everything else that you see, is achieved
courtesy of the game's procedural generation system" (Game Developer). There is no shape tool at all.

(b) How the good look is achieved: the tiles are CORNER pieces, not whole cells - "approximately 500
architectural tiles that function as corner segments rather than complete building chunks" composed with
marching cubes on an irregular grid, with Wave Function Collapse choosing among pieces that fit the
neighbours (Game Developer). His design focus: "what's important is what happens when things change. So
what happens when one material meets another material?" (Game Developer) - i.e. the art budget goes into
transitions and corners, not into the flat middle.

(c) Controls and interface: click to add, click to remove, pick a colour (Wikipedia; Game Developer).

(d) Player/critic feedback: critics praised how easy and calming it is - "an absolutely joyous little time
waster" (Eurogamer), towns feel "more instantly homely" than city-builders (PC Gamer), "simple concept
that's sure to put you at ease" (TouchArcade) - all via Wikipedia's reception section. Metacritic 86 (PC).
The shapes being automatic is the whole appeal; nobody asks for a shape picker.

(e) Fit for Bug Farmer: the PRINCIPLE fits perfectly and answers the owner's worry directly: players make
one simple choice per square (which ground), and the corner-piece art makes the shape. Townscaper's
corner-piece idea is the same family as the dual-grid autotiling our grass research already recommends
(tiles drawn on the corners between four squares). Its limit for us: pure-auto means the player can never
choose "square here, round there" - fine for most ground, possibly limiting for builders who want a sharp
corner (see ACNH's one-press override as the fix).

---

## 9. Fields of Mistria (NPC Studio, early access 2024)

Source deep-read:
- Fields of Mistria Wiki (wiki.gg), "Stone Path" https://fieldsofmistria.wiki.gg/wiki/Stone_Path
- (and the wiki's own search results page for "path", which lists the path items)

(a) What the player controls: a path is FURNITURE, not ground. "Stone Path" is "Ground decoration
furniture", category "Farm & Outdoor > Ground", in two variants - "Single Stone" and "Double Stone" -
"Paved stones for making paths", crafted from 2 stone (wiki). The player places loose stepping-stone
pieces with the furniture tool. Whether pieces join their neighbours: unsure (the page does not say).

(b) How the good look is achieved: the art is loose stones on top of the grass, so there is no square edge
to hide - the outline is organic by design. Seasonal art variants (wiki).

(c) Controls and interface: normal furniture placement (unsure beyond the category).

(d) Player feedback: none read (the web-search budget ran out before I could look for threads).

(e) Fit for Bug Farmer: a useful SIDE option, not the main system. "Stepping stones" as a decoration that
needs no edge art is cheap and pretty (Stardew's "Random" connect type is the same idea). But our ground
is a real material layer that the shovel digs and that bugs and crops react to, so ground itself must stay
a per-square material.

---

## 10. Valheim (Iron Gate, 2021) - noted, NOT deep-read

Sources: none read this session - the Valheim wikis (fandom, wiki.gg) blocked the fetch (Cloudflare /
401). Everything below is unsure (general knowledge; our own GDD P12 cites it the same way).

(a) A tool with a small menu of ground jobs (level ground, raise ground, pathen, paved road costing stone)
- unsure. (b) Free-form circular brush, not a grid, so edges are soft by nature - unsure. (e) Fit: the
"one tool, a small menu of ground jobs" idea is already our P12 (R cycles the shovel's modes); Valheim
offers nothing on grid corners.

---

## Not researched (and why)

Core Keeper, Dinkum, Palia, Coral Island, Disney Dreamlight Valley, The Sims 4 (quarter tiles and triangle
floors) and Tiny Glade were on the list or relevant, but I could not read a source for them: this
session's web-search budget ran out part-way (200 of 200 searches used, including earlier work in the
same session), and their wikis refused direct fetches (fandom.com HTTP 402 / Cloudflare; several wiki.gg
wikis HTTP 401/403). Nothing is claimed about them here. If they matter, a later pass can read them.

Our own game, checked in the repo (read-only) so the fit notes are grounded:
- The OLD shaped-ground builder is the "picker" approach: `ShovelSelection.cs` cycles `ShapeIndex` through
  `TileCompositor.Shapes` (full, 4 diagonal halves, 4 straight halves, 4 quadrants) on the mouse wheel and
  places `matA~matB~shape` ids (`architecture_shaped_ground.md`). It was dropped on 2026-09-27 ("ground is
  laid in whole squares; the diagonal shapes go", GDD overview) and diagonals are being reconsidered
  (D69, 2026-09-29).
- The zone builder ALREADY has automatic diagonals for authored roads: `tools/zonegen/features/terrain.py`
  `smooth_paths()` turns every stair-step corner (a grass cell with exactly one N/S and one E/W road
  neighbour of the same material) into a 45-degree half-road tile (`stone_path_d_ne` ... `dirt_path_d_sw`,
  8 PNGs in `Resources/Tiles/`). It only ever adds road, never narrows it, and skips mixed-material
  corners. `docs/guides/authoring/roads.md` already says: "Player-placed roads (future): the same
  neighbor rule runs as AUTOTILE when a tile is placed - the system picks the variant; players never flip
  through sprites."
- Our grass research (`docs/product/investigations/grass-overhaul/techniques_autotiling_transitions.md`,
  11 sources) already recommends dual-grid corner tiles + priority overlay for natural ground.

---

## Summary table

| # | Game | (a) Player controls | (b) How the good look is made | (c) Controls / interface | (d) What players say (source) | (e) Fit for Bug Farmer |
|---|------|--------------------|-------------------------------|--------------------------|-------------------------------|------------------------|
| 1 | Animal Crossing: New Horizons | Squares, then "press A again" on a laid square to round or 45-degree-cut its corner (same tool, same button; needs a neighbour; rivers/cliffs need a stair-step first) | One result per press, no list (paths round; rivers/cliffs cut at 45 degrees); same paths merge seamlessly, different paths keep a grass gap | "+" menu of path types; A = lay / round / remove; no undo, no shape menu, no on-screen hint | Players didn't know it existed until told (Bell Tree); custom paths couldn't round - players burned design slots on corner tiles until a transparent-pixel trick (TheGamer) | Very good for control: no new key or menu. Needs a visible hint; our cursor can pick the corner instead of facing |
| 2 | Terraria | Squares, then a separate hammer cycles 6 shapes per hit | Each shape is a drawn tile state; framing joins neighbours (unsure) | One button, blind cycle, no preview | "No one really wants to click 10 times" (forum); popular mods fix it two ways: auto-smoothing (Hammer My Terrain, 20k subs, "how is this not in normal terraria") and a sticky radial picker (Hammer Mode, 35k subs) | Lesson only: a blind shape cycle is the thing to avoid |
| 3 | Stardew Valley | Squares only; no shapes | Per-floor ConnectType (Default / Path / CornerDecorated / Random) + CornerSize border + "Contoured" shadow that follows the outline; winter art | Place like an item; tool to remove | Thin: players/modders want diagonal paths (snippets only - unsure) | Good for looks at zero control cost; gives borders, not diagonals |
| 4 | Minecraft | Shape is a separate item (slab, stair); corners automatic; shovel turns grass into a path block | Stair corner shape (inner/outer, left/right) recomputed from neighbours on every change | Direction from where you look/point; no menu, no preview | Forum poll: 65.5% want a formed corner to STAY when its neighbour goes; only 20.7% want a toggle, 3.4% separate corner blocks | Auto corners fit; shape-items would add clutter |
| 5 | Don't Starve (Together) | Squares only (dig turf with pitchfork, lay turf) | Priority overlay: higher-ranked turf draws over lower with an organic edge; a tile can look smaller or larger than its square | Tile indicator while digging; no undo | Geometric Placement mod (7.5M subscribers, 50k ratings) shows the real grid while placing - mostly for structures, with a turf-grid option | Blending fits; the lesson: always show the true square while laying |
| 6 | RimWorld | Squares only (built floors) | Per-terrain renderPrecedence + edgeType (Hard / Fade / FadeRough / Water): natural ground fades, built floors stay crisp | Architect menu; colonists build; "Remove floor" order | Not read | Per-material edge style fits exactly (wood floor crisp, dirt/grass soft) |
| 7 | Factorio | Squares with a resizable square brush | Engine-drawn transition pieces (side, inner corner, outer corner, double side, U) by tile layer; random variation weights | LMB lay, RMB remove, numpad +/- brush size; laying over another path replaces it | Not read | Priority transitions fit; replace-on-lay fits; brush size optional |
| 8 | Townscaper | Add/remove a block and pick a colour - nothing else | ~500 corner-segment tiles, marching cubes + WFC choose from the neighbours | Click to add/remove | Critics: "absolutely joyous", "sure to put you at ease"; Metacritic 86 | The principle the owner wants: one choice per square, the art makes the shape |
| 9 | Fields of Mistria | Path = a decoration object (single / double stepping stones), not ground | Loose-stone art has no square edge to hide; seasonal art | Furniture placement | Not read | Nice extra decoration; not a replacement for ground |
| 10 | Valheim (not read - unsure) | One tool with a small menu of ground jobs; free-form circle brush | Soft edges by nature | unsure | not read | Already mirrored by our P12 (R cycles the shovel) |

---

## The distinct approaches

### Approach 1 - Plain squares, hard edges
Games: RimWorld built floors (edgeType Hard); our current "whole squares" decision.
Pros: nothing to learn; what you see is exactly the data; cheapest art.
Cons: every diagonal or curve is a staircase; the owner already finds this not good enough for roads.

### Approach 2 - Squares + automatic borders and blending (no diagonals)
Games: Stardew (ConnectType + contoured shadow), Factorio (layered transition pieces), RimWorld natural
terrain (Fade / FadeRough by precedence), Don't Starve (priority overlay).
Pros: zero new controls; laid areas look designed; the look is DERIVED from the squares, so nothing new is
saved or sent over the network; each material gets its own edge style as data.
Cons: diagonal roads still read as staircases; soft edges can hide where the real squares are - Don't
Starve's grid-overlay mod (mainly for structures, with a turf-grid option) has 7.5 million subscribers.

### Approach 3 - Squares + automatic corner SHAPES (the game rounds or cuts corners from the neighbours)
Games: Townscaper (corner pieces), Minecraft stairs (auto inner/outer corners), Terraria's most popular
auto-smoothing mod, and our own `smooth_paths` for authored roads.
Pros: diagonals and curves with NO shape control at all - a stair-step of road squares simply looks like a
diagonal road; one decision per square (which ground), which is exactly what R already offers; still
derived from the squares, so no new saved data or network messages.
Technique note (Boris the Brave, "Quarter-Tile Autotiling", deep-read,
https://www.boristhebrave.com/2023/05/31/quarter-tile-autotiling/): the dual-grid / marching-squares method
draws tiles "at a half-cell offset to the base grid" and picks each from the four squares at its corners
(16 tiles, or 6 with rotation, versus 48 for the classic blob set). Quarter-tiles are cheaper but "you
cannot make swooping curves of radius larger than half the size of a tile, something perfectly possible
with marching squares" - so for real diagonals and curves, marching squares / dual-grid is the method.
Its stated costs: "ambiguous tiles" (two squares touching only at a corner) and a "dual grid is difficult
to get your head around" - for the programmer, not the player.
Cons: the player cannot keep a sharp corner where the rule says "round" (and vice versa); a shape can
change when a neighbour changes (Minecraft's top request is to keep a formed corner); the drawn edge no
longer matches the square exactly, so the placement cursor must show the real square; more art (a corner
set per material, or procedural masks like our existing composite shader).

### Approach 4 - "Hit it again to cut the corner" with the same tool (one sensible result, no menu)
Games: Animal Crossing: New Horizons (paths; rivers and cliffs via stair-step + press A; the game forbids
opposing diagonals side by side).
Pros: no new key, no menu, no shape list - the game decides the only sensible cut; the default stays a
plain square, so nobody is surprised; gives builders control exactly where they want it.
Cons: hidden unless the interface hints at it (an ACNH player had to ask); needs a per-square corner flag
saved and synced; one extra click per corner - tedious on long roads if it is the ONLY way to get
diagonals.

### Approach 5 - A separate reshape tool with a shape cycle or picker
Games: Terraria's hammer (blind 6-step cycle), the Hammer Mode mod (radial picker with a sticky mode
and a cursor icon), our own old shaped-ground builder (13 shapes on the mouse wheel + a second-material
panel).
Pros: any shape anywhere; full control for dedicated builders.
Cons: the confusing, tedious option - Terraria players say so, and our own playtest led to it being
dropped. Needs previews, a second material, and more states to learn.

### Approach 6 - Shape as a separate item or decoration
Games: Minecraft slabs and stairs; Fields of Mistria stepping-stone paths (decor objects); Stardew's
"Random" (non-joining) floors.
Pros: explicit; decor stepping stones need no edge art and read as organic.
Cons: more items and inventory clutter; shape items still need orientation rules; a decor path is a
different system from ground that the shovel digs and crops and bugs react to.

---

## Recommendation for Bug Farmer

Build Approach 3 as the main system, styled per material (the data idea from Approach 2), keep the true
square visible while laying, and hold Approach 4 in reserve as an optional extra. Do not bring back a
shape picker (Approach 5).

1. The player keeps doing exactly what P12 says: pick a ground with R, click one square at a time. No shape
   key, no shape menu, no second material.
2. The game draws the corners from the neighbours, with a corner STYLE per material (artist's data, like
   Stardew's ConnectType and RimWorld's edgeType):
   - stone path (and dirt path): 45-degree cut on every clean stair-step - a staircase of squares reads as a
     straight diagonal road. This is the owner's "roads look better" wish, with nothing to learn.
   - grass, dirt, sand, mud: soft, organic edges blended by priority (the grass research already
     recommends dual-grid corner tiles + priority overlay for these).
   - wooden floor: square corners with a neat trim - it is a built floor, like RimWorld's hard-edged floors.
3. While the shovel is in a laying mode, the cursor shows a crisp square outline of the real square, plus a
   see-through preview of how the result will look with its automatic corners. Don't Starve's 7.5-million-
   subscriber grid mod (structures mainly, turf grid included) is the warning: players want to see the
   grid while placing, and rounded art makes the true square harder to see.
4. Only clean stair-steps get cut, and single-square spikes and checkerboards are left square - the same
   restraint ACNH has (it refuses two opposing diagonals in neighbouring squares) and our `smooth_paths`
   already has (exactly one N/S and one E/W neighbour of the same material).
   *Correction (2026-09-29, checked by running the rule): `smooth_paths` does NOT leave these square. A square
   sticking out of a road gets a diagonal on each side, a one-square branch flares where it joins, stepping stones
   laid corner to corner join into a path, and a checkerboard gets diagonals at its outer corners. See
   `tools/_generated/previews/examples/ground-edges/methods.png` and `laying-ground.md`.*
5. Optional later, only if playtests show builders want a sharp corner on a road or a round corner on a
   floor: ACNH's one-press override - laying the same ground onto a square that is already that ground
   toggles the corner under the cursor between "automatic" and "square", shown in the preview first. Two
   states only, never a cycle.

Why this over the alternatives:
- It answers the owner's exact worry: players make one choice per square; the shape is never theirs to
  pick. Townscaper is the proof that "the player chooses where, the art chooses the shape" feels easy
  and delightful; Terraria is the proof that a blind shape cycle feels like a chore, and its two most
  popular mods move either to automatic smoothing or to a visible sticky mode.
- It costs almost nothing in control space: R, the hotbar wheel, and right-click stay exactly as P12
  decided.
- It needs no new saved data and no new network message: the ground stays one id per square, and every
  player's screen draws the same corners from the same squares (drawn only, not part of the bug
  simulation, so it cannot desync). Approach 4 would need a small per-square flag - another reason to
  keep it optional.
- It reuses what we have: the 45-degree neighbour rule (`smooth_paths`) and 8 diagonal road tiles already
  exist for authored zones, and `roads.md` already planned to run that rule for player-laid roads. The
  composite shader already draws diagonal halves.
- Honest costs: (1) a player cannot get a sharp corner on a stone road unless we add the optional
  override; (2) corners change when neighbours change - fine for ground, where the shape should always
  match what is there; (3) the drawn edge and the real square differ by up to half a square at a cut,
  so gameplay stays per square and the preview must show the square; (4) art: each material needs its
  corner set or a procedural mask.
- One open technical choice for the plan, not for the owner: "fill only" (as `smooth_paths` does: the
  grass square inside the stair-step draws a road triangle, so the road never looks narrower than what was
  laid) versus a full dual-grid (outer corners are cut AND inner corners filled, so the drawn road stays
  the same width as the laid squares on average). Either is drawn only; the square data does not change.
- Two details for that plan: gameplay (walking, farming, "bugs never appear on a floor", the bug
  simulation) keeps reading the square ids exactly as today; and a square at the edge of the area a
  client has loaded must redraw its corners when the neighbouring area arrives (unsure how our client
  loads ground at area edges - not checked in this research).

