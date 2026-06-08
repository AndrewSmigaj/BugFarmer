# Brainstorm — Village Bugs

The bug ecology for the **village** (`village_21`) — the game's **fly-ecology showcase** and the
*safe* starting hub. No threats: only the fly chain (and its predators) plus benign town bugs that
make the place feel alive. The orchard + Fly Farm make the chain legible to a new player.

**The documented chain (zone doc §"Key species & ecology"):**
> fruit trees → fallen fruit → **rot** → **flies** → predators (frogs / spiders, migrant wasps)

**Already in the catalog (reuse, don't re-add):** flies — `fly_house`, `fly_horse`, `fly_bot`,
`fruitfly_common`, `fruitfly_vinegar`, `fruitfly_spotwing`; predators/visitors — `spider_orb`,
`wasp_paper`, `wasp_yellowjacket`; benign — `ladybug_orange`, `ladybug_giant`, `bee_carpenter`,
`firefly_blue`, `firefly_great`, `butterfly_swallowtail`, `butterfly_emperor`, `moth_brown`,
`moth_luna`, `snail_pond`, `roach_common`. Everything below is **new** and fills village-specific gaps.

Bugs use `"family": "creature"` and `"materials": ["dirt"]` like the existing entries.

---

## 1. The fly chain — life stages & missing links
The chain is currently "adult flies appear on rot". To make it *legible and farmable* (the Fly Farm
demo) we want the **egg → larva → adult** stages visible, plus a couple more adult flies.

| id | one-line | role / rarity |
|----|----------|---------------|
| `fly_eggs` | a tiny cluster of pale FLY EGGS laid on rotting fruit, top-down | stage 1 — appears on `rotten_fruit`; common |
| `maggot` | a small pale fly LARVA / maggot wriggling on rot, top-down | stage 2 — the harvestable bait/feed; common |
| `fly_pupa` | a small brown capsule-shaped fly PUPA case | stage 3 — pre-adult; common |
| `fly_cluster` | a knot of several HOUSEFLIES swarming a spot, top-down | the "flies are here" mass marker over rot/compost |
| `fly_flesh` | a metallic blue-grey FLESH FLY, top-down, bristly | adult variety; favors deeper rot; uncommon |
| `fly_greenbottle` | a brilliant metallic-GREEN blowfly, top-down | shiny adult variety; the prettiest fly to catch; uncommon |
| `fly_bluebottle` | a metallic-BLUE blowfly, stout, top-down | adult variety; common around compost |
| `fly_crane` | a big gangly CRANE FLY with very long dangling legs, top-down | gentle giant; harmless; dusk; uncommon |
| `fly_hover` | a HOVERFLY — black-yellow wasp-mimic that hovers over flowers, top-down | *beneficial* — a pollinator AND its larvae eat aphids; uncommon |
| `fly_drone` | a DRONE FLY (bee-mimic hoverfly), top-down | flower visitor; benign mimic; uncommon |

## 2. Predators of the fly chain (the population control)
The town stays in balance because predators crop the flies. These are the "good" hunters a player
*wants* around the orchard/farm — and the migrant wasps that drift in from the Wasp Thicket (E).

| id | one-line | role / rarity |
|----|----------|---------------|
| `frog_green` | a plump green POND FROG, top-down | the SW-lake fly-eater; signature village critter; common |
| `frog_brown` | a small brown toad-like FROG, top-down | garden/compost frog variety; common |
| `tadpole` | a little dark TADPOLE in the shallows, top-down | the frog's young; lake-margin life; common |
| `spider_house` | a small thin grey HOUSE SPIDER, top-down | indoor/eaves fly-catcher; common |
| `spider_garden_cross` | a CROSS / garden ORB-WEAVER on its web, top-down | orchard web-spinner (companion to `spider_orb`); common |
| `wasp_common` | a slim black-yellow COMMON WASP, top-down | migrant from the Wasp Thicket; scavenges fruit + hunts flies; uncommon |
| `wasp_hornet` | a large brown-yellow HORNET, top-down | rarer migrant; the "edge of danger" visitor; rare |
| `mantis_garden` | a green PRAYING MANTIS perched, top-down | elite benign ambush predator; prized sighting; rare |
| `dragonfly_common` | a slim blue DAMSEL/DRAGONFLY over the lake, top-down | aerial fly-hunter at the water (lighter than the elite `dragonfly_*`); uncommon |
| `bird_robin` | a small red-breasted ROBIN hopping on the lawn, top-down | (if birds are in scope) eats grubs/flies; charming town life; common |
| `chicken_hen` | a brown farmyard HEN pecking, top-down | NPC-yard fowl that eats bugs; lived-in farm detail; common |

## 3. Benign town bugs (atmosphere — the place feels alive)
No combat role; they make the village *charming* and tie to the pollinator/decoration loops.

| id | one-line | role / rarity |
|----|----------|---------------|
| `bee_honey` | a fuzzy golden-brown HONEYBEE, top-down | the village pollinator; drifts from the Bee Meadow (W); common |
| `bee_bumble` | a round fuzzy black-yellow BUMBLEBEE, top-down | gentle big pollinator; flower beds; common |
| `ladybug_red` | the classic RED ladybug with black spots, top-down | beloved benign beetle; aphid-eater; common |
| `ladybug_yellow` | a yellow 22-spot LADYBUG, top-down | ladybug variety; uncommon |
| `butterfly_cabbage_white` | a small white CABBAGE WHITE butterfly, top-down | the everyday town butterfly; veg-patch regular; common |
| `butterfly_monarch` | an orange-black MONARCH butterfly, top-down | migrant beauty on `milkweed`; uncommon |
| `butterfly_painted_lady` | an orange-brown PAINTED LADY butterfly, top-down | flowerbed visitor; common |
| `moth_garden_tiger` | a bold cream-and-orange TIGER MOTH, top-down | night flowerbed moth; uncommon |
| `firefly_common` | a small beetle with a soft green glowing tail, top-down | dusk lawn/lake magic (lighter than elite fireflies); common at night |
| `grasshopper_green` | a green GRASSHOPPER, top-down | meadow-edge hopper; harmless; common |
| `cricket_field` | a brown FIELD CRICKET, top-down | the night-sound bug; lawn/hearth; common |
| `beetle_garden` | a small iridescent GROUND BEETLE, top-down | benign garden-soil beetle; common |
| `earthworm` | a pink EARTHWORM half out of the soil, top-down | compost/garden health indicator; fishing bait; common |
| `snail_garden` | a brown-shelled GARDEN SNAIL, top-down | benign (mild crop nibbler); after-rain detail; common |
| `slug_garden` | a soft grey GARDEN SLUG, top-down | damp-corner critter; veg-patch pest (very mild); common |
| `ant_garden` | a single black GARDEN ANT, top-down | trails to crumbs/aphids; lived-in detail; common |
| `pillbug` | a grey ROLY-POLY / woodlouse, top-down | under-log/compost detritivore; harmless; common |
| `lacewing` | a delicate green LACEWING with lacy wings, top-down | *beneficial* — its larvae eat aphids; uncommon |

---

### Ecology + economy hooks (for the ecology proposal / balance docs)
- **The teachable chain:** `rotten_fruit` → `fly_eggs` → `maggot` → `fly_pupa` → adult
  (`fly_house`/`fruitfly_*`). The **Fly Farm** demos this on purpose (compost + fallen fruit + nets);
  the **Orchard** is the wild version. `maggot` is the harvestable feed/bait output.
- **Predators crop flies:** `frog_green`/`frog_brown` (lake & garden), `spider_house`/
  `spider_garden_cross` (eaves & orchard), migrant `wasp_common`/`wasp_hornet` (from the E thicket),
  plus `mantis_garden` as the prize sighting. Player keeping predators around = fewer flies.
- **Beneficials vs pests:** `fly_hover`/`fly_drone`/`lacewing`/`ladybug_*` eat aphids and pollinate —
  candidates for a *beneficial-bug* decoration/farm bonus. `slug_garden`/`snail_garden` are the only
  (very mild) "pests" — they keep the safe hub safe while still teaching the pest concept.
- **Pollinators tie to flora:** bees/butterflies/hoverflies follow the flower beds and blossom trees
  from [`flora/village.md`](../flora/village.md) and [`trees/village.md`](../trees/village.md) —
  a hook for a pollinator-attract decoration bonus.
- **Night layer:** `firefly_common`, `cricket_field`, `moth_garden_tiger` give the village a distinct
  dusk mood around the lake and lamp posts.
