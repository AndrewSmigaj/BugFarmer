# Bug Farmer

2D multiplayer farming/bug game. Unity client + Nakama (Go) server, with a Python
pipeline that generates the sprite/world art.

## How we work (every step)
Carefully review the plan and/or the code you're about to write to make sure it's correct
and well-designed. **Never guess — always read and verify the actual code involved** (the real
function, the real call site, the real data shape) before relying on how it behaves. This holds
for every step, not just the big ones.

**Always double-check sub-agent findings against the real code.** Sub-agents (Explore/Plan/etc.)
are great for breadth but can be wrong or imprecise — re-read the load-bearing claims in the actual
source before relying on them. (This has already caught a real agent error mid-task — a wrong claim
about when a swarm clears its prey target during a gnaw.)

## Build for quality — this is a real product, not a prototype
This is a serious indie game aiming for **professional, shippable quality**. Do NOT default to
bare-minimum or "prototype-first" work — prototyping then reimplementing the real thing wastes
time (you end up building every feature twice). For every feature:
- **Research best practices first.** Web-search how good 2D games actually do this (real
  techniques, modern approaches), then design something professional BEFORE writing code.
- **Aim for the bar of a polished commercial 2D game**, not a placeholder. When a cheap version
  and a good version both exist, build the good version once. (e.g. weather "fog" is layered
  scrolling noise + depth/parallax + light interaction, NOT a flat color tint.)
- **Take the time to design it properly** — you're run on high effort deliberately. Surface the
  design and trade-offs; don't silently ship the easy path or call something "modern" that isn't.
- **"Done" = professional-quality AND verified**, never "technically works."

## Repo map
- `BugFarmerClient/` — Unity 6 client (C#); all art lives under `Assets/Resources/`.
- `nakama/` — Nakama Go server (authoritative game logic) + canonical entity data.
- `tools/` — Python sprite/world pipeline (gen → clean → preview → publish), the test-zone
  generator (`tools/world/make_test_zone.py`), and the headless `.NET` netcode harness (`sync-harness/`).
  Art prompts are DATA: `tools/art/style.json` (global look) + `tools/art/catalog/*.json` (per-item).
  Zone/scene authoring: `tools/zonegen/` (builder + `features/` primitives + `scenes/`). Previews are
  plain PNG folders under `tools/_generated/previews/` (browse in a file explorer — no html):
  `catalog/<group>/` = every in-game object by category (rebuild: `python3 tools/world/previews.py`, generated
  from entity data so it can't drift); `zones/<zone>/` = each zone's full render + region crops + its
  composing `scenes/`. `tools/README.md` is the map of every script + where outputs go.
- `docs/` — `product/` (how the game works, incl. the GDD `game_design.md`) and `guides/`
  (`art/` = how sprites look & are made; `authoring/` = how to build zones/scenes — start at its `README.md`).
- `.claude/skills/` — task playbooks: `test-changes` (verify ANY change — every test/determinism gate),
  `frontier-sync` (wire a new deterministic bug-sim mechanic), `perf-tuning` (profile + optimize the sim),
  `ecology-tuning` (balance the bug food web), `bug-spawning` (why a zone has the wrong # of bugs —
  spawn paths, the walkability + stale-save gotchas, populate/reset/persist), `run-backend`
  (the Nakama/Postgres/Go stack), `add-object` / `regenerate-sprite` (world art), `author-zone` (zone/scene
  MECHANICS), `zone-craft` (zone/scene QUALITY — the craft loop: brief quotas, options, zone lenses,
  the CORRECTIONS.md owner-taste ledger; start here when a place must be INTERESTING, not just built),
  `economy` (items/stores/crafting/drops — the unified entity registry + the `catalogs/` map + coverage audit),
  `deep-investigate` (root-cause ONE reported problem → an evidence-gated findings + recommendation doc under
  `docs/product/investigations/`, NO fix — for working a playtest issue list rigorously),
  `certainty-assessment` (score a plan/design/just-built change → an evidence-anchored numeric certainty TABLE,
  MIN-aggregated; the scoring layer for the review machinery below — run it before claiming "done/verified/safe"),
  `thorough-research` (invoke for ANY "research / look up how X is done / how do good games do Y" task BEFORE
  designing — the anti-bare-minimum gate: agent fan-out + deep-read quotas + ≥4 scored candidates + an
  adversarial cold-critic loop until dry + self-verification of load-bearing claims; a half-search is a failure).

## Where things live
- **Repo organization rule (read before creating a folder or saving generated output):**
  `docs/guides/authoring/ORGANIZATION.md`. One rule — **reusable technique → `examples/<feature>`,
  a specific place → `zones/<zone>`, game content → `catalog/`** — mirrored across docs, previews, and
  scene code. **Don't invent new top-level buckets.** Previews = exactly `catalog/ examples/ zones/ player/`.
- World art (loaded by `key` at runtime): `Assets/Resources/{Objects,Tiles,Items,Bugs,Effects}/`.
- Player + player gear (hand-authored): `Assets/Resources/Player/`.
- Entity data is **canonical** in `nakama/data/entities/{occupants,placeables,items,crops}.json`
  — the Go server and every Python tool read only from there.
- The client's `Assets/Resources/Data/entities/` is **published output** — never hand-edit it;
  run `python3 tools/data/publish_entities.py` after editing the canonical JSON.

## Hard rules (the gotchas that bite)
- **Building/reworking a ZONE = invoke the `zone-craft` skill and clear ITS GATE first.** Before
  writing ANY zone/scene code you MUST produce + post: the BRIEF, the named LANDMARK-SCENE LIST
  (every interesting place is a crafted `place_*(b,ox,oy)` piece with its OWN preview under
  `previews/zones/<zone>/scenes/`), and 2-3 rendered OPTIONS per major feature. Build landmarks as
  crafted scenes (text-grids/rows), compose-in-place, then LENS PASS + LEDGER CHECK. **NEVER a
  monolithic prop-scatter `zone_*.py`** (the repeated failure). `dirt areas` = dirt-block MASSES with
  stone/ore CORES so digging finds things (caves.md Rule 4) — never a flat pure-dirt fill.
- **Zone orientation is FIXED: HIGH y = NORTH = top of every render; LOW y = SOUTH (= deep
  underground); x=0 = WEST, x=255 = EAST** (`zone.go`: "+Y = north"). Never re-derive it —
  sanity-check: `village_21_B`'s big lake is at (x=46, y=48) and IS in the SW quadrant. Getting
  this wrong has burned us 3×.
- **The GAME loads the SAVE, not the builder.** Editing a `zone_*.py` builder changes NOTHING
  in-game until you regenerate the save. After ANY zone-builder change you MUST re-`save()`
  (`--save`) AND verify the SAVED data north-up (`python3 tools/world/view_world.py <zone>` →
  look). A "fixed" builder with a stale save = the game silently loads the OLD/flipped zone.
  Never overwrite a committed zone without a temp-save + render check first.
- **Don't resize sprites by hand.** The runtime NEAREST-scales to `sprite_w × sprite_h`;
  `pixelclean.py`'s downscale is the only intended resize. See [object_pipeline.md](docs/guides/art/object_pipeline.md).
- **No `jq`** — decode the gpt-image-1 base64 with Python (curl-piped large base64 fails).
- **No ComfyUI** anywhere in the flow.
- **Even-width occupants need the footprint-X shift** (`worldPos.x += (footprint.x-1)*0.5*cellSize`),
  applied in both the game and `make_scene.py`, or they sit half a cell off-grid.

## Two pipelines (scoped by *what* you make — never a per-task choice)
- **A — gpt-image-1** for **all world art** (objects, occupants, tiles, items, bugs):
  `gen_sprites.py` → `pixelclean.py` → `make_scene.py`.
- **B — hand-authored** for **the player sprite + player gear only**:
  `generate_player_sprites.py` writes explicit RGBA grids (no API, no cleanup).

## Common commands
```bash
python3 tools/data/publish_entities.py                  # canonical entity JSON -> client (run after editing)
python3 tools/sprites/gen_sprites.py --keys <key> --dry-run # preview the prompt, no API spend
python3 tools/sprites/gen_sprites.py --keys <key>           # generate (default source = placeables.json)
python3 tools/sprites/pixelclean.py                         # clean sprites in place under Resources/
python3 tools/make_scene.py                         # render tools/_generated/previews/scene.png
```

## Entry points for an AI coder (start here)
- **Verify ANY change / run tests:** the `test-changes` skill — the single source of truth for every test
  gate (Go unit tests, headless sync-harness, the determinism / "are all players in sync" checks, Unity pass).
- **Understand the deterministic world + add a bug-sim mechanic:** `docs/product/architecture/architecture_swarm_sync.md`
  **§0 as-built quick reference** (the guarantee, the one invariant, the ledger-event glossary, the recipe),
  then the `frontier-sync` skill (the step-by-step recipe).
- **Performance — profile or optimize the sim:** the `perf-tuning` skill (run a profiled session, read the
  `current/index.html` dashboard, the safe-optimization discipline; sim-touching opts are determinism changes).
- **Any complex / risky / determinism change:** run it through `.claude/complex-change-review.md` (stages ×
  failure-modes + the BugFarmer invariant checklist) + `.claude/lenses.md` (review lenses) before coding.
- **Git workflow (how we branch/commit/merge):** `.claude/git-guidelines.md`.

## Find depth in
- `docs/product/architecture/ARCHITECTURE.md` — top-level architecture + index to all product docs.
- `docs/product/BACKLOG.md` — the live "what's next" queue (Now / Next / Later). The throwaway plan
  doc covers only the item we're actively working; the backlog is what persists between sessions.
- `docs/guides/art/object_pipeline.md` — canonical art/sprite pipeline (the one to read first).

## Keep the canonical docs in step with the code
When you finish a plan's work — before you call it done — reconcile the docs the change touched:
- **`docs/product/BACKLOG.md`** — move/remove the item you completed; add anything new the work surfaced.
- **The affected `docs/product/architecture_*.md`** — if behavior, data flow, or a contract changed,
  update that doc so it still describes how the game actually works.
- If nothing architectural changed, say so explicitly rather than skipping silently.

This is the project's weak point: docs drift because updates happen at a different time than the code.
Plan-completion is the reconciliation point.
