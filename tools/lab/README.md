# Design Lab — local dev server for picking art in real scenes

A small local web app for choosing art variants by **seeing them in the actual game scenes**, then setting
them live with one click. It is the single, organized home for this workflow (and is built to grow into
item-icon and zone-layout design — see "Extending" below).

## Run it
```bash
python3 tools/lab_server.py          # renders the scenes once, then serves
# open http://localhost:8765
```
(Stdlib only — no pip installs. Ctrl-C to stop.)

## How it works
- **One set of scenes.** On start it renders the real scene scripts (caverns, mining_camp, underground_house,
  cliff, houses, desert) to `tools/_generated/previews/` — the *same* previews folder we already use — and
  records each swappable block/tile's exact draw position.
- **Pick.** In the browser: choose a scene, zoom, and for each block/tile step its approach/variant. The
  scene redraws live (the chosen variant is overlaid at the recorded positions, **back-to-front** so things
  in front occlude correctly).
- **Apply.** The green **Apply** button promotes every chosen variant to the **live game sprite**
  (`Resources/Objects|Tiles/<key>.png`, `.meta` patched) **and re-renders the previews** — so the previews
  always reflect the current selection.
- **Remembered.** The selection is saved to `tools/_generated/blocklab/selection.json` and loaded on open,
  so reopening shows what's currently chosen/live.

## Where things live
- `tools/lab_server.py` — the server (state, render, promote, `/api` routes, static serving).
- `tools/lab/index.html` — the web app (the picker UI).
- `tools/_generated/blocklab/<approach>/`, `…/tiles/` — the candidate variants (made by `tools/blocklab.py`).
- `tools/_generated/blocklab/selection.json` — the persisted current selection.
- `tools/_generated/previews/` — the rendered scenes (the one preview set).

## Add more variants
`python3 tools/blocklab.py --blocks <key>` writes new variants into the approach folders; restart the server
to pick them up. (Tiles like `cave_floor` live in `blocklab/tiles/`.)

## Extending (item / zone design later)
The server is structured for it: add a new `/api/...` route + a page/tab in `index.html`. The render +
promote + selection-persistence pieces are already factored as functions in `lab_server.py`, so an
item-icon lab or a zone-layout lab slots in alongside the variant picker without a rewrite.
```
GET  /api/state        -> scenes (+ draw rects), variants, saved selection
POST /api/apply        -> promote selection to live sprites + re-render previews + persist
GET  /scene/<file>     -> a rendered preview PNG
GET  /variant/<path>   -> a candidate variant PNG
```
