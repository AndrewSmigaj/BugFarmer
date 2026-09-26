# Economy Findings — what we have today (as-built review)

A grounded review of the **crafting, items, equipment, economy (selling/recipes), and NPC** systems as
they actually exist in the code right now (June 2026), so the brainstorm/design docs in this folder build
on reality, not guesses. Companion docs: [`stats_and_bonuses.md`](stats_and_bonuses.md),
[`item_catalog.md`](item_catalog.md), [`suggestions.md`](suggestions.md). Authoritative design intent lives
in the GDD (`../game_design.md` §11, §13, §14, §15) and `../crafting_design.md`.

**Legend:** ✅ built · 🟡 data/seam only (no behavior) · 🔴 designed, not started.

---

## 1. Crafting & stations

| Piece | Status | Where |
|---|---|---|
| Recipe data model (`inputs`, `output`, `station`, `process_ticks`, `catalyst`, `unlock`) | ✅ | `nakama/modules/entities/recipe.go`, `nakama/data/entities/recipes.json` |
| One-system station model (right-click → pick recipe → inputs leave bag → process bar → output grid → Get-all) | ✅ | `craft_stations.go`, `CraftingPanel.cs` |
| Stations live: **workbench, stonecutter, furnace, anvil** | ✅ | `recipes.json` (10 recipes total) |
| Ore→bar smelt (furnace: 2 iron_ore + 1 coal → iron_bar, 200 ticks) | ✅ | `recipes.json` |
| Stations designed not built: sawmill, loom, forge, cauldron, cooking_pot/stove, chopping_block, honey_extractor, jeweler, dye/tailoring, electronics | 🔴 | `../crafting_design.md` §"Stations & recipes" |
| **A placeable is a station iff it has recipes** (no dedicated flag) | ✅ | `RecipesByStation[entityID]` |
| Inputs consumed up-front; output piles into an 8-slot output grid; queue stalls if grid full | ✅ | `craft_stations.go` |
| Crafting is **display-only / never hashed** (not part of the deterministic bug sim) | ✅ | `../architecture_crafting.md` |

**Recipes that exist (10):** torch, chair_wood, table_wood, fence_wood, sword_wood (workbench); brick,
wall_stone (stonecutter); iron_bar (furnace); pickaxe_iron, axe_iron (anvil).

## 2. Recipe acquisition (auto-unlock vs learned)

- Every recipe has an `unlock` string. Today **all 10 are `"default"`** → always available once you're at
  the station. **The only real gate is owning/building the station.** ✅
- The seam for learned/bought/found recipes is **designed, not wired**: `unlock: "recipe:<id>"`
  (learn from a found scroll / prereq) and `unlock: "shop:<npc>"` (buy from a vendor) exist as a string
  convention only. 🟡 No per-character "known recipes" set, no shop, no scroll item.
- Player persistence exists (`CharacterSave`) so the known-recipes set has a home when we build it. ✅

## 3. Items & equipment

- **101 items** in `items.json`. Categories: `resource, tool, armor, backpack, seed, consumable`.
  Item fields: `name, category, tags[], stackable, max_stack, sell_price, buy_price, tool_type,
  tool_tier, reach, mining_speed, durability, cooldown_ticks, swing_time, arc_degrees, catch_cap,
  moves{}, armor_slot, overlay, slot_bonus, food_value, effect, places_crop, icon_from`. ✅
  — **There is no stat/bonus field on items** (no defense, damage mult, speed, luck, etc.). 🔴
- **8 equipment slots** (`Equipment[8]`): head, body, arms, legs, feet, **acc1, acc2**, backpack. ✅
  Accessory slots already exist (5 & 6).
- **Armor is purely cosmetic today** — `overlay` renders a paper-doll layer; **no defense math**. The
  Go struct comment literally says defense is "a planned follow-up." 🔴
- **Accessories exist as items** (`bee_charm`, `lucky_clover`, `armor_slot:"accessory"`) but carry **no
  stat fields** → equipping them does nothing yet. 🟡
- **The only working bonus in the whole game** is the **backpack `slot_bonus`** (+10 inventory slots when
  the backpack is equipped). ✅
- Tools carry intrinsic numbers (`tool_tier` 1–4 gates ore, `mining_speed`, `reach`, net `catch_cap`/`arc`,
  weapon `moves[].damage`) — but these are **per-item constants, not modifiable by any bonus path**. ✅/🔴

**Tool/weapon/armor tiers that exist:** pickaxe/axe/shovel wood→stone→copper→iron; hoe wood/stone;
scythe_wood; small/large net; sword_wood, spear_wood; watering_can basic/large; armor sets leather +
iron (head/body/arms/legs/feet) + straw_hat, copper_helmet; accessories bee_charm, lucky_clover; backpack.

## 4. Player stats (what a bonus could even modify today)

`PlayerState` has almost nothing to buff: `HP` (1–10), `MaxHP` (**hardcoded 10**), `ItemSlotsUnlocked`
(30 + backpack), `EquippedTool`, cooldown gates. There is **no** defense, damage multiplier, move speed,
light radius, luck, yield, growth-rate, or catch-rate stat anywhere. So a bonus system has to **introduce
the stats first**, then the items that move them.

| System | What's there to bonus | Stat exists? |
|---|---|---|
| Combat | fixed 10 HP, weapon move damage, centipede bite = 2 HP flat | 🔴 no defense / dmg mult / regen |
| Mining | tool_tier gates ore, mining_speed/reach on the pickaxe | 🔴 not modifiable; mining loop is thin |
| Farming | crop growth/water (server), watering-can capacity | 🔴 no yield/growth/water bonus |
| Bug farming | net catch_cap/arc/reach, swarm catch sweep | 🔴 no catch-rate / lure bonus |
| Movement/light | fixed speed; flashlight is cosmetic (no light stat) | 🔴 none |
| Inventory | backpack slot_bonus | ✅ the one real bonus |

## 5. Economy — selling, buying, currency

- `sell_price` / `buy_price` are **priced on items** (wood 2, iron_ore 12, iron_bar 25, diamond 100, …)
  🟡 but there are **no buy/sell RPCs, no merchant UI, and no currency** — `CharacterSave` has no coins
  field. So nothing can actually be bought or sold yet. 🔴
- No money sink, no recipe shop, no land-deed/upgrade purchases.

## 6. NPCs, dialogue, interaction

- **No NPC system, no dialogue UI.** NPC sprites (`merchant_down`, `miner_down`, `farmer_down`,
  `scholar_down`) are placed **in scene previews only** (`tools/zonegen/scenes/scene_market/_smith/
  _carpenter/_ecologist.py`) via `place_player()` — they are **not persisted** to zone data and **cannot
  be interacted with**. 🔴
- The **interaction framework is solid** though: occupants carry `interaction_type` and the client
  right-click router dispatches per type. Live types: `station/craft, storage, sleep, fruit_tree`.
  Designed-inert: `sign, beehive, well, door`. ✅ A new `interaction_type:"npc"` slots straight in.
- `OpCodeAction` (opcode 2) is declared "talk to NPC / open chest" but **unused**. 🟡
- GDD §13 NPC roles: **Ecologist** (only ecology quests), **Builder, Miner, Beekeeper, Traders**. Quests
  are optional / world-state-driven / never forced.

## 7. Design intent already on record (the guardrails)

From the GDD — the brainstorm must stay inside these:
- **"Power comes from items and preparation"** (§14). Real-time combat, **HP only, no stamina, no skill
  trees, no stat grinding** (§6 intro, §14).
- **Accessories = "small, meaningful bonuses, 2–4 slots, no loot treadmill, encourage experimentation"**
  (§15.2). Armor layers = armor + utility-overlay + accessories, **no gear friction / forced swapping**.
- **Furniture/decoration idle boosts** with **diminishing returns per `id` + an overall cap** (§11.5) —
  a real mechanic, not just décor. The per-item bonus VALUE is a field to add *with* that system.
- **Progression is item/knowledge/spatial**, not XP. Optional industrial power route later (§11.6).
- Auto-catching is allowed only as the slow, capacity-capped **autonet** (§11.4) — no fast automation.

## 8. The gap, in one line

We have a **clean Stage-1 crafting spine** (recipes + stations + determinism boundary) and a **rich item
list**, but the **whole "RPG layer" is missing**: no defense/stat system, accessories/armor do nothing,
no currency/merchant, no recipe acquisition, and no NPCs. That layer is what the rest of this folder
designs — see [`suggestions.md`](suggestions.md).
