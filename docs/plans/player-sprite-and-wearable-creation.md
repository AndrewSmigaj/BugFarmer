# Player sprite + wearable creation system

**Status: IN PROGRESS (record saved 2026-07-25).** The durable, committed record of the effort to build and use
a system for **creating the player character and its wearables**. Saved here (committed to git, clean name) so
it is NOT lost when the ephemeral `~/.claude/plans/` file gets cleaned up. Picking this up later: this is the
source of truth — do not start over from transcripts.

## What we're building (the actual goal — not "folder organization")
A repeatable way for a non-artist to produce the player character and **hundreds of wearables** (armor /
clothing / hats / hair) with consistent pixel art, plus the workflow to get them into the game. Parts:
- **The AI pipeline (`aipipe`)** — generate a wearable painted onto a recoloured *mannequin* of the locked base
  character, normalize it in code, pixelize it, cut it into per-slot pieces, compose. Model: gpt-image-1.5.
  Consistency comes from **constraint** (always painting onto the same locked base), not prompting. Full detail:
  the `player-sprites` skill (`.claude/skills/player-sprites/SKILL.md`); code in `tools/player_sprites/aipipe/`.
- **The masking workflow** — the owner cuts a rendered suit into game pieces in Aseprite, saves the pieces,
  approves them, and they get published into the game.
- **The workspace + guardrails** — a clean place to do the work + a read-gate so the assistant reads the
  conventions instead of reinventing folders. (This is the part that's *fully* built; it supports the above.)

## Where it stands
- **Pipeline:** built + working (`tools/player_sprites/aipipe/`: `common.py`, `pixelsnap.py`, `run_pilot.py`).
  The base character + bald base + hair + mannequin exist (in `player/references/`).
- **First wearables:** copper + silver armor sets are **in progress** — rendered, being masked into pieces.
- **Nothing is in the game yet** — the live player is still the old hand-authored 16×32 base; NO AI-generated
  wearable has been published to `Resources/Player/layers/` yet.
- **Workspace + governance:** built (below).

## The workspace — where the work lives
`tools/_generated/player/` (gitignored except the structure docs). Rules: `tools/_generated/player/README.md`.
- **`current/`** — a preview (`character.png`) of what's LIVE in the game. Real game files: `Resources/Player/layers/`.
- **`in-progress/<item>/<YYYY-MM-DD_HHMM_label>/`** — active work, **per item, per dated attempt** (newest =
  latest). Each attempt: `suit.png` + `pieces/`. Dated folders kill the `copper_v2_final_ACTUAL` naming mess.
- **`references/`** — the shared `base` / `bald` / `mannequin` you mask against.
- **`old/`** — finished / abandoned / historical (nothing was deleted in the reorg — it's all here).

## The governance (so it stays clean)
- **`player-sprites` skill** — the pipeline + folder rules. A read-gate (`.claude/manifest.json`) blocks editing
  `tools/player_sprites/**` until it's read (verified firing).
- **`scaffolding-review` skill** (`.claude/skills/scaffolding-review/SKILL.md`) — how to safely change a
  skill / hook / manifest.
- **The `_generated/` map** — `tools/_generated/README.md`. **Org rule** — `docs/guides/authoring/ORGANIZATION.md`.

## What REMAINS (the real work is mostly still ahead)
1. **Produce + publish the wearables.** Finish masking copper/silver (in `player/in-progress/`), then publish
   pieces to `Resources/Player/layers/` + refresh `current/`. Then keep going — the whole point is *hundreds*.
2. **Crisp size-bump (owner-gated).** The pipeline works at 64×128 native but the game publishes 16×32. Bumping
   the published size touches `CharacterComposer.cs` + every layer — a deliberate integration, not a silent one.
3. **`farmer_down.png` (36×44) vs the 16×32 composed player** — the remote-player sprite (`RemoteEntity.cs`) is a
   different size/style than the local composed character; reconcile.
4. **`_generated/` root tidy — owner call:** `scratch/` (~255 MB — has `blocks_FINAL` + contact sheets, LOOK
   before deleting), `variants/` (~116 KB), `previews/{ui,title,brood,dug_experiment}` (art-taxonomy question).
5. **5 old design-spike scripts** — `tools/player_sprites/{generate,player_designs,player_designs2,vector_player,
   walk_candidates}.py` (superseded; outputs in `player/old/`) — can be deleted.

## Commits
Landed across several commits on `feature/player-art-scaffolding` (the two skills + the manifest read-gate; the
`_generated` map + `.gitignore`; the `ORGANIZATION.md`/`ARCHITECTURE.md` rewrite; the player-folder layout with
dated attempts). `git log` on that branch has them.
