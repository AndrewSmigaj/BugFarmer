# Investigation: #18 couldn't break something behind a tree (did the tree intercept the click?)
_status: READY — confirmed latent bug (shared with #5) · investigated 2026-06-28 (time-boxed) · investigate-only_

## Debrief (read me first)
- **TL;DR:** Yes, a tree CAN intercept the break click — same root cause as #5. `BreakingController.cs:68`
  picks the target with a single `Physics2D.OverlapPoint(mouseWorld)` and takes whatever ONE collider it
  returns (`:81`). Every occupant has a `BoxCollider2D` sized to its **full sprite bounds** (`TilemapManager.cs
  :906-913`); a tree's sprite is tall and extends DOWN over the cells in front of it, so its collider overlaps
  a target there. `OverlapPoint` has no topmost/intended-target rule → it can hand back the tree, and the break
  either hits the tree or, if it returns a non-breakable occupant, does nothing ("Hit … but no
  OccupantClickTarget or not breakable", `:86`). The reporter's "they were wrong" is plausible (intermittent —
  depends which collider OverlapPoint returns), but the defect is real.
- **Fix:** the shared `OverlapPointAll` + topmost-interactable resolution (see #5 / index cross-cutting note) —
  prefer the occupant whose anchor cell is nearest the click / highest sorting order / matches the action.
- **Certainty:** mechanism **90%** · that this is exactly what the reporter hit **55%** (intermittent, reporter
  unsure). **Needs your decision:** none. **Status:** `READY` (folded into the shared OverlapPoint fix).

## 1. Issue
> "supposedly someone was unable to break something behind a tree so not sure if the tree intercepted the click and just did nothing they were wrong"

## 2. Evidence
- `BreakingController.HandleBreak`: `Collider2D hitCollider = Physics2D.OverlapPoint(mouseWorld)` (`:68`) →
  `hitCollider.GetComponent<OccupantClickTarget>()` (`:81`); if that's null/not-breakable → logs and does
  nothing (`:86`). Single arbitrary collider, no preference.
- Occupant colliders are sized to the **sprite** (`:906-913`), so tall sprites (trees) overlap the cells in
  front/below them.

## 3. Recommendation
Fix once via the shared `ResolveClickedOccupant` helper (`OverlapPointAll` → topmost interactable), used by
BreakingController + all right-click handlers. Closes #18 + #5-open + de-risks #12/#14/#10/#4. No determinism
impact (client target selection). A cheap interim: in BreakingController, if the single hit isn't breakable,
fall back to `OverlapPointAll` and pick the nearest breakable.
