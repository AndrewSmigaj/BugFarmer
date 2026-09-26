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

**Outfits are whole sets, not modular pieces.** Owner decision (2026-07-28): we generate a complete outfit —
copper, silver, bronze… — rather than composing chest/legs/boots layers. The old paperdoll route needed
hand-fixing on every piece. A modular pipeline may come back later; it is not this.

That decision stands; the mechanism under it has changed. It used to mean one 12-frame render per outfit, on
the reasoning that a single image removes drift. It didn't work — a twelve-cell sheet leaves each figure too
small to carry a pixel grid. An outfit is now **one turnaround plus one call per direction**, and the drift
that the single render was meant to prevent is handled by seeding every direction from the same approved
turnaround and then measuring the results against each other.

---

## Where things live
```
tools/_generated/player/
  bases/          armless_front.png, armless_side.png   <- EXACTLY two files. The only source of a base.
  outfits/<name>/ tries/ frames/ gauntlet/ anim/ archive/   <- see "Iterating on a sprite" below
  props/<name>/   non-character props (practice dummy, …)
  gallery.html    generated. Open it to see every outfit as it stands.
```
Folders are named for **what is in them**, never for how they were made. Looking for the bronze armour means
knowing it is called bronze — not knowing which run produced it.

---

## Iterating on a sprite — READ THIS BEFORE MAKING OR MOVING ANYTHING

Sprites are not made once. They are **iterated**, the owner picks, and the pick has to survive the session.
Everything below exists because it didn't: variants named `set_a` / `batch2` / `profile_option_1`, dumped in
one folder, approvals never written down, and then neither of us could say what was current. That cost three
days and a day of approved work.

### The four stages an outfit passes through

| stage | produces | API? |
|---|---|---|
| `tries/` | every candidate render, one folder per run with its `RECORD.txt` | **paid — ask first** |
| `frames/` | the picked renders **cut** into `front_1..4` `side_1..4` `back_1..4` | free |
| `gauntlet/` | that outfit's five hands | **paid — ask first** |
| `anim/` | the built gifs. `build.py` writes these; never hand-made. | free |

```
outfits/<name>/
  tries/2026-08-15-frontwalk/    result.png + RECORD.txt (prompt, model, refs) per run
  frames/                        front_1..4  side_1..4  back_1..4   <- what build.py reads
  gauntlet/                      front back side grip_back grip_palm
  anim/                          walk_side.gif, run_front.gif, swing_*.gif …
  archive/                       superseded work. Nothing deleted, ever.
```

**Four frames per direction, always** — contact, passing, opposite contact, opposite passing, played
`[1,2,3,4]`. Frame 2 is the neutral the whole bank is measured against (`build.NEUTRAL`).

### The rules, in the order they get broken

1. **Never name a file for how it was made.** Not `set_a`, not `batch2`, not `option_1`, not `result.png`.
   The *batch folder* carries the meaning — dated and named for the idea — and `RECORD.txt` inside it holds
   the prompt. Today every candidate on disk is called `result.png`, which is most of why nothing is findable.
2. **Batch folders are `YYYY-MM-DD-HHMM-what-it-was`.** Year first so Explorer sorts them; no colons, Windows
   forbids them.
3. **To make something current, run `promote.py` — do not copy files by hand.**
   ```bash
   python3 tools/player_sprites/promote.py <outfit> <path-under-scratchpad> "<the owner's words, verbatim>"
   ```
   It copies to `current/`, moves the old current to `archive/`, appends the `CURRENT.md` row, re-renders the
   animations and refreshes the gallery — atomically. **Promoting IS recording.** A hand-copy skips the
   record, and a decision with no record is a decision that gets lost. The pre-commit hook fails the commit if
   `CURRENT.md` and `current/` disagree.
4. **Quote the owner verbatim in the ledger.** Not your paraphrase of what they approved. Approvals sound like
   *"row 2 fist PALM is great"* and *"walk b is fine"* — the exact words are what makes it unambiguous later.
5. **Nothing is deleted or overwritten.** Superseded work moves to `archive/`. **Never bulk re-cut or bulk
   move** — every bulk run so far has destroyed or hidden something the owner was using. Show the list first.
6. **Scratchpad is tracked in git.** Work in progress is real work. Decisions are not instant.
7. **One shape for every sprite.** The bare character is just another outfit. No special buckets.

### Seeing what you have
`python3 tools/player_sprites/gallery.py` regenerates `gallery.html` — every outfit's current animations and
frames, a progress board showing which stage each outfit is at, and per-outfit candidate comparison. Open it
before asking the owner to look at anything, and re-run it after any promotion.

`gallery_gif.py` renders that same grid, animated, into one `ALL_OUTFITS_ALL_ANIMATIONS.gif` — the version
that can be sent to someone.

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

**Four paid calls minimum: the turnaround, then one per walk direction, then the gauntlets.**
Everything after that is free. Do not try to get more than one direction out of a call — see
"Why one direction at a time" below.

### 1. The turnaround — one call, and it sets everything downstream
`1536x1024`, references = the two bases. Ask for THREE standing views in a row: front, strict right
profile, rear.

This is the design lock. The owner approves the design here, and every later call for this outfit is
seeded from one of these three views — the front walk from the front view, and so on. Snap all three
**on one grid** so they are guaranteed the same size, and keep them as `view_front/side/back.png`.

Two consequences worth knowing:
- A direction's calls never see the other directions, so the back view can't come back as the front
  with the head turned round — there is no front view in the room.
- Nothing cross-checks the directions either. The turnaround is the ONLY place they are forced to
  agree, which is why every walk is seeded from it. Measure each walk against the others anyway.

### 2. Each walk direction — one call each, THREE calls
`1536x1024` (landscape), reference = that direction's turnaround view. Four walk frames in a row:

> Frame 1: left leg forward, right leg back.
> Frame 2: passing pose, legs closer together, transition between steps.
> Frame 3: right leg forward, left leg back.
> Frame 4: passing pose opposite to frame 2, transition back toward frame 1.
>
> Very important: the 4 frames must be DIFFERENT phases of a walk cycle, not repeated standing poses.

plus the armless clause enumerating "arms, hands, elbows, forearms, gauntlets", the pixel-density
clause, and the magenta background. Compose it from `outfits.py`; `gen.py` refuses to spend on a
character prompt missing a mandatory clause.

**The walk prompt is `outfits.walk_prompt(what, view)` — do not type one.** It was typed fresh per run
until 2026-08-18 and survived only inside each run's `RECORD.txt`, which is three chances to drift
across three outfits and a guarantee across twenty-five. Every sentence in it is a defect that shipped;
`outfits.py` says which. Change the wording there, once, and show the owner the diff before spending.

**For the camera-facing views it says the legs do not swing sideways.** The default is feet kicking out
to either side, which reads as a dance (*"they are ridiculous like someone doing a russian dance"*).

**Knee lift is MEDIUM-HIGH, and it is now measured.** "Lift the knee HIGH" produced 13.8–19.8% of body
height across the three built outfits — owner, 2026-08-18: *"its lifting the knees really high which is
ok for running but not walking"*. `outfits.WALK_KNEE` asks for a lift of about a tenth of the
character's height, and `cut_walk_row.check_lift` warns outside `LIFT_BAND` (7–15%). The band is
provisional and a WARNING, not a fail — look at the render.

⚠ **One leg set serves both walk and run.** `official.ANIMATIONS` gives `walk_side` and `run_side` the
same `frames="side"` bank; the run differs only in arm swing, fist size and timing. So the walk's knee
lift IS the run's knee lift. A higher run would need a second set of leg frames per direction — three
more paid calls per outfit — and that has not been agreed.

**Side comes back facing LEFT.** Mirror it at cut time (`cut_walk(..., mirror=True)`), never after
rendering — `gait`'s wrist-lean maths assumes the character faces +x, so mirroring the finished
animation puts the wrists on backwards.

#### Why one direction at a time
The old approach asked for all twelve frames as a 3x4 sheet in one call. It never produced
convertible pixel art. A twelve-cell sheet gives each figure about a twelfth of the canvas, so the
blocks come back too small to form a grid, and the render is smooth with nothing to snap to. Four
frames in a row gives each figure the same room as the standing turnaround, which is the layout that
converts every time.

### 3. The gauntlets — one call, on a PORTRAIT canvas
`1024x1536`, references = (1) a template image, (2) the crisp hand strip for shape.

The hand must end up **exactly `round(body_height * ratio)` tall** — 13 pixels for a 77-pixel body at
the walk's 0.17. It has to be BORN at that size. It cannot be shrunk to it afterwards: `gait._sz`
resizing a 20px hand down to 13 deletes rows, and rescaling player art is banned.

Getting there is arithmetic, not wording. **The model always draws a hand about 200 screen pixels
tall**, whatever you ask, so the hand's size in real pixels is `200 / grid`, and the grid is set by
how tall the character gets drawn. On a landscape canvas the character can't exceed ~900px, which
pins the grid near 12 and floors the hands at ~16. Four different phrasings — "one sixth as tall as
the character", "exactly 13 blocks, count them", correctly-sized boxes to draw inside — returned
19.7, 19.5, 16.0, 19.3. None of them could work.

Portrait fixes it. Put the character on the left and the five hands **stacked in a column** on the
right; the template is then taller than it is wide, so the canvas height binds, the character is
drawn ~1400px tall, the grid goes to ~18.5, and the usual 200px hand lands on 13.

Predict it before spending: `grid ≈ 1400 / template_height_in_blocks`, `hand ≈ 200 / grid`.

The template also carries the character sprite itself at 1:1, which is what makes "the same pixel
density as the character" binding rather than hopeful — both are drawn on one canvas, so they cannot
disagree. The character came back at 25.0 x 76.5 against a 25 x 76 reference.

### 4. Cut — free, `cut_walk_row.py`
```python
from cut_walk_row import cut_walk, cut_gauntlet_column, check_alternation
cut_walk(render, frames_dir, "front", pitch=12.25)
cut_gauntlet_column(render, hands_dir, pitch=18.50)
```

**Pixel conversion is mandatory, not optional.** It is what makes a player sprite a sprite. See
[[player-sprites-are-pixelsnapped]]: snapping RECOVERS the pixels gpt drew, at their true grid — it
is not a downscale, and downscaling player art is banned outright.

- **Snap the whole canvas on ONE grid, then split.** All four frames were drawn at one scale, so
  there is one true grid. Per-frame detection disagrees with itself and the character shimmers.
- **Pass the pitch explicitly.** `detect_pitch` takes the smallest pitch scoring near-max and a comb
  at half the true pitch also lands on every line, so it returns the harmonic constantly — 9.25 for a
  true 18.50, 4.65 for a true 23.00. Score the candidates, check what figure height each implies,
  then pass it.
- **Run `check_alternation` on the front and back banks, every time.** The model returns cycles where
  BOTH stepping frames lift the same leg. It looks fine in a still and wrong only once it loops, as a
  foot tapping twice. That shipped before anyone caught it, and it was caught by measuring. The side
  bank can't be checked this way and has to be judged by eye.
- **Measure the three directions against each other.** They come from separate calls and nothing
  makes them agree. A front that came back at 90 pixels against a side of 77 is a visible size jump
  when the character turns; reroll rather than rescale.

---

## Motion (all free, all in code)

**One hand-size constant, relative to BODY height — currently 0.17.** Never size the hand off the tool sprite:
that bug made the same hand 25% of body height while swinging and 17% while walking, so it grew the moment a
weapon was drawn.

- **Walk** — hands swing fore and aft *through* the body, opposite phase, extended on the stride frames and
  tucked at the hip on the passing frames, tilting with the direction of travel. The near hand draws over the
  torso, the far hand behind it and dimmed. Anchor to the **torso width at chest height**, measured once from
  the neutral frame — measuring per frame makes the hands jitter as the legs change the silhouette.
- **Run** — the same four frames played faster (90ms vs 150ms), but a **DIFFERENT HAND POSE, not the walk
  sped up.** The run is a real, approved motion — `RUN` settled 2026-07-29 ("RUN_r75.gif is fine, looks the
  best") and `FRONT_RUN` 2026-08-14 ("we will go with wisdest lowest"). It shares the walk's leg frames BY
  DESIGN and lives in the arm swing, fist size and timing; sharing legs is not a gap to be filled. Both fists visible *even side-on*, raised to **chest** height (~0.05 of body height above the
  torso row — 0.13 puts them over the face), rotated **~75° to point forward and held there** with only a
  small roll (~16°) on top, and bigger travel (0.62 vs the walk's 0.42). **No new art for running.**
  Reference render: `outfits/bronze/RUN_r75.gif`, owner-approved — match it, don't re-derive it.
  ⚠ Running the *walk* pose fast is the failure: its ±55° roll at running speed reads as **flapping**, and
  shipping that in the showcase was caught immediately.
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
**Five paid calls, everything else free**, in this order. Ask before each; stop and look at every render
before cutting it.

| # | call | canvas | reference | out |
|---|---|---|---|---|
| 1 | turnaround — 3 standing views | 1536x1024 | the two bases | `view_front/side/back.png`, snapped on ONE grid |
| 2 | front walk — 4 frames in a row | 1536x1024 | `view_front.png` | `front_1..4.png` |
| 3 | side walk | 1536x1024 | `view_side.png` | `side_1..4.png` (mirror at cut time) |
| 4 | back walk | 1536x1024 | `view_back.png` | `back_1..4.png` |
| 5 | gauntlets — character + hand column | **1024x1536** | template + hand strip | the five hands at 13px |

Then, free:
```bash
python3 tools/player_sprites/build.py steel        # every animation
python3 tools/player_sprites/preview_all.py        # both ALL_*.png pages
```

**Gate every cut on the numbers, not on a glance:** the three directions within a pixel or two of each
other, `check_alternation` clean on front and back, and the hands at exactly the height the walk asks for.
Each of those three has shipped broken while looking fine.

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
