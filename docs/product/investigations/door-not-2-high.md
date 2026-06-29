# Investigation: #1 door is not 2 blocks high
_status: READY (data fix; 1 small ambiguity — which door) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Pure data inconsistency across the 3 door placeables. Render height = `sprite_h / 16` cells:
  - `door_iron` — 16×32, footprint `[1,2]` → **1 wide × 2 tall** ✅ (the correct doorway).
  - `door_wood` — 32×32, footprint `[2,1]` → **2 wide × 2 tall** (a double-wide door; footprint looks
    transposed vs door_iron — `[2,1]` blocks 2-wide × 1-deep).
  - `door_square` — 16×24, footprint `[1,1]` → **1 wide × 1.5 tall** ❌ (genuinely < 2 high).
- **Most likely what you placed:** `door_wood` (the basic door) reads wrong because it's 2-wide with a 1-deep
  footprint, or `door_square` because it's only 1.5 cells tall. Either way it's the size data, not code.
- **Fix:** standardize doors to the `door_iron` shape — **sprite 16×32, footprint `[1,2]`, pivot bc** — so a
  door is 1 wide and 2 tall and blocks both vertical cells. (Regenerate door_wood/door_square art at 16×32 if
  kept; door_wood may be intentionally a double door — confirm.)
- **Certainty:** data measurements **98%** · which door you meant **~70%**. **Needs your decision:** is
  `door_wood` meant to be a single (1-wide) or double (2-wide) door? **Status:** `READY` (data).

## 1. Issue
> "Door is not 2 blocks high."

## 2. Evidence
Render height comes from `sprite_h` (`TilemapManager.RenderOccupant`: `spriteHeightCells = targetSize.y/16`,
baseline at `cellY + 0.5·spriteHeightCells`). Measured from `placeables.json` + the PNGs:
| door | sprite_w×h | footprint [w,deep] | renders | verdict |
|---|---|---|---|---|
| door_iron | 16×32 | [1,2] | 1w × 2h | correct doorway |
| door_wood | 32×32 | [2,1] | 2w × 2h | 2-wide; footprint transposed vs iron |
| door_square | 16×24 | [1,1] | 1w × 1.5h | too short (< 2 high) |

## 3. Recommendation
Pick the canonical door shape = **16×32, footprint `[1,2]`** (door_iron). Bring door_square up to it
(`sprite_h 24→32`, footprint `[1,1]→[1,2]`, regenerate art). Decide door_wood: if it's a single door, set it
to 16×32 / `[1,2]` and regenerate at 16 wide; if it's intentionally a double door, leave width but fix the
footprint to `[2,2]` so it blocks both vertical cells. Pure data + (for resized ones) an art regen; publish.
- Determinism: a door's `blocks_players`/`blocks_bugs` footprint change touches collision — re-save the zone
  + run sim-determinism if doors block bugs (cf. #9). Today these doors have `blocks_players:null` (don't even
  block!) — worth fixing alongside.
