# Investigation: #6 "missing NPCs" in village_21_B
_status: RESOLVED (no NPC-authoring fix needed) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** The NPCs are **correctly authored** in village_21_B — not a missing-content bug. Andrew
  confirmed in-session ("all npcs are considered there… don't worry about that"). The data backs it: 9/10
  shop NPCs (incl. the two named — "market person" = `general_store_merchant`, "bug salesperson" =
  `bug_dealer`) are present in the saved chunks.
- **Only real finding:** **`fisherman` was placement-skipped** — it's in the builder (`zone_village_21_B.py:222`,
  cell 41,109) but ABSENT from the saved chunks (the known "P3a placement skips" class — `place_occupant`
  silently skips a blocked/occupied target cell). Minor authoring gap, optional fix.
- **If they ever looked missing in-game:** an already-running match holds pre-NPC chunks in memory; the zone
  data is **live volume-mounted** (`docker-compose.yml:47 ./nakama/data:/nakama/data`), so a server/match
  **reload** (not a rebuild) reflects the current files. Not a code bug.
- **Certainty:** authoring-correct **98%** · fisherman-skipped **95%**. **Needs your decision:** none.
  **Status:** `READY (no-op for NPCs; optional: re-place fisherman)`.

## 1. Issue, repro & evidence
> "missing NPCs like market person and such, not in their store nor is the bug salesperson (village 21 B …
> please ensure they are all looking at the right zone." → later: "yeah all npcs are considered there… don't worry about that."
- **Acceptance:** NPCs present at their stores in village_21_B. **Met** by the data (below).

## 2. What the evidence shows
- **Authored chunks** (`nakama/data/zones/village_21_B/chunk_*.json`, occupants = a 32×32 row-major grid
  `occupants[ly][lx]`) contain, at sensible cells: `general_store_merchant` (60,138), `bug_dealer` (64,142),
  `mayor` (103,134), `ecologist` (190,144), `blacksmith` (141,105), `carpenter` (159,105), `weaver` (143,85),
  `stonemason` (176,90), `modern_wares` (190,88). Each is a 1×2 occupant (`footprint [1,2]`, pivot `bc`,
  `sprite 16×32`, `interaction_type:"shop"`). Sprites all exist.
- **Only `fisherman` is absent** from the saved chunks despite being in the builder (`:222`) → placement skip.
- **Server serves them correctly:** zone load reads the **authored chunk fresh** then applies the persisted
  *delta* overlay (`handlers_world.go:36 applyChunkSave`) — a stale overlay adds edits, it does NOT remove base
  occupants the player didn't break. No occupant-category filter drops NPCs from the broadcast.
- **Data is live-mounted** into Nakama → updated zone files are visible without a container rebuild; only an
  already-loaded match needs a reload.

## 3. Ruled out
- "NPCs never placed / wrong zone" — falsified: 9/10 are in the village_21_B authored chunks (the zone the
  WorldMenu loads as "Village B").
- "Stale container has old zone files" — falsified: `./nakama/data` is a live volume mount.
- "Persisted overlay deleted them" — the overlay is a delta vs the authored base at save time; it can't remove
  an occupant the player didn't break.

## 4. Recommendation
No NPC-authoring fix needed. **Optional small fixes** (for the fix-pass, not blocking):
1. **fisherman placement-skip** — its cell (41,109) is likely blocked/water; move it to a clear adjacent cell
   in `zone_village_21_B.py` and re-save, OR drop it (fishing is deferred anyway).
2. If "looking at the right zone" referred to the NPCs' **shop stock targeting a zone**, that's not an NPC
   *placement* issue and would surface under #5 (selling) — investigated there.
