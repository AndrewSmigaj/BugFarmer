# Base ladder — pick one per rung

**`LADDER_game_size.png`** — all 21 designs at **real game size** (71px tall), one row per rung, in ladder
order, on grass with the bare character at the top for scale.

This is the same 7 sheets you already had, in one image. The per-rung `explore/<name>/REVIEW.png` files
are still where you look at a design **large**; this one exists to answer the question none of them can —
**does the ladder work as a ladder**, and do any two rungs collapse into the same blob at game size.

```
C:/Users/emily/BugFarmer/tools/_generated/player/reviews/2026-08-13-base-ladder-pick/LADDER_game_size.png
```

Regenerate: `python3 tools/player_sprites/preview_explore.py --ladder leather wood wood-r2 bronze-r2 copper iron steel`

## What I need from you

**One option per rung, or "re-roll".** Six rungs: leather, wood (from `wood` or `wood-r2`), bronze,
copper, iron, steel. A pick then costs one paid call for that outfit's gauntlet; everything else — cutting
the sheet, the walk/run/swing animations, the gallery — is free.

## ⚠ The faces rule and the metal rungs — your call

Faces became the default on 2026-08-07 (*"we should show faces… yes show faces"*). **Copper, iron and
steel were generated ~an hour before that change, and all nine of their options are sealed helms** — a
dark slit, no face. Checked at full resolution, not skimmed. Leather, wood-r2 and bronze-r2 show faces.

So either:

1. **Re-roll copper, iron and steel with faces** — 3 paid calls, and the ladder is consistent.
2. **Plate rungs are the exception** — a great-helm is what plate armour *is*, and `official.py` already
   keeps `HEAD_COVERED` for exactly that. Pick from what is on the sheet, nothing to spend.
3. Pick now, re-roll later.

I have no stake in this one — it is a look decision, not a research-answerable one.

## Defects, so a pick is not a surprise later

- **steel option 3** — the open helm came back as a **black void** where the face should be. A defect, not
  a design; it would need a re-roll if you want that one.
- **wood-r2 option 3** — bare skin at the upper thighs, which the shared prompt forbids.
- **wood option 2** (the basket) — magenta bleed in the hair, so the cutter would leave pink pixels. It is
  also the one I would cut anyway.

## My read — you decide

- **leather** — the best sheet. All three land and are genuinely different.
- **wood-r2** — the re-roll fixed it. All three read as armour now instead of a basket and a barrel.
  The original `wood` row is kept above it for comparison; I would not use it.
- **bronze-r2** — all three land, all face-visible, all clearly bronze rather than copper-pink. Only the
  body is replaced; bronze's five approved hands are untouched, so the animations keep working.
- **copper** — reads salmon-pink at game size, which is the risk with copper. Option 3 (the scale coat)
  holds its shape best; option 1's brim eats the head.
- **iron** — very dark. Options 1 and 2 read as a near-black silhouette on grass and will disappear
  underground. Option 3 has the most internal contrast.
- **steel** — strong, and clearly a step above iron. Option 2 (full plate, big pauldrons) is the most
  legible at 71px.
