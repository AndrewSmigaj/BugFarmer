# Investigation: #2 placement preview lower than where the block lands (some blocks)
_status: READY TO IMPLEMENT · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** The placement **ghost** positions at the raw cell center (`CellToWorld(cellPos)`,
  `PlacementController.cs:174`) but the **real render** applies two extra shifts (`RenderOccupant`): a
  footprint-X centering (`:857`) and, for **bottom-pivot** occupants, a **Y baseline that raises the sprite to
  `cellY + 0.5·spriteHeightCells`** (`:868`). So a *tall, bottom-pivot* block renders higher than its ghost →
  the preview sits **lower** than the placement. 1-cell-tall and center-pivot blocks match → "not everything."
- **Fix:** compute the occupant's world position in ONE shared helper (the footprint-X + pivot-Y baseline) and
  call it from BOTH `RenderOccupant` and the ghost, so preview == placement by construction.
- **Certainty:** root cause **95%**. **Needs your decision:** none. **Status:** `READY`.

## 1. Issue
> "when placing a block (not everything) the preview is lower than where it actually gets placed."

## 2. Root cause (verified — the two positions diverge)
- **Ghost** (`PlacementController.UpdateGhostPreview:174`): `ghostPreview.transform.position =
  CellToWorld(cellPos)` — cell center only. (It DOES scale the ghost to target size, `:130-137`, so size
  matches — only the baseline differs.)
- **Render** (`TilemapManager.RenderOccupant`): `worldPos = CellToWorld(cellPos)`; then
  `worldPos.x += (footprint.x-1)*0.5*cellSize` (`:857`); then for `pivot.y≈0`:
  `worldPos.y = cellPos.y*cellSize + 0.5*spriteHeightCells*cellSize` (`:868`), where
  `spriteHeightCells = targetSize.y/16`.
- **Delta** (bottom-pivot): render is higher than the ghost by `(0.5·spriteHeightCells − 0.5)` cells → 0 for a
  1-cell sprite, growing with height. Plus an even-width X offset of half a cell. Center-pivot (`pivot.y=0.5`)
  blocks aren't shifted → no offset. Exactly matches "lower" + "not everything."

## 3. Recommendation
Extract a single `TilemapManager.OccupantWorldPos(cellPos, occupantId, dir)` that does the footprint-X shift +
the pivot-Y baseline, and use it in **both** `RenderOccupant` (replace the inline math) and
`PlacementController.UpdateGhostPreview` (replace the bare `CellToWorld`). One source of truth → ghost and
placement can't drift. (Same "one position helper" theme touches #13's ground-item baseline.)
- Determinism: none (pure client preview).
