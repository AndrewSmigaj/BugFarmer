# Biome → Feature Map

Which `tools/zonegen/features/` primitives to reach for per biome, and the density/feel to aim for. Pair
this with the per-zone design doc (`docs/product/zones/<zone_id>.md`) and `ZONE_GENERATION_GUIDE.md`.
Precedence always: **biome base → water → roads → buildings → farms → scatter** (place hard features first).

| Biome | Base tile | Primary features | Density / feel | Signature props |
|-------|-----------|------------------|----------------|-----------------|
| **Village / town** | grass | `terrain.hpath/vpath` (roads), `room`/`house` + `houses/layouts`, `yard`, `garden`, `terrain.pond` (lake) | Buildings clustered on roads; open meadow around; lake SW | signs, stalls, well, statues, docks, fences |
| **Flowering meadow** | grass (lush) | heavy `scatter` (flowers + milkweed + tall grass + bushes), tree **clusters**, `place_bug` (pollinators/wasps) | Flowers dominant; few dirt patches; airy | milkweed stand, flower glade, boulder, broken fence |
| **Forest / forest-edge** | grass→dirt | dense tree clusters, `scatter` (ferns, mushrooms, bushes), stumps, fallen logs | Darker, denser northward; canopy gaps | fallen-log bridge, stumps, mushroom rings |
| **Cave / mining** | cave_floor | `cave.carve_tunnel` (meander + straight rail), `carve_cavern`, `fill_solid` (ore veins), `place_pool` | Mostly solid rock carved into tunnels/caverns; ore veins ~12–18% | rail track, mine cart, camp (workbench/torches), glow pool |
| **Ant nest** | dirt/clay | `cave.carve_tunnel` (branching off a trunk), `carve_cavern` (chambers), `fill_solid` (dirt/clay/ore) | Claustrophobic, organic, busy; warm dim glow | egg chambers, fungus terraces, aphid pastures, mounds |
| **Desert** | sand | `scatter` (cacti, dry brush, rocks), sandstone cliffs, sparse `terrain.pond` (oasis) | Sparse, sun-bleached, wide | bleached bones, ruins, cliff, oasis |
| **Swamp / wetland** | mud/shallow water | `terrain.pond`/`stream`, `scatter` (reeds, cattails, lily pads), gnarled trees | Wet, low-visibility, water-threaded | sunken logs, mist, stilt platforms |
| **Water / pond edge** | shallow/deep water | `terrain.pond`/`stream`, `garden` (lily pads), reeds | Use for lakes, streams, oases | docks, reeds, frogs |

Notes
- **EVERYTHING snaps to the grid except BUGS.** Trees, plants, flowers and crops are grid `place_occupant`s
  (the player plants them; they're saved to the zone). Only **bugs** (`place_bug`) — plus incidental pickups
  like fallen fruit / lily-pads-on-water (`place_decor`) — are sub-grid floats.
- Aim for **variety + little features** in every zone (a poor→nice range, named landmarks) — a sparse map
  reads as a tech demo. Brainstorm the content first (`docs/brainstorms/<topic>/`).
