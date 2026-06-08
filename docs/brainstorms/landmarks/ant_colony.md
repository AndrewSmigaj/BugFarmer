# Ant Colony — Landmarks brainstorm

The "little features" that make the nest feel like a real excavated, living place: the great chambers, the
busy tunnels, the farmed terraces, and the grim relics of the miners who dug too deep. Be generous and
evocative — these are the set-pieces a scene is built around, the things a player rounds a corner and *sees*.
Each is a composed vignette (occupants + decor + bugs), not a single sprite.

---

## The royal & brood chambers (the colony's heart)

- **The Queen's Domed Hall** — a great vaulted clay dome, the colossal `ant_queen` enthroned on a raised
  earthen dais, ringed by attendant nurses and heaped pale egg-piles; warm ember-fungus glow. The climactic
  landmark (semi-boss). *Scene: `scene_ant_queen_hall`.*
- **The Royal Antechamber** — the guarded approach to the hall: a pinch-point arch flanked by `ant_soldier_giant`
  gatekeepers, drone ants drifting, the floor scarred by countless feet.
- **The Brood Nursery** — a low warm chamber of stacked pale egg clutches, soft larvae, and cocoon pupae,
  swarmed with fussing nurse ants; the most "alive," squirming corner of the nest.
- **The Pupae Vault** — a quieter side cell of cocoon-wrapped pupae racked in clay shelves, near hatching.
- **The Nuptial Shaft** — a vertical shaft up which winged drones and a virgin queen are massing for a
  founding flight; daylight glimmers faintly far above.

## The fungus garden (the cultivated landmark)

- **The Fungus Garden Terraces** — the signature set-piece: stacked spongy fungus terraces glowing pale,
  threaded with leaf-mash beds and minor ants tending the crop; damp, organic, luminous. *Scene: `scene_ant_nest`.*
- **The Leafcutter Trail** — a worn green-littered trail down which a column of `ant_leafcutter` haul
  leaf-discs overhead, ending at the garden's substrate beds; a river of moving leaves.
- **The Compost Pit** — the garden's lowest terrace: dark spent substrate being recycled, woodlice and
  springtails working it, warm and rich-smelling.
- **The Blighted Garden** — an abandoned terrace overrun by `escovopsis_blight` and `creeping_white_mold`,
  rotting and gray — the *out-of-balance* landmark (what the garden becomes when the workers die).
- **The Honeypot Ceiling** — a chamber where swollen `ant_repletes` hang from the roof like living amber
  jars of honeydew; the colony's larder.

## The aphid pastures (the herded landmark)

- **The Aphid Pasture Wall** — a clay wall sheeted in `root_tendril` grazed by a herd of aphids, soldier
  ants standing guard, honeydew beading and dripping; the mutualism made visible.
- **The Weeping Root Pasture** — a sap-bleeding `weeping_taproot` pillar crawling with the best of the herd,
  honeydew pooling at its foot.
- **The Milking Station** — a busy spot where workers stroke the aphids with their antennae to draw
  honeydew; the "dairy" of the nest.

## The tunnels & highways (the connective landmark)

- **The Great Trunk Tunnel** — the colony's central highway, two `ant_worker` columns streaming opposite
  ways past each other, walls polished smooth by traffic. The nest's main artery.
- **The Crossroads Chamber** — a node where several tunnels meet, traffic snarling, a soldier directing the
  press; pebble-arch reinforced.
- **The Pebble Arch Gate** — a tunnel mouth reinforced with mortared pebbles into a crude arch; ant
  engineering on display.
- **The Ventilation Chimney** — a `hollow_root_husk` repurposed as a vertical air shaft; cool draft, faint
  glowworm light.
- **The Deep Sump** — the lowest wet point of the nest, dripstone and pale algae, a black still pool;
  feels like the bottom of the world (hints at deeper zones).

## The grim relics (lost-miner / abandoned-dig landmarks)

- **The Abandoned Dig** — a half-collapsed side tunnel breaking in from the ore caves above, timber supports
  snapped, a **crushed mine cart** on bent rails spilling ore. Where the human world meets the nest.
- **The Lost Miner's Pack** — a grim loot landmark: a fallen miner's rucksack and dropped lantern (still
  faintly lit), bones half-claimed by `bone_fungus`, beside a dropped pickaxe. *Loot cache.*
- **The Sealed Breach** — a tunnel the ants have walled off with packed clay where the miners broke through;
  scratch-marks on the human side, an unsettling barrier.
- **The Ore-Studded Wall** — deep clay glittering with gems and ore seams the ants tunneled around but
  cannot use; the richest (and deepest) mining reward, guarded by soldiers.
- **The Boneyard** — a refuse midden where the colony dumps dead ants, husks, and prey carcasses; picked
  over by silverfish and nest moths. Cordyceps-stalked corpses stud the heap.

## Eerie & ambient (texture landmarks)

- **The Cordyceps Cluster** — a knot of `cordyceps_ant` corpses frozen mid-climb on a root, fungal stalks
  jutting — the nest's most unsettling sight.
- **The Glowworm Curtain** — a damp ceiling hung with a sheet of glowworm light, the only "stars" in the dark.
- **The Antlion Pit** — a conical sand-trap at a tunnel pinch, jaws of a buried `antlion_larva` waiting below.
- **The Alarm-Scent Cloud** — (event landmark) a disturbed chamber where alarm pheromone has the whole
  colony boiling and converging; you've been noticed.

---

## Notes
- Two showcase scenes anchor these: `scene_ant_nest` (trunk tunnel + brood + fungus garden + worker columns)
  and `scene_ant_queen_hall` (the Queen, attendants, egg piles, aphid pasture). See the zone doc.
- The grim-relic landmarks (abandoned dig, lost miner's pack, sealed breach) tie the nest to the **Mining
  Caves** above and reward exploration with loot + lore.
- Out-of-balance landmarks (Blighted Garden, Alarm-Scent Cloud, Boneyard cordyceps) visualize the ecology
  proposal: the colony's health and the consequences of disrupting it.
