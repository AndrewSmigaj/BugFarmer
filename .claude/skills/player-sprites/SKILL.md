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
  bases/            armless_front.png, armless_side.png   <- EXACTLY two files. The only source of a base.
  explore/<run>/    every PAID run: result.png, RECORD.txt (prompt, model, references) and each reference
                    exactly as sent (ref_N_*.png). gen.py writes these; RUNS.txt lists every run.
  outfits/<name>/   frames/ gauntlet/ anim/  = what official.py points at
                    tries/<date>-<what>/     = attempts, cut and waiting for review (never read by the build
                                               unless the outfit is PENDING — see step 7)
                    archive/                 = superseded work. Nothing deleted, ever.
  APPROVED/DECISIONS.md   every decision, the owner's words verbatim
  gallery.html      generated. Open it to see every official outfit as it stands.
```
Folders are named for **what is in them**, never for how they were made. Looking for the bronze armour means
knowing it is called bronze — not knowing which run produced it. (Run folders under `explore/` are the exception:
they are named `<name>-<step>` and `-r2`, `-r3` for rerolls, because they record *attempts*.)

---

## Iterating on a sprite — READ THIS BEFORE MAKING OR MOVING ANYTHING

Sprites are not made once. They are **iterated**, the owner picks, and the pick has to survive the session.
Everything below exists because it didn't: variants named `set_a` / `batch2` / `profile_option_1`, dumped in
one folder, approvals never written down, and then neither of us could say what was current. That cost three
days and a day of approved work.

### What an outfit is made of

| part | produces | API? |
|---|---|---|
| `explore/<name>-*/` | the paid renders, one folder per call, each with its `RECORD.txt` | **paid — ask first** |
| `frames/` | the renders **cut** into `front_1..4` `side_1..4` `back_1..4` | free |
| `gauntlet/` | that outfit's five hands: `front back side grip_back grip_palm` | free (cut from a paid render) |
| `anim/` | the built gifs. `build.py` writes these; never hand-made. | free |

**Four frames per direction, always** — contact, passing, opposite contact, opposite passing, played
`[1,2,3,4]`. Frame 2 is the neutral the whole bank is measured against (`build.NEUTRAL`).

### The rules, in the order they get broken

1. **Never name a file for how it was made.** Not `set_a`, not `batch2`, not `option_1`, not `result.png`.
   The *batch folder* carries the meaning — dated and named for the idea — and `RECORD.txt` inside it holds
   the prompt. Today every candidate on disk is called `result.png`, which is most of why nothing is findable.
2. **Batch folders are `YYYY-MM-DD-HHMM-what-it-was`.** Year first so Explorer sorts them; no colons, Windows
   forbids them.
3. **Official = the owner's yes, then a copy, then `official.py`.** Only after he approves the review sheet:
   copy the attempt's `frames/` + `gauntlet/` into `outfits/<name>/` (whatever was there moves to `archive/`),
   add the outfit to `official.OUTFITS` with his words and the date, run `build.py <name>`, `gallery.py`, and
   record it in `APPROVED/DECISIONS.md`. **Recording is part of choosing** — a decision with no record is a
   decision that gets lost. (`promote.py` belongs to an older `current/` layout; none of the official outfits
   use it.)
4. **Quote the owner verbatim in the ledger.** Not your paraphrase of what they approved. Approvals sound like
   *"row 2 fist PALM is great"* and *"walk b is fine"* — the exact words are what makes it unambiguous later.
5. **Nothing is deleted or overwritten.** Superseded work moves to `archive/`. **Never bulk re-cut or bulk
   move** — every bulk run so far has destroyed or hidden something the owner was using. Show the list first.
6. **`explore/` and `tries/` are tracked in git.** Work in progress is real work. Decisions are not instant.
7. **One shape for every sprite.** The bare character is just another outfit. No special buckets.

### Seeing what you have
`python3 tools/player_sprites/gallery.py` regenerates `gallery.html` — every outfit's current animations and
frames, a progress board showing which stage each outfit is at, and per-outfit candidate comparison. Open it
before asking the owner to look at anything, and re-run it after any promotion.

`gallery_gif.py` renders that same grid, animated, into one `ALL_OUTFITS_ALL_ANIMATIONS.gif` — the version
that can be sent to someone.

`gen.py` is the **only** way to generate, and `procedure.py` / `outfits.py` call it for every paid step. Every
run writes `RECORD.txt` beside the result (prompt, model, references as sent, timestamp) and appends a line to
`RUNS.txt`. Nothing about a run lives in chat or in the assistant's head, because that is exactly what kept
getting lost — and it is why the procedure below could be rebuilt from the records.

## ⚠ ASK BEFORE EVERY PAID IMAGE CALL
The spend is unrecoverable and a wrong guess buys nothing. State how many calls and what each is for, then
wait. An earlier "use the API as needed" is **not** standing permission. Free work — compositing, cutting,
measuring, rendering previews — needs no permission, but say plainly which kind a result came from.

---

## Making an outfit — the procedure (proven 2026-08-15, approved)

Proven on fire-ant, then black-ant and bronze — owner: *"those are fine, so this approach works"* — and official
2026-08-18. The commands are `tools/player_sprites/procedure.py`; **`procedure.py verify` reproduces those three
runs with no image calls** (prompts word for word, references pixel for pixel, every committed frame and hand byte
for byte). Run it after touching any prompt, cutter or template.

| # | step | command | cost | the owner's part |
|---|---|---|---|---|
| 1 | three designs in one image | `outfits.py explore <name>` | 1 call | **picks one** — his words recorded |
| 2 | the pick | his figure, cropped from the render, saved as `explore/<run>/CHOSEN_<name>.png` | free | — |
| 3 | the pick in real pixels | `procedure.py grids <run> --option N` → judge → `procedure.py pick <name> <run> --pitch P` | free | — |
| 4 | turnaround (front, side, back) | `procedure.py turnaround <name>` → `views <name> --pitch P` | 1 call | looks |
| 5 | walks, one direction per call | `procedure.py walk <name> <view>` → `cutwalk <name> <view> --pitch P` | 3 calls | looks |
| 6 | the five hands | `procedure.py hands <name>` → `cuthands <name> --pitch P` | 1 call | looks |
| 7 | review, then official | a review sheet → **his yes** → copy into place → `official.py` | free | **approves** |

**Five paid calls per outfit after the pick** (turnaround, three walks, hands), plus rerolls. As run: bronze 5,
fire-ant 10 (plus research), black-ant about 14; the design step took 1–6 calls before a pick (copper 3, platinum 6).
A paid command **without `--go`** prepares its references in the run folder and prints the exact prompt, each
reference at the size the model will see, and the canvas — and spends nothing. `--go` only after the owner's yes.

**Timing (owner, 2026-09-26):** *"most outfits and other things will be made after signing off on the GDD … (and
with test batches so we can ensure you are doing it right)"*. The eight picked designs (`CHOSEN_*` — *"anything with
CHOSEN has been picked"*) go through steps 3–7 batch by batch, each asked for; everything else starts at step 1,
worked through with him.

### Step 1 — three designs
One call, 1536x1024, the `EXPLORE` template with three UNDIRECTED slots ("your own design…", "clearly different…"),
face visible, magenta; reference = the base (plus an existing `CHOSEN_*.png` when asking for variants of a picked
design). He judges from `preview_explore.py <name>` — the three large AND at game size on grass (`--ladder` for tier
rows). **The brief is his**: an undirected brief beat every directed one, and a brief with three dictated designs
was a waste of calls (see [[prompts-are-the-owners]]).

### Steps 2–3 — the pick, in real pixels
His figure is cut from the render at full size (`CHOSEN_<name>.png`). Step 3 converts it: the WHOLE render snapped
on ONE grid, split into its three designs, his cropped, magenta fringe cleaned → `explore/<name>-turnaround/CHOSEN_ref.png`.
`pick` finds which design he chose by locating `CHOSEN_<name>.png` in the render. The grid is chosen **by eye**
(below). For scale: bronze 27x68, fire-ant 23x76, black-ant 34x89; the bare base character is 25x62.

### Step 4 — the turnaround: one call, and it sets everything downstream
1536x1024, the ONLY reference is the pick in real pixels (sent enlarged ×14), prompt = `outfits.TURNAROUND` — the
approved text, identical for all three approved outfits. It carries no outfit name: the design rides entirely on
the reference. `gen.py` accepts it by exact match (its clauses are spelled differently); **change a word and it is
checked like any other prompt — and prompts are his: show him the diff first.** ⚠ It says *"The helmet is open-faced
but covers the whole head"*; for a design without a helmet (a cap, a hood), show him that sentence before the call.

Cut with `views --pitch P`: the three views on ONE grid, each cropped to its figure → `view_front/side/back.png`. The
side view is kept as drawn. Every later call for this outfit is seeded from one of these views, so the three
directions can only agree because they share this image — and nothing else forces them to: measure them against
each other anyway.

### Step 5 — the walks: one call per direction
1536x1024, reference = that direction's view (copied into the run folder as `CHOSEN_ref.png`), prompt =
**`outfits.walk_prompt(what, view)` — do not type one.** `what` is `outfits.OUTFITS[name][0]`; an outfit missing
from `OUTFITS` has no words yet — add them and show him before spending. Every sentence in the prompt is a defect
that shipped (`outfits.py` says which); it matches the August runs word for word except the knee sentence, changed
on his 2026-08-18 note.

- **Camera-facing views: the legs do not swing sideways.** The default is feet kicking out to either side, which
  reads as a dance (*"they are ridiculous like someone doing a russian dance"*).
- **Knee lift is MEDIUM-HIGH, and measured.** "Lift the knee HIGH" produced 13.8–19.8% of body height — owner,
  2026-08-18: *"its lifting the knees really high which is ok for running but not walking"*. `check_lift` warns
  outside 7–15%; it is a WARNING, not a fail — look at the render. ⚠ One leg set serves both walk and run
  (`walk_side` and `run_side` share `frames="side"`), so the walk's lift IS the run's lift.
- **The side frames must end up facing RIGHT** (`gait`'s wrist maths assumes +x). All three approved side walks came
  back facing LEFT whatever the prompt said; copper's (2026-09-26) came back facing RIGHT. So look, and tell `cutwalk`
  which way the render faces (`--faces left|right`); it mirrors a left-facing render at cut time — never after
  rendering, which puts the wrists on backwards.
- **Why one direction at a time:** a 3x4 twelve-frame sheet gives each figure a twelfth of the canvas, the blocks come
  back too small to form a grid, and the render is smooth with nothing to snap to. Four in a row gives each figure the
  room the turnaround had — the layout that converts every time.
- **Rerolls are asked for separately.** Two kinds were used: a fresh roll (new run folder, same prompt) for a size
  miss, and a **correction call** — the first roll's four snapped frames as the reference and a prompt naming what to
  fix — for a wrong cycle (fire-ant front/back r4, black-ant front/back r2). The correction wording is not a template
  yet; write it from those runs' `RECORD.txt` and show it first.

### Step 6 — the hands: one call, on a PORTRAIT canvas
1024x1536. Reference 1 = the template `procedure.hands_template()` draws: the front view at 1:1 on magenta with five
empty cyan boxes beside it, each exactly one hand tall. Reference 2 = the five hand SHAPES
(`explore/bronze-v2-gauntlet/REF_shapes.png`, bronze's pre-August hands, 20 px — what black-ant and bronze both
sent). Prompt = `outfits.hands_prompt(what, glove, blocks)`, the approved text with three slots: the outfit, what
the hands are made of (`OUTFITS[name][3]`), and the hand height in words.

The hand must be **exactly `round(front height × 0.17)`** — 12 for bronze's 68 px, 13 for fire-ant's 76, 15 for
black-ant's 91 — the size the walk shows it. It has to be BORN at that size: rescaling player art is banned. Getting
there is arithmetic, not wording: **the model draws a hand about 200 screen pixels tall** whatever you ask, so the hand
is `200 / grid` pixels, and the grid is set by how tall the character is drawn. On a landscape canvas that floors the
hands near 16 (four phrasings returned 19.7, 19.5, 16.0, 19.3). Portrait, with the hands stacked beside the
character, puts the grid near 18.5 and the hands on 13. The template also carries the character itself, which is what
makes "the same pixel density as the character" binding: both are drawn on one canvas. `cuthands` pads or trims at
the wrist to the exact height — never rescales — and says how many rows it touched.

### Step 7 — review, then official. Always.
*"we always want to review before updating anything official."* The cut attempt sits in
`outfits/<name>/tries/<date>-procedure/` (`frames/`, `gauntlet/`, and `CUTS.txt` saying which render and grid each
came from). To render it for review, list it in `official.PENDING` with `dir` = that attempt folder, then
`build.py <name>` (it renders a PENDING outfit only when named, into the attempt's `anim/`, and says so). Show him the
thing itself — the animations and a `review.pixel_proof` sheet — in `reviews/<date>-<name>/` with a README. **Only
after his yes:** copy into `outfits/<name>/`, move the entry from PENDING to OUTFITS with his words and the date,
`build.py <name>`, `gallery.py`, and a row in `APPROVED/DECISIONS.md`.

### The grid — chosen by eye, as it always was
**Pixel conversion is mandatory.** Snapping RECOVERS the pixels the model drew, at their true grid — it is not a
downscale, and downscaling player art is banned ([[player-sprites-are-pixelsnapped]]).
- **Snap the whole canvas on ONE grid, then split.** All figures in a render were drawn at one scale; per-figure
  detection disagrees with itself and the character shimmers.
- **Pass the grid explicitly.** `pixelsnap.detect_pitch` takes the largest grid scoring within 90% of the best
  (older comments said "smallest"; the code says largest), and it is still wrong often: 12.8 for bronze's 13.0, 10.9
  for black-ant's 10.25, 9.25 for a hands column whose grid was 18.5.
- **`procedure.py grids <run>`** scores every grid by how even each sampled cell is, and draws the quietest few side
  by side (plus their doubles — on a hands render the quietest is HALF the grid). Tested on the 16 approved cuts, the
  quietest is on or within 0.05–0.2 of the chosen grid for whole figures; it is a shortlist, not the answer. Judge the
  shortlist enlarged against the full-size render: at the true grid a 1-px feature stays 1 px (copper's two-pixel eyes
  came out doubled at 13.30, 13.45 and 13.50 and right at 13.35).

### Gate every cut on the numbers, not a glance
The three directions within a pixel or two of each other and of the turnaround (a front at 90 against a side of 77 is
a visible jump when he turns — reroll, never rescale); `check_alternation` clean on front and back (the model returns
cycles where both stepping frames lift the SAME leg — it looks fine in a still and wrong only in motion); the knee lift
in band or looked at; the hands at exactly the height the walk asks for. Each of these has shipped broken while
looking fine. The side cycle cannot be checked by numbers — look at it.

**A metal set earns its rung by COLOUR, not by shape** — at sprite size the silhouettes are identical, so "another
grey" is a wasted tier. Measure it: mean luma over the worn material of `front_1.png` ran iron 66 → steel 90 →
silver 113 → platinum 157. Judging this by eye once produced a confident wrong call.

### `gen.py` is the only way to spend
Every run writes `RECORD.txt` beside the result (prompt, model, references as sent, timestamp) and appends a line to
`RUNS.txt`. It enlarges every reference under 400 px ×14 before sending, refuses a character prompt missing a
mandatory clause (`NO ARMS`, `bare skin`, `MAGENTA`, `PIXEL DENSITY`; hands runs and the exact approved turnaround
excepted), and writes the result atomically — a failed call leaves no file that looks like a result.

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

## Pointers
- `tools/player_sprites/procedure.py` — the procedure's commands; `verify` reproduces the approved runs.
- `tools/_generated/player/APPROVED/DECISIONS.md` — every pick and approval, his words; `RUNS.txt` — every call.
- `docs/product/BACKLOG.md`, top item — where each outfit stands, and the world-art regeneration that reuses this.
- `docs/guides/art/CHARACTER_DESIGN_GUIDE.md` — the as-built format.
- `tools/player_sprites/demo_swings.py` — the motion preview. Imports `swing_lab.py` approach 6 (the
  designed swing) rather than copying it, so the preview cannot drift from the design.
- `docs/product/investigations/swing-design/` — why the swing is what it is: 10 sources, 5 iterations, the result.
- `docs/product/economy/catalogs/armor.md` — the canonical list of which sets exist and are planned.
