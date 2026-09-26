# Investigation: #12 picking up bugs/things — some work, some don't
_status: READY — mostly by-design + discoverability; ties to #13/#11 · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Not one bug — pickup has **three separate mechanics** and which applies isn't signposted:
  1. **Walk-over auto-pickup** (`PickupController`, `autoPickupRange 1.25`) grabs ordinary drops (wood, fiber,
     flowers, produce) automatically. ← the "works fine" set.
  2. **E-required** for exactly the 4 fruit (`apple/orange/plum/cherry`, all `no_auto_pickup:true`) + bug food
     (`rotten_*`, excluded via `includeBugFood:false`). Walking over them does nothing → "doesn't work" until
     you press E. ← the "doesn't work" set.
  3. **Bug catching** (`CatchingController`, net/hand) — not "pickup" at all; which bugs you can catch is the
     net-size/catch-condition rule (= #11, backlogged). ← "picking up bugs … some work, some don't."
- **No hard bug found** in the item paths: every item is covered by auto OR E (range-based, not click — so the
  OverlapPoint issue doesn't apply here). The inconsistency is the unsignposted split.
- **Recommendations:** (a) #13's design makes fruit **hit-to-collect**, removing the fruit-needs-E surprise;
  (b) add a pickup affordance/prompt for E-required items (the highlight exists — make the "press E" read);
  (c) bug-catching net rules = #11. Worth a quick live check that E-pickup + catch have no range/cap edge bug.
- **Certainty:** the 3-mechanic split **90%** · "discoverability not a hard bug" **70%** (a live E-pickup test
  would close it). **Needs your decision:** auto-pickup fruit too, or keep E/hit? **Status:** `READY`.

## 1. Issue
> "picking up bugs and/or other things doesn't seem to work, some things seem to work fine picking up others dont so an investigation is needed"

## 2. Evidence
- `PickupController.TryAutoPickup` → `GetClosestItem(pos, 1.25, includeBugFood:false)` — auto-grabs non-bug-food
  drops only (`:73-80`). `E` (`:61`) handles the rest via a range query `GetItemAtPosition(pos, highlightRange)`
  (`:103`) — range-based, not OverlapPoint.
- `no_auto_pickup` items = **apple, orange, plum, cherry** (only these 4). Bug food (`rotten_*`) is the other
  E-required class ("what the bugs eat belongs to the bugs").
- Bugs: caught by `CatchingController` (net sweep / hand radius), gated by species net-size/catch-condition.

## 3. Recommendation
Make the split legible + reduce its surface: adopt #13 (fruit → hit-to-collect) so the only "manual" pickup is
bug food (intentional), surface the E-prompt on E-required highlights, and treat bug-catch consistency under
#11. Determinism: none (client pickup + server-validated inventory transfer). If you want a hard-bug ruling,
a 5-min live test (walk over wood = auto; stand on an apple + press E = picks up; net a fly vs a centipede)
distinguishes "by design" from a real reach/cap bug.
