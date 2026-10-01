# Accessories in other games: what they do, how many, how they stay interesting

Research for Bug Farmer (2026-10-01). Question: the old accessory list has been dropped and a new set is to be
designed from scratch: real-world objects (garden gloves, knee pads, a pedometer...) whose effects can be
game-logical rather than strictly physical (garden gloves that raise harvest yield). Levers named: harvest amounts,
station output amounts, stats (speed, defence...), bonuses such as night vision or resistances, and more. The game
has whole outfits (one worn at a time) plus separate accessory slots (2 in the prototype today).

Method: web search was not available this session, so wiki pages were fetched directly and read in full (several
prompts per long page). Every number below comes from a page named in the source table; anything not confirmed
from a page is marked **unverified**. Fandom-hosted wikis could not be fetched (HTTP 402) and were skipped.
Findings were appended game by game as each was finished.

Status: complete (2026-10-01). Sections were written incrementally as each game was read.

---

## 1. Source table

| # | Source URL | What it shows | How it applies to us |
|---|---|---|---|
| 1 | https://terraria.wiki.gg/wiki/Accessories | Slot counts (5/6/7), no duplicates, one pair of wings, accessory modifiers are bonus-only, informational items work from the bag, the 13 accessory categories | Slot budget + "no duplicates" rule; information items need no slot |
| 2 | https://terraria.wiki.gg/wiki/Informational_Accessories | ~23 read-out gadgets (watch, depth meter, compass, radar, metal detector, weather radio...) that work from the inventory, combining into GPS / Fish Finder / Goblin Tech / R.E.K. 3000 / PDA | The cleanest model for "information" items: real gadgets, no slot cost, combine to save bag space |
| 3 | https://terraria.wiki.gg/wiki/Construction_Accessories | Toolbelt, Extendo Grip, Brick Layer, Cement Mixer, Paint Sprayer, Ancient Chisel (+25% mining speed), combining into Architect Gizmo Pack / Hand of Creation | Real tools-as-accessories for building and mining; reach and speed levers |
| 4 | https://terraria.wiki.gg/wiki/Fishing_Accessories | Angler Earring (+10 fishing power), High Test Line, Tackle Box, Inner Tube, combining into Angler / Lavaproof Tackle Bag; earned from the fishing NPC's quests | Fishing kit as accessories; quest-reward sourcing |
| 5 | https://terraria.wiki.gg/wiki/Miscellaneous_Accessories | Discount Card (-20% shop prices), Gold Ring / Lucky Coin / Greedy Ring, Treasure Magnet (pickup 2.6 -> 12 tiles), Flower Boots, Guide to Plant Fiber Cordage (vines drop rope) | Economy + pickup levers; a book that changes what a resource drops |
| 6 | https://terraria.wiki.gg/wiki/Movement_Accessories | Aglet +5%, Anklet +10%, boots chain (Hermes -> Spectre -> Lightning -> Frostspark -> Terraspark), terrain-specific boots, climbing, swimming | Speed tiers, terrain-specific items, long upgrade chains |
| 7 | https://terraria.wiki.gg/wiki/Tinkerer%27s_Workshop | The combining station (10 gold from the Goblin Tinkerer); combined items keep component effects and get a fresh random modifier | Combining as the answer to a small slot count |
| 8 | https://terraria.wiki.gg/wiki/Goblin_Tinkerer | Reforge = re-roll an accessory's modifier for 1/3 of its value | Optional, probably avoid (random re-rolls) |
| 9 | https://stardewvalleywiki.com/Rings | 2 ring slots, 30 rings: light, magnet (pickup range), combat, defence, luck; how each is got (crafted at a skill level, bought after a mine depth, monster-slaying goals) | The closest genre match; shows a farming game whose rings do almost nothing for farming |
| 10 | https://stardewvalleywiki.com/Forge | Combining two rings (20 Cinder Shards, identical rings can't combine, combined can't combine again, un-forge splits them back); tool enchantments (Generous, Reaching, Preserving, Bottomless...) | Combining as a late-game slot expander; farming/fishing boosts live on TOOLS there, not accessories |
| 11 | https://stardewvalleywiki.com/Trinkets | 1.6 trinkets: unlocked after combat mastery, random stats re-rolled at an anvil for 3 iridium bars, "Trinkets do not stack" | A late, combat-only extra slot; random-stat re-roll pattern |
| 12 | https://stardewvalleywiki.com/Footwear | 1 boots slot, 18 boots with only Defence + Immunity; tailoring moves the stats onto another pair's looks | Looks and stats separated (relevant to whole outfits) |
| 13 | https://necessewiki.com/Trinkets | 4 trinket slots + 1 "ability" slot, rising to 8 via boss-dropped slot items; about 85 trinkets + 23 active ones, grouped mining/tool, mobility, light/vision, defence, damage, summons, building, utility; trade-off trinkets (Digging Claw, Jonas' Gambit) | Slot growth as a reward; a mining/building trinket family; a separate slot for an "active" item |
| 14 | https://necessewiki.com/Toolbox | Toolbox = Construction Hammer + Telescopic Ladder + Tool Extender + Item Attractor at the Tungsten Workstation | Combining real tools into one kit |
| 15 | https://necessewiki.com/Calming_Miners_Bouquet , /Mining_Charm , /Calming_Rose , /Item_Attractor | Mining Charm (+40% tool damage, desert cave chests) + Calming Rose (fewer monster spawns, snow cave chests) -> Bouquet; Item Attractor = reward of a journal challenge, then sold by an NPC for 200 | Found-in-a-biome sourcing; "do a challenge, then it's buyable" |
| 16 | https://sunhaven.wiki.gg/wiki/Accessories | 2 ring slots + 1 amulet + 1 keepsake; amulet stats (health, mana, attack speed, dodge) | A farming RPG's slot layout |
| 17 | https://sunhaven.wiki.gg/wiki/Rings | 29 rings + 26 marriage rings; small gathering stats: Fruit Ring "Extra Crop Chance 4%", Foraging Ring "Extra Forageable Chance 20%", Miner's Blessing "Mining Damage 10%", fishing minigame helpers, "Hardwood 8 per Day", trade-off rings | The nearest real example of harvest-yield accessories, and of their small numbers |
| 18 | https://sunhaven.wiki.gg/wiki/Keepsakes | 1 keepsake slot: a starting choice (6) or a gift from a partner (25): real objects with game-logical stats - "Liam's Oven Mitts: Bonus Farming EXP 12%", stethoscope, diary, tea pot, house key ("Gold Per Day 400") | Matches the brief: everyday objects whose effect is game-logical, not physical |
| 19 | https://sunhaven.wiki.gg/wiki/Fruit_Ring | Crafted at the Jeweler's Desk from 3 gold bars + 5 blueberries + 5 oranges (3 h), also found in chests | The recipe uses the thing it boosts (fruit for a crop ring) |
| 20 | https://grounded.wiki.gg/wiki/Trinkets_(Grounded) | Giant-bug backyard survival game: ONE trinket slot, about 49 trinkets crafted from bug parts, dropped by bugs, found as unique "badges" with a plus and a minus | Closest theme to ours (bug parts as materials, bug drops, resistances to heat/gas/dust) |
| 21 | https://grounded.wiki.gg/wiki/Intern_Badge , /Speed_Droplet , /Insulating_Larva_Spike | Intern Badge: hauling +15 planks, movement -30%; Speed Droplet +10% speed (stolen from aphids, 1 in 12); Larva Spike 50% heat protection (5% drop, or a guaranteed drop from one named larva) | Real numbers for a trade-off item, a speed item and a resistance item; a guaranteed source beside a random one |
| 22 | https://grounded.wiki.gg/wiki/Mutations_(Grounded) | 41 perks earned by DOING things (chop 50 grass blades -> tiers at 200, 500), 2 slots rising to 5, loadouts | "Earned by doing" as a source; a second, separate slot budget |
| 23 | https://dontstarve.wiki.gg/wiki/Dress_Tab | Wearables are everyday objects (straw hat, rain coat, walking cane, beekeeper hat) that "counter Seasons' effects" | Everyday-object wearables with game effects (the game also has magic items; only the everyday ones are relevant) |
| 24 | https://dontstarve.wiki.gg/wiki/Walking_Cane , /Beekeeper_Hat , /Miner_Hat | Cane "25% faster movement" but it fills the weapon hand; Beekeeper Hat "80% of damage taken from all types of Bees"; Miner Hat runs on FIREFLIES (refuel 38.5% = 180 s) | A trade-off by slot; a species-specific protection; an insect-fuelled lamp |
| 25 | https://apico.wiki.gg/wiki/APICO_Wiki , /wiki/Diving_Helmet | The beekeeping game has NO stat accessories: tools only (net, magnifying glass, hive wand); the Diving Helmet works "when in your inventory" | A bee game that put everything on tools and machines; the "works from the bag" key-item pattern |
| 26 | https://hollowknight.wiki/w/Notch | Charm budget: 3 notches at the start, 11 max; 45 charms; each charm costs 1-3 notches; "Overcharmed" = may exceed the budget but "all damage the Knight takes is doubled" | A cost-per-item budget instead of fixed slots |
| 27 | https://hollowknight.wiki/w/Wayward_Compass , /Gathering_Swarm , /Fragile_Greed , /Sprintmaster | Compass (1 notch, shows you on the map, 220 Geo), Gathering Swarm (collects dropped money, 300), Fragile Greed (+20% money, BREAKS on death, repair 150, made unbreakable for 9,000), Sprintmaster (~20% run speed; 39% with Dashmaster) | Cheap info items; a fragile/unbreakable upgrade path; a designed two-item synergy |
| 28 | https://terraria.wiki.gg/wiki/Alchemy_Table | A STATION that gives "a 1/3 (33.33%) chance for each ingredient not to be consumed" when making potions | Station output boosts can live in the station, not on the player |
| 29 | https://minecraft.wiki/w/Fortune | Tool enchantment: ore drops x1.33 / x1.75 / x2.2 on average at levels I-III; crops get +1 maximum drop per level | The biggest yield boosts in the genre sit on tools |
| 30 | https://wiki.factorio.com/Productivity_module | Machine module: +4% output, -5% speed, +40% energy, +5% pollution; "only ... intermediate products" | Output boost bought with a cost; limited to bulk materials |
| 31 | https://satisfactory.wiki.gg/wiki/Somersloop | A rare found object slotted into a machine: "+100% for doubled output" at up to "4x" power; 106 in the world | Station output as a rare exploration reward |
| - | Could not load: Core Keeper (corekeeper.wiki.gg is an unfinished Chinese placeholder; core-keeper.wiki.gg 404), Fae Farm and Coral Island (wiki.gg 401), Valheim (wiki.gg 401), Hollow Knight's main Charms page (503 - single charm pages were read instead). Fandom wikis skipped (402). | - | - |

---

## 2. Per game

At a glance (details and quotes in 2.1-2.9):

| Game | Accessory slots | How many | Combining / upgrading | Same item twice? | Random stats? |
|---|---|---|---|---|---|
| Terraria | 5 (6 Expert, 7 Master) + vanity slot each | 130+ on the category pages read | Yes - Tinkerer's Workshop, long chains | No ("Duplicate accessories cannot be equipped") | Yes, bonus-only prefixes, re-rollable |
| Stardew Valley | 2 rings + 1 boots (+1 trinket after combat mastery) | 30 rings, 18 boots, 8 trinkets | Forge merges 2 rings into 1 (20 shards); un-forge free | Allowed; magnet/glow rings stack | Trinkets only, re-roll 3 iridium bars |
| Necesse | 4 + 1 active ("ability"), up to 8 | about 85 + 23 active (counted from the page) | Yes - at tiered workstations | Not stated (**unverified**) | Not seen |
| Sun Haven | 2 rings + 1 amulet + 1 keepsake | 29 rings, 26 marriage rings, 7 amulets, 31 keepsakes | None found | Not stated (**unverified**) | Not seen |
| Grounded | 1 trinket (+ 2-5 perk slots) | about 49 trinkets, 41 perks | Perks tier up by doing | n/a (one slot) | A few "randomized status effect" items |
| Don't Starve | none (head / body / hand gear) | - | Upgrades by recipe (Straw Hat -> Miner Hat) | n/a | No; most wear out or use fuel |
| Hollow Knight | budget: 3 -> 11 notches, items cost 1-3 | 45 charms | Fragile -> Unbreakable for a fee | n/a | No |
| APICO | none - tools and machines only | 0 | - | - | - |

### 2.1 Terraria (Re-Logic, 2011-) - sources 1-8

- **Slots:** "In Classic Mode worlds, the player is limited to five accessory slots." Expert: a sixth by consuming
  a Demon Heart. Master: a sixth by default, seventh with the Demon Heart. Each slot also has a
  vanity slot (looks only, "no stat bonuses") and a dye slot. Loadouts let a player swap whole accessory sets.
- **Stacking rules:** "Duplicate accessories cannot be equipped." "The player can only equip one pair of wings at a
  time." An accessory and its own ingredients can be worn together but "their effects will not necessarily combine"
  (Spectre Boots + Hermes Boots: the speed does not add).
- **Random modifiers:** accessories roll a prefix that is bonus-only: "1-4 points of defense, 20 points of mana
  capacity, or a 1%-4% bonus on ... damage, critical strike chance, movement speed, or melee speed". Re-rolled at the
  Goblin Tinkerer for "one-third of the item's current value".
- **Categories on the page (13):** Movement (speed / air / water / other), Informational, Health and Mana, Combat
  (offensive / defensive), Debuff Immunity, Construction, Fishing, Yoyos, Miscellaneous, Vanity, Music Boxes, Golf
  Balls, Expert-only. No farming/harvest category exists (Terraria has no harvest-yield accessory on any page read).
- **How many:** the total is not stated. The category pages read list well over 130 between them (movement ~70 incl.
  combinations, informational ~23 + 5 combinations, construction 10, fishing ~14, miscellaneous ~15) before combat,
  immunity, health/mana and vanity.
- **How obtained:** found in biome chests and fishing crates (most movement items: Hermes Boots from Gold Chests,
  Flower Boots from jungle crates), bought (Toolbelt 10 gold from the Goblin Tinkerer; Extendo Grip, Brick Layer,
  Cement Mixer, Paint Sprayer 10 gold each from the Traveling Merchant), quest rewards (fishing items from the Angler's
  daily quests), enemy drops (Discount Card, Lucky Coin, Gold Ring from pirates), fished (Frog Leg, Balloon Pufferfish)
  and crafted (Magiluminescence at an anvil).
- **Combining (the Tinkerer's Workshop, 10 gold):** "combine multiple accessories into single items that usually
  provide the abilities of their components"; the result gets a new random modifier. Chains are long: Hermes Boots +
  Rocket Boots -> Spectre Boots; + Aglet + Anklet of the Wind -> Lightning Boots; + Ice Skates -> Frostspark Boots; +
  Lava Waders (itself a combination) -> Terraspark Boots - at least seven items' effects in one slot. Building: Brick
  Layer + Extendo Grip + Paint Sprayer + Portable Cement Mixer -> Architect Gizmo Pack; + Ancient Chisel + Treasure
  Magnet + Step Stool -> Hand of Creation. Fishing: Angler Earring + High Test Fishing Line + Tackle Box -> Angler
  Tackle Bag; + Lavaproof Fishing Hook -> Lavaproof Tackle Bag. Money: Gold Ring + Lucky Coin -> Coin Ring; + Discount
  Card -> Greedy Ring.
- **Information items need no slot:** "informational accessories do not need to be equipped in an accessory slot.
  They may be carried in the player's inventory or Void Bag without loss of functionality." They combine anyway
  (watch + depth meter + compass -> GPS; pocket guide + weather radio + sextant -> Fish Finder; all four combos -> PDA)
  to save bag space.

### 2.2 Stardew Valley (ConcernedApe, 2016-) - sources 9-12

- **Slots:** two rings ("any two rings"), one boots slot, one hat (looks only - unverified, not on the pages read),
  and since 1.6 a trinket slot unlocked after combat mastery (the Trinkets page does not state the count; 1 slot is
  **unverified**).
- **Stacking rules:** two identical rings may be worn; "Some ring effects stack" - the magnet rings "Stack with
  itself", glow rings stack with each other. Trinkets: "The player can obtain the same trinket multiple times.
  Trinkets do not stack."
- **Categories (rings, 30 listed, 1 unobtainable):** light (Small Glow 5 radius, Glow 10 radius), pickup range
  (Small Magnet +1 tile, Magnet +2 tiles), combined light + magnet (Glowstone Ring, crafted at Mining level 4; Iridium
  Band = glow + magnet + Ruby's +10% attack, Combat level 9), combat (Ruby +10% attack, Emerald +10% weapon speed,
  Aquamarine +10% crit chance, Jade +10% crit power, Amethyst +10% knockback), defence (Topaz +1, Crabshell +5,
  Immunity Band +4 immunity, Protection Ring +0.4 s invincibility, Sturdy Ring halves debuff time), on-kill effects
  (Vampire +2 health, Soul Sapper +4 energy, Savage +2 speed for 3 s, Napalm explosions, Burglar's "rolls twice on drop
  table"), one-off (Phoenix: once a day back to 50% health; Slime Charmer: no damage from one enemy family), luck
  (Lucky Ring +1), social (Wedding Ring). **No ring raises crop, fish, ore or forage yields** - those boosts live on
  professions, fertiliser and tool enchantments (see 2.2 note below).
- **Boots (1 slot, 18 pairs):** only Defence and Immunity, e.g. Sneakers +1/0, Rubber Boots 0/+1, Work Boots +2/0,
  Combat Boots +3/0, Firewalker +3/+3, Space Boots +4/+4, Mermaid Boots +5/+8. Better pairs sit deeper in the mine
  and cost more at the guild (500g -> 5,000g). "Footwear can be custom-tailored to transfer the stats from one pair
  to another" - looks and stats separated.
- **How obtained:** bought at the Adventurer's Guild once the player reaches a mine depth (Topaz/Amethyst 1,000g after
  the first quest; Aquamarine/Jade 2,500g after floor 40; Emerald/Ruby 5,000g after floor 80); unlocked by slaying
  goals (Vampire Ring: 200 bats; Burglar's Ring: 500 Dust Sprites; Napalm: 250 Serpents; Crabshell: 60 Rock Crabs);
  crafted when a skill reaches a level (Sturdy Ring at Combat 1: 2 copper bars + 25 bug meat + 25 slime; Glowstone at
  Mining 4: 5 solar essence + 5 iron bars); found (mine barrels, fishing treasure chests, Volcano chests: Hot Java,
  Protection, Soul Sapper, Phoenix); bundle rewards (Glow Ring from the Night Fishing bundle, Small Magnet from the
  Adventurer's bundle).
- **Combining - the Forge (Volcano floor 10):** two rings merge for "20 Cinder Shards"; "Two of the same ring cannot
  be combined into one" and "Three or more rings cannot be combined into one"; "Unforging is free, but only returns
  some of the Cinder Shards used". Net effect: 2 slots hold up to 4 ring effects late in the game.
- **Random re-rolls:** trinkets have random stats; "can be re-forged on an Anvil. This randomizes their stats and costs
  3 Iridium Bars per re-roll."
- **Note - where Stardew puts gathering boosts instead:** the Forge's tool enchantments: Generous (hoe: "50% chance of
  double item after digging" - items dug up, not crop harvests), Reaching (hoe / watering can / pan: area up to 5x5),
  Bottomless (watering can: infinite water), Preserving (rod: "50% chance that bait and tackle aren't consumed"),
  Master (rod: +1 fishing level), Auto-Hook, Swift ("33% faster"), Efficient (no energy drain), Shaving (axe: extra
  wood), Archaeologist (more artifacts). "Each weapon or tool can have only one enchantment ... and the applied
  enchantments are random"; re-applying (same price: one Prismatic Shard + 20 Cinder Shards) replaces it. This is the
  strongest counter-example: a farming game that keeps its accessory slots for combat/survival and puts harvest boosts
  on tools.

### 2.3 Necesse (Fair Games, 2019-) - sources 13-15

- **Slots:** "4 trinket slots and 1 ability trinket slot" at the start; up to 8 regular slots, each extra one from a
  boss-linked item (Void Wizard -> Empty Pendant -> 5; Pirate Captain -> Pirate Sheath -> 6; Fallen Wizard -> Wizard
  Socket -> 7; tier 5+ Incursion -> Wormhole Locket -> 8). The page warns that using a later slot item first skips the
  earlier ones. The ability slot takes one ACTIVE item (a shield that blocks a % of damage, or dash boots).
- **Stacking rules:** the Trinkets page states none; individual pages read state none (**unverified** whether duplicates
  are blocked).
- **Categories (as the page groups them):** mining/tool (Mining Charm +40% tool damage; Digging Claw +50% tool damage,
  +50% mining speed but -2 mining range; Tool Extender +mining range; Miner's Prosthetic: mining rocks cleaves),
  building (Construction Hammer +building speed; Telescopic Ladder +building range), utility (Item Attractor +pickup
  range; Fins "Doubles swim speed"; Calming Rose "Reduces mob spawn rate"; travel cloaks: big speed out of combat),
  light/vision (Shine Belt, Explorer Satchel "Lights up the area"; Will-o'-Wisp Lantern; Pirate Telescope and Explorer
  Cloak extend map-reveal range), mobility (Tracker/Spiked Boots +10-15% speed; Spiked Bat Boots +25%), defence
  (Chain Shirt +50 max resilience; Shell of Retribution / Spider Charm poison attackers), damage and crit (class "foci"
  +20% to one damage type and -20% to the others), summons, ammo savers (Ammo Box: "75%" bullet reduction),
  mana, dash.
- **How many:** the Trinkets page lists about 85 regular trinkets plus 23 ability trinkets (count made from the
  page; approximate).
- **How obtained:** found in biome chests (Mining Charm in desert cave chests; Calming Rose in snow cave chests),
  challenge rewards that then become buyable (Item Attractor: the "Swamp Surface Adventure Journal Challenge", then
  sold by the Elder for 200), boss/incursion drops, crafted.
- **Combining:** at workstations of rising tier. Toolbox = Construction Hammer + Telescopic Ladder + Tool Extender +
  Item Attractor (Tungsten Workstation): "Increases building speed / building range / mining range / item pickup
  range". Calming Miners Bouquet = Mining Charm + Calming Rose (Demonic Workstation): +40% tool damage, +25% mining
  speed, fewer spawns - and the calm part "can be toggled off".
- **Trade-offs are explicit:** Digging Claw (-2 mining range), Melee Foci (+20% melee, -20% other damage), Bloodstone
  Ring (-20 armour, +4 health/s regen below 50% health), Jonas' Gambit (+25 armour, +20% damage, +15% crit, -50%
  movement speed), Forbidden Spellbook (+50% magic damage, +100% mana use).

### 2.4 Sun Haven (Pixel Sprout, 2023) - sources 16-19

- **Slots:** "Each character has two ring slots", plus one amulet and one keepsake (Accessories page).
- **Stacking rules:** not stated on any page read (**unverified**).
- **Categories:**
  - Rings (29 + 26 marriage rings): health/mana, attack/spell damage tiers by metal (Copper +2, Iron +3, Adamant
    +4, Mithril +5, Sunite +7, each with a rising combat-level requirement), defence (Stone Ring +4), and a large
    GATHERING group with small numbers: Fruit Ring "Extra Crop Chance 4%" + 5 health; Foraging Ring "Extra Forageable
    Chance 20%"; Miner's Blessing "Mining Damage 10%"; Fisherman's Blessing "Fishing Minigame Speed 10%"; Ring of Quiet
    "Fishing Win Area 6%"; Farmer's Ring "Bonus Farming EXP 5%"; Hardwood Ring "Hardwood 8 per Day" (a daily
    delivery); Bounty Hunter's Ring "Enemy Gold Drop 20%". Trade-offs: Cracked Mage's Ring (health -4, mana +10),
    Explorer's Blessing (defence -2, mana +8, movement speed 3%).
  - Amulets (7): health/mana/regen/attack speed/dodge, Amulet of Immortality "Invulnerability Time 25%".
  - Keepsakes: chosen at character creation (6: Adventure, Peace "Bonus Farming EXP 5%", Warrior, Romance, Time,
    Riches "Gold Per Day 80") or given by a partner (25). These are everyday objects with game-logical effects:
    Liam's Oven Mitts "Bonus Farming EXP 12%", Wornhardt's Stethoscope (accuracy, regen), Jun's Diary (regen,
    health), Miyeon's Tea Pot (bonus experience), Claude's House Key "Gold Per Day 400", Anne's Pearl Earrings "Gold
    Per Craft 4, Gold Per Day 180", Lynn's Shield "Mining Damage 5%", Kitty's Cat Toy "Fishing Skill 5".
- **How obtained:** the Rings page says rings "can be obtained through shops, crafting, exploration, and special
  events" (the coin column is the sell price). Example: Fruit Ring crafted at a Jeweler's Desk from "3 Gold Bar, 5
  Blueberry, 5 Orange" (3-hour craft) or from a chest. Marriage rings come from marrying that character; keepsakes from
  the start choice or relationship progress.
- **Combining / upgrading:** none found on the pages read.
- **Take-away:** Sun Haven proves gathering-yield accessories work in a farming RPG, but keeps them small (4% extra
  crop) and mixes them with health/mana so most slots go to combat stats. Its stat list is long and fiddly (bonus
  EXP, gold per day, tickets per day) - a model of breadth, not of clarity.

### 2.5 Grounded (Obsidian, 2020-2022) - sources 20-22 (the nearest theme: shrunk humans among giant bugs)

- **Slots:** ONE trinket slot ("Accessories"). Separately, 2 mutation (perk) slots rising to 5, with up to 4 saved
  mutation loadouts.
- **Stacking rules:** with one slot, none needed. Unique items can be copied with the "Super Duper" for science
  points (Intern Badge: 7,500 Raw Science).
- **Categories (about 49 trinkets, one of them test-mode only; tiers 1-3):** crafted at a workbench from bug parts and
  backyard materials (Astonishing Acid: 5 Acid Gland + 2 Sap; Nifty Needle: 1 Thistle Needle + 2 Sap + 3 Gnat Fuzz;
  Sturdy Shell: 1 Acorn Shell + 2 Sap + 3 Grub Hide); creature drops (Wasp Queen Trinket: arrow refund; Mantis
  Trinket; Insulating Larva Spike: "50% sizzle protection" - 5% drop from Ladybird Larvae, or a guaranteed drop from
  one larva in the Ladybird Burrow); resource-node drops (Fungal Charm: explosive resist, from Haze Fungus); stolen
  from creatures with the Sticky Fingers trinket (Speed Droplet: "+10%" movement speed, 1 in 12 from aphids); found
  once, as unique "badges" that each carry a plus and a minus (Intern Badge: "Hauling Strength by 15 planks" but
  "movement speed by 30%" lower; Defense Badge: +damage resist, -attack; Toxicology Badge: +gas resist, +dust guard,
  -poison resist).
- **What the trinkets do:** mostly combat perks and RESISTANCES to the backyard's hazards (heat "sizzle", gas, dust,
  explosions, falls, diving), plus a few utility (hauling, food generation). No gathering-yield trinket; the
  gathering-themed perks (Grass Master, Rock Cracker) are mutations, unlocked by doing that gathering (their effects
  were not on the page read).
- **Mutations - earned by doing (41):** "Grass Master" unlocks after "Chop 50 Blades of Grass" and tiers up at 200 and
  500; "Rock Cracker" after busting 25 rocks (60, 105); "Natural Explorer" after discovering 20 landmarks (50, 80).
  Some are bought from the robot vendor with science instead, and those don't tier up.
- **Take-away:** a one-slot design forces a real choice every outing (heat cave -> heat trinket); bug-part recipes
  make every accessory a reason to hunt a specific bug; the unique found badges are prized because each has a
  memorable downside.

### 2.6 Don't Starve (Klei, 2013-) - sources 23-24

- **Slots:** three equipment slots - head, body, hand (the hand slot is also the weapon/tool slot). No separate
  accessory slots (slot names from the pages read; the full slot list is not stated on them - **unverified** beyond
  head/body/hand).
- **What wearables do:** the Dress tab says they "make it easier to counter Seasons' effects such as Freezing,
  Overheating, or Wetness, often granting extra Sanity regeneration too." Every item is an everyday object: Straw Hat,
  Top Hat, Winter Hat, Rain Hat, Rain Coat, Beekeeper Hat, Walking Cane, Eyebrella.
- **Numbers:** Walking Cane "25% faster movement speed", infinite durability, but it takes the hand slot so the player
  swaps to a weapon to fight. Beekeeper Hat: "80% of damage taken from all types of Bees" (bees only), 750 durability,
  made from 8 silk + 1 rope. Miner Hat: a lamp that runs about one in-game day and is refuelled with FIREFLIES (one
  firefly = 38.5% = 180 s), light bulbs or slurtle slime.
- **How obtained:** crafted, gated by a research station tier (the Alchemy Engine).
- **Durability/fuel:** most wearables wear out or burn fuel - a running cost (Bug Farmer has decided tools never wear
  out, D49; whether that extends to accessories is open).

### 2.7 APICO (TNgineers, 2022) - source 25 (a beekeeping game - a "no accessories" data point)

- No stat accessories, hats or rings appear in the wiki's navigation; everything is tools (Butterfly Net, Magnifying
  Glass, Hive Wand, Fishing Rod...) and machines. The Diving Helmet is a key item: "Allows you to dive in the deeper
  patches of water when in your inventory", bought for 500 Rubees.
- **Take-away:** a bug/bee game can carry its whole progression on tools and stations; accessories are optional
  extra depth, not a requirement.

### 2.8 Hollow Knight (Team Cherry, 2017) - sources 26-27 (the "budget" model)

- **Slots:** no fixed slots - a notch budget. "The Knight begins with 3 notches, and 8 additional notches can be
  acquired ... for a maximum of 11." Each charm costs 1-3 notches. Notches come from a shop that unlocks as you
  collect charms (120 Geo after 5 charms; 500 after 10; 900 after 18; 1,400 after 25), from exploration, and from
  beating challenges.
- **Over-budget rule:** "If the Knight has free Notches but not enough remaining to equip a desired Charm, the Knight
  can be Overcharmed" - the charm goes on, but "all damage the Knight takes is doubled" - a deliberate risk option.
- **How many:** "A total of 45 charms exist."
- **Examples:** Wayward Compass, 1 notch, "Shows the Knight's location on map", 220 Geo - the shopkeeper recommends it
  early and the wiki suggests dropping it for combat charms later (an information item that competes for budget).
  Gathering Swarm, 1 notch, "Collects dropped Geo", 300 Geo. Sprintmaster, "Increases run speed by ~20%" (8.3 ->
  10), 400 Geo; with Dashmaster the bonus becomes 39% (designed synergy). Fragile Greed, 2 notches, "Enemies drop
  20-100% more Geo" but "will break if its bearer is killed" (repair 150 Geo); an NPC makes it unbreakable for 9,000
  Geo - a late money sink that removes the risk.
- **Take-away:** a cost-per-item budget lets small utility items (compass, coin collector) coexist with big ones
  without needing more slots; the shop that sells notches unlocks by how many charms you own, so collecting itself
  grows the budget.

### 2.9 Where other games put "more output from stations" - sources 28-31

None of the accessory lists read has a worn item that raises a crafting station's output, except Sun Haven's small
"Gold Per Craft" stat on two keepsakes (+4, +5 coins per craft). Output boosts live elsewhere:
- **In the station:** Terraria's Alchemy Table gives "a 1/3 (33.33%) chance for each ingredient not to be consumed"
  when brewing, checked per ingredient. Factorio's productivity module 1: "+4%" output but "-5%" speed, "+40%"
  energy, "+5%" pollution, and only for "intermediate products" (bulk materials, not finished items). Satisfactory's
  Somersloop, a rare found object put into a machine: "+100% for doubled output" for up to "4x" the power; "106
  Somersloops in the world".
- **On the tool:** Minecraft's Fortune: ore drops average x1.33 / x1.75 / x2.2 at levels I / II / III; crops get one
  more possible drop per level. Stardew's Generous hoe: "50% chance of double item after digging".
- **Take-away for us:** worn station boosts are rare in the genre, so there is room to do something new, but two
  lessons carry over: (1) output boosts only make sense on BULK products (bars, planks, thread, honey, meals), never on
  one-off gear (Factorio limits them to intermediates); (2) a big output boost is paid for with something (speed,
  energy, rarity).

---

## 3. Concrete examples by activity (exact effects and numbers)

All quotes are from the source pages in section 1. "(tool)" or "(station)" marks a boost that is NOT an accessory
in that game but answers the same need.

### 3.1 Farming and harvest
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Fruit Ring (Sun Haven) | "Extra Crop Chance 4%", Health 5 | Jeweler's Desk: 3 gold bars + 5 blueberries + 5 oranges; chests |
| Liam's wedding ring (Sun Haven) | "Extra Crop Chance 8%", bonus experience 10%, health 25 | Marrying that character |
| Foraging Ring (Sun Haven) | "Extra Forageable Chance 20%" | Rings come from "shops, crafting, exploration, and special events" |
| Farmer's Ring / Liam's Oven Mitts (Sun Haven) | "Bonus Farming EXP 5%" / "12%" | Ring: as above; mitts: a partner's keepsake |
| Hardwood Ring (Sun Haven) | "Hardwood 8 per Day" | as above |
| Flower Boots (Terraria) | "Causes flowers to grow where the wearer walks on grass" | Jungle crates / Ivy chests |
| Guide to Plant Fiber Cordage (Terraria) | "Causes destroyed vines to drop Vine Rope" | Chests; Skeleton Merchant 2 gold 50 silver |
| Generous hoe (Stardew, tool) | "50% chance of double item after digging" | Forge enchantment (random) |
| Reaching / Bottomless can (Stardew, tool) | area "to 5x5 tiles" / "Infinite water" | Forge enchantment (random) |
| Fortune (Minecraft, tool) | crops: one more possible drop per level | Enchanting |

Observation: of the accessory lists read, only Sun Haven gives a direct crop-yield accessory, and its numbers are
small (4%, 8% on a marriage ring). Terraria and Stardew have none.

### 3.2 Crafting and station output
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Zaria's Doubloon / Anne's Pearl Earrings (Sun Haven) | "Gold Per Craft +5" / "Gold Per Craft 4" (plus gold per day) | Partner keepsakes |
| Alchemy Table (Terraria, station) | "a 1/3 (33.33%) chance for each ingredient not to be consumed" (potions) | Found in the Dungeon |
| Productivity module 1 (Factorio, station) | +4% output, -5% speed, +40% energy, +5% pollution; intermediates only | Crafted |
| Somersloop (Satisfactory, station) | "+100% for doubled output", power "up to 4x" | 106 found in the world |
| Brick Layer (Terraria) | "Increases item placement speed by 50%" | Traveling Merchant, 10 gold |
| Portable Cement Mixer (Terraria) | "Increases wall placement speed by 50%" | Traveling Merchant, 10 gold |
| Extendo Grip (Terraria) | placement and tool range +3 across, +2 up/down | Traveling Merchant, 10 gold |
| Toolbelt (Terraria) | "Increases block placement range by 1" | Goblin Tinkerer, 10 gold |
| Toolbox (Necesse) | building speed, building range, mining range, item pickup range (no numbers on the page) | Combined from 4 trinkets at the Tungsten Workstation |

### 3.3 Fishing
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Angler Earring (Terraria) | "Increases fishing power by 10" | Fishing quest rewards |
| High Test Fishing Line (Terraria) | "Prevents fishing line from breaking" | Fishing quest rewards |
| Tackle Box (Terraria) | "Decreases chance of bait consumption" (no number on the page) | Fishing quest rewards |
| Angler Tackle Bag (Terraria) | all three above in one slot | Combined at the Tinkerer's Workshop |
| Inner Tube (Terraria) | float on liquids; "fishing power by 5 when in liquids" | Water chests, ocean crates |
| Fisherman's Pocket Guide (Terraria) | "Displays fishing power" - works from the bag | Informational |
| Fisherman's Blessing Ring (Sun Haven) | "Fishing Minigame Speed 10%" | Shops/crafting/exploration |
| Ring of Quiet (Sun Haven) | "Fishing Win Area 6%" | as above |
| Preserving rod (Stardew, tool) | "50% chance that bait and tackle aren't consumed" | Forge enchantment |
| Master rod (Stardew, tool) | "Adds an extra fishing level" | Forge enchantment |

### 3.4 Mining
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Ancient Chisel (Terraria) | "Increases mining speed by 25%" | Desert fishing crates, Sandstone chests |
| Mining Charm (Necesse) | "Increases tool damage by 40%" | Desert cave chests |
| Digging Claw (Necesse) | +50% tool damage, +50% mining speed, "-2 mining range" | (source not on the page read) |
| Calming Miners Bouquet (Necesse) | +40% tool damage, +25% mining speed, fewer monster spawns (toggle) | Mining Charm + Calming Rose, Demonic Workstation |
| Miner's Blessing Ring (Sun Haven) | "Mining Damage 10%" | Shops/crafting/exploration |
| Glow Ring / Small Glow Ring (Stardew) | "Emits 10 radius circle of light" / "5 radius" | Mine floors (slimes, barrels), fishing chests, a bundle |
| Glowstone Ring (Stardew) | 10-radius light + 2 tiles magnetism | Crafted at Mining level 4: 5 solar essence + 5 iron bars |
| Metal Detector (Terraria) | "Displays nearby valuable objects" - from the bag | Informational |
| Miner Hat (Don't Starve) | light for about a day; refuel with fireflies (one = 180 s) | Crafted: straw hat + gold nugget + fireflies |
| Fortune (Minecraft, tool) | ore drops average x1.33 / x1.75 / x2.2 | Enchanting |

### 3.5 Catching and collecting
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Treasure Magnet (Terraria) | item pickup range "from 2.625 to 12 tiles" | Shadow chests / Obsidian lock boxes |
| Gold Ring (Terraria) | coin pickup range "from 2.625 to 24.5 tiles" | Pirate drop |
| Lifeform Analyzer (Terraria) | "Displays the name of nearby rare enemies, critters, and NPCs" (critters are what the bug net catches) | Informational |
| Small Magnet / Magnet Ring (Stardew) | "Increases Magnetism by one tile" / "two tiles"; stack with each other and themselves | Bundle reward; mine drops; barrels |
| Item Attractor (Necesse) | "Increases item pickup range" | Journal challenge reward, then the Elder sells it for 200 |
| Gathering Swarm (Hollow Knight) | "Collects dropped Geo" | Shop, 300 Geo |
| Sticky Fingers (Grounded) | steals an item from a creature (Speed Droplet: 1 in 12 from aphids) | Found once (a chewed-gum spot) |
| Burglar's Ring (Stardew) | "Monsters drop items more often; rolls twice on drop table" | Slaying goal (500 Dust Sprites) |

Observation: no accessory read raises the chance of CATCHING a creature; catching is always a tool (Terraria's bug
nets, APICO's butterfly net). That is a gap Bug Farmer can fill.

### 3.6 Movement
| Item (game) | Exact effect | How obtained |
|---|---|---|
| Aglet / Anklet of the Wind (Terraria) | "+5%" / "+10%" movement speed | Chests; jungle crates |
| Hermes Boots (Terraria) | top run speed raised to 22.5 tiles/s (Magiluminescence's figure puts the default near 11.25) | Gold chests |
| Dunerider Boots (Terraria) | as Hermes, plus 15% more speed and 75% more acceleration on sand | Desert chests and crates |
| Lightning Boots (Terraria) | "+8%" speed, flight, 25.31 tiles/s top speed | Combined: Spectre Boots + Anklet + Aglet |
| Panic Necklace (Terraria) | "+100% for five seconds after the wearer takes damage" | Crimson hearts and crates |
| Tracker / Spiked Boots; Spiked Bat Boots (Necesse) | "+10%-15%"; "+25%" movement speed | (not on the page read) |
| Fins (Necesse) | "Doubles swim speed" | (not on the page read) |
| Speed Droplet (Grounded) | movement speed "by 10%" | Stolen from aphids, 1 in 12 |
| Walking Cane (Don't Starve) | "25% faster movement speed", but fills the weapon hand | Crafted |
| Sprintmaster (Hollow Knight) | "~20%" run speed (8.3 -> 10); 39% with Dashmaster | Shop, 400 Geo |
| Savage Ring (Stardew) | "3-second Speed (+2) buff after slaying monster" | Slaying goal (150 Void Spirits) |
| Explorer's Blessing Ring (Sun Haven) | "Movement Speed 3%", Defence -2, Mana +8 | Shops/crafting/exploration |

---

## 4. How these games keep a big accessory list from feeling like bloat

1. **Every item has one job you can name.** Terraria's 130+ are sorted into jobs (movement, information,
   construction, fishing, immunity...), and within a job the items do different things (a speed boot, a climbing
   claw, a flipper), not the same thing at +5%. Stardew's 30 rings split into light, pickup range, attack, crit, speed,
   defence, on-kill effects. The bloat cases are the opposite: Sun Haven's rings repeat "Health +4 / +8 / +12 / +16 /
   +20" and "Attack Damage +2 / +3 / +4 / +5 / +7" by metal - many items, few decisions.
2. **Situational items: great in one place, idle elsewhere.** Dunerider Boots only shine on sand, Ice Skates on ice,
   Inner Tube in water, Lavaproof Fishing Hook in lava (Terraria); the Beekeeper Hat only blocks bees (Don't Starve);
   Slime Charmer Ring only slimes (Stardew); Insulating Larva Spike only heat (Grounded). A situational item can be
   strong without breaking the game, and it makes packing for a trip a decision ("heading to the heat cave - swap in
   the spike").
3. **Information items cost no slot, or almost none.** Terraria: they "do not need to be equipped", they work from
   the bag, and they still combine (GPS, Fish Finder, PDA) so the bag isn't cluttered. Hollow Knight: the compass
   costs 1 of 3-11 notches and the wiki itself suggests swapping it for combat charms before boss fights. Either
   way, knowing things never competes with doing things for long.
4. **Combining turns old items into progress instead of clutter.** Terraria's chains (Hermes + Rocket Boots + Aglet +
   Anklet + Ice Skates + Lava Waders into Terraspark Boots; 7 building gadgets into the Hand of Creation; 3 fishing
   items into the Tackle Bag), Stardew's two-rings-into-one at the Forge, Necesse's Toolbox. Every early item stays
   useful as an ingredient, and the slot limit grows "for free" late in the game without adding slots.
5. **Trade-offs make a choice out of a single item.** Grounded's found badges each carry a minus (Intern Badge: +15
   planks hauled, -30% speed); Necesse's foci (+20% one damage type, -20% the others) and Digging Claw (-2 range);
   Sun Haven's Explorer's ring (-2 defence). Hollow Knight's over-budget charm doubles damage taken.
6. **Families replace each other instead of stacking.** Terraria: "Duplicate accessories cannot be equipped", "only
   one pair of wings", and an item worn with its own ingredient doesn't add up. Within a family, the better item
   replaces the worse one, so tiers don't multiply slots.
7. **A budget, not just a count.** Hollow Knight prices items in notches (1-3), so a cheap utility item and a big
   item compete on the same budget, and the budget itself grows as a reward (shop unlocks after 5 / 10 / 18 / 25
   charms owned). Necesse and Grounded grow slots through bosses and items.
8. **Sources are spread across activities.** Stardew sells rings by mine depth reached and awards some for slaying
   goals; Terraria hides them in biome chests and fishing crates and gives fishing ones for quests; Grounded makes
   them from bug parts and finds unique ones in hidden spots. The list feels like a collection to complete across the
   whole world, not a shop catalogue.
9. **Visible vs invisible.** Most Terraria construction and fishing accessories show "Visible on character: No";
   Stardew rings are not drawn. Small pocket/wrist items need no art on the body - relevant because Bug Farmer
   draws each outfit as one whole image set.
10. **Where bloat does creep in:** stat soup that needs a spreadsheet (Sun Haven's bonus EXP, tickets per day, gold
   per craft, gold per day, orbs per day); random rolls that make the same item good or bad (Terraria prefixes,
   Stardew trinkets), which turn into a re-roll grind; and many near-identical tiers.

---

## 5. Patterns to copy, patterns to avoid, and candidate accessories for Bug Farmer

### 5.1 What Bug Farmer has already decided that shapes accessories
Restated from `docs/gdd/overview.md` and `docs/product/economy/DECISIONS.md` (dates are the owner's decisions):
- One whole outfit at a time; each role (combat, mining, fishing, farming, bug-catching, beekeeping, stealth...) has
  its own best outfit, and non-combat outfits raise a yield or make a job easier (2026-08-06, 2026-09-27). So the
  ROLE bonus already lives on the outfit.
- No magic (P2, 2026-09-28); no mammals, and birds, amphibians and reptiles died out too (2026-09-27) - so no
  horseshoes, wool, horn, feathers, frogs. Bug materials exist: chitin, bug leather (from flies and butterflies),
  silk, venom, formic acid, honey.
- No upkeep chores: tools never wear out (2026-09-27). Dying costs little (2026-09-27).
- Dodging is the only defensive move (2026-07-11); stamina is a small pool for dodging and running (P14, 2026-09-28).
- No mining dangers - no gas, no cave-ins (2026-09-27); no diving (August 2026); shallow water is waded in a wading
  OUTFIT, with no separate waders item (2026-09-27). The underground is pitch dark (2026-07-08); light comes from bug
  lanterns, torches and electric lights (D12, 2026-09-27), and the overview's tools summary also lists a headlamp.
- Potions already cover night sight, venom resistance, antivenom and a salve for sprays and acid (P16, 2026-09-27).
- The basic stations stand in the village and belong to the townspeople - players use them but can't take them
  (2026-09-28). Electronics are bought, never player-made (D1, D26).
- Examining an item shows what it does and the real biology behind it (2026-09-26).
- A loupe accessory was confirmed in June (D12, 2026-06-25), and the General Store was to sell garden gloves with a
  harvest bonus (D26, 2026-06-27) - both before the earlier accessory ideas were judged not to fit (2026-09-27).
- In the prototype: 2 accessory slots; the accessories in the game do nothing yet.

### 5.2 Patterns to copy (and why)
1. **Role on the outfit, task on the accessory.** Because outfits already carry the role bonus, an accessory that
   repeats it ("+farming yield") would just multiply with the farming outfit. Better: accessories do a narrower job -
   one station, one species, one terrain, one tool - or a utility the outfits don't (reach, pickup, stamina,
   information). Stardew splits the same way: boots carry only defence/immunity, rings do everything else.
2. **One of each; families replace each other.** Terraria's "Duplicate accessories cannot be equipped" and "one pair
   of wings". With only 2 slots, two Garden Gloves would become the mandatory farming build. A headlamp family
   (glowworm -> LED) should replace, not add up.
3. **Information items work from the bag** (Terraria's informational accessories). Real gadgets - barometer, metal
   detector, field guide, two-way radio - that never compete with the 2 slots. This fits the decided "examine shows
   the real biology" and the curiosity pillar.
4. **Strong but situational.** Species-, zone- or terrain-specific items (Don't Starve's Beekeeper Hat: 80% vs bees
   only; Terraria's Dunerider Boots on sand; Grounded's 50% heat protection) can carry big numbers without breaking
   the game, and every new zone adds a reason to re-pack. Bug Farmer's zones are already themed by species (Scorpion
   Rocks, Spider Vale, the swamps), so accessories can be too.
5. **Make them from the thing they help.** Sun Haven's Fruit Ring uses fruit; Grounded's trinkets use bug parts.
   Recipes in chitin, silk, venom and bug leather tie each accessory to the food chain (farm wasps -> make the
   wasp-themed item), which is Bug Farmer's progression.
6. **Combining as late progression.** Terraria's Tinkerer's Workshop, Stardew's Forge, Necesse's Toolbox: two or three
   early items merge into one kit, so 2 slots carry more late in the game without adding slots, and early items never
   become junk. Real-world framing fits: a "builder's kit", a "tackle bag", a "field kit".
7. **A few trade-offs, not many.** Grounded's badges (+15 planks hauled, -30% speed) and Necesse's foci are memorable
   because they are the exception. Give a handful of items a clear minus; keep the rest clean.
8. **Small yield numbers on worn items, big ones on tools and stations.** Sun Haven's worn crop bonus is 4% (8% on a
   marriage ring); Minecraft's tool-borne Fortune reaches x2.2; Factorio's station module is +4% and costs 40% more
   energy. Worn yields stack with outfit, fertiliser and plot decorations, so they should stay a modest "chance of
   one extra".
9. **Spread the sources over the whole game.** Stardew unlocks ring sales by mine depth and awards rings for slaying
   goals; Terraria's fishing accessories come from the fisherman's quests; Necesse's Item Attractor becomes buyable
   after a challenge; many of Grounded's pieces are bug drops or hidden finds. For us: village shops, the western town,
   the Fisherman, the Ecologist's tasks, bug-extractor materials and zone secrets - one or two accessories per zone,
   the way nearly every zone is meant to hide an outfit recipe.
10. **Invisible pocket/wrist/belt objects.** Most Terraria construction and fishing accessories are "Visible on
   character: No" and Stardew rings are not drawn. Because each Bug Farmer outfit is drawn as one whole image set,
   accessories that sit in a pocket or on a belt need no per-outfit art.
11. **Quick-swap sets for job-specific items.** Grounded saves up to 4 perk sets; Terraria has accessory loadouts. If
   station items are worn (see 5.4), one key that swaps a saved pair keeps "put on the tape measure before the
   sawmill" from becoming a chore.

### 5.3 Patterns to avoid (and why)
1. **Random stats and re-roll grinds** (Terraria's prefixes and Reforge, Stardew's trinket re-roll for 3 iridium
   bars). Two copies of the same item behaving differently fights "the description says what it does"; re-rolling is
   a coin sink with no play in it.
2. **Luck stats** (Stardew's Lucky Ring, Terraria's Lucky Coin and Horseshoe). Luck charms are out, and horseshoes are
   a mammal-era object the GDD already removed.
3. **Magic and transformations** (Terraria's Cloud in a Bottle, Moon Charm). Out under P2.
4. **Wear, fuel and breaking** (Don't Starve's refuelled Miner Hat; Hollow Knight's Fragile charms that break on
   death). These are upkeep chores, and dying is meant to cost little.
5. **Stat soup** (Sun Haven's bonus EXP, gold per craft, gold/tickets/orbs per day). Bug Farmer has no experience
   points, and daily income for wearing an item pays players for being idle on a persistent server - against
   "machines ease chores but never play for the player".
6. **Near-identical tiers** (Sun Haven's attack rings +2 / +3 / +4 / +5 / +7 by metal; its health rings). The metal
   ladder belongs to tools and armour; a second metal ladder of stat rings is many items with no decisions.
7. **Active defensive items** (Necesse's ability slot: shields that block 40-100%). Dodging is the decided only
   defensive move.
8. **Items for systems the game has ruled out** (gas masks - no mining dangers; diving gear - no diving; waders - the
   wading outfit does that).
9. **Stacking two of the same** (Stardew's magnet rings "stack with itself"). With 2 slots that makes one item
   compulsory.
10. **A big multiplier on a worn item** (anything near Fortune's x2.2). It multiplies with the outfit, fertiliser and
   decorations and makes the item mandatory.
11. **Information that costs a slot.** The Hollow Knight wiki advises swapping the compass out for combat charms before
   boss fights; with only 2 slots, a slot-costing information item would rarely be worn.
12. **Hidden technical cost (Bug Farmer-specific):** an accessory that changes how BUGS behave (a repeller, a scent
   blocker, a longer smoker calm) feeds the deterministic bug simulation that every player must compute identically;
   it has to be wired through the bug-sync recipe (`frontier-sync` skill). Yields, stations, movement, light and
   information do not (catch reach and drag speed may count too - to check against
   `docs/product/architecture/architecture_swarm_sync.md`). Such items are fine, but cost more to build - they are
   marked "Sim" in the list below.

### 5.4 Recommendations on structure (owner's call where marked)
- **Slots:** keep 2 worn slots, information items free in the bag, and combining (5.2 #6) as the late-game way to
  carry more. One extra slot as a late reward (as Necesse and Hollow Knight grow theirs) is worth considering -
  **owner's call** (the slot count is still open in §08).
- **Station output from a worn item - how it should apply:** worn station items act on jobs the wearer STARTS, locked
  in when the job starts (swapping mid-job changes nothing; the job's tooltip names the bonus), and only on bulk
  products (bars, planks, thread, dye, meals, honey, extractor materials) - never on one-off gear, where "an extra"
  makes no sense (Factorio limits its module the same way). Installing the bonus into the station instead (Terraria's
  Alchemy Table, Factorio, Satisfactory) doesn't fit the village stations, which belong to the townspeople. A
  saved-set quick swap (5.2 #11) removes the swap chore. In co-op, the friend wearing the tape measure runs the
  sawmill - a small role.
- **Numbers:** a worn yield item as "a chance of one extra" in the 10-25% range, as Sun Haven and Terraria's Alchemy
  Table do; speed items 10-30%; situational items can go higher (40-80%) because they only work in one place. These
  ranges come from section 3, not from testing - **illustrative, not decided**.
- **Showing it:** examining any accessory states its number and the real reason it works ("rosin improves grip"; "a
  scorpion's shell glows under UV light"), as decided for all items.

### 5.5 Candidate accessories (50)

All numbers are illustrative sizes from section 3 for discussion, not proposals to lock. "Bag" = works from the bag,
takes no slot. "Sim" = changes bug behaviour (5.3 #12). "Needs" = depends on a system not built yet. Early = the
village, Bee Meadow, the first mine and Ant Tunnels; mid = the next ring of zones and the western town; late = the
far and deep zones.

| # | Real object | One effect (illustrative) | Lever | When | Notes |
|---|---|---|---|---|---|
| | **Farming and harvest** | | | | |
| 1 | Garden gloves (cotton, bug-leather palms) | Harvesting a crop: 15% chance of one extra | Harvest amount | Early | The General Store was to sell them (D26, 2026-06-27) |
| 2 | Seed tin | Harvesting: 20% more often a seed comes back | Harvest amount (seeds) | Early | |
| 3 | Harvest knife (hori-hori) | Cutting a plant down: 20% chance of one extra part | Harvest amount (cut plants) | Early-mid | Uses P11's cut-down plants |
| 4 | Orchard picking bag | Fruit knocked from a tree drops straight into your bag; 10% chance of one extra | Harvest amount + pickup | Early-mid | How fallen fruit is collected is still open |
| 5 | Soil test kit | Shows every plot's water and fertiliser at a glance | Information | Early | Bag |
| | **Bugs, catching and ranching** | | | | |
| 6 | Hive tool (steel) | Harvesting a hive: 25% chance of an extra honeycomb | Bug-product yield | Early | Bee Meadow |
| 7 | Field guide | Names the highest-tier bug within 20 squares (like Terraria's Lifeform Analyzer) | Information | Early | Bag; check overlap with magnifying-glass research (P8) |
| 8 | Telescopic net pole | Hand nets reach one square further | Catch reach | Early-mid | |
| 9 | Rubber grip gloves | Drag a subdued big bug 25% faster | Drag speed | Mid | Uses P15; possibly Sim (a dragged bug moves) |
| 10 | Smoker fuel tin (pine needles) | Smoke keeps bees calm 30% longer | Calm duration | Early-mid | Sim |
| 11 | Ultrasonic repeller | Small biting bugs keep 3 squares away - but you can't net anything while it's on | Protection, with a trade-off | Mid | Sim; bought (electronics) |
| | **Station output (jobs you start; bulk products only)** | | | | |
| 12 | Oven mitts (silk-padded) | Meals you cook: 20% chance of an extra portion | Station output (cooking) | Early | |
| 13 | Compost thermometer | Compost bins you fill finish 25% sooner | Station speed | Early | |
| 14 | Tape measure | Sawmill: 20% chance of an extra plank per log ("measure twice, cut once") | Station output | Early | |
| 15 | Thimble (bronze) | Loom and sewing machine: 25% chance a job uses no thread | Ingredient saving | Early-mid | |
| 16 | Classifier sieve (steel mesh) | Crusher and sluice: 15% chance of an extra piece | Station output (ore chain) | Mid | |
| 17 | Infrared pyrometer | Furnace jobs finish 25% sooner | Station speed | Mid | Bought (electronics) |
| 18 | Mortar and pestle (stone) | Dye station: 20% chance of an extra dye | Station output | Mid | Examine text: cochineal red comes from a scale insect |
| 19 | Dissecting kit | Bug extractor: 20% chance of an extra material (chitin, bug leather, formic acid...) | Station output | Mid | |
| 20 | Measuring cylinder (glass) | Cauldron: each ingredient has a 25% chance not to be used | Ingredient saving | Mid | Terraria's Alchemy Table does 33% |
| 21 | Canvas work apron | Every station job you start finishes 10% sooner | Station speed (all) | Mid | The generalist beside the specialists |
| | **Mining and the dark** | | | | |
| 22 | Headlamp (glowworm, later LED) | Light around you with both hands free: radius 3 (glowworm), 6 (LED) | Light | Early / mid-late | One family - the LED replaces the glowworm; the overview already lists a headlamp as a light source |
| 23 | Prospector's loupe (glass) | Breaking stone: 10% chance of a rough gem | Harvest amount (gems) | Mid | A loupe accessory was confirmed in D12 |
| 24 | Specimen bag (canvas) | Breaking an ore block: 15% chance of one extra ore | Harvest amount (ore) | Mid | |
| 25 | Metal detector | Marks ore veins within 8 squares | Information | Mid | Bag; bought (electronics) |
| | **Fishing** | | | | |
| 26 | Polarised sunglasses | See fish shadows under the surface | Vision / information | Early | Real: polarising lenses cut surface glare |
| 27 | Tackle box | 30% chance bait isn't used | Ingredient saving | Early | The Fisherman's |
| 28 | Fingerless fishing gloves | The mini-game's catch zone is 15% bigger | Fishing mini-game | Early-mid | Needs the fishing mini-game |
| 29 | Bite alarm | Fish bite 20% sooner and it beeps when one does | Fishing speed | Mid | Bought (electronics) |
| 30 | Angler's almanac | Shows which fish bite here at this hour | Information | Early | Bag |
| | **Movement and stamina** | | | | |
| 31 | Pedometer | Running uses 20% less stamina | Stamina | Early | Uses P14 |
| 32 | Trail-running insoles | 10% faster on paths and floors | Movement (situational) | Early-mid | Rewards laying paths |
| 33 | Knee pads (chitin plates, silk straps) | Dodging costs 25% less stamina | Stamina / defence | Early-mid | Uses P14 |
| 34 | Trekking poles | No slow-down in mud or sand (wading stays the wading outfit's job) | Terrain | Mid | Needs terrain slow-down |
| | **Combat and protection** | | | | |
| 35 | Whetstone (pocket) | Blades (sword, axe) do 10% more damage | Damage | Early | |
| 36 | Rosin bag (pine rosin) | Swings 8% faster | Attack speed | Mid | |
| 37 | Aramid arm guards | Every bite and sting does 1 less damage (minimum 1) | Defence | Mid | |
| 38 | Puncture-proof gaiters | Centipede and spider bites do 40% less damage | Species defence | Mid | Millipede Forest, Spider Vale |
| 39 | Safety goggles | Ant acid sprays can't blind or burn you | Resistance | Early-mid | Ant Tunnels; check against the spray salve potion |
| 40 | Venom extractor pump | Venom and poison wear off 40% faster | Resistance | Mid | Check against the antivenom potion |
| 41 | Citronella wristband | Mosquitoes and midges ignore you | Species protection | Mid | Sim; only if mosquitoes ship (swamp zone sheets) |
| 42 | UV torch (clip-on) | Scorpions glow and show through the dark within 10 squares | Vision (species) | Mid-late | Scorpion Rocks; real: scorpion shells fluoresce under UV |
| 43 | Night-vision goggles | See the surface at night about as well as at dusk (not the pitch-dark underground) | Vision | Late | Bought; the night-sight potion is the temporary version |
| | **Information, utility, money and co-op** | | | | |
| 44 | Barometer | Shows tomorrow's weather: rain or drought | Information | Early-mid | Bag |
| 45 | Two-way radio | Friends show on your map with their health | Information (co-op) | Early-mid | Bag; bought; needs the map |
| 46 | Litter picker (reacher-grabber) | Pick things up from 2 squares further away | Pickup range | Early | |
| 47 | Nail apron | Place blocks, floors and fence posts 30% faster | Build speed | Early-mid | |
| 48 | Pocket scale | Bugs and carcasses sell for 5% more | Sell price | Mid | |
| 49 | First-aid pouch | Bandages heal 25% more | Healing (co-op) | Early-mid | |
| 50 | Thermos flask | A meal's boost lasts 25% longer | Boost duration | Mid | |

Possible combinations (5.2 #6), as examples only: Garden gloves + Seed tin -> "Gardener's kit"; Tackle box +
Fingerless gloves + Bite alarm -> "Tackle bag"; Nail apron + Litter picker -> "Builder's belt"; Barometer + Angler's
almanac + Field guide -> a single "field computer" (bag).

### 5.6 Gaps and unverified points
- Core Keeper, Fae Farm, Coral Island and Valheim could not be read (section 1); their accessory systems are not
  covered. Core Keeper in particular is known for many gathering accessories (unverified - not read).
- Necesse's and Sun Haven's rules on wearing duplicates were not on the pages read (unverified).
- Stardew's trinket slot count and hat effects were not on the pages read (unverified).
- No game read gives an accessory that raises the chance of CATCHING a creature; whether one exists elsewhere is
  unverified.
- Every number in 5.5 is illustrative and untested.
