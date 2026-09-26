# Tools — the catalog (finalized 2026-06-25)

The tool slot, trimmed to **"metal tiers + a few meaningful specials"** per `DECISIONS.md` D12–D14 — thorough,
not excessive. Cost model + stations in `../crafting.md`; pacing in `../progression.md`. ✅ = id exists in
`items.json` today. Design-only; nothing here is wired.

> **Cut from earlier drafts** (D12): special pick variants (`deepcut_pick`, `fortune_drill`, `fortune_pick`),
> watering-can metal tiers, `silk_net`/`gossamer_net` framing, harpoons, `cave_rod`, `dowsing_rod`,
> `watering_wand`, `shears`, and the nonsense lanterns (`catcher_lantern`, `ranger_lantern`, oil refills).

---

## (A) Base tier families — the metal ladder
Each gathering verb upgrades by metal: **wood → stone → copper → iron → steel → silver → gold → platinum**
(**platinum is the top — no diamond tools/armour**, D11). Station: **anvil ≤iron, forge steel+**. Recipe
`{bar}×2 + wood×2` unless noted. Shown compactly (one row per family + the per-tier stat curve).

| Family | Tiers | Stat it scales | Notes |
|---|---|---|---|
| **pickaxe** | wood✅→stone✅→copper✅→iron✅→steel→silver→gold→platinum | mining_speed + the ore the tier unlocks | NO special variants — just metals (D12). Each tier breaks the next ore (copper→iron, iron→silver/gold, steel→platinum). |
| **axe** | wood✅→…→platinum | chop_speed (+ stab secondary) | See **saw** below — big trees need it; better axes return above the saw so axes never go dead (D12). |
| **shovel** | wood✅→stone✅→…→platinum | dig_speed (dirt/sand/clay/peat) | digs the `sand_block`/`clay_block` clumps. |
| **hoe** | wood✅→stone✅→…→platinum | till cooldown (+ AoE at higher tiers) | farming is **early-unlocked**; tiers just speed it. |
| **scythe** | wood✅→…→platinum | reap cooldown + **AoE** | the AoE harvest verb (see **harvest sickle**). |
| **net** | **small✅ + large✅ only** | catch_cap / arc | large = "just bigger." Better/cast nets + **bug-size matching** → backlog (D12). |
| **watering_can** | **small✅(basic) + large✅ only** | capacity | NO metal tiers (D12) — farming isn't gated behind fancy metals. |

## (A2) The few meaningful non-metal tools
| id | station | effect | tier |
|---|---|---|---|
| **`magnifying_glass`** | jeweler | **inspect bugs** (rarity/value/needs before catching). **Given from the start.** | T1 (starter) |
| **`saw`** | anvil | fells **large/tough trees** the early axes can't; sits one tier **above current axes**, more planks/tree. Better axes arrive later above it. | ~T3–T4 |
| **`harvest_sickle`** | anvil | **AoE plant harvest** — cuts more plants per swing than hand-harvesting (for the larger wheat/grass fields). | ~T3 |
| **`bee_smoker`** ×3 | anvil | harvest hives without aggro; **3 tiers** for faster/stronger (and hostile) bees — part of the **beekeeping system** (backlog). | T2 → up |
| **`bug_vacuum`** | workbench | hand vacuum — auto-catches small bugs in a cone into a hold. | T4 |
| **`grappling_hook`** | forge | cross **deep-water gaps** / pull-to-ledge; introduced later-ish. | ~T4 |
| **`firefly_lantern`** | workbench | catch fireflies → bottled light (`light_radius`+night_vision). Available in an **early area**. | T1–T2 |
| **`headlamp`** | anvil | hands-free cave light (`light_radius`+vein_sense). | T3 |
| **`glowworm_lantern`** | workbench | the best natural light (green); from glowworm caves. | T3 |
| **`torch`** ✅ | workbench | basic placed/held light (many torches are **cosmetic**). | T1 |
| **`flashlight`** ✅ | workbench / buy | held directional light (`tool_type: flashlight`) — **as-built** early cave light. | T1–T2 |

*Light is kept deliberately small — a few sources at different radii (D12). Decorative light + their bonuses
are the separate **home-plot décor** system (backlog).*

## (A3) Bug collection (passive)
- **`autonet`** ✅ — placed auto-collector (sprite exists), capacity-capped like all stations.
- **`bug_vacuum`** — the handheld version (above).
- *Silk:* cut webbing with a **sword/blade** (no `shears`).

---

## (B) Mining station chain (NEW — D13) + pending mechanics
Mining is a priority loop and a deliberately slow, exploratory ramp.

| id | type | effect | status |
|---|---|---|---|
| **`rock_crusher`** | station | crushes rock + ore → **`paydirt`** *(name TBD)* | design (D13) |
| **`sluice`** | station | runs `paydirt` → separates out ore / gems | design (D13) |
| **`dredge`** | placeable + tiers | place on water → station "dredge" button → hose-tool you click water with; weaker→stronger + a **swamp dredge** variant | **backlog mechanic** (D14) |
| **`mine_cart` + `cart_rail`** | hauling | rail goes L/R/U/D (diagonal TBD); auto-haul ore | **backlog** — research Minecraft minecarts first |
| **`drill`** / `electric_drill` | powered mining | fast AoE mining; runs on **batteries** (buy/find) → later a **battery recharger** | **backlog — electricity EXPANSION** (wealth-gated, not zone-gated) |

## (C) Fishing (D12 — no harpoons)
- **`fishing_rod`** — base rod; **rod TIERS** (not cave-vs-normal). The catch is a **mini-game** (backlog).
- **fish traps** — passive, over-time, **capacity-capped** (like all stations); faster/better-effectiveness
  tiers. (e.g. a basic trap → a better trap.)
- Harpoons, cast/thrown nets, bows → **backlog** (mechanics undecided).

## (D) Farming automation
- **Sprinklers — small + large** (Stardew-style auto-water aura). The one genuinely-new farming mechanic; the
  rest of automation is data. (See `../crafting.md §6`.)

---

**Scope:** ~7 base metal families (platinum-topped) + ~10 meaningful specials + the mining/fishing/automation
station chains. The metal ladders are the bulk; specials are kept few and purposeful (D12).
