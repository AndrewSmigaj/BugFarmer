# Bug-Farming Toolkit — Brainstorm

The objects/tools that turn the core fantasy ("ALL bugs farmable if penned strongly enough")
into placeable content. This is a CONTENT brainstorm — design only, no code/data/art here.

Read alongside:
- `docs/product/game_design.md` §7 (capture), §8 (containment & escape), §11 (automation).
- `docs/brainstorms/materials/ores_metals.md` for the **pen-material ladder** (Wood → Iron →
  Steel → Advanced/exotic). Pen tiers below reference that ladder so containment strength stays
  one consistent progression across the game.

## Design rules this file follows
- **Containment is emergent, never bought.** You don't buy a "fly pen"; you buy/craft fences,
  walls, doors, nets and *build* an enclosure. Pen entries here are the **building blocks** and
  **purpose-built containment furniture** (terrariums/tanks/cages), not pre-solved pens.
- **Tools unlock behaviors & efficiency, they don't replace older ones** (§7.3). A starter net
  still works on easy bugs forever; better gear adds reach, speed, and access to harder bugs.
- **No fast/free automation.** The autonet (already in catalog) is the only auto-catcher, and it's
  deliberately slow + capacity-capped. Anything "auto" below inherits those constraints.
- **Variety across a poor→fancy value ladder** — quality is just sell_price/material tier.
- **Bug taxonomy** (§4): SWARM bugs (flies, mosquitoes, butterflies, bees, gnats, moths) interact at
  the swarm level; INDIVIDUAL bugs (spiders, wasps, frogs, beetles, scorpions, mantises, GIANT/boss
  arthropods) are tracked one at a time. Tools note which they serve.

Existing catalog ids you'll see referenced (extend, don't duplicate): `autonet`, `net_post`,
`fly_netting`, `bait_basket`, `collection_tray`, `bug_terrarium`, `aquarium`, `compost_bin`,
`beehive_basic/medium/large/deluxe`, `honey_extractor`, `fence_wood/iron/electric`, `gate_wood/iron`,
`wall_wood/stone/brick`, `ant_eggs`.

---

## 1. CATCHING

### 1.1 Hand nets (tiered by material — held tools, item icons)
The core capture verb (§7.1). Bigger/better = larger AoE, faster swing, catches tougher bugs.

| id | one-line | tier | bonus / role |
|----|----------|------|--------------|
| `net_twig` | crude bent-twig net with a cloth scrap hoop | starter | tiny AoE, easy swarm bugs only; what you begin with |
| `net_basic` | simple wooden-handle butterfly net, pale mesh | common | reliable single-swarm catch |
| `net_copper` | copper-ringed net, sturdier hoop, wider mouth | uncommon | +AoE, faster swing |
| `net_iron` | iron-hoop net, fine durable mesh | mid | catches faster/agitated swarm bugs |
| `net_steel` | steel-frame net, taut high-strength mesh | high | can net small individual bugs (spiders, beetles) |
| `net_silk` | featherlight silk-mesh net on a polished handle | high | very fast swing, low agitation (won't spook swarms) |
| `net_giant` | huge two-handed reinforced net | high | the only hand net that catches GIANT individual bugs (slow swing) |
| `net_gilded` | ornate gold-trim collector's net | fancy | prestige/show piece; top AoE + speed |

### 1.2 Thrown / area nets (consumables & gear, §7.1 variants)
| id | one-line | role |
|----|----------|------|
| `throw_net` | weighted bola-style net you fling over a target | ranged single-catch on skittish/fast individual bugs |
| `net_grenade` | tossed pod that bursts into a spreading mesh | area capture of a clustered swarm; consumable |
| `bola_capture` | tri-weighted cord that tangles legs | downs large/giant individual bugs so a giant net can finish |

### 1.3 Placeable ground nets & traps (world objects, passive)
Set-and-check catching for farming layouts (§7.1 "placeable ground nets").
| id | one-line | tier | notes |
|----|----------|------|-------|
| `fly_netting` *(exists)* | hung mesh panel that snags passing flies | poor | extend with bait/lure slots below |
| `pitfall_trap` | a covered sunken pot flush with the ground | poor | catches ground-walking individual bugs (beetles, crickets) |
| `sticky_trap` | a flat sticky board on a short stake | poor | passive swarm trickle (gnats, flies); fills then clogs |
| `funnel_trap` | wood-and-mesh cone funnel into a jar | common | one-way intake; check to collect |
| `box_trap` | a propped wooden box on a trigger stick | common | single skittish individual bug |
| `cage_trap` | iron live-cage trap with a tripping plate | mid | larger individual bugs, unharmed |
| `glass_dome_trap` | a clear dome that drops over a bug | mid | clean capture for prized/display specimens (no damage) |
| `auto_trap_resetting` | spring trap a Bug Handler NPC can re-arm | mid | pairs with the Bug Handler worker (§11.2); still slow |

### 1.4 Jars & containers (the "where the catch goes" tier)
Catching produces a held creature that needs a vessel; bigger jars = more/bigger captures.
| id | one-line | tier |
|----|----------|------|
| `bug_jar` | small glass jar with a punched-lid | starter |
| `mason_jar` | larger lidded jar with a wire bail | common |
| `specimen_vial` | slim corked vial for tiny/delicate bugs | common |
| `critter_box` | ventilated wooden carry-box | mid |
| `kritter_keeper` | hinged clear plastic-style carry case | mid |
| `glass_canister` | big brass-lidded glass canister | high |
| `giant_capture_drum` | a wheeled reinforced drum for giant bugs | high |

### 1.5 Baits (consumables — placed in/near a trap to raise catch rate)
Bait is bug-type-specific; matching the bait to the swarm is the skill.
| id | one-line | attracts |
|----|----------|----------|
| `rotten_fruit` | a mush of fermenting fruit | flies, gnats (ties to §6.2 egg piles, §9.3) |
| `nectar_dab` | a smear of sweet nectar | butterflies, bees, moths |
| `sugar_water` | a dish of sweet water | most swarm bugs, mild |
| `meat_scrap` | a chunk of raw meat | wasps, carrion beetles, predators |
| `dung_pat` | a pat of dung | dung beetles, certain flies |
| `aphid_culture` | a leaf seeded with aphids | ladybugs, ants, predatory bugs |
| `fungal_bait` | a cap of mushroom paste | cave/underground bugs (springtails, cave crickets) |
| `blood_drop` | a drop of blood | mosquitoes |

### 1.6 Lures & pheromones (placed attractant stations / consumables, by bug type)
Stronger, longer-range, type-targeted draw than plain bait; pull a swarm center toward a spot
(ties to §5.3 swarm meters and §9.2 pollination heuristics).
| id | one-line | targets |
|----|----------|---------|
| `floral_lure` | a perfumed blossom cluster on a stake | butterflies, bees, moths |
| `pheromone_wick` | a slow-release scent wick (generic) | nearest swarm of any matching type |
| `bee_pheromone` | queen-scent lure | bees (draws toward hives; pairs with beekeeping) |
| `moth_pheromone` | female-moth scent lure | moths at night |
| `ant_trail_scent` | a painted formic-acid trail | ants (steer a colony's foraging line) |
| `wasp_lure` | a fermented-protein lure | wasps (dangerous — draws predators in) |
| `mosquito_attractant` | a warm CO2-mimic puck | mosquitoes |
| `mega_lure` | a potent broad-spectrum attractant | any swarm, big radius; rare/expensive |

### 1.7 Light traps (night catching — passive, ambiance crossover)
Light pulls night-flying swarm bugs (moths, gnats, some flies, lanternbugs).
| id | one-line | tier |
|----|----------|------|
| `candle_trap` | a candle over a funnel and pan | poor |
| `lantern_trap` | a hung lantern above a collection tray | common |
| `uv_light_trap` | a violet bug-zapper-style lamp + tray | mid (needs fuel/power per §11.6) |
| `mercury_lamp_sheet` | a bright lamp on a white sheet (mothing rig) | high; best night-bug variety |
| `glowbug_lure` | a jar of captive glow-bugs used as living bait | mid; bug-farming crossover (see lighting_ambiance.md `glowbug_jar`) |

### 1.8 Subdual tools (don't catch — make the catch possible, §7.2/§7.3)
| id | one-line | role |
|----|----------|------|
| `smoker` *(see §7.2)* | hand bellows-smoker that calms bees/insects | lowers agitation before harvest/catch |
| `smoke_bomb` | thrown smoke pod | area calm for an angry swarm |
| `chill_canister` | a cold-gas puff that briefly slows a bug | down fast individual bugs to net them |
| `stun_rod` | a short prod that briefly stuns | knock down a large bug w/o killing (combat-lite) |
| `magnify_glass` *(study, §17)* | inspect a captured bug for its needs | unlocks breeding conditions/preferences |

---

## 2. PENNING (containment by MATERIAL × SIZE)

Containment strength = **material tier** (from `materials/ores_metals.md` ladder). Escape behavior
(§8.2) keys off material vs bug: gentle bugs never break out; chewers (termites) shred weak wood
fast; strong/giant bugs need iron/steel/exotic. The grid below is the **build-it-yourself** ladder;
purpose-built containment furniture follows.

### 2.1 Pen-material ladder (fences/walls/gates — building blocks you arrange)
Extends existing `fence_*`, `gate_*`, `wall_*`. SIZE is how many you place; MATERIAL is the row.
| material tier | fence id | gate id | wall id | holds |
|---------------|----------|---------|---------|-------|
| Wood (poor) | `fence_wood` *(exists)* | `gate_wood` *(exists)* | `wall_wood` *(exists)* | calm/weak bugs; chewed by termites/strong bugs |
| Woven/wicker | `fence_wicker` | `gate_wicker` | — | flightless small bugs; cheap, frail |
| Stone | `fence_stone` *(exists)* | `gate_stone` | `wall_stone` *(exists)* | digging bugs (won't be chewed); not flyers |
| Iron | `fence_iron` *(exists)* | `gate_iron` *(exists)* | `wall_iron` | strong bugs, most individual bugs |
| Mesh/screen | `fence_mesh` | `gate_mesh` | `wall_mesh` | FLYERS (lets air/light through, blocks flight) |
| Electric | `fence_electric` *(exists)* | `gate_electric` | — | deters/zaps escapees; needs power (§11.6) |
| Steel | `fence_steel` | `gate_steel` | `wall_steel` | aggressive/large individual bugs |
| Reinforced/exotic | `fence_reinforced` | `gate_blast` | `wall_reinforced` | GIANT/boss-scale bugs; top of ladder |
| Glass panel | `fence_glass` | — | `wall_glass` | display pens; see-through, climb-proof |

Helpers/parts that make hand-built pens work:
| id | one-line | role |
|----|----------|------|
| `fence_corner_wood` *(exists)* | corner post for clean turns | layout |
| `fence_corner_iron` | iron corner post | layout |
| `pen_canopy` | a mesh roof panel | stops flyers escaping over an open-top pen |
| `pen_floor_screen` | a buried screen floor section | stops diggers tunneling out |
| `feed_gate` | a small hatch in a fence for feeding without opening | reduces escapes during chores |

### 2.2 Terrariums (small individual bugs — purpose-built display/farm furniture)
Extends existing `bug_terrarium`. SIZE × richness ladder.
| id | one-line | tier | holds |
|----|----------|------|-------|
| `terrarium_jar` | a planted glass jar habitat | poor | one tiny bug |
| `bug_terrarium` *(exists)* | glass display case on a wooden stand | common | one prized specimen |
| `terrarium_planted` | a lush bioactive glass tank with moss & wood | mid | small bugs that breed in cover (crickets, beetles) |
| `terrarium_desert` | a sand-and-rock arid tank under a lamp | mid | scorpions, desert beetles |
| `terrarium_grand` | a tall ornate vivarium with brass frame | fancy | showpiece; multi-bug exhibit |

### 2.3 Cages (individual bugs — wire/metal, by material × size)
| id | one-line | tier | holds |
|----|----------|------|-------|
| `cage_wicker` | a small woven dome cage | poor | a single calm cricket/beetle |
| `cage_wire` | a round wire cage on a stand | common | small-to-mid individual bugs |
| `cage_iron` | a sturdy barred iron cage | mid | aggressive mid bugs (mantises, wasps singly) |
| `cage_steel` | a heavy bolted steel cage | high | large individual bugs |
| `cage_aviary_dome` | a big domed mesh cage | high | flying individual bugs / many small flyers |

### 2.4 Aquariums & larva tanks (aquatic bugs & larvae)
Extends existing `aquarium`. Aquatic stages of many bugs (mosquito larvae, dragonfly nymphs).
| id | one-line | tier | holds |
|----|----------|------|-------|
| `aquarium` *(exists)* | small glass tank with fish & plants | common | aquatic bugs/nymphs; repurpose for larvae |
| `larva_tank` | a shallow water tray with floating debris | common | mosquito/fly larvae (rearing) |
| `nymph_pond` | a planted water-edge tank | mid | dragonfly/damselfly nymphs |
| `aquarium_grand` | a tall reef-style display tank | fancy | showpiece aquatic exhibit |

### 2.5 Aviaries & flight enclosures (flying swarm bugs)
| id | one-line | tier | holds |
|----|----------|------|-------|
| `butterfly_house` | a tall mesh A-frame with flowers inside | common | butterflies/moths (pairs w/ milkweed, §9.1) |
| `flight_aviary` | a room-sized mesh aviary frame | mid | bee/butterfly swarms |
| `screened_gazebo` | a fancy screened pavilion | fancy | mixed-flyer showpiece; sit inside |

### 2.6 Giant-bug pens (top of the ladder, §4/§14 boss-scale)
GIANT bugs only hold in reinforced/exotic builds; cheap pens are destroyed (§8.2).
| id | one-line | tier | notes |
|----|----------|------|-------|
| `pen_post_reinforced` | a massive anchored steel post | high | the corner of a giant pen, paired with `fence_reinforced` |
| `containment_pylon` | a humming exotic-material pylon | top | projects a containment field segment for giant bugs |
| `giant_corral_gate` | a huge winched blast gate | high | the openable section of a giant pen |
| `bedrock_anchor` | a deep foundation block | high | stops giant diggers/burrowers undermining a pen |

---

## 3. HERDING (move penned/loose bugs without catching them)

Driving swarm centers and individual bugs around a plot — layout-driven, gentle.
| id | one-line | targets / role |
|----|----------|----------------|
| `herding_rod` | a long flexible rod with a fluttering tip | nudges individual bugs / a swarm center to move |
| `herding_flag` | a hand flag to wave bugs along | poor herding tool; wide slow push |
| `lure_wand` | a handheld lure on a stick (carryable bait) | leads a swarm by walking it toward food |
| `smoker` | bellows-smoker (also §1.8) | smoke drives bees/insects away from a spot, calm |
| `smoke_curtain` | a placed smoldering pot making a smoke line | a temporary "soft wall" bugs avoid |
| `drover_fence` | a low angled guide rail | funnels herded bugs toward a gate/intake |
| `one_way_baffle` | a v-shaped one-way gap in a fence | bugs enter the pen but can't easily leave |
| `herding_lamp` | a portable light to lead night flyers | walk moths/gnats into an aviary after dark |
| `chill_fan` | a placed fan blowing cool air | bugs drift away from the cold; steer flyers |
| `scent_post` | a re-applicable pheromone post (§1.6 family) | a fixed attract/repel point to shape paths |

---

## 4. BREEDING / GROWING (population production, §6 life stages)

Life stages (egg → larva/juvenile → adult) are tracked at population level (§6.1). These objects
feed, breed, and rear bugs. None are "free production" — they enable, they don't auto-solve.

### 4.1 Feeders (keep a penned population fed → reproduction readiness, §9.2)
| id | one-line | feeds |
|----|----------|-------|
| `feed_trough` | a low wooden trough of scraps | general penned bugs |
| `nectar_feeder` | a hung sugar-water feeder | bees, butterflies, moths |
| `fruit_feeder` | a spiked tray for fruit halves | fruit flies, beetles |
| `meat_feeder` | a hook holding carrion | wasps, predatory bugs |
| `leaf_feeder` | a clip holding fresh host leaves | caterpillars, leaf-eaters (needs the right plant) |
| `auto_feeder` | a hopper that drips feed on a slow timer | reduces feeding-chore tedium; capacity-capped |

### 4.2 Breeding boxes & nurseries (pairing/laying → eggs)
| id | one-line | tier | role |
|----|----------|------|------|
| `breeding_box` | a small dark wooden mating box | common | pair adults to produce egg piles (§6.2) |
| `breeding_terrarium` | a planted breeding vivarium | mid | controlled breeding w/ visible conditions |
| `nursery_rack` | shelved trays for many small broods | mid | rear several broods at once; layout reward |
| `nursery_grand` | a glass-fronted climate nursery | fancy | best brood survival; showpiece |
| `egg_tray` | a dimpled tray that collects/holds egg piles | poor | gather eggs (§6.2) for incubation |

### 4.3 Incubators (egg → hatch, faster/safer than the wild)
| id | one-line | tier | role |
|----|----------|------|------|
| `incubator_box` | a small insulated wooden warm-box | common | warms egg piles to hatch (manual fuel) |
| `incubator_lamp` | a heat-lamp incubator shelf | mid | several clutches; needs fuel/power (§11.6) |
| `incubator_climate` | a glass climate-controlled incubator | high | precise temp/humidity; rare-bug hatching |

### 4.4 Larva tanks & rearing (juvenile stage grow-out)
| id | one-line | rears |
|----|----------|-------|
| `larva_tank` *(see §2.4)* | shallow water rearing tray | aquatic larvae |
| `grub_bed` | a tray of damp substrate/compost | beetle grubs, fly maggots (ties to `compost_bin`) |
| `caterpillar_rack` | netted leaf-feeding frames | caterpillars → pupae/chrysalis |
| `pupa_shelf` | a quiet shelf to hang pupae/cocoons | metamorphosis stage; don't disturb |
| `silkworm_tray` | mulberry-leaf rearing trays | silkworms → silk/cocoons (feeds alchemy_potions.md silk) |

### 4.5 Honeydew / aphid ranching (a whole mini-system)
Ants "farm" aphids for honeydew; the player can too. Crossover with ants (§9) & cooking.
| id | one-line | role |
|----|----------|------|
| `aphid_ranch` | a potted host-plant with a managed aphid colony | produces honeydew; food source |
| `honeydew_tap` | a collector clipped under the ranch | harvests honeydew (cooking_food.md, alchemy) |
| `ladybug_gate` | a controllable hatch to admit/exclude ladybugs | predator control — let them in to cull, keep them out to ranch |
| `ant_dairy` | a managed ant-tended aphid station | ants protect aphids; higher honeydew yield |

### 4.6 Bee & queen housing (extends existing beekeeping)
Existing: `beehive_basic/medium/large/deluxe`, `honey_extractor`. Add support gear.
| id | one-line | role |
|----|----------|------|
| `queen_cell_box` | a small box rearing new queens | split/expand a bee colony |
| `nuc_box` | a small starter nucleus hive | seed a new hive from an existing one |
| `bee_skep` | a rustic woven straw beehive | poor/decorative early hive |
| `swarm_trap_box` | a baited box to catch a wild bee swarm | start a colony from a wild swarm |
| `wasp_nest_box` | a sheltered box for a wasp colony | farm wasps (needs prey supply, §9.2) |
| `ant_formicarium` | a sand-filled glass ant farm + nest tube | farm an ant colony (extends `ant_eggs`) |
| `queen_chamber` | a protected nest chamber for a queen | keeps a colony's queen safe = stable population |

---

## 5. Which bug types need what (quick matrix)

| bug type | catch with | pen with | breed/grow with |
|----------|-----------|----------|-----------------|
| flies / gnats | nets, `fly_netting`, rotten_fruit bait, sticky/light traps, autonet | mesh fence/aviary (flyers) | `grub_bed`, egg piles, `larva_tank` |
| mosquitoes | blood_drop bait, uv_light_trap, mosquito_attractant | mesh/aviary | `larva_tank` (aquatic larvae) |
| butterflies/moths | floral_lure, light traps (moths), gentle nets | `butterfly_house`, mesh | `caterpillar_rack` + host plant, `pupa_shelf` |
| bees | smoker + nets, bee_pheromone, swarm_trap_box | hives + `flight_aviary` | hives, `queen_cell_box`, `nuc_box`, nectar_feeder |
| wasps | meat_scrap/wasp_lure, cage_trap | iron/steel cage, `wasp_nest_box` | `wasp_nest_box` + prey (predation, §9.2) |
| ants | ant_trail_scent, fungal_bait | `ant_formicarium` (glass) | `ant_formicarium`, `queen_chamber`, aphid ranch |
| aphids | aphid_culture (cultured, not "caught") | on host plants | `aphid_ranch`, `ant_dairy` |
| beetles/crickets | pitfall/box trap, nets | terrariums, wire/iron cage | `grub_bed`, `breeding_box` |
| spiders | box/cage trap (individual) | `cage_iron`, terrarium | `breeding_terrarium` (careful — cannibal) |
| scorpions | cage_trap, chill_canister | `terrarium_desert`, iron cage | desert breeding terrarium + heat |
| dragonflies | gentle/silk net, nymph rearing | `flight_aviary` | `nymph_pond` (aquatic nymph stage) |
| cave bugs | fungal_bait, glowbug_lure | terrarium (dark/damp) | substrate trays |
| GIANT/boss bugs | `net_giant`, `bola_capture`, stun_rod | `containment_pylon` + `fence_reinforced` + `bedrock_anchor` | reinforced breeding corral (very slow) |

---

## Open questions / follow-ups
- Exact escape rates per (material × bug) belong in the ecology proposal (P2), not here.
- Some "auto" entries (auto_feeder, auto_trap_resetting, autonet) need the fuel/power flag from
  §11.6 — do not add to entity schema ahead of that feature.
- Display vs farm: terrariums/cages double as decor (idle furniture boosts, §11.5) and containment;
  flag which are showpieces vs working pens when these graduate to the catalog.
