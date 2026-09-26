# §00 · Premise, pillars & what belongs in the world
<!-- gdd: id=00 status=review updated=2026-09-26 -->

## The experience
It is 2126. A plague killed nearly every mammal, and people bred bugs big enough to eat. You arrive on the
frontier with almost nothing and make a life as a bug farmer: you catch, calm, breed and sell giant bugs, grow the
plants that feed them, and push out into wilder places where the bugs get bigger and meaner. Nobody tells you what
to do next. The world is a living food web, and learning to read it is the game. With friends it becomes a shared
frontier — anything goes out in the wild, while your own plot stays safe.

## Decided
- **The premise** — your opening text, in the game today: *"It is the year 2126. A plague swept the Earth. Nearly
  every mammal — gone. Humans held on. But humans still had to eat. So we made the bugs bigger. Bigger than anyone
  meant to. Out on the frontier, you start over. As a bug farmer."*
- **Bugs are giant** — *"keep in mind bug farmer is in the future where bugs are giant"* (2026-09-26). Their size
  stays as designed: *"The way we designed it why even bring this up?"* (2026-09-26)
- **No storyline; progress is earned** — *"there will be tutorials that unlock, the ecology tab has its own little
  tasks and quests, but no overarching storyline it is like terraria where you just do whatever - things are gated
  by costs and such so you have to work on your char before going to certain zones."* (2026-09-26)
- **A chaotic shared world, a safe private plot** — *"absolutely keep them, it is part of the critical game design
  where the world is chaotic and anything goes (except stealing citizens stuff or destroying their houses, a message
  will pop up saying its basically not nice)"* (2026-09-26)
- **New bugs are welcome, with care** — *"We can add as many new bugs as we want as long as things stay balanced
  and things are explained"*; and on adding the honeypot ants and grasshoppers some food ideas need: *"I am
  willing to add some as long as it doesnt mess up the balance and require completely new zones."* (2026-09-26)
- **The biology shows when you examine things** — *"We need to make sure to include the biology lesson so it makes
  sense, when you examine it as a recipe or item you should see what it does."* (2026-09-26)
- **Surprise and curiosity matter** — *"we like surprises, the lens of curiosity and lens of surprise are important
  lenses from the book of lenses."* (2026-09-26)
- **No frogs** — recorded as *"frogs explicitly REJECTED"* in the decisions log after the 2026-07-05 playtest
  review (`economy/DECISIONS.md`, D31).

## Current design
What the design documents already say, gathered in one place:
- **The genre.** *"A top-down multiplayer sandbox game inspired by Terraria and Stardew Valley, focused on emergent
  ecology, insect farming, environmental interaction, and player-driven problem solving."* There is no endgame:
  *"The world evolves through player interaction and ecological dynamics."* (GDD §1–2)
- **Two ways to play at once:** *"hands-on, risky exploration in the shared world"* and *"stable,
  optimization-focused farming in private plots."* (GDD §1, §10)
- **Bugs are livestock.** Some bugs make a product at a station (bees → honey, silkworms → silk); the rest — flies,
  wasps — are sold as meat. The food chain is the progression: farm flies to feed wasps, and so on up to bigger,
  rarer bugs. (`bug_ecology_plan.md`)
- **Progress comes from items**, not skill trees or experience points: *"Progression is driven by tools, knowledge,
  preparation, and spatial design—not skill trees, scripted events, or stat grinding."* (GDD §1, §18)
- **Machines ease chores, never play for you** — automation is allowed but slow and capped: *"no instant
  auto-catching, no automated combat"*. The slow autonet is the first automatic catcher and others in the same
  spirit are allowed (GDD §11.4); you've also named automatic bug catchers and bug zappers for the powered age.
- **No disasters on a timer:** *"No timer-based disasters · No forced invasions"* (GDD §12.2).
- **The seven pillars** of the January 2026 GDD (§18): emergent systems over scripts · player agency over
  obligation · readable ecology · item-based progression · no offline punishment · no autoplay · no forced chaos.
- **Lean into variety** — lots of things to gather, craft and decorate with. (GDD §19)

## As built
- The opening text plays before the title screen (`OpeningSequence.cs`, lines 28–42).
- 15 bug species are in the game: Common Fly, Meadow Butterfly, Honeybee, Wasp, Wasp Soldier, Giant Hornet, Carrion
  Beetle, Garden Centipede, Tiger Centipede, Giant Centipede, Garden Millipede, Worker Ant, Scout Ant, Firefly and
  Dragonfly. About 75 more are designed on paper (`economy/species_and_drops.md`).
- **There is no examine view yet.** Hovering an item shows only its name (`InventorySlotUI.cs` → `TooltipUI.cs`);
  bugs have a one-line description on their info card; only 2 of the 654 items, objects and placeables have any
  description (compost and the compost bin). Your "biology on examine" rule means an examine view plus about 650
  short texts — now on the roadmap as its own content pass.
- A few things in the game data don't fit the premise: `cow_skull`, `cat_statue`, `hay_bale` and the `birdbath`
  (decorations), and `bone` and `bone_pile` (a material with no use yet, and piles in the caves). More are designed
  on paper — see the proposals below.

## Proposals
### P1. A one-line pitch that steers every decision
**"Farm giant bugs on a frontier where nearly every mammal is gone — a living food web you learn to read, bend and
harvest, alone or with friends."** It goes at the top of the design document and becomes the first test for any new
idea: does this make that sentence more true?

**Lenses:** Unification — one sentence every section serves. Already covered? — the GDD's opening line says what
kind of game it is; this says what it is about.

### P2. The pillars, updated with what you've said since January
1. **A living food web you can read** — everything eats, breeds, dies and rots; the Ecologist and the Ecology tab
   help you understand it.
2. **Bugs are livestock; the food chain is the progression** — to keep bigger bugs you farm the smaller ones they
   eat.
3. **Progress through gear and preparation, gated by cost** — no experience points, no skill trees.
4. **A chaotic shared world, a safe private plot** — the chaos comes from other players and the bugs, never from
   disasters on a timer; anything goes out there (except citizens' property); your plot is yours.
5. **Your own goals** — no storyline; tutorials and Ecology-tab tasks unlock as you go.
6. **Real biology, shown when you examine things** — every bug, item and recipe says what it is and why it works.
7. **Curiosity and surprise** — poking around is rewarded: secrets, hidden places, things that aren't what they
   seem.
8. **Fair to your time** — no punishment for being away, and machines ease chores but never play for you.

Pillars 1, 3, 4, 5 and 8 carry all seven January pillars; 2 comes from the ecology design; 6 and 7 are your words
from this week.

**Lenses:** Built from the January pillars and your answers this week — every pillar traces to your words or a
design document. Unification.

### P3. Keep the old world's relics — they tell the story without a storyline
Keep `cow_skull`, `bone_pile` / `bone` and `cat_statue` (and the designed dog statue) as **relics from before the
plague**, each with a line of examine text — for example *"A cow's skull, bleached by the sun. From before the
plague."* Bones get the use already designed for them: **bone meal**, a real fertiliser
(`brainstorms/farming/farming_tools.md`, `economy/catalogs/materials.md`).

**Lenses:** Premise — these are remains and memories, not living mammals. Storyteller — with no storyline, the world
itself has to show what happened. Cost — the art exists and bone meal is already designed. Dead ends — `bone` has no
use in the game yet.

### P4. The hay bale becomes cricket feed
Keep `hay_bale` and its art. Examine text: *"Dried grass. Crickets will eat it."* It becomes a feed item when
crickets arrive (cave crickets are designed). Wiring it up is data only — the same way flies are drawn to the
compost bin today.

**Lenses:** Premise — hay only exists for livestock, and here the livestock are bugs. Bestiary — crickets are
already designed, not new.

### P5. Cut dairy
Cut the designed dairy things — milk, cheese, the cheese press, the milk churn, milk bottles and the cheese-wheel
stack. None are built, and `crafting.md` already marks milk as *"future livestock"*. The sweet side of cooking
stays with honey and **aphid honeydew**: ants really do tend aphids for the sweet honeydew they make, and the aphid
ranch, honeydew tap and ant dairy are already designed (`brainstorms/bug_farming/bug_farming.md`).

**Lenses:** Premise — no cows, no milk. Already covered — the honeydew line exists on paper.

### P6. Bats become moth roosts; bat guano becomes frass
Cut the designed `cave_bat` and `bat_swarm` — bats are mammals. The cave design already has the bug version:
`cave_moth_roost`, a ceiling cluster of pale moths that bursts out like bats. The cave fertiliser `bat_guano`
becomes **frass** — insect droppings, a real fertiliser that farms sell today — left by cave crickets, and it takes
over guano's other job too (the damp salve's saltpetre note, `economy/zones/centipede_cavern.md`).

**Lenses:** Premise. Bestiary — both replacements are already designed. Explain on examine.

### P7. Animal parts and names become bug ones — and the frog items go
| designed item | becomes | why |
|---|---|---|
| Lucky Rabbit's Foot (a charm) | **Beetle charm**, cut from a beetle's shell | the ancient Egyptians carried scarab-beetle charms for luck and protection |
| `cat_grace_band` (protects from falls) | **Dragline band** | jumping spiders really fix a silk safety line before every leap |
| antler chandelier | **stag-horn chandelier** | a stag beetle's huge jaws look like antlers; `stag_horn` is already designed |
| bearskin rug | **tarantula-molt rug** | tarantulas shed their whole skin, hairs and all — no killing needed |
| Frog Legs (walk on water) | **cut** | water-walking is already covered: the lily glider, strider gear and skater boots |
| the frog items: `frog_spawn`, `frog_toxin`, `frog_leg_charm`, `frog_pen`, `frog_green`, `frog_brown` | **cut** | frogs were rejected; the swamp poison moves to a swamp bug (the Deep Swamp zone design picks which) |
| the frog fountain spout | **beetle spout** | same fountain, a bug on it |

**Lenses:** Premise. Bestiary — every replacement uses a designed bug or none. Already covered — water-walking.
Explain on examine.

### P8. Cut horseshoes and live pets; animal statues stay
Cut the designed `sign_horseshoe` and `horseshoe_pile` (no horses — the smith's sign becomes an anvil) and the
`dog_kennel` (no living pets). The `cat_basket` goes too — unless P9 is kept, when it becomes the last cat's bed.
The cat and dog statues stay as relics (P3).

**Lenses:** Premise.

### P9. A village secret: the last cat (optional)
Somewhere in the village, behind a door you have to find, an old resident keeps what may be the last cat. It can't
be hurt, taken or farmed — it belongs to a citizen. It's just there, asleep. Examine text: *"A cat. Alive."* Cost:
one small sprite, one resident, one hidden room in an existing house.

**Lenses:** Premise — *"nearly every mammal"* leaves room for one. Surprise and Curiosity — the kind of find players
tell each other about. Fits "village secrets" on your village list. Zone freedom — one place, not a rule for every
zone.

## Questions
### Q1. Which animals share the world with the bugs?
Fish exist — fishing is on your list, and a blind cave fish is already designed. Frogs are out. The open part is
birds. The plague took mammals, so if birds are gone too the game needs a reason (for example, the giant bugs
drove them out). Birds already appear in a few places: the `birdbath` is in the game, and a bird feeder, bird
house, owl decoy, robin and a feathered fishing fly are designed. The July look-and-feel research suggested small
birds as cheap background life that makes the world feel alive.
- **A.** Bugs and fish only. Bird things get bug versions: the bird feeder becomes a butterfly feeder (nectar feeders are
  real), the birdbath a butterfly puddling dish (butterflies really sip minerals from wet sand), the bird house a
  bee hotel, the owl decoy and robin are cut (the scarecrow
  scares bugs), and the fishing fly is tied from silk.
- **B.** A few small birds as harmless background life, like robins on the lawn. Next to giant bugs, a robin would
  be smaller than many of them.
- **C.** Birds as part of the food web: they hunt bugs, including your livestock.

**Recommendation: A.** It draws the same line as the frog decision; everything on screen is then part of the bug
world or fishing, and nothing competes with the bugs for attention. B and C each add a new family of creatures to
draw, animate and balance.

### Q2. The early "meteor infection" idea
The first requirements (December 2025) and the world notes written a week later describe meteors that bring space
bacteria: patches of infected ground, aggressive "zombie bugs" that spread it, and a cure spray. None of it is
built, and nothing written since January 2026 mentions it.
- **A.** Drop it. (The meteorite ore in old craters and the zombie-ant fungus are separate designs and stay either
  way.)
- **B.** Keep it as designed: meteor strikes, infection patches, zombie bugs, the cure spray.
- **C.** Replace it with farm diseases that come from how you keep bugs: crowd too many into a pen and disease can
  break out; give them space and keep pens clean to prevent it; a cure spray treats it. This really happens — a
  virus devastated North America's commercial cricket farms from 2009
  ([PubMed](https://pubmed.ncbi.nlm.nih.gov/21167171/)). It is a big new part of the bug simulation, so it would be
  designed in §05, not here.

**Recommendation: A.** Random meteor strikes clash with the GDD's *"No timer-based disasters"* (§12.2) and *"No
forced chaos"* (§18), and with your *"we dont want mechanics forcing rules on zones"*; the plague already gives the
world its history, and a second plague from space muddies it. C is good on its own merits but big — I'd bring it
back as a proposal in §05 rather than decide it here.

### Q3. How should the game feel?
The opening is sombre; the art is bright and full of flowers; the two reference games are Stardew Valley and
Terraria.
- **A.** Warm and curious, with danger at the edges — the plague is history you glimpse in relics and examine text;
  home is cosy; the far zones are genuinely dangerous.
- **B.** Frontier survival — wonder, but the wild is harsh everywhere and scarcity bites.
- **C.** Light and funny — the strangeness of giant bugs played for laughs.

**Recommendation: A.** It matches the art, both reference games and the pillars (fair to your time, no forced
chaos). How dangerous the far zones get is set in §07 Combat.

## Sources
- Your answers, 2026-09-26 (this session) — quoted above.
- `BugFarmerClient/Assets/Scripts/UI/OpeningSequence.cs` (the opening text); `InventorySlotUI.cs`, `TooltipUI.cs`
  (hover shows the name only); `nakama/data/species.json` (the 15 live species).
- `docs/product/design/game_design.md` §1, §2, §10, §11, §12.2, §18, §19 (January 2026 GDD).
- `docs/product/design/requirements.md` §12 and `docs/product/architecture/architecture_world.md` "Random Events"
  (the meteor infection idea, December 2025).
- `docs/brainstorms/ecology/bug_ecology_plan.md` (bugs as livestock; the food chain as progression).
- `docs/product/economy/DECISIONS.md` D31 (frogs); `docs/product/economy/crafting.md` (milk);
  `docs/product/investigations/research_look_and_feel.md` (ambient birds).
- Premise audit — game data: `nakama/data/entities/{items,occupants,placeables}.json` (`bone`, `bone_pile`,
  `cow_skull`, `cat_statue`, `hay_bale`, `birdbath`). Designs: `brainstorms/bugs/mining_caves.md` (cave bat, bat
  swarm, moth roost, cave crickets), `brainstorms/bug_farming/bug_farming.md` (aphid ranch, honeydew tap, ant dairy),
  `brainstorms/decorations/village.md` (horseshoes, dairy props, pets, statues, bird feeder, bird house, frog
  spout), `brainstorms/farming/farming_tools.md` (bone meal, owl decoy, cheese press),
  `brainstorms/objects/fishing_gear.md` (feathered fly), `brainstorms/objects/lighting_ambiance.md` (antler
  chandelier), `brainstorms/bugs/village.md` (robin), `economy/stats_and_bonuses.md` (Frog Legs, Lucky Rabbit's
  Foot), `economy/catalogs/accessories.md` (`cat_grace_band`, `frog_leg_charm`, lily glider),
  `economy/catalogs/materials.md` (frog toxin, bone meal), `economy/zones/deep_swamp.md` (bog frogs),
  `economy/zones/centipede_cavern.md` (bat guano), `economy/species_and_drops.md` (`strider_leg`, `stag_horn`,
  skater oil), `brainstorms/materials/ores_metals.md` (meteorite ore), `BACKLOG.md` (bearskin rug).
- Science: the cricket-farm virus — [PubMed 21167171](https://pubmed.ncbi.nlm.nih.gov/21167171/),
  [Genome Announcements 2013](https://journals.asm.org/doi/10.1128/genomea.00629-13).
