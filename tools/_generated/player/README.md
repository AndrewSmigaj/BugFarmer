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
| `<outfit>/hands/grip_*.png` | **SWINGS ONLY** |

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
