# Potions, tonics and outfit sets in other games

Research for Bug Farmer (2026-10-01). Two questions:

- **A. Potions and other drinkable or usable consumables.** The old potion list has been dropped; a new set is to be
  designed from scratch out of real things (tonics, teas, salves, liniments, energy drinks, smelling salts...) whose
  effects can be game-logical. How do good games shape their potion and buff lists?
- **B. Outfit and armour sets beyond a metal ladder.** How do games give role sets (a mining set, a fishing set, a
  beekeeper set) and special armour, and what makes a role set worth wearing?

Rulings this research must respect (restated, with dates):

- A healing potion heals at once, then a short wait before another can heal the same player, as Terraria's potion
  sickness; other potions have no wait (D54, 2026-09-27).
- A meal heals slowly and gives one "fullness" boost at a time; a new meal replaces the last, as Stardew Valley
  (D54, 2026-09-27).
- Antivenom, a salve for sprays and acid, venom resistance and night sight exist; stronger bugs' venom makes stronger
  potions; the cauldron is the potion station (D54, 2026-09-27).
- No magic, 2126 science (D65); nothing from living mammals, birds, reptiles or amphibians; fish survive (D31, D32);
  no luck brews, no breathing underwater, no lamp oils, calming is per species (overview P16, accepted 2026-09-27).
- No hunger, tools never wear out, food doesn't spoil (D49, D50, D54).
- Each role has its own best gear and no single set is best at everything (2026-08-06).
- An outfit is drawn and worn as one whole set, not separate pieces (2026-08-05, tentatively confirmed 2026-09-26);
  accessory slots are separate (two in the prototype today).

Method: web search was not available this session. Wiki pages were fetched directly (MediaWiki `api.php?action=parse`
through curl, rendered to text by a small script): 44 game-wiki pages read in full, tables included, and 45 Wikipedia
articles fetched and checked for the specific real-world facts used in section 5. Every number below comes from a
page in the source table unless marked **unverified**. Fandom pages can't be opened directly (HTTP 402/403); the
non-Fandom wikis found for Core Keeper and Valheim were empty (corekeeper.wiki.gg) or closed (valheim.wiki.gg, HTTP
401), so those two Fandom wikis were read through the same MediaWiki API (sources 21-26 say so). Don't Starve was read
on its non-Fandom wiki.gg. No sub-agents were used (as asked), so the "cold critic" pass of the `thorough-research`
skill was done as a self-review: the numbers were re-checked against the saved page text, and the corrections are
already in.

Status: COMPLETE (research, 2026-10-01). Research only - nothing here is decided; section 5 is a menu for the owner.

---

## 1. Source table

| # | Source URL | What it shows | How it applies to us |
|---|---|---|---|
| 1 | https://terraria.wiki.gg/wiki/Potions | The four potion families (recovery, buff, flask, other); quick-buff / quick-heal keys; all potion buffs except flasks are lost on death | The family split and the one-key "drink my buffs" convenience |
| 2 | https://terraria.wiki.gg/wiki/Buff_potions | All 43 buff potions with ingredients, effect and duration (30 s-45 min), grouped Battle / Movement / Mining / Fishing / Misc | The reference list shape: one lever per potion, 2-4 ingredients each, durations by power |
| 3 | https://terraria.wiki.gg/wiki/Recovery_potions | Heal amounts 15-200, potion sickness 30-60 s per item, sources (crafted, bought, found, dropped) | The healing ladder and its wait, which D54 already copies |
| 4 | https://terraria.wiki.gg/wiki/Potion_Sickness | The wait is one debuff shared by every healing item; 25% shorter with certain accessories; the nurse can't remove it | Wait belongs to the person, not the bottle |
| 5 | https://terraria.wiki.gg/wiki/Flasks | 8 weapon coatings, 20 min each, only one at a time, kept through death | The model for a venom coating on blades |
| 6 | https://terraria.wiki.gg/wiki/Well_Fed | 3 food-buff tiers (all-stat bonuses), 1-48 min, only one at a time, latest replaces | The "one fullness boost" rule we already chose |
| 7 | https://terraria.wiki.gg/wiki/Buffs | 44 buff slots; buffs lost on death except flasks; furniture buffs (click a station for a buff) and nearby-object buffs (campfire, sunflower, honey) | Buffs from places and furniture, not only bottles |
| 8 | https://terraria.wiki.gg/wiki/Other_potions | Teleport / recall / wormhole potions | Out of scope for us (no teleporting brews), noted only |
| 9 | https://stardewvalleywiki.com/Buffs | One food buff + one drink buff at a time; only speed, max energy and luck can add across the two; special buffs and debuffs sit apart; all buffs clear on sleep; immunity resists debuffs | The cleanest "one meal + one drink" rule; a reason for a separate drink slot |
| 10 | https://stardewvalleywiki.com/Cooking | ~81 recipes, 39 with a buff; buffs are farming / fishing / mining / foraging skill, attack, defence, max energy, speed, luck, pickup radius; 3.5-17 min | Gathering-skill food buffs are the genre norm; fishing is the most common buff |
| 11 | https://stardewvalleywiki.com/Coffee | Coffee +1 speed 1 min 23 s; espresso 4 min 12 s; a drink, so it stacks with a meal | A real energy drink as the speed lever |
| 12 | https://stardewvalleywiki.com/Energy_Tonic , /Muscle_Remedy , /Life_Elixir , /Oil_of_Garlic | Clinic remedies (energy +500; clears exhaustion), a full-heal elixir from four mushrooms, a garlic drink that stops weaker monsters spawning 10 min | Real-world remedies sold by a doctor; a repellent drink |
| 13 | https://stardewvalleywiki.com/Footwear | 18 boots with only defence and immunity (1-8); tailoring moves one pair's stats onto another's look | Boots as a small, readable stat slot; separate look from stats |
| 14 | https://stardewvalleywiki.com/Hats | Hats are purely cosmetic, unlocked mostly by achievements | Cosmetic rewards for goals, not power |
| 15 | https://necessewiki.com/Potions | 3 healing potions (flat + % of max, 30 s wait), 3 mana potions, 35 buff potions (mostly 5 min; building 30 min; passive 15 min), "greater" versions made from the base potion at a later alchemy table | A second, independent copy of the Terraria shape; better stations make stronger versions of the same potion |
| 16 | https://necessewiki.com/Food , /Hunger , /Buffs | Food in three qualities: simple 4 min one small stat; fine 8 min (coffee 30-45 min); gourmet 12-20 min, 2-5 stats; area buffs from banners and campfires | Quality tiers of one food buff; coffee as a long movement-speed drink; placed area buffs |
| 17 | https://necessewiki.com/Armor | 35 sets on the page (more on an incursion-tier page) with set bonuses; one body with a choice of head piece decides the class; active "press V" set abilities on cooldowns; late upgrades bring all sets to similar defence so the set bonus decides | The strongest model for "a set is a job", and for keeping old role sets useful |
| 18 | https://terraria.wiki.gg/wiki/Armor | 70 sets (36 early, 34 late); full-table defence and bonuses; head-piece variants per class; vanity slots; single special pieces; mixing pieces late game | Role sets beside the metal ladder, with numbers |
| 19 | https://terraria.wiki.gg/wiki/Aggro | "Aggro" shifts which player enemies pick in multiplayer: distance minus aggro | The mechanism behind a "draw the bugs to me" tank outfit, and its opposite |
| 20 | https://minecraft.wiki/w/Potion , https://minecraft.wiki/w/Brewing | ~20 effect potions from one base; five modifiers (stronger, longer, thrown, lingering cloud, inverted); stronger = shorter; re-drinking resets, never adds; a mixed-effect potion (-60% speed, -60% damage taken) | Modifiers as a way to get many potions from few recipes; the clearest stacking rule |
| 21 | https://core-keeper.fandom.com/wiki/Potions (read through the wiki's MediaWiki API, since Fandom pages block direct fetching) | 2 healing potions (+30% / +40% health, 5 s wait); ~20 drinks and potions with short strong effects (20 s-1 min): +30% damage, +58 armour, cure poison, a risky +40% damage / +40% damage taken | Potions short and strong, food long and broad; a cure-only potion; a deliberate gamble potion |
| 22 | https://core-keeper.fandom.com/wiki/Food , /Cooking | 2 ingredients in a cooking pot make one meal; the meal keeps the best of each effect; heal-over-time 20 s, buffs ~10 min; rarer (golden) ingredients from a gardening skill; a few foods give permanent max health once | A two-ingredient meal rule that makes thousands of meals from 74 ingredients; "best of each effect" merge |
| 23 | https://core-keeper.fandom.com/wiki/Armor , /Set_bonus | 56 sets + 30 single pieces; set bonuses at 2, 3 and 5 pieces, some counting rings and necklaces; many conditional bonuses (after mining a wall, standing still, at full or low health, beside water) | Behavioural set bonuses; role sets for cooking, fishing, pets, explosives, mining, a larva disguise, acid immunity |
| 24 | https://valheim.fandom.com/wiki/Mead (via the wiki's API) | 21 meads: brewed as a base, then fermented; per-group cooldowns (healing meads share 2 min); resistances 10 min; carry weight +250; anti-mosquito concoction; x2 taming speed; a trade-off "berserkir" mead | Group cooldowns; a real two-step brew; carrying, repellent and taming levers |
| 25 | https://valheim.fandom.com/wiki/Food , /Status_effects | Three different foods at once, each fading as digested; "rested" from shelter and fire; fishing hat +20 fishing | The road we did not take (three food slots); home-comfort buff |
| 26 | https://valheim.fandom.com/wiki/Armor | Each biome has a light set (skill bonus, resistances and a weakness) and a heavy set (-5% movement per piece); armour upgrades +2 per level; capes with one utility each | Light role set vs heavy armour as a standing trade-off; a bug-carapace heavy set exists |
| 27 | https://dontstarve.wiki.gg/wiki/Armor/DS , /Dress_Tab , /Beekeeper_Hat , /Gas_Mask , /Bush_Hat , /Miner_Hat , /Pith_Hat | Armour as % damage absorbed with big trade-offs (marble suit 95% but -30% speed); single-threat gear (beekeeper hat only stops bees); chitin ant-disguise suit and mask; gas mask, bush-hat hiding, headlamp fuelled by fireflies | The cleanest real-world role gear: one threat, one item; disguise among a species |
| 28 | Wikipedia (read through its API, 2026-10-01): Chitosan, Smelling salts, Calamine, Calamine (mineral), Oral rehydration therapy, Activated carbon, Liniment, Insect repellent, Bee smoker, Hermetia illucens, Diamphidia, Vitamin A deficiency, Carrot, Anti-reflective coating, Antivenom, Allergen immunotherapy, Royal jelly, Isoamyl acetate, Caffeine, Sodium bicarbonate, Uropygi, Urticating hair, Salammoniac, Pheromone trap, Spider silk, Shellac, Bombardier beetle, Millipede, Firefly, Eugenol, Salicin, Magnesium carbonate, Zinc oxide, Myrmecophily, Ephedra (medicine), Propolis, Bee sting, Fire ant, Formic acid, Black garden ant, Dragonfly, Bulletproof vest | The real-world facts behind each candidate in section 5 (what the remedy is, what it really does, what it is made from) | Every "real basis" line in section 5 cites one of these; anything not checked there is marked **unverified** |

---

## 2. Potions and consumables, per game

### 2.1 Terraria (terraria.wiki.gg, read 2026-10-01)

**The list shape.** Four families: recovery potions (heal now), buff potions (a timed effect), flasks (a weapon
coating) and a handful of "other" potions (teleport, recall). Food is a fifth, separate family. Potions are found in
chests and pots, dropped by enemies, bought from shopkeepers, or made at a placed bottle / alchemy table (sources 1, 3).

**Healing (source 3, 4).** Twelve healing items heal 15 to 200 at once: mushroom 15, bottled water 30, lesser healing
potion 50, strange brew 70-120, bottled honey 80, eggnog 80, restoration potion 90, healing potion 100, honeyfin 120,
greater healing potion 150, jungle juice 180, super healing potion 200. Every one of them starts the same
**potion sickness** debuff: 60 s for the real potions, 30-45 s for the weak ones (mushroom 30, bottled water 45,
restoration 45, eggnog 40, strange brew 40-70). While sick, no healing item works. So the wait is a property of the
person, shared across all healing items, and weak heals have shorter waits. A few accessories cut the wait by 25%
(not stacking). The healing ladder is a craft chain: lesser potion + glowing mushroom = healing potion; greater + rare
fragments = super.

**Buff potions (source 2, 7)** — 43 of them (two, Love and Stink, are thrown at someone else); each changes **one**
thing. By the wiki's own grouping:

| Group | Count | Examples (effect, duration) |
|---|---|---|
| Battle | 20 | Ironskin +8 defence 8 min; Endurance -10% damage taken 4 min; Regeneration +2 HP/s 8 min; Wrath +10% damage 4 min; Rage +10% crit 4 min; Lifeforce +20% max life 8 min; Thorns reflects melee damage 8 min; Titan +50% knockback 8 min; Warmth -30% damage from cold enemies 15 min; Hunter shows enemies 8 min; Dangersense shows traps 10 min; Battle (more enemies) 7 min; Calming (39% fewer spawns) 12 min |
| Movement | 5 | Swiftness +25% move speed 8 min; Featherfall 10 min; Flipper (swim) 8 min; Water walking 10 min; Gravitation 3 min |
| Mining | 3 | Mining +25% mining speed 10 min; Spelunker shows ore and treasure 5 min; Shine (the player glows) 10 min |
| Fishing | 3 | Fishing +15 fishing power 8 min; Sonar (see what is biting) 8 min; Crate (crate chance 10% -> 25%) 4 min |
| Miscellaneous | 12 | Builder +25% placing speed and +1 reach 45 min; Night Owl (night vision) 10 min; Obsidian Skin (lava immunity) 6 min; Gills 4 min; Invisibility 3 min; Biome Sight 5 min; three Luck potions 5/10/15 min; Love and Stink (thrown) 30 s |

Patterns in the numbers:
- **Duration follows power.** The strongest combat buffs (Wrath, Rage, Endurance, Magic Power, Inferno) last
  4 minutes; ordinary ones 8 minutes; most exploration ones 10 minutes (Spelunker 5); Warmth 15; the Builder potion
  45 minutes because it is a pure convenience.
- **Small recipes.** Every buff potion is bottled water + 2-4 ingredients (26 of 43 use just 2), usually one herb plus
  one material that "explains" the effect: Ironskin = iron ore; Mining = antlion mandible; Spelunker = gold ore;
  Warmth = a cold fish; Hunter = shark fin; Dangersense = cobweb. That link between ingredient and effect makes
  recipes guessable.
- **Many can run at once** (44 buff and debuff slots in all); a buff is either on or off, and quick-buff (one key)
  drinks one of each potion whose buff isn't already running. Whether re-drinking an active potion resets or adds
  time is not stated on these pages (**unverified**). All potion and food buffs are lost on death; flask coatings
  are not.
- **Information potions are a real category**: Hunter, Dangersense, Spelunker, Sonar, Biome Sight, Night Owl, Shine
  show the player something rather than make them stronger.

**Flasks (source 5).** Eight weapon coatings made at a separate imbuing station: a melee or whip hit inflicts poison,
fire, acid venom, confusion, lowered defence, or more coin drops. Each lasts 20 minutes, only **one** can be active
(a new one replaces the old), and they **survive death**. Recipes: bottled water + one material (a stinger makes the
poison flask; vial of venom makes the venom flask).

**Food (source 6).** Three tiers of one all-round buff: Well Fed (+2 defence, +5% damage, +2% crit, +5% melee speed,
+20% move speed, +5% mining speed), Plenty Satisfied (x1.5 of that), Exquisitely Stuffed (x2). Lasts 1-48 minutes
by food. **Only one can be active; the most recently eaten replaces it.** In Expert mode, natural health regeneration is
only full while one is active. Food is the long, broad, cheap buff; potions are short, narrow and strong.

**Buffs from places (source 7).** Some buffs come from furniture or nearby objects rather than bottles: right-click a
sharpening station (+12 armour penetration for melee), an ammo box, a crystal ball, a slice of cake (+20% move and
mining speed, 2 min); stand near a campfire (+0.5 HP/s regeneration), a heart lantern (+1 HP/s), a sunflower (+10%
speed, fewer spawns), a peace candle (fewer spawns), or sit in honey (+1 HP/s, natural regeneration x3). One more
station, the alchemy flask, makes every potion drunk afterwards last 20% longer.

### 2.2 Stardew Valley (stardewvalleywiki.com, read 2026-10-01)

**The list shape.** Stardew has almost no "potions": buffs come from **food and drink**. Of about 81 cooking recipes,
39 give a buff (source 10). Counting buff lines across those 39: fishing 10, luck 7, defence 7, farming 6, max energy 6,
mining 6, speed 5, foraging 4, pickup radius ("magnetism") 3, attack 2. So most food buffs serve **work** (gathering
skills, energy, speed), not fighting. Values are small (+1 to +4 skill levels, +30 to +50 max energy, +1 speed) and
durations run 3 min 30 s to 16 min 47 s of real time; all buffs clear when the player sleeps (source 9).

**The stacking rule (source 9) — the most useful single rule found.**
- Exactly **one food's buffs and one drink's buffs** can be active. A new food wipes the old food's buffs but not the
  drink's; a new drink replaces the old drink but leaves the food. Food with no buff leaves buffs alone.
- Only three stats come from both sides and so add up: speed (coffee, espresso, cola +1, green tea +0.5, on top of a
  meal's +1), max energy (green tea +30 on top of a meal's +30 to +50) and luck (ginger ale +1).
- **Special effects sit apart**: Oil of Garlic, Monster Musk, the debuff-immunity of Squid Ink Ravioli, and ring
  procs each run on their own, one instance each, untouched by food or drink.
- Debuffs from enemies (burnt, frozen, weakness -20 attack, darkness, nauseated = can't eat or drink for 2 min,
  slimed) are resisted by the **immunity** stat; boots and some rings give immunity.

**Drinks (source 11).** Coffee (5 beans in a keg) gives +1 speed for 1 min 23 s; Triple Shot Espresso (3 coffees)
gives the same +1 for 4 min 12 s. The stronger version lasts longer rather than going higher. Alcohol makes the player
"tipsy" (-1 speed, 30 s).

**Remedies (source 12).** The clinic sells two medicines: an Energy Tonic (+500 energy, 1,000g) and a Muscle Remedy
that clears the "exhaustion" penalty ("when you've pushed your body too hard"). The Life Elixir (four kinds of mushroom,
recipe at combat level 2) restores health to full. Oil of Garlic (garlic x10 + oil, combat level 6) stops monsters
spawning in the normal mines for 10 minutes: a **repellent**, not a stat boost. Monster Musk does the opposite
(doubles enemies, 10 min).

### 2.3 Necesse (necessewiki.com, read 2026-10-01)

**The list shape (source 15).** Health potions restore a flat amount plus a share of maximum health (50 + 10%,
100 + 20%, 150 + 30%) and have a **30-second wait** before another can be drunk; mana potions likewise. 35 buff
potions (24 base + 11 "greater" versions), each one lever, almost all **5 minutes**; the utility ones last longer (Building +50% placing speed 30 min;
Passive = fewer hostile spawns 15 min; Spelunker / Tracker / Treasure, which light up ore, enemies and treasure,
10 min; Invisibility 10 min). Levers: damage +10%, crit +10%, attack speed +15%, armour +8, health regen +0.5,
movement +20%, mining speed +40%, fishing power +20% and an extra line, knockback +50%, projectile speed, thorns,
slow-on-hit (web potion, made with silk), fire resistance, minion count.

**Strength comes from a better station, not a new recipe.** Each "greater" potion is the base potion + 10 alchemy
shards at the late Fallen Alchemy Table (greater mining +80% for 15 min, greater speed +30%, greater armour +32).
Stations climb: Alchemy Table -> Caveglow / Void Alchemy Table -> Fallen Alchemy Table; a recipe's station tells the
player where in the game it belongs. Ingredients are mostly local flowers and fish, plus one material that explains
the effect (iron bar for mining, silk for the web potion, any stone for the armour potion). Special potion: a revival
potion used on the player's settlers, not on the player.

**Food (source 16).** Food has nutrition (hunger is on by default, optional per world) and a buff by quality:
- *Simple* (raw crops): one small stat, 4 minutes (+10% mining speed from a beet, +0.25 health regen from a cabbage).
  Raw meat and raw eggs give -10 max health: eating raw is a mild penalty.
- *Fine* (one cooking step): one or two stats, mostly 8 minutes (4-20); Black Coffee +25% movement 30 min; Cappuccino
  +30% movement 45 min.
- *Gourmet* (3-6 ingredients): one to five stats (mostly 2-3), 12-20 minutes (Miner's Stew: +50% mining speed,
  +1 mining range, +15% movement, 16 min). Two gourmet dishes carry a cost: the chicken cutlet trades -10% movement
  for +25 armour; raspberry jam trades -50 max health for +200 max mana.
- The buffs page lists a single "Food consumed" buff, which suggests one food buff at a time, but the page does not
  state the rule (**unverified**).

**Area buffs (source 16, Buffs page).** Placed banners give everyone nearby +15% damage, or 10% less damage taken, or
+30% movement, or stop enemy spawns; a campfire nearby gives +2 regeneration out of combat and halves spawns.
Spoilage exists (2-18 hours) - not relevant to us, since our food doesn't spoil.

### 2.4 Minecraft (minecraft.wiki, read 2026-10-01)

**The list shape (source 20).** About 20 effect potions, all brewed from one base (a water bottle, then an "awkward
potion" made with nether wart), in a brewing stand (20 s per brew, fuelled by blaze powder); potions are also found as loot, fished up and
traded.
Effects: regeneration, swiftness, fire resistance, healing, night vision, strength, leaping, water breathing,
invisibility, slow falling, and negative ones meant for throwing (poison, weakness, slowness, harming).

**Modifiers do most of the work.** Five ingredients change any potion rather than making a new one:
- *Stronger* (glowstone): level II, but **shorter** (swiftness 3:00 at +20% becomes 1:30 at +40%).
- *Longer* (redstone): 3:00 becomes 8:00. Stronger and longer are **mutually exclusive**.
- *Thrown* (gunpowder): a splash potion that affects everything it lands on - how you heal a friend or poison a foe.
- *Lingering* (a rare material): a splash potion that leaves an area cloud; lingering potions also tip arrows.
- *Inverted* (fermented spider eye): swiftness becomes slowness, night vision becomes invisibility, poison becomes
  harming.

**Stacking.** "Drinking a potion while already under the effects of the same potion does not add onto the effect's
duration, but simply resets it", and a weaker level never replaces a stronger one that is running.

**A trade-off potion.** The Turtle Master potion gives -60% speed and 60% less damage taken for 20 s (level II: -90%
speed, -80% damage). A potion can be a choice, not just a bonus.

### 2.5 Core Keeper (core-keeper.fandom.com via its API, read 2026-10-01)

**Potions are short and strong (source 21).** Two healing potions heal a share of health at once (+30%, +40%) with a
**5-second** wait. The buff potions and drinks last 20 s to 1 minute and are big: +30% melee, ranged, magic or minion
damage for 1 min; Stoneskin +58 armour for 1 min; Guardian's Potion 12% less damage from bosses for 1 min; coffee
+7.4% attack speed for 40 s; cave coffee +23% movement for 20 s. A **cure-only** potion (Poison Aid) removes poison
and does nothing else. The **Unusual Potion** is a gamble on purpose: +40% damage dealt and +40% damage taken for
1 min. One potion (Splendid Amalgam) gives +40 max health permanently, once.

**Food is the long buff (source 22).** Hunger exists (1 food point per 20 tiles walked). A cooking pot combines **two
ingredients** into one meal whose type and name come from the ingredients ("Hearty Pepper Wrap"). The meal takes the
effects of both ingredients and the dish; **where two give the same effect, only the higher value is kept** (permanent
max-health gains are the exception and add up). Typical meal: a heal over 20 s plus one or two 10-minute buffs
(+23 armour, +22% ranged damage, +45 mining damage, +63 fishing, immunity to acid for 10 min, immunity to mould).
74 ingredients make 2,775 possible meals. Rare and epic meals (from "golden" crops grown with a gardening skill) are
25% / 50% stronger. Wiki tips advise eating the summoner meals in a set order so one doesn't overwrite another's
effects, which implies effects from different meals can run together when they don't overlap (the rule is not stated
on the page - **unverified**).

**Drinks are a separate, quick family**: sodas, coffee, hot punch - small effects for 20-40 s (one soda's tooltip
says it came "from a strange vending machine"; the page doesn't list where potions come from).

### 2.6 Valheim (valheim.fandom.com via its API, read 2026-10-01)

**The list shape (source 24).** 21 meads, made in two steps: mix a mead base at a kettle, then leave it to ferment
in a fermenter (6 meads per batch). Most are honey + berries + one telling ingredient (the poison-resistance mead uses
a neck-tail and coal; the frost one a "bloodbag"). Effects by group:
- Healing (50 / 75 / 125 health over 10 s) and stamina (80 / 160 over 2 s): all healing meads **share one 2-minute
  cooldown group**, all stamina meads another. Lingering versions: +25% regeneration for 5 min.
- Resistances (fire, frost, poison): 10 min, 10 min cooldown.
- Utility, mostly with no cooldown: +15% walking and running speed 10 min; +250 carry weight 5 min (2 min cooldown); x2 taming
  speed 10 min; -50% swimming stamina 5 min; better jumps 10 min; an **anti-sting concoction that stops giant
  mosquitoes attacking you for 10 min**.
- Trade-offs: Tasty mead (-50% health regen, +100% stamina regen); Berserkir mead (-80% stamina for attacks, blocks
  and dodges for 20 s, but 1.5x damage taken).

**Food (source 25).** Up to **three different foods** at once; each raises maximum health and/or stamina and fades as
it is digested (10-50 min). Starvation doesn't exist. Eating the same food again refreshes it. Food icons are
colour-coded (red = health, yellow = stamina). This is the opposite of our one-meal rule; it makes food choice a
small loadout every trip.

**Comfort as a buff (source 25).** Shelter plus a fire gives "resting", which becomes "rested" (+50% health regen,
+100% stamina regen) after 20 s or a night in a bed. A home that is pleasant to be in pays out as a buff (the
duration's link to the base's comfort level is not stated on this page - **unverified**). Being wet or cold is a
debuff that shelter and fire remove.

---

## 3. Outfit and armour sets, per game

### 3.1 Necesse (source 17, read 2026-10-01)

- **Armour value is simple:** each point removes 0.5 damage from a hit. A full matching set adds a **set bonus**; sets
  are labelled by class (melee, ranged, magic, summoner).
- **One body, several heads.** Many sets share a chest and boots but offer 2-4 head pieces; the head chosen decides
  the set bonus (Frost: helmet = melee hits slow and burn; hood = +10% crit, faster arrows; hat = magic crit and mana).
  So one set covers several roles without new body art.
- **Set bonuses are verbs, not only numbers.** Spider: attacks poison (10 damage over 5 s), immune to slows, +1
  summon. Shark: hits make the target bleed (40 damage over 4 s), and each enemy bled recently gives you speed and
  damage. Bloodplate: after being hit, health
  regeneration doubles for 4 s. Dryad: out of combat you build up to 3 "barkskin" layers of +10 armour, and lose one
  per hit. Tungsten (the plain heavy metal set): +30 resilience, knockback resistance, +50% knockback dealt.
- **Active abilities on a key, with cooldowns.** Demonic: spend 10% of max health for +15% damage, crit and speed for
  8 s. Ancient Fossil: 100% crit for 5 s, 60 s cooldown. Thief: throw 25 coins, 15 s cooldown. Phoenix: once every
  5 minutes, a lethal hit is prevented and you heal.
- **Trade-offs are explicit and small.** Arachnid chestplate: +10% summon damage but +50% knockback taken. Pharaoh's
  headdress: +10% magic damage but +10% mana use. Demonic's ability costs health.
- **A single odd piece can be a whole idea**: the Stealth Basket (no set) makes you invisible after standing still for
  2 s.
- **Old sets stay useful.** Once incursions unlock, an upgrade station raises every armour piece to similar defence,
  "without considering the unique set bonus, even a weak early game armor can be relevant for end game content" (the
  wiki's note). From then on, a set is chosen for its job, not its tier.
- **Role sets made from a monster's material.** Spider set from cave spider glands; Shark set from teeth, scales and
  fins; Thief's set from coins; Ninja set dropped by ninjas. The material tells you the role.

### 3.2 Terraria (sources 18, 19, read 2026-10-01)

**Scale.** 70 armour sets: 36 before the mid-game switch ("hardmode"), 34 after. A full set of one kind adds a set
bonus. Several late sets come in one body with a choice of helmets, one per fighting class (as Necesse). Separate
vanity slots let a player wear one set's look over another's stats.

**The plain metal sets have dull bonuses on purpose.** Copper to platinum (and the wood sets) only add +1 to +4
defence as a set bonus. Everything interesting is in the role and material sets beside them:

| Set | Defence | Job (bonus) | Made from / how got |
|---|---|---|---|
| Mining | 4 | +20% mining speed from the pieces, set bonus +10% (+30% total); helmet gives light | Helmet bought from the merchant; shirt and pants rare drops from undead miners |
| Prospector (late mining set) | 33 | The same +30% mining and light, with late-game defence | The three mining pieces + 30 late-metal bars (an upgrade, not a new set) |
| Angler | 4 | +15 fishing power; set bonus: fewer enemies spawn | Quest rewards from the fisherman (the Angler NPC) |
| Captain (late angler set) | 33 | The same, with late-game defence | The three angler pieces + 30 late-metal bars |
| Snow | 9 | Immune to chilled and frozen | Rare drop from frozen zombies |
| Ash Wood | 7 | Lava contact damage and burning halved | 75 ash wood |
| Cactus | 3 | Thorns (attackers take 15-45 damage) | 75 cactus |
| Gladiator | 16 | Immune to knockback | Rare drop |
| Ninja | 9 | +9% crit; set bonus +20% movement speed | Dropped by the King Slime boss |
| Bee | 13 | Summoner: +2 minions, +23% summon damage | 30 bee wax |
| Jungle | 17 | Magic: +80 mana, -16% mana cost | Jungle spores, **stingers**, vines |
| Necro | 19 | Ranged: +15% ranged damage, +10% ranged crit | Cobwebs and bones |
| Fossil | 13 | Ranged: 20% chance not to use ammo | 60 sturdy fossils |
| Spider | 20 | Summoner: +3 minions, +28% summon damage | 36 spider fangs (late) |
| Turtle | 65 | Tank: thorns 200% of contact damage, 15% less damage taken, +750 aggro (enemies prefer you) | 3 turtle shells + late metal |
| Beetle (shell) | 73 | Tank: "Beetle Endurance" - every 3 s without being hit, 15% less damage, up to 45%, one step lost per hit; +900 aggro | Beetle husks + a full turtle set |
| Beetle (scale mail) | 61 | Melee: each hit builds +10% melee damage and speed, up to +30% | Same set, other chest piece |
| Spectre (hood) | 30 | Healer: -40% magic damage, but 20% of magic damage dealt heals you or the lowest-health ally nearby | Late magic set |
| Shroomite | 51 | Ranged stealth while standing still: -750 aggro, up to +50% ranged damage | Late ranged set |
| Hallowed | 27-50 | After you strike an enemy, you dodge the next attack | Late set, one helmet per class |
| Vortex | 62 | Stealth toggle: -1200 aggro, up to +80% ranged damage, but movement x0.3 | Final-tier ranged set |

Single special pieces (no set): night-vision helmet (works like the night-vision potion); an "ultrabright" helmet
combining the mining helmet and night vision, which still counts for the mining set bonus; a diving helmet (longer
breath); a "dead man's sweater" that halves damage and debuff time from traps; a slow-fall foot piece.

**Lessons the numbers show.**
- **A role set's defence is low on purpose** (mining 4, angler 4 when copper is 6 and platinum 20): wearing it is a
  choice to work, not fight. The game then gives each role set a **late copy with real defence** (Prospector,
  Captain) so the role doesn't get abandoned.
- **The set bonus is often the role's signature**: mining +30%, fishing +15 power, the beetle's damage reduction
  that grows while you avoid hits, the spectre's healing. Several bonuses are behaviours, not numbers.
- **Material = role.** Stingers in the magic set, cobwebs in the ranged set, bee wax in the bee set, beetle husks in
  the tank set.
- **Trade-offs are explicit on the strongest sets**: Spectre gives up 40% damage to heal allies; Vortex stealth slows
  you to 30% speed; Turtle draws enemies to you.
- **Aggro is the multiplayer role lever** (source 19): enemies choose the player with the smallest
  `distance - aggro`, so a tank outfit pulls enemies off friends and a stealth outfit sheds them. In single player it
  barely matters.
- **The wiki's own tips** say the cheaper late ore sets are often wrongly seen as downgrades because their bonuses are
  more class-specific; and that late-game players mix pieces (a regenerating chest with another set's helmet) once
  set bonuses matter less.

### 3.3 Core Keeper (source 23, read 2026-10-01)

**Scale.** 56 armour sets and 30 single pieces; a set is 2 or 3 armour pieces, and some set bonuses also count rings
and necklaces (up to 5 items). Bonuses can come in steps: a 2-piece and a 3-piece or 5-piece bonus. Stats are listed as
ranges by item level (whether every piece can be levelled up at a station is not stated on these pages - **unverified**).

**Role sets and their jobs (numbers at their highest level):**

| Set | Job | Set bonus | Trade-off / source |
|---|---|---|---|
| Pot / Cooking Pot (2 pieces) | Cook | Well-fed (food) buffs +40% / +84% stronger | Also crit chance; the cooking-pot set drops from a boss |
| Diving (3 + 2 accessories) | Fisher | Up to +62 fishing, rarer fish, bait sometimes not used; 3 set: fishing power adds ranged damage; 5 set: +29% double fish | Pieces fished up in different waters |
| Wildwarden (3 + 2 accessories) | Pet keeper | Pet attack speed, damage and crits; +15% health when a pet is out; 5 set: pet talents +10% | Chests, a boss, fishing |
| Miner's (3 + 2) | Miner | +32-42% mining damage, +16-20% mining speed, light; 3 set: speed burst after breaking a wall; 5 set: mining damage adds to melee | Fished from lava, found in chests |
| Larva (2) | Heavy digger | Up to +264 mining damage; 2 set: **disguised as a larva** | -10.6% movement speed; from hive bosses |
| Carapace (2) | Digger-fighter | +36% explosives damage; 2 set: +23.8% damage briefly after mining a wall | Tin, larva meat, slime, fibre |
| Hivebone (3) | Bruiser | Attack speed and thorns; 3 set: **immune to acid** | From the hive mother boss |
| Hazmat (3) | Hazard worker | 3 set: immune to radiation damage | Bought from a merchant |
| Blast | Demolition | Less damage from your own team's explosions; a chance that explosives drop their parts | - |
| Stone | Boss fighter | Less damage from bosses; 2 set: +20% damage to bosses | - |
| Hunter (2) | Sniper | Ranged damage and dodge; 2 set: +15% crit after standing still a moment | Dropped by caveling hunters |
| Assassin (2) | Dodger | Dodge and speed; 2 set: +26.6% attack speed briefly after a dodge | Less armour than other sets of its level |
| Iron (3) | Soldier | 3 set: +19% armour at low health | Plain metal set with a twist |
| Core Commander (3) | Team leader | 2 set: +25% damage for you **and nearby allies** | Boss drop |
| Slime (3) | Brawler | 2 set: immune to slippery ground; 3 set: melee attackers become slippery | Boss drop |
| Pandorium (3) | Glass cannon | Dodge and speed, no armour stat; 3 set: +80% melee damage while you haven't been hit for a while | Late, crafted |
| Researcher's (3) | Explorer | Glow (light), up to +14% movement speed | Found in office crates |

**Lessons.**
- **Even the plain metal set gets a twist** (iron: more armour at low health), so no set is just a number.
- **Conditional bonuses create play**: after mining a wall, after standing still, after a dodge, at full health, while
  unhurt, beside water. Each tells the player how to act while wearing it.
- **Disguise as a creature** (the larva set) - directly bug-relevant; Terraria's Royal Gel does the same for slimes.
- **A team bonus** (+25% damage for nearby allies) gives a reason to wear a set in a group.
- **Immunity sets** (acid, radiation, mould, burning) are the simplest role sets: one hazard, one outfit.

### 3.4 Valheim (source 26, read 2026-10-01)

**Two sets per region, light and heavy.** Each region of the world has a heavy metal set and a light set made from that
region's creatures:
- Heavy sets (bronze, iron, wolf, padded, carapace, flametal): the most armour, but **-5% movement speed per chest
  and leg piece**.
- Light sets carry a skill bonus plus a resistance and a weakness: Troll set +15 sneaking; Root set +15 bows, resists
  poison and piercing, but 1.5x fire damage; Fenris set +15 fists, +3% speed per piece, resists fire and frost; Bear
  and Vilebone sets add health and stamina regeneration and more damage but take +25% physical damage.
- **Carapace armour** is the heavy set of the misty region, made from carapace and mandibles of giant insect enemies -
  a precedent for bug-plate heavy armour (-5% movement per piece like other heavy sets).
- Capes are a third, light slot where each cape does one thing (frost resistance; a feather cape removes fall damage
  but doubles fire damage).
- Every piece can be upgraded at the station (+2 armour per level, four levels), so a favourite set keeps up for a
  while.

### 3.5 Don't Starve (dontstarve.wiki.gg, read 2026-10-01)

Not a set game - one body slot and one head slot - but the clearest example of **real-world role gear** (source 27).
- **Armour is "% of damage absorbed", and the strong pieces cost something.** Log suit 80%; marble suit 95% but
  **-30% movement**; night armour 95% but drains sanity; tin suit 85% and -10% speed; scalemail 70% plus immunity to
  fire and sets attackers alight; cactus armour 80% and hurts attackers.
- **Single-threat gear.** The beekeeper hat (silk x8 + rope) absorbs 80% of damage **from bees only** and nothing
  from anything else. A seashell suit and a horned helmet stop poison from contact. The gas mask stops poison gas and
  hay fever but drains 10 sanity a minute.
- **Disguise among a species.** The mant suit and mant mask (both made with **chitin**) make the ant-people neutral
  to you when worn together. Cactus armour makes cactus creatures ignore you.
- **Hide in place.** The bush hat lets you hide where you stand; enemies walk past until you move.
- **Headlamp from bugs.** The miner hat lights the way hands-free and is refuelled with **fireflies** (or glowing
  bulbs or slime) - a light source powered by a living light.
- **A shell to hide in.** The snurtle shell armour lets you hide inside it, absorbing all damage while hidden.
- Clothing ("dress") answers weather: straw hat for heat, winter hat for cold, raincoat for wet, a pith hat for fog.

### 3.6 Stardew Valley (sources 13, 14, read 2026-10-01)

- **Boots are the only stat clothing**: 18 pairs with just two numbers, defence (0-7) and immunity (0-8). Shirts and
  trousers are cosmetic. Boots come from mine floors, fishing chests and the adventurers' guild shop as you reach
  deeper floors.
- **Look and stats are separated**: tailoring moves one pair's stats onto another pair's look.
- **Hats are purely cosmetic**, mostly unlocked by achievements and sold by a mouse in an abandoned house - a reward
  for goals rather than power.
- Gear-based roles in Stardew live in **rings**, not clothes (rings are covered in the sibling research file
  `accessories-in-games.md`).

---

## 4. Patterns to copy or avoid, with reasons

The games agree on more than they differ. Below, "copy" means the pattern fits our rulings; "avoid" means it clashes
with a ruling or with the no-magic premise. Owner-taste calls are listed separately at the end of the section.

### 4.1 Potions and other consumables - copy

| # | Pattern | Seen in | Why it fits us |
|---|---|---|---|
| P1 | **One effect per potion.** | Terraria (43 buff potions, one lever each), Necesse (35), Minecraft | Readable at a glance; the examine text can explain one real effect; matches "one step per station". |
| P2 | **The ingredient explains the effect.** | Terraria (iron ore -> +defence, antlion mandible -> mining, cobweb -> danger sense), Necesse (silk -> web potion, iron bar -> mining), Valheim (neck-tail -> poison resistance) | For us the ingredient can carry the real biology: the bug's own venom makes its antivenom, moth eyes make night-sight drops, zinc ore makes calamine. This is the strongest single tie between potions, bug farming and "examine shows the real biology". |
| P3 | **Small recipes:** water + two ingredients for most potions. | Terraria (26 of 43 use two), Necesse (most one to three) | Keeps the cauldron to one step; no brewing chains (the overview's own lens for P16). |
| P4 | **Duration follows strength: potions short and strong, food long and broad.** | Terraria (strongest combat potions 4 min, ordinary 8, utility 10, building 45); Core Keeper (potions 20 s-1 min, meals 10 min); Minecraft (stronger = shorter) | Already our rule ("food is slow and long, potions are quick and strong"). A sensible ladder: cures instant; combat tonics 1-3 min; resistances and senses 5-10 min; pure conveniences 15-30 min. |
| P5 | **One heal wait shared by every healing item, owned by the person; weaker heals have shorter waits.** | Terraria (60 s for potions, 30-45 s for weak heals; accessories cut it 25%); Valheim (all healing meads share one 2-min group); Necesse 30 s; Core Keeper 5 s | Already decided. Waits seen: 5 s (Core Keeper), 30 s (Necesse), 60 s (Terraria), 2 min (Valheim). The weaker-heal-shorter-wait detail and an accessory that shortens the wait are free extras worth offering. |
| P6 | **Re-drinking the same potion resets its timer, never adds; a weaker one never replaces a stronger one running.** | Minecraft (stated rule); Terraria quick-buff skips buffs already running | The simplest stacking rule there is; stops stockpiling hours of a buff. Different potions all run together (Terraria allows 44 buffs at once). |
| P7 | **Cure-only items.** | Core Keeper (Poison Aid), Stardew (Muscle Remedy clears exhaustion; ginger and ginger ale clear nausea) | Our antivenom and acid salve are exactly this; each new harmful status should arrive with its cure. |
| P8 | **One weapon coating at a time, long duration, kept through death.** | Terraria flasks (8 kinds, 20 min, survive death) | The ready-made shape for the venom coating offered back in P16. |
| P9 | **A repellent you drink or wear, scoped to a pest.** | Valheim anti-sting concoction (stops giant mosquitoes 10 min); Stardew Oil of Garlic (stops spawns 10 min) | Real repellents exist and are species-specific in practice; "calming is per species" already says the scope. |
| P10 | **A one-key "drink my buffs" and "heal" button.** | Terraria quick-buff / quick-heal | Pure convenience for a game with several potions at once; quick-heal picks the right healing item. |
| P11 | **A few trade-off potions.** | Minecraft Turtle Master (-60% speed, -60% damage taken), Core Keeper Unusual Potion (+40% damage dealt and taken), Valheim Berserkir and Tasty meads | One or two give the list a decision rather than only bonuses. Keep them rare. |
| P12 | **Buffs from places, not only bottles.** | Terraria campfire / heart lantern / honey / sunflower; Necesse banners and campfire; Valheim "rested" from shelter + fire | Not potions, but the natural home for a home-comfort bonus on the plot (fits the decorative-outfit idea of comfort as a reward). Noted for the farming / building sections. |
| P13 | **Meet a potion before you can make it.** | Terraria (lesser healing potions in chests, pots and boss drops; shop stock), Stardew (the clinic sells remedies; elixirs drop in the Skull Cavern) | Fits P16 (basic recipes are known; stronger ones are found, bought or earned): finding a strange bottle in the wild is how players learn it exists. |
| P14 | **Show every running effect as an icon with its time left; blink before it ends; right-click to cancel.** | Terraria (buff bar with timers, right-click cancels), Stardew (icons blink before expiring since 1.5; tooltips show durations since 1.6) | Several potions plus a meal at once are only readable with this. |

### 4.2 Potions - avoid

| # | Pattern | Seen in | Why it clashes |
|---|---|---|---|
| A1 | **Flat "+defence" or "+damage" drinks with no real mechanism** (Ironskin, Wrath, Rage, Stoneskin). | Terraria, Necesse, Core Keeper | No magic (D65): nothing you drink hardens skin. Defence and damage belong to outfits and weapons; real drinks act on stamina, pain, alertness, toxins and senses. |
| A2 | **Seeing through rock** (Spelunker, Hunter, Danger Sense, Biome Sight, Treasure). | Terraria, Necesse | No real basis; information is better delivered by real tools (a detector, a lamp) or by senses that really exist (night sight). |
| A3 | **Modifier chains** (stronger / longer / thrown / lingering / inverted via extra brewing steps; base then ferment). | Minecraft, Valheim | Clashes with "one step per station" and "no brewing chains". Our strength ladder is already the **ingredient tier** (stronger bug venom -> stronger antivenom), as Necesse does with its "greater" potions. |
| A4 | **Luck, teleport and water-breathing potions.** | Terraria, Necesse, Minecraft | Ruled out (luck, diving) or not real (teleport). Terraria's battle potion (more spawns everywhere) has a real, per-species cousin: the pheromone lure (5.1 #19). |
| A5 | **Hunger, spoilage, three food slots.** | Necesse, Core Keeper, Valheim | Decided against (no hunger, no spoilage, one meal boost). |
| A6 | **Very long lists.** | Terraria 43 + 12 heals + 8 flasks; Necesse 35 + 6 | "A small set to start" (P16) and "variety with taste" (D55): a first list of about 12-15, grown later. |
| A7 | **Thrown (splash) healing.** | Minecraft | Not needed: P17 already lets you click a potion onto a friend. |

### 4.3 Outfits and sets - copy

| # | Pattern | Seen in | Why it fits us |
|---|---|---|---|
| S1 | **A role set is a job with a signature bonus.** | Terraria (mining +30% mining and light; angler +15 fishing), Core Keeper (cooking pot +84% food buffs; diving +fishing; wildwarden pets), Necesse (spider = poison and summons) | Matches the brainstorm's frame (one primary + one or two minor levers, `brainstorm_armor.md` §2) and "each role has its own best gear". |
| S2 | **Keep role sets alive with a stronger remake.** | Terraria: Prospector = the three mining pieces + 30 late-metal bars (defence 4 -> 33); Captain = angler set + metal. Necesse: an upgrade station brings every set to similar defence. Valheim: +2 armour per upgrade level. | Answers the brainstorm's rule that defence is the spine and no set is perk-only, without throwing away an early role set: re-forge the same outfit with a better metal or plate to raise its defence and keep its job. The roster's basic / armoured / deep mining (and fishing, beekeeping) lines are this pattern. |
| S3 | **Bonuses that ask you to act a certain way.** | Core Keeper (after mining a wall; after standing still; after a dodge; at full health; beside water), Terraria (beetle shell: damage reduction grows while you avoid hits), Necesse (dryad: barkskin layers out of combat; shark: each enemy bled recently gives you speed and damage) | These are verbs, which is the brainstorm's rule for functional outfits (§7): personal, active, safe in a shared world. |
| S4 | **One small, visible cost per outfit.** | Valheim (heavy pieces -5% speed each; light sets weak to fire), Don't Starve (marble suit -30% speed; gas mask drains sanity), Core Keeper (larva set -10.6% speed), Necesse (+50% knockback taken), Terraria (vortex stealth x0.3 speed) | Makes "no single best set" true by construction: each outfit is the right answer somewhere and the wrong one elsewhere. |
| S5 | **Single-threat gear.** | Don't Starve beekeeper hat (absorbs bee damage only), gas mask, seashell suit (contact poison); Core Keeper hazmat / hivebone (acid) / moldweb; Terraria snow and ash-wood sets | The roster's ranger (anti-wasp/hornet) and the existing `sting_immune` flag already lean this way; a hazard set works as a key to a place (brainstorm §1). |
| S6 | **Disguise among a species.** | Don't Starve mant suit + mask (chitin) makes the ant-people neutral; Core Keeper larva set "disguised as a larva"; Terraria royal gel for slimes | Real biology backs it: some spiders use ant mimicry and chemical mimicry to get into ant nests (Wikipedia, Myrmecophily). A bug farmer walking unharmed through an ant colony in ant-chitin is a strong moment. Per species, like calming. Terraria builds its slime disguise (the royal gel) into the same targeting sum as aggro - the wearer counts as 1000 pixels farther away for slimes only (source 19) - so disguise and S8 can share one mechanism. |
| S7 | **A team-helper outfit.** | Core Keeper Core Commander (+25% damage for you and nearby allies), Terraria spectre hood (gives up 40% damage; 20% of damage dealt heals the weakest ally nearby) | Pairs with P17 (click a bandage or potion onto a friend): a healer's outfit that makes your heals on others stronger. The roster already lists a village healer's garb. |
| S8 | **Drawing or shedding attention in multiplayer.** | Terraria aggro (+750 turtle, +900 beetle, -1200 vortex stealth): enemies pick the player with the smallest distance minus aggro | A guard outfit that pulls bugs off friends, and a quiet one that sheds them. **Cost:** which player a bug chases is decided in the synchronized client bug simulation (`BugAgent.SimulateTick` keeps a `TargetPlayerId` that rides the late-join snapshot), so an outfit that changes it is a new simulation input wired by the `frontier-sync` recipe. Damage-side bonuses are cheaper: the bee suit's `sting_immune` is already a server damage hook (`nakama/modules/world/handlers_player.go`, the sting-immunity check). |
| S9 | **Hide in place.** | Don't Starve bush hat (hide until you move), Core Keeper hunter set (+15% crit after standing still), Terraria shroomite (stealth while still) | A stealth outfit with a clear rule ("stand still and the bugs lose you") instead of an invisible number. Fits the roster's forest plate (camouflage). |
| S10 | **An outfit plus a matching accessory unlocks a second bonus.** | Core Keeper (diving set: 3 pieces + necklace + ring for a 5-piece bonus; miner's and wildwarden the same), Terraria (any wizard hat + any gem robe gives a set bonus) | Works with whole-outfit art: the variety lives in the two accessory slots, so no new outfit art is needed (e.g. angler's waders + a tackle box). |

### 4.4 Outfits and sets - avoid

| # | Pattern | Seen in | Why |
|---|---|---|---|
| X1 | **Plain metal sets whose only bonus is a little more defence.** | Terraria copper -> platinum (+1 to +4) | Core Keeper shows even the iron set can carry a twist (+19% armour at low health). A small twist per metal outfit is cheap and keeps the spine interesting. |
| X2 | **Head-piece variants and mixing pieces.** | Terraria, Necesse, late-game mixing tips | Our outfits are drawn whole (2026-08-05); the same job is better done by an outfit plus accessories. |
| X3 | **Magic and summoner classes.** | All four set games | No magic. The nearest real role is a **bug handler** whose own bugs fight or work beside them (Core Keeper's wildwarden pet set is the model) - only if bugs that follow the player are ever decided. |
| X4 | **Durability, repair, random stat rolls.** | Don't Starve (durability), Terraria (random modifiers), Core Keeper (stat ranges by item level) | No wear-and-tear (D49, D50); random rolls fight "readable". |
| X5 | **Everything levelled to the same defence late on.** | Necesse incursion upgrades | Keeps old sets alive but flattens "danger rises outward". A per-line remake (S2) does the same job with control. |

### 4.5 Questions for the owner (taste, not research)

1. **Do potions survive death?** Terraria: potion and food buffs are lost on death, weapon coatings are kept.
2. **Are teas and coffees "potions" (no wait, run alongside the one meal) or a second "drink" slot as in Stardew?**
   Simplest reading of the existing rules: they are potions.
3. **Work tonics or not?** Meals already give "quicker work" (P16). Short, stronger work tonics (coffee, grip chalk,
   liniment) would stack with the meal, as Stardew's coffee stacks with food. Or work boosts stay meal-only.
4. **Trade-off potions** (5.1 #24, a stimulant with a crash) - one or two, or none?
5. **A "guard" outfit that draws bugs off friends** - wanted, given its sync cost?
6. **A look slot** (wear one outfit's look over another's stats, as Terraria's vanity slots and Stardew's tailoring).
7. **Which harmful states exist beyond venom and acid?** Itching, stun, blindness and food poisoning would each bring a
   cure (5.1 #4-7); each is a new status to build, show and balance, so the cure list should follow that choice, not
   lead it.

---

## 5. Candidate lists

Proposals for the owner to pick from, not decisions. Every "real basis" restates a fact from the source-28 articles
(read 2026-10-01); anything not checked there says **unverified**. "Decided" marks the five things D54 already settled - here they only
get a real-thing form and a recipe idea. Durations follow pattern P4 (cures instant; combat tonics 1-3 min; resistances
and senses 5-10 min; conveniences longer). Nothing below uses mammals, birds, reptiles or amphibians; "bug leather" is
the extractor's output (D11, D18), not hide.

### 5.1 Potions, tonics and remedies (24)

| # | Real thing (working name) | One effect in the game | Lever | Plausible ingredients (bug / plant / mineral) | Real basis | Status |
|---|---|---|---|---|---|---|
| **Heal (the only one with a wait)** |||||||
| 1 | **Clotting draught** | Heals a lot at once; starts the shared heal wait | Health now | Chitosan (bug shell chitin soaked in lye) + honey; better shells for stronger grades | Chitosan is made by treating chitin shells with an alkali; chitosan dressings reduce bleeding by making blood clot. Real chitosan goes on wounds, not in drinks - the draught is game-logical | Decided (the healing potion) - form proposed |
| **Cures (instant, no wait)** |||||||
| 2 | **Antivenom** | Ends venom poisoning | Cure venom | The venom of the same bug tier (wasp, hornet, scorpion, centipede, fire ant) | Antivenom is antibodies raised against a venom; made in horses, sheep and other hosts; versions exist for spider and scorpion stings; synthetic antibodies are in research. **Fire ants inject an alkaloid venom with a sting** | Decided |
| 3 | **Acid salve** (bicarbonate salve) | Ends acid or spray burning | Cure acid | Baking soda (natural mineral nahcolite, or from trona) + beeswax | Bicarbonate neutralises acids. **Formicine ants spray formic acid** (fire ants don't); vinegaroons spray acetic acid; bombardier beetles a hot chemical spray. Rinsing with water is the real first aid for splashes (**unverified** here) - examine text shouldn't claim more | Decided |
| 4 | **Calamine lotion** | Ends itching (caterpillar or tarantula hairs, bites) | Cure itch | Zinc ore + rust or ochre (iron oxide) | Calamine is zinc oxide + 0.5% ferric oxide, used for mild itching and insect bites; "calamine" is also the old name of a zinc ore; many caterpillars and tarantulas defend with urticating hairs | New - needs an itch status (e.g. slower tool use) |
| 5 | **Activated charcoal** | Ends sickness from eating something bad | Cure food poisoning | Charcoal heated with steam at the furnace | Activated carbon (charcoal made porous with steam at 600-1200 °C) treats swallowed poisons; useless against corrosives and cyanide | New - only if raw or toxic food can make you sick (§11 "eating raw food" is open) |
| 6 | **Smelling salts** | Ends a daze or stun at once; works on a friend too | Cure stun | Sal ammoniac (mineral crust from volcanic vents and burning coal seams) + chalk (the route to ammonium carbonate is **unverified**) | Ammonium carbonate inhalants restore consciousness after fainting and are used on dazed athletes; the old "spirit of hartshorn" came from antlers - avoided | New - needs a stun status |
| 7 | **Eye wash** | Ends blindness from a spray in the eyes | Cure blind | Salt + boiled water | Tarantula hairs can embed in eyes; vinegaroons and bombardier beetles spray. Rinsing as first aid is **unverified** here | Optional - could fold into the acid salve |
| **Resistances (timed)** |||||||
| 8 | **Venom tolerance tonic** | Less venom damage and shorter venom, 10 min | Resist venom | A tiny dose of that tier's venom + royal jelly | Allergen immunotherapy (desensitisation) works for stinging-insect allergy - it treats allergy over months, not toxicity, so the tonic is game-logical | Decided (venom resistance) |
| 9 | **Repellent** (one per pest) | One named biting pest won't target you, 10 min | Avoided by one species | Lemon-eucalyptus leaves, citronella grass | DEET, picaridin, oil of lemon eucalyptus (PMD) and IR3535 are recommended against mosquitoes and ticks; citronella and lemongrass were also tested | New - per species (P16); real repellents suit blood-feeders, so wasps and hornets are better left to smoke and outfits |
| 10 | **Handler's barrier cream** | Your livestock's stings, sprays and hairs don't hurt while you handle them, 10 min | Farm handling | Beeswax + zinc oxide | Zinc oxide is used in creams against rashes and in antiseptic ointments | New - a bug-rancher item |
| 11 | **Hive smoke** (smoker fuel) | One hive's bees stay calm while you open it, 5 min | Calm one species | Dry puffball fungus or dry grass, burned in the smoker | Smoke calms bees by masking alarm pheromones (isopentyl acetate, which a bee's sting releases to call others); some Native Americans burned puffball fungus | New - fits "calming is per species" |
| **Senses** |||||||
| 12 | **Night-sight drops** | See in the dark, 10 min | Vision | Moth eyes + a vitamin-A plant (carrot) | Moths' eyes carry an anti-reflective nanostructure that lets them see in the dark; lack of vitamin A causes night blindness; "carrots make you see in the dark" was WWII propaganda hiding radar - good examine text | Decided |
| 13 | **Firefly glow paint** | You glow softly, hands free, 10 min | Light | Firefly light organs + wax | Fireflies make light when luciferase acts on luciferin with ATP and oxygen; a paint that keeps glowing is game-logical | Optional - overlaps the glowworm outfit's light job; pick one home |
| **Work (short; runs alongside the one meal - see 4.5 question 3)** |||||||
| 14 | **Strong coffee** (or tea) | Walk faster, 3 min | Speed | Coffee or tea plant + honey | Caffeine improves reaction time, wakefulness and coordination; caffeine in nectar improves bees' memory of a flower | New |
| 15 | **Electrolyte drink** (rehydration salts) | Refills stamina at once | Stamina | Salt + honey + potash or citrus | Oral rehydration solution: water with sugar, sodium and potassium | New - if stamina (P14) is built |
| 16 | **Soda loading** (bicarbonate drink) | Sprinting costs less stamina, 2 min | Sprint stamina | Baking soda + water | Sodium bicarbonate is taken as a sports supplement for short, high-intensity effort | New - pick this or #15, not both |
| 17 | **Muscle liniment** | Tool swings cost less stamina, 5 min | Work stamina | Mint (menthol) + chilli (capsaicin), in spirit | Liniments with menthol, capsaicin or methyl salicylate relieve muscle aches by counter-irritation | New |
| 18 | **Grip chalk** | Faster pickaxe and axe swings, 5 min | Tool speed | Magnesium carbonate (mineral) | Powdered magnesium carbonate is climbing and gym chalk, a drying agent for grip | New - dusted on the hands, not drunk |
| **Farm, fish, catch (used, not drunk)** |||||||
| 19 | **Pheromone lure** (one per species) | Draws one species to a spot or trap, 5 min | Attract one species | Scent glands of that species (from the extractor) | Pheromone traps use species-specific pheromones to lure insects | New - also lures a pest away from your plot |
| 20 | **Fly-larva chum** | Thrown in water, fish bite faster there, 5 min | Fishing | Dried larvae from your own fly farm | Black soldier fly larvae are a protein source for aquaculture and approved as fish feed in the EU | New - ties the fly farm to fishing |
| 21 | **Royal jelly feed** | Fed to a larva in a pen, it grows into a breeder (queen) | Breeding | Royal jelly (already an item) | Royal jelly feeds all bee larvae; larvae in queen cells get "copious amounts" of it, which helps make them queens | New - a farm item for the ranching section, not the cauldron |
| **Combat** |||||||
| 22 | **Venom coating** | For 20 min, weapon hits add venom damage over time; one coating at a time | Damage over time | The venom of the bug tier, as for antivenom | San hunters poison arrows with the larvae and pupae of Diamphidia beetles - a real bug-made weapon poison | Offered back in P16; shape from Terraria flasks |
| 23 | **Clove numbing tincture** | Hits don't make you flinch or stagger, 2 min | Stagger resistance | Cloves (eugenol) + spirit | Eugenol is a local anaesthetic, used in dental pastes to reduce acute pain | New |
| 24 | **Stimulant shot** (trade-off) | Faster attacks and movement for 30 s, then "jittery" (slower stamina regen) for 60 s | Burst vs crash | Strong coffee + honey | Common minor caffeine effects include jitteriness and reduced coordination | New - see 4.5 question 4. Not ephedra: ephedra supplements were banned in the US in 2004 for serious side effects |

Left out on purpose: luck, teleporting, breathing underwater, "+defence" and "+damage" drinks (A1, A4); bee-venom
"therapy" (apitherapy is not an accepted medical treatment - source 28, Bee sting); anything from mammals or birds
(the antler route to smelling salts, milk, eggs).

**A real-biology split worth using:** the two decided ant species map onto the two decided cures - fire ants
sting with an alkaloid venom (antivenom), while formicine ants such as the black garden ant (*Lasius niger*) spray
formic acid (the salve). Whether the game's black ant is a formicine depends on the real-species naming pass (§03).

### 5.2 Role outfits and special armour (23)

Each is one whole outfit (2026-08-05). "Roster" = already listed in `docs/product/design/outfit_roster_scratchpad.md`
(an assistant's working list, not a decision); the research adds a job, a verb-style bonus and a cost. Defence stays
the spine (brainstorm §1): each also has real defence for its tier.

"Works on" is the build cost: **Damage** bonuses can follow the bee suit's existing server damage hook (`sting_immune`
in `nakama/modules/world/handlers_player.go`); **Player** bonuses change the player's own movement, light, tools or
items; **Bug behaviour** bonuses change what bugs notice, chase or flee from, which lives in the synchronized client
bug simulation (`BugFarmerClient/Assets/Scripts/Bugs/BugAgent.cs`) and goes through the `frontier-sync` recipe - the
costliest kind. How thorns damage on a bug would sync was not checked here.

| # | Outfit (materials) | Job | Signature bonus | Trade-off | Works on | Precedent | Roster |
|---|---|---|---|---|---|---|---|
| 1 | **Beetle-shell plate** (carrion-beetle chitin) | First bug-made armour, all-round | "Shell up": damage taken falls step by step while you go unhit; one hit resets it | Heavy: -5% walking speed | Damage | Terraria beetle endurance; Valheim heavy sets | Yes (picked) |
| 2 | **Fire-ant plate** (fire-ant carapace) | Fighting fire ants | Fire-ant stings don't get through | Helps against fire ants only; heavy | Damage | Don't Starve beekeeper hat (one threat); `sting_immune` | Yes (made) |
| 3 | **Black-ant plate** (black-ant carapace) | Walking inside an ant colony | Disguise: the colony's workers ignore you until you strike one | Strike or steal brood and the alarm brings every nearby ant at once | Bug behaviour | Don't Starve mant suit (chitin); Core Keeper larva set; real ant-mimicking spiders | Yes (made) |
| 4 | **Scorpion plate** (scorpion plates and stings) | Hot, venomous rock country | Venom resistance + heat resistance | Heavy: -5% speed | Damage | Valheim resist-and-weakness sets | Yes (not made) |
| 5 | **Thorn mail** - wasp, then hornet, then killer-bee tiers (stingers set in bug leather) | Melee brawler | Anything that bites or stings you in melee takes venom damage | No help against sprayers and spitters; less base defence than plate | Damage (reflected onto bugs) | Terraria cactus and turtle sets; Necesse thorns potion | Yes (thorn line) |
| 6 | **Centipede mail** (segmented centipede plates) | Skirmisher | After a dodge, a few seconds of faster attacks | Less armour than plate of its tier | Player | Core Keeper assassin set | New |
| 7 | **Dragonfly scout coat** (dragonfly-wing membrane over bug leather) | Scouting new zones | Faster walking and a wider view around you | Lowest armour of its tier | Player | Dragonflies' eyes have nearly 24,000 facets each | New |
| 8 | **Cave-spider silk robe** | Quiet travel | Bugs notice you only from close range while you walk (not run) | Light defence | Bug behaviour | Roster's silk = light, fast, quiet, weak | Yes |
| 9 | **Widow's armour** (widow silk and fangs) | Venomous zones | Venom resistance | Weak against crushing hits | Damage | Valheim root set (resists one damage type, weak to another) | Yes |
| 10 | **Silk sting-vest** (many layers of hunting-spider silk) | Anti-pierce | Stings and mandibles pierce less (venom still lands if a sting does) | No help against crushing charges or sprays | Damage | In 1887 a doctor tested silk vests of 18-30 layers against bullets, and silk vests followed that could stop slow handgun rounds; spider silk is tougher than steel and Kevlar | New (could be the hunting-spider silk set) |
| 11 | **Beekeeper's suit** (silk-mesh veil, waxed cloth) | Harvesting hives | Bee stings can't get through; smoker smoke lasts longer | Bees only; -speed | Damage (exists: `sting_immune`) | Don't Starve beekeeper hat (bees only) | Yes (beekeeping line) |
| 12 | **Bug wrangler's leathers** (bug leather, hornet-chitin cuffs) | Ranching livestock bugs | Your own livestock stay calm around you; more from nest harvests | You smell of the herd: that species' predators notice you sooner | Bug behaviour | Core Keeper wildwarden (pet keeper) | Yes (bug wrangler) |
| 13 | **Entomologist's field coat** | Catching and studying | Better net catches; hovering a bug shows species, age and health | Low defence | Player | Core Keeper researcher's set | Yes |
| 14 | **Butterfly collector's whites** | Butterflies and moths | They don't flee from you | That family only | Bug behaviour | Single-species gear (S5) | Yes |
| 15 | **Miner's gear** (bug leather, metal helmet, glowworm lamp) - basic, armoured, deep | Digging | Hands-free light; a short speed burst after breaking a block; more ore carried | Heavy boots: slower above ground | Player | Terraria mining and prospector sets; Core Keeper miner's set | Yes (3 tiers = pattern S2) |
| 16 | **Angler's waders** (waxed bug leather) | Fishing | Wade shallow water; faster bites | Slow on land | Player | Terraria angler set; P1 wading outfit | Yes (fishing line) |
| 17 | **Glowworm lantern plate** (glowworm material) | Dark caves | Light around you | Night hunters see you from farther | Player; the cost is bug behaviour | Terraria shine / mining helmet; Don't Starve firefly-fuelled miner hat | Yes (light line) |
| 18 | **Village healer's garb** (linen, honey-wax) | Support in a group | Bandages and potions you give to others heal 25% more | Less damage dealt | Player | Terraria spectre hood (gives up 40% damage to heal allies) | Yes |
| 19 | **Industrial chemist's coat** (wax-coated canvas, glass goggles) | Brewing; acid zones | Acid splashes don't burn you; one extra potion per cauldron batch | Low defence; the brew bonus only counts at the cauldron, so it leans on the acid job to pass the brainstorm's "suits an expedition" test | Damage + cauldron | Core Keeper hazmat; brainstorm §7 | Yes |
| 20 | **Forest plate** (special timbers, resin) | Camouflaged tank | Stand still and bugs lose you | Slower | Bug behaviour | Don't Starve bush hat; Core Keeper hunter set | Yes |
| 21 | **Warden's plate** (hornet plate over steel) | Protecting friends | Bugs prefer to target you over nearby friends | You take the hits; heavy; **sync cost** (bug targeting is a deterministic simulation input) | Bug behaviour | Terraria aggro (turtle +750, beetle +900) | New - see 4.5 question 5 |
| 22 | **Gilded-steel plate** (gold over steel) | Acid key (Deadly Ants) | Acid-proof | Heavy, costly | Damage | Core Keeper hivebone (acid immunity) | Yes (picked). That gold resists acids is general chemistry, **unverified** here |
| 23 | **Lacquered remakes** (any bug plate coated in shellac) | Keeping a favourite role outfit useful later | Same job, higher defence | A material cost per remake | Damage | Terraria prospector/captain = role set + late metal; shellac is a resin secreted by the lac bug | New way to do S2 with bug materials |

Not proposed: a pill-bug curl set (the roster lists it as cut), diving gear (no diving), any wool, fur or feather
outfit (no living mammals or birds).
