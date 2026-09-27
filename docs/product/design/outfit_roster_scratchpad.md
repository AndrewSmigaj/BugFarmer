# Outfit roster — the list, for review

**Scratchpad. Mark it up.** Design reasoning: [`brainstorm_armor.md`](brainstorm_armor.md).
**One paid call = one sheet of THREE design options**, so the count is per set.

Status: ✅ done · 🎨 old art, needs a fresh roll · ⬜ nothing yet · ⚠ needs your call

> ⚠ **PREREQUISITE — the species list.** Several sets below depend on which bugs have how many tiers.
> `species.json` has **15 entries**; the design docs describe many more. Owner direction: every bug needs simpler
> and more advanced versions — most bugs have three species across their tiers, though some have two and
> some only one. **Wasps and hornets: ~2 types each. Bees: 3, including killer bee.**
> Worth settling that list before the thorn and bee sets get briefed.

---

## 1. Base ladder — 6 to make

leather · wood · **bronze ✅** · copper · iron · steel · platinum
*(bronze, tin, stone, silver-as-a-set: cut)* — all 🎨 except bronze.

## 2. Metal specials — 2

| set | what it is |
|---|---|
| **gilded steel plate** | gold over steel → acid-proof (Deadly Ants) |
| **fancy plate** | silver, expensive, plain good defence. Recipe from the NW town |

## 3. Legendaries — 2 (+1 open ⚠)

**queens' set** — parts from BOTH queens, chest in an underground fortress · **spider-plate set** — Spider Vale

## 4. Combat / chitin — 4

| set | source | why it exists |
|---|---|---|
| **beetle-shell** 🎨 | `beetle_carrion` — **live** in village, Bee Meadow, Underground Passages | **The entry-level bug armour.** The first thing you make *from* bugs rather than buy: above ground, before the ant colonies. `dead_beetle → chitin` is **60 ticks, the fastest of the five** chitin recipes, so beetles are the game's primary chitin source. Elytra also reads nothing like ant chitin — iridescent, domed, colour-shifting vs matte segmented plates |
| **fireant** ✅ | Ant Colony | |
| **blackant** ✅ | Ant Colony | |
| **scorpion** ⬜ | Scorpion Rocks (sand/desert) | venom + heat |

> I had cut beetle-shell as "redundant". That was wrong. The owner's ruling that only two chitin sets are
> needed — fire ant and black ant — was about **ant variants** — don't make five ant sets — and I generalised
> it into "no other bug-plate armour", which would also have ruled out the scorpion and thorn sets he
> explicitly asked for.

## 5. Thorn line — 3  ·  species-specific

Attackers that hit the wearer get stung (owner). **Not one ladder** — wasps and hornets are different species; hornets
*hunt* wasps. Three separate sets, three zones, three ingredient sources. Each may need thorns from
**multiple species within its own family**.

| | set | source | names to try |
|---|---|---|---|
| 1st | **wasp thorn** | the ranger zone, east | Bramblejack · Sting-Coat · Waspmail |
| 2nd | **hornet thorn** | | Hornetplate · Spinemail · Brutebarb |
| 3rd | **killer-bee thorn** | the bee line's late payoff | Killer's Coat · Swarmplate · Goldspine |

## 6. Place & anti-species — 2

| set | what it is | names to try |
|---|---|---|
| **ranger** 🎨 | wasp/hornet protection. From the eastern outpost zone | *(keep "ranger")* |
| **forest plate** ⬜ | **samurai-ish. No bugs** — special trees and plants. **CAMO**: some creatures struggle to see you, plus tank defence, but **slower** | Forest Plate · Bark Harness · Greenwarden |

## 7. Silk / stealth — 3  ·  light, fast, quiet, WEAK

⚠ **Correction: silk is NOT venom-related.** Silk is stealth and speed — the robes are quiet *because they
weigh so little*. Venom comes from elsewhere: **weapons** cause poisoned states, and **widow's armour reduces
venom**.

**Two different stealth flavours, deliberately:** silk = light-and-quiet (fast, weak) · forest = camo
(hidden, tanky, slow).

| | set | source |
|---|---|---|
| 1 | cave-spider silk ⬜ | Underground Passages |
| 2 | hunting-spider silk ⬜ | Spider Vale West |
| 3 | **widow's armour** ⬜ | Spider Vale East — the venom-reduction one |

## 8. Mining — 3

Plus: the **underground combat armour** (§4/§3) also carries mining bonuses — ore chance, carry capacity,
station bonuses. *(Dredging: later.)*

**basic mining gear** ⬜ · **armoured mining gear** ⬜ · **deep mining gear** ⬜

## 9. Fishing — 3, maybe 4

⚠ **My mistake:** I had this as one dock set plus two underground-river sets, which covers only a small part of
the water world (owner correction). **There is no diving in this game.**

**basic fishing gear** 🎨 · **cave fishing gear** ⬜ · **armoured fishing gear** ⬜ · *(ultimate fishing gear?* ⚠*)*

## 10. Beekeeping — 3 or 4 ⚠

**cheap beesuit** 🎨 · **professional beesuit** ⬜ *(a store sells it)* · **padded beesuit** ⬜ ·
*(fancy armoured beesuit?* ⚠*)*
Names to try: Hivecloth · Apiarist's Suit · Smoke-and-Veil · Combwarden

## 11. Farming — 3

**farmhand's clothes** 🎨 · **padded/armoured farming outfit** ⬜ · **industrial farming gear** ⬜ ⚠ *(no idea
what it looks like yet)*
Names to try: Furrow Coat · Tiller's Kit · Harvest Rig · Threshers

## 12. Bug catching — 3

**entomologist** 🎨 · **butterfly collector** ⬜ · **bug wrangler** ⬜ *(cowboy — same thing as "bug rancher",
one set only)*

## 13. Potions — 2

**village healer's garb** ⬜ · **industrial chemist** ⬜ — the owner likes potions being made from these two angles.

## 14. Light — 2 (+1 experiment)

⚠ **Brief it as ARMOUR, like everything else** — not an outfit that turns the wearer into a mutant glowworm
humanoid. That is what made the old sheet ugly.

| set | note |
|---|---|
| **glowworm armour** 🎨 redo | armour MADE FROM glowworm material |
| **glowstick armour** ⬜ | built from glowsticks |
| *(one option: a "glowstick man" version — it's a real thing, worth seeing once)* | |

## 15. Decorative / social — 6+  ·  ⏸ ON HOLD

Owner decision (2026-08-07): clothing is on hold. The list stands; nothing gets briefed yet.

**Dye is a RECOLOUR, not new sprites.** Owner direction: dye applies to cloth items, and he wants to try recolouring existing sprites
with a script (e.g. Python) rather than generating new sprites, which would take far too long. So dye
is a palette-swap pass over an existing cloth outfit — free, no API — and only cloth sets are dyeable.
Parked until the clothing line starts.

Clothes that exist to look good; bonus may be farm output or happiness. Not filler — this is the furniture role.

| set | what it is |
|---|---|
| **festival wear** | village fair / harvest festival |
| **pinstripe suit** | town formal |
| **beach outfit** | Bee Meadow coast |
| **honey-gold formal** | the beekeeper's Sunday best — bee-inspired, warm gold and cream |
| **moth-wool knits** 🎨 | ⚠ **repurpose**: it was never a convincing armour, but it is a *lovely* cosy winter set. Solves the open question |
| **traveller's coat** | the road between zones; a merchant look without a merchant stat |
| **sleepwear** | you have a house and idle content |

---

## Cut — confirmed

deep-sea explorer · diving *(no diving in the game)* · storm gear · pill-bug · hermit/bog alchemist ·
prospector's oilskin · queen's regalia *(it IS the queens' set)* · merchant · locust set *(D10)*

## Your calls

1. **Fishing 4th** — is there a top-tier fishing outfit?
2. **Beekeeping 4th** — is there a top-tier armoured beesuit?
3. **The third legendary** — still an empty slot.
4. **Names** — pick from the candidates above, or say the flavour and I will try more.

## Scale

**~43 sets.** 3 done, ~11 with old art to re-roll. At three paid calls each (candidates → sheet →
gauntlet) that is roughly **115 calls** — paced in batches with your review between each, never one spend.
