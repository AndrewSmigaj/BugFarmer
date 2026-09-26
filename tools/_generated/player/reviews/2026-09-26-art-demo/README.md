# 2026-09-26 — Art demo: pixel art drawn by Claude, in code

Folder: `C:\Users\emily\BugFarmer\tools\_generated\player\reviews\2026-09-26-art-demo\`

Everything here was drawn by Claude writing code — shapes, one light from the top-left, one shared palette,
outlines and clean-up — at 32 pixels per grid square, in the game's current style. **No image API, no paid
calls, no other tools.** The code is `tools/sprites/drawn/` (run `python3 tools/sprites/drawn/demo.py` to
rebuild this folder). Nothing in the game was changed.

## Open these first
1. **`01_scene_today_vs_new.png`** — the same little scene twice: today's art as the game draws it (left) and
   the new art (right). This is the main judgement: does the new one look like one coherent game?
2. **`06_player_sheet.png`** — the player in 3 facings × 4 walk frames: floating hands (the approved design)
   and with arms; the plain base and a full bronze armour set.
3. **`06b_armour_layers_front.png`** / **`_side.png`** — the armour pulled apart: body, leg plates, boots,
   chestplate, helmet, gauntlets are **separate pieces**, drawn on the same skeleton, so they line up in every
   frame. This is what makes separate armour pieces possible again instead of whole outfits.

## Everything else
| file | what it is |
|---|---|
| `01b_scene_new_3x.png` | the new scene on its own, larger |
| `02_ground_tiles.png` | 4 grass and 3 dirt tiles, each seamless, sharing one palette |
| `02b_transitions_1/2.png` | the 16 grass↔dirt edge tiles that make the winding path |
| `03_chest_and_tree.png` | today's chest + oak beside the new chest + flowering tree |
| `04_beetle.png`, `04_beetle_walk.gif` | the burying beetle (`beetle_carrion`) — glossy black, two orange bands, orange-tipped antennae — walking in the real insect tripod gait (6 frames). Today's is the 12×12 blob on the left |
| `05_icons.png` | today's copper axe + honey beside new copper/iron/gold axes (one tool family) and a honey jar |
| `06_walk_*.gif` | every player walk, animated (hands/arms × base/bronze × front/side/back) |
| `07_ui.png` | a framed parchment panel, item slots (gold ring = selected), hearts full/half/empty |
| `sprites/` | the raw 1× sprites |
| `lint.txt` | the numbers below |

## The numbers (checked by script, not by eye)
Every sprite uses **only** the one master palette (0 off-palette colours). Colours per sprite: chest 15,
tree 15, beetle 11, axe 12, honey jar 16, grass 4, dirt 7, bronze player 15, UI panel 13. For comparison,
today's 431 object sprites use **8,226** different colours between them because each one has its own palette —
that is the main reason today's art doesn't look like one game.

## My honest read
- **Strongest:** the ground (calm grass, natural path edges), the beetle, the tool icons as a family, the UI,
  and above all that everything matches.
- **Weakest:** the tree canopy is less detailed than today's oak; the armour is cleaner but simpler than the
  approved bronze outfit; the front-facing walk has a small step (like the approved one).
- **Fairness note:** in the game, today's roads also use 45° corner tiles; the left scene uses plain square
  tiles, so today's paths look blockier here than they sometimes do in the game.

## What I need from you
1. Is this the bar you want? Which pieces are good enough, and which need another pass?
2. **Floating hands or arms?** (both are in `06_player_sheet.png` and the gifs)
3. **Separate armour pieces or whole outfits?** (`06b_*` shows separate pieces working)
