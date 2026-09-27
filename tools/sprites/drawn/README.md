# tools/sprites/drawn/ — REJECTED: not for game art

Pixel art drawn by Claude in code (shapes, one light, a master palette, outlines), built on 2026-09-26 when the
owner asked for it. The owner reviewed two rounds and rejected the approach:

- the art demo — `tools/_generated/player/reviews/2026-09-26-art-demo/` (`demo.py`, `palette.py`, `canvas.py`,
  `player.py`, `tiles.py`, `objects.py`, `items.py`, `bugs.py`, `ui.py`);
- a cleanup pass on the player base — `tools/_generated/player/reviews/2026-09-26-base-pass/` (`base_pass.py`,
  `base_palette.py`), also rejected.

The decision that followed: all art is made with gpt-image-2, with whole outfits. All game art — outfits, NPCs, world objects, items, tiles, bugs — goes through gpt-image-2 +
pixelsnap (the `player-sprites` skill; the top item of `docs/product/BACKLOG.md`).

This folder is kept as a record of what was tried. Do not use it to make or fix game art, and do not propose it
again. The GDD review page's walking beetle (`tools/gdd/build_page.py`) still reads the demo's beetle frames — it
is a save indicator on a work tool, not game art.
