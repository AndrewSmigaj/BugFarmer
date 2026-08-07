# Armour & outfit design — brainstorm

Working document for the outfit roster. **Owner rulings are quoted; everything else is a proposal.**
Numbers are deliberately absent — this is about what each set IS FOR, not balance.

Related: [`../economy/DECISIONS.md`](../economy/DECISIONS.md) D10/D11 · [`../economy/catalogs/armor.md`](../economy/catalogs/armor.md)
· [`../economy/stats_and_bonuses.md`](../economy/stats_and_bonuses.md) (the 36-stat vocab).

---

## 1. The frame

> *"combat is not a tiny little part of the game its important with lots of levers the armors can move…
> i just want us not get into the 'defense is one aspect so we should have one small set of defense
> related armors' — defense is critical."* — owner, 2026-08-06

**Defence is the spine, not a side category.** The base ladder is the backbone of progression; every
specialty set still carries real defence plus its perk. A set is never perk-only.

**Above steel, a set should be a KEY to a hazard, not a bigger number.** The zones already pose distinct
problems — venom (Scorpion Rocks, Spider Vale), **acid** (Deadly Ants is the "fire/acid endgame", and
`formic_acid` is a live item), water (swamps, underground river), dark (caves), heat. A set that answers a
hazard makes finding it feel like unlocking a place.

**Delivery is the point.** Owner: *"in most areas there will be at least one recipe hidden somewhere in a
chest, vendor, etc. which requires materials including new materials from that zone… minimum of one new
outfit per zone."* More recipes concentrate in the **two towns** (Starting Village, NW town) and the
**Mining Camp**.

> **This does not contradict D10** ("sets are CONCEPTUAL, not one-per-zone"). D10 governs what a set IS;
> this governs where you FIND it. A zone hands you a material and a hidden recipe; the set it unlocks can
> still belong to a concept line — "mining tier 2" can perfectly well be the thing hidden in the Passages.

---

## 2. The levers

Owner's list, plus three the mining line needs. Each outfit moves **one primary + one or two minor** —
owner: *"one might have higher boat speed but also a fishing speed or whatever bonus."*

| lever | notes |
|---|---|
| **Defence / strength** | the spine. Every set has some |
| **Stealth / being ignored** | *"some specific to some species like a beesuit only helps with variety of bees"* — so stealth is not one number; species-scoped immunity already exists (`sting_immune`) |
| **Speed / agility** | |
| **Harvest yield** | *"you get a percentage of the available harvest, the rest is deleted"* — finishing farming is backlogged |
| **Fishing + boat speed** | weak alone, so these sets carry two bonuses |
| **Bug catching** | *"they avoid less naturally, higher rates of harvesting nests"* |
| *(added)* **Light** | caves are dark; the Miner's kit already designs a built-in `light_radius` so no torch is needed |
| *(added)* **Carry weight** | mining's real constraint |
| *(added)* **Hazard / element resist** | acid, venom, heat — what makes the gilded and specialist sets keys |

---

## 3. The base ladder — leather → platinum

Owner: bronze **cut** (*"too similar to copper"*), tin **cut**, stone/rock **cut**, silver-as-a-set **cut**.

| rung | source |
|---|---|
| leather | processing bugs |
| **wood** | *"a step up from leather you get by processing bugs"* — bug processing station |
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
| **Fancy plate** ✅ | silver in an expensive, ordinary plate. Recipe from the **NW town** | Owner: *"just standard nothing magical expensive plate — decent defence."* Silver earns its place by cost, not by magic |

**Cut, and why** — kept as a record so they are not re-proposed:
*blackened silver* (owner: doesn't make sense) · *silvered chitin* · *honeycomb plate* (owner: *"too fragile
for armor armor"*) · *royal-jelly lining* (owner: *"does not heal by putting it in your armor"*) ·
*crystal* (owner: *"crystals also dont really do much"*).

**Wax / waterproofing — parked.** Owner: *"we already have things that let you move around the marsh and
shallow water faster."* Only worth a stat if **deep** water becomes traversable; otherwise beeswax stays a
crafting ingredient, not a bonus.

**Amber — open.** Owner: *"maybe amber but we dont have bugs that generate that yet."* Worth noting amber is
fossilised **tree resin**, not bug-made — so the Millipede Forest could source it without any new bug. A
bug *trapped* in amber is then a collectible, not the source.

## 5. The legendaries — secrets

> *"i do want secrets."*

Two or three of the most powerful sets in the game, each behind a find rather than a shop:

1. **Queens' set** — needs parts from **both** colony queens (the col-0 intro colony and the col-3 deadly
   one) plus rare metals. *"locked in a chest in a little underground fortress"* → **backlogged**.
   Requiring both queens is good design: it forces you across the whole underground, east and west.
2. **Spider-plate set** — built on spider plate. Gated behind Spider Vale, so it is endgame by geography.
3. *(slot open for a third)*

## 6. Categories — three tiers minimum each

Owner: *"maybe 3 tiers minimum for each category."* The tiers have natural homes in the world already:

| category | t1 | t2 | t3 |
|---|---|---|---|
| **Stealth** | cave-spider silk — Underground Passages | orb-weaver — Spider Vale West | widow — Spider Vale East |
| **Mining** | Underground Passages (3,1) | deep — Cavern / row 4 | Deadly Ants col 3 |
| **Fishing** | shore / Bee Meadow coast | swamp + river | underground lake, sunken ruins (4,2) |
| **Beekeeping** | plain cloth | the NPC's fancy suit | armoured, for the aggressive bees |
| **Farming** | plain farmer | fancy farmer | *see below* |
| **Bug catching** | **one** entomologist, plus several others that help differently | | |

**Farming's third tier** — owner: *"those are not obvious."* Proposal: since the lever is *% of available
harvest*, tier the sets by **what they change** rather than by material —
plain (yield %) → fancy (yield % + range: `harvest_aoe`/`water_aoe` are already built stats) → a
**bug-component** set. The obvious one is a **pollinator's kit** from bee materials (flowering crops), or a
**composter's** set from carrion beetles, which already carry `produces_compost`.

**Combat sets** carry real defence plus a small perk — the ant chitin pair (fireant, blackant — owner:
*"we have 2 ant species in the game in different zones"*), wasp, hornet.

---

## 7. Two rules that decide what a bonus may be

### An outfit suits an EXPEDITION, not an ACTION

> *"outfits should be something we dont want to micromanage and constantly swap out they should not be
> completely single purpose so still have defense just other bonuses."* — owner

Every outfit is **defence + two or three bonuses**, chosen so you pick one for a **trip**. The mining kit
carries you through digging, fighting what lives down there, and hauling back — you do not change clothes
at each activity. This is the test that kills single-purpose ideas: a *composter's* or *pollinator's* set
fails it, which is why the owner is right that **tools are the better home for those**.

### An outfit changes what YOU DO — a decoration changes what the PLACE IS

The owner raised two doubts that are the same doubt:

- *"in the shared open world there is no way of having something go faster for you than other people"*
- *"why should you wearing a better farming outfit increase things on your home plot"*

Both fail for one reason. "Faster growth in this area" is **world state**; "your home honey rate" is
**place state**; neither can be personal, and the home plot is **idle** content while an outfit is **worn**.
An outfit that boosts idle output either has to be worn while you idle — which is not idle, and wastes the
slot — or apply while unworn, which is incoherent.

**So: the home farm stays decoration-driven, and outfit bonuses attach to VERBS.** Watering AoE when you
water, extra-crop chance when you harvest, seed return when you plant, carry when you haul. Personal,
active, and safe in a shared world by construction.

## 8. Farming — the naming problem

Owner: *"not sure what the 3 farmer related ones will be, those are not obvious."*

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

> *"recall we have stealth, mining, combat, etc all sorts of different things each which will have their
> own best version and a few which are mix and matches of them… there will be a best stealth and a best
> mining and a best tank and a best agility and such."* — owner, 2026-08-06
>
> *"the spider zone stealth is NOT the top outfit."*

**Not one ladder, and not two — a set of roles, each with its own top.** Tank · attack · agility · stealth ·
mining · fishing · farming · bug-catching · beekeeping. Nothing is "the best armour in the game"; a set is
the best *at something*. This is why *"which key do I need"* beats *"do I have the best one yet"*, and it is
the shape that pays off the curiosity lens — no zone hands you the endgame, each hands you the top of one
thing.

**Two axes, and an outfit sits on both.**

| axis | what it means |
|---|---|
| **Role** | tank, attack, agility, stealth, mining, fishing, farming, catching — each has an apex |
| **Situation** | *"bonus defense and/or attack against wasps compared to other armors in the zone"* — best HERE, or against THIS, rather than best outright |

The situational axis is the expedition rule again: you bring gear for **where you are going**, not for a
number. And it lets a mid-tier set be genuinely correct in its own zone, which keeps old sets alive.

**Hybrids are first-class.** *"a few which are mix and matches of them."* The named example:

> **Underground combat-mining set** — ant parts, mining buffs *and* real combat. Second in power to the
> spider-zone combat gear **as combat gear**, while being far better than it at mining. That is exactly
> how a hybrid should read: top of nothing, strong at two things.

⚠ **Correction:** `fireant` and `blackant` are **combat/chitin sets, NOT mining outfits.** The ant-parts
mining hybrid above is a separate, deeper set.

*(Difficulty context, owner: the upper surface and the lower underground are roughly even; swamp ≈
underground river ≈ lake; Spider Vale is the hardest surface zone and the fireant domain the hardest
underground one. So the hardest zones are peers — but "hardest zone" produces "best of a role", not
"best overall".)*

## 10. Settled 2026-08-06 — ranger, forest, thorns, catching

**Ranger — YES, and it is the wasp/hornet answer.** *"the ranger thing is good for wasps… ranger armor
yeah wasp and hornet protection."* You get it in a zone with **a little outpost, infested with wasps and
hornets, seeded by an active bubble of flies** — that zone is **not designed yet**.

**Forest — a separate set, keep the plain name.** *"just call it that, gives bonus in forest zones and
maybe things involving forests."* So ranger and forest both exist; ranger is anti-wasp, forest is
place-and-material.

**Thorn armour — 3 tiers, a combat buff.** *"basically things that hit you get stung."* The tiers follow
the species ladder that already exists (`wasp_common` → `wasp_soldier` → `hornet_giant`), so **wasp thorn**
and **hornet thorn** are two of the three. Owner: *"not sure we need candidates"* — the look follows from
the bug, so the proposal is **explore tier 1 only, then tiers 2–3 reference that design** with the material
and spine-intensity stepped up. Same pattern as the gauntlets referencing bronze: one design, then variants.

**Bug-catching — 3 outfits, one lever family, conceptually distinct.** *"we dont want literally 3
entomologist outfits but 3 outfits that do similar things… related to bugs ignoring you and the harvest
success rate."* So: **entomologist** (the scientist), **butterfly collector** (butterfly-scoped), and a
third yet to be named — all moving *being ignored* and *harvest success*, none of them a re-skin.

**Build the sprite ahead of the mechanic.** Ocean zones and hostile bees are backlogged and stay
backlogged. Owner: *"we do not step aside from building sprites to build every single little related
mechanic, focus now we are creating sprites."*

## 11. Open

- **Scale.** Six rungs + ~5 metal/legendary + 3×(stealth, mining, fishing, beekeeping, farming) + the
  catching sets + combat chitin + ≥1 per zone across 20 zones lands somewhere near **45–60 outfits**.
  At three paid calls each (candidates → sheet → gauntlet) that is a **long-running programme**, not a
  batch. Worth pacing deliberately.
- **The third legendary** is an empty slot.
- **Amber's source** — trees rather than bugs, if it goes ahead.
- **Wax** — only if deep water becomes traversable.
