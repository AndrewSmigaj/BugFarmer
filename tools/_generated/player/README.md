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
archive/          superseded work. Nothing is deleted, ever.
gallery.html      generated. The thing to open.
```

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

## Rules that keep getting broken

- **Never name a file for how it was made** — not `set_a`, `batch2`, `option_1`, or `result.png`. The batch
  folder carries the meaning (`2026-08-02-1344-woodland-cloak`) and its `RECORD.txt` holds the prompt.
- **Never bulk re-cut or bulk move.** Every bulk run against this folder has destroyed or hidden something.
  `migrate.py` is dry-run by default for exactly this reason.
- **Nothing is deleted.** Superseded work moves to `archive/`.
- **Ask before every paid image call.** The spend is unrecoverable.

Governed by the `player-sprites` skill (`.claude/skills/player-sprites/SKILL.md`); the format and the
owner-approved motion constants are in `docs/guides/art/CHARACTER_DESIGN_GUIDE.md`.
