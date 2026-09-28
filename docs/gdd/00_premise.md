# §00 · Premise, pillars & what belongs in the world
<!-- gdd: id=00 status=review updated=2026-09-28 -->

## The experience
It is 2126. A plague killed nearly every mammal, and people bred bugs big enough to eat. You arrive on the frontier
with almost nothing and make a life as a bug farmer. You catch, calm, breed and sell giant bugs, and fight the ones
that bite back. You farm, fish, mine, craft and build, trade with the townspeople, and push out from the village into
wilder land where the bugs get bigger. There is no storyline: lessons and quests are offered, never forced, and you
set your own goals. The world is a living food web that answers what you do — you can keep it in balance or tip it.
With friends it becomes a shared frontier: the wild is lawless, while your own plot stays safe.

## Decided
Each line is the owner's decision in my words, with its date.
- **The premise**: the year 2126; a plague killed nearly every mammal — people held on; people bred bugs bigger to
  have food; the player starts over on the frontier as a bug farmer (the owner's opening script, June 2026). The
  game's opening text is only a stand-in for now (2026-09-27).
- **The bugs are giant**, and their size stays as designed (2026-09-26).
- **Bugs, fish and people survive**; birds, amphibians and reptiles died out too, so no frogs (2026-09-27; D31, D32).
- **A bug is an insect or another arthropod** — spiders, scorpions, centipedes, millipedes, pill bugs, crayfish,
  crabs; fish are separate; no worms and no leeches (2026-09-28, D64).
- **Nothing from the mammal world**: cave bats and bat guano, milk and cheese, horseshoes, livestock and manure, a
  rabbit's-foot charm and a pack mule are dropped; so is the old idea of a meteor-borne infection (2026-09-27, D32).
  The prototype's own misfits — the cow skull, the cat statue, the hay bale, the birdbath, bones and bone piles — can
  be removed; the prototype isn't finished (2026-09-27).
- **No magic**: the world runs on 2126 science (2026-09-28, D65).
- **Every creature is a real species** with real behaviour, and the game teaches a little ecology and biology
  (2026-07-11; 2026-09-27, D39). New species are welcome if each is explained, keeps the balance and doesn't need a
  whole new zone (2026-09-26).
- **No storyline, and no ending**: players set their own goals in an open world, as in Terraria; the hardest zones
  hold the bosses and the legendary sets, and some quest lines lead there (2026-09-26; 2026-09-28, D55).
- **Food chains are the ladders** — several, some short and some tall, rather than one long climb up from flies; bugs are
  livestock, sold as meat or kept for their product (2026-09-27).
- **Players may tip the ecosystem** — balancing or unbalancing it is the point of the game, within the safety caps
  (2026-09-28, D62, D63).
- **It's a game, not a simulation**: real facts, but no realistic chores or extra steps — one step per station, and
  no knocking at doors (2026-09-27, D42, D54).
- **No wear-and-tear chores**: no hunger, tools never wear out, and food doesn't spoil (2026-09-27, D49, D50;
  2026-09-28, D54).
- **Combat matters and defence is critical**; each role has its own best gear, and no single set is best at
  everything (2026-08-06). Starter zones are cosy, nights are more dangerous, and danger rises outward from the
  village (2026-07-11; 2026-09-27, D46).
- **A lawless shared world and safe private plots**: out in the world anything goes except the townspeople's
  property (2026-09-26; D41); players fight each other only where a server allows it — the game is players against
  the world (2026-09-28, D58); private plots are invite-only, and nothing on one is damaged while its owner is away
  (2026-09-28, D58).
- **Everything in the shared world runs the same for every player** (2026-09-28, D58), and everything in the world
  persists, as in Terraria (July 2026, D31).
- **Examining an item or a recipe shows what it does and the real biology behind it** (2026-09-26).
- **Curiosity and surprise** are priorities (2026-09-26).
- **No rule is forced on every zone** (2026-09-26). **No seasons** (January 2026; confirmed 2026-09-27).
- **Every system gets a polishing pass**, with suggestions from taste and good game design (2026-09-28, D59).
- **Nothing is locked, and the prototype is not the design**: only the owner's dated decisions are decisions
  (2026-09-27, D33, D48).

## Current design
What the older design documents say that still stands:
- **The genre**: a top-down multiplayer sandbox inspired by Terraria and Stardew Valley, about emergent ecology,
  insect farming, shaping the environment and solving problems your own way (January 2026, §1–2).
- **Two ways to play at once**: risky exploration in the shared world, and calm, carefully laid-out farming on the
  private plot (January 2026, §1, §10).
- **Progress comes from items** — tools, knowledge, preparation and layout — not skill trees or experience points
  (January 2026, §1, §18).
- **No disasters on a timer and no forced invasions**, and **machines ease chores but never play for the player**
  (January 2026, §11–12).
- **The seven January 2026 pillars** (§18): emergent systems over scripts · player agency over obligation · readable
  ecology · item-based progression · no offline punishment · no autoplay · no forced chaos.
- **Variety with taste** — many kinds of things to gather, craft and decorate with, each earning its place; the item
  pass may cut many (2026-09-28, D55).
- Replaced since: "there is no endgame" (now an open world with no ending, D55) and the NPC workers (none, D56).
- **Dropped by the rulings above**, so the item table won't bring them back: the frog items (frog spawn, frog toxin,
  the frog-leg charm, the frog pen, the frog spout); bat guano; the antler chandelier and the bearskin rug; the robin,
  the feathered fishing fly, the bird feeder, the bird house and the owl decoy; the dog kennel, the cat basket, the
  cat-grace band and the dog statue; the horseshoe sign and pile; the dairy props; the dung pat. Where a bug-world
  version fits — a beetle charm, a dragline band, a stag-horn chandelier, a moth roost, frass — the item table
  offers it.

## As built
- The opening text plays before the title screen (`OpeningSequence.cs`, lines 28–42); it is a placeholder.
- Fifteen bug species are in the prototype, all unfinished. The old zone sheets name 84 species (listed in §03) — a
  list to cut from, not a plan.
- There is no examine view yet: hovering an item shows only its name, and only 2 of the game's 654 things have a
  description. About 650 examine texts are on the roadmap as their own pass.
- The prototype's misfits and where they stand: 34 bone piles in the first mine (and the general store buys bones, as
  a material); in the village, one cat statue, three hay bales and two birdbaths (the birdbath has a stonecutter
  recipe); the cow skull is placed nowhere. The fly's data still lists a manure pile among its breeding places, and a
  scarecrow — a bird-scarer — exists as an object.

## Proposals
### P1. A pitch that names the whole game
**Farm giant bugs on a frontier where nearly every mammal is gone. Catch them, breed them and fight them; farm, fish,
mine, craft and build; trade with the townspeople; and push out from the village into wilder land where the bugs get
bigger — alone or with friends, in a living ecosystem you can balance or tip.**

It goes at the top of the design document, and it is the first test for any new idea: does this make those two
sentences more true? The first try (2026-09-26) named only the bugs and the food web; this one names every main
activity, fighting included.

**Lenses:** Unification — one statement every section serves. Premise — it opens with the world's situation, not a
feature list. Completeness — checked against every activity in the overview.

### P2. The pillars, rebuilt from everything decided
1. **Bugs are the farm** — catch, calm, pen, breed and sell giant bugs; several food chains, some short and some
   tall, are the ladders. *(2026-09-27; D39)*
2. **A living ecosystem you can tip** — everything eats, breeds, ages and dies; players keep it in balance or tip
   it, within the safety caps; the Ecologist and the Ecology tab help them read it. *(D62, D63)*
3. **A whole sandbox, real facts, simple steps** — farming, mining, crafting, building, cooking, fishing and trading,
   each a game-like system with one step per station and no realistic chores. *(D42, D54, D64)*
4. **Danger you prepare for** — real fights against bugs; defence matters; gear by role, with no single best set;
   danger rises outward from the cosy starter zones to the bosses in the hardest ones. *(2026-08-06; D46; D55)*
5. **Progress through gear and preparation** — no levels, no storyline, no ending; better tools open new ores and
   zones. *(2026-09-26; D55)*
6. **Real creatures, no magic** — every creature is a real species with real behaviour, examining anything shows the
   real biology, and the world runs on 2126 science. *(2026-07-11; D39; D65)*
7. **Curiosity and surprise** — secrets to find across the world, research that reveals each species, and things
   that aren't what they seem. *(2026-09-26; D63)*
8. **Together, fairly** — the wild is lawless except for the townspeople's things; players fight the world, and each
   other only where a server allows it; plots are safe and invite-only; everything runs the same for every player.
   *(D41; D58)*
9. **Fair to your time** — no wear-and-tear chores, nothing on your plot lost or damaged while you're away, no
   disasters on a timer; machines ease chores and never play for you. *(D49, D50, D54; D58; the January design)*

The seven January pillars live on inside these.

**Lenses:** Built from decisions — each pillar names its source. Unification — each one can reject an idea.
Completeness — the first try missed mining, crafting and building; pillars 3 and 4 name every activity, fighting
included.

### P3. The misfits go
You said the prototype's misfits can go (2026-09-27). My recommendation for each:
- **Go**: the cow skull, the cat statue (the village cottage keeps its bug statue), the bones and the 34 bone piles
  in the first mine, and the manure pile in the fly's data (D32).
- **Become bug-world things**: the hay bale becomes a **straw bale** — straw comes from cutting wheat (P11 of the
  overview, accepted) and makes mulch; the birdbath becomes a **puddling dish** — butterflies really gather on damp
  ground to sip water and minerals; the scarecrow becomes a bug-scaring scarecrow or goes, since there are no birds.
- The old world's story is told by the examine texts and the townspeople, not by animal remains.

**Lenses:** Premise — nothing from the mammal world. Already covered — straw is already coming (P11), and puddling is
real butterfly behaviour. **Cost:** removing the placed ones from the village and the first mine; the birdbath's
recipe changes to the dish's.

### P4. Bugs that lived on the vanished animals
Some designed bugs depend on animals that died out: ticks, mosquitoes and horse flies drink the blood of mammals and
birds; dung beetles live on dung; bot flies grow inside mammals. With the animals gone, **each such species is either
gone or lives on what's left — people, fish, plants and rot** — whichever is true of the real species. So mosquitoes,
ticks and horse flies that bite people survive as pests the player deals with; dung beetles that can also live on
carrion or rotting fruit survive as scavengers; the rest are gone. §03 applies this species by species, and the
examine text says why — a real lesson in how species depend on each other.

**Lenses:** Premise — the plague's effects reach the bugs too. Real biology — host dependence is real, and many of
these bugs really do bite people or switch food. Curiosity — a pest that bites the player, with a reason. **Cost:**
none in code yet; it shapes §03's species list.

## Questions
### Q1. The voice of the words
The shape is decided: cosy at home, danger rising outward, no storyline. What's open is how the words sound — the
examine texts, the townspeople's lines and the opening. Your own opening turns wry at the end: "Bigger than anyone
meant to."
- **A.** Earnest and wistful — a quiet sadness for what was lost, and wonder at what's left.
- **B.** Dry and wry — plain-spoken, with the understatement of the opening's last line.
- **C.** Openly comic — the strangeness of giant bugs played for laughs.

**Recommendation: B.** It matches your own opening, it carries real biology without preaching, and it lets a sad
fact land lightly — which suits a cosy game with a plague in its past.

## Sources
- The owner's decisions, restated above; `docs/product/economy/DECISIONS.md` D31–D65; `docs/gdd/overview.md` (final,
  2026-09-28).
- `BugFarmerClient/Assets/Scripts/UI/OpeningSequence.cs` (the opening script); `nakama/data/species.json` (the
  fifteen prototype species; the fly's breeding places); `nakama/data/entities/{items,occupants,placeables}.json` and
  `recipes.json` (the misfits, the birdbath recipe, the scarecrow); the zone saves under `nakama/data/zones/` (where the
  misfits stand).
- `docs/product/design/game_design.md` §1, §2, §10–12, §18 (the January 2026 design).
- The replacements for dropped items: the 2026-09-26 draft of this section (git history).
