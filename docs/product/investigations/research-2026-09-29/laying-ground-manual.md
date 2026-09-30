# Laying shaped ground by hand — the design (2026-09-29)

**The owner's direction (2026-09-29).**
- Shapes are placed by hand, not drawn automatically. Players must be able to build checkerboards, and full squares
  plus the four diagonals are required for roads.
- Straight halves and quarters are welcome if the controls stay simple. Squares may be small on many screens.
- A shape goes on top of whatever ground is already in the square, so one material is chosen, unless two materials
  prove better.
- Digging peels ground away down to a shared base that can't be dug, so a square is never empty.
- He suggested pointing at the part of the square, or a small painter-style panel with a key to rotate; either way
  there's always a preview.

This replaces the automatic proposal in [laying-ground.md](laying-ground.md). How the shovel's controls work is the
assistant's to design (D45; the overview's part on controls), so the controls below are presented for the owner's
objections. Only the rules that change play are asked about.

**What we're working with.**
- The shovel's R steps through Dig and each kind of ground, the choice is always on screen, and the mouse wheel stays
  on the hotbar (P12, P24).
- Settings have hold-to-repeat and a "no holds" option. Placement previews show ticks and crosses, never colour alone.
  A gamepad aims at the square in front, or with an optional cursor on the right stick (P24).
- A private plot is protected: nobody can add or change anything on it without its owner (D67).
- The prototype already draws full squares, the four diagonals, the four halves and the four quarters
  (`TileCompositor.cs:25-31`). T is used nowhere in the game or in the controls plan.
- How big a square looks on screen: the camera shows 15.4 squares from top to bottom (`SampleScene.unity:954`):

  | Screen | One square | A quarter of a square |
  |---|---|---|
  | 720p laptop | 47 px | 23 px |
  | Steam Deck | 52 px | 26 px |
  | 1080p | 70 px | 35 px |
  | 1440p | 94 px | 47 px |

  A comfortable click target is at least about 24 px, and 44 px is easy. So aiming at part of a square works for
  corners at 1080p and up, is borderline on a laptop or Steam Deck, and fails for sides below about 72 px squares.
  Anything that needs aiming inside a square can't be the only way.

**Evidence.**
- [shape-placement-games.md](shape-placement-games.md) covers 16 games and tools.
- [shape-placement-controls.md](shape-placement-controls.md) covers target sizes, menu speed, gamepad and
  accessibility guidelines, and how other games store layered ground.
- The researchers had no web search, so player feedback is thin. A quick playtest early would settle what the evidence
  can't.

## The options, scored honestly (1–5, higher is better)
| | Controls | Easy to learn | Fast | Small squares | Gamepad | No holds | Fits R and the mouse wheel | Easy to find | Total |
|---|---|---|---|---|---|---|---|---|---|
| A | Pointing only: the part of the square you point at sets the direction | 3 | 5 | 2 | 2 | 5 | 5 | 2 | 24 |
| B | A rotate key only (Factorio) | 4 | 3 | 5 | 5 | 5 | 4 | 3 | 29 |
| C | A painter panel at the screen's edge, plus a rotate key | 5 | 2 | 5 | 3 | 5 | 4 | 5 | 29 |
| E | Hit again to cycle through shapes (Terraria's hammer) | 3 | 1 | 5 | 5 | 5 | 5 | 2 | 26 |
| F | T steps through shape kinds (with a clickable strip), and pointing sets the direction | 4 | 5 | 2 | 2 | 5 | 4 | 4 | 26 |
| G | The middle of the square means full, and its corners mean diagonal, with no kind key (like the Tweakeroo mod) | 3 | 4 | 2 | 2 | 5 | 5 | 2 | 23 |
| H | Full squares and diagonals only, T toggles between them, and pointing sets the direction | 5 | 5 | 2 | 2 | 5 | 5 | 3 | 27 |
| **W** | **A shape wheel at the cursor (T): pick the exact shape from pictures; a rotate key turns it** | 5 | 4 | 5 | 5 | 5 | 4 | 4 | **32** |

- **W is the pick, but it's close, not a sweep.**
  - The wheel works the same way on every screen and on a gamepad.
  - It needs no fine aiming inside a small square.
  - Every choice is a picture, so nothing is hidden. It is the owner's painter panel, brought to the cursor, where
    reaching it costs no trip across the screen.
- **H is simpler still,** but gives up the halves, and it needs aiming inside the square.
- **Pointing (A and F) is the fastest with a mouse on a big screen,** so it stays as an option (point 7 below).

## The design — see the mock-up
Picture: C:/Users/emily/BugFarmer/tools/_generated/previews/examples/ground-edges/shapes_mockup.png
(drawn by `tools/gdd/ground_shapes_mockup.py`).

1. **R picks the ground. T opens the shape wheel at the cursor.**
   - Full sits in the middle, the four diagonals at the corners and the four halves at the sides. Each picture's stone
     part points the way it sits on the wheel.
   - Click one: the whole slice of the wheel counts, not just the picture. Or press T again to keep the current
     shape.
   - The shape stays selected, and shows on the shovel's hotbar slot and beside the cursor ("Stone path · Diagonal").
   - Full is the default, so ordinary laying doesn't change.
2. **A rotate key turns the chosen shape a quarter turn** (with Shift, the other way). Two presses give the opposite
   edge of a road. A diagonal road takes about four strokes:
   - lay the road's squares as a 45° line;
   - pick a diagonal on the wheel and lay one edge as a 45° line;
   - press rotate twice;
   - lay the other edge.
3. **Click a square to lay.**
   - A see-through ghost shows exactly what will be laid and what it covers.
   - It carries a tick and the cost, or a cross and the reason: "Not your plot", "Need 1 stone", "Something is
     standing here", "Nothing would change".
4. **Digging has a preview too:** the piece that will come off is outlined.
5. **Laying a line** (hold, or click to start and click to end under "no holds"):
   - Lines snap straight or to 45°, one square per step, so a diagonal edge gets exactly one triangle per step.
   - A line that runs out of ground stops. The shovel then shows Dig and says so, as P12 has it, but the held button
     never starts digging; the next press does.
6. **A copy key** sets the shovel to a square's ground and shape. It copies the choice, not the materials, and it's
   the quickest way to carry on an edge or a checkerboard.
   - There's no undo. Nothing is lost when you lay over something (see Layers), so a mistake is fixed by laying or
     digging again. Without undo, there's also no way to use it to duplicate materials.
7. **An option for mouse players: "aim by pointing".** The part of the square under the pointer sets the direction:
   the corner for a diagonal, the side for a half.
   - It's on by default where squares are big enough for corners (about 1080p and up) and off below.
   - Halves are only aimed by pointing on bigger squares, about 1440p; below that they keep the wheel's direction.
   - With pointing on, the wheel picks the kind and pointing picks the direction.
   - The direction locks when a line starts, so a line along a 45° edge can't flip its triangles.
8. **Gamepad:** a button opens the wheel, the stick picks the shape, and another button rotates it. The square is the
   one in front, or the right-stick cursor's.
9. **Which shapes first:** full, the four diagonals and the four halves, all on the one wheel with no extra rule.
   Quarters can follow if wanted, on a second page of the wheel. That applies the owner's condition that extra shapes
   come only if the controls stay simple.

## Layers and materials
- **A square holds:**
  - a **base** that can't be dug, the same everywhere: the bare soil a dug square shows today;
  - its **ground**, a full square such as grass, dirt, sand or stone path;
  - at most **one shaped piece** on top.
- **Laying over something gives it back, as if you had dug it up.** This is the owner's lean, 2026-09-30.
  - A full square replaces the ground and any shaped piece; a shape replaces any shaped piece.
  - Whatever was covered comes back as its materials: tile under grass gives the tile back, and wild grass gives turf,
    exactly as digging would. The materials land where dug materials land.
  - Laying over something takes as many swings as digging it would, so a better shovel still saves time (D69). With
    the iron shovel it's one swing; with the wooden one, three. The cracks show the progress, as when digging.
  - So nothing is ever lost by laying, and it can't be used as a free, instant dig.
- **A shaped piece costs what a full square of that ground costs** (its usual recipe), and gives the same back when
  dug. The owner's rule that a square made of two materials costs both holds, because each layer is paid for when it's
  laid. D69's hits per square apply to each layer.
- **Changing your mind is free.**
  - Laying the same ground in another shape reshapes the piece at no cost.
  - Laying a full square of the same ground over its piece completes it, and the piece's recipe comes back.
- **Two pieces that complete a square both stay.** If the new piece fills exactly the rest of the square, its ground
  becomes the ground under the old piece: a sand triangle beside a stone triangle makes a square of both. If the new
  piece overlaps the old one instead, the old one is removed, and the ghost marks it first.
- **Two matching pieces of the same ground join into a full square,** two halves or two opposite diagonals, and one
  recipe's worth comes back.
- **Laying on the base,** a dug hole, is allowed. The base itself can't be dug or given back.
- **Garden plots.**
  - **The owner's rule (2026-09-30):** no shaped piece can be laid on a garden plot, so there are no partial plots.
    The ghost shows a cross and "Not on a garden plot".
  - **Which squares the hoe can till: option A, chosen by the owner (2026-09-30, D72; adjustable later).** He had
    asked for help thinking it through. Today the
    hoe tills only full grass or full dirt, in one swing, and nothing comes back (`tiles.json` tool actions). The
    options:
    - (A, recommended) **Soft ground tills where it lies.** Any square made only of soft ground (grass, dirt, sand or
      mud, whole or mixed) becomes a plot in one swing, and nothing comes back, as in farming games generally. A
      square with a hard part (stone path, stone floor, wooden floor) needs that part dug first, and the ghost says
      so.
    - (B) **The hoe clears, gives back, then tills.** As A, but the grass or sand comes back as materials, as if dug.
      Nothing is lost, but every hoed meadow fills the bag with turf. The iron hoe, at three by three, would also dig
      grass and sand faster than any shovel.
    - (C) **Plain squares only.** Anything mixed must be dug first. Fiddly, and not recommended.
  - **Removing a plot (recommended):** dig it back to bare soil, or lay any ground straight over it. Neither works
    while something is growing; the ghost says why. Empty plots don't disappear by themselves.
- **Refused:**
  - laying exactly what is already there;
  - a shaped piece of the same ground as the ground under it;
  - a shaped piece on a garden plot.
- **Another player's plot:** nothing is laid or dug there (D67).
- **A square with a shaped piece behaves as that piece's ground,** as the prototype does (`tiles.go:99`). Since
  pieces never go on garden plots, this matters only for walking and for floors.

## For the build plan later (my calls, not the owner's)
- **Data.** Keep one ground id per square, add a short list of shaped pieces (a material, a shape and where), and the
  base.
- **Moving old data over.**
  - Today's `A~B~shape` ids become a shaped piece A over ground B. They exist only in dev saves, which get a one-off
    sweep.
  - The committed zones' 413 diagonal squares (`stone_path_d_*`, `dirt_path_d_*`, which can't be dug today) become
    shaped pieces over grass. Check which way each faces, then re-save the zones and view them north-up.
- **Drawing.** Two layers: the ground, which keeps each square's own grass variant, and the shaped pieces, each
  material cut by the shape masks at 32 pixels. This removes the prototype compositor's problems: the same grass on
  every square, and the path shrunk to the grass's size.
- **The bug simulation doesn't read ground today;** ground never blocks bugs (`TilemapManager.cs:1467-1471`). So
  there's no sync risk now. If "bugs never appear on a floor" is built, it reads the use rule above, through the
  determinism checks.
- **Server.** It checks each change against the square as the client saw it, and handles costs, give-backs, joins,
  swings and the plot rule.
- **Give-backs must match costs exactly.** For every ground, digging it and laying over it return exactly the recipe
  that laying it costs. Check the current recipes and dig results line by line (for example stone floor costs 2 stone),
  or laying and covering could slowly create or lose materials.
- **Keys.** T, the rotate key and the copy key are placeholders until the controls section settles them, and every key
  can be rebound. The copy key isn't called "pick up", because that is P24's item pick-up.
- **Screens.** Whole-number scaling and a zoom are planned settings (P24). A zoom while shaping would help small
  screens; it's worth adding when the zoom is built.
- **Tests:**
  - the wheel and pointing at 720p, on Steam Deck and at 1080p;
  - gamepad, no holds, and lines along a 45° edge;
  - joining, and digging order;
  - plot borders;
  - laying over each kind of ground at each shovel tier, with the give-backs counted;
  - garden plots: hoe, dig and cover, with and without a crop;
  - two players on one square;
  - saving, loading, and the late-join snapshot.

## The owner's answers (2026-09-30) and what's still open
- **Garden plots:** no shaped pieces on them (his rule). The hoe tills any soft square where it lies, and a hard
  part must be dug first (option A, chosen 2026-09-30). Plot removal is a recommendation above.
- **Laying over something:** he leans toward getting it back, as if dug up. The design above follows that, with the
  swings added so a better shovel still matters, and no undo.
- **The base:** left to the assistant: the bare soil a dug square shows today, the same everywhere.
- **Open, for his OK:** the plot removal, and "laying over takes the dig's swings; no undo".
