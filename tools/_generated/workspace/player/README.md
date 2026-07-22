# `workspace/player/` — player character + wearables (WIP)

Active creation of player sprites and wearables (clothing / armor / hats / hair). The governing procedure is
the **player-sprites** skill (`.claude/skills/player-sprites/SKILL.md`); the as-built format is
`docs/guides/art/CHARACTER_DESIGN_GUIDE.md`. Where every generated thing lives: `tools/_generated/README.md`.

## The tiers
- **`refs/`** — durable references you generate/mask against: the locked base, the bald base, the green
  mannequin (`aipipe.common.make_mannequin`). Regenerable, but kept for convenience.
- **`in-progress/<slug>/`** — one folder per thing being made (e.g. `in-progress/copper_armor/`): the raw
  render, the pixelized/aligned pieces, and the masking working files. **"Make a new hat" starts here.**
- **`archived/`** — dated old experiments and superseded versions (e.g. `archived/2026-07_early_designs/`).

## Where the finished sprite goes (and how you polish it)
Publish the extracted, pixelized layers to **`Resources/Player/layers/{slot}/{id}_{dir}{_w1|_w3}.png`** (the
9 slots `CharacterComposer` reads). That is the single source of "current" — the game loads it, and you
**polish it by editing that file directly** (each layer PNG is already an isolated, transparent, true-pixel
piece). There is deliberately **no `current/` tier and no `.ase` master** here — a second copy of a shipped
sprite only drifts out of sync.

## Committed vs local
This `README.md` and `CATALOG.md` are in git (so the structure is visible in the repo). The WIP **images** are
gitignored — local-only. If a finished set should be backed up, it lives in `Resources/` (the game asset),
not here.
