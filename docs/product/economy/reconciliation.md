# Reconciliation — crafting / items / economy: DESIGNED vs BUILT (you adjudicate the drift)

**Why this doc exists.** The economy docs are fragmented and contradict each other, so neither of us can
trust them. This is a **non-destructive** reconciliation: for each topic it states what we **DESIGNED** (the
intent, linked — not altered), what is **BUILT** (verified against the real code/data, with file:line), and a
numbered list of **DIVERGENCES** for *you* to decide. **Nothing here rewrites a doc or changes code.** Since
you designed it and the AI wrote the code, a divergence may mean **the code is wrong** — that's your call, per
item. Verified 2026-06-26 against the actual source (no scans, no unverified agents).

**Legend:** ✅ built & verified · 🟡 data/seam only (no behavior) · 🔴 designed, not started.
**How to use:** skim the DIVERGENCES (D1…Dn). For each, tell me **fix-code** (build/repair to match design) or
**update-design** (intent changed — amend the design doc). I touch nothing until you say.

---

## 1. Item obtainability — FOUND / BUILT / BOUGHT
**DESIGNED** ([`architecture_items.md §0`](../architecture/architecture_items.md), [`crafting.md`](crafting.md),
[`merchants.md`](merchants.md), [`DECISIONS.md` D18](DECISIONS.md)): every item is **FOUND** (mine/forage/
harvest/fruit/kill-drop), **BUILT** (a recipe output), or **BOUGHT** (an NPC sells it). Bug kills drop only
`dead_<bug>`; a **Bug Extractor** turns those into materials (chitin/silk/venom/leather).

**BUILT** — `items.json` has **101 items**; routes that actually work in code:
- **Mine** ✅ — ore deposits are **occupants** (`occupants.json`, `category:"ore"`) with explicit
  `breakable.drops` → the ore item (`ore_copper_block` "Copper Deposit" → `copper_ore`). Break path:
  `breakOccupantAt` rolls `def.GetDrops()` (`handlers_world.go:547-548`) — **no self-drop fallback, so every
  block lists its own drop** (the "blocks drop blocks" rule: `stone_block`→`stone_block`, `placeables.json`).
- **Forage** ✅ — flora occupants list their item (`flower_red`→`flower`, `bush`→`fiber`(+`seed_tomato`),
  `mushroom_glow`→`mushroom_glow`; `occupants.json` `breakable.drops`).
- **Harvest** ✅ — `crops.json` `harvest_item` (7 crops).
- **Fruit** ✅ — `tree_apple/orange/plum/cherry` carry `fruit_type` (`occupants.json`); the live `fruit_tree`
  interaction yields the fruit.
- **Kill-drop** ✅ — `spawnCarcass` drops the species' carcass = `dead_<species>` (`handlers_combat.go:309-342`).
- **Craft** ✅ — 10 recipe outputs (see §2).
- **Buy** 🟡 — `buy_price` on ~41 items, but **no buy mechanic** (see §5).

**DIVERGENCES**
- **D1** — ✅ **RESOLVED (2026-06-26).** `architecture_items.md` §1–15 (the stale ~300-item tables: 9-tier
  ladders, per-bug `parts`, `coin_copper`, blueprint-item) were **retired to a pointer**; **§0 (the accurate
  as-built model) kept**. The reconciled real item set now lives in the [`catalogs/`](catalogs/) pages (5 new:
  furniture/containers/decoration/structures/plants), grounded in the entity JSON and held drift-free by
  `tools/data/catalog_coverage.py` (no-orphan gate). D18 is applied in `species.json`. Nothing was deleted from
  the *game* — only stale doc text (git preserves it).
- **D2** — **Bug Extractor (D18/D11)**: designed to turn `dead_<bug>` → materials (chitin/silk/venom/leather)
  + bug-food. **Not built** — no `bug_extractor` entity or recipes (only `honey_extractor` exists). Today
  `dead_<bug>` is just an edible carcass. → build the extractor + recipes, or keep deferred?
- **D3** — `DECISIONS.md` D19 itself contradicts: flowers "drop `wildflower_petals`" then "**Cut** village
  materials: `wildflower_petals`". → which is it?

## 2. Crafting — stations & recipes
**DESIGNED** ([`crafting.md`](crafting.md), [`DECISIONS.md` D1/D13/D17/D19](DECISIONS.md)): ~15 stations, each
≥4–6 recipes, a tier-value cost model, bug-derived chains, sprinklers, a mining crusher→sluice chain (D13);
village places workbench/furnace/anvil/cauldron/forge/sawmill/keg + Bug Extractor + compost (D19).

**BUILT** ✅ (`recipes.json`, `architecture_crafting.md` — verified accurate): **4 stations**
(workbench, stonecutter, furnace, anvil), **10 recipes**, all `unlock:"default"`. A placeable is a station
**iff** `RecipesByStation[id]` is non-empty (no flag). Flow: right-click → `OpCodeContainer 98` → inputs leave
bag up-front → `processCraftStations` tick → output grid → collect; **non-hashed / determinism-safe**.

**DIVERGENCES**
- **D4** — **11+ designed stations are unbuilt** (sawmill, loom, forge, cauldron, cooking_pot, keg,
  honey_extractor, jeweler, dye_vat, electronics, + bug_extractor + mining crusher/sluice). D19 claims several
  are "placed in `village_21`" — but **placed ≠ functional**: with no recipes they're inert décor. → which
  stations + recipes do we actually build now (D17 says Village + Mining Camp only)?
- **D5** — designed recipe families (copper/steel/silver/gold bars, full tool/armor tiers, meals, potions,
  artisan goods) are **absent**; only the 10 exist. → which are in-scope for the two active zones?

## 3. Recipe acquisition — default / bought / found
**DESIGNED** ([`crafting.md`](crafting.md), [`merchants.md §2`](merchants.md), [`DECISIONS.md` D20](DECISIONS.md)):
**basic recipes auto-unlock** at their station; **shops sell** some recipes (`unlock:"shop:<npc>"`); a few are
**found** (scroll). "You buy the recipe, then craft the item."

**BUILT** 🟡/🔴: the `unlock` field **exists** in the schema (`recipe.go`) but is **never checked** —
`craft_stations.go` has **no unlock/known logic** (only an "Unknown station action" error at :260). There is
**no `KnownRecipes`** on `CharacterSave` (it has `Coins` at `character_persist.go:31`, nothing for recipes).
So today: own/build the station ⇒ you can craft all its recipes. No bought/found recipes, no scroll item.

**DIVERGENCES**
- **D6** — bought + found recipe paths are **designed, unbuilt** (no `KnownRecipes`, no enforcement, no scroll,
  no shop). This is the planned feature. → confirm: build `KnownRecipes` + enforce `unlock` + `recipe_scroll`.

## 4. Inventory / equipment / storage
**DESIGNED** ([`architecture_inventory.md`](../architecture/architecture_inventory.md),
[`stats_and_bonuses.md`](stats_and_bonuses.md), GDD §11.5/§14–15, [`DECISIONS.md` D11/D19](DECISIONS.md)):
slot inventory + hotbar; **armor gives defense**, **accessories give capped bonuses**; storage ladder
sack→basket→backpack; start with a net.

**BUILT** (per [`findings.md §3–4`](findings.md) + `character_persist.go`): slot inventory + hotbar + 8
equipment slots ✅; **backpack `slot_bonus` (+10 slots) is the ONLY working bonus** ✅; **armor is cosmetic
only — `overlay`, no defense math** 🔴; **accessories carry no stat fields — equipping does nothing** 🟡;
no defense/damage/speed/luck/yield stats exist at all 🔴 (the whole "RPG layer").

**DIVERGENCES**
- **D7** — `architecture_inventory.md` is itself stale/mixed: its **"Shop System" + OpCodes 30–37** +
  `ShopPanel.cs`/`NPCManager.cs`/`shop.go` file lists describe a **plan that was never built** (verified: no
  such files, no buy/sell handler) and contradict the real opcodes (container = 98/99; armor = 96/97). Its
  `ItemSlots[10]` Data Model is also stale (inventory later expanded for the backpack). → the doc needs the
  unbuilt-plan parts clearly marked DESIGN (cleanup) — and **when we build the shop, do we use this doc's
  opcodes 30–37 or the newer container pattern 98/99?**
- **D8** — armor/accessory **bonuses** are designed but inert (no stat system). Out of scope for the economy
  pass, but flagged: build the stat layer, or keep armor cosmetic for now?
- **D9** — storage ladder sack→basket→backpack (D19): only **backpack** exists. → add sack/basket recipes/items?

## 5. Currency & buy/sell economy
**DESIGNED** ([`merchants.md`](merchants.md), [`DECISIONS.md` D6](DECISIONS.md), [`crafting.md §1`](crafting.md)):
one coin; buy/sell at NPCs; cost model (sell ≈ 0.5× craft cost, buy ≈ 1.6–2×, artisan ≈ 2–3×); coin
sources (sell crops/bugs/artisan) vs sinks (recipes, stations, deeds).

**BUILT** 🟡/🔴: `sell_price`/`buy_price` priced on items (data); `Coins int64` on `CharacterSave`
(`character_persist.go:31`) — but **never earned or spent**: `Coins` only appears in persist load/save and
status copies (`character_persist.go:71/88/124`, `match.go:622`), **never `+=`/`-=`**. **No buy/sell handler
exists** (grep across `nakama/modules/world/*.go`: none). So nothing can be bought or sold.

**DIVERGENCES**
- **D10** — currency is **plumbed (field + prices) but has zero behavior**. The planned feature. → build
  earn/spend + buy/sell RPCs.

## 6. NPCs / dialogue / shops
**DESIGNED** ([`merchants.md`](merchants.md), [`DECISIONS.md` D20](DECISIONS.md), `suggestions.md §3`): 5
village NPCs — **Merchant (General Store), Fisherman, Blacksmith, Carpenter, Mayor** — as occupants with
`interaction_type:"npc"` + `npc{role,intro,shop,tips[]}`; right-click → intro then random tips → shop;
randomized stock with rare "teases."

**BUILT** 🔴: **nothing.** `OpCodeAction` (2) is declared "talk to NPC / open chest" but **unused**
(`messages.go:8`). No NPC entity, no dialogue UI, no shop UI, no handler (grep: none). NPC sprites
(`merchant_down`…) exist **in scene previews only** ([`findings.md §6`](findings.md)) — not real entities.

**DIVERGENCES**
- **D11** — the entire NPC/dialogue/shop layer is **designed, unbuilt**. The planned feature. → build the
  village Merchant (Marjoram) end-to-end first (per the approved scope), framework ready for the other 4.

---

## Summary of the decisions you own
Most divergences are **"design is ahead of code"** (the feature backlog) — **D2, D6, D8, D9, D10, D11** are
"build it (now / later?)". A few are **"the docs lie to us"** and need cleanup once you rule —
**D1, D3, D7** (stale tables/plans/contradictions). **D4, D5** are scope calls (which stations/recipes for the
two active zones). I won't change any doc or code until you mark each **fix-code** or **update-design**.
