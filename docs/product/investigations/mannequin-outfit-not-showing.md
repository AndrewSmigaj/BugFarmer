# Investigation: #4 mannequins don't visually show worn items
_status: READY (it's a feature to BUILD, not a bug) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** Not a bug — the **worn-outfit visual was never built**. The mannequin's outfit *storage* works (it's
  a filtered `ContainerState`, filter "clothing"), but the piece that paints the worn clothing onto the
  mannequin's sprite is an **explicitly-deferred follow-up**. The code says so itself:
  `MannequinController.cs:19-20` — "the mannequin SPRITE composing the worn outfit (a paper-doll like
  RemoteEntity) is the follow-up … see BACKLOG 'mannequin render Increment-A/B'." No render code exists.
- **Effort:** M — it's a real feature (server must broadcast the mannequin's worn items as occupant render
  data; client composes the clothing layers onto the mannequin sprite + re-composes on change), reusing the
  player paper-doll machinery.
- **Certainty:** unbuilt-feature **95%**. **Needs your decision:** prioritize building it now vs leave
  backlogged? **Status:** `READY` (as a build task) — recommend scoping it with the player paper-doll reuse.

## 1. Issue
> "mannequins do not visually show when i put things on them"

## 2. What's there vs not (verified)
- **Storage — works:** right-click a `interaction_type:"mannequin"` occupant → `MannequinController` outfit
  panel (5 equip slots), backed by the server `ContainerState` with filter "clothing" (`:14-16`). Putting
  items on the mannequin succeeds and persists.
- **Visual — absent:** there is NO code that renders the worn items onto the placed mannequin sprite.
  `TilemapManager.RenderOccupant` draws the single base mannequin PNG via `GetWorldSprite` and nothing else.
  The server carries the worn items only inside the mannequin's `ContainerState`; it is never sent as occupant
  *render* data, and the client never composes it. (Task #224's "render" was the mannequin base sprite +
  blocks_bugs, not the outfit.)

## 3. Recommendation (build it — reuse the player paper-doll)
1. **Server:** include a mannequin's worn-clothing ids in the occupant render payload (a small per-occupant
   overlay list), broadcast on change + on chunk-subscribe (mirror the fruit-overlay re-send pattern,
   `handlers_farming.go:1041`).
2. **Client:** in the mannequin's occupant render, compose the clothing layers over the base sprite using the
   existing player layer-compose path (`RemoteEntity` / the character paper-doll used for armor), re-composing
   when the overlay changes.
3. Authored body/clothing layers for the mannequin pose may be needed (the BACKLOG "Increment-A/B" note).
- Determinism: none (cosmetic display only).
