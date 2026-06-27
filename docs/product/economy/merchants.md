# Merchants & the buy-side

The three shops, the currency, and the **craft-vs-buy mix** (it's a mix, not either/or — `DECISIONS.md` D1).
Recipes/costs live in `crafting.md`; pacing in `progression.md`; the NPC sketch this builds on is
`suggestions.md §3`.

> **BUILT — commerce spine v1 (2026-06-27, DECISIONS D25):** currency is now live (earn/spend, persisted),
> and **two NPC vendors** work end-to-end in the village — the **General Store** (`general_store_merchant`:
> buy seeds/tools, sell crops/forage) and the **Bug Dealer** (`bug_dealer`: sell live bugs at
> `species.sell_price` + dead bugs; buy a couple back). Server: `handlers_shop.go` on `OpCodeAction(2)` +
> a load-time arbitrage invariant; client: `ShopController` (OnGUI). The full multi-shop roster + recipe-
> selling + rotating stock below is still design.

---

## 1. Currency (D6)
One coin type, matching the existing `sell_price`/`buy_price` on items. Lives as `coins` on `CharacterSave`
(designed, unbuilt). No barter.

## 2. The three shops — what each gives
Each shop sells **finished goods**, **recipes** (buying a recipe unlocks crafting it), and some **stations**.
Stock **grows with progress** — not everything is offered at once (Lens of Pacing/Reward).

### General Store — *"Marjoram's"* (opens in the Village, early)
- **Goods:** seeds, torches, watering can, containers/sacks, basic consumables (calm_spray, bait), a few
  buy-only décor pieces.
- **Recipes:** a couple of cheap starter recipes.
- **Buys:** general items at base price (crops, foraged goods, raw materials) — the early coin source.

### Blacksmith — *miner-themed* (unlocks mid, near Scorpion Rocks / cliff entry)
- **Goods:** ore & bars you can't mine yet (markup), accessories.
- **Recipes:** metal **tool / weapon / armor** recipes, **gated by tier** (drip as you progress), advanced
  tech recipes late.
- **Stations:** anvil & forge as a **buy** convenience; the **electronics bench** is **buy-only** here (too
  complex to craft).
- **Buys:** ore & bars **high** (a reason to over-mine).

### Carpenter — *builder-themed* (unlocks mid, town)
- **Goods:** wood, planks, building materials, buy-only flavor furniture.
- **Recipes:** **furniture & structure** recipes (the bulk of décor), some artisan-station recipes.
- **Stations:** sawmill & loom as a **buy** convenience.
- **Buys:** wood/planks/furniture.

## 3. Craft-vs-buy matrix (the balance — D1)
| Category | Craft | Buy | Both? | Balance rule |
|---|---|---|---|---|
| Bars / planks / cloth | ✅ at your stations | ✅ blacksmith/carpenter (markup) | **both** | buy = skip the gather, pay the premium |
| Tools / weapons / armor | ✅ anvil/forge | recipe @ blacksmith; finished gear early @ markup | **both** | crafting is cheaper; buying is the convenience/coin path |
| Stations | most ✅ craft | wood/metal stations + **electronics (buy-only)** | mostly both | one un-craftable station = a real sink |
| Furniture / décor | ~70% ✅ | ~20% buy-only flavor | mixed | ~10% **find** only (exploration) |
| Seeds | later (seed-maker) | ✅ general store (early) | eventually both | seeds are the early buy staple |
| Recipes | — | ✅ blacksmith/carpenter | n/a | you **buy the recipe**, then **craft** the item |
| Consumables / potions | ✅ cauldron/cooking | basics @ general store | **both** | — |
| Accessories | ✅ jeweler | ✅ blacksmith | **both** | — |
| Artisan goods | ✅ keg/preserves | — | craft-only | the player-run money engine, not bought |

**Principle:** buying is never strictly better — it costs coins and a premium (Lens of Economy), while
crafting costs materials + time + the station/recipe. Many things are **both** so the player chooses; a few
are deliberately one-sided (electronics buy-only; artisan goods craft-only) to anchor the economy.

## 4. Coin sources vs sinks (Lens of Economy — must balance)
- **Sources:** sell crops, caught bugs, surplus ore/bars, and especially **artisan goods** (raw→processed
  ~2–3×, the main engine).
- **Sinks:** bought recipes, bought stations (esp. electronics), bought materials you can't yet farm,
  convenience finished goods, and later **land deeds / plot upgrades**.
- Tuned so a diligent player is never *rich enough to skip crafting* nor *too poor to ever buy* — buying is a
  choice, not a necessity.

## 5. How it maps onto the (unbuilt) systems
- NPCs = occupants with `interaction_type:"npc"` + an `npc{role, intro, shop, tips[]}` block
  (`suggestions.md §3`). Right-click → intro on first meet, random tip after, shop panel.
- Shop stock & recipe gating use the recipe `unlock` seam: `buy@general` / `buy@blacksmith` / `buy@carpenter`.
- Needs: `coins` on `CharacterSave`, buy/sell RPC, a shop UI — all **build-phase** (see `production.md`).
