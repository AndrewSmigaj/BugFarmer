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

**Nothing in the game is finished.** What the prototype has now is a first version: every system, every number in
the data (prices, timings, counts) and every bug is a placeholder until it has been designed and tuned, and every bug
still needs more passes for behaviour, combat and ecology (owner, 2026-09-27). "In the prototype now" below means
exactly that — not "done".

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
- **The premise**: the year 2126; a plague killed nearly every mammal; people bred bugs bigger to have food; the
  player starts over on the frontier as a bug farmer. (The opening text in the game is a placeholder.)
- **The bugs are giant**, and their size stays as designed (2026-09-26).
- **Bugs, fish and people survive**; birds, amphibians and reptiles died out too, so no frogs (2026-09-27; D31).
- **Every creature is a real species** with real behaviour (2026-07-11). New species are welcome as long as each is
  explained, keeps the balance, and doesn't need a whole new zone (2026-09-26).
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
- **No seasons** (January 2026; confirmed 2026-09-27).
- **All art is made with gpt-image-2 and pixel-snapped**, 32 art pixels to a grid square, and regenerated after this
  document is signed off, in test batches (2026-09-26).
- From the January 2026 design document: **no stamina**, **no disasters on a timer and no forced invasions**,
  **nothing on a player's private plot is lost while they are away**, and **machines ease chores but never play for
  the player**.

## The game, activity by activity

### 0 · What belongs in the world
Bugs, fish and people made it through. The plague took the mammals, and birds, amphibians and reptiles died out too.
Everything in the world has to fit that.

**Decided**
- **Bugs, fish and people survive; birds, amphibians and reptiles died out too** (2026-09-27). No frogs (D31)
  follows from this.
- **Nothing from the mammal world**: the mammal things that slipped into the old idea lists — cave bats and bat
  guano, milk and cheese, horseshoes, livestock and manure, a rabbit's-foot charm, a pack mule — are dropped
  (2026-09-27).
- **No meteors**: the December 2025 idea of a meteor-borne infection is dropped (2026-09-27).
- The premise, giant bugs, real species, and new species on three conditions (see the frame).

**In the prototype now** — a placeholder opening text; a few items in the data that don't fit the premise (a cow
skull, a cat statue, a hay bale, a birdbath, bones and bone piles) — §00 decides whether any stay as relics of the
old world or go.

**Still open** (→ §00) — what counts as a "bug" (Q2 below); how the game should feel.

### 1 · Catching and farming bugs — the heart of the game
Any bug can be farmed if it can be held. The player catches bugs, keeps them in pens built from fences and walls,
breeds them at nurseries and host plants, and harvests either the bug itself or its product at a station — honey
from bees today; silk, venom and more on paper. Food chains make several ladders, some short and some tall — flies
feeding wasps is one of them, not the bottom rung of a single ladder. Bugs are caught three ways: with hand nets, in
catchers placed on the ground that bugs fly or walk into, and by the autonet, a machine that draws in bugs from the area
just ahead of it. Placed catchers and the autonet take bugs out of the world.

**Decided**
- Killing a bug drops only its carcass (D18); the bug extractor turns carcasses into materials — the owner's bug map
  (2026-06-28) gives chitin from beetles, centipedes, millipedes and wasps, and leather from flies and butterflies;
  ants give formic acid (2026-07-07).
- **Calming is one system, set bug by bug** (2026-09-27): many bugs can't be calmed at all, and what calms one (smoke
  calms bees) may irritate another. (The prototype's "most bugs can be calmed" came from an older note and is
  replaced.)
- **Catching** (2026-09-27): a small and a large hand net, each good only up to a certain size of bug; bigger bugs are
  taken by catchers placed on the ground; early placed nets that bugs fly into hold only a few; the autonet draws
  in bugs from the area just ahead of it and holds more. How these work in detail is proposal P3.
- **Pens hold every bug — no bug flies over a fence or wall** (2026-09-27; for wasps since 2026-06-18). Each species
  has up to three tiers, stronger and often bigger, and a fence material holds only the bugs it is strong enough for;
  some bugs can't damage some fence types at all. Strengths are tuned with the ecology.
- **Fencing is overhauled**: posts that connect, as in other games, instead of one repeated fence block
  (2026-09-27). How is proposal P5.
- **A live bug and a dead one are worth the same**; processing a carcass may pay more or less (2026-09-27). Coins also
  come from other things than bugs.
- **Compost is sold and is also a fertiliser source** (2026-09-27).
- **Butterflies** (2026-09-27): the nursery holds the eggs and the young caterpillars; caterpillars go out into the
  world, grow, form a chrysalis and emerge as butterflies. How they grow is proposal P7.
- The flies breeding in a compost bin keep their pupa stage (2026-07-17).
- **Anything the game has but can't be obtained** — the bug extractor, the large net and the rest — gets a way to
  obtain it at the right point in the game (2026-09-27).

**In the prototype now** — nets (bare hands and the small net take small bugs; wasps, hornets and dragonflies need
the large net, which can't be bought or made; centipedes can't be caught); one calming threshold with placeholder
values; pens that hold walking bugs and wasps; breeding you can see — eggs, larvae and pupae, with untuned timings;
the compost bin making sellable compost while flies breed in it; beekeeping at Maren's farm, while the four
beehives in the rebuilt village never come alive; the Bug Dealer buying bugs at placeholder prices; the bug
extractor only in a test zone; the autonet only storing things. Three prototype rules are **not** the design and
go: bees, dragonflies and fireflies flying over fences; wooden fences chewable by centipedes with stone as the
cure-all; carrion beetles making compost.

**Designed, not built** — bug research with the magnifying glass (wanted — P8); aphids (small ones); specimen
collecting; keeping ants; traps and bait (not decided — P4 suggests a way); villagers mending fences (P6).
(Two old items are gone: using wasps as pest control, since wasps already eat flies, and roofed pens for flying
bugs, since no bug flies over.)

**Still open** (→ §05) — the tiers and fence strengths themselves (tuning); which bugs give which materials beyond
the lines the materials catalogue already plans (chitin, silk, venom, glow and wing-scale lines — §10 checks the
gaps).

### 2 · The bugs themselves
**Decided**
- **Real species with real behaviour** (2026-07-11): the game teaches a little ecology and biology (2026-09-27).
  The prototype's invented names (the soldier wasp, the giant hornet and others) are replaced by real species.
- **Every bug is unfinished**, including the ones already worked on: each needs more passes for behaviour, combat
  and ecology tuning (2026-09-27).
- **Tiers belong to a species, not a rule**: some bugs have one form, some two, none more than three — aphids have
  one (2026-09-27).
- **Two ant species, black ants and fire ants**, in different zones, so no more ant zones are needed (August 2026;
  2026-09-27). The other ant species in the zone designs — garden, harvester, army and bullet ants — go.
- **Mini-bosses**: yes — set off by conditions or simply placed in the world (2026-09-27).
- Spiders live only in the lower underground (D21).

**In the prototype now** — fifteen species: common fly, meadow butterfly, honeybee, wasp, soldier wasp, giant hornet,
carrion beetle, garden centipede, tiger centipede, giant centipede, millipede, worker ant, scout ant, firefly and
dragonfly. Flies flee, butterflies are curious, bees are gentle until provoked, wasps and hornets hunt and dive,
fireflies blink at night. Centipedes are grouped only to keep network traffic down; real centipedes hunt alone, so
they should spread out rather than hunt as packs (2026-09-27). The lighting as a whole is a prototype.

**Designed** — the zone sheets name 84 species (98 rows across 17 zones, some repeated), including about 16
mini-bosses — more than the owner expected. They include invented names, the extra ant species, and animals that
aren't insects; most zones aren't designed yet, so the list is a starting point to prune, not a plan.

**Still open** (→ §03) — the full list, zone by zone, as the zones are designed; what counts as a bug (Q2).

### 3 · The living ecosystem and the Ecologist
Everything eats, breeds, ages and dies, and the player can see why numbers rise and fall and act on it. Many levers
hold populations in a living balance — food, breeding sites and host plants, predators, lifespans, habitat, weather,
fences and everything the player does — with a hidden balancing system stepping in only at the extremes. The
**Ecologist** lives in a house east of the village. The Ecology tab's button starts greyed out and says to find
him; meeting him unlocks the tab, but a zone's information only appears once the player places a bug monitoring
station there — his first quest. His quests — rebalancing a population, placing stations and more — are the tab's
tasks; there is one system, not two. The **magnifying glass** works like research in Apico: looking at enough of a
species unlocks facts about it — what helps it breed, what it dislikes, what it eats and more — shown on that bug's
own information page. The Ecology tab holds the population charts.

**Decided**
- The ecology works as designed and gets more passes as tuning and new behaviours arrive (2026-09-27).
- The Ecologist, the tab, the monitoring station and the quests work as described above (2026-09-27).
- Research with the magnifying glass fills in the bug's information page, not the Ecology tab (2026-09-27).
- Every bug is its own creature, behaving the same on every player's screen (2026-07-13), and each species feeds its
  own way: a wasp hunts a fly and eats it, sometimes leaving the corpse; ants gather food; spiders hunt, or wait in
  webs.
- Quest rewards: money, and sometimes gear or recipes for big tasks such as taming a new area (2026-09-27).
- **No seasons** (January 2026; confirmed 2026-09-27).

**In the prototype now** — the food web runs; the balancing system re-seeds and thins, and can hold back the rain;
each zone also has a hard ceiling per species (1,500 flies in the rebuilt village, for example); there is no Ecology
tab (only a developer graph), and the village Ecologist sells six decoration recipes.

**Designed, not built** — crop pests (aphids, caterpillars, locusts), each with its own natural enemies — ladybugs
eat aphids; pollination raising yields.

**Still open** (→ §04) — the quest list and rewards (P9 suggests some); the tab's design (P9); whether a left-behind
corpse feeds other bugs; how far the per-bug model goes, part of the ecology or all of it (the owner's call); fewer
fruit on the ground, with another lever raised instead (P10).

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
- Compost is a fertiliser source (2026-09-27); what fertiliser does is deferred (July 2026).

**In the prototype now**
- Hoe a plot, plant a seed, water it with a watering can (refilled at water). Crops grow as they are watered, never
  wilt, and sometimes drop a seed. Seven crops — tomato, eggplant, corn, wheat, carrot, pumpkin and cabbage; tomato
  and eggplant give several harvests. Rain waters everything when it falls.
- Fruit trees — apple, orange, plum and cherry — fruit after a few days of water; ripe fruit falls in the evening and
  rots into fly food, which disappears if nothing eats it. There is too much fruit on the ground (to be lowered — see
  part 3). Fruit is picked up by hand.
- **Not built:** sprinklers, fertiliser, crop pests, pollination.

**Still open** (→ §06) — what fertiliser does (the January 2026 farming design says more yield, not faster growth);
how fallen fruit is collected by hitting it — the owner asked for that after the June playtest, and two ways to
build it wait for a pick; how many more crops, and where each first appears.

### 5 · Mining and the underground
A block world. The surface has dirt and stone to dig; the underground is solid rock the player carves through; ore
sits in veins that grow richer and rarer with depth; the dark needs light; and the mining ideas have danger guarding
the best ore.

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

**In the prototype now**
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

**In the prototype now** — 185 recipes on 15 stations. 105 are known from the start; 80 are bought from shopkeepers, singly or
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

**In the prototype now** — about 280 placeable things, placed from the hotbar with a green or red preview; the shovel places
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

**In the prototype now**
- Hearts for health; stings and bites take some away. Every attack gives a warning — a flash and a hiss — before it
  lands, and a dodge dash gives a moment of safety.
- Sword and spear with two moves each, and an axe jab. Soldier wasps, giant hornets and tiger and giant centipedes
  are the tougher tiers (their names are placeholders — see part 2). Wasp nests raid; centipedes lunge after a
  warning hiss.
- **Fainting costs nothing**: the player wakes at the zone's start point or their bed, at full health, with
  everything they carried.
- **Not built:** armour protection (armour is looks only, except the bee suit, which stops stings); night danger (no
  bug is marked as a night hunter yet); bosses; poison and other effects; bows and other ranged weapons (set aside for
  later, D12).

**Still open** (→ §07) — why the player fights and what fighting rewards; what an expedition risks, since fainting
costs nothing; which enemies come next (spiders, scorpions, warrior ants) and how bosses work.

### 9 · Gear: outfits, armour and accessories
An outfit is chosen for a trip, not swapped per action, and each role — tank, attack, agility, stealth, mining,
fishing, farming, bug-catching, beekeeping — has its own best set, with a few hybrids. The armour notes suggest
each set gives some defence plus one main bonus and one or two small ones (the owner's example: a set that raises
boat speed and fishing speed). Legendary sets hide behind secrets; decorative outfits boost the farm. About 43 sets are
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

**In the prototype now** — eight equipment slots (head, body, arms, legs, feet, two accessories, backpack). New characters
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

**In the prototype now** — pickaxe, axe, shovel and hoe in eight tiers from wood to platinum, the scythe in seven; saw and
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

**In the prototype now** — food items exist and sell, but eating does nothing. No meals exist (the planned starter stew isn't
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

**In the prototype now** — nothing to play. Docks and fishing props are decoration; the Fisherman (rods, nets, a boat for 400
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

**In the prototype now** — eight shopkeepers in the rebuilt village (general store, Bug Dealer, blacksmith, carpenter,
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

**In the prototype now** — five playable zones joined by walking off their edges: the rebuilt village, the Bee Meadow (sea,
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

**In the prototype now** — tool tiers gate ores; 80 recipes are bought from shopkeepers; better bars and tools cost coins;
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

**In the prototype now** — nothing; the windmill, electric fence and heater exist as decoration only.

**Designed** — electricity as a wealth-gated expansion bought from a shop (the economy catalogues).

**Still open** (→ §12) — how far automation goes (the December 2025 requirements preferred NPC workers to machines;
later ideas design conveyors and sorters).

### 17 · Time, weather and light
**Decided** — no seasons (January 2026; confirmed 2026-09-27); the underground is pitch dark (2026-07-08); empty
zones stay frozen and catch up on the first visit (2026-09-26).

**In the prototype now** — a 14-minute day and a clock; golden dusk and dawn; nights dark enough to need a torch or lamp; rain on
some days, with thunder; fruit falls in the evening. A bed only sets where the player wakes. Each zone
keeps its own clock and stops when it is empty, so two zones can show different times of day.

**Designed** — one clock for the whole world (the roadmap).

**Still open** (→ §18) — sleeping to skip the night; the droughts the owner wants to design.

### 18 · Playing together
**Decided** (2026-09-26) — Terraria-style hosting; our own server is just another server, and each server holds as
many players as is measured to work; players join by typing an address, with Epic's free relay first and Steam
later; each world keeps its own characters, with a setting that lets a host admit characters from other worlds; a
lawless shared world and safe private plots. Everything in the world persists (D31).

**In the prototype now** — each zone is shared, every player sees the same bugs, and players who join late see everything as
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

**In the prototype now** — a hotbar and an inventory at the screen edges while the world keeps running; one panel for crafting,
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

**In the prototype now** — about 775 images from the older route, not pixel-snapped; four approved outfits made the new way but
not yet in the game; dark nights with lamps and torches, animated water, swaying plants, dust and shadows; the grass
overhaul (July 2026). The bloom, the pixel-perfect camera and the colour grade are not built — the screen-wide
effects are switched off. Sound is eight simple effects generated in code (hit, kill, sting, faint, thunder, hiss,
chewing, axe); there is no music, footsteps or background sound, though a library of 203 bug sounds and music tracks
sits in the repo, unused.

**Still open** (→ §21, §22) — how the townspeople look (all eleven are still old placeholders); the music and sound
plan.

## As built
**What a new player can do in the prototype now.** Make a character and watch the opening; arrive wearing leather with wooden tools,
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
12. Each zone has a hard ceiling per species, while the design uses the ecology's many levers instead.
13. Prototype rules that were never the design: bees, dragonflies and fireflies fly over fences; wooden fences are
    chewable by centipedes and stone stops them; carrion beetles make compost; centipedes move as packs; "most bugs
    can be calmed"; invented species names (the soldier wasp, the giant hornet).

Some documents are also plainly out of date against the game — recipe counts, net sizes, hive types, the lighting
document, rotting fruit, the zone scale. I'll correct each as its section is rebuilt.

## Proposals
### P1. Where a later owner decision replaced an older text, the later one stands
The older documents get a note saying so:
- one seamless world (December 2025) → separate zones joined at their edges (the grid the owner's June rulings and the
  approved roadmap build on);
- bugs flying over fences (January 2026) → no bug flies over a fence or wall (the owner's corrections, 2026-06-18
  for wasps and 2026-09-27 for all);
- butterfly caterpillars staying on the milkweed (the backlog, 2026-07-16) → caterpillars go out into the world to
  grow and pupate (2026-09-27);
- no source for leather (the June 2026 crafting design) → leather from processing bugs (D11; the owner's bug map,
  2026-06-28);
- ore going straight from the sluice to a bar (D26) → crushed, washed, then smelted (the owner's choice, 2026-06-28);
- no formic items (D18) → ants give formic acid (2026-07-07);
- Apico as the owner's benchmark (the July research) → one example among many, not a target (2026-07-08);
- a diver's set and diving in the zone designs → no diving in this game (August 2026);
- building only the village and the first mine (D17, June 2026) and fishing left out of the first release (D5) → all
  twenty zones, ring by ring, with fishing arriving with the Underground River (the approved roadmap, 2026-09-26).

Three disagreements are **not** settled here:
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

### P3. Catching: hand nets for the small ones, placed catchers for everything bigger
Bugs here are giant — even a fly is the size of a cat next to the player — so every catcher is sized to that.
- **Each species has a size for each of its tiers**, shown on its information page.
- **Hand nets** (tools you swing): the small net takes the smallest bugs; the large net takes middle-sized ones. No
  hand net takes anything bigger. A bug that has to be calmed first can only be netted once it is calm.
- **Placed catchers** (bugs have to come to them; each holds only a few, and you can see what is inside):
  - **net runs** — netting stretched between posts, put up with the same tool as fences. Flying bugs blunder into
    them and hang there, like a real interception net. Fine mesh holds the smallest; heavy netting holds big flyers.
    The prototype already has net posts and fly netting to build on.
  - **pit traps** for walking bugs — a covered pit you place as an object (the ground itself is never dug into a
    hole), in sizes up to the biggest walkers.
  - **cage traps** for the largest bugs — a baited cage with a drop door.
- **The autonet**: the machine that draws in bugs from the area just ahead of it; it holds more and stops when full.
- **Lights at night** (the owner's idea, for the powered age): lamps draw night-flying bugs, and nets, automatic
  catchers or bug zappers placed around them do the catching; a zapper leaves carcasses, not live bugs.
Every catcher takes bugs out of the world, keeps them alive (except the zapper), and is emptied into the bug bag by
hand.

**Lenses:** Premise — sized for giant bugs, with no tiny-bug tools (the pooter and the Berlese funnel were rejected
for that reason). Real biology — interception nets, pit traps and light traps are how bugs are really caught. Economy
— small capacities and hand-emptying keep the January rule that machines ease chores, never play. **Cost and risk:**
placed catchers are new objects in the shared bug simulation (every player must see the same bug caught), and each
size needs art; balancing them against the hand net will take several passes.

### P4. Traps and bait without the silliness
- **Nothing bigger than the player goes in the backpack.** Small catchers are carried and placed like furniture. Big
  ones — long net runs, large pits, cages — are put up where they stand from posts, netting and planks, and taking one
  down gives back those parts, not the whole trap. That is an exception to D22 (placed objects drop themselves) for
  structures bigger than the player, and it applies to fences too.
- **Bait sits in a dish beside a catcher** and draws the species that like it from nearby: rotting fruit for flies,
  a carcass for carrion beetles, something sweet for wasps — though sweet bait draws bees just as well, so beekeepers
  have to think about where they put it. Which bait works on which bug is something the magnifying glass teaches (P8).

**Lenses:** The owner's worry answered — no trap ten times the player's size in the backpack. Curiosity — finding the
right bait is a small discovery for each species. **Cost and risk:** building big catchers in place needs the same
assembly the fence overhaul needs (P5) — worth doing once for both; bait needs an "attraction" source the simulation
can share, which the prototype has in a simple form (flies are drawn to compost).

### P5. Fences built from posts, and pens that hold some bugs and not others
- **Building**: place a post; drag to another post along the grid and rails fill the run; pieces join up on their
  own — straight runs, corners, T-joins, crossings and gates. The simulation still sees fences square by square, so
  the shared bug simulation doesn't change; only placing and drawing do.
- **Different bugs damage fences in different ways, and each material resists each way differently**, so no material
  is best against everything: real wasps scrape wood fibre off fences to make their paper nests; big beetles shove;
  some bugs never touch a fence. (The prototype's centipede chewing wood goes — real centipedes don't.) Numbers are
  set when the ecology is tuned.
- **No bug flies over**, as decided — so a fence also keeps out bees and other pollinators, and a fenced garden needs
  a way in for them (a gate, a gap, or a plant barrier, P8).
- **Private plots are safe**: nothing damages a fence on a private plot while its owner is away (the January 2026
  rule).

**Lenses:** Readability — a pen reads as a pen, a gap as a gap. Real biology — damage comes from what each bug really
does. Economy — materials become a choice, not a ladder with one answer. **Cost and risk:** the joining pieces need a
sprite for every shape and material (fewer if posts and rails are drawn separately and combined); the pollinator
consequence is real and needs a design answer, not an afterthought.

### P6. Village fences mended by villagers, and hired hands later
- **Players can't damage or take the townspeople's things**; trying shows a short message (as decided). The village's
  own fences, buildings and goods are marked as the village's when the zone is made — today a placed object records
  only what it is, where it faces and any sign text, so this mark is new.
- **Bugs can damage village fences, and villagers mend them, visibly, from the start**: a villager walks to the damaged
  stretch and works on it until it is whole. This fits the owner's own locked design for workers (December 2025):
  workers are like stations with a job, not roaming characters — no pathfinding across the map, and the walking is for
  show.
- **Hired hands on private plots — my recommendation: not in the first release; afterwards, station-tenders and fence-
  menders only.** Why: the private plot is where the player's own farm design is the fun; the catchers, the autonet
  and powered stations already take chores off the player's hands; and workers who gather and farm (the December 2025
  list had woodcutters and miners) would play the game for the player, against the January rule. The real costs are
  character art for every kind of worker, the hiring and assigning screens, and balance — not pathfinding, which the
  locked design already avoids. **This narrows a locked decision of the owner's, so it is his call.** (For reference:
  Necesse builds its whole game on settlers who work; Stardew keeps them to late-game helpers.)

**Lenses:** Fair start — new players can't strip the village for early money. Pillars — machines and helpers ease
chores, never play. Picture the moment — a centipede damages the village fence at night; next morning a villager is
there mending it. **Cost and risk:** village ownership marks on every authored object; villager repair walks need the
villagers to exist as characters with a little behaviour, which they don't yet (today they stand at their counters).

### P7. Butterflies grow up out in the world
- **On a milkweed plant** — which is itself the butterfly nursery — eggs hatch into small caterpillars.
- The caterpillars leave the plant and eat milkweed nearby — real monarch caterpillars eat nothing else — growing
  through three visible sizes, small to large. (Real ones go through five stages.)
- A fully grown caterpillar wanders to a sheltered spot the player can see from above — a fence post, a branch, a wall
  — hangs, and forms a **chrysalis**; later a butterfly comes out. (Real monarchs often wander away from the milkweed
  to do this.)
- Players can catch caterpillars with the small net and move a chrysalis to a better spot; wasps hunt caterpillars, as
  real wasps do. So farming butterflies means planting milkweed and giving caterpillars safe places to change.
- Moths are the same shape with one difference: silk moths spin a **cocoon** of silk instead of forming a bare
  chrysalis — and that cocoon is where silk comes from.

**Lenses:** Real biology — the monarch–milkweed bond is one of the best-known facts in ecology, and chrysalis versus
cocoon is a real, teachable difference. Picture the moment — finding a green chrysalis hanging from your own fence.
**Cost and risk:** caterpillars and chrysalises are more bugs in the shared simulation, each with its own movement and
timing; wasps eating them needs the predation to cover them.

### P8. Research with the magnifying glass, and plants as a gentler fence
- **Research is a list of small tasks per species**, not a head count: look at it, watch it feed, find it breeding,
  catch one, see it at night — each task done a few times. (Counting "different individuals" can't work: the game
  renumbers bugs when swarms split or merge. Task lists are how Pokémon Legends: Arceus does research, and Apico
  rewards looking closely in a similar way.)
- Progress opens facts in three steps: **what it is** (real name, size, food); **how to keep it** (what helps it
  breed, what calms or irritates it, which bait draws it); **its secrets** (what it avoids, its predators and prey, how
  long it lives, a real fact from biology). They appear on the bug's information page, not in the Ecology tab.
- **Plants that push and pull**: farmers really use "push–pull" planting — some plants drive a pest away while others
  draw it off somewhere harmless — and "trap crops", planted as bait for a pest so it leaves the real crop alone.
  Research reveals which plants do what for each species, so a player can steer bugs without walls. Because fences
  stop every bug, plants become the **selective** barrier — one that keeps a pest out but lets bees through.

**Lenses:** Real biology — push–pull and trap crops are real farming methods, so the game teaches something true (no
claims of plants that "repel" bugs unless the evidence is real). Curiosity — every species has something to find.
**Cost and risk:** facts for every species, written and checked — about 650 short texts are already planned for the
examine view; plant effects need the simulation to share them like any other lever.

### P9. The Ecologist's quests and the Ecology tab
- **The flow** (as decided): the tab button is greyed out; meeting the Ecologist east of the village unlocks it; his
  first quest is to place a monitoring station, and that zone's information appears.
- **A station hands the zone to the player**: where one stands, the hidden balancing system waits before it steps in —
  first the Ecologist asks the player to fix a problem, and the system acts only if nobody does (the ecology notes
  already plan this grace period). Without that, it would fix everything first and there would be no quests.
- **Kinds of quest**:
  1. **Survey** — place a station in a new zone and research a few of its species.
  2. **Rebalance** — a species is outside its healthy range; fix it any way you like (plant, move bugs, cull, bring in
     a predator, clean up food). Paid when the numbers come back and stay back; problems the player caused (by
     releasing bugs, say) don't start a paid quest.
  3. **Restore** — bring a species back to a zone it has vanished from.
  4. **Specimens** — bring a live bug or a chrysalis for his collection; a display in his house fills up.
  5. **Outbreak** — a pest booms on the farms and he asks for its natural enemy: ladybugs eat aphids.
  6. **Tag and release** — catch, mark and release a number of one species, then count how many marked ones you catch
     again: this "mark and recapture" is how real ecologists estimate a population.
  7. **Tame a new area** — a chain in a new zone ending in the mini-boss that grew out of an imbalance; the reward is
     gear or a recipe.
- **Rewards**: coins, recipes (station upgrades, planters, nurseries) and, for the big chains, gear — but never the
  basic tools a player needs to play; those are always sold or crafted.
- **Rules**: quests belong to each player; the zone's balance is shared, so everyone benefits from a fixed ecosystem.
  No outbreak or mini-boss comes to a private plot while its owner is away.
- **The tab**: for each zone with a station, each species' numbers over time against its healthy range, and that
  zone's quests with their progress; zones without a station stay blank.

**Lenses:** Player agency — every problem has several solutions (a January 2026 pillar). Real biology — biological
control, restoration and mark-and-recapture are real ecology. No forced chaos — quests come from real conditions and
are optional. **Cost and risk:** a quest system is a new system; the rules against farming paid quests need testing;
multiplayer ownership needs care.

### P10. Ecology tuning — several food chains, fewer fruit, habitat instead of hard caps
- **Several food chains, some short and some tall**, as decided — for example: rotting fruit and compost → flies →
  wasps; flowers → bees → hornets; milkweed → caterpillars and butterflies → wasps; carcasses → carrion beetles;
  leaf litter → millipedes. Each is tuned on its own.
- **Fewer fruit on the ground** (as asked): first shorten how long uneaten fruit lies before it rots away, then lower
  the fruit per tree if needed. Wild zones have no compost bins, so the flies' food there has to come from the land
  itself — carcasses, rot and plants. The prototype's fly data still lists a manure pile among its breeding places
  (unused), and that goes with everything else from the mammal world.
- **Habitat instead of hard caps**: each species needs its own kind of place — flowers, rot, water, shade — and a crowd
  thins where there isn't enough; today's fixed ceilings stay only as a high safety net.
- **Mini-bosses set off by conditions** (decided) — the natural ones follow real biology: crowded locusts really do
  change into swarming locusts, and crowded aphids grow wings; other mini-bosses are simply placed.

**Lenses:** The owner's direction — many levers, not hard caps. Readability — the player can see why a population
moved. Real biology — the locust and aphid changes are real. **Cost and risk:** habitat-based limits are a real change
to the shared simulation and need the determinism checks; each food chain is its own tuning job.

## Questions
### Q1. Does this describe the game?
If anything is wrong or missing, say what in the note or the box at the bottom.
- **A.** Yes — rebuild the sections from it.
- **B.** Mostly — fix what I noted, then rebuild the sections.
- **C.** No — something big is wrong or missing; let's go over it first.

### Q2. What counts as a "bug"?
Bugs, fish and people survived; birds, amphibians and reptiles didn't. Spiders, scorpions, centipedes, millipedes and
pill bugs are what most people call bugs; the zone designs also include snails, leeches, crayfish and a cave crab
(the Underground River's mini-boss, with materials and gear built on it).
- **A.** Every land and freshwater creature without a backbone counts — snails, leeches, crayfish and crabs stay.
- **B.** Only the creepy-crawlies: insects, spiders, scorpions, centipedes, millipedes and pill bugs. Snails, leeches,
  crayfish and the cave crab go, with the Underground River materials and gear built on them.
- **C.** As B, but crayfish and crabs stay as catches in fish traps, like fish; snails and leeches go.

**Recommendation: C.** Everything called a bug on screen reads as a bug, and the Underground River keeps its catches
as fishing; its cave-crab mini-boss would need a new, real-bug replacement.

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
