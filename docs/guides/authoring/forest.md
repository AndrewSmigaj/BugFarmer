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

## TODO as the real forest zone lands
- Forest ground tiles (leaf litter / forest_floor) + a tree-density brush in zonegen.
- A scene primitive for "nest clearing" (nest + prey flowers + a carrion spot).
- Centipede density tuning (village cap 2 = "a problem"; forest = "their home").
- Underbrush occupants that block players but NOT bugs (ambush grass).
