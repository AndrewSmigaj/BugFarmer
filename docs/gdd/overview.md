# §OV · The game as the documents describe it
<!-- gdd: id=OV status=review updated=2026-09-26 -->

Before redoing the design document, every design document in the repo was read in full — about 240 files: the
December 2025 requirements, the January 2026 design document, the brainstorms, the economy and zone designs, the
architecture documents, the roadmap, backlog and changelog, the authoring and art guides, and the investigations.
Five readers each took a share and wrote notes with file and line references; I read all of their notes and checked
the claims that matter against the documents and the game's own code and data; then two separate reviews checked
this overview against the notes and the code. (The 63 raw research notes behind the July research were searched for
decisions rather than read line by line.)

This is the whole game as those documents describe it, in my own words, organised by what the player does. For each
activity it says what has been **decided** (and when), what is **built** in the game today, what is **designed but
not built**, and what is **still open**, with the section where each open point will come to you. "D" numbers (D1 to
D31) are entries in the decision log of June and July 2026 (`docs/product/economy/DECISIONS.md`); a few of its
entries mix the owner's rulings with my own defaults, and where that matters I say which.

Please correct anything I got wrong or left out. The sections are rebuilt from this once you have checked it.

## The experience
It is 2126. A plague killed nearly every mammal, and people bred bugs big enough to eat. The player starts over on
the frontier as a bug farmer.

Bug Farmer is a top-down multiplayer sandbox in the spirit of Terraria and Stardew Valley. The player **catches,
breeds and sells bugs**; **grows crops and fruit trees**; **digs and mines** into rock for ore; **crafts** tools,
gear, furniture and materials at stations; **builds** pens, fences and a home; **fights** the bugs that bite back;
**trades** with the town's shopkeepers; and **explores** outward — north and east across the surface and down
underground — where the bugs get bigger and the rewards richer.

Under all of it runs a living ecosystem. Fruit falls and rots, flies breed on it, wasps hunt the flies, and every
bug eats, breeds, ages and dies — and every player sees the same bugs doing the same things. Bugs are the livestock:
some make a product at a station (bees make honey), the rest are sold as meat. The food chain is the progression —
to keep bigger bugs, the player farms the smaller ones they eat.

There is no storyline. Progress comes from better tools and gear, from knowledge and from preparation, and the harder
places are gated by what it costs to survive them. With friends it becomes a shared frontier: the wild is lawless,
and a private plot is safe.

## Decided
The frame the rest of the design sits inside. Each line is the owner's decision in my words, with its date, unless
it names another source.
- **The premise** (the game's opening text, in the game since June 2026): the year 2126; a plague killed nearly
  every mammal; people bred bugs bigger to have food; the player starts over on the frontier as a bug farmer.
- **The bugs are giant**, and their size stays as designed (2026-09-26).
- **Every creature is a real species** with real behaviour (2026-07-11); **no frogs** (D31, July 2026). New species
  are welcome as long as each is explained, keeps the balance, and doesn't need a whole new zone (2026-09-26).
- **No storyline; the player sets their own goals.** Progress comes from gear and preparation and is gated by cost;
  tutorials unlock as the player goes, and the Ecology tab has its own small tasks (2026-09-26).
- **The food chain is the progression**, and bugs are livestock — sold as meat or kept for their product
  (the ecology plan; confirmed in the roadmap, 2026-09-26).
- **No rule is forced on every zone** (2026-09-26).
- **A lawless shared world and a safe private plot.** Private plots come from City Hall; out in the world anything
  goes, except that the townspeople's property is protected (2026-09-26).
- **Everything in the world persists**, as in Terraria (D31, July 2026).
- **Examining an item or a recipe shows what it does and the real biology behind it** (2026-09-26).
- **Curiosity and surprise** are priorities (2026-09-26).
- **Combat matters and defence is critical**; each role has its own best gear (2026-08-06). Starter zones stay
  cosy, dodging is the only defensive move, and nights are more dangerous (2026-07-11).
- **Gear is about roles and trips**: an outfit is chosen per expedition, and no single set is best at everything
  (2026-08-06).
- **Potions are ordinary items, not magic**, and one player can hand another a potion (2026-08-06).
- **The world is a grid of zones** — surface to the north, underground to the south, danger rising with distance;
  five rows, with a sixth, deepest row left for later (D2, June 2026).
- **Hosting works like Terraria** — host and play, join a friend, or run a dedicated server — and each world keeps
  its own characters, as in Necesse (2026-09-26).
- **Empty zones stay frozen** and catch up when a player first returns (2026-09-26).
- **All art is made with gpt-image-2 and pixel-snapped**, 32 art pixels to a grid square, and regenerated after this
  document is signed off, in test batches (2026-09-26).
- From the January 2026 design document: **no stamina**, **no disasters on a timer and no forced invasions**,
  **nothing on a player's private plot is lost while they are away**, and **machines ease chores but never play for
  the player**.

## The game, activity by activity

### 0 · What belongs in the world
The premise draws the line: bugs, the plants they live on, and people. Everything else has to earn its place.

**Decided** — the premise, giant bugs, real species only, no frogs, and new species welcome on the three conditions
above (see the frame).

**Built today** — the opening text plays before the title screen. A few things in the game data don't fit the
premise: a cow skull, a cat statue, a hay bale, a birdbath, and bones and bone piles.

**Designed, not built** — more of the same in the old idea lists: cave bats and bat guano, milk and cheese, horseshoes,
livestock and manure, a rabbit's-foot charm, a pack mule.

**Still open** (→ §00) — which animals besides bugs survive (birds? fish — fishing implies them?); what becomes of the
mammal-era things; the December 2025 idea of meteors bringing an infection that turns bugs into "zombie bugs", which
nothing written since mentions; how the game should feel.

### 1 · Catching and farming bugs — the heart of the game
Any bug can be farmed if it can be held. The player catches bugs with a net sized to the bug — most need calming or
weakening first — keeps them in pens built from fences and walls, breeds them at nurseries and host plants, and
harvests either the bug itself (sold as meat) or its product at a station: honey from bees today; silk, honeydew,
venom and more on paper. The food chain is the ladder: flies first, fed by the fruit that falls and rots under fruit
trees and by compost; then wasps, kept alive on a surplus of flies; then bigger and rarer bugs. The first automatic
catcher is the **autonet** — slow, and it stops when full; other slow catchers in the same spirit are allowed, and
the owner has named automatic catchers and bug zappers for the powered age.

**Decided**
- Killing a bug drops only its carcass (D18). The owner's bug map (2026-06-28): carcasses of beetles, centipedes,
  millipedes and wasps give chitin; flies and butterflies give leather; ants give formic acid (2026-07-07). (The game
  also makes chitin from ants.)
- **Calming is one general system** — most bugs can be calmed (D31, the owner's correction).
- The flies breeding in a compost bin keep their pupa stage (2026-07-17).

**Built today**
- Nets: bare hands and the small net take small bugs (flies, butterflies, beetles, millipedes, ants, bees,
  fireflies). Wasps, hornets and dragonflies need the large net — **which no shop sells and no recipe makes**, so in
  normal play they can't be caught. **Centipedes can't be caught at all**: they are marked for traps, and no trap
  exists.
- Calming: smoke or calm spray raises a bug's calm, and one threshold decides both whether it attacks and whether it
  can be caught; bees must be calmed first. Caught bugs go into their own 20-slot bag; dropping them back into the
  world joins a nearby swarm or starts a new one.
- Pens: fences, walls and gates hold walking bugs **and wasps and hornets** (the owner had wasps flying over fences
  corrected in June 2026); bees, dragonflies and fireflies fly over them. Centipedes chew through wooden fences;
  stone holds them.
- Breeding is visible: eggs, larvae and pupae develop over about a game hour, two young per hatch. The compost bin,
  milkweed, wasp nest and beehive all open one panel, where the player can take eggs, larvae and pupae out as items
  or put them back.
- The compost bin turns scraps into sellable compost while flies breed inside it. Carcasses feed the beetles, the
  beetles make compost, and compost feeds the flies — a closed loop.
- Beekeeping works end to end at Maren's farm in the Bee Meadow: bees come only from hives (wild ones, or hive boxes
  a wild colony moves into), and each honeycomb becomes honey or beeswax, the player's choice (D31 — written into the
  decision log as my choice, not as the owner's ruling). The four beehives in the rebuilt village never come alive —
  no bee colony lives there.
- The Bug Dealer buys live bugs at each species' price (1 to 75 coins) and carcasses for a coin each. A new player's
  first coins come from selling a caught bug.
- The Bug Extractor, which turns carcasses into those materials, stands only in a test zone, so in normal play
  carcasses can only be sold or composted. The autonet exists as an object but doesn't catch anything yet.

**Designed, not built** — traps and bait; bug research with the magnifying glass; specimen collecting; keeping ants;
aphids farmed for honeydew; wasps used as pest control; roofed pens for flying bugs; NPC workers who mend fences and
calm escaped bugs (December 2025 and January 2026; since then only in a June 2026 idea list).

**Still open** (→ §05) — whether butterfly young stay on the milkweed through every stage (the backlog recorded that
as the owner's call on 2026-07-16; a design written three hours later says the caterpillar wanders off to pupate,
deferred); whether a caught bug sells for more alive or as meat; which bugs make which products; how strong each pen
material is (three different ladders on paper); whether NPC workers are still wanted.

### 2 · The bugs themselves
**Decided**
- Every bug family gets simpler and more advanced species — most have three, some two or one; wasps and hornets
  about two each; bees three, including a killer bee (owner direction, August 2026).
- Two ant species live in different zones — fire ants and black ants (August 2026).
- Real species with real behaviour (2026-07-11), so the invented names in the game — soldier wasp, giant hornet —
  are due a renaming pass; no frogs (D31); spiders live only in the lower underground (D21).

**Built today** — fifteen species: common fly, meadow butterfly, honeybee, wasp, soldier wasp, giant hornet, carrion
beetle, garden centipede, tiger centipede, giant centipede, millipede, worker ant, scout ant, firefly and blue
dragonfly. Flies flee, butterflies are curious, bees are gentle until provoked, wasps and hornets hunt and dive,
centipedes hunt in packs and lunge, fireflies glow at night and dragonflies hunt wasps.

**Designed, not built** — about 84 species across the seventeen zone sheets, with about a dozen mini-bosses; each
family with easy, medium and elite members; spiders and webs, scorpions, mosquitoes, moths, mayflies, cicadas,
glowworms and aphids among them.

**Still open** (→ §03) — the full list: which species, in which zones, in which order; how the two ant species fit
the designed ant rosters (the Deadly Ants' army, fire and bullet ants) and the worker and scout ants in the game.

### 3 · The living ecosystem and the Ecologist
Everything eats, breeds, ages and dies, and the player can see why numbers rise and fall and act on it — plant a host
plant, remove a predator, leave fruit to rot. Populations are held in a living balance by food, by predators that get
full, and by old age, with a hidden balancing system stepping in only at the extremes: it re-seeds a species that is
nearly gone, thins one that is exploding, and can even hold back the rain. The **Ecologist** is the one character who
explains the ecology and asks for help when something is really out of balance; the **magnifying glass** reveals what
a bug eats; an **Ecology tab** collects what the player has learned.

**Decided**
- Numbers should rise and fall around a target, limited by food, predators and age rather than hard caps (June–July
  2026).
- The living ecosystem is the heart of the game, and every player sees it the same way; the Ecologist and the Ecology
  tab let players read and steer it, and ecology stations open the tab area by area (the approved roadmap,
  2026-09-26). The tab has its own small tasks (2026-09-26).
- Every bug is its own creature, behaving the same on every player's screen (2026-07-13); the model is one wasp
  hunting one fly, killing it and eating the corpse — sometimes leaving it behind.

**Built today**
- The food web runs: flies breed on rotting fruit and compost; butterflies drink nectar and breed on milkweed; wasps
  hunt single flies and eat them; bees gather nectar; centipedes hunt; millipedes and beetles eat litter and
  carcasses.
- Natural death leaves carcasses; starvation thins a crowd; the balancing system re-seeds and thins, and can call a
  drought. Each zone also has a hard ceiling per species (1,500 flies in the rebuilt village, for example).
- **Not built:** the Ecology tab (only a developer graph exists), the Ecologist's tasks and the magnifying glass. The
  village Ecologist today sells six decoration recipes.

**Designed, not built** — crop pests (aphids, caterpillars, locusts) with ladybugs as the answer; pollination raising
yields; frozen zones catching up on the first visit.

**Still open** (→ §04) — what the Ecologist's tasks are and what they reward; whether a left-behind corpse feeds
other bugs; how far the per-bug model goes, part of the ecology or all of it (the owner's call). Seasons are asked
under 17, Time and weather.

### 4 · Farming and gardening
Crops in tilled plots, watered by hand or by rain; fruit trees whose fallen fruit feeds the flies; later
sprinklers, fertiliser from compost, pests and pollination. Farming is open from the start and limited only by what
materials cost.

**Decided**
- The village grows garden vegetables; **wheat is bought up north** — fast-growing and profitable, a reason to
  travel; cotton comes later; new crops arrive with new zones (D19, June 2026).
- One harvest rule for every plant: a harvest always gives the plant's resource and sometimes a seed, and plants
  regrow from seed (D24). Crops already work this way; flowers, bushes, trees and milkweed don't yet.
- A harvest gives a share of what is there; the rest is lost (August 2026).
- Fertiliser is deferred (July 2026).

**Built today**
- Hoe a plot, plant a seed, water it (a can holds 40 uses and refills at water). Crops grow with watering, at most
  twice a day, never wilt, and drop a seed now and then. Seven crops: tomato and eggplant give several harvests; corn,
  wheat, carrot, pumpkin and cabbage one. Rain waters everything on about three days in ten.
- Fruit trees — apple, orange, plum and cherry — fruit after three days of water; ripe fruit falls in the evening,
  rots in about two days into fly food, and vanishes after six days if nothing eats it. Fruit is picked up by hand.
- **Not built:** sprinklers, fertiliser, crop pests, pollination.

**Still open** (→ §06) — what fertiliser does (the January 2026 farming design says more yield, not faster growth);
how fallen fruit is collected by hitting it — the owner asked for that after the June playtest, and two ways to
build it wait for a pick; how many more crops, and where each first appears.

### 5 · Mining and the underground
A block world. The surface has dirt and stone to dig; the underground is solid rock the player carves through; ore
sits in veins that grow richer and rarer with depth; the dark needs light; and danger is meant to guard the best ore.

**Decided**
- **It is a block world**: a player facing sideways digs the block beside them, not the ground below (2026-08-04).
- **One kind of rock.** Depth shows in the floor and the ores, never in harder rock (D22).
- **Ore only in veins** of three to six blocks, never placed by hand — even rare ores — richer and rarer with depth
  (2026-07-06).
- **Dirt areas are diggable masses** of dirt blocks around stone and ore cores, never flat painted dirt
  (2026-07-06).
- **Underground is pitch dark**, as in Terraria, and a torch is needed (2026-07-08).
- Mining is a main loop, slow and exploratory (D13). Ore is refined in steps — crushed, washed, then smelted — the
  owner's choice over a shorter chain written into D26 (2026-06-28).

**Built today**
- Ore is gated by pickaxe: coal, copper and tin with a wooden pick, up to diamond with a steel one; tools come in
  eight tiers from wood to platinum.
- The recipes for six metals exist — crusher, sluice, furnace with coal, bar; tin goes into bronze; gem blocks drop
  rough gems for a gem cutter. **But the rock crusher and the gem cutter stand only in a test zone**, so in normal play
  mined ore can't be refined and gems can't be cut. The blacksmith sells copper, iron, bronze and steel bars; silver,
  gold and platinum bars can't be had at all, so the top three metal tiers are out of reach.
- Two underground zones: Underground Passages, the first mine, and the Ant Tunnels.
- Darkness: buried blocks go dark everywhere, but dark tunnels only work in a test zone so far.
- **Not built:** mining dangers (gas, cave-ins), drills, dynamite, carts and rails, prospecting — the backlog itself
  calls mining thin beyond the basics.

**Still open** (→ §14) — what mining's dangers are; how deep the tiers go; whether carrying capacity limits a trip
(the armour notes propose it; the game counts only bag slots); the first mine's name ("Mining Camp" in some
documents, "Underground Passages" in others) and its difficulty (easy in one, medium to hard in another).

### 6 · Crafting and processing
Stations turn materials into better ones over time: workbench, sawmill, furnace, forge, anvil, stonecutter, loom,
spinning wheel, sewing machine, dye vat, bug extractor, crusher, sluice, gem cutter and honey extractor. Materials
climb ladders — ore to bar to alloy, fibre to thread to cloth, log to plank. Some recipes are known from the start;
the rest are bought or found, and most of them gather in the two towns and the first mine.

**Decided**
- Basic recipes unlock by themselves at their station — every metal tier of tools, weapons and armour included —
  and tools are never locked behind a purchase; décor, furniture and advanced recipes are bought or found (D26).
- Stations are crafted or bought, occasionally found (D1). Cooking is its own system, separate from crafting (D19).
- Leather and a new "wood" armour rung come from processing bugs; players make clothes and a dyer dyes them (August
  2026).
- Making dyes and dyeing cloth are separate stations (2026-06-28) — not built: the dye vat still makes the dyes.

**Built today** — 185 recipes on 15 stations. 105 are known from the start; 80 are bought from shopkeepers, singly or
as recipe books, and each character remembers them. The slow stations run two jobs at once; ingredients leave the
bag when a job starts, and results collect in the station's output slots. Three of the fifteen stations — the rock
crusher, bug extractor and gem cutter — stand only in a test zone; twelve stand in the game, and eleven have
something to do (the sluice waits on the crusher).

**Not working** — the cooking stations (campfire, stove, cooking pot, cauldron, keg) have no recipes. Eleven of the
fifteen stations — the workbench, furnace, anvil, forge and sawmill among them — can't be crafted or bought,
although D1 says they can; the only way to own one is to break one where it stands and carry it off. (The Weaver's
four — loom, spinning wheel, sewing machine, dye vat — are made at the workbench from recipes she sells, and so are a
campfire, a wood stove and a keg.) The eight floral-furniture recipes can never be learned, because no one sells
their book; there are no bronze tools, though bronze weapons exist; the wooden spear, scythe and shovel, the large
net and the backpack can't be bought or made; and bookshelves and wine racks accept nothing.

**Still open** (→ §10) — how the player gets each station; what the rare recipes are and where they hide; whether
dyeing recolours cloth outfits (to be tried when clothing starts).

### 7 · Building, pens and homes
The player places blocks, floors, walls, fences, gates, doors, furniture and stations on the grid, and reshapes the
ground with a shovel. Pens are always built, never bought. A private plot, bought through City Hall, is the safe
home for calm, careful farming; decorations there give small production bonuses that shrink with every duplicate,
so variety pays. Bugs can't appear on floors, so paving keeps them away.

**Decided**
- Private plots from City Hall are safe and central to the design (2026-09-26).
- Bugs never appear on a floor (December 2025).
- No roofs — the view is from above (D19). Placed objects drop themselves when broken (D22).
- Furniture doesn't rotate (June 2026).
- Decorative outfits are approved as a class, adding to farm output or happiness the way furniture does; making them
  is on hold (2026-08-07).

**Built today** — about 280 placeable things, placed from the hotbar with a green or red preview; the shovel places
ground in thirteen shapes, and a tile made of two materials costs both; it also digs a cell down to bare soil (the
ground is never a hole). A bed sets where the player wakes; containers have filters (a wardrobe takes clothes, a
fridge food).

**Not built** — private plots, City Hall and land deeds; decoration bonuses; floors stopping bugs from appearing; a
limit on how far away a player can place things; items that hang on walls; doors that stop players; mannequins
showing the clothes put on them; sorting and quick-stacking in chests.

**Still open** (→ §15) — how a player builds a house (walls, doors, rooms), which no document designs; how big a plot
is, what it costs and who may enter; whether a player can live in the village (the village design says no; one
economy sheet says "build out your house").

### 8 · Combat and danger
Real-time fights against bugs, with health but no stamina, and power from gear and preparation rather than levels.
Starter zones are cosy; danger rises going north, east and deeper. Enemies warn before they strike and the player
dodges. Bosses grow out of populations that got out of hand — a bloated queen, a locust swarm — alongside designed
ones such as the Ant Colony's queen.

**Decided**
- Combat is important and defence is critical (2026-08-06); starter zones cosy, dodge only, more danger at night, and
  at most two bugs from one swarm striking at a time (2026-07-11).
- Venom and poison are real effects; gear should change a variety of things rather than lean too hard on venom (D16).
- Spider Vale is the hardest surface zone and the fire-ant domain the hardest underground; the swamp, the underground
  river and the lake are about equal (August 2026).
- The Ant Colony's queen is a mini-boss for the middle of the game (D3); a scripted, game-style encounter is
  acceptable (2026-07-06).

**Built today**
- Ten hearts. A sting takes one to three hearts, a centipede bite two to four. Every attack flashes and hisses 0.4 to
  0.9 seconds before it lands; a dodge dash gives half a second of safety.
- Sword and spear with two moves each, and an axe jab. Soldier wasps, giant hornets and tiger and giant centipedes
  are the tougher tiers. Wasp nests raid; centipedes hunt in packs.
- **Fainting costs nothing**: the player wakes at the zone's start point or their bed, at full health, with
  everything they carried.
- **Not built:** armour protection (armour is looks only, except the bee suit, which stops stings); night danger (no
  bug is marked as a night hunter yet); bosses; poison and other effects; bows and other ranged weapons (set aside for
  later, D12).

**Still open** (→ §07) — why the player fights and what fighting rewards; what an expedition risks, since fainting
costs nothing; which enemies come next (spiders, scorpions, warrior ants) and how bosses work.

### 9 · Gear: outfits, armour and accessories
An outfit is chosen for a trip, not swapped per action. Each gives defence plus one main bonus and one or two small
ones; each role — tank, attack, agility, stealth, mining, fishing, farming, bug-catching, beekeeping — has its own
best set, with a few hybrids. Legendary sets hide behind secrets; decorative outfits boost the farm. About 43 sets are
planned. (The armour notes also propose light as a role, and sets above steel as keys to a zone's hazard — acid,
venom, water, dark, heat.)

**Decided**
- Each role has its own best set; nothing is the best armour in the game (2026-08-06).
- Nearly every zone hides at least one outfit recipe, calling for materials partly new to that zone (2026-08-06).
- Outfits are drawn whole rather than as layered pieces — a tentative choice (2026-08-05, reaffirmed on 2026-09-26
  with some hesitation); four are finished and approved — bronze, fire-ant, black-ant and copper.
- Armour is made *of* a material and never a costume of the creature; faces show (August 2026).
- Crowns are kept for higher-value armour (2026-08-15). Trinkets and shields are not for now (August 2026).
  Decorative clothing is on hold (2026-08-07).

**Built today** — eight equipment slots (head, body, arms, legs, feet, two accessories, backpack). New characters
wear leather. Armour shows on other players but does nothing except the bee suit (stops stings) and a backpack (more
slots — though none can be had yet); the two accessories in the game, a bee charm and a lucky clover, do nothing.
None of the new outfit art is in the game yet: it still draws the old small layered farmer.

**Designed, not built** — about 88 accessories, set aside for later (D26); the stats that make gear matter (defence,
damage, stealth, light radius and the rest).

**Still open** (→ §08) — how outfits are equipped (one outfit slot, or pieces); how big the player is on screen; the
starting outfit; what becomes of the class, hair and skin choices; the armour ladder — the decision log (D11) lists
nine rungs (leather, padded cloth, copper, bronze, iron, steel, silver, gold, platinum), while the August armour
notes list six (leather, wood, copper, iron, steel, platinum), cutting bronze — one of the four approved outfits —
and silver; what the wizard's robe the owner asked for is (a set, a costume, or dropped).

### 10 · Tools and weapons
Metal tiers plus a few specials that matter (D12). Picks come in metal tiers only; watering cans small and large;
nets small and large; a saw for big trees; a harvest sickle; smokers in three tiers; fishing rods in tiers with fish
traps and no harpoons; **bugs are the light source** — firefly and glowworm lanterns replace oil lamps; the
magnifying glass from the start; a grappling hook later; a bug vacuum and a headlamp; bows and cast nets set aside.

**Built today** — pickaxe, axe, shovel and hoe in eight tiers from wood to platinum, the scythe in seven; saw and
harvest sickle; sword and spear in eight tiers; both nets; watering cans; torch; flashlight; smoker; calm spray; the
magnifying glass, which does nothing yet and isn't in the starting kit (the general store sells it). Durability
exists in the data but isn't used.

**Motions** — swings must feel natural: a shovel scoops, it isn't swung (2026-07-09). In the game every tool has a
basic motion — seven kinds, built in July 2026 — with two known flaws: a hard snap back to rest, and the tool drawing
through the body. For the new outfit art, the sword, axe, net, hoe and shovel have designed swings and only the sword
is approved in all three facings; the floating hand can vanish against same-coloured armour; **the pickaxe, the main
mining tool, has no swing yet**, and the spear's isn't agreed.

**Still open** (→ §09) — whether tools wear out; the bug lanterns, the grappling hook and the specials; the top of
the metal ladder (diamond is an ore but not a tool tier; the backlog plans deep metals).

### 11 · Food, cooking and potions
Meals are short boosts. Stoves grow from one dish at a time to several. Bug food is the signature branch — meat from
carcasses, honey, royal jelly. Potions heal, cure and coat weapons, and one player can hand another a potion; healing
a friend means holding the potion in the off hand.

**Decided** — cooking is its own system and was set aside for later (D19); potions and alchemy likewise, with venom
and poison staying real (D16); potions are not magic and can be given to other players (2026-08-06).

**Built today** — food items exist and sell, but eating does nothing. No meals exist (the planned starter stew isn't
in the game), the cooking stations have no recipes, and health comes back only by slowly regenerating.

**Designed** — about 78 potions and 47 meals in the economy catalogue; eating fruit to heal; fridges that stop food
rotting.

**Still open** (→ §11) — whether there is hunger: the economy catalogues say there isn't and credit the design
document, which only rules out stamina; what food and potions are for; how healing works.

### 12 · Fishing and water
A fishing mini-game with rod tiers and bug baits, fish traps as the slow option, and boats for getting around;
fishing arrives with the Underground River and its blind cave fish.

**Decided** — **no diving** in this game (August 2026); fishing outfits carry two bonuses, fishing and boat speed
(August 2026); rods in tiers with a mini-game, fish traps, no harpoons (D12); bugs fly over water (the owner's
playtest rule of 2026-06-11); water divides the map — waders for the marsh (D10) and deep water walling off islands
(the swamp design).

**Built today** — nothing to play. Docks and fishing props are decoration; the Fisherman (rods, nets, a boat for 400
coins) exists in the data but stands in no zone. Every water tile stops players, and bugs fly over water.

**Planned** — fishing arrives with the Underground River (the approved roadmap; it replaces D5, which in June 2026
kept fishing out of the first release — see P1). Also designed: a dredge set on the water and worked with a hose, in
tiers (D14).

**Still open** (→ §01 and §13) — whether players wade slowly through shallow water, as the older world design says,
or are stopped, as the game does now.

### 13 · Towns, shopkeepers and trade
A safe starting village full of shops; a second town — a small western-style town in the Locust Farmland — and the
first mine, where most recipes gather; one coin currency; the player starts with no money and earns the first coins
by selling a bug. Shopkeepers sell tools, seeds, recipes and recipe books; the Ecologist explains the ecology; the
Mayor sells land.

**Decided**
- One coin and no bartering (D6, D29).
- Which shops the village has (D20, D26), and what the village still needs: its townspeople and their behaviour,
  better buildings and layout, polish, and secrets (2026-09-26).
- The second town is a small western-style town in the Locust Farmland; the village windmill that powers its houses
  can only be bought or built after the player reaches it (2026-06-27).
- A myrmecologist — an ant specialist — sells from a wooden building at the Ant Tunnels' entrance (2026-07-07).

**Built today** — eight shopkeepers in the rebuilt village (general store, Bug Dealer, blacksmith, carpenter,
weaver, stonemason, modern wares, Ecologist) and Maren in the Bee Meadow; the Mayor is there too, and talks, but
sells nothing yet. Players start with no coins. Shops sell items, single recipes and recipe books; six shopkeepers
buy things (the general store, Bug Dealer, blacksmith, carpenter and weaver, and Maren); selling uses a basket;
talking to someone shows a portrait and a greeting; a check stops buy-low, sell-high loops.

**Not built** — land deeds; the Fisherman's shop; townspeople who walk about; quests; the second town; the shops at
the mine; the myrmecologist.

**Designed** — quests that are optional, grow out of what is happening in the world, can be solved several ways and
are never forced (January 2026).

**Still open** (→ §16) — bounties (in the founding documents, and a bounty board designed for the Deadly Ants
outpost); what townspeople do beyond trading; prices overall.

### 14 · The world and exploring
Twenty zones of 256 by 256 squares on a grid five rows deep and four wide — three rows of surface, two underground —
around the starting village. Danger rises going north and east on the surface and going deeper; rivers, cliffs and
deep water separate the harder places, with crossings. Every zone is meant to have named places, landmarks and
secrets, and signposts give fast travel.

| | west | | | east |
|---|---|---|---|---|
| far north | Locust Farmland · the western town | Millipede Forest | Spider Vale West | Spider Vale East |
| north | Hilltop Meadow | Butterfly Fields | Scorpion Rocks | Deep Swamp |
| the village's row | **Bee Meadow** — built | **the Village** — built | Wasp Thicket | Shallow Swamp |
| underground | **Ant Tunnels** — built | **Underground Passages** (the first mine) — built | Underground River | Deadly Ants outpost |
| deep underground | Ant Colony and its queen | Centipede Cavern | the deep river's sunken ruins | Deadly Ants core |

**Decided** — the grid and its orientation (north at the top, underground to the south); the second town in the
Locust Farmland (2026-06-27); **bugs really cross from one zone to the next** (2026-07-06) — finishing that is part of
finishing the game, and how is left to me: whole swarms migrate (2026-09-26); objects need a reason to be there; no
standalone rocks; wild zones are wooded by default, with clearings; zone borders blend on gradients; the view is from
above, so caves show no ceilings; the village gets secrets (2026-09-26); a small underground fortress hides a
legendary set in a locked chest (2026-08-06).

**Built today** — five playable zones joined by walking off their edges: the rebuilt village, the Bee Meadow (sea,
coves, Maren's farm, a fishing hamlet), Underground Passages and the Ant Tunnels, plus the old demo village — **which
is where new players start, although it has no shops**. The Ant Tunnels were built after the owner went through their
design line by line (2026-07-07); the Ant Colony and the Centipede Cavern are designed but not built. About sixteen
test zones. Bugs can't yet cross from one zone to another. No map, no fast travel, no working signposts.

**Designed** — an economy sheet for seventeen zones, fuller zone designs for seven, landmark lists for four; secrets
such as hermit cabins, special merchants and hidden caverns.

**Still open** (→ §01, §17) — a few places disagree between documents (where the ranger station is; Spider Vale East
described as the "western edge"); how fast travel is unlocked.

### 15 · Progression and tiers
The player moves up by getting better tools, which open harder ore, which makes better bars and gear, which open
harder and deeper zones and new materials. The food chain is the other ladder: to keep bigger bugs, farm the smaller
ones.

**Decided**
- Progress through gear and preparation, gated by cost; no storyline (2026-09-26).
- Balance is pacing, not minimalism: each kind of content has a minimum count, and tuning changes numbers, never
  deletes content (D4, June 2026).
- No rule is forced on every zone (2026-09-26).

**Built today** — tool tiers gate ores; 80 recipes are bought from shopkeepers; better bars and tools cost coins;
backpacks would add bag slots (none can be had yet). No experience points and no skill levels.

**Designed** — about five tiers across three phases, each a complete chapter; iron a few sessions in; each new tool
roughly halves the effort of gathering; the player can always name the current goal and the next two (the economy's
progression design).

**Still open** (→ §02) — whether there is an end-game (the legendary sets, the deadliest zones and the deep metals
suggest one; the January 2026 design says there is none); where the metal ladder stops; some documents keep the
anvil, forge and armour out of the village while D19 and D26 put them in; whether sprinklers come early or late.

### 16 · Power and automation
An optional industrial route for later: wind turbines and solar panels make powered areas; powered versions of
gardening and bug-farming tools and of stations, some fully automatic; batteries before a recharger; power lines. The
rule stays the same: machines ease chores, and they never play for the player.

**Decided** — power from wind turbines and solar panels, with powered tools and powered versions of stations; the
details are mine to design (2026-09-26); the electronics are bought, never player-made (D1, D26); the village windmill
waits for the western town (2026-06-27).

**Built today** — nothing; the windmill, electric fence and heater exist as decoration only.

**Designed** — electricity as a wealth-gated expansion bought from a shop (the economy catalogues).

**Still open** (→ §12) — how far automation goes (the December 2025 requirements preferred NPC workers to machines;
later ideas design conveyors and sorters).

### 17 · Time, weather and light
**Decided** — the underground is pitch dark (2026-07-08); empty zones stay frozen and catch up on the first visit
(2026-09-26).

**Built today** — a 14-minute day and a clock; golden dusk and dawn; nights dark enough to need a torch or lamp; rain on
about three days in ten, with thunder; fruit falls in the evening. A bed only sets where the player wakes. Each zone
keeps its own clock and stops when it is empty, so two zones can show different times of day.

**Designed** — one clock for the whole world (the roadmap).

**Still open** (→ §18) — seasons ("no seasons" in January 2026, since reopened); sleeping to skip the night; the
droughts the owner wants to design.

### 18 · Playing together
**Decided** (2026-09-26) — Terraria-style hosting; our own server is just another server, and each server holds as
many players as is measured to work; players join by typing an address, with Epic's free relay first and Steam
later; each world keeps its own characters, with a setting that lets a host admit characters from other worlds; a
lawless shared world and safe private plots. Everything in the world persists (D31).

**Built today** — each zone is shared, every player sees the same bugs, and players who join late see everything as
it is. An account holds up to eight characters, usable in any world; zones save every ten minutes; the game's server
decides damage, catches, inventories and prices.

**Not built** — reconnecting after a dropped connection; chat; trading between players; the hosting menus. Two known
faults: two players arriving at once can create two copies of a zone, and a failed zone crossing can strand a player.

**Still open** (→ §19) — player-versus-player combat (only the combat research touches it: no friendly fire by
default; §19 already asks); griefing, such as releasing wasps into someone's farm; the owner's doubt (August 2026)
whether anything in the shared world should go faster for one player than for another.

### 19 · The interface and learning the game
**Decided** — examining an item or a recipe shows what it does and its real biology; tutorials unlock as the player
goes (2026-09-26). The roadmap plans about 650 short texts for it.

**Built today** — a hotbar and an inventory at the screen edges while the world keeps running; one panel for crafting,
storage, compost, nurseries and hives; a shop basket; hearts; the clock; a bug card; a message for most refused
actions (nursery deposits still fail silently); character select, the opening text and the title screen. Hovering
shows only a name — 2 of the game's 654 things have a description.

**Designed** — a bar of buttons for the inventory, Ecologist, Mayor and Herbalist; tutorials; the Ecology tab; station
panels with their own look.

**Still open** (→ §20) — how tutorials are delivered; the controls and settings.

### 20 · Art and sound
**Decided** (2026-09-26) — all art made with gpt-image-2 and pixel-snapped, 32 art pixels to a square, regenerated
after sign-off in test batches; code-drawn art rejected; every paid image call asked for first. Earlier (2026-07-08):
a look of its own — other indie games, Apico among them, are examples and not targets — with subtle bloom, a
pixel-perfect camera and one colour grade. Necesse is the target for the grass (July 2026). The art guides set the
style: seen from above at an angle, lit from the top left, chunky pixel art with three to five shades per material,
and every sprite facing the camera.

**Built today** — about 775 images from the older route, not pixel-snapped; four approved outfits made the new way but
not yet in the game; dark nights with lamps and torches, animated water, swaying plants, dust and shadows; the grass
overhaul (July 2026). The bloom, the pixel-perfect camera and the colour grade are not built — the screen-wide
effects are switched off. Sound is eight simple effects generated in code (hit, kill, sting, faint, thunder, hiss,
chewing, axe); there is no music, footsteps or background sound, though a library of 203 bug sounds and music tracks
sits in the repo, unused.

**Still open** (→ §21, §22) — how the townspeople look (all eleven are still old placeholders); the music and sound
plan.

## As built
**What a new player can do today.** Make a character and watch the opening; arrive wearing leather with wooden tools,
a small net, a watering can, three kinds of seeds, torches, a flashlight, fencing for a pen and no money; catch flies,
butterflies and other small bugs; breed bugs in a compost bin; grow seven crops and pick fruit; mine ore (though not
refine it); buy copper to steel bars and craft at eleven working stations; buy from eight shopkeepers and sell to
six; fight wasps and centipedes; and walk between five zones. They can't yet cook, fish, eat to heal, use power,
travel fast, read an Ecology tab, or get anything from armour except the bee suit.

**Where the game and the design disagree today** — each goes on the backlog or into its section:
1. New players start in the old demo village, which has no shops; the rebuilt village is meant to be the start.
2. The rock crusher, bug extractor and gem cutter stand only in a test zone: mined ore can't be refined, carcasses
   can't be processed and gems can't be cut, and silver, gold and platinum are out of reach.
3. Wasps, hornets and dragonflies need the large net, which can't be bought or made; centipedes need a trap, and there
   is none; no backpack can be had either.
4. Eleven of the fifteen stations can't be crafted or bought, although D1 says they can.
5. No bug hunts at night, so nights add no danger yet: real wasps and hornets hunt by day, and night danger waits for
   a real night-active species.
6. The Ecology tab doesn't exist, although the roadmap's opening brief assumed it did (a note there now corrects
   it); the magnifying glass does nothing and isn't in the starting kit, although D12 says it should be.
7. Floors don't stop bugs appearing; no door stops players; mud and shallow water don't slow anyone.
8. Wheat is still sold and planted in the village.
9. The autonet doesn't catch anything; the rebuilt village's beehives never come alive; mannequins don't show
   clothes; the Fisherman isn't placed.
10. Breaking a full compost bin leaves an invisible food source behind; wild bug broods on the ground can't be seen;
    milkweed and compost bins can't be seeded from empty, and nursery refusals give no message; breaking the gem
    cutter drops a rock crusher.
11. At 88 places, walking off one zone's edge would put the player inside rock or a wall on the other side (35 of them
    boxed in); the fix is decided — land on the nearest open ground.
12. Each zone has a hard ceiling per species, while the decided limits are food, predators and age.

Some documents are also plainly out of date against the game — recipe counts, net sizes, hive types, the lighting
document, rotting fruit, the zone scale. I'll correct each as its section is rebuilt.

## Proposals
### P1. Where a later owner decision replaced an older text, the later one stands
The older documents get a note saying so:
- one seamless world (December 2025) → separate zones joined at their edges (the grid the owner's June rulings and the
  approved roadmap build on);
- wasps flying over fences (January 2026) → fences hold wasps (the owner's correction, 2026-06-18);
- no source for leather (the June 2026 crafting design) → leather from processing bugs (D11; the owner's bug map,
  2026-06-28);
- ore going straight from the sluice to a bar (D26) → crushed, washed, then smelted (the owner's choice, 2026-06-28);
- no formic items (D18) → ants give formic acid (2026-07-07);
- Apico as the owner's benchmark (the July research) → one example among many, not a target (2026-07-08);
- a diver's set and diving in the zone designs → no diving in this game (August 2026);
- building only the village and the first mine (D17, June 2026) and fishing left out of the first release (D5) → all
  twenty zones, ring by ring, with fishing arriving with the Underground River (the approved roadmap, 2026-09-26).

Four disagreements are **not** settled here:
- whether butterfly young stay on the milkweed — the later text isn't clearly the owner's (§05);
- how outfits are worn — drawing them whole is the owner's tentative choice, but it doesn't decide whether they are
  equipped as one outfit or as pieces (§08);
- the armour ladder — the owner's August cuts (bronze, silver, tin and stone out, wood in) would replace D11's nine
  rungs, but a bronze outfit was approved after them, on 2026-08-15 (§08);
- where the metal ladder stops — no ruling either way (§02, §09).

**Lenses:** Don't reopen settled decisions — each replacement is a later owner decision or the approved roadmap.
Already covered — nothing here is new design.

### P2. No magic
The world is 2126 science. The magic and fantasy races in the old brainstorms — enchanting, arcane tools and books,
magic bait, dwarven ruins — are dropped. The deep fantasy metals the backlog plans for end-game gear (mithril,
adamant) are a separate question for §02. The one signal the other way is the wizard's robe the owner asked for: P2
still allows costumes like it — a look, with no powers — and what the robe becomes is §08's question.

**Lenses:** Premise — people survived a plague by breeding bugs, and science is how the world works. It extends two
narrow rulings of the owner's: potions are ordinary items, and the fancy plate is non-magical. Surprise — the wonder
comes from real biology (the examine texts), not spells.

## Questions
### Q1. Does this describe the game?
If anything is wrong or missing, say what in the note or the box at the bottom.
- **A.** Yes — rebuild the sections from it.
- **B.** Mostly — fix what I noted, then rebuild the sections.
- **C.** No — something big is wrong or missing; let's go over it first.

## Sources
- The design documents — `docs/product/design/` (the December 2025 requirements, the January 2026 design document,
  the armour notes and the outfit roster), `docs/brainstorms/`, `docs/plans/`, `docs/product/ecology/`: 52 files.
- The economy and zones — `docs/product/economy/` (the decision log D1–D31, the catalogues, the zone sheets) and
  `docs/product/zones/`: 56 files.
- How the game works as built — `docs/product/architecture/`, plus `ROADMAP.md`, `BACKLOG.md`, `CHANGELOG.md` and
  `art_needed.md`: 21 files, with 45 claims checked against the code.
- The guides — `docs/guides/` (authoring, art, the owner's correction ledger): 32 files.
- The investigations — `docs/product/investigations/`: the playtest investigations, design investigations and deep
  research — 80 files, plus a search of the 63 raw research notes for recorded decisions.
- Decision records kept with the art: `tools/_generated/player/APPROVED/DECISIONS.md` and the review notes beside it
  (for example the crowns ruling of 2026-08-15).
- The game itself — `nakama/data/` (species, entities, recipes, crops, zones), `nakama/modules/`,
  `BugFarmerClient/Assets/Scripts/`. Checked there: the 15 species, the 185 recipes, the seven crops, the stations in
  each zone, the shops' stock, the nets, fences and water, the start village, fainting, night hunters, the autonet.
- The drafted sections that record the owner's decisions of 2026-09-26: `docs/gdd/00_premise.md`, `01_world.md`,
  `08_gear.md` and `19_multiplayer.md`, beside `docs/product/ROADMAP.md`.
- Two separate reviews checked this overview against all of the above.
