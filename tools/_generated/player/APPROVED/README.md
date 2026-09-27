# APPROVED — open this first

**Where the agreed animations are:** the table below. Every path starts at
`C:\Users\emily\BugFarmer\tools\_generated\player\APPROVED\`.

Nothing goes in this folder unless you explicitly approved it, and each approval is recorded in
`DECISIONS.md` in clean prose, dated and attributed.

---

## The current character animation, in real pixels

**`2026-08-15-fireant-v2\ALL_ANIMATIONS.gif`** ← this is the one. All six at once, walks on top,
runs underneath. Approved 2026-08-15: the results were accepted, confirming that the new generation
approach works.

| file | |
|---|---|
| `2026-08-15-fireant-v2\walk_side.gif` `walk_front.gif` `walk_back.gif` | the three walks, one at a time |
| `2026-08-15-fireant-v2\run_side.gif` `run_front.gif` `run_back.gif` | the three runs |
| `2026-08-15-fireant-v2\frames\` | **the actual pixels.** 12 PNGs, four frames per direction. side 39x77, front 26x77, back 27x78 — that is their true size, not a preview |
| `2026-08-15-fireant-v2\gauntlet\` | its five hands, drawn at 13px |

The gifs are shown at 6x so you can see them. The `frames\` PNGs are the sprites themselves.

Working copy of the same thing (what the tools read): `outfits\fireant-v2\`.
The review write-up: `reviews\2026-08-15-fireant-v2\README.md`.

---

## The base character, 2026-07-28/29

Made before the pixel conversion existed. Still the reference for the *motion*, not for the pixels.

| file | |
|---|---|
| `01_WALK_front.gif` `02_WALK_side.gif` `03_RUN_side.gif` | the approved gaits |
| `04_HAND_SHAPE_front_rot90.gif` | the chosen hand shape |
| `05_SWING_iteration7_best_for_SWORD.gif` `06_SWING_iteration11_best_overall.gif` | the swings — best so far, not final |
| `hands\h1.png h2.png h3.png` | the three hand sprites the animations use |

---

## Built but NOT approved — you have not seen these yet

They are finished on disk and waiting on your eyes. They are deliberately **not** in this folder.

| what | watch | pixels |
|---|---|---|
| black-ant, rebuilt (Lasius niger) | `reviews\2026-08-15-blackant-reroll\ALL_ANIMATIONS.gif` | `outfits\blackant-v3\frames\` |
| bronze, rebuilt | `reviews\2026-08-15-bronze-reroll\ALL_ANIMATIONS.gif` | `outfits\bronze-v2\frames\` |

You picked the *design* for both (option 2 for black-ant, which you judged good; option 2 for bronze).
The animations built from those designs have not been shown to you — the bronze one finished at
18:09 on 08-15, which is when the power went out.

---

## What the game still uses

`tools\player_sprites\official.py` — still points at the **old** 2026-08-06 `outfits\bronze`,
`outfits\fireant`, `outfits\blackant`. None of the three rebuilds above are wired in. Nothing you
see here is in the game yet.
