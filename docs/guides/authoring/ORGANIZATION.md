# Where things go — the repo organization rule

Read this before creating a folder or saving a generated file. Two parts: the **zone-authoring rule** (how
docs/previews/scenes for world-building are organized — stable and good) and the **`_generated/` tree** (whose
authority is `tools/_generated/README.md`, the map).

> This doc is a working convention, not scripture. If it's wrong or a better structure exists, the fix is to
> **correct this doc** (with a real reason) — not to contort the work to satisfy a stale rule.

## Part 1 — the zone-authoring rule (technique vs place vs content)
> ### Is it a REUSABLE technique, or a specific PLACE (a zone)?
> - **Reusable technique** (a kind of thing used across zones — a building, a river, a cave, a block) →
>   organized **by feature**, under an `examples/<feature>/` area.
> - **A specific place** (the starting village, the underground passages, the desert) → organized
>   **by zone**, under that zone's folder.
> - **Game content** (every object/sprite that exists) → organized **by category**, under `catalog/`.

Both axes exist on purpose and cross-link: a *river* has a general guide AND a zone's concrete river. You look
at the general one when building a reusable thing, the zone one when working on that place.

### The three mirrors of the rule
| What | General (reusable technique) | Zone-specific (a place) | Content |
|------|------------------------------|-------------------------|---------|
| **Docs** | `docs/guides/authoring/<feature>.md` | `docs/product/zones/<zone>.md` | — |
| **Previews** | `tools/_generated/previews/examples/<feature>/` | `…/previews/zones/<zone>/` | `…/previews/catalog/<category>/` |
| **Scenes (code)** | scene declares `PREVIEW = "examples/<feature>"` | `PREVIEW = "zones/<zone>/scenes"` | — |

A scene renders to its `PREVIEW` folder (declared in the scene file); `tools/world/previews.py` is the one
command that rebuilds the catalog and all scenes.

## Part 2 — the `_generated/` tree (authority: `tools/_generated/README.md`)
`tools/_generated/` holds more than zone previews — read its README before saving generated output. It's
organized by **what each thing is + its lifecycle**, not one flat rule:
- **`previews/`** — deterministic VIEWS of committed art you look at: `catalog/`, `examples/`, `zones/` (the
  three mirrors above). A few category renders (`ui/`, `title/`, …) also live here and don't fit the three
  cleanly — an acknowledged open tidy item, not a pattern to copy. (This replaces the old "exactly four
  folders, nothing else" claim, which the tree never actually satisfied.)
- **`player/`** — the player character + wearable art work (WIP creation). A first-class home, NOT a "preview."
- **`raw/`, `ab/`, `blocklab/`** — paid render caches (don't delete).
- **`ecology_charts/`** — non-art sim output (the only git-tracked subset).
- **`footprints.md`** — a generated reference.

Scripts DO hand-type their output path (`ui_sprites.py` → `previews/ui/`, etc.) — that's fine; the MAP records
where each writes.

### Player art lives in `player/`, not a previews mirror
Player character + wearables are made in `tools/_generated/player/`: `current/` (a preview of the live look),
`in-progress/<item>/<YYYY-MM-DD_label>/` (per-item, dated attempts), `references/`, `old/`. The FINISHED sprite
lives with every other sprite at `Resources/Player/layers/{slot}/{id}_{dir}.png` (the game's copy — polish it
directly). There is no `previews/player/` mirror. (Governed by the **player-sprites** skill; start at
`tools/_generated/player/README.md`.)

## Docs — general vs zone-specific
- General how-to (build a house, a river, a cave) → `docs/guides/authoring/<feature>.md`.
- A specific zone's design + implementation (the village's river system, its ecologist house) →
  `docs/product/zones/<zone>.md`, cross-linking the general guide it uses.
- `docs/product/` is split by kind: `architecture/`, `zones/`, `economy/`, `ecology/`, `design/`,
  `investigations/` (living queues `BACKLOG.md` + `art_needed.md` stay at the product root).

## Tools — by purpose, scripts find the repo root the same way
`tools/` CLI scripts live in `sprites/`, `world/`, `ecology/`, `netcode/`, `data/`. Shared libraries that are
*imported* (not run), like `make_scene`, stay at `tools/` root. **Every script finds the repo root the same
way** — walk up from `__file__` to the folder containing `.git` — so a script's folder location never breaks
its paths. Co-dependent scripts share a folder so their imports resolve when run.

## The one rule that still holds
**Don't invent a new top-level bucket casually.** If something doesn't obviously fit, it's almost always a
technique (→ `examples`), a place (→ a zone), content (→ `catalog`), or player-art WIP (→ `player/`). When
genuinely unsure, ask — or, if the honest answer is that this doc is missing a category, add it here with a
reason.
