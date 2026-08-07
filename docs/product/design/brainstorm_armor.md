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

## 7. Open

- **Scale.** Six rungs + ~5 metal/legendary + 3×(stealth, mining, fishing, beekeeping, farming) + the
  catching sets + combat chitin + ≥1 per zone across 20 zones lands somewhere near **45–60 outfits**.
  At three paid calls each (candidates → sheet → gauntlet) that is a **long-running programme**, not a
  batch. Worth pacing deliberately.
- **The third legendary** is an empty slot.
- **Amber's source** — trees rather than bugs, if it goes ahead.
- **Wax** — only if deep water becomes traversable.
