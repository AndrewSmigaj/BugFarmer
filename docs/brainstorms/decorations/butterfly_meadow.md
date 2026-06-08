# Brainstorm: Butterfly Meadow — Decorations & Props

Placeable decor/props that fit a **flowering meadow → forest edge** theme (`butterfly_meadow_11`).
Two jobs:
1. **Zone dressing** — props that make the authored meadow scenes feel inhabited and storied (the
   failed farm, the bug-watcher's camp, the wild beauty).
2. **Player-farm bonuses** — decorations placed in the **private plot** grant small idle production
   multipliers with **diminishing returns per duplicate + an overall cap** (`game_design.md §11.5`).
   So variety matters: a poor→fancy ladder gives players a real layout puzzle. The standout meadow hook
   is **pollinator-attracting decor** — props that boost the pollination/nectar economy.

Bonus tags below are *proposed hooks* (the actual per-item value field is added with the §11.5 system).
Existing ids marked **[exists]** (from `decor.json` / `structures.json` / `lighting.json` / `furniture.json`).
EXTEND, don't duplicate. The "Decorations (passive-bonus hooks)" list in `docs/product/brainstorm_items.md`
is the cross-cutting menu; this is the meadow-flavored slice + new pollinator-themed props.

---

## Pollinator-attracting decor (the meadow's signature bonus class)
The headline mechanic for this zone: props that draw or support pollinators → boost the nectar/
pollination economy (more flowers/seeds, faster bug breeding, higher-value pollinator catches).
A poor→fancy ladder so the bonus scales with investment.
- `bee_skep` — a classic woven straw conical beehive (the storybook kind). **bonus: pollinator/honey.**
  *Decorative wild-hive look; the cheap-charming entry to the bee economy. Pairs with the Honey Hollow landmark.*
- `bee_box` — a simple stacked wooden Langstroth hive box. **bonus: pollinator/honey (higher than skep).**
  *The "real" beekeeping upgrade; cf. `beehive` in the cross-cutting menu.*
- `butterfly_house` — a tall narrow wooden box with vertical butterfly slots and a little roof.
  **bonus: pollinator (butterfly-weighted).** *The butterfly analog of a birdhouse; thematic centerpiece.*
- `mason_bee_hotel` — a wooden frame packed with hollow reeds/drilled blocks for solitary bees.
  **bonus: pollinator.** *Charming, "eco" flavor; supports `bee_mason`/`bee_carpenter`.*
- `nectar_feeder` — a hanging glass globe of sugar-water with little perches. **bonus: pollinator/nectar.**
  *Directly "feeds" the pollination heuristic; a mid-tier attractor.*
- `puddling_dish` — a shallow stone dish of damp sand/mud (butterfly mineral bar). **bonus: pollinator.**
  *Stages the real "puddling" behavior; cheap, lovely, on-theme.*
- `flower_planter` — a wooden `planter_box` (**[exists]**) overflowing with mixed wildflowers.
  **bonus: pollinator/comfort.** *Portable nectar; a way to bring the meadow into the plot.*
- `wildflower_pot` — a single terracotta pot of `flower_aster`/`lavender`. **bonus: pollinator (small).**
  *The cheapest pollinator decor; the first rung.*
- `pollinator_garden_sign` — a hand-painted "Pollinator Garden" stake sign. **bonus: set-completion flavor.**
  *A capstone marker; could grant a small bonus when N pollinator decor are nearby (set bonus).*
- `flower_arch` — a `garden_arch` (**[exists]**) wreathed in `morning_glory`/`bee_balm`.
  **bonus: pollinator/comfort.** *Doubles as the meadow's gateway prop and a nectar attractor.*

## Garden & comfort decor (pretty; comfort/happiness bonus)
General farm-prettiness that suits a meadow aesthetic.
- `sundial` — a stone pedestal sundial. **bonus: comfort.** *The literal heart of a "flower-clock glade"; classic.*
- `birdbath` **[exists]** — a stone basin on a pedestal. **bonus: comfort.** *Birds eat caterpillars — a subtle ecology nod; pretty.*
- `bird_feeder` — a hanging seed feeder on a pole. **bonus: comfort.** *Brings birds (and ambient life).* 
- `fountain` **[exists]** — a tiered water fountain. **bonus: comfort (high).** *The fancy end of water decor.*
- `wind_chime` — hanging tubes on a stand/branch. **bonus: comfort.** *Gentle motion + sound flavor.*
- `whirligig` — a painted wooden wind-spinner (a flying-insect whirligig). **bonus: comfort.** *Folk-art charm; meadow-breezy.*
- `garden_bench` — a `bench` (**[exists]**) for sitting among the flowers. **bonus: comfort.** *A "rest and watch the butterflies" spot.*
- `bench_stone` **[exists]** — a weathered stone bench. **bonus: comfort.** *Older, mossier counterpart.*
- `picnic_blanket` — a checkered blanket spread on the grass, maybe a basket. **bonus: comfort.** *Cozy human warmth; lovely in a meadow.*
- `flower_trellis` — a lattice `trellis`/`garden_arch` with climbing blooms. **bonus: comfort/pollinator.** *Vertical flower interest.*
- `flower_barrow` — an old wheelbarrow planted full of wildflowers. **bonus: comfort/pollinator.** *Failed-farm relic repurposed as decor; rustic.*
- `topiary_butterfly` — a shrub clipped into a butterfly shape. **bonus: comfort (fancy).** *Whimsical high-tier garden statement.*
- `gazing_ball` — a mirrored garden globe on a stand. **bonus: comfort.** *Classic kitsch-pretty garden ornament.*

## Statuary & focal points (fancy; comfort/trophy bonus)
A poor→fancy ladder of centerpiece statues, meadow-themed.
- `statue_butterfly` — a stone butterfly statue, wings spread. **bonus: comfort/trophy.** *Theme centerpiece; cf. `statue_bug` (**[exists]**) for a generic version.*
- `statue_bee` — a carved bee on a plinth. **bonus: comfort.** *Pollinator-themed focal point.*
- `statue_stone` **[exists]** — a generic weathered stone statue. **bonus: comfort.** *Neutral classic.*
- `statue_bronze_butterfly` *(fancy)* — a verdigris bronze butterfly. **bonus: comfort/trophy (high).** *The upscale tier.*
- `statue_gilded_monarch` *(rare/fancy)* — a gold-leafed monarch on a marble base. **bonus: comfort/trophy (top).** *The luxury capstone — the "I've made it" meadow trophy.*
- `flower_obelisk` — a tall stone marker carved with vines and blooms. **bonus: comfort.** *A vertical focal point for a flower garden.*

## Trophy & collector decor (rare-bug bonus)
The lepidopterist angle — displaying your catches, with a rare-bug/collection bonus hook.
- `specimen_case` — a glass-topped display case of pinned butterflies/moths. **bonus: trophy/rare-bug.** *The meadow's signature trophy; cf. `bug_terrarium` (**[exists]**).*
- `butterfly_terrarium` — a domed glass terrarium with live plants + a butterfly. **bonus: trophy/comfort.** *Living-display upscale of the case.*
- `specimen_jars` — a shelf/crate of labeled glass collecting jars. **bonus: trophy (small).** *Cluttered field-collector flavor; dresses the lepidopterist's blind.*
- `pinned_board` — a cork board of pinned specimens with handwritten labels. **bonus: trophy.** *The scientist's wall; great camp/study dressing.*
- `big_catch_plaque` — a mounted plaque for a record monarch/emperor. **bonus: trophy/rare-bug.** *Achievement flavor.*
- `pressed_flower_frame` — a framed arrangement of pressed wildflowers. **bonus: comfort/trophy.** *A botanical counterpart to the bug case; quiet and pretty.*

## Lighting & evening decor (evening/glow bonus)
For dusk moth-watching and the §11.5 evening-glow bonus class.
- `lantern` **[exists]** / `lantern_post` — a hung/posted lantern. **bonus: lighting.** *Moths gather here at dusk (`moth_brown`/`moth_luna`); ties lighting to the bug cast.*
- `lamp_post` **[exists]** — a meadow path lamp. **bonus: lighting.** *Path-lining classic.*
- `firefly_jar` — a glass jar of glowing fireflies on a post. **bonus: lighting/comfort.** *Magical dusk decor; pairs with `firefly_blue`.*
- `string_lights` — a strung line of warm bulbs (between posts/arches). **bonus: lighting/comfort.** *Festive meadow-evening warmth.*
- `paper_lantern` — a soft glowing paper lantern. **bonus: lighting.** *Gentle, pretty; festival flavor.*
- `moth_lamp` — a tall lantern with a pale sheet/screen behind it (a moth-trapping light). **bonus: lighting/trophy.** *The lepidopterist's night tool; doubles as moth-attractor flavor.*

## Rustic / failed-farm props (zone-dressing; story)
Mostly scene-dressing, but several work as rustic farm decor with a comfort bonus.
- `fence_wood` **[exists]** / `split_rail_fence` — the broken-fence material. *split-rail variant for the relic look.*
- `gate_wood` **[exists]** — a leaning farm gate. *Story prop; opens onto nothing.*
- `old_cart` — a broken wooden handcart, one wheel gone, weeds growing through it. **bonus: comfort (rustic).** *Failed-farm centerpiece; great planted with flowers (`flower_barrow`).*
- `hay_bale` — a round/square straw bale. **bonus: comfort (rustic/seasonal).** *Meadow-harvest flavor; seating; cf. cross-cutting menu.*
- `rain_barrel` — a wooden barrel catching water under a downspout-less post. **bonus: comfort/utility.** *Rustic water-collection prop.*
- `well` **[exists]** — an old stone well. **bonus: comfort.** *Failed-farm water source, now wild.*
- `weathervane` — a rusty rooster/butterfly weathervane on a post. **bonus: comfort.** *Reads the meadow breeze; rustic farm topper.*
- `nest_box` — a small wooden birdhouse on a pole. **bonus: comfort.** *Cheerful; birds = ambient + caterpillar control.*
- `stone_trough` — a cracked mossy stone water trough. **bonus: comfort.** *Failed-farm relic; butterflies puddle at its rim (links to the Stone Trough landmark).*
- `garden_marker` / `seed_stake` — little hand-lettered plant-row stakes. **bonus: flavor.** *Tiny detail props; the ghost of the old vegetable rows.*

## Naturalia (scene scatter; mostly cosmetic, minor bonuses)
Small natural props that dress scenes and (a few) grant tiny comfort bonuses in the plot.
- `boulder` / `boulder_mossy` — a big rounded rock (the Basking Boulder material). **bonus: comfort (small).** *Sun-warmed bug perch; natural focal point.*
- `flat_rock` — a low broad basking slab. *Butterfly/beetle basking spot; scene scatter.*
- `stone_cluster` — a few smaller scattered rocks (NB: project rule — no standalone "rocks"; use blocks/boulders). *Edge scatter via boulders, not loose rocks.*
- `dewdrop_web` — a dew-laden spider web strung on a frame/fence (decor capture of the orb-weaver beat). **bonus: flavor.** *A beautiful dawn detail prop.*
- `flower_wreath` — a woven ring of wildflowers (hung on a gate/post). **bonus: comfort.** *Handmade meadow charm; seasonal.*
- `wildflower_bundle` — a tied bunch of cut flowers leaning against a post. **bonus: comfort.** *Cozy "just gathered" flavor.*
- `nectar_log` — a hollow log with sap/fruit smeared on it (a butterfly bait log). **bonus: pollinator (butterfly).** *Baits `butterfly_emperor`/fruit-feeders; ties to the Emperor's Oak trick.*

## Notes on the bonus system (§11.5)
- Bonuses are **private-plot** idle multipliers with **diminishing returns per duplicate `id`** + a cap
  — so the design intent is **variety over stacking**. The meadow's contribution to the catalog is the
  **pollinator-attractor class** (a new themed bonus axis: nectar/pollination/honey) plus a rich
  comfort/trophy/lighting ladder.
- A future **set bonus** idea: placing a threshold of distinct pollinator decor near each other (skep +
  butterfly house + nectar feeder + flower planter + puddling dish) triggers a "pollinator paradise"
  bump — rewarding a themed garden, not a pile of one item. (`pollinator_garden_sign` as the marker.)
- Many entries above are **zone-dressing first** (failed-farm relics, the lepidopterist's camp) and only
  incidentally plot decor — flagged by their rustic/story framing. The scenes
  (`scene_butterfly_meadow.py`, `scene_meadow_forest_edge.py`) draw their props from here.
- Cross-reference the cross-cutting decoration menu in `docs/product/brainstorm_items.md` to avoid
  duplicating generic items; this doc adds the **meadow/pollinator-specific** props it doesn't cover.
