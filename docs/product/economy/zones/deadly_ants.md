# Zone Content Sheet — Deadly Ants (underground col 3 · `deadly_ants`)

> **Grid: outpost `3,3` (HARD) + core `4,3` (EXTRA HARD)** · the **deep endgame ant-warfare colony** ·
> difficulty **HARD → EXTRA HARD** · **tier T4 → T5** (steel → gold → platinum/diamond).
>
> The **fire/acid + elite-chitin + swarm-warfare** capstone underground zone. Past the ore caves and the
> early ant nest, col 3 drops into a **militarized super-colony at war** — branching galleries packed with
> marching **army-ant rivers**, **bullet-ant** sentinels whose sting drops a careless player, **fire ants**
> that turn whole chambers into burning hazard floors, and **soldier ants** plated like living armor. The
> **outpost (3,3)** is the foraging frontier — the colony's columns push *up* toward the surface swamp, so
> the player fights down into it; the **core (4,3)** is the **War-Queen's** brood-fortress, the EXTRA-HARD
> climax. This is where **fire-resist becomes mandatory**, where **acid eats your armor**, where the
> **top ant-derived gear** is forged, and where the rarest recipes are **found, not bought**. Everything is
> gated **T4 → T5** so it lands as the player's *last* gear leap (steel in hand, reaching gold → platinum
> → diamond). Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses the **Ant Colony** ids
> (`ant_hill`/`ant_queen`/`ant_scout`/`ant_worker`/`ant_soldier`, `chitin`, `formic_acid`, `honeydew`,
> `ant_egg`, `dead_ant`) and the prior tier's **`potent_venom`** seed where sensible; new ids are snake_case
> and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat
> vocab + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (the **Late** phase — silver→platinum, top + bug-derived gear,
> Deadly Ants by name); shop seam from [`../merchants.md`](../merchants.md). Zone fiction from
> [`../../zones/ant_colony.md`](../../zones/ant_colony.md) (the same colony, one tier deeper & deadlier).
> Species roster from the world guide: **bullet ants, soldier ants, army ants, fire ants + a War-Queen.**

---

## Species & drops

Five concrete species span the EXTRA-HARD curve — a relentless swarm river, a fire/burn hazard layer, an
armored bruiser, a single-sting killer, and the War-Queen climax — plus the existing `ant_worker`/`ant_scout`
labor as harmless ambient column traffic (reused from the Ant Colony, no new drops). The signature themes are
**fire/burn (`scorched`/`ignited`)**, **corrosive acid (`corroded` — chews armor `defense`)**, and
**overwhelming swarm pressure**. Behaviors slot onto the existing arthropod ecology vocabulary (swarm-river,
anchor-and-guard, telegraphed-lunge, hazard-floor, nest-defend) and the ant colony/brood/nest reuse from
`design_ants_spiders.md` — no new sim primitives required.

| Species (id) | Tier feel | Where | Behavior | Primary drop | Secondary drop(s) |
|---|---|---|---|---|---|
| `army_ant` | **swarm river** (the zone's signature threat) | the great trunk galleries; streams up the outpost columns toward the surface swamp | Moves as a **dense marching river** that never truly stops — a swarm center that floods a gallery, **bivouacs** (balls up) when provoked, then resumes. Individually weak; en masse it's a wall of mandibles that **out-attrits** a careless player. You don't out-DPS the river — you bottleneck it, AoE it, or use a swarm-defense item to break the column. | `army_ant_mandible` (new ✅) | `chitin` ✅ (common), `dead_ant` ✅ |
| `fire_ant` | **fire/burn hazard layer** | scorched chambers, the magma-lit lower core; clusters on `fire_mound` nests | Aggressive cluster-attacker that **bites then sprays formic/venom that IGNITES** — applies `scorched` (a fierce burn DoT). Dying fire ants leave a brief **burning patch** on the floor (`ignited` ground hazard). Mass them and a chamber becomes a **floor of fire** — the zone's mandatory **fire-resist** check. Drawn to and reinforced by `fire_mound`. | `fire_ant_gland` (new ✅) | `formic_acid` ✅, `dead_ant` ✅ |
| `soldier_ant` | **armored bruiser** | chamber mouths, brood-gallery chokes, the War-Queen's hall | Reuse/upgrade of the Ant Colony `ant_soldier` — **huge mandibles, heavily plated** (high `defense`, telegraphed shear-bite with knockback). Anchors and guards a chamber; doesn't chase far but **punishes the choke**. Its back-plate is the best raw armor chitin in the game. | `soldier_ant_plate` (new ✅) | `chitin` ✅, `dead_ant` ✅ |
| `bullet_ant` | **single-sting killer** (elite harasser) | sentry posts along the deep galleries; ambush from wall-nooks | Solitary, fast, **does NOT swarm** — but its sting is the most lethal single hit in the zone: a heavy **`envenomed` + `stagger`** (the "bullet" — brief stun/heavy DoT) that can end a run that ignored armor. Telegraphed rear-up before the lunge; high value, low volume. Bring `iframes`/`dodge` and a cure. | `bullet_ant_stinger` (new ✅) | `venom` ✅, `dead_ant` ✅ |
| `war_queen` | **MINI-BOSS** (EXTRA-HARD, core `4,3`) | the **War-Queen's brood-fortress** at the colony heart | The climax. A bloated, armored matriarch anchored to her **royal_brood** dais. **Continuously hatches adds** — alternating `army_ant` rivers and `fire_ant` clusters — via the existing brood/nest loop until her brood chambers are destroyed; then she descends to fight directly with a **shearing soldier-bite, an AoE acid-spray (`corroded`), and a fire-breath cone (`scorched` + an `ignited` floor)**. The full fire **and** acid **and** swarm test in one fight. | `war_queen_chitin` (new ✅, guaranteed 1–2) | `royal_jelly` ✅-style (new), `queen_venom` (new), `ant_egg` ✅ (×3–6) |

**Drop notes**
- `army_ant_mandible`, `fire_ant_gland`, `soldier_ant_plate`, `bullet_ant_stinger` are the **four species-signature
  drops** the brief requires — each anchors a different gear line (swarm-AoE / fire / armor-plate / venom-crit).
- `war_queen_chitin` is the **best chitin in the game** (gated behind the mini-boss); `queen_venom` is the
  **endgame venom seed** (one tier hotter than the prior zone's `potent_venom`, which is still accepted as an
  input); `royal_jelly` is the rare endgame buff/luck ingredient.
- `chitin` ✅, `formic_acid` ✅, `venom` ✅, `ant_egg` ✅, `honeydew` ✅, `dead_ant` ✅ are **existing ids** — reused.
- `ant_worker` / `ant_scout` (Ant Colony) appear as **ambient labor** (column traffic, carrion foraging) with
  **no new drops** — they make the colony read as alive without padding the loot table.

**Drop → use at a glance**
- `army_ant_mandible` → the **swarm-breaker** AoE weapon + the swarm-defense item (the answer to the river).
- `fire_ant_gland` → **fire weapons/coatings** (`scorched` on-hit) AND the **fire-resist** armor temper.
- `soldier_ant_plate` → the **endgame heavy armor** (the Legionnaire body/shield) — top raw `defense`.
- `bullet_ant_stinger` → the **venom-crit** sidearm + the marquee endgame venom weapon.
- `war_queen_chitin` → the **set keystone** (Fire-Warden helm/crown) + the trophy.
- `queen_venom` → the hottest venom coating/weapon; `royal_jelly` → the endgame luck/regen consumable.

---

## New ingredients & materials

Fire-, acid-, and elite-chitin-themed gatherables you **mine or forage from the deep colony environment**
(not bug drops) plus the two crafted **temper/alloy intermediates** the gear lines need. Source = `mine`,
`forage`, `craft`. Reuses the deep-ore ladder (all ores → platinum, `granite`, `hard_stone`, `crystal`,
`diamond`) which this zone exists to open the **top** of.

| Id | Source (find@deadly_ants) | Cost-pt | Use |
|---|---|---|---|
| `ember_resin` | forage/mine — hardened sap-glass beaded along the scorched magma-lit galleries (glows faintly). Uncommon. | 4 | The zone's **fire-binder**: the burn-coating base, the fire-temper flux, and a glowing fire-décor inlay. Pairs with `fire_ant_gland`. |
| `acid_crystal` | mine — corrosive crystalline deposits etched into the gallery walls where the army rivers' formic acid pooled. Uncommon. | 10 | The **acid line**: an armor-shred throwable, the gem/metal **etch agent** (jeweler/forge cutting), and the acid-temper for piercing weapons. A `crystal`/`quartz`-class node hardened to gem-minor cost. |
| `magma_rock` | mine — heat-fused stone from the deepest core chambers (a `hard_stone`/`granite`-class block, but heat-charged). Common-ish in the core. | 4 | The signature **fire-forge building stone** (stonecutter walls/floors that shrug heat), a **forge flux** that boosts steel→platinum smelts, and the heat-shelter décor. |
| `elite_chitin` | **craft** — `chitin` ×3 + `soldier_ant_plate` ×1 hardened at the **forge** (the "lamellar plate" intermediate). | 16 | The **armor backbone** of the endgame set — refined plate that takes both fire-temper and acid-temper. The chitin equivalent of a `platinum_bar` for armor. |
| `flame_alloy` | **craft** — `steel_bar` ×1 + `ember_resin` ×2 + `fire_ant_gland` ×1 at the **forge**. | 16 | The **fire-tempered metal** for fire weapons + the fire-resist armor cores. The "you've reached the fire tier" bar. Bridges T4 steel → T5. |
| `royal_jelly` | drop/forage — rich brood-secretion harvested from the War-Queen's nursery cells (also a `war_queen` drop). Rare. | 16 | Endgame **luck/regen** consumable base + the set's accessory inlay; the "queen-stuff" payoff. |

> **Why these:** `ember_resin` + `magma_rock` carry the **fire** identity (binder + building stone + flux);
> `acid_crystal` powers the **acid** line (etch, shred, temper) — the two environmental hazards become two
> crafting verbs. `elite_chitin` + `flame_alloy` are the **two endgame intermediates** that gate the top gear
> (you must *process* a soldier plate and a fire gland before the set exists — a deliberate T4→T5 speed bump).
> `royal_jelly` is the rare queen-stuff that keeps an endgame luck/regen answer special. Deep ore
> (`gold_bar`/`platinum_bar`/`diamond`) is reused, not re-introduced — this zone opens the *top* of that ladder.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; everything is **gated T4 → T5**. `unlock`: **craft** (have
station + recipe) / **buy@exterminators_base** / **find@deadly_ants** (rare FIND recipes — a colony theme).

### Weapons — fire & acid & venom (the endgame offense)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `firebrand_blade` (fire endgame weapon) | forge | `flame_alloy` ×2, `fire_ant_gland` ×3, `ember_resin` ×2, `gold_bar` ✅ ×1 | **find@deadly_ants** (recipe in a scorched cache) | `damage_pct +34`, `crit_chance +8`, **on-hit `scorched`** (fierce burn DoT) + leaves a brief `ignited` floor on crit; the marquee fire weapon | T5 |
| `acid_lance` (acid pierce weapon) | forge | `steel_bar` ✅ ×2, `acid_crystal` ×2, `bullet_ant_stinger` ×2 | buy@exterminators_base (recipe) | `damage_pct +28`, `crit_chance +10`, long reach, **on-hit `corroded`** (shreds enemy `defense`) — answers armored soldiers | T4→T5 |
| `mandible_maul` (swarm-breaker AoE) | forge | `flame_alloy` ×1, `army_ant_mandible` ×4, `elite_chitin` ×1 | buy@exterminators_base (recipe) | `damage_pct +24`, **wide cleave AoE** + `knockback +2` — built to **break the `army_ant` river**; weak vs single targets, brutal vs the column | T4→T5 |
| `bullet_sting_dagger` (venom-crit sidearm) | forge | `steel_bar` ✅ ×1, `bullet_ant_stinger` ×3, `queen_venom` ×1 *(or `potent_venom` ✅ ×2)* | **find@deadly_ants** (rare recipe scroll) | `damage_pct +20`, **`crit_chance +14`, `crit_mult +0.4`**, on-hit strong `envenomed` — the high-crit endgame sidearm | T5 |
| `inferno_coating` (weapon coating, consumable) | cauldron | `fire_ant_gland` ×1, `ember_resin` ×1, `resin_glob` ✅ ×1 | auto (cauldron + zone access) | **Coats your current weapon** — adds strong `scorched` on-hit for a duration; upgrades any blade to fire-tier | T4 |

### Defense — fire-resist & swarm survival (the "answer to the zone")

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `fireguard_cloak` (fire-resist endgame armor, back/cloak slot) | forge | `flame_alloy` ×1, `elite_chitin` ×1, `ember_resin` ×3, `cloth` ✅ ×2 | buy@exterminators_base (recipe) | `defense +6`, **`hazard_resist +4` (fire)**, `max_hp +8`; the **mandatory fire-resist** piece that stops `scorched`/`ignited` chip — the answer to the fire ants | T4→T5 |
| `swarm_repeller` (swarm-defense item, throwable/aura consumable) | cauldron | `formic_acid` ✅ ×2, `acid_crystal` ×1, `army_ant_mandible` ×1, `ember_resin` ×1 | craft / buy@exterminators_base | Throws a **smoke-and-acid burst**: `army_ant` columns **scatter/bivouac** and won't re-form for a duration — breaks the river so you can pass or focus the Queen | T4 |
| `acid_balm` (cure + temper consumable) | cauldron | `aloe_leaf` ✅ ×2, `acid_crystal` ×1, `royal_jelly` ×1 | craft / buy@exterminators_base | **Cures `corroded` + `envenomed`** + short `hazard_resist` (acid/venom) — the answer to bullet-ant stings & soldier acid; the survival staple | T4→T5 |

> **Supply logic:** `fire_ant_gland` is the bottleneck on **fire offense AND fire-resist** (you fight fire
> ants to both burn and not-burn — a clean tension). `army_ant_mandible` gates the **swarm answers** (the maul
> + the repeller). `bullet_ant_stinger` + `queen_venom` gate the **crit/venom** spikes. The two **find@**
> recipes (`firebrand_blade`, `bullet_sting_dagger`) are the rare colony-cache rewards. `aloe_leaf` ✅ (from
> Scorpion Rocks) + `formic_acid` ✅ keep the **survival** answers always-craftable so a prepared player is
> never locked out of staying alive — only of the spicy endgame weapons.

---

## Signature gear — the **Fire-Warden's Legion** (T4 → T5 bonus set)

A 3-piece (+ optional 4th) **fire-warden / legionnaire** plate set: lamellar `elite_chitin` over a
`flame_alloy` core, soldier-plate pauldrons, and a War-Queen-chitin crown. Theme = **the exterminator who
marches *into* the burning swarm and doesn't flinch** — the militarized counterpart to the Scorpion Rocks
Prospector's Rig. This is a **pure-combat / hazard-tank** set, so its signature stats are
**`defense` + `hazard_resist` (fire) + `damage_pct` + `thorns` + `knockback`** with high `max_hp`. Built at
the **forge** (the fire-temper) + an **anvil** finish + a **jeweler** crown inlay — a mixed-station endgame
set. T4→T5 (steel/gold reaching platinum/diamond + the elite ant drops).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` | Unlock |
|---|---|---|---|---|---|---|
| `firewarden_crown` | head | jeweler | `war_queen_chitin` ×1, `flame_alloy` ×1, `gold_bar` ✅ ×1, `royal_jelly` ×1 | `defense:4, hazard_resist:3, damage_pct:6, light_radius:1` | `firewarden` | **find@deadly_ants** (rare — War-Queen cache) |
| `firewarden_plate` | body | forge | `elite_chitin` ×2, `flame_alloy` ×2, `soldier_ant_plate` ×2, `platinum_bar` ✅ ×1 | `defense:9, max_hp:14, hazard_resist:3, thorns:3` | `firewarden` | buy@exterminators_base (recipe) **or** drop@war_queen |
| `firewarden_greaves` | feet | anvil | `elite_chitin` ×1, `flame_alloy` ×1, `soldier_ant_plate` ×1, `steel_bar` ✅ ×2 | `defense:5, hazard_resist:2, knockback:1, move_speed_pct:2` | `firewarden` | craft (auto at forge+anvil) |
| `firewarden_pauldrons` *(optional 4th)* | shoulders | forge | `soldier_ant_plate` ×2, `elite_chitin` ×1, `ember_resin` ×2 | `defense:4, thorns:2, hazard_resist:1` | `firewarden` | **find@deadly_ants** (rare) |

**Set bonus (`set: firewarden`, 3/3 — crown + plate + greaves):**
> *"March into the fire. Let the swarm break on you."*
> - **+`hazard_resist +4` (fire)** → **full fire immunity**: `scorched`/`ignited` floors stop chipping your HP
>   entirely (no `fireguard_cloak`/coating needed for *fire* once the set is complete),
> - **+`thorns +5`, `damage_pct +8`, `knockback +1`** — the marching `army_ant` river **damages itself on your
>   plate** (thorns shred the swarm that surrounds you) while you cleave through it,
> - **+`max_hp +10`** to soak the bullet-ant spikes.
> - **4/4 (with pauldrons):** add **`life_on_hit +3`** and the thorns reflect also applies a short `ignited`
>   to anything that touches you — you become a **walking burning wall** the swarm dies against.
> - **Fantasy realized:** fully kitted, you wade into a fire-floored gallery as an `army_ant` river floods
>   around you — flames don't touch you, the swarm shreds itself on your thorns, your `firebrand_blade` leaves
>   `ignited` trails, and you walk to the War-Queen's dais untouched. The deadly gauntlet becomes **your**
>   colony to harvest. That power spike is the endgame reward — the top of the gear ladder.

**Unlock spread (a couple marked `find` per the brief):** the **crown** and the optional **pauldrons** are
**rare finds** (War-Queen / deep caches) — the keystone flex pieces; the **plate** is bought OR drops from the
War-Queen (dual path); the **greaves** auto-unlock at forge+anvil so you can always grind the base set. Pairs
naturally with `fireguard_cloak` (back slot), `firebrand_blade`, and `acid_balm` for a full fire-tank build.

---

## Shop / NPC stock — **the Exterminator's Base** (`exterminators_base`) + the **Bounty Board**

The endgame vendor: a hardened **Exterminator** dug into a **fortified forward camp** at the safe edge of the
outpost (`3,3`) — sandbags, fire-screens, a forge under guard. He's seen the colony swallow lesser adventurers;
he **sells the fire/acid survival kit and the keystone recipes**, sells **deep bars you can't yet smelt at a
markup**, and **buys ant drops high** (a reason to over-cull the swarm). Bolted to his camp is the
**Bounty Board** — a **task/contract** seam (kill-N-fire-ants, break-a-river, bring-the-War-Queen-chitin) that
pays coins + rare recipe scrolls, the endgame coin source and the hook that sends you deeper into `4,3`.

**Sells (buy@exterminators_base):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: fireguard_cloak` | recipe | 480 | The **mandatory fire-resist** piece — the gate recipe. |
| `recipe: acid_lance` | recipe | 520 | Armor-shred pierce weapon (answers soldiers). |
| `recipe: mandible_maul` | recipe | 560 | The swarm-breaker AoE. |
| `recipe: firewarden_plate` | recipe | 700 | Set keystone (alt path to the War-Queen drop). |
| `acid_balm` | consumable | 60 | Pre-made cure (corroded/envenomed); daily stock cap (forces gathering). |
| `inferno_coating` / `swarm_repeller` | consumable | 50 / 70 | Fire offense + swarm answer on hand before you craft your own. |
| `fireguard_cloak` | gear | 260 | Pre-made fire-resist so you can survive the first push into the fire chambers. |
| `gold_bar` ✅ / `platinum_bar` ✅ | material | 150 / 320 | The deep bars you can't yet smelt — for the set's stretch inputs (small daily cap, markup). |
| `forge` / `jeweler` (station) | station | 400 / 360 | Buy-the-station convenience for the endgame lines. |

**Bounty Board (task → reward):**

| Bounty | Reward |
|---|---|
| Cull N `fire_ant` / break an `army_ant` river with a `swarm_repeller` | coins + `recipe: inferno_coating` / `swarm_repeller` stock |
| Bring `soldier_ant_plate` ×N | coins + a `firewarden_greaves` recipe nudge / discount |
| **Slay the `war_queen`** (bring `war_queen_chitin`) | big coins + the **`firebrand_blade` find-recipe** unlock + `royal_jelly` |

**Buys (sell to vendor — the endgame coin sink + over-cull incentive):** `army_ant_mandible`, `fire_ant_gland`,
`soldier_ant_plate`, `bullet_ant_stinger`, `chitin`, `formic_acid`, `venom`, `ember_resin`, `acid_crystal`,
`magma_rock`, `ant_egg` — with a **`bug_value_pct` premium on the elite ant drops**. `war_queen_chitin`,
`queen_venom`, and `royal_jelly` sell **highest** (the boss flex).

---

## "New toys" hook

Deadly Ants is where BugFarmer's **combat goes full warfare** and the hazards go *lethal in two directions at
once*. The new toys are all about **surviving a burning swarm and turning it into your harvest**: a
**`fireguard_cloak`** + **`acid_balm`** that finally let you stand in a fire-floored, acid-spraying gallery; a
**`swarm_repeller`** that breaks the unstoppable `army_ant` river; a **`mandible_maul`** that cleaves the column,
an **`acid_lance`** that melts the soldiers' armor, a **`bullet_sting_dagger`** that crits like the bullet ant's
own sting, and the marquee **`firebrand_blade`** (a rare colony-cache *find*) that leaves trails of fire. The
capstone is the **Fire-Warden's Legion** set — fire immunity + `thorns` that shred the swarm that surrounds you
+ a 4-piece "walking burning wall" — the **top of the gear ladder**. The whole loop is gated behind the two
new intermediates (`elite_chitin`, `flame_alloy`), so reaching the fire tier *feels* earned. Beat the
**War-Queen** in the EXTRA-HARD core (`4,3`) and you walk out with **`war_queen_chitin`** (the best chitin in
the game), **`queen_venom`** (the hottest venom), and **`royal_jelly`** — plus the Exterminator's **Bounty
Board** keeps paying you to march back in. The deadly endgame gauntlet becomes a **living, self-stocking
arsenal** — exactly the last "I'm fully kitted" power fantasy the progression curve has been building toward.

---

## New id ledger

**materials:**
- `ember_resin` — forage/mine@deadly_ants (fire-binder; burn-coating base, fire-temper flux, fire décor)
- `acid_crystal` — mine@deadly_ants (acid line; etch agent, armor-shred throwable, acid-temper)
- `magma_rock` — mine@deadly_ants (fire-forge building stone; forge flux; heat-shelter décor)
- `elite_chitin` — craft@forge (chitin ×3 + soldier_ant_plate ×1; the endgame armor-plate intermediate)
- `flame_alloy` — craft@forge (steel_bar + ember_resin ×2 + fire_ant_gland; fire-tempered metal, T4→T5 bridge)
- `royal_jelly` — drop/forage@deadly_ants (queen-stuff; endgame luck/regen + set accessory inlay)
- `army_ant_mandible` — drop, army_ant (swarm-breaker AoE weapon + swarm-defense item)
- `fire_ant_gland` — drop, fire_ant (fire weapons/coatings AND fire-resist armor temper)
- `soldier_ant_plate` — drop, soldier_ant (endgame heavy armor; top raw defense; → elite_chitin)
- `bullet_ant_stinger` — drop, bullet_ant (venom-crit sidearm + acid_lance)
- `war_queen_chitin` — guaranteed drop, war_queen (best chitin; set keystone crown + trophy)
- `queen_venom` — drop, war_queen (hottest endgame venom; one tier above potent_venom ✅)
- *(reused ✅: `chitin`, `formic_acid`, `venom`, `ant_egg`, `honeydew`, `dead_ant`, `potent_venom`, `aloe_leaf`,
  `resin_glob`, `cloth`, deep bars `steel_bar`/`gold_bar`/`platinum_bar`, `granite`/`hard_stone`/`crystal`/`diamond`)*

**species:** (id → primary drop)
- `army_ant` → `army_ant_mandible` (also `chitin` ✅, `dead_ant` ✅) — the swarm river
- `fire_ant` → `fire_ant_gland` (also `formic_acid` ✅, `dead_ant` ✅) — fire/burn hazard layer
- `soldier_ant` → `soldier_ant_plate` (also `chitin` ✅, `dead_ant` ✅) — armored bruiser
- `bullet_ant` → `bullet_ant_stinger` (also `venom` ✅, `dead_ant` ✅) — single-sting killer
- `war_queen` → `war_queen_chitin` (mini-boss; also `queen_venom`, `royal_jelly`, `ant_egg` ✅)
- *(ambient, reused ✅, no new drops: `ant_worker`, `ant_scout` — column traffic / carrion labor)*

**items:**
- `firebrand_blade` — weapon (fire endgame), forge, T5 — damage_pct/crit + on-hit scorched + ignited crit-floor; **find**
- `acid_lance` — weapon (acid pierce), forge, T4→T5 — damage_pct/crit/reach + on-hit corroded (armor-shred)
- `mandible_maul` — weapon (swarm-breaker AoE), forge, T4→T5 — cleave AoE + knockback (breaks army_ant river)
- `bullet_sting_dagger` — weapon (venom-crit sidearm), forge, T5 — crit_chance/crit_mult + envenomed; **find**
- `inferno_coating` — weapon coating consumable, cauldron, T4 — adds strong scorched on-hit
- `fireguard_cloak` — armor (back/cloak, fire-resist), forge, T4→T5 — defense/hazard_resist(fire)/max_hp
- `swarm_repeller` — swarm-defense throwable, cauldron, T4 — scatters/bivouacs army_ant columns
- `acid_balm` — cure consumable, cauldron, T4→T5 — cures corroded/envenomed + hazard_resist(acid/venom)
- `firewarden_crown` — armor (head), jeweler, T5 — defense/hazard_resist/damage_pct; set: firewarden; **find** (keystone)
- `firewarden_plate` — armor (body), forge, T4→T5 — defense/max_hp/hazard_resist/thorns; set: firewarden (buy or war_queen drop)
- `firewarden_greaves` — armor (feet), anvil, T4→T5 — defense/hazard_resist/knockback/move_speed; set: firewarden (auto)
- `firewarden_pauldrons` — armor (shoulders, optional 4th), forge, T5 — defense/thorns/hazard_resist; set: firewarden; **find**
- `exterminators_base` — NPC ("the Exterminator's Base") — endgame fire/acid survival + recipe shop + **Bounty Board** (task seam) at the outpost edge
