# Brainstorm — Village Decorations

The dressing that makes the **village** (`village_21`) the game's showcase: shop **signs** that make
each building unmistakable, **market stalls & awnings**, statues/fountains, benches & lamp posts,
planters, **fences & gates** in a poor→fancy range, banners, crates/barrels, the Smith's forge kit,
and **fancy mayor's-house** pieces (marble, columns, fancy mirrors). Plus **farm-bonus decorations**
— variety matters because player-farm decorations grant bonuses, so we want a clear poor→fancy ladder.

This is the richest doc on purpose. Sub-sections:
1. Building signs · 2. Market (stalls/awnings/produce) · 3. Statues & monuments · 4. Fountains &
water ornaments · 5. Seating · 6. Lighting & lamp posts · 7. Planters & garden ornaments ·
8. Fences, gates & walls · 9. Banners, flags & bunting · 10. Crates, barrels & storage ·
11. Smith / carpenter exterior props · 12. Fancy mayor / town-hall pieces · 13. NPC-cottage character
props · 14. Farm-bonus decorations (poor→fancy ladders) · 15. NEW furniture variety worth adding.

**Already in the catalog (reuse, don't re-add):** `bench`, `bench_padded`, `bench_stone`,
`lamp_post`, `lamp_floor`, `lantern`, `candle`, `candelabra`, `fountain`, `birdbath`, `well`,
`statue_stone`, `statue_bug`, `planter_box`, `vase`, `plant_large`, `rug`/`rug_large`/`rug_round`,
`mirror_standing`, `fence_wood`/`gate_wood`/`fence_iron`/`fence_electric`, `hedge`, `garden_arch`,
`notice_board`, `signpost`, `apple_crate`, `chest_wood`, `compost_bin`, `log_pile`, `chopping_block`,
`sawhorse`, `ladder`, `scarecrow`, `suit_of_armor`, `throne`, `column`(?—not present, add below).
Everything below is **new**.

---

## 1. Building SIGNS (make each shop unmistakable)
Signage is the zone's primary "this is the X shop" tell. Two formats per shop where useful: a
**hanging bracket sign** (over the door) and a **board/standee** (by the entrance).

| id | one-line | role / notes |
|----|----------|--------------|
| `sign_hanging_blank` | a blank wooden SIGN hanging from an iron bracket | base for any shop; re-skinned per shop |
| `sign_anchor` | a hanging sign with a painted ANCHOR (boat/fishing store) | the Boat & Fishing Store sign |
| `sign_fish` | a hanging sign shaped like / painted with a FISH | fishing-store variant |
| `sign_anvil` | a hanging sign with a forged ANVIL silhouette | the Smith's sign |
| `sign_horseshoe` | a hanging sign with a HORSESHOE | smith variant |
| `sign_hammer_saw` | a sign crossing a HAMMER and SAW (carpenter) | the Carpenter/Furniture sign |
| `sign_plank` | a rough sawn-PLANK sign with carved letters | carpenter standee |
| `sign_market_board` | a big hanging "MARKET" board | the market's hanging board |
| `sign_basket_goods` | a sign with a BASKET of goods (general store) | the General Store sign |
| `sign_mortar_pestle` | a sign with a MORTAR & PESTLE (apothecary/ecologist) | the Ecologist's / herb sign |
| `sign_leaf_bug` | a sign with a LEAF-and-BUG crest (ecologist) | ecologist's-house sign |
| `sign_crest_town` | a carved heraldic TOWN CREST shield | the Town Hall sign/crest |
| `sign_sandwich_board` | a folding A-frame chalk SANDWICH BOARD | "today's specials"; any shop |
| `sign_arrow_painted` | a small painted ARROW sign on a post | "this way to ___" |
| `sign_open_closed` | a little hanging OPEN/CLOSED door placard | shop-door detail |
| `shop_awning_sign` | a sign band printed across a shop AWNING valance | market/store frontage text |

## 2. Market — stalls, awnings & produce
The market is open-air stalls under a roof; lots of variety to fill it.

| id | one-line | role / notes |
|----|----------|--------------|
| `market_stall` | a wooden STALL — a counter under a striped peaked awning | the core market unit |
| `market_stall_empty` | a bare stall frame, no awning | "closed/unrented" stall |
| `awning_striped` | a striped fabric AWNING projecting from a wall | shop frontage; re-color per shop |
| `awning_scalloped` | a scallop-edged AWNING | fancier frontage |
| `canopy_tent` | a peaked market CANOPY tent on poles | bigger covered stall |
| `produce_box_veg` | an angled display BOX of mixed vegetables | stall produce; colorful |
| `produce_box_fruit` | a display BOX of mixed fruit | stall produce |
| `produce_basket_pile` | a cluster of woven BASKETS heaped with goods | stall front dressing |
| `hanging_sausages` | a string of cured SAUSAGES hung at a stall | food-stall detail |
| `hanging_herbs` | bundles of dried HERBS hung to dry | herb/apothecary stall |
| `cheese_wheel_stack` | a stack of round CHEESE wheels | dairy stall |
| `bread_basket` | a basket of LOAVES / baguettes | baker's stall |
| `flower_stall_buckets` | metal BUCKETS of cut flower bunches | flower stall (ties to flora doc) |
| `fish_stall_slab` | a slab of iced FISH on display | fishmonger stall |
| `scale_balance` | a brass two-pan balance SCALE | market weighing prop; "fancy" market detail |
| `cash_box` | a small wooden COIN box on a counter | stall/till detail |
| `price_chalkboard` | a small CHALKBOARD of prices | stall pricing |
| `barrel_open_apples` | an open BARREL spilling apples | market/general-store produce |

## 3. Statues & monuments (square / town hall / gardens)
Extends `statue_stone`/`statue_bug`. Poor→fancy: weathered grey stone → bronze → gilded marble.

| id | one-line | role / notes |
|----|----------|--------------|
| `statue_fountain_cherub` | a small cherub figure spouting water (statue+fountain) | town-hall garden centerpiece |
| `statue_bronze_figure` | a green-patina BRONZE figure on a plinth | civic statue (mid tier) |
| `statue_marble_figure` | a white MARBLE classical figure | "fancy" mayor/town-hall statue |
| `statue_animal_cat` | a carved stone CAT statue | NPC-cottage character piece (per zone doc) |
| `statue_animal_dog` | a carved stone DOG / hound statue | gatepost guardian pair |
| `statue_lion_gate` | a stone LION couchant for flanking gates | grand-entrance pair; "fancy" |
| `statue_gnome_garden` | a cheeky painted GARDEN GNOME | humble/cute farm-bonus decor |
| `bust_on_pedestal` | a small carved BUST on a slim pedestal | hall/study accent (overlaps mayor pieces) |
| `sundial` | a stone SUNDIAL on a pedestal | civic-garden ornament |
| `urn_stone` | a large carved stone URN (decorative, planted or empty) | flanks steps; classical |

## 4. Fountains & water ornaments
See landmarks for the big set-piece fountains; these are placeable garden ornaments.

| id | one-line | role / notes |
|----|----------|--------------|
| `fountain_birdbath_fancy` | an ornate carved BIRDBATH with a spout | fancier than `birdbath` |
| `garden_pond_small` | a small lined ORNAMENTAL POND with a lily | cottage-garden water feature (farm-bonus) |
| `water_jar_spilling` | a tipped JAR fountain trickling into a bowl | rustic courtyard water ornament |
| `fountain_frog_spout` | a small bronze FROG spouting into a basin | playful garden fountain |

## 5. Seating
Extends `bench`/`bench_padded`/`bench_stone`.

| id | one-line | role / notes |
|----|----------|--------------|
| `bench_iron_garden` | an ornate wrought-IRON GARDEN BENCH with a curved back | "fancy" square/garden seat |
| `bench_picnic` | a wooden PICNIC TABLE with attached bench seats | farm/market communal seat |
| `bench_log` | a split-LOG bench, rustic | poor/rustic seat (carpenter/cottage) |
| `bench_swing` | a hanging porch SWING SEAT on a frame | cottage-porch charm; farm-bonus |
| `chair_outdoor` | a simple slatted OUTDOOR CHAIR | cafe/stall seat |
| `cafe_table_round` | a small round bistro CAFE TABLE | paired with outdoor chairs at the square |
| `deck_chair` | a striped folding DECK CHAIR | lakeside leisure piece |

## 6. Lighting & lamp posts
Extends `lamp_post`/`lantern`/`candle`/`candelabra`.

| id | one-line | role / notes |
|----|----------|--------------|
| `lamp_post_double` | a lamp post with TWO lanterns on a scrolled arm | grander street lighting |
| `lamp_post_fancy` | an ornate cast-iron LAMP POST with gilt details | town-hall / square "fancy" lighting |
| `lantern_hanging` | a LANTERN hanging from a wall bracket | shop frontage / dock lighting |
| `lantern_post_dock` | a weathered lantern on a short DOCK post | the docks' lighting (per zone doc) |
| `string_lights` | a swag of small festive STRING LIGHTS | festival/market dressing |
| `torch_garden` | a tiki/garden TORCH on a stake | path lighting; rustic |
| `brazier_iron` | an iron BRAZIER with glowing coals | square/forge ambient warmth |
| `paper_lantern` | a soft round paper LANTERN, glowing | festival lighting variety |
| `gas_lamp_wall` | a wall-mounted GAS LAMP fixture | building-exterior lighting |

## 7. Planters & garden ornaments
Extends `planter_box`/`vase`/`plant_large`. Poor (clay pot) → fancy (urn/jardiniere).

| id | one-line | role / notes |
|----|----------|--------------|
| `pot_terracotta` | a single TERRACOTTA pot with a small plant | the humble planter; everywhere |
| `pot_terracotta_row` | a ROW of three clay pots with herbs | windowsill/step grouping |
| `window_box` | a WINDOW BOX of trailing flowers (mounts under a window) | the NPC-cottage signature (per zone doc) |
| `planter_trough_stone` | a long STONE TROUGH planter | civic-quality planter |
| `planter_urn_fancy` | a carved stone URN spilling flowers | "fancy" doorway planter |
| `planter_barrel` | a half-BARREL planter of flowers | rustic farm planter |
| `planter_wheelbarrow` | an old WHEELBARROW planted with flowers | charming farm-bonus decor |
| `hanging_basket` | a HANGING BASKET of trailing blooms on a bracket | shop/porch frontage |
| `plant_stand_tiered` | a tiered PLANT STAND of potted plants | porch/conservatory display |
| `jardiniere` | an ornate footed JARDINIERE planter | "fancy" interior/forecourt |
| `garden_gnome_group` | (see `statue_gnome_garden`) | — |
| `gazing_ball` | a mirrored GAZING BALL on a stand | kitschy/charming garden ornament |
| `bird_feeder` | a hanging BIRD FEEDER on a pole | ties to town birds; farm-bonus |
| `bird_house` | a little BIRDHOUSE on a post | cottage-garden charm |
| `bug_hotel` | a stacked "BUG HOTEL" habitat box | ecologist/farm decor; pollinator-bonus tie-in |

## 8. Fences, gates & walls (poor→fancy)
Extends `fence_wood`/`gate_wood`/`fence_iron`/`fence_electric`/`hedge`/`garden_arch`.

| id | one-line | role / notes |
|----|----------|--------------|
| `fence_picket` | a white PICKET fence section | the classic tidy cottage fence |
| `gate_picket` | a matching white PICKET gate | cottage front gate |
| `fence_picket_weathered` | a grey peeling PICKET fence | poor/run-down variant |
| `fence_stone_low` | a low dry-STONE WALL section | rustic field/cottage boundary |
| `wall_stone_capped` | a mortared stone wall with a flat CAP | tidier garden wall |
| `wall_brick_garden` | a low BRICK garden wall section | town garden boundary |
| `fence_iron_ornate` | an ornate wrought-IRON railing with finials | "fancy" town-hall railing |
| `gate_iron_grand` | a tall double WROUGHT-IRON GATE with a crest | town-hall / mayor entrance; "fancy" |
| `gate_arch_iron` | an iron arch with a sign over a gate | grand garden entrance |
| `fence_post_chain` | low POSTS linked by swag CHAIN | bordering monuments/beds |
| `bollard_stone` | a short stone BOLLARD | edges paving / keeps carts out |
| `trellis_panel` | a lattice TRELLIS panel for climbers | pairs with `rose_climber`/`wisteria_vine` |
| `pergola_section` | a beamed PERGOLA section over a path | "fancy" garden structure |

## 9. Banners, flags & bunting (festive town)
| id | one-line | role / notes |
|----|----------|--------------|
| `banner_town_crest` | a vertical hanging BANNER with the town crest | town-hall frontage (per zone doc) |
| `banner_shop` | a colored shop BANNER on a pole | shop frontage variety |
| `bunting_triangle` | a string of triangular flag BUNTING | strung across the square / market; festive |
| `flag_on_pole` | a small FLAG on a wall pole | building accent |
| `pennant_pair` | a crossed pair of PENNANTS | gate/entrance heraldry |
| `welcome_mat` | a woven WELCOME MAT at a door, top-down | cottage-door charm |
| `garland_evergreen` | a draped EVERGREEN garland | seasonal door/rail dressing |

## 10. Crates, barrels & storage (lived-in clutter)
Extends `apple_crate`/`chest_wood`/`compost_bin`.

| id | one-line | role / notes |
|----|----------|--------------|
| `barrel_wood` | a plain closed wooden BARREL | the ubiquitous shop-front prop |
| `barrel_stack` | a STACK of barrels | warehouse/store dressing |
| `crate_plain` | a plain wooden CRATE (no apples) | generic storage (vs `apple_crate`) |
| `crate_stack` | a STACK of mixed crates | store/market backdrop |
| `sack_grain` | a bulging burlap SACK of grain | general-store / market |
| `sack_pile` | a heap of stacked SACKS | store dressing |
| `barrel_pickle` | an open BARREL of pickles/brine | market food detail |
| `milk_churn` | a metal MILK CHURN | farm/dairy-stall prop |
| `crate_bottles` | a crate of glass BOTTLES | general-store / cider tie-in |
| `basket_wicker` | a large empty WICKER basket | versatile market/cottage prop |
| `firewood_rack` | a RACK of stacked firewood against a wall | cottage-exterior dressing |

## 11. Smith / carpenter exterior props
The Smith and Carpenter announce themselves with working props (per zone doc).

| id | one-line | role / notes |
|----|----------|--------------|
| `anvil` | a heavy steel ANVIL on a stump | the Smith's signature; exterior forge |
| `forge_outdoor` | a stone FORGE hearth with glowing coals and a chimney | the Smith's exterior forge (the fire glow) |
| `bellows` | a leather BELLOWS beside a forge | smith prop |
| `coal_bin` | an iron BIN of black coal | smith fuel store |
| `tool_rack_wall` | a wall RACK of hung hammers/tongs | smith/carpenter tool display |
| `quench_barrel` | a barrel of water with tongs (quenching) | smith prop |
| `grindstone` | a foot-pedal GRINDSTONE wheel | sharpening; smith/carpenter |
| `horseshoe_pile` | a small heap of HORSESHOES | smith product dressing |
| `metal_bar_stack` | a stack of iron BAR stock | smith raw material; ties to pen-upgrade lore |
| `workbench_carpenter` | a sturdy WORKBENCH with a vise and tools | the Carpenter's working surface |
| `lathe_wood` | a treadle wood LATHE | carpenter workshop centerpiece |
| `furniture_display_outdoor` | a chair/table set on DISPLAY out front | carpenter showroom (per zone doc) |
| `lumber_rack` | a slanted RACK of sorted planks | carpenter stock display |
| `plane_chisels` | hand PLANE and chisels on a bench | carpenter detail |
| `wood_glue_clamps` | a glued-up piece in CLAMPS | carpenter detail |

## 12. Fancy mayor / town-hall pieces (marble, columns, mirrors)
The Town Hall is the largest, fanciest building (per zone doc): marble walls, columns, a statue out
front, a big map table, a fancy mirror. Extends `throne`/`suit_of_armor`/`mirror_standing`.

| id | one-line | role / notes |
|----|----------|--------------|
| `column_marble` | a fluted white MARBLE COLUMN | the town-hall portico; place in a row |
| `column_marble_half` | a half-column PILASTER against a wall | wall-articulation accent |
| `pediment_carved` | a carved triangular PEDIMENT over a doorway | grand-entrance crown |
| `balustrade_marble` | a section of carved marble BALUSTRADE rail | hall stair/terrace rail |
| `mirror_gilt_fancy` | a large GILT-framed ornate wall MIRROR | the "fancy mirror" (per zone doc) |
| `map_table_big` | a large map TABLE strewn with charts | the mayor's "buy land" table (per zone doc) |
| `chandelier_crystal` | a hanging CRYSTAL CHANDELIER | town-hall ceiling "fancy" |
| `red_carpet_runner` | a long RED CARPET runner, top-down | the grand-entrance runner |
| `velvet_rope_stanchion` | a brass POST-AND-VELVET-ROPE pair | cordons in the hall; "fancy" |
| `marble_floor_inlay` | a decorative MARBLE FLOOR medallion, top-down | hall floor centerpiece |
| `bust_marble_pedestal` | a marble BUST on a fluted pedestal | hall/foyer vanity (overlaps statues) |
| `tapestry_wall` | a large woven WALL TAPESTRY with a crest | hall wall hanging |
| `gilt_frame_portrait` | a gilt-framed PORTRAIT of a past mayor | hall wall art |
| `coat_of_arms_shield` | a mounted heraldic SHIELD / coat of arms | hall/gate heraldry |
| `urn_marble_pair` | a pair of carved MARBLE URNS | flank the hall steps |

## 13. NPC-cottage character props (each house themed)
The zone doc wants each cottage distinct (cat statue, laundry line, chimney smoke, veg patch). Small
exterior props that give a cottage personality.

| id | one-line | role / notes |
|----|----------|--------------|
| `laundry_line` | a LINE of hung washing between two posts | the "lived-in" tell |
| `clothes_drying_rack` | a folding wooden DRYING RACK of clothes | cottage-yard detail |
| `chimney_smoke` | a small CHIMNEY pot with a wisp of smoke | rooftop life (if rooftop props exist) |
| `door_wreath_seasonal` | a seasonal WREATH on a cottage door | charm; varies by house |
| `boot_scraper` | a small iron BOOT SCRAPER by a door | cottage detail |
| `milk_bottles_step` | a couple of MILK BOTTLES on a doorstep | morning-life detail |
| `cat_basket` | a wicker CAT BASKET with a sleeping cat | the cat-themed cottage |
| `dog_kennel` | a small wooden DOG KENNEL | the dog-themed cottage |
| `rain_barrel` | a water BUTT / rain barrel under a downpipe | practical cottage prop |
| `garden_tools_leaning` | a rake, hoe and spade LEANING on a wall | gardener-cottage detail |
| `watering_can` | a metal WATERING CAN | veg-patch prop; common |
| `wheelbarrow` | a wooden WHEELBARROW (empty/with soil) | garden work prop |
| `compost_heap_open` | an open COMPOST heap (vs `compost_bin`) | scruffy veg-patch corner |
| `garden_kneeler` | a small foam KNEELER pad and trowel | gardener detail |
| `doormat_coir` | a coir DOORMAT, top-down | cottage threshold |
| `flowerpot_windowsill` | a small POT on a windowsill ledge | cottage-window detail |

## 14. Farm-bonus decorations (the poor→fancy ladders)
Player-farm decorations grant bonuses, so variety + a clear ladder is the point. Group by a likely
*theme bonus* (final numbers belong in a balance doc). Each list runs **poor → fancy**.

| theme / likely bonus | poor → fancy ladder (ids) |
|----|----|
| **Seating / comfort** (rest/mood) | `bench_log` → `bench` → `bench_padded` → `bench_iron_garden` → `bench_swing` |
| **Lighting** (night yield / safety) | `torch_garden` → `lamp_post` → `lamp_post_double` → `lamp_post_fancy`; `paper_lantern`/`string_lights` (festive) |
| **Water features** (calm / pollinator) | `birdbath` → `garden_pond_small` → `fountain_simple` → `fountain` → `fountain_tiered_grand` |
| **Planters / flowers** (growth / pollinator) | `pot_terracotta` → `planter_box` → `planter_barrel` → `planter_trough_stone` → `planter_urn_fancy`/`jardiniere` |
| **Statuary / prestige** (value / visitors) | `statue_gnome_garden` → `statue_stone` → `statue_bronze_figure` → `statue_marble_figure`/`statue_lion_gate` |
| **Fencing / order** (farm tidiness) | `fence_picket_weathered` → `fence_wood` → `fence_picket` → `fence_iron` → `fence_iron_ornate` |
| **Wildlife / habitat** (bug attract) | `bird_house` → `bird_feeder` → `bug_hotel` → `beehive_orchard` |
| **Festive** (event bonus) | `bunting_triangle`, `string_lights`, `garland_floral`, `flower_wreath`, `flagpole` |
| **Pathing** (movement / charm) | `stepping_stones`, `garden_arch`, `trellis_panel`, `pergola_section`, `gate_arch_town` |

> Design note: keep each ladder's *poor* end genuinely humble (weathered, rustic, single-item) and the
> *fancy* end clearly premium (marble, gilt, ornate iron, multi-tier) so the bonus delta reads visually.

## 15. NEW furniture variety worth adding (interiors of shops & homes)
Beyond decor — these fill the *interiors* the zone doc calls out (cozy NPC homes, the carpenter's
showroom, the fancy town hall). Extends the existing furniture catalog.

| id | one-line | role / notes |
|----|----------|--------------|
| `sofa_modern` | a clean low-line MODERN SOFA, square cushions | the "modern" end vs `sofa`/`sofa_fancy` (modern↔comfy range) |
| `sofa_comfy_worn` | a soft, slightly worn overstuffed COUCH | the cozy/poor end of the sofa range |
| `armchair_wicker` | a woven WICKER armchair | porch/conservatory seat |
| `dining_set_rustic` | a plain farmhouse TABLE with bench seats | the cottage dining set (vs `dining_table_fancy`) |
| `kitchen_dresser` | a tall farmhouse DRESSER with open plate shelves above drawers | cottage-kitchen storage |
| `welsh_settle` | a high-backed wooden SETTLE bench | rustic cottage hall seat |
| `writing_bureau` | a slant-front BUREAU desk with pigeonholes | study/ecologist piece (vs plain `desk`) |
| `display_counter_shop` | a glass-front SHOP COUNTER with goods | general-store / market interior |
| `shop_shelving` | tall STORE SHELVING stocked with sundries | the goods "visible through the open front" (per zone doc) |
| `seed_rack` | a rack of labelled SEED packets/drawers | general-store seed display |
| `apothecary_cabinet` | a many-drawered APOTHECARY cabinet | ecologist's-house specimen storage |
| `specimen_shelf` | a shelf of SPECIMEN JARS | ecologist's house (per zone doc) |
| `map_table_small` | a small TABLE with a rolled map | study/ecologist piece |
| `card_catalog` | a small drawered CARD CATALOG | ecologist's records |
| `hat_stand` | a curved wooden HAT/coat stand | hall entry (vs `coat_rack`) |
| `umbrella_stand` | a tall STAND of umbrellas/canes | hall-entry detail |
| `fire_screen` | a decorative FIRE SCREEN before a hearth | pairs with `fireplace` |
| `log_basket` | a woven BASKET of firewood by the hearth | cozy-hearth detail |
| `tea_trolley` | a two-tier rolling TEA TROLLEY with a pot | cottage/parlor charm (vs `bar_cart`) |
| `dresser_painted` | a cheerfully PAINTED dresser | the "comfy/charming" range vs `dresser_fancy` |
| `bench_settle_storage` | a wooden bench-chest with a hinged seat (storage) | hall/entry combo piece |

---

### Cross-references
- Signs/awnings make each shop legible — the zone doc's core requirement (§"The town — buildings").
- Planters/window boxes pull plants from [`flora/village.md`](../flora/village.md); orchard/carpenter
  wood props connect to [`trees/village.md`](../trees/village.md).
- Set-piece landmarks (the docks, square monument, fly farm) live in
  [`landmarks/village.md`](../landmarks/village.md); this doc is the *props that dress them*.
- The bug-attract / pollinator decorations (`bug_hotel`, `bird_feeder`, `beehive_orchard`, flower
  planters) tie to the benign town ecology in [`bugs/village.md`](../bugs/village.md).
