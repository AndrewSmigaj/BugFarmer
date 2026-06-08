# Brainstorm: Butterfly Meadow — Bugs & Ecology

The living cast of the **Butterfly Meadow** (`butterfly_meadow_11`) — the zone where the
pollination-vs-predation balance is on full display (`game_design.md §9.1`, zone design
`butterfly_meadow_11.md`). This is the player's first real ecosystem to **read** and (optionally) **tip**.

Difficulty is **Medium** — a gentle step up from the village. Bugs are placed as `place_bug` (sub-grid,
scaled) and **drift**; the meadow is authoritative-swarm ecology (`§4`, `§9.2`).

Difficulty tags: **harmless / neutral / nuisance / dangerous / elite**. Ecology tags note diet, what
preys on it, and its breeding requirement. Existing ids (`tools/art/catalog/bugs.json`) marked
**[exists]**; the rest are new proposals. Note the bug pipeline renders centipede/millipede from
**segmented head/body/tail parts** — those parts already exist. EXTEND, don't duplicate.

---

## Butterflies (the headline pollinators)
The zone's icon. Breed ONLY on their host plants — lose the hosts and they age out (`§9.1`). They
pollinate flowers via swarm-proximity, and they're prime wasp/spider prey. The zone design calls for
**2–3 butterflies** (a monarch-like on milkweed, a swallowtail, a small common); listed generously here
so we can pick the best.
- `butterfly_monarch` — bold orange wings with black veins and white-dotted margins. **harmless.** *Ecology: THE keystone pollinator. Host = `milkweed` ONLY → its caterpillars eat milkweed and become toxic, so most predators avoid it. The iconic resident of the Great Milkweed Stand. Rarity: common but cherished; over-collecting them drops pollination.*
- `butterfly_swallowtail` **[exists]** — broad yellow-and-black wings, blue spots, tail extensions. **harmless.** *Ecology: the second butterfly. Host = `dill`/`fennel`/`spicebush`. A strong flier; favors tall flowers (foxglove, bee balm). Rarity: common.*
- `butterfly_cabbage_white` — small plain white wings, a couple of black dots. **harmless.** *Ecology: the "small common" butterfly — the everyman. Host = various weeds. Cheap, abundant, the first one a player catches. Rarity: very common.*
- `butterfly_common_blue` — tiny shimmering blue wings (males), brown (females). **harmless.** *Ecology: clover/legume host; flutters low over the groundcover. A small, pretty catch. Rarity: common.*
- `butterfly_painted_lady` — orange-brown marbled wings with white-spotted black tips. **harmless.** *Ecology: a wandering generalist; thistle/mallow host. Drifts through in loose numbers. Rarity: common.*
- `butterfly_fritillary` — bright orange wings with a silver-spotted underside. **harmless.** *Ecology: host = `violet_wood` (forest-edge) → bridges meadow and shade. Rarity: uncommon.*
- `butterfly_red_admiral` — black wings with bold red bands and white tips. **harmless.** *Ecology: nettle host; territorial — basks on the boulder and the broken fence. A handsome catch. Rarity: uncommon.*
- `butterfly_tortoiseshell` — warm orange-and-black scalloped wings with blue-spotted edges. **harmless.** *Ecology: nettle host; overwinters in deadwood/hollows at the edge. Rarity: uncommon.*
- `butterfly_emperor` **[exists]** — large iridescent purple-blue wings with white bands; **elite, regal.** *Ecology: the rare showpiece (purple emperor) — patrols the forest-edge oak tops, rarely descends; drawn down by rotting fruit, not flowers. Rarity: rare. A trophy catch + a reason to keep `fallen_fruit` around.*

## Bees & other pollinators (the secondary nectar crew)
Bees pollinate too, and they're the wasps' favorite prey — the engine of wasp reproduction (`§9.2`).
Moths are the night/dusk shift.
- `bee_bumble` — fat fuzzy black-and-yellow rounded bee. **harmless** (bumbles low). *Ecology: a top pollinator, esp. of deep flowers (foxglove, bee balm — it climbs inside). Wasp prey. Reproduces via a small ground/tussock nest. Rarity: common.*
- `bee_honey` — slimmer amber-and-brown honeybee. **harmless.** *Ecology: hive pollinator (`§9.2`: bees reproduce when a hive exists + food is sufficient) — ties into a placed/wild hive. Wasp prey. The classic "bee farming" species. Rarity: common.*
- `bee_carpenter` **[exists]** — large shiny black-and-gold robust bee. **neutral** (big, can bumble defensively). *Ecology: a chunky solitary pollinator that nests in deadwood at the forest edge — ties bees to the logs/snags. Rarity: uncommon.*
- `bee_mason` — small dark metallic-blue solitary bee. **harmless.** *Ecology: an efficient early-spring pollinator; nests in hollow stems/holes. Rarity: uncommon.*
- `hoverfly` — a slim fly mimicking wasp yellow-black stripes, hovers in place. **harmless** (a mimic — looks scary, totally safe). *Ecology: a surprise pollinator AND its larvae eat aphids → a tiny natural pest-control. The "it's not what it looks like" beat. Rarity: common.*
- `moth_brown` **[exists]** — small dusty grey-brown moth. **harmless.** *Ecology: dusk pollinator; the drab night-shift counterpart to the butterflies. Moth-to-light interaction near the lepidopterist's lantern. Rarity: common.*
- `moth_hummingbird` — a plump moth that hovers at flowers like a hummingbird, with a long tongue. **harmless.** *Ecology: a day-flying moth that pollinates deep tube flowers (phlox, bee balm); a delightful "is that a tiny bird?" catch. Rarity: uncommon.*
- `moth_luna` **[exists]** — pale green broad wings with long trailing tails. **harmless.** *Ecology: a stunning dusk moth of the forest edge; doesn't even feed as an adult — pure beauty. Rarity: rare; a trophy.*
- `moth_atlas` **[exists]** — enormous patterned red-brown wings; **elite.** *Ecology: the giant — an exceptional forest-edge night find; the moth equivalent of the emperor butterfly. Rarity: rare/elite trophy.*

## The 2 wasps (the predation pressure)
The zone's signature threat and the core of the predation dynamic. **Wasps prey on caterpillars,
butterflies, and bees; wasp reproduction requires successful predation** (`§9.2`). Two tiers, as the
zone design specifies — an easier paper wasp and a harder yellowjacket (wasps get nastier further out).
- `wasp_paper` **[exists]** — slim yellow-and-black body, very narrow waist, long folded wings. **dangerous (easier).** *Ecology: the EASY wasp. Hunts caterpillars and soft larvae more than adults; builds a small open paper nest (a hanging-comb landmark). Defensive near its nest but not relentless. Kill it and caterpillars boom; it's the player's first "predator I can handle." Rarity: common.*
- `wasp_yellowjacket` **[exists]** — stocky bright yellow-and-black striped, aggressive stance. **dangerous (harder).** *Ecology: the HARD wasp. Faster, hits harder, stings repeatedly, aggressively chases bees AND butterflies; nests in the ground at the forest edge. The real predation cap on the pollinator population. A clear difficulty step toward the northern zones. Rarity: uncommon.*
- `wasp_ichneumon` *(optional 3rd, exotic)* — a very long slender wasp with a thread-like tail (ovipositor). **neutral to player / dangerous to caterpillars.** *Ecology: a parasitoid — it doesn't sting the player much, it lays eggs IN caterpillars. A subtler, creepier predation vector that targets the breeding stock directly. Rarity: uncommon; great flavor + a deeper ecology lever.*

## Caterpillars & larvae (the brood stage — the link between plants and butterflies)
The middle of the food web: born on host plants, eaten by wasps/birds, become butterflies. Visible
caterpillars make the breeding loop legible. These are slow, ground/plant-bound, **harmless** to the
player but the wasps' main food.
- `caterpillar_monarch` — plump caterpillar boldly banded white-yellow-black. **harmless** (toxic to predators). *Ecology: on `milkweed` only; eats milkweed → becomes a toxic monarch. The visible proof the milkweed is doing its job. Wasps mostly avoid it (toxic) → why monarchs persist. Rarity: common on milkweed.*
- `caterpillar_swallowtail` — green caterpillar with black bands and false eyespots. **harmless.** *Ecology: on dill/fennel; rears up & flashes a forked orange "osmeterium" gland when poked (a fun interaction). Prime wasp prey. Rarity: common on host.*
- `caterpillar_woolly` — fuzzy black-and-rust banded caterpillar trundling along. **harmless.** *Ecology: a generalist (becomes a tiger moth); famously folklore-y. Wasp prey. Rarity: common.*
- `caterpillar_inchworm` — a thin green looper that humps along. **harmless.** *Ecology: tree-canopy feeder; dangles on silk. The smallest, cheapest brood bug. Rarity: common.*
- `caterpillar_tent` — clustered hairy caterpillars in a silk tent in a tree fork. **nuisance (to trees).** *Ecology: defoliates branches if unchecked → a small "pest outbreak" the player or wasps can curb. Ties wasps' predation to a tangible benefit. Rarity: uncommon (event-y).*
- `chrysalis_monarch` — a jade-green chrysalis with gold dots, hanging from a milkweed leaf. **harmless** (static). *Ecology: the pupa stage — a beautiful, fragile static object; protect it and a monarch emerges. A gatherable-but-precious beat. Rarity: common near milkweed.*
- `cocoon_silk` — a papery spun cocoon tucked on a stem or under a leaf. **harmless** (static). *Ecology: moth pupa; the drab counterpart to the chrysalis. Rarity: common.*
- `bee_grub` — a pale C-shaped grub in a nest cell. **harmless** (static). *Ecology: bee brood; wasps raid these — shows wasps attacking the bee population at the source. Rarity: uncommon (in/near hives).*

## Neutral meadow bugs (the ambient cast — texture + minor roles)
Not pollinators, not threats — they make the meadow feel alive and fill out the food web (extra wasp
prey, extra forage, minor pests). Mostly **harmless/neutral**.
- `grasshopper_meadow` — green-brown grasshopper that springs away when approached. **harmless.** *Ecology: abundant herbivore; springs in arcs — lively motion; wasp/spider prey. Rarity: very common.*
- `cricket_field` — a dark chunky cricket; chirps in the grass. **harmless.** *Ecology: ambient chirp/sound flavor; ground forager. Rarity: common.*
- `ladybug_orange` **[exists]** — round orange domed beetle with black spots. **harmless** (beneficial). *Ecology: eats aphids → natural pest control on the flowers. A "good bug." Rarity: common.*
- `ladybug_giant` **[exists]** — large red domed beetle; **elite.** *Ecology: the rare oversized ladybug — a trophy version of a friendly bug. Rarity: rare.*
- `aphid_colony` — a cluster of tiny green sap-suckers on a stem. **nuisance (to plants).** *Ecology: drains flowers/milkweed; food for ladybugs & hoverfly larvae → drives the pest-control sub-loop. Rarity: common (clumped).*
- `beetle_dung` — a stout dark beetle rolling a tiny ball. **harmless.** *Ecology: the meadow's recycler — processes droppings near the (story) failed farm. Quirky charm. Rarity: uncommon.*
- `beetle_jewel` — a small brilliant metallic-green/copper beetle glinting in the sun. **harmless.** *Ecology: pure beauty + a shiny collectible; basks on warm leaves and the boulder. Rarity: uncommon; a pretty catch.*
- `beetle_soldier` — a slim red-and-black beetle that hangs out on flower umbels (yarrow, fennel). **harmless.** *Ecology: a flower-top predator of aphids/small bugs; minor pollinator. Rarity: common.*
- `dragonfly_meadow` — a slim darter dragonfly patrolling over the grass and spring. **neutral** (predator of small bugs). *Ecology: aerial hunter of flies/mosquitoes near the water; a flash of fast motion. (See `dragonfly_emperor`/`dragonfly_hawker` **[exists]** for fancier/elite variants near the spring.) Rarity: common.*
- `damselfly` — a delicate needle-thin blue dragonfly relative near the puddle. **harmless.** *Ecology: tiny aerial hunter; ties the water feature into the bug cast. Rarity: common.*
- `fly_house` **[exists]** — small grey-black housefly. **harmless.** *Ecology: ambient; gathers on `fallen_fruit`/`rotten_fruit` → properly a "fly farming" carryover from the village; wasp prey. Rarity: common.*
- `firefly_blue` **[exists]** — slim dark beetle with a glowing tip. **harmless.** *Ecology: dusk magic near the forest edge; a glowing evening catch that pairs with the lepidopterist's lantern. Rarity: uncommon.*
- `snail_garden` — a small spiral-shelled snail trailing along a damp leaf. **harmless.** *Ecology: slow forager; thrives near the spring & shaded edge; an easy catch. (Cf. `snail_pond` **[exists]**.) Rarity: common.*
- `spider_orb` **[exists]** — round yellow-and-black garden spider at a web hub. **neutral (predator).** *Ecology: a SECONDARY predator alongside wasps — catches butterflies/bees in its web strung between fence rails or stems. Adds a second predation vector (and `§9.1` lists spiders as butterfly predators). Rarity: common.*
- `spider_crab` — a small flat spider that sits camouflaged ON a flower, ambushing visitors. **neutral (ambush predator).** *Ecology: the hidden danger in the buffet — picks off bees/butterflies mid-sip. A "the flowers themselves can bite" beat. Rarity: uncommon.*

## Edge threats (the forest-edge danger — the difficulty ramp)
Seep in from the cooler northern forest edge; the danger ramps as you go north (`§9.1` framing). These
are the zone's "first place that bites back" beyond wasps. Rendered from **segmented head/body/tail
parts** (all **[exists]**), so they read as proper chained crawlers.
- `millipede` (`millipede_head_a/b` + `millipede_body_a/b` + `millipede_tail_a/b` **[exists]**) — a long rounded many-legged crawler. **dangerous (slow, armored, mostly defensive).** *Ecology: a DETRITIVORE — eats rotting leaves/logs at the forest edge (ties to the deadwood + fungus). Slow and armored; curls into a defensive coil rather than chasing; secretes a foul/mildly-toxic defense if grabbed. Low aggression, high tankiness → the "armored but passive" threat that teaches caution. Rarity: common at the edge.*
- `centipede` (`centipede_head_a/b` + `centipede_body_a/b` + `centipede_tail_a/b` **[exists]**) — a flattened fast many-legged crawler with fangs. **dangerous (fast, venomous).** *Ecology: an active PREDATOR — fast, venomous bite, hunts other bugs (and harasses the player); the real edge danger. Hides under logs/stumps/rocks by day → flipping deadwood can reveal one. The clear "things get scarier north" signal. Rarity: uncommon at the edge, more common further north.*
- `centipede_tiger` *(rare, harder variant)* — a larger boldly banded centipede. **elite.** *Ecology: the forest-edge's nastiest resident — a preview of the millipede/centipede zones to the north. Faster, more venomous, more aggressive. Rarity: rare; a mini-boss-flavored encounter near the hollow tree / fallen-log bridge.*
- `woodlouse` — a small grey armored roly-poly crawler under the deadwood. **harmless.** *Ecology: a tiny detritivore (millipede's harmless cousin); rolls into a ball when touched. Comic-relief edge bug + a sign you're flipping the right logs. Rarity: common under wood.*
- `harvestman` — a tiny round body on long thread-thin legs (daddy-long-legs). **harmless.** *Ecology: a gentle forest-edge scavenger; NOT a true spider, doesn't bite — another "looks scarier than it is" beat. Rarity: common at the edge.*

## Ecology relationships (the web at a glance)
- **Pollination loop (the payoff):** flowers (nectar) → butterflies/bees/moths feed & pollinate
  (swarm-proximity, `§9.2`) → more flowers/seeds. Keeping blooms up visibly grows the pollinator clouds.
- **Breeding gate (the constraint):** butterflies breed ONLY on host plants — `milkweed` (monarch),
  `dill`/`fennel`/`spicebush` (swallowtails), `nettle`/`violet` (others). Kill the hosts → no
  caterpillars → that butterfly ages out (`§9.1`). Caterpillars/chrysalises make this loop visible.
- **Predation pressure (the brake):** wasps eat caterpillars, butterflies, AND bees; **wasp
  reproduction requires successful predation** (`§9.2`). Spiders (orb + crab) are a second predator,
  and the ichneumon parasitizes caterpillars directly.
- **The toxic shield:** milkweed/dogbane make monarch caterpillars toxic → wasps prefer the
  *un*protected prey (bees, swallowtail/woolly caterpillars). This is *why* monarchs survive the wasps.
- **Out-of-balance levers (player can tip it):**
  - Kill all **milkweed** → monarchs age out.
  - Kill all **wasps** → caterpillars/butterflies boom and may strip the flowers (then pollination
    crashes anyway) — a lesson in why predators matter.
  - Over-collect **butterflies/bees** → pollination drops → fewer flowers/seeds next cycle.
  - Let **aphids** run unchecked → flowers suffer; ladybugs/hoverflies are the natural answer.
- **The difficulty gradient (north):** harmless meadow bugs → wasps (medium) → edge millipede/centipede
  (slow-tank vs fast-venom) → `centipede_tiger` (a taste of the forest zones). The bug cast itself
  teaches the player to read danger by location.
