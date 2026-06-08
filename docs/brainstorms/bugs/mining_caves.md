# Brainstorm — Mining Caves bugs

Cave fauna for the **Mining Caves** zone (underground, south of village). Cave ecology is **sparse, slow,
and adapted to dark**: blindness or huge eyes, pale/white "troglomorphic" bodies, long antennae, lower
metabolism, fungus- and detritus-based food webs. Threats cluster around **ore-bearing chambers** (a
risk/reward gate on the good loot). Per the zone doc, bugs live in **carved caverns, not solid rock**.

Reuse where possible: the segmented `centipede_*`/`millipede_*` body-part sprites already exist; cave
spiders can reskin `spider_funnel`/`spider_wolf`; `roach_*`, `springtail`(new), `firefly_*` (→ glowworm).
Favor variety — propose pale/blind variants freely.

Legend: **Diff** = combat/threat difficulty (Trivial→Boss) · **Farm** = farmable/penned · **Use** = drops/role · **Rarity**.

---

## 1. Detritivores & fungus-eaters (the base of the food web — mostly harmless, farmable)
The harmless majority. They eat fungus, mold, guano, and rot — good early forage/farm stock.
- `cave_isopod` — pale giant pillbug/woodlouse trundling over rubble; rolls into a ball when poked. Diff: Trivial. Farm: yes. Use: chitin, fungus-tender. common.
- `cave_isopod_giant` — dinner-plate-sized blind isopod, armored grey plates. Diff: Easy (slow, defensive). Farm: yes. Use: armor-chitin, food. uncommon.
- `springtail_cave` — tiny pale springtail swarming on damp film; flicks away. Diff: Trivial. Farm: yes (feeder). Use: bait, fungus-soil booster. common.
- `cave_snail_pale` — translucent snail grazing glow-algae on pool rims (cf. `snail_pond`). Diff: Trivial. Farm: yes. Use: slime (alchemy), shell. common.
- `cave_millipede` — long pale millipede coiling over rot (reuse `millipede_*` segments, recolor). Diff: Trivial (curls, mild defensive secretion). Farm: yes. Use: leaf/detritus processor. common.
- `fungus_gnat_swarm` — clouds of tiny gnats over fruiting fungus; harmless nuisance. Diff: Trivial. Farm: n/a. Use: pollinator/feeder swarm. common.
- `cave_mite_white` — speck-sized white mites on fungus gardens. Diff: Trivial. Farm: feeder. Use: ecology filler. common.

## 2. Crickets & roaches (scavengers — skittish, lurk at edges)
- `cave_cricket` — long-legged, long-antennae camel/cave cricket; leaps wildly when lit. Diff: Trivial (flees). Farm: yes. Use: bait, food, fishing. common.
- `cave_cricket_giant` — oversized cave cricket, unsettling antennae. Diff: Easy. Farm: yes. Use: premium bait. uncommon.
- `roach_cave` — pale wingless cave roach scattering from torchlight (reuse `roach_common`/`roach_giant`). Diff: Trivial→Easy. Farm: yes (hardy feeder). Use: detritivore, scuttle swarm. common.
- `cave_silverfish` — fast scaly silverfish in cracks and old camp crates; chews supplies. Diff: Trivial. Farm: no. Use: pest flavor, minor drop. common.

## 3. Glow bugs (the living lights — prized, gentle, atmospheric)
The luminous beauty of the zone; collectible and decor-tier.
- `glowworm` — larva on a wet ceiling spinning glowing snare-threads (NZ-glowworm vibe); whole ceiling sparkles. Diff: Trivial. Farm: yes (glow-decor). Use: light source, silk-thread, jar decor. uncommon.
- `cave_firefly` — pale steady-glow firefly drifting in still air (reuse `firefly_blue`/`firefly_great`). Diff: Trivial. Farm: yes. Use: light decor, alchemy luminescence. uncommon.
- `glowbeetle` — beetle with luminous abdomen panels crawling ore veins; a "lantern that walks." Diff: Easy. Farm: yes. Use: light, chitin. uncommon.
- `lantern_moth_pale` — ghost-white cave moth with faintly glowing eyespots, drawn to torches. Diff: Trivial. Farm: yes. Use: glow-dust, decor. rare.

## 4. Blind hunters (predators — the early threats)
Pale, eyeless, sense vibration/scent. The first thing that makes mining *risky*.
- `blind_beetle` — pale eyeless ground beetle, fast pincers, hunts isopods (in zone doc). Diff: Easy. Farm: pen-able predator. Use: chitin, mandible. common.
- `cave_centipede` — long venomous pale centipede, the classic cave menace (reuse `centipede_*` segments, pale recolor). Diff: Medium (venom). Farm: risky. Use: venom (alchemy), chitin segments. uncommon.
- `cave_centipede_giant` — a monstrous multi-segment centipede; mini-threat of the deeper veins. Diff: Hard. Farm: no. Use: potent venom, trophy. rare.
- `whip_spider_cave` — flat eyeless amblypygid with long feeler-legs; creepy but low-damage, ambush. Diff: Medium. Farm: no. Use: trophy, fright flavor. uncommon.
- `cave_scorpion_pale` — small translucent scorpion under rocks (reuse `scorpion`/`scorpion_bark`). Diff: Medium (sting). Farm: risky. Use: venom, chitin. uncommon.
- `vampire_leech_cave` — pale leech in cave pools/seeps (reuse `leech_common`/`leech_giant`). Diff: Easy (drains over time). Farm: no. Use: alchemy (blood/anticoagulant). uncommon.

## 5. Cave spiders (web-builders — the dark corners)
- `cave_spider` — small pale cave spider, the in-zone-doc baseline (reuse `spider_wolf`/`spider_funnel`). Diff: Easy. Farm: yes (silk). Use: silk, venom. common.
- `cave_spider_funnel` — pale funnel-web spinner guarding a silk-lined crevice burrow. Diff: Medium. Farm: risky. Use: dense silk, venom. uncommon.
- `cave_widow_pale` — translucent widow with a faint hourglass; small but nasty. Diff: Medium (venom). Farm: no. Use: potent venom. rare.
- `tunnel_weaver` — spider whose sheet-webs span narrow tunnels (slows/snares the player). Diff: Easy (hazard more than fighter). Use: web-blockade flavor, silk. uncommon.

## 6. Ore-cave threats (the risk gate on good loot — biggest, scariest)
These cluster near rich veins / crystal chambers; beating them is the price of the haul. (Lore can tie
them to "drawn to / made of minerals.")
- `crystal_beetle` — heavy beetle with crystalline-encrusted carapace guarding geodes; refracts light. Diff: Hard. Farm: no. Use: crystal shards, prime chitin, trophy. rare.
- `rock_mite_swarm` — swarm of grey mineral-mites that erupt from a struck vein and chew tools. Diff: Medium (swarm, gear-damage). Use: ore dust, swarm threat. uncommon.
- `magma_centipede` — red-hot centipede near lava cracks/`emberfungus`; burns on contact. Diff: Hard. Farm: no. Use: fire reagent, ember-chitin. rare (deep only).
- `deep_stalker` — large pale eyeless predator (amphibian/arthropod hybrid) that ambushes in the darkest galleries; the zone's apex. Diff: Boss-ish. Farm: no. Use: rare trophy, gates deepest loot. very rare.
- `gem_mimic` — a "crystal cluster" that is actually a sleeping creature; springs when you mine it. Diff: Hard (ambush). Use: surprise threat, gem + creature drops. rare.

## 7. Bats & flyers (the vertebrate question — keep light)
GDD is a *bug* game, so vertebrates are an open question — list them but flag.
- `cave_bat` — small bat roosting in colonies on the ceiling; bursts into a swarm when disturbed. Diff: Easy (swarm startle). Farm: no. Use: guano (the fungus food-web fuel + fertilizer!), atmosphere. uncommon. **Flag: vertebrate — include only if non-bug fauna is allowed; else replace with a giant cave moth roost.**
- `bat_swarm` — the disturbed-colony swarm event (cf. `locust_swarm`); fills a chamber, flees to exits. Diff: Easy (hazard/jumpscare). Use: ambiance event. uncommon. (same vertebrate flag)
- `cave_moth_roost` — bug-safe substitute: a ceiling cluster of pale moths that scatter like bats. Diff: Trivial. Farm: yes. Use: glow-dust, decor. uncommon.

---

## Ecology summary (for the ecology proposal doc)
- **Food web:** guano (`cave_bat`) + surface detritus down sinkholes + fungus (flora doc) → detritivores
  (isopods, millipedes, springtails, snails, roaches) → predators (blind_beetle, centipedes, spiders,
  scorpions) → apex (`deep_stalker`). Glow bugs feed gnats/moths drawn to their light.
- **Fungus farming by bugs:** `fungus_garden_patch` (flora) tended by `cave_isopod`/`cave_mite` — a
  ready-made "the bugs farm too" emergent beat the player can co-opt.
- **Difficulty gradient:** harmless detritivores in starter caverns → predators mid → ore-cave threats and
  `deep_stalker` deep/near rich veins, so danger scales with reward (matches the ore rarity gradient).
- **Farmable / useful highlights:** isopods, crickets, roaches, snails (food/bait/feeder); glowworm,
  cave_firefly, glowbeetle (light decor + alchemy); cave_spider/funnel (silk); centipede/scorpion/widow
  (venom — risky); crystal_beetle (crystal + trophy).

## Open questions
- Vertebrates (bats) yes/no? If no, `cave_moth_roost` covers the ecological niche bug-safely.
- Do glow bugs provide a *placed-light* farm bonus (jar them like `firefly jar` in `brainstorm_items`)?
- Should ore-cave threats literally guard veins (spawn-on-strike), making mining a fight, or just lurk nearby?
- Reusing segmented centipede/millipede art: pale recolor + scale, or new cave-specific sprites?
