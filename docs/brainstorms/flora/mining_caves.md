# Brainstorm — Mining Caves flora

Underground flora for the **Mining Caves** zone (`underground_passages_31` and the deeper cave/mining-camp
scenes — south of the village). This is a sunless world: no real photosynthesis, so the "plants" here are
**fungi, mosses, lichens, algae, root intrusions from above, and etiolated (pale, light-starved) growth**.
Theme: damp stone, faint bioluminescence, decay, slow growth on minerals and bone.

Design note (matches `caves.md`): minerals/crystals use the **mineral** art family; the entries below
are the *living/soft* dressing that fills cavern floors, walls, pools, and rubble between ore veins. Many double
as **glow sources** (light bonus), **alchemy reagents**, or **edible** cave forage. Existing surface flora ids
(`mushroom_blue`, `mushroom_bracket`, `moss_clump`, `fern`, `ivy`, etc.) are reused where sensible; new
cave-specific ids are proposed below. Favor VARIETY — AI sprites are cheap.

Legend: **Glow** = emits light · **Edible** = food forage · **Alchemy** = potion/dye reagent · **Rarity**.

---

## 1. Glowing fungi (the cave's light source — atmospheric anchor)
The signature look of the zone. These should be the most varied family.

- `cave_glowcap` — small domed mushroom with a soft blue-green luminous cap; the workhorse glow plant. Glow, Edible(low), common.
- `cave_glowcap_cluster` — a tight ring/cluster of glowcaps on the floor; brighter pooled light. Glow, common.
- `lanternshroom` — tall stalk topped by a bulbous glowing "lantern" sac, faint yellow-warm. Glow, uncommon.
- `mushroom_blue` *(existing)* — reuse as a cool-blue glow mushroom in damper grottoes. Glow, common.
- `foxfire_shelf` — bracket fungus on cave walls that glows a ghostly green at the rim ("foxfire"). Glow, Alchemy(luminous dye), uncommon.
- `emberfungus` — orange-red glowing fungus clinging near warm vents/lava cracks; pulses slowly. Glow, Alchemy(heat reagent), rare.
- `starcap_moss_fungus` — pinprick blue glow-dots speckled over a low fuzzy mat; reads like a tiny night sky. Glow(dim), uncommon.
- `pale_deathcap` — luminous bone-white cap, beautiful and **toxic**; harvest for poison reagents only. Glow, Alchemy(toxin), Edible=DANGER, uncommon.
- `gillglow` — fan mushroom whose underside gills glow; cap stays dark, light leaks downward onto rock. Glow, uncommon.

## 2. Shelf / bracket fungus (wall-clinging, non-glowing)
- `mushroom_bracket` *(existing)* — woody shelf fungus stepping up a damp wall. Edible(tough), common.
- `cave_shelf_white` — pale layered shelf fungus, stacked plates. Edible, common.
- `tinder_conk` — hard hoof-shaped conk on petrified wood/root; harvest as **tinder/fire-starter** material. Alchemy(craft), uncommon.
- `crimson_bracket` — deep-red shelf fungus, leathery; striking accent. Alchemy(red dye), uncommon.
- `oyster_shelf` — clustered fan shelves on fallen roots, edible and prized. Edible(good), uncommon.

## 3. Mold, mildew & crust (the decay layer)
- `cave_mold_patch` — fuzzy grey-green mold spreading over damp stone. Alchemy(antibiotic base), common.
- `slime_mold_yellow` — bright yellow plasmodial slime creeping across rubble; weirdly alive-looking. Alchemy(novelty reagent), uncommon.
- `black_rot_crust` — dark spreading crust on dead wood/bone; ugly, ominous. common (deeper).
- `saltpeter_bloom` — white mineral-salt efflorescence "flowering" on old walls (looks botanical). Alchemy(saltpeter→explosives), uncommon.
- `cobweb_mold` — wispy white mycelial webbing draped between rocks (not a spider web). decor filler, common.

## 4. Lichen & moss (slow crust on stone)
- `cave_lichen_grey` — crusty grey-green lichen flaking over bare rock. common.
- `cave_lichen_orange` — vivid orange lichen rosettes near air currents/cave mouths. Alchemy(dye), uncommon.
- `frill_lichen` — pale ruffled leafy lichen hanging off ledges. uncommon.
- `moss_clump` *(existing)* — reuse as dark damp cave moss in wetter corners. common.
- `glow_moss` — moss faintly luminescent blue-green where moisture is high; carpets pool rims. Glow(dim), Edible(low), common.
- `dripstone_moss` — moss colonizing wet flowstone/stalactite bases; beaded with water. common.
- `liverwort_mat` — flat green liverwort hugging seep lines on walls. common.

## 5. Glow-algae & pool growth (on/around underground water)
For grottoes, springs, and still pools (see `caves.md §3`).
- `glow_algae_film` — luminescent blue-green film skimming a still pool surface; the pool *glows*. Glow, Alchemy(luminescence), common (on water).
- `glow_algae_dense` — thick algal mat at a pool edge, brighter, slightly bubbling. Glow, uncommon.
- `cave_pondweed` — pale stringy submerged weed in clear cave water (etiolated version of `pondweed`). uncommon.
- `mineral_crust_pool` — colorful bacterial/mineral crust ringing a spring (hot-spring travertine vibe). decor, uncommon.
- `dripping_seaweed` — sheets of slick algae hanging where water sheets down a wall. decor, uncommon.
- `cave_lily` — rare pale, near-translucent water-lily-like growth on a deep glow-pool. Glow(faint), Alchemy, rare.

## 6. Root intrusions & tendrils (life reaching DOWN from the surface)
Story beat: the surface world is *just above*. These tie the cave to the world overhead.
- `root_tendril` — thin pale roots threading down through a ceiling crack. common.
- `root_curtain` — a hanging curtain/veil of fine rootlets, like underground willow hair. decor, uncommon.
- `taproot_descent` — a single fat woody taproot punching through the ceiling into the chamber. uncommon.
- `root_mat_floor` — tangled root mat spread across a cavern floor under a surface tree. common.
- `ivy` *(existing)* — reuse as pale cave ivy creeping down from a sinkhole/light shaft. uncommon.
- `glow_root` — root tendril with faintly luminescent sap-nodes (where it meets glow-fungus). Glow(dim), Alchemy, rare.

## 7. Etiolated / pale "true" plants (light-starved survivors)
Plants that fell/seeded in but grow blanched and stretched without sun — eerie and pale.
- `pale_fern` — bleached white-green fern (etiolated `fern`); long and leggy. Edible(fiddleheads), uncommon.
- `ghost_grass` — colorless wispy grass tufts under a light shaft. common (near shafts only).
- `etiolated_sprout` — leggy yellow-white seedling reaching for any light. common.
- `cave_clover` — pale four-leaf-ish clover near a sinkhole; "lucky" flavor. Edible, rare.
- `ghost_flower` *(monotropa/"corpse plant" vibe)* — waxy white parasitic flower with no chlorophyll, lives off fungus. Alchemy(spirit reagent), rare.
- `blanched_nettle` — pale stinging nettle near a seep; still stings. Alchemy(potion base), uncommon.

## 8. Spore & misc dressing (filler + flavor)
- `puffball_cave` — pale puffball that bursts spores when disturbed (cf. `mushroom_puffball`). Alchemy(spore powder), common.
- `spore_stalk` — tall thin stalk topped with a spore pod, releases drifting motes. decor/atmosphere, uncommon.
- `fungal_garden_patch` — a "farmed-looking" patch of mixed fungi (lore: tended by cave insects, see bugs doc). Edible, uncommon.
- `bone_fungus` — small fungus fruiting directly out of an old bone/skull in rubble. Alchemy(macabre reagent), uncommon.
- `mushroom_ring_fairy` — a faint ring of tiny mushrooms on a chamber floor; folklore accent. rare.

---

## Uses summary (for later ecology/crafting docs)
- **Glow plants** → light/ambiance bonus when placed as farm decor; key to a "glow garden" theme; alchemy luminescence reagents.
- **Edible cave forage** → early underground food before crops; risk/reward with toxic look-alikes (`pale_deathcap`).
- **Alchemy reagents** → dyes (lichens, brackets), toxins (deathcap), saltpeter (mining/explosives), spore powders, "spirit" reagents (ghost_flower).
- **Farm-decor crossovers** → glowcaps, glow_algae pools, root_curtain, foxfire_shelf, crystal-adjacent fungi all make atmospheric base/cave-home decor.

## Open questions
- Do glow plants need a day/night or "dark zone" lighting hook to make their bonus meaningful?
- Fungal farming loop: can the player *cultivate* `cave_glowcap`/`fungal_garden_patch` on substrate (logs, compost, bone)?
- Toxic look-alikes (deathcap vs glowcap): a "foraging skill / identify" mechanic, or just lore?
