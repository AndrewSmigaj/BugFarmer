# Armor & Clothing — Five Slots, Sets & Bonuses

> **Status:** brainstorm / design bible. No code, no entity JSON, no art.
>
> **Grounding:**
> - Materials + tiers from `../materials/ores_metals.md` (shared tier→rarity color table).
> - Rarity ladder mirrors `../weapons/weapons.md` (Common→Legendary).
> - Bonus types tie to real systems in `docs/product/architecture/architecture_bugs.md` (catch chance,
>   condition meters, net size, sell price) and the farming/mining loops.

**Design intent:** equipment for **FIVE slots** — **helmet, body (chest), arms
(gauntlets/gloves), legs (pants), shoes/boots** — with MANY options across materials, plus
themed **SETS** that grant a set bonus when worn together. Sets cover **combat AND
utility/farming/bug-handling**. Many neat **non-metal** pieces. Rarity ladder throughout.

---

## 0. Bonus vocabulary (what a piece can give)

To keep it consistent across pieces and sets:

| Bonus | Meaning |
|-------|---------|
| **DEF** | Damage reduction vs hostile bugs (bees, wasps, scorpions, giant beetle). |
| **catch_chance** | Higher % of a swarm caught / less escape on partial net overlap. |
| **subdue+** | Condition tools (smoke/stun/bait) fill the meter faster. |
| **safe_handling** | Reduces or negates hostile-bug retaliation (stings, venom). |
| **farm_yield** | Crop / breeding-pen output bonus. |
| **mine_speed / mine_tier** | Faster mining / can mine one tier harder rock. |
| **move_speed** | Walk/run speed. |
| **light** | Emits light radius (caves/night). |
| **luck** | Better rare drops / geode rolls / rare-bug spawn near you. |
| **pen_strength** | Pens you build/maintain hold one effective tier higher (passive). |
| **carry** | Inventory/stack bonus. |
| **stealth** | Bugs notice you later (bigger catch window before flee). |

Pieces give small single bonuses; **full SET = a bigger signature bonus** (the reason to commit
to a theme).

---

## 1. Individual pieces by slot (the menu)

Rarity in (). Most are craftable from the materials doc; a few rare finds noted.

### Helmet

| Piece | Rarity | Slot bonus | Notes |
|-------|--------|-----------|-------|
| `straw_hat` | Common | +farm_yield (small), sun | Non-metal classic; farmer starter. |
| `leather_cap` | Common | +DEF (tiny) | Bark-tanned. |
| `mushroom_cap_helm` | Uncommon | +light (faint), spore resist | Non-metal, from big caps; cave-cute. |
| `miners_helmet` | Uncommon | **+light**, +mine_speed | Lamp on front; caves. |
| `beekeeper_veil` | Uncommon | **+safe_handling**, +subdue(calm) | Netted hood; bee/wasp safety. |
| `wizard_hat` | Rare | +magic dmg, +subdue(spore/smoke) | Non-metal, pointy; mage core. |
| `iron_helm` | Uncommon | +DEF | Standard metal. |
| `chitin_helm` | Rare | +DEF, +catch_chance | From beetle chitin; light. |
| `goggles` (quartz_lens) | Rare | **reveals bug stats / weak points** | Inspect-on-sight; mining glare resist. |
| `steel_greathelm` | Rare | +DEF (high) | Tanky. |
| `feathered_explorer_hat` | Superior | +move_speed, +luck (small) | Ranger/explorer flavor. |
| `crystal_circlet` | Exquisite | +magic, +light | Glowing. |
| `hive_crown` | Legendary | +safe_handling (full), summons-friendly | Hive boss drop. |
| `void_visor` | Legendary | +DEF, +stealth | Endgame. |

### Body (chest)

| Piece | Rarity | Slot bonus | Notes |
|-------|--------|-----------|-------|
| `cloth_shirt` | Common | — (cosmetic base) | Starter. |
| `leather_vest` | Common | +DEF (small) | — |
| `silk_robe` | Uncommon | +subdue, +move_speed | Non-metal; mage/handler base. |
| `padded_gambeson` | Uncommon | +DEF | Cloth armor. |
| `iron_chestplate` | Uncommon | +DEF | — |
| `beekeeper_suit_top` | Rare | **+safe_handling (big)** | Sealed; the bee/wasp answer. |
| `chitin_cuirass` | Rare | +DEF, +catch_chance | Bug-set core. |
| `steel_breastplate` | Rare | +DEF (high) | — |
| `ranger_jerkin` | Superior | +ranged dmg, +move_speed | — |
| `carapace_plate` | Exquisite | **+DEF (very high)**, +pen_strength | From giant-bug carapace; tanky + thematic. |
| `wizard_robe` | Rare | **+magic dmg/regen** | Non-metal; mage core. |
| `living_wood_mantle` | Heroic | +DEF, +farm_yield, self-repair | Nature-set. |
| `mythril_hauberk` | Mythic | +DEF, enchant slot | — |
| `arcane_silk_robe` | Legendary | +magic (huge), +subdue | Spider-boss silk. |
| `voidsteel_aegis` | Legendary | +DEF (max) | Endgame combat. |

### Arms (gauntlets / gloves)

| Piece | Rarity | Slot bonus | Notes |
|-------|--------|-----------|-------|
| `cloth_wraps` | Common | — | Starter. |
| `leather_gloves` | Common | **+catch_chance (small)** | Grip — handle bugs better. |
| `gardening_gloves` | Uncommon | +farm_yield, +catch_chance | Farmer-set. |
| `bee_gloves` | Uncommon | +safe_handling | Padded against stings. |
| `iron_gauntlets` | Uncommon | +DEF, +melee | — |
| `silk_handler_gloves` | Rare | **+catch_chance (big)**, +subdue | Bug-handling specialist. |
| `chitin_bracers` | Rare | +DEF, +melee speed | Bug-set. |
| `miners_gloves` | Uncommon | +mine_speed | — |
| `electrum_gloves` | Superior | +luck, +light | Pretty + lucky. |
| `mythril_gauntlets` | Mythic | +DEF, enchant | — |
| `arcane_gloves` | Legendary | +magic, +web-handling | Cast-speed; web traps. |
| `titan_grips` (adamant) | Mythic | **+pen_strength (big)**, +carry | Wrestle giant bugs into pens. |

### Legs (pants)

| Piece | Rarity | Slot bonus | Notes |
|-------|--------|-----------|-------|
| `cloth_trousers` | Common | — | Starter. |
| `leather_leggings` | Common | +DEF (small) | — |
| `work_overalls` | Uncommon | +farm_yield, +carry | Farmer-set. |
| `beekeeper_trousers` | Rare | +safe_handling | Sealed cuffs. |
| `iron_greaves` | Uncommon | +DEF | — |
| `chitin_legs` | Rare | +DEF, +move_speed | Bug-set. |
| `silk_leggings` | Uncommon | +move_speed, +subdue | — |
| `ranger_breeches` | Superior | +move_speed, +ranged | Explorer/ranger. |
| `steel_legplates` | Rare | +DEF (high) | — |
| `carapace_greaves` | Exquisite | +DEF (very high) | Bug-tank. |
| `mythril_legguards` | Mythic | +DEF, enchant | — |
| `arcane_leggings` | Legendary | +magic, +move_speed | — |

### Shoes / boots

| Piece | Rarity | Slot bonus | Notes |
|-------|--------|-----------|-------|
| `bare_sandals` | Common | — | Starter. |
| `leather_boots` | Common | +move_speed (small) | Non-metal classic. |
| `straw_clogs` | Common | +farm_yield (tiny) | Farmer flavor. |
| `rubber_waders` | Uncommon | **water-walk/wade**, pond-bug access | Backswimmers, striders, dytiscids. |
| `mining_boots` | Uncommon | +DEF (small), no-slip on gravel | — |
| `silk_slippers` | Rare | +move_speed, +stealth | Quiet — bugs flee later. |
| `chitin_treads` | Rare | +move_speed, +DEF | Bug-set. |
| `spring_boots` | Superior | +jump/dash, +move_speed | Mobility. |
| `explorer_boots` | Superior | +move_speed, +luck | Ranger/explorer. |
| `lumen_boots` | Exquisite | +light trail, +move_speed at night | From lumen_essence. |
| `mythril_sabatons` | Mythic | +DEF, +move_speed | — |
| `voidstriders` | Legendary | +move_speed (max), short blink | Endgame. |

---

## 2. SETS (wear all five → set bonus)

Mix of combat and utility/farming/handling. Each lists pieces, the per-tier feel, and the
**signature set bonus**.

### Combat sets

**Iron Guard** *(Uncommon, T2)*
Iron helm / chestplate / gauntlets / greaves / mining boots.
- **Set bonus:** +DEF block chance; first hostile-bug hit each fight reduced. Cheap tank entry.

**Steel Sentinel** *(Rare, T3)*
Steel greathelm / breastplate / gauntlets / legplates / mining boots.
- **Set bonus:** big DEF; stagger-resist vs giant-bug rams. The "go fight giants" set.

**Chitin Carapace** *(Rare→Exquisite, bug-sourced)*
Chitin helm / cuirass / bracers / legs / treads (carapace upgrades at Exquisite).
- **Set bonus:** **+catch_chance AND +DEF** — the "fight-and-farm" hybrid. Light, fast.
  Thematic: armor made FROM the bugs you farm.

**Mythril Vanguard** *(Mythic, T7)* — full mythril, enchant slots on every piece.
- **Set bonus:** every piece's enchant active + cooldowns reduced; flexible endgame combat.

**Voidsteel Aegis** *(Legendary, T8–T9)* — voidsteel pieces, boss-tier.
- **Set bonus:** max DEF; immune to standard hostile-bug damage; only true giants threaten you.

### Utility / farming / handling sets

**Farmer's Kit** *(Common→Uncommon, non-metal-heavy)*
Straw hat / work overalls (or cloth shirt) / gardening gloves / work overalls legs / straw clogs.
- **Set bonus:** **+farm_yield** (crops + breeding pens), faster watering/harvest. Cozy start.

**Beekeeper Suit** *(Rare, the safe-handling set)*
Beekeeper veil / suit top / bee gloves / beekeeper trousers / mining boots.
- **Set bonus:** **full safe_handling** — bees/wasps/hornets don't retaliate; +subdue(calm) so
  you mass-catch hives. Essential for the bee-farm zone.

**Miner's Kit** *(Uncommon, the mining/light set)*
Miners helmet / leather vest / miners gloves / leather leggings / mining boots.
- **Set bonus:** **+light radius + +mine_speed + one mine_tier**; reveals nearby ore veins.
  The caves enabler.

**Explorer / Ranger** *(Superior, mobility + ranged)*
Feathered explorer hat / ranger jerkin / electrum gloves / ranger breeches / explorer boots.
- **Set bonus:** **+move_speed + +stealth + +ranged dmg**; bugs flee later → bigger catch window.
  For chasing fliers (dragonflies/moths) and covering ground.

**Wizard / Mage** *(Rare→Legendary, magic + spore subdue)*
Wizard hat / wizard robe (→arcane_silk_robe) / arcane gloves / arcane leggings / silk slippers.
- **Set bonus:** **+magic dmg & regen + +subdue (spore/smoke)**; staves/fungal weapons hit
  harder. Caves + magic-bug synergy.

**Lucky Set** *(Exquisite, the gambler)*
Crystal circlet / electrum/lumen accents / electrum gloves / silk leggings / explorer boots
(electrum/lucky-charm pieces).
- **Set bonus:** **+luck** — better geode rolls, rare-bug spawns near you, rare drops. Pairs with
  mining + bug-hunting.

**Handler's Garb** *(Rare, the bug-catch specialist)*
Goggles / silk robe / silk_handler_gloves / silk leggings / silk slippers.
- **Set bonus:** **max catch_chance + +subdue + reveals bug stats**; less escape on partial nets.
  The dedicated bug-catcher's outfit (light, no DEF).

**Pen-Keeper / Titan** *(Mythic, the containment set)*
Void visor / carapace_plate / titan_grips / carapace_greaves / mythril sabatons.
- **Set bonus:** **+pen_strength (big)** — your pens hold an effective tier higher AND breakout
  attempts are slower; +carry for hauling materials. The "I farm GIANTS" set.

**Spelunker's Glow** *(Exquisite, deep-cave kit)*
Mushroom_cap_helm or crystal circlet / living_wood_mantle / chitin bracers / chitin legs /
lumen_boots.
- **Set bonus:** **+light (large) + spore/poison resist + +luck in caves**; for the deepest
  colony layers and glow-bug hunting.

**Nature / Grove** *(Heroic, eco set)*
Feathered hat or mushroom helm / living_wood_mantle / leather/garden gloves / living_wood legs /
leather boots.
- **Set bonus:** **self-repairing gear + +farm_yield + crops/pens regen faster**; living_wood
  theme. Sustainable cozy-power.

---

## 3. Set bonus summary (pick your playstyle)

| Set | Rarity band | Headline bonus | Loop it serves |
|-----|-------------|----------------|----------------|
| Iron Guard | Uncommon | DEF block | early combat |
| Steel Sentinel | Rare | DEF + anti-giant stagger | fight giants |
| Chitin Carapace | Rare–Exquisite | DEF + catch_chance | fight-and-farm |
| Mythril Vanguard | Mythic | enchant synergy | endgame combat |
| Voidsteel Aegis | Legendary | damage immunity | boss combat |
| Farmer's Kit | Common–Unc. | farm_yield | crops/breeding |
| Beekeeper Suit | Rare | safe_handling + calm | bee/wasp farming |
| Miner's Kit | Uncommon | light + mine_speed/tier | caves |
| Explorer/Ranger | Superior | speed + stealth + ranged | chasing fliers |
| Wizard/Mage | Rare–Legend. | magic + spore subdue | magic-bug + caves |
| Lucky Set | Exquisite | luck | drops/geodes/rares |
| Handler's Garb | Rare | catch_chance + reveal | dedicated catching |
| Pen-Keeper/Titan | Mythic | pen_strength + carry | farming GIANTS |
| Spelunker's Glow | Exquisite | light + resist + cave luck | deep colony |
| Nature/Grove | Heroic | self-repair + farm regen | sustainable cozy |

### Open questions / balance TODO
- **Slot bonuses stacking with set bonus:** additive or does the set replace? (Lean additive but
  cap catch_chance/safe_handling near 100%.)
- **Mixing sets** for partial bonuses (2-piece / 4-piece breakpoints like Terraria) vs all-or-
  nothing 5-piece? 2/4/5 breakpoints give more build variety.
- **Cosmetic / vanity slots** so players keep the straw-hat look while wearing voidsteel?
- Do **utility bonuses** (farm_yield, pen_strength, luck) need a combat downside to avoid
  "always wear the farm set"? Maybe utility sets give little/no DEF (already drafted that way).
