# Where things go — the repo organization rule

Read this before creating a folder or saving a generated file. **One rule decides everything:**

> ## Is it a REUSABLE technique, or a specific PLACE (a zone)?
> - **Reusable technique** (a kind of thing used across zones — a building, a river, a cave, a block) →
>   organized **by feature**, under an `examples/<feature>/` area.
> - **A specific place** (the starting village, the underground passages, the desert) → organized
>   **by zone**, under that zone's folder.
> - **Game content** (every object/sprite that exists) → organized **by category**, under `catalog/`.

Both axes exist on purpose and cross-link: a *river* has a general guide AND a zone's concrete river. You
look at the general one when building a reusable thing, the zone one when working on that place.

**Do not invent new top-level buckets.** If something doesn't obviously fit, it's almost always a
technique (→ examples) or a place (→ a zone). When unsure, ask — don't make a new folder.

## The three mirrors of the rule
| What | General (reusable technique) | Zone-specific (a place) | Content |
|------|------------------------------|-------------------------|---------|
| **Docs** | `docs/guides/authoring/<feature>.md` | `docs/product/zones/<zone>.md` | — |
| **Previews** | `tools/_generated/previews/examples/<feature>/` | `…/previews/zones/<zone>/` | `…/previews/catalog/<category>/` |
| **Scenes (code)** | scene declares `PREVIEW = "examples/<feature>"` | `PREVIEW = "zones/<zone>/scenes"` | — |

## Previews — the four folders, nothing else
`tools/_generated/previews/` contains exactly:
- `catalog/<category>/` — every in-game object, by category (`furniture/`, `blocks/`, `nature/`, `bugs/`,
  `tiles/`…). Generated from the entity data by `tools/world/previews.py`; each group has a `_sheet.png`
  (all at a glance) **and** every object as its own `<id>.png`.
- `examples/<feature>/` — reusable technique demos (`buildings/`, `blocks/`, `roads/`, `water/`, …).
- `zones/<zone>/` — each zone: `full.png` + region crops + a `scenes/` folder of the vignettes that compose it.
- `player/` — player sprites + animations.

A scene renders to its `PREVIEW` folder (declared in the scene file); `tools/world/previews.py` is the one
command that rebuilds the catalog and all scenes. No html, no registry, no hand-typed output paths.

## Docs — general vs zone-specific
- General how-to (build a house, a river, a cave) → `docs/guides/authoring/<feature>.md`.
- A specific zone's design + implementation (the village's river system, its ecologist house) →
  `docs/product/zones/<zone>.md`, cross-linking the general guide it uses.
- `docs/product/` is split by kind: `architecture/`, `zones/`, `economy/`, `ecology/`, `design/`,
  `investigations/` (living queues `BACKLOG.md` + `art_needed.md` stay at the product root).

## Tools — by purpose, scripts find the repo root the same way
`tools/` CLI scripts live in `sprites/`, `world/`, `ecology/`, `netcode/`, `data/`. Shared libraries that
are *imported* (not run), like `make_scene`, stay at `tools/` root. **Every script finds the repo root the
same way** — walk up from `__file__` to the folder containing `.git` — so a script's folder location never
breaks its paths. Co-dependent scripts share a folder so their imports resolve when run.
