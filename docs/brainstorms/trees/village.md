# Brainstorm — Village Trees

Trees for the **village** (`village_21`): the grid-aligned **orchard** (the fly-ecology engine —
fruit → fallen fruit → rot → flies), tidy **shade/ornamental trees** lining roads and the civic
square, and the **woodcutter/carpenter's stock** (logs, stumps, sawn goods). These trees read
*planted and managed*, not wild forest.

**Scope note:** stumps/log piles/chopping props that are clearly *cut wood* are also relevant to
[`decorations/village.md`](../decorations/village.md); ground fruit / fallen fruit / compost are in
[`flora/village.md`](../flora/village.md). Bug ties are in [`bugs/village.md`](../bugs/village.md).

**Already in the catalog (reuse, don't re-add):** `tree_apple`, `tree_orange` (occupants),
`tree_oak`, `tree_pine`, `tree_palm`, `tree_dead`, `tree_fruit` (generic), `stump`, `log_pile`,
`fallen_fruit`, `fallen_orange`, `compost_pile`, `chopping_block`, `sawhorse`, `ladder`,
`apple_crate`, `grapevine`. Everything below is **new**.

---

## 1. Orchard fruit trees (the rows; the ecology engine)
Grid-aligned rows are the orchard's signature. Each fruiting tree should have a clear ripe form and
drop matching `fallen_*` fruit that rots into a fly attractant. A poor→prize range = a scrappy
seedling vs a heavy-laden mature tree vs an espaliered show specimen.

| id | one-line | role / notes |
|----|----------|--------------|
| `tree_pear` | a PEAR TREE — upright leafy canopy dotted with green-gold pears | core orchard row; drops `fallen_pear` |
| `tree_cherry` | a CHERRY TREE — rounded canopy with clusters of small red cherries | spring blossom + summer fruit; drops `fallen_cherry` |
| `tree_cherry_blossom` | a CHERRY tree in full pink BLOSSOM, no fruit | seasonal/ornamental form; civic-square showpiece |
| `tree_plum` | a PLUM TREE — dark-leaved canopy with purple plums | orchard variety; drops `fallen_plum` |
| `tree_peach` | a PEACH TREE — soft green canopy with fuzzy blush-orange peaches | orchard variety; drops `fallen_peach` |
| `tree_apricot` | an APRICOT TREE — small round canopy with golden apricots | warm-corner orchard tree |
| `tree_lemon` | a LEMON TREE — glossy dark leaves studded with yellow lemons | citrus row beside `tree_orange` |
| `tree_lime` | a LIME TREE — dense canopy with small green limes | citrus variety |
| `tree_fig` | a FIG TREE — broad-lobed leaves with purple figs | the rot/fly favorite (very fly-attractive when dropped) |
| `tree_mulberry` | a MULBERRY TREE — heart leaves and dark messy berries | drops staining fruit; heavy fly draw |
| `tree_quince` | a QUINCE TREE — gnarled small tree with knobbly yellow quinces | old-orchard character tree |
| `tree_walnut` | a WALNUT TREE — tall spreading canopy, green husked nuts | nut crop; bigger orchard anchor |
| `tree_apple_blossom` | an APPLE TREE in white-pink BLOSSOM, no fruit | spring/ornamental form of `tree_apple` |
| `tree_apple_espalier` | an APPLE TREE trained FLAT against a wall/wire in tiers | "fancy" managed orchard / kitchen-garden wall tree |
| `tree_orchard_sapling` | a young thin FRUIT SAPLING staked, few leaves | the poor end; newly planted row gap / nursery stock |
| `tree_fruit_heavy` | a fruit tree visibly OVERLADEN, branches bending, fruit-laden | the prize/"fancy" tree; max harvest read |

### Matching fallen fruit (extends `fallen_fruit`/`fallen_orange`)
The orchard's drop layer that drives the fly chain. All seen top-down on the ground.

| id | one-line | role / notes |
|----|----------|--------------|
| `fallen_pear` | two or three whole green-gold PEARS on the ground | rots → fly attractant |
| `fallen_cherry` | a scatter of small red CHERRIES on the ground | rots fast; fruit-fly draw |
| `fallen_plum` | two or three purple PLUMS on the ground | rots → flies |
| `fallen_peach` | a couple of bruised blush PEACHES on the ground | bruises quickly; strong attractant |
| `fallen_fig` | split purple FIGS oozing on the ground | the strongest fly draw (sweet, splits open) |
| `fallen_apple_rotting` | mushy brown half-rotted APPLES with fruit-fly haze | the explicit mid-rot stage between `fallen_fruit` and `rotten_fruit` |
| `windfall_pile` | a small heap of mixed FALLEN FRUIT raked together | orchard cleanup pile; feeds the compost / fly farm |

## 2. Shade & ornamental trees (roads, square, cottage yards)
Planted, tidy, often paired or rowed along the stone roads. Contrast to the wild oaks/pines.

| id | one-line | role / notes |
|----|----------|--------------|
| `tree_maple` | a MAPLE TREE — rounded canopy, green palmate leaves | road-line shade tree |
| `tree_maple_autumn` | a MAPLE in fiery red-orange AUTUMN leaf | seasonal variant; square showpiece |
| `tree_birch` | a BIRCH TREE — slim white-barked trunk, light airy canopy | elegant cottage-yard tree |
| `tree_willow` | a weeping WILLOW — long trailing draped branches | pondside SW-lake signature tree |
| `tree_chestnut` | a horse-CHESTNUT — big broad canopy with white flower spikes | grand civic-square shade tree |
| `tree_linden` | a LINDEN/lime shade tree — neat heart-leaf canopy | the classic European town-square avenue tree |
| `tree_poplar` | a tall narrow POPLAR column | screening / boundary row tree |
| `tree_magnolia` | a MAGNOLIA — bare-ish branches with big pink-white blooms | ornamental flowering specimen; "fancy" |
| `tree_hawthorn` | a small HAWTHORN — dense thorny canopy with white blossom / red haws | hedgerow + boundary tree; bird/bug friendly |
| `tree_rowan` | a ROWAN — feathery leaves and clusters of orange-red berries | slim ornamental; lore: planted by doorways |
| `tree_olive` | a gnarled OLIVE — silver-grey leaves, small dark fruit | warm-courtyard ornamental |
| `tree_topiary_standard` | a clipped lollipop STANDARD tree — a ball of foliage on a clean trunk | formal pair-piece for town-hall steps / gates |
| `tree_potted_bay` | a clipped BAY tree in a large pot/tub | doorway-flanking container tree (overlaps decor planters) |
| `tree_young` | a small staked YOUNG SHADE TREE, thin trunk | the poor/new-planting end; recently planted street tree |
| `tree_stump_fresh` | a freshly cut pale STUMP with sawdust, no weathering | "just felled" read (vs the weathered `stump`) |

## 3. Woodcutter / carpenter stock (cut-wood forms)
The carpenter's yard and the orchard's pruning both produce these. Extends `log_pile`/`stump`/
`chopping_block`/`sawhorse`.

| id | one-line | role / notes |
|----|----------|--------------|
| `log_single` | one large felled LOG lying on the ground, bark on, cut ends | raw stock; yard scatter (vs the stacked `log_pile`) |
| `log_stack_tall` | a tall neatly cross-stacked WOODPILE | bigger carpenter/firewood store than `log_pile` |
| `firewood_split` | a low heap of SPLIT firewood billets | cottage hearth supply; sells as fuel |
| `lumber_planks` | a stack of sawn flat PLANKS / boards | carpenter's finished stock; building material |
| `lumber_beams` | a bundle of squared timber BEAMS | heavier building stock |
| `tree_felled` | a whole TREE lying felled with branches still on | dramatic "just cut" yard piece |
| `sawdust_pile` | a small mound of pale SAWDUST | carpenter-yard ground detail |
| `wood_shavings` | a curl of pale wood SHAVINGS on the ground | workshop floor detail |
| `tree_marked` | a standing tree with a painted CUT-MARK / blaze | "to be felled" — woodcutter quest dressing |
| `nursery_pot_tree` | a sapling in a burlap-wrapped ROOT BALL / nursery pot | the carpenter/general-store *sells trees*; saleable stock |

---

### Ecology hook
The orchard is the **fly engine**: fruiting trees (§1) drop `fallen_*` fruit → it rots
(`fallen_apple_rotting` → `rotten_fruit`) → fruit-flies/houseflies spawn → predators arrive. Figs
and mulberries are the strongest attractants and good places to *demo* the chain near the Fly Farm.
See [`bugs/village.md`](../bugs/village.md) and [`landmarks/village.md`](../landmarks/village.md).
Blossom variants (`tree_cherry_blossom`, `tree_apple_blossom`, `tree_magnolia`) double as
pollinator draws for the benign bee/butterfly town bugs.
