# Authoring forests (STARTED 2026-06 — grows with the forest-zone work)

The beginner forest is the centipede's home and the next zone after the village remake.
This guide collects the rules as we learn them; the first real forest zone will harden it.

## What exists today
- A small TEST forest patch in village_21 around **(105, 240)** (chunk 3_7; NORTH of
  spawn, past the crop fields): oaks, pines, bushes, one wild `wasp_nest` at (107,240),
  and the centipede spawn circle (zone.json spawn_areas `forest_patch` cx105 cy240).
- The wasp-pen vignette near the fly farm at **(124, 232)** (also NORTH, west of the
  road): a wild nest beside the stone path with wood OBSERVATION fencing (deliberately
  wood: the lesson is that fences do NOT stop wings) and flowers.

## Rules learned so far
1. **Pen walls must be EDGE-CONNECTED.** The bug raycast steps at 0.5 and the client
   per-bug collision checks destination cells only — fence cells touching solely at a
   CORNER leak diagonally (consistently on all clients, so it's an authoring rule, not
   a sync bug).
2. **Wood vs stone is the centipede lesson.** `gnawable: true` lives on the wood fence
   family (fence_wood, gate_wood, pickets, corners). Forest pens that must HOLD
   against centipedes need stone/iron. Wasps ignore all fences (they fly) — forest
   apiaries need future roofs (`blocks_flying`), not walls.
3. **Nest placement = danger geography.** A nest's raid field is `home_range` (40)
   around it; wild flies inside that field absorb most raids (the buffer). Place nests
   INSIDE natural prey areas, far side from paths. Forest = density is the message
   (multiple nests); village = exactly one.
4. **Chunk-touch activation.** Nests and fruit trees come alive when a player first
   loads their chunk; wild prey spawns zone-wide from match start. Deep-forest content
   effectively "starts" on first exploration — fine, and worth exploiting for pacing.
5. **Content-update workflow:** chunk files are read at chunk-touch and never written
   back. Edit/regenerate → restart the server → walk there.

## Forest composition (absorbed from trees-and-ponds.md; what's primitive-backed)
- **Masses, not scatter**: a forest boundary is `terrain.forest()` blobs (density
  ≈0.5-0.6) CHAINED along the rim with gaps only at road mouths; scatter is only the
  FADE between masses. (PRIMITIVE-BACKED. The old guide's noise-density-field
  approach remains ASPIRATIONAL — don't reach for functions that don't exist.)
- **Deep forest floor**: pass `dirt=True` — the canopy core darkens to dirt, the
  edge stays grass (the scene_meadow_forest_edge gradient; a dedicated
  leaf-litter/forest_floor TILE is still future art).
- **Edge gradient + clearings + understory**: forest() thins to a ragged edge and
  leaves noise clearings; give 1-2 clearings a feature (log pile, mushroom ring,
  stump circle). Understory (fern/mushroom/bush/stump) scatters at clumping ≈0.85.
- Bands per the old checklist: core = trees, mid = trees+bushes, edge = bushes +
  tall grass + the odd tree.

## TODO as the real forest zone lands
- A leaf-litter / forest_floor ground TILE (art) — `dirt=True` is the stand-in.
- A scene primitive for "nest clearing" (nest + prey flowers + a carrion spot).
- Centipede density tuning — PARTIALLY DONE 2026-06: centipedes are now KNOTS
  (swarms of 1-3 sharing a center; max_swarm_size is data); the village runs
  initial 2×2 / max 3 swarms / pop 8. Forest zones can push the knobs higher
  ("their home").
- Underbrush occupants that block players but NOT bugs (ambush grass).
