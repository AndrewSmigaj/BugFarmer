# Investigation: #8 bed not working (one no message; one set but respawned to the square)
_status: BLOCKED ON 1 live confirm (bed 2) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** All 4 beds are correctly tagged `interaction_type:"sleep"`, and the server `handleSetHome` +
  faint-respawn code are **correct** (sets `HomeZone=current zone`, `HomeX/Y=bed cell`; respawn uses HomeX/Y
  when `HomeZone==zoneID`, `handlers_player.go:83`). Both failures are upstream:
  - **Bed 1 — "no message":** beds are **large 2×4 occupants**; clicking one lands on an overlapping bedroom
    occupant via the shared single-`OverlapPoint` resolution (see index cross-cutting note), so the `_sleep`
    right-click handler never fires → no set_home → no message.
  - **Bed 2 — "setting bed message but respawned to the square":** either the message was a **client-optimistic**
    one and the server then rejected (the click resolved to a footprint cell of the 2×4 bed → handleSetHome's
    anchor check `!cell.Occupant.Anchor` → "No bed there"; or out of range), OR `HomeZone` didn't match the
    zone at respawn. The server set/respawn logic itself is sound.
- **Fix:** (1) the shared OverlapPoint topmost-resolution so a large bed reliably resolves to the bed (anchor);
  (2) show the "home set" confirmation **only on the server SetHomeAck**, never optimistically; (3) live-confirm
  the respawn (set home → faint → should wake at the bed) to rule out a HomeZone mismatch.
- **Certainty:** bed-1 (OverlapPoint) **70%** · bed-2 root **55%** (server code correct → it's the click/message
  or a runtime zone mismatch). **Needs your decision/confirm:** is the "setting bed" text a server ack or a
  client-optimistic message? **Status:** `BLOCKED ON: bed-2 live confirm`.

## 1. Issue
> "bed wasn't working, one didnt show the message the other said the setting bed message but put the user back in the square"

## 2. Verified facts
- Beds: `bed_basic/bed_fancy/bed_canopy` footprint `[2,4]`, `bunk_bed` `[2,3]`, pivot bc, `interaction_type
  "sleep"`, interactable. Large → many overlap-prone cells.
- `handleSetHome` (`handlers_home.go`): requires the clicked cell be the **anchor** + sleep type + range 3.0;
  on success sets `player.HomeZone = currentZone`, `HomeX/Y = msg.GX/GY + 0.5`, persists async.
- Faint respawn (`handlers_player.go:73-87`): `spawn = zone spawn`; `if HomeZone != "" && HomeZone == zoneID {
  spawn = HomeX,HomeY }`. Correct.

## 3. Recommendation
Adopt the shared `OverlapPointAll` topmost-interactable resolution (fixes bed 1 + #5/#18 etc.). Make the bed
"home set" message server-confirmed. Then a 3-minute live test (set home at a bed, take faint damage, confirm
you wake at the bed not the plaza) pins whether bed 2 is the optimistic-message/anchor reject or a real
respawn/zone-match bug — instrument the server SetHome path (accept vs which error) during the test.
- Determinism: none.
