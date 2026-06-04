# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

## Done (recent) — sync stability + headless test infra
- Fixed the frontier-gated freeze (spurious resync — "caught up" was wrongly treated as a stall)
  and the reconnect seq-desync (stale `PendingInfluence` leaked to the next client). Details in
  `architecture_swarm_sync.md` §11.
- World lifecycle: pause-when-empty + `world_enter` (singleton Normal/Test worlds; the frontend no
  longer creates worlds).
- Test infra: headless `.NET` sync-harness (`tools/sync-harness/`, incl. a reconnect scenario),
  test-zone generator (`tools/make_test_zone.py`), `sim_test` zone; single-source zone config
  (removed `debug_mode` + `species_debug.json`).
- New world-select login (`WorldMenu`).

## Now — Safe cleanup only (no refactoring, no splitting files)
Tidy what's clearly safe; leave anything risky alone.
- Delete dead one-off experiments in `tools/gen_sprites.py` (`player_spike`, `paperdoll_spike`,
  `walk_sheet_spike` and helpers nothing else uses) — but **keep** the sprite-sheet + cropping code
  (`segment_sheet` etc.); the next item builds on it.
- Remove scratch/clutter and any empty dirs left over from earlier reorgs.
- No structural refactors, no god-class splits — those are deferred until we have a way to verify
  them (there are currently no automated tests).

## Next — Get multi-frame sprites working (hands-on, together)
Experimental and human-in-the-loop — we try things and look at the output together, not plan it up
front.
- First: see if gpt-image-1 will output a clean sprite sheet we can crop. Start with the garden
  bed (dry vs watered).
- If it won't: fall back to a base bed plus a separate water-drops layer (procedural or old-style).
  The plant is drawn on top as its own layer either way.
- Once a method works, reuse it for crop growth stages, then later bug animation frames.

## Next — Zone-design guides cleanup
Consolidate the contradictory zone guides into one coherent set so we can design natural, non-rigid
zones (no dead-straight roads, no uniform scatter). Gets its own plan when we start.

## Next — Zone graphics: 6 preview scenes
Fill missing entity data, generate/clean remaining sprites, render 3 surface + 3 mining preview
scenes. Depends on the two items above.

## Later — captured, not scoped yet
- Bug behaviour / AI.
- Authoring brand-new zones.
- Weapons / tools rework (currently weak).
- An enemy.
- Active/inactive zones: simulate bugs in detail only in zones that have players; cheaply
  aggregate the rest; pause a zone entirely when it has no one. Finer-grained than today's
  per-match pause-when-empty (which only idles when the *whole* world is empty).
- Free long-idle matches + clean up accumulated world metadata (matches currently idle when
  empty but are never freed; harness `world_create` runs leave stale metadata).
