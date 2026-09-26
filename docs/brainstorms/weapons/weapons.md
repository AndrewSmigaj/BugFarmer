# Weapons — Terraria-style Rarity Ladder

> **Status:** brainstorm / design bible. No code, no entity JSON, no art.
>
> **Grounding:**
> - Materials + tiers come from `../materials/ores_metals.md` (the tier→color table is shared).
> - Combat ties into `docs/product/architecture/architecture_bugs.md`: most bugs are caught via **condition
>   meters** (calm/stunned/distracted) or by **weakening to HP=0** then netting. So "weapons"
>   here are mostly **subdue/weaken tools** that fill the `damage`/`stun` path, plus the nets
>   themselves. A few are pure damage for hostile bugs (bees/wasps/scorpions/giant beetle attack).
> - Existing tools to respect: `small_net`, `large_net` (add `medium`), `calm_spray`, and the
>   pickaxe/axe ladders (wood→stone→copper→iron) in `nakama/data/entities/items.json`.

**Design intent:** MANY weapons, spread across a colored rarity ladder. Mix of **craftable**
(from the materials doc) and **rare finds / boss-bug drops**. Each entry: short name, one-line
description, **rarity**, rough **damage/feel**, and **bug/ecology synergy** where relevant.

---

## Rarity ladder (8 named tiers + colors)

Shared with materials/armor. Color = the inventory name-tint.

| # | Rarity name | Color | Typical source | Material band |
|---|-------------|-------|----------------|---------------|
| 1 | **Common** | White | craft from wood/stone/copper | T0–T1 |
| 2 | **Uncommon** | Blue | bronze/iron, simple bug parts | T2 |
| 3 | **Rare** | Green | steel/silver, refined chitin | T3 |
| 4 | **Superior** | Orange | hardsteel/gold, stinger/venom | T4 |
| 5 | **Exquisite** | Light Red | crystal/electrum, big-bug drops | T5 |
| 6 | **Heroic** | Pink | cobalt/obsidian/living-bronze | T6 |
| 7 | **Mythic** | Light Purple | mythril/adamant/orichalcum, mini-boss | T7 |
| 8 | **Legendary** | Yellow→Rainbow | voidsteel/arcane, boss-bug drops | T8–T9 |

Two cross-cutting **damage flavors** that matter for bugs:
- **Subdue** (non-lethal): fills stun/calm/distract meters → catch alive (best sell value).
- **Lethal** (HP damage): weakens to HP=0; needed for hostile/giant bugs, but a killed bug may
  drop parts instead of being caught whole (lower live-sell value, higher material yield).
Many weapons can do both depending on a **toggle or an attached reagent** (e.g., venom = lethal,
smoke-coating = subdue).

---

## A. Melee

### Swords (fast, balanced)

| Weapon | Rarity | Damage/feel | Bug/ecology synergy |
|--------|--------|-------------|---------------------|
| `copper_shortsword` | Common | Low, fast pokes | Starter. Lethal only. |
| `bronze_sword` | Uncommon | Low-mid, quick | Cheap upgrade. |
| `iron_sword` | Uncommon | Mid | The reliable early blade. |
| `steel_longsword` | Rare | Mid-high, longer reach | Good vs medium hostile bugs. |
| `silver_rapier` | Rare | Mid, fast crits | **Bonus vs "creeping"/swarm bugs** (silver theme). |
| `chitin_saber` | Rare | Mid, very fast | Crafted from beetle chitin; **light, +catch on subdued**. |
| `stinger_blade` | Superior | Mid + **venom DoT** | From bee/wasp/scorpion stingers; venom = lethal flavor. |
| `obsidian_cleaver` | Heroic | High, slow swing | Sharp; bleeds big bugs. |
| `cobalt_saber` | Heroic | Mid-high, fastest | Speed weapon for swarms. |
| `mythril_blade` | Mythic | High, enchantable | Holds a reforge (e.g., +stun on hit). |
| `mandible_dagger` | Superior | Low dmg, **high stun** | Ant/stag-beetle jaws; SUBDUE weapon — knock bugs out to net. |
| `orichalcum_edge` | Mythic | High + minor AoE | Pink magic blade. |
| `voidfang` | Legendary | Very high, **lifesteal-ish "drain"** | Boss drop; drains bug essence on kill. |
| `living_wood_blade` | Exquisite | Mid, **self-repairs** | Nature-set synergy; never degrades. |

### Spears & polearms (reach, thrust)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `wood_spear` | Common | Low, long reach | Poke from outside a pen safely. |
| `iron_pike` | Uncommon | Mid, reach | Keep hostile bugs at range. |
| `steel_halberd` | Rare | Mid-high, sweep | Hits a small arc — multi-bug. |
| `stinger_lance` | Superior | Mid + venom, long | Stinger-tipped; great vs scorpions. |
| `crystal_glaive` | Exquisite | High, glow | Crystal edge; bonus vs cave bugs. |
| `adamant_partisan` | Mythic | High, very long | Anti-giant: reach keeps you out of stomp range. |

### Hammers & maces (slow, **stun-heavy** → ideal SUBDUE tools)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `stone_maul` | Common | Low dmg, **good stun**, slow | Starter subdue; knock a beetle out, then net it. |
| `lead_mallet` | Uncommon | Low dmg, **heavy stun** | Weighted — best stun-per-hit early. |
| `iron_warhammer` | Rare | Mid, high stun | Reliable knock-out for medium bugs. |
| `hardsteel_maul` | Superior | High, big stun | Stuns giants for a window. |
| `cobalt_hammer` | Heroic | Mid, fast stun | Faster swing = chain-stun. |
| `gravel_flail`→see flails | — | — | — |

### Flails (swingy, area)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `pebble_flail` | Common | Low, awkward arc | Junk-tier fun. |
| `chain_morningstar` | Uncommon | Mid, AoE-ish | Crowd small swarms. |
| `honeycomb_flail` | Rare | Low dmg, **sticky = applies "slowed"** | Wax/comb head; slows fleeing bugs so net lands. |
| `meteor_flail` | Mythic | High, ranged loop | Meteorite head; minor burn. |

### Scythes (wide sweep — anti-swarm)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `harvest_scythe` | Common | Low, **wide sweep** | Doubles as crop tool; clips many tiny bugs. |
| `steel_warscythe` | Rare | Mid, wide arc | Anti-swarm crowd control. |
| `reaper_scythe` | Heroic | High, big arc + reach | Bone/obsidian; spooky-set synergy. |
| `mantis_scythe` | Legendary | Very high arc | **Boss drop (giant mantis)**; signature sweep weapon. |

---

## B. Ranged

> Ranged is great for **fliers** (dragonflies, moths, bees) and for applying subdue from
> distance. Optional **gunpowder chain** (`coal`+`sulfur`+`saltpeter` from materials doc) gates
> the louder weapons; bows/slings/blowguns need no powder.

### Bows & slings

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `sling` | Common | Low, uses gravel/pebbles | Cheapest ranged; knock bugs off plants. |
| `wood_shortbow` | Common | Low-mid | Starter bow. |
| `hardwood_longbow` | Uncommon | Mid, charged shots | Reach for high fliers. |
| `ironbark_recurve` | Rare | Mid-high | Naturally tough wood bow. |
| `silver_hunterbow` | Superior | Mid, **fast vs swarms** | Silver-tipped arrows; anti-creep. |
| `crystal_bow` | Exquisite | High, glowing arrows | Lights up cave shots. |
| `living_wood_bow` | Heroic | Mid, **regrows arrows** (limited) | Nature-set; eco-friendly ammo. |
| `void_recurve` | Legendary | Very high, homing-ish | Boss drop; arrows curve to nearest bug. |

**Arrow/ammo types (subdue vs lethal):** `stone_arrow` (lethal), `tranq_arrow` (stun, +chitin),
`smoke_arrow` (calm AoE — beekeeping at range), `bait_arrow` (sticks bait to a spot to lure),
`net_arrow` (rare: fires a mini-net to catch at range).

### Blowguns (quiet, **subdue-focused**)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `reed_blowgun` | Common | Tiny dmg, **applies stun/calm darts** | Quiet → doesn't alert nearby swarms. Great early subdue. |
| `bamboo_blowpipe` | Uncommon | Low, faster darts | — |
| `venom_blowgun` | Superior | **Venom darts (lethal)** or tranq darts | From venom_gland; toggle lethal/subdue. |
| `glass_dartgun` | Rare | Low, **fragile capsule darts** | Glass capsules carry smoke/calm payload. |

### Bug-launchers & oddball ranged (gunpowder chain)

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `pea_popper` | Uncommon | Low, rapid | Powder toy gun; pelts swarms. |
| `smoke_cannon` | Rare | No dmg, **big calm AoE** | Beekeeping artillery — calm a whole hive to mass-catch. |
| `bug_launcher` | Heroic | Loads a CAUGHT bug as ammo! | **Signature ecology weapon:** fire an angry wasp/scorpion at enemies; consumes the bug. |
| `firefly_flarergun` | Exquisite | Low dmg, **lights area + lures night bugs** | Uses lumen_essence; doubles as a lure. |
| `stinger_repeater` | Mythic | Mid, rapid venom needles | Crafted from many stingers; sustained DoT. |
| `meteor_blunderbuss` | Mythic | High, spread + burn | Meteorite shot; loud, alerts bugs. |
| `arc_railsling` | Legendary | Very high, pierce | Voidsteel/orichalcum coil; endgame ranged. |

---

## C. Thrown

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `throwing_pebble` | Common | Tiny | Free, infinite-ish ammo. |
| `bone_shuriken` | Uncommon | Low, fast | From bone; cheap volume. |
| `smoke_bomb` | Uncommon | No dmg, **calm AoE cloud** | Mass-subdue bees/wasps; also escape tool. |
| `bait_bola` | Rare | No dmg, **lures + tangles** | Distract + slow a fleeing bug (ant/beetle). |
| `tangle_net_ball` | Rare | No dmg, **mini-net catch** | Throw to catch a single medium bug at range. |
| `venom_vial` | Superior | **Poison puddle (lethal DoT)** | Area denial vs giant bugs; from venom_gland. |
| `sticky_resin_pod` | Rare | No dmg, **roots bug in place** | Tree-resin; pin a flier so you can net it. |
| `firebomb` | Heroic | High AoE burn | Sulfur/oil; clears nests (but burns drops). |
| `crystal_grenade` | Exquisite | High shard burst | — |
| `hive_bomb` | Legendary | **Summons your own angry swarm on impact** | Boss-tier; releases bred wasps to attack. |

---

## D. Bug / nature / magic oddities (the flavor pile)

These lean into the "you farm bugs, so your gear IS bugs" identity. Mostly Rare+; many are
boss-bug drops or craft from rare organics in the materials doc.

| Weapon | Rarity | Damage/feel | Synergy |
|--------|--------|-------------|---------|
| `web_shooter` | Rare | No dmg, **fires sticky web → roots/slows** | From silk; pin bugs, swing/cross gaps, set web-traps. |
| `silk_whip` | Superior | Mid, **pulls bug toward you** | Yank a flier down to net range. |
| `wasp_summon_horn` | Heroic | Summons allied wasps that sting enemies | Consumes bred wasps; temporary swarm pet. |
| `bee_scepter` | Exquisite | Summons bees that home on target | Calmer cousin of the horn; also pollinates crops. |
| `fungal_staff` | Rare | Lobs **spore bolts (poison + slow)** | From glow/cave mushrooms; cave-bug synergy. |
| `spore_puffer` | Uncommon | No dmg, **sleep/calm spore cloud** | Puffball-based subdue. |
| `lumen_wand` | Exquisite | Mid light-bolts, **lights area** | From lumen_essence; blinds & lures night bugs. |
| `crystal_focus_staff` | Heroic | High arcane bolts | Quartz/crystal focus; mage-set core. |
| `enchanted_codex` | Mythic | Multi-bolt magic, scaling | Uses enchanted_dust; spell weapon. |
| `royal_jelly_censer` | Mythic | No dmg, **mass-calm + heals you** | Hive boss drop; ultimate beekeeping tool. |
| `antlion_funnel_trap` | Superior | Placed trap, **pulls walking bugs in** | Ant-colony themed; passive catch for ground bugs. |
| `stinger_storm` (relic) | Legendary | Orbiting stinger swarm, auto-attacks | Boss drop; passive DPS + chip-stun. |
| `the_collector` (relic net-blade) | Legendary | Hybrid: damages AND auto-nets weakened bugs | Capstone bug-farmer weapon; one tool to weaken + catch. |

---

## E. Nets as "weapons" (the catch tools — reconcile with existing items)

Nets aren't damage, but they ARE the win condition, so they belong on the ladder. Reconcile
with `small_net`/`large_net` already in items.json (add medium + higher tiers).

| Net | Rarity | Net size band | Notes |
|-----|--------|---------------|-------|
| `small_net` *(exists)* | Common | small | Flies, fruitflies, tiny calm bugs. |
| `medium_net` *(add)* | Uncommon | medium | Beetles, bees, spiders. |
| `large_net` *(exists)* | Rare | large | Giant beetle, big spiders, scorpions. |
| `reinforced_net` (steel rim) | Superior | large + faster | Less escape on partial overlap. |
| `silk_net` | Rare | medium/large, wider | From silk; bigger catch radius. |
| `crystal_net` | Exquisite | large, **catches special bugs** | Holds glow/venom bugs nets normally fail on. |
| `arcane_net` | Legendary | trap_only-tier giants | Endgame: the only net that bags the biggest bosses. |

> Note: per the catch system, **net size must MATCH the species' `net_size`**, and most bugs
> still need the right **condition** (calm/stun/HP) first — so the weapons above (subdue tools,
> stun hammers, smoke gear) are what *make* a bug nettable. Weapons + nets are a combo, not
> either/or.

### Open questions / balance TODO
- Do we commit to the **gunpowder chain**, or keep ranged powder-free for simplicity?
- **Lethal vs subdue** tradeoff numbers: how much live-sell value lost on a kill vs material gain?
- Should **`bug_launcher` / `wasp_summon_horn`** consume from your pens (real cost) or a separate
  ammo pool? Consuming pens is more thematic but harsher.
- Which weapons are **craftable** vs **boss-only**? Current draft: Legendary + most relics are
  boss/rare drops; everything else craftable from the materials doc.
