# Armour & outfit design — brainstorm

> **Replaced in part (P1, accepted 2026-09-28)** — later decisions stand over this document: diving isn't part of the game (August 2026), so a diver's set and any diving here are dropped; marsh waders become a wading outfit for shallow water, and deep water takes a boat (D51). See `docs/gdd/overview.md` and `docs/product/economy/DECISIONS.md`.


Working document for the outfit roster. **Owner rulings are restated in clean prose, dated and attributed — never his words; everything else is a proposal.**
Numbers are deliberately absent — this is about what each set IS FOR, not balance.

Related: [`../economy/DECISIONS.md`](../economy/DECISIONS.md) D10/D11 · [`../economy/catalogs/armor.md`](../economy/catalogs/armor.md)
· [`../economy/stats_and_bonuses.md`](../economy/stats_and_bonuses.md) (the 36-stat vocab).

---

## 1. The frame

> Owner direction (2026-08-06): combat is an important part of the game, not a minor one, with many levers
> the armours can move. Defence must not be treated as one aspect served by a small set of defence-related
> armours — defence is critical.

**Defence is the spine, not a side category.** The base ladder is the backbone of progression; every
specialty set still carries real defence plus its perk. A set is never perk-only.

**Above steel, a set should be a KEY to a hazard, not a bigger number.** The zones already pose distinct
problems — venom (Scorpion Rocks, Spider Vale), **acid** (Deadly Ants is the "fire/acid endgame", and
`formic_acid` is a live item), water (swamps, underground river), dark (caves), heat. A set that answers a
hazard makes finding it feel like unlocking a place.

**Delivery is the point.** Owner direction: nearly every area hides at least one outfit recipe (in a chest,
with a vendor, and so on) that calls for materials, some of them new to that zone — at least one new
outfit per zone. More recipes concentrate in the **two towns** (Starting Village, NW town) and the
**Mining Camp**.

> **This does not contradict D10** ("sets are CONCEPTUAL, not one-per-zone"). D10 governs what a set IS;
> this governs where you FIND it. A zone hands you a material and a hidden recipe; the set it unlocks can
> still belong to a concept line — "mining tier 2" can perfectly well be the thing hidden in the Passages.

---

## 2. The levers

Owner's list, plus three the mining line needs. Each outfit moves **one primary + one or two minor** —
the owner's example: one set might raise boat speed and also give a fishing-speed or similar bonus.

| lever | notes |
|---|---|
| **Defence / strength** | the spine. Every set has some |
| **Stealth / being ignored** | some are species-specific — a beesuit only helps against the various bees (owner) — so stealth is not one number; species-scoped immunity already exists (`sting_immune`) |
| **Speed / agility** | |
| **Harvest yield** | the player gets a percentage of the available harvest and the rest is lost (owner) — finishing farming is backlogged |
| **Fishing + boat speed** | weak alone, so these sets carry two bonuses |
| **Bug catching** | bugs avoid the wearer less, and nest-harvest rates are higher (owner) |
| *(added)* **Light** | caves are dark; the Miner's kit already designs a built-in `light_radius` so no torch is needed |
| *(added)* **Carry weight** | mining's real constraint |
| *(added)* **Hazard / element resist** | acid, venom, heat — what makes the gilded and specialist sets keys |

---

## 3. The base ladder — leather → platinum

Owner: bronze **cut** (too similar to copper), tin **cut**, stone/rock **cut**, silver-as-a-set **cut**.

| rung | source |
|---|---|
| leather | processing bugs |
| **wood** | a step up from leather, obtained by processing bugs (owner) — bug processing station |
| copper | |
| iron | |
| steel | |
| platinum | the top (D11) |

Six rungs — tight and readable. The metal specials below sit **beside** platinum as specialists rather
than under it, so the top of the game is *"which key do I need"* rather than *"do I have the best one yet."*

## 4. Metal specials

| set | what it is | why it is not just "fancy" |
|---|---|---|
| **Gilded steel plate** ✅ | gold leaf over a steel core | Gold **never corrodes** → acid-proof, the Deadly Ants counter. Logical *because* gold is too soft to forge alone — it is a skin, not a body |
| **Fancy plate** ✅ | silver in an expensive, ordinary plate. Recipe from the **NW town** | Owner: a standard, non-magical, expensive plate with decent defence. Silver earns its place by cost, not by magic |

**Cut, and why** — kept as a record so they are not re-proposed:
*blackened silver* (owner: doesn't make sense) · *silvered chitin* · *honeycomb plate* (owner: too fragile
for armour) · *royal-jelly lining* (owner: it would not heal anyone by being in armour) ·
*crystal* (owner: crystals would not add much).

**Wax / waterproofing — parked.** Owner: the game already has ways to move faster through marsh and
shallow water. Only worth a stat if **deep** water becomes traversable; otherwise beeswax stays a
crafting ingredient, not a bonus.

**Amber — open.** Owner: amber is a possibility, but no bug produces it yet. Worth noting amber is
fossilised **tree resin**, not bug-made — so the Millipede Forest could source it without any new bug. A
bug *trapped* in amber is then a collectible, not the source.

## 5. The legendaries — secrets

> The owner wants secrets.

A few of the strongest sets in the game (two or three), each behind a find rather than a shop:

1. **Queens' set** — needs parts from **both** colony queens (the col-0 intro colony and the col-3 deadly
   one) plus rare metals, locked in a chest in a small underground fortress (owner) → **backlogged**.
   Requiring both queens is good design: it forces you across the whole underground, east and west.
2. **Spider-plate set** — built on spider plate. Gated behind Spider Vale, so it is endgame by geography.
3. *(slot open for a third)*

## 6. Categories — three tiers minimum each

Owner: perhaps a minimum of 3 tiers per category. The tiers have natural homes in the world already:

| category | t1 | t2 | t3 |
|---|---|---|---|
| **Stealth** | cave-spider silk — Underground Passages | orb-weaver — Spider Vale West | widow — Spider Vale East |
| **Mining** | Underground Passages (3,1) | deep — Cavern / row 4 | Deadly Ants col 3 |
| **Fishing** | shore / Bee Meadow coast | swamp + river | underground lake, sunken ruins (4,2) |
| **Beekeeping** | plain cloth | the NPC's fancy suit | armoured, for the aggressive bees |
| **Farming** | plain farmer | fancy farmer | *see below* |
| **Bug catching** | **one** entomologist, plus several others that help differently | | |

**Farming's third tier** — the owner noted these are not obvious. Proposal: since the lever is *% of available
harvest*, tier the sets by **what they change** rather than by material —
plain (yield %) → fancy (yield % + range: `harvest_aoe`/`water_aoe` are already built stats) → a
**bug-component** set. The obvious one is a **pollinator's kit** from bee materials (flowering crops), or a
**composter's** set from carrion beetles, which already carry `produces_compost`.

**Combat sets** carry real defence plus a small perk — the ant chitin pair (fireant, blackant — owner:
the game has two ant species, in different zones), wasp, hornet.

---

## 7. Two rules that decide what a bonus may be

### An outfit suits an EXPEDITION, not an ACTION

> Owner direction: outfits should not need micromanaging or constant swapping, and should not be
> completely single-purpose — they still have defence, plus other bonuses.

Every outfit is **defence + two or three bonuses**, chosen so you pick one for a **trip**. The mining kit
carries you through digging, fighting what lives down there, and hauling back — you do not change clothes
at each activity. This is the test that kills single-purpose ideas: a *composter's* or *pollinator's* set
fails it, which is why the owner is right that **tools are the better home for those**.

### An outfit changes what YOU DO — a decoration changes what the PLACE IS

The owner raised two doubts that are the same doubt:

- In the shared open world, nothing can go faster for one player than for everyone else.
- Why should wearing a better farming outfit increase output on the home plot?

Both fail for one reason. "Faster growth in this area" is **world state**; "your home honey rate" is
**place state**; neither can be personal, and the home plot is **idle** content while an outfit is **worn**.
An outfit that boosts idle output either has to be worn while you idle — which is not idle, and wastes the
slot — or apply while unworn, which is incoherent.

**So a FUNCTIONAL outfit's bonuses attach to VERBS.** Watering AoE when you water, extra-crop chance when
you harvest, seed return when you plant, carry when you haul. Personal, active, and safe in a shared world
by construction. A mining or farming set should not quietly boost idle output.

> ⚠ **I over-applied this.** The owner was *musing* — he said it might not work well as a design — and I
> wrote it up as a law, then used it to cut festival wear. He corrected it 2026-08-07:
>
> Some outfits are wanted as clothes that simply look good, whose only bonus is to the player's farm output,
> happiness or decoration; in that sense outfits work like decorations, and he likes them.
>
> **There is a third class: DECORATIVE outfits.** Clothes that exist to look good, sold and found across
> different zones, whose whole bonus may be farm output or happiness — the same role furniture plays. They
> are not filler and the verb rule does not govern them. The rule above constrains **functional** sets so
> they do not become idle-boosters; it was never meant to ban the decorative class.

## 8. Farming — the naming problem

Owner: undecided on the three farming outfits — they are not obvious.

The game is **Bug** Farmer, so farming has two halves. Splitting on that gives three without inventing a
third crop tier that has no identity:

| | covers | bonuses (verbs) |
|---|---|---|
| **Farmhand** | starter, general | small yield, small carry |
| **Market gardener** | the crop half | extra-crop chance, watering AoE, carry |
| **Bug rancher** | the bug half — owner's word | nest-harvest yield, calm radius, handling |

Bug rancher moves **your** yield and **your** handling, never breeding rates — the shared-world constraint
above.

## 9. There is no single best armour. Every ROLE has its own apex.

> Owner direction (2026-08-06): stealth, mining, combat and the other roles each have their own best
> version, plus a few hybrids that mix them — a best stealth set, a best mining set, a best tank, a best
> agility set, and so on.
>
> The spider-zone stealth set is NOT the top outfit.

**Not one ladder, and not two — a set of roles, each with its own top.** Tank · attack · agility · stealth ·
mining · fishing · farming · bug-catching · beekeeping. Nothing is "the best armour in the game"; a set is
the best *at something*. This is why *"which key do I need"* beats *"do I have the best one yet"*, and it is
the shape that pays off the curiosity lens — no zone hands you the endgame, each hands you the top of one
thing.

**Two axes, and an outfit sits on both.**

| axis | what it means |
|---|---|
| **Role** | tank, attack, agility, stealth, mining, fishing, farming, catching — each has an apex |
| **Situation** | bonus defence and/or attack against wasps compared with other armours in the zone (owner) — best HERE, or against THIS, rather than best outright |

The situational axis is the expedition rule again: you bring gear for **where you are going**, not for a
number. And it lets a mid-tier set be genuinely correct in its own zone, which keeps old sets alive.

**Hybrids are first-class** — a few sets mix roles. The named example:

> **Underground combat-mining set** — ant parts, mining buffs *and* real combat. Only the spider-zone
> combat gear beats it **as combat gear**, while being far better than it at mining. That is exactly
> how a hybrid should read: top of nothing, strong at two things.

⚠ **Correction:** `fireant` and `blackant` are **combat/chitin sets, NOT mining outfits.** The ant-parts
mining hybrid above is a separate, deeper set.

*(Difficulty context, owner: the upper surface and the lower underground are roughly even; swamp ≈
underground river ≈ lake; Spider Vale is the hardest surface zone and the fireant domain the hardest
underground one. So the hardest zones are peers — but "hardest zone" produces "best of a role", not
"best overall".)*

## 10. Settled 2026-08-06 — ranger, forest, thorns, catching

**Ranger — YES, and it is the wasp/hornet answer.** The owner confirmed ranger armour as the wasp and
hornet protection. You get it in a zone with **a small outpost overrun by wasps and
hornets, fed by an active fly bubble** — that zone is **not designed yet**.

**Forest — a separate set, keep the plain name.** The owner kept the plain name; it gives a bonus in forest zones and
perhaps in forest-related activities. So ranger and forest both exist; ranger is anti-wasp, forest is
place-and-material.

**Thorn armour — 3 tiers, a combat buff.** Attackers that hit the wearer get stung (owner). The tiers follow
the species ladder that already exists (`wasp_common` → `wasp_soldier` → `hornet_giant`), so **wasp thorn**
and **hornet thorn** are two of the three. The owner doubted candidates are needed — the look follows from
the bug, so the proposal is **explore tier 1 only, then tiers 2–3 reference that design** with the material
and spine-intensity stepped up. Same pattern as the gauntlets referencing bronze: one design, then variants.

**Bug-catching — 3 outfits, one lever family, conceptually distinct.** Not three entomologist
outfits, but three outfits that do similar things — bugs ignoring the wearer, and harvest success rate
(owner). So: **entomologist** (the scientist), **butterfly collector** (butterfly-scoped), and a
third yet to be named — all moving *being ignored* and *harvest success*, none of them a re-skin.

**Build the sprite ahead of the mechanic.** Ocean zones and hostile bees are backlogged and stay
backlogged. Owner direction: sprite production does not pause to build every related mechanic;
the current focus is creating sprites.

## 11. The saturation test

> Owner direction (2026-08-06): more outfits are wanted, but not so many that the roster is flooded and
> each one means less.

**A set earns its slot if you can say what it is FOR in one phrase, and no other set has the same answer.**
Two sets with the same answer means one of them is filler, and filler is what makes a wardrobe feel cheap.

Corollary the owner gave, and it is freeing: **not every bug needs an outfit.** Some bugs may only be
used for certain tools — it is fine to have no mosquito-based armour, for example, if the mosquito feeds a
weapon. Bugs feed tools, weapons, potions and decor as well as armour.

## 12. The roster — zone by zone

Every zone gives at least one, none give the same answer twice.

| zone | set(s) | role it tops or serves |
|---|---|---|
| (0,0) Locust Farmland | — | **none.** D10 cut the locust set; it is a place you defend, not a look |
| (0,1) Millipede Forest | **forest** | situational: forest zones + forest materials |
| (0,2) Spider Vale W | silk (mid) | stealth |
| (0,3) Spider Vale E | **widow** · **spider-plate** ⭐ | stealth apex · a legendary |
| (1,0) Meadow | beekeeper (armoured) | beekeeping apex |
| (1,1) Butterfly Fields | **butterfly collector** | catching |
| (1,2) Scorpion Rocks *(sand/desert)* | **scorpion** | combat + venom/heat — **NEW, owner asked** |
| (1,3) Deep Swamp | swamp gear | situational: marsh traversal |
| (2,0) Bee Meadow | beekeeper (plain) | beekeeping t1 |
| (2,1) **Village** *(town → many recipes)* | farmhand · market gardener · **village alchemist** · **dyed clothes** | farming · potions · utility |
| (2,2) Wasp Thicket *(outpost, wasp/hornet infested)* | **ranger** | anti-wasp/hornet |
| (2,3) Shallow Swamp *(dock, Fisher's hut)* | fisherman | fishing t1 |
| (3,0) Ant Colony intro | **fireant ✅ · blackant ✅** | combat/chitin |
| (3,1) Underground Passages | mining t1 · cave-spider silk | mining · stealth t1 |
| (3,2) Underground River | fishing t2 / diving | fishing |
| (3,3) Deadly Ants outpost | thorn line | combat buff |
| (4,0) Ant Colony + Queen | **queens' set** ⭐ *(part 1)* | a legendary |
| (4,1) Centipede Cavern | **glowworm** | light |
| (4,2) Underground River deep *(sunken ruins)* | fishing/diving apex | fishing apex |
| (4,3) Deadly Ants core | **ant combat-mining hybrid** · queens' set *(part 2)* | hybrid · legendary |
| **NW town** | **industrial chemist** · **fancy plate** | potions apex · defence |

**Potions — new, owner 2026-08-06.** Potions are ordinary items, not magic, so one player can hand another a potion. A basic
**village alchemist / healer** garb and an advanced **industrial chemist** found in town. Mechanic note for
later: healing someone is having the potion **equipped in the off hand**, not right-clicking (which drinks
it) — ties to the backlogged sword-and-shield work. Trinkets and shields are **not for now**.

**Clothing vs armour — new line.** Players can also make clothes; a dyer dyes them, and they
give bonuses to potion-making, harvesting and so on (owner). Light **clothing** with utility bonuses and low defence
is a legitimate trade against the armour line, and dyeing gives colour variety without new designs. ⚠ Open:
is dye a **recolour system** applied to any cloth outfit, or are dyed clothes their own sets?

**Bug wrangler / rancher — the third catching set.** A cowboy theme, with bonuses for catching ants,
beetles and other bugs worth wrangling (owner). ⚠ Name collision: I had proposed *bug rancher* for
farming's third tier. Clean split — **wrangler** = catching wild bugs (cowboy), **rancher** = your own
bug farm. Or drop farming to two and let the cowboy own the name.

## 13. What I would CUT, and why

Applying the saturation test to my own earlier proposals:

| cut | because |
|---|---|
| deep-sea explorer | fishing already has three tiers; this is a fourth aquatic answer to the same question, and there is no ocean zone |
| ~~glowworm as two outfits~~ | **REVERSED 2026-08-07.** Explore genuinely different *designs*, not one re-rolled. The owner rejected the existing sheet as weird and ugly — it is armour, not a half-human, half-glowworm creature — so the brief must say **ARMOUR MADE FROM glowworm materials, never a glowworm-creature**, with one option built from **glowsticks**. If other approaches look better, the set may simply use glowworm ingredients, or both may be made (owner). |
| hermit / bog alchemist | the village alchemist now owns potions |
| prospector's oilskin | that is mining t1 |
| ~~festival / sunday best~~ | **KEEP — I was wrong.** Decorative outfits are a legitimate class (see §7); the owner approved festival wear |
| storm / weather gear | **cut, confirmed** |
| pill-bug plate | a fun silhouette with no answer that "tank" does not already give |
| queen's regalia | it **is** the queens' legendary; one thing, one name |
| beetle-shell · moth-wool | old art, never confirmed. Beetle-shell overlaps chitin (capped at the two ants); moth-wool overlaps butterfly collector's zone. **Owner call** |
| merchant / trader | folds into the town cluster unless shop prices become a real lever |

**Scale after the cut: ~40 sets.** That is what the owner's own constraints produce — six ladder rungs,
three tiers across six categories, one-plus per zone across twenty zones — and it is the number to sanity
check before committing, at three paid calls each.

## 14. Open

- **Scale.** Six rungs + ~5 metal/legendary + 3×(stealth, mining, fishing, beekeeping, farming) + the
  catching sets + combat chitin + ≥1 per zone across 20 zones lands somewhere near **45–60 outfits**.
  At three paid calls each (candidates → sheet → gauntlet) that is a **long-running programme**, not a
  batch. Worth pacing deliberately.
- **The third legendary** is an empty slot.
- **Amber's source** — trees rather than bugs, if it goes ahead.
- **Wax** — only if deep water becomes traversable.
