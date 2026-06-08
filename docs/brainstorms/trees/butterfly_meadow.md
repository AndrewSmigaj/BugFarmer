# Brainstorm: Butterfly Meadow — Trees, Stumps & Deadwood

Trees for the **Butterfly Meadow** (`butterfly_meadow_11`). Two distinct populations:
1. **Scattered meadow trees** — lone or small-clustered, sun-loving, open-grown (wide crowns); shade
   islands the meadow drifts around.
2. **The northern forest-edge band** — trees thicken into a wall of woodland along the top edge, plus
   the **deadwood** (stumps, fallen logs, snags) that hosts fungus and shelters the millipedes/centipedes.

The trees are NOT just backdrop: open-grown trees are basking/perch spots and shade refuges; flowering
trees are seasonal **nectar** booms; deadwood is the decomposition layer and the cover the edge threats
hide under. Favor a poor→fancy/dense range so the gradient reads: lone meadow tree → thicket → forest wall.

Existing ids (`tools/art/catalog/flora.json`) marked **[exists]**; the rest are new proposals.
EXTEND, don't duplicate.

---

## Scattered meadow trees (open-grown, sun-loving)
Lone or in 2–3 clusters; wide round crowns from growing in the open. These define the meadow's
"islands" and give pollinators perches.
- `tree_oak` **[exists]** — thick trunk, big round full canopy. *Ecology: the lone landmark oak; a basking-and-shade island; oaks host huge numbers of caterpillars (a quiet caterpillar engine even out in the meadow).*
- `tree_apple` **[exists]** — green canopy dotted with red apples. **nectar** (spring blossom boom) + **edible/gatherable** (apples; ties to `fallen_fruit`). *Ecology: a relic of the failed farm by the broken fence — blossoms feed pollinators, windfalls feed flies. Story + ecology.*
- `tree_crabapple` — smaller gnarled apple with a cloud of pink-white blossom and tiny sour fruit. **nectar** (massive blossom) + **gatherable**. *Ecology: an even bigger spring nectar boom than the apple; a butterfly magnet in bloom.*
- `tree_hawthorn` — small dense thorny tree, white flower clusters, red haws. **nectar** + **edible** + cover. *Ecology: thorny refuge tree; bridges meadow shrubs and the forest edge.*
- `tree_willow_meadow` — a lone weeping willow leaning over the damp spring/puddle, trailing fronds. *Ecology: marks the water feature; cool, drooping, a different silhouette.*
- `tree_birch_lone` — slender white-barked birch, light airy canopy. *Ecology: a bright, elegant meadow accent tree; reads "edge of woodland coming."*
- `tree_rowan` — small tree with feathery leaves and orange-red berry clusters (mountain ash). **edible/gatherable** (berries) + minor **nectar**. *Pretty, story-book; fruit for foragers.*
- `tree_serviceberry` — small multi-stem tree, early white blossom, dark sweet berries. **nectar** + **edible**. *Ecology: one of the earliest spring nectar sources — first food after winter.*
- `tree_redbud` — small tree whose bare branches flush with pink-purple flowers. **nectar** (very early). *Rarity: uncommon; a showpiece spring-color accent.*

## Forest-edge trees (the northern band — denser, taller, shadier)
These crowd together along the top edge into a darkening wall. Tall, narrow, shade-casting — the
visual + ecological "you are leaving the safe meadow" signal.
- `tree_pine` **[exists]** — tall conical evergreen. *Ecology: anchors the forest band; deep shade; the dark green that cools the palette northward.*
- `tree_spruce` — narrower, denser, darker conical evergreen. *Tighter, gloomier than pine — packs the densest part of the band.*
- `tree_maple` — broad-canopy deciduous, leaves blushing red/orange at the edge. **gatherable** (sap → syrup). *Ecology: a warm-toned forest-edge tree; seasonal color where meadow meets woods.*
- `tree_beech` — smooth grey trunk, dense leafy crown casting heavy shade. *Ecology: closes the canopy — under it, almost nothing flowers (the "gloom" begins).*
- `tree_birch_clump` — a tight stand of several white birches. *A denser counterpart to the lone birch; transition density.*
- `tree_alder` — damp-loving small tree near the spring's forest-edge run. *Ecology: ties the water feature into the shaded north.*
- `tree_dead` — a bare, leafless grey snag still standing, branches like antlers. *Ecology: a standing dead tree — woodpecker holes, bracket fungus, beetle galleries; an ominous edge silhouette.*
- `tree_hollow` *(rare)* — an old hollow-trunked tree with a dark cavity at the base. *Ecology: a den — centipedes/millipedes (and maybe worse) emerge from it; a natural "spawn point" landmark.*

## Stumps, logs & deadwood (the decomposition + cover layer)
The forest edge is littered with dead wood from old clearing. This is where **fungus grows**
(see the flora doc) and where the **edge threats shelter** — flipping/clearing it is a risk-reward beat.
- `stump` **[exists]** — low cut stump showing rings + roots. **gatherable** (wood) + fungus host. *Ecology: relic of the failed farm's clearing; centipedes hide beneath; bracket fungus grows on it.*
- `stump_mossy` — a stump furred over with green moss and a few toadstools. *Ecology: an older, "reclaimed" stump — the forest taking the clearing back.*
- `log_pile` **[exists]** — neat stack of cut logs, pale ends out. **gatherable** (wood). *Ecology: another failed-farm relic; cover for bugs in the gaps.*
- `log_fallen` — a long single fallen trunk lying across the ground. *Ecology: THE forest-edge "fallen-log bridge" landmark; oyster/turkeytail fungus on it; a centipede highway.*
- `log_mossy` — a rotting moss-covered log crumbling into the soil. **gatherable** (rotten wood) + heavy fungus host. *Ecology: late-stage decay; richest fungus + grub habitat → millipede feeding ground.*
- `branch_pile` — a loose heap of fallen sticks and twigs. **gatherable** (kindling). *Cheap scatter detail; minor cover.*
- `root_tangle` — a clump of exposed gnarled roots from a toppled tree. *Ecology: dramatic edge detail; dark hollows beneath for lurkers.*
- `snag_short` — a short broken-off trunk, jagged top, woodpecker holes. *Mid-tier deadwood between stump and dead tree.*
- `sawn_stump_fresh` — a pale fresh-cut stump with sawdust around it. *Ecology: a story prop — someone has been logging here recently (hook for the lumberjack NPC / forest zones north).*

## Ecology & gradient notes
- **Open vs. closed canopy** is the core gradient: scattered wide-crown meadow trees (sun reaches the
  ground → flowers thrive) → the dense forest-edge band (canopy closes → flowers give way to ferns,
  moss, and mushrooms). Trees literally control where the meadow's nectar can grow.
- **Flowering trees are seasonal nectar spikes:** apple/crabapple/hawthorn/serviceberry/redbud blooms
  are short, intense pollinator booms — a reason for swarms to surge to a tree island in season.
- **Deadwood is the danger layer:** stumps, logs, and snags are where fungus grows AND where
  millipedes/centipedes shelter. Clearing/harvesting wood near the edge should feel risk-rewardy —
  good loot, but you might flip a centipede.
- **The fallen-log bridge** (`log_fallen`) is both a landmark and a literal crossing into harder ground;
  it's the visual handoff from meadow to forest.
- **Caterpillar host trees:** oak, willow, and birch quietly host many caterpillar species — so even
  the meadow's trees feed the food web, not just the milkweed.
- **Wood gatherables ladder:** branch pile / kindling (cheap) → stump / log pile (mid) → big fallen
  logs (most wood, but guarded by edge threats). Wood is the zone's only real non-forage material.
