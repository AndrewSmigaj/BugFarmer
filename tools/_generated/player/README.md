# Player art — start here

Everything for the player character and its outfits lives here.

**Open `gallery.html`** (double-click it) to see every outfit as it stands right now — all its animations,
how far along it is, and its candidate sheets. That is the answer to "what do we have". Regenerate with
`python3 tools/player_sprites/gallery.py`.

## The character

**Armless by design.** No sprite has arms. The hands are separate little fists moved and rotated in code,
so a walk, a run and a weapon swing cost no drawn art — and adding a new weapon costs no animation work.

**Outfits are whole sets, not modular pieces.** One 12-frame sheet per outfit (front, back and side walk
cycles, 4 columns each), generated in a single image so nothing drifts out of register.

> The old paper-doll pipeline this file used to describe — `suit.png`, Aseprite masking, cut `pieces/`
> published to `Resources/Player/layers/` — was **abandoned on 2026-07-28**. None of it exists any more.

## Folders

```
bases/            armless_front.png, armless_side.png   <- EXACTLY two files. The only source of a base.
outfits/<name>/   one folder per outfit. The bare character is just another outfit.
props/<name>/     non-character props (practice dummy, …)
APPROVED/         the owner's approved animations + DECISIONS.md, the record of what was agreed
explore/          early look-exploration sheets
reviews/<date>-<what>/   cross-outfit comparison sheets a decision was made from
archive/          superseded work from before 2026-08-06. Per-outfit archives are gone: tries/ + git
                  already keep every version, and a third system was one place too many.
gallery.html      generated. The thing to open.
```

> ⚠ **Anything you want the owner to LOOK at goes in the repo, never a temp folder.** The assistant runs
> in a VM; `/tmp/...` paths do not exist on his machine, so showing him one shows him nothing. Comparison
> sheets go in `reviews/<date>-<what>/` with a `README.md` saying what each image is, and the path quoted
> back to him starts `C:/Users/emily/BugFarmer/`. This has gone wrong repeatedly.

### Inside an outfit

**`tools/player_sprites/official.py` is the answer to "what are we using".** The build reads it and nothing
else — no directory scanning, no fallbacks, and a missing file stops the build naming it. Folders hold the
art; `official.py` says which art counts.

Every outfit has the same four folders. The names are fixed by the system, not chosen per outfit, so
"where are this outfit's hands?" has one answer for all thirty:

```
outfits/bronze/
  tries/<YYYY-MM-DD>-<what>/   every attempt, kept forever. THE BUILD NEVER READS THIS.
  frames/                      the chosen body frames
  gauntlet/                    the chosen hands — one per official.HAND_ROLES (there are FIVE)
  anim/                        rendered animations. build.py OWNS this folder and removes
                               anything official.py does not name.
```

**Choosing = COPY from `tries/` into place. Never a move.** The attempt stays where it was, so nothing is
consumed and nothing can be overwritten; git holds every prior state. This is why there is no `archive/`
per outfit any more — it was a third version system sitting next to `tries/` and git.

## How to work

1. **Generate candidates** into `tries/<date>-<what>/`. Paid; **ask first**.
2. **The owner picks one.**
3. **Copy it into place** — `frames/` or `gauntlet/` — and add or update the outfit's row in `official.py`
   with the date and his words verbatim.
4. **Build:**

   ```bash
   python3 tools/player_sprites/build.py --status   # what is official, what is pending
   python3 tools/player_sprites/build.py bronze     # frames -> animations
   python3 tools/player_sprites/gallery.py          # the page to open
   ```

An outfit is either complete and in `OUTFITS`, or listed in `PENDING` and **not built at all**. There is no
third state where it renders using another outfit's parts — which is exactly what the old fallback chain
did to 21 of 24 outfits.

`.claude/hooks/check_official_build.py` runs on pre-commit: it re-renders from `official.py` and compares
the actual GIF bytes, so committed art cannot drift from what is declared. (It replaced
`check_sprite_ledger.py`, which compared *filenames* against a hand-written `CURRENT.md` and never opened
an image — every animation could have been wrong and it would still have passed.)

**Deploying into the game** is separate and later; nothing under `_generated/player/` ships today. The game
loads `Resources/Player/layers/` via `CharacterComposer.cs`.

## The side row must face RIGHT

Everything downstream assumes it: the walk swings the near hand to `+x` as the forward one, and every
swing arcs toward `+x`. An outfit whose side row came out facing **left** therefore walks and swings
backwards. Copper and farmer both did.

```bash
python3 tools/player_sprites/flip_side.py copper farmer --go   # mirrors only side_*.png
```

**Check it by eye, in the gallery** — the face, visor slit or hat brim points the way the character
faces, and it must point right. **Do not automate this**: a centroid heuristic was tried and agreed with
a careful visual read on only 6 of 8 outfits, and a detector that is wrong a quarter of the time would
mirror sprites the wrong way, silently, across the whole set.

## Which hand each animation uses — THIS IS SETTLED, DO NOT SUBSTITUTE

Every outfit has **its own version of all five**, in `<outfit>/gauntlet/`, under the same five names —
`official.HAND_ROLES`. There is no per-outfit variation in the count or the naming.

| `<outfit>/gauntlet/…` | used by |
|---|---|
| `front.png` | knuckles / back of hand — walk + run, the **near** hand |
| `back.png` | palm — walk + run, the **far** hand (dimmed, drawn behind the body) |
| `side.png` | profile — walking **toward or away** from the camera |
| `grip_back.png` | **SWINGS ONLY** — the arm you see the back of |
| `grip_palm.png` | **SWINGS ONLY** — *"the other arm so you would see the palm"* |

The two grips are a **pair, one per arm**, approved together. A two-handed swing uses **both**. Never
mirror one to make the other — mirroring the back of a hand gives a mirrored back of a hand, never a palm.

> ⚠ **This is why nothing could copy bronze.** The gauntlet sheet only ever asked for FOUR hands, so no
> other outfit had a fifth, and `grip_palm` silently fell back to `grip_back`. Verified by comparing the
> arrays: **23 of 24 outfits held a two-handed tool with the same hand twice.** Bronze was the only one
> with a real pair — and its five lived in two other folders under different names (`APPROVED/hands/h1–h3`
> plus `hands/grip_*`), reached by a hardcoded exception in the loader. Bronze's are now copied into
> `outfits/bronze/gauntlet/` under the standard names; `APPROVED/hands/` stays as the approval record.

### The sword swing (settled 2026-08-04)

**The hand travels and the tool follows it.** Not the other way round — the old model rotated the *tool*
about a point near the body and stuck the hand on afterwards, so the fist sat by the shoulder and spun in
place. *"do people take a sword in their fist, hold their fist up to their shoulder and rotate their fist
to swing it? ever?"*

Arm **128° → −104°** (past straight down, so the hand finishes **at the hip**), blade **85° → 52°** behind
the arm (decreasing, so the **tip keeps dropping** after the arm stops), reach 0.60, `HAND_PERP = 180`.
`render_animations.sword_motion`; full record in `APPROVED/DECISIONS.md`.

**Facing down / facing up are separate attacks** (`swing_sword_down.gif`, `swing_sword_up.gif`), settled
2026-08-04 as **E_double_back**: out across, then whipped back through the other way. A top-down attack is
a sweep **across the body that passes THROUGH** the tile being hit — never a thrust *along* the attack
direction, which gives a reverse stab. 12 frames × 20ms = 0.24s: 1 anticipation, 4 strike (with a blade
trail), 2 hold, 5 recovery.

**A SHOVEL IS A LEVER HELD LOW — it is not a battering ram, and not held up by your face.** Two things the
rig could not express until `attack_frames` grew `pivot` and `second`:

- **`pivot`** slides the point the tool sits on the driving hand **up the shaft**. A sword pivots at the
  butt (`pivot=0`) and the whole weapon swings. A shovel is gripped partway along, and the motion is a
  **rotation about the LOW hand** — which barely moves — while the top hand swings. With `pivot=0` and both
  fists welded to the tool, the only thing the rig can do is slide the whole shovel forward.
- **`second`** places the other fist relative to that point. **Negative** puts it *behind*, toward the
  butt, which is where the top hand actually goes on a shovel.

**Hands stay LOW.** The arm aims steeply down (≈−55°) so the hands sit at **50-57% down the body** — waist
to hip — and the blade is brought back up to a shallow forward angle by a large `back`. Aiming near
horizontal from the shoulder (30% down) puts the hands at chest height, holding the shovel up by his face.

Check the lever numerically: between drive-in and lift the hand should move **almost nothing** while the
blade rotates a lot. Currently 0.11 cells of hand travel against 46° of blade rotation.

**THIS IS A BLOCK WORLD — aim the tool at the BLOCK IT IS ACTUALLY BREAKING.** Standing sideways, he digs
the block **beside** him, not the ground under his feet. Owner: *"this is a block based world so when
standing sideways you are digging dirt to the side of you not below you."* So the side-view shovel is a
roughly **horizontal** drive into the adjacent cell; a downward jab is the *facing-down* animation, which
breaks the block below. A cell is half his body height, so the block beside him spans his lower half —
aim a little under horizontal to land in it.

**Working tools start at the HIP**, close in, not already extended. The reach is the stroke.

**WHERE THE HANDS SIT — measure the sprite, do not assume.** Bronze's width profile: helmet to ~22% down,
shoulders ~30%, waist ~50%, legs below 65%. The shoulder pivot (`SHOULDER`, 0.40 cells above body centre)
lands at **30%** — correctly on the shoulder line. The character is **not** chibi; asserting that without
looking sent one whole pass in the wrong direction.

⚠ **The trap is aiming HORIZONTALLY from the shoulder**, which parks the hands at shoulder height, up by
his head. A two-handed spear sits at chest/waist, a bug-scoop at waist. **Thrusts and scoops aim BELOW
horizontal** (spear −20°). Check it by computing where the hand lands as a % down the body, not by eye:
spear 32-47%, net 48-57%, shovel 42-69%.

**Every attack holds at REST for 4 frames before looping** (`ATK_REST`) — without it a looping gif
ping-pongs and you cannot tell which direction the swing runs.

**`build()` RENDERS FROM `motions.py`. THERE IS NO SECOND SET OF NUMBERS.**

This was the root of a whole day of churn. `motions.py` recorded what the owner picked; `build()` had its
own constants and never imported it. Every pick got written into the record, hand-placed as a gif, and
then **silently overwritten by the next re-render** with the superseded motion — so approved things kept
coming back wrong. Owner: *"they are NOT using the official agreed on animations. why has this been so
convoluted and difficult?"*

Measured at the time, in bronze's own `current/anim/`: the sword was the agreed 320ms frame budget while
axe, hoe, net and shovel were all still the old shoulder-pivot approaches.

⚠ **A tool with no agreed motion is SKIPPED and reported as a GAP** — never falls back to an older one.
Silence was the failure mode, so a missing decision has to be loud. The spear correctly reports a gap on
all 24 outfits.

**Every tool now uses the hand-travels model**, each with its own verb: axe CHOPS (bites and stops), hoe
TILLS (chop then drag back), net CATCHES (hoop leads, then lifts to enclose), shovel DIGS (push in, lever,
lift, toss — not a swing at all), spear THRUSTS (cocked back, reach is the whole motion).

⚠ **Tool length is a parameter** — `attack_frames(scale=…)`. The spear is **1.9×** a cell; it sat at sword
length for weeks.

**Facing down and up are aimed differently, not just rotated** (`swing_facings.py`): the shoulder sits in
a different place in each view, the weapon draws **behind** him when he faces away, the facing-down swing
**stops in front** instead of carrying to the hip, and the blade has to unwind **further** when the arm
travels less — or the tip finishes pointing up at the end of a downward swing.

These are bronze's, and **every other outfit's gauntlet was generated from them**, so a non-bronze outfit
uses its own gauntlet in the same three roles: `front`→h1, `back`→h2, `side`→h3.

The two side-on hands tilt in **opposite** directions — each follows its own direction of travel.

> ⚠ **Never build an animation on the cut gauntlet views for an outfit that has approved hands.**
> `APPROVED/DECISIONS.md`: those cuts "are a re-cut made on 08-01 and were never approved... anything
> unapproved living here is how the wrong sprite gets picked later." All 264 animations were once built
> on them — bronze's walk used a discarded sprite and its swing used the tool-grip hand, which is for
> holding a handle. The approved reference gifs in `APPROVED/` are what a correct render looks like;
> compare against them before claiming an animation is right.

**All three sword swings run on the frame budget** (`attack_frames`), one spec per facing in
`SWORD_FACINGS`: `SWORD_SIDE` side-on, `DOUBLE_BACK` facing down and up. 1 anticipation, 4 strike with a
blade trail, 2 hold, 5 recovery, 4 at rest. The eased `sword_motion` path is no longer used for the sword.

**AGREED MOTIONS LIVE IN `tools/player_sprites/motions.py`, WHICH ONLY EVER GROWS.** The lab files
(`swing_tools.py` and friends) are scratch — their variants get overwritten every time a new idea is
tried, and nothing in them is durable.

⚠ **The spec IS the artifact, not just the gif.** Timestamped review folders stopped the *gifs* being
overwritten, but the **numbers that define a motion** had the same bug one level down and it went
unnoticed: each new variant replaced the last in the lab file, so a picked motion had to be dug out of git
history. Owner: *"after all this desperate trying to get you to get organized, you think its ok while
developing which animation to use in the game you are just throwing them away as we go?"*

Every lab run now also writes **`SPECS.json` beside its gifs**, so a review folder is self-describing and
any gif can be traced to its exact numbers without git archaeology.

**A picked motion is COPIED into `motions.py`, never edited in place.** Superseding one means adding the
replacement beside it and marking the old superseded.

**AGREED ANIMATIONS LIVE IN `outfits/bronze/current/anim/`, NOT IN A REVIEW FOLDER.** Bronze is the
reference outfit: motions are designed on it, then applied to the other 21 with their own gauntlets.

**The moment he says "this one", copy it there and add a `CURRENT.md` row the same day.** Everything under
`reviews/` is exploration — later runs regenerate it and it is not safe. Owner: *"these animations need to
stay somewhere so we can use them - we cant just willy nilly explore things and when i say 'this one' just
shrug and move on."*

`CURRENT.md` records, per animation, **the motion constant in code** that produces it as well as his
words, so it can be rebuilt from source alone rather than only existing as a gif.

⚠ `anim/` **is ledgered.** It was once excluded as derived output, on the assumption animations are just
regenerated from the frames. That is wrong: the **motion is the decision**. An agreed animation that is
not ledgered is exactly what went missing across 2026-08-04.

## Rules that keep getting broken

- **Never name a file for how it was made** — not `set_a`, `batch2`, `option_1`, or `result.png`. The batch
  folder carries the meaning (`2026-08-02-1344-woodland-cloak`) and its `RECORD.txt` holds the prompt.
- **Never bulk re-cut or bulk move.** Every bulk run against this folder has destroyed or hidden something.
  `migrate.py` is dry-run by default for exactly this reason.
- **Nothing is deleted.** Superseded work moves to `archive/`.
- **Ask before every paid image call.** The spend is unrecoverable.

Governed by the `player-sprites` skill (`.claude/skills/player-sprites/SKILL.md`); the format and the
owner-approved motion constants are in `docs/guides/art/CHARACTER_DESIGN_GUIDE.md`.
