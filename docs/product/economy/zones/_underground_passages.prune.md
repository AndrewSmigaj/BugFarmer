# PRUNE — Underground Passages (first mining zone, grid 3,1) + the Miner's Outpost

> **Working decision doc (scratch).** Source of truth = [`underground_passages.md`](underground_passages.md)
> (status there: *"design only — nothing wired in yet"*). The design was authored **generous-to-prune**.
> Mark each row **KEEP** / **CUT** / **LATER** (push to a deeper zone) in the leftmost box. After you
> prune, the KEEPers get created as real entities (data + sprites + recipes) and the Outpost is stocked
> with the survivors. **Nothing is built until you've cut.**
>
> **Status column (checked against real entity data 2026-06-27):**
> `✅` exists today (real id in parens if different) · `🆕` must be created · `⚠️` id exists but as a
> DIFFERENT thing (collision — decide rename/reuse) · `⏸` exists but its *mechanic* is unbuilt ·
> `⛔` the design itself already supersedes/cuts it.
>
> **Reality check up front:** the base crafting ladder is mostly unbuilt too — **missing:** `glass`,
> `plank`, `cloth`/`thread`/`silk`, raw `leather`/`chitin`, `rope`, the bar ladder beyond `iron_bar`
> (`copper_bar`/`silver_bar`/…), `jeweler`, `rock_crusher`, all gems. So many KEEPs pull in base-material
> prerequisites — see §9. **Already exist:** `iron_bar`, `coal`, ores, `crystal`, `quartz`, `sand`,
> `brick`, `clay_block`, `stone_block`, `cave_moss`, `mushroom_glow`, `dead_beetle`, and the stations
> `furnace/anvil/forge/workbench/stonecutter/sawmill/loom/cauldron/cooking_pot`.

---

## 1. SPECIES (5) — each = sprite + deterministic AI (a SEPARATE frontier-sync pass regardless)
| Decision | Species | Status | Primary drop | Behaviour (sim cost) |
|:--:|---|:--:|---|---|
| ☐ | `springtail` | 🆕 | `springtail_dust` 🆕 (+`dead_springtail`🆕, `cave_moss`✅) | light-shy swarm cloud (lamp scatters them) |
| ☐ | `blind_beetle` | 🆕 | `blind_beetle_shell` 🆕 (+`chitin`🆕, `dead_beetle`✅) | slow armored detritivore, ignores light |
| ☐ | `mole_cricket` | 🆕 | `mole_cricket_claw` 🆕 (+`chitin`🆕, `dead_cricket`🆕, `soft_stone`🆕) | burrow-erupt charge, drawn to mining |
| ☐ | `cave_spider` | 🆕 | `cave_spider_silk` 🆕 (+`spider_venom`🆕, `dead_spider`🆕) | ceiling ambush, `venomed` DoT, lamp deters |
| ☐ | `glow_grub` (bonus) | 🆕 | `glow_sac` 🆕 (+`glow_grub` body, `raw_gem`🆕) | forage catch, clings to gem veins |

## 2. GATHERED MATERIALS (mine / forage in-zone)
| Decision | Id | Status | cost-pt | Use |
|:--:|---|:--:|:--:|---|
| ☐ | `saltpeter` | 🆕 | 1 | black-powder/blast base, preservative, flux |
| ☐ | `glowshroom` | 🆕 | 1 | light-flora: lantern fuel, night-eye, dye, light meal |
| ☐ | `cave_nitre` | 🆕 | 2 | lens/optics crystal (light line + glass clarity) |
| ☐ | `raw_emerald` | 🆕 | 2→10 | green gem → `cut_emerald` |
| ☐ | `raw_sapphire` | 🆕 | 2→16 | blue gem → `cut_sapphire` (T4–T5 stretch) |
| ☐ | `soft_stone` | 🆕 | 1 | cave brick/path, cart rubble, filler |
| — | reuse: `iron_ore`✅ `silver_ore`✅ `coal`✅ `crystal`✅ `quartz`✅ `cave_moss`✅ `mushroom_glow`✅ | ✅ | — | already in data |

## 3. DROP MATERIALS & CRAFTED INTERMEDIATES
| Decision | Id | Status | From / note |
|:--:|---|:--:|---|
| ☐ | `springtail_dust` | 🆕 | springtail — luminescent reagent + dye |
| ☐ | `blind_beetle_shell` | 🆕 | blind_beetle — thick pale plate |
| ☐ | `mole_cricket_claw` | 🆕 | mole_cricket — heavy dig claw |
| ☐ | `cave_spider_silk` | 🆕 | cave_spider — fine silk |
| ☐ | `spider_venom` | 🆕 | cave_spider — light venom |
| ☐ | `glow_sac` | 🆕 | glow_grub — cold-light gel |
| ☐ | `dead_springtail` / `dead_cricket` / `dead_spider` | 🆕 | new `dead_*` carcasses (note: `dead_spider` is NOT in data yet despite the sheet's ✅) |
| ☐ | `chitin` | 🆕 | secondary drop (beetle/cricket) — raw material, NOT yet in data |
| ☐ | `cut_emerald` / `cut_sapphire` | 🆕 | jeweler gem-cut intermediates |
| ☐ | `paydirt` (name TBD) | 🆕⏸ | rock_crusher output (processing chain) |

## 4. STATIONS
| Decision | Id | Status | Role |
|:--:|---|:--:|---|
| ☐ | `rock_crusher` | 🆕⏸ | crush rock+ore → `paydirt` (art-needed already logged) |
| ☐ | `sluice` | ✅⏸ (`ore_sluice` exists as a structure) | `paydirt` → ore + gems — reuse `ore_sluice`? mechanic unbuilt |
| ☐ | `jeweler` | 🆕 | gem-cut + accessories (designed-not-built; gates `cut_*`/loupe/band) |

## 5. RECIPES / CRAFTABLE ITEMS  (output · station · inputs · unlock)
### 5a. Mining tools & dig-shortcut
| Decision | Output | Status | Station | Inputs | Unlock |
|:--:|---|:--:|---|---|---|
| ☐ | `blast_charge` (dig consumable) | 🆕 | workbench | `saltpeter`2 + `coal`1 + `clay_block`1 | craft / buy@outpost |
| ✗ | ~~`deepcut_pick`~~ | ⛔ | — | — | superseded → metal pick ladder (D12) |
| ✗ | ~~`fortune_drill`~~ | ⛔ | — | — | superseded → Spelunker set + loupe |
### 5b. Light gear (zone survival headline)
| Decision | Output | Status | Station | Inputs | Unlock |
|:--:|---|:--:|---|---|---|
| ☐ | `glow_lantern` (held) | 🆕 | workbench | `iron_bar`1 + `glass`🆕2 + `glow_sac`1 + `cave_nitre`1 | craft / buy@outpost |
| ☐ | `cave_headlamp` (head, hands-free) | 🆕 | anvil | `iron_bar`1 + `cave_nitre`1 + `springtail_dust`2 + `cave_spider_silk`2 | **buy@outpost (recipe)** |
| ☐ | `glowstick` (throwable) | 🆕 | workbench | `glowshroom`2 + `springtail_dust`1 | craft |
### 5c. Hauling  (cart system PENDING — research first)
| Decision | Output | Status | Station | Inputs | Unlock |
|:--:|---|:--:|---|---|---|
| ☐ | `ore_sack` (carry gear) | ⚠️ id exists as **decoration prop** — collision; the carry-gear is new | loom | `cave_spider_silk`6 + `cloth`🆕2 + `blind_beetle_shell`1 | craft / buy@outpost |
| ☐ | `mine_cart` (hauling) | ⚠️⏸ exists as decorative structure; functional cart = PENDING mechanic | anvil | `iron_bar`3 + `plank`🆕4 + `mole_cricket_claw`1 + `soft_stone`4 | buy/craft |
| ☐ | `cart_rail` ×4 | ⚠️⏸ (`mine_rail` exists as decor) | stonecutter | `iron_bar`1 + `soft_stone`4 | craft |
### 5d. Ore / gem processing  (chain mechanic PENDING)
| Decision | Output | Status | Station | Inputs | Unlock |
|:--:|---|:--:|---|---|---|
| ☐ | `paydirt` (TBD) | 🆕⏸ | rock_crusher | rock + ore | craft |
| ☐ | ore + gems (sluice output) | ⏸ | sluice/`ore_sluice` | `paydirt` | craft |
| ☐ | `cut_emerald` | 🆕 | jeweler🆕 | `raw_emerald`2 + `quartz`1 | craft |
| ☐ | `cut_sapphire` | 🆕 | jeweler🆕 | `raw_sapphire`2 + `cave_nitre`1 | craft / find |
| ☐ | `prospectors_loupe` (accessory) | 🆕 | jeweler🆕 | `cave_nitre`1 + `cut_emerald`1 + `silver_bar`🆕1 | craft / buy@outpost |
### 5e. Cave décor / structure / food / consumable
| Decision | Output | Status | Station | Inputs | Unlock |
|:--:|---|:--:|---|---|---|
| ☐ | `cave_block` ×4 | 🆕 | stonecutter | `soft_stone`4 | craft |
| ☐ | `cave_brick` ×4 | 🆕 | stonecutter | `soft_stone`2 + `saltpeter`2 | craft |
| ☐ | `glowshroom_lamp` (light décor) | 🆕 | workbench | `glowshroom`2 + `cave_nitre`1 + `iron_bar`1 | craft |
| ☐ | `geode_cluster` (trophy décor) | 🆕 | jeweler🆕 | `raw_sapphire`1 + `cut_emerald`1 + `iron_bar`1 | find / craft |
| ☐ | `glow_jerky` (food buff) | 🆕 | cooking_pot | `dead_beetle`1 + `glowshroom`1 + `saltpeter`1 | craft |
| ☐ | `spider_antidote` (consumable) | 🆕 | cauldron | `glowshroom`1 + `spider_venom`1 + `cave_moss`1 | craft / buy@outpost |

## 6. ARMOR — Spelunker's Kit (T3 set) + off-hand/accessory
| Decision | Piece | Status | Slot | Station | Inputs |
|:--:|---|:--:|---|---|---|
| ☐ | `spelunker_helm` | 🆕 | head | anvil | `iron_bar`2 + `blind_beetle_shell`2 + `cave_nitre`1 + `cut_emerald`1 |
| ☐ | `spelunker_vest` | 🆕 | body | loom | `iron_bar`2 + `cave_spider_silk`4 + `blind_beetle_shell`2 + `cloth`🆕2 — **buy@outpost OR find** |
| ☐ | `spelunker_boots` | 🆕 | feet | anvil | `iron_bar`1 + `cave_spider_silk`2 + `blind_beetle_shell`1 + `soft_stone`2 |
| ☐ | `shell_buckler` (off-hand) | 🆕 | offhand | workbench | `blind_beetle_shell`4 + `iron_bar`1 |
| ☐ | `spelunker_band` (opt. 4th) | 🆕 | accessory | jeweler🆕 | `cut_sapphire`1 + `silver_bar`🆕1 + `mole_cricket_claw`1 |
> Per-piece + set `bonuses{}` (light_radius/mining_speed_pct/carry_weight/vein_sense/defense) are
> specced in the sheet. The `bonuses{}` STAT SYSTEM itself is separate (stats_and_bonuses.md) — flag if
> we wire stats now or stub them.

## 7. MINER'S OUTPOST (`miners_outpost`) — MERCHANDISE
**Sells (buy@miners_outpost; placeholder prices):**
| Decision | Entry | Type | Price | Depends on |
|:--:|---|---|:--:|---|
| ☐ | recipe `rock_crusher` | recipe | 280 | §4 |
| ☐ | recipe `sluice` | recipe | 220 | §4 |
| ☐ | recipe `cave_headlamp` | recipe | 180 | §5b |
| ☐ | recipe `ore_sack` | recipe | 160 | §5c |
| ☐ | recipe `spelunker_vest` | recipe | 420 | §6 |
| ☐ | `glow_lantern` (finished) | gear | 120 | §5b |
| ☐ | `glowstick` ×3 | consumable | 30 | §5b (daily cap) |
| ☐ | `blast_charge` | consumable | 40 | §5a (daily cap) |
| ☐ | `spider_antidote` | consumable | 25 | §5e |
| ☐ | `iron_bar` ✅ | material | 35 | restock (cap, markup) |
| ☐ | `coal` ✅ | material | 15 | restock (cap, markup) |
| ☐ | `silver_bar` 🆕 | material | 90 | needs the bar ladder built |
| ☐ | station `jeweler` 🆕 | station | 260 | §4 |
| ☐ | station `rock_crusher` 🆕 | station | 240 | §4 |

**Buys (sell-to; ore/gem + silk/venom premiums — premium not yet expressible, see §9):**
`iron_ore`✅, `silver_ore`✅, `coal`✅, `soft_stone`🆕, `saltpeter`🆕, `cave_nitre`🆕, `raw_emerald`🆕,
`raw_sapphire`🆕, `crystal`✅, `quartz`✅, `cave_spider_silk`🆕, `blind_beetle_shell`🆕,
`mole_cricket_claw`🆕, `spider_venom`🆕, `springtail_dust`🆕, `glow_sac`🆕.

**Booth + crew (all ✅):** `market_stall`, `sign_camp`/`sign_shop`, `awning`, `counter`, `tool_rack`,
`ore_pile`, `mine_support`. Plus 2–3 ambient `miner_npc` 🆕 (talk-only).

## 8. THE DESIGN'S OWN PRE-CUTS / PENDING (decide to honor or override)
- ⛔ `deepcut_pick`, `fortune_drill` — superseded by the metal pick ladder (D12).
- ⏸ Cart system (`mine_cart`/`cart_rail`) — mechanics undecided (research Minecraft carts first; backlog).
- ⏸ Processing chain `rock_crusher → paydirt → sluice` — D13 design; `ore_sluice` exists but inert.
- `paydirt` — name TBD. `tnt`/`powder_keg` already exist as structures (relevant if you want blast props).
- T4–T5 gem stretch (`raw_sapphire`, `cut_sapphire`, `prospectors_loupe`, `spelunker_band`) — candidate **LATER**/deeper-zone.

## 9. PREREQUISITE / DEPENDENCY GAPS the KEEPs will pull in (so cuts are eyes-open)
- **Base materials missing:** `glass` (→ glow_lantern), `cloth`/`thread`/`silk` (→ ore_sack, spelunker_vest; loom exists but no recipes), `plank` (→ mine_cart; sawmill exists, no recipe), raw `chitin` (drop + cooking), `silver_bar` + the rest of the **bar ladder** (only `iron_bar` exists).
- **Stations missing:** `jeweler` (gates ALL gem-cut + loupe + band + geode), `rock_crusher`.
- **`ore_sack` id COLLISION:** an `ore_sack` *decoration prop* already exists — the carry-gear needs a rename or repurpose.
- **Per-shop "buy ore HIGH" premium** isn't expressible — sell price is global per item (backlog per-shop multipliers).
- **Stat bonuses** (`light_radius`/`vein_sense`/etc.) have no engine yet — light/mining gear would be cosmetic until that lands.

## 10. AFTER PRUNE → build order (re-planned against your cuts)
Create KEEP base-mats → KEEP items/intermediates (data+sprites, full fields) → KEEP recipes (auto vs
`shop:miners_outpost`) + any new stations → recipe-unlock mechanism → NPC sprites + dialogue shell →
place Outpost + miners + booth in `scene_underground_mining_camp.py` → verify + commit. **Species AI =
separate frontier-sync pass. Cart/processing mechanics = backlog unless you keep+spec them.**
