# BugFarmer encyclopedia — bugs & plants (taxonomy for sprite generation)

A rich, expandable catalogue of creatures and flora. We make **variants** so the world has depth and a
difficulty ladder: most families get **3 difficulty tiers** — `easy` / `medium` / `elite` (elite =
stronger, tougher, breaks more, higher value). Sprites are generated **A/B** (two candidates each) for
picking; names are obvious for now (the in-game magnifying glass will surface value/toughness later).
Bugs use the `creature` art family; plants use the `flora` family. Catalogue grows over time — add rows
freely; we can delete later.

Status legend: ☐ planned · ◐ data+catalog added · ● art generated.

## BUGS — normal
| family | easy | medium | elite |
|--------|------|--------|-------|
| housefly | `fly_house` | `fly_horse` | `fly_bot` |
| fruit fly | `fruitfly_common` | `fruitfly_vinegar` | `fruitfly_spotwing` |
| mosquito | `mosquito_common` | `mosquito_tiger` | `mosquito_malaria` |
| bee | `bee_honey` | `bee_bumble` | `bee_carpenter` |
| wasp/hornet | `wasp_paper` | `wasp_yellowjacket` | `hornet_giant` |
| beetle | `beetle_ground` | `beetle_rhino` | `beetle_stag` |
| butterfly | `butterfly_cabbage` | `butterfly_swallowtail` | `butterfly_emperor` |
| moth | `moth_brown` | `moth_luna` | `moth_atlas` |
| grasshopper/locust | `grasshopper_field` | `locust_migratory` | `locust_swarm` |
| hunting spider | `spider_jumping` | `spider_wolf` | `spider_huntsman` |
| web spider | `spider_orb` | `spider_widow` | `spider_funnel` |
| ant | `ant_worker` | `ant_soldier` | `ant_queen` |
| scorpion | `scorpion_bark` | `scorpion_desert` | `scorpion_emperor` |
| centipede | (segments: `centipede_*_a/b`) | `centipede_giant` | `centipede_titan` |
| millipede | (segments: `millipede_*_a/b`) | `millipede_giant` | `millipede_titan` |
| roach | `roach_common` | `roach_hisser` | `roach_giant` |
| firefly | `firefly_common` | `firefly_blue` | `firefly_great` |
| dragonfly | `dragonfly_common` | `dragonfly_emperor` | `dragonfly_hawker` |
| cicada | `cicada_annual` | `cicada_dog` | `cicada_periodical` |
| ladybug | `ladybug_seven` | `ladybug_orange` | `ladybug_giant` |

## BUGS — water
| family | easy | medium | elite |
|--------|------|--------|-------|
| water strider | `strider_common` | `strider_giant` | `strider_sea` |
| diving beetle | `dytiscid_small` | `dytiscid_great` | `dytiscid_giant` |
| backswimmer | `backswimmer_common` | `backswimmer_giant` | `backswimmer_great` |
| dragonfly nymph | `nymph_dragon` | `nymph_hawker` | `nymph_emperor` |
| mayfly | `mayfly_common` | `mayfly_burrowing` | `mayfly_giant` |
| larva/grub | `larva_mosquito` | `grub_white` | `grub_giant` |
| leech | `leech_common` | `leech_horse` | `leech_giant` |
| pond snail | `snail_pond` | `snail_ramshorn` | `snail_apple` |

## PLANTS (3 variants where sensible)
| family | members |
|--------|---------|
| wildflower | `flower_red/blue/yellow`, `poppy`, `chamomile`, `lavender`, `clover`, `dandelion`, + `flower_aster`, `flower_foxglove`, `flower_bluebell` |
| mushroom | `mushroom_brown/red/glow/blue/chanterelle/puffball/cluster/morel/bracket/inkcap` (have) |
| grass/reed | `tall_grass`, `reeds`, `cattail`, `pampas` |
| fern/moss | `fern`, `cave_moss`, `moss_clump`, `clubmoss` |
| bush/berry | `bush`, `wild_berry_bush`, `bush_flowering`, `bramble` |
| herb | `mint`, `sage`, `thyme`, `fennel` (potion ingredients) |
| cactus/succulent | `cactus_saguaro/barrel/prickly` (have), `aloe`, `agave` |
| aquatic | `lily_pad`, `water_lily`, `duckweed`, `pondweed` |
| vine/climber | `ivy`, `morning_glory`, `grapevine` |

## Generation process
1. Pick a family; add the 3 members as DATA (`nakama/data/bugs.json` for creatures with a `category` +
   tier, or `occupants.json`/`items.json` for plants) + a catalog row (`look`, `family: creature`/none).
2. **Test batch one family** (A/B), `Read` the A/B sheet, refine the prompt if needed.
3. A/B-generate the family; build a category A/B contact sheet for review.
4. Loop. Difficulty reads visually: elite = bigger, darker/armored, meaner.

(Existing bug sprites in `Resources/Bugs/` cover many easy/medium members already — reuse, don't
duplicate; generate the missing tiers + new families.)
