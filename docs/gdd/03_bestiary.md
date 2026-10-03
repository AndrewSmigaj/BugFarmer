# §03 · Bestiary & tiers
<!-- gdd: id=03 status=review updated=2026-10-03 -->

## The experience
Every bug is a real animal doing what it really does, made giant. You learn them the way a naturalist does: where
each lives, when it's out, what it eats, how it breeds, how it warns you. The fly roosts high at night and can't be
swatted; the paper wasp raises its wings before it stings; the cave spider drops on a thread from a white egg sac on
the roof; the locusts turn yellow and black when they crowd; five ants follow your bug stick off their trail while the
rest carry on. Each family plays differently, danger grows outward, and every danger warns you first.

## Decided
- **Real species with real behaviour** (2026-07-11): the game teaches a little ecology and biology; the prototype's
  invented names are replaced (2026-09-27). **Every bug carries its real name** (D80).
- **Bugs, fish and people survive**; birds, amphibians and reptiles died out too (2026-09-27).
- **Every bug is unfinished**, including those already in the prototype; each needs more passes for behaviour, combat
  and ecology tuning (2026-09-27) — no bug is finished today, and every one is polished or redone (2026-10-03).
- **The roster**: the bug list is settled (D79; 54 kept, 62 cut) and the bug lineups are the roster (D80–D82): bees
  climb in danger (honeybee, then the killer bee, and a proposed third that must live in hives — D81, D82; the bumblebee
  is accepted); termites and the stick insect are cut; mantis egg cases come from the game's own mantises; the farm
  cricket is a maybe.
- **Tiers belong to a species, not a rule**: one form, two or at most three (2026-09-27).
- **Two ant species**, black ants and fire ants, each with workers, warriors and a queen; fire ants far more dangerous
  (August 2026; 2026-10-02, D79).
- **The bug stick** (2026-10-02, D79): a non-lethal stick that can steer ants off their trail and herd them by tapping.
- **Mini-bosses and bosses**: set off by conditions or placed; a boss is the biggest of a few species, for real reasons
  (accepted, overview P13, 2026-09-28).
- **Ecosystems, not events** (D79); **no seasons** (2026-09-27).
- **What counts as a bug** (2026-09-28): insects and the other arthropods — spiders, scorpions, centipedes, millipedes,
  crayfish and crabs; fish are separate; no worms or leeches.
- **Bugs are livestock**: raised and farmed like animals on a farm, the heart of the game (2026-09-28).

## Current design
The roster by family (58 bugs; details per bug in P9 onward):
- **Flies:** house fly, horse fly, cave fly, ant-decapitating fly.
- **Wasps and hornets:** paper wasp, yellowjacket, European hornet, northern giant hornet, tarantula hawk.
- **Bees:** honeybee, killer bee, bumblebee, Asian honey bee (proposed).
- **Ants:** black ants, fire ants.
- **Centipedes and millipedes:** garden, tiger and giant centipedes; garden, giant African and dragon millipedes.
- **Scorpions:** forest scorpion, fat-tailed scorpion.
- **Dragonflies:** blue dasher, emperor dragonfly, dragonhunter.
- **Butterflies and moths:** queen butterfly (name open), monarch, purple emperor, luna moth, death's-head hawkmoth,
  silk moth.
- **Beetles:** carrion (burying) beetle, cave beetle, Hercules beetle, stag beetle, Colorado beetle, bombardier beetle.
- **Spiders and their kin:** cave spider, daddy longlegs, wolf spider, jumping spider, Brazilian wandering spider, black
  widow, Goliath tarantula, giant huntsman.
- **Water bugs:** house and malaria mosquitoes, water strider, crayfish, river crab.
- **Mantises and crickets:** Chinese mantis, orchid mantis, house cricket (maybe), field cricket.
- **Lights and swarms:** firefly, cave glowworm, desert locust.

Where each lives is GDD §04 (one proposal per zone).

## As built
- **Fifteen bugs run in the prototype**, all unfinished: the fly, the meadow butterfly, the paper wasp (as "the wasp"),
  the yellowjacket (as "the wasp soldier"), the European hornet (as "the giant hornet"), the honeybee, black ant workers
  and scouts, the garden, tiger and giant centipedes, the millipede, the carrion beetle, the dragonfly and the firefly.
- **The engine** (`architecture_bug_behaviour.md` §1): groups of bugs simulated identically on every player's computer;
  five ways of moving; flee, curious or attack reactions; a shared combat foundation with telegraphed attacks; four ways
  of feeding and breeding; ant trails that work per group, not per ant.
- **Gaps** (2026-10-03): the centipedes have no breeding place; the dragonfly never breeds and hunts the wrong prey; the
  firefly has no food; the hornet's nest has no picture or zone; the yellowjacket shares the paper wasp's nest.
- The other forty-three bugs exist only as designs (and some as pictures).

## How it will work
In short (the full plan is `docs/product/architecture/architecture_bug_behaviour.md`, and P2 below): about a dozen
shared building blocks are built once — leaving a group, trails, the bug stick, routines, nests, life stages, water
life, ambush, webs, defences, lights, parasites, locust crowding — and each bug is then its numbers, foods and homes
plus one signature mechanic. The home zones' bugs come first, one zone at a time; each bug is watched in its own Bug Lab
pen, checked so every player's game stays identical, and signed off by you before it goes into its zone.

## Proposals

### P1. Every bug has a home, a want, a routine and a signature
*The bestiary's rule for every bug.*
- **A home**: where it lives and rests (a nest, a burrow, a web, under logs, a crack in the rock, the water).
- **A want**: what it eats and where it breeds, both real and both present in its zone (§04 P1).
- **A routine**: when it's out (day, night, dusk), where it goes, and what rain or drought does to it. There are no
  seasons (decided), so the routine is daily.
- **A signature**: one thing it does that no other bug does, taken from the real animal — the ant's trail, the
  bombardier's boiling spray, the cave spider dropping on a single thread, the firefly's flash code. Bugs of the
  same family differ in how they play, not just in their numbers (the bestiary research, 2026-10-02).
- Each bug's sheet below (P9 onward) gives these, plus how it treats you, what it's for on the farm, and what it
  needs built.

**Lenses:** Real biology — every line comes from the real species (facts and sources in
`docs/product/investigations/research-2026-10-03/`). Picture the moment — a player learns where to look for each
bug, and when. **Cost and risk:** none here; the cost is in each bug.

### P2. How behaviour gets built: shared building blocks, zone by zone, signed off bug by bug
*The plan for building it (detail: `docs/product/architecture/architecture_bug_behaviour.md`).*
- **About a dozen shared building blocks** are built once and reused: leaving a group and acting alone; trails;
  the bug stick; day-and-night routines; nests and colonies; eggs, grubs and cocoons you can see; life in water;
  ambush and lures; webs; defences (sprays, clouds, curling up); lights and sounds; parasites and burial; locust
  crowding; and the player's tools on bugs. A new bug is then mostly its numbers, foods and homes plus its
  signature.
- **Order:** the blocks the home zones need first, then the five home zones one at a time (Village, Bee Meadow,
  Ant Tunnels, Mining Camp, Ant Colony) — every bug already there redone to its sheet, the newcomers added, then
  the zone's food web tuned. The later rings follow as each zone is built.
- **For each bug:** its sheet agreed with you → its numbers and homes → its behaviour → its picture (each batch
  of paid images asked for first) → a pen in the Bug Lab test zone where you can watch it feed, breed, hunt and
  react to you, with a short recording → the checks that every player's game stays identical → your sign-off →
  placed and tuned in its zone.
- **A bug is done** when it does what its sheet says, passes those checks with its behaviour actually happening,
  has its final art, carcass and examine facts, holds its numbers in its zone without the safety net doing the
  work, and you have signed it off. Until then it isn't finished — none is today.

**Lenses:** Fit — behaviour before numbers, as you accepted (overview P10); every bug runs on the players'
computers, identically, the way the game already works. Picture the moment — you watch each bug in its pen before
it reaches a zone. **Cost and risk:** large: about fifty-eight bugs and a dozen blocks. The individual behaviour
on players' computers is the biggest piece, so it is built one block at a time, ants first.

### P3. Groups where it doesn't matter, individuals where it does
- Flies, gnats, mosquitoes and bees out foraging can move as loose groups, which keeps hundreds of them cheap.
- A bug you handle, follow or fight acts on its own: an ant you tap, a wasp guarding its nest, a spider at its web,
  a scorpion in its burrow, a mother wolf spider. It can leave its group and come back.
- This is the step the ant trail needs (P4) and the one the whole bestiary leans on.

**Lenses:** Picture the moment — your example: five ants peel away and follow you while the column carries on.
Real biology — real colonies are individuals following shared signals. **Cost and risk:** the per-bug decision
logic runs on every player's computer and must stay identical; built and checked one block at a time.

### P4. The bug stick: tap, steer and lead
*Your mechanic (D79), designed.*
- **A tap** on a walking bug turns it from what it was doing to follow the stick for a short while. One tap takes
  one bug, or a few that are touching; a better stick takes more and holds them longer.
- **Ants** leave their trail and follow you; the rest of the column keeps going (P22, the black ants). Lead them
  to food and they start a new trail home that others follow; lead them nowhere and they drift back.
- **Other walkers** — beetles, crickets, millipedes, caterpillars — can be steered into a pen or away from your
  crops the same way. Fliers can't be tapped; stinging bugs don't follow, they defend.
- **Non-lethal:** the stick never harms a bug, so it's the gentle farmer's tool; a smoked bug can't be led.

**Lenses:** Fit — your idea, and a sandbox tool: it gives herding, feeding and pest control without walls.
Picture the moment — leading a line of ants past your bug catcher. **Cost and risk:** a new tool item, the tap
as a shared event, and the follow behaviour (P3); the item row joins the item table.

### P5. Eggs, grubs and cocoons you can see and farm
- Where a bug's young matter to play, they're in the world: caterpillars on milkweed (built), silkworms on the
  mulberry, stag beetle grubs in dead wood, mantis egg cases on stems, cave spider egg sacs on cave roofs, a wolf
  spider mother carrying her young, mosquito egg rafts on still water, glowworms on cave ceilings.
- The player can take, move or protect them: move caterpillars to a better plant, keep cocoons for silk, set
  mantis egg cases out against locusts, scrape mosquito rafts off a pond, leave a wolf spider mother alone.
- Young elsewhere stay unseen (a fly's maggots in rot), so the world isn't cluttered.

**Lenses:** Real biology — each is the real life cycle (the facts files). Curiosity — the life cycle is something
to find. **Cost and risk:** one model, already built for the butterfly, carried to new hosts.

### P6. Every danger warns first, and every danger has an answer
- Anything that hurts you shows a tell you can learn and dodge — a wasp's dive, a centipede's freeze, a
  scorpion's ground breaking open, a spider rearing up — as the combat foundation already does.
- Each danger has more than one answer: distance, smoke, light, stone instead of wood, the right outfit, an
  antidote, bait to draw it off, or its natural enemy.
- Stinging nests escalate: hitting a nest or crushing its bugs calls more defenders (real alarm scent); smoke
  stops the call (the July research's finding, and real beekeeping).

**Lenses:** Fit — preparation beats reflexes, the combat zones' design. Real biology — alarm scent and smoke.
**Cost and risk:** mostly built; the alarm call is one new shared event.

### P7. Night, light and lamps
- Night is its own world: fireflies flash, moths and the hornet come to lamps (real for both), glowworms light
  the caves, mosquitoes bite at dusk, wolf spiders' eyes shine back at a torch, scorpions glow under ultraviolet
  light (real), and the wandering spider walks.
- Lamps are therefore a choice: a lamp by your door draws moths for catching, and hornets with them.

**Lenses:** Picture the moment — a lamp ringed with moths, a torch sweeping a meadow and catching green eye-shine.
Real biology — every one of these is real. **Cost and risk:** lamps as lures are a small attraction grid; the
glows are display only.

### P8. An option for players afraid of spiders
- A setting that redraws spiders as rounder, legless critters, in steps, without changing how they behave or
  warn (the way Grounded does it).

**Lenses:** Player care — spiders are a common fear, and four zones lean on them. **Cost and risk:** extra
pictures only; nothing in the simulation changes.

### P9. House fly (Musca domestica) — the first livestock
*Village, and anywhere with rot · by day · in the prototype now (the fly), to be redone.*
- **Lives and moves:** loose, jittering clouds over rot and compost; at night they settle high up — tree crowns,
  fences, roofs — and lift off again at dawn (real flies rest high at night).
- **Eats:** rotting fruit, food waste, compost and carcasses — soft, wet food. The manure piles of the old world are
  gone with the mammals (decided), so the orchard and the compost are its whole world.
- **Breeds:** eggs on rot and compost; the maggots stay unseen in the rot; egg to fly in about a week at best, the
  fastest breeder in the game, as in life.
- **With you:** flies off; harmless. It sees about seven times faster than people, so a swung weapon misses and a
  net works — the slow, the full and the resting are the easy catches.
- **On the farm:** the starter livestock: raised in pens on compost, sold as meat and kept as maggots for bug feed
  and fish bait (the item rows).
- **Signature:** the fly you can't swat — it jinks away from a swing a moment before it lands.
- **To build:** the night roost on high perches (routine block); the dodge from a swing; the old manure entry
  taken out of its data.

**Lenses:** Real biology — eggs on rot, a week-long life cycle, high night roosts, fast eyes (facts file A).
Picture the moment — an orchard at dusk, flies settling on the branches like dust. **Cost and risk:** small.

### P10. Horse fly (the black horse fly, Tabanus atratus) — the biter of sunny wet edges
*Shallow Swamp edges and sunny wet meadows; Deep Swamp · by day only · new.*
- **Lives and moves:** fast, straight-flying, out in the sun; it avoids shade and stops at dusk.
- **Eats:** the females need blood to make eggs, and in 2126 the only large warm-blooded animals left are people,
  so they bite players; the males drink nectar.
- **Breeds:** egg masses on reed stems and stones over the water; the young live in the wet mud, hunting other
  water bugs' young (unseen).
- **With you:** females find you by sight and are drawn to dark, shiny, moving things (real), so a dark outfit and
  running draw them, and standing in shade breaks the chase. A bite is a small, sharp hit; it can't be smoked away
  because it has no nest to calm.
- **On the farm:** a pest, and a catch for the Bug Dealer.
- **Signature:** your outfit's colour matters — light clothes and shade are real protection.
- **To build:** a target pick that weighs dark, moving players (the outfit's colour is already known to the game);
  the shade-avoiding routine.

**Lenses:** Real biology — blood-feeding females, day flight, sight and dark surfaces (facts A; the species-level
sources are thin, so its numbers lean on the horse-fly family). Picture the moment — noon on the marsh edge, a
heavy fly circling your dark coat until you step into the shade of a willow. **Cost and risk:** the colour-aware
target pick is new.

### P11. Cave fly (the coffin fly, Conicera tibialis — species to be rechecked) — the runner of the underground
*Mining Camp, Ant Colony, the caves · no day or night underground · new (your underground fly).*
- **Lives and moves:** a scuttle fly: it runs across surfaces in fast, jerky bursts rather than flying, so it
  slips into gaps other bugs can't (real for the family).
- **Eats and breeds:** a problem found in the research: the coffin fly's real young eat buried human bodies, and no
  source puts it in caves or ant nests. I propose keeping your faster, stronger underground fly but rechecking its
  species against a scuttle fly that really lives in caves or ant nests before it's built; until then its food is
  the underground's dead bugs and the ants' refuse.
- **With you:** harmless and hard to net — a swing at the air misses a bug that runs; a net swept along the ground
  catches it.
- **On the farm:** food for cave spiders and glowworms, which is why it matters: it carries the dark food chain.
- **Signature:** the fly that runs instead of flying, so you catch it low.
- **To build:** the burst-running movement (a new movement style); a recheck of its real species.

**Lenses:** Real biology — scuttle flies really run in bursts (facts A). Honesty — its cave life isn't confirmed
for the species named in the bug lineups. **Cost and risk:** a new movement style; the species question.

### P12. Ant-decapitating fly (Pseudacteon tricuspis) — the fire ants' living enemy
*Deadly Ants outpost and core, and wherever fire ants forage · by day, most at midday · new.*
- **Lives and moves:** tiny flies hovering a few millimetres above fire-ant columns, darting down.
- **Eats:** adults take sugar; its young eat a fire ant from the inside.
- **Breeds:** it injects one egg into a fire-ant worker; after about two weeks the ant leaves the nest like a
  sleepwalker and dies, its head falls off, and the new fly grows in the empty head (real).
- **With you:** harmless; easy to net.
- **On the farm:** the safe answer to fire ants: raise them and release them over a mound, as the United States
  really did. Real fire ants forage far less when these flies are about (about 84% less).
- **Signature:** a fire-ant column that thins and slows when the flies hover over it, and "zombie" ants wandering
  away from the mound.
- **To build:** the parasite block (one bug living in another); a scare effect that cuts fire-ant foraging while
  flies are near.

**Lenses:** Real biology — every step is from the sources (facts A). Picture the moment — specks hovering over a
red column, one ant staggering off alone. **Cost and risk:** the parasite block.

### P13. Paper wasp (the European paper wasp, Polistes dominula) — the village wasp that teaches warnings
*Village, Bee Meadow edges · by day, home at night · in the prototype now (the wasp), to be redone.*
- **Lives and moves:** a queen and her workers on an open, umbrella-shaped paper comb hung under eaves, branches
  and fence rails — the whole nest in plain view, eggs and grubs in the cells.
- **Eats:** adults drink nectar, fruit juice and sap, and bite into ripe fruit (a real fruit pest); the young are
  fed chewed caterpillars above all, and flies.
- **Breeds:** one egg per cell in the open comb; a thriving nest founds daughter nests (built).
- **Hunts:** caterpillars on plants and flies, so it is the village's caterpillar check — which cuts both ways: it
  protects tomatoes from caterpillars and takes the young of your milkweed butterflies.
- **With you:** calm away from its nest. Near it, it warns in three steps — wings raised, then patrolling, then a
  wasp flies out and stings — the least aggressive wasp and the one that teaches the player to read warnings.
  Smoke calms it.
- **On the farm:** pest control for crops, a threat to a butterfly farm, and wasp grubs from its comb.
- **Signature:** the open nest you can watch, and the three-step warning.
- **To build:** hunting caterpillars on host plants; the three-step warning; its own nest picture, separate from
  the yellowjacket's.

**Lenses:** Real biology — open comb, caterpillar prey, fruit biting (facts A). Picture the moment — a comb under
the eaves of the Bug Dealer's shop, workers raising their wings as you come close. **Cost and risk:** small; the
caterpillar hunt uses the life-stage block.

### P14. Yellowjacket (the common wasp, Vespula vulgaris) — the hidden nest that boils over
*Wasp Thicket · by day, most in the morning · in the prototype now as the "wasp soldier", to be redone.*
- **Lives and moves:** thousands of workers from a hidden paper nest underground or in a hollow tree; they come and
  go through one entrance, so you find the nest by watching where they go.
- **Eats:** adults take nectar, rotten fruit and honey, and raid beehives for it; the young eat chewed insects —
  caterpillars, bees, flies, other wasps.
- **Breeds:** a big nest of thousands of cells; daughter nests when thriving.
- **Hunts:** a generalist hunter, and the beekeeper's thief at the hive door.
- **With you:** it stings again and again. Before stinging it rises on its legs, head forward, wings buzzing (its
  real threat pose). Hit the nest or crush a wasp and more come — the alarm call (P6). Smoke stops the call; the
  nest is safest at night.
- **On the farm:** a pest of hives and orchards; its grubs are food.
- **Signature:** finding the hidden nest by watching the workers, and the alarm that escalates.
- **To build:** the hidden ground or tree nest (its own nest picture); the alarm call (a new shared event);
  raiding hives for honey.

**Lenses:** Real biology — underground nests, repeat stings, threat pose, honey raids (facts A). Picture the moment
— watching workers stream into a hole under a root, then deciding whether to smoke it. **Cost and risk:** the alarm
event is new.

### P15. European hornet (Vespa crabro) — the night hunter at your lamps
*Wasp Thicket (the ranger station's lights), Hilltop Meadow (its top threat) · day and night · in the prototype now
(the "giant hornet"), to be redone.*
- **Lives and moves:** big, slow-cruising hunters from a paper nest in a hollow tree; it hunts by moonlight and
  comes to lamps (real).
- **Eats:** adults take sap (it strips bark from twigs to drink it), fallen fruit and other sweet things; the
  young are fed large insects: other wasps, dragonflies, mantises, moths, honeybees. It robs spider webs.
- **Breeds:** one nest per hollow tree, hundreds of workers; daughter nests when thriving.
- **Hunts:** the big insects of its zone, including the yellowjacket — so it checks the wasps as well as threatening
  your bees.
- **With you:** it avoids trouble unless stepped on, grabbed, or near its nest or its food; before attacking it does
  an alarm dance, buzzing and darting in and out (the July research). Smoke calms it.
- **On the farm:** a lamp by your hives brings hornets to them at night; a lamp far from them draws hornets away
  and lets you catch the moths they chase.
- **Signature:** lamps as bait — light decides where it hunts.
- **To build:** the night routine and lamp attraction (lights block); the hollow-tree nest; web robbing where
  spiders are.

**Lenses:** Real biology — night flight to lights, hollow-tree nests, prey list (facts A). Picture the moment — your
porch lamp at midnight, moths spiralling, a hornet sliding in out of the dark. **Cost and risk:** lamp attraction is
a small grid; the rest exists.

### P16. Northern giant hornet (Vespa mandarinia) — the hive raider of the far forest
*Millipede Forest · by day · new (your giant hornet).*
- **Lives and moves:** queens over 50 mm long; a nest underground among rotten roots; it flies far
  and fast to forage.
- **Eats:** adults drink sap, soft fruit and honey (they can't digest solids); the young are fed honeybees, other
  hornets and wasps, mantises and big moths.
- **Breeds:** an underground nest with several combs; daughter colonies when thriving.
- **Hunts:** the raid, in three real phases: a scout hunts single bees and marks the hive with scent; then a group of
  hornets comes for the slaughter — fewer than fifty can kill a hive of tens of thousands in hours; then they occupy
  the hive and carry off the brood.
- **With you:** it clicks its jaws as a warning; its sting is dangerous. During the slaughter the hornets don't fight
  back (real), which is the moment to strike.
- **On the farm:** the far-ring beekeeper's enemy, and why the Asian honey bee matters there (P21).
- **Signature:** the scout you must stop before it brings the raid.
- **To build:** the raid (a scout's scent mark on a hive, then the group); the slaughter and occupation; its own
  underground nest.

**Lenses:** Real biology — the three-phase raid, the scent mark, the jaw click (facts A). Picture the moment — a lone
hornet hovering at your hive door, and the choice to chase it before it flies home. **Cost and risk:** the raid is
the largest new piece among the wasps; it builds on the existing nest-defence and hunting code.

### P17. Tarantula hawk (Pepsis grossa) — the wasp that hunts tarantulas
*Spider Vale East · at dusk and dawn · new.*
- **Lives and moves:** a huge, blue-black wasp with rust-red wings, flying low over the ground; the males perch on
  high points watching for females (real "hill-topping").
- **Eats:** adults drink nectar, milkweed among their favourites; its young eat one paralysed tarantula alive.
- **Breeds:** a female finds a tarantula, stings it still, drags it into a burrow, lays one egg on it and seals the
  burrow (real).
- **Hunts:** tarantulas only — in the game, the Goliath tarantula of the same vale, so it keeps the vale's biggest
  spider in check.
- **With you:** docile; it stings only if handled or trapped, and its sting ranks among the most painful of any insect
  but short and not dangerous — in the game a brief stun, little damage.
- **On the farm:** a check on tarantulas.
- **Signature:** a wasp dragging a spider many times its weight across the ground.
- **To build:** the parasite block (a paralysed tarantula dragged to a burrow); milkweed in Spider Vale East for its
  nectar.

**Lenses:** Real biology — every step is sourced (facts A). Picture the moment — a rust-winged wasp hauling a
Goliath tarantula past your boots. **Cost and risk:** shares the parasite block with the decapitating fly.

### P18. Honeybee (the western honey bee, Apis mellifera) — where the beekeeping ladder starts
*Village hives, Bee Meadow (wild hives and Maren's farm) · by day · in the prototype now, to be redone.*
- **Lives and moves:** a colony of a queen, tens of thousands of workers and drones on wax combs in a hollow tree
  or a hive box; foragers range out to flowers and back; guards at the entrance check who comes in.
- **Eats:** nectar (made into honey) and pollen; the young get royal jelly, then pollen and nectar.
- **Breeds:** the colony splits by swarming: the old queen leaves with part of the workers and the swarm moves
  into an empty box or hollow (built — this is how an apiary comes alive).
- **With you:** stings only to defend the hive; a stinging worker usually dies (real); smoke calms the hive, and a
  swarm hanging in a cluster is calm because it has no home to defend (real).
- **On the farm:** honey, honeycomb, wax, pollen and royal jelly (the item rows); pollination for crops.
- **Signature:** the swarm — a humming cluster on a branch that you can coax into your box — and the waggle dance at
  the hive door (display only).
- **To build:** visible guards; robbing by yellowjackets and the death's-head moth; its own nest picture per bee
  species.

**Lenses:** Real biology — swarming, guards, the calm swarm, the dying sting (facts A). Fit — the ladder's first step
(D80). **Cost and risk:** small; most of it is built.

### P19. Killer bee (the Africanized honey bee) — the dangerous step up
*Locust Farmland, Scorpion Rocks · by day · new (D79, D80).*
- **Lives and moves:** a honeybee colony with a short temper; more often in ground cavities and rock crevices than
  honeybees; it swarms more often and abandons a hive when food runs short.
- **Eats:** as the honeybee, but it gathers more pollen and forages farther in dry country.
- **With you:** a larger alarm zone, three to four times the defenders, a chase of up to 400 m and about ten times
  the stings (real); a small visual tell such as darker bands, since real ones look the same as honeybees. Needs
  the stronger smoker.
- **On the farm:** a real upgrade: more honey per hive and better resistance to mites and disease. A keeper tames a
  hive by requeening it with a calm queen, as real beekeepers do; the hive calms as the new queen's workers replace
  the old.
- **Signature:** requeening — taming a dangerous hive over time.
- **To build:** the bigger alarm and longer chase (numbers on the existing defence); absconding; requeening (a queen
  item placed in a hive, then a gradual change).

**Lenses:** Real biology — every figure is from the sources (facts A). Fit — your dangerous step up (D80). **Cost and
risk:** requeening is new; the rest is tuning.

### P20. Bumblebee (the buff-tailed bumblebee, Bombus terrestris) — the greenhouse bee
*Bee Meadow, Hilltop Meadow · by day, and in cool weather when honeybees stay home · new (accepted, D81).*
- **Lives and moves:** a small colony of a few hundred, underground in an old hollow or in a nest box (real ones use old
  rodent burrows, gone in 2126); it warms up by shivering,
  so it flies on cool, damp days when honeybees stay in.
- **Eats:** nectar and pollen from the widest range of flowers of any bumblebee.
- **Breeds:** a queen starts a colony alone; in the game a queen founds her colony in a bumblebee nest box (the item
  row).
- **With you:** gentle; it stings only if its nest is disturbed or it's hurt, and it can sting more than once.
- **On the farm:** buzz pollination — it shakes pollen out of tomato flowers, which other bees can't, so a nest box
  in a glass greenhouse makes the tomatoes there give more; little honey, since it stores only a few days' food.
- **Signature:** the bee that works the greenhouse and the rainy days.
- **To build:** the nest box; the cool-weather routine; the tomato pollination bonus.

**Lenses:** Real biology — buzz pollination, cool-weather flight, small stores (facts A). Picture the moment — a grey
morning, honeybees indoors, bumblebees droning in the greenhouse. **Cost and risk:** small.

### P21. Asian honey bee (Apis cerana) — the hive that survives the giant hornets (proposed third step)
*Millipede Forest · by day · new, open (D82).*
- **Lives and moves:** a smaller colony (several thousand workers) in a small cavity or hive box; less likely to
  sting than the honeybee (real).
- **Eats:** nectar and pollen; it keeps a third of its nectar as honey for lean times.
- **Breeds:** swarming, as the honeybee; it abandons a hive more readily when food runs short, so a neglected hive can
  empty.
- **With you:** gentle; smoke calms it.
- **On the farm:** the one hive that holds out where the giant hornets raid: when a hornet attacks, waves of wing
  shimmering ripple across the comb, and about 500 bees ball round the hornet and heat it to 47 °C, just below what
  kills the bees themselves (real). It grooms off the mites that trouble other bees.
- **Signature:** the heat-ball.
- **To build:** the defence against a raid (a hornet in the ball dies); absconding.

**Lenses:** Real biology — heat-balling, shimmering, absconding (facts A). Fit — a hive bee, as you asked (D81,
D82). **Cost and risk:** small once the giant hornet's raid exists.

### P22. Black ants (the black garden ant, Lasius niger) — the trail you can redirect
*Ant Tunnels, Ant Colony; foraging into the Bee Meadow and the Mining Camp · day and night · in the prototype now
(workers and scouts), to be redone.*
- **Lives and moves:** one queen in a deep chamber, thousands of workers. Scouts range out; when one finds food it
  carries a load home, marking the way, and workers follow the scent in files; trails strengthen with use and fade
  when the food runs out. They roof their busiest trails with earth tunnels (real).
- **Castes:** workers; scouts; warriors — older, bigger workers that stay by the queen and the nest mouths (real
  black garden ants have no soldier caste, decided as warriors in D79); the queen; and, in time, winged queens and
  males that leave on a mating flight on warm afternoons and found new colonies (real).
- **Eats:** nectar, fruit, carcasses and small bugs (with aphids cut, as the lineup has it).
- **With you:** workers ignore you; touch the nest and the warriors bite and squirt formic acid (real — no sting).
- **On the farm:** a clean-up crew for carcasses; a colony to keep, read and lead.
- **Signature:** the trail you can redirect: tap a few ants with the bug stick and they follow you while the column
  carries on; bring them to food and a new trail grows (P4).
- **To build:** the trail grid with per-ant following; the tap and follow; the formic-acid spray; mating flights;
  earth roofs over busy trails (display).

**Lenses:** Real biology — trail scent laid by successful foragers, no soldiers, formic acid, mating flights (facts A).
Picture the moment — your example: five ants leaving the line to follow your stick. **Cost and risk:** the largest
ant piece is the per-ant trail; it is the first block built (architecture doc, §4).

### P23. Fire ants (the red imported fire ant, Solenopsis invicta) — the mound that boils over
*Deadly Ants outpost and core; foraging up into the Shallow Swamp (decided) · by day on warm ground · new.*
- **Lives and moves:** a colony of hundreds of thousands under a mound with no entrance you can see; tunnels run
  metres out from it, and foragers spread from their ends.
- **Castes:** small workers, major workers (up to a third of the colony and four times heavier — the warriors), the
  queen, and winged queens and males.
- **Eats:** almost anything: flies, beetles, crickets, millipedes, centipedes, seeds, nectar, carcasses; it piles its
  waste outside the mound.
- **Breeds:** a queen lays hundreds of eggs a day; mating flights in warm, humid, calm weather found new mounds.
- **With you:** touch the mound and it boils over; each ant grips with its jaws and stings again and again, leaving a
  burning blister — in the game a lasting burn that a remedy treats. A forager that finds rich food brings a crowd
  within half an hour.
- **Hazards:** after heavy rain the colony links into a floating raft with the queen inside — more aggressive and
  dangerous to touch (real).
- **On the farm:** nothing to keep; an enemy to weaken with the ant-decapitating fly (P12) and fire resistance.
- **Signature:** the boiling mound, and the living raft on flood water.
- **To build:** the mound (an ant nest of its own); the recruitment rush; the burn; rafts after heavy rain.

**Lenses:** Real biology — the hidden entrance, the majors, the raft, the recruitment rush (facts A). Picture the
moment — a red raft turning slowly on brown floodwater. **Cost and risk:** rafts need the water block; the rest
reuses the black ants' work.

### P24. Garden centipede (the stone centipede, Lithobius forficatus) — the village's first fight
*Village, the north-east woods' logs and stones · at night · in the prototype now, to be redone.*
- **Lives and moves:** under stones, logs and bark by day, out at night; it runs very fast for cover when uncovered
  (real).
- **Eats:** insects, spiders and flies, killed with venom from its front claws (real; the slugs and worms it also eats
  are gone).
- **Breeds:** eggs laid one at a time on the ground; the young add legs as they grow (real); it lives five or six
  years (real).
- **With you:** the game's first real fight — it lunges (the built lunge). Its real kind is harmless to people and too
  small to break the skin, a fact for its description. Its real defence is a gem: it raises its last legs and flings
  sticky droplets that string into threads and glue an attacker (real) — in the game a short sticky slow on you.
- **On the farm:** a check on flies near the woods; carcass for materials.
- **Signature:** the sticky-thread defence — it glues what attacks it.
- **To build:** breeding under stones and logs (it has no breeding place today); the sticky slow (defence block);
  prey beyond flies.

**Lenses:** Real biology — night hunting, fast retreat, the telopod threads (facts A; the "lunges at anything warm"
line is the game's, not the animal's). **Cost and risk:** small.

### P25. Tiger centipede (Scolopendra polymorpha) — the banded night hunter by the ants
*Mining Camp (D21's cave centipede), Ant Colony seam, Centipede Cavern's upper halls · at night, in cool damp ·
in the prototype now, to be redone.*
- **Lives and moves:** under rocks, in burrows and rotting logs; it comes out only when it's cool and damp, and stays
  dug in otherwise (real).
- **Eats:** insects and other bugs (real for its genus) — in the game the ants at the colony's edge, the insects at
  hand (the sources don't confirm ants specifically).
- **Breeds:** the mother guards her eggs, curled round them (real for its family).
- **With you:** a stronger lunge than the garden centipede. Its venom is real and painful; after a big bite the venom's
  volume mostly comes back in two days, but its strength takes months (real) — in the game, one that has just bitten
  hits a little weaker for a while.
- **On the farm:** carcass for venom and chitin.
- **Signature:** the brooding mother curled round her eggs under a stone — and the weaker second bite.
- **To build:** breeding with a brooding mother (life-stage block); cool-and-damp routine; the venom recovery.

**Lenses:** Real biology — burrows, damp nights, the venom refill numbers (facts A; its natural history sources are
thin). Fit — the centipedes that live by the ants (D79). **Cost and risk:** small.

### P26. Giant centipede (the Amazonian giant, Scolopendra gigantea) — the one on the ceiling
*Centipede Cavern's depths, Millipede Forest, Spider Vale West · at night · in the prototype now, to be redone.*
- **Lives and moves:** the world's largest centipede, over 30 cm (real); in dark, damp places — leaf litter, rotten
  wood, caves (real).
- **Eats:** big insects, spiders, millipedes, scorpions and tarantulas (real). Real ones climb cave ceilings and catch
  bats in flight, holding on with a few legs (real) — the bats are gone, so in the game it takes big flying bugs that
  pass below.
- **Breeds:** the female broods her eggs until the young can feed themselves (real); it lives about ten years (real).
- **With you:** dangerous: a bite strong enough to wound a person, and one killed a child (real). In the cavern it hangs
  from the ceiling and drops on what passes below — look up.
- **On the farm:** Centipede Fang and venom; its boss form is an old mother curled round her eggs (the item rows).
- **Signature:** the ceiling ambush.
- **To build:** hanging from the ceiling and dropping (ambush block); brooding; prey beyond flies.

**Lenses:** Real biology — size, the ceiling hunt, brooding, the danger (facts A). Picture the moment — your torch
finds a shape on the cave roof. **Cost and risk:** the ceiling drop is shared with the cave spider.

### P27. Garden millipede (the American giant millipede, Narceus americanus) — the slow recycler
*Village woods, Butterfly Fields' edge, the forests · at night · in the prototype now, to be redone.*
- **Lives and moves:** in and under rotting logs, out at night; it digs in when the surface dries (real).
- **Eats:** rotting wood and leaf litter; given the choice it prefers fresh fruit (real).
- **Breeds:** a single egg in a nest of chewed litter, with the mother wrapped round it for several weeks (real); it
  lives up to eleven years (real).
- **With you:** harmless if left alone; when threatened it curls up or oozes a liquid that stains the skin brown and
  stings the eyes (real) — in the game a short sting if you grab it bare-handed.
- **On the farm:** the leaf-litter recycler; not food.
- **Signature:** the curled spiral you can pick up — carefully.
- **To build:** curling up (defence block); the single egg and brooding mother.

**Lenses:** Real biology — single-egg nests, curling, the brown "burn" (facts A, a single source). **Cost and risk:**
small.

### P28. Giant African millipede (Archispirostreptus gigas) — the armoured one
*Millipede Forest, Mining Camp (D21's tougher cave millipede) · new.*
- **Lives and moves:** one of the largest millipedes, up to 33 cm with about 256 legs (real); docile (real).
- **Eats:** decaying plants (real for millipedes).
- **Breeds:** eggs on moist ground (real for millipedes); it lives seven to ten years (real).
- **With you:** it curls into a tight spiral showing only its shell (real) and oozes a liquid from pores along its body
  that harms the eyes (real) — in the game a short spray when struck, so keep your distance or wear goggles (the
  spray is the game's; real ones ooze).
- **On the farm:** small mites ride on its shell and clean it (real); its plates for armour (the item rows).
- **Signature:** the hard spiral that a weapon glances off.
- **To build:** curling (defence block) with a tougher shell; the spray.

**Lenses:** Real biology — size, the spiral, the secretion, the cleaning mites (facts A; thin sources). **Cost and
risk:** small.

### P29. Shocking pink dragon millipede (Desmoxytes purpurosea) — the poisonous one
*Deep in the Millipede Forest · comes out in numbers after rain · new.*
- **Lives and moves:** vivid pink and spiny, out in the open on leaf litter; it appears in large numbers after rain
  (real).
- **Eats:** decaying plants (real for millipedes).
- **With you:** it makes hydrogen cyanide and smells of almonds; the colour is the warning (real). In the game a struck
  one leaves a small poison cloud (the game's; the sources say only that it makes the cyanide).
- **On the farm:** a poison ingredient (my proposal) and a specimen.
- **Signature:** the rain march — after a shower the forest floor turns pink.
- **To build:** the rain routine (routine block); the poison cloud (defence block).

**Lenses:** Real biology — the cyanide, the warning colour, the rain appearance (facts A; very thin sources). Picture
the moment — rain stops, and pink spines are everywhere. **Cost and risk:** small.

### P30. Forest scorpion (the Asian forest scorpion, Heterometrus spinifer) — big claws, mild sting
*Wasp Thicket, under logs in the damp woods · at night · new.*
- **Lives and moves:** big, black and shiny (10–12 cm); it digs a burrow and hides by day, waiting at the mouth at night
  (real).
- **Eats:** insects — crickets, locusts' kin and the like (real).
- **Breeds:** live young that ride on the mother's back until their first moult (real for scorpions); some of its genus
  breed without males (real).
- **With you:** it fights with its big claws more than its tail (real) — in the game a pinch that holds you briefly, the
  sting only if you struggle (scorpions really save the sting for big prey). Its sting hurts badly but isn't dangerous
  (real). Glows blue-green under ultraviolet light (real for scorpions).
- **On the farm:** Scorpion Shell from its carcass (the item rows).
- **Signature:** the big-claw grab — the scorpion that holds, where the desert one kills.
- **To build:** the burrow ambush with an emerge warning (ambush block, from the July design); the grab-then-sting
  (combat).

**Lenses:** Real biology — claws before sting, burrows, carried young, the glow (facts A). Fit — your woodland scorpion
(D79): big claws, weak sting, the pair's rule of thumb. **Cost and risk:** the grab is new; the July scorpion design
covers it.

### P31. Fat-tailed scorpion (the yellow fat-tailed scorpion, Androctonus australis) — the deadly one
*Scorpion Rocks · at night · new.*
- **Lives and moves:** thin claws and a fat tail; hides in crevices and dark, damp spots by day (real); its shell is
  covered in tiny bumps that resist blowing sand (real).
- **Eats:** insects, and anything that moves and is smaller than itself (real; the small lizards it also takes are
  gone); it eats its own kind (real).
- **Breeds:** live young carried on the mother's back (real for scorpions) — the boss form is a big mother carrying
  hers (the item rows).
- **With you:** one of the world's most dangerous scorpions (real): its sting needs antivenom. It crushes with its claws
  and stings to paralyse (real). Glows under ultraviolet light, so an ultraviolet lantern shows where they wait.
- **On the farm:** Scorpion Venom and Shell (the item rows).
- **Signature:** thin claws mean deadly venom — the rule of thumb the two scorpions teach.
- **To build:** the burrow-and-crevice ambush; venom that needs antivenom.

**Lenses:** Real biology — danger, crevices, cannibalism, the bumpy shell (facts A). Fit — your dry-zone scorpion (D79)
and the rocky zone you pictured. **Cost and risk:** small once the forest scorpion exists.

### P32. Blue dasher (Pachydiplax longipennis) — the pond's fly catcher
*Village (the west side's water), Bee Meadow river · by day · in the prototype now (the dragonfly), to be redone.*
- **Lives and moves:** a sit-and-wait hunter: it perches still on a reed and darts out at prey, then returns; males hold
  territories fiercely and point their tails at the sky (real); at night they roost in trees (real).
- **Eats:** nearly any small flying insect — flies, gnats, mosquitoes, small moths — hundreds a day (real). The
  prototype has it hunt the village wasps; no source says blue dashers eat wasps, so I propose it hunts flies and other
  small fliers instead.
- **Breeds:** eggs in the water; the young live in the pond hunting other water bugs' young (real) — the reedy pond is
  its nursery (today it never breeds).
- **With you:** harmless; a fast, prized catch.
- **On the farm:** free fly control around water.
- **Signature:** the perch-and-dart — a dragonfly on a reed tip, gone, back again.
- **To build:** perch-and-sally hunting (the July design); breeding in the pond (water block); prey changed from wasps
  to flies.

**Lenses:** Real biology — sit-and-wait hunting, territories, the tail-up pose, roosting in trees (facts A). Honesty —
the wasp-hunting was the prototype's, not the animal's. **Cost and risk:** small, plus the water block.

### P33. Emperor dragonfly (Anax imperator) — the butterfly hawk
*Butterfly Fields, both Swamps · by day · new.*
- **Lives and moves:** big (about 8 cm, wings 10 cm), it rarely lands and eats its prey in flight (real); males are
  territorial (real).
- **Eats:** butterflies, other dragonflies and damselflies, caught high in the air (real; the tadpoles it also takes are
  gone).
- **Breeds:** the female lays alone into floating water plants in large, well-planted ponds and slow rivers (real); the
  young are fierce underwater hunters (real).
- **With you:** harmless.
- **On the farm:** a threat to a butterfly farm and to the smaller dragonflies.
- **Signature:** the hawk that never lands.
- **To build:** in-flight hunting of butterflies (a hunt in the air); breeding ponds (water block) — the Butterfly
  Fields need one.

**Lenses:** Real biology — prey, flight, egg-laying in floating plants (facts A). **Cost and risk:** the water block.

### P34. Dragonhunter (Hagenius brevistylus) — the dragonfly that eats dragonflies
*The surface river, past the Butterfly Fields and the Millipede Forest (moved from the underground, a correction) ·
by day · new.*
- **Lives and moves:** a big black-and-yellow dragonfly (about 8.4 cm) with green eyes; it ambushes other dragonflies
  from above (real).
- **Eats:** other dragonflies — darners like the emperor — and monarch butterflies (real).
- **Breeds:** its young are flat, slow, camouflaged hunters among bark and leaf litter at the stream's edge (real).
- **With you:** harmless.
- **On the farm:** a danger to a dragonfly or butterfly collection near the river.
- **Signature:** the strike from above on another dragonfly.
- **To build:** in-flight hunting of dragonflies; its young along the river (water block).

**Lenses:** Real biology — it lives on streams (facts A; its bug lineup's "deep river" put it underground, where a sight
hunter can't live). **Cost and risk:** small.

### P35. Meadow butterfly (the queen butterfly, Danaus gilippus — name open) — the village butterfly
*Village meadows, Bee Meadow, Butterfly Fields · by day · in the prototype now (the meadow butterfly), to be redone.*
- **Lives and moves:** gliding, curious; males patrol all day for females (real).
- **Eats:** flower nectar and rotting fruit (real); its caterpillars eat milkweed (real).
- **Breeds:** the female tests a leaf with her feet, then lays single eggs on milkweed leaves, stems and buds (real);
  caterpillars, chrysalis and butterfly on the plant (built — the milkweed nursery, D38).
- **With you:** curious; it drifts near you (built).
- **On the farm:** the butterfly farm's first species; it is mildly poisonous, as poisonous as its milkweed makes it
  (real), so only some hunters take it.
- **Signature:** the milkweed nursery you can tend — and its real name, still yours to accept (my suggestion is the
  queen, darker and plainer than a monarch, the look you wanted).
- **To build:** mostly built; the patrolling flight and the poison reading from its plant are new.

**Lenses:** Real biology — milkweed hosts, leaf-testing, the food-plant poison (facts A, a single source). Fit — the
cartoonish milkweed butterfly you wanted (2026-06-23). **Cost and risk:** small.

### P36. Monarch (Danaus plexippus) — the poisonous cluster
*Butterfly Fields · by day · new.*
- **Lives and moves:** orange and black, strong fliers; at night they roost together in clusters, from a few to
  thousands, on trees (real for travelling monarchs).
- **Eats:** nectar from milkweeds, sunflowers, asters and goldenrods; it sips water and salts from damp ground (real).
  Its caterpillars eat milkweed only, and big ones cut a leaf's vein to drain the sticky sap before eating (real).
- **Breeds:** single eggs under young milkweed leaves; egg to butterfly in as little as 25 days (real); a caterpillar
  may walk up to 10 m to find a place to pupate (real).
- **With you:** harmless.
- **On the farm:** a prize; poisonous, with most of the poison in its wings (real), so hunters leave it — but the paper
  wasp takes its caterpillars and the dragonhunter takes adults (real).
- **Signature:** the roost — a tree hung with monarchs at dusk.
- **To build:** clustering at night (a resting group); milkweed nursery (built for the meadow butterfly); the poison
  reading for hunters.

**Lenses:** Real biology — clusters, milkweed-only young, the poison in the wings, its real enemies on our roster (facts
A). Picture the moment — a tree turning orange at dusk. **Cost and risk:** small.

### P37. Purple emperor (Apatura iris) — the treetop butterfly you lure down
*Wasp Thicket, high in the oaks · by day · new.*
- **Lives and moves:** lives high in the treetops; males gather at the same "master trees" and defend treetop
  territories (real). The male's purple shows only at some angles to the sun (real).
- **Eats:** not flowers: sap oozing from oaks, rot and carcasses, and salts — males even drink sweat from people
  watching them (real). Its caterpillars eat willows (sallows), not oaks (real), so the Thicket needs willow scrub.
- **Breeds:** single eggs on willow leaves in half-shade; the caterpillar takes almost a year, growing two horns (real).
- **With you:** a male may land on you to drink your sweat (real).
- **On the farm:** a prize catch: old collectors lured males down with carcasses and a long net (real) — in the game a
  dead bug as bait under the master trees.
- **Signature:** the butterfly you can't chase but can lure.
- **To build:** treetop life and coming down to bait; landing on a still player; willow scrub in the Thicket for its
  young.

**Lenses:** Real biology — master trees, the angle-dependent purple, carrion bait, sweat-drinking (facts A). Picture the
moment — standing still under an oak while a purple butterfly settles on your arm. **Cost and risk:** small.

### P38. Luna moth (Actias luna) — the pale night visitor
*Butterfly Fields, Wasp Thicket · at night · new.*
- **Lives and moves:** big, pale-green moths with long tails, out at night, and like many moths drawn to lamps; by day
  they sit still on leaves and pass for leaves (real).
- **Eats:** the adult never eats and lives about a week (real); the caterpillars eat the leaves of walnut, hickory,
  sweetgum, white birch, persimmon and sumac (real; they do very poorly on oak and cherry).
- **Breeds:** eggs on the undersides of host-tree leaves; the caterpillars grow for six or seven weeks, then go down
  to spin a thin cocoon wrapped in dead leaves on the ground (real).
- **With you:** harmless; a prize night catch. A disturbed caterpillar clicks and spits up its gut (real).
- **On the farm:** a specimen and a sight; it gives no silk (the silk moth does).
- **Signature:** a moth that only lives a week — so every one is a short-lived find — and comes to your lamp.
- **To build:** lamp attraction (lights block); caterpillars on host trees (life-stage block); host trees in its
  zones.

**Lenses:** Real biology — the non-eating week-long adult, host trees, leaf-wrapped cocoons (facts B). Picture the
moment — a lamp at midnight and a pale green moth the size of your hand. **Cost and risk:** small.

### P39. Death's-head hawkmoth (Acherontia atropos) — the honey thief
*Bee Meadow · late at night · new.*
- **Lives and moves:** a heavy, fast moth with a skull-like mark, flying late at night.
- **Eats:** nectar and honey: it walks into honeybee hives undisturbed because it smells like the bees, and drinks
  the honey (real); its caterpillars eat nightshade-family plants, potato above all — in the game the player's
  tomatoes and eggplants and wild nightshades.
- **Breeds:** eggs singly under leaves of those plants; the caterpillar grows huge (up to about 12 cm) and pupates in
  a chamber underground (real).
- **With you:** harmless. Handle it and it squeaks loudly and flashes its striped abdomen (real).
- **On the farm:** a honey thief at the hive and a tomato pest in the garden — two reasons to watch the night.
- **Signature:** the squeak — a moth that talks back — and the hive raid.
- **To build:** the night hive raid (it enters a hive and takes honey, unharmed by the guards); caterpillars on
  tomato-family plants (life-stage block, a crop host).

**Lenses:** Real biology — scent mimicry in the hive, the squeak, nightshade hosts (facts B; tomato and eggplant are
nightshades, though the sources name potato). Picture the moment — finding a hive's honey low in the morning, and a
squeak from the hive door at night. **Cost and risk:** the hive raid is new.

### P40. Silk moth (Bombyx mori, the silkworm) — the farm moth
*The player's farm, on a mulberry tree · new.*
- **Lives and moves:** a moth that can't fly and doesn't exist in the wild; the adult doesn't eat (real).
- **Eats:** its caterpillars, the silkworms, eat mulberry leaves and almost nothing else (real).
- **Breeds:** the weaver sells the first eggs (my proposal); after that, a player lets some cocoons hatch, the moths
  pair (they need people to bring them together, real) and the female lays a few hundred eggs.
- **With you:** harmless; the moths flutter but can't fly away.
- **On the farm:** silk: each cocoon is a single thread hundreds of metres long (real); kept cocoons give the next
  generation, taken cocoons give silk.
- **Signature:** the choice at every cocoon — silk now, or moths for the next batch.
- **To build:** the mulberry tree, the eggs, the silkworms and cocoons (life-stage block, the item rows).

**Lenses:** Real biology — domesticated, flightless, mulberry-only, single-thread cocoons (facts B). Fit — livestock
in the truest sense. **Cost and risk:** small; the item rows exist.

### P41. Carrion beetle (a burying beetle, Nicrophorus vespilloides) — the undertaker
*Village and anywhere carcasses fall · often at night, like carrion beetles generally · in the prototype now, to be
redone.*
- **Lives and moves:** it smells a carcass from far off with its clubbed antennae (real) and flies or walks to it.
- **Eats:** carcasses — in 2126 dead bugs, since the small birds and rodents real ones bury are gone (the stand-in).
- **Breeds:** a pair buries a carcass — it sinks into the ground over a few hours — and both parents raise their
  grubs on it, feeding them by mouth (real). Mites riding on the beetles eat fly eggs on the carcass (real), a link
  to the fly farm.
- **With you:** harmless; it ignores you.
- **On the farm:** the clean-up crew: carcasses vanish into the ground instead of feeding flies; its grubs are bug
  feed (the item rows).
- **Signature:** the burial — a carcass sinking slowly into the soil with two beetles under it.
- **To build:** the burial (a carcass becomes a brood in the ground; the parasite and burial block); the mites'
  effect on fly breeding at that carcass.

**Lenses:** Real biology — burial, two-parent care, the mites (facts B); the dead-bug stand-in is named. Picture the
moment — a dead wasp that wasn't there the next morning, and a little mound of soil. **Cost and risk:** the burial
is new.

### P42. Cave beetle (Leptodirus hochenwartii) — the blind beetle of cold caves
*Mining Camp, Centipede Cavern, the cold caves · no day or night · new (D21).*
- **Lives and moves:** small, blind, wingless and pale, with long legs and a domed back that holds moist air; it
  feels its way by touch and senses the damp with its antennae (real).
- **Eats:** what seeping water carries into the cave and dead cave bugs (real ones also eat bat droppings, gone in
  2126 — the stand-in).
- **Breeds:** a few big eggs; the young don't eat before they change (real) — slow to breed.
- **With you:** harmless; it feels the ground shake and shies away.
- **On the farm:** a specimen, and food for cave spiders.
- **Signature:** found where water seeps down cave walls — follow the wet rock.
- **To build:** seeping-water spots on cave walls as its food; slow breeding.

**Lenses:** Real biology — blind, wingless, damp-sensing, slow-breeding (facts B; the first cave beetle described,
1831). **Cost and risk:** small.

### P43. Rhinoceros beetle (the Hercules beetle, Dynastes hercules) — the horned wrestler
*Millipede Forest (its boss form) · at night · new.*
- **Lives and moves:** the longest beetle in the world (males to 17 cm with the horn, real); by day it hides in leaf
  litter, at night it forages.
- **Eats:** fallen, rotting fruit and tree sap, carving bark to reach it; its grubs eat rotting wood for up to two
  years (real).
- **Breeds:** eggs on or in dead wood; huge grubs in fallen trees.
- **With you:** males fight each other by grabbing a rival between the two horns, lifting it and throwing it (real); it
  warns with a huffing sound (real). The forest's boss is the biggest of its kind (overview P13): it throws a player the
  same way.
- **On the farm:** its horn makes the Beetle-Horn Maul (decided); grubs and a big steak.
- **Signature:** the lift-and-throw, and the huff before it.
- **To build:** the grab-and-throw attack (new combat move); grubs in fallen trees (life-stage block); its wing
  cases changing colour with humidity (real; display only).

**Lenses:** Real biology — the throw, the huff, the grubs (facts B). Fit — your horned beetle (D75, D79). **Cost and
risk:** a new throw move.

### P44. Stag beetle (Lucanus cervus) — the antlered jousters of the oak woods
*Wasp Thicket woods · at dusk · new.*
- **Lives and moves:** males fly at sunset looking for females (real); adults live only a few weeks.
- **Eats:** adults sip sap and fruit juice if anything; the grubs eat rotting wood for three to seven years (real).
- **Breeds:** about 30 eggs in decaying wood underground; the grubs talk to each other by scraping their legs (real).
- **With you:** males wrestle on logs, trying to throw each other off; the males' jaws can't hurt you, but a
  female's bite pinches (real).
- **On the farm:** its grubs, found in dead wood, are the item rows' grubs (my proposal: roasted in the ashes or
  rendered into fat); the jaw makes the Mandible Sickle.
- **Signature:** the jousting on a log at sunset.
- **To build:** grubs in dead trees and fallen logs (life-stage block); the wrestling (two bugs, display).

**Lenses:** Real biology — the jousts, the long-lived grubs, the dusk flights (facts B). Picture the moment — two
males locked on a mossy log as the light goes. **Cost and risk:** small.

### P45. Colorado beetle (Leptinotarsa decemlineata) — the crop stripper
*Locust Farmland · by day · new.*
- **Lives and moves:** a striped beetle that walks and flies from field to field.
- **Eats:** leaves of the tomato family — potato, eggplant, tomato and wild nightshade; each larva eats about 40 cm²
  of leaf in its life (real).
- **Breeds:** yellow-orange egg clusters under the leaves; the larvae drop to the soil to pupate; egg to adult in
  as little as three weeks, so numbers build quickly (real).
- **With you:** harmless.
- **On the farm:** a true crop pest: it strips tomatoes and eggplants; the answers are its enemies (in the game the
  mantis), handpicking and squashing its egg clusters, trap crops (accepted, overview P8), and crop rotation.
- **Signature:** a race against its generations — clear the egg clusters before they hatch.
- **To build:** crop damage on the tomato family (crops feed bugs, D62); egg clusters under leaves (life-stage
  block).

**Lenses:** Real biology — the hosts, the egg clusters, the fast generations (facts B). Fit — the western farm town's
pest. **Cost and risk:** crop damage is a small new link.

### P46. Bombardier beetle (Brachinus crepitans) — the boiling spray
*Hilltop Meadow, under stones · at night · new.*
- **Lives and moves:** a small ground beetle under stones by day, out hunting at night; several often shelter
  together (real for bombardier beetles).
- **Eats:** other small bugs; its young live on the pupae of other beetles (real).
- **Breeds:** little is known in life; in the game, eggs in the soil under stones.
- **With you:** lift its stone or grab it and it fires a boiling, foul spray with a pop — about 20 shots before it
  runs dry (real). In the game a short-range spray that burns a little, then a few seconds' wait before the next.
- **On the farm:** a specimen; maybe a chemical ingredient later.
- **Signature:** the pop — the spray you hear before you feel it, and the beetle that runs dry.
- **To build:** the spray (defence block, with a shot count); life under stones (a "lift the stone" interaction).

**Lenses:** Real biology — the chemistry and the 20 shots (facts B; sources are thin at species level). Picture the
moment — lifting a flat stone and getting a pop of hot spray. **Cost and risk:** the spray is the defence block's
first use.

### P47. Cave spider (the European cave spider, Meta menardi) — the drop from the dark
*Lower underground: Centipede Cavern and deeper (D21: not the first Mining Camp) · emerges at dusk · new.*
- **Lives and moves:** shuns light, lives near cave mouths and tunnels; it drops onto prey on a single silk line and
  swings down (real).
- **Eats:** millipedes and centipedes above all (real; the slugs it also eats are gone in 2126).
- **Breeds:** white, tear-shaped egg sacs, 2–3 cm, hung from the cave roof near the entrance, each with a few hundred
  eggs (real) — visible, and a sign the spider is near.
- **With you:** not dangerous; it drops and bites only if you blunder into it. Its young, after a few moults, are
  drawn to light and leave the cave (real) — so spiderlings drift toward your torch.
- **On the farm:** the cave's check on millipedes and centipedes; its silk (Cave Spider Silk) for the stealth outfits.
- **Signature:** the drop on a line, and the white egg sacs on the roof.
- **To build:** the drop from above (ambush block); egg sacs on the cave roof (life-stage block); spiderlings drawn
  to light.

**Lenses:** Real biology — the lasso drop, the egg sacs, light-shy adults and light-seeking young (facts B). Picture
the moment — a white teardrop over the tunnel, and a spider sliding down on a thread. **Cost and risk:** the drop is
new.

### P48. Daddy longlegs (the eastern harvestman, Leiobunum vittatum) — the cluster that bobs
*Mining Camp caves, both Spider Vales, the woods · at night · new.*
- **Lives and moves:** long-legged, harmless; gathers in clusters of thousands (real for its kind) on walls and
  overhangs; when alarmed the whole cluster bobs its bodies to blur them (real).
- **Eats:** small insects, plants, fungi and dead things — a scavenger and omnivore (real; earthworms gone).
- **Breeds:** eggs (the sources don't say where for this species); in the game, in damp ground.
- **With you:** harmless — no venom, no bite (real; not a spider). Grab one and it drops a leg that keeps twitching
  while it escapes (real).
- **On the farm:** a cleaner of small dead things; a specimen.
- **Signature:** the bobbing cluster, and the twitching dropped leg.
- **To build:** clusters (a group that rests together); the dropped-leg decoy (defence block).

**Lenses:** Real biology — clusters, bobbing, leg-dropping, no venom (facts B; species-level sources thin). Picture the
moment — a cave wall that shivers when your torch touches it. **Cost and risk:** small.

### P49. Wolf spider (the Carolina wolf spider, Hogna carolinensis) — the eyes in the torchlight
*Spider Vale West · at night · new.*
- **Lives and moves:** no web: it waits at the mouth of its burrow at night and rushes what comes near, or chases a
  short way (real).
- **Eats:** crickets and locusts' kin and other bugs (real).
- **Breeds:** the mother carries her egg sac on her spinnerets, then about 200 spiderlings on her back (real).
- **With you:** its eyes shine back at a torch (real) — a field of sparks at night. It bites if handled or
  cornered, a mild bite.
- **On the farm:** a check on crickets and locusts; a mother carrying young is the vale's boss form, and gives
  Egg-Sac Silk (the item rows).
- **Signature:** eyeshine — sweep a torch and see where they wait.
- **To build:** burrow ambush (ambush block); eyeshine (display, from the player's light); the mother carrying her
  young (a mother that scatters spiderlings when struck).

**Lenses:** Real biology — burrow ambush, eyeshine, the carried young (facts B). Picture the moment — your torch
sweeping the vale and fifty points of light looking back. **Cost and risk:** small for the base spider; the boss mother
is more.

### P50. Jumping spider (the bold jumping spider, Phidippus audax) — the harmless jumper
*Butterfly Fields, Spider Vale West · by day · new.*
- **Lives and moves:** a small, bold, hairy jumper with big front eyes; it hunts by sight, stalks, ties on a silk
  safety line and leaps; if it misses it climbs back up the line (real). At night it rests in a silk pouch.
- **Eats:** caterpillars, dragonflies, grasshoppers and other spiders (real).
- **Breeds:** a guarded egg sac under bark or stones (real).
- **With you:** it turns to watch you, and flees from anything too big to eat (real); a rare mild bite if handled.
- **On the farm:** pest control on caterpillars; a favourite catch.
- **Signature:** it watches you — the spider that turns its head.
- **To build:** stalk and leap (the centipede lunge reused, from the June design); the watching turn (display).

**Lenses:** Real biology — the safety-line leap, sight hunting, fleeing big animals (facts B). Picture the moment — a
fuzzy spider on a fence post turning to look at you. **Cost and risk:** small (the June design's first spider).

### P51. Brazilian wandering spider (Phoneutria nigriventer) — the vale's real danger
*Spider Vale West · at night · new.*
- **Lives and moves:** no web and no lair: it wanders the ground at night and hides under logs and in crevices by day
  (real).
- **Eats:** crickets, katydids and mantises (real; the frogs, lizards and bats it also takes are gone).
- **Breeds:** a silk egg sac of up to about 1,000 eggs (real).
- **With you:** its warning is a real threat display: it rears up, raises its front legs to show the bands beneath
  and sways (real). Ignore it and it bites; its venom is truly dangerous (real), so the bite needs antivenom.
- **On the farm:** nothing to keep; respect it.
- **Signature:** the swaying threat display — the clearest warning in the game, because the bite is the worst.
- **To build:** night wandering; the threat display as the telegraph (combat); venom that needs antivenom.

**Lenses:** Real biology — wandering, the display, the danger (facts B). Picture the moment — a spider rising on its
hind legs in your torchlight. **Cost and risk:** small.

### P52. Black widow (the southern black widow, Latrodectus mactans) — the tangle in the dark
*Spider Vale East · at night · new.*
- **Lives and moves:** a messy, strong tangle web in a sheltered spot — under stones, in crevices — with a silk
  tunnel where she waits by day (real); at the slightest disturbance she drops and plays dead (real).
- **Eats:** insects, millipedes, centipedes and other spiders caught in the web (real).
- **Breeds:** several pear-shaped egg sacs kept in the web (real).
- **With you:** walk into the web and you're slowed; she bites only if pressed against, but the venom hurts (real) —
  painful, rarely fatal.
- **On the farm:** Black Widow Silk and venom (the item rows).
- **Signature:** the web as a trap for you and your bugs — the vale's hidden hazard.
- **To build:** the web (web block: slows a player, catches small bugs, cut for silk); playing dead.

**Lenses:** Real biology — the tangle web, playing dead, egg sacs, venom (facts B). Picture the moment — a gleam of
silk between two stones, and a black shape in the tunnel behind it. **Cost and risk:** the web block.

### P53. Tarantula (the Goliath tarantula, Theraphosa blondi) — the hissing giant
*Spider Vale East, deep burrows in damp ground · at night · new.*
- **Lives and moves:** a huge tarantula (legs to 30 cm) in a deep burrow; it drags prey back to the burrow to eat
  (real).
- **Eats:** large bugs (real; the worms, frogs and rodents it also eats are gone).
- **Breeds:** an egg sac covered in its own irritating hairs (real); it lives many years.
- **With you:** it hisses by rubbing its legs (real) — the first warning; then it rubs its abdomen and flicks barbed
  hairs that sting the eyes and skin (real) — in the game a short cloud that blurs your view and itches; its bite is
  like a wasp sting (real).
- **On the farm:** Spider Plate and Fried Spider (the item rows; it really is eaten roasted, hairs singed off).
- **Signature:** hiss, then hairs — two warnings before a bite.
- **To build:** burrow ambush (ambush block); the hair cloud (defence block).

**Lenses:** Real biology — burrows, hissing, urticating hairs, its use as food (facts B). Picture the moment — a hiss
from a hole the size of a hand. **Cost and risk:** small.

### P54. Giant huntsman (Heteropoda maxima) — the wall runner
*Spider Vale East's caves · at night · new.*
- **Lives and moves:** the widest spider in the world (legs to 30 cm), a cave dweller; huntsmen run fast, spring as
  they run, walk on walls and ceilings and hide in crevices (real for the family).
- **Eats:** insects and other bugs (real for the family).
- **Breeds:** the female guards her egg sac fiercely (real for the family).
- **With you:** when provoked it rears in a threat display, then bites if you ignore it (real for the family); its
  speed is the danger.
- **On the farm:** Huntsman Fang (the item rows).
- **Signature:** the fastest spider — it runs on the cave walls, not the floor.
- **To build:** wall running (a new movement style along cave walls).

**Lenses:** Real biology — size and cave life (facts B; behaviour is the family's, the species sources are thin).
Picture the moment — something long-legged crossing the cave wall faster than your torch. **Cost and risk:** wall
running is new.

### P55. Marsh mosquito (the house mosquito, Culex pipiens) — the dusk swarm
*Shallow Swamp · at dusk and night · new.*
- **Lives and moves:** mating swarms dance at sunset and sunrise (real); females hunt by the carbon dioxide people
  breathe out (real), weaving toward you.
- **Eats:** nectar; females also bite — in 2126, people, the last warm-blooded animals left (one real form bites
  mainly people).
- **Breeds:** floating rafts of about 200 eggs on still water (real), so sand laid on the marsh stops them, as you
  said (D79); the young need still water with rotting matter in it (real).
- **With you:** a slow, weaving approach you can read and dodge (the July research's "cast-and-surge"); a bite is a
  small hit with an itch.
- **On the farm:** a pest; food for dragonflies and water striders, which eat them and their young (real).
- **Signature:** egg rafts you can see and scrape off still water — the pond keeper's chore.
- **To build:** water life (eggs and young in still water; the water block); sand that stops breeding; the
  weaving approach.

**Lenses:** Real biology — rafts, dusk swarms, carbon-dioxide hunting (facts B). Fit — your sand rule (D79). **Cost and
risk:** the water block.

### P56. Swamp mosquito (the common malaria mosquito, Anopheles quadrimaculatus) — the quiet biter of the deep swamp
*Deep Swamp · at dusk, dawn and night · new (your later-stage mosquito, D79).*
- **Lives and moves:** rests by day in shade — hollow trees, under the stilt walkways — and comes out at dusk; it
  rests with its tail tipped up, unlike the marsh mosquito (real). Most stay near their breeding water (real).
- **Eats:** nectar; the females need blood to lay eggs, and in 2126 that means people. A 2014 study found a related
  malaria mosquito drinking caterpillars' body fluid and living longer for it — so in the game it also feeds on the
  swamp's soft young bugs, a stretch of real behaviour (my proposal).
- **Breeds:** single floating eggs on still, sunlit water with plants; the young lie flat just under the surface
  (real) — sand laid on the marsh stops them too (D79).
- **With you:** your later, lunging and swarming mosquito (D79): the lunge and the swarm are the game's (real ones
  bite quietly); it weaves in on your breath like the marsh mosquito, faster and in numbers.
- **On the farm:** a pest; food for dragonflies and water striders.
- **Signature:** the swarm at dusk over black water, held back only by what you do to its water.
- **To build:** as the marsh mosquito (water block), plus the swarm-and-lunge attack.

**Lenses:** Real biology — resting pose, dusk activity, floating eggs, flat-lying young (facts B); the caterpillar
feeding is the related species' and is labelled as a stretch. Fit — your later-stage danger (D79). **Cost and risk:**
shares the marsh mosquito's work.

### P57. Water strider (the common pond skater, Gerris lacustris) — the ripple reader
*Village lake, Shallow and Deep Swamps · new.*
- **Lives and moves:** skates on the water surface on water-repellent hairs, rowing fast (real); each holds a patch of
  water and warns others off with ripples (real).
- **Eats:** insects that fall on the water, and mosquitoes and their young (real) — it finds them by feeling the
  ripples of a struggling bug (real).
- **Breeds:** eggs glued to underwater stones and stems (real for the family); nymphs skate like small adults.
- **With you:** harmless; it skates away from your shadow.
- **On the farm:** the pond's mosquito control — a pond with striders breeds fewer mosquitoes.
- **Signature:** drop a dead fly on the water and watch the striders race to the ripples.
- **To build:** water-surface movement (the water block); prey found by ripples (a bug that falls on water draws
  them).

**Lenses:** Real biology — ripple hunting, territories, mosquito prey (facts B). Picture the moment — tossing a fly
onto the lake and seeing three striders converge on the rings. **Cost and risk:** the water block.

### P58. Crayfish (the red swamp crayfish, Procambarus clarkii) — the farmed crawfish
*Village lake, both Swamps · at dusk and night · new.*
- **Lives and moves:** hides in its burrow by day and forages at dusk (real); digs burrows down to the water in dry
  spells and can wander across wet ground between waters (real).
- **Eats:** almost anything: water plants, rot, insects, other crayfish and fish (real; the snails and frog spawn it
  also eats are gone).
- **Breeds:** the female carries her eggs and then her young under her tail (real); a generation takes about four
  and a half months (real), fast for its size.
- **With you:** it backs away from you; in the game, a small pinch if you grab it bare-handed.
- **On the farm:** real livestock — farmed in rice fields for centuries (real); caught in the fish trap; the crayfish
  boil. Its burrows weaken banks (real), so a crayfish pond needs watching.
- **Signature:** a mother carrying her young under her tail, and burrows along the bank.
- **To build:** water life (the water block); burrows in banks (a new small habitat object); the fish trap.

**Lenses:** Real biology — burrows, dusk foraging, carried young, farming history (facts B). Fit — the item rows'
crayfish boil and fish trap. **Cost and risk:** the water block.

### P59. River crab (Potamon fluviatile) — the right-handed fighter
*Underground River, shallow and deep · after dark · new.*
- **Lives and moves:** burrows in the banks, small ones under stones; it forages on land near the water and can go
  tens of metres from it (real).
- **Eats:** algae, plant debris, insects and their young, small fish (real; the frogs and snails it also eats are gone).
- **Breeds:** about 200 eggs carried under the female; the young hatch as tiny crabs and ride with their mother for
  two weeks (real). It lives ten to twelve years (real).
- **With you:** aggressive; about nine in ten are right-handed and attack mostly with the bigger right claw (real) —
  watch that claw.
- **On the farm:** caught in the fish trap; eaten since antiquity (real).
- **Signature:** the right claw — a tell you can learn.
- **Honest note:** real river crabs live in streams and rivers, not caves; the underground river is a stretch. Its
  long life and nocturnal habits suit the dark well.
- **To build:** the water block; a claw attack telegraphed from the right.

**Lenses:** Real biology — right-handedness, carried young, land foraging (facts B; thin sources). Fit — the river
crab of the bug lineups. **Cost and risk:** small once the water block exists.

### P60. Praying mantis (the Chinese mantis, Tenodera sinensis) — the still hunter you can keep
*Locust Farmland, the Wasp Thicket's edges · by day · new.*
- **Lives and moves:** sits motionless on plants until prey comes within reach, then snaps out its forelegs (real).
- **Eats:** large insects — hornets, grasshoppers, spiders, caterpillars, bees (real); the biggest mantis in North
  America, up to about 11 cm (real).
- **Breeds:** egg cases the size of a toasted marshmallow, up to 300 eggs each, stuck to twigs (real); the female may
  eat the male (real).
- **With you:** harmless.
- **On the farm:** keep mantises and set their egg cases out against the locusts (D80, the Mantis Egg Case row). In
  life, mantis egg cases are sold to gardeners but don't control pests well — in the game they're a real help, the
  game's choice.
- **Signature:** the strike from stillness — and egg cases you collect and place.
- **To build:** ambush on plants (ambush block); egg cases (life-stage block, the item row).

**Lenses:** Real biology — the strike, the egg cases, the prey (facts B); the pest-control effect is the game's, and
said so. Fit — mantis eggs from your own mantises (D80). **Cost and risk:** the ambush block.

### P61. Orchid mantis (Hymenopus coronatus) — the flower that eats butterflies
*Butterfly Fields · by day · new.*
- **Lives and moves:** pink and white, shaped like an orchid; it climbs to a cluster of flowers and holds still (real).
  It draws more pollinators than real flowers do, and to bees its colour can't be told from the flowers (real).
- **Eats:** bees, flies, crickets, beetles — and in the lab it prefers butterflies and moths (real).
- **Breeds:** its young look like assassin bugs, then turn into flowers as they grow (real); the young glide on their
  petal-shaped legs (real).
- **With you:** harmless; it shifts between pink and brown to match its perch (real).
- **On the farm:** a quiet danger to a butterfly farm and a prize catch.
- **Signature:** the flower that isn't — a bee lands on it and doesn't leave.
- **To build:** ambush as a lure (it draws pollinators the way a flower does; the ambush block).

**Lenses:** Real biology — pollinator deception measured in the field (facts B). Picture the moment — a pink flower
among the clover that moves. **Cost and risk:** the ambush block's lure.

### P62. House cricket (Acheta domesticus) — the farm cricket (a maybe, D80)
*The player's farm; the western town's farm store · mostly at night, like most crickets · new, open.*
- **Lives and moves:** small, fast-breeding, happy in a box of damp bedding.
- **Eats:** almost anything — leaves, fruit, scraps, dead bugs (real).
- **Breeds:** eggs in damp ground; egg to adult in two to three months in warmth (real).
- **With you:** harmless; males sing at night (real).
- **On the farm:** the cricket protein drink and cricket flour — farmed today for food and feed (real).
- **Signature:** the easiest livestock: feed scraps, get protein.
- **To build:** a cricket pen (a farm object); song (sound).

**Lenses:** Real biology — farming and diet (facts B). Fit — the farm cricket you left as a maybe (D80). **Cost and
risk:** small.

### P63. Field cricket (Gryllus campestris) — the singer at his door
*Bee Meadow, Hilltop Meadow, on dry, sunny, short-grass ground · day and early night · new.*
- **Lives and moves:** each male digs a burrow with a little platform at the mouth and sings there, audible 50–200 m
  away (real); females wander. Flightless; it rarely jumps (real).
- **Eats:** leaves and roots, and small soil bugs and carcasses (real).
- **Breeds:** eggs buried singly near the burrow (real).
- **With you:** harmless; in the game it goes quiet and drops into its burrow as you come close. Males defend their
  burrows fiercely against other males, sometimes to the death (real).
- **On the farm:** a specimen; food for wolf spiders.
- **Signature:** find it by its song — the meadow sings, and goes silent around you.
- **To build:** the burrow and song (sound tied to position); going quiet when a player nears.

**Lenses:** Real biology — burrow platforms, singing, fights (facts B). Picture the moment — a hilltop full of song
that hushes in a ring around your feet. **Cost and risk:** small; sound is display only.

### P64. Firefly (the common eastern firefly, Photinus pyralis) — the J of light
*Village meadows at dusk, Butterfly Fields at night · at dusk and night · in the prototype now, to be redone.*
- **Lives and moves:** males fly over long grass at dusk tracing a J, lighting on the upswing, every five or six
  seconds; females answer from the ground a second or two later (real).
- **Eats:** most adults don't eat; the young live in damp soil for one to two years and hunt worms, slugs and snails
  (real) — all gone in 2126, so in the game they hunt soft insect young in the soil, such as fly maggots, which real
  ones also take.
- **Breeds:** about 500 eggs on damp soil; the young glow as a warning (real).
- **With you:** harmless; when grabbed it bleeds a bitter fluid (real), so hunters leave it alone.
- **On the farm:** living light: a jar of fireflies is a lantern (the item rows).
- **Signature:** the flash code — answer it with a lantern and males come to you.
- **To build:** the J-flash (display, from the shared clock); larvae in damp ground eating maggots (the stand-in);
  the answer-a-flash lure (lights block).

**Lenses:** Real biology — the J flight, the timed answer, the bitter blood, the glowing young (facts B). Picture the
moment — dusk over the village meadow, the grass lighting in J's. **Cost and risk:** the lure is new; the glow is
display only.

### P65. Cave glowworm (the New Zealand glowworm, Arachnocampa luminosa) — the starry ceiling
*Mining Camp, Centipede Cavern, a ceiling over the Underground River · always · new (D21).*
- **Lives and moves:** a fly larva in a silk nest on the cave ceiling, hanging up to 30 sticky threads below it; its
  glow lures small flying bugs into the threads (real).
- **Eats:** small flies above all, also moths, mosquitoes, millipedes and spiders that touch the threads (real); in the
  game the cave flies on the wing.
- **Breeds:** eggs in clumps on the cave wall; the larva lives six months to a year; the adult fly can't eat and lives
  three or four days (real).
- **With you:** harmless. Touch it or its threads and its light goes out and it pulls back into its nest (real) — so a
  careless player darkens the cave around them.
- **On the farm:** living light: catch one for a lantern (D21).
- **Signature:** the lights go out where you touch.
- **To build:** a ceiling bug with threads (the web block's sticky lines); its light (lights block); going dark when
  touched.

**Lenses:** Real biology — the snares, the lure, the touch response (facts B). Picture the moment — a cave ceiling like
a night sky, and a dark patch spreading where your shoulder brushed the threads. **Cost and risk:** small.

### P66. Locust (the desert locust, Schistocerca gregaria) — the swarm with a cause
*Locust Farmland, spilling into the zones around it (decided) · solitary ones fly at night, swarms by day · new.*
- **Lives and moves:** two forms of one insect. Solitary locusts are green or beige, avoid each other and fly at night.
  When rain brings a flush of green and they crowd, legs bumping, they change within hours into the swarming form —
  yellow and black, marching in bands as young, then flying in swarms by day (real).
- **Eats:** almost every green plant, about its own weight a day (real) — wheat and the other crops, as decided.
- **Breeds:** egg pods of up to about 150 eggs pushed into bare soil and sealed with foam (real).
- **With you:** no bite; the swarm is the danger to your crops, not to you.
- **On the farm:** a crop disaster and a harvest: people really net and eat them (real); grilled locust legs and the
  protein drink (the item rows).
- **Signature:** you can see it coming: crowding turns them; keeping their numbers down keeps them from crowding — the
  real trigger. Harvesting and mantises are the game's ways to do it (real natural enemies do little, because swarms
  move on).
- **To build:** the crowding switch (swarm-change block); marching bands and flying swarms; egg pods in bare soil.

**Lenses:** Real biology — the phase change, its trigger, the colours, egg pods, night flight of solitary adults (facts
B). Fit — locust swarms eat wheat and aren't bosses (decided). **Cost and risk:** the swarm-change block is the most
striking new mechanic outside the ants.

## To settle later (not in this review)
- Each bug's numbers (speed, damage, breeding rates, caps) — set in the Bug Lab and the zone tuning runs, after its
  behaviour is signed off (overview P10).
- Which species get a boss beyond the ant queens and the Hercules beetle (within overview P13, with each zone's design).
- How dangerous venom is overall, and what the antidotes cost (GDD §07 combat, §11 potions).
- The art for the forty-three new bugs, batch by batch, each paid batch asked for first.

## Sources
- The bug lineups (`docs/gdd/bug_lineups.jsonl`) and the bug list (`docs/gdd/bug_table.jsonl`); decisions D21, D39,
  D79–D82 (`docs/product/economy/DECISIONS.md`).
- Facts per bug, with their sources: `docs/product/investigations/research-2026-10-03/bug-ecology-facts-A.md` and
  `bug-ecology-facts-B.md`.
- How games and biology handle trails, nests, hunting, defences, schedules and herding:
  `docs/product/investigations/research-2026-10-03/bug-mechanics-in-games.md`; the July 2026 per-family research
  (`docs/product/investigations/deep_research_2026-07/bugs/`); the June ants-and-spiders design
  (`docs/product/ecology/design_ants_spiders.md`).
- The engine and the building plan: `docs/product/architecture/architecture_bug_behaviour.md`,
  `architecture_swarm_sync.md` §0, `architecture_combat.md`, `nakama/data/species.json`.
