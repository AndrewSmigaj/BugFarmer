# Brainstorm — Village Flora

Cultivated and decorative plants for the starting **village** (`village_21`): a lived-in town
of shops around a civic square, NPC cottages with window boxes and veg patches, an orchard, and
the SW lake. The mood is *tended and tidy* — garden flowers, hedges, planted edging, kitchen
crops — the opposite of the wild meadow north of town. Fungus is deliberately minimal here.

**Scope note:** orchard/shade trees live in [`trees/village.md`](../trees/village.md); pots, planter
boxes, troughs and the planters-as-furniture live in [`decorations/village.md`](../decorations/village.md).
This doc is the *plants themselves*.

**Already in the catalog (reuse, don't re-add):** `flower_red`, `flower_blue`, `flower_yellow`,
`flower_aster`, `flower_bluebell`, `flower_foxglove`, `poppy`, `sunflower`, `dandelion`, `clover`,
`chamomile`, `lavender`, `yarrow`, `mint`, `sage`, `thyme`, `fennel`, `milkweed`, `fern`, `bush`,
`bush_flowering`, `bramble`, `wild_berry_bush`, `hedge` (decor/structures), `ivy`, `morning_glory`,
`grapevine`, `tall_grass`, `plant_tomato`, `plant_corn`, `plant_wheat`, `fallen_fruit`,
`fallen_orange`, `rotten_fruit`, `compost_pile`, `water_lily`, `duckweed`, `pondweed`, `cattail`.
Everything below is **new** and fills the cultivated-town gap.

---

## 1. Garden flowers (cottage beds & civic flower beds)
A poor→fancy range: weedy self-seeders read "humble", show blooms read "tended", a prize bloom reads "mayor".

| id | one-line | role / notes |
|----|----------|--------------|
| `flower_rose_red` | a single red garden ROSE on a thorny stem with glossy leaves | the iconic tended bloom; civic beds, cottage doorways |
| `flower_rose_pink` | a soft pink rose, fuller and blowsier than the red | variety; pairs with red in beds |
| `flower_rose_white` | a pure white rose, formal | town-hall / wedding feel |
| `rose_bush` | a rounded shrub rose dotted with many small pink-red blooms | bushy mass-planting (vs single stem) |
| `flower_tulip_red` | an upright red TULIP, cupped petals on a smooth stem | classic spring bed; plants in tidy rows |
| `flower_tulip_yellow` | a bright yellow tulip | row/bed variety |
| `flower_tulip_pink` | a pink-and-white striped tulip | fancier bed variety |
| `flower_daffodil` | a yellow DAFFODIL with a trumpet center and a flat star of petals | early-spring civic edging |
| `flower_marigold` | a dense ruffled orange-gold MARIGOLD | cheerful; also a natural pest-deterrent (lore: repels flies) |
| `flower_pansy` | a low cluster of purple-and-yellow-faced PANSIES | window-box & border filler |
| `flower_petunia` | a trailing PETUNIA with trumpet pink-purple blooms | spills over planter rims; window boxes |
| `flower_geranium` | a potted-looking GERANIUM, rounded leaves topped with a red flower ball | the classic window-box red |
| `flower_hydrangea` | a big rounded blue-pink HYDRANGEA mophead on a leafy shrub | fancy cottage corner; shade-tolerant |
| `flower_peony` | a huge blowsy pink PEONY bloom, many soft petals | "fancy" tier; show garden |
| `flower_iris` | a tall purple-blue IRIS with upright and falling petals | pondside & formal beds |
| `flower_daisy_oxeye` | a clump of white OX-EYE DAISIES with yellow centers | informal, naturalized edges |
| `flower_cosmos` | airy COSMOS — tall wiry stems, pink-and-white open flowers | loose meadow-edge planting |
| `flower_snapdragon` | a SNAPDRAGON spike of stacked dragon-mouth pink-yellow flowers | vertical accent in beds |
| `flower_hollyhock` | a very tall HOLLYHOCK spire studded with pink saucer blooms | against cottage walls; cottage-garden signature |
| `flower_zinnia` | a bright multi-colored ZINNIA, flat round bloom | easy mixed-bed color |
| `flower_carnation` | a frilled pink-red CARNATION on a slim grey-green stem | buttonhole / formal bed |
| `forget_me_not` | a low spray of tiny sky-blue FORGET-ME-NOTS | edging filler; delicate |
| `primrose` | a low rosette of leaves with pale-yellow PRIMROSE flowers | early, ground-hugging border |
| `bleeding_heart` | an arching stem hung with pink heart-shaped BLEEDING-HEART flowers | shady cottage-corner curiosity |

## 2. Flowering / structural shrubs & climbers (town greenery)
| id | one-line | role / notes |
|----|----------|--------------|
| `hedge_flowering` | a trimmed hedge block flushed with small white blossoms | flowering variant of `hedge`; tiles like the plain one |
| `hedge_low` | a low clipped boxwood EDGING hedge, knee-high | bed borders & parterre edging (vs full-height `hedge`) |
| `topiary_ball` | a clipped shrub trained into a neat green SPHERE on a short trunk | formal; flanks doorways/gates |
| `topiary_cone` | a shrub clipped into a tall CONE/spiral | formal pair-piece for town hall steps |
| `boxwood_shrub` | a small dense dark-green boxwood mound | generic tidy shrub for foundations |
| `lilac_bush` | a leafy shrub topped with purple LILAC flower cones | fragrant spring shrub; cottage corners |
| `rhododendron` | a broad-leaved shrub massed with pink-purple blooms | big spring show shrub |
| `rose_climber` | a CLIMBING ROSE — a leggy cane of red roses, meant to scramble a wall/arch | dresses the `garden_arch` and trellises |
| `wisteria_vine` | a woody vine dripping with purple WISTERIA flower chains | drapes pergolas/porches; "fancy" |
| `clematis_vine` | a climbing CLEMATIS with big flat purple star flowers | trellis/fence climber |
| `honeysuckle` | a twining vine with tubular cream-yellow honeysuckle flowers | fragrant fence/arch climber; bee-friendly |
| `boston_ivy_wall` | a sheet of climbing ivy turning red-green over a wall face | wall-dressing variant (warmer than plain `ivy`) |

## 3. Kitchen-garden crops & herbs (NPC veg patches, general-store seeds)
The orchard handles fruit *trees*; these are the bedded/row crops a cottager grows. Extends the
existing `plant_tomato`/`plant_corn`/`plant_wheat` trio into a proper kitchen plot.

| id | one-line | role / notes |
|----|----------|--------------|
| `plant_cabbage` | a low round CABBAGE — tight blue-green leaf ball on the soil | classic veg-patch row crop |
| `plant_lettuce` | a loose LETTUCE rosette of crinkled bright-green leaves | fast salad crop |
| `plant_carrot` | a feathery CARROT top with an orange root shoulder showing at the soil | root-row crop |
| `plant_pumpkin` | a sprawling vine with one fat orange PUMPKIN and big leaves | autumn showpiece; harvest decor |
| `plant_bean_pole` | a teepee of bean POLES laced with climbing vines and green pods | vertical kitchen-garden structure |
| `plant_pepper` | a bushy plant hung with glossy red and green PEPPERS | mixed-bed crop |
| `plant_strawberry` | a low STRAWBERRY plant with white flowers and red berries | border/bed crop; sweet |
| `plant_cucumber` | a trailing CUCUMBER vine with green fruits and yellow flowers | trellised veg |
| `plant_onion` | a row of ONION tops — green spears over swelling bulbs | staple row crop |
| `plant_potato_hill` | a leafy POTATO plant on a mounded soil hill | hilled-row crop |
| `plant_pea` | a low PEA plant with tendrils, white flowers and green pods | early kitchen crop |
| `herb_rosemary` | an upright woody ROSEMARY shrub, needle leaves, faint blue flowers | kitchen herb (pairs `mint`/`sage`/`thyme`) |
| `herb_basil` | a leafy bright-green BASIL clump | pot/bed kitchen herb |
| `herb_parsley` | a low tuft of curly PARSLEY | bed/pot herb |
| `herb_chives` | a clump of grassy CHIVES topped with purple pompom flowers | bed-edge herb, pretty + useful |
| `garlic_braid` | (harvested) a hanging BRAID of dried garlic bulbs | kitchen/larder dressing, not a growing plant |
| `seed_tray` | a wooden TRAY of soil cells with tiny green SEEDLINGS sprouting | general-store / greenhouse prop; "starts" |

## 4. Lawn, path-edging & ground cover (the tended-ground layer)
The town floor should read *kept*: mown turf, neat edges, mossy cracks only where old.

| id | one-line | role / notes |
|----|----------|--------------|
| `turf_patch` | a small patch of short mown lawn GRASS, even and tidy | lawn-fill scatter (contrast to wild `tall_grass`) |
| `grass_tuft_tidy` | a small neat tuft of garden grass | sparse lawn detailing |
| `clover_patch_white` | a low spread of white CLOVER flowers in lawn | benign lawn weed; bee-friendly |
| `creeping_thyme_mat` | a flat mat of CREEPING THYME with tiny pink flowers | between-paver ground cover; fragrant |
| `path_edging_flowers` | a tidy ribbon of low mixed border FLOWERS, meant to line a path | path-edge strip planting |
| `garden_border_stone` | a row of small rounded EDGING STONES bounding a bed | hard edging (overlaps decor; listed for bed context) |
| `garden_border_log` | a low half-LOG bed edging | rustic cottage edging |
| `lawn_weeds` | a scruffy patch of plantain/dandelion LEAVES in turf | "neglected lawn" tell for a poorer cottage |
| `mushroom_lawn` | a tiny ring of small pale LAWN MUSHROOMS in grass | the one sanctioned fungus — a damp-corner detail only |

## 5. Pond & waterside planting (SW lake margin)
Extends existing `cattail`/`water_lily`/`duckweed`/`pondweed`/`reeds`. Tended-ish, since it's a town pond.

| id | one-line | role / notes |
|----|----------|--------------|
| `reed_clump` | a dense clump of tall green pond REEDS | softens the dock edge; frog/dragonfly cover |
| `bulrush` | tall BULRUSHES with brown sausage seed-heads | pond-margin vertical (distinct from `cattail` styling) |
| `iris_water` | a yellow WATER IRIS rising from the shallows | showy pond-edge bloom |
| `marsh_marigold` | low glossy leaves with bright yellow MARSH-MARIGOLD cups at the water's edge | early waterside color |
| `lotus_flower` | a large pink LOTUS bloom standing above round floating leaves | "fancy" ornamental pond centerpiece |
| `pickerel_weed` | a clump of spear leaves with a blue flower spike in the shallows | pond-margin filler |

## 6. Festive / seasonal dressing (the town is the showcase)
Cheap-to-author variety that makes the square feel *occasioned*.

| id | one-line | role / notes |
|----|----------|--------------|
| `flower_wreath` | a circular WREATH woven of greenery and small flowers | hang on doors/gates; festival dressing |
| `garland_floral` | a draping GARLAND of leaves and flowers | strung between posts/stalls on market day |
| `pumpkin_harvest` | a clustered group of harvest PUMPKINS and a gourd | autumn-festival ground decor |
| `corn_stook` | a tied STOOK/sheaf of dried corn stalks | harvest dressing against a post |
| `flower_pile_market` | a heaped market display of CUT FLOWERS in bunches | the flower-stall product; ground/stall decor |

---

### Bonus hook (for later balance docs)
Decorative flowers/hedges feed the **player-farm decoration bonus** system, so the poor→fancy
range matters: a single `flower_red` < a `flower_rose_red` bed < a `flower_peony`/`topiary` set.
Bee/butterfly-friendly plants (`flower_marigold`, `lavender`, `honeysuckle`, `clover_patch_white`,
`milkweed`) are natural candidates to tie a *pollinator-attract* bonus to, reinforcing the village's
benign-bug ecology — see [`bugs/village.md`](../bugs/village.md).
