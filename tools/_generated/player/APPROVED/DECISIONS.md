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
