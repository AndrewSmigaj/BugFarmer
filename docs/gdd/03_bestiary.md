# §03 · Bestiary & tiers
<!-- gdd: id=03 status=draft updated=2026-09-27 -->

Not written yet. This section will gather the design from the sources below, run every idea through the
idea lenses, then go to the review page.

## Decided
- **Real species with real behaviour** (2026-07-11) — the game teaches a little ecology and biology; the
  prototype's invented names are replaced (2026-09-27).
- **Bugs, fish and people survive**; birds, amphibians and reptiles died out too (2026-09-27).
- **Every bug is unfinished**, including those already worked on; each needs more passes for behaviour, combat and
  ecology tuning (2026-09-27).
- **Tiers belong to a species, not a rule**: one form, two or at most three; aphids have one (2026-09-27).
- **Two ant species**, black ants and fire ants, in different zones (August 2026; 2026-09-27).
- **Mini-bosses** are set off by conditions or simply placed in the world (2026-09-27).
- Real centipedes hunt alone; the game groups them only to keep network traffic down (2026-09-27).
- **What counts as a bug** (2026-09-28): insects and the other arthropods — spiders, scorpions, centipedes, millipedes,
  pill bugs, crayfish and crabs; fish are separate; no worms or leeches (snails go by the same rule — my reading).

## To settle (raw list — not yet checked against the idea lenses)
- **Reviewing every bug (2026-10-02)** — done: the Bugs list on the items page (`docs/gdd/bug_table.jsonl`, 116 bugs:
  the game's 15, the zone plans' 84 below, the picture-only extras in the game's bug file, the bugs the owner has asked
  for and the bugs the item rows name) is settled by the owner's marks and the accepted bug lineups (D79–D81): 54 kept,
  62 cut. The lineups (`docs/gdd/bug_lineups.jsonl`) are the roster.
- Which species the game ships with, and in which zones — most zones aren't designed yet (2026-09-27); the bug lineups
  (D80, D81) now place most kept species in their zones.
- The real-species naming pass for the fifteen species in the prototype: the names are chosen, all but the meadow
  butterfly's (D80); renaming them in the game is in the BACKLOG.
- **The species the zone designs name** — 84 distinct species in 98 rows across 17 zone sheets, marked against the
  rulings above. The zone sheets were written to be generous ("prune later"), so this is a list to cut from, not a
  plan:

- **Starting Village** — fly, ladybug, aphid, pill bug, garden ant (the black ant itself: the owner's black ant is the black garden ant, 2026-08-15), garden snail (not an insect — Q2).
- **Bee Meadow** — honeybee, mason bee, leafcutter bee, sweat bee, pollen beetle.
- **Wasp Thicket** — paper wasp, mud dauber, earwig, silverfish, thicket matriarch (mini-boss; invented — needs a real species).
- **Shallow Swamp** — damselfly, pond skater, whirligig beetle, leech (not an insect — Q2), marsh mosquito, bog centipede.
- **Hilltop Meadow** — bumblebee, carpenter bee, hornet (mini-boss), paper wasp, cabbage white.
- **Butterfly Fields** — butterfly, monarch, glasswing, luna moth, emperor moth, firefly, cicada, hawk moth.
- **Scorpion Rocks** — bark scorpion, desert tick, harvestman, vinegaroon, den matron (mini-boss; invented — needs a real species).
- **Deep Swamp** — swamp mosquito, dragonfly, dragonfly nymph, water strider, giant water bug (mini-boss), swamp leech (not an insect — Q2), bog serpent fly (invented — needs a real species).
- **Locust Farmland** — locust, grasshopper, cricket, crop beetle, mantis (mini-boss), nymph.
- **Millipede Forest** — giant millipede, forest centipede, bark beetle, stag beetle, rhino beetle (mini-boss), forest snail (not an insect — Q2).
- **Spider Vale West** — orb weaver, wolf spider, jumping spider, armored centipede, web tender (invented — needs a real species), vale broodmother (mini-boss; invented — needs a real species).
- **Spider Vale East** — black widow, tarantula, trapdoor spider, spiderling swarm (invented — needs a real species), giant huntsman (mini-boss).
- **Ant Colony** — garden ant (the black ant itself: the owner's black ant is the black garden ant, 2026-08-15), black ant, harvester ant (ant species — cut (D39)), soldier ant (an ant caste — belongs to black or fire ants), colony queen (mini-boss; an ant caste — belongs to black or fire ants).
- **Centipede Cavern** — giant centipede, glowworm, cave beetle, camel cricket, centipede matron (mini-boss; invented — needs a real species).
- **Underground Passages** — springtail, blind beetle, mole cricket, cave spider, glow grub (invented — needs a real species).
- **Underground River** — cave crayfish (not an insect — Q2), water beetle, aquatic larva, albino isopod, glow mayfly (invented — needs a real species), blind cave fish (a fish), cave crab (mini-boss; not an insect — Q2).
- **Deadly Ants** — army ant (ant species — cut (D39)), fire ant, soldier ant (an ant caste — belongs to black or fire ants), bullet ant (ant species — cut (D39)), war queen (mini-boss; an ant caste — belongs to black or fire ants), ant worker (an ant caste — belongs to black or fire ants).

## Sources to gather
- `docs/product/economy/species_and_drops.md`
- `docs/product/design/encyclopedia.md`
- `docs/brainstorms/bugs/*.md`
- `docs/product/architecture/architecture_bugs.md`
- `docs/product/ecology/design_ants_spiders.md`
- `docs/product/investigations/deep_research_2026-07/bugs/`
- `nakama/data/species.json`
