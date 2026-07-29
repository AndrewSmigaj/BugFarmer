---
name: player-sprites
description: Use when creating or processing the PLAYER character or any player OUTFIT — armour sets, clothing, helmets, gauntlets/hands — including generating the sprite sheet, cutting it into frames, the walk/run/swing motion, and where the work lives on disk. Covers tools/player_sprites/** and tools/_generated/player/**. Does NOT cover world objects / occupants / tiles / items — that is the add-object skill.
---

# Player sprites & outfits

**The character is ARMLESS by design.** No sprite has arms. The hands are separate little fists that float
where hands would be. That one decision is what makes this cheap:

- no shoulder joint, no socket, no hole to repaint when a limb moves;
- no per-outfit arm to keep in register;
- a walk, a run and a **weapon swing** are done by *moving* the hand in code, so no swing pose is ever drawn.

One animator drives every tool. Adding a new weapon costs no animation work.

**Outfits are whole sets, not modular pieces.** Owner decision (2026-07-28): we generate a complete 12-frame
sheet per outfit — copper, silver, bronze… — rather than composing chest/legs/boots layers. The old paperdoll
route needed hand-fixing on every piece; generating the whole sheet in one image removes drift entirely
because everything shares a single render. A modular pipeline may come back later; it is not this.

---

## Where things live
```
tools/_generated/player/
  bases/          armless_front.png, armless_side.png   <- EXACTLY two files. The only source of a base.
  outfits/<name>/ result.png (the 12-frame sheet), the 12 cut frames, gauntlet/, preview gifs
  props/<name>/   non-character props (practice dummy, …)
  archive/        superseded work. Nothing is deleted.
```
Folders are named for **what is in them**, never for how they were made. Looking for the bronze armour means
knowing it is called bronze — not knowing which run produced it.

`gen.py` is the **only** way to generate. Every run writes `RECORD.txt` beside the result (prompt, model,
references as sent, timestamp) and appends a line to `RUNS.txt`. Nothing about a run lives in chat or in the
assistant's head, because that is exactly what kept getting lost.

```bash
python3 tools/player_sprites/gen.py --dest outfits/steel --size 1024x1024 \
  --ref tools/_generated/player/bases/armless_front.png \
  --ref tools/_generated/player/bases/armless_side.png \
  --prompt "..."
```

## ⚠ ASK BEFORE EVERY PAID IMAGE CALL
The spend is unrecoverable and a wrong guess buys nothing. State how many calls and what each is for, then
wait. An earlier "use the API as needed" is **not** standing permission. Free work — compositing, cutting,
measuring, rendering previews — needs no permission, but say plainly which kind a result came from.

---

## Making an outfit

### 1. The sheet — one call
Model **gpt-image-2**, **no mask**, `1024x1024`, both bases as references in order (front, then side).

> Draw a single sprite sheet showing the SAME character in **\<OUTFIT\>** as a 12-frame walk-cycle sheet. Use
> the same character design, proportions, and no-arm anatomy consistently across the whole sheet.
>
> Layout: 3 rows by 4 columns, evenly spaced, all sprites at the same scale and aligned to the same baseline
> within each row.
>
> Row 1: FRONT walk cycle, 4 distinct frames.
> Row 2: BACK walk cycle, 4 distinct frames.
> Row 3: RIGHT-FACING SIDE walk cycle, 4 distinct frames.
>
> Very important: the 4 frames in each row must be DIFFERENT phases of a walk cycle, not repeated standing
> poses.
>
> For each row, the 4 columns must be:
> Column 1: left leg forward, right leg back.
> Column 2: passing pose, legs closer together, transition between steps.
> Column 3: right leg forward, left leg back.
> Column 4: passing pose opposite to column 2, transition back toward column 1.
>
> Because the character has NO ARMS, the walking motion must be shown by leg motion, slight hip shift, and a
> subtle torso/head bob only. Do not add arms, hands, elbows, forearms, or gauntlets. The rounded shoulder
> caps must end at the armless shoulder openings.
>
> Outfit: **\<material, colours, shadows, highlights\>**. Include a **\<HEADGEAR\>** covering the whole
> head, a breastplate, rounded shoulder caps, a waist and hip piece covering the crotch, thigh plates on both
> legs, greaves, and boots. No bare skin between the waist and the boots. The headgear is on the character in
> all 12 frames.
>
> Keep the front row front-facing, the back row back-facing, and the bottom row a strict right-facing side
> profile. Do not drift into a three-quarter view.
>
> Big simple shapes, not fine detail. This is a small pixel art sprite sheet. All 12 sprites must clearly be
> the same character, but each frame in a row must be a distinct walking frame. If two adjacent frames in a
> row are identical, the sheet is wrong.

**Every outfit gets its headgear.** A set without one is inconsistent with the rest and has to be redone.

### 2. The gauntlet/hand — one call
Reference **that outfit's own sheet** so the material matches.

> The attached image is a sprite sheet of a character wearing \<OUTFIT\>.
>
> Draw FOUR small \<MATERIAL\> GAUNTLET HANDS in a row on a black background, evenly spaced, large and
> centred. Nothing else in the image — no character, no body, no arms, just the four hands.
>
> Each is the SAME \<MATERIAL\> as the armour in the attached image, same darker shadows, same bright
> highlights, dark outline.
>
> Left to right, the same hand from four angles: (1) back of the hand facing the viewer, (2) palm side,
> (3) in profile facing right, (4) three-quarter view.
>
> Care about the SILHOUETTE above all. The outline is a soft rounded shape, slightly taller than wide,
> narrowing a little at the wrist. No separate fingers are drawn — at this size the hand reads entirely by its
> outline and two or three shading bands inside it.
>
> Big simple shapes, chunky pixels. This is a small pixel art sprite — each hand is about ten pixels across in
> the game, so use a handful of large blocks, no rivets, no filigree, no fine detail.

Tested prompt strategies: describing the **silhouette** and forbidding interior detail works. Describing
**anatomy** ("fingers curled, thumb along the index") does not — the model draws a realistic hand and then
shrinks it into mush.

### 3. Cut the sheet — free
1. Threshold the black background (`rgb.sum() > 70`).
2. **Dilate before labelling** (`binary_dilation(…, ones((9,9)))`) — dark plate gaps split one figure into
   several blobs otherwise.
3. Connected components; keep blobs over ~4000 px; sort by row centre → front / back / side; sort each row by
   column centre.
4. Give each row **one shared ground line** so the figure doesn't bounce between frames.
5. Left = **mirror of right**. Never generate it.

Frames 1, 2, 3 are the cycle. **Drop frame 4** — it comes back as a second stride rather than the opposite
passing pose, which reads as a skip. Play **1, 2, 3, 2**.

### 4. Pixelize — only if you need the true grid
`aipipe/pixelsnap.py` recovers the real pixel grid. **Verify the pitch yourself** — measure the most common
run-length of constant colour along a few rows and compare. `--auto` once reported **9.5** against a true
**~3.17** and silently discarded two thirds of the sprite. Pass `--pitch` explicitly.

Never hand-roll a downscaler. Cell-median or area-average resampling turns pixel art to mush; that mistake was
made twice in one session while the correct tool sat unused.

---

## Motion (all free, all in code)

**One hand-size constant, relative to BODY height — currently 0.17.** Never size the hand off the tool sprite:
that bug made the same hand 25% of body height while swinging and 17% while walking, so it grew the moment a
weapon was drawn.

- **Walk** — hands swing fore and aft *through* the body, opposite phase, extended on the stride frames and
  tucked at the hip on the passing frames, tilting with the direction of travel. The near hand draws over the
  torso, the far hand behind it and dimmed. Anchor to the **torso width at chest height**, measured once from
  the neutral frame — measuring per frame makes the hands jitter as the legs change the silhouette.
- **Run** — same twelve frames played faster (≈90ms vs 150ms), hands rotated ~75° to point forward and raised
  toward the chest, bigger travel. **No new art for running.**
- **Swing** — the hand rides the tool. Grip position is **measured per tool** off its own sprite (a sword
  grips high on a short hilt, a hoe low on a long shaft), then rotated **225°** with the hand sitting **+16%**
  further down the handle. The motion curves live in `PlayerToolAnimator.cs` and differ per tool kind:
  Swing overshoots, Chop **holds at impact**, Sweep is symmetric with no overshoot (the trail *is* the catch
  area), Till chops down then **drags back** toward the player. Read the actual `case`; do not assume one
  curve fits all.

---

## Failures worth never repeating
- **Masks produce black boxes.** Every masked run came back ruined; every unmasked run worked. The old
  guidance in this file said the opposite and cost most of a day.
- **Say "the character has no arms" explicitly.** Minimal-delta preserves what is *present*, not what is
  *absent* — without the sentence the model draws arms back on, even from an armless reference.
- **Don't carve pieces out of a finished render.** A drawn arm only contains the pixels visible in that pose;
  rotate it and you expose a surface that was never drawn. Author the pieces, don't cut them.
- **One canonical copy of each base.** The base once existed under four names in four folders and the wrong
  one was picked three times in a single session.
- **Look at the render.** Repeatedly a change was made, the output described as working, and the actual image
  showed it buried in the hip, cropped off-frame, or a hand the size of the head.

## Making a whole set, end to end
Two paid calls, everything else free. `outfits.py` holds the set list and the one shared prompt, so a new
set is a dict entry, not a new script.

```bash
python3 tools/player_sprites/outfits.py sheet    steel   # PAID - the 12-frame sheet.  ASK FIRST.
python3 tools/player_sprites/cut_outfit.py outfit outfits/steel     # free - 9 frames
python3 tools/player_sprites/outfits.py gauntlet steel   # PAID - the 4 hands.  ASK FIRST.
python3 tools/player_sprites/cut_outfit.py gauntlet outfits/steel   # free - front/back/side/grip
python3 tools/player_sprites/demo_swings.py steel                   # free - DEMO.gif
python3 tools/player_sprites/preview_all.py                         # free - both ALL_*.png pages
```

**Look at the sheet before cutting, and at the cut frames before the demo.** Both have failed silently.

**A metal set earns its rung by COLOUR, not by shape** — at sprite size the silhouettes are identical, so
"another grey" is a wasted tier. Check it by measuring, not by eye: mean luma over the worn material of
`front_1.png` currently runs iron 66 → steel 90 → silver 113 → platinum 157. Judging this by eye once
produced a confident wrong call (steel "collides with silver"; the numbers said otherwise).

## Pointers
- `docs/guides/art/CHARACTER_DESIGN_GUIDE.md` — the as-built format.
- `tools/player_sprites/demo_swings.py` — the motion preview. Imports `swing_lab.py` approach 6 (the
  designed swing) rather than copying it, so the preview cannot drift from the design.
- `docs/product/investigations/swing-design/` — why the swing is what it is: 10 sources, 5 iterations, the result.
- `docs/product/economy/catalogs/armor.md` — the canonical list of which sets exist and are planned.
