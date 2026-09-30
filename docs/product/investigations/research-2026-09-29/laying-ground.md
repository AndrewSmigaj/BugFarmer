# Laying ground with diagonals — options and a recommendation (2026-09-29)

**The question (D69).**
- In his item-pass note on shovels, the owner thought diagonals would be awkward to use.
- In D69 he said he'd prefer ground with diagonals too, because roads look better with them, if the controls and
  screens keep it easy. He added that he might be underestimating players.
- Asked: how should laying ground work, diagonals included? Until this is settled, whole squares stand (D45, P12).

**Fixed points this must respect.**
- The shovel digs and lays. R steps through Dig and each kind of ground the player has, the choice is always on screen,
  and the mouse wheel stays on the hotbar (P12 and P24, accepted 2026-09-28).
- P12 names five grounds: dirt, grass (laid from turf), sand, stone path and wooden floor. The prototype also has mud,
  stone floor and cave floor, subject to the item pass.
- Settings have hold-to-repeat and a "no holds" option. On gamepad the game picks a square. The placement preview shows
  ticks and crosses (P24).
- A private plot is protected: nobody can add or change anything on it without its owner (D67).
- A square built from two materials costs both and gives both back (the owner's rule; `tiles.go:106-108`,
  `architecture_shaped_ground.md`).

**Evidence.**
- [laying-ground-games.md](laying-ground-games.md) covers ten games and five sources of player feedback.
- [laying-ground-techniques.md](laying-ground-techniques.md) covers drawing methods, layering and interface patterns,
  with code studied from four projects.
- What the repo already has:
  - The built zones get diagonal roads from `smooth_paths` (`tools/zonegen/features/terrain.py:220`). A grass square
    with exactly one road neighbour above or below and one beside, of the same material, gets a 45° half of road.
  - 413 squares in three zones are saved with these diagonal ids.
  - The zones' dirt roads are plain `dirt` ground, the same id as a forest's natural dirt floor.
  - No committed zone uses the prototype's 13 hand-picked shapes (0 of 540 chunk files).

**The comparison picture** (free, drawn in the game's own tiles by `tools/gdd/ground_edges_sheet.py`):
C:/Users/emily/BugFarmer/tools/_generated/previews/examples/ground-edges/methods.png. Ten layouts, each drawn three
ways: as laid; "fill the steps" (the zones' rule); and "cut the corners", which also trims the outside corners, so a
lone square shows as a diamond. Roads carry on past each panel's edges. Two simplifications: in "cut the corners",
squares touching only at corners are joined (the method could keep them apart); and the zones' pieces have a
1-pixel checkered edge between path and grass that the picture leaves out.

## What the research found, in short
- **Automatic corner shapes** are what Townscaper, Minecraft's corner stairs and a popular Terraria smoothing mod
  (about 20,000 subscribers) do: the game shapes the corners and the player never picks one.
- **Automatic blended edges without diagonals** are what Don't Starve, Stardew, Factorio and RimWorld do, with an edge
  style set per ground.
- **Builders also value control, when it's visible and remembered.**
  - Terraria's own hammer, which cycles a block's shape one click at a time, drew complaints on its forum about the
    number of clicks.
  - Its most popular fix (about 35,000 subscribers) is a shape menu whose choice stays selected and shows beside the
    cursor.
  - The games note concludes that automatic shapes suit terrain, and a visible, lasting choice suits deliberate building.
- **Animal Crossing** lays square paths; pressing again on a laid square rounds that corner. It cuts at 45° only for
  rivers and cliffs.

## The two looks (see the picture)
| | Fill the steps (the zones' rule) | Cut the corners |
|---|---|---|
| A square on its own | a square | a small diamond |
| The end of a road, a paved yard | square ends and corners | bevelled ends and corners |
| A diagonal road laid as steps | a straight diagonal, about twice as wide as a one-square path | a straight diagonal, about as wide as laid |
| Stepping stones corner to corner | join into a diagonal path | join into a thin diagonal path |
| A square dug out of a road | a square hole | a diamond hole |
| A road turning a corner | a diagonal in the inside corner; the outside corner stays square | a diagonal in the inside corner; the outside corner is bevelled |
| A square sticking out, a narrow path joining | a flat-topped bump; a flared join | a smaller pointed peak that trims the laid square; a smaller flare |
| A checkerboard of paving | diagonals at its outer corners only | becomes a criss-cross lattice with diamond holes |
| Every square the player laid | always shows as at least that square | can show smaller than a square |

## The options, scored (1–5, higher is better)
| | Option | Easy for players | Looks | Control | Fits the decided controls | Cost to build | Total |
|---|---|---|---|---|---|---|---|
| A | Whole squares only (today's decision) | 5 | 2 | 3 | 5 | 5 | 20 |
| B | The prototype's shape picker, cycled (13 shapes) | 1 | 4 | 5 | 2 — a second cycle beside R's | 4 — already built | 16 |
| C | A reshaping tool used after laying (Terraria's hammer) | 2 | 4 | 5 | 4 | 3 | 18 |
| D1 | Fill the steps, automatically | 5 | 4 | 2 | 5 | 3 | 19 |
| D2 | Cut the corners, automatically | 4 — squares can show as diamonds | 4 — but paving patterns break | 2 | 4 — the cursor's square draws as a diamond | 2 | 16 |
| E | D1, plus: laying grass on a square showing a diagonal takes it away, and laying grass there again brings it back | 5 | 5 | 4 | 5 | 2 — a stored mark per square, plus new art for the dirt path | 21 |

The scores are close, so the pick rests on the owner's goal, diagonal paths that stay easy, not on the arithmetic.

## Recommendation (option E)
1. **The game draws the diagonals.** Players lay whole squares exactly as P12 decided. When a square of grass sits in a
   step between two path squares of the same kind, the game draws the path over half of it at 45°. There's no shape
   key or shape menu, and the prototype's 13-shape picker goes.
2. **Only paths get diagonals:** the stone path, and a new dirt path, laid from dirt and drawn as packed earth so it
   looks different from natural dirt (it needs its own tile). It would be a sixth ground on R, beside P12's five. The
   zones' dirt roads would use it too.
   - Natural dirt, sand and mud, such as forest floors and beaches, never get straight cuts. Their edges come from the
     grass rework already planned: blades of grass hanging over the edge (`docs/plans/grass-overhaul.md`, phase 4).
     Those blades hang over a diagonal path edge in the same way.
   - The wooden floor stays square, since it's a built floor. Hoed garden plots and dug holes stay square, so farming
     stays easy to read.
3. **To take a diagonal away, lay grass on that square; lay grass there again to bring it back.**
   - This gives a builder a sharp corner, a checkerboard or separate stepping stones, using the Lay the player already
     knows.
   - Covering the path half costs one turf, and bringing the diagonal back returns it.
   - Laying grass anywhere else is just grass. Where it would change nothing, the preview shows a cross and nothing is
     spent.
   - Digging a square with a diagonal works like digging grass: a hole, and the turf comes back. The path half was free,
     so it gives nothing.
4. **The preview shows the truth.** The cursor outlines the real square. A see-through preview shows it with any
   diagonals the click would add or remove, and keeps the ticks and crosses.
5. **A diagonal costs nothing.** It's the path's edge, like a kerb, not an extra square. That differs from the rule
   that a square made of two materials costs both, so it needs the owner's yes.

**Honest effects.**
- A diagonal can appear or disappear when a neighbouring square is laid or dug; that's what makes it automatic.
- Diagonal roads come out wider than a one-square path. A square sticking out of a path gets a diagonal on each side,
  and a narrow path flares where it joins a wider one.
- Stepping stones laid corner to corner join into a path, and a checkerboard gets diagonals at its outer corners,
  unless grass is laid there (point 3).
- Diagonals form only over grass, never over dirt, sand or another path, and never under an object such as a fence or
  a bench. When the object goes, the rule runs again.

## For the build plan later (my calls, not the owner's)
- **Drawing.** The zones' pre-made diagonal pieces carry an older grass, and today's grass has five variants per square
  (`TilemapManager.cs:984-1000`). So a diagonal square is drawn as that square's own grass, with the path half laid
  over it through a mask at runtime.
  - The prototype's `TileCompositor` is the natural home, stored in the existing `matA~matB~shape` form. As built,
    though, it has two problems:
    - It loads only the plain textures and keeps one tile per id, so every diagonal square would show the same grass.
    - It sizes the result from the first material. Grass is 16 pixels and the path 32, so the path would be shrunk.

    It must build at 32 pixels, with the grass scaled up exactly twice, and keep each square's own grass variant; or
    the path half is drawn as a masked overlay on a layer of its own. Remove only the player-facing picker and the
    shapes other than the four diagonals.
  - **The "taken away" mark** is stored per square with the ground, which changes the save and the late-join snapshot.
    A new ground id would miss the grass variants, the recipes and the hoe, so it isn't used.
  - **Materials.** A diagonal square costs and gives back only its grass; the path half never drops anything. Today
    digging a two-material square drops both, which would hand out free stone.
  - Don't re-run `make_diagonal_tiles.py`: it resizes the road down to the grass's size, and runtime resizing is not
    allowed.
- **The rule.** It runs on the server when a square is laid or dug (`BACKLOG.md:1160`). Port only the diagonal part of
  `smooth_paths`, not its pothole repaving (`terrain.py:262-277`), which would turn a player's dirt into free stone.
  A diagonal never counts as path for its neighbours, so changes can't cascade.
- **Plot borders.** A diagonal forms only when the grass square and both path squares are on the same land. Re-run the
  rule along a plot's border when the plot is claimed or released.
- **Grass tufts.** Tufts are placed only in the grass half of a diagonal square. They're rebuilt for a changed square
  and its neighbours, not only when a chunk loads (`TilemapManager.cs:835-845`).
- **Clean-up.** Remove the server's acceptance of player-chosen shapes (`tiles.go:144-152`, `shovelShapes` 126-132),
  keeping the plain-ground check. Sweep dev saves for old shaped ids. Move the 413 zone squares to the new form when
  the first zones are redone (D69), with a re-save and a north-up check.
- **Tests.**
  - Every path in steps, rectangles, checkerboards, spikes and branches.
  - Laid grass next to a path.
  - Plot borders.
  - Loading and unloading chunk edges.
  - Hold-to-repeat, which must not switch one square back and forth.
  - A held Lay that runs out of turf stops, rather than falling back to Dig and digging holes along the path.
  - The gamepad.
- **Corrections found on the way.**
  - The grass-rework research note says the ground isn't drawn with Unity's Tilemap, but it is
    (`TilemapManager.cs:1011`).
  - The games note's line that the zones' rule leaves spikes and checkerboards square is wrong; see the picture.

## Questions for the owner
1. **The look:** fill the steps (my recommendation) or cut the corners? See the picture.
2. **Diagonals on paths only:** the stone path, plus a new dirt path laid from dirt that looks like packed earth, so
   that natural dirt, sand and mud keep the soft edges the grass rework plans. All right?
3. **To take a diagonal away, lay grass on that square;** lay grass there again to bring it back. All right?
4. **A diagonal costs nothing,** since it's the path's edge, not an extra square. All right?
