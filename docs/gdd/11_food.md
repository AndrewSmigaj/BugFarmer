# §11 · Food, cooking & potions
<!-- gdd: id=11 status=review updated=2026-10-02 -->

## The experience
There's no hunger: you eat to be ready for the trip ahead. Food is what your farm, your nets and your rod bring home —
a fly roasted whole on the campfire's spit, a beetle's chest seared as a steak, a crayfish boil, sourdough from your
own wheat. Better food raises your Health and Stamina more while it lasts, and most dishes add one boost: a better
haul at the lake, more from a harvest, one pickaxe hit fewer. One meal works at a time, and a new one replaces it.
Potions are short and strong, for the moment you need them — a healing draught in a fight, antivenom after a scorpion,
night vision for the dark — and one timed potion works at a time. How cooking itself plays in your hands is the big
question of this section.

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
- **One simple step per station** (2026-09-27, D42; P11, accepted 2026-09-28, D63) — put something in, take something
  out, with no realistic sub-steps such as soaking or threshing: a game, not a simulation of real processing.
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
- **How cooking plays is to be designed**, with options (2026-10-02, D76) — this section's main question.

## Current design
- **The food list** (proposed 2026-10-01/02, waiting for your marks): 50 rows in the item table — a rules row, 8
  staples, 38 dishes and 3 drinks — each a real dish or marked as adapted from one, apart from the scorpion tail,
  marked as game logic (`research-2026-10-01/foods-real-dishes.md`). Every dish carries one of the eight boosts:
  Stamina, Sturdy, Harvest, Forage, Fishing, Catch (your net reaches further), Mining and Swift. The proposed length
  follows effort: about 5 minutes for a campfire dish, about 10 for a stove dish or something from the keg, and about
  20 for a big stove dish (three or more main foods, or a dough, pastry or bread) or food dried or smoked for the
  trail.
- **The stations** (the same rules row): the campfire, with its spit and coals, cooks one dish at a time and is made
  at the workbench from the start; the wood stove cooks two and bakes; the range, the big powered stove, cooks several
  (in the village only in the Mayor's house, D56); the keg makes drinks and ferments, the fruit press juice and oil,
  the mill flour and cornmeal. The separate cooking pot and spit objects are proposed cut. (The January 2026 design
  had the starter wood stove cooking one dish, and stoves growing from hand-fed fuel to powered, `game_design.md`
  §11.6–11.7.)
- **A new player's first food**: five dishes are known from the start — the roast fly (the fly farm's first dinner),
  corn on the cob, roasted seeds, salt-grilled fish and damper — and four come with the wood stove (fly soup, polenta,
  pumpkin soup, mushroom soup); the General Store sells flour, cornmeal and salt. Who shows a new player how to cook
  could be one of the townspeople's lessons (§20).
- **The potion list**: settled — the potion rules, the calm spray, bandages, the healing potion, the antivenom, the
  burn salve, strong coffee, the bug bomb, the Night Vision Potion and the Venom Resistance Potion; waiting for your
  marks — the stamina tonic, the cricket protein drink, the pollen tonic, the mint and sting balms, the cover scent
  and the lavender incense.
- **The old brainstorm** (`cooking_food.md`) imagined a roasting spit, a soup pot, ovens and a grand feast platter as
  the showpiece dish.

## As built
- The cooking stations exist as objects with no recipes: the campfire, the stove, the cooking pot, the cauldron and
  the keg (found 2026-07-03, D30). Eating does nothing yet, health comes back only by slow regeneration, nothing can
  give a timed effect, and venom on the player isn't built.
- The stations run on the crafting engine: a recipe names its station, its exact inputs, one output and a time; a
  station can cook a set number of recipes at once, each with a queue of batches that runs while you do other things;
  finished things wait in the station's tray until collected (`nakama/modules/world/craft_stations.go`;
  `docs/product/architecture/architecture_crafting.md`). Ingredients come only from your bag. Each player has their
  own list of known recipes, and a recipe can be locked until learned (`recipeKnown`).
- **A gap found today:** a station's tray belongs to no one, so anyone at a shared station can collect what someone
  else made (`craftCollectOne`); and two players queuing the same recipe share one queue, their batches merging. It
  affects every shared station, not only cooking, and is now in the backlog.

## How it will work
- A meal raises the most Health and Stamina you can have while it lasts and heals you over a while (D54, D76); the
  meal and the potion are named entries on the character sheet (§08): the strength they add, their boost and their
  time. A dish's box states exactly what it gives. A meal's effect ends when you faint, as a potion's does (§08
  P4).
- Batches run on the stations' existing queue; taking ingredients from nearby chests and the sound when a batch is
  done are new. If dishes are cooked by hand (Q1), your game records when you pressed, counted from the cook's start,
  and the server checks the time is possible: the result can't be faked, and a slow connection doesn't make you late.
- New recipe data: ingredient groups (any fish, any fruit, any fat, any edible bug) and, per player, which dishes they
  know and how well they've cooked them.
- Cooking never touches the shared bug simulation, except that a dish dropped on the ground feeds bugs like any food
  (P17).

## Proposals
### P1. Better food is a ladder you can see
What you cook sets a meal's strength: a campfire dish a little, a stove dish more, a big stove dish or a bake more
again, a feast most. Depending on Q2, how well you cook may add a step; and if ranching later adds prime (well-raised)
bugs, a prime fly lifts its dish one step too. The dish's box says exactly what it gives — the strength, the boost and
the minutes — with no luck and no hidden numbers. How many dots each step adds is set with the sheet's numbers (§08).
Your normal Health and Stamina are enough for ordinary play: a meal is a bonus you choose, never hunger in disguise
(D50). Campfire food keeps a lasting job: it's the cheapest to make, and the campfire's dried and smoked food lasts
longest of all. How much a meal heals, and how that fits with the raise, is set with the numbers.

**Lenses:** Readability — in Zelda the best dishes come down to luck, and a Palia player complained that its quality
stars aren't explained; a ladder in plain steps avoids both. Balance — it sits on top of the length rule proposed in
the food rows (more effort, a longer meal), which is still waiting for your marks; Valheim shows the danger of food
becoming a chore when an unfed player is too weak, which the rule that a meal is a bonus you choose prevents. **Cost
and risk:** small; numbers to tune.

### P2. Cook from the book
Every dish you know can be queued in batches on a station and collected later: ingredients come from your bag and
nearby chests you may open, the station sounds when it's done, and some dishes make several portions. A meal every 5
to 20 minutes then costs a few clicks, not a chore. Every route in Q1 includes this as its everyday way to cook.

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
as its parts, never dragged down by its worst one. Feasts work with any route in Q1.

**Lenses:** Picture the moment — a table on your plot, the platter emptying as your friends eat before a trip to the
fire-ant domain. Multiplayer — Valheim's feast feeds a group from one tray of ten servings; Overcooked shows that
sharing work is fun when there is waiting to share. **Cost and risk:** a table and a platter that empties in a few
stages; who may eat at a village table needs a rule.

### P5. Nothing hidden
Each ingredient's box shows its group (bug, fish, fruit, vegetable, grain, fat, egg, seasoning) and the boost it leans
towards. The cookbook records every dish you know, with favourites; if you can experiment (Q1), it also records every
attempt. Townspeople teach dishes when their ingredients are within reach.

**Lenses:** Readability — some Don't Starve players use a mod to predict their dishes, and Core Keeper players ask to
see food effects, because the rules are hidden; one Stardew player complained of recipes taught for crops out of
season. **Cost and risk:** a cookbook screen.

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
with no hands-on action and no brewing chains, whatever Q1 decides for cooking.

**Lenses:** Fit — P16's own rule (no brewing chains) and the potion rules row; cooking carries the hands-on moment, if
any. **Cost and risk:** none.

## Questions
### Q1. How should cooking play in your hands?
The research behind these is in `docs/product/investigations/research-2026-10-02/cooking-systems.md` (89 sources,
about 28 games). Every option keeps one meal at a time, better food making a stronger meal, and bugs cooked as they
are; every option also gets cooking from the book for everyday meals (P2) and can have feasts (P4). The options differ
in how you first make a dish and whether your hands change it.
- **A.** **From the book, as in Stardew Valley.** Pick a dish you know and cook it — in Stardew it's instant; here it
  runs on the station while you do other things. Better food means choosing a better dish. It's the clearest and the
  least work to build, but nothing you do changes a dish. With feasts (P4), friends still cook together.
- **B.** **Prepared ingredients, as in Palia.** A dish is made from ingredients you prepare first, each in one step at
  its own station: chop the vegetables at a prep counter, knead the dough, then cook at the stove, each step a short
  skill moment. Once you know a dish, the book cooks it and prepares its ingredients for you; doing the steps by hand
  is how you learn a dish and, depending on Q2, make it better. It's the best for cooking together — friends take
  different steps at once, and a newcomer can take a step that needs no ingredients — and gives the strongest feeling
  of having cooked. But it needs a prep counter, many half-made ingredients (each with its own art and data) and
  several skill moments, and a dish's first cooks take a minute or more. Preparing steps like chopping are the kind of
  sub-step your one-step rule (D42) left out of processing, so whether cooking is the exception is your call; bugs
  would still go to the stove whole (D76). The light form — staples made in one step at their own station (tortillas,
  sourdough starter, fish sauce, seed oil, flour) — is already in the food list.
- **C.** **The open pot, as in Disney Dreamlight Valley, Zelda and Don't Starve.** Put ingredients in and see what you
  make; a match writes the dish in your cookbook, and from then on you can cook it from the book. Better food comes
  from what you put in: more and better main ingredients make a stronger dish. Discovery is the fun, but your skill at
  cooking never changes a dish, and hidden rules send players to wikis unless every ingredient shows its group (P5).
- **D.** **Learn it, then master it by hand, as in Coral Island, with Genshin Impact's mastery.** You can try
  ingredients at a station, as in C, and a match is a new dish in your book (Q3). A dish you've learned — taught,
  bought, found or discovered — can be cooked from the book straight away, as a *fair* dish. Cooking it by hand is one
  short action that suits the station: watch the fly turn on the spit and lift it when its skin turns golden and the
  sizzle changes, take the pot off at a simmer, take the bread out of the oven in time (Q5). It comes out *well done*,
  or fair if you're early or late; nothing is ever ruined, and stopping gives the ingredients back. The keg, the press
  and the mill take time only. After a few well-done cooks by hand (say three), you've mastered the dish, and its
  batches come out well done too (Q6). But it's the most work after B — a hands-on moment for three kinds of cooking,
  a grade and a mastery count for every player and dish, matching for the open pot, a cookbook — two grades of the
  same dish sit in separate stacks in your bag, and like C, the open pot needs every ingredient's group shown (P5). An
  option for anyone who wants it widens the timing window, so everyone can reach well done and nobody gets it for
  free.

**Recommendation: D.** Like every option, it keeps Stardew Valley's book for every day and can put Palia's
cooking-together into feasts; what D adds is that your effort changes the dish, but only while you master it, never as
a tax on every meal (with Q2 A and Q6 A). A is the sensible fallback if a hands-on moment isn't wanted: with feasts it
still gives the group moment. Also considered, for later: a base dish plus a seasoning that picks the boost, as in
Don't Starve Together and Grounded.

### Q2. If dishes are cooked by hand (B or D), does cooking well make a dish stronger?
- **A.** Yes: a well-done dish is one step stronger than a fair one.
- **B.** Only longer: well done lasts longer, with the same strength.
- **C.** No: cooking by hand only teaches or masters the dish (then D's grades and mastery go).

**Recommendation: A.** Effort you can see on the sheet is what makes the hands-on moment worth doing. In a Coral
Island thread one player called its cooking action pointless, while another wished it set the dish's quality.

### Q3. If you can experiment (C or D), how many dishes can you find that way?
About 29 dishes are taught by townspeople, sold or found today; about 19 of them are simple (one or two main foods,
no dough, pastry or bread),
and about 8 of those are made only from what the village grows and catches.
- **A.** Any dish; townspeople and found notes become shortcuts and hints.
- **B.** The simple ones (about 19); big dishes must be taught, bought or found.
- **C.** Only the simple village ones (about 8); everything else is taught, bought or found.

**Recommendation: B.** Small experiments stay satisfying, the big dishes keep the townspeople and the zones worth
seeking out, and nobody needs a wiki to find a four-ingredient stew.

### Q4. What does a feast give?
- **A.** The strongest meal in the game and one boost from its parts, chosen by whoever lays the table.
- **B.** The strongest meal, and no boost.
- **C.** The strongest meal, and each person who eats picks one boost from the feast's parts.

**Recommendation: C.** A mixed group heading out together — miners and anglers — can each take what they need, and
it still keeps one boost per meal.

### Q5. If dishes are cooked by hand (D), how does the spit work?
- **A.** You stay and lift the fly at the right moment.
- **B.** You can walk away and come back within a window.
- **C.** Both: lift it at the moment if you stay, or leave it and come back in time.

**Recommendation: C.** Players who enjoy the moment get it, and a busy farmer is never pinned to the fire.

### Q6. Once a dish is mastered (D), do its batches come out well done?
- **A.** Yes: the hands-on step is a one-off for each dish.
- **B.** No: the best food is always cooked by hand.

**Recommendation: A.** It keeps the hands-on moment a pleasure rather than a chore on every meal; B suits players who
love cooking but taxes everyone else.

### Q7. If you can experiment (C or D), what happens when a mix matches no dish?
- **A.** You get a plain dish named by how it was cooked — a simple stew, a campfire roast — weak but never wasted.
- **B.** Nothing is cooked: the ingredients come back, and the cookbook notes the try.

**Recommendation: B.** The list stays real dishes only, with nothing silly (D74), and nothing is wasted; the cookbook
keeps the try so a player never repeats it by mistake.

## To settle later (not in this review)
- **Eating raw food for a small heal** — a carrot or an apple straight from the bag (the old catalogue's idea).
- **The early heal** — answered by the cloth bandage (D74).
- **Numbers** — how many dots each step of food adds, how much a meal heals, each dish's portions, and a feast's
  servings and length, once the sheet's numbers are set (§08).
- **Feasts** — who may eat at a table in the village, whether a newcomer can cook a part they haven't learned, and
  whether a feast left out on a table draws flies, like food on the ground (P17).

## Sources
- Your answers, 2026-06-25 to 2026-10-02 — restated above; `docs/product/economy/DECISIONS.md` D16, D19, D30, D42,
  D47, D50, D54, D55, D56, D59, D63, D74, D75, D76; `docs/gdd/overview.md` part 11, P11, P14, P16, P17.
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
