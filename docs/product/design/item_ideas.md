# Item ideas — running scratchpad

A brainstorm wishlist of possible world items (decorations, furniture, functional), to pull from
when building scenes/zones. Not committed work — promote an item by adding the entity
(`add-object`) and an `OBJECT_DESC`, then it moves to `art_needed.md`. ✅ = already exists in the
catalog. Sizes are rough footprint guesses.

## Fly-farm / bug lifecycle (functional)
- ✅ autonet — slow auto-catcher (vat + fan), GDD §11.4
- ✅ compost_bin — loadable, attracts flies
- ✅ fly_netting — pen enclosure mesh (blocks bugs)
- ✅ fallen_fruit / ✅ rotten_fruit — food / fly attractant
- ✅ bait_basket — lure (needs art)
- ✅ collection_tray — passive catch surface (needs art)
- ✅ net_post — placeable net station (needs art)
- egg_pile (1×1) — rotten substrate → eggs (GDD §6 life stages)
- larva_tray / incubator (1×1–2×1) — eggs → larvae → adults
- fly_lure / bait_station (1×1) — active attractant
- extractor (2×2) — process caught bugs into goods
- feed_trough / water_trough (2×1) — sustain a pen
- specimen_jar (1×1) — captured single bug on display (pairs with bug_terrarium)

## Outdoor / garden decor
- ✅ fountain (2×2) — expensive centerpiece
- ✅ well, ✅ statue_stone, ✅ signpost, ✅ planter_box, ✅ bench, ✅ lamp_floor
- ✅ stump, ✅ log_pile, ✅ compost_pile, ✅ apple_crate, ✅ notice_board (some need art)
- birdbath (1×1) — small water feature, attracts bugs
- trellis / garden_arch (1×2) — vines/flowers climbing
- hedge (1×1, tileable like fence) — green privacy row
- lamp_post (1×1, tall) — outdoor light
- wheelbarrow (2×1), hay_bale (1×1 or 2×1), barrel_planter (1×1)
- scarecrow (1×2) — decor, maybe minor bug effect
- stepping_stones (1×1 path decor), garden_gnome (1×1 whimsy), wind_chime (1×1)
- small pond + lily_pad (toward the docks/water scene), reeds ✅
- weathervane / small windmill (1×2)

## Interior furniture (more variety)
- ✅ sofa, armchair, nightstand, dresser, rug, bookshelf, bed_basic/fancy, table_wood/stone,
  chair_wood/fancy, fridge, stove, sink, counter, keg, bug_terrarium, vase, lamp_floor/table
- wardrobe (2×1), desk (2×1) + stool (1×1), coffee_table (2×1), side_table (1×1)
- rocking_chair (1×1), crib (2×2), wine_rack (1×1), kitchen_island (2×2)
- pot_rack / spice_rack (wall — see below), bookshelf_tall, dresser_mirror

## Wall-hung (need the deferred WALL-OVERLAY render feature first)
Orphan sprites already exist for several; they need entities + the overlay pass to place on walls.
- painting_small ✅, painting_large ✅, clock ✅, mirror ✅, banner ✅, shelf ✅ (all orphan art)
- mounted bug frame / trophy, wall sconce, wall_clock, pennant, calendar, wall torch (torch_wall ✅)

## Bugs (sprites already in Resources/Bugs — render via place_bug)
- ✅ fly_common, butterfly_common, butterfly_monarch, honeybee, bumblebee, dragonfly, firefly,
  moth_common, ladybug, grasshopper, cricket, beetle_common, stag_beetle, wasp_common, hornet,
  locust, centipede, millipede, spiders (jumping/wolf/cave/tarantula/black_widow), scorpion,
  ant_worker/queen
- TODO bug types to add (GDD): mosquito (swarm), more butterflies, frog/spider as predators

## Notes
- Decorative **rocks** were considered and dropped for now (old rule: no standalone rocks, use
  `stone_block`). Revisit if a natural-rock look is wanted later.
- Wall-hung items are blocked on the wall-overlay render feature (occupant cells are reserved by
  the wall sprite, so an overlay layer is needed).
