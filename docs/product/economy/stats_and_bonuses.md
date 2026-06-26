# Stats & Bonuses — the brainstorm menu

Everything we could let an item, outfit, accessory, consumable, or decoration **change about a player**,
across every system (combat, mining, farming, bug farming, movement, economy). This is a *menu to prune
from*, not a commitment. Grounded in the GDD guardrails (`../game_design.md`):

> **Power comes from items and preparation. Accessories = small, meaningful bonuses, 2–4 slots, no loot
> treadmill, encourage experimentation. No skill trees, no stat grinding.** (§14, §15.2)

So the design target is **build expression** (pick an outfit + 2 accessories that suit what you're doing
right now) and **trade-offs** (a bonus often costs something), **not** a number-go-up treadmill.

Companion: [`item_catalog.md`](item_catalog.md) assigns these bonuses to concrete items + their cost/source.

---

## 1. The data model (one small schema add)

Today items have **no stat fields** (see [`findings.md`](findings.md)). Add **one optional block** to the
entity schema — a flat bag of named modifiers — and a derived `PlayerStats` the server recomputes whenever
equipment changes:

```jsonc
"bee_suit_chest": {
  "category": "armor", "armor_slot": "body", "overlay": "bee_suit_chest",
  "bonuses": { "defense": 2, "bee_calm": 1, "honey_yield_pct": 15, "move_speed_pct": -3 },
  "set": "beekeeper"                 // optional: contributes to a set bonus
}
```

- **Additive** by default (`+2 defense`), `_pct` fields are percent multipliers (sum then apply).
- Sources that contribute: 5 armor slots + 2 accessory slots + backpack + **active consumable buffs** +
  **decoration idle aura** (§11.5, plot-only). Server sums them into `PlayerStats`; client shows the total.
- **Set bonus:** wearing N pieces sharing a `set` adds an extra `set_bonuses[N]` block (Terraria-style).
- **Diminishing returns / caps** are mandatory for the idle/decoration source (§11.5: per-`id`, overall cap)
  and recommended as a soft cap on the big ones (defense, speed) so stacking can't trivialize the game.

This is the *only* schema change the whole bonus system needs. Everything below is content on top of it.

---

## 2. The full stat list (per system)

Each row: the stat, what it does, and whether the underlying system exists yet (🟢 exists / 🟡 partial /
🔴 needs building first). "Needs building" stats are still worth listing — they tell us what gameplay to
add so the bonus has something to hook.

### Combat
| Stat | Effect | System ready? |
|---|---|---|
| `max_hp` | raise the 10-HP cap (hearts) | 🟡 HP exists, cap hardcoded |
| `defense` | flat damage reduction per hit | 🔴 no mitigation today |
| `damage_pct` | melee damage multiplier | 🟢 weapon moves have damage |
| `crit_chance` / `crit_mult` | chance for bonus-damage hit | 🔴 |
| `attack_speed_pct` | shorter swing cooldown | 🟢 cooldown_ticks exists |
| `reach_bonus` | longer melee arc reach | 🟢 reach on moves |
| `knockback` | push bugs back on hit (breathing room) | 🔴 |
| `hp_regen` | slow passive heal (out of combat) | 🔴 |
| `life_on_hit` | heal a sliver per kill | 🔴 |
| `thorns` | reflect a fraction of bite damage | 🔴 |
| `iframes_pct` | longer invulnerability window after a hit | 🟡 1s window exists |
| `dodge_chance` | chance to negate a hit | 🔴 |

### Mining (the loop is thin today — see [`suggestions.md`](suggestions.md) + BACKLOG to deepen it)
| Stat | Effect | System ready? |
|---|---|---|
| `mining_speed_pct` | faster block break | 🟢 mining_speed on pick |
| `effective_tool_tier` | mine one tier above your pick | 🟢 tool_tier gates ore |
| `ore_fortune` | chance to double ore drops | 🔴 |
| `gem_luck` | chance for gems/geodes in stone | 🔴 |
| `light_radius` | see further underground | 🔴 no light stat |
| `dig_aoe` | break a 3×1 / plus-shape of soft blocks | 🔴 |
| `hazard_resist` | reduce cave hazard damage (gas, fall) | 🔴 |
| `vein_sense` | highlight nearby ore (minimap ping) | 🔴 |
| `carry_weight` | mining-specific stack/ore-sack size | 🟡 backpack slots |

### Farming
| Stat | Effect | System ready? |
|---|---|---|
| `crop_growth_pct` | crops mature faster | 🟢 growth is server-driven |
| `water_retention_pct` | soil dries slower (less watering) | 🟢 crop water exists |
| `water_aoe` | watering can hits a 3×3 | 🟢 watering can |
| `harvest_yield` | chance of +1 crop on harvest | 🔴 |
| `crop_quality` | higher sell value / size tier | 🔴 |
| `seed_return` | chance to refund a seed | 🔴 |
| `fertilizer_potency` | compost/fertilizer works harder | 🟡 compost exists |
| `harvest_aoe` | scythe clears a wider swathe | 🟢 scythe |
| `pollination` | nearby bees boost adjacent crops | 🟡 bees exist |

### Bug farming / catching
| Stat | Effect | System ready? |
|---|---|---|
| `catch_radius` / `catch_arc` | wider net sweep | 🟢 net arc/reach |
| `catch_cap` | more bugs per swing | 🟢 catch_cap |
| `catch_success_pct` | beat tougher `catch_difficulty` | 🟡 catch is all-or-nothing |
| `lure_radius` | bugs drift toward you / a station | 🔴 |
| `calm_radius` | bugs flee less / are catchable longer | 🟡 calm_spray effect |
| `rare_bug_luck` | better odds of rare species | 🔴 |
| `bug_value_pct` | caught bugs sell for more | 🟢 sell_price |
| `pen_capacity` / `breed_rate` | farm-side throughput | 🟡 ecology sim |
| `honey_yield_pct` | more honey per hive | 🟡 beekeeping |
| `sting_immunity` | bees/wasps don't damage you | 🔴 (bee suit's headline) |

### Movement & exploration
| Stat | Effect | System ready? |
|---|---|---|
| `move_speed_pct` | base run speed | 🔴 fixed speed today |
| `terrain_immunity` | no mud/sand slow | 🔴 |
| `water_walk` / `water_breath` | cross/enter water (gates fishing & islands) | 🔴 |
| `light_radius` | torch/lantern aura (also a combat/mining safety) | 🔴 |
| `night_vision` | brighten caves/night | 🔴 |
| `fall_resist` | survive mine drops | 🔴 |
| `pickup_radius` | magnet for dropped items | 🟡 auto-pickup exists |

### Economy & utility
| Stat | Effect | System ready? |
|---|---|---|
| `sell_pct` | merchants pay more | 🔴 no economy yet |
| `buy_discount_pct` | cheaper purchases / recipes | 🔴 |
| `luck` | global rare-drop nudge (bugs, ore, fishing) | 🔴 |
| `inventory_slots` | the existing backpack bonus | 🟢 slot_bonus |
| `tool_durability_pct` | tools last longer | 🟢 durability |
| `stack_pct` | bigger stacks | 🟡 max_stack |

### Idle / production (decorations, plot-only, §11.5)
`comfort` (a meta-score that feeds a farm/production multiplier), `production_pct` (per station/category),
`station_speed_pct`. **Always** diminishing-returns per `id` + capped.

---

## 3. Bonus SOURCES (where the numbers come from)

Five layers, matching GDD §15.1 (armor + utility-overlay + accessories) plus consumables + décor:

1. **Armor sets** — every piece gives `defense`; a **full set grants a themed set bonus.** The progression
   ladder: *leather → copper → bug-chitin → iron → silver → crystal/gold (endgame).*
2. **Utility outfits** (the "much better than bare minimum" headline — §4 below) — themed working clothes
   that trade combat defense for **big bonuses to one activity** (bee suit, fisherman's vest, miner's kit…).
3. **Accessories** (2 slots, small bonuses, mix-and-match — §5 below).
4. **Consumables** — timed buffs from the cauldron/kitchen (potions, meals). Strong but expire.
5. **Decorations** — passive plot aura, capped (§11.5).

**Rule of thumb:** armor = survivability, outfits = *what you're doing this session*, accessories = fine
tuning, consumables = burst, décor = slow idle. You can't wear two outfits, so swapping IS the build choice.

---

## 4. Utility outfits (themed working sets) — the fun part

Each is a 1–3 piece overlay set whose **set bonus defines a playstyle.** These are the "bee suits, special
clothing like a fisherman's vest" the request called for. Defense on these is low — they're tools, not armor.

| Outfit | Pieces | Headline set bonus | Smaller per-piece bonuses |
|---|---|---|---|
| **Beekeeper suit** | hood, smock, gloves | **sting immunity** (bees/wasps can't hurt you) | `honey_yield_pct`, `bee_calm`, tiny `defense` |
| **Fisherman's vest** | hat, vest, waders | `water_walk` + later fishing yield/luck | `pickup_radius` (reel-in), `water_breath` (waders) |
| **Miner's kit** | helmet (lamp), jacket, boots | **built-in `light_radius`** (no torch needed) + `hazard_resist` | `mining_speed_pct`, `fall_resist`, `ore_fortune` |
| **Gardener's apron** | straw hat, apron, gloves | `crop_growth_pct` + `water_aoe` on your plot | `harvest_yield`, `seed_return` |
| **Entomologist's coat** | pith helmet, coat, satchel | `rare_bug_luck` + `calm_radius` | `catch_arc`, `bug_value_pct` |
| **Explorer's cloak** | hood, cloak, boots | `move_speed_pct` + `night_vision` | `terrain_immunity`, `pickup_radius` |
| **Forager's poncho** | wide hat, poncho | `gem_luck` + `luck` (find more while gathering) | `pickup_radius` |
| **Combat plate (true armor)** | helm, plate, greaves, boots, gauntlets (5) | `damage_pct` + big `defense` + `knockback` | `iframes_pct`, `hp_regen` |
| **Chitin / carapace set** (bug-themed armor) | head/body/legs | `thorns` + `defense` (made from boss-bug drops) | `dodge_chance` |

> Each outfit is also a **paper-doll overlay** (the system already renders `overlay` layers), so they read
> at a glance — you can SEE the beekeeper vs the miner. That visual identity is half the appeal.

## 5. Accessories (2 slots — small, swappable, expressive)

Per §15.2: small bonuses, mix-and-match, no treadmill. Sourced from the jeweler (gems→trinkets), rare
drops, and quest rewards. A taste of the menu:

- **Movement:** Swift Boots (`move_speed`), Frog Legs (water cross), Featherfall Charm (`fall_resist`).
- **Combat:** Warding Band (`defense`), Sharpened Fang (`damage`), Vampiric Locket (`life_on_hit`),
  Adrenaline Pin (`attack_speed`).
- **Gathering:** Lucky Clover (`luck` — exists!), Prospector's Loupe (`gem_luck`), Magnet Stone
  (`pickup_radius`), Green Thumb Ring (`crop_growth`).
- **Bug:** Bee Charm (`honey_yield` — exists!), Lens of Focus (`rare_bug_luck`), Calming Pendant
  (`calm_radius`).
- **Economy:** Merchant's Seal (`sell_pct`), Coin Pouch (`buy_discount`).
- **Light/utility:** Glowstone Amulet (`light_radius`), Tinkerer's Gear (`tool_durability`).

## 6. Trade-off items ("bonus while detrimenting") — Terraria flavor

The request specifically asked for items that **bonus while hurting another stat.** These create build
tension and let a player over-commit. Examples (all just a `bonuses` block with a negative field):

| Item | Gives | Costs |
|---|---|---|
| **Heavy Plate** | big `defense`, `knockback` | `move_speed_pct -15` |
| **Glass Cannon Charm** | `damage_pct +40` | `defense -50%`, `max_hp -2` |
| **Berserker Band** | `attack_speed` + `damage` when **below 30% HP** | takes +20% damage |
| **Greed Ring** | `sell_pct +25` | `luck -` (the world gives you fewer rare drops) |
| **Featherweight Boots** | `move_speed` | you get knocked back **further** |
| **Magnifier Goggles** | `rare_bug_luck +` | `catch_arc -` (tunnel vision — fewer per swing) |
| **Overloaded Rucksack** | `+stacks` / `inventory_slots` | `move_speed_pct -10` |
| **Caffeine Tonic** (consumable) | `+everything` for 60s | a `move_speed`/`attack_speed` **slump** after |
| **Lucky Rabbit's Foot** | `luck +` | `tool_durability -` (luck wears your gear) |
| **Glow Tattoo** | permanent `light_radius` | bugs notice you sooner (`lure_radius` on enemies) |

These are optional, never required — they reward knowing the systems. Keep the magnitudes spicy but the
*net* power roughly neutral, so it's a *choice*, not a no-brainer.

## 7. Stacking & balance rules (so it stays "small, meaningful")

- **Soft caps** on the headline stats: e.g. `defense` caps at ~50% mitigation; `move_speed` at ~+30%;
  `crop_growth` at ~+50%. Past the cap, extra points give heavily diminishing value.
- **Diminishing returns** are *mandatory* for the décor/idle source (per-`id`, overall cap — §11.5).
- **One outfit at a time** (you wear one body/legs/etc.) is the natural limiter — the big bonuses live on
  outfits, so you can't have the bee suit *and* the miner kit active.
- **No XP / no permanent stat growth** — power is the gear you chose to bring (GDD). Keep it that way.
- **`catch`/`mining`/`farming` bonuses are display/economy-side** (yields, sell value, speeds) — they
  must NOT feed the deterministic bug sim hash.
- **Combat math is SERVER-authoritative.** Player HP + damage-taken live server-side; `defense`/`max_hp`/
  `hp_regen` must be applied **where the server owns HP** (so it's consistent across clients), with the
  client only *displaying* the result. `damage_pct`/`attack_speed` modify the player's outgoing hits — also
  resolved server-side against bug HP. Don't apply mitigation client-only or players desync on damage.

## 8. What to build first (so a bonus has teeth)

Listed fully in [`suggestions.md`](suggestions.md), but the dependency order is: **(a)** the `bonuses`
schema + `PlayerStats` recompute → **(b)** wire `defense` + `damage_pct` into combat (gives armor a point)
→ **(c)** `move_speed` + `light_radius` (unlocks the explorer/miner fantasy) → **(d)** the activity yields
(`ore_fortune`, `harvest_yield`, `catch_success`, `honey_yield`) → **(e)** outfits + accessories + trade-off
items as content. Currency + merchant (so you can *buy* them) is its own track in `suggestions.md`.
