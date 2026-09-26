# Zone Design: Ant Colony (deep underground · `ant_colony`) — SUPERSEDED

> **SUPERSEDED 2026-07-06.** This is the DEMO-era sheet ("Grid cell TBD", pre-restructure).
> The current truth: ants own **col 0** — Ant Tunnels **(3,0)** + Ant Colony w/ Queen
> **(4,0)** (decisions D2/D3/D9; owner 2026-07-06: colony in the SW zone, scout tunnels
> above leading outside south of the bee zone). See the live docs:
> `ant_tunnels_30.md` and `ant_colony_40.md`. Kept for its prose ideas only (the fungus
> garden, aphid livestock, THE GREAT TRUNK TUNNEL survive as candidates there).

## Overview
- **Zone ID / Grid:** `ant_colony` · deep underground (below `underground_passages_31`)
- **Biome / Difficulty:** Excavated ant nest in soil/clay · **Hard** (the deepest demo zone)
- **The feel:** You've dug past the ore caves into a **living nest** — branching tunnels packed with marching
  **workers**, guarded by armored **soldiers**, all radiating from the **Queen's hall**. It's claustrophobic,
  organic, and busy: brood chambers of pale eggs, a **fungus garden** the ants farm, and herded **aphid
  "livestock"** milked for honeydew. The colony is itself an ecosystem — and a threat if you provoke it.

## Connections (map)
- **N/up →** Mining Caves (`underground_passages_31`) via a dug shaft / the deepest tunnel. (Possibly deeper
  cells below for an Ant Queen boss zone later.)

## Key species & ecology
- **Worker ants** — haul, dig, farm; mostly non-aggressive alone but overwhelming in numbers; the colony's
  labor.
- **Soldier ants** — large mandibles, the real danger; guard chambers and swarm intruders.
- **The Queen** — enormous, immobile, the colony's heart; a semi-boss. Threatening her triggers the swarm.
- **Aphid "livestock"** — ants **herd aphids** (protect them, milk **honeydew**) — a real-world mutualism and
  a great emergent hook (disrupt the aphids → starve/anger the colony). Ties to bug-farming (you can learn to
  ranch aphids).
- **Colony fungus** — leafcutter-style **fungus garden** the ants cultivate on chewed plant matter; spreads
  if unmanaged.
- **Out of balance:** kill the workers → the fungus garden rots, aphids scatter; kill the Queen → colony
  collapses (loot windfall, but the niche it filled changes). (See `ecology_proposal.md`.)

## Landmarks & little features
- **The Queen's Hall** — a great domed chamber, the Queen surrounded by attendants and egg piles.
- **Brood / egg chambers** — clusters of pale eggs and larvae, tended by workers.
- **The Fungus Garden** — pale glowing fungus terraces, leaf fragments, a damp organic glow.
- **Aphid pastures** — a wall of aphids on root tendrils, soldier ants standing guard.
- **The Great Trunk Tunnel** — the colony's highway, worker columns streaming both ways.
- **Abandoned dig** — a half-collapsed side tunnel with a crushed mine cart from the ore caves above.

## Structures / NPCs
- No buildings. Ant-made structure only: chambers, the queen's dais, fungus terraces, dirt/clay walls,
  pebble-reinforced arches. A lost miner's body/pack could be a grim loot landmark.

## Materials / loot
- **Chitin** (from soldiers — a crafting material; armor/pen components), **formic acid** (alchemy),
  **honeydew** (sweet good), **royal jelly/queen-stuff** (rare), ant eggs (food/bait). Rich gems/ore can
  stud the deep clay walls (deepest tier).

## Biome composition (for the generator)
- Base **dirt/clay** (the existing cave/soil features); carve branching **tunnels** (`cave.carve_tunnel`,
  meander) + **chambers** (`carve_cavern`) off a central trunk; `fill_solid` the rest with dirt/clay/ore
  blocks; ant mounds, egg clusters, fungus terraces, aphid root-walls as occupants; ants as `place_bug`
  (workers in columns along tunnels, soldiers at chamber mouths, the Queen huge in her hall). Dim, warm glow.

## Scenes (showcase)
- `scene_ant_nest.py` — a cross-section of the nest: trunk tunnel + brood chamber + fungus garden + worker
  columns + a soldier or two.
- `scene_ant_queen_hall.py` — the Queen's domed hall (Queen, attendants, egg piles, aphid pasture nearby) —
  the climactic landmark.

## Not present
- No surface light, no town/shops, no player building (hostile zone).
