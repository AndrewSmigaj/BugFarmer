# Base ladder — pick one per rung

**`LADDER_game_size.png`** — all 21 designs shrunk to game height (71px), one row per rung, in ladder
order, on grass with the bare character at the top for scale.

> ⚠ **These are design SKETCHES, not sprites, and they do not look like fireant or blackant yet.** They
> are stage 1 of three: `outfits.py explore` draws three design options standing on magenta — a big
> illustration whose only job is to let you choose a SILHOUETTE. Shrinking it here is a photographic
> downscale, so it keeps illustration noise (which is most of why iron and steel look busy).
>
> **Stage 2 is where the look comes from.** Once you pick, a second paid call — `outfits.py sheet` —
> redraws *that design* as the 12-frame walk sheet, under a different prompt that says *"big simple
> shapes, not fine detail. This is a small pixel art sprite sheet."* That redraw is what makes fireant
> look like fireant. Then cutting, hands and animations are free.
>
> So judge these on **shape** — helm outline, shoulder mass, hem — and not on surface or finish.

## ⛔ Before you pick anything — the ladder was briefed differently from the ants

**`WHY_THE_LADDER_LOOKS_WORSE.png`** — three rows, same tool, same model, same size, same reference.

The ant explorations you liked were **undirected**. The three slots said, verbatim:

```
1. your own design - decide for yourself what this armour looks like
2. a second design, clearly and obviously different from the first
3. a third design, clearly and obviously different from both of the others
```

Every base-ladder sheet (2026-08-06/07) replaced that with a **dictated** brief — *"a KETTLE-HAT SET — a
wide flat circular brimmed helm, a plain rounded breastplate and a short flared skirt of plates"*, and two
more like it, per rung. Three changes went in, not one:

| | ants (good) | base ladder |
|---|---|---|
| the three options | **undirected** — the model designs | **dictated** — a named historical armour each |
| head | face visible | *copper / iron / steel:* sealed helm |
| framing | "ARMOUR WORN BY A PERSON" | dropped |

`outfits.py` records why that was the wrong move, in a comment written at the time:

> *No design briefs — **the undirected round beat both directed ones**.*

and your instruction it came from, 2026-08-05:

> Three ant-carapace armour designs, from a prompt that says **nothing about what to draw** beyond the sprite
> itself and its material (ant parts and carapace).

So the directed brief had already been tried on the same subject, lost, and been dropped at your
instruction — and then the whole base ladder was generated with it anyway. That is the bug, and it is
mine. Two variables differ between the good row and the bad ones (direction and faces), so I can't split
their contributions from these images alone; the fix is to stop differing on either.

**Nothing here is worth picking from.** The ask below stands only if you want to salvage a design.

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

Faces became the default on 2026-08-07 (your decision to show faces). **Copper, iron and
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
