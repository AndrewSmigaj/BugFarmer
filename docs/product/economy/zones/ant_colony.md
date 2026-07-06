# Zone Content Sheet — Ant Colony (intro · col 0, row 3 · `ant_colony`)

> **Grid (3,0)** *(row,col — fixed 2026-07-06; an old (col,row) slip said "(0,3)")* · the first **underground** intro zone of column 0 · **difficulty EASY→MEDIUM** ·
> **tier T2→T3 (copper/bronze era reaching toward iron, with the first light/cave gear)**
>
> The **friendly-but-organized ant colony** — BugFarmer's underground intro. Past the surface meadows the
> player drops into the first cave system and finds it isn't empty rock: it's a **living colony** where ants
> **farm fungus** in tended galleries, run tidy supply trails, and answer to a **Colony Queen**. This is the
> zone that introduces **darkness** (you need light to work), **fungus farming** (a unique food/material chain
> the ants give you access to), **formic-acid alchemy** (the ants' own chemical defense becomes your reagent),
> **ant-chitin light armor**, and a **Myrmecologist vendor** who trades ant lore and ant-eggs. Row 3 is the
> easy entry galleries; **row 4 is medium and ends at the `colony_queen` mini-boss** in the royal chamber.
>
> **Design intent (pacing, per `../README.md` + `../progression.md` §"Mid" — "intro Ants (col 0)"):** this is
> the gentle on-ramp to *underground play*. The colony is mostly **harmless and helpful** (garden/black ants
> ignore you, harvester ants are stubborn but slow, the fungus is a generous free pantry) — the only real
> danger is the **soldier ants** guarding the deep galleries and the **Queen**. You don't brute-force the
> dark; you bring a light source, learn the fungus loop, brew a little formic alchemy, plate up in
> ant-chitin, and **then** the colony becomes a friendly, self-stocking food-and-material farm with a boss at
> the bottom. Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat vocab
> + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T2→T3, "intro Ants (col 0)", the ant **Queen** mini-boss seam);
> shop seam from [`../merchants.md`](../merchants.md) (a new dedicated **Myrmecologist's camp** vendor at the
> colony mouth). World-guide species: garden ants, black ants, harvester ants, soldier ants, + the **Queen**.
> Reuses the existing ant ids `ant_egg`, `formic_dab` / `formic_acid`, and the underground flora
> `mushroom_glow` / `cave_moss`.

---

## Species & drops

Five concrete species span the friendly→guarded curve — two harmless workers, a stubborn forager, a guard
threat, and the royal mini-boss. Behaviors slot into the existing ant/arthropod vocabulary (trail-follow,
anchor-and-patrol, flank, swarm-the-crumb-not-you, flee) without needing new sim primitives. The signature
theme is **the organized colony**: ants run *trails*, *farm fungus*, defend with *formic acid*, and answer to
the **Queen**. Most are catch/forage targets, not kill targets — only soldiers and the Queen fight back.

| Species (id) | Tier feel | Behavior | Primary drop — new id | Secondary drop(s) |
|---|---|---|---|---|
| `garden_ant` ✅ | harmless worker (reuse) | Reused from the village — basic black worker marching tidy trails between mound and food. Here it tends the **fungus gardens**: follows pheromone trails carrying leaf bits to the fungus combs. Disturb a trail and they swarm the *crumb*, not you. The "ants are friendly" teach. | `ant_egg` ✅ (brood pearl) | `formic_dab` ✅ (a drop of formic acid), `dead_ant` (new `dead_*` carcass) |
| `black_ant` | harmless worker | The colony's haulers — larger black workers that **carry forage in long supply columns** through the galleries. Ignore the player entirely unless you stand on the trail; gentle nuisance pressure on the fungus, not the player. A *column* catch (many in a line), teaching trail timing. | `ant_fungus` ✅(new — they shed/spill fungus bits they're hauling) | `formic_dab` ✅, `dead_ant` (new) |
| `harvester_ant` | stubborn forager | Big red seed-harvesters that **anchor to a `seed_cache` granary** and trundle out to gather. **Slow but stubborn** — won't flee, will bite if you grab their cache (a light `nipped` sting, no DoT). The "wait it out / take the cache when the trail's away" teach. Worth chasing for the heavy mandibles. | `harvester_mandible` ✅(new) | `seed_husk` (new — granary chaff), `chitin` ✅ (common), `dead_ant` (new) |
| `soldier_ant` | core threat (guard) | The colony's **guards** — armored major-caste ants anchored to the deep gallery mouths and the royal approach. **Patrols, flanks, and bites hard**; sprays **formic acid** when pressed (an `acid_burn` armor-chip debuff, lighter than scorpion venom). Aggressive only near what they guard — leave the deep galleries alone and they leave you alone. The first real fight of column 0. | `soldier_chitin` ✅(new) | `formic_acid` ✅ (concentrated, off a guard), `chitin` ✅, `dead_ant` (new) |
| `colony_queen` | **mini-boss** (the royal chamber) | The **signature fight** — a bloated egg-laying matriarch anchored to the **royal chamber** at the bottom of row 4. Stationary-ish; **continuously emits `soldier_ant` adds** from her brood until you break the brood piles, then defends directly with a sweeping mandible slam + a **formic-spray AoE** ground hazard. Gear-gated, not twitch-gated. | `royal_jelly_ant` ✅(new — guaranteed, 1–2) | `queen_chitin` (rare carapace — décor/trophy + the keystone armor input), `ant_egg` ✅ (×3–5, royal brood), `royal_pheromone` (new — the colony-command reagent) |

**Drop notes**
- `garden_ant`, `ant_egg`, `formic_dab`, `formic_acid`, `chitin` are **existing ids** — reused as-is. The
  `dead_*` carcass is `dead_ant` (new, in the existing family).
- `ant_fungus` is the keystone of the **fungus food chain** (see materials + the food recipes); `black_ant`
  spilling it is the in-fiction supply.
- `harvester_mandible` + `soldier_chitin` are species-signature crafting drops (mining/grip tools + the light
  armor). `seed_husk` is the harvester granary chaff (compost/feed input). `queen_chitin` and
  `royal_pheromone` round out the mini-boss table — the "I beat the Queen" flex + the keystone armor/command
  inputs. `royal_jelly_ant` is the marquee Queen reagent (alchemy + the buff food).
- **Two-tier formic supply mirrors the venom zones:** `formic_dab` (common worker drop, reused) → `formic_acid`
  (concentrated, off the **soldier_ant** guards) — a clean cheap→strong reagent ladder for the alchemy line.

**Drop → use at a glance**
- `ant_fungus` → the **fungus food chain** (the unique ant-farmed pantry) + a fungus-leather binder.
- `harvester_mandible` → pincer-grip tools (the colony's light dig pick + the armor's gauntlet).
- `soldier_chitin` → the **ant-chitin light armor** plating (the zone's signature set).
- `formic_dab` ✅ / `formic_acid` ✅ → **formic-acid alchemy** (etch, cleaner, the acid throwable, a sour
  cooking note) — cheap vs strong tier.
- `royal_jelly_ant` → the marquee buff food + the Queen-tier alchemy reagent.
- `queen_chitin` → the keystone armor piece + the royal trophy/décor.
- `royal_pheromone` → the **colony-command** consumable (calm/lure the ants — the friendly-colony payoff).

---

## New ingredients & materials

Cave-, fungus-, and ant-themed gatherables you **mine or forage from the underground environment** (not bug
drops). They give the zone non-combat reasons to explore the dark and feed the recipe list. Source = `mine`
(break a node/vein), `forage` (pick). Most are cost-point 1–2.

| Id | Source (find@ant_colony) | Cost-pt | Use |
|---|---|---|---|
| `mushroom_glow` ✅ | forage — bioluminescent caps clustered on damp gallery walls (reuse the existing underground flora). Common. | 1 | The zone's **free light source** — feeds the early glow-lamp + glow-paint + a `light_radius`/`night_vision` cooking note; the "you can see by the mushrooms" teach. |
| `cave_moss` ✅ | forage — soft luminescent moss on the cooler north walls (reuse). Common. | 1 | A cheap green dye/binder + a soft bedding/insulation décor + a mild glow note for paint; the underground's cheap-forage-flora analog. |
| `ant_fungus` ✅ | forage from the **fungus gardens** (also spilled by `black_ant`) — the pale combs the ants farm on chewed leaf-mulch. Common in tended galleries. | 2 | The keystone **food-chain** ingredient (fungus bread/stew/jerky) **and** a **fungus-leather** binder for the chitin armor's soft layers. The unique ant-farmed material. |
| `mycelium_mat` | forage — the dense root-web mat under a mature fungus garden (a richer, processed `ant_fungus`). Uncommon. | 2 | Premium fungus-leather + a `crop_growth`/compost substrate (the colony's farming wisdom) + the fungus-farm "seed" to start your own gallery. |
| `fungal_spore` | forage — puffed spore pods on old combs; harvest a cloud. Uncommon. | 2 | Inoculant to **seed a new fungus garden** (the player's own underground farm) + a rare-bug/`luck` bait note + a spore-bomb throwable base. |
| `chalk_stone` | mine — soft pale limestone the galleries are dug through (the colony's bedrock). Common. | 1 | The signature underground building stone: stonecutter blocks/paths/walls, the gallery-shelter décor, and a lime/grit for the cleaner; cuts at the **stonecutter**. |
| `glow_quartz` | mine — quartz nodules that hold the mushroom-glow, found in deep-gallery veins. Uncommon. | 2 | A self-lighting `crystal`/`quartz` source for the **glow-lamp** + the colony's `light_radius` décor flex; cracks at the **stonecutter/jeweler**. |
| `copper_ore` ✅ | mine — the first metal veins threaded through the `chalk_stone` (reuse; this is the zone that **introduces underground metal mining**). | — | Reuse — smelt → `copper_bar`/`bronze_bar` at the furnace; the T2→T3 metal supply this zone opens up. |
| `coal` ✅ | mine — dark seams in the chalk (reuse). | — | Reuse — fuel for furnace/forge; the underground heat economy and the bridge toward iron. |

> **Why these:** `mushroom_glow` + `cave_moss` + `glow_quartz` carry the **light/underground** identity so the
> player is never stuck in the dark (the cheap light answer is always craftable); `ant_fungus` + `mycelium_mat`
> + `fungal_spore` are the dedicated **fungus-farm chain** so the food recipes and the chitin armor's soft
> layers have a unique input the ants give you; `chalk_stone` carries the underground *building* identity;
> `copper_ore`/`coal` are the reused ores this zone exists to open. The survival answer (light) is cheap and
> always craftable so a careful player is never locked out of *seeing* — only of the spicy Queen-tier gear.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; everything is **gated T2→T3** (a couple reach `iron_bar` /
`queen_chitin` as a stretch toward T3+). `unlock`: **craft** (have station + recipe) / **buy@myrmecologist** /
**find@ant_colony**.

### Underground light tools (the zone's headline — you must *see* to work)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `glow_lantern` (held light) | workbench | `mushroom_glow` ×3, `glass` ×1, `wood` ×2 | find@ant_colony (tutorial gift) / craft | `light_radius +2`, `night_vision +1`; the **first cave light** — bottled glow-mushroom, no fuel | T2 |
| `glowquartz_lamp` (held/head light) | workbench | `glow_quartz` ×2, `copper_bar` ×1, `glass` ×1 | craft / buy@myrmecologist | `light_radius +3`, `night_vision +1`; brighter, sustained — the deep-gallery upgrade | T2→T3 |
| `glow_paint` (placeable utility) | dye_vat | `mushroom_glow` ×2, `cave_moss` ×1, `fungal_spore` ×1 | craft | paints a **breadcrumb glow-marker** on walls (won't get lost in the galleries); décor `light_radius` aura | T2 |

### Fungus food chain (cooking_pot — the unique ant-farmed pantry, timed buffs)

| Output (id) | Station | Inputs | Unlock | Buff | Tier |
|---|---|---|---|---|---|
| `fungus_bread` | cooking_pot | `ant_fungus` ×2, `wheat` ✅ ×1 | craft | `hp_regen +1` (short, hearty) — the staple loaf of the underground | T2 |
| `fungus_stew` | cooking_pot | `ant_fungus` ×2, `mushroom_glow` ×1, `carrot` ✅ ×1 | craft | `light_radius +1` + `night_vision +1` (short) — "eat the glow, see in the dark" | T2 |
| `royal_jelly_tonic` | cooking_pot | `royal_jelly_ant` ×1, `honeydew` ✅ ×1 | craft / find | `max_hp +5` + `hp_regen +1` (long, rich) — the Queen-drop payoff meal | T3 |
| `fungus_jerky` (preserved) | cooking_pot | `ant_fungus` ×2, `dead_ant` ×1 *(or any `dead_*` bug-meat)* + `chalk_stone` ×1 *(lime cure)* | craft | salt/lime-cured — long-duration `defense +1` / `hp_regen +1` (preservation payoff) | T2→T3 |

### Formic-acid alchemy (cauldron — the ants' chemistry becomes your reagent)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `formic_etch` (utility reagent) | cauldron | `formic_acid` ✅ ×1, `chalk_stone` ×1 | craft / buy@myrmecologist | An **etch/cutting agent** for the stonecutter & jeweler (gem-cut, fine brick) + a strong cleaner; the colony's industrial output | T2 |
| `acid_flask` (throwable weapon) | cauldron | `formic_acid` ✅ ×2, `glass` ×1, `fungal_spore` ×1 | find@ant_colony (recipe) / craft | Thrown — AoE `acid_burn` (armor-chip DoT) on the soldier swarms; the anti-guard answer (turns their own acid on them) | T2→T3 |
| `formic_salve` (consumable buff) | cauldron | `formic_dab` ✅ ×2, `cave_moss` ×1, `yarrow` ✅ ×1 | craft | Short **`hazard_resist +2` (acid)** + `hp_regen +1` — cures/resists the soldiers' `acid_burn`; the survival answer | T2 |

### Colony command + farm (the friendly-colony payoff)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `pheromone_whistle` (consumable) | cauldron | `royal_pheromone` ×1, `formic_dab` ✅ ×2, `honeydew` ✅ ×1 | buy@myrmecologist (recipe) / find | Short aura: **ants calm & follow** (`calm_radius` + a friendly `lure_radius`) — walk the colony unmolested, herd workers to your fungus farm; the marquee "the colony likes you" toy | T3 |
| `fungus_garden` (placeable farm/station) | workbench | `wood` ×6, `mycelium_mat` ×2, `fungal_spore` ×1 | craft / buy@myrmecologist | Seeds **your own fungus garden** — passively grows `ant_fungus` from leaf-mulch input (the underground farm plot) | T2→T3 |
| `colony_compost` (fertilizer) | compost_bin | `seed_husk` ×2, `ant_fungus` ×1, `cave_moss` ×1 | craft | `crop_growth_pct` soil boost — the harvester-granary + fungus compost (the ants' farming wisdom, surfaced) | T2 |

### Underground stone / gem-cut décor & structure (stonecutter / jeweler)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `chalk_block` ×4 | stonecutter | `chalk_stone` ×4 | craft | structure / pale underground wall & path material | T2 |
| `chalk_brick` ×4 | stonecutter | `chalk_stone` ×2 + `formic_etch` ×1 (mortar/etch) | craft | finer gallery brick (acid-mortared) — the building line | T2 |
| `cut_glowquartz` | jeweler | `glow_quartz` ×2 + `formic_etch` ×1 (etch) | craft | **Gem-cut** intermediate — polished self-glowing quartz for jewelry/inlay/lamps | T2→T3 |
| `glowquartz_chandelier` | jeweler | `cut_glowquartz` ×1, `copper_bar` ×1, `mushroom_glow` ×1 | craft | light décor — a glowing gallery centerpiece (`light_radius` aura), the colony flex piece | T3 |
| `colonist_charm` (accessory) | jeweler | `cut_glowquartz` ×1, `harvester_mandible` ×1, `copper_bar` ×1 | craft / buy@myrmecologist | `light_radius +1`, `harvest_yield +1`, `luck +1` — the underground-forager trinket | T2→T3 |

> **Supply logic:** light (`glow_lantern` → `glowquartz_lamp`) is the zone's progression spine — the first
> lets you work the easy galleries, the second lights the deep row-4 approach. `mushroom_glow`/`cave_moss`/
> `chalk_stone` (common gatherables) keep light, salve, and building **cheap and always craftable**. The
> formic ladder gates the spicy `acid_flask` on the soldiers' `formic_acid`, while `formic_dab` (common) keeps
> the salve cheap. `ant_fungus` (the unique farmed input) anchors the food chain; `mycelium_mat`/`fungal_spore`
> let the player **build their own fungus garden**. `royal_jelly_ant` / `royal_pheromone` / `queen_chitin`
> (mini-boss) gate the marquee tonic, the colony-command whistle, and the keystone armor — held in reserve as
> the **Queen reward** and the forward hook to deeper column-0 ant zones (Deadly Ants, per progression "Late").

---

## Signature gear — the **Colonist's Carapace** (T2→T3 bonus set)

A 3-piece ant-chitin **light armor** outfit: layered `soldier_chitin` plating over a soft `ant_fungus`-leather
underweave, a harvester-mandible gauntlet, and a glow-quartz lamped helm. Theme = **the colonist who walks the
dark galleries lit and protected, at home among the ants**. This is a *light-armor + underground-utility* set
(not a heavy combat set), so its signature stats are **`defense` (light) + `light_radius` + `hazard_resist`
(acid) + an ant-related `harvest_yield`/`night_vision`**, with the **set bonus** delivering the friendly-colony
fantasy. Built at **anvil/forge** (chitin plating) + **loom** (the fungus-leather underweave) + a **jeweler**
inlay (the lamp) — a mixed-station set that shows off the zone's identity. T2→T3 (drops + copper/bronze, the
keystone reaching `queen_chitin`).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `colonist_helm` | head | anvil | `soldier_chitin` ×2, `glow_quartz` ×1, `copper_bar` ×1 | `defense:2, light_radius:2, night_vision:1, hazard_resist:1` (built-in glow-lamp) | `colonist` |
| `colonist_vest` | body | loom | `soldier_chitin` ×3, `ant_fungus` ×3, `chitin` ×2, `copper_bar` ×1 | `defense:4, max_hp:5, hazard_resist:2 (acid), harvest_yield:1` (fungus-leather underweave) | `colonist` |
| `colonist_boots` | feet | anvil | `soldier_chitin` ×2, `ant_fungus` ×2, `copper_bar` ×1 | `defense:2, move_speed_pct:3, hazard_resist:1, pickup_radius:1` | `colonist` |

**Set bonus (`set: colonist`, all 3 worn):**
> *"At home in the dark, kin to the colony."*
> - **+`light_radius +2`**, **+`night_vision +1`** (the galleries light up — no held lantern needed),
> - **full acid immunity** — the soldiers' `acid_burn` stops chipping you entirely (`hazard_resist` no longer
>   needs the salve for *acid*),
> - **+`harvest_yield +1`** on the fungus gardens, and — the friendly-colony payoff — **garden/black/harvester
>   ants treat you as colony** (they don't bristle on their trails; a passive `calm_radius`).
> - **Fantasy realized:** fully kitted, you stride the deep galleries with your own glow, soldiers' acid
>   sparking harmlessly off the chitin, fungus combs yielding bonus harvests, the workers parting around you
>   like one of their own. The colony goes from a dark, guarded warren to a friendly, self-stocking
>   food-and-material farm — and that power carries straight into the **Queen fight** and the deeper ant zones.

**Unlock:** helm + boots recipes **auto** at the anvil (you can grind the set yourself); the **vest** recipe is
**bought from the Myrmecologist** OR **dropped by the `colony_queen`** (mini-boss) — and a **stretch upgrade
re-crafts the vest with `queen_chitin` ×1** for a +1 `defense`/`max_hp` "royal" variant. So the keystone piece
rewards either the merchant loop or the boss fight, with the boss carapace as the deluxe finish.

> Optional matching accessory: `colonist_band` (jeweler — `cut_glowquartz` ×1, `harvester_mandible` ×1,
> `copper_bar` ×1): `light_radius +1`, `harvest_yield +1`. A cheap 4th-slot stretch that deepens the
> underground-forager identity; prune if the 3-piece reads cleaner. (Pairs naturally with `glowquartz_lamp` +
> `colonist_charm` for a full light/forage build.) *(This is the same role as `colonist_charm` above — keep
> one as the set accessory, the other as the open-market trinket, or fold them together on prune.)*

---

## Shop / NPC stock — **the Myrmecologist's Camp** (`myrmecologist`)

A new dedicated vendor camped at the **colony mouth** (the safe surface entry to the galleries) — an
ant-obsessed naturalist who **teaches the colony** (ant lore + the tips/tutorial beat: trails, fungus farming,
formic acid, "the soldiers guard, the workers don't care, the Queen is the prize"), sells the **first light
gear, the fungus-farm seeds, formic-alchemy and survival recipes, and the keystone armor recipe**, **trades in
ant-eggs** (buys your `ant_egg` and sells brood for the player's own ant farm), and **buys your fungus, chitin,
and formic drops high** (a reason to over-harvest the colony). Currency = coins (existing). She is the gate that
teaches "light up and learn the colony before you push to the Queen." This realizes the dedicated ant vendor
implied by `merchants.md` §"NPCs = occupants with `npc{role, intro, shop, tips[]}`" and the progression
"intro Ants (col 0)" beat.

**Sells (buy@myrmecologist):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: glowquartz_lamp` | recipe | 120 | The deep-gallery light upgrade — the headline unlock. |
| `recipe: fungus_garden` | recipe | 160 | Seeds the player's own underground fungus farm. |
| `recipe: formic_etch` | recipe | 100 | The industrial etch/cleaner — opens the gem-cut & fine-brick line. |
| `recipe: formic_salve` | recipe | 90 | Cures/resists `acid_burn` — the survival recipe. |
| `recipe: pheromone_whistle` | recipe | 200 | Colony-command consumable (needs `royal_pheromone` to build). |
| `recipe: colonist_vest` | recipe | 240 | Keystone set piece (alt path to the Queen drop). |
| `glow_lantern` | gear | 70 | Pre-made first light so you can see the galleries immediately. |
| `formic_salve` | consumable | 25 | Pre-made; stock-limited daily (forces gathering too). |
| `fungus_bread` / `fungus_stew` | consumable | 15 / 25 | The fungus pantry on hand before you farm your own. |
| `ant_egg` ✅ | material | 30 | **Brood trade** — buy royal brood to seed your own ant farm (small daily cap). |
| `copper_bar` / `coal` | material | 30 / 15 | Convenience restock of the T2 metal & fuel (small daily cap, markup). |
| `iron_bar` ✅ | material | 70 | The bridge-tier metal you can't yet mine — for the T3 stretch recipes (capped). |
| `stonecutter` / `jeweler` (station) | station | 180 / 240 | Buy-the-station convenience for the chalk/gem-cut line. |

**Buys (sell to vendor — the zone's coin sink + over-harvest incentive):** `ant_fungus`, `mycelium_mat`,
`fungal_spore`, `chalk_stone`, `glow_quartz`, `ant_egg`, `harvester_mandible`, `soldier_chitin`, `seed_husk`,
`formic_dab`, `formic_acid`, `chitin`, `dead_ant` — with a **`harvest_yield`/`sell_pct` premium on fungus &
ant-eggs** and a **`bug_value_pct` premium on chitin & formic** (she pays well for both, reinforcing the
farm-and-fight loop). `royal_jelly_ant`, `queen_chitin`, and `royal_pheromone` sell **highest** (the Queen
flex / boss reward).

---

## "New toys" hook

The Ant Colony is where BugFarmer **goes underground** and the world stops being empty rock — it's a *living,
organized colony you can join*. The new toys are all about *seeing in the dark, farming fungus, and befriending
the ants*: your **first cave light** (`glow_lantern` — bottled glow-mushroom, no fuel), then the brighter
**`glowquartz_lamp`** and **`glow_paint`** breadcrumb markers so the deep galleries open up; the **fungus food
chain** (`fungus_bread` → `fungus_stew` that literally lets you *eat the glow and see in the dark* →
`royal_jelly_tonic`) plus your **own `fungus_garden`** to grow it; **formic-acid alchemy** that turns the
soldiers' own chemistry into an `acid_flask` throwable, an industrial `formic_etch`, and the `formic_salve`
answer to their burn; the **`pheromone_whistle`** that makes the colony *calm and follow you*; and the
**Colonist's Carapace** ant-chitin armor set, whose `light_radius` + acid-immunity + a passive "the colony
treats you as kin" bonus turns the dark, guarded warren into a friendly, self-stocking food-and-material farm.
The capstone is the **`colony_queen`** mini-boss in the royal chamber: beat her and you walk out with
**`royal_jelly_ant`** (the marquee tonic + alchemy reagent), **`queen_chitin`** (the deluxe royal armor finish
+ a trophy for the wall), and **`royal_pheromone`** — the seed of the deeper column-0 ant zones' command toys.

---

## New id ledger

**materials:**
- `ant_fungus` ✅(new) — forage@ant_colony (also spilled by `black_ant`; the unique ant-farmed food-chain input + fungus-leather binder)
- `mycelium_mat` — forage@ant_colony (premium fungus-leather + compost substrate + fungus-garden seed)
- `fungal_spore` — forage@ant_colony (inoculant to seed a fungus garden + bait note + spore-bomb base)
- `chalk_stone` — mine@ant_colony (signature underground building stone; stonecutter line + lime cure)
- `glow_quartz` — mine@ant_colony (self-lighting quartz; glow-lamp + light_radius décor; cuts to cut_glowquartz)
- `seed_husk` — drop, harvester_ant (granary chaff; compost/fertilizer + feed input)
- `harvester_mandible` ✅(new) — drop, harvester_ant (pincer-grip tools + the armor gauntlet)
- `soldier_chitin` ✅(new) — drop, soldier_ant (the ant-chitin light-armor plating)
- `formic_acid` ✅ — concentrated drop, soldier_ant (reuse the existing formic id; the strong tier of the formic ladder)
- `queen_chitin` — rare drop, colony_queen (keystone armor piece / royal trophy & décor)
- `royal_pheromone` — drop, colony_queen (the colony-command reagent — pheromone_whistle)
- `cut_glowquartz` — crafted intermediate (jeweler; gem-cut self-glowing quartz)
- *(reused existing: `ant_egg`, `formic_dab`, `mushroom_glow`, `cave_moss`, `chitin`, `copper_ore`, `coal`. New `dead_*` carcass: `dead_ant`.)*

**species:** (id → primary drop)
- `garden_ant` ✅ → `ant_egg` ✅ (reuse; also `formic_dab` ✅, `dead_ant`)
- `black_ant` → `ant_fungus` ✅(new) (also `formic_dab` ✅, `dead_ant`)
- `harvester_ant` → `harvester_mandible` ✅(new) (also `seed_husk`, `chitin` ✅, `dead_ant`)
- `soldier_ant` → `soldier_chitin` ✅(new) (also `formic_acid` ✅, `chitin` ✅, `dead_ant`)
- `colony_queen` → `royal_jelly_ant` ✅(new) (mini-boss; also `queen_chitin`, `ant_egg` ✅, `royal_pheromone`)

**items:**
- `glow_lantern` — light gear (held), workbench, T2 — light_radius/night_vision (first cave light)
- `glowquartz_lamp` — light gear (held/head), workbench, T2→T3 — light_radius/night_vision (deep-gallery upgrade)
- `glow_paint` — placeable utility, dye_vat, T2 — breadcrumb glow-marker / light_radius aura
- `fungus_bread` — food, cooking_pot, T2 — hp_regen (fungus staple)
- `fungus_stew` — food, cooking_pot, T2 — light_radius/night_vision (eat the glow)
- `royal_jelly_tonic` — food, cooking_pot, T3 — max_hp/hp_regen (Queen-drop meal)
- `fungus_jerky` — preserved food, cooking_pot, T2→T3 — long defense/hp_regen (preservation)
- `formic_etch` — utility reagent, cauldron, T2 — gem-cut/fine-brick etch + cleaner
- `acid_flask` — throwable weapon, cauldron, T2→T3 — AoE acid_burn (anti-soldier)
- `formic_salve` — consumable buff, cauldron, T2 — hazard_resist(acid)/hp_regen (cures acid_burn)
- `pheromone_whistle` — consumable, cauldron, T3 — calm_radius/lure_radius (ants follow; needs royal_pheromone)
- `fungus_garden` — placeable farm/station, workbench, T2→T3 — grows ant_fungus (player's underground farm)
- `colony_compost` — fertilizer, compost_bin, T2 — crop_growth_pct soil boost
- `chalk_block` — structure ×4, stonecutter, T2 — underground wall/path
- `chalk_brick` — structure ×4, stonecutter, T2 — finer gallery brick (acid-mortared)
- `cut_glowquartz` — gem-cut intermediate, jeweler, T2→T3 — polished self-glowing quartz
- `glowquartz_chandelier` — light décor, jeweler, T3 — light_radius aura (colony flex piece)
- `colonist_charm` — accessory, jeweler, T2→T3 — light_radius/harvest_yield/luck (underground-forager trinket)
- `colonist_helm` — armor (head), anvil, T2→T3 — defense/light_radius/night_vision/hazard_resist; set: colonist
- `colonist_vest` — armor (body), loom, T2→T3 — defense/max_hp/hazard_resist/harvest_yield; set: colonist (keystone; royal queen_chitin variant)
- `colonist_boots` — armor (feet), anvil, T2→T3 — defense/move_speed/hazard_resist/pickup_radius; set: colonist
- `colonist_band` — accessory (optional 4th), jeweler, T2→T3 — light_radius/harvest_yield
- `myrmecologist` — NPC ("the Myrmecologist's Camp", ant-lore vendor) — light/fungus/formic supply + ant-egg trade at the colony mouth
