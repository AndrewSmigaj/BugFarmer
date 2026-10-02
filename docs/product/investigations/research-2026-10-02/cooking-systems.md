# How cooking plays in other games, and routes for Bug Farmer

Research for Bug Farmer (2026-10-02). The game's food list exists (real dishes from what players grow, fish and farm,
plus the bugs themselves), but how cooking *plays* does not: today it is "recipe in, dish out". This page studies how
other games make cooking into play, then sets out routes Bug Farmer could take, scored, with a recommendation.

Research only: nothing here is decided. The routes are a menu for the game's designer.

Status: COMPLETE (2026-10-02).

> **Read with GDD §11 (2026-10-02).** `docs/gdd/11_food.md` Q1 restates these routes with corrections from two cold
> reviews: every route gets cooking from the book; route B prepares ingredients one step at each station, and whether
> preparing steps are allowed is the owner's call, not a breach of P11; meal lengths by effort are a proposal awaiting
> his marks, not a decision.

## Summary

- **Pick: Route D, "learn it by hand, cook it from the book, feast together."** You cook a new dish by hand at its
  station with one short action (lift the roasting fly off the spit when it turns golden; take the pot off at a
  simmer; take the bread out of the oven in time), which teaches the dish and grades it *well done* or *fair*. Known
  dishes then cook in batches on the station while you do other things, and after a few well-done cooks the batches
  come out well done too. Feasts, made from three or four dishes cooked at different stations, are set out on a table
  with a fixed number of servings for everyone: cooking together without copying food.
- **The other routes, in one line each:**
  - **A, straight recipes (Stardew-like):** cheapest and clearest, but nothing the player does changes the dish;
    keep it as the fast path inside D.
  - **B, prepared ingredients at stations (Palia-like):** the best cooking-together, but minutes of steps per meal,
    against the accepted one-step-per-station rule; keep only its shared steps, for feasts.
  - **C, free-form combining with discovery (Dreamlight / Zelda / Don't Starve-like):** the richest discovery, but
    quality is only about ingredients and hidden rules send players to wikis; keep its open pot and
    cookbook inside D.
  - **E, base dish plus a seasoning that picks the boost (Don't Starve Together-like):** few recipes cover every boost,
    but dishes lose their identity; a possible late addition.
- **How better food works in D:** a visible ladder of three steps: *what* you cook (campfire < stove < big dish <
  feast), *how well* (well done or fair), and later *what goes in* (prime bugs, if ranching adds them). No luck, no
  hidden numbers.
- **How many steps before tedium:** none for a routine meal; one 5 to 10 second action while learning a dish; at
  most two stations for a big dish; a feast takes 5 to 10 minutes with friends.
- **Two things in the game's own code to settle before cooking ships, whatever the route:** at a shared station,
  finished food belongs to no one (anyone at the station can collect it), and a one-lane campfire can run only one
  player's job at a time.
- Six taste questions for the designer are at the end of Part 4.

## What Bug Farmer's cooking has to fit (restated from the design records)

- No hunger. One meal works at a time; a new meal replaces the last (D50, D54, 2026-09-27). A meal raises Health and
  Stamina while it lasts, better food raising them more, and many dishes also add one boost from eight families
  (stamina, toughness, harvest, foraging, fishing, net reach, mining, walking speed). Health and Stamina are two of six
  meters on a new character sheet, shown as dots, and the one meal is the item that raises them (D76, 2026-10-02).
  Food doesn't spoil (D54). Coffee is sold with food but works like a potion (D76).
- How long a meal lasts already follows the effort that went into it: about 5 minutes for a campfire dish, about 10
  for a stove dish or something fermented, about 20 for a big stove dish, a bread or pastry, or food dried or smoked
  for the trail (the meal-set rules row in `docs/gdd/item_table.jsonl`, 2026-10-01).
- Stations: a campfire (one dish at a time), a wood stove (two at once, and it bakes), a range (several); a keg for
  drinks and ferments, a fruit press, a mill (the meal-set row). Basic stations stand in the village and belong to the
  townspeople; players use them but can't take them (D55). Processing elsewhere in the game is deliberately one
  simple step per station, "put something in, take something out", with no realistic sub-steps such as soaking or
  threshing (proposal P11, accepted 2026-09-28; D42).
- Recipes: a few dishes are known from the start, the plainest stove dishes come with the stove, and the rest are
  taught or sold by townspeople or found in the zones (the meal-set row).
- **Bugs go straight to the stove** (D75, 2026-10-01, revised by D76, 2026-10-02): dishes take the bugs themselves. A
  fly (about the size of a cat) roasts whole like a small bird, a big beetle cooks as a steak, and giant ant eggs are
  the eggs. Players don't prepare cuts: the separate cuts and "bug meat" planned on 2026-10-01 are gone, and the bug
  extractor makes materials only. (The meal-set row in the item table predates this and still lists the cuts.)
- **Quality today:** the design has no quality grades for crops, fish or bugs; fertiliser raises yield, not quality
  (D42). A quality mark for well-raised bugs ("prime" materials) is left open, to return with the ranching design (D76).
- A recipe can take "any fish", "any fruit", "any fat" (ingredient groups; the meal-set row).
- The Oven Mitts accessory gives a 30% chance of an extra portion when cooking a dish (item table, 2026-10-01).
- Multiplayer: a shared world that runs the same for every player; nothing goes faster for one player than another
  (D58). Items can be given to other players (D50). Some dishes make several portions to share (the meal-set row).
- As built: cooking stations exist as objects but have no recipes yet (D30). The crafting engine they would use is
  "recipe in, dish out": a recipe names its station, inputs, output and a single processing time; a station has one or
  more *lanes* (parallel jobs); inputs leave your bag when you queue, the job runs on the server while you do other
  things, and finished items wait in the station's output grid until collected
  (`docs/product/architecture/architecture_crafting.md`). Each player already has their own list of known recipes, and
  a recipe can be locked until learned (`recipeKnown` in `nakama/modules/world/craft_stations.go`).

## Method

One researcher, no helpers, writing each section to this file as it was finished. The web-search tool's budget for the
session was already used up, so pages were found another way: DuckDuckGo's plain-HTML search (until it started refusing
requests), each wiki's own search, Steam's discussion search and Game Developer's site search. Every cited page was
fetched with a script and read as plain text, not through a summarising tool. Reddit could not be reached from this
machine, so player opinion comes from Steam reviews (Steam's public review feed, pulled in its most-helpful order for
the last year and searched for cooking words), Steam discussion threads, forums, press articles and the wikis' own
notes. Game details come mostly from fan wikis, which can lag behind a game's latest version.

Four search angles were used, as asked:
1. **By technique**: ingredient preparation, free-form combining, quality stars, cooking minigames, shared feasts.
2. **By game**: each game's wiki and guides.
3. **By developer and design writeups**: developer blogs, patch notes, talks and interviews.
4. **By player complaint**: Steam reviews and discussions, press criticism.

Game terms are explained the first time they appear.

---

## Part 1. How cooking plays in other games

Each game below gets the same seven questions: how cooking works step by step; how recipes are learned; what decides
a dish's quality or strength; preparation steps and minigames (a *minigame* is a short skill test inside the game,
such as pressing a button in time); how it works with other players; what players praise and complain about; and how
long cooking takes. Source numbers (S1, S2 ...) point to the source list in Part 2.

### 1.1 Palia (2023, an online "cozy" life game for many players)

**How it works, step by step** (S1, S2, S3, S4):
1. You choose a recipe at the station where it starts (for example the mixing station for a poke bowl). A tick-box
   lets star-quality ingredients be used (S5).
2. A countdown starts above that station, and a small prompt appears above every other station the recipe needs,
   saying what has to be done there. The poke bowl's countdown is 3 minutes 40 seconds; a bean burger's 4 minutes 40;
   the celebration cake's 5 minutes (S3, S4).
3. You walk between the stations doing each step, and each step is a small minigame:
   - **prep station, chopping**: lines slide across a chopping board towards a target and you press in rhythm, with
     a sound cue; a miss restarts the minigame but keeps the chops already made;
   - **prep station, rolling**: a marker moves up and down and you press when it is inside a target;
   - **mixing station and stove, stirring**: hold the button until a meter fills;
   - **stove, flipping**: hold the button and release when a moving marker lines up with the target;
   - **oven, baking**: put prepared food in and take it out after a set time, before it burns (S2).
4. Each step makes an *intermediate ingredient* (a half-made ingredient such as chopped onion, fish fillet, cake
   batter, cake layer). The poke bowl needs six chopping steps and two mixing steps before the final stir that
   assembles it (S3).
5. If the countdown runs out first, you get Ruined Food and the ingredients are gone (S6).

The campfire is the exception: a campfire dish takes about 15 seconds, has no minigames and can't be ruined (S7).

**What the food does.** Palia has no damage or health. Food fills *Focus*, a meter that adds bonus experience to every
skill while it lasts; better dishes give much more (a poke bowl gives 525 Focus, or 787 at star quality) (S3, S8).

**Learning recipes.** Bought from the cooking guild's shop as your cooking level rises, found in the world, or given
by quests; the stations themselves are recipes from the same shop (S1).

**Quality.** Ingredients come in normal and *star* quality. The wiki says a dish cooked from star ingredients gives
more Focus and sells for more (S5). How the star is decided is not published: one Steam thread complains that star
ingredients and a faultless cook still gave a plain dish, while another player gets star dishes "9 times out of 10"
from plain ingredients and believes cooking level matters (S9). A search result from a Reddit thread (which could not
be opened) suggests minigame accuracy and the group's average skill also count; this could not be confirmed.

**Cooking with others.** Anyone who starts a recipe or completes at least one of its minigames receives the same
dish, at the same quality and quantity, as the cook; helpers only need to be on the host's plot (S1). Steps can be
done at the same time, so a group is faster. A helper brings only the ingredients for their own step, and can join in
on recipes they don't know (S1, S10). This grew into the famous *cake parties*: the celebration cake has 15 steps, a
host builds 15 stations, each guest takes one role (leaf-crusher, batter-maker, froster, oven-tender and so on) and
every participant gets 3 cakes per round, so a 50-round party gives each guest 150 cakes (S11). The oven role needs no
ingredients, and hosts give it to beginners (S12). The game rewards group cooking directly: a weekly challenge to cook
3 dishes with other players, and an achievement for cooking every recipe with a friend (S1).

**Praise.** The detail of the cooking: "an enjoyable minigame, unlike other cozy games I've played where it feels
like an insufferable chore" (S10, review 234418840). Cake parties as the one place the game feels like an online world:
chatting, meeting people, beginners included, a group photo at the end (S12).

**Complaints.**
- Solo cooking becomes repetitive, and players must eat a lot: "Cooking gets repetitive and boring, it is my least
  favorite skill" (S10, review 232404985).
- The countdown punishes lag and bugs: a glitch mid-cook ruins the dish and loses the ingredients (S10, reviews
  229739098, 236323148, 236495934).
- Unclear quality rules (S9).
- Big group recipes need careful menus: the cake-party guide tells guests to lock away ingredients they don't need,
  because the station menus jump about and it is easy to make the wrong thing (S11).
- Everyone getting a full copy multiplied the economy, and the developers said so. In patch 0.169 they explained that
  "with how cooking was designed ... the ceiling for profit, especially with other players, had the potential to be
  very high"; celebration cakes were "making more profit than with any other gold-generating activity, in any skill,
  by a large margin", and even after changing the cake, "co-op cooking was still generating value several levels
  higher than all other activities". They cut the cake's price by about 40% and every dish's by 25%, aware that this
  hurt "those who'd prefer to cook solo", with the stated goal of "Cooking Parties, not just Cake Parties" (S88). A
  dish's sell value, and so its Focus, comes from a formula on its ingredients' value (S88). Some parties also go
  silent, people acting "like a machine designed to bake cakes" (S12).
- Group cooking has technical costs the developers list in their patch notes: players stuck at stations while the
  countdown runs out; a minigame timer that froze for everyone when one player left it; frame-rate drops "when cooking
  in large groups" (S89). They added a "nearby" chat partly to help players coordinate cooking parties (S89).

**Time.** About 15 seconds at the campfire; a kitchen dish must be finished inside its 3 to 5 minute countdown (S3,
S4, S7).

**Lesson for Bug Farmer.** Steps at different stations, done together, make cooking a social activity that players
organise themselves around, and the step that needs no ingredients is a natural way in for a newcomer. But (a) every
helper receiving a full copy breaks a shared economy, as the developers themselves found (S88), (b) a countdown turns lag into lost ingredients, (c) a quality
rule players can't see makes their effort feel wasted (S9), and (d) the full chain is too long for one person doing a
routine meal.

### 1.2 Stardew Valley (2016, a farming game for one to eight players)

**How it works** (S13, S16): the first house upgrade adds a kitchen, a stove and a fridge. The stove opens a menu of
every recipe you know. Ingredients are taken from your bag and the fridge as if they were one, so you never carry
food to the stove. A known recipe whose ingredients you have lights up; missing ingredients show in red; unknown
recipes are dark shapes marked "???". One click makes the dish at once. From foraging level 3 a Cookout Kit (a small
campfire you build) lets you cook anywhere until the next morning.

**Learning recipes** (S13, S15, S21): a cooking show on the in-game TV teaches one recipe each Sunday for two in-game years,
with repeats on Wednesdays; villagers mail recipes as friendships grow; seven come from skill levels; a few are bought
at the saloon. Only one recipe is known at the start (the fried egg).

**Quality.** Ingredient quality does not matter: every dish of a kind is the same. The only upgrade is Qi Seasoning, a
late-game shop item that makes a dish "gold quality": 80% more health and energy, a 50% higher price, and each boost one
step stronger (S13).

**Boosts** (S14): exactly one food's boosts and one drink's boosts can be active at once; eating a food with boosts
replaces the last food's boosts, while a food without boosts leaves them alone. Durations are counted in real minutes
and everything clears when you sleep. This is the same "one meal at a time" rule Bug Farmer has chosen.

**Two smaller ideas worth noting.** Some dishes are ingredients of other dishes (a fried egg, hash browns and pancakes
go into a "complete breakfast") (S13). And at the Desert Festival a chef lets you pick two ingredients, a sauce and a
base, and the meal's boosts are the two ingredients' boosts added together (S17): a tiny "build your own dish" that
needs no recipe book.

**Multiplayer.** Each player learns recipes separately and cooks alone; there is no cooking together. A new
multiplayer farm can lower all sale prices, cooked food included, to balance more players earning (S18). The one
shared pot is a festival: at the summer Luau every villager adds an ingredient to a communal soup and the governor
judges it; in multiplayer every player must add something, and **the worst ingredient decides the result** (S87), so
one careless or mischievous player can spoil it for all.

**Praise.** The boosts that matter are used and liked: fishing boosts for the legendary fish, speed boosts, a cheap
dish that turns leftover fish into one stack (S19). Some players enjoy cooking as a collection: find every recipe, cook
everything once, get a star (S19).

**Complaints.**
- Cooking is a loss: "The energy/health goes DOWN when you cook? And the profit difference is so minimal" (S19). A
  dish often restores less than its raw ingredients would.
- Most dishes have no reason to exist: "there are 80 dishes in the game. I would say maybe 15 have any use. the rest
  are just there to make perfection more of a task" (S19).
- Recipes arrive slowly, at random, and out of season, so the recipes you hold don't match the crops you have (S19).
- No skill, no minigame, no growth: "Cooking is the only mechanic in the game I earnestly dislike. If I had my way,
  Cooking would be a skill, there would be a mini-game involved, and we'd be able to cook at campfires" (S20). A
  press piece makes the same case: "all recipes turn out exactly the same and give the same benefits every time", and
  asks for quality ingredients to make better dishes and for experimenting (S21).

**Time.** Instant: one click.

**Lesson for Bug Farmer.** Stardew's rule for boosts is already Bug Farmer's, and the fridge-linked menu is a model of
convenience. Its cooking is criticised because nothing the player does changes the dish, cooking can lose value, and
most dishes don't matter. Bug Farmer must make every dish worth more than its raw parts and give the player some way to
make it better.

### 1.3 Valheim (2021 early access, 1.0 in September 2026; survival and building for 1 to 10 players; S83, S84)

**What food does** (S22). There is no starving, but food is how you get a usable health and stamina bar. You can have
three different foods active at once; each raises your maximum health and stamina (and a magic bar later) and your
healing rate, and its bonus fades as it is digested, slowly at first and quickly near the end. Each food leans to
health, stamina or balanced, shown by a coloured fork on its icon, so players choose a mix for what they are about to
do: stamina food for exploring, health food for a boss. Food from each later region is stronger, so food is one of
the game's main ways to grow stronger (a meadows boar steak gives 30 health; plains bread 23 health and 70 stamina).

**How it works: a chain of real objects in the world** (S23 to S27).
- **Cooking station**: a spit placed over a campfire. Put raw meat on it; after 25 seconds it is cooked; leave it too
  long and it turns to coal. Players line up seven to ten spits over one fire.
- **Cauldron**: hangs over a fire and makes stews, soups and jams from a menu. It is upgraded by building tools beside
  it (a spice rack, a butcher's table, pots and pans, a mortar and pestle, rolling pins and boards), each upgrade
  opening more recipes (S24).
- **Food preparation table, then stone oven**: the table turns flour and other things into uncooked dishes (bread
  dough, an uncooked pie); the oven holds four at once, bakes in 50 seconds, and burns them to coal after 100. Bread
  is barley, ground to flour at the windmill, made into dough at the table, then baked (S26).
- **Mead kettle, then fermenter**: the kettle makes a mead base; the fermenter, which must stand under a roof, turns
  it into six meads over two in-game days (S25).
- **Feasts** (a later addition): a big dish made at the preparation table with a spice bought from a late trader. You
  set it down on a table with a serving tray; it holds 10 servings that anyone can eat, each serving of the first
  feast lasts 50 minutes, and the platter looks emptier as servings go (S27).

**Learning recipes.** There are no recipe items. Recipes appear in a station's menu as the station is built and
upgraded; the cauldron itself only appears once you have smelted tin and built a forge (S24). The exact unlocking rule
for each food was not confirmed (see Part 5).

**Quality.** None. A dish is always the same; strength comes only from which dish, which comes from how far into the
world you have travelled.

**Minigames.** None, but the spit and the oven ask you to come back in time or lose the food to coal: a light
"don't burn it" tension that runs in the world while you do other things.

**Multiplayer.** Every station is a shared object in the world, so friends share a kitchen, a fire and the chests
that feed it. Feasts are built for groups: one cook, ten servings, set out on the table.

**Praise** (S28). Food as a way to choose how to play instead of a hunger bar: "Using different food types as a way to
switch to different survival/battle modes is a good change from simply continuously stuffing your face" (review
235149084); "The food system is powerful and rewarding instead of some ... meter I have to constantly fill or else it
kills me" (review 235995588).

**Complaints** (S28, mostly reviews written after the 1.0 release):
- Food becomes upkeep: "Food becomes another job" (review 235402427); without three good foods "you still feel really
  weak" (review 235736034); you respawn after death with no food and a tiny stamina bar (review 236307649).
- The fading bonus feels like a trick: a 20-minute food is at about half strength by minute 10, and you can only eat
  again "at some arbitrary point" (review 235306504).
- Waiting and gating: "food needs to be cooked by standing in front of a campfire and waiting a minute every time"
  (review 234934305); you can catch fish from the start but can't cook them until the third region (reviews 235387848,
  236307649).
- The bonus is only numbers: "You simply increase your stamina and HP depending on what you eat" (review 235693089).

**Time.** 25 seconds a spit, 50 seconds an oven load, two in-game days for mead; the farming behind food is the long
part.

**Lesson for Bug Farmer.** Valheim is the closest match to Bug Farmer's rule that food raises Health and Stamina, and
its chain of physical stations (spit over a fire, a pot that grows with tools beside it, table then oven, kettle then
fermenter) is a strong model for the campfire, stove, range, keg and mill. Its feast is the clearest multiplayer meal
in any game studied: one cook, a dish on the table, servings for the group. Its warning: if the bonus is large enough
that you feel weak without it, eating becomes a chore; a bonus that fades in strength reads as unfair; and recipes
locked far behind ingredients you already hold frustrate.

### 1.4 The Legend of Zelda: Breath of the Wild (2017) and Tears of the Kingdom (2023), single player

**How it works** (S29, S30). There are no recipe items. You hold up to five materials and drop them into a lit cooking
pot, or simply roast one over any fire (a roasted material gives 50% more health than raw but loses its special
effect), or leave it somewhere freezing. The result depends only on the materials:
- **Health**: a pot dish restores twice what its raw materials would.
- **One effect only.** Many materials carry an effect (attack, defence, stealth, speed, heat or cold resistance,
  extra stamina and so on). "Combining ingredients with different effects will not cause the resulting food to have
  multiple effects. Instead, the resulting food will have only the most prominent effect present. If all ingredients
  cancel each other out, the resulting food won't have any special effect at all" (S30).
- **Strength**: each effect material has a *potency* number; the dish's total decides whether the effect is low,
  middle or high level.
- **Length**: every material adds 30 seconds, matching effect materials add more, and a few special materials (an
  egg, a spice, rare parts) add a fixed bonus once each.
- **Failure**: putting monster parts with food, or wood and ore in the pot, makes Dubious Food or Rock-Hard Food,
  which looks bad and does little (S31). *Elixirs* are made the same way from bugs and monster parts: the bugs set the
  strength and the monster parts the length (S29).
- **Luck**: one cook in ten is a *critical cook*, adding one random bonus (more health, five more minutes, one effect
  level up, an extra heart or stamina); on the night of a "blood moon" every cook is critical for a short window (S29).

**Learning recipes.** By experiment, and from hints: townspeople, posters and books mention dishes (S29). The press
piece on Stardew holds this up as the model: players "discover powerful recipes to make through their own
experimentation as well as through hints to better recipes scattered throughout the map" (S21). Tears of the Kingdom
adds a single-use portable pot to cook anywhere (S31). Whether Tears of the Kingdom also saves cooked recipes for
quick re-cooking could not be confirmed from a source (see Part 5).

**Quality.** Entirely from what goes in: more and stronger materials of the same effect give a stronger, longer
effect; mixed effects cancel. There is no star rating; the numbers are the quality.

**Minigames and time.** None. One short cooking animation per dish, one dish at a time.

**Multiplayer.** None (single-player games).

**Lesson for Bug Farmer.** Zelda already solves Bug Farmer's "one boost per dish" rule: a dish's boost is whichever
effect its ingredients carry most of, its strength and length come from how much of that effect went in, and mixed
effects cancel into a plain dish. Its exact numbers are hidden in the game, though, and are documented by players in
wiki tables of potency and duration (S29); and every dish is cooked one at a time.

### 1.5 Disney Dreamlight Valley (2022 early access, 2023 full release)

**How it works** (S32, S33). At any stove you drag ingredients into a pot and press "Start Cooking", which uses up
one coal (dishes need one to five ingredients; the pot's exact limit was not confirmed). If the mix matches a recipe
you get that dish; you don't need to know the recipe first, so recipes are discovered by trying. Known recipes are listed in a book; pinning one shows how many of each ingredient you
hold, and an *autofill* button drops in the right ingredients for a known recipe.

Recipes mix fixed and open slots. A history panel in the game colours each ingredient of your last 20 meals: green for a
*mandatory* ingredient (this exact item), yellow for a *versatile* one ("any fish", "any vegetable") and red for an
*unnecessary* extra. A specific ingredient can take over a general recipe (three "any vegetable" make a grilled veggie
platter, but if one of them is lettuce you get a hearty salad).

**Quality.** Each dish has 1 to 5 stars, which simply follow how many ingredients the recipe needs. Extra ingredients
and better "versatile" ingredients raise the energy the dish gives and its sale price, but not its stars. Stars matter
mainly for a task list (S33).

**What food does.** Meals restore *energy* (the bar that farming and mining use) and can overfill it into a "Well Fed"
surplus that makes you walk faster until it runs out (S33).

**A helpful character.** At Remy's restaurant the chef Remy (a rat from the film *Ratatouille*) stands by the pot and
reacts as you add ingredients: he raises his arms when the pot now makes a complete dish, waits when it doesn't, and
droops when you remove something that changes the dish (S32). This is a gentle, in-world hint system for discovery.

**Multiplayer.** The game now lists multiplayer on its store page (S86); no shared cooking was found in the pages read.

**Complaints.** Players' main complaint found was quest design rather than cooking: being made to cook meals for
unrelated side quests to continue the story (S34, review 233154375). One review calls it a "quite questionable cooking
system" without saying why (review 233200410). Little else could be found (see Part 5).

**Time.** A click and a short animation per dish.

**Lesson for Bug Farmer.** Free-form discovery and a recipe book live happily together: anything that matches a recipe
works, a found recipe is remembered and can be autofilled, and "any fish"-style open slots (which Bug Farmer's design
already has) let better ingredients make a better dish. Stars that only count ingredients are not a quality system
players care about. A cook who reacts to the pot is a lovely way to hint.

### 1.6 Don't Starve and Don't Starve Together (2013, 2016; survival, alone or together)

**How it works** (S35). The *crock pot* is a station with exactly four slots, all of which must be filled. Each
ingredient has *food values* in groups (meat, vegetable, fruit, egg, fish, sweetener and so on; a drumstick counts as
much meat as two small morsels). When you start, the game checks every recipe's rules against the totals (honey ham
needs a meat value of at least 2 plus honey; dragonpie forbids any meat), and if several recipes fit, the one with the
highest *priority* wins, a tie being settled at random. Anything that matches nothing becomes Wet Goop. Twigs and other
*fillers* can fill spare slots without changing the result. Cooking takes 10 to 20 seconds for most recipes, and the
pot gets more out of food than eating it raw, even turning twigs into part of a meal.

**Learning recipes.** By experiment, or from the community's tables. Don't Starve Together later added a cookbook
that records the dishes you have cooked and the ingredient sets you used, and shows a dish's health, sanity and hunger
only after you have eaten it (S37).

**Quality.** No stars: the dish is decided by the food values; better ingredients make it easier to reach a stronger
recipe. Don't Starve Together's chef character, Warly, adds a second step: he grinds spices at a mill (chilli flakes,
garlic powder, honey crystals, seasoning salt) and seasons any crock-pot dish at a seasoning station, which adds one
effect: chilli for 20% more damage, garlic to absorb a third of incoming damage, honey to double mining and chopping
(S36).

**Multiplayer.** The pot is a shared object anyone can use. Warly is designed as the group's cook: "In multiplayer,
others can help farm and gather while he focuses on meal prep and seasoning" (S36), and he dislikes eating the same
dish again within two days (each repeat is worth less), which pushes variety.

**Praise and complaints** (S38). Players love finding things out for themselves, but many reach for the wiki: "A lot of
the game feels like it requires having the wiki open. Many mechanics and crafting recipes aren't very intuitive"
(review 235457905), and one long-time player recommends a mod that predicts what the crock pot will make (review
230925937). Remembering recipes becomes a shared joke among friends ("hey anyone remember how to make trail mix?",
review 234584165).

**Lesson for Bug Farmer.** A recipe defined by *food values in groups* is the cleanest engine for free-form cooking,
and it handles "any bug" or "any fish" naturally. Seasoning a finished dish to give it its effect is a neat way to
separate "what the dish is" from "what it boosts". But hidden rules send players to the wiki or to mods, so whatever is
hidden must be recorded in-game the moment it is found.

### 1.7 Coral Island (2022 early access, 2023 full release; a farming game with online co-op, S86), with Sun Haven and Fae Farm

**Coral Island: utensils, a learn-by-doing minigame, quality from ingredients** (S39, S40, S41).
- Cooking opens with the kitchen house upgrade. A shop sells *utensils*: blender, ceramic bowl, chef knife, frying pan,
  iron skewer, seasoning set, skillet; recipes also name a pot, oven or grill. Each recipe needs one utensil.
- **Two ways to cook.** If you know the recipe and own its utensil, you pick it from a menu and it cooks at once, taking
  ingredients from your bag or a global storage chest. If you don't know it, you can still cook it *by hand*: choose the
  utensil and ingredients yourself, then play a short timing minigame (press when a sliding marker is inside a
  highlighted section). Success makes the dish and teaches you the recipe. A wrong combination, wrong utensil or
  missed press gives a failed dish.
- Many recipes take ingredient groups ("any egg", "any fish", "any oil"), and most make two servings.
- **Quality**: the quality of the ingredients sets the dish's quality (base, bronze, silver, gold, osmium), which
  raises its price and how long its boost lasts, from 2 hours at base to 4 at osmium (the wiki warns that some of the
  middle values may be swapped by a bug). One food boost and one drink boost can be active at once (S41).
- **Praise**: "Interesting cooking dynamic (you have to buy the kitchenware first, and you can 'discover' recipes with
  manual cooking). Quality of cooking ingredients increases quality of food. Most recipes make 2 servings" (S42, review
  235636746). **Complaint**: the slider "serves no purpose and just adds an extra step for no reason", because it
  doesn't change the dish (S79).
- **Time**: menu cooking needs no minigame; the hand-cooking slider takes a moment.

**Sun Haven** (S43, S44) spreads cooking over many specialised stations: a cooking pot, a baker's station, a grill, a
jam maker (jams give bonus experience to one skill each), juicers, a keg, a dessert station, a sushi table, an ice-cream
maker and a tea kettle. Its distinctive rule: **eating dishes permanently raises your stats**, with a cap of 100 for each
individual dish and diminishing returns, so variety is how you grow (S44). A player singles this out: "Eating
different food gives you permanent mana and health so it gives you a reason to want to cook" (S85, review 232625521);
another wants recipes earned over time instead of "dumped on you all at once", so early dishes get used (review
232176449). Sun Haven has online co-op (S86).

**Fae Farm** (2023, online co-op for up to four players) (S45, S56) uses three cooking stations: a cooking fire for
simple food from one open ingredient group ("1 fish", "1 root vegetable"), a cooking hearth for better food that also
gives skill boosts, and a food preparation table that makes chopped intermediates (chopped vegetables, sliced
mushrooms) for the hearth.

**Lesson for Bug Farmer.** Coral Island shows that a recipe system and a discovery system can be one system: known
recipes cook from a menu, unknown ones can be attempted by hand, and the attempt teaches the recipe. Ingredient
quality setting the boost's *length* is one of the clearest "better food" rules found, and it sits comfortably beside
Bug Farmer's existing rule that effort sets length. Fae Farm's split (fire for one-ingredient food, hearth for dishes, table for
prep) is almost exactly Bug Farmer's campfire, stove and a possible prep counter.

### 1.8 Rune Factory 4 (2012) and Story of Seasons: Friends of Mineral Town (2019 remake)

**Rune Factory 4** (S46). Seven *cooking tools* are pieces of furniture bought from the restaurant: a cooking table
(free), then a knife, frying pan and mixer (with a basic licence) and an oven, steamer and pot (with a professional
licence). Every dish belongs to one tool.
- **Learning**: mostly by eating *Cooking Bread*, a bread that teaches one random recipe suited to your skill (bought,
  won at festivals or found in chests). You can also cook without the recipe if you put in the right ingredients, but
  it costs much more of your energy, and if it costs more than your maximum the attempt fails.
- **Recipes are minimums**: up to six ingredients can go in; extra ingredients don't spoil the dish.
- **Quality**: every ingredient has a level from 1 to 10, and the dish's level is the *average* of its ingredients'
  levels rounded down; each level adds 12.5% to all the dish's effects, up to +112.5% at level 10, so only level-10
  ingredients make a level-10 dish.
- **Failure**: missing ingredients or too much energy cost gives a Failed Dish ("Edible, but tastes pretty bad"), and
  occasionally a Disastrous Dish.
- Once every tool is bought, a "unify" order lets you reach every tool's menu from any one tool, a late convenience.

**Story of Seasons: Friends of Mineral Town** (S47). After the second house upgrade the shop sells one utensil at a
time, the next only ten days after the last: knife, frying pan, pot, mixer, whisk, rolling pin, oven and a seasoning
set. A recipe can need several utensils at once (one needs the seasoning set, knife, pot, rolling pin and oven).
Recipes come from villagers, from a cooking show on Tuesdays, and some from *using* ingredients: cook dishes with 20
cucumbers, tomatoes, carrots and cabbages and you learn a recipe.

Both are single-player games (S86), and few of their Steam reviews mention cooking (S85).

**Lesson for Bug Farmer.** Utensils make kitchen progress visible and buyable; in Bug Farmer, where the village's
stations belong to the townspeople, the equivalent is the stations a player builds or buys for their own plot. The
average-of-ingredients rule is simple and fair, but it makes one poor ingredient drag the whole dish
down, so seasonings and fillers should be left out of the average. Learning a recipe by using its ingredients often
fits a farming game well.

### 1.9 Spiritfarer (2020; a second player can join as the cat, Daffodil)

**How it works** (S48, S49). The kitchen is a building on your boat. You add up to five of an ingredient, confirm, and
it cooks on a timer shown beside the oven. You can walk away; when it is ready the kitchen smokes and a notice with a
steaming bowl and a timer's ding follows you round the boat. Leave it too long and it becomes Burnt Food. At first a
dish has one kind of ingredient; a kitchen upgrade allows two.

**Learning recipes.** Choose a known recipe from the book, or just put ingredients in to find new ones.

**What decides a dish's worth.** There is no quality score. Each dish has a *type* (comfort, fine dining, dessert,
soup, pub food and so on, fifteen in all), and each passenger loves or hates certain types and refuses some ingredients
(one eats only fruit; one is vegan). Feeding them what they love lifts their mood, and happy passengers help on the
boat (one clears burnt food from the oven) (S49).

**Opinions** (S85). One player likes the calm: "Plenty of timers and countdowns to watch, but there's no rush"
(review 231020409). Others find the round of chores, cooking included, "too repetitive and tedious" (review 234226279)
and ask why the passengers never "go to the kitchen and eat something for themself" (review 233962197).

**Lesson for Bug Farmer.** The walk-away timer with a ding and a "don't let it burn" window is a calm, low-pressure way
to make cooking a background task while you do other jobs. And cooking *for someone* (the people you feed, not only a
number) gives dishes meaning; Bug Farmer's townspeople could have favourite dishes the same way.

### 1.10 Graveyard Keeper (2018; single player, S86)

**How it works** (S50, S51). The kitchen has a cooking table (for components and cold dishes) and an oven (for most hot
food), which must be fuelled first and cooks in a few real seconds. Complex dishes are built from components made at
the table and in the oven. There is batch production: you can order several of a dish at once (S50).

**Quality.** Many dishes come in three qualities, shown as copper, silver and gold stars, and higher quality restores
more energy (a pumpkin soup restores 40, 50 or 60). The quality of a complex dish is a chance built from its inputs:
the "dinner" starts with a 30% quality chance and each star-rated component adds 33%, 67% or 100% for copper, silver or
gold (S51). Some recipes carry a "base downgrade", a penalty to quality.

**Complaints** (S52). Quality turns batch cooking off: "The developer added a system to craft multiple of the same
items at once, which is great! So why can I not use it when I craft items with a quality star? Having to put 1 onion
ring at a time in the oven gets really annoying" (review 234684008). The same reviewer dislikes not being able to stop
a batch once started. Another says selling many gold-star items crashes their price (review 234670227). Long chains of
small steps are a common complaint about the game generally (review 233787314).

**Lesson for Bug Farmer.** If quality comes from ingredients, the interface must still let a player cook several at
once when the ingredients match; otherwise quality becomes a clicking tax.

### 1.11 Action cooking: Overcooked (2016) and Cooking Mama (2006)

**Overcooked** (S53, S54) is a cooking game for up to four people: fetch, chop, cook, plate, serve and wash up against
the clock, in kitchens built to force teamwork. Its designer's account of building it is the best source found on
cooking *together* (S54):
- The core: "you can choose to perform all actions yourself but you quickly learn that by sharing the workload you can
  drastically reduce the time it takes... Many hands make light work." The first prototype was a counter between two
  players: carry an ingredient round, or pass it over the counter for your partner to chop.
- Players soon fell into fixed roles and stopped talking. Three fixes made it work: always **more jobs than players**;
  **delays** (a pot takes time to cook, so you must do something else and risk it catching fire); and **disruptions**
  that change the kitchen mid-round.
- **Freedom versus frustration**: at first the pot showed no contents and players lost track ("Erm... I think I've put 3
  onions in that one!"). They added icons showing what is in each pot, limited what could go in, stopped unprepared
  ingredients from going in, and replaced words with pictures, keeping enough to talk about without constant
  mistakes.
- Losing lives felt like constant failure; a timed score where a failed order costs a little was more fun.
- All chefs are equal (no faster choppers), so the game is about the team, not individual skill.

**Cooking Mama** (S55) is a chain of tiny minigames, each under about 10 seconds (draw lines to chop, time the heat,
flip in the pan, arrange the plate); a dish needs from one to a dozen of them. Each dish is graded bronze, silver or
gold from the average of its steps, and the best medal is shown beside the dish. A failed step isn't the end: Mama
appears, eyes aflame, saying "Don't worry, Mama will fix it!" and the dish goes on.

**Lesson for Bug Farmer.** These are the clearest rules for any hands-on cooking: keep each step to seconds; let a
failure cost a little, not the whole dish; always show what is in the pot; and if cooking is shared, make waiting time
the reason to split up the work. Overcooked's real-time chaos is a whole game in itself and too much for a sandbox
meal; its counter-passing and visible pot contents are worth borrowing.

### 1.12 Other games with a lesson for Bug Farmer

**Core Keeper** (2022 early access; a top-down mining and farming sandbox for up to eight players) (S57, S58). The
cooking pot takes exactly **two ingredients**, and any two work. The dish's kind (soup, salad, wrap, steak, fillet...)
comes from the main ingredient, its name gets a word from the other ("Hearty Pepper Wrap"), and its colour blends
both. Its effects are the dish kind's own effects plus both ingredients' effects; if two give the same effect, the
higher wins. *Golden* versions of crops, grown by a skilled gardener, make the dish rare or epic, raising every effect
by 25% or 50%. 74 ingredients give 2,775 possible dishes. The ingredients' hidden effects are not shown in the game.
*Lesson*: two-slot free cooking is quick to read and endlessly varied, and a rarer version of an ingredient is a
natural quality source (in Bug Farmer, prime bugs if the ranching design adds them). Players do ask for the hidden
effects to be shown (S80).

**Grounded** (2020 early access, 2022 full; four teenagers shrunk to insect size, for up to four players; it has
hunger and thirst) (S59, S60). The closest premise to Bug Farmer's: weevil roast, aphid roast, gnat roast and grub
roast are the everyday meals. A roasting spit takes three raw meats, turns them visibly, and they are done in 30 seconds ("You can tell food is ready
when it looks tasty"); a jerky rack dries three over 16 real minutes into jerky that never spoils; a smoothie station
makes drinks from a *recipe plus a base*, where the recipe sets the effect and the base sets the strength or length (a
"beefy" base heals twice as much, a "sticky" base doubles the effect's length). Smoothie recipes are learned by
analysing their ingredients at a research machine.
*Lesson*: bugs as meat read naturally when cooked on a visible spit; the "recipe sets the effect, base sets the
strength" split is a tidy way to make better food without new recipes.

**Genshin Impact** (2020) (S61, S62). Cooking a dish by hand is a timing test: stop a moving marker in the orange band
for a Delicious dish (full effect), yellow for Regular, grey for Suspicious (weakest). Leaving the test costs no
ingredients. Each Delicious cook raises that dish's *proficiency*; after 5 to 25 perfect cooks (more for rarer dishes)
**Auto Cook** unlocks, making up to 99 at once, always Delicious. Some characters cook a special version of their
favourite dish, and some have a 12% chance to make double. Food boosts are grouped (attack, defence, stamina,
elemental), and only one boost per group works at a time.
*Lesson*: the clearest answer found to "how many steps before it gets tedious": the skill test matters while a dish is
new, then the player earns the right to skip it.

**Monster Hunter: World** (2018) (S63, S64). Two ideas. In the field, a portable *BBQ spit* roasts raw meat while a
tune plays: take it off too early and you get a rare steak (no stamina effect), at the right moment a well-done steak,
too late burnt meat; "The cooking process is all about timing (or careful listening)." At the canteen you can order a
preset platter or build one from 2, then 4, then 6 ingredients (meat raises attack, fish defence, vegetables
resistances, and more of one kind stacks); fresh ingredients raise the chance of bonus food skills; you can save five
favourite platters; and a voucher makes the next meal free for every hunter in the shared hub.
*Lesson*: a single short timing test on a spit, with three readable outcomes, is the simplest cooking test found,
and it is exactly Bug Farmer's roast fly. A meal that one player can buy for everyone in the room is a
simple social gesture.

**Pokémon Scarlet and Violet** (2022) (S65, S66). Sandwiches are built at a picnic, by hand: choose up to six fillings
and four condiments yourself ("creative mode"), or pick a recipe taught by a townsperson, which chooses the
ingredients for you; then drop the fillings onto the bread one by one (they can slide off), put the top slice on, and
push in a pick. A sandwich that matches no recipe is named "A Tasty (player name) Original". Each sandwich gives three
*meal powers* for 30 minutes, each at one of three levels. Friends can make one sandwich together in multiplayer. How
their contributions combine could not be confirmed (see Part 5).
*Lesson*: a homely physical step (placing fillings) and a personal name for an original dish give free-form cooking
warmth; a recipe mode that auto-selects ingredients keeps it quick.

**Terraria** (2011; a 2D sandbox, alone or with others) (S67, S68). Food gives one of three versions of the same
boost: Well Fed (minor improvements to all stats and faster healing), Plenty Satisfied (medium) or Exquisitely Stuffed
(major), lasting 1 to 48 minutes depending on the food. Only one can be active; the most recent wins. Food is crafted
instantly at a cooking pot and can be set out on plates as decoration.
*Lesson*: the plainest "better food raises them more" rule: three named tiers of one general boost.

**Necesse** (a top-down survival and settlement sandbox with co-op; 1.0 in 2025, S86) (S69). Every food is Simple (raw, 4-minute
boost), Fine (cooked; boosts of 5 to 45 minutes in the examples read) or Gourmet (several ingredients, often several
boosts at once), and food also makes the settlers who eat it happy.
*Lesson*: three tiers by dish complexity are easy to read, and feeding townspeople is a second use for cooking.

**My Time at Sandrock** (2023) (S70, S71). Cooking stations are upgraded to unlock *methods* (pot and steamer, then a
wok, then an oven). A known recipe is queued like any other crafting job. To discover one, choose up to five
ingredients and herbs and a method; the right formula unlocks and cooks the dish, a wrong one consumes the ingredients
and makes nothing. Recipes also come from recipe books hidden in the world, from missions, and from chatting with two
townspeople, who sell recipes and give them free to close friends.
Players complain about ingredient bottlenecks (salt for cooking can only be bought in small amounts each day) and
that the cooking table can't be placed indoors (S85, reviews 231624324, 230915152). The game has online co-op (S86).
*Lesson*: "method" (roast, boil, fry, bake) as a dimension of a recipe maps neatly onto Bug Farmer's stations, but
losing everything on a failed experiment is harsh, and a basic ingredient rationed by a shop becomes a chore.

**Potion Craft** (2021 early access, 2022 full) (S72, S73). Not cooking, but the most praised hands-on crafting found.
Grinding an ingredient in a mortar (how finely matters), adding it, stirring, heating and adding water move the brew
across a hidden map, and an effect is gained by reaching its spot; the closer, the stronger. Reviewers called it
"tactile but never difficult" and said it "makes sure that players understand the purpose of every crafting step"
(S72). A finished recipe can be saved in a recipe book (with limited pages) and brewed again from it.

**Kingdom Come: Deliverance** (2018) and its sequel (2025) (S74, S75). Alchemy follows a written recipe step by step at
a bench (add the base, add herbs, grind, boil, finish); a perfect brew gives three potions for one set of ingredients,
and higher skill forgives mistakes. Once you have brewed a potion by hand, a perk (*Routine*, at alchemy level 10)
lets you **auto-brew** it. The wiki pages cover both games, and which game the auto-brew perk belongs to was not
confirmed (see Part 5).
*Lesson* (with Potion Craft and Genshin): make the hands-on version the way you *learn* a dish, then let the player
repeat it without the hands-on steps.

### 1.13 What designers and players say about cooking systems in general

**Designers.**
- *Fruitbus* (a 2024 deep dive by one of its developers, S76): the team first tried physical simulation (knives that
  really cut a mesh, a "cookedness" number per piece, blenders mixing bits) and got "a messy kitchen with the floor
  full of various bits and chunks of fruit, mysterious liquids, and dubious amounts of state". They kept the feeling
  and dropped the precision: "It is the feeling of cooking that is important, not the preciseness of the simulation",
  which their director called "Hollywood Cooking". The model that worked: **processes** (verbs such as cut, fry, boil,
  blend, bake), **appliances** that run a process on their own once started (a blender, an oven) and **tools** that
  need the player's repeated input (a knife), and food that is an archetype plus a state (an apple, sliced and fried).
  A recipe is then a short sentence of processes ("Dice an apple and liquefy it. Bake bread...").
- *"The unrealized potential of cooking in games"* (a 2024 opinion piece, S77) sorts cooking into two forms:
  combining gathered ingredients for bonuses (Breath of the Wild, Monster Hunter, Stardew) and chains of timing
  minigames (Cooking Mama, Overcooked). It finds "just combining ingredient to assemble a predetermined recipe can be
  tedious", that minigame chains get repetitive, and that most games lack the creative part of cooking: "swapping
  ingredients, improving the taste of a dish by choosing the right spices, or trying unusual ingredient combinations
  ... the path to the final dish is usually a straight line with a binary win state". It praises *Order Up!*, where
  some customers want food overdone, raw or spicy: "an overdone dish needs to be removed just on the cusp of burning".
- *Against the Storm* (a 2024 article drawing on its designer's talk, S78): complex dishes are worth making because
  they are inputs to other things as well as outputs (villagers of different races want different dishes, drinks
  run service buildings, packed food trades well), so food is "more than the bare essentials".

**Players** (beyond those quoted under each game).
- *Coral Island*: "They can get rid of the little game in cooking, serves no purpose and just adds an extra step for
  no reason." A reply: "I kind of wish the mini game related to the quality of the food... But I kind of like the mini
  game it makes it seem like you are at least DOING something" (S79).
- *Core Keeper*: players ask to filter ingredients by the boost they give, because the effects are hidden and "the game
  only remembers the only recipe that you crafted, rather than remembering what ingredient you used"; another finds
  the cooking menu cluttered with every combination ever tried and asks for favourites (S80).
- *Disney Dreamlight Valley*: a tip that repeated cooking is faster with a controller, because you can "mash A as fast
  as you can to end the animation"; a new player can't find how to experiment (you drag ingredients into the pot)
  (S81).

**Common threads.** Across every game and complaint, five things decide whether cooking feels good or like a chore:
1. **Does the player's effort change the result?** Minigames that don't affect the dish are called pointless (Coral
   Island); dishes that are always identical are called shallow (Stardew).
2. **Is the dish worth more than its parts?** If cooking loses value, nobody cooks (Stardew).
3. **Can a routine meal be made quickly?** Every game that lasts has a fast path for known dishes: a menu (Stardew,
   Coral Island), autofill (Dreamlight), auto-cook after mastery (Genshin), auto-brew (Kingdom Come), a saved recipe
   (Potion Craft), batch production (Graveyard Keeper, Sandrock). Where the fast path is missing, players complain
   (Graveyard Keeper's one-at-a-time quality items, Dreamlight's animations, Palia's solo routine).
4. **Are the rules visible?** Hidden values send players to wikis and mods (Don't Starve, Core Keeper, Zelda);
   unclear quality rules annoy (Palia). Recording discoveries in-game helps (Don't Starve Together's cookbook,
   Dreamlight's history panel).
5. **Is there a reason to cook together?** Few games make cooking itself a group activity (Palia's parties,
   Overcooked, Pokémon's shared sandwiches); Valheim and Monster Hunter make *eating* a group moment (a feast, a free
   meal for the room).

---

## Part 2. Source table: technique, cost to players, fit for Bug Farmer

One row per concrete technique. "Cost to players" is what the technique asks of a player each time (time, clicks,
attention) and what players complain about. "Fit" is judged against the rules at the top of this page.

| Source | Concrete technique | What it costs players | Fit for Bug Farmer |
|---|---|---|---|
| Stardew Valley (S13, S14) | Pick a known recipe from a station menu; the fridge counts as your bag; one food boost and one drink boost at a time | One click, instant. Called shallow: every dish identical, effort changes nothing (S19 to S21) | **High as the fast path.** The one-meal rule is already Bug Farmer's |
| Stardew Valley (S15, S19) | Recipes from a weekly TV show, friendship letters and skill levels | Nothing per cook; unlocks are slow, random and out of season (S19) | Medium: teach recipes for ingredients the player has *now* |
| Stardew Valley (S13) | Qi Seasoning: a late item lifts any dish to gold quality (+80% healing, boosts one step up) | One consumable per cook | Medium: "an extra ingredient lifts quality", but Bug Farmer's seasonings already have a meaning |
| Stardew Valley (S17) | Desert Festival chef: pick two ingredients, boosts add together | Seconds | Medium: a quick "build your own dish" stall |
| Stardew Valley (S87) | Festival potluck: everyone adds one ingredient to a shared soup; in multiplayer the worst ingredient decides | Seconds, once a year | Warning: a shared dish must not be judged by its worst part |
| Palia (S1 to S6) | A dish as a chain of prep steps at several stations, each a small minigame, under a 3 to 5 minute countdown; intermediate ingredients | Minutes per dish; up to 15 steps; lag or a slip ruins the dish and the ingredients (S10); solo players find it repetitive (S10) | **Low for everyday meals**: clashes with one-step processing (P11) and with meals that last only 5 to 20 minutes |
| Palia (S1, S11, S12, S88) | Cook together: each helper does one step; everyone who helps receives the full dish; the oven step needs no ingredients | Social time is the point; menus jump, wrong items get made (S11); full copies for every helper inflated the economy (S11, S12, S88) | **Keep the parallel steps and the beginner role; reject copies for everyone** in a shared economy |
| Palia (S7) | Campfire: 15-second cooks, no minigame, cannot fail | Seconds | High: the campfire's simple role |
| Valheim (S22) | Food raises maximum health and stamina; three foods at once; the bonus fades as it digests | Upkeep: "Food becomes another job"; respawning without food is crippling; the fade feels unfair (S28) | **High** (Bug Farmer's meal raises Health and Stamina) with a warning: keep the base usable, don't fade the bonus |
| Valheim (S23 to S26) | Physical chain of stations: spit over a fire (25 s, burns to coal), a pot upgraded by tools placed beside it, prep table then oven (50 s, burns at 100 s), kettle then fermenter (2 in-game days) | Waiting at the fire is a complaint (S28); otherwise light | **High**: matches campfire, stove, keg and mill; "don't let it burn" is cheap tension |
| Valheim (S27) | Feast: a dish set on a table with 10 servings anyone can eat | One cook, many eaters | **High**: the model for a group meal |
| Zelda (S29, S30) | Free-form pot of up to five; the dish takes the *most prominent* effect; strength = sum of potency; length grows per ingredient; mixed effects cancel; wrong mixes make dubious food | Seconds per dish but one at a time; numbers hidden, players use wikis | **High for the boost rule** (one boost per dish) |
| Zelda (S29) | Critical cook: 10% chance of a random bonus | None | Low: random quality is opaque |
| Dreamlight Valley (S32, S33) | Free-form pot; recipes with exact, "any X" and extra slots; any match works; recipe book with autofill; a history panel colours each ingredient's role | Drag, click, then an animation per dish; players mash buttons to skip it (S81) | **High**: "any fish/any fruit" is already in Bug Farmer's data; autofill is the fast path |
| Dreamlight Valley (S32) | A cook character (Remy) reacts to each ingredient you add | None | **High**: a townsperson cook who hints |
| Don't Starve (S35) | Ingredient *food values* by group; recipes as rules on the totals; priority settles ties; fillers; Wet Goop when nothing matches | Four slots, 10 to 20 s; hidden values drive players to wikis and prediction mods (S38) | Medium: a good engine for groups; must show values |
| Don't Starve Together (S36) | Seasoning a finished dish at a separate station adds one effect | An extra step and a grinding step | Medium: "seasoning picks the boost" (Route E) |
| Don't Starve Together (S37) | Cookbook records every dish and ingredient set you've cooked; stats shown after eating | None | **High**: any discovery route needs it |
| Coral Island (S39, S41) | Utensils bought over time; cook an unknown dish by hand with a one-press slider, which teaches it; known dishes cook from a menu; ingredient quality sets boost length; most dishes make two servings | One slider per attempt; called "an extra step for no reason" when it doesn't affect the dish (S79) | **High**: "learn by hand, cook from the book"; make the hand step matter |
| Rune Factory 4 (S46) | Cooking tools as furniture; a "Cooking Bread" teaches a random recipe; extra ingredients allowed; dish level = average of ingredient levels | None per cook | Medium: the average rule is simple; keep seasonings out of it |
| Story of Seasons (S47) | Utensils sold one at a time; some recipes learned by using an ingredient many times | Slow unlocks | Medium: "learn by using" suits a farm |
| Spiritfarer (S48, S49) | Walk-away oven: a timer, a ding that follows you, burnt food if left; passengers love or hate dish types | Low attention | **High**: walk-away timing; townspeople's tastes |
| Graveyard Keeper (S50 to S52) | Star quality as a chance built from star ingredients | Batch crafting switched off for quality items: "1 onion ring at a time" (S52) | Warning: quality must never switch off batch cooking |
| Overcooked (S53, S54) | More jobs than players; waits that force you to split work; visible pot contents; wrong inputs blocked; score not lives | Intense; a whole game in itself | Medium: borrow visible contents and waiting as a reason to share work |
| Cooking Mama (S55) | Chains of minigames under 10 s each; graded by the average; a failed step is fixed, not fatal | Each dish 1 to 12 minigames | Medium: keep any hands-on step under 10 s; failure costs little |
| Core Keeper (S57) | Two-ingredient pot; the dish keeps every effect (highest wins); golden crops make rare or epic dishes (+25% / +50%) | Seconds; hidden effects; a cluttered recipe list (S80) | Medium-high: "rarer ingredient, better dish"; show effects; add favourites |
| Grounded (S59) | Spit with visible doneness (3 meats, 30 s); jerky rack (16 min, never spoils); smoothie = recipe + base, the base setting strength or length | Walk-away | **High**: premise match (bugs as meat); "base sets strength" |
| Genshin Impact (S61, S62) | A timing test grades each hand-cooked dish (3 grades); perfect cooks build proficiency; after 5 to 25, auto-cook up to 99 at top grade; quitting the test costs nothing | About 5 s a dish until mastered, then none | **High**: the clearest cure for tedium |
| Monster Hunter: World (S63, S64) | BBQ spit by sound: rare, well-done or burnt; canteen platters from 2 to 6 ingredients; saved favourites; a voucher feeds the whole hub | A few seconds | **High**: the roast fly; a meal for the room |
| Pokémon Scarlet and Violet (S65) | Creative mode or recipe mode; fillings placed by hand; friends build one sandwich; an unmatched sandwich is named after its maker | A minute or two | Medium: personal names for originals; co-op building |
| Terraria (S67, S68) | Three tiers of one general food boost, by dish | Instant | **High**: the plainest "better food raises them more" |
| Necesse (S69) | Simple / Fine / Gourmet by dish complexity; settlers are happier when fed | Instant | **High**: tiers by complexity; feeding townspeople |
| My Time at Sandrock (S70) | Station upgrades add *methods* (pot, steamer, wok, oven); experiment with a method and up to five ingredients; known recipes queue | A failed experiment destroys the ingredients | Medium: methods map onto stations; never destroy ingredients |
| Potion Craft (S72, S73) | Tactile steps (grind finer, stir, heat) steer a brew on a hidden map; finished recipes saved and re-brewed | A minute or two per new potion; saved ones are quick | Medium: the tactile feel; save-a-recipe |
| Kingdom Come (S74, S75) | Brew step by step; skill forgives mistakes; a perfect brew gives three; auto-brew once brewed by hand | Long by hand, then none | **High**: "by hand once, then automatic" |
| Fruitbus (S76) | Processes (verbs), appliances that run on their own, tools that need input; food = archetype + state; "Hollywood cooking" | Not applicable | **High**: the data model for stations and hand actions |
| Game Developer opinion (S77) | Most games lack improvisation; *Order Up!*'s customers who want food overdone or raw | Not applicable | Medium: tastes as optional bonuses |
| Against the Storm (S78) | Complex food is also an input: needs, services, trade | Not applicable | **High**: give dishes uses beyond eating |
| Game Accessibility Guidelines (S82) | Don't make precise timing essential; avoid mashing and held buttons; offer a skip | Not applicable | **Required** for any timed action |

### Sources (all read in full unless marked)

Numbers match the citations above. "Steam reviews" means Steam's public review feed for that game, pulled in Steam's
most-helpful order (English, the last year) and searched for cooking words; review numbers are Steam's own IDs.

| # | Source | Address | Read |
|---|---|---|---|
| S1 | Palia wiki (official, wiki.gg): Cooking | https://palia.wiki.gg/wiki/Cooking | full text via API |
| S2 | Palia wiki: Cooking Interface | https://palia.wiki.gg/wiki/Cooking_Interface | full |
| S3 | Palia wiki: Poke Bowl | https://palia.wiki.gg/wiki/Poke_Bowl | full |
| S4 | Palia wiki: Prep Station | https://palia.wiki.gg/wiki/Prep_Station | full |
| S5 | Palia wiki: Star Quality | https://palia.wiki.gg/wiki/Star_Quality | full (stub) |
| S6 | Palia wiki: Ruined Food | https://palia.wiki.gg/wiki/Ruined_Food | full |
| S7 | Palia wiki: Campfire | https://palia.wiki.gg/wiki/Campfire | full |
| S8 | Palia wiki: Focus | https://palia.wiki.gg/wiki/Focus | full |
| S9 | Steam discussion "Star ingredients should give star food" (Palia, Nov 2024) | https://steamcommunity.com/app/2707930/discussions/0/4634860616374300645/ | full |
| S10 | Steam reviews, Palia (454 most-helpful English reviews of the last year, searched for "cook") | https://store.steampowered.com/appreviews/2707930 | full |
| S11 | Palia wiki: Guide:Cake Party | https://palia.wiki.gg/wiki/Guide:Cake_Party | full |
| S12 | Forsaken Chronicles blog, "My First Ever Cake Party in Palia!" (2023-08-28) | https://forsakenchronicles.blogspot.com/2023/08/my-first-ever-cake-party-in-palia.html | full |
| S13 | Stardew Valley wiki: Cooking | https://stardewvalleywiki.com/Cooking | full |
| S14 | Stardew Valley wiki: Buffs | https://stardewvalleywiki.com/Buffs | full |
| S15 | Stardew Valley wiki: The Queen of Sauce | https://stardewvalleywiki.com/The_Queen_of_Sauce | full |
| S16 | Stardew Valley wiki: Cookout Kit | https://stardewvalleywiki.com/Cookout_Kit | full |
| S17 | Stardew Valley wiki: Desert Festival (the Chef) | https://stardewvalleywiki.com/Desert_Festival | section read |
| S18 | Stardew Valley wiki: Multiplayer | https://stardewvalleywiki.com/Multiplayer | searched for cooking |
| S19 | Steam discussion "Cooking makes no sense" (Stardew Valley, May 2024, 35 replies) | https://steamcommunity.com/app/413150/discussions/0/4363502064158315533/ | first page read |
| S20 | Stardew Valley forums, "Which mechanic do you detest the most in SDV?" (2020) | https://forums.stardewvalley.net/threads/which-mechanic-do-you-detest-the-most-in-sdv.407/ | cooking posts read |
| S21 | Screen Rant, "Why Cooking In Stardew Valley Should Have Its Own Leveling System" | https://screenrant.com/stardew-valley-new-cooking-leveling-system/ | full |
| S22 | Valheim wiki (Fandom, officially approved): Food | https://valheim.fandom.com/wiki/Food | full |
| S23 | Valheim wiki: Cooking Station | https://valheim.fandom.com/wiki/Cooking_station | full |
| S24 | Valheim wiki: Cauldron | https://valheim.fandom.com/wiki/Cauldron | full |
| S25 | Valheim wiki: Fermenter; Mead ketill | https://valheim.fandom.com/wiki/Fermenter , https://valheim.fandom.com/wiki/Mead_ketill | full |
| S26 | Valheim wiki: Stone Oven; Food Preparation Table; Bread dough; Barley flour | https://valheim.fandom.com/wiki/Stone_oven (+3) | full |
| S27 | Valheim wiki: Feast; Whole Roasted Meadow Boar | https://valheim.fandom.com/wiki/Feast | full |
| S28 | Steam reviews, Valheim (3,097 most-helpful English reviews of the last year, most from September 2026; 202 mention food or cooking) | https://store.steampowered.com/appreviews/892970 | searched |
| S29 | Zelda Wiki (Fandom): Cooking (Breath of the Wild rules, potency, duration, critical cook) | https://zelda.fandom.com/wiki/Cooking | full |
| S30 | Zelda Wiki (Fandom): Food (incl. "only the most prominent effect") | https://zelda.fandom.com/wiki/Food | searched sections |
| S31 | Zelda Wiki (Fandom): Dubious Food; Elixir; Portable Pot | https://zelda.fandom.com/wiki/Dubious_Food | full |
| S32 | Disney Dreamlight Valley Wiki (Fandom): Cooking | https://disneydreamlightvalley.fandom.com/wiki/Cooking | full |
| S33 | Disney Dreamlight Valley Wiki (Fandom): Meals | https://disneydreamlightvalley.fandom.com/wiki/Meals | intro read |
| S34 | Steam reviews, Disney Dreamlight Valley (216 most-helpful English reviews; 5 mention cooking) | https://store.steampowered.com/appreviews/1401590 | searched |
| S35 | Don't Starve Wiki (Fandom): Crock Pot | https://dontstarve.fandom.com/wiki/Crock_Pot | full |
| S36 | Don't Starve Wiki: Warly (Don't Starve Together); Portable Seasoning Station; Honey Crystals, Garlic Powder, Chili Flakes | https://dontstarve.fandom.com/wiki/Warly/Don%27t_Starve_Together | full |
| S37 | Don't Starve Wiki: Cookbook | https://dontstarve.fandom.com/wiki/Cookbook | full |
| S38 | Steam reviews, Don't Starve Together (437 most-helpful English reviews; 6 mention the crock pot, recipes or the wiki) | https://store.steampowered.com/appreviews/322330 | searched |
| S39 | Coral Island Wiki (Fandom): Cooking | https://coralisland.fandom.com/wiki/Cooking | full |
| S40 | Coral Island Wiki: Frying pan | https://coralisland.fandom.com/wiki/Frying_pan | read |
| S41 | Coral Island Wiki: Buffs | https://coralisland.fandom.com/wiki/Buffs | read |
| S42 | Steam reviews, Coral Island (177 most-helpful English reviews; 9 mention cooking) | https://store.steampowered.com/appreviews/1158160 | searched |
| S43 | Sun Haven Wiki (Fandom): Cooking | https://sun-haven.fandom.com/wiki/Cooking | full |
| S44 | Sun Haven Wiki: Food | https://sun-haven.fandom.com/wiki/Food | full |
| S45 | Fae Farm Wiki (Fandom): Cooking; Cooking Fire; Cooking Hearth; Food Prep Table; Cooking Recipes | https://faefarm.fandom.com/wiki/Cooking | full (short pages) |
| S46 | Rune Factory Wiki (Fandom): Cooking (RF4) | https://runefactory.fandom.com/wiki/Cooking_(RF4) | full |
| S47 | Story of Seasons Wiki (Fandom): Cooking (SoSFoMT) | https://storyofseasons.fandom.com/wiki/Cooking_(SoSFoMT) | full |
| S48 | Spiritfarer Wiki (Fandom): Kitchen | https://spiritfarer.fandom.com/wiki/Kitchen | full |
| S49 | Spiritfarer Wiki: Cooking | https://spiritfarer.fandom.com/wiki/Cooking | full |
| S50 | Graveyard Keeper Wiki (Fandom): Cooking | https://graveyardkeeper.fandom.com/wiki/Cooking | full |
| S51 | Graveyard Keeper Wiki: Dinner; Pumpkin soup; Burger | https://graveyardkeeper.fandom.com/wiki/Dinner | full |
| S52 | Steam reviews, Graveyard Keeper (422 most-helpful English reviews; 101 mention cooking, recipes or stars) | https://store.steampowered.com/appreviews/599140 | searched |
| S53 | Wikipedia: Overcooked | https://en.wikipedia.org/wiki/Overcooked | full |
| S54 | Phil Duncan (Ghost Town Games), "Game Design Deep Dive: Building truly cooperative play in Overcooked", Gamasutra/Game Developer, 2016-08-26 | https://www.gamedeveloper.com/design/game-design-deep-dive-building-truly-cooperative-play-in-i-overcooked-i- | full |
| S55 | Wikipedia: Cooking Mama | https://en.wikipedia.org/wiki/Cooking_Mama | full |
| S56 | Fae Farm Wiki: Co-op; Spiritfarer Wiki: Daffodil (co-op checks) | https://faefarm.fandom.com/wiki/Co-op , https://spiritfarer.fandom.com/wiki/Daffodil | full (short) |
| S57 | Core Keeper Wiki (Fandom): Cooking (incl. "Calculating effects") | https://corekeeper.fandom.com/wiki/Cooking | full |
| S58 | Wikipedia: Core Keeper (player count) | https://en.wikipedia.org/wiki/Core_Keeper | intro |
| S59 | Grounded Wiki (wiki.gg): Roasting Spit; Weevil Roast; Jerky Rack; Smoothie Station | https://grounded.wiki.gg/wiki/Roasting_Spit | full |
| S60 | Wikipedia: Grounded (video game) (dates, premise, four-player co-op, hunger and thirst) | https://en.wikipedia.org/wiki/Grounded_(video_game) | full |
| S61 | Genshin Impact Wiki (Fandom): Cooking | https://genshin-impact.fandom.com/wiki/Cooking | full |
| S62 | Genshin Impact Wiki: Food (buff groups, fullness) | https://genshin-impact.fandom.com/wiki/Food | sections |
| S63 | Monster Hunter World Wiki (Fextralife): BBQ Spit | https://monsterhunterworld.wiki.fextralife.com/BBQ+Spit | full |
| S64 | Monster Hunter Wiki (Fandom): MHWI: Canteen; Meat List (MHF2) | https://monsterhunter.fandom.com/wiki/MHWI:_Canteen | intro + rules |
| S65 | Pokémon Wiki (Fandom): Sandwich | https://pokemon.fandom.com/wiki/Sandwich | full |
| S66 | Serebii: Scarlet & Violet Picnic | https://www.serebii.net/scarletviolet/picnic.shtml | read |
| S67 | Terraria Wiki (wiki.gg): Food | https://terraria.wiki.gg/wiki/Food | intro |
| S68 | Terraria Wiki: Well Fed | https://terraria.wiki.gg/wiki/Well_Fed | full |
| S69 | Necesse Wiki: Food | https://necessewiki.com/Food | full |
| S70 | My Time at Sandrock Wiki (Fandom): Cooking | https://mytimeatsandrock.fandom.com/wiki/Cooking | full |
| S71 | My Time at Sandrock Wiki: Chef's Cooking Station | https://mytimeatsandrock.fandom.com/wiki/Chef%27s_Cooking_Station | read |
| S72 | Wikipedia: Potion Craft: Alchemist Simulator (incl. review quotes from PC Gamer, Rock Paper Shotgun, CBR) | https://en.wikipedia.org/wiki/Potion_Craft:_Alchemist_Simulator | full |
| S73 | Potion Craft Wiki (Fandom): Recipe Book; Potion Craft | https://potion-craft.fandom.com/wiki/Recipe_Book | full |
| S74 | Kingdom Come: Deliverance Wiki (Fandom): Alchemy | https://kingdomcomedeliverance.fandom.com/wiki/Alchemy | full |
| S75 | Kingdom Come: Deliverance Wiki: Autobrew | https://kingdomcomedeliverance.fandom.com/wiki/Autobrew | full |
| S76 | Dennis Foose (Krillbite Studio), "Deep Dive: Cooking up a palatable food prep experience in Fruitbus", Game Developer, 2024-06-04 | https://www.gamedeveloper.com/programming/deep-dive-cooking-in-fruitbus | full |
| S77 | Leonardo Ferreira, "The unrealized potential of cooking in games", Game Developer (blog), 2024-06-07 | https://www.gamedeveloper.com/design/the-unrealized-potential-of-cooking-in-games | full |
| S78 | "Strategy games like Against the Storm let us think about the bigger picture of cooking", Game Developer, 2024-06-03 | https://www.gamedeveloper.com/design/strategy-games-like-against-the-storm-let-us-think-about-the-bigger-picture-of-cooking | full |
| S79 | Steam discussion "Cooking" (Coral Island, June 2024) | https://steamcommunity.com/app/1158160/discussions/0/4337608846038911321/ | full |
| S80 | Steam discussions, Core Keeper: "Cooking Suggestion" (Aug 2025), "Cook book suggestion:" (Nov 2024), "Bigger Cooking pot?" (Jun 2025) | https://steamcommunity.com/app/1621690/discussions/0/599662086417694143/ (+2) | full |
| S81 | Steam discussions, Disney Dreamlight Valley: "Cooking" (Apr 2023), "cooking" (Oct 2022) | https://steamcommunity.com/app/1401590/discussions/0/5243919379694490353/ (+1) | full |
| S82 | Game Accessibility Guidelines, full list | https://gameaccessibilityguidelines.com/full-list/ | full |
| S83 | Steam store data for Valheim ("for 1-10 players") | https://store.steampowered.com/api/appdetails?appids=892970 | full |
| S84 | Valheim news, "Valheim 1.0 Has Arrived!" (September 2026) | https://www.valheimgame.com/news/valheim-1-0-has-arrived-/ | full |
| S85 | Steam reviews searched for cooking: Spiritfarer (141 reviews, 13 mention cooking), Sun Haven (153, 3), My Time at Sandrock (132, 3), Rune Factory 4 Special (43, 1), Story of Seasons: Friends of Mineral Town (49, 0), Fae Farm (57, 0) | https://store.steampowered.com/appreviews/972660 (and the others' app numbers) | searched |
| S86 | Steam store data (player modes and release dates) for Graveyard Keeper, Rune Factory 4 Special, Story of Seasons: Friends of Mineral Town, Disney Dreamlight Valley, Coral Island, Sun Haven, Necesse, My Time at Sandrock, Spiritfarer | https://store.steampowered.com/api/appdetails?appids=599140 (and the others) | full |
| S87 | Stardew Valley wiki: Luau (the potluck soup) | https://stardewvalleywiki.com/Luau | full |
| S88 | Palia patch notes, Build 0.169 (the developers' cooking and cake-party changes, with their reasons) | https://palia.wiki.gg/wiki/Patch_Notes/Build_0.169 | cooking section |
| S89 | Palia patch notes, Builds 0.165 to 0.207 and the betas, searched for cooking (known issues and fixes in 0.167, 0.170, 0.177, 0.181, 0.200, 0.202 to 0.204) | https://palia.wiki.gg/wiki/Patch_Notes | searched |

Also read but not relied on: two Palia guide sites (farminggames.help and playpaliaguide.com) whose figures could not be
checked and which read as machine-written; the GDC Vault page for the 2024 Palia talk "It Takes a Village: Cultivating
Social Coziness in 'Palia'" (only the abstract is public).

---

## Part 3. Routes for Bug Farmer's cooking

Five routes, each a complete answer to "how does cooking play?". Dish names are from the current food list (item
table, 2026-10-01). Every route keeps the rules at the top of this page: one meal at a time, Health and Stamina raised
more by better food, one boost per dish, length set by effort, the campfire / stove / range / keg / press / mill, and
bugs cooked as they are.

**Scores** are 1 to 5, higher is better, on five axes: *fun and feel* (how good the moment of cooking is, judged from
what players praise and complain about), *depth* (whether it stays interesting over a long game), *readability* (can a
new player follow it without a wiki), *fit* (with the rules above, including multiplayer and bugs as ingredients), and
*build cost*, where **5 means cheapest** (judged against the crafting engine the game already has).

### Route A: Straight recipes ("cook from the book"), as in Stardew Valley

**How it plays.** Open the campfire or stove, see the dishes you know (unknown ones as dark shapes), pick one, choose
how many, press Cook. Ingredients come from your bag (and, ideally, nearby chests). The station works through the job
on its lanes while you do something else (one at the campfire, two on the wood stove, several on the range); you
collect the dishes later. Example: queue four Fly Soups on the stove, go fishing, come back and collect.

**Better food.** Only by choosing a better dish: campfire food raises Health and Stamina least, stove dishes more, big
stove dishes and bakes most. Length already follows effort. If the ranching design adds "prime" bugs later, a prime
fly could make a better roast fly.

**Learning.** Townspeople teach, shops sell, notes are found in the zones.

**With others.** Shared stations, gifts, dishes with several portions. No cooking together as such.

**Time per dish.** A few clicks; the job runs on its own.

**For.** It is exactly what the crafting engine already does (recipes, lanes, a timer, an output grid), so it is the
cheapest and clearest route, and every other route needs it as its fast path. **Against.** It is the system players
call shallow in Stardew: the player's effort never changes the dish, and most dishes end up unused (S19 to S21).
Cooking stays "recipe in, dish out", with nothing to play.

Scores: fun 2, depth 2, readability 5, fit 4, build cost 5.
**Keep as the foundation (the fast path inside the chosen route), reject as the whole answer.**

### Route B: Prepared ingredients at stations ("kitchen sessions"), as in Palia

**How it plays.** A dish is a short chain across stations. Fly Soup: clean the fly and chop the carrot and cabbage at a
prep counter (a rhythm chop each), then simmer at the stove (a stir that fills a meter), then ladle into bowls. Bread:
grind at the mill, knead dough at the counter (a rolling press), prove it, then bake in the oven (take it out before
it burns). Each step makes a half-made ingredient. Without Palia's countdown, a dish could be left half-done safely.

**Better food.** The average of how well each step went (as Cooking Mama grades a dish), plus prime ingredients later.

**Learning.** As Route A.

**With others.** The best of any route: friends split the steps and work at once, and a beginner can take a step that
needs no ingredients, as Palia's oven role does (S12). Bug Farmer should share portions rather than give every helper a
full copy, which in Palia multiplied money in a shared economy (S11, S12, S88).

**Time per dish.** Palia's kitchen dishes run 3 to 5 minutes each (S3, S4); a Bug Farmer version would be 1 to 3
minutes alone.

**For.** Real social cooking, a strong "I cooked this" feeling. **Against.** A player who wants the meal bonus all the
time eats every 5 to 20 minutes, and solo players already call Palia's cooking repetitive (S10); it goes against the accepted rule that
processing is one simple step per station with no realistic sub-steps (P11); it needs a prep counter, many half-made
items (art and data for each) and five minigames; lag can spoil timed steps (S10). Bug Farmer already has the light
form of this idea: flour, cornmeal, tortillas, sourdough starter, fish sauce, seed oil and grub fat are each made in
one step at another station (item table, 2026-10-01).

Scores: fun 3 (solo 2, together 5), depth 3, readability 2, fit 2, build cost 1.
**Reject as the everyday route; keep its group step-sharing for a rare, special dish (the feast in Route D).**

### Route C: Free-form combining with discovery ("the open pot"), as in Dreamlight Valley, Zelda and Don't Starve

**How it plays.** No recipe is needed to try. Put a dead fly on the campfire spit and you make a roast fly; put a fly,
a carrot and a cabbage in the stove pot and you make fly soup. The game reads each ingredient's *group* (bug, fish,
fruit, vegetable, grain or flour, fat, egg, seasoning) and matches the set against the dishes, as Don't Starve's food
values (S35) and Dreamlight's "any vegetable" slots (S32) do. A match makes that dish and writes it in your cookbook;
from then on the book can autofill and batch it. A mix that matches nothing makes a plain, honest dish named by its
method ("a simple stew", "a campfire roast"), weak but edible, never wasted.

**Better food.** From what goes in: more main ingredients and stronger ones raise Health and Stamina more (Dreamlight's
richer ingredients make a richer dish, S32; Core Keeper's golden crops make rare dishes, S57). The boost follows Zelda's
rule: the dish takes the boost its ingredients carry most of, and mixed boosts cancel into a plain dish (S30).

**Learning.** By trying, helped by hints: a townsperson describes a dish ("my gran stewed flies with carrots and
cabbage"), recipe notes found in the zones show the ingredients, and a cook in the village reacts to what is in the
pot, like Remy (S32).

**With others.** A shared pot: several players can add to one dish, which then makes portions for each (Pokémon's
sandwiches are built together, S65). It must not be judged by its worst ingredient, as Stardew's festival soup is
(S87).

**Time per dish.** Seconds once known; experiments take a little longer.

**For.** Discovery is praised wherever it was found (Zelda by the press, S21; Don't Starve by its players, S38), and
Bug Farmer's data already has ingredient groups. **Against.** Hidden rules send players to wikis and mods (S38, S80) unless the game
shows each ingredient's group and boost and records every attempt; a free mix sits awkwardly with a curated list of
real dishes with nothing silly among them (D74), so the fallback must stay plain; the effort the player makes still doesn't change
how *well* a dish is cooked.

Scores: fun 4, depth 4, readability 3, fit 3, build cost 3.
**Keep its discovery and cookbook inside Route D; reject as the whole answer, because quality stays purely a matter of
ingredients and hidden rules are a known trap.**

### Route D: Learn it by hand, cook it from the book, feast together (a hybrid)

Built from Coral Island's two ways to cook (S39), Genshin's mastery and auto-cook (S61), Monster Hunter's spit (S63),
Valheim's and Spiritfarer's "don't let it burn" stations (S23, S48), Dreamlight's open pot and autofill (S32), and
Valheim's feast (S27).

**How it plays.**
1. **By hand, one dish at a time.** At a station you put the ingredients in yourself, open-pot style (Route C): the pot
   shows exactly what is in it, and a cook or a hint tells you if it now makes a dish. Then you do *one* short action
   that suits the station, a few seconds long:
   - **Campfire spit, skewer or coals:** the whole fly turns over the fire, its skin going from pale to golden to dark,
     with a sizzle that changes as it cooks; lift it when it is golden (Monster Hunter's spit, S63; Grounded's visible
     doneness, S59). Food dried or smoked for the trail is a walk-away job instead.
   - **Stove pot or pan:** bring it to a simmer and take it off the heat in the right band (Genshin's single timing
     stop, S61).
   - **Oven (the wood stove bakes):** walk away; a ding follows you when it is ready; take it out in the window
     (Spiritfarer, S48; Valheim's oven, S26).
   - **Keg, press, mill:** no action; they take time only.

   The result is graded: **well done**, or **fair** if you were early or late. Nothing is ruined, and quitting gives
   the ingredients back (Genshin, S61; unlike Palia and Sandrock). Cooking a new dish by hand teaches it, as in Coral
   Island (S39).
2. **From the book, in batches.** Every dish you know (taught, bought, found or discovered) can be queued on the
   station's lanes and left to cook while you are away: the engine that exists today. Batches come out *fair*; after a
   few well-done cooks by hand, that dish's batches come out *well done* (Genshin's proficiency, S61; Kingdom Come's
   auto-brew, S75). The hands-on step is how you learn and master a dish, not a tax on every meal.
3. **Feasts, together.** A few big dishes are feasts: they need three or four finished dishes from different stations
   (for example a roast fly from the spit, a bread from the oven, a pumpkin soup from the pot and juice from the press)
   brought together at a table. The result is a platter with a fixed number of servings that anyone can eat, each
   serving counting as that player's one meal (Valheim, S27). Friends can cook the parts at the same time, Palia-style,
   and a newcomer can take the simplest part with ingredients the host hands them; or one player can make the parts
   over a day, since food doesn't spoil.

**Better food: a ladder the player can see.**
- *What you cook*: campfire food < stove dishes < big stove dishes and bakes < feasts. This sets how far the meal
  raises Health and Stamina; length already follows effort.
- *How well you cook it*: well done gives the dish's full raise; fair gives one step less.
- *What you put in* (later): if the ranching design adds "prime" bugs (D76), a prime fly lifts its dish one step.
- The dish's name and tooltip show its grade and exactly what it does (the dots it adds, its boost, its minutes):
  no hidden numbers, no luck.

**Learning.** Taught by townspeople (each with a line that hints how it is cooked), sold, found as notes in the zones,
or discovered by hand. The cookbook records every dish and every attempt, with favourites.

**With others.** Shared village stations (each player's jobs and finished dishes must stay that player's: see Part 4),
gifts, dishes with several portions, and feasts as the moment of cooking together.

**Time per dish.** By hand: about 10 seconds of attention. From the book: none. A feast: 5 to 10 minutes with friends.

**For.** Every complaint found has an answer: effort changes the dish (Stardew, Coral Island), the routine meal costs
nothing (Palia, Graveyard Keeper, Dreamlight), nothing is lost to a slip or lag (Palia), the rules are visible (Don't
Starve, Core Keeper), and there is a real reason to cook together without copying food (Palia). It keeps P11's one step
per station, and the spit puts the game's premise on screen: a cat-sized fly roasting whole. **Against.** It is the
most work after Route B: a hand-cooking panel for three kinds of station, a grade and mastery record per player and
dish, the matching rules, a cookbook, and the feast platter. Two grades split stacks of the same dish in the bag
(Stardew's quality stars do the same), which is why the grades should stay at two. A timing action must have an
assist (S82).

Scores: fun 4, depth 4, readability 4, fit 5, build cost 2.
**Keep: the recommended route** (Part 4).

### Route E: A base dish plus a seasoning that picks the boost, as in Don't Starve Together and Grounded

**How it plays.** Recipes make *base dishes* that set how much Health and Stamina a meal raises and how long it lasts
(a fly soup, a cornbread, a roast fly). When you cook, you may add one seasoning, and the seasoning chooses the boost:
for example thyme for toughness, sage for stamina, mint for mining, fish sauce for fishing, a honey glaze for walking
speed (an illustration only, not a proposal for which seasoning does what). This is how Warly's seasonings work (S36) and how Grounded's smoothie *bases* change a drink's strength while the
recipe sets its effect (S59).

**Better food.** By the base dish (tier); the seasoning only steers.

**Learning, with others, time.** As Route A.

**For.** Few recipes cover all eight boosts at every tier; players choose the boost they want for the next job; the
herbs the item pass kept for cooking get a clear role. **Against.** Dishes lose their identity (a fly soup could be any
boost), the current list assigns one boost to each dish (item table), and it adds a choice to every cook. It is a good
late extension (a spice rack), not a route on its own.

Scores: fun 3, depth 3, readability 4, fit 3, build cost 4.
**Reject as the main route; keep as a possible late addition.**

### Scores side by side

Weights for the weighted total: fun x2, depth x2, readability x1, fit x2, build cost x1. Fun and depth count double
because the question is how cooking should *play*; fit counts double because the rules are settled; build cost counts
once because the project's aim is to build the good version once rather than a cheap one twice.

| Route | Fun | Depth | Readability | Fit | Build cost (5 = cheapest) | Plain total | Weighted total |
|---|---|---|---|---|---|---|---|
| A: straight recipes | 2 | 2 | 5 | 4 | 5 | 18 | 26 |
| B: prepared ingredients (Palia) | 3 | 3 | 2 | 2 | 1 | 11 | 19 |
| C: open pot, discovery | 4 | 4 | 3 | 3 | 3 | 17 | 28 |
| **D: learn by hand, book, feasts** | **4** | **4** | **4** | **5** | **2** | **19** | **32** |
| E: base plus seasoning | 3 | 3 | 4 | 3 | 4 | 17 | 26 |

**Applies to every route: cook for someone.** Whatever route is chosen, dishes should matter beyond the eater's own
meters: townspeople with favourite dishes (Spiritfarer's passengers, S49; *Order Up!*'s customers who want food
overdone or raw, S77), orders and gifts, and food as an input to other things (Against the Storm, S78). Stardew's
lesson is that dishes nobody needs go uncooked (S19).

---

## Part 4. The pick: Route D, and what a great version of it needs

**Pick: Route D, "learn it by hand, cook it from the book, feast together".** It answers more of the recurring
complaints found in Part 1 than any other route while keeping the settled rules: the player's effort changes the dish; routine
meals cost no attention; nothing is lost to a slip; the rules are visible; and there is a real reason to cook with
friends that doesn't copy food into a shared economy. It grows out of the engine the game already has (Route A is its
first phase) and keeps P11's one step per station. Route C was the close second: it has the discovery but not the
craft of cooking well, and its hidden-rule trap is well documented.

### What a great version needs

1. **A quality ladder the player can see.** Three things raise a meal, one step each, shown on the dish: *what* you cook
   (campfire < stove < big dish or bake < feast), *how well* you cook it (well done or fair), and later *what goes in*
   (prime bugs, if ranching adds them, D76). Each step raises Health and Stamina a little more; length keeps following effort, as the food rows propose (still waiting for the owner's marks). No random quality (Palia's unexplained stars annoy players, S9; Zelda's critical cooks are
   luck, S29). The tooltip states the dots, the boost and the minutes.
2. **One short hands-on action per dish, only while learning.** About 5 to 10 seconds, one press, never a hold or button
   mashing (S82), never a countdown across stations (Palia's ruin-by-lag, S10). A miss gives a fair dish, not a ruined
   one; quitting returns the ingredients (Genshin, S61). After a few well-done cooks the dish batches at well done, so
   the action is never a permanent tax (Genshin, S61; Kingdom Come, S75).
3. **A fast path for every known dish.** The book with autofill (Dreamlight, S32), ingredients drawn from the bag and
   nearby chests (Stardew's fridge, S13), batches on the station's lanes, a ding when done (Spiritfarer, S48), and batch
   cooking that quality never switches off (Graveyard Keeper's complaint, S52). Several portions per cook for big
   dishes (Coral Island, S39) and the Oven Mitts' extra portion (item table) keep a 5 to 20 minute meal rhythm easy.
4. **Discovery that never strands anyone.** Each ingredient's tooltip shows its group and the boost it leans to (Core
   Keeper's players ask for exactly this, S80); the pot shows its contents (Overcooked, S54); a village cook or hint
   reacts as you add things (Dreamlight's Remy, S32); the cookbook records every attempt, with favourites (Don't Starve
   Together, S37; Core Keeper, S80); a mix that matches nothing makes a plain real dish, never nothing (unlike Sandrock,
   S70) and never a joke dish (D74). Recipes taught by townspeople should arrive when their ingredients are in reach
   (Stardew's out-of-season recipes, S19).
5. **Cooking together, without copies.**
   - **Each player's jobs stay theirs at shared stations.** Today a station's lanes and finished items are not tied to
     anyone: a lane records only its recipe, queue and progress, and collecting takes any item from the station's one
     output grid (`CraftProcessor` and `craftCollectOne` in `nakama/modules/world/craft_stations.go`). A campfire with
     one lane can also serve only one player's job at a time. If the village keeps shared cooking stations, as it does
     its other basic stations (D55), a dish should belong to the player who cooked it until they collect it or give it
     away, and those stations may need a lane per player.
   - **Feasts as the set piece**: three or four parts from different stations, assembled at a table into a platter with
     a fixed number of servings (Valheim, S27); parts cooked at the same time by different players (Overcooked's lesson:
     waiting is the reason to share work, S54); a part simple enough for a newcomer (Palia's oven role, S12). Everyone
     who eats gets one serving; nobody gets a full copy (Palia's duplication, S11, S12, S88). A feast's quality should
     build up from its parts, never fall to its worst one: Stardew's festival soup is judged by the worst ingredient,
     so one player can spoil it for everyone (S87).
   - Giving food (D50) and dishes with several portions cover everything else.
6. **A bonus that is welcome, not required.** Valheim shows what happens when food is the only way to have a usable
   health bar: "Food becomes another job" (S28). Bug Farmer's base Health and Stamina should be fine for normal play; a
   meal is a clear, steady bonus with a visible timer that doesn't fade in strength (S28).
7. **Picture the moment, and make it sound right.** The spit turning a whole cat-sized fly over the fire, skin going
   golden, the sizzle changing; a stew bubbling; a crust browning in the oven. Potion Craft's reviews single out its
   sounds ("the crunch of a root as you crush it into powder", S72). Hollywood cooking, not simulation (Fruitbus, S76).
8. **A simple data model.** Following Fruitbus (S76): stations are *appliances* that run a process on their own once
   started (roast, simmer, fry, bake, ferment, press, grind); the hand action is the one *tool* moment; a recipe is a
   short sentence of processes over ingredient groups. Per player, the game stores which dishes are known and how many
   well-done cooks each has. Cooking stays on the crafting side, outside the bug simulation's shared state
   (`architecture_crafting.md`).
9. **Accessibility from the start.** An option that makes the hand action succeed automatically (or widens its
   window), with both a sound and a colour cue (S82).
10. **Fairness and trust.** The settled rule that everything in the shared world runs the same for every player, with
    nothing going faster for one player than another (D58), reads as being about the world running at one speed: a
    well-done dish is better, not faster, and batches run at the same speed for everyone. The
    hand action happens on the player's own screen and its grade is sent to the server like any other input; it only
    affects that player's own dish, so trusting it is low-risk.
11. **Art that the code can carry.** Each bug that can be roasted needs a sprite on the spit; doneness can be a colour
    shift drawn in code rather than three paintings. A feast needs a platter that empties in a few stages (Valheim's
    shows three, S27). Every dish needs an icon in any route.
12. **Build it in three playable phases.** (1) Meals and book cooking: the meal effect (one meal, Health and Stamina,
    one boost, timer), cooking recipes on the existing engine, ingredient groups, recipe learning, per-player jobs at
    shared stations. This is Route A and every route needs it. (2) Cooking by hand: the station actions, grades,
    mastery, discovery and the cookbook. (3) Feasts.

### How many steps before cooking gets tedious

These limits are my reading of the evidence, not measured thresholds:

| Kind of cooking | Hands-on steps | Attention | Evidence |
|---|---|---|---|
| Routine meal of a known dish | None: queue a batch, collect later | A few clicks | Genshin's auto-cook (S61); Graveyard Keeper's one-at-a-time complaint (S52); Dreamlight players mashing through animations (S81) |
| Learning or perfecting a dish | One action | 5 to 10 seconds | Cooking Mama's steps under 10 seconds (S55); Coral Island's single press called pointless only when it changed nothing (S79) |
| A big dish (bread, pie, three-main stew) | At most two stations, one of them a walk-away oven or keg | Under about 30 seconds | Palia's 3 to 5 minute kitchen dishes called repetitive alone (S3, S10); Valheim's oven windows (S26) |
| A feast with friends | Three or four parts at different stations | 5 to 10 minutes, shared | Palia's cake parties enjoyed as a social event (S12); Valheim's 10-serving feasts (S27) |

### Questions for the designer (taste calls; the research can't settle them)

1. Should how well a dish is cooked change how much it raises Health and Stamina?
   (a) yes, one step, as proposed; (b) only how long it lasts; (c) no, cooking well only teaches the dish.
2. After a dish is mastered, should batches come out at the top grade?
   (a) yes, as proposed, so the hands-on step is never a tax; (b) no, the best food is always hand-made.
3. How many dishes can be found by experiment?
   (a) all; (b) the simple ones, with the rest taught or found; (c) none, recipes only.
4. When a mix matches no dish:
   (a) a plain dish named by its method, as proposed; (b) nothing is cooked and the ingredients come back.
5. Should a feast carry one boost (whose?) or a bigger Health and Stamina raise and no boost?
6. The spit: (a) lift it at the right moment, Monster Hunter style; (b) a walk-away window, Valheim style; (c) both,
   the first when you stay, the second when you leave it.

---

## Part 5. Claims I could not verify

These are left open or stated with a caveat above; none of them is load-bearing for the pick.

1. **How Palia decides a star-quality dish.** The wiki says only that star ingredients give more Focus (S5); players
   disagree (S9). A Reddit search result, which could not be opened, says minigame accuracy and the group's average
   skill also count.
2. **Whether Palia's cake parties are still common today.** The developers' own reason for cutting dish prices was
   found (S88), but the sources on the parties themselves date from 2023 and 2024.
3. **Whether Tears of the Kingdom saves cooked recipes** for quick re-cooking. The Zelda wikis that would cover it
   could not be reached.
4. **Valheim details:** the exact rule that unlocks each food recipe; how long meat can sit on the spit before it
   burns; and whether the 1.0 release (September 2026, S84) changed any food values (the fan wiki may be older).
5. **Disney Dreamlight Valley:** the pot's maximum number of ingredients; and players' wider view of its cooking (few
   Steam reviews mention it, and Reddit could not be reached).
6. **Pokémon Scarlet and Violet:** how several players' fillings combine in one shared sandwich, and how a sandwich's
   strength is worked out.
7. **Kingdom Come:** whether the auto-brew perk belongs to the first game, the second, or both.
8. **Graveyard Keeper:** the quality rule for most dishes; only the dinner's rule was found (S51).
9. **Coral Island:** whether its cooking minigame affects quality (players say it does not, S79; the wiki is silent).
10. **Monster Hunter: World's spit:** the guide quotes the in-game hint about timing and listening (S63); the exact
    length of the tune and the size of the "well-done" window were not checked.
11. **Genshin Impact:** whether co-op players can cook together; the wiki describes only solo cooking.
12. **Necesse and Sun Haven:** Necesse's boost lengths beyond the examples read; which of Sun Haven's seven stats
    each dish raises.
13. **Against the Storm:** the article draws on its designer's 2024 conference talk, which was not watched (S78). The
    2024 Palia talk was likewise known only from its summary.
14. **Release years and player counts** that could not be checked were left out rather than guessed.
15. **Player opinion samples are small and recent**: Steam's most-helpful reviews from the last year only (for
    example 216 for Dreamlight Valley, 177 for Coral Island), searched by keyword. Reddit, the largest source of
    player opinion on these games, could not be read at all.
16. **My route scores and the Route D design are judgment**, built on the evidence above but not tested in play. The
    weighted totals depend on the weights stated in Part 3.

Status: COMPLETE (research, 2026-10-02). Research only; nothing here is decided.
