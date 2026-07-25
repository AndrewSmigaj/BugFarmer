# Player art organization + governance

**Status: BUILT (2026-07-25).** This is the durable, committed record of the player-sprite / wearable
organization work — so it is NOT lost when the ephemeral `~/.claude/plans/` file gets cleaned up. If you (or a
future session) are picking this up: everything below is the source of truth. Do not "start from scratch."

## Goal
Make working on the player character + wearables (clothing / armor / hats / hair) smooth: (1) a workspace that
is easy to navigate — find the current one and the latest in-progress ones at a glance; (2) guardrails so the
assistant reads the conventions before touching player art instead of reinventing folders and making messes.

## The folder structure — where player art lives
`tools/_generated/player/` (gitignored except the structure docs). Full rules: `tools/_generated/player/README.md`.
- **`current/`** — a preview (`character.png`) of what's LIVE in the game + a note. The real game files are the
  layers in `BugFarmerClient/Assets/Resources/Player/layers/` (that's what the game loads — the single "current").
- **`in-progress/<item>/<YYYY-MM-DD_HHMM_label>/`** — active work, **per item, per dated attempt.** Newest date
  = the latest. Each attempt holds `suit.png` (the render to cut) + `pieces/` (the cut game pieces). Dated
  folders are deliberate: they kill the `copper_v2_final_ACTUAL` naming mess and make "which is newest" obvious.
- **`references/`** — the ONE shared `base` / `bald` / `mannequin` you mask against (not copied per attempt).
- **`old/`** — finished + abandoned / historical stuff, out of the way. Nothing was deleted in the reorg — all
  prior experiments live here.
- **`README.md`** (the map) + **`HOW_TO_ASEPRITE.md`** (the masking tutorial).

**Workflow:** open `in-progress/<item>/<newest-date>/`, open its `suit.png` + `references/base.png` in Aseprite,
cut pieces into that attempt's `pieces/`. When a set is approved → publish its pieces to `Resources/Player/
layers/`, refresh `current/`, and log which attempt went live in `current/README.md`.

## The governance (so it stays clean)
- **`player-sprites` skill** — `.claude/skills/player-sprites/SKILL.md`. The pipeline (aipipe: mannequin →
  masked gpt-image-1.5 render → align → pixelize → cut → compose) + the folder rules + the hard-won prompting
  learnings. A **read-gate** (`.claude/manifest.json`, `authoring_gates`) blocks editing `tools/player_sprites/**`
  until this skill is read — verified firing.
- **`scaffolding-review` skill** — `.claude/skills/scaffolding-review/SKILL.md`. How to safely change a
  skill / hook / manifest (the 7-dimension lens; sibling of `certainty-assessment`).
- **The `_generated/` map** — `tools/_generated/README.md` (every folder, who writes it, what's committed).
- **Org rule** — `docs/guides/authoring/ORGANIZATION.md` (rewritten to describe the real tree honestly).
- Pipeline code: `tools/player_sprites/aipipe/` (`common.py`, `pixelsnap.py`, `run_pilot.py`).

## What REMAINS (pick up here — nothing else lost)
1. **Publish the copper/silver armor.** The masking is in `tools/_generated/player/in-progress/{copper-armor,
   silver-armor}/`. Owner cuts the pieces in Aseprite → approves → publish pieces to `Resources/Player/layers/`
   + refresh `current/`. (No AI wearables are live in the game yet — the current player is still the old 16×32
   hand-authored base.)
2. **`_generated/` root tidy — owner call (ambiguous, not touched):** `scratch/` (~255 MB — has `blocks_FINAL`
   + contact sheets, so LOOK before deleting), `variants/` (~116 KB block variants), and
   `previews/{ui,title,brood,dug_experiment}` (where do non-catalog category renders belong? — an art-taxonomy
   decision).
3. **5 old design-spike scripts** — `tools/player_sprites/{generate,player_designs,player_designs2,
   vector_player,walk_candidates}.py`. Superseded (their outputs are in `player/old/`); can be deleted/archived.
4. **Crisp size-bump (owner-gated).** The pipeline works at 64×128 native but the game publishes 16×32. Bumping
   the published size is a separate integration — it touches `CharacterComposer.cs` + every layer's size; do it
   deliberately with the owner, not silently.
5. **`farmer_down.png` (36×44) vs the 16×32 composed player.** The remote-player sprite (`RemoteEntity.cs`) is a
   different size/style than the local composed character — a mismatch to reconcile eventually.
6. **(Future, optional)** extend the item → dated-attempt pattern to the other ~1000 sprites (objects / items /
   bugs) if a broader art-org pass is wanted. Scales; not in scope now.

## Commits (durable in git history)
The work landed across several commits on `feature/player-art-scaffolding` (the two skills + manifest gate; the
`_generated` map + `.gitignore`; the honest `ORGANIZATION.md`/`ARCHITECTURE.md` rewrite; and the player-folder
redo into `current`/`in-progress`/`references`/`old` with dated attempts). `git log` on that branch has them.
