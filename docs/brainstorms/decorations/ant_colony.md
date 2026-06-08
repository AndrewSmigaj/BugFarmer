# Ant Colony — Decorations brainstorm

The placeable building-blocks of the nest: the **ant-made structures** (mounds, arches, walls, terraces)
and **nest decor** (egg clusters, soil heaps, leaf piles) that the zone generator scatters to make a tunnel
feel inhabited and busy. These are occupants/placeables, not bugs. Many double as the *exotic farm decor*
the player could earn once they learn colony husbandry (tagged **[tame→decor]**) — feeding the passive
decoration-bonus mechanic (`game_design.md §11.5`). Lean into organic, busy, claustrophobic.

---

## Ant-made structures (engineering)

- `ant_mound` — a conical heap of excavated soil pellets, the classic nest entrance/spoil pile. *[tame→decor]*
- `ant_mound_large` — a big thatched mound (forest-ant style) of soil and chewed plant matter.
- `pebble_arch` — a tunnel-mouth arch of mortared pebbles, crude ant masonry. *[tame→decor]*
- `pebble_pillar` — a stacked pebble support column reinforcing a chamber roof.
- `clay_wall` — a packed clay/soil wall the ants have smoothed; the nest's main partition. *(block-like)*
- `dirt_wall` — a rougher dug earth wall, root-threaded and crumbly.
- `mud_brick_wall` — a wall of saliva-bound mud pellets, faintly pebbled in texture.
- `tunnel_buttress` — a thickened clay rib bracing a wide chamber, like a vault rib.
- `soil_pellet_heap` — a tidy pile of spat-out excavation pellets beside a fresh dig. *[tame→decor]*
- `spoil_heap` — a loose mound of dug dirt and stones dumped at a tunnel side.
- `clay_chimney` — a sculpted clay vent-tube rising from the floor (ventilation/temperature control).
- `dirt_ramp` — a packed earthen ramp the ants built between two terrace levels.

## Brood & egg decor

- `egg_cluster` — a clutch of glossy pale eggs piled on the chamber floor (matches existing `ant_eggs`).
  *[tame→decor: an exotic curio.]*
- `egg_clutch_large` — a big mounded heap of eggs in a nursery, tended-looking.
- `larva_pile` — a soft heap of pale grubs in a hollow; squirming nest texture.
- `pupa_rack` — cocoon pupae nestled in a clay shelf-row, near hatching.
- `brood_cradle` — a smoothed clay cup the nurses keep a special clutch in (royal brood). *Rare.*

## Fungus garden decor (placeables)

- `fungus_terrace` — a stacked spongy fungus-growing terrace, pale and glowing; the garden's tile-block.
  *[tame→decor: a glowing planter for a farm.]*
- `fungus_terrace_tall` — a multi-tier terrace tower of fungus beds climbing a wall.
- `leaf_substrate_bed` — a flat bed of chewed leaf-mash topped with white mycelium; pre-crop.
- `chewed_leaf_pile` — a mound of half-shredded leaf scraps awaiting processing. *[tame→decor: rustic.]*
- `compost_heap` — a dark heap of spent substrate being recycled; detritivores work it.
- `glowcap_cluster` — a placed clump of glowing lantern-caps used as nest lighting. *[tame→decor: a glow-lamp.]*
- `spore_pod_stand` — a swollen spore-pod on a stalk, used as a marker/light. *[tame→decor]*

## Aphid pasture decor (placeables)

- `aphid_root_wall` — a wall panel of `root_tendril` sheeted with grazing aphids; the pasture tile-block.
- `root_tendril_clump` — a hanging bundle of pale roots, an empty grazing surface awaiting a herd.
- `honeydew_drip` — a glistening sticky deposit of honeydew beaded on a wall/ledge. *[tame→decor: a sweet curio.]*
- `honeypot_hangers` — swollen honeypot-ant repletes hung from a ceiling beam as living larder (decor occupant).
- `milking_perch` — a worn ledge where workers tend the herd; aphid wax and honeydew crusting.

## Trails, traffic & busy-nest texture

- `ant_trail_groove` — a worn smooth groove in the floor polished by endless marching feet; a "path tile."
- `leaf_litter_scatter` — scattered green leaf fragments dropped along the leafcutter trail.
- `forage_petal_scatter` — bright surface flower-petals dragged down and dropped; vivid color flecks.
- `food_cache` — a tidy hoard of seeds and crumbs the foragers stored in a side cell. *Loot-ish.*
- `seed_husk_pile` — discarded husks from processed forage; midden texture.
- `prey_carcass` — a dismembered beetle or grub carcass being hauled in/eaten; grim busy detail.
- `refuse_midden` — a dump-heap of husks, dead ants, and scraps (the colony's trash pile).

## Lighting & ambient decor

- `glowworm_string` — a hanging string of glowworm-lit silk on a ceiling (decor/light occupant).
- `foxfire_patch` — a glowing green bracket-fungus patch on a wall, cold light.
- `ember_fungus_cluster` — a warm orange glowing fungus clump, the brood-chamber hearth-light.
- `dripstone_formation` — a cluster of clay/mineral dripstones over the wet sump; ambient cave detail.
- `crystal_seam_decor` — a small ore/gem seam glittering in the deep clay wall (deep-tier sparkle).

## Grim / relic decor (lost-miner ties)

- `crushed_mine_cart` — a wrecked, bent ore cart from the caves above, spilling rock; the abandoned-dig
  centerpiece. *[loot landmark.]*
- `broken_rail` — twisted snapped mine-rail segments leading nowhere.
- `snapped_timber` — a splintered mine support beam jammed into the clay.
- `miner_pack` — a dropped rucksack with a still-lit lantern; the lost-miner relic. *[loot.]*
- `dropped_lantern` — a fallen miner's lantern, glass cracked but glowing faintly. *[tame→decor: an antique lamp.]*
- `bone_scatter` — picked-clean bones half-claimed by `bone_fungus`; grim.
- `sealed_breach_patch` — a section of wall the ants packed shut with clay where miners broke through.

---

## Notes
- These are the **generator's scatter + structure vocabulary**: `ant_mound`/`pebble_arch`/`clay_wall` build
  the nest skeleton; `egg_cluster`/`fungus_terrace`/`aphid_root_wall` populate chambers; the trail/midden/
  petal scatter makes tunnels feel *busy and lived-in*.
- **[tame→decor]** items are the payoff of learning colony husbandry — exotic, organic farm decorations
  (glowing fungus planters, a honeydew curio, an ant-mound feature, an antique miner's lantern) that feed
  the passive decoration-bonus ladder. A glow-fungus or honeypot decor leans the "evening/glow" and
  "comfort" bonus hooks; the miner relics lean "trophy."
- Several decor entries deliberately mirror flora/landmark entries (fungus terraces, aphid root-walls, egg
  clusters) — here they're the *placeable* form the zone generator drops, vs. the flora doc's living-system
  framing and the landmark doc's composed vignettes.
