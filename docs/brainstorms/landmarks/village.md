# Brainstorm — Village Landmarks

The "little features" that make the **village** (`village_21`) read as a real, lived-in town: the
civic square and its monument, the SW lake with its fishing docks and moored boat, the orchard, the
Fly Farm demo, and the navigational furniture (notice board, signpost, fountains). These are the
multi-tile *set pieces* a scene is built around — the individual props that dress them live in
[`decorations/village.md`](../decorations/village.md).

**Already in the catalog (reuse, don't re-add):** `well`, `fountain`, `birdbath`, `statue_stone`,
`statue_bug`, `notice_board`, `signpost`, `compost_pile`, `net_post`, `bait_basket`,
`collection_tray`, `fly_netting`, `autonet`, `garden_arch`, `fence_wood`/`gate_wood`,
`fence_iron`, `lamp_post`, `apple_crate`, `lily_pad`. Everything below is **new** village landmark
material. Many are *composite* set pieces (a docks landmark is dock-tiles + posts + boat + nets).

---

## 1. The civic square (town center)
The social heart: a monument, seating, navigation, and beds. Each shop announces itself by signage
(see decorations doc), but the *square* is the shared landmark.

| id | one-line | role / notes |
|----|----------|--------------|
| `monument_obelisk` | a tall stone OBELISK on a stepped base | the square's centerpiece monument; "founding of the town" |
| `monument_plinth` | an empty carved stone PLINTH with an inscription panel | hosts a statue or stands as a memorial |
| `statue_founder` | a bronze STATUE of a robed town founder on a plinth | civic statue (vs the generic `statue_stone`); the square's figure |
| `statue_mayor_bust` | a marble BUST of the mayor on a column | town-hall-forecourt vanity piece; "fancy" |
| `war_memorial` | a stone cross / memorial slab with a small wreath | solemn square corner; lore flavor |
| `town_clock` | a free-standing CLOCK on an ornate iron post | square focal point; "the town keeps time" |
| `flagpole` | a tall FLAGPOLE flying the village banner | civic marker by the town hall |
| `village_sign` | a grand carved "Welcome to ___" entry SIGN on posts | placed at the road-edge approaches |
| `square_paving_feature` | a decorative circular PAVING medallion (compass/crest inlay) | center-of-square ground feature |
| `bandstand` | a small open hexagonal BANDSTAND with a roof and rail | festival/music set piece; "fancy" town |

## 2. The well & fountains (water features)
Extends `well`/`fountain`/`birdbath` with a poor→fancy water-feature range.

| id | one-line | role / notes |
|----|----------|--------------|
| `well_open` | a plain stone WELL ring with no roof, bucket on the rim | the humble/old well (vs roofed `well`) |
| `pump_village` | a cast-iron hand PUMP over a stone trough | the working public water point |
| `water_trough` | a long stone TROUGH of water | for animals; rustic square edge |
| `fountain_tiered_grand` | a large multi-TIER ornate fountain with spouting figures | town-hall forecourt "fancy" centerpiece |
| `fountain_wall` | a WALL fountain — a carved mask spouting into a basin | tucked against a wall; courtyard feature |
| `fountain_simple` | a single low BASIN fountain with a bubbling jet | modest square fountain (vs grand `fountain`) |
| `wishing_well_coins` | a well with COINS glinting in the water | quest/lore variant; "make a wish" |

## 3. The SW lake — fishing docks, boat & shore
The Boat & Fishing Store sits *on the docks*. This is a composite landmark: water tiles + a dock
structure + posts/lanterns + a moored boat + shore dressing.

| id | one-line | role / notes |
|----|----------|--------------|
| `dock_plank` | a section of weathered wooden DOCK decking, top-down | the tile-able dock walkway out over the water |
| `dock_post` | a thick wooden mooring POST / piling rising from the water | dock edge; pairs with lanterns/rope |
| `dock_ladder` | a wooden LADDER down the dock edge into the water | dock detail |
| `boat_rowboat` | a small wooden ROWBOAT with two oars, top-down | the moored boat; rentable later |
| `boat_fishing` | a larger fishing BOAT with nets and crates aboard | the store's signature moored vessel |
| `boat_capsized` | an old half-sunk overturned BOAT at the shore | derelict shore flavor |
| `mooring_rope` | a coil of thick MOORING ROPE / a rope looped on a post | ties the boat to the dock |
| `buoy_float` | a red-and-white floating BUOY on the water | marks the swim/fish area |
| `fishing_net_drying` | a large fishing NET strung up to DRY on a frame | shore/dock dressing (distinct from bug `fly_netting`) |
| `lobster_pot` | a wicker/wire fishing TRAP / pot stacked on the dock | fishing-store prop; stackable |
| `fish_crate_iced` | a CRATE of fresh fish on ice | the store's catch on display |
| `tackle_box` | an open angler's TACKLE BOX of hooks and lures | fishing-store / dock prop |
| `fishing_rod_rack` | a RACK holding several fishing RODS upright | store display |
| `reed_bed` | a dense composite BED of lakeshore reeds | softens the shore; frog/dragonfly habitat |
| `stepping_stones` | a line of flat STONES across shallow water | crossing detail at the lake margin |
| `boathouse_small` | a small open-sided BOATHOUSE shed over the water | shelters the boat; lake set piece |
| `shore_rocks` | a cluster of wet shoreline ROCKS | natural lake-edge dressing |

## 4. The orchard (the wild fly engine)
Grid-aligned rows (trees from [`trees/village.md`](../trees/village.md)) plus the management props
and the rot layer that drives the fly chain.

| id | one-line | role / notes |
|----|----------|--------------|
| `orchard_row_marker` | a low painted ROW STAKE / number marker | reads "managed orchard rows" |
| `tree_guard` | a wooden GUARD cage around a young trunk | protects saplings; orchard detail |
| `fruit_ladder_lean` | a tall A-frame ORCHARD LADDER leaning on a tree | picking; pairs with the existing `ladder` |
| `picking_basket` | a wide shallow wicker FRUIT BASKET, half-full | harvest prop on the ground |
| `orchard_crate_stack` | a stack of fruit CRATES (apples/pears) | harvest storage (extends `apple_crate`) |
| `cider_press` | a wooden screw CIDER PRESS with a tub | the orchard's "what the fruit becomes"; lore/quest |
| `windfall_heap` | a raked HEAP of fallen fruit going soft | the rot source feeding flies/compost |
| `beehive_orchard` | a stacked wooden langstroth BEEHIVE among the trees | pollination; ties to bee town bugs |
| `scarecrow_orchard` | (reuse `scarecrow`) | bird deterrent; orchard dressing |

## 5. The Fly Farm (the *demo* of the ecology)
The legible, fenced version of the orchard's chain — the teaching set piece. Extends `compost_bin`,
`net_post`, `bait_basket`, `collection_tray`, `fly_netting`, `autonet`.

| id | one-line | role / notes |
|----|----------|--------------|
| `fly_farm_sign` | a painted "FLY FARM" board on a post with a fly icon | labels the enclosure |
| `bait_station` | a post-mounted DISH of rotting bait under a small roof | the controlled attractant; spawns flies |
| `rot_barrel` | an open BARREL of fermenting fruit mash, flies hazing above | strong controlled attractant |
| `larva_tray` | a shallow TRAY of squirming maggots/larvae | the farm's harvestable output (feed/bait) |
| `pupae_box` | a slatted BOX of fly pupae cases | rearing stage on display |
| `screen_cage` | a fine-MESH walk-in CAGE frame | keeps flies in for harvest; the farm's core structure |
| `funnel_trap` | a clear funnel-jar fly TRAP on a stand | passive catcher; teaching prop |
| `frog_pen` | a small fenced damp PEN with a frog (predator demo) | shows predators cropping the flies |
| `fly_chart_board` | a board diagramming the egg→maggot→fly→predator chain | the explicit teaching panel; ties to ecology proposal |

## 6. Navigation & town furniture (the small civic features)
| id | one-line | role / notes |
|----|----------|--------------|
| `signpost_directional` | a post with several arrow BOARDS pointing to neighbor zones | fast-travel/wayfinding (extends `signpost`) |
| `signpost_carved_fancy` | an ornate carved finger-post with gilded lettering | the town-hall-quality wayfinder |
| `notice_board_roofed` | a roofed glass-fronted NOTICE case of pinned papers | the quest/announcement board (extends `notice_board`) |
| `map_board` | a painted "You are here" MAP board on posts | town map for new players (spawn point) |
| `milestone_stone` | a small carved MILESTONE giving distances | road-edge wayfinding flavor |
| `bus_stop_post` | a simple shelter post marking the fast-travel point | the spawn/travel marker if not a signpost |
| `bridge_wood` | a short arched wooden BRIDGE over a stream/inlet | crossing the lake inlet / drainage |
| `gate_arch_town` | a stone/timber ARCHWAY gate over the entry road | the town's grand entrance landmark |

---

### How these compose into a scene (for `scene_village.py`)
- **Square:** `monument_obelisk` or `statue_founder` center, `bench`/`bench_stone` around it, beds of
  village flowers, `lamp_post`s, `town_clock`/`flagpole`, `notice_board_roofed` + `signpost_directional`,
  a `fountain_simple` or the grand one by the town hall.
- **SW lake:** water tiles, `dock_plank` run with `dock_post`s + dock lanterns, `boat_fishing` moored
  with `mooring_rope`, `reed_bed`/`reed_clump`, frogs + `lily_pad`s, the fishing store at the dock head.
- **Orchard:** rows of `tree_apple`/`tree_pear`/`tree_cherry`, `orchard_row_marker`s, `fruit_ladder_lean`,
  `windfall_heap` + `compost_pile`, `beehive_orchard`.
- **Fly Farm:** fenced (`fence_wood`/`gate_wood`), `screen_cage`, `bait_station`/`rot_barrel`,
  `net_post`s, `larva_tray`/`collection_tray`, `frog_pen`, `fly_chart_board`, `fly_farm_sign`.
The fly chain (egg→maggot→fly→predator) is detailed in [`bugs/village.md`](../bugs/village.md).
