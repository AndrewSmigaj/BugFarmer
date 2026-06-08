# Materials Progression — Ores, Metals, Alloys & Non-Metals

> **Status:** brainstorm / design bible. No code, no entity JSON, no art. Names are
> snake_case proposals; tiers and numbers are starting points to balance later.
>
> **Grounding (read alongside):**
> - Existing ores/blocks: `tools/art/catalog/blocks.json` (copper, coal, tin, iron, silver,
>   gold, platinum, diamond + stone/clay/quartz/sand/sandstone).
> - Existing item materials: `nakama/data/entities/items.json` already has `wood`, `fiber`,
>   `flower`, `crystal`, `bone`, `coal`, `*_ore`, `quartz`, `sand`, `diamond`, `iron_bar`, `brick`.
> - Ore rarity + zone placement: `docs/guides/authoring/caves.md` (veins, 12–18% density,
>   deeper = rarer).
> - The pen ladder below ties to the catch system in `docs/product/architecture_bugs.md`
>   (net sizes small/medium/large/trap_only; "some bugs are GIANT").

This doc is the **single source for what materials exist and how they ladder up**, so the
weapons and armor docs can just reference a material + tier instead of re-deriving it.

---

## 0. How the ladder reads

Every material has:

- **Tier** — a rough power band 0–9 (T0 starter junk → T9 endgame/arcane). Tiers map loosely
  to the Terraria-style rarity colors used in `weapons.md` and `armor_clothing.md`.
- **Where found** — tied to the demo zones:
  - **Surface — village / meadow / woods**: wood, fiber, plant materials, clay, surface stone,
    low bug drops (chitin, silk).
  - **Mining caves (`underground_passages_*`)**: the ore ladder, stone, crystal, geodes.
  - **Ant colony (deep)**: the deepest ores + colony-only organics (royal wax, ant-resin,
    chitin from big colony bugs) + the first "exotic" materials.
  - **Desert / pond / special**: amber, glass-sand, salt, shell, specialty drops.
- **Uses** — tools, weapons, armor, building, pens, refining, station fuel.

### Tier → rarity-color cheat sheet (shared with weapons/armor)

| Tier | Rarity color (Terraria-style) | Feel |
|------|-------------------------------|------|
| T0 | Gray | junk / starter |
| T1 | White | common craftable |
| T2 | Blue | solid early |
| T3 | Green | mid |
| T4 | Orange | strong mid |
| T5 | Light Red | rare |
| T6 | Pink | very rare |
| T7 | Light Purple | epic / alloy |
| T8 | Lime | crystal / magic |
| T9 | Yellow→Rainbow | legendary / arcane / boss |

---

## 1. Raw ores (mined as blocks → smelt to bars)

These already exist as `ore_*_block` occupants and `*_ore` items; tiers/zone notes formalized.

| Ore (raw) | Smelts to | Tier | Where found | Notes |
|-----------|-----------|------|-------------|-------|
| `coal` | (fuel, not a bar) | T1 | caves, common veins | Smelter/forge fuel; also a black dye + gunpowder-ish reagent. |
| `copper_ore` | `copper_bar` | T1 | caves near entrance, common | First real metal; starter tools/weapons. |
| `tin_ore` | `tin_bar` | T1 | caves, rare small bits | Pairs with copper → **bronze**. |
| `iron_ore` | `iron_bar` | T2 | caves, uncommon | Backbone metal; `iron_bar` already in items.json. |
| `silver_ore` | `silver_bar` | T3 | caves, rare deeper | Precious; anti-"creep" bonus vs swarms (see ecology). |
| `gold_ore` | `gold_bar` | T4 | deep caves / colony fringe | Value, light electronics, fancy gear. |
| `platinum_ore` | `platinum_bar` | T5 | deep caves / colony | Premium swap for gold; stronger gear. |
| `diamond` (gem) | (cut → `diamond_cut`) | T6 | deepest caves / colony | Gem, not smelted; tool tips, lenses, top pens. |
| `quartz` | (cut → `quartz_lens` / flux) | T2 | caves, milky veins | Glassmaking flux, lenses, weak magic focus. |

### Proposed NEW raw ores (extend the ladder)

| Ore (raw) | Smelts to | Tier | Where found | Notes |
|-----------|-----------|------|-------------|-------|
| `lead_ore` | `lead_bar` | T2 | caves, alongside iron | Heavy; sling shot, weighted hammers, ballast for big pens. |
| `nickel_ore` | `nickel_bar` | T3 | caves mid-deep | Alloy component for steel-family + corrosion resistance. |
| `cobalt_ore` | `cobalt_bar` | T6 | colony-deep / "blue rock" pockets | Vivid blue; fast tools, light blades. |
| `mythril_ore` | `mythril_bar` | T7 | deepest colony veins | Classic mid-magic metal; lightweight, holds enchant. |
| `adamant_ore` | `adamant_bar` | T7 | deepest colony veins (rival to mythril) | Heavy, high-armor variant; chosen vs mythril per world. |
| `meteorite_ore` | `meteorite_bar` | T8 | rare surface "fall" sites (meadow craters) | Glows; space-themed tier, mild burn hazard raw. |
| `sulfur` | (reagent) | T2 | caves near vents / desert | Smoke-bombs, gunpowder, calm-incense, fungicide. |
| `saltpeter` | (reagent) | T2 | cave walls / desert | Gunpowder, preserving bug bait, fertilizer. |
| `rock_salt` | `salt` | T1 | desert / dry caves | Preserves bug specimens (sell-value boost), slug repellent. |

---

## 2. Smelted metals (bars)

| Bar | From | Tier | Primary uses |
|-----|------|------|--------------|
| `copper_bar` | copper | T1 | starter tools, copper pickaxe (exists), wire, low pens |
| `tin_bar` | tin | T1 | bronze input, tin cans/lanterns |
| `iron_bar` | iron | T2 | tools, **iron cage pen**, nails, structural |
| `lead_bar` | lead | T2 | weights, pipes, slingshot ammo |
| `nickel_bar` | nickel | T3 | steel/electrum alloying, plating |
| `silver_bar` | silver | T3 | jewelry, "clean" gear, anti-rot fittings |
| `gold_bar` | gold | T4 | value, conductive parts, decorative gear |
| `platinum_bar` | platinum | T5 | premium gear, lab/station parts |
| `cobalt_bar` | cobalt | T6 | fast tools, light blades |
| `mythril_bar` | mythril | T7 | enchantable mid-magic gear |
| `adamant_bar` | adamant | T7 | heavy high-defense gear |
| `meteorite_bar` | meteorite | T8 | space-tier gear, glowing fittings |

---

## 3. Alloys (combine bars at a forge)

The interesting middle of the ladder — alloys gate progression so single-ore luck doesn't
trivialize gear.

| Alloy | Recipe (bars/reagents) | Tier | Uses / character |
|-------|------------------------|------|------------------|
| `bronze_bar` | copper + tin | T2 | Better than copper; classic tier-2 tools/weapons/pens. |
| `steel_bar` | iron + coal (carbon) | T3 | The workhorse: **steel cage pen**, sturdy swords, armor. |
| `hardsteel_bar` | steel + nickel | T4 | Tougher steel; reinforced pens, hammers, heavy armor. |
| `electrum_bar` | gold + silver | T4 | Conductive + pretty; lanterns, light-magic foci, luck gear. |
| `sterling_bar` | silver + a little copper | T3 | Durable silver for tools/jewelry; anti-rot. |
| `pewter_bar` | tin + lead + a little copper | T2 | Cheap castable fittings, mugs, decorative. |
| `cobalt_steel_bar` | steel + cobalt | T6 | Fast + strong; high-end mining + blades. |
| `mythril_steel_bar` | mythril + steel | T7 | Enchantable armor backbone. |
| `adamantite_plate` | adamant + hardsteel | T8 | Top mundane defense; **fortress-grade pen** bars. |
| `orichalcum_bar` | platinum + cobalt + quartz-flux | T8 | Pink-tinted magic metal; ranger/mage hybrid gear. |
| `voidsteel_bar` | meteorite + adamant + obsidian | T9 | Endgame; boss-bug pens, legendary weapons. |
| `living_bronze` | bronze + amber + royal_wax | T6 | Bug-themed "warm" alloy; bonuses to bug handling/pens. |

---

## 4. Refined / rare / magic materials

Non-bar specialty materials (cut gems, processed organics, magic essences). These are the
"sparkle" tier and most boss/rare drops live here.

| Material | Tier | Where / how | Uses |
|----------|------|-------------|------|
| `diamond_cut` | T6 | cut raw diamond (jeweler's bench) | Tool tips, top pen lattice, lenses, magic focus. |
| `quartz_lens` | T2 | grind quartz | Magnifying glass (inspect bugs), goggles, weak focus. |
| `crystal_shard` | T5 | cave crystals (`crystal_small/large`, `crystal_quartz`) | Glow gear, mage staves, **crystal pen** mesh. |
| `geode_core` | T5 | crack a `geode` | Random gem; gambling/luck loop. |
| `obsidian` | T6 | water + lava contact (deep) / volcanic | Sharp blades, dark armor, voidsteel input. |
| `amber` | T4 | tree-sap fossils (woods) / dig | **Bug-in-amber** trophies; living_bronze input; preserves specimens. |
| `glass` | T2 | smelt `sand` (+ quartz flux) | Jars/terrariums (live bug storage!), windows, lanterns, bottles. |
| `enchanted_dust` | T7 | grind crystal_shard + rare bug essence | Enchanting/reforging reagent. |
| `lumen_essence` | T8 | distilled from firefly/glow-bug swarms | Permanent light gear, glow weapons, night-luck. |
| `chitin_plate` | T4 | refined chitin (see §5) from big beetles/roaches | Lightweight bug-armor, **chitin pen** panels. |
| `arcane_silk` | T7 | spider-boss silk woven with enchanted_dust | Mage robes, web-traps, **arcane pen** netting. |
| `royal_jelly` | T6 | bee/wasp colony (boss-ish hives) | Buff consumable; living_bronze + healing gear. |
| `venom_gland` | T5 | scorpions/wasps/spiders | Poison weapons, antivenom, strong bait. |
| `bioluminescent_gel` | T6 | glow-mushrooms + fireflies | Lanterns, glow ammo, terrarium lighting. |

---

## 5. Non-metal materials (the organic + earth ladder)

VARIETY mandate — these are first-class, not afterthoughts. Many are bug/plant-sourced,
tying materials directly to the catch-and-farm loop.

### Plant & wood

| Material | Tier | Where | Uses |
|----------|------|-------|------|
| `wood` | T1 | trees (surface) — already an item | Everything early: tools, **twig/wood pens**, walls, fuel. |
| `softwood` | T1 | pine/palm | Cheap planks, kindling. |
| `hardwood` | T2 | oak/apple/orange (slow-grow) | Sturdier pens, bows, hafts, **reinforced wood pen**. |
| `ironbark` | T4 | rare ancient trees (deep woods) | Naturally tough wood; mid pens without metal; bows. |
| `living_wood` | T5 | magic grove / boss tree | Grows/self-repairs; nature-set gear, regrowing pens. |
| `fiber` | T0 | grasses/reeds — already an item | Twine, nets, straw hat, cheap cloth. |
| `straw` | T0 | wheat/grass | Straw hat, thatch roofs, bedding for bred bugs (yield buff). |
| `cotton` / `plant_cloth` | T2 | farmed fiber crop | Cloth → clothing, beekeeper suit base. |
| `resin` / `tree_sap` | T2 | tapping trees | Glue, sealant, amber precursor, sticky bug-trap. |
| `bark` | T1 | trees | Tannin (leather), cheap shields, kindling. |

### Bug & animal-sourced (ecology core)

| Material | Tier | Source bug | Uses |
|----------|------|-----------|------|
| `silk` | T2 | spiders (orb/funnel/huntsman/wolf), moth cocoons | Cloth, nets, **silk-net pen**, ropes, mage robe. |
| `spider_silk_heavy` | T4 | big spiders (funnel/huntsman) | Strong netting, climbing gear, web-traps. |
| `arcane_silk` | T7 | spider boss | see §4. |
| `chitin` | T3 | beetles (rhino/stag), roaches (giant/hisser), big bugs | Refines to `chitin_plate`; light armor; bug-set gear. |
| `carapace` | T5 | GIANT bugs (giant beetle, giant roach, scorpion) | Heavy bug-armor, **carapace pen** panels (holds large bugs). |
| `stinger` | T4 | bees/wasps/scorpions | Stinger blades/spears (see weapons), needle ammo. |
| `mandible` | T4 | ants (colony)/stag beetle | Pincer blades, digging tools. |
| `bee_wax` / `honeycomb` | T3 | bees | Candles, wax seals, beekeeper gear, polish. |
| `royal_wax` | T5 | deep colony / hive boss | living_bronze input, premium candles, buff food. |
| `royal_jelly` | T6 | hive boss | see §4. |
| `bug_essence` (generic) | varies | any rare bug on release/sell | Enchanting dust input; "you ARE what you farm" loop. |
| `web` (raw) | T1 | any spider | Sticky trap component, cheap binding. |
| `leech_extract` | T4 | giant leech | Medicine, sticky adhesive, water-bug bait. |

### Earth, stone, mineral

| Material | Tier | Where | Uses |
|----------|------|-------|------|
| `stone` | T1 | surface + caves (`stone_block`) — already implied | **Stone pen walls**, stone tools (exist), masonry, furnace. |
| `hard_stone` | T2 | deeper caves (`hard_stone_block`) | Tougher walls, needs better pick; sturdier pens. |
| `clay` | T1 | designated zones (`clay_block`) | Bricks (exists), pottery, terracotta pens/pots. |
| `brick` | T2 | fired clay — already an item | Walls, kilns, **brick pen** (decent + cheap mid). |
| `sand` | T1 | desert/beach (`sand_block`) — already an item | Glass, mortar, sandbag pens (cheap, weak). |
| `sandstone` | T2 | desert (`sandstone_block`) | Desert masonry, walls, pens. |
| `crystal` | T5 | caves — already an item | Glow, magic, **crystal pen** (see §4 crystal_shard). |
| `bone` | T3 | `bone_pile` (caves) / big bug remains | Bone tools/weapons, bonemeal fertilizer, bone-set gear, spooky pens. |
| `ash` | T1 | burnt wood/coal | Lye/soap, fertilizer, gray dye. |
| `gravel` | T0 | caves | Cheap fill, paths, slingshot ammo. |

---

## 6. ⭐ PEN MATERIALS — the material → pen-tier ladder

> **Why this is the crucial section:** the whole pitch is "ALL bugs can be farmed if penned
> strongly enough, and some bugs are GIANT." A pen is a containment structure built from a
> material; **the material's tier sets the pen's containment strength**. Bigger/stronger bugs
> push or chew through weak pens and escape (or break out and attack). This ladder maps a
> material to roughly **what bug strength/size it can hold**.

### Containment-strength concept

Each pen tier has a **containment rating** that gates which bugs it can hold without breakout.
We tie it to the catch system's existing axes (`net_size` small/medium/large/trap_only, plus
HP for the big combat bugs):

- **Hold check ≈** pen tier vs bug "escape pressure" (a function of size + strength + whether
  it's hostile/HP-based). A pen below the bug's requirement → periodic **breakout attempts**
  (chew/ram), and eventually escape or pen damage.
- Pens can take **upgrades** (e.g., add a roof/lid for fliers, a lock, reinforcement bars).

### The ladder

| Pen tier | Material | Mat. tier | Holds (size / strength) | Example bugs | Notes / failure mode |
|----------|----------|-----------|--------------------------|--------------|----------------------|
| **P0 Twig pen** | `wood`/`fiber` twigs + twine | T0–T1 | Tiny, harmless, `net=small`, no HP | flies, fruitflies, mayflies, small mosquitoes, ladybugs, common snail | Anything bigger walks through. Cheapest starter. |
| **P1 Wood pen** | planks (`wood`) + nails | T1 | Small–medium calm bugs, `net=small/medium`, low HP | bees, paper wasps, common beetles, moths, fireflies, crickets/locusts | Hostile or strong bugs chew out over time. Needs lid for fliers. |
| **P2 Reinforced wood / Hardwood pen** | `hardwood`/`ironbark` + iron bracing | T2 | Medium bugs incl. mildly hostile, `net=medium` | stag beetle, rhino beetle (small), big spiders (orb/wolf), roach common, dragonflies | Giant or high-HP bugs still break out. |
| **P3 Brick / Stone pen** | `brick`/`stone`/`sandstone` masonry | T2 | Medium-heavy, diggers, `net=medium`, moderate HP | ants (colony), centipedes, scorpions (small/bark), hisser roach | Walls stop chewing; fliers need mesh roof; giants ram through. |
| **P4 Iron cage** | `iron_bar` bars | T2–T3 | Strong/hostile medium bugs, early `net=large`, mid HP | desert scorpion, huntsman/funnel spider, giant ladybug, large beetles | First "real" cage. Bars stop most chewing; very large bugs bend them. |
| **P5 Steel cage** | `steel_bar` | T3 | Large + aggressive, `net=large`, higher HP | giant beetle (rhino/stag giant), giant roach, emperor scorpion, giant strider | Workhorse big-bug pen. Hardsteel upgrade for the largest. |
| **P6 Reinforced / Hardsteel / Carapace pen** | `hardsteel_bar` / `carapace` panels | T4–T5 | GIANT bugs, high HP, strong ram | giant dytiscid, giant leech, atlas/luna giants, giant mayfly, big colony soldiers | Made partly FROM giant-bug carapace — thematic. Anchored to ground. |
| **P7 Crystal pen** | `crystal_shard` lattice / `diamond_cut` mesh | T5–T6 | Huge + special (glow/venom/burrow), very high HP | glow/firefly giants, venomous giants, "shimmer" rares, mini-bosses | Translucent showpiece; also dampens special abilities (venom/light). |
| **P8 Alloy fortress pen** | `adamantite_plate` / `cobalt_steel` | T7–T8 | Boss-scale bugs, extreme HP/strength | hive boss, spider boss, colony queen, named giants | Fortress-grade; built into the ground; multi-cell footprint. |
| **P9 Arcane / Voidsteel containment** | `arcane_silk` + `voidsteel_bar` + `enchanted_dust` | T8–T9 | THE giant/legendary bosses, anything | endgame boss bugs, "world" bugs | Magically reinforced; suppresses breakout entirely; endgame sink. |

### Pen design notes / hooks

- **Size vs strength are separate.** A giant-but-docile bug needs a big but not super-strong
  pen (P5 by footprint); a small-but-furious hostile bug may need P4+ for its HP/aggression.
  Recommend the hold check use **max(size_tier, strength_tier)**.
- **Upgrades, not just rebuilds:** lid/mesh (contain fliers), lock (multiplayer theft), bedding
  (`straw`) for breeding-yield, feeder, name plaque. Lets a pen tier stretch one band.
- **Material thematics:** carapace pens come from giant bugs (farm one giant to pen the next),
  silk/arcane-silk pens from spiders, crystal pens from caves — every pen tier sources from a
  zone, pulling players through the world.
- **Breakout = content:** an escaped giant becomes a roaming hazard (great for multiplayer
  events) — reinforcing "pen it strongly enough or it gets out."

---

## 7. Material → progression summary (the spine)

```
Surface:   fiber/wood → hardwood/ironbark → living_wood
           clay → brick ; sand → glass ; plant_cloth → cloth gear
Caves:     copper/tin → bronze → iron → steel → silver/gold → platinum
           quartz → glass/lens ; crystal → crystal_shard ; geode → gems
Deep/colony: cobalt → mythril/adamant → orichalcum/adamantite → voidsteel(+meteorite)
Bugs:      web/silk → heavy silk/chitin → carapace → arcane_silk
           wax/honeycomb → royal_wax → royal_jelly ; essences → enchanted_dust/lumen
Pens:      twig → wood → reinforced/stone → iron → steel → carapace/hardsteel
           → crystal → alloy fortress → arcane/voidsteel
```

### Open questions / balance TODO
- Pick **mythril XOR adamant** per world, or allow both as parallel T7 (heavy vs light)?
- Exact **containment numbers** (escape pressure per bug) — tune once bug stats exist in
  `species` config.
- Is `coal`/`sulfur`/`saltpeter` a real **gunpowder** chain (for bug-launchers in weapons), or
  keep ranged ammo simple? (See `weapons.md` §ranged.)
- Should **glass terrariums** be a parallel "soft storage" for tiny bugs (display/sell) distinct
  from pens (farming/breeding)?
