# §OV · The game as the documents describe it
<!-- gdd: id=OV status=review updated=2026-09-27 -->

Before redoing the design document, every design document in the repo was read in full — about 240 files: the
December 2025 requirements, the January 2026 design document, the brainstorms, the economy and zone designs, the
architecture documents, the roadmap, backlog and changelog, the authoring and art guides, and the investigations.
Five readers each took a share and wrote notes with file and line references; I read all of their notes and checked
the claims that matter against the documents and the game's own code and data; then two separate reviews checked
this overview against the notes and the code. (The 63 raw research notes behind the July research were searched for
decisions rather than read line by line.)

This is the whole game as those documents describe it, in my own words, organised by what the player does. For each
activity it says what has been **decided** (and when), what is **in the prototype now**, what is **designed but not
built**, and what is **still open**, with the section where each open point will come to you. "D" numbers are entries
in the decision log (`docs/product/economy/DECISIONS.md`): D1 to D31 from June and July 2026, D32 onward from the
owner's review of this overview. A few of the early entries mix the owner's rulings with my own defaults, and where
that matters I say which.

**Nothing in the game is finished.** What the prototype has now is a first version: every system, every number in
the data (prices, timings, counts) and every bug is a placeholder until it has been designed and tuned, and every bug
still needs more passes for behaviour, combat and ecology (owner, 2026-09-27). "In the prototype now" below means
exactly that — not "done".

Please correct anything I got wrong or left out. The sections are rebuilt from this once you have checked it.

## The experience
It is 2126. A plague killed nearly every mammal, and people bred bugs big enough to eat. The player starts over on
the frontier as a bug farmer.

Bug Farmer is a top-down multiplayer sandbox in the spirit of Terraria and Stardew Valley. The player **catches,
breeds and sells bugs**; **grows crops and fruit trees**; **digs and mines** for ore; **crafts** tools, gear,
furniture and materials at stations; **builds** pens, fences and a home; **fights** the bugs that bite back;
**trades** with the town's shopkeepers; and **explores** outward from the village — across the surface and down
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
- **Gear is about roles**: combat, mining, stealth, fishing, farming and the other roles each have their own best
  outfit, and no single set is best at everything (2026-08-06); one outfit is worn at a time, whole, and changed any
  time from the inventory (2026-09-27).
- **Potions are ordinary items, not magic** (2026-08-06); meals and potions heal and give boosts, and a bandage or a
  potion can be used on another player (2026-09-27).
- **No upkeep chores**: no hunger, and tools never wear out (2026-09-27).
- **The world is a grid of zones** — surface to the north, underground to the south, danger rising with distance;
  five rows, with a sixth, deepest row left for later (D2, June 2026).
- **Hosting works like Terraria** — host and play, join a friend, or run a dedicated server — and each world keeps
  its own characters, as in Necesse (2026-09-26).
- **Empty zones stay frozen** and catch up when a player first returns (2026-09-26).
- **No seasons** (January 2026; confirmed 2026-09-27).
- **All art is made with gpt-image-2 and pixel-snapped**, 32 art pixels to a grid square, and regenerated after this
  document is signed off, in test batches (2026-09-26).
- From the January 2026 design document: **no disasters on a timer and no forced invasions**, **nothing on a
  player's private plot is lost while they are away**, and **machines ease chores but never play for the player**.
  (Its "no stamina" is replaced: stamina is allowed, 2026-09-27.)

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

**Proposals for this part:** P2; Q2 asks what counts as a bug.

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

**Designed, not built** — bug research with the magnifying glass (wanted — P8); aphids — small ones living on plants, shown in the plant's own view (part 8); specimen
collecting; keeping ants; traps and bait (not decided — P4 suggests a way); villagers mending fences (P6).
(Two old items are gone: using wasps as pest control, since wasps already eat flies, and roofed pens for flying
bugs, since no bug flies over.)

**Still open** (→ §05) — the tiers and fence strengths themselves (tuning); which bugs give which materials beyond
the lines the materials catalogue already plans (chitin, silk, venom, glow and wing-scale lines — §10 checks the
gaps).

**Proposals for this part:** P3, P4, P15.

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

**Proposals for this part:** P7, P13.

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
- **Players may tip the ecosystem**, for better or worse — that is the point of the game; fewer fruit on the ground
  was for looks, and the flies are retuned to live on less; the caps are the safety net (2026-09-28, D62).

**In the prototype now** — the food web runs; the balancing system re-seeds and thins, and can hold back the rain;
each zone also has a hard ceiling per species (1,500 flies in the rebuilt village, for example); there is no Ecology
tab (only a developer graph), and the village Ecologist sells six decoration recipes.

**Designed, not built** — crop pests (aphids, caterpillars, locusts), each with its own natural enemies — ladybugs
eat aphids; pollination raising yields.

**Still open** (→ §04) — the quest list and rewards (P9 suggests some); the tab's design (P9); whether a left-behind
corpse feeds other bugs; how far the per-bug model goes, part of the ecology or all of it (the owner's call); fewer
fruit on the ground, with another lever raised instead (P10).

**Proposals for this part:** P8, P9, P10.

### 4 · Farming and gardening
Crops in tilled plots, watered by hand or by rain; fruit trees whose fallen fruit feeds the flies; later sprinklers,
fertiliser, pests and pollination. Farming is open from the start and limited only by what materials cost. Harvesting
takes a plant's product and sometimes a seed; a plant that would keep producing can also be cut down, and its parts
processed at stations.

**Decided**
- The village grows garden vegetables, and new crops come with new zones (D19). **Wheat comes from the Locust
  Farmland**: its seeds are bought there or harvested from its fields, and the zone has a small village of its own with
  shops and people to meet (2026-09-27).
- **One harvest rule**: harvesting gives the plant's product and sometimes a seed, and plants are grown again from
  seed (D24; confirmed 2026-09-27). **Plants can also be cut down** and their parts processed at stations
  (2026-09-27) — proposal P11.
- **Fertiliser increases yield** (2026-09-27), and compost is a fertiliser source (2026-09-27).
- A harvest gives a share of what is there; the rest is lost (August 2026).

**In the prototype now**
- Hoe a plot, plant a seed, water it with a watering can (refilled at water). Crops grow as they are watered, never
  wilt, and sometimes drop a seed. Seven crops — tomato, eggplant, corn, wheat, carrot, pumpkin and cabbage; tomato
  and eggplant give several harvests.
- Fruit trees — apple, orange, plum and cherry — fruit after a few days of water; ripe fruit falls in the evening and
  rots into fly food, which disappears if nothing eats it. There is too much fruit on the ground (to be lowered — part
  3). Fruit is picked up by hand.
- **Rain waters crops and trees but doesn't show it.** The droplet over a tree means "not watered by you today", and
  rain doesn't count as that, so the droplet stays; and rain only darkens plots that already have a crop in them. A fix
  is queued: rain counts as the day's watering and wets every tilled plot.
- **Not built:** sprinklers, fertiliser, crop pests, pollination.

**Still open** (→ §06) — how fallen fruit is collected by hitting it: the owner asked for that after the June playtest,
and two ways to build it wait for a pick; how many more crops, and where each first appears.

**Proposals for this part:** P11.

### 5 · Mining and the underground
A block world. The surface has dirt and stone to dig; underground, each zone is made of what fits it — the ant zones
are dirt, because ants don't dig through rock, and the mining zones are rock. Ore sits in veins that grow richer and
rarer with depth, the dark needs light, and a trip is limited by how much the player can carry.

**Decided**
- **It is a block world**: a player facing sideways digs the block beside them, not the ground below (2026-08-04).
- **Each underground zone is made of what fits it** — dirt for the ant zones, rock for the mining zones (2026-09-27).
- **One kind of rock.** Depth shows in the floor and the ores, never in harder rock (D22).
- **Ore only in veins** of three to six blocks, never placed by hand — even rare ores — richer and rarer with depth
  (2026-07-06).
- **Dirt areas are diggable masses** of dirt blocks around stone and ore cores, never flat painted dirt (2026-07-06).
- **Underground is pitch dark**, as in Terraria, and a torch is needed (2026-07-08) — in every real underground zone
  (2026-09-27).
- Mining is a main loop, slow and exploratory (D13); ore is crushed, washed, then smelted (2026-06-28).
- **A carrying limit** caps what a trip brings back (2026-09-27); how it works is open.
- **No mining dangers** — no gas, no cave-ins (2026-09-27).
- **Prospecting with a pan** (2026-09-27).
- **The metal ladder** (P20, accepted 2026-09-28): each tool rung opens an ore; cobalt and tungsten are new ores;
  silver, gold and platinum stay as deep rewards for money and machines.

**In the prototype now**
- Ore is gated by pickaxe: coal, copper and tin with a wooden pick, up to diamond with a steel one; tools come in eight
  tiers from wood to platinum.
- The refining recipes exist for six metals, but the rock crusher and the gem cutter stand only in a test zone for now
  — part of the crafting and resources work that isn't finished (part 6).
- **Underground zones**: two are in the prototype — Underground Passages (the first mine) and the Ant Tunnels — and two
  more are designed, the Ant Colony and the Centipede Cavern.
- Darkness: buried blocks go dark everywhere; the darkness of tunnels so far works only in a test zone and has to be
  brought into the real zones.
- **Not built:** drills, dynamite, carts and rails, the prospecting pan.

**Still open** (→ §14) — how the carrying limit works; the first mine's name ("Mining Camp" in
some documents, "Underground Passages" in others) and its difficulty.

**Proposals for this part:** P20.

### 6 · Crafting and processing
Stations turn materials into better ones over time: workbench, sawmill, furnace, forge, anvil, stonecutter, loom,
spinning wheel, sewing machine, dye vat, bug extractor, crusher, sluice, gem cutter and honey extractor. Materials
climb ladders — ore to bar to alloy, fibre to thread to cloth, log to plank. Some recipes are known from the start; the
rest are bought or found, and most gather in the two towns and the first mine. Crafting and resources are partway done
and need finishing and polish.

**Decided**
- Basic recipes unlock by themselves at their station — every metal tier of tools, weapons and armour included — and
  tools are never locked behind a purchase; décor, furniture and advanced recipes are bought or found (D26).
- **Where a station comes from**: found abandoned in the world, bought from someone, or crafted from a recipe
  (2026-09-27). **Stations that belong to someone** — like those in a mining camp — can't be taken; trying gives a short
  refusal (2026-09-27).
- Cooking is its own system, separate from crafting (D19).
- Leather and a new "wood" armour rung come from processing bugs; players make clothes and a dyer dyes them (August
  2026). **Dyes recolour cloth outfits**, using a recolouring method we build (2026-09-27).
- Making dyes and dyeing cloth are separate stations (2026-06-28).
- The missing stations, and everything else here that doesn't work yet, are part of finishing the system
  (2026-09-27).

**In the prototype now** — 185 recipes on 15 stations. 105 are known from the start; 80 are bought from shopkeepers,
singly or as recipe books, and each character remembers them. The slow stations run two jobs at once; ingredients
leave the bag when a job starts, and results collect in the station's output slots.

**Not finished yet** — three stations (the rock crusher, bug extractor and gem cutter) stand only in a test zone; the
cooking stations have no recipes; eleven stations can't be crafted or bought yet (the Weaver's four and a campfire,
wood stove and keg can); nothing belongs to anyone yet, so any station can be broken and carried off; the eight
floral-furniture recipes can't be learned; there are no bronze tools; the wooden spear, scythe and shovel, the large
net and the backpack can't be bought or made; bookshelves and wine racks accept nothing.

**Still open** (→ §10) — which stations come from where; what the rare recipes are and where they hide.

**Proposals for this part:** P11, P20.

### 7 · Building, pens and homes
The player places blocks, floors, walls, fences, gates, doors, furniture and stations on the grid, builds houses, and
digs with a shovel. Pens are always built, never bought. A private plot, bought through City Hall, is the safe home for
calm, careful farming; decorations there are meant to give small production bonuses that shrink with every duplicate,
so variety pays.

**Decided**
- Private plots from City Hall are safe and central to the design (2026-09-26).
- **Players build houses** — walls, floors, doors — and that works in the prototype (2026-09-27).
- **Players can live in the village** by building their own house there; they can't sleep in a bed that belongs to
  someone, only in an abandoned one (2026-09-27).
- **Doors turn to fit the wall they are placed in**, which needs a second, side-facing door sprite (2026-09-27).
- **Ground is laid in whole squares**; the diagonal shapes go (2026-09-27). How the shovel switches between digging and
  laying is proposal P12.
- Bugs never appear on a floor (December 2025).
- No roofs — the view is from above (D19). Placed objects drop themselves when broken (D22).
- Furniture doesn't rotate (June 2026; confirmed 2026-09-27).
- **Tents are three squares wide** — today's are too small (2026-09-27).
- **Mannequins are overhauled** to show whole outfits, on a plain white-faced figure (2026-09-27).
- Decorative outfits are approved as a class, adding to farm output or happiness the way furniture does; they simply
  haven't been made yet (2026-08-07; 2026-09-27).

**In the prototype now** — about 280 placeable things, placed from the hotbar with a green or red preview; houses can
be built; the shovel lays ground in thirteen shapes (the diagonals go) and digs a cell down to bare soil; a bed sets
where the player wakes; containers have filters (a wardrobe takes clothes, a fridge food).

**Not built** — the private plot's bonuses from decorations; private plots, City Hall and land deeds; floors stopping
bugs from appearing; a limit on how far away a player can place things; items that hang on walls; doors that stop
players; mannequins showing outfits; sorting and quick-stacking in chests.

**Still open** (→ §15) — how big a plot is, what it costs and who may enter.

**Proposals for this part:** P5, P12.

### 8 · Combat and danger
Real-time fights against bugs, with power from gear and preparation rather than levels. Starter areas are cosy, and
danger rises outward from the village. Players fight to sell carcasses or to catch bugs to farm; a big bug, once
subdued and still, is dragged away. Dying costs little — mostly the walk back. Bosses are harder, usually bigger
versions of their species.

**Decided**
- Combat is important and defence is critical (2026-08-06); starter zones cosy, dodge the only defensive move, more
  danger at night (2026-07-11).
- **Danger rises outward from the village**, not by compass direction (2026-09-27).
- **Swarms attack all at once, in sync, as they used to** (2026-09-27) — this replaces a two-at-a-time limit recorded
  in July.
- **Only lunging species wind up before they strike** — millipedes, perhaps scorpions — decided bug by bug for fun and
  fair play (2026-09-27).
- **Axe swings are attacks too**, as well as cutting trees (2026-09-27).
- **Why players fight**: to sell carcasses, or to catch bugs to farm; large bugs, once subdued and still, are dragged
  (2026-09-27) — proposal P15.
- **Dying costs little** — mostly the walk back (2026-09-27).
- **Stamina is allowed** (2026-09-27, replacing the January 2026 "no stamina") — what it is for is proposal P14.
- **Bosses** are fully grown adults, harder and usually bigger; not added at random; perhaps only one at a time; a
  locust swarm is a boss; only species where a fight is fun get one — no aphid boss (2026-09-27) — proposal P13.
- **Aphids live on plants**, seen in the plant's own view the way the milkweed nursery shows its young — tiny bugs on
  flowers, not roaming swarms (2026-09-27).
- Venom and poison are real effects (D16). Spider Vale is the hardest surface zone and the fire-ant domain the hardest
  underground (August 2026). The Ant Colony's queen is a mini-boss (D3; a scripted encounter is acceptable,
  2026-07-06).
- **Enemies come zone by zone**, every one eventually, with test zones where the real zone isn't built yet
  (2026-09-27).

**In the prototype now** — hearts for health; stings and bites take some away; every attack warns before it lands
(to change: only lunges should); a dodge dash; sword and spear with two moves each, and an axe jab (its swing becomes
an attack too); tougher tiers with placeholder names; wasp nests raid; centipedes lunge; fainting costs nothing — the
player wakes at the zone's start point or their bed with everything they carried.

**Not built** — armour protection (armour is looks only, except the bee suit, which stops stings); night danger (no
night hunter yet); bosses; poison and other effects; stamina; bows and other ranged weapons (set aside, D12).

**Still open** (→ §07) — which enemies come in which zone; the boss list (P13).

**Proposals for this part:** P13, P14, P15.

### 9 · Gear: outfits, armour and accessories
One outfit is worn at a time, whole, and can be changed any time from the inventory. Each role — tank, attack,
agility, stealth, mining, fishing, farming, bug-catching, beekeeping — has its own best set, with a few hybrids.
Non-combat outfits usually raise a yield or make a job easier, and their description says how. Legendary sets hide
behind secrets; decorative outfits boost the farm. About 43 sets are in the roster so far.

**Decided**
- **One outfit, worn whole — no pieces** (2026-09-27; drawn whole since 2026-08-05), **changed any time from the
  inventory** (2026-09-27).
- Each role has its own best set; nothing is the best armour in the game (2026-08-06).
- **Non-combat outfits raise a yield or make a job easier**, as their description explains (2026-09-27).
- Nearly every zone hides at least one outfit recipe, calling for materials partly new to that zone (2026-08-06).
- Armour is made *of* a material and never a costume of the creature; faces show (August 2026).
- **Player characters come in several skin colours** — the same base character, recoloured, so no one has to play a
  white character (2026-09-27).
- **The wizard's robe is dropped**; an alchemist's robe comes with a potion station instead (2026-09-27).
- **Accessories need new ideas** — the earlier ones, like the lucky clover, don't fit (2026-09-27).
- Crowns are kept for higher-value armour (2026-08-15). Trinkets and shields are not for now (August 2026).
- **The tiers are still to be resolved**; everything is a work in progress (2026-09-27).
- Four outfits are finished and approved — bronze, fire-ant, black-ant and copper.
- **Armour follows the tool metals**: bug leather and padded cloth, then copper, bronze, iron, steel and cobalt
  steel; platinum goes into fancy armour that also needs steel — the platinum outfit picked — sells well as money,
  and turns up in recipes where it fits (P20, accepted 2026-09-28).

**In the prototype now** — eight equipment slots (head, body, arms, legs, feet, two accessories, backpack). New
characters wear leather. Armour shows on other players but does nothing except the bee suit (stops stings) and a
backpack (more slots — though none can be had yet); the two accessories in the game do nothing. None of the new outfit
art is in the game yet: it still draws the old small layered farmer.

**Still open** (→ §08) — how big the player is on screen; the starting outfit; what else the character screen offers
besides skin colour (class, hair).

**Proposals for this part:** P20.

### 10 · Tools and weapons
Metal tiers plus a few specials that matter (D12): picks in metal tiers only; watering cans small and large; nets small
and large; a saw for big trees; a harvest sickle; smokers in three tiers; fishing rods; the magnifying glass from the
start; a hand bug vacuum; a grappling hook later; bows and cast nets set aside. Light comes from bug lanterns (firefly
and glowworm), torches, a headlamp and electric lights. Tools never wear out.

**Decided**
- **Light comes from several sources**: bug lanterns, torches and electric lights; oil lamps are out (D12,
  2026-09-27).
- **Tools never wear out** — nothing to repair or replace (2026-09-27).
- **No diamond or gold tools** — neither makes sense as a tool (2026-09-27).
- **The swing motions are worked out** (July 2026) — a shovel scoops rather than swings (2026-07-09) — and the
  pickaxe swings like the axe (2026-09-27).
- Metal tiers plus a few specials that matter (D12).
- **The metal ladder** (P20, accepted 2026-09-28): wood → stone → copper → bronze → iron → steel → cobalt steel →
  tungsten carbide for tools; weapons climb the same metals to steel, and past it the best blades and spears come from
  bug parts; no gold, silver or platinum tools or weapons.
- **What a better tool does** (P21, accepted 2026-09-28): a hit does the tool's strength minus the material's
  toughness, so a newly reached ore starts slow and the next tier roughly halves the hits; the ores are the keys;
  power tools, such as a rock drill and a chainsaw, sit in the tiers.

**In the prototype now** — pickaxe, axe, shovel and hoe in eight tiers from wood to platinum, gold among them; the
scythe in seven; sword and spear in eight, gold among them too; saw and harvest sickle; both nets; watering cans;
torch; flashlight; smoker; calm spray; the magnifying glass, which does nothing yet and isn't in the starting kit (the
general store sells it). Every tool moves with a simple motion from June 2026 that has two known flaws — a hard snap
back to rest, and the tool drawing through the body; the worked-out motions aren't in the game yet. An unused wear
value in the data goes.

**Still open** (→ §09) — how many tiers each tool has (the item table); the grappling hook and the specials.

**Proposals for this part:** P20, P21.

### 11 · Food, cooking and potions
There is no hunger. Meals heal and give boosts; potions heal more strongly and give effects food can't; a bandage or a
potion can be used on another player to heal them. Stoves grow from one dish at a time to several. Bug food is a
signature branch — meat from carcasses, honey, royal jelly.

**Decided**
- **No hunger** — meals heal and give boosts (2026-09-27); which meal does what is decided with the recipe list.
- **Potions heal more and do what food can't** — stronger healing and other effects where food doesn't make sense
  (2026-09-27). Potions are ordinary items, not magic (2026-08-06).
- **Healing someone else**: hold a bandage or a potion and use it on them (2026-09-27).
- **Things can be given to other players**, as in Terraria or Stardew Valley (2026-09-27): right-click a player to
  offer an item, bugs or coins; left-click a bandage or potion on a friend to heal them at once; a new action drops
  things on the ground (P17, accepted 2026-09-27).
- **Meals and potions** (P16, accepted 2026-09-27): a meal heals over a while and gives one fullness boost at a time; a
  healing potion heals at once, then the person healed waits a short while before another works on them; other
  potions — antivenom, a salve for sprays and acid, venom resistance, night sight — have no wait; stronger bugs make
  stronger potions; the cauldron is the potion station; food doesn't spoil in bags or chests.
- Cooking is its own system (D19); venom and poison are real effects (D16).

**In the prototype now** — food items exist and sell, but eating does nothing. No meals exist, the cooking stations
have no recipes, and health comes back only by slowly regenerating.

**Designed** — the old catalogue lists about 78 potions and 47 meals, weapon coatings among them (P16 cuts it to a
small starting set); eating fruit to heal; fridges that stop food rotting (under P16 food doesn't spoil, so the fridge
is a food chest).

**Still open** (→ §11) — the recipe list, which meal does what, and whether a venom coating joins the starting set.

**Proposals for this part:** P16, P17.

### 12 · Fishing and water
Fishing starts in the starting village, at its lake and the fisherman's house, with rods, bug baits, fish traps and
boats. Water divides the map: rivers, lakes and the sea keep areas from running into each other, without having to sit
exactly on zone borders. Shallow water can be waded slowly in a wading outfit; deep water always takes a boat. There are no separate sea zones: the coast comes into the western and eastern
zones, and off the west coast at least one inlet holds an island shaped like a bug, with little inlets making its legs.

**Decided**
- **Fishing starts in the village**, at its lake and the fisherman's house (2026-09-27).
- **Crossing water**: shallow water can be waded, slowly, by a player in a wading outfit; deep water always needs a
  boat; there is no separate waders item (2026-09-27).
- **Natural barriers** — rivers, lakes, the sea — keep areas from mixing too much, and needn't match zone borders
  exactly (2026-09-27).
- **No sea zones**: the coastline comes into the western and eastern zones, with at least one inlet off the west coast
  holding a bug-shaped island (2026-09-27).
- No diving (August 2026); fishing outfits carry fishing and boat-speed bonuses (August 2026); rods with a mini-game,
  fish traps, no harpoons (D12); bugs fly over water (2026-06-11).

**In the prototype now** — nothing to play. The village has its lake, the fisherman's house and his boat store with a
dock, but the Fisherman himself was left out when the village was saved (his spot is blocked). Docks and fishing props
are decoration. Every water tile stops players; bugs fly over water.

**Designed** — a dredge set on the water and worked with a hose, in tiers (D14).

**Still open** (→ §13) — how the fishing mini-game plays.

### 13 · Towns, shopkeepers and trade
A safe starting village full of shops; a second town — a small western-style town in the Locust Farmland — and the
first mine, where most recipes gather. Shopkeepers sell tools, seeds, recipes and recipe books; the Mayor sells land.
Trading takes coins or goods: a townsperson may take goods of the kinds they deal in instead of coins, as in Baldur's
Gate. Coins come from many sources. Townspeople live in their town: they keep their shops, do the chores, and sleep at
home at night, and several of them give quests.

**Decided**
- **Coins and barter**: one coin, and bartering too — goods can be offered instead of coins to a townsperson who takes
  that kind of goods, as in Baldur's Gate (2026-09-27; replaces "no bartering" in D6). **Coins come from many sources**
  (2026-09-27).
- Which shops the village has (D20, D26), and what the village still needs: its townspeople and their behaviour,
  better buildings and layout, polish, and secrets (2026-09-26).
- **Townspeople** mend fences, gather fruit, deal with pest bugs and more — whatever makes the game better — and sleep
  in their houses at night (2026-09-27). Shopkeepers keep their counters by day, chores fall early and late or to
  townspeople without a shop, and at night players simply walk in and trade with them at home (P18, accepted
  2026-09-27).
- **Trading** is one screen with what you give and what you take; goods count at the price that townsperson pays,
  and coins make up the difference either way (P19, accepted 2026-09-27).
- **Quests from several townspeople**, not only the Ecologist (2026-09-27): the myrmecologist has quests and a board of
  retrieval jobs, some of them out of reach until later. **No bounties** (2026-09-27).
- **The second town** is a small western-style town in the Locust Farmland (2026-06-27) — a small village with shops and
  people of its own, which needs more townspeople — with strings of lights and other electric things (2026-09-27).
- **The starting village is mostly unpowered**: its windmill lights only part of it, such as the Mayor's house — a
  glimpse of what power will bring. Players can't take it (2026-09-27), and can buy or build a windmill of their own
  only after reaching the Locust Farmland (2026-06-27).
- A myrmecologist — an ant specialist — sells from a wooden building at the Ant Tunnels' entrance (2026-07-07).

**In the prototype now** — eight shopkeepers in the rebuilt village (general store, Bug Dealer, blacksmith, carpenter,
weaver, stonemason, modern wares, Ecologist) and Maren in the Bee Meadow; the Mayor is there too, and talks, but sells
nothing yet. Players start with no coins. Shops sell items, single recipes and recipe books, though the shop screen
shows only a shop's first six goods, so most of the general store's stock can't be bought yet; six shopkeepers buy
things — the player's bag opens beside the shop, they move what they want to sell into a small "to sell" box, and one
button sells it all for coins; talking to someone shows a portrait and a greeting; a check stops buy-low, sell-high
loops.

**Not built** — bartering; land deeds; the Fisherman; townspeople who work, walk about or sleep; quests; the second
town; the shops at the mine; the myrmecologist.

**Designed** — quests that are optional, grow out of what is happening in the world, can be solved several ways and
are never forced (January 2026); which townspeople give which quests isn't designed yet.

**Still open** (→ §16) — prices overall; the quests themselves.

**Proposals for this part:** P6, P18, P19.

### 14 · The world and exploring
Twenty zones of 256 by 256 squares on a grid five rows deep and four wide — three rows of surface, two underground —
around the starting village. Danger rises outward from the village and going deeper; rivers, lakes, cliffs and the
sea keep areas apart, with crossings; the coast comes into the western and eastern zones. Every zone is meant to have
named places, landmarks and secrets, and signposts give fast travel.

| | west | | | east |
|---|---|---|---|---|
| far north | Locust Farmland · the western town | Millipede Forest | Spider Vale West | Spider Vale East |
| north | Hilltop Meadow | Butterfly Fields | Scorpion Rocks | Deep Swamp |
| the village's row | **Bee Meadow** — in the prototype | **the Village** — in the prototype | Wasp Thicket | Shallow Swamp |
| underground | **Ant Tunnels** — in the prototype | **Underground Passages** (the first mine) — in the prototype | Underground River | Deadly Ants outpost |
| deep underground | Ant Colony and its queen | Centipede Cavern | the deep river's sunken ruins | Deadly Ants core |

**Decided**
- The grid and its orientation (north at the top, underground to the south); the second town in the Locust Farmland
  (2026-06-27).
- **Bugs cross from one zone to the next, but each species only spawns in its own spawn areas** (2026-07-06;
  2026-09-27). How they cross is left to me: whole swarms migrate (2026-09-26).
- **Every zone built so far gets redesigned**, now that zones can be designed much better; some houses also don't
  meet the roads properly (2026-09-27).
- **Secrets everywhere**: the small underground fortress holding the Queens' set in a locked chest (2026-08-06) is one
  example among many, not the only secret (2026-09-27).
- Objects need a reason to be there; no standalone rocks; wild zones are wooded by default, with clearings; zone
  borders blend on gradients; the view is from above, so caves show no ceilings; the village gets secrets
  (2026-09-26).
- The coast and the bug-shaped island (part 12).

**In the prototype now** — four zones, joined by walking off their edges: the rebuilt village, the Bee Meadow (sea,
coves, Maren's farm, a fishing hamlet), Underground Passages and the Ant Tunnels. New players are still sent into an
old version of the village, which isn't one of the game's zones. The Ant Tunnels were built after the owner went
through their design line by line (2026-07-07); the Ant Colony and the Centipede Cavern are designed but not built.
There are test zones for trying things. Bugs can't yet cross from one zone to another. No map, no fast travel, no
working signposts.

**Designed** — economy sheets for seventeen zones, fuller zone designs for seven, landmark lists for four; secrets such
as hermit cabins, special merchants and hidden caverns.

**Still open** (→ §01, §17) — a few places where documents disagree (where the ranger station is; Spider Vale East
called the "western edge"), to be resolved together (2026-09-27); how fast travel is unlocked.

**Proposals for this part:** P25.

### 15 · Progression and tiers
The player moves up by getting better tools, which open harder ore, which makes better bars and gear, which open
harder and deeper zones and new materials. The food chain is the other ladder: to keep bigger bugs, farm the smaller
ones. It is an open world with no ending: the hardest zones hold the bosses and the legendary sets, and some quest
lines lead there, but every player plays it their own way.

**Decided**
- Progress through gear and preparation, gated by cost; no storyline (2026-09-26).
- **An open world with no ending**: there is no game over and no finale; the legendary sets are powerful and come
  from the hardest zones; some quest lines lead there to fight bosses; players play however they like, as in Terraria
  (2026-09-28).
- **The basic stations are in the village** — the anvil, the forge and the other basic stations stand at the
  blacksmith's and the other shops. Players can use them once they have the materials, and can't take them, since
  they belong to the townspeople. Other stations turn up in other places, mostly the first few zones, and powered
  versions arrive once the player reaches a place where generators can be bought or built (2026-09-28).
- **The metal ladder** (P20) and **what a better tool does** (P21) — both accepted 2026-09-28: eight rungs of real
  tool metals, and a newly reached ore starting slow, with the next tier roughly halving its hits (Terraria's tiers
  don't halve the effort; they mostly decide what can be mined).
- **Every item gets a thorough pass for taste**: the old lists were written without much taste, and many of the
  accessories will probably go; I give the owner a table of recommended additions, changes and cuts covering every
  item in the game (2026-09-28). So cutting content is on the table, and D4's "tuning never deletes content" no
  longer holds.
- No rule is forced on every zone (2026-09-26).

**In the prototype now** — tool tiers gate ores; 80 recipes are bought from shopkeepers; better bars and tools cost coins;
backpacks would add bag slots (none can be had yet). No experience points and no skill levels.

**Designed** — about five tiers across three phases, each a complete chapter; iron a few sessions in; each new tool
roughly halves the effort of gathering (P21 checks this); the player can always name the current goal and the next
two (the economy's progression design).

**Still open** (→ §02) — the item table (next).

**Proposals for this part:** P20, P21.

### 16 · Power and automation
An optional industrial route for later: wind turbines and solar panels make powered areas; powered versions of
gardening and bug-farming tools and of stations; batteries before a recharger; power lines. Early farming is done by
hand, and automation comes from stations and tools as the player reaches them — there are no hired workers. Machines
ease chores, and they never play for the player.

**Decided**
- Power from wind turbines and solar panels, with powered tools and powered versions of stations; the details are
  mine to design (2026-09-26); the electronics are bought, never player-made (D1, D26).
- **No hired workers**: automation comes from stations and tools as the player reaches them, and the early ones are
  more manual (2026-09-28). This replaces the NPC workers of the older designs.
- **Sprinklers**: small ones are sold in the village, but they cost enough that the player saves up for them;
  larger ones come from other places, such as the western town; the rest of the design is mine (2026-09-28) —
  proposal P22.
- **Modern Wares sells powered things before the player can power them** — a player who wants to can set up just
  outside the Mayor's house and run them on his power (2026-09-28).
- **The Mayor's house has powered things the player may use**, such as a fridge; everyone else in the village lives by
  torches and bug lanterns (2026-09-28). The village is otherwise unpowered (2026-09-27), and players can buy or build
  a windmill only after reaching the Locust Farmland (2026-06-27).
- **Sprinklers water whatever is in reach**, fruit trees included, and crops need one watering a day (2026-09-28);
  a hand pump feeding the sprinklers, then a powered pump, is the owner's idea, worked out in P22.

**In the prototype now** — nothing runs on power yet; the windmill, electric fence, heater, fridge, stove and floor
lamps exist as objects only. There are no sprinklers.

**Designed** — a power unit powers every square within a radius, shown while placing it; fuel-fed machines (a wood
stove) come before electric ones; power lines are laid with a line tool; stoves grow from one dish at a time to a
four-burner range (January 2026); electricity is a wealth-gated expansion bought from a shop (the economy
catalogues).

**Still open** (→ §12) — the pump and sprinkler ladder (P22, revised).

**Proposals for this part:** P22.

### 17 · Time, weather and light
**Decided**
- No seasons (January 2026; confirmed 2026-09-27); the underground is pitch dark (2026-07-08).
- **One clock for the whole world**: every zone shows the same time of day, so walking into the next zone never jumps
  from day to night (2026-09-28).
- **No skipping the night**: sleeping doesn't move time on, since this is a multiplayer game; the world stops only
  when no player is online (2026-09-28). A bed sets where the player wakes.
- **Empty zones stay frozen and catch up on the first visit** (2026-09-26), **with random border events**: while a
  zone is frozen, a few of its bugs now and then turn up at the edge of a neighbouring zone that has players
  (2026-09-28) — proposal P25.
- **Droughts are part of the game**, like rain; both need tuning (2026-09-28).
- **Balance doesn't lean on the weather.** The prototype's balancing system calls a drought or extra rain whenever a
  species runs too high or too low; that kept happening and made for poor play. Balance comes from many levers, and
  if it leans on weather events too much, the other levers get rethought (2026-09-28).
- **Retuning is part of the bug overhaul**, and comes after bug behaviour has been polished and updated, because
  bugs that behave differently change the numbers. Everything is retuned anyway, since fallen fruit is being cut
  (2026-09-28).
- **Border events** work as P25 describes (accepted 2026-09-28): a few bugs wander over from a frozen neighbour's
  surplus, the exchange runs both ways, and a dangerous zone never trickles into a safe one.

**In the prototype now** — a 14-minute day and a clock; golden dusk and dawn; nights dark enough to need a torch or
lamp; rain on some days, with thunder; fruit falls in the evening. The balancing system starts droughts and extra
rain to steer species numbers, and each zone keeps its own clock and stops when it is empty, so two zones can show
different times of day — both go. A bed only sets where the player wakes.

**Designed** — one clock for the whole world (the roadmap).

**Still open** (→ §18) — how often rain and drought come once they no longer steer the ecology.

**Proposals for this part:** P25; P10 covers the tuning.

### 18 · Playing together
**Decided** (2026-09-26) — Terraria-style hosting; our own server is just another server, and each server holds as
many players as is measured to work; players join by typing an address, with Epic's free relay first and Steam
later; each world keeps its own characters, with a setting that lets a host admit characters from other worlds; a
lawless shared world and safe private plots. Everything in the world persists (D31).
- **Everything in the shared world runs the same for every player** — nothing goes faster for one player than for
  another (2026-09-28).
- **No limit on characters per account** — they cost nothing to make (2026-09-28).
- **Fights between players only if the server allows them**: the game is about players against the world, but a
  server can switch player-versus-player on for those who want it (2026-09-28).
- **Private plots are invite-only**, which keeps griefing down. They follow the January 2026 plot design — small
  production bonuses from decorations, less for each duplicate, up to a cap; nothing damaged while the owner is
  away — and need their own panel for the happiness level and the bonuses (2026-09-28) — proposal P26.
- **What runs on the server gets a thorough review.** The game began with the server running everything, then moved
  to every player's computer running the same simulation in step; whatever still runs on the server has to justify
  its place. This is one of the most fragile parts of the game (2026-09-28).
- **The plot's happiness** works as P26 describes (accepted 2026-09-28): a badge and a panel, decorations raising the
  plot's crops and stations up to a cap, each copy counting half the one before.

**In the prototype now** — each zone is shared, every player sees the same bugs, and players who join late see everything as
it is. An account holds up to eight characters (the limit goes); zones save every ten minutes; the server decides
damage, catches, inventories and prices (under review).

**Not built** — reconnecting after a dropped connection; chat; trading between players; the hosting menus; private
plots. Two known faults: two players arriving at once can create two copies of a zone, and a failed zone crossing can
strand a player.

**Still open** (→ §19) — what a server's player-versus-player setting covers.

**Proposals for this part:** P26; P17 covers giving things.

### 19 · The interface and learning the game
**Decided**
- Examining an item or a recipe shows what it does and its real biology; tutorials unlock as the player goes
  (2026-09-26).
- **Every system gets a polishing pass, the interface included**, with my suggestions from taste and good game design
  (2026-09-28).
- **Tutorials are mine to design** (2026-09-28): some come from townspeople as the first quests, some unlock on
  joining, some when the player reaches a new area, and many end with a task that leads into the next — often back
  at a townsperson who sends the player on to another — proposal P23.
- **Controls and settings are mine to design** (2026-09-28) — proposal P24.
- **Lessons** work as P23 describes and **controls and settings** as P24 (both accepted 2026-09-28): a first chain
  through the village's townspeople, tips the first time something happens, a Journal; genre-standard keys, R for
  a tool's mode so the wheel stays on the hotbar, everything rebindable.

**In the prototype now** — a hotbar and an inventory at the screen edges while the world keeps running; one panel for crafting,
storage, compost, nurseries and hives; a "to sell" box in shops; hearts; the clock; a bug card; a message for most refused
actions (nursery deposits still fail silently); character select, the opening text and the title screen. Hovering
shows only a name — 2 of the game's 654 things have a description.

**Designed** — a bar of buttons for the inventory, Ecologist, Mayor and Herbalist; tutorials; the Ecology tab; station
panels with their own look; Terraria-style controls — keys to move, the mouse to aim and use tools (December 2025).

**Still open** (→ §20) — the lesson lines for each townsperson, written with the townspeople's redesign.

**Proposals for this part:** P23, P24.

### 20 · Art and sound
**Decided**
- **Most art is made with gpt-image-2 and pixel-snapped**, 32 art pixels to a square, regenerated after sign-off in
  test batches; every paid image call asked for first (2026-09-26).
- **The interface and the blocks are mine to draw in code**, improved over several rounds with the owner —
  gpt-image-2 draws blocks poorly — while characters stay with gpt-image-2 (2026-09-28). This narrows 2026-09-26's
  "code-drawn art rejected" to characters.
- **Townspeople** are drawn by gpt-image-2, each with walking frames and floating hands like the player's, and a
  matching face portrait for conversations; their looks are left to gpt-image-2, and they are people of many
  ethnicities (2026-09-28).
- **The look gets a polishing pass**: lighting, which falls short of Necesse and similar games (Unity's screen
  effects may help); clearer signs of hitting and being hit; wind sway done the way good games do it, and only on
  plants (2026-09-28).
- **Sound and music are mine to make**, by whatever method works best, without paid services; the owner has music
  packs, and each zone can have music of its own (2026-09-28).
- Earlier (2026-07-08): a look of its own — other indie games, Apico among them, are examples and not targets — with
  subtle bloom, a pixel-perfect camera and one colour grade. Necesse is the target for the grass (July 2026). The art
  guides set the style: seen from above at an angle, lit from the top left, chunky pixel art with three to five
  shades per material, and every sprite facing the camera.

**In the prototype now** — about 775 images from the older route, not pixel-snapped; four approved outfits made the new way but
not yet in the game; dark nights with lamps and torches, animated water, swaying plants, dust and shadows; the grass
overhaul (July 2026). About 25 solid things sway in the wind too — standing stones, crystals, stumps, nests, a
shipwreck — because swaying follows the "natural" category. The bloom, the pixel-perfect camera and the colour grade
are not built — the screen-wide effects are switched off. Sound is eight simple effects generated in code (hit,
kill, sting, faint, thunder, hiss, chewing, axe); there is no music, footsteps or background sound, though a library
of 203 bug sounds and music tracks sits in the repo, unused.

**Still open** (→ §21, §22) — how the sound library and the music are made.

## As built
**What a new player can do in the prototype now.** Make a character and watch the opening; arrive wearing leather with wooden tools,
a small net, a watering can, three kinds of seeds, torches, a flashlight, fencing for a pen and no money; catch flies,
butterflies and other small bugs; breed bugs in a compost bin; grow seven crops and pick fruit; mine ore (though not
refine it); buy copper to steel bars and craft at eleven working stations; buy from eight shopkeepers and sell to
six; fight wasps and centipedes; and walk between the four zones. They can't yet cook, fish, eat to heal, use power,
travel fast, read an Ecology tab, or get anything from armour except the bee suit.

**Unfinished, or different from the design** — the prototype is partway done; these are the places a player would
notice, each on the backlog:
1. New players are sent into an old version of the village, which has no shops; the rebuilt village is the start.
2. The rock crusher, bug extractor and gem cutter stand only in a test zone for now: mined ore can't be refined,
   carcasses can't be processed and gems can't be cut, and silver, gold and platinum are out of reach.
3. Wasps, hornets and dragonflies need the large net, which can't be bought or made; centipedes need a trap, and there
   is none; no backpack can be had either.
4. Eleven of the fifteen stations can't be crafted or bought yet, and nothing belongs to anyone yet, so any station
   can be broken and carried off.
5. No bug hunts at night, so nights add no danger yet: real wasps and hornets hunt by day, and night danger waits for
   a real night-active species.
6. The Ecology tab doesn't exist, although the roadmap's opening brief assumed it did (a note there now corrects
   it); the magnifying glass does nothing and isn't in the starting kit, although D12 says it should be.
7. Floors don't stop bugs appearing; no door stops players; mud doesn't slow anyone, and all water stops everyone
   (shallow water is meant to be waded in a wading outfit, part 12).
8. Wheat is still sold and planted in the village.
9. The autonet doesn't catch anything; the rebuilt village's beehives never come alive; mannequins don't show
   clothes; the Fisherman is missing from the village.
10. Breaking a full compost bin leaves an invisible food source behind; wild bug broods on the ground can't be seen;
    milkweed and compost bins can't be seeded from empty, and nursery refusals give no message; breaking the gem
    cutter drops a rock crusher.
11. At 88 places, walking off one zone's edge would put the player inside rock or a wall on the other side (35 of them
    boxed in); the fix is decided — land on the nearest open ground.
12. Each zone has a hard ceiling per species, while the design uses the ecology's many levers instead.
13. Prototype rules that were never the design: bees, dragonflies and fireflies fly over fences; wooden fences are
    chewable by centipedes and stone stops them; carrion beetles make compost; centipedes move as packs; "most bugs
    can be calmed"; invented species names (the soldier wasp, the giant hornet); every attack giving a warning; at
    most two attackers at a time.
14. Rain waters crops and trees but doesn't show it (part 4); the darkness of tunnels works only in a test zone
    (part 5); tents are too small (part 7).
15. Tools come in gold, which goes, and carry a wear value that nothing uses (part 10).
16. The shop screen shows only the first six goods of each shop: the general store's net, watering cans, wooden
    tools, calm spray, magnifying glass, gloves, cot, torch, lantern and fence, and the blacksmith's axes, weapons and
    armour, can't be bought. The carpenter buys no furniture (the "furniture" it asks for matches no item), and the
    blacksmith buys ore as well as bars.
17. A hit does one point of damage whatever the tool, so tool tiers only decide what can be broken, and the top three
    pickaxes open nothing; two players hitting the same block restart each other's progress; with the shovel in hand
    the mouse wheel can't reach the other hotbar slots (parts 10, 15 and 19).
18. Solid things such as standing stones, crystals, stumps and nests sway in the wind with the plants; the balancing
    system steers species numbers with droughts and extra rain; each zone keeps its own clock (parts 17 and 20).

Some documents are also plainly out of date against the game — recipe counts, net sizes, hive types, the lighting
document, rotting fruit, the zone scale. I'll correct each as its section is rebuilt.

## Proposals
### P1. Where a later owner decision replaced an older text, the later one stands
*The whole document.*
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
- building only the village and the first mine (D17, June 2026) → all twenty zones, ring by ring (the approved
  roadmap, 2026-09-26);
- fishing left out of the first release (D5) → fishing from the start, in the village (2026-09-27);
- no bartering (D6) → coins and barter, as in Baldur's Gate (2026-09-27);
- waders for the marsh (D10) → a wading outfit for shallow water; deep water always takes a boat (2026-09-27);
- tools that wear out (the durability in the economy designs and the item data) → tools never wear out (2026-09-27);
- NPC workers on farms and plots (December 2025; January 2026) → no hired workers; automation comes from stations and
  tools (2026-09-28);
- no end-game (January 2026) → an open world with no ending, whose hardest zones hold the bosses and the legendary
  sets (2026-09-28);
- the anvil and forge kept out of the village (some economy documents) → the basic stations stand in the village, at
  the blacksmith's and the other shops (2026-09-28);
- tuning never deletes content (D4) → every item gets a pass that may cut it (2026-09-28).

The three disagreements this list couldn't settle are now answered: outfits are worn whole, one at a time (D47,
2026-09-27); the armour ladder and where the metal ladder stops are mine to recommend (P20, 2026-09-28).

**Lenses:** Don't reopen settled decisions — each replacement is a later owner decision or the approved roadmap.
Already covered — nothing here is new design.

### P2. No magic
*Part 0 · what belongs in the world.*
The world is 2126 science. The magic and fantasy races in the old brainstorms — enchanting, arcane tools and books,
magic bait, dwarven ruins — are dropped. The deep fantasy metals the backlog planned for end-game gear (mithril,
adamant) go too; P20 recommends real metals instead. The wizard's robe is dropped for an alchemist's robe (D47).

**Lenses:** Premise — people survived a plague by breeding bugs, and science is how the world works. It extends two
narrow rulings of the owner's: potions are ordinary items, and the fancy plate is non-magical. Surprise — the wonder
comes from real biology (the examine texts), not spells.

### P3. Catching: hand nets for the small ones, placed catchers for everything bigger
*Part 1 · catching and farming bugs.*
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
Every catcher takes bugs out of the world, keeps them alive (except the zapper), and is emptied by hand — small
bugs into the bug bag, big ones dragged out (P15).

**Lenses:** Premise — sized for giant bugs, with no tiny-bug tools (the pooter and the Berlese funnel were rejected
for that reason). Real biology — interception nets, pit traps and light traps are how bugs are really caught. Economy
— small capacities and hand-emptying keep the January rule that machines ease chores, never play. **Cost and risk:**
placed catchers are new objects in the shared bug simulation (every player must see the same bug caught), and each
size needs art; balancing them against the hand net will take several passes.

### P4. Traps and bait without the silliness
*Part 1 · catching and farming bugs.*
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
*Part 7 · building, pens and homes.*
- **Building**: place a post; drag to another post along the grid and rails fill the run; pieces join up on their
  own — straight runs, corners, T-joins, crossings and gates. The simulation still sees fences square by square, so
  the shared bug simulation doesn't change; only placing and drawing do.
- **Different bugs damage fences in different ways, and each material resists each way differently**, so no material
  is best against everything: real wasps scrape wood fibre off fences to make their paper nests; big beetles shove;
  some bugs never touch a fence. (The prototype's centipede chewing wood goes — real centipedes don't.) Numbers are
  set when the ecology is tuned.
- **No bug flies over**, as decided — so a fence also keeps out bees and other pollinators, and a fenced garden needs
  a way in for them (a gate, a gap, or a plant barrier, P8).
- **Private plots are safe**: they are invite-only (2026-09-28), and nothing damages a fence on a private plot while
  its owner is away (the January 2026 rule).

**Lenses:** Readability — a pen reads as a pen, a gap as a gap. Real biology — damage comes from what each bug really
does. Economy — materials become a choice, not a ladder with one answer. **Cost and risk:** the joining pieces need a
sprite for every shape and material (fewer if posts and rails are drawn separately and combined); the pollinator
consequence is real and needs a design answer, not an afterthought.

### P6. Village property and repairs — now covered by your rulings
*Part 13 · towns and shopkeepers.*
- Players can't damage or take the townspeople's things; bugs can damage village fences, and villagers mend them
  (D41) as part of their daily round (P18, accepted).
- There are no hired workers (2026-09-28).
- One build detail is left: the village's own fences, buildings and goods are marked as the village's when the zone is
  made. Today a placed object records only what it is, where it faces and any sign text, so this mark is new.

**Lenses:** Fair start — new players can't strip the village for early money. **Cost and risk:** an ownership mark on
every authored object in the village.

### P7. Butterflies grow up out in the world
*Part 2 · the bugs themselves.*
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
*Part 3 · the ecosystem and the Ecologist.*
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
*Part 3 · the ecosystem and the Ecologist.*
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
- **Other quest-givers**: the Ecologist's quests are the ecology ones; other townspeople give their own (P18), and
  some quest lines lead into the hardest zones and their bosses (2026-09-28).
- **Rules**: quests belong to each player; the zone's balance is shared, so everyone benefits from a fixed ecosystem.
  No outbreak or mini-boss comes to a private plot while its owner is away.
- **The tab**: for each zone with a station, each species' numbers over time against its healthy range, and that
  zone's quests with their progress; zones without a station stay blank.

**Lenses:** Player agency — every problem has several solutions (a January 2026 pillar). Real biology — biological
control, restoration and mark-and-recapture are real ecology. No forced chaos — quests come from real conditions and
are optional. **Cost and risk:** a quest system is a new system; the rules against farming paid quests need testing;
multiplayer ownership needs care.

### P10. Ecology tuning — several food chains, fewer fruit, habitat instead of hard caps
*Parts 3 and 17 · the ecosystem; time and weather.*
- **Several food chains, some short and some tall**, as decided — for example: rotting fruit and compost → flies →
  wasps; flowers → bees → hornets; milkweed → caterpillars and butterflies → wasps; carcasses → carrion beetles;
  leaf litter → millipedes. Each is tuned on its own.
- **Fewer fruit on the ground** (as asked — for looks, since hundreds of fruit lying about look ugly; the flies are
  retuned to live on less, 2026-09-28): first shorten how long uneaten fruit lies before it rots away, then lower
  the fruit per tree if needed. Wild zones have no compost bins, so the flies' food there has to come from the land
  itself — carcasses, rot and plants. The prototype's fly data still lists a manure pile among its breeding places
  (unused), and that goes with everything else from the mammal world.
- **Habitat instead of hard caps**: each species needs its own kind of place — flowers, rot, water, shade — and a crowd
  thins where there isn't enough; today's fixed ceilings stay only as a high safety net.
- **Bosses set off by conditions** (decided) follow real biology where they can — crowded locusts really do change
  into swarming locusts; how bosses come about is proposal P13.
- **Players may tip the balance** (2026-09-28): changing the ecosystem, for better or worse, is the point of the
  game — a player who waters an orchard into a fly boom is free to, and the caps are the safety net (D62).
- **No steering by weather** (2026-09-28): the prototype's balancing system that calls droughts and extra rain when a
  species runs too high or too low goes. Rain and drought keep a rhythm of their own, and balance comes from the
  levers above.
- **Behaviour first, then numbers** (2026-09-28): bug behaviour is polished and updated before any tuning, and the
  whole retune is part of the bug overhaul.

**Lenses:** The owner's direction — many levers, not hard caps. Readability — the player can see why a population
moved. Real biology — the locust change is real. **Cost and risk:** habitat-based limits are a real change
to the shared simulation and need the determinism checks; each food chain is its own tuning job.

### P11. Cutting plants down, and simple stations for what you cut
*Parts 4 and 6 · farming; crafting.*
- **Harvesting takes the product** — fruit, grain, flowers or leaves — and sometimes a seed. Most crops are gone once
  harvested; fruit trees, bushes and some crops keep producing.
- **Cutting down removes a plant that would otherwise keep going** and gives its materials straight away — wood,
  fibre, straw, stalks. Hands harvest; the axe, scythe or shovel cuts.
- **Processing is one simple step**, the way Stardew Valley's machines work — put something in, take something out:
  - fibre → thread and cloth, on the spinning wheel and loom the game already has;
  - wheat → grain and straw when cut; a mill turns grain into flour;
  - fruit → juice in a press, for the keg once drinks arrive;
  - flowers, leaves and roots → dyes at the dye station;
  - herbs → potion ingredients at the potion station;
  - straw → mulch that keeps a plot wet longer, a straw beehive, a straw hat; anything left over → compost.
- Milkweed is the butterflies' nursery, so cutting it down ends the nursery on it.

**Lenses:** Game first — one step per station, no realistic sub-steps; the real biology stays with the bugs and the
ecology. Economy — ties farming to cloth, potions, beekeeping and compost. **Cost and risk:** a mill and a press are
new stations; the rest exist or are already planned.

### P12. One shovel, a clear switch between digging and laying
*Part 7 · building.*
- **The shovel does both, and R is the switch** (my change from the mouse wheel, so the wheel always stays on the
  hotbar — P24; R no longer rotates anything): pressing it steps through **Dig** and each kind of ground the player
  has materials for — dirt, grass (laid from turf), sand, stone path, wooden floor — each with its count; Shift + R
  steps back. When the chosen ground runs out mid-path, the shovel falls back to Dig and says so.
- **The choice is always visible**: the shovel's hotbar slot shows the current mode's icon, the cursor matches (a spade
  for digging, a square of the chosen ground for laying), and a short label under the cursor names it.
- **Laying uses the raw materials**, as today — stone for a stone path, planks for a wooden floor, sand for sand — one
  whole square at a time; the diagonal shapes go, as decided.
- **What goes**: the hidden Shift-to-dig and the separate materials panel. Right-click stays free for doors, beds,
  stations and signs, as it is now.
- The same idea in a well-liked game: Valheim's hoe is one tool with a small menu of ground jobs, and paving it costs
  stone.

**Lenses:** Readability — the mode is on screen at all times, never a hidden key. The owner's ruling — one shovel, a
clearly shown switch. **Cost and risk:** small — one key and icons for each ground kind; the wheel stops being taken
over by the shovel, which today traps it there.

### P13. Bosses: the biggest of a few species
*Parts 2 and 8 · the bugs; combat.*
(The zone designs call them mini-bosses; this uses "boss" for both.)
- **A boss is the biggest of its kind, for real reasons**: queens are far bigger than their workers; larvae that feed
  well grow into bigger adults; and many centipedes and millipedes keep growing through their lives, so their oldest
  really are the biggest. (Insects don't grow once they are adults.) Only species where a big fight would be fun get
  one — no aphid boss.
- **Only one boss per zone at a time** — my reading of the owner's "perhaps only one".
- **Where they come from** — never at random:
  - **placed**: some live in a place made for them, like the Ant Colony's queen in her chamber;
  - **grown**: when a wild population thrives for long enough, one of its young is fed into a giant, or a nest raises a
    new, huge queen. The Ecologist warns about it in any zone with a monitoring station;
  - **swarming**: a locust swarm is a boss made of many — real locusts change into swarming locusts when they crowd —
    beaten by thinning it until it breaks up.
- **What a boss leaves**: its carcass, like any bug, and the bug extractor turns it into materials only a boss gives; a
  mounted carcass makes a trophy. Recipes come from the Ecologist's quests (P9). A queen might even be caught alive —
  a queen founding a colony on your farm.
- **Consequences**: killing a queen ends her colony until a new queen founds another. Bosses have a lifespan like any
  bug.
- **Safe places**: a boss never grows from penned bugs or on a private plot, and a swarm never enters a private plot.

**Lenses:** Real biology — queens, well-fed larvae, lifelong growth in centipedes, crowding locusts. Curiosity and
surprise — a neglected nest becomes an event, with warning. No forced chaos — conditions the player can see coming.
**Cost and risk:** each boss is its own art, animation and fight design; a swarm boss is expensive for the shared
simulation (many bugs at once); "grown" bosses need the ecology to track how long a population has thrived.

### P14. Stamina for dodging
*Part 8 · combat.*
- **Stamina is a small pool of dodges**: each dodge spends some, and it refills on its own in a few seconds. Today the
  dodge has a fixed wait between uses; a pool lets a player chain two or three dodges in a tight spot, and lets gear
  make it bigger or refill faster.
- Nothing else uses it — no sprint unless the owner wants one, and tools, farming and catching never tire the player.
- **Food helps before a trip**: once cooking arrives, some meals give a timed boost to stamina — a bigger pool or a
  faster refill — eaten to prepare for a hard zone.

**Lenses:** Combat — the dodge becomes a resource to manage, not a free escape. Fairness to the player's time — daily
work never waits on a bar. Economy — food gets a purpose without hunger. **Cost and risk:** a small bar on screen; the
bugs' attack timing has to be retuned around it.

### P15. Moving big bugs: grab and drag
*Parts 1 and 8 · catching; combat.*
- **A big bug can be grabbed once it is subdued and still** — calmed, or worn down in a fight (the backlogged
  "weakened" catch) — or dead. Stand next to it and press E; press E again to let go. The E prompt looks like the
  game's other prompts.
- While dragging, the player walks slowly, can't use tools, and drags one bug at a time.
- Drag a live one into a pen to keep it, or a carcass to the bug extractor or a buyer. A subdued bug left alone wakes
  and goes back to what it was doing; a carcass left behind rots and feeds the carrion beetles.
- **Placed catchers holding big bugs** (P3) are emptied the same way: open it, and the bug is dragged out rather than
  going into the bag.
- It ties to the carrying limit (D43): a hand cart can come later for hauling more at once.
- Dragging across a zone's edge needs bugs to cross zones for real, which is planned but not built.

**Lenses:** Picture the moment — hauling a giant beetle home across the meadow. Readability — "too big for the bag"
always has an answer. Real biology — carcasses feed the scavengers. **Cost and risk:** a dragging animation for every
large species; a clear look for "subdued"; crossing zones waits for cross-zone bugs.

### P16. Food for a trip, potions for a fight
*Part 11 · food and potions.*
**Accepted by the owner on 2026-09-27**, with seeing in the dark kept in.
- **A meal heals you over a while and gives one fullness boost** — a bigger stamina pool (P14), quicker work, a
  better catch. One boost at a time: a new meal replaces the last, as in Stardew Valley. Which meal does what comes
  with the recipe list, as decided.
- **A healing potion heals a lot at once.** Then there is a short wait, shown as a small timer, before that player can
  be healed by another one — whoever gives it — as in Terraria, where only healing potions have a wait. So friends
  can't stack heals, and a fight stays about dodging, not drinking.
- **Other potions do what food can't, with no wait**: an antivenom for stings and bites, a salve for sprays and acid
  burns (millipedes, ants), resistance to venom for a while, and seeing in the dark for a while. Venom and poison are
  already decided as real effects (D16).
- **Stronger bugs make stronger potions**: venom from a higher-tier bug makes a stronger antivenom, so potions follow
  the same ladder as the rest of the game.
- **A small set to start** — a healing potion, the antivenom, the salve, venom resistance, night sight, and perhaps
  one venom coating for blades and spears (offered back from the old list rather than dropped quietly). Each gets true examine
  text: before the plague, antivenom was made in horses; now it is made in labs from the venom itself.
- **Bandages** are the cheap heal over a few seconds, one at a time — cloth first, then better ones from honey or
  chitin, both real wound dressings.
- **Made at the potion station** — the cauldron, which already exists in the game but makes nothing yet. Basic recipes
  are known there; stronger ones are found, bought or earned in quests.
- **Food doesn't spoil** in bags or chests, for the same reason tools don't wear out, so the fridge becomes a food
  chest. Fallen fruit still rots on the ground, where flies breed.
- **What goes from the old list of 78 potions**: potions that later decisions rule out — breathing underwater (no
  diving), lamp oils (no oil lamps), calming every bug nearby (calming is per species) — and luck brews (nothing real
  makes anyone luckier); the several night-sight brews become the one potion. Its thirteen cures fold into the
  antivenom and the salve, in strengths, and ingredients from extinct animals (frogs, bats) are swapped. The rest —
  thrown bombs, stat brews, more coatings — stay on the list for the owner to pick from.

**Lenses:** Game first — food is slow and long, potions are quick and strong, and there are no brewing chains.
Premise — real remedies, no magic (P2). Playing together — the wait belongs to whoever is healed. Economy — bug
ingredients tie potions to bug farming. Picture the moment — an antivenom after a scorpion's sting. **Cost and risk:**
nothing in the game can give a timed effect yet, so that comes first, then venom and poison on stings, then the cures;
icons for every potion, meal and bandage (paid images, asked first).

### P17. Giving things to other players
*Parts 11 and 18 · healing; playing together.*
**Accepted by the owner on 2026-09-27.**
- **Right-click a player to offer** what you're holding — an item or a stack of bugs — with a box for adding coins,
  since coins aren't items. They accept with one key; if their bag is full, nothing is lost. An offer nobody answers
  fades after a few seconds, and each player has one offer out at a time.
- **Left-click to heal**: holding a bandage or a potion, point at a friend within reach and click. It works at once,
  with no question asked, and a small cross shows who will get it.
- **Drop things on the ground** for anyone to pick up, as in Terraria and Stardew Valley — a new action; the game has
  none today. Dropped food feeds bugs like fallen fruit; anything else stays until a zone holds too much, and then the
  oldest goes.
- No trade screen between players at first; if one comes later, it is P19's screen with a player on the other side.

**Lenses:** Game first — right-click already means "interact" (doors, beds, stations, townspeople) and left-click
means "use". Picture the moment — mid-fight, a friend's bandage lands with no pop-up. Fairness — the accept step stops
anyone filling another player's bag. **Cost and risk:** the offer prompt with its coin box; aimed healing (today a
click while holding bugs releases them, so a player under the cursor has to come first); the drop action and its limit
— dropped food feeds bugs, which every player's game has to agree on, so it needs the same checks as fallen fruit.

### P18. Townspeople with a day of their own
*Part 13 · towns.*
**Accepted by the owner on 2026-09-27**, with players simply walking in to trade at night.
- **By day, shopkeepers keep their counters.** Chores happen early and late, or are done by townspeople who don't keep
  a shop (both towns need more people anyway): mending fences that bugs have damaged (P6), gathering fallen fruit in
  town, and dealing with bugs that threaten people in the streets, such as wasps and centipedes — swatting them or
  emptying the town's traps — never the flies and butterflies new players come to catch.
- **At night they sleep at home, and players simply walk in and trade with them there**, as Terraria's townspeople
  trade from their houses at night. Night is a large part of every day and nobody can skip it yet, so closed shops
  would leave a player back from a trip with a full bag and nothing to do.
- **Every player sees the same townspeople in the same place.** They keep to their own town, and stop walking while
  anyone is talking to them.
- **Quests from several townspeople.** The myrmecologist's board asks for things to be found and brought back — a
  lost tool, a specimen, a live queen — never a number of dead ants, which would be a bounty by another name. A job
  the player can't do yet shows what it needs.
- Nobody can hurt them or take their things (D41), and bugs leave them alone.

**Lenses:** Picture the moment — at dusk the blacksmith locks up and walks home past the orchard; later there's a
player walks in and trades with him at home. Readability — the village is visibly alive. Ecology — gathering fruit is the same
lever as P10's fruit cut, and the two are tuned together. Playing together — nobody waits for a shop to open. **Cost
and risk:** today a shopkeeper is a fixed object at a counter, so townspeople become characters that move and are
shown to every player; picking up fruit, mending fences and swatting bugs all change the bugs' world, which every
player's game has to agree on, so each needs those checks; walking, working and sleeping animations for every
townsperson (paid images, asked first).

### P19. Trading: coins, goods or both, on one screen
*Part 13 · trade.*
**Accepted by the owner on 2026-09-27.**
- **One screen, two sides**: what you give — goods, bugs, coins — and what you take — goods, recipes, books.
- **Prices don't change**: what you give counts at what that townsperson pays for it, and what you take costs what
  they charge. The difference is paid in coins automatically, either way, and the button says what you'll get or pay.
  So bartering is selling and buying in one step, never a better or worse deal, and the check that stops buy-low,
  sell-high loops still holds.
- **Each townsperson takes the goods they deal in** — the lists the game already has (the blacksmith metal bars, the
  weaver fibre and cloth, the carpenter wood and furniture, the general store materials and food, Maren her honey and
  wax, the Bug Dealer bugs and carcasses) — plus fish for the fisherman and stone for the stonemason. Modern Wares
  takes coins only.
- **Coins come from many places**: selling bugs, carcasses, compost, crops, materials and crafted goods, and quests
  from the Ecologist, the myrmecologist and others.
- Stock and coins stay unlimited, as now, so several players can trade with one townsperson at once.

**Lenses:** Game first — one screen for buying, selling and bartering; the owner's Baldur's Gate reference.
Readability — the balance is always shown. Fairness — no deal is better than plain selling, so nothing can be gamed.
**Cost and risk:** modest — today's screen already has a buy side and a "to sell" box; new are a "to take" box, the
coin difference, and one step that swaps everything at once, tested against duplication the way the sell box was.
The screen must show a whole shop's stock — today it shows only the first six goods — and the carpenter's
"furniture" must match real items, so furniture can be sold.

### P20. A metal ladder made of real tool metals
*Parts 10 and 15 · tools; progression. Also parts 5, 6 and 9.*
**Accepted by the owner on 2026-09-28**, without manganese steel — I've put cobalt steel on that rung instead — and
with eight rungs; platinum goes into fancy armour.
- **Silver and platinum leave the tools too, not just gold.** All three are soft — about as soft as pure copper,
  softer than bronze or steel — and gold and platinum weigh more than twice as much as steel, while the cheaper metal
  on the rung below already does the job better.
- **Tools climb eight rungs, every one a real tool material**: **wood → stone → copper → bronze → iron → steel →
  cobalt steel → tungsten carbide.** Bronze gives tools the rung weapons already have; the iron rung is an iron head
  with a steel edge, as real iron tools were; cobalt steel is today's premium steel for drill bits, and in its tough
  form (maraging steel) the steel of fencing blades; tungsten carbide, set as tips in a steel head, is what real rock
  drills and mining picks use. The top tool can wear a thin gold-coloured coating (titanium nitride, used on real drill
  bits), so it looks golden with no gold in it. Power tools sit in the tiers too (P21).
- **Each rung opens an ore**, so none is skippable: stone reaches copper, copper reaches tin, bronze reaches iron, and
  so on up to the deep ores and gems. That needs two new ores, **cobalt** and **tungsten**, each with a true fact for
  its examine text: cobalt ore weathers into a pink crust ("cobalt bloom") that real prospectors followed to silver,
  and tungsten ore glows sky-blue under ultraviolet light.
- **Weapons climb the same metals to steel. Past steel, the best blades and spears come from the bugs themselves**:
  real ants, scorpions and spiders harden their jaws, stings and fangs with zinc — up to a quarter of their dry
  weight — which makes them light and very sharp, though no harder than aluminium. So bug parts make blades, spears,
  sickles and daggers, never pickaxes; and the zinc builds up for days after an ant's last moult, so the best jaws come
  from older adults — a reason to keep bugs to a good age. The legendary sets sit above both, in the hardest zones
  (D55).
- **Armour follows the tool metals** — bug leather and padded cloth, then copper up to cobalt steel. **Platinum**
  goes into fancy armour that also needs steel (the platinum outfit you picked), sells well as money, and turns up in
  recipes where it fits (2026-09-28).
- **Silver, gold and platinum become the metals of money and machines**: silver for solar panels, contacts and
  mirrors; gold for connectors and for gilding (the gilded-steel outfit); platinum as the catalyst that turns spare wind
  and solar power into stored hydrogen; all three for jewelry. Since the electronics are bought (D1, D26), players
  bring these metals to whoever builds their power parts. Their ores stay in the world as deep rewards.

**Lenses:** Premise — 2126 science: every rung is a real material with a real reason to beat the one before; no
fantasy metals (P2). Readability — household names (bronze, iron, steel), with cobalt and tungsten from Terraria.
Real biology — metal-hardened jaws are published science and give a reason to raise bugs to a good age. Economy —
the precious metals get real jobs. **Cost and risk:** two new ores; every tool, weapon and armour rung renamed, and
each needs its icon (paid images, asked first), as do the bug-part weapons; recipes and item data reworked with the
item table.

### P21. What a better tool does: the newest material starts slow
*Part 15 · progression; part 10 · tools.*
**Accepted by the owner on 2026-09-28**, with powered tools counted among the tiers.
- **Your question answered: no, Terraria doesn't halve the effort each tier.** Its eight early pickaxes are only about
  1.1 times faster per step — 1.5 times from copper to platinum — and its tiers mainly decide what can be mined. None of
  the games checked (Terraria, Stardew Valley, Minecraft, Core Keeper, Valheim, Necesse, Luanti) halves every tier:
  eight halvings would make the top pick 128 times faster. What the good ones share is this: the first tool that can
  reach a new material takes it slowly, **the next tool roughly halves the hits on it**, and later tools shave off a
  hit or two more. In the prototype a hit always does one point of damage whatever the tool, so tiers only decide what
  can be broken.
- **The rule**: each gathering tool has a strength and each natural material a toughness; a hit does strength minus
  toughness, and a tool too weak to dent it gets "Need a better tool" (Core Keeper gates the same way). On the material
  a tool has just opened: about ten hits; with the next tier about five; then three, two, one.
- **The keys are the ores and gems** — one kind of rock stays, as decided (D22), so no harder rock and no tougher zone
  walls. The pickaxe gets one tier per ore (P20). **Axes and shovels get fewer tiers**: the axe's open a few big, tough
  trees (the saw sits among them, D12); dirt, sand and clay need no gate, so the shovel's are about speed and the
  ground it can lay. The item table settles how many each tool has.
- **Swings stay the same speed**; what the player feels is the number of hits, which the cracks on the block already
  show. Placed things — furniture, fences, stations — keep breaking in a few hits with the right tool; toughness is for
  natural materials only, and it doesn't change how bugs damage fences (P5).
- **Farm tools improve by area, not speed**, and stay few (watering cans small and large, D12): a better hoe or
  scythe covers more squares per swing.
- **Friends dig together**: two players hitting the same block add up — today a second player's hit restarts it.
- **Power tools are part of the tiers** (2026-09-28): the top rungs include powered tools, such as a rock drill with
  carbide bits and a chainsaw; how they draw their power is designed with the power system (part 16).

**Lenses:** Game first — one number per tool, and the hit count is visible. Pacing — the newest material is always a
little work, however many tiers there are. Playing together — the same gates for everyone, and co-op digging adds up.
**Cost and risk:** the break handler takes one point per hit today, and the tool's unused speed value is the slot for
its strength; every ore, gem and tree needs a toughness. An axe hit knocks a fruit off a fruit tree, so fewer hits per
tree means less fallen fruit — a small change to the bugs' food, checked like any other. An axe's damage to bugs is
set separately from its strength on wood.

### P22. From the watering can to powered farming — revised with a hand pump
*Part 16 · power and automation.*
**Revised 2026-09-28 after the owner's notes**: a hand pump feeds the sprinklers, then a powered pump; sprinklers
water whatever is in reach, fruit trees included; crops need one watering a day (decided).
- **The ladder**:
  1. **By hand**: the watering can; rain waters everything it falls on.
  2. **A hand pump and small sprinklers.** The pump is a well the player sets on the farm: a few strokes fill its
     cistern, and every sprinkler within its reach draws on it at dawn. One fill lasts a few days, and rain tops it
     up. The small sprinkler — sold in the village, priced as something to save up for — waters the eight squares
     around it.
  3. **The large sprinkler** — from other places, such as the western town — waters two rings around it (a
     five-by-five), from the same pump.
  4. **The powered pump** — inside a powered area it keeps the cistern full by itself, and the pressure pushes every
     sprinkler one ring further. The same power runs the powered versions of stations.
- **Why the pump works**: it keeps the early machines the manual ones, as decided (D56) — watering every square
  becomes one short job every few days — and it gives power a real job to take over: the pumping. The pump's reach is
  shown the way power's reach is, so players learn one idea, a machine that serves everything around it.
- **Sprinklers water whatever is in reach** — crops, fruit trees, flower beds. An orchard kept wet fruits more, more
  fruit feeds more flies, and a player who wants that is free to have it, up to the cap (D62).
- **Crops need one watering a day** (decided 2026-09-28; the prototype asks for two), so the sprinklers take the whole
  chore.
- **Planting, harvesting and picking fruit always stay with the player**, and catching stays hands-on — placed
  catchers hold only a few and are emptied by hand (P3).
- **Easy to read**: holding a sprinkler or a pump shows the squares it will reach; the pump shows its cistern as
  full, half or empty; crops that nothing waters get a small dry mark while the player holds a watering can. Hoes and
  shovels never knock a sprinkler over by accident.

**Lenses:** Game first — one short pumping job instead of watering every square, and power takes that away too. The
owner's fixed points — small sprinklers saved up for in the village, larger ones from further out, early machines
more manual. Picture the moment — a few strokes at the pump on a dry morning, then the whole farm hisses into life at
dawn. **Cost and risk:** the dawn watering runs on the server like the rain; watered trees feed the bugs, so it is
checked like any other change to their food; when a zone has been frozen, its catch-up (decided, not built) has to
apply the dawns it missed; the pump, its cistern and two sprinklers need art (paid images, asked first).

### P23. Lessons that lead into each other
*Part 19 · the interface and learning the game.*
**Accepted by the owner on 2026-09-28.**
- **One lesson system with three ways in, and one Journal**:
  - **On joining**: three one-line prompts — walk, pick a tool, talk to the Mayor — each showing the player's own key.
  - **From townspeople**: a first chain in the village, where finishing with one person often sends the player on to
    another, as decided.
  - **On first meeting something, or reaching a new place**: a one-line tip the first time a wasp comes close (the
    dodge key), a pickaxe can't break an ore (what can), the bag fills up, or night falls (torches; shopkeepers trade at
    home); and a new townsperson's lessons when the player first reaches their place — Maren in the Bee Meadow, the
    Fisherman at the lake, the myrmecologist at the Ant Tunnels.
  - **The Journal** holds every lesson to read again, the people met and what they deal in, and the key list, and
    shows the next one or two lessons greyed out with a hint of where they start.
- **The first chain** (townspeople by role, since they get redesigned):
  1. The **Mayor** welcomes the player, hands over the Journal, and names three people to meet, in any order.
  2. The **Bug Dealer**: catch two small bugs with the net — any kind, day or night — sell one to him and keep the
     other. The first coins.
  3. The **general store**: till, plant three seeds and water them in the teaching beds beside the shop; refill the
     can. A few seeds as thanks, and a harvest note later when the first crop is ripe.
  4. The **carpenter** gives the gate recipe: close a ring of fence, let the kept bug go inside, cut some wood and make a
     gate at his workbench. A few planks as thanks.
  5. Back to the **Mayor**, who sends the player east.
  6. The **Ecologist**: the greyed Ecology tab lights up, and he asks the player to set up a monitoring station in the
     village meadow — or, if one already stands, to read it. His quests follow in the tab.
  7. The **blacksmith** offers to show how ore becomes metal: take torches down the first mine, bring back copper ore
     and coal, and make a copper bar at his stations — crush, wash, smelt. After that the world is open.
- **Rules**: each character has its own lessons, so a late joiner starts fresh whatever others have done; a lesson
  that teaches a control counts only the player's own action; a reward is paid only once the server has seen the
  deed, and stays small, so new characters can't farm them; nothing expires or can be failed; any lesson can be
  skipped and prompts turned off; a "!" over a townsperson shows only to the player it's for, and a guide arrow appears
  only if the player seems stuck. The teaching pen and beds belong to the village and reset, so a busy server doesn't
  fill up with lesson leftovers.
- **Every item's examine page says what it's made at and what it's used in** — Terraria's Guide and Minecraft's recipe
  book built into the page — which does more than any chain to keep players off a wiki.

**Lenses:** No storyline — each step is an optional job with a small reward. Show, don't tell — one line at a time,
at the moment it's needed. Playing together — every player has their own chain. Readability — the Journal can be
reread. **Cost and risk:** a lesson list in the data; a per-character record beside the existing "intro seen" flag;
server checks for rewarded steps; the prompts, the Journal, the per-player marker; lines for each townsperson. It
depends on other pieces: the crusher, sluice and furnace at the blacksmith's (D55); a starting pick that can mine
copper (a stone one under P20); teaching beds and pen in the village; and a small bug to catch at night — fireflies,
whose lantern is decided for the first area (D12), living in the village.

### P24. Controls and settings
*Part 19 · the interface.*
**Accepted by the owner on 2026-09-28.**
- **The genre's standard where there is one**: W A S D to walk; left mouse uses what's in the hand — swing, catch,
  water, place, heal a friend; right mouse works with whatever is under the cursor — talk, open, trade, sleep, offer
  something to a player — and on empty ground does the held weapon's second move (the sword's jab, the spear's sweep);
  1 to 0 and the mouse wheel pick the hotbar slot; M opens the map.
- **Our own actions on easy keys**: Space dodges; **R switches a tool's mode** — the shovel's Dig and each kind of
  ground — so **the mouse wheel always stays on the hotbar** and a player laying a path can still scroll to a weapon
  when a wasp arrives (this is why P12 uses R); Tab opens the bag; J the Journal; B the bug pages and the Ecology tab;
  V examines what's under the cursor; G drops the held item; Enter opens chat; Esc closes or opens the menu.
- **E does the nearest thing, in a fixed order**: while dragging a big bug, E lets go (P15); otherwise it grabs a
  subdued bug in reach, then picks up an item, then uses the nearest townsperson, door or station.
- **Q heals quickly**, using only bandages and healing potions — never a meal, which would replace a boost eaten for a
  trip (P16) — and skips potions while their wait is running.
- **Offers from other players are accepted with F** (or a click), never with E, so picking things up can't accept a
  trade by accident. **Releasing bugs** works as today: with bugs on the cursor, a left click lets them all go and a
  right click one — unless a player is under the cursor, which offers them instead (P17).
- **Everything can be rebound**, with two keys per action, and every prompt shows the player's own keys — or the
  gamepad's buttons. R no longer rotates anything: furniture doesn't rotate and doors turn by themselves (D45).
- **Gamepad and Steam Deck**: the game picks the target square from the tool in hand — the net takes the nearest bug it
  can catch, the hoe the square in front — with an optional free cursor on the right stick; menus move by focus.
- **Settings, grouped as players look for them**: gameplay (lesson prompts, hold-to-repeat or one action per click,
  auto pick-up, damage numbers); controls (keyboard and gamepad); display (window, resolution, frame cap,
  pixel-perfect scaling, zoom kept apart from interface size, brightness, bloom and colour grade); interface (size up to
  200%, pixel or clear font, hotbar at the top or the bottom); audio (master, music, effects, ambient, interface);
  captions for important sounds, with a direction arrow; accessibility (reduce motion — shake, flashes, plant sway; no
  holds, which turns every hold into a press; clearer outlines on bugs that can hurt; never colour alone — ticks and
  crosses on the placement preview). A short first-launch screen sets text size, captions and shake, and settings
  open from the title screen.
- **Three accessibility guidelines can't be met in a shared world that always runs**: slowing the game, choosing a
  difficulty per player, and pausing. The no-holds option, smart targeting and captions stand in for them.

**Lenses:** Readability — familiar keys where the genre agrees, our own verbs on the easiest reach, and one meaning
per key. Accessibility — the must-haves of the Game Accessibility Guidelines and Xbox's. Playing together — offers
never accepted by accident, and game keys off while typing in chat. **Cost and risk:** the biggest job comes first —
moving the input code onto Unity's Input System (already installed, unused) so keys can be rebound and named in
prompts; then a settings screen; full gamepad play after the keyboard version, if Steam Deck support is wanted.

### P25. Border events: bugs wander over from a frozen neighbour
*Part 17 · time and weather; part 14 · the world.*
**Accepted by the owner on 2026-09-28.**
- **What the player sees**: now and then, a small group of bugs arrives at the edge of their zone from the zone next
  door, which has no players and is frozen — flying or walking in like any migrating swarm, at a stretch of the edge
  no player is looking at.
- **Both ways, so nothing drains**: bugs that wander off a live zone into a frozen one are added to its saved bugs (the
  planned hand-over between zones), and only a frozen zone's surplus — bugs above its normal level — ever leaves it,
  so a busy neighbour can't empty it over time.
- **Which bugs**: drawn from the frozen zone's saved bugs, in proportion to how many of each it holds. Only bugs that
  really travel come — flyers, and walkers across land edges (water divides the map) — never a queen, a nest, a boss,
  or aphids that live on a plant; and only species that live in the zone they're entering, so a dangerous frozen zone
  never trickles hornets into the village.
- **How many**: one to a few bugs at a time, on a random timer for each shared edge, with a limit per game day; a
  crowded neighbour sends more — the same reason live bugs spread out when they crowd, so a frozen border behaves like a
  live one.
- **Border events move bugs; they never create them.** Bugs are born only in their species' spawn areas (D53). The
  prototype's trickle that creates new swarms in each habitat, and the balancing system's reseeding, become births in
  spawn areas when the ecology is retuned.
- **The same for every player**: the server decides each event and announces it like any other zone crossing. It has
  to be the server, because nobody's computer is running the frozen zone — which is the kind of reason the server
  review asks for (D58).

**Lenses:** The owner's direction — borders stay alive while the far side sleeps. Real biology — crowded populations
really do spread into neighbouring land. Fairness — the exchange runs both ways and only surplus leaves. **Cost and
risk:** it depends on pieces not built yet — bugs crossing between zones, and the frozen zones' catch-up (whose
server-side stand-in for the ecology is part of the same server review); arriving bugs change the shared bug
simulation, so they go through the same hand-over and checks as live migration.

### P26. The plot's happiness, shown plainly
*Part 18 · playing together; part 7 · building.*
**Accepted by the owner on 2026-09-28.**
- **Whose happiness — my pick: the plot's own.** Decorations raise it, and it raises what the plot's crops and
  stations produce — hives and nurseries included — by a small amount, up to a cap (the January 2026 plot design). It
  doesn't change how the live bugs behave, so it stays outside the shared bug simulation, and it's the same number for
  every player.
- **Duplicates — my pick: each copy counts half the one before, and a fourth adds nothing** (a sofa worth 8 gives 8,
  then 4, then 2, then 0), so a second copy is always worth less than a new item of the same value. Decoration values
  are kept to multiples of four so the halves stay whole.
- **A badge on screen** while the player stands on a plot — a face and a word (Bare, Plain, Pleasant, Cosy,
  Delightful). Clicking it opens the panel; the plot's sign and a button in the inventory open it too, and visitors
  can look.
- **The panel**: a bar that ends at the cap, with the number and what it does in plain words (for example "62 / 100 —
  crops and stations here +6%"; all numbers here are made up); below it the decorations grouped by kind — seating,
  lighting, plants, art, textiles, outfits on mannequins — each folded to one line, and unfolding shows every copy's
  value side by side ("Sofa ×3: +8 +4 +2"); at the bottom two short hints about what the plot hasn't got yet ("no rug
  yet").
- **On the plot itself**, on demand: each decoration outlined gold (counts in full), silver (counts less) or grey (adds
  nothing), each with a small mark as well as the colour; and while the player holds a decoration, a small number by
  the cursor says what placing it would add ("+2 — a third sofa").
- **Decorative outfits count when they stand on a mannequin on the plot** (my pick), like any other decoration.

**Lenses:** Readability — hidden happiness sends players to fan calculators (Terraria), while a named band plus a
reason list is what RimWorld, Necesse and Oxygen Not Included use. Economy — variety over repetition. Picture the
moment — holding a fourth stool and seeing "+0". **Cost and risk:** it depends on the private plots themselves, which
aren't designed yet (size, cost, whether a plot is its own zone); the bonus values and display groups are added with
the system; the panel reuses the station panel's column and bars; the outlines draw above the night lighting.

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
