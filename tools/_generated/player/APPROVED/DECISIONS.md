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

## The hands (`hands/`)

`h1`–`h4` are `hand-D-pixel`, the set chosen out of the A/B/C/D prompt comparison on 07-28.
`front/back/side/grip.png` are the cut gauntlet views the animation code actually loads.

| sprite | used by |
|---|---|
| `h1` / `front` — knuckles, back of hand | side walk + run (near fist) **and the tool swing** |
| `h2` / `back` — palm | side walk + run (far fist, dimmed and drawn behind the body) |
| `h3` / `side` — profile | front-facing walk |
| `h4` / `grip` — closed round a pole | **nothing currently loads this** |

**The tool-swing hand is the knuckles, not the grip.** The grip was chosen first —
*"for swinging tools 'grip' is fine"* (04:53) — and then superseded the same session:

> *"the correct hand would be **nuckles** but it has to go down at least 10 percent of the total width of
> the sword, then it needs to be rotated so that the nuckles are roughly the other way"* — 06:43
> *"**225 works** though keeping in mind thumb is on one side but yeah that works fine — soqn **+16%** so
> the last one"* — 06:48

Those two numbers are `HAND_ROT = 225` and `GRIP_EXTRA = 0.16` in `swing_lab.py`.

⚠ `bronze/gauntlet/{front,back,side,grip}.png` were **overwritten on 2026-08-01 by a bulk re-cut**. The
copies here are that re-cut, not the 07-28 originals. The source sheet (`bronze/gauntlet/result.png`,
07-28) is untouched, so they are reproducible, but they are not byte-identical to what was approved.

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
