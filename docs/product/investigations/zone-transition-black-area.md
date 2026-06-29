# Investigation: #3 zone transition broke (black area instead of the mining camp)
_status: ✅ RESOLVED 2026-06-29 — restored `village_21_B` `{"south":"underground_passages_31"}` (matching the
underground's `"north":"village_21_B"`) via a post-save patch in `zone_village_21_B.py`. The general builder fix
(first-class `ZoneBuilder.neighbors` so no rebuild drops links) is deferred → BACKLOG. · investigated 2026-06-28_

## Debrief (read me first)
- **TL;DR:** A regression. **village_21_B lost its `neighbors` block.** Commit `ce4102a` (the village_21_B
  6-species ecology rebuild) regenerated `village_21_B/zone.json` **without** neighbors — the git diff literally
  shows `- "neighbors": { - "south": "underground_passages_31" }` removed. The **zone builder never writes
  neighbors**, so any rebuild drops them. So the cross-zone link OUT of village_21_B (south → the
  underground/mining area) is gone; walking that edge no longer transitions.
- **"Goes sometimes":** village_21 ("Normal") still has `south → underground_passages_31`, and
  `underground_passages_31` still has `north → village_21_B` — so transitions work from those, but not from
  village_21_B. Whichever zone you were in explains "sometimes."
- **Fix:** (1) restore `village_21_B` `neighbors: {"south":"underground_passages_31"}`; (2) **make the builder
  emit neighbors** (a `neighbors=` param / `set_neighbors`) so a rebuild can't silently drop them again — the
  durable fix. Re-save the zone.
- **Certainty:** dropped-neighbors regression **95%** · that it's also the "black area" **75%** (the black is a
  downstream symptom of the broken/asymmetric adjacency — confirm with a live crossing after the fix).
  **Needs your decision:** none. **Status:** `READY`.

## 1. Issue
> "at some point the zone transition broke, it goes sometimes doesnt others and leads to a black area not the north mining camp area it used to work so not sure why it doesnt now."

## 2. Root cause (verified)
- Neighbors are loaded per-zone from `zone.json`'s `neighbors` map (`world.go:398 LoadZoneConfig` →
  `ZoneNeighbors{North,South,…}`; `zone.go:121`). The client edge-clamps when a zone has no neighbor for that
  edge; with a present-but-stale/empty target the swap can land on nothing = a black screen.
- Current state: `village_21_B` neighbors = **absent**; `underground_passages_31` = `{north: village_21_B}`;
  `village_21` = `{south: underground_passages_31}`.
- `git log -S neighbors` shows commit **ce4102a** removed `village_21_B`'s `{south: underground_passages_31}`.
- `tools/zonegen/scenes/zone_village_21_B.py` (+ `zonebuilder.py`) never writes a neighbors block → every
  rebuild regenerates `zone.json` without it. That's the regression mechanism.
- `underground_passages_31` is NOT empty (64 chunks, full ground) — so the "black" isn't a missing target
  zone; it's the broken/asymmetric adjacency (transition fires toward a neighbor village_21_B doesn't declare).

## 3. Recommendation
1. Restore `village_21_B/zone.json` neighbors `{"south": "underground_passages_31"}` (matching the surviving
   reverse link), then re-save.
2. Teach the zonebuilder/scene to carry neighbors (a `neighbors` arg written into `zone.json`) so future
   rebuilds preserve them — the real fix. Audit the other built zones for the same drop.
3. Live-confirm the black-area is gone after restoring the link (walk village_21_B south edge → underground).
- Determinism: none (adjacency is connectivity metadata, not bug-sim state).
