# Brainstorm: Butterfly Meadow — Flora & Fungus

Plants and fungus for the **Butterfly Meadow** (`butterfly_meadow_11`), the flowering meadow north of
the village that shades into a cool forest edge. This is the zone's living foundation: **nectar** feeds
the pollinators, **milkweed** is the keystone the butterflies breed on, and the **forest-edge ferns &
mushrooms** mark the difficulty ramp into millipede/centipede country.

Theme: bright, drifting, sun-warm meadow → cool, mossy, shaded forest edge. Favor VARIETY and a
poor→fancy range (ragged weeds → showpiece blooms). Tags used below:
- **nectar** — pollinators feed here (raises the local nectar/pollination heuristic).
- **host** — caterpillars/larvae develop on it (breeding requirement, e.g. milkweed for monarchs).
- **edible / gatherable** — yields a material or food when harvested.
- **ecology** — its role in the pollination-vs-predation web.

Many ids already exist in `tools/art/catalog/flora.json` (marked **[exists]**); the rest are new
brainstorm proposals. EXTEND, don't duplicate.

---

## Groundcover (the meadow floor)
- `grass_lush` — thick bright meadow grass tuft, taller and greener than village grass. *Ecology: base layer; visual lushness of a healthy meadow.*
- `tall_grass` **[exists]** — wild fanning grass blades; the meadow's bulk filler. *Gatherable: thatch/straw.*
- `clover` **[exists]** — low trefoil patch with white-pink heads. **nectar** (bees love it). *Ecology: nitrogen-fixer, keeps the meadow fertile; a baseline bee feeder.*
- `clover_red` — taller red-clover with deep pink globe heads. **nectar** (bumblebees, long-tongued). *Fancier clover.*
- `moss_clump` **[exists]** — soft green cushion; drifts in toward the shaded north. *Ecology: marks cooler, damper forest-edge ground.*
- `clubmoss` **[exists]** — low creeping scale-leaved mat; forest-edge groundcover.
- `meadow_sedge` — low arching grass-like sedge tuft, blue-green. *Filler near the damp spring.*
- `wild_strawberry` — low trailing runner with white flowers and tiny red berries. **nectar** + **edible** (forage snack). *Ecology: ground-level nectar + a sweet gatherable.*
- `creeping_thyme` — flat spreading mat dotted with tiny purple flowers (see `thyme` **[exists]**). **nectar** (bees). *Ecology: fragrant low nectar carpet.*
- `selfheal` — low creeping weed with stubby violet flower spikes. **nectar**. *Common, humble, everywhere.*
- `plantain_weed` — ribbed-leaf rosette with a thin seed-spike; scruffy "failed-farm" weed. *Ecology: poor-soil indicator near the broken fence.*

## Wildflowers — nectar sources (the pollinator buffet)
The meadow's headline variety. Spread a wide color range so a swarm drifting across reads as a moving
field of blooms. All are **nectar** unless noted; richer/showier ones rate as higher-value feeders.
- `flower_aster` **[exists]** — purple daisy-rays, yellow center. **nectar** (a top butterfly feeder; monarchs fuel up on asters before migrating). *Ecology: keystone nectar flower.*
- `flower_yellow` **[exists]** — bright yellow blossom, dark center. **nectar**.
- `flower_red` **[exists]** — bright red blossom, yellow center. **nectar**.
- `flower_blue` **[exists]** — bright blue blossom, yellow center. **nectar**.
- `flower_bluebell` **[exists]** — arching stem of drooping blue bells. **nectar** (long-tongued bees). *Ecology: drifts toward the shadier forest edge.*
- `flower_foxglove` **[exists]** — tall pink-purple bell spire. **nectar** (bumblebees climb inside). *Note: showy, mildly toxic — a "pretty but poisonous" story beat.*
- `poppy` **[exists]** — red cup, dark center, nodding bud. **nectar** (pollen-rich; bees). *Ecology: pioneer of disturbed ground near the broken fence.*
- `dandelion` **[exists]** — yellow flower + white seed puff. **nectar** (an early, reliable feeder). *Ecology: the humble everyman flower; first to colonize bare patches.*
- `chamomile` **[exists]** — little white daisies, yellow centers. **nectar** + **gatherable** (tea). 
- `yarrow` **[exists]** — flat white flower cluster. **nectar** (flat landing-pads for small flies & beetles). *Ecology: feeds the less-glamorous pollinators too.*
- `lavender` **[exists]** — purple flower spikes, grey-green clump. **nectar** (bees, butterflies) + **gatherable**. *Ecology: a dense, high-value nectar magnet; great near the lepidopterist's blind.*
- `cornflower` — slender stem with a frilled brilliant-blue bachelor's-button head. **nectar**. *Classic meadow blue.*
- `oxeye_daisy` — tall white-petal daisy with a big gold center. **nectar**. *The archetypal meadow daisy; flower-clock material.*
- `black_eyed_susan` — gold petals around a dark domed center. **nectar** (butterflies bask + feed). *Warm-toned showpiece.*
- `coneflower_purple` — drooping mauve rays around a spiky copper cone (echinacea). **nectar** (a butterfly favorite) + **gatherable** (medicinal). *Higher-value feeder.*
- `cosmos` — airy fern-leaf stems topped with pink/white open daisies. **nectar**. *Tall, drifting, delicate.*
- `bee_balm` — shaggy scarlet tufted flower head (monarda). **nectar** (bees, butterflies, hummingbird-moths). *Ecology: top-tier nectar; magnet for the showier pollinators.*
- `goldenrod` — arching plume of tiny golden flowers. **nectar** (late-season fuel for migrating monarchs). *Ecology: critical end-of-cycle feeder.*
- `joe_pye_weed` — tall dusky-pink domed flower cluster on a strong stem. **nectar** (butterfly skyscraper). *Tall back-of-meadow anchor.*
- `phlox` — domed cluster of flat pink-lilac flowers. **nectar** (deep tubes — butterfly tongues, hawkmoths). 
- `cosmos_chocolate` *(rare)* — deep maroon cosmos with a faint cocoa scent. **nectar**. *Rarity: uncommon; a collector's bloom.*
- `gentian_fringed` *(rare, forest-edge)* — vivid blue fringed trumpet in the cool shade strip. **nectar**. *Rarity: rare; the meadow's most prized wildflower, only near the gloom edge.*

## Milkweed & keystone host plants (the breeding engine)
The reason butterflies exist here. Lose all of these → caterpillars can't develop → the butterfly
population ages out (`game_design.md §9.1`).
- `milkweed` **[exists]** — tall stem, paired broad leaves, pink-mauve flower umbel. **host** (the monarch's only breeding plant) + **nectar** + **gatherable** (pods/floss). *Ecology: THE keystone. Toxic latex makes monarch caterpillars poisonous → predators learn to avoid them. Kill all milkweed and the monarchs vanish.*
- `milkweed_common` — shorter, scruffier milkweed variant for filler density. **host** + **nectar**. *Lets the Great Milkweed Stand read as a real colony, not three identical sprites.*
- `milkweed_swamp` — slimmer milkweed with rose-pink flowers, near the damp spring. **host** + **nectar**. *Ecology: ties milkweed to the water feature.*
- `milkweed_pod` — a split seed pod spilling silky white floss (a gatherable spawn / late-stage state). **gatherable** (floss → stuffing/material). *Ecology: the harvest payoff; over-harvesting pods = fewer next-gen milkweed.*
- `dogbane` — milkweed cousin: branched stem, small white bells, also bleeds latex. **host** (tiger-moth caterpillars). *Ecology: secondary host that buffers the milkweed monoculture.*
- `dill` — feathery blue-green fronds with a yellow flower umbel (see `fennel` **[exists]**). **host** (swallowtail caterpillars feed here) + **nectar** (umbel feeds small flies/wasps). *Ecology: the SWALLOWTAIL's host plant — the second butterfly's breeding requirement.*
- `fennel` **[exists]** — tall feathery stalk, yellow umbel. **host** (swallowtail) + **nectar**. *Ecology: alternate swallowtail host alongside dill.*
- `nettle` — toothed leafy weed with stinging hairs, in the cooler edge. **host** (tortoiseshell/comma caterpillars) + **gatherable** (fiber/tea). *Ecology: an "ugly but essential" host; touching it could even sting the player — a small hazard.*
- `violet_wood` — low heart-leaf clump with small purple flowers, forest-edge shade. **host** (fritillary caterpillars) + **nectar**. *Ecology: the shade-loving host that bridges meadow and forest.*

## Bushes & shrubs (structure + cover)
- `bush` **[exists]** — compact green mound, no trunk. *Ecology: cover; bugs shelter here from wasps.*
- `bush_flowering` **[exists]** — green shrub dotted white-pink blossoms. **nectar**. *Ecology: shrub-tier nectar; butterflies bask on the open faces.*
- `wild_berry_bush` **[exists]** — low shrub with red berry clusters. **nectar** (flowers) + **edible/gatherable** (berries). *Ecology: feeds pollinators in bloom, foragers in fruit.*
- `bramble` **[exists]** — thorny tangle with blackberries. **nectar** + **edible** + cover. *Ecology: dense thorny refuge; thickens toward the forest edge.*
- `butterfly_bush` — arching shrub heavy with long lilac-purple flower spikes (buddleia). **nectar** (an enormous butterfly magnet — the name says it). *Ecology: highest-value nectar shrub; a natural anchor for a pollinator swarm. Place near the lepidopterist's blind.*
- `spicebush` — rounded green shrub with tiny yellow spring flowers. **host** (spicebush-swallowtail caterpillars) + **nectar**. *Ecology: a host that is ALSO a bush — structure + breeding in one.*
- `elderberry` — tall shrub with flat white flower plates and dark berry clusters. **nectar** + **edible/gatherable**. *Forest-edge transition shrub.*
- `viburnum` — leafy shrub with rounded white flower domes. **nectar**. *Pretty forest-edge filler.*
- `hazel_shrub` — multi-stem leafy shrub with nuts; marks where meadow becomes thicket. **gatherable** (nuts). *Ecology: structural step toward the tree band.*

## Forest-edge ferns, moss & damp greens (the cool north strip)
The shaded transition where the meadow gives way to trees and the millipedes/centipedes leak in.
Darker, damper, no bright nectar — the visual "temperature drop."
- `fern` **[exists]** — arching feathery fronds, no flowers. *Ecology: signals shade & damp; centipede cover.*
- `fern_ostrich` — tall vase-shaped fern clump, lush. *Bigger, fancier fern for the dense edge.*
- `fern_fiddlehead` — tight coiled new fern shoots. **edible/gatherable** (spring forage). *Ecology: a gatherable that ties the forest edge to food.*
- `bracken` — coarse low spreading fern carpet over the forest floor. *Ground cover under the tree band.*
- `hart_tongue` — strap-leaf glossy fern in deep shade. *Rarer, fancier shade fern.*
- `wood_sorrel` — clover-like shamrock leaves with tiny white flowers, shade. **edible** (tart leaves) + minor **nectar**. *Delicate forest-edge groundcover.*
- `wild_ginger` — low heart-leaf groundcover hiding small maroon flowers at soil level. *Ecology: deep-shade specialist marking true forest edge.*
- `liverwort` — flat green lobed mat on damp wood/stone. *Damp-rock detailer near the basking boulder's shaded side.*

## Mushrooms & fungus (forest-edge decay loop)
The fungus cluster strongly at the shaded north edge and on the dead wood (stumps, the fallen log).
Mostly **gatherable** with a poor→fancy/rare value ladder; a couple are decorative-only or hazardous.
- `mushroom_brown` **[exists]** — small domed brown cap. **gatherable** (common). *Ecology: leaf-litter decomposer; the everyman mushroom.*
- `mushroom_cluster` **[exists]** — dense little group of tan caps on a mossy base. **gatherable**. *Filler clump at the forest edge.*
- `mushroom_bracket` **[exists]** — woody banded shelves on dead wood. **gatherable** (tough). *Ecology: grows on the stumps & fallen-log bridge — visually ties fungus to the wood.*
- `mushroom_chanterelle` **[exists]** — golden funnel cap. **edible/gatherable** (prized). *Rarity: uncommon; a high-value forage find.*
- `mushroom_morel` **[exists]** — honeycomb conical cap. **edible/gatherable** (prized). *Rarity: rare; the forager's trophy.*
- `mushroom_puffball` **[exists]** — smooth cream ball. **edible** (young) / spore-puff (old). *Ecology: stomp it and it puffs spores — a tiny playful interaction.*
- `mushroom_inkcap` **[exists]** — shaggy bell dissolving to ink. **gatherable** (briefly). *Ecology: decays fast → a "catch it before it melts" beat.*
- `mushroom_fairy_ring` — a ring of small tan toadstools in the grass. **gatherable**. *Ecology: a natural circle — pairs beautifully with the flower-clock glade as a landmark detail.*
- `mushroom_fly_agaric` — iconic red cap with white spots (amanita). decorative / **hazardous** (toxic — don't eat). *Rarity: uncommon; the storybook "do not touch" mushroom.*
- `mushroom_oyster` — fan-shaped pale shelf clusters on the fallen log. **edible/gatherable**. *Ecology: log-rot decomposer on the bridge log.*
- `mushroom_turkeytail` — concentric banded thin brackets on stumps. decorative / **gatherable** (medicinal). *Detailer on dead wood.*
- `mushroom_jelly` — translucent amber wobbly fungus on damp wood (wood-ear). **gatherable** (odd). *Weird, fancy forest-edge find.*
- `slime_mold` — a bright yellow spreading blob on a rotting log (dog-vomit slime). decorative oddity. *Ecology: pure flavor — the meadow's strangest decomposer; a "what IS that" moment.*

## Ecology notes (how the flora drives the zone)
- **Pollination loop:** dense **nectar** flowers raise the local nectar value → butterflies/bees/moths
  linger and pollinate (swarm-proximity heuristic, `§9.2`) → more flowers/seeds next cycle. Visible
  payoff for keeping blooms up.
- **Breeding gate:** **milkweed** (monarch) + **dill/fennel/spicebush** (swallowtails) + **nettle/violet**
  (others) are the breeding requirement. Different butterflies need different hosts → host VARIETY
  controls which butterflies the meadow can support.
- **The poison defense:** milkweed and dogbane make their caterpillars toxic, so wasps prey on the
  *unprotected* species (bees, soft caterpillars) preferentially — a built-in reason monarchs persist
  even under wasp pressure.
- **Forest-edge gradient:** bright nectar flowers → shrubs → ferns/moss → mushrooms on dead wood. The
  flora itself tells the player "danger and difficulty rise as you go north."
- **Gatherables ladder:** common brown mushroom / floss / berries (cheap) → chanterelle / fiddlehead /
  elderberry (mid) → morel / chocolate-cosmos / fringed-gentian (rare). A forage value curve that
  rewards exploring the whole zone.
