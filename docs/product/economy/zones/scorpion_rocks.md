# Zone Content Sheet — Scorpion Rocks

> **Grid (1,2)** · rocky outcrops & sun-baked clay east of the river · **difficulty HARD** · **tier T3
> (iron era, reaching toward T4)**
>
> The **desert/rock + mining-intro + potent-venom** zone. Past the Wasp Thicket the land breaks open into
> shadeless stone benches, gravel washes, and shattered outcrops baking in the heat — the first place the
> player **mines for real** and the first place the **venom can outright kill** a careless run. This is where
> the **Miner's camp** sits (mining tips, the first pickaxe *upgrades*, mining gear & recipes), where
> **sandstone, quartz/gem-luck, and heat/hazard survival** debut, and where **scorpion venom** — far stronger
> than the Thicket's wasp venom — anchors a new venom-weapon tier. Everything is gated **T3** so it lands once
> the player has iron tools and is reaching for steel.
>
> **Design intent (pacing, per `../README.md` + `../progression.md` §"Mid"):** this zone teaches *the mining
> loop and heat/venom preparation*. You don't brute-force the rocks — you bring a heat-resist kit, an
> upgraded pickaxe with `ore_fortune`/`vein_sense`, an anti-venom answer, and **then** the deep veins and the
> scorpion dens become a generous ore-and-gem farm. Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat
> vocab + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T3 "Mid" / mining begins); shop seam from
> [`../merchants.md`](../merchants.md) (the **Blacksmith = miner-themed**, "unlocks mid, near Scorpion Rocks"
> — realized here as the **Miner's Camp**). World-guide species: scorpions, ticks, harvestmen, vinegaroons.

---

## Species & drops

Five concrete species span the difficulty curve — a swarming nuisance, two ground harassers, a heavy venom
threat, and a den mini-boss. Behaviors slot into the existing arthropod ecology vocabulary (anchor-and-patrol,
flank, flee, swarm) without needing new sim primitives. The signature theme is **potent venom** (`scorpion_venom`
is the strongest venom material in the game so far) plus **rock/heat hazards**.

| Species (id) | Tier feel | Behavior | Primary drop | Secondary drop(s) |
|---|---|---|---|---|
| `bark_scorpion` | core threat | Den-anchored under rock slabs. Patrols a radius around its `scorpion_den`; **claws to grapple, then stings** — the sting applies a strong `envenomed` debuff (a heavier DoT than the Thicket's `poisoned`). Low-light hunter (more aggressive at night / in shade). Fast skitter, telegraphed tail-strike. | `scorpion_venom` ✅(new) | `scorpion_claw` (uncommon), `dead_scorpion` (new ✅-style) |
| `desert_tick` | swarm / parasite | Clusters in gravel & on the den approaches; **latches** onto the player (a slow `bleed`/HP-leech tick while attached) and is annoying to shake. Fragile, low value individually, but a *cluster* catch. Drains slowly — you out-prepare it, you don't out-twitch it. | `tick_sac` ✅(new) | `dead_tick` (new), `fiber` ✅ (matted hair/web it nests in) |
| `harvestman` | ground harasser | Long-legged daddy-longlegs that **stilts over the rocks**, flanks, and **flees** when struck (high dodge, no venom). Skitters between shade pockets. Worth chasing for its legs (a springy cordage material) and as light ecology pressure on the zone's flora. | `harvestman_leg` ✅(new) | `chitin` ✅ (common), `dead_centipede` ✅ (reuse — leggy ground bug) |
| `vinegaroon` | solitary bruiser | Whip-scorpion anchored to crevices; **solitary, does NOT swarm** but tanky and heavy-hitting. **Sprays defensive acid** (`acetic`/corrosion debuff — chews armor `defense` briefly) instead of venom. Slow, telegraphs the spray; punishes standing in front of it. | `vinegaroon_acid` ✅(new) | `chitin` ✅, `dead_scorpion` (new) |
| `den_matron` | **mini-boss** (scorpion brood) | The **signature fight** — a bloated brood-mother scorpion anchored to the **great den** at the zone's heart. Stationary-ish; **continuously spawns `bark_scorpion` adds** from the den until it's destroyed, then descends to fight directly with a heavy `envenomed` sting + an AoE **venom-mist** ground hazard. | `potent_venom` (guaranteed, 1–2) | `scorpion_den` ✅ (×3–5), `scorpion_brood` (×2–4), `matron_carapace` (rare décor/trophy) |

**Drop notes**
- `scorpion_venom` is the **strong venom material** (off `bark_scorpion`); `potent_venom` is its **rare/upgraded**
  form, gated behind the `den_matron` — a clean two-tier venom supply mirroring the Thicket's `venom_sac` →
  `royal_venom`, but a tier hotter. (`scorpion_venom` is *stronger* than the Thicket's `venom_sac`; `potent_venom`
  is the T3→T4 venom seed for the next zone.)
- `tick_sac`, `harvestman_leg`, `vinegaroon_acid` are each species-signature crafting drops (see uses below).
- `chitin`, `fiber`, `dead_centipede` are **existing ids** — reused. `dead_scorpion` / `dead_tick` are the
  carcass drops in the existing `dead_*` family.
- `scorpion_den` (looted nest chunk) + `scorpion_brood` (larvae) + `matron_carapace` (rare trophy) round out the
  mini-boss table — the "I cleared the rocks" flex + venom/armor inputs.

**Drop → use at a glance**
- `scorpion_venom` → the strong venom weapons/coatings (this zone's offense).
- `scorpion_claw` → pincer-tipped tools/weapons + the miner set's grip pieces.
- `tick_sac` → a HP-leech/lifesteal coating + bait; the parasite-themed consumable.
- `harvestman_leg` → springy cordage → the miner harness/climbing gear (`fall_resist`, reach).
- `vinegaroon_acid` → an **etch/cutting agent** for the stonecutter & jeweler (gem-cutting), and an armor-shredding throwable.
- `potent_venom` → the marquee venom weapon + a forward hook into the next zone's tier.

---

## New ingredients & materials

Rock-, sand-, and mineral-themed gatherables you **mine or forage from the environment** (not bug drops). They
give the zone non-combat reasons to explore and feed the recipe list. Source = `mine` (break a node/vein),
`forage` (pick). Most are cost-point 1 (raw stone/sand class) unless noted.

| Id | Source (find@scorpion_rocks) | Cost-pt | Use |
|---|---|---|---|
| `sandstone` | mine — the layered rock benches & cliff faces (the zone's bedrock). Common. | 1 | The signature building stone: stonecutter blocks/paths/walls, the heat-shelter décor, and a smelting flux. Cuts at the **stonecutter**. |
| `desert_sand` | forage/mine — the gravel washes & dune pockets (a coarser, richer `sand`). Common. | 1 | A richer `sand` for `glass` & the furnace; abrasive grit for polishing gems; mortar for `sandstone` brick. |
| `rock_salt` | mine — pale evaporite veins in the low washes. Common. | 1 | **Preservation** (cures bug-meat/jerky for long buffs), an etch/desiccant agent, and an anti-tick repellent base. |
| `gem_geode` | mine — cracked-open nodules in the deep veins (yields a raw `crystal`/`quartz` inside). Uncommon. | 2 | Cracked at the **stonecutter/jeweler** for `quartz`/`crystal`; the zone's `gem_luck` payoff node — the "should I bring a fortune pick" tease. |
| `iron_ore` ✅ | mine — the primary ore benches (reuse existing `iron_ore`; this is the zone that **introduces real mining of it**). | — | Reuse — smelt → `iron_bar` at the furnace; the T3 metal supply this zone exists to open up. |
| `coal` ✅ | mine — dark seams threaded through the `sandstone`. | — | Reuse — fuel for furnace/forge (and the T4 steel reach); the heat economy of the rocks. |
| `aloe_leaf` | forage — hardy succulents tucked in shaded crevices. Uncommon. | 1 | The desert **soothe/heal** flora: feeds the heat-salve and the venom **antivenom** (counter-irritant), parallel to the Thicket's `nettle_leaf`/`yarrow`. |
| `dust_lichen` | forage — crusty lichen on north-shade rock. Common. | 1 | A cheap dye/binder + a light water-purifier note for the canteen consumable; minor décor moss. |

> **Why these:** `sandstone` + `desert_sand` carry the desert *building/glass* identity; `rock_salt` powers
> preservation + the anti-tick answer; `gem_geode` is the dedicated `gem_luck` node so the new pickaxe stats
> have something to *mine for*; `iron_ore`/`coal` are the reused ores this zone exists to open; `aloe_leaf` +
> `dust_lichen` keep the **survival** answers (heat-salve, antivenom, canteen) cheap and always craftable so a
> careful player is never locked out of staying alive — only of the spicy venom weapons.

---

## Recipes debuting here

Eight recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; everything is **gated T3** (a couple reach a `steel_bar`/gem
as a stretch toward T4). `unlock`: **craft** (have station + recipe) / **buy@miners_camp** / **find@scorpion_rocks**.

### Mining tools & accessories (the zone's headline — pickaxe *upgrades*)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `iron_pickaxe` | anvil | `iron_bar` ×3, `plank` ×2, `harvestman_leg` ×2 | buy@miners_camp (recipe) / craft | `mining_speed_pct +25`, `light_radius +1`; the **first real pickaxe upgrade** (breaks T3 ore benches) | T3 |
| `fortune_pick` | anvil | `iron_bar` ×3, `quartz` ×2, `scorpion_claw` ×2, `coal` ×2 | find@scorpion_rocks (recipe in the deep den) | `mining_speed_pct +15`, **`ore_fortune +2`, `gem_luck +2`** — the "mine for gems" pick | T3 |
| `prospector_lamp` (head/held light) | workbench | `iron_bar` ×1, `glass` ×2, `coal` ×1 | craft / buy@miners_camp | `light_radius +3`, `night_vision +1`, **`vein_sense +1`** (highlights nearby ore in the dark) | T3 |
| `miners_charm` (accessory) | jeweler | `quartz` ×2, `crystal` ×1, `gem_geode` ×1, `copper_bar` ×1 | buy@miners_camp (recipe) | `ore_fortune +1`, `gem_luck +2`, `luck +1` — the gem-luck trinket | T3 |

### Weapons — potent venom (the strong-venom tier)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `scorpion_pick` (war-pick weapon) | forge | `iron_bar` ×2, `scorpion_claw` ×3, `scorpion_venom` ×2 | find@scorpion_rocks (recipe scroll) | `damage_pct +20`, `crit_chance +6`, **on-hit `envenomed`** (strong DoT); doubles as a light digging tool | T3 |
| `venom_lash` (whip, vinegaroon-themed) | forge | `iron_bar` ×2, `harvestman_leg` ×3, `potent_venom` ×1 | buy@miners_camp (recipe) | `damage_pct +24`, `knockback +1`, long reach (anti-tick-swarm spacing), strong `envenomed` on-hit | T3→T4 (needs `potent_venom`) |
| `venom_oil` (weapon coating, consumable) | cauldron | `scorpion_venom` ×1, `resin_glob` ✅ ×1, `aloe_leaf` ×1 | auto (once cauldron + zone access) | **Coats your current weapon** — adds strong `envenomed` on-hit for a duration; upgrades any blade to scorpion-tier venom | T3 |

### Survival — hazard / heat / venom answers (the "answer to the zone")

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `antivenom` | cauldron | `aloe_leaf` ×2, `rock_salt` ×1, `scorpion_venom` ×1 | buy@miners_camp (recipe) | **Cures `envenomed`** + short `hazard_resist` (resists new venom). The answer to the scorpions. | T3 |
| `heat_salve` (consumable buff) | cauldron | `aloe_leaf` ×2, `dust_lichen` ×1, `yarrow` ✅ ×1 | craft | Short **`hazard_resist +2` (heat)** + `hp_regen +1` — lets you work the shadeless benches without chip damage. | T3 |
| `desert_canteen` (utility consumable) | workbench | `glass` ×1, `dust_lichen` ×1, `desert_sand` ×1 | craft / buy@miners_camp | Refillable — a sustained `hazard_resist` (heat/dehydration) tick while exploring; a coin-sink staple | T3 |
| `tick_repellent` (consumable) | cauldron | `rock_salt` ×2, `dust_lichen` ×1, `tick_sac` ×1 | craft | Short aura: `desert_tick` won't latch (counters the leech) — the parasite answer | T3 |

### Gem-cut & stone décor / structure (stonecutter / jeweler — the gem payoff)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `cut_quartz` | jeweler | `quartz` ×2 + `vinegaroon_acid` ×1 (etch) | craft | **Gem-cut** intermediate — polished gem for jewelry/inlay (the `vinegaroon_acid` etch is the gem-cutting agent) | T3 |
| `quartz_pendant` (accessory) | jeweler | `cut_quartz` ×1, `silver_bar` ✅ ×1, `scorpion_claw` ×1 | craft / find | `crit_chance +6`, `gem_luck +1`, `rare_bug_luck +1` — a T3→T5 bridge accessory (needs `silver_bar`) | T3→T5 |
| `sandstone_block` ×4 | stonecutter | `sandstone` ×4 | craft | structure / desert wall & path material | T3 |
| `sandstone_brick` ×4 | stonecutter | `sandstone` ×2 + `desert_sand` ×2 | craft | finer desert brick (mortared) — building line | T3 |
| `geode_lamp` | jeweler | `gem_geode` ×1, `iron_bar` ×1, `coal` ×1 | craft | light décor — a glowing cracked geode (`light_radius` aura), the rock-zone flex piece | T3 |
| `desert_jerky` (food) | cooking_pot | `dead_scorpion` ×1 *(or any `dead_*` bug-meat)* + `rock_salt` ×1 + `sage` ✅ ×1 | craft | salt-cured — long-duration `max_hp +5` / `hp_regen +1` buff (preservation payoff) | T3 |

> **Supply logic:** `scorpion_venom` (the strong drop) is the bottleneck on offense; `aloe_leaf` / `rock_salt`
> / `dust_lichen` (common gatherables) keep the **survival** answers (antivenom, heat-salve, canteen,
> repellent) cheap and always craftable. `potent_venom` (mini-boss) gates the spicy `venom_lash` and is held in
> reserve as the **forward hook** to the next zone's hotter venom tier. The pickaxe line (`iron_pickaxe` →
> `fortune_pick`) is the zone's progression spine: the first opens T3 ore, the second turns the deep veins into
> a gem farm.

---

## Signature gear — the **Prospector's Rig** (T3 bonus set)

A 3-piece miner/desert outfit: iron-studded sandstone-leather plating with a scorpion-claw grip and a brimmed,
lamped helm. Theme = **the deep-rock prospector who shrugs off heat and reads the veins**. This is a *mining
+ survival* set (not a pure-combat set like the Thicket's Thornweave), so its signature stats are
**`mining_speed_pct` + `hazard_resist` + `gem_luck` + `light_radius`** with solid `defense` to survive the
scorpions. Built at **anvil** (studs/plate) + **loom** (the desert-leather/harness weave) + a **jeweler** inlay
— a mixed-station set that shows off the zone's mining identity. Pure T3 (drops + iron).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `prospector_helm` | head | anvil | `iron_bar` ×2, `sandstone` ×2, `glass` ×1, `coal` ×1 | `defense:3, light_radius:2, hazard_resist:1, vein_sense:1` (built-in lamp) | `prospector` |
| `prospector_vest` | body | loom | `iron_bar` ×2, `harvestman_leg` ×3, `chitin` ×2, `sandstone` ×2 | `defense:5, max_hp:6, hazard_resist:2, mining_speed_pct:5` | `prospector` |
| `prospector_boots` | feet | anvil | `iron_bar` ×1, `harvestman_leg` ×2, `sandstone` ×2 | `defense:3, move_speed_pct:4, fall_resist:1, hazard_resist:1` | `prospector` |

**Set bonus (`set: prospector`, all 3 worn):**
> *"Read the rock, beat the heat."*
> - **+`mining_speed_pct +20`**, **+`ore_fortune +1`**, **+`gem_luck +2`** (mining payoff),
> - **full heat immunity** — the shadeless benches stop chipping your HP entirely (`hazard_resist` no longer
>   needs the salve/canteen for *heat*),
> - **+`vein_sense +1`** (stacks with the lamp — ore glows through the rock at range).
> - **Fantasy realized:** fully kitted, you stand in the noon sun on a deep vein, ore lit up through the stone,
>   pickaxe ripping out `ore_fortune` + `gem_luck` bonus drops while the scorpions' stings barely scratch your
>   plate. The rocks go from a lethal slog to a generous, self-stocking **ore-and-gem mine**. That power spike
>   is the reward for clearing the zone — and it carries straight into the next, deeper zone's mining.

**Unlock:** helm + boots recipes **auto** at the anvil (you can grind the set yourself); the **vest** recipe is
**bought from the Miner's Camp** OR **dropped by the `den_matron`** (mini-boss) — so the keystone piece rewards
either the merchant loop or the boss fight.

> Optional matching accessory: `prospector_band` (jeweler — `cut_quartz` ×1, `iron_bar` ×1, `scorpion_claw` ×2):
> `mining_speed_pct +5`, `gem_luck +1`. A cheap 4th-slot stretch that deepens the mining identity; prune if the
> 3-piece reads cleaner. (Pairs naturally with `fortune_pick` + `miners_charm` for a full ore-fortune build.)

---

## Shop / NPC stock — **the Miner's Camp** (`miners_camp`)

The miner-themed vendor camped at the **cliff entry / safe edge** of the rocks (this realizes the
`merchants.md` **Blacksmith — miner-themed**, "unlocks mid, near Scorpion Rocks"). A weathered prospector who
runs the camp: he **teaches mining** (the tips/tutorial beat), sells the **first pickaxe upgrades, mining gear,
heat survival, and the keystone recipes**, sells **ore/bars you can't mine yet at a markup**, and **buys your
ore & venom high** (a reason to over-mine). Currency = coins (existing). He is the gate that teaches "kit up
before you push into the deep veins."

**Sells (buy@miners_camp):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: iron_pickaxe` | recipe | 180 | The first pickaxe upgrade — the headline unlock. |
| `recipe: miners_charm` | recipe | 220 | The `gem_luck` trinket. |
| `recipe: antivenom` | recipe | 160 | Cures `envenomed` — the survival recipe. |
| `recipe: venom_lash` | recipe | 350 | Marquee venom weapon (needs `potent_venom` to build). |
| `recipe: prospector_vest` | recipe | 420 | Keystone set piece (alt path to the boss drop). |
| `antivenom` | consumable | 30 | Pre-made; stock-limited daily (forces gathering too). |
| `heat_salve` / `desert_canteen` | consumable | 25 / 60 | Heat survival on hand before you craft your own. |
| `prospector_lamp` | gear | 110 | Pre-made light/`vein_sense` so you can see the veins immediately. |
| `iron_bar` / `coal` | material | 35 / 15 | Convenience restock of the T3 metal & fuel (small daily cap, markup). |
| `silver_bar` ✅ | material | 90 | The bridge-tier metal you can't yet mine — for the `quartz_pendant` stretch (capped). |
| `stonecutter` / `jeweler` (station) | station | 200 / 260 | Buy-the-station convenience for the gem-cut line. |

**Buys (sell to vendor — the zone's coin sink + over-mine incentive):** `iron_ore`, `coal`, `sandstone`,
`gem_geode`, `quartz`, `crystal`, `scorpion_venom`, `scorpion_claw`, `tick_sac`, `harvestman_leg`,
`vinegaroon_acid`, `scorpion_brood` — with an **`ore_value_pct` premium on ore/gems** and a **`bug_value_pct`
premium on venom** (he pays well for both, reinforcing the mine-and-fight loop). `potent_venom` and
`matron_carapace` sell highest (the boss flex).

---

## "New toys" hook

Scorpion Rocks is where BugFarmer's **mining loop turns on** and the venom gets *lethal*. The new toys are all
about *digging and surviving the rocks*: your **first real pickaxe upgrade** (`iron_pickaxe`) that finally
chews through T3 ore, then the **`fortune_pick`** that makes the deep veins rain `ore_fortune` + `gem_luck`
bonus drops, a **`prospector_lamp`** with `vein_sense` that lights ore up through the dark, a **scorpion war-pick**
and **venom whip** that turn the scorpions' own venom into a weapon, and the survival kit — **antivenom**,
**heat-salve**, **desert canteen**, **tick repellent** — that takes the shadeless, venomous rocks from "this
kills careless runs" to "this is my ore farm." The capstone is the **Prospector's Rig** set, whose
`mining_speed_pct` + heat-immunity + `gem_luck` + `vein_sense` bonus lets you stand on a deep vein in the noon
sun, ore glowing through the stone, ripping out gems while scorpion stings barely scratch your plate. Beat the
`den_matron` and you walk out with **`potent_venom`** — the seed of the next zone's hotter weapons — plus the
`matron_carapace` trophy for the wall.

---

## New id ledger

**materials:**
- `sandstone` — mine@scorpion_rocks (signature building stone; stonecutter line + flux)
- `desert_sand` — forage/mine@scorpion_rocks (richer sand; glass/furnace, polishing grit, mortar)
- `rock_salt` — mine@scorpion_rocks (preservation/jerky, etch/desiccant, anti-tick base)
- `gem_geode` — mine@scorpion_rocks (cracks to quartz/crystal; the `gem_luck` node)
- `aloe_leaf` — forage@scorpion_rocks (desert soothe flora; antivenom + heat-salve)
- `dust_lichen` — forage@scorpion_rocks (cheap dye/binder; canteen/heat-salve note)
- `scorpion_claw` — uncommon drop, bark_scorpion (pincer tools/weapons + miner grip)
- `vinegaroon_acid` — drop, vinegaroon (gem-cut etch agent + armor-shred throwable)
- `potent_venom` — guaranteed drop, den_matron (rare/upgraded strong venom; forward hook to next zone)
- `scorpion_brood` — drop, den_matron (larvae; venom/armor input)
- `matron_carapace` — rare décor/trophy drop, den_matron
- `cut_quartz` — crafted intermediate (jeweler; gem-cut polished quartz)

**species:** (id → primary drop)
- `bark_scorpion` → `scorpion_venom` (also `scorpion_claw`, `dead_scorpion`)
- `desert_tick` → `tick_sac` (also `dead_tick`, `fiber` ✅)
- `harvestman` → `harvestman_leg` (also `chitin` ✅, `dead_centipede` ✅)
- `vinegaroon` → `vinegaroon_acid` (also `chitin` ✅, `dead_scorpion`)
- `den_matron` → `potent_venom` (mini-boss; also `scorpion_den` ✅, `scorpion_brood`, `matron_carapace`)

*(New `dead_*` carcass ids in the existing family: `dead_scorpion`, `dead_tick`. New venom/bug drop ids per the
brief: `scorpion_venom`, `tick_sac`, `harvestman_leg`, `vinegaroon_acid`.)*

**items:**
- `iron_pickaxe` — mining tool, anvil, T3 — mining_speed_pct/light_radius (first pickaxe upgrade)
- `fortune_pick` — mining tool, anvil, T3 — mining_speed_pct/ore_fortune/gem_luck (gem-mining pick)
- `prospector_lamp` — light gear, workbench, T3 — light_radius/night_vision/vein_sense
- `miners_charm` — accessory, jeweler, T3 — ore_fortune/gem_luck/luck
- `scorpion_pick` — weapon (war-pick), forge, T3 — damage_pct/crit_chance + on-hit envenomed
- `venom_lash` — weapon (whip), forge, T3→T4 — damage_pct/knockback, long reach + strong envenomed
- `venom_oil` — weapon coating consumable, cauldron, T3 — adds strong envenomed on-hit
- `antivenom` — consumable, cauldron, T3 — cures envenomed + hazard_resist
- `heat_salve` — consumable buff, cauldron, T3 — hazard_resist(heat)/hp_regen
- `desert_canteen` — utility consumable, workbench, T3 — sustained hazard_resist(heat)
- `tick_repellent` — consumable, cauldron, T3 — desert_tick won't latch
- `cut_quartz` — gem-cut intermediate, jeweler, T3 — polished quartz for jewelry/inlay
- `quartz_pendant` — accessory, jeweler, T3→T5 — crit_chance/gem_luck/rare_bug_luck (needs silver_bar)
- `sandstone_block` — structure ×4, stonecutter, T3 — desert wall/path
- `sandstone_brick` — structure ×4, stonecutter, T3 — finer desert brick
- `geode_lamp` — light décor, jeweler, T3 — light_radius aura
- `desert_jerky` — food, cooking_pot, T3 — long max_hp/hp_regen buff (preservation)
- `prospector_helm` — armor (head), anvil, T3 — defense/light_radius/hazard_resist/vein_sense; set: prospector
- `prospector_vest` — armor (body), loom, T3 — defense/max_hp/hazard_resist/mining_speed_pct; set: prospector (keystone)
- `prospector_boots` — armor (feet), anvil, T3 — defense/move_speed/fall_resist/hazard_resist; set: prospector
- `prospector_band` — accessory (optional 4th), jeweler, T3 — mining_speed_pct/gem_luck
- `miners_camp` — NPC ("the Miner's Camp", miner-themed Blacksmith) — mining-supply shop at the cliff entry
