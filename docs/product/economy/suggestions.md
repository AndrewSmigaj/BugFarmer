# Economy & Crafting — Suggestions

Recommendations for turning the Stage-1 crafting spine + flat item list ([`findings.md`](findings.md)) into
the **fleshed-out, "much better than bare minimum"** system the request wants — including the **town NPCs
(merchant, blacksmith, carpenter)** with intro dialogue + random tips. Companion design:
[`stats_and_bonuses.md`](stats_and_bonuses.md), [`item_catalog.md`](item_catalog.md). Stays inside the GDD
guardrails (item-driven power, no grind, small accessories, capped idle bonuses).

---

## 0. The one-sentence vision

Make the **gather → sell → buy recipes/materials → craft better gear → reach deeper content** loop real:
mining/farming/catching feed an **economy** (currency + merchant), the economy feeds **crafting** (auto +
bought + found recipes), and crafting outputs **gear with bonuses** that make each activity better — with
**NPCs** as the social glue and tip-givers.

## 1. Crafting system review (what's good / what to add)

**Keep (it's well-built):**
- The single-system station model (one panel, `process_ticks` is the only speed knob) — simple + extensible.
- Inputs-consumed-up-front + output-grid + Get-all — Terraria-familiar, collision-safe.
- "A placeable is a station iff it has recipes" — zero schema overhead to add stations.
- Crafting is display-only (never hashed) — adding recipes/stations can't break determinism.

**Add (in rough priority):**
1. **The bonus/stat layer** ([`stats_and_bonuses.md`](stats_and_bonuses.md)) — the single biggest gap.
   Without it, all armor/accessories/outfits are cosmetic. This is the foundation for "extensive weapons &
   accessories." Build the `bonuses{}` schema + `PlayerStats` recompute, then wire `defense`+`damage` first.
2. **The new stations + their material ladders** ([`item_catalog.md`](item_catalog.md) §1): sawmill (planks),
   loom (cloth), forge (alloys/steel), cauldron (potions), stove/cooking_pot (meals), jeweler (accessories),
   honey_extractor. Each is just data (entity + recipes) once the art exists — see `art_needed.md`.
3. **Recipe acquisition** (the `unlock` seam): per-character "known recipes" set + the three-way content
   rule (auto / buy@npc / find) from [`item_catalog.md`](item_catalog.md) §8. This is what makes shopping
   and exploring feed crafting.
4. **Themed station UI** (deferred polish): a smelter shows a fuel tank + heat bar, etc. Nice, not blocking.
5. **Drag-drop** in the panel (the server `move` op already exists; client wiring deferred).
6. **Item tooltips that surface bonuses** — a bonus is worthless if invisible. The hover tooltip must show
   the `bonuses{}` block ("+2 Defense, +15% Honey", and red for trade-off costs). There's already a tooltip
   task in flight (BACKLOG/task "Part 5: tooltips") — fold the bonus display into it; it's the discovery
   layer for the whole gear system.

## 2. Economy: currency + merchant (the missing half)

Selling is data-only today (`sell_price` priced, no RPC, no coins). To close the loop:

- **Currency:** add `coins` to `CharacterSave` (one coin type — simplest, matches the existing prices).
  Show it on the HUD. Persisted per character.
- **Buy/Sell RPCs:** `sell(item, qty)` → coins += `sell_price*qty`; `buy(item, qty)` → coins -= `buy_price`,
  if affordable. Validate server-side. A merchant panel (reuse the crafting/container panel plumbing — it's
  the same grid + opcode pattern).
- **Money sinks** (so coins have meaning): bought recipes (the outfits/top gear), bought materials you
  can't farm yet, convenience stations, later land deeds / plot upgrades (GDD city-hall).
- **Sell channels:** the **Merchant NPC** (general buy/sell), plus specialists who pay more for their
  domain (Ecologist buys bugs high, Blacksmith buys ore/bars). `sell_pct` accessories plug in here.

## 3. NPC system (merchant, blacksmith, carpenter) + random tips

The request's part 1. The interaction framework already exists; this is a clean new `interaction_type`.

### Data
- Add NPC entities to `nakama/data/entities/occupants.json` (they render like any occupant):
  ```jsonc
  "npc_merchant": {
    "name": "Marjoram the Trader", "sprite": "merchant_down",
    "world": { "footprint": [1,1], "blocks_players": true,
               "interactable": true, "interaction_type": "npc" },
    "npc": {
      "role": "merchant",                       // merchant | blacksmith | carpenter | ecologist | beekeeper
      "intro": "Welcome to Marjoram's! Buy low, sell... well, sell to me.",
      "shop": "general",                        // later: which buy/sell + recipe catalog
      "tips": [
        "Heard the caves get richer the deeper you dig — bring a lamp.",
        "Bugs sell better to the Ecologist than to me, between you and me.",
        "A full armor set is worth more than the pieces apart — set bonuses, they call it."
      ]
    }
  }
  ```
- Sprites exist for preview (`merchant_down`, `miner_down`=blacksmith, `farmer_down`=carpenter,
  `scholar_down`=ecologist). Promote them to real occupant sprites under `Resources/Objects/`.
- **Persist them into the village**: the village builders currently drop NPCs via `place_player()`
  (preview-only). Switch the town NPCs to `place_occupant("npc_merchant", x, y)` so they exist in the
  saved zone and are interactable. (`tools/zonegen/scenes/scene_market/_smith/_carpenter.py`.)

### Behavior (intro then random tips)
- **First talk** with an NPC (per character) → show the `intro` line. Track "met" NPCs in `CharacterSave`
  (a small set of NPC ids), so the intro only plays once.
- **Every later talk** → show a **random `tip`** from that NPC's list. Tips are flavor + genuinely useful
  hints (mechanics, where to find things, what they sell) — cheap content that makes the town feel alive
  and teaches the game without a tutorial. (Use the deterministic per-match RNG or a simple client pick —
  dialogue is display-only, not hashed.)
- Merchants/blacksmith/carpenter additionally open their **shop/craft** on a second prompt (or a button in
  the dialogue) once the economy/recipe-buy layer lands. For the first cut, dialogue + tips only.

### Client
- New `NPCDialogueController` in the right-click router chain (`PlayerInputRouter.cs`, alongside
  Sleep/Station/Craft) — on right-click an `interaction_type:"npc"` occupant, request its dialogue.
- A simple **dialogue panel** (TMP text box + portrait + "next/close") — the one genuinely net-new UI.
- Server: wire the unused `OpCodeAction` (or a small `NPCTalk` opcode) → returns intro-or-random-tip (+
  later the shop payload). Server owns "have you met them" so it's consistent across sessions.

### Scope for "for now"
Merchant, Blacksmith, Carpenter — each: a placed interactable NPC, an intro line, ~4–6 tips, a dialogue
box. Shops/recipe-buying come with the economy track (§2). The Ecologist/Beekeeper reuse the exact same
system later (GDD §13 roles).

## 4. Mining — needs depth (the request flagged this; backlogged)

Mining today is thin: tool_tier gates ore, you break a block, you get ore. To make mining a *loop* worth
gearing for (and to give the miner kit / `ore_fortune` / `gem_luck` / `light_radius` bonuses meaning),
the suggestions (now in BACKLOG):
- **Depth & risk:** deeper layers = better ore + hazards (dark, gas pockets, fall drops, cave-ins) →
  light/`hazard_resist`/`fall_resist` matter.
- **Yield variety:** `ore_fortune` (double drops), `gem_luck` (gems/geodes in stone), rare nodes.
- **Tools beyond the pick:** drill (fast/AoE), dynamite ✅ (already a concept), ore cart/rail ✅ (haul),
  prospector tools (vein sense).
- **A reason to go deep:** exclusive deep materials (mithril/adamant) gate the endgame gear in
  [`item_catalog.md`](item_catalog.md).
- **Light as a real stat:** a `light_radius` system (miner kit, lanterns, torches placed) — currently the
  flashlight is cosmetic.

## 5. Recommended build order (phased, each shippable)

1. **Bonus foundation** — `bonuses{}` schema + `PlayerStats` recompute + wire `defense` & `damage_pct`
   into combat. *Now armor/accessories DO something.* (Smallest change, biggest unlock.)
2. **Currency + merchant** — coins on `CharacterSave`, buy/sell RPCs, merchant panel. *Selling matters.*
3. **NPCs + dialogue** — merchant/blacksmith/carpenter as interactable occupants, intro + random tips,
   dialogue panel. *Town comes alive; vendors have a home.*
4. **Material stations** — sawmill/loom/forge/cauldron/stove/jeweler + their auto recipes + the metal/cloth
   ladders. *The crafting tree fills in.*
5. **Recipe acquisition** — known-recipes set + buy@npc + find scrolls. *Crafting becomes a loop.*
6. **Gear content** — armor tiers, the utility outfits, accessories, trade-off items, consumables. *The
   "extensive weapons & accessories" payoff.*
7. **Mining depth** (parallel track, §4) — so the gear has somewhere to be used + the bonuses have teeth.

Each phase is independently valuable and low-risk (crafting/economy are display-side, never hashed).

## 6. Risks / things to get right

- **Don't out-pace the bug sim:** combat power creep could trivialize the ecology threats. Tune `defense`
  soft caps; let boss-bugs scale via the Director (GDD §14.2).
- **Keep bonuses small + capped** (§15.2) — resist the loot-treadmill. The fun is *picking a build*, not
  maxing a number.
- **Currency inflation:** price sells modestly; put real sinks (recipes, top gear, deeds) so coins stay
  meaningful.
- **No mandatory recipes:** every progression-critical recipe stays `auto`; `buy`/`find` are for flavor +
  power, never required.
- **Art is the long pole:** the new stations/outfits/accessories need icons (`art_needed.md`) — the
  systems are cheap, the sprites are the work. Sequence content behind the gpt-image-1 pipeline.
