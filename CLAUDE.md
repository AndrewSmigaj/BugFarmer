# Bug Farmer

2D multiplayer farming/bug game. Unity client + Nakama (Go) server, with a Python
pipeline that generates the sprite/world art.

## How we work (every step)
Carefully review the plan and/or the code you're about to write to make sure it's correct
and well-designed. **Never guess — always read and verify the actual code involved** (the real
function, the real call site, the real data shape) before relying on how it behaves. This holds
for every step, not just the big ones.

## Repo map
- `BugFarmerClient/` — Unity 6 client (C#); all art lives under `Assets/Resources/`.
- `nakama/` — Nakama Go server (authoritative game logic) + canonical entity data.
- `tools/` — Python sprite/world pipeline (gen → clean → preview → publish), the test-zone
  generator (`make_test_zone.py`), and the headless `.NET` netcode harness (`sync-harness/`).
- `docs/` — `product/` (how the game works) and `guides/` (how to operate the pipeline).
- `.claude/skills/` — task playbooks (`add-object`, `regenerate-sprite`, `run-backend`).

## Where things live
- World art (loaded by `key` at runtime): `Assets/Resources/{Objects,Tiles,Items,Bugs,Effects}/`.
- Player + player gear (hand-authored): `Assets/Resources/Player/`.
- Entity data is **canonical** in `nakama/data/entities/{occupants,placeables,items,crops}.json`
  — the Go server and every Python tool read only from there.
- The client's `Assets/Resources/Data/entities/` is **published output** — never hand-edit it;
  run `python3 tools/publish_entities.py` after editing the canonical JSON.

## Hard rules (the gotchas that bite)
- **Don't resize sprites by hand.** The runtime NEAREST-scales to `sprite_w × sprite_h`;
  `pixelclean.py`'s downscale is the only intended resize. See [object_pipeline.md](docs/guides/object_pipeline.md).
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
python3 tools/publish_entities.py                  # canonical entity JSON -> client (run after editing)
python3 tools/gen_sprites.py --keys <key> --dry-run # preview the prompt, no API spend
python3 tools/gen_sprites.py --keys <key>           # generate (default source = placeables.json)
python3 tools/pixelclean.py                         # clean sprites in place under Resources/
python3 tools/make_scene.py                         # render tools/_generated/previews/scene.png
```

## Find depth in
- `docs/product/ARCHITECTURE.md` — top-level architecture + index to all product docs.
- `docs/product/BACKLOG.md` — the live "what's next" queue (Now / Next / Later). The throwaway plan
  doc covers only the item we're actively working; the backlog is what persists between sessions.
- `docs/guides/object_pipeline.md` — canonical art/sprite pipeline (the one to read first).

## Keep the canonical docs in step with the code
When you finish a plan's work — before you call it done — reconcile the docs the change touched:
- **`docs/product/BACKLOG.md`** — move/remove the item you completed; add anything new the work surfaced.
- **The affected `docs/product/architecture_*.md`** — if behavior, data flow, or a contract changed,
  update that doc so it still describes how the game actually works.
- If nothing architectural changed, say so explicitly rather than skipping silently.

This is the project's weak point: docs drift because updates happen at a different time than the code.
Plan-completion is the reconciliation point.
