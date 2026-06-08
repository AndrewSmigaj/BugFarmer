# Ant Colony — Bugs brainstorm

The deepest, hardest demo zone is itself a living creature: one **superorganism** of ant castes radiating
from the Queen, the herded **aphid livestock**, the **parasites and raiders** that prey on the nest, and the
hangers-on (**myrmecophiles**) that live secretly among the ants. Lean into ecology — mutualisms, defense,
caste roles — and difficulty. Top-down sprites; large bugs (Queen, soldiers, raiders) are elite.

---

## The ant castes (the colony / superorganism)

The whole nest is effectively one organism; the castes are its "organs." Provoking one alerts the rest.

- `ant_worker` — the common small dark ant; hauls, digs, tends garden; mostly harmless alone but
  **overwhelming in numbers**. The colony's labor and the zone's filler bug. *Common. Low threat solo,
  swarm threat. Defense: numbers/alarm pheromone.*
- `ant_worker_laden` — a worker carrying a leaf fragment or a grub; same ant, "busy" variant for trails.
- `ant_forager` — a leaner, faster worker that roams the tunnels and surface shaft scouting for food.
- `ant_leafcutter` — a worker hefting a cut leaf-disc overhead; works the leaf trail down into the garden.
  *Mutualism: feeds the fungus farm.*
- `ant_minor` — a tiny ant caste that tends the delicate fungus and grooms larvae; gentle, non-combatant.
- `ant_major` / `ant_soldier` — large, armored, with oversized mandibles; **the real danger**, guards
  chambers and swarms intruders. *Uncommon. High threat. Drops chitin + formic acid. Defense: bite + acid spray.*
- `ant_soldier_giant` — an outsized super-soldier with massive head and shearing jaws; mini-elite gatekeeper
  of the Queen's approaches. *Rare, elite.*
- `ant_nurse` — a pale worker tending eggs and larvae in the brood chambers; non-aggressive unless the
  brood is threatened (then frantic). *Defense: rallies soldiers.*
- `ant_drone` — a winged male ant, clumsy and short-lived, drifting near the royal chambers ahead of a
  nuptial flight. *Uncommon. Harmless. Flavor/loot.*
- `ant_repletes` — "honeypot" workers with grossly swollen honeydew-filled abdomens, hanging from a chamber
  ceiling as living storage jars. *Living larder; harvestable honeydew. Defenseless.*
- `ant_queen` — **enormous, immobile, the colony's heart**; a swollen egg-laying abdomen, attended by a
  ring of nurses. Threatening her triggers the full swarm. *Semi-boss. Drops royal jelly / queen-stuff
  (rare). Killing her collapses the colony (windfall + niche change).* See `ecology_proposal.md`.
- `ant_queen_winged` — a young virgin queen with wings, poised to leave on a founding flight; rare alternate.
- `ant_larva` — a soft pale grub in the brood pile, tended by nurses; not a threat, a "resource." *Food/bait.*
- `ant_pupa` — a cocoon-wrapped pupa in the nursery, on the edge of hatching.

### Other ant species (rivals / variants for variety)
- `army_ant` — a nomadic blind raider ant moving in living rivers; appears as a raiding column, not a
  resident. *Elite swarm event; consumes everything in its path, including the nest.*
- `fire_ant` — a coppery-red aggressive ant with a venomous sting; a rival colony pocket. *Uncommon.
  Venom (alchemy); stings.*
- `carpenter_ant_big` — a large black ant nesting in the dead root husks; chews wood, mostly defensive.
- `bullet_ant` — a single huge solitary ant with an agonizing sting; rare deep-tunnel terror. *Rare, elite.
  Potent venom.*
- `slave_maker_ant` — a raider ant that steals brood from other colonies; a dark-ecology curiosity.

---

## The aphid "livestock" (the herded mutualists)

The ants protect and milk aphids for honeydew — the zone's signature mutualism and the bug-farming hook.

- `aphid` — a small soft pear-shaped green/yellow sap-sucker clustered on root tendrils; the colony's
  "cattle." *Common. Harmless. Produces honeydew when tended. Tame-able (ranching hook).*
- `aphid_winged` — a winged aphid (dispersal morph) ready to fly off and found a new herd; alternate.
- `aphid_giant` — an outsized prize aphid, a swollen honeydew factory the ants prize. *Uncommon. Big honeydew yield.*
- `aphid_red` / `aphid_woolly` — color/woolly-wax variants for pasture variety; the woolly one trails white fluff.
- `aphid_herd` — a dense cluster occupant: a knot of aphids covering a root patch (a "head of livestock").
- `scale_insect` — a sedentary sap-sucker that the ants also farm, glued to a root like a little limpet;
  alternate livestock. *Honeydew; very passive.*
- `mealybug` — a soft white waxy sap-sucker, another tended honeydew-producer; clusters in root crevices.
- `treehopper_tended` — a horned hopper the ants guard for its honeydew (a real ant mutualism); livelier
  livestock that bounces away if spooked.

---

## Parasites, invaders & raiders (the threats to the nest)

The colony is prey too — these attack, infiltrate, or raid the nest. Ecology + danger.

- `parasitoid_wasp` — a slender wasp that hunts the tunnels to lay eggs in ant grubs; the nest's terror.
  *Uncommon, dangerous. Sting; alchemy (venom). Threatens brood → nurses panic.*
- `phorid_fly` — a tiny "ant-decapitator" fly that lays an egg in a worker's head (a real ant parasite);
  workers flee it in panic disproportionate to its size. *Flavor + ecology gem. Harmless to player.*
- `nest_beetle_raider` — an armored beetle that breaks into nests to eat brood and fungus; shrugs off ant
  bites. *Uncommon, tanky. Drops chitin.*
- `rove_beetle_mimic` — a beetle that **chemically mimics ant scent** to live among them and eat their larvae
  (a myrmecophile predator); looks almost like an ant until it strikes. *Rare. Stealth predator.*
- `blister_beetle` — a beetle whose larvae parasitize the brood; the adult bleeds caustic fluid if crushed.
  *Alchemy (cantharidin); caustic hazard.*
- `velvet_ant` — actually a wasp (a "cow killer") that invades for grubs and has a ferocious sting; fuzzy red.
  *Rare, elite. Powerful sting.*
- `antlion_larva` — a buried ambush larva at a sandy tunnel pinch, jaws waiting in a pit-trap; doesn't move,
  but seizes whatever falls in. *Trap-predator landmark-bug. Drops jaws.*
- `parasitic_mite_swarm` — a creeping film of tiny mites riding on and draining the workers; an infestation
  occupant rather than a single bug. *Pest; out-of-balance indicator.*
- `cordyceps_ant` — a worker killed by a fungus, frozen in a death-grip on a root with a fruiting stalk
  jutting from its head (zombie-ant fungus). *Eerie static occupant; alchemy (rare spores).*

---

## Myrmecophiles & deep nest hangers-on (live secretly among the ants)

The strange ecology of things that have evolved to exploit a colony — great for "huh, what's that?" finds.

- `aphid_wolf` (lacewing larva) — a tiny predator that disguises itself in wax/corpses and eats the aphid
  herd from within; the rancher's pest. *Uncommon.*
- `ant_cricket` — a tiny wingless cricket that lives in the nest stealing food from workers' mouths.
  *Harmless flavor.*
- `silverfish_nest` — pale silverfish scuttling through the brood chambers eating scraps and shed skin.
- `springtail_swarm` — a haze of tiny springtails on the damp garden floor recycling waste; harmless,
  busy texture-bug. *The garden's "cleanup crew."*
- `nest_woodlouse` — a pale isopod trundling the compost terraces eating spent substrate; gentle detritivore.
- `pseudoscorpion` — a tiny clawed pincher-bug riding the workers, hunting mites (a beneficial guest).
  *Uncommon curiosity.*
- `myrmecophile_beetle` — a smooth tortoise-like beetle the ants tolerate and even groom; mooches food.
- `nest_moth` — a wax/detritus moth whose grubs eat refuse in the deep chambers; flutters in lantern-glow.

---

## Deep-tier wanderers (where the nest meets the mining caves)

The boundary with the ore caves above lets a few cave bugs leak in (ties to the Mining Caves zone).

- `cave_roach` — a pale armored roach scavenging the abandoned dig and the miner's pack; see `roach_giant`.
- `centipede_hunter` — a fast venomous centipede that hunts down the tunnels; preys on workers. *Dangerous;
  segmented (head + body, per the segmented-bug pipeline).*
- `cave_cricket` — a long-legged pale cricket springing through the upper shaft.
- `mining_grub` — a fat pale grub burrowing the deep clay near the ore seams; passive, good bait.
- `glowworm_string` — a curtain of glowworm larvae on a damp ceiling, points of cold light; ambient + light.

---

## Notes (ecology, defense, difficulty)
- **Superorganism alarm:** harming any caste releases an alarm response — soldiers converge, the threat
  level ramps. The Queen is the apex: provoking her triggers a full-nest swarm (semi-boss fight).
- **Caste loot ladder:** workers → little (chitin scraps, ant eggs); soldiers → chitin + formic acid;
  giants/raiders → elite chitin; Queen → royal jelly / queen-stuff (rare). Honeypot `ant_repletes` and the
  aphid herd → honeydew.
- **Mutualisms to disrupt (emergent hooks):** ants ↔ aphids (honeydew), ants ↔ fungus garden (food).
  Disrupt the aphids or kill the workers and the colony starves/destabilizes (mold overruns the garden) —
  per `ecology_proposal.md`. Killing the Queen collapses the colony entirely.
- **Bug-farming hook:** the aphids (and scale/mealybug/treehopper) are the tame-able livestock the zone
  teaches — learn ant husbandry, ranch your own honeydew.
- **Difficulty:** Hard. Soldiers + raiders + parasitoid wasp are real threats; the Queen is a semi-boss.
  Army-ant raids and antlion pits make the tunnels dangerous even between fights.
