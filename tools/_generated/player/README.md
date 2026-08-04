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
archive/          superseded work. Nothing is deleted, ever.
gallery.html      generated. The thing to open.
```

> ⚠ **Anything you want the owner to LOOK at goes in the repo, never a temp folder.** The assistant runs
> in a VM; `/tmp/...` paths do not exist on his machine, so showing him one shows him nothing. Comparison
> sheets go in `reviews/<date>-<what>/` with a `README.md` saying what each image is, and the path quoted
> back to him starts `C:/Users/emily/BugFarmer/`. This has gone wrong repeatedly.

### Inside an outfit

Every outfit has the same three folders, whatever stage it is at:

```
outfits/bronze/
  scratchpad/          IN PROGRESS. One folder per batch, dated and named for the idea.
    1-candidates/        whole 12-frame sheets — pick one            (paid: ASK FIRST)
    2-frames/            the picked sheet cut into front/side/back   (free)
    3-gauntlets/         that outfit's hands                         (paid: ASK FIRST)
  current/             WHAT WE AGREED ON. The answer to "what are we using".
    CURRENT.md           what it is, when agreed, the owner's words, which batch it came from
    front_*.png side_*.png back_*.png
    gauntlet/
    anim/                the rendered animations — DERIVED, regenerated on every promotion
  archive/             superseded currents
```

To see what an outfit looks like right now, open its `current/`. That is the whole rule.

## How to work

1. **Generate candidates** — several whole sheets for one outfit. Paid; ask first.
2. **The owner picks one.**
3. **Cut it** into front/side/back frames. Free.
4. **Generate the gauntlets** for that outfit. Paid; ask first.
5. **Promote** — and promoting *is* recording:

   ```bash
   python3 tools/player_sprites/promote.py bronze scratchpad/2-frames/2026-08-02-1344-first-cut \
       "ok lets use this one moving forward"
   ```

   That copies into `current/`, moves what it replaced into `archive/`, writes the `CURRENT.md` row with the
   owner's words verbatim, re-renders the animations and refreshes the gallery. There is no way to promote
   without recording, because recording as a separate step is what kept getting skipped.

6. **Deploying into the game** is separate and later — `deploy.py`, which stamps the date in `CURRENT.md` so
   "agreed" and "in the game" stay distinct.

`check_sprite_ledger.py` runs on pre-commit and fails the commit if `CURRENT.md` and `current/` disagree.

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

| sprite | used by |
|---|---|
| `APPROVED/hands/h1.png` | knuckles / back of hand — walk + run, the **near** hand |
| `APPROVED/hands/h2.png` | palm — walk + run, the **far** hand (dimmed, drawn behind the body) |
| `APPROVED/hands/h3.png` | profile — walking **toward or away** from the camera |
| `<outfit>/hands/grip_back_of_hand.png` | **SWINGS ONLY** — the arm you see the back of |
| `<outfit>/hands/grip_palm.png` | **SWINGS ONLY** — *"the other arm so you would see the palm"* |

The two grips are a **pair, one per arm**, approved together. A two-handed swing uses **both**. Never
mirror one to make the other — mirroring the back of a hand gives a mirrored back of a hand, never a palm.

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

## Rules that keep getting broken

- **Never name a file for how it was made** — not `set_a`, `batch2`, `option_1`, or `result.png`. The batch
  folder carries the meaning (`2026-08-02-1344-woodland-cloak`) and its `RECORD.txt` holds the prompt.
- **Never bulk re-cut or bulk move.** Every bulk run against this folder has destroyed or hidden something.
  `migrate.py` is dry-run by default for exactly this reason.
- **Nothing is deleted.** Superseded work moves to `archive/`.
- **Ask before every paid image call.** The spend is unrecoverable.

Governed by the `player-sprites` skill (`.claude/skills/player-sprites/SKILL.md`); the format and the
owner-approved motion constants are in `docs/guides/art/CHARACTER_DESIGN_GUIDE.md`.
