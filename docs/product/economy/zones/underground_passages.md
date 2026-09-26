# Zone Content Sheet — Underground Passages

> **Grid (underground 3,1)** · connecting tunnels & ore galleries below the rocks · **difficulty
> MEDIUM–HARD** · **tier T3 (iron era — the underground mining hub, the gateway deeper)**
>
> The **core MINING zone**. Where Scorpion Rocks (1,2) was the sunlit *intro* to mining — heat, surface
> benches, first pickaxe — the **Underground Passages** is the real thing: a lamplit warren of tunnels and
> ore galleries that **connects the dig-deeper loop together**. This is the home of the **Miner's outpost**
> (the underground vendor hub), and it is where the four pillars of mining actually live: **mining tools &
> upgrades**, **light gear** (you are in the dark now — light is survival, not flavor), **ore/gem
> processing**, and **hauling** (the mine-cart / ore-sack carry loop). It is the gateway: every deeper
> underground zone is reached *through* these passages, so the gear you build here is what carries you down.
>
> **Design intent (pacing, per `../progression.md` §2–3 "Mid"):** the player arrives with iron tools and a
> torch and learns that *the dark itself is the hazard* — you can't fortune-mine a vein you can't see, and you
> can't farm ore you can't haul out. So the loop here is **light up → read the veins → break ore →
> process/cut on-site → haul it home → upgrade → push deeper**. Generous content below — **we prune later,
> never thin.** Everything is gated **T3** (iron + this zone's drops/minerals); a couple of pieces reach a
> `silver_bar`/`gem` stretch toward T4–T5.
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat vocab
> + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T3 "Mid" / mining loop); shop seam from
> [`../merchants.md`](../merchants.md) (the **Blacksmith = miner-themed** vendor — realized here as the deeper
> **Miner's outpost**, the sibling of Scorpion Rocks' surface **Miner's Camp**). World-guide species: **cave
> spiders, blind beetles, mole crickets, springtails.** Sibling sheet: [`scorpion_rocks.md`](scorpion_rocks.md)
> (surface mining intro — this zone deliberately reuses its `quartz`/`gem_geode`/`cut_quartz` gem-cut seam and
> escalates it underground).

> **FINALIZE NOTES (2026-06-25, `../DECISIONS.md`).** This is one of the two active "Mining Camp" zones (D17).
> Reconcile *in place* — keep the content, apply these as the rulings:
> - **Picks = metal tiers only** (D12): `deepcut_pick` / `fortune_drill` below are **superseded** — the
>   deeper-mining gateway is the metal pick ladder (iron → steel breaks harder stone). `blast_charge` stays as
>   the one dig *consumable*. (`fortune`/`vein_sense` effects move onto the Spelunker set + the loupe.)
> - **Mining processing chain** (D13): replace the ore-doubler `crusher` with **`rock_crusher` → `paydirt`
>   (name TBD) → `sluice`** (crush rock+ore → paydirt → sluice separates ore + gems).
> - **Cart system PENDING** (D12/backlog): `mine_cart` / `cart_rail` stay as the goal, mechanics undecided
>   (research Minecraft minecarts first).
> - **`crusher`/light décor/spelunker_band** etc. — keep; the Spelunker set is the canonical **Miner** set (D10).
> - Venom/poison are real (D16), so `spider_antidote` stays.

---

## Species & drops

Four core species span the dark: a swarming low-threat detritivore, a fragile-but-numerous gem grub, a
burrowing ground bruiser, and a venom/ambush spider. None need new sim primitives — they slot into the
existing arthropod vocabulary (drift/swarm, flee, anchor-and-patrol, ambush). The signature theme is **the
dark**: most are eyeless or low-light hunters, several *react to your light* (drawn to it or flushed by it),
which turns your `light_radius` gear into a real tactical lever — the brighter you burn, the more you see
**and** the more you stir up.

| Species (id) | Tier feel | Behavior | Primary drop — new id | Secondary drop(s) |
|---|---|---|---|---|
| `springtail` | swarm / nuisance | Tiny, jumpy detritivores that boil up in **clouds** off cave-moss and fungus mats, **ping-ponging away from your lamp** (light-shy) before re-forming. The zone's "catch a hundred" trash bug — harmless, fast, a *cloud* catch. Drawn to `glowshroom` patches. | `springtail_dust` ✅(new) — a fine luminescent spore-dust | `dead_springtail` (new `dead_*`), `cave_moss` ✅ (the mat it grazes) |
| `blind_beetle` | armored grinder | Eyeless, pale, slow detritivore that **trundles the gallery floor by feel**, curling/wedging into cracks when struck (high `defense`, no ranged threat). Grinds fungus and carrion. A patience catch; tanky, valuable for its thick pale shell. Ignores light entirely — you can mine right past it. | `blind_beetle_shell` ✅(new) — thick pale chitin plate | `chitin` ✅ (common), `dead_beetle` ✅ (reuse) |
| `mole_cricket` | burrowing bruiser | Stout digging cricket anchored to a **burrow** in the soft-stone walls; **erupts from the floor/wall to shove & gnaw** (knockback charge), then re-burrows. Tanky and heavy-hitting; **its powerful digging claw is the prize.** Telegraphs the eruption (a soil-heave tell). Drawn *toward* vibration (your mining). | `mole_cricket_claw` ✅(new) — a heavy digging claw | `chitin` ✅, `dead_cricket` (new `dead_*`), `soft_stone` chunk |
| `cave_spider` | venom / ambush | Pale low-light hunter that **drops from the ceiling on silk** and ambushes from web-choked side-passages; **bites for a `venomed` DoT** (lighter than the scorpion's `envenomed`), then skitters. Fast, fragile, high dodge. **Its silk is the zone's signature soft material.** More aggressive in the dark — a bright lamp keeps them at bay (a `light_radius` counter). | `cave_spider_silk` ✅(new) — fine cave silk thread | `spider_venom` (new — light venom), `dead_spider` ✅ (reuse) |
| `glow_grub` | *(bonus species — gem/light flavor)* | Slow, fat luminescent larva that **clings to gem veins** and glows soft blue — a living vein-marker. Pure forage-style catch (won't fight, barely flees); pop it for `gem_luck` bait and a soft cold-light material. Its presence *is* the `vein_sense` tutorial — follow the glowing grubs to the ore. | `glow_grub` (the body — light material/bait) | `glow_sac` (new — a cold-light gel), `raw_gem` ✅ (occasionally, clinging to the vein) |

**Calm/catch teaching (escalated from the village's surface bugs):** springtails teach the *light-shy cloud*
catch (your lamp scatters them — a new wrinkle), blind beetles & glow-grubs teach *patience* in the dark,
mole crickets teach *the telegraphed eruption / wait-out-the-burst*, cave spiders teach *the ambush answer
(burn bright, watch the ceiling)*. Light is now part of every catch.

**Drop notes**
- `cave_spider_silk` is the zone's **soft-material spine** — a fine silk thread (lighter than the existing
  `silk`) that feeds the spelunker outfit's weave, rope/harness for hauling, and bug-net upgrades.
- `blind_beetle_shell` is the **plate spine** — thick pale chitin for the spelunker armor & shield, parallel
  to Scorpion Rocks' `harvestman_leg`/`chitin` but a dedicated underground plate.
- `mole_cricket_claw` is the **dig spine** — a heavy claw that tips the zone's pickaxe upgrade and the cart's
  dig-bit, the in-fiction reason your gear can chew deeper.
- `springtail_dust` is a **luminescent reagent** — the glow component of light items, a cheap dye, and a
  fungus-bait. `glow_sac` is its richer cousin (a strong cold-light gel for the headline lamp).
- `spider_venom` is a **light venom** (weaker than `scorpion_venom`) — a cheap coating/potion reagent that
  keeps a venom answer present underground without out-classing the surface tier.
- `chitin`, `cave_moss`, `raw_gem`, `dead_beetle`, `dead_spider` are **existing ids** — reused.
  `dead_springtail`, `dead_cricket` are new carcasses in the existing `dead_*` family.

**Drop → use at a glance**
- `cave_spider_silk` → spelunker weave (outfit body/legs), hauling rope & climbing harness, net upgrade.
- `blind_beetle_shell` → spelunker plate (helm/body) + the `shell_buckler` off-hand.
- `mole_cricket_claw` → the deeper-ore pickaxe + the mine-cart's dig-bit. *(see Finalize Notes: picks = metal tiers)*
- `springtail_dust` / `glow_sac` → the **light line** (glow-lantern, glowstick, headlamp upgrade) + dye.
- `spider_venom` → a light venom coating + the antidote/potion reagent.
- `glow_grub` / `glow_sac` → `gem_luck` bait, cold-light décor, the headline lamp's fuel.

---

## New ingredients & materials

Cave-mineral, fungus, and ore-themed gatherables you **mine or forage from the environment** (not bug drops).
They give non-combat reasons to explore the dark and feed the recipe list. Source = `mine` (break a node/vein)
or `forage` (pick). Most are cost-point 1–2 (raw stone/mineral class) unless noted. Reuses the existing
underground flora (`mushroom_glow`, `cave_moss`) and the ore/gem ladder
(`iron_ore`→`silver_ore`, `coal`, `crystal`, `quartz`, `raw_gem`).

| Id | Source (find@underground_passages) | Cost-pt | Use |
|---|---|---|---|
| `saltpeter` | mine — pale crusted niter veins weeping down the gallery walls (cave evaporite). Common. | 1 | **Black-powder / blasting** base (the `blast_charge` dig tool that opens hard-stone shortcuts), a preservative/desiccant, and a flux note. The cave's "dig faster by blasting, not just picking" answer. |
| `glowshroom` | forage — clustered glowing caps on damp `cave_moss` mats (a richer, brighter cousin of `mushroom_glow`). Common. | 1 | The **light-flora** spine: feeds the glow-lantern fuel, the night-eye potion, a soft cold-light dye, and a cooked light-buff meal. Always-craftable light so a careful player is never trapped in the dark. |
| `cave_nitre` | mine — clear hexagonal crystal druse lining the deeper galleries (a structural crystal between `quartz` and `crystal`). Uncommon. | 2 | A **lens/light** crystal — focuses the headlamp & glow-lantern (`light_radius`), the prospector's loupe, and a glass-clarity additive. The dedicated optics material for the light line. |
| `raw_emerald` | mine — green gem pockets in the soft-stone seams (a *colored* `raw_gem` variant). Uncommon. | 2→10 | The zone's **green gem** — cut at the jeweler/stonecutter into `cut_emerald` for the gem-luck accessory line; the first *colored* gem, escalating the surface `quartz` seam. |
| `raw_sapphire` | mine — deep-blue gem pockets in the hardest galleries (rarer, deeper than emerald). Rare. | 2→16 | The zone's **blue gem** (deeper/rarer) — cut into `cut_sapphire` for the marquee accessory and the headlamp's focusing lens; a T3→T5 bridge material. |
| `soft_stone` | mine — the crumbly tunnel walls the mole crickets burrow (digs fast, low yield). Very common. | 1 | Cheap fill/mortar for cave brick, the **rubble** the cart hauls, and a stonecutter input for cave-block paths. The "every swing gives you *something*" filler. |
| `iron_ore` ✅ | mine — the primary ore galleries (the T3 metal supply this hub exists to open up). | — | Reuse — smelt → `iron_bar`; the spine of every recipe here. The passages are where iron is *mined in volume* (Scorpion Rocks merely introduced it). |
| `silver_ore` ✅ | mine — pale ribbon veins in the deepest galleries (the T5-bridge metal you reach for here). Rare. | — | Reuse — smelt → `silver_bar`; gates the marquee accessory + the deeper-gear stretch toward T4–T5. |
| `coal` ✅ | mine — dark seams threaded through the soft-stone. Common. | — | Reuse — fuel for furnace/forge and the **blast_charge** powder; the heat & blasting economy of the deep. |

> **Why these:** `glowshroom` + `cave_nitre` carry the cave's **light** identity (you build your own daylight
> down here); `saltpeter` + `coal` power the **blasting** dig-shortcut (a second way deeper besides a better
> pick); `raw_emerald` + `raw_sapphire` escalate the surface `quartz` gem seam into a real **colored-gem
> processing** loop (the gem-cut payoff this zone leans into); `soft_stone` is the always-something filler the
> cart hauls; `iron_ore`/`silver_ore`/`coal` are the reused ores the hub exists to mine *in volume* — the
> gateway's whole point.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later), one per the four mandated pillars and then some. Each
lists output · station · inputs(+counts) · unlock · stat/bonus · tier. Costs use the tier-point model;
everything is **gated T3** (a couple reach `silver_bar`/a major gem as a stretch toward T4–T5). `unlock`:
**craft** (have station + recipe) / **buy@miners_outpost** / **find@underground_passages**.

### Mining tools & a dig-shortcut  *(see Finalize Notes: picks → metal ladder; `blast_charge` stays)*

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| ~~`deepcut_pick`~~ *(superseded — use `pickaxe_steel`)* | anvil | `iron_bar` ×3, `mole_cricket_claw` ×2, `cave_nitre` ×1, `plank` ×2 | — | *was: mining_speed/effective_tool_tier+1/vein_sense* | T3 |
| ~~`fortune_drill`~~ *(superseded — `ore_fortune`/`gem_luck` moves to the Spelunker set + loupe)* | forge | `iron_bar` ×3, `cut_emerald` ×1, `mole_cricket_claw` ×1, `coal` ×2 | — | *was: ore_fortune/gem_luck drill* | T3 |
| `blast_charge` (dig consumable) | workbench | `saltpeter` ×2, `coal` ×1, `clay` ×1 | craft / buy@miners_outpost | **Blasts a small cluster of hard/soft stone open** (a one-shot dig-AoE — the shortcut through a wall you'd otherwise grind); also flushes mole-cricket burrows | T3 |

### Light gear (the zone's survival headline — you are in the dark)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `glow_lantern` (held light) | workbench | `iron_bar` ×1, `glass` ×2, `glow_sac` ×1, `cave_nitre` ×1 | craft / buy@miners_outpost | **`light_radius +4`, `night_vision +1`** — the **strong light item**: a cold-glow lantern that out-burns any torch; the brightest portable light in the game so far | T3 |
| `cave_headlamp` (head light, hands-free) | anvil | `iron_bar` ×1, `cave_nitre` ×1, `springtail_dust` ×2, `cave_spider_silk` ×2 (strap) | buy@miners_outpost (recipe) | `light_radius +3`, `vein_sense +1`, **hands-free** (light while you mine/fight — no held slot used) | T3 |
| `glowstick` (throwable light, consumable) | workbench | `glowshroom` ×2, `springtail_dust` ×1 | craft | **Throw to light a far gallery / mark a route** — a cheap scout light; reveals a spot before you commit | T3 |

### Hauling — the carry / mine-cart loop  *(cart system PENDING — see Finalize Notes)*

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `ore_sack` (carry gear) | loom | `cave_spider_silk` ×6, `cloth` ×2, `blind_beetle_shell` ×1 | craft / buy@miners_outpost | **`carry_weight +30`, `pickup_radius +1`** — the dedicated ore-hauling backpack (lets you over-mine without trekking home half-full) | T3 |
| `mine_cart` (hauling structure) *(PENDING)* | anvil | `iron_bar` ×3, `plank` ×4, `mole_cricket_claw` ×1 (dig-bit), `soft_stone` ×4 | buy@miners_outpost / craft | **Placeable rail cart** — auto-vacuums mined ore in a radius into its hold, then you haul the full cart out. Cart-system mechanics backlogged. | T3 |
| `cart_rail` ×4 (structure) *(PENDING)* | stonecutter | `iron_bar` ×1, `soft_stone` ×4 | craft | Lays the track the `mine_cart` rides | T3 |

### Ore / gem processing  *(see Finalize Notes: add `rock_crusher` → `paydirt` → `sluice`)*

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `paydirt` *(name TBD)* | **rock_crusher** | mined rock + ore (`soft_stone`/`granite` + `{ore}`) | craft | crushed rock+ore the sluice processes (D13) | T3 |
| ore + gems | **sluice** | `paydirt` | craft | separates out ore bars-worth + a chance of `raw_emerald`/`raw_sapphire`/`raw_gem` (D13) | T3 |
| `cut_emerald` | jeweler | `raw_emerald` ×2 + `quartz` ×1 (abrasive) | craft | **Gem-cut** intermediate — polished green gem (feeds the spelunker band, the lamp lens) | T3 |
| `cut_sapphire` | jeweler | `raw_sapphire` ×2 + `cave_nitre` ×1 (etch/abrasive) | craft / find | **Gem-cut** intermediate — the rarer polished blue gem; marquee accessory + headlamp lens (T3→T5 reach) | T3→T5 |
| `prospectors_loupe` (accessory) | jeweler | `cave_nitre` ×1, `cut_emerald` ×1, `silver_bar` ✅ ×1 | craft / buy@miners_outpost | `gem_luck +2`, `vein_sense +1`, `light_radius +1` — the gem-finder trinket (T3→T5 reach) | T3→T5 |

### Cave décor / structure / food (the rest of the floor)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `cave_block` ×4 | stonecutter | `soft_stone` ×4 | craft | structure / cave wall & path material | T3 |
| `cave_brick` ×4 | stonecutter | `soft_stone` ×2 + `saltpeter` ×2 (mortar) | craft | finer cave brick (mortared) — the underground building line | T3 |
| `glowshroom_lamp` (light décor) | workbench | `glowshroom` ×2, `cave_nitre` ×1, `iron_bar` ×1 | craft | a glowing cultivated-cap lamp (`light_radius` aura) — the cave-base flex décor | T3 |
| `geode_cluster` (trophy décor) | jeweler | `raw_sapphire` ×1, `cut_emerald` ×1, `iron_bar` ×1 | find / craft | a mounted glittering gem cluster — the "I worked the deep galleries" flex piece (light + comfort aura) | T3 |
| `glow_jerky` (food) | cooking_pot | `dead_beetle` ×1 *(or any `dead_*` bug-meat)* + `glowshroom` ×1 + `saltpeter` ×1 (cure) | craft | salt-cured cave-meat — long-duration **`night_vision +1` / `hp_regen +1`** buff (eat before a deep dive) | T3 |
| `spider_antidote` (consumable) | cauldron | `glowshroom` ×1, `spider_venom` ×1, `cave_moss` ×1 | craft / buy@miners_outpost | **Cures `venomed`** (the cave spider's bite) + short `hazard_resist` — the underground venom answer | T3 |

> **Supply logic:** `mole_cricket_claw` (the bruiser drop) is the bottleneck on the **dig/haul** line
> (`mine_cart`, the steel pick); `cave_spider_silk` (ambush drop) is the bottleneck on the **haul/weave** line
> (`ore_sack`, rope/harness, spelunker outfit). `glowshroom` + `cave_nitre` keep the **light** answers
> (`glow_lantern`, `glowstick`, headlamp, antidote, night-eye) cheap and always craftable so a careful player is
> **never trapped in the dark** — only gated out of the spicy gem drills.

---

## Signature gear — the **Spelunker's Kit** (T3 bonus set — the canonical Miner set, D10)

A 3-piece miner/cave outfit: a silk-strapped, gem-lensed **lamped helm**, a beetle-plate-and-cave-silk vest
with a rope harness, and grippy soft-soled boots. Theme = **the deep-tunnel spelunker who carries their own
daylight, reads the veins, and hauls a heavy load**. This is a *mining + light + hauling* set. Signature
stats: **`light_radius` + `mining_speed_pct` + `carry_weight` + `vein_sense`**, with solid `defense` to
survive the crickets & spiders. Built at **anvil** (plate/lamp) + **loom** (the cave-silk weave & harness) + a
**jeweler** lens inlay — a mixed-station set that shows off the zone's mining identity. Pure T3 (drops + iron +
the cut gem).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `spelunker_helm` | head | anvil | `iron_bar` ×2, `blind_beetle_shell` ×2, `cave_nitre` ×1, `cut_emerald` ×1 (lens) | `defense:3, light_radius:3, vein_sense:1, night_vision:1` (built-in headlamp) | `spelunker` |
| `spelunker_vest` | body | loom | `iron_bar` ×2, `cave_spider_silk` ×4, `blind_beetle_shell` ×2, `cloth` ×2 | `defense:5, max_hp:6, carry_weight:20, mining_speed_pct:5` | `spelunker` |
| `spelunker_boots` | feet | anvil | `iron_bar` ×1, `cave_spider_silk` ×2, `blind_beetle_shell` ×1, `soft_stone` ×2 | `defense:3, move_speed_pct:4, fall_resist:2, hazard_resist:1` | `spelunker` |

**Set bonus (`set: spelunker`, all 3 worn):**
> *"Carry your own daylight; come back loaded."*
> - **+`light_radius +3`** (the helm-lamp flares to a wide aura — the dark stops mattering; no held lantern
>   needed),
> - **+`mining_speed_pct +20`**, **+`ore_fortune +1`**, **+`gem_luck +2`** (mining payoff),
> - **+`vein_sense +2`** (ore glows through the rock at range — the glow-grubs were just the tutorial),
> - **+`carry_weight +20`** (haul a full vein's worth out in one trip).
> - **Fantasy realized:** fully kitted, you walk a pitch-black gallery as a moving pool of daylight, ore lit up
>   through the stone, ripping out `ore_fortune` + `gem_luck` bonus drops straight into your over-sized load,
>   cave spiders held at bay by your glare and the crickets' shoves barely denting your beetle-plate. The
>   passages go from a lethal, blind slog to a generous, self-stocking **ore-and-gem mine you can actually
>   carry home** — and the steel pick you forge here is the key that opens the deeper zone below.

**Unlock:** helm + boots recipes **auto** at the anvil (you can grind the set yourself); the **vest** recipe is
**bought from the Miner's outpost** OR **found in a sealed deep gallery** — so the keystone piece rewards either
the merchant loop or the exploration push.

> Optional matching accessory: `spelunker_band` (jeweler — `cut_sapphire` ×1, `silver_bar` ✅ ×1,
> `mole_cricket_claw` ×1): `mining_speed_pct +5`, `carry_weight +10`, `light_radius +1`. A T3→T5 4th-slot
> stretch; prune if the 3-piece reads cleaner. (Pairs naturally with `prospectors_loupe` + `ore_sack`.)

---

## Shop / NPC stock — **the Miner's outpost** (`miners_outpost`)

The underground vendor hub — a lamplit dugout where the passages branch (this realizes the `merchants.md`
**Blacksmith — miner-themed**, the *deeper* sibling of Scorpion Rocks' surface **Miner's Camp**). A grizzled
tunnel-foreman who runs the outpost: he sells the **light gear, the hauling kit, the gem-cut/processing
recipes, and the keystone set piece**; sells **ore/bars/gems you can't reach yet at a markup**; sells **light
consumables on hand** (so you're never stranded in the dark); and **buys your ore, gems, and silk high** (a
reason to over-mine & over-haul). Currency = coins (existing). He is the gate that teaches "**light up, kit
out, and dig for the deeper zone.**"

**Sells (buy@miners_outpost):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: rock_crusher` / `recipe: sluice` | recipe | 280 / 220 | The ore-processing chain (D13) — the headline payoff. |
| `recipe: cave_headlamp` | recipe | 180 | Hands-free light — the survival staple. |
| `recipe: ore_sack` | recipe | 160 | The hauling upgrade. |
| `recipe: spelunker_vest` | recipe | 420 | Keystone set piece (alt path to the deep-gallery find). |
| `glow_lantern` | gear | 120 | Pre-made strong light so you can see the galleries immediately. |
| `glowstick` ×3 | consumable | 30 | Throwable scout light, on hand (stock-limited daily — forces gathering too). |
| `blast_charge` | consumable | 40 | The dig-shortcut, pre-made; small daily cap. |
| `spider_antidote` | consumable | 25 | The venom answer, on hand before you craft your own. |
| `iron_bar` / `coal` | material | 35 / 15 | Convenience restock of the T3 metal & fuel (small daily cap, markup). |
| `silver_bar` ✅ | material | 90 | The T5-bridge metal you barely mine yet — for the loupe/band stretch (capped). |
| `jeweler` / `rock_crusher` (station) | station | 260 / 240 | Buy-the-station convenience for the gem-cut & ore-processing lines. |

**Buys (sell to vendor — the zone's coin sink + over-mine incentive):** `iron_ore`, `silver_ore`, `coal`,
`soft_stone`, `saltpeter`, `cave_nitre`, `raw_emerald`, `raw_sapphire`, `crystal` ✅, `quartz` ✅,
`cave_spider_silk`, `blind_beetle_shell`, `mole_cricket_claw`, `spider_venom`, `springtail_dust`, `glow_sac` —
with an **`ore_value_pct` premium on ore/gems** and a **`bug_value_pct` premium on silk/venom** (he pays well
for both, reinforcing the mine-and-fight loop). `cut_emerald` / `cut_sapphire` and `raw_sapphire` sell highest
(the deep-gallery flex).

---

## "New toys" hook

The Underground Passages is where BugFarmer's **mining loop becomes a *base of operations*** — Scorpion Rocks
taught you to mine in the sun; here you learn to **own the dark**. The new toys are all about *lighting it,
digging it, processing it, and hauling it home*: a **`glow_lantern`** and hands-free **`cave_headlamp`** that
turn you into a moving pool of daylight (light is now survival, and your brightness literally controls which
bugs swarm or flee you), the **steel pick** you forge here whose tier is the *literal key* that breaks the
stone to the next zone down, **`blast_charge`** to blow a shortcut straight through a wall, and the hauling
kit — **`ore_sack`**, the (pending) **`mine_cart`** + **`cart_rail`**, and the **`rock_crusher` → `paydirt` →
`sluice`** chain — that lets you strip a whole gallery and refine your ore *without ever trekking back
half-full*. The first **colored gems** (`raw_emerald`/`raw_sapphire` → `cut_emerald`/`cut_sapphire`) escalate
the surface quartz-cut seam into a real processing loop. The capstone is the **Spelunker's Kit** set, whose
`light_radius` + `mining_speed_pct` + `carry_weight` + `vein_sense` bonus lets you stand in a pitch-black
gallery as your own daylight, veins glowing through the rock, while spiders cower from your glare. Kit out, light
the dark, and the passages become the **self-stocking ore-and-gem mine and the gateway** that carries you down.

---

## New id ledger

**materials:**
- `paydirt` *(name TBD, D13)* — crusher output the sluice processes
- `saltpeter` — mine@underground_passages (black-powder/blast base; preservative; flux)
- `glowshroom` — forage@underground_passages (light-flora; lantern fuel, night-eye, dye, light meal)
- `cave_nitre` — mine@underground_passages (lens/optics crystal; light line + glass clarity)
- `raw_emerald` — mine@underground_passages (green gem; cuts to `cut_emerald`; gem-luck line)
- `raw_sapphire` — mine@underground_passages (blue gem, rarer/deeper; cuts to `cut_sapphire`; T3→T5 bridge)
- `soft_stone` — mine@underground_passages (crumbly tunnel wall; cave brick/path, cart rubble, filler)
- `cut_emerald` — crafted intermediate (jeweler; gem-cut green gem)
- `cut_sapphire` — crafted intermediate (jeweler; gem-cut blue gem, T3→T5)
- `cave_spider_silk` — drop, cave_spider (fine cave silk; weave/haul/net line)
- `blind_beetle_shell` — drop, blind_beetle (thick pale plate; spelunker armor + buckler)
- `mole_cricket_claw` — drop, mole_cricket (heavy digging claw; cart dig-bit)
- `springtail_dust` — drop, springtail (luminescent spore-dust; light reagent + dye)
- `spider_venom` — drop, cave_spider (light venom; coating + antidote/potion reagent)
- `glow_sac` — drop, glow_grub (cold-light gel; the `glow_lantern` fuel + décor)
- *(reused: `iron_ore`, `silver_ore`, `coal`, `crystal`, `quartz`, `raw_gem`, `granite`, `chitin`, `cave_moss`,
  `mushroom_glow`, `cloth`, `plank`, `clay`, `glass`, `silver_bar`, `dead_beetle`, `dead_spider`)*

**species:** (id → primary drop)
- `springtail` → `springtail_dust` (also `dead_springtail`, `cave_moss` ✅)
- `blind_beetle` → `blind_beetle_shell` (also `chitin` ✅, `dead_beetle` ✅)
- `mole_cricket` → `mole_cricket_claw` (also `chitin` ✅, `dead_cricket`, `soft_stone`)
- `cave_spider` → `cave_spider_silk` (also `spider_venom`, `dead_spider` ✅)
- `glow_grub` → `glow_sac` (bonus species; also `glow_grub` body, `raw_gem` ✅)

*(New `dead_*` carcass ids: `dead_springtail`, `dead_cricket`. New stations: `rock_crusher`, `sluice`.)*

**items:**
- ~~`deepcut_pick`~~ / ~~`fortune_drill`~~ — superseded (picks = metal ladder, D12)
- `blast_charge` — dig consumable, workbench, T3 — one-shot dig-AoE (blast a stone wall open)
- `rock_crusher` / `sluice` — mining-processing stations (D13)
- `glow_lantern` — light gear (held), workbench, T3 — light_radius+4/night_vision (the strong light item)
- `cave_headlamp` — light gear (head, hands-free), anvil, T3 — light_radius/vein_sense
- `glowstick` — throwable light consumable, workbench, T3 — light a far gallery / mark route
- `ore_sack` — carry gear, loom, T3 — carry_weight/pickup_radius (the haul backpack)
- `mine_cart` / `cart_rail` — hauling (PENDING, cart system backlog)
- `cut_emerald` / `cut_sapphire` — gem-cut intermediates, jeweler
- `prospectors_loupe` — accessory, jeweler, T3→T5 — gem_luck/vein_sense/light_radius
- `cave_block` / `cave_brick` — structure ×4, stonecutter, T3
- `glowshroom_lamp` — light décor, workbench, T3 — light_radius aura
- `geode_cluster` — trophy décor, jeweler, T3 — light + comfort aura
- `glow_jerky` — food, cooking_pot, T3 — long night_vision/hp_regen buff
- `spider_antidote` — consumable, cauldron, T3 — cures venomed + hazard_resist
- `shell_buckler` — off-hand shield, workbench, T3 — defense/knockback (blind_beetle_shell ×4 + iron_bar ×1)
- `spelunker_helm` / `_vest` / `_boots` — armor set `spelunker` (the canonical Miner set, D10)
- `spelunker_band` — accessory (optional 4th), jeweler, T3→T5
- `miners_outpost` — NPC ("the Miner's outpost", miner-themed Blacksmith)
