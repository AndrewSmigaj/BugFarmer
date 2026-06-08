# Brainstorm — Mining Caves landmarks

The "little features" — **destination spaces and set-pieces** that make the **Mining Caves** zone worth
exploring, so it isn't an undifferentiated field of `stone_block`. These are the rooms/moments a player
remembers: a glowing geode chamber, an abandoned camp, a collapsed shaft. Most are **carved caverns dressed
with a coherent theme** (per `caves.md §2`); each combines floor type + occupants + flora + bugs into
a recognizable beat.

Crystals/minerals use the **mineral** art family. Many landmarks reuse decoration ids — see the decorations
doc. Rarity = how often a zone should contain one. Be generous: variety here = a world that rewards digging.

---

## 1. Crystal & mineral set-pieces (the reward rooms)
- `crystal_geode_chamber` — a hollow geode you break into: walls lined with `quartz_block`/amethyst druzy,
  glittering. The signature "you struck it rich" room. rare. Reward: gems, awe.
- `giant_crystal` — a single towering crystal spire jutting from the floor, refracting torchlight; landmark
  centerpiece of a chamber. rare.
- `crystal_cluster_grove` — a floor studded with many crystal clusters of mixed color (the "selenite cave"
  look). uncommon.
- `amethyst_pocket` — a wall pocket of purple crystal points, smaller find. common.
- `glowing_crystal_node` — a crystal that emits its own faint light (no torch needed). Glow. uncommon.
- `ore_vein_wall` — a wall face streaked with visible ore (copper/iron/silver bands) — telegraphs a vein to
  mine. common (the everyday "ooh, ore" beat).
- `gem_pocket_rare` — a tiny seam of cut-worthy gems (emerald/ruby/sapphire/diamond) deep down. very rare.
- `salt_crystal_grotto` — pale translucent salt formations and brine; a different mineral palette. uncommon.

## 2. Water features (the grottoes & springs)
- `glow_pool_grotto` — a still pool skinned in glow-algae (flora doc) casting blue light up the walls; the
  prettiest cave room. uncommon. Dress: `cave_lily`, glow_moss, cave_snail.
- `underground_spring` — water welling up from a floor crack, source of a stream; clear and cold. uncommon.
- `mineral_hot_spring` — steaming pool ringed with travertine/`mineral_crust_pool`; warm microclimate. rare.
- `dripstone_pool` — a pool fed by ceiling drips, ringed with stalactites/stalagmites; constant *plink*. common.
- `flooded_gallery` — a long chamber half-submerged in still black water; wade or raft across. uncommon.
- `frozen_pool` *(if deep/cold zones)* — an iced-over cave pool, pale blue. rare. (flag: may belong to an ice zone)

## 3. Mining infrastructure (the man-made layer — shows people were here)
Per `caves.md §1`, straight = man-made and must carry rail + supports.
- `rail_tunnel` — a straight, timber-supported tunnel with `mine_rail` down the center; the built spine of
  the mine. common (the zone's man-made artery).
- `mine_cart_scene` — a `mine_cart` on rails (full of ore, tipped over, or abandoned); set dressing along
  the rail. common.
- `mine_junction` — where rails split/turn with a switch and a signpost; orientation landmark. uncommon.
- `shaft_with_ladder` / `winch_shaft` — a vertical shaft with a ladder or a hand-winch + bucket, hinting at
  a level above/below. uncommon.
- `ore_loading_bay` — a rail terminus with ore sacks, a chute, and a holding bin. uncommon.
- `support_hall` — a wide chamber held up by a forest of `mine_support` timbers; structural drama. uncommon.

## 4. Abandoned / human-story set-pieces (atmosphere + loot)
- `abandoned_miners_camp` — a long-cold camp: dead campfire, bedroll, scattered tools, a tin cup, a journal
  page. uncommon. Reward: lore, salvage, maybe a stash.
- `miners_camp_active` — the *current* mining-camp scene: miner NPC, workbench, torches, signpost, chest
  (matches zone doc's Miner's Camp). one per zone (the hub).
- `lost_prospector_skeleton` — a skeleton slumped against a wall clutching a pick, a small treasure beside
  it. rare. Reward: relic + grim lore.
- `forgotten_shrine` — a small carved-stone shrine/idol in a side grotto, offerings long rotted. rare.
- `old_mine_office` — a timbered alcove with a ledger desk, a lantern, claim notices on the wall. rare.
- `dwarven_hall_ruin` *(deep, optional fantasy beat)* — carved pillars and broken stonework of an older,
  grander digging civilization. very rare.

## 5. Hazards & structural drama (danger landmarks)
- `collapsed_shaft` — a cave-in of rubble blocking a passage (dig through, or it gates an area). common.
- `rockfall_zone` — a chamber with cracked ceiling that drops rocks — a moving hazard room. uncommon.
- `lava_crack` — a glowing fissure venting heat, home to `emberfungus`/`magma_centipede`; light + danger. rare (deep).
- `gas_pocket_pocket` — a chamber with a hiss and a warning (firedamp): no open flame, or it blows. rare.
- `deep_chasm` — a black bottomless rift crossed by a rickety plank bridge or rope. uncommon. Tension beat.
- `unstable_floor` — a thin floor over a void that crumbles if overloaded. uncommon.

## 6. Bone, fossil & overgrown beats (the deep-time / ecology landmarks)
- `bone_pile_chamber` — a heap of old bones (prey of past predators); `bone_fungus` growing through (zone doc). uncommon.
- `fossil_wall` — a cliff face full of embedded fossils/`fossil_log_embedded`; collectible flavor. uncommon.
- `petrified_grove` — the small stand of petrified stumps (see trees doc) — a frozen-forest room. rare.
- `great_fungus_chamber` — the cavern of the `great_fungus_tree` (trees doc): glowing canopy, fungal garden
  floor, gentle detritivores. very rare. The zone's showpiece grotto.
- `sinkhole_light_shaft` — a hole to the surface dropping a shaft of daylight; etiolated plants + cave ivy
  cluster in the light pool. uncommon. The one place the surface world reaches in.
- `guano_chamber` — a bat/moth roost ceiling over a rich guano floor feeding lush fungus. uncommon.

---

## Notes
- **Composition role:** scatter 1 hub (`miners_camp_active`) + the `rail_tunnel` spine + 4–7 of these
  destinations per zone, connected by natural meandering tunnels (so most rooms feel *found*, not laid out).
- **Reward gradient:** prettiest/richest rooms (geode, gem_pocket, great_fungus_chamber) sit deepest / behind
  ore-cave threats (bugs doc) — danger gates spectacle.
- **Light contrast:** keep most of the cave dark; glow landmarks (glow_pool_grotto, glowing_crystal_node,
  great_fungus_chamber, sinkhole_light_shaft) are the visual payoffs of exploring.
- Several of these are **assemblies of decoration ids**, not single sprites — see the decorations doc for the
  parts (torches, supports, cart, sacks, campfire, stalactites…).
