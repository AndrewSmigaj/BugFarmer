# §11 · Food, cooking & potions
<!-- gdd: id=11 status=review updated=2026-10-02 -->

## The experience
There's no hunger: you eat to be ready for the trip ahead. Food is what your farm, your nets and your rod bring home —
a fly roasted whole on the spit, a beetle's chest seared as a steak, a crayfish boil, sourdough from your own wheat.
Better food raises your Health and Stamina more while it lasts, and most dishes add one boost: a better haul at the
lake, more from a harvest, one pickaxe hit fewer. One meal works at a time, and a new one replaces it. Potions are
short and strong, for the moment you need them — a healing draught in a fight, antivenom after a scorpion, night
vision for the dark — and one timed potion works at a time. You cook from recipes, single ones and whole recipe books
found in the world or bought, each at the station it names, from the spit to the cooking range.

## Decided
Each line is the owner's decision in my words, with its date.
- **No hunger** (2026-09-27, D50) — meals heal and give boosts; potions heal more strongly and do what food can't.
  Potions are ordinary items, not magic (2026-08-06). Venom and poison are real effects (2026-06-25, D16).
- **Meals and potions** (P16, accepted 2026-09-27; D54) — a meal heals over a while; one meal works at a time, and a
  new one replaces the last; a healing potion heals at once, then the person healed waits a short while before another
  works on them; other potions have no wait; stronger bugs make stronger potions; the cauldron is the potion station,
  where the basic recipes are known and stronger ones are found, bought or earned in quests; food doesn't spoil in
  bags or chests. Night vision stays in the starting set (D54). An alchemist's robe comes with the potion station
  (D47).
- **Some meals help stamina** (P14, accepted 2026-09-28) — a bigger pool or a faster refill, eaten to get ready for a
  hard zone.
- **Healing and giving** (2026-09-27, D50, P17) — hold a bandage or a potion and use it on someone to heal them;
  items, bugs and coins can be given to other players.
- **Cooking is its own system** (2026-06-25, D19) — it gets its own recipes and rules.
- **One simple step per station** (2026-09-27, D42; the overview's P11, accepted 2026-09-28, D63) — put something in,
  take something out, with no realistic sub-steps such as soaking or threshing: a game, not a simulation of real
  processing.
- **Real food** (2026-10-01, D74) — every dish is a real one cooked from what you grow, fish and farm, with nothing
  silly; everything in the world needs a use, or whether it belongs is questioned; several things can give the same
  boost.
- **Bugs are livestock in the kitchen** (2026-10-01, D75; 2026-10-02, D76) — a fly roasts whole like a small bird, a
  big beetle gives a steak, giant ant eggs are the eggs; the stove takes the bugs themselves, and the bug extractor
  only makes materials. Some bugs aren't food, for their real reasons: fireflies, millipedes, milkweed caterpillars,
  carrion beetles and ladybirds.
- **Drinks** (2026-10-01, D75) — the teas are cut; juice, cider and mead come in glass bottles, which are bought or
  made.
- **What a meal does** (2026-10-02, D76) — it raises your Health and Stamina while it lasts, better food more, and
  many dishes add one of the eight boosts, depending on the food. These are guidelines, not laws: coffee is made and
  sold with food but works like a potion.
- **Potions** (2026-10-01, D74, D75) — designed effect first, ingredient second; one timed potion at a time, potions
  you drink and balms alike, while cures and healing don't count against it; no weapon coatings, so venom comes only
  on weapons made from venomous parts; the Night Vision Potion (carrot and glowing mushroom) and the Venom Resistance
  Potion.
- **The Oven Mitts** (2026-10-01, D75) — an accessory: cooking a dish (not the staples that go into one) has a 30%
  chance of an extra portion.
- **Cooking from recipes** (2026-10-02, D77) — dishes are cooked from recipes you know, with no experimenting and no
  Palia-style chains of preparing steps (single steps at other stations, such as milling flour, stay); recipes come
  singly and in recipe books, found in the world and bought. The list needs rare dishes as well as everyday ones. Each
  recipe names its station: some need the range, others only the spit, whose own recipe takes a campfire (your
  leaning).

## Current design
- **The food list** (proposed 2026-10-01/02, waiting for your marks): 51 rows in the item table — two rules rows (the
  meals, and recipes and recipe books), 8 staples, 38 dishes and 3 drinks — each a real dish or marked as adapted from
  one, apart from the scorpion tail, marked as game logic (`research-2026-10-01/foods-real-dishes.md`). Every dish
  carries one of the eight boosts: Stamina, Sturdy, Harvest, Forage, Fishing, Catch (your net reaches further), Mining
  and Swift. The proposed length follows effort: about 5 minutes for a dish from the spit, about 10 for a stove dish
  or something from the keg, and about 20 for a big stove dish (three or more main foods, or a dough, pastry or bread)
  or food dried or smoked for the trail.
- **The stations** (the same rules row): the spit, a campfire with a spit over it, cooks one dish at a time; it is
  made at the workbench from the start, with a campfire as one of its parts (D77, your leaning). The wood stove cooks
  two and bakes; the range, the big powered stove, cooks several (Modern Wares sells it; until you have power of your
  own, a windmill after reaching the Locust Farmland, it runs on the Mayor's, set up just outside the Mayor's house,
  D56); the keg makes drinks and ferments, the fruit press juice and oil, the mill flour and cornmeal. The plain
  campfire stays the camp light (P10), and the separate cooking pot is proposed cut. (The January 2026 design had the
  starter wood stove cooking one dish, and stoves growing from hand-fed fuel to powered, `game_design.md` §11.6–11.7.)
- **A new player's first food**: five dishes are known from the start, cooked on the spit — the roast fly (the fly
  farm's first dinner), corn on the cob, roasted seeds, salt-grilled fish and damper — and four come with the wood
  stove (fly soup, polenta, pumpkin soup, mushroom soup); the General Store sells flour, cornmeal and salt. Who shows
  a new player how to cook could be one of the townspeople's lessons (§20).
- **The potion list**: settled — the potion rules, the calm spray, bandages, the healing potion, the antivenom, the
  burn salve, strong coffee, the bug bomb, the Night Vision Potion and the Venom Resistance Potion; waiting for your
  marks — the stamina tonic, the cricket protein drink, the pollen tonic, the mint and sting balms, the cover scent
  and the lavender incense.
- **The old brainstorm** (`cooking_food.md`) imagined a roasting spit, a soup pot, ovens and a grand feast platter as
  the showpiece dish.

## As built
- The cooking stations exist as objects with no recipes: the campfire, the old two-plate stove, the cooking pot, the
  cauldron and the keg (found 2026-07-03, D30). Eating does nothing yet, health comes back only by slow regeneration,
  nothing can give a timed effect, and venom on the player isn't built. The spit exists too, made at the workbench
  from wood and an iron bar, and like the campfire it has no recipes. The wood stove and the range exist as objects
  with no cooking panel at all.
- The stations run on the crafting engine: a recipe names its station, its exact inputs, one output and a time; a
  station can cook a set number of recipes at once, each with a queue of batches that runs while you do other things;
  finished things wait in the station's tray until collected (`nakama/modules/world/craft_stations.go`;
  `docs/product/architecture/architecture_crafting.md`). Ingredients come only from your bag. Each player has their
  own list of known recipes, and a recipe can be locked until learned (`recipeKnown`).
- **A gap found today:** a station's tray belongs to no one, so anyone at a shared station can collect what someone
  else made (`craftCollectOne`); and two players queuing the same recipe share one queue, their batches merging. It
  affects every shared station, not only cooking, and is now in the backlog.
- **Recipes are already sold.** A townsperson can sell single recipes and recipe books, and buying one teaches it at
  once; a book teaches a whole set (`shopBuyRecipe`, `shopBuyBook`, `nakama/modules/world/handlers_shop.go`). The
  carpenter, the weaver and the stonemason sell books today. A recipe can be set to be found rather than bought, but
  nothing in the game yet lets a player find one.

## How it will work
- A meal raises the most Health and Stamina you can have while it lasts and heals you over a while (D54, D76); the
  meal and the potion are named entries on the character sheet (§08): the strength they add, their boost and their
  time. A dish's box states exactly what it gives. A meal's effect ends when you faint, as a potion's does (§08 P4).
- Batches run on the stations' existing queue; taking ingredients from nearby chests and the sound when a batch is
  done are new.
- New recipe data: ingredient groups (any fish, any fruit, any fat, any edible bug). Which recipes each player knows
  is already kept, and shops already sell recipes and books (As built); recipes found in the world, read where they
  lie, are new (P9).
- Cooking never touches the shared bug simulation, except that a dish dropped on the ground feeds bugs like any food
  (P17).

## Proposals
### P1. Better food is a ladder you can see
What you cook sets a meal's strength: a dish from the spit a little, a stove dish more, a big dish or a bake from the
stove or the range more again, a feast most; a rare dish (P11) is one step above the everyday dish it's most like,
never above a feast. If ranching later adds prime (well-raised) bugs, a prime fly lifts its dish one step too. The
dish's box says exactly what it gives — the strength, the boost and the minutes — with no luck and no hidden numbers.
How many dots each step adds is set with the sheet's numbers (§08). Your normal Health and Stamina are enough for
ordinary play: a meal is a bonus you choose, never hunger in disguise (D50). Food from the spit keeps a lasting job:
it's the cheapest to make, and its dried and smoked food lasts as long as the biggest dishes. How much a meal heals,
and how that fits with the raise, is set with the numbers.

**Lenses:** Readability — in Zelda the best dishes come down to luck, and a Palia player complained that its quality
stars aren't explained; a ladder in plain steps avoids both. Balance — it sits on top of the length rule proposed in
the food rows (more effort, a longer meal), which is still waiting for your marks; Valheim shows the danger of food
becoming a chore when an unfed player is too weak, which the rule that a meal is a bonus you choose prevents. **Cost
and risk:** small; numbers to tune.

### P2. Cooking from the book, in batches
Every recipe you know can be queued in batches on a station and collected later: ingredients come from your bag and
nearby chests you may open, the station sounds when it's done, and some dishes make several portions. A meal every 5
to 20 minutes then costs a few clicks, not a chore. This is how all cooking works (D77).

**Lenses:** Readability — Disney Dreamlight Valley's ingredient autofill; Stardew Valley's kitchen reads from the
fridge as well as the bag. Fit — the stations' queue already runs batches; the nearby chests and the done-sound are
new. **Cost and risk:** small.

### P3. Your cooking stays yours at a shared station
At the village's shared stations, each player's batches and finished dishes belong to them until they collect them or
give them away. This mends the gap found today in every shared station — the blacksmith's furnace as much as the
village's wood stove. How many things a shared station can cook at once for several players is §10's to settle.

**Lenses:** What can go wrong — without it, one player can take another's cooking or bars; the village's stations are
shared by your decision (D55), so this has to hold before people play together. **Cost and risk:** a change to every
shared station's tray; things left uncollected need a rule (§10).

### P4. Feasts, cooked together
A few big dishes are feasts: three or four finished dishes, cooked at more than one station — say a roast fly from the
spit, bread and pumpkin soup from the wood stove, and juice from the press — laid on a table as one platter with a
fixed number of servings. Each serving counts as that player's one meal and lasts longer than any single dish (say 30
minutes). Friends cook the parts at the same time, a newcomer can take the simplest part, or one player can make them
over a day, since food doesn't spoil. Nobody gets a copy: Palia gives every helper a full dish, its group cooking
out-earned everything else, and its developers cut every dish's price by a quarter (patch 0.169). A feast is as good
as its parts, never dragged down by its worst one.

**Lenses:** Picture the moment — a table on your plot, the platter emptying as your friends eat before a trip to the
fire-ant domain. Multiplayer — Valheim's feast feeds a group from one tray of ten servings; Overcooked shows that
sharing work is fun when there is waiting to share. **Cost and risk:** a table and a platter that empties in a few
stages; who may eat at a village table needs a rule.

### P5. Nothing hidden
Each dish's box says exactly what it gives and what it needs, including any group it takes (any fish, any fruit, any
fat, any edible bug). The cookbook lists every recipe you know, with favourites and the station each one needs.
Townspeople teach and sell recipes when their ingredients are within reach.

**Lenses:** Readability — Core Keeper players ask to see what a food does before they cook it; one Stardew player
complained of recipes taught for crops out of season. **Cost and risk:** a cookbook screen.

### P6. Every dish is wanted by someone
Food matters beyond your own meters: some townspeople's requests ask for a dish, a dish makes a good gift, and dishes
sell. A dish nobody wants goes uncooked, as Stardew Valley's unused recipes show. How townspeople's requests and gifts
work is designed in §16.

**Lenses:** Fit — your rule that things need a use, applied to dishes. **Cost and risk:** none here; the work is
§16's.

### P7. Drinks, and kitchen drinks that act like potions
Juice, cider and mead are a small heal over a few seconds, one at a time, like a bandage, and take neither the meal's
spot nor the potion's. Coffee, and any later kitchen drink that works like a potion, takes the timed potion's spot on
the sheet (§08 P7) — the same rule as §08 P2, so one answer settles both — and follows the potion rules — so drinking
coffee replaces a running potion such as night vision, and the other way round.

**Lenses:** Fit — your exception for coffee (D76), given one clear place; Stardew Valley likewise keeps drinks in
their own slot beside food. **Cost and risk:** none.

### P8. Brewing stays simple
Potions are brewed from the book at the cauldron — basic recipes known there, stronger ones found, bought or earned —
with no hands-on action and no brewing chains, the same as cooking (D77).

**Lenses:** Fit — P16's own rule (no brewing chains), the potion rules row, and cooking's own rule (D77). **Cost and
risk:** none.

### P9. Recipes, single and in books
Cooking uses the recipe shops the game already has: townspeople sell single recipes and recipe books, and buying one
teaches it at once (the rows say who teaches each dish) — the Bug Dealer's five bug dishes as one book, or the
Fisherman's fish dishes. Found recipes are new. A found recipe is a book or a note left somewhere in a zone, and it's
read where it lies: everyone who reads it learns it, and it stays for the next player, so in a shared world nobody
takes it from the others. A message in a bottle can point to one, as its row already says, and a quest can teach one
as its reward. Everyday recipes are bought in the village; others are found, earned, or bought farther away, as the
western town's farm store already teaches its grilled locust legs — the same three ways as stronger potion recipes
(D54).

**Lenses:** Fit — your answer (D77), on the system the carpenter, the weaver and the stonemason already use for their
recipe books. Multiplayer — a recipe read where it lies can't be taken by the first player to arrive. Picture the
moment — a water-stained book of desert recipes, hidden in Scorpion Rocks. **Cost and risk:** small for bought
recipes, which exist, though the shop screen shows at most six recipes and three books today, so a cook's shop needs a
longer list; found ones need an object you read in place.

### P10. The spit, the first cooking station
The spit is a campfire with a wooden spit over it, made at the workbench from a campfire and wood (D77; the campfire
as a part is your leaning), so a new player can make it on the first day: today's recipe also takes an iron bar, 40
coins at the blacksmith (a lot on the first day) or smelted from iron ore that needs a better pickaxe. It cooks the
fire dishes: roasts, skewers, grilled fish, corn and damper in the coals beneath it, and food dried or smoked for the
trail. The plain campfire stays the camp light and cooks nothing, and its description says to add a spit to cook: two
stations doing the same job is why the spit was cut before. The wood stove cooks stews, soups, breads and pies; the
range, the powered stove, cooks the biggest dishes and many of the rare ones (which stations can cook which dishes is
Q2).

**Lenses:** Fit — your answer (D77); Valheim works the same way, its cooking station a spit set over a fire. Picture
the moment — the first evening on the fly farm, a fly turning on the spit. **Cost and risk:** a new recipe for the
spit; the spit needs the campfire's light, which it lacks today, and its picture roasts what looks like a ham, which
this world doesn't have (D32), so it's redrawn with a fly when the art is made.

### P11. Everyday and rare dishes
Beside the everyday dishes sits a set of rare ones: about a dozen to start, spread over the zones beyond the village,
with more of them in the harder ones. A rare dish takes a rare ingredient — royal jelly, the blind cave fish of the
Underground River, and the fruit and other finds of zones still to be designed (D72) — and its recipe is found,
earned, or bought far from the village (P9). Each is one step above the everyday dish it's most like, never above a
feast (P1), and sells for more than any everyday dish. The rare dishes are drafted next, as rows on the items page for
your marks.

**Lenses:** Fit — your ask for a good spread of everyday and rare dishes (D77). Curiosity — a rare recipe is a reason
to go farther out. **Cost and risk:** more dishes, each needing an icon.

## Questions
### Q1. What does a feast give?
If you keep feasts (P4):
- **A.** The strongest meal in the game and one boost from its parts, chosen by whoever lays the table.
- **B.** The strongest meal, and no boost.
- **C.** The strongest meal, and each person who eats picks one boost from the feast's parts.

**Recommendation: C.** A mixed group heading out together — miners and anglers — can each take what they need, and it
still keeps one boost per meal.

### Q2. Can a bigger station cook a smaller one's dishes?
Your answer names a station for each recipe (D77); this settles what that means, before each dish gets its station.
- **A.** Only its own station: a range can't cook a wood-stove soup.
- **B.** Any bigger station too: the wood stove and the range can cook the spit's dishes as well, so once you have a
  stove the spit is only a cheap fire for the road, a light and one more place to cook.
- **C.** The range cooks everything the wood stove does, since it's the bigger stove, but only the spit cooks the fire
  dishes (roasts, skewers, smoking), so the spit keeps its job all game.

**Recommendation: C.** The range is a bigger stove, so it should make a stove's soup, but no stove can turn a spit or
smoke fish over an open fire, so the fire dishes stay the spit's and it keeps a real job all game. The wood stove
stays the stove for anyone without power, and a second place to cook beside a range.

## To settle later (not in this review)
- **Eating raw food for a small heal** — a carrot or an apple straight from the bag (the old catalogue's idea).
- **The early heal** — answered by the cloth bandage (D74).
- **Numbers** — how many dots each step of food adds, how much a meal heals, each dish's portions, and a feast's
  servings and length, once the sheet's numbers are set (§08).
- **Feasts** — who may eat at a table in the village, and whether a feast left out on a table draws flies, like food
  on the ground (P17).
- **The rare dishes and each dish's station** — drafted next as rows on the items page (P10, P11, Q2), including which
  drafted dishes count as rare, such as the ones whose recipes are found in a zone.

## Sources
- Your answers, 2026-06-25 to 2026-10-02 — restated above; `docs/product/economy/DECISIONS.md` D16, D19, D30, D32,
  D42, D47, D50, D54, D55, D56, D59, D63, D72, D74, D75, D76, D77; `docs/gdd/overview.md` part 11, P11, P14, P16, P17.
- `docs/product/design/game_design.md` §11.6–11.7 (January 2026); `docs/brainstorms/objects/cooking_food.md`,
  `docs/brainstorms/objects/alchemy_potions.md`, `docs/product/economy/catalogs/consumables.md` (the old lists,
  replaced in the item pass).
- The item table, `docs/gdd/item_table.jsonl` (the meal, potion and station rows).
- Research: `docs/product/investigations/research-2026-10-02/cooking-systems.md` (Palia, Stardew Valley, Valheim,
  Zelda, Disney Dreamlight Valley, Don't Starve, Coral Island, Sun Haven, Fae Farm, Rune Factory, Story of Seasons,
  Spiritfarer, Graveyard Keeper, Overcooked, Cooking Mama, Genshin Impact, Monster Hunter and others);
  `docs/product/investigations/research-2026-10-01/foods-real-dishes.md`. Palia's patch notes for build 0.169, checked
  2026-10-02 (the price cut); a cold review of this section (2026-10-02).
- Code: `nakama/modules/world/craft_stations.go`; `docs/product/architecture/architecture_crafting.md`.
