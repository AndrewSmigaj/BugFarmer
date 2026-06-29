# Investigation: #15 can't water ground without a seed/plant in it
_status: READY TO IMPLEMENT · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** By design today: `handleWatering` (`handlers_farming.go:73-89`) waters a cell only if it has a
  `CropState` or a `FruitTreeState`. An empty tilled `garden_plot` with no crop falls through to
  `"No crop here"` and is rejected. There is no code path to water a bare bed.
- **Fix:** when `crop==nil && tree==nil`, check the ground tile — if it's `garden_plot` (tilled soil), flip it
  to **`garden_plot_wet`** (that wet variant already exists, used by `PlacementController.CanPlaceAt`) instead
  of erroring. ~8 lines in `handleWatering`. Gives the expected "water the bed" + visible wet soil.
- **Certainty:** root cause **95%** · fix-shape **85%**. **Needs your decision:** should watering a bare bed
  do anything mechanically (e.g. a moisture timer that speeds the next crop), or just visually wet + accept
  the water? **Status:** `READY`.

## 1. Issue
> "unable to water ground without a seed or plant in it (watering garden beds)"

## 2. Root cause (verified)
`handleWatering`: refill on water tiles → else `cropKey="gx,gy"`; `crop := state.CropStates[cropKey]`; if nil,
try `state.FruitTreeStates[cropKey]` (water the tree tank); if that's also nil → `sendWorldError("No crop
here")` and return (`:88`). So the watering can does nothing on tilled-but-unplanted soil.

## 3. Recommendation
In `handleWatering`, before the "No crop here" error, handle bare tilled soil: if
`chunk.GetGroundTile(lx,ly) == "garden_plot"`, set it to `garden_plot_wet` (persist via the ground CellEdit
path), decrement the can, broadcast the tile change, and return OK. Optionally add a moisture timer that wets
the soil for N ticks (and decays back to `garden_plot`), so a later-planted seed benefits — confirm desired
behavior with the user. Determinism: ground-tile moisture isn't a bug-sim input (cosmetic/crop-growth only);
re-check it doesn't feed `ComputeStateHash` before shipping, but expected low-risk.
