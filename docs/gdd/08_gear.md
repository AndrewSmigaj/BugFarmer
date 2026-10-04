# §08 · Gear, accessories & the character sheet
<!-- gdd: id=08 status=review updated=2026-10-02 -->

## The experience
Your character screen shows six meters as rows of dots — Health, Stamina, Armor, Strength, Speed and Stealth — then
your protection against stings, venom and acid, then a short list of what your gear lets you do, each in one plain
line with its number. Point at an outfit and the dots it would change light up before you put it on. You wear one
outfit whole and can change it any time from your bag: a bee suit at the hives, the ranger's kit in the wasp thicket,
the miner's gear, with a lamp on its helmet, in the deep tunnels. Two trade tools ride in your accessory slots, and a
meal, with maybe one potion, tops you up for the next stretch of play. Nothing is the best armour in the game: each
role has its own best set.

## Decided
Each line is the owner's decision in my words, with its date. (Armor is the spelling players see; this document
writes armour.)
- **Whole outfits, worn one at a time** (2026-08-05; D47, 2026-09-27) — no separate pieces; any outfit in your bag can
  be put on at any time. Each outfit is drawn as one complete set because cutting every piece out separately wasn't
  workable; that way of drawing them was confirmed tentatively on 2026-09-26, when the code-drawn pieces were
  rejected.
- **An armless character with floating hands** (2026-07-28) — the hands are separate fists moved by code, so a new
  weapon needs no new body poses. Every approved outfit is built this way.
- **How an outfit is made** (2026-09-26) — three designs in one image, one picked, then a turnaround, one walk per
  direction and the five hands, and the finished animations approved (the `player-sprites` skill). Made: bronze,
  fire-ant, black-ant and copper. Picked, not yet made: iron, platinum, steel, leather, beetle-shell, gilded-steel and
  fancy; since 2026-10-01 (D75) gilded steel is cut and Fancy Armor uses the fancy design, so the platinum and
  gilded-steel designs have no armour for now.
- **Armour is made of a material**, never a costume of the creature, and faces show (August 2026). Trinkets and
  shields are not for now (August 2026).
- **Defence is the spine** (2026-08-06) — combat matters, so every armour and working outfit carries defence beside
  its other bonuses.
- **No constant changing, never single-purpose** (2026-08-06) — outfits shouldn't need micromanaging; each keeps
  defence plus other bonuses. **A working outfit raises a yield or makes a job easier, and its description says how**
  (D47, 2026-09-27).
- **Each role has its own best set** (2026-08-06) — stealth, mining, combat and the other roles each have a best
  version, a best tank, a best agility set and so on, with a few hybrids that mix two; some sets are best in one place
  or against one kind of bug.
- **Decorative outfits** (2026-08-07) — clothes that exist to look good, whose bonus is the farm's output or its
  happiness, like furniture; they count when shown on a mannequin, and so does armour made for show, such as Fancy
  Armor (2026-10-01, D75). Mannequins show whole outfits on a plain white-faced figure (2026-09-27).
- **Outfits are hidden through the world** (2026-08-06) — nearly every area holds at least one outfit recipe, often
  calling for materials from that area; more gather in the towns and the mining camp.
- **More outfits, without flooding** (2026-08-06) — more are wanted, but not so many that each one means less. **No
  art budget limits the roster** (2026-10-02, D76).
- **Dye recolours cloth outfits** (2026-09-27, D44); the dye vat dyes cloth (2026-06-28).
- **Player characters come in several skin colours** — the same base, recoloured (2026-09-27, D47). The wizard's robe
  is dropped; an alchemist's robe comes with the potion station (D47).
- **Stamina is for dodging and running** (P14, accepted 2026-09-28) — tools, farming and catching never tire you;
  gear can make the pool bigger or refill it faster.
- **Never colour alone; gamepad menus move by focus** (P24, accepted 2026-09-28).
- **Nothing goes faster for one player than another** in the shared world (2026-09-28, D58).
- **The armour batch** (2026-10-01, D75) — the metal sets are armour: Copper, Bronze, Iron, Steel and Cobalt-Steel
  Armor. A new character starts in the Farmer's Outfit; Bug-Leather Armor is an early craft. Gilded steel is cut;
  Fancy Armor, made with gold and the high metals and not the strongest, raises a plot's happiness on a mannequin.
  Cobalt-Steel Armor gets its own late-game look.
- **Bee suits** (2026-10-01, D75) — the bee suit stops every sting but is weak armour, worn for the bees; the ranger
  outfit stops wasp and hornet stings and is quicker and better armoured; the Padded Bee Suit comes later with real
  armour. Fire ants and scorpions still hurt a bee-suited player through their bites and claws.
- **Accessories** (2026-10-01, D75) — two slots, as today. After his marks they are the work tools and the lights: the
  garden gloves, seed tin, hive tool, oven mitts, tape measure, thimble, ore sieve, dyer's gloves, both headlamps, the
  first-aid kit, and the telescopic net pole on trial; a station accessory gives a 30% chance of an extra.
- **The character sheet, as a start** (2026-10-02, D76) — six meters shown as dots, three protections and a list of
  standalone perks, with a job for each kind of item; a meal raises Health and Stamina while it lasts, better food
  more. These are guidelines, not laws: an item may break the pattern when that makes sense. Small mechanics are perks
  rather than items of their own, and an outfit can carry several.

## Current design
- **The January 2026 design** sets the tone: progress comes from tools, knowledge and preparation, not skill trees or
  stat grinding; accessories are few, small and meaningful, with no endless loot (`game_design.md` §14–15).
- **The armour catalog** (June 2026, D10–D11) set two layers, a metal ladder and a few sets built around an idea
  rather than one per zone; the item pass has since replaced its rungs (P20, D75).
- **The stat menu** (June 2026, `stats_and_bonuses.md`) lists everything gear could change, stores each bonus as a
  named entry the server adds up, and caps the big ones; it keeps bonuses to catching, mining and farming outside the
  shared bug simulation. Its durability stat went when tools stopped wearing out (D49).
- **The roster** (August 2026, `outfit_roster_scratchpad.md`, `brainstorm_armor.md`) is now rows in the item table: 41
  outfits and armours, plus families of decorative, fishing and farming outfits, each with a place in the world. The
  August brainstorm also suggested ideas of my own that are not decided: that an outfit suits a trip rather than one
  action, that it carries defence plus two or three bonuses, and that each can be summed up in one phrase no other
  outfit shares. Its levers: defence and strength, stealth, speed, harvest, fishing, catching, light, carrying, and
  protection against hazards (venom, acid, the dark, heat).

## As built
- Eight equipment slots: head, body, arms, legs, feet, two accessories and a backpack
  (`nakama/modules/world/handlers_world.go` line 812). The game draws the first five on the player; accessories
  don't show (`BugFarmerClient/Assets/Scripts/Player/CharacterComposer.cs` line 47).
- Armour shows on other players but does nothing, except the bee suit: a body piece marked `sting_immune` cancels
  every sting, while bites still land (`handlers_player.go` lines 73–80). The stinging bugs today are the honeybee,
  both wasps and the giant hornet (`nakama/data/species.json`); no black ant, fire ant, scorpion or spider exists yet,
  and there is no venom or acid yet.
- Worn items carry no stats beyond their slot, the bee suit's flag and the backpack's extra slots (`entities.go` lines
  57–67). Health is 10, shown as hearts, and a bite does 1 to 4.

## How it will work
- **The five armour slots become one outfit slot** (D47), beside the two accessories and the backpack. The backpack
  keeps adding bag space; carrying shows in the bag, not on the sheet.
- **Every bonus is a named entry**: where it comes from (the outfit, an accessory, the meal, the potion, a place),
  what it changes (a meter, a protection or a perk), by how much, and when it ends if it's timed. Totals are always
  worked out again from those entries, so taking something off removes exactly its bonus; the server keeps track of
  Health and damage, as today. The sheet's numbers and its words come from the same entries, so they can't disagree.
- **The numbers need a finer scale than today's** (Health 10, bites of 1 to 4): for example Health in tens and hits of
  10 to 40, set when combat is tuned. Every number in this section is an example until then.
- **What touches the shared bug world is the costly part.** Stealth, the perks for one kind of bug (P8), faster
  dragging and faster calming all change what bugs do, so each player's values must be known to every player's game
  and used the same way, through the checks that keep every player's bugs identical. Everything else on the sheet
  stays outside the bug simulation.
- Items gain new data for their dots, protections and perks.

## Proposals
### P1. Six meters, ten dots each
<!-- key: 08.six-meters-ten-dots-each -->
The sheet shows six meters as rows of ten dots; you start partway up each (Armor starts at what your outfit gives),
and items add or take away whole dots. What each one means (the numbers are examples, set when combat is tuned):

| meter | what it does | start | raised by | lowered by |
|---|---|---|---|---|
| Health | the most health you can have | 5 dots (today's 10 hearts) | meals, the pollen tonic | — |
| Stamina | your pool for dodging and running (P14) | 5 | meals, some outfits (the Stamina Tonic makes it refill faster instead, P5) | heavy armour |
| Armor | how much every hit is lowered, about 8% a dot | from your outfit | outfits, toughening meals, the mint balm | — |
| Strength | how hard your weapons hit | 5 | the strength drink | — |
| Speed | your walking pace | 5 | speed meals, coffee, a few light outfits | heavy armour |
| Stealth | how close a bug gets before it notices you | 5 | stealth outfits, the cover scent | — |

A dot looks different by where it comes from, so the row reads without colour (P24): a **round dot** is what you
have with nothing worn or eaten; a **square dot** comes from your outfit and stays while you wear it;
a **round dot with a ring** comes from your meal or potion and goes when its time runs out; an **empty dot with a
slash** was taken away by an item; an **empty outline** is not yet reached. They always sit in that order, left to
right. Pointing at a meter (or moving to it on a gamepad) shows the number, what it means in play and where every dot
comes from — for example "Speed 5 of 10: you walk at the normal pace. One more dot: 5% faster. Starting 5, Steel
Armor −1, a speed meal +1 (8 minutes left)."

**Lenses:** Readability — Minecraft draws health and armour as segments players count at a glance, and RimWorld's
"where does this number come from" breakdown keeps hundreds of stats readable; Grounded's players asked for exactly
the totals Grounded didn't show. Strength stays the fighter's meter; Health, Stamina, Speed and Stealth serve every
player. **Cost and risk:** a character screen built from scratch; its dot shapes are drawn in code, like the rest of
the interface (D60).

### P2. A job for each kind of item
<!-- key: 08.job-each-kind-item -->
| item | what it can do |
|---|---|
| Outfit (one, worn whole) | sets Armor and protections, can shift one or two other meters, and gives one to three perks that suit its role |
| Accessories (two) | perks only: the work tools and the lights |
| Meal (one) | raises the most Health and Stamina you can have while it lasts (D76) and heals you over a while (D54), better food more, and often adds one of the eight food boosts |
| Potion (one timed) | one strong, short change: a meter, a protection or a perk |
| Tools | their metal is their power; meters never change them, so the ore ladder holds |
| Weapons | damage, speed, reach and one trait; Strength makes every weapon hit harder |

Read this way, each item explains itself in a line: the bee suit is "Armor ●, stops every sting"; the ranger outfit
"Armor ●●●, Speed +●, wasp and hornet stings can't get through"; Strong Coffee "Speed +2 for 3 minutes". Of the eight
food boosts, Stamina, Sturdy and Swift become dots on Stamina, Armor and Speed, and the work boosts (harvest,
foraging, fishing, net reach, mining) become perks. Not everything from the cauldron is a timed potion: cures and
heals (the antivenom, the burn salve, bandages, the healing potion with its wait) work any time and don't take the
potion's place, and the bug bomb, the calm spray and the plot's incense don't touch the sheet at all. Exceptions are
fine where an item calls for one: coffee is made and sold with food but takes the potion's place.

**Lenses:** Readability — one grammar for every item. Premise — tools stay the gate to deeper ore (P20), so nothing
on the sheet skips a pickaxe. Balance — the slots themselves limit how many things can touch a meter. **Cost and
risk:** every item in the table needs its dots, protections and perks written down; a pass over the rows.

### P3. Three protections: stings, venom and acid
<!-- key: 08.three-protections-stings-venom-acid -->
Every bite, pinch or sting is a hit, and Armor lowers it. On top of that:
- **Sting** lowers what a sting does — bees, wasps, hornets, fire ants, scorpions. The bee suit stops every sting
  completely, and the ranger outfit stops wasps' and hornets' (D75).
- **Venom** is what some stings and bites leave in you — wasps, hornets, centipedes, fire ants, scorpions, spiders;
  Venom protection makes it hurt less and end sooner.
- **Acid** covers burns from sprays — the black ants' acid and the millipedes' — and lowers both the burn and how long
  it lasts.

So a scorpion is claws (Armor), a sting (Sting) and its venom (Venom); a fire ant is a bite (Armor) and a sting (Sting
and Venom). Each protection shows as an icon and a percentage in steps of 10 ("Venom 40%"). Protections from different
slots add up, to at most 80%; Armor and a protection then work one after the other, so Armor that halves a hit and
Sting 50% let a quarter of a sting through. A small share of every hit always lands, shown on the sheet — except where
an item stops a kind of sting completely, as the bee suit does. An outfit with a weakness can show a minus. Pointing
at a protection turns it into a real case: "a wasp sting: 30 → 20". Heat, which the August list named, isn't among
them; it could become a perk if a hot zone ever needs it.

**Lenses:** Premise — the bugs' own weapons, true to life: fire ants bite to grip and then sting, and scorpions grab
with their claws and sting; the game chooses which stings and bites leave venom behind, and a sting that's stopped
leaves none. Readability — dots for meters and percentages for protections keep
the two kinds of number visibly apart; Grounded's ten damage types are a lot to learn. **Cost and risk:** venom and
acid aren't built yet, and fire ants and scorpions need a two-part attack (today each bug has one).

### P4. One rule for adding up
<!-- key: 08.one-rule-adding-up -->
Each slot holds one thing and the slots add up: the outfit, two accessories, the meal and the potion. Meters stop at
their top (Q2) and protections at their cap; a wasted dot shows as a dim "+1 over", and an item warns you before you
put it on ("Speed +1 — wasted, Speed is already full"). Two perks of the same kind add up, to a limit set for each
kind and shown on the perk. Perks that speed a tool — a mining meal, the Miner's Gear — save at most one hit per block
between them and never let a pickaxe break what its metal can't (P20, P21). A cut against one kind of bug (P5) works
like a protection, after Armor. As decided, a new meal replaces the last (D54); eating the same one again resets its
time, and potions work the same way. Timed effects end when you faint.

**Lenses:** Readability — a rule you can say in one sentence; Core Keeper's players were still arguing about its food
rule years later. What can go wrong — every dot comes from a named entry, so no bonus can get stuck on. **Cost and
risk:** small; it decides the arithmetic every other proposal uses.

### P5. Two kinds of perk, in standard sizes
<!-- key: 08.two-kinds-perk-standard-sizes -->
- **Switches** change what you can do: night vision, a lamp in your helmet, no knockback, a bug that bites you takes
  a hit back, a wider view. You have one or you don't.
- **Sized perks** come in three sizes from one table, written on the item as a number:

| kind | small | medium | large |
|---|---|---|---|
| more from a job (planks, honey, ore, a harvest) | 15% chance of an extra | 30% | 50% |
| something you do yourself, done faster (dragging, reeling) | 15% less time | 30% less | 45% less |
| reach or light, in squares | +1 | +2 | +3 |
| harm from one kind of bug | 15% less | 30% | 50% |
| your hits on one kind of bug | 15% more | 30% | 50% |
| healing you give | 15% more | 30% | 50% |
| stamina refill | 15% faster | 30% | 50% |

Meter shifts — from outfits, meals and potions, never accessories — come in the same sizes, +1, +2 or +3 dots, and
don't count against a perk budget (P10). Your station accessories' 30% is the medium size. Every perk is one sentence
with one number, never vague words, and the smallest size must make a difference you can feel — at least one extra
item in an ordinary batch. No small conditional perks ("+5% against slowed bugs"). "Faster" perks only speed what your
own character does; stations, crops and bugs run the same for everyone (D58). An outfit whose Stealth changes only at
night or while walking shows that as a perk line rather than dots.

**Lenses:** Readability — Monster Hunter and Terraria use fixed steps players learn once; Grounded used one name for
effects from 2% to 50%, and its players had to look the size up; Grounded later raised one trinket's effect from 10%
to 50%. **Cost and risk:** the table is tuning, and it can grow a kind when a real item needs one.

### P6. See it before you wear it
<!-- key: 08.see-before-wear -->
Pointing at an outfit, accessory, meal or potion shows the result on the sheet: dots that would be gained pulse with a
small +, dots that would be lost pulse with a small −, and perks that would come or go are marked + or −. The item's
own box lists only what changes, best first. A meal or potion says what it would replace and how long that has left
("replaces your Fly Soup, 3 minutes left") and warns if it's weaker or would waste dots. With both accessory slots
full, a new accessory asks which one it replaces and previews both. With reduced motion on (P24), the + and − marks
alone show the change. Since an outfit is worn whole, there's only ever one outfit to compare with.

**Lenses:** Readability — Elden Ring and Monster Hunter show the changed numbers beside the current ones, and Slay the
Spire shows the result before you act. Picture the moment — standing at the blacksmith's, watching your Speed lose a
dot as you look at the steel armour. **Cost and risk:** part of the character screen's build.

### P7. Two spots for what's running out
<!-- key: 08.two-spots-whats-running-out -->
Beside Health and Stamina sit two fixed spots, one for your meal and one for your potion: the item's icon, a ring that
drains, the minutes left, a slow blink near the end (no fast flashing, P24), and a faint outline when empty — a quiet
reminder that you could eat. Other effects (venom in you, an acid burn, the healing potion's wait, night vision from
the Shadow Robe) go in one short row: round frames for timed effects, square for gear, none for a place, each with
an up or down arrow. Pointing at one gives its name, its number, its time left and where it came from.

**Lenses:** Readability — Minecraft and Stardew Valley blink an effect near its end; Elden Ring's frame shapes show
where an effect comes from. Because the game allows one meal and one potion, this area never grows. **Cost and risk:**
small, on the always-on display.

### P8. Perks for one kind of bug
<!-- key: 08.perks-one-kind-bug -->
Some of the clearest perks are about how one kind of bug treats you: black ants taking you for one of their own until
you strike one (offered as a costly option on the Black-Ant Armor's row), skittish flies fleeing later (the
entomologist's coat), curious butterflies coming from further away (the collector's whites). They sit beside Stealth:
Stealth says how close any bug gets before it notices you, and these perks say which kind doesn't mind you, which
keeps alive the August point that a bee suit is for bees. A perk like this can carry its own cost. Grounded's bard hat
makes wasps neutral but bees always hostile, and its red-ant armour makes red soldier ants passive. In play you can
see it work: a bug that notices you reacts — a wasp turns on you, a fly darts away — and one that accepts you goes on
with what it was doing.

**Lenses:** Premise — bugs raised like livestock and a world that answers what you do; a rancher whose ants accept
them is the fantasy. Picture the moment — walking through the colony in Black-Ant Armor while the ants go about their
work around you. **Cost and risk:** each one changes what bugs do, so each needs the shared-world checks; few and
chosen.

### P9. Heavier armour costs something
<!-- key: 08.heavier-armour-costs-something -->
Each tier has light, medium and heavy outfits. Light ones give a dot or two less Armor than the metal armour of the
same tier and cost nothing; heavy ones give the most Armor and a slashed dot of Speed or Stamina. The role outfits are
mostly light, the metal armours medium and heavy, and a few, like the Brigandine, trade a little Armor for speed. As a
sketch, the armours climb from about 2 dots (bug leather) to about 7 (cobalt steel), the legendary sets a little
higher, and meals and potions add the rest — so ten dots hold the whole ladder. The cost shows on the sheet as a lost
dot, so it's never hidden. Worn, a decorative outfit is the lightest of all, a dot of Armor and no perks; its bonus
counts on a mannequin (D75).

**Lenses:** Balance — the roster's rules already make heavier armour a little slower; Grounded's light, medium and
heavy armour trade damage taken for stamina the same way. Readability — the trade-off is visible in the dots. **Cost
and risk:** the roster's rows each need a weight; a tuning pass.

### P10. The sheet stays the same size
<!-- key: 08.sheet-stays-same-size -->
The six meters and three protections never grow: a new idea becomes a perk, either a switch or a sized perk. Perks you
don't have are hidden, so the list only shows what you have. Each kind of item has a perk budget — outfit one to
three, accessory one or two, meal one boost, potion one change — so the sheet stays around ten lines however big the
item list grows. Meter shifts don't count against the budget.

**Lenses:** Readability — Diablo IV's 2024 overhaul cut its items down to two or three stronger lines because players
couldn't tell what was an upgrade; RimWorld hides stats at their default. Fit — the sheet is a start, not a law, so an
item can still break the pattern on purpose. **Cost and risk:** none to build; it is a rule for writing new items.

## Questions
### Q1. Should the fire-ant and scorpion armours stop their own bugs' stings completely?
<!-- key: 08.fire-ant-scorpion-armours-stop -->
The bee suit stops every sting and the ranger outfit stops wasps' and hornets' (your calls, D75). The roster also has
the Fire-Ant Armor and the Scorpion Armor stopping their own bugs' stings. Every other protection stops at 80% (P3).
- **A.** Yes: the Fire-Ant and Scorpion Armor stop their own bugs' stings completely, and their plates cut those bugs'
  bites and claws by half (the large size, P5) — the key to each zone. The cost: once you have it, that zone's stings
  stop mattering, so the zone gets much easier for whoever has its armour.
- **B.** No: they lower those stings strongly, to the usual cap, and only the bee suit and the ranger outfit stop a
  sting completely.

**Recommendation: A.** It makes each armour the answer to its own zone, the way the ranger outfit is to the wasp
thicket, and it still differs from the bee suit, which stops every sting but leaves you open to bites and claws.

### Q2. How full can a meter get?
<!-- key: 08.full-can-meter-get -->
Each meter has ten dots (P1), and the best armour reaches about 7 or 8 (P9).
- **A.** Gear can reach ten.
- **B.** Gear tops out at eight, and only meals and potions fill the last two.
- **C.** Gear can reach ten, and a few legendary items lift one meter past ten.

**Recommendation: B.** A good meal and the right potion then always matter, even in the best gear, and nobody sits at
a full meter with food that does nothing.

## To settle later (not in this review)
- **How big the player is on screen.** The finished outfits are 64–91 pixels tall (bronze to black-ant); the game
  still draws the old 16×32 farmer. To be decided by looking at a rendered scene, not in the abstract (backlog,
  2026-07-29).
- **Character choices** — today you pick a class, hair and skin (5 × 5 × 3, `CharacterSelectPanel.cs` lines 28–30).
  Skin colours stay (D47); since each outfit is drawn with its own head, hair and helmet, a hair choice would multiply
  every outfit's art, so how hair and class work with whole outfits is still open.
- **Other players** — whether you can see a friend's sheet, and whether healing perks count for the giver.
- **Tool motions still missing** — the game animates 9 tools; the sword has approved motions in all three facings;
  axe, hoe, net and shovel only side-on; pickaxe, scythe, spear and watering can none (§09).
- **The roster itself** is reviewed row by row on the items page; still open there: a third legendary set, fourth
  tiers for fishing and beekeeping gear, and the outfits' names.

## Sources
- Your answers, 2026-06-28 to 2026-10-02 — restated above; `docs/product/economy/DECISIONS.md` D10, D11, D44, D47,
  D49, D58, D60, D75, D76; `docs/gdd/overview.md` part 9, P14, P15, P20, P21, P24, P26.
- `docs/product/design/brainstorm_armor.md`, `docs/product/design/outfit_roster_scratchpad.md` (August 2026),
  `docs/product/economy/stats_and_bonuses.md`, `docs/product/economy/catalogs/armor.md`,
  `docs/product/economy/catalogs/accessories.md`, `docs/brainstorms/armor/armor_clothing.md`,
  `docs/product/investigations/dye-station-design.md`; `docs/product/design/game_design.md` §14–15 (January 2026).
- The item table, `docs/gdd/item_table.jsonl` (the armour, accessory and potion rows).
- Research: `docs/product/investigations/research-2026-10-02/stat-sheet-and-perks.md` (16 games, 60 sources:
  Minecraft, Terraria, Stardew Valley, Valheim, Grounded and Grounded 2, Core Keeper, RimWorld, Necesse, Don't Starve,
  Hades, Slay the Spire, Diablo IV, Monster Hunter, Elden Ring, and three open-source games); Grounded's wiki, checked
  2026-10-02 (the red-ant armour's set bonus, the bard hat's wasp perk, the aphid slippers); a cold review of this
  section (2026-10-02).
- Code: `nakama/modules/world/handlers_world.go`, `handlers_player.go`, `entities.go`, `nakama/data/species.json`,
  `BugFarmerClient/Assets/Scripts/Player/CharacterComposer.cs`.
