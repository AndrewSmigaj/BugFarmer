# Zone Content Sheet — Spider Vale East (0,3 · `spider_vale_east`)

> **Status:** design only (content brainstorm). Generous-by-design — **we prune later, never thin.**
> Reuses existing ids where they exist; new ids are `snake_case` and called out in the trailing id ledger.
>
> **The harder twin of Spider Vale West.** This sheet is the **EAST hollow** — the *endgame surface
> gauntlet*. Where the West vale teaches the spider loop (web traversal, the basic silk/venom gear), the
> East hollow is where the **best surface weapons & armor and the rarest drops** live. It deliberately
> **reuses West's silk/venom vocabulary** (`spider_silk`, `venom_gland`, `web_anchor`, `silk_bolt`,
> `antivenom`-line) rather than re-coining it, and pushes it one tier hotter — *potent* venom, *royal*
> silk, a mini-boss huntsman, and an abandoned-camp loot vendor that trades in **rare FIND recipes**.

| | |
|---|---|
| **Zone** | Spider Vale East |
| **Grid** | 0,3 — a dark, web-choked hollow at the western edge of the world |
| **Tier band** | **T5** (silver → gold → platinum / diamond) — **the hardest SURFACE zone** |
| **Difficulty** | **EXTRA-EXTRA HARD** — deadly venom, ambush predators, a mini-boss; come kitted or die |
| **Theme** | The **endgame surface gauntlet** — top spider-silk/venom gear, the best surface drops, a mini-boss huntsman, an abandoned-camp loot vendor + rare FIND recipes |
| **Identity** | Where the player **finishes their surface build**: the marquee venom weapon, the endgame silk/venom armor set, the powerful accessory, and the rare found recipes that aren't sold anywhere |
| **World-guide species** | **black widows, tarantulas, trapdoor spiders, giant huntsman** (mini-boss) |
| **Existing spider vocab (reuse from `spider_vale_west.md`)** | `spider_silk` ✅, `web_silk`, `venom_gland`, `web_anchor`, `silk_bolt`, `silk_cloth` ✅, `spun_silk` ✅, `antivenom` ✅-line, `envenomed` debuff, `resin_glob` ✅, the `web` traversal hazard |
| **Hazards** | **lethal venom** (`envenomed` here is a *heavy, stacking* DoT — a careless run dies to it); **trip-web ambush** (trapdoor & web-anchored predators strike from cover the instant you cross a strand); **dark hollow** (`light_radius` / `night_vision` mandatory — the vale is permanently dim); **trapdoor pits** (`fall_resist` softens the ambush drop); **venom-mist** ground patches near the huntsman lair |

The East hollow is where Spider Vale West's *traversal and basic silk gear* stops being enough. West's
`silk_bolt` crossbow and starter web-armor get you **into** the hollow; the East's widows and tarantulas
hit harder, the venom is **lethal** rather than annoying, and the only way through is the **endgame
surface kit** built right here — *potent* venom weapons, *royal*-silk armor, and the rare recipes you can
only **find** in the abandoned camp at the vale's heart. Clear it and you walk out with the best surface
gear in the game and the seed materials for whatever lies underground.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat
> vocab + `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T5 "Endgame surface"); shop seam from
> [`../merchants.md`](../merchants.md) (realized as the **abandoned camp / scavenger** vendor). Pairs as
> the hard twin of [`spider_vale_west.md`](spider_vale_west.md) — reuse its silk/venom ids, push one tier up.

---

## Species & drops

Five concrete species span the difficulty curve — an ambush venom threat, a tanky bruiser, a trap
predator, and a mini-boss apex hunter — plus a swarm of spiderlings as ecology pressure. Behaviors slot
into the existing arthropod vocabulary (anchor-and-patrol, ambush-from-cover, flank, swarm, boss-adds)
without new sim primitives. The signature theme is **deadly venom** (`widow_venom` is the strongest
venom material in the game) plus **web-ambush** and **darkness**.

| Species (id) | Tier feel | Behavior | Primary drop (new) | Secondary drop(s) |
|---|---|---|---|---|
| `black_widow` | core threat | Web-anchored in dark corners under ledges and in the camp ruins. Patrols a small radius around its `web_anchor` ✅; **drops on a silk line and bites** — the bite applies a **heavy, stacking `envenomed`** (the worst DoT in the game; two bites can kill an under-prepared player). Fast, low HP, retreats up its thread when struck, re-drops. The marquee venom source. | `widow_venom` ✅(new) | `spider_silk` ✅ (common), `dead_spider` (new `dead_*`), `web_silk` (reuse from West) |
| `tarantula` | solitary bruiser | Big, slow, **tanky** ground spider anchored to a burrow. **Solitary, does NOT swarm** but has high HP and hits hard; **flicks barbed urticating hairs** (a `hazard_resist`-able irritant cloud / brief `defense`-shred) before closing to a heavy fanged bite. Telegraphs the hair-flick; punishes standing in front of it. | `tarantula_hair` ✅(new) | `chitin` ✅, `venom_gland` (reuse from West), `dead_spider` |
| `trapdoor_spider` | ambush predator | Hidden under a hinged `trapdoor` lid flush with the hollow floor; **invisible until you cross its trigger-line**, then **bursts out, grabs, and drags toward the pit** (a knockback-into-a-fall). High burst, then retreats back under the lid to reset. Rewards `fall_resist`, `vein_sense`-style web-sense, and not face-tanking. | `trapdoor_silk` ✅(new — the dense lid/lining silk) | `spider_silk` ✅, `dead_spider`, `trapdoor_lid` (rare décor/structure) |
| `spiderling_swarm` | swarm / harasser | The widows' brood — **dense clusters of tiny spiders** that pour from a disturbed `egg_sac` and skitter at the player, biting for small stacking `envenomed`. Fragile, low value individually; a *wide-arc* clear, not a twitch fight. Light ecology pressure + the venom-bottleneck filler. | `spiderling_cluster` (new) | `egg_sac` (new — the burst nest), `spider_silk` ✅ |
| `giant_huntsman` | **mini-boss** (apex hunter) | The **signature fight** — a huge, fast, **free-roaming** huntsman that hunts the player across the whole hollow (no anchor — it *comes to you*). Phase 1: lightning skitter-charges + heavy fanged bites applying heavy `envenomed`; tears open `egg_sac`s to summon `spiderling_swarm` adds. Phase 2 (under 50% HP): **wall-runs the canopy webs**, drops venom-mist ground patches, and lunges from above. The hardest surface fight in the game. | `huntsman_fang` ✅(new, guaranteed 1–2) | `potent_venom` ✅ (reuse from Scorpion Rocks — guaranteed boss seed), `royal_silk` (new, guaranteed — the endgame silk), `huntsman_carapace` (rare décor/trophy), `huntsman_eye` (rare accessory drop) |

**Drop notes**
- `widow_venom` is the **strongest venom material in the game** (off `black_widow`) — it is the East's
  offensive bottleneck and a tier hotter than the West's `venom_gland` / Scorpion Rocks' `scorpion_venom`.
  `potent_venom` ✅ (reused, here as a **guaranteed huntsman drop**) is the *upgraded/rare* venom seed that
  gates the marquee weapon — a clean two-tier venom supply (`widow_venom` → `potent_venom`) mirroring the
  West and the Thicket, one tier up.
- `tarantula_hair`, `trapdoor_silk`, `huntsman_fang` are each species-signature crafting drops (uses below).
- `royal_silk` is the **endgame silk material** — the premium thread that anchors the T5 armor set, a rung
  above the West's `web_silk` and the Butterfly Fields' `emperor_silk_cloth` line.
- `spider_silk` ✅, `chitin` ✅, `venom_gland` / `web_silk` / `web_anchor` (reuse from West), `resin_glob` ✅
  are **existing ids** — reused. `dead_spider` is the carcass in the existing `dead_*` family.
- `egg_sac`, `spiderling_cluster`, `trapdoor_lid`, `huntsman_carapace`, `huntsman_eye` round out the swarm
  and boss tables — the venom/silk inputs plus the "I cleared the vale" flex trophies.

**Drop → use at a glance**
- `widow_venom` → the strongest venom weapons & coatings (this zone's offense) + the deadliest poison-bomb.
- `tarantula_hair` → the urticating-irritant throwable + a `thorns`/barbed lining for the armor set.
- `trapdoor_silk` → the densest silk → the endgame **silk armor body** + the heavy net/trap line.
- `royal_silk` → the **set keystone** — spun into the endgame silk cloth for the signature armor.
- `huntsman_fang` → the marquee venom weapon's fang-blade + the apex accessory.
- `potent_venom` ✅ → the marquee weapon's venom charge + a forward hook into the underground tier.

---

## New ingredients & materials

Vale-themed gatherables you **forage or harvest from the environment** (not bug drops) plus the two new
**spun/refined** materials the silk line needs. Source = `forage` (pick), `harvest` (cut a web/node),
`craft` (spun at the loom). The brief asks for ≥3 new materials; here are five (prune later).

| Id | Source (@spider_vale_east) | Cost-pt | Use |
|---|---|---|---|
| `royal_silk` | **drop** — guaranteed off `giant_huntsman`; rarely from a deep `egg_sac` | 16 (gem-major class — endgame, boss-gated) | **The endgame silk material.** Spun → `royal_silk_cloth`; anchors the T5 **Widow's armor set** + the apex silk gear. The keystone the whole set flows through. |
| `potent_venom` ✅ | **drop** — guaranteed off `giant_huntsman` (reuse from Scorpion Rocks) | 16 | The **upgraded venom seed** — gates the marquee venom weapon; held as the **forward hook** into the underground/cave tier (its hotter venom). |
| `gloom_moss` | forage — luminescent moss crusting the dark hollow walls & camp ruins. Uncommon. | 1 | The vale's **light/night** flora: feeds the glow-lamp décor, the `night_vision` tonic, and a soft glow-dye. Always craftable so a careful player can always see. |
| `cave_nettle` | forage — pale stinging nettles in the damp shade (the West's `nettle_leaf` cousin, hardier). Common. | 1 | The **antivenom counter-irritant** + the heat/soothe note for the heavy `envenomed` cure — keeps survival cheap and always craftable. |
| `royal_silk_cloth` | **craft** (loom) — `royal_silk` spun + `spun_silk` ✅ blended | 16+ | The premium **endgame cloth bolt** → every piece of the Widow's set + the apex silk décor. The gateway from raw royal silk to wearable. |
| `web_anchor` (reuse) | harvest — the silk anchor-points strung across the hollow (reuse from West) | (existing) | Tough cordage for the heavy net / trap line and the armor's web-weave; reused, not re-coined. |
| `spider_silk` ✅ / `spun_silk` ✅ / `silk_cloth` ✅ | drop / craft (reuse) | (existing) | The base silk ladder — `spider_silk` → `spun_silk` → `silk_cloth`; the East blends these **up** into `royal_silk_cloth`, it doesn't replace them. |

> **Why these:** `royal_silk` + `royal_silk_cloth` carry the **endgame silk identity** (the set keystone,
> boss-gated so it *feels* earned); `potent_venom` (reused) is the marquee-weapon gate + the forward hook;
> `gloom_moss` + `cave_nettle` keep the **survival answers** (light, the heavy-`envenomed` antivenom) cheap
> and always craftable, so a careful player is never *locked out* of staying alive — only of the spicy
> endgame venom weapons. The base silk ladder (`spider_silk`/`spun_silk`/`silk_cloth`) is **reused from the
> West**, not re-coined — the East just adds the top rung.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) ·
unlock · stat/bonus · tier. Costs use the tier-point model; everything is **gated T5** (silver → gold →
platinum/diamond + boss drops). `unlock`: **craft** (have station + recipe) / **buy@scavenger_camp** /
**find@spider_vale_east** (the rare camp/lair recipe scrolls). **Marked `find` = rare** — not sold anywhere.

### Weapons — the top surface venom tier

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `widowfang_blade` (the **marquee venom weapon**) | forge | `gold_bar` ✅ ×2, `huntsman_fang` ✅ ×2, `widow_venom` ✅ ×3, `potent_venom` ✅ ×1 | **find@spider_vale_east** (rare lair recipe scroll) — *not sold* | `damage_pct +30`, `crit_chance +8`, `crit_mult +0.4`, **on-hit applies heavy stacking `envenomed`** (the strongest on-hit venom in the game); the best surface weapon | **T5** |
| `silk_repeater` (venom crossbow — `silk_bolt` upgrade) | forge | `silver_bar` ✅ ×2, `trapdoor_silk` ✅ ×3, `widow_venom` ✅ ×2, `web_anchor` ×2 | buy@scavenger_camp (recipe) | `damage_pct +22`, `attack_speed_pct +15`, ranged, **bolts carry `envenomed`**; long-reach answer to the web-ambush spacing | T5 |
| `venom_draught` (weapon coating, consumable) | cauldron | `widow_venom` ✅ ×1, `resin_glob` ✅ ×1, `cave_nettle` ×1 | craft (once cauldron + zone access) | **Coats your current weapon** — adds heavy `envenomed` on-hit for a duration; upgrades any blade to widow-tier venom | T5 |

### Survival — the answer to the zone (heavy-venom + dark)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `widow_antivenom` (the **required survival item**) | cauldron | `cave_nettle` ×2, `widow_venom` ✅ ×1, `gloom_moss` ×1 | buy@scavenger_camp (recipe) | **Clears all heavy `envenomed` stacks** + a temporary venom-immunity window + small `hp_regen`. The answer to the widows. | T5 |
| `gloom_tonic` (consumable buff) | cauldron | `gloom_moss` ×2, `cave_nettle` ×1, `sage` ✅ ×1 | craft | Sustained **`night_vision +1` + `light_radius +2`** — lets you see the trip-webs and trapdoors in the permanent dark. | T5 |
| `widow_bomb` (thrown consumable) | cauldron | `widow_venom` ✅ ×2, `tarantula_hair` ✅ ×1, `clay` ✅ ×1 | **find@spider_vale_east** (rare recipe scroll) — *not sold* | **Throwable** — a heavy-`envenomed` + `defense`-shred AoE cloud (the hairs); melts swarms & the huntsman adds | T5 |

### Accessory + endgame jewelry (jeweler — the powerful trinket)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `huntsman_charm` (the **powerful accessory**) | jeweler | `huntsman_fang` ✅ ×1, `huntsman_eye` ×1, `diamond` ✅ ×1, `gold_bar` ✅ ×1 | **find@spider_vale_east** (rare boss-lair recipe) — *not sold* | `crit_chance +8`, `crit_mult +0.5`, `damage_pct +8`, `rare_bug_luck +1` — the apex surface offense trinket; the huntsman's gift | **T5** |
| `web_walker_band` (accessory) | jeweler | `royal_silk` ✅ ×1, `silver_bar` ✅ ×1, `trapdoor_silk` ✅ ×1 | craft / find | `dodge_chance +6`, `move_speed_pct +4`, `fall_resist +1` — read the webs, skip the trapdoor ambush | T5 |

### Trap / structure / décor (sawmill · stonecutter · jeweler)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `silk_snare` (deployable trap) | workbench | `trapdoor_silk` ✅ ×2, `web_anchor` ×2, `resin_glob` ✅ ×1 | craft / find | a placeable web-snare that holds bugs (catch-loop tool vs the fast widows/huntsman adds) | T5 |
| `gloom_lamp` | jeweler | `gloom_moss` ×2, `glass` ✅ ×1, `silver_bar` ✅ ×1 | craft | light décor — a glowing moss-lantern (`light_radius` aura); the dark-hollow flex piece | T5 |
| `huntsman_trophy` | workbench | `huntsman_carapace` ×1, `plank` ✅ ×2, `royal_silk_cloth` ×1 | find (boss drop assembles it) | mounted trophy décor — the "I beat the huntsman" wall flex (idle aura tag) | T5 |
| `royal_silk_bolt` (cloth-grade décor/material) | loom | `royal_silk` ✅ ×2, `spun_silk` ✅ ×2 | craft | intermediate → `royal_silk_cloth`; also a luxury upholstery/décor bolt | T5 |

> **Supply logic:** `widow_venom` (the strong common drop) is the bottleneck on offense; `cave_nettle` /
> `gloom_moss` (common gatherables) keep the **survival** answers (`widow_antivenom`, `gloom_tonic`) cheap
> and always craftable. `potent_venom` + `huntsman_fang` + `royal_silk` (all **huntsman-gated**) lock the
> three marquee items — the `widowfang_blade`, the `huntsman_charm`, and the Widow's-set keystone — behind
> the mini-boss, and the spiciest recipes (`widowfang_blade`, `huntsman_charm`, `widow_bomb`) are **rare
> FINDs, not sold** — so the abandoned camp sells the *bread-and-butter* gear and the **lair** rewards the
> exploration. `potent_venom` is held in reserve as the **forward hook** into the underground tier's venom.

---

## Signature gear — the **Widow's Shroud** (T5 bonus set)

The endgame **surface** combat set: woven from `royal_silk_cloth` over a chitin-and-gold-stud frame, lined
with barbed `tarantula_hair`, fanged at the gauntlets. Theme = **the assassin who turns the spiders' own
venom and silk against them** — a *glass-assassin / crit-venom* set (high crit & life-on-hit, modest
defense), a deliberate contrast to the heavy-`defense` armor sets of the metal zones. Built at **loom**
(the royal-silk weave) + **anvil** (the gold studs/plate) + a **jeweler** fang-inlay — a mixed-station
endgame set. Pure T5 (royal silk + gold + boss drops + diamond).

`bonuses{}` schema per [`../stats_and_bonuses.md`](../stats_and_bonuses.md) (additive; `_pct` are percent;
`set` ties the set bonus). Two of the three pieces are **`unlock=find`** (rare) — the set is *earned in the
hollow*, not bought wholesale.

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` | Unlock |
|---|---|---|---|---|---|---|
| `widow_hood` | head | loom | `royal_silk_cloth` ×2, `gold_bar` ✅ ×1, `widow_venom` ✅ ×1, `gloom_moss` ×1 | `defense:4, crit_chance:6, night_vision:1, rare_bug_luck:1` | `widow` | craft / buy@scavenger_camp |
| `widow_shroud` | body | loom | `royal_silk_cloth` ×3, `gold_bar` ✅ ×2, `trapdoor_silk` ✅ ×2, `tarantula_hair` ✅ ×2 | `defense:6, max_hp:8, crit_mult:0.3, life_on_hit:1, thorns:2` | `widow` | **find@spider_vale_east** (rare lair recipe) — keystone |
| `widow_steps` | feet | loom | `royal_silk_cloth` ×2, `gold_bar` ✅ ×1, `trapdoor_silk` ✅ ×1 | `defense:4, move_speed_pct:5, dodge_chance:6, fall_resist:1` | `widow` | **find@spider_vale_east** (rare camp recipe) |

**Set bonus (`set: widow`, all 3 worn):**
> *"Drop on them from the dark. Their venom is yours now."*
> - **+`crit_chance +10`**, **+`crit_mult +0.5`**, **+`damage_pct +10`** (the assassin's burst),
> - **+`life_on_hit +2`** and **`envenomed`-immunity** — the widows' own venom *can no longer hurt you*
>   (you walk the hollow without the antivenom for *heavy `envenomed`*),
> - **+`dodge_chance +6`** and **silent on webs** — trip-webs & trapdoors **don't trigger on you**
>   (the ambush predators can't open on the spider-shrouded hunter).
> - **Fantasy realized:** fully kitted in the Widow's Shroud, you stalk the dark hollow *immune to its
>   venom*, the trapdoors never spring, your crits land venom DoTs that the widows can't survive, and every
>   hit heals you back. The vale that *killed* you on the way in becomes a generous, self-stocking venom &
>   silk farm — and the set is the best **surface** combat gear in the game, the reward for clearing the
>   gauntlet. That power carries straight into the underground tier below.

**Unlock logic:** `widow_hood` is **auto/buy** (you can start the set yourself); the **`widow_shroud`**
(keystone body) and **`widow_steps`** are **rare FINDs** — the shroud recipe in the **huntsman's lair**,
the steps in the **abandoned camp ruins** — so the set is *earned by exploring the hollow*, not bought
whole. (The `widow_shroud` recipe can alternately drop from the `giant_huntsman` — boss path or find path.)

> Optional matching accessory: `widow_locket` (jeweler — `royal_silk` ✅ ×1, `huntsman_fang` ✅ ×1,
> `diamond` ✅ ×1): `life_on_hit +1`, `crit_chance +4`. A 4th-slot stretch that deepens the lifesteal-crit
> identity; prune if the 3-piece reads cleaner. (Pairs naturally with `huntsman_charm` + `widowfang_blade`
> for a full crit-venom-assassin build.)

---

## Shop / NPC stock — **the Scavenger's Camp** (`scavenger_camp`)

An **abandoned camp** at the safe edge of the hollow, run by a lone **scavenger** who survived in the vale
by looting what the spiders left and trading it. This realizes the brief's "abandoned-camp loot vendor +
rare FIND recipes" seam. She **sells salvaged endgame loot and the bread-and-butter recipes**, **trades in
rare materials you can't yet farm**, and **buys your venom & silk high** (a reason to over-hunt the
widows). She does **NOT** sell the spiciest recipes — the `widowfang_blade`, `huntsman_charm`, `widow_bomb`,
and the two keystone armor pieces are **rare FINDs in the lair/ruins**, not shop stock. Currency = coins.

**Sells (buy@scavenger_camp):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: silk_repeater` | recipe | 480 | The venom crossbow — the bread-and-butter ranged answer. |
| `recipe: widow_antivenom` | recipe | 320 | Clears heavy `envenomed` — the required survival recipe. |
| `recipe: web_walker_band` | recipe | 360 | The dodge/web-walk accessory. |
| `recipe: widow_hood` | recipe | 400 | The set's starter piece (the keystones are finds). |
| `widow_antivenom` | consumable | 70 | Pre-made; stock-limited daily (forces hunting venom too). |
| `gloom_tonic` | consumable | 45 | Night-vision/light on hand before you craft your own. |
| `silk_repeater` (salvaged) | gear | 600 | A pre-made looted crossbow so you can fight ranged immediately. |
| `royal_silk` ✅ | material | 220 | A *single* salvaged strand at a steep markup — bridges you to the first cloth bolt before the boss. Hard daily cap. |
| `silver_bar` ✅ / `gold_bar` ✅ | material | 90 / 180 | The T5 metals you may not have stockpiled — capped, marked up. |
| `loom` / `jeweler` (station) | station | 240 / 320 | Buy-the-station convenience for the royal-silk + jewelry lines. |

**Buys (sell to vendor — the zone's coin sink + over-hunt incentive):** `widow_venom`, `tarantula_hair`,
`trapdoor_silk`, `spider_silk` ✅, `venom_gland`, `web_silk`, `spiderling_cluster`, `egg_sac`, `chitin` ✅ —
with a **`bug_value_pct` premium on venom & silk** (she pays well for both, reinforcing the hunt loop).
`huntsman_fang`, `royal_silk`, `potent_venom` ✅, `huntsman_carapace`, and `huntsman_eye` sell **highest**
(the boss flex).

---

## "New toys" hook

Spider Vale East is where BugFarmer's **surface build finishes** and the venom turns *lethal*. The new toys
are the **best surface gear in the game**: the `widowfang_blade`, a gold-and-fang sword whose crits stack
the strongest `envenomed` DoT anywhere; the `silk_repeater` venom crossbow that lets you out-space the
web-ambush predators; the `venom_draught` coating that pushes *any* weapon to widow-tier venom; and the
survival kit — `widow_antivenom`, `gloom_tonic`, `widow_bomb` — that takes the dark, deadly hollow from
"this kills careless runs" to "this is my venom-and-silk farm." The capstone is the **Widow's Shroud** set,
whose crit-venom-lifesteal bonus makes you *immune to the vale's own venom*, *invisible to its trapdoors*,
and lethal — turning the gauntlet that killed you into a generous farm. The rarest rewards are **found, not
bought**: the marquee blade and the keystone armor are recipe scrolls in the **huntsman's lair** and the
**abandoned camp ruins**, and the scavenger trades the loot the spiders left behind. Beat the
`giant_huntsman` and you walk out with `huntsman_fang`, `royal_silk`, and `potent_venom` — the apex accessory,
the endgame set keystone, and the **seed of the next tier's hotter (underground) venom**.

---

## New id ledger

**materials:**
- `royal_silk` — drop@giant_huntsman (guaranteed) / rare egg_sac (the endgame silk material; set keystone, cost-pt 16)
- `royal_silk_cloth` — craft (loom; `royal_silk` + `spun_silk` ✅ → the premium endgame cloth bolt)
- `gloom_moss` — forage@spider_vale_east (luminescent moss; glow-lamp, night_vision tonic, glow-dye — cheap survival)
- `cave_nettle` — forage@spider_vale_east (hardy stinging nettle; the heavy-`envenomed` antivenom counter-irritant)
- `widow_venom` — drop, black_widow (the **strongest venom material in the game**; venom 10+ class, offense bottleneck)
- `tarantula_hair` — drop, tarantula (urticating-irritant throwable + barbed `thorns` armor lining)
- `trapdoor_silk` — drop, trapdoor_spider (the densest silk; endgame silk armor body + heavy net/trap line)
- `huntsman_fang` — drop, giant_huntsman (guaranteed; marquee weapon fang-blade + apex accessory)
- `huntsman_eye` — rare drop, giant_huntsman (apex accessory input — `huntsman_charm`)
- `huntsman_carapace` — rare décor/trophy drop, giant_huntsman
- `spiderling_cluster` — drop, spiderling_swarm (venom-input filler; vendor sells)
- `egg_sac` — drop/nest, spiderling_swarm & black_widow brood (the burst nest; venom/silk input)
- `trapdoor_lid` — rare drop, trapdoor_spider (décor/structure)
- `dead_spider` — carcass drop (existing `dead_*` family; off all spiders)
- `potent_venom` ✅ — drop@giant_huntsman (REUSE from Scorpion Rocks — guaranteed boss seed + forward hook to the underground venom tier)
- *(reused, not re-coined: `spider_silk` ✅, `spun_silk` ✅, `silk_cloth` ✅, `web_silk`, `venom_gland`, `web_anchor`, `resin_glob` ✅, `chitin` ✅ — from `spider_vale_west.md` + global catalog)*

**species:** (id → primary drop)
- `black_widow` → `widow_venom` (also `spider_silk` ✅, `dead_spider`, `web_silk`)
- `tarantula` → `tarantula_hair` (also `chitin` ✅, `venom_gland`, `dead_spider`)
- `trapdoor_spider` → `trapdoor_silk` (also `spider_silk` ✅, `dead_spider`, `trapdoor_lid`)
- `spiderling_swarm` → `spiderling_cluster` (also `egg_sac`, `spider_silk` ✅)
- `giant_huntsman` → `huntsman_fang` (mini-boss; also `potent_venom` ✅, `royal_silk`, `huntsman_carapace`, `huntsman_eye`)

**items:**
- `widowfang_blade` — weapon (sword), forge, T5 — damage_pct/crit_chance/crit_mult + heavy on-hit envenomed (marquee; unlock=find, rare)
- `silk_repeater` — weapon (crossbow), forge, T5 — damage_pct/attack_speed, ranged + envenomed bolts (buy@scavenger_camp)
- `venom_draught` — weapon coating consumable, cauldron, T5 — adds heavy envenomed on-hit
- `widow_antivenom` — consumable, cauldron, T5 — clears heavy envenomed + immunity window + hp_regen (required survival; buy)
- `gloom_tonic` — consumable buff, cauldron, T5 — sustained night_vision/light_radius
- `widow_bomb` — thrown consumable, cauldron, T5 — heavy envenomed + defense-shred AoE (unlock=find, rare)
- `huntsman_charm` — accessory, jeweler, T5 — crit_chance/crit_mult/damage_pct/rare_bug_luck (powerful; unlock=find, rare)
- `web_walker_band` — accessory, jeweler, T5 — dodge_chance/move_speed_pct/fall_resist
- `silk_snare` — deployable trap, workbench, T5 — holds bugs (catch-loop tool)
- `gloom_lamp` — light décor, jeweler, T5 — light_radius aura
- `huntsman_trophy` — décor, workbench, T5 — boss trophy (idle aura; unlock=find)
- `royal_silk_bolt` — intermediate/décor material, loom, T5 — → royal_silk_cloth + luxury bolt
- `widow_hood` — armor (head), loom, T5 — defense/crit_chance/night_vision/rare_bug_luck; set: widow (craft/buy)
- `widow_shroud` — armor (body), loom, T5 — defense/max_hp/crit_mult/life_on_hit/thorns; set: widow (KEYSTONE; unlock=find, rare)
- `widow_steps` — armor (feet), loom, T5 — defense/move_speed/dodge_chance/fall_resist; set: widow (unlock=find, rare)
- `widow_locket` — accessory (optional 4th), jeweler, T5 — life_on_hit/crit_chance
- `scavenger_camp` — NPC ("the Scavenger's Camp", abandoned-camp loot vendor) — endgame surface loot + bread-and-butter recipes at the hollow edge
