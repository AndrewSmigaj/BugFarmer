# APPROVED player animations — the owner's decisions, with his words

Every file here was explicitly approved. The quote next to each is verbatim from the session where it
was chosen, with its timestamp, so there is no ambiguity about what "that's the one" referred to.

**This folder is the record. It should be in git.** These decisions were made on 2026-07-28/29 and were
never written down; the script that produced them lived in a temp directory and the art folder was
gitignored, so when the decisions were needed again they had to be reconstructed from session
transcripts. That must not happen a second time.

---

## The animations

| file | what it is | approved, verbatim |
|---|---|---|
| `01_WALK_front.gif` | walking, front-facing | *"first for walking forward gait_front_d3_bigger.gif is great"* — 2026-07-29 06:01 |
| `02_WALK_side.gif` | walking, side-on | *"walk b is fine"* — 06:06 |
| `03_RUN_side.gif` | running, side-on | *"RUN_r75.gif is fine, looks the best"* — 06:11 |
| `04_HAND_SHAPE_front_rot90.gif` | the chosen hand shape/orientation for the front view | *"ok lets do the 2 rot 90 one (the good one), it looks pretty good as is, that will work"* — 04:53 |
| `05_SWING_iteration7_best_for_SWORD.gif` | tool/weapon swing — best for the sword | *"for the sword iteration 7 is the best"* — 2026-07-29 20:43 |
| `06_SWING_iteration11_best_overall.gif` | tool/weapon swing — best overall so far | *"iteration 11 looks best"* — 23:37 |

Original filenames, for tracing: `GAIT_front_D3_bigger.gif`, `SWING3_walk_b.gif`, `RUN_r75.gif`,
`HANDS_front_shape_2_rot90_outward.gif`, `swing-design/iteration-7.gif`, `swing-design/iteration-11.gif`.

**The swings are not finished** — 7 and 11 are the best *so far*, not a final pick. Outstanding notes on
them: the axe should swing round in one arc without hovering cocked-back; the net is backwards (the hoop
is the opening and it should lead); the hoe should lift a little, strike the ground and pull rather than
whip; the shovel should jab straight down; the spear should be longer and two-handed.

## Standing / idle
**Not approved, because it was never made.** No idle animation was produced in that session. The tool at
rest sits at `IDLE_ANGLE = -35°`; there is no standing gif to point at.

## The back-facing walk
**Requested, never delivered.** *"so we have forward and sideways might as well finish with back"* (06:11)
— the session moved to tool swings instead.

---

## APPROVED 2026-08-01 — the two TOOL-GRIP hands (bronze)

These are the hands used **for holding tools and weapons only**. They are not the walking or running
hands — see the warning below.

| file | which arm | approved, verbatim |
|---|---|---|
| `outfits/bronze/hands/grip_back_of_hand.png` | the arm where you see the **back** of the hand | *"the first rows' grip does look good enough we can use it"* — the axe and hoe read right "because the knuckles are appropriately pointing down" |
| `outfits/bronze/hands/grip_palm.png` | the **other arm**, where you see the palm | *"For the other si[de] (the other arm so you would s[ee] the palm and knuckles) row 2 fist PALM is great"* |

Provenance so this can never be lost again: `grip_back_of_hand.png` is the **3rd hand of
`hands/candidates/set_a/result.png`**; `grip_palm.png` is the **4th hand of
`hands/candidates/set_b/result.png`**. Both cut with `compare_hands.cut_hands`.
Seen in context in `hands/candidates/hands_in_motion_row1_row2_grips.gif`.

### ⚠ THE GRIP HANDS ARE NOT THE WALK/RUN HANDS

> *"the weapon grabbing is NOT to be blindly replacing walk and/or running — they all should be
> carefully thought about and the best one picked"*

Every animation gets its own hand **and its own rotation**, chosen deliberately. Reusing the grip hand
for walking produced impossible poses, and he named them exactly:

- **walking** — fingers pointing *upward*. A hand hanging at the waist cannot point its fingers up.
- **running** — pointing *backward*, and *alternating between open and fist* between frames.

So the walk and run hands are still **UNDECIDED** and must be chosen separately. The grips above are
settled; nothing else is.

## The hands (`hands/`)

**Only the three sprites the animations actually use are kept here.** From `hand-D-pixel`, the set chosen
out of the A/B/C/D prompt comparison on 07-28.

| sprite | used by |
|---|---|
| `h1` — knuckles, back of hand | side walk + run (near fist) **and the tool swing** |
| `h2` — palm | side walk + run (far fist, dimmed and drawn behind the body) |
| `h3` — profile | front-facing walk |

Deliberately **not** here: `h4` (the fist closed round a pole) — nothing loads it — and the cut gauntlet
views `front/back/side/grip.png`, which are a re-cut made on 08-01 and were never approved. This folder
holds approved work only; anything unapproved living here is how the wrong sprite gets picked later.

**The tool-swing hand is the knuckles, not the grip.** The grip was chosen first —
*"for swinging tools 'grip' is fine"* (04:53) — and then superseded the same session:

> *"the correct hand would be **nuckles** but it has to go down at least 10 percent of the total width of
> the sword, then it needs to be rotated so that the nuckles are roughly the other way"* — 06:43
> *"**225 works** though keeping in mind thumb is on one side but yeah that works fine — soqn **+16%** so
> the last one"* — 06:48

Those two numbers are `HAND_ROT = 225` and `GRIP_EXTRA = 0.16` in `swing_lab.py`.

⚠ `bronze/gauntlet/{front,back,side,grip}.png` in the outfits folder were **overwritten on 2026-08-01 by
a bulk re-cut**, so those files are no longer the 07-28 originals. The source sheet
(`bronze/gauntlet/result.png`, 07-28) is untouched, so they are reproducible. The three sprites in this
folder are from `hand-D-pixel`, which was never overwritten.

## The motion parameters

Recovered verbatim and committed in `tools/player_sprites/gait.py`:

| | amp (×torso width) | rise | rotation | tilt | fist (×body H) | height down body | ms |
|---|---|---|---|---|---|---|---|
| walk | 0.52 | 0.013 | 0° | 22° | 0.17 | 0.60 (waist) | 150 |
| run | 0.58 | 0.032 | 75° | 14° | 0.19 | 0.46 (chest) | 90 |

Both fists swing through the body around the torso centre (measured once at 42% down the neutral frame);
the far fist is dimmed to 0.62 and drawn behind. Beat phase `[0.5, 0.0, 1.5, 1.0]`.

The **front** walk is a separate implementation, not the side one re-aimed: hands sit *outside* the body
edges, edges measured per frame at 0.62 down, one hand rises while the other drops (±0.15 of body span),
phase `[1, 0, -1, 0]`, left hand mirrored, neither rotated nor dimmed.

---

## 2026-08-04 — THE SWING: the hand travels, the tool follows

### What was wrong with every swing before this

> *"do people take a sword in their fist, hold their fist up to their shoulder and rotate their fist to
> swing it? ever?"* — 2026-08-04

No. And that is exactly what `swing_frames` did. It computed **one angle**, placed the **tool** at a fixed
small radius from the body centre, then stuck the hand onto the tool's grip. The tool led and the hand was
downstream of it, so the fist stayed parked beside the shoulder and **rotated in place** while the blade
swept round it like a clock hand bolted to his chest.

Every "fix" for weeks — iterations 1-12, the four "vertical" variants of this morning — retimed that same
motion. **Timing was never the problem.** `DESIGN.md` already said *"Drive the HAND, then hang the tool off
it"*; the renderer contradicted its own design doc and nobody checked.

### The model, settled

```
shoulder    a fixed point on the body
hand        shoulder + reach(t) x direction(t)              <- THE HAND TRAVELS
blade       held at a FIXED angle behind the arm            <- no wrist articulation
tool        placed so its measured grip lands on the hand   <- the tool FOLLOWS
```

`tools/player_sprites/swing_arm.py`.

### Decided today

| | value | his words |
|---|---|---|
| hand rotation | **`HAND_PERP = 180`** | *"hand perp 180"* — picked off `HAND_ROTATION_which_way.png`, which renders 0/90/180/270 side by side |
| wrist | **none** — blade at one fixed angle behind the arm for the whole swing | *"you dont need to have the wrist angle with respect to the pommel of the sword, its awkward"* |
| path | starts a little behind the head (128°), swings down to −74° | *"it should start a little behind the head and swing down"* |
| reach | **0.60 cells** | *"similar to far"* |
| two-handed | **both** approved grips — back of hand on one arm, palm on the other | the pair approved 08-01, one per arm |

**The "keep the hand near the shoulder" constraint is OVERTURNED.** `DESIGN.md` said *"keep the hand
within roughly a third of a cell of the shoulder"* because a fist out at arm's length was thought to look
detached with no arm drawn. That is what pinned the hand at the shoulder and made a real swing impossible.

> *"dont care about the arm missing, though it doesnt have to be realistic just out some"* — 2026-08-04

⚠ **`HAND_ROT = 225` and `GRIP_EXTRA = 0.16` belong to the OLD shoulder-pivot swing.** They were tuned when
the tool led. They are meaningless once the hand travels — do not carry them forward.

### ✅ THE OFFICIAL SWORD SWING — picked 2026-08-04

> *"they look great, do sword_1h_f4_back85 as the official one, but have it pull back a tad more at the
> end so the hand is at the hip not forward a little, you can also have tip slightly continue down more
> as you dow"*

F4 (blade 85° behind the arm) with the two changes he asked for. **Live in
`render_animations.arm_swing_frames` / `sword_motion`** — the sword no longer uses the old
shoulder-pivot `swing_frames`.

| | value | why |
|---|---|---|
| arm direction | **128° → −104°** | past straight-down, so the hand finishes **at the hip**, not out in front |
| blade behind arm | **85° → 52°** | decreasing, so the **tip keeps dropping** after the arm has stopped |
| reach | 0.60 cells | |
| hand rotation | `HAND_PERP = 180` | |
| duration | 0.30 s | |

Rendered: `reviews/2026-08-04-swing-official/` — `OFFICIAL_filmstrip.png` shows start → end, and the
last frame is the hand-at-hip pose he asked for.

### ✅ FACING DOWN AND FACING UP — picked 2026-08-04: **E_double_back**

> *"lets do double back for both, they seem good"*

Out across, then whipped back through the other way. Live in `render_animations.attack_frames` /
`DOUBLE_BACK`, rendered as `swing_sword_down.gif` and `swing_sword_up.gif`.

**The structural rule these settle:** a top-down attack is a sweep **across the body that passes THROUGH**
the tile being hit. It is **not** a thrust *along* the attack direction — doing that gave a reverse stab
(*"its a backwards stabby motion as in going the wrong way"*). Motions are written relative to `centre`
(−90 facing down, +90 facing up) and the arc **crosses** centre rather than ending on it.

**And an attack is a frame budget, not an eased sweep** (*"the user has to watch the play pull back the
sword the swing the sword, its not a video game swing"*):

| frames | | |
|---|---|---|
| 0 | anticipation | ONE frame — *"it really does not need that swing back"* |
| 1-4 | strike | the whole arc, with a blade trail |
| 5-6 | hold | sits on the exit pose — this is what reads as impact |
| 7-11 | recovery | eases home |

12 frames × 20 ms = **0.24 s**. The eased version measured 0.46 s.

### Still open

- Only the **sword** is done. Axe, hoe, net, shovel and spear still run the old shoulder-pivot
  approaches and are next in line to be rebuilt the same way.
- The swing has **no idle anchor** in this model — it starts with the sword already behind the head
  rather than coming from rest, so the game will pop on entry until `RestoreIdle` is reconciled.

---

## 2026-08-14 — the base-ladder picks, and the rule about prompts

### THE PROMPT RULE (this one caused everything below)

Owner, verbatim: *"I literally just want gpt to make 'copper armor' with 'open face helmet' and the things
to make it consistent and such… I dont want you to constrain gpt with your garbage descriptions, remember
the old copper armor one looked like a fucking mushroom the others huge barrels it was dumb."*

**A brief is the MATERIAL and nothing else.** No silhouettes, no helm shapes, no hems, no "reads as the top
of the ladder". The three options are left to the model:

```
1. your own design - decide for yourself what this armour looks like
2. a second design, clearly and obviously different from the first
3. a third design, clearly and obviously different from both of the others
```

The technical block stays — magenta, armless, face visible, silhouette-over-detail at 40px, hard edges.
Those are quality rules, not design direction. `FACE_SETS = "ALL"` supplies the open-face clause.

This had already been settled on 2026-08-05 for the ants and was broken anyway on 08-06, which cost 7 paid
calls and 21 rejected designs. It was then broken a second time on 08-14 by a **duplicate dict key** —
`platinum-r2` existed twice in `EXPLORATIONS`, so Python kept the later, directed one and silently
discarded the undirected entry. That roll is `explore/platinum-r2/` and is NOT to be used.

### The picks

| set | picked | where the art is |
|---|---|---|
| **copper** | option 1 of `copper-r3` | `explore/copper-r3/CHOSEN_copper.png` |
| **iron** | option 1 of `iron-r2` | `explore/iron-r2/CHOSEN_iron.png` |
| **platinum** | option 1 of `platinum-r4` | `explore/platinum-r4/CHOSEN_platinum.png` — *corrected 2026-09-26: the pick is `explore/platinum-r5/CHOSEN_platinum.png`; r4 holds the superseded option* |
| **fancy** | NOT PICKED YET | `explore/fancy/result.png` — three options waiting — *corrected 2026-09-26: picked in the second roll, `explore/fancy-r2/CHOSEN_fancy.png`* |

Copper needed three rolls: `copper` (directed, rejected), `copper-r2` (*"the copper is way too high res"*),
then `copper-r3` with the owner's own fix — *"perhaps we can then try to say keep the pixel density"* — which
anchors density to the attached reference rather than to a number. That line is what made it chunky.

### What is DONE and what is NOT

| | copper | iron | platinum | fancy |
|---|---|---|---|---|
| design picked | ✅ | ✅ | ✅ | ❌ |
| `CHOSEN_*.png` cut | ✅ | ✅ | ✅ | — |
| 12-frame sheet | ✅ `outfits/<n>/result.png` | ✅ | ❌ | ❌ |
| gauntlet | ⚠ generated, TOO SOFT | ⚠ same | ❌ | ❌ |
| sheet cut to 9 frames | ❌ | ❌ | ❌ | ❌ |
| hands cut to 5 roles | ❌ | ❌ | ❌ | ❌ |
| in `official.py` | ❌ | ❌ | ❌ | ❌ |

**The gauntlets need redoing.** Owner: *"the gauntlets need to have the same pixel density I dont want to
make slop."* Both came back smoothly shaded with no dark outline, unlike bronze's crisp hands. The fix is
the same trick that fixed copper: the gauntlet call already sends bronze's five approved hands as the shape
reference, and those *are* low-res cut sprites, so the prompt should anchor density to that reference.

### Other decisions made the same day

- **run_front** — the camera-facing run had no pose of its own (`FRONT_RUN` was byte-identical to `FRONT`
  apart from `ms`). Picked `W3_widest_lowest`, *"we will go with wisdest lowest"*. Numbers and the two
  rejected attempts: `reviews/2026-08-14-run-front-pump/DECISION.md`. **Shares numbers with `run_back`.**
- **swing while running** — picked half pump, *"half pump is the one"*.
  `reviews/2026-08-14-swing-while-running/DECISION.md`. Not built.

---

## 2026-08-15 — the generation pipeline changed. Approved: *"those are fine, so this approach works"*

Worked through on fire-ant. Renders, gifs and the reasoning:
`reviews/2026-08-15-fireant-v2/` (start at its `README.md`).

### One direction per call, not one sheet

The 3x4 twelve-frame sheet is **retired**. It never produced convertible pixel art — twelve cells leave
each figure about a twelfth of the canvas, the blocks come back too small to form a grid, and the render is
smooth with nothing to snap to. Repeated attempts to rescue it (a reference board, a template with
pre-placed masters and registration guides) fixed the scale drift but the model repainted rather than
edited: 22x75 pixel art in, 253x380 smooth out.

An outfit is now **five paid calls**: a three-view standing turnaround (the design lock), then one call per
walk direction with four frames in a row on a 1536x1024 canvas, then the gauntlets. Every direction is
seeded from its own view of the approved turnaround.

Measured on fire-ant: side 77, front 77.6, back 78.3 art-pixels — within a pixel of each other, all on
real grids.

### All four frames are used

`gait.CYCLE` is now `[1,2,3,4]`. Owner: *"we really should use the full animation frames unless there is a
reason not to (why replace 4 with 2? makes no sense)"*.

`[1,2,3,2]` was correct for the old sheet, whose frame 4 came back as a second copy of the same stride. On
the camera-facing banks of a one-direction render, frames 2 and 4 are the two DIFFERENT passing poses —
opposite leg leading — so playing frame 2 twice threw a real pose away. (On the side bank frames 2 and 4
still come back identical, 0 silhouette pixels differing, so both cycles render the same there.)

`build.NEUTRAL` is now a single value, 1 — every bank measures itself against frame 2, the feet-together
pose.

### Gauntlets are drawn at the size they are used

**13 pixels**, `round(77 * 0.17)` — the hand ratio is unchanged. The old hands were 20px and got squashed
to 13 at render time, deleting rows; now `gait._sz` is an identity for five of the six gaits (only
`run_side` scales, and it is a 1.15 upscale, which duplicates rows rather than deleting them).

The hand has to be BORN at 13. It cannot be shrunk to it — rescaling player art is banned, and the one
attempt to build a 13px reference by downscaling the 20px hands produced hands the model redrew as
rectangles.

**This is arithmetic, not prompt wording.** The model always draws a hand about 200 screen pixels tall, so
the hand's real-pixel size is `200 / grid`, and the grid is set by how tall the character is drawn. A
landscape canvas caps the character near 900px, pinning the grid at ~12 and flooring the hands at ~16. Four
phrasings were tried and returned 19.7, 19.5, 16.0, 19.3. The fix is a **portrait** canvas with the hands
stacked in a column beside the character: the character is drawn ~1400px, the grid goes to 18.5, and the
usual 200px hand lands on 13. Predicted 12.4 before spending; measured 12.1–14.1.

### Legs: the failure to check for

Two defects, both found by measuring rather than looking:

1. **Feet kicking out sideways** on the camera-facing walks — read as a dance. Owner: *"they are ridiculous
   like someone doing a russian dance"*. Fixed by asking for the step to be straight up and down with both
   feet under the hips, knees and feet forward, and a higher knee lift.
2. **Both stepping frames lifting the SAME leg.** Frames 1 and 3 both raised the left foot, so the cycle was
   tap-left, together, tap-left, together. Invisible in a still; wrong only once it loops. Owner: *"it is
   not correct in how it loops"*. `cut_walk_row.check_alternation` now tests this and must be run on the
   front and back banks every time. The side bank cannot be tested this way — in profile both feet are
   planted in a contact frame, and which leg leads is carried by shading, not silhouette.

### Also fixed

The magenta fringe. `pixelsnap.sample` medians all four channels together, so a cell straddling the
silhouette got a half-transparent *magenta* pixel. `cut_walk_row.sample_masked` takes each cell's colour
from the figure pixels only.

### Still open

- **Everything gets regenerated on this pipeline.** Owner: *"we are going to regenerate everything… it is
  new software, nothing old needs to be supported, all sprites will use the same pipelines."* bronze and
  blackant currently have three frames per bank and will not build until they are redone.
- `promote.py` and the skill's rule 3 still target a `scratchpad/` → `current/` layout that no outfit on
  disk uses (the real one is `tries/ frames/ gauntlet/ anim/`).
- `cut_outfit.cut_outfit()` and `cut_outfit.cut_gauntlet()` are the old sheet and hand-row cutters. Nothing
  but their own CLI calls them. The shared helpers in that module are still used.

### The files that approval refers to

Filed 2026-08-18, after the folder was left holding only 2026-08-01 work while the thing that was
actually approved sat in a review folder.

`APPROVED/2026-08-15-fireant-v2/` — the six gifs, the twelve real-pixel frames, the five hands.
Working copy `outfits/fireant-v2/` (was named `outfits/fireant-sidewalk/`, which is why it could
not be found; nothing referenced that name).

`APPROVED/README.md` is the index. Start there.

---

## 2026-08-18 — the camera-facing walk hangs its hands off the SHOULDER LINE

Owner, shown bronze, fire-ant and black-ant side by side: *"black ant is the only good one"*.

Every number placing a fist used to be a fraction of the whole silhouette — row 0.62 down the figure,
size 0.17 of total height. A percentage is not a place on a body: the headgear is not a constant share
of the figure (bronze's helm 19 of 68px, black-ant's 31 of 87, fire-ant's ant head **40 of 77**), so the
same 0.62 landed at the hip on bronze and at the ARMPIT on fire-ant, and the body's width there ran
0.73 / 0.70 / 0.61 of the shoulders — three different reaches.

Now measured against `gait.shoulder_line()`, the widest row across the torso, with the fist's OUTER
EDGE flush to the shoulder edge. **Black-ant is the calibration** — every constant was solved so it
renders as it did (front bank within 1px; its back bank moved more, see the review). The other two
moved to match it: reach 1.19 / 1.17 / 1.02 -> **1.09 on all three**, hand height 35% / 31% / 27% of
shoulders-to-feet -> **33% on all three**.

`FRONT` and `FRONT_RUN` in `official.GAITS` changed UNITS, not design. The side walk was not touched.

Renders and the full numbers: `reviews/2026-08-18-walk-hands/`.

---

## 2026-09-26 — gpt-image-2 for everything; whole outfits; the picks

Code-drawn art was tried (an art demo and a cleanup of the base) and rejected: *"they look terrible"*. Then,
verbatim:

> *"we will use gpt-image-2 for everything, just full outfits I guess as yours are really bad, so we were partway
> done with the outfits and we had planned regenerating all the world and item actual sprites with gpt-image-2 as
> it was a different pipeline and we did not use pixelsnap correctly like our new pipeline. anyways so that needs to
> be done at some point (the only thing done correctly are the outfits). It should be in the plans and backlog"*

> *"we were generating three different variants for each outfit, I would decide, then we created all the animation
> frames - you see in fireant there is a 'CHOSEN' png but you dont see it some of the others as we didn't do them all
> we just did one batch. we need to finish this but you need to figure and understand the entire procedure rather
> than just assuming/guessing and rushing. as it is most outfits and other things will be made after signing off on
> the GDD but you should know that (and with test batches so we can ensure you are doing it right)"*

> *"anything with CHOSEN has been picked, the others we still need to work through together, yes you can do a batch
> now"*

### What that settles
- **One pipeline for all art:** gpt-image-2 + pixelsnap, as the outfits are made. The 2026-08-15 note *"all sprites
  will use the same pipelines"* now covers world, item, bug, tile and UI art too.
- **Whole outfits** (with his "I guess" — the reason given was that the drawn-in-code pieces were bad).
- **The picks** — every design with a `CHOSEN_*.png` is picked:

| set | the pick |
|---|---|
| copper | `explore/copper-r3/CHOSEN_copper.png` |
| iron | `explore/iron-r2/CHOSEN_iron.png` |
| platinum | `explore/platinum-r5/CHOSEN_platinum.png` (the 2026-08-14 table below says r4 — it is r5) |
| steel | `explore/steel-r5/CHOSEN_steel.png` |
| leather | `explore/leather-r2/CHOSEN_leather.png` |
| beetle-shell | `explore/beetle-shell-r3/CHOSEN_beetle-shell.png` |
| gilded-steel | `explore/gilded-steel/CHOSEN_gilded-steel.png` |
| fancy | `explore/fancy-r2/CHOSEN_fancy.png` (the 2026-08-14 table below says "not picked" — the second roll was picked) |

  Already built from their picks: bronze (`bronze-r3`), fire-ant (`fireant-pair2`), black-ant (`ant-carapace-black4`).
- **The rest are worked through with him**: the explored-but-unpicked sets (wood, ranger, scorpion, the wasp /
  hornet / killer-bee thorn and stinger sets, glowworm, fisherman, swamp-gear) and everything never explored on this
  procedure.
- **Timing:** most outfits and other art are made after the GDD is signed off, with test batches first. One test
  batch approved now (copper).

### Later the same day — the side-walk wording, and running the copper batch
Rebuilding the procedure from the records (`tools/player_sprites/procedure.py`, which reproduces the three approved
outfits with no calls) found that when the walk prompt moved into code on 2026-08-18, the side view's first
paragraph changed from *"…all facing RIGHT."* — the words every approved side walk was made with — to *"…all seen in
right profile."*, which no paid call ever used. Asked: (a) keep "all facing RIGHT" (recommended), or (b) use "all
seen in right profile". Owner: *"whatever your recommendation is"* → **"all facing RIGHT"** (`outfits.WALK_FACING`).

The first copper call was stopped by Claude Code's own permission check for spending. Owner: *"yeah you can add it,
add it to the permissions"* — `Bash(python3 tools/player_sprites/procedure.py:*)` is allowed in his local
settings. Each batch is still asked for first; this only lets an approved batch run.
