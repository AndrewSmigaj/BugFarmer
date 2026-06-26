# Weapons — the full catalog

Every weapon in the economy, in two layers:

- **(A) BASE tiered families** — the cross-cutting metal-tier weapon ladder the *zones don't cover*. Six
  families × eight metal tiers, crafted at the anvil/forge from bars. The dependable, always-available spine
  that any player can build from materials alone (recipe `auto`).
- **(B) SPECIAL / bug-themed weapons** — the *characterful, zone-gated* offense indexed out of every
  `../zones/*.md`. Built from boss/species drops (venom, fire, acid, chitin, horn…), each tied to a zone, a
  station, and a marquee effect. The reason fighting a zone's apex *matters*.

Conventions match the rest of the economy docs:
- **Station:** `anvil` (≤iron tier) · `forge` (steel+ / alloys) · `cauldron` (coatings & throwables) · `jeweler`/`loom` only where a special weapon's recipe says so.
- **Cost model (base families):** `{bar}×2 + wood×1`. Tier-points (from `../crafting.md §1`): copper_bar=3, bronze_bar=4, iron_bar=6, steel/silver_bar=10, gold_bar=16, platinum_bar=24; wood=1.
- **Cost (special):** Σ(input tier-points), venom/steel/silver=10, gold=16, diamond=24–40 per the same table.
- **Unlock:** `auto` (recipe always at the station) · `buy@<npc>` · `find@<zone>` (rare scroll/cache).
- ✅ = id already exists in data today (`sword_wood` ✅, `spear_wood` ✅); the rest are design proposals.
- **Primary stat menu** (from `../stats_and_bonuses.md`): `damage_pct` · `attack_speed_pct` · `knockback` · `crit_chance`/`crit_mult` · `reach`. On-hit effects: `poisoned`/`envenomed` (DoT), `scorched` (burn DoT), `corroded`/`acid_burn` (armor-shred), `stagger`/`webbed` (control).

> Status: **design only** — nothing here is wired yet. Pacing/gating rationale lives in `../progression.md`;
> the master cost model in `../crafting.md`. This file is the *content menu* of the weapon slot.

---

## (A) BASE tiered families — the cross-cutting spine

Six families, each spanning the full metal ladder **wood → copper → bronze → iron → steel → silver → gold → platinum**.
This is the **always-craftable** backbone (recipe `auto`): a player who never touches a special drop can still
arm up by metal tier. The **family character** is the *meaningful choice* (Lens of Triangularity) — same tier,
different feel — so the special weapons in §B read as *upgrades on a known axis*, not noise.

### Family character (the choice axis)
| Family | Character | Primary stat | Trade-off |
|---|---|---|---|
| **sword** | the all-rounder; a **wide arc** that hits a small cluster | `damage_pct` (balanced) | no standout — jack of all trades |
| **spear** | **reach**, single-target poke; keeps fast bugs spaced | `reach` | narrow (no arc); low knockback |
| **dagger** | **fast + crit**; the dodge/flank build's sidearm | `attack_speed_pct` + `crit_chance` | low base `damage_pct`, short reach |
| **mace / maul** | **knockback**, heavy & slow; staggers bruisers | `knockback` | low `attack_speed_pct` |
| **club** | the **cheap stun** starter; budget knockback + `stagger` | `knockback` (low cost) | low `damage_pct`, crude |
| **bow / sling** | **ranged**; out-spaces apexes & swarms | `reach` (ranged) | needs ammo; low per-hit `damage_pct` |

### Per-tier formula & cost
Each row below is one **family**; the cost is `{bar}×2 + wood×1` per tier. The **primary stat** scales with
tier (the listed stat is the one this family *leads* on; all families also gain flat `damage_pct` per tier).
`sword_wood` ✅ and `spear_wood` ✅ already exist — **reuse, don't recreate**.

**Tier-cost reference** (Σ input pts; identical for every family since the formula is shared):

| tier | bar | bar pts | recipe | craft cost (pts) | station |
|---|---|---|---|---|---|
| wood | — (wood ×3) | 1 | wood ×3 | **3** | anvil |
| copper | copper_bar | 3 | copper_bar ×2 + wood ×1 | **7** | anvil |
| bronze | bronze_bar | 4 | bronze_bar ×2 + wood ×1 | **9** | anvil |
| iron | iron_bar | 6 | iron_bar ×2 + wood ×1 | **13** | anvil |
| steel | steel_bar | 10 | steel_bar ×2 + wood ×1 | **21** | forge |
| silver | silver_bar | 10 | silver_bar ×2 + wood ×1 | **21** | forge |
| gold | gold_bar | 16 | gold_bar ×2 + wood ×1 | **33** | forge |
| platinum | platinum_bar | 24 | platinum_bar ×2 + wood ×1 | **49** | forge |

> Station rule: **anvil ≤ iron, forge for steel+** (matches `../crafting.md §3` — the forge is gated behind the
> anvil, so the top half of every ladder lives there).

#### sword — `sword_{tier}` (all-rounder, wide arc)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `sword_wood` ✅ | wood | anvil | wood ×3 | `damage_pct` (base) |
| `sword_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `damage_pct` |
| `sword_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `damage_pct` |
| `sword_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `damage_pct` |
| `sword_steel` | steel | forge | steel_bar ×2 + wood ×1 | `damage_pct` |
| `sword_silver` | silver | forge | silver_bar ×2 + wood ×1 | `damage_pct` (+ vs bugs) |
| `sword_gold` | gold | forge | gold_bar ×2 + wood ×1 | `damage_pct` |
| `sword_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `damage_pct` |

#### spear — `spear_{tier}` (reach, single-target)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `spear_wood` ✅ | wood | anvil | wood ×3 | `reach` |
| `spear_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `reach` |
| `spear_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `reach` |
| `spear_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `reach` |
| `spear_steel` | steel | forge | steel_bar ×2 + wood ×1 | `reach` |
| `spear_silver` | silver | forge | silver_bar ×2 + wood ×1 | `reach` |
| `spear_gold` | gold | forge | gold_bar ×2 + wood ×1 | `reach` |
| `spear_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `reach` |

#### dagger — `dagger_{tier}` (fast + crit)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `dagger_wood` | wood | anvil | wood ×3 | `attack_speed_pct` + `crit_chance` |
| `dagger_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_steel` | steel | forge | steel_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_silver` | silver | forge | silver_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_gold` | gold | forge | gold_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |
| `dagger_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `attack_speed_pct` + `crit_chance` |

#### mace / maul — `mace_{tier}` (knockback, slow)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `mace_wood` | wood | anvil | wood ×3 | `knockback` |
| `mace_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `knockback` |
| `mace_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `knockback` |
| `mace_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `knockback` |
| `mace_steel` | steel | forge | steel_bar ×2 + wood ×1 | `knockback` |
| `mace_silver` | silver | forge | silver_bar ×2 + wood ×1 | `knockback` |
| `mace_gold` | gold | forge | gold_bar ×2 + wood ×1 | `knockback` |
| `mace_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `knockback` |

#### club — `club_{tier}` (cheap stun)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `club_wood` | wood | anvil | wood ×3 | `knockback` + on-hit `stagger` |
| `club_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_steel` | steel | forge | steel_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_silver` | silver | forge | silver_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_gold` | gold | forge | gold_bar ×2 + wood ×1 | `knockback` + `stagger` |
| `club_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `knockback` + `stagger` |

#### bow / sling — `bow_{tier}` (ranged)
| id | tier | station | inputs | primary stat |
|---|---|---|---|---|
| `bow_wood` | wood | anvil | wood ×3 | `reach` (ranged) |
| `bow_copper` | copper | anvil | copper_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_bronze` | bronze | anvil | bronze_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_iron` | iron | anvil | iron_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_steel` | steel | forge | steel_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_silver` | silver | forge | silver_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_gold` | gold | forge | gold_bar ×2 + wood ×1 | `reach` (ranged) |
| `bow_platinum` | platinum | forge | platinum_bar ×2 + wood ×1 | `reach` (ranged) |

> Note: the lowest sling/bow tier may instead be a `loom`-leaning `wood + fiber` build (cf. `item_catalog.md §3`,
> "slingshot/bow = wood + fiber"); kept on the metal ladder here for one consistent formula. Ammo (arrows/shot)
> is a cheap consumable — out of scope for this catalog (tracked with `culler_charge`-style ammo).

**Base count: 6 families × 8 tiers = 48** (2 already exist: `sword_wood`, `spear_wood`).

---

## (B) SPECIAL / bug-themed weapons — indexed by zone

Each is gated behind a zone's species/boss drops. Effects come from those drops: **venom** (the spider/scorpion/
centipede/wasp line → `envenomed`/`poisoned` DoT), **fire** (`fire_ant_gland` → `scorched`), **acid** (`formic_acid`/
`acid_crystal` → `corroded`/`acid_burn` armor-shred), **AoE-vs-swarm** (`mantis_scythe`/`army_ant_mandible` → cleave),
and **horn/blunt** (`stag_horn`/`rhino_horn` → big `knockback`). "Obtain": `craft` = build it (recipe `auto`);
`buy@npc` = learn recipe from that zone's vendor; `find` = rare cache/scroll, *not sold*.

### Wasp Thicket (T2)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `venom_dagger` | T2 | forge | `damage_pct +12`, `attack_speed_pct +10`, **on-hit `poisoned`** (DoT) — marquee venom blade | buy@thicket_vendor (recipe) |
| `stinger_spear` | T2 | forge | `damage_pct +18`, `knockback +1`, **longer reach** (anti-swarm spacing) | find@wasp_thicket (matriarch-chamber scroll) |
| `venom_coat` | T2 | cauldron | weapon **coating** (consumable) — adds `poisoned` on-hit for a window; any blade goes venom-tipped | auto (cauldron + zone access) |

### Ant Colony (T2→T3)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `acid_flask` | T2→T3 | cauldron | **thrown** AoE `acid_burn` (armor-chip DoT) on soldier swarms — the anti-guard answer | find@ant_colony (recipe) / craft |

### Meadow (T3)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `hornet_lance` (spear) | T3 | forge | `damage_pct +20`, `knockback +1`, **long reach**, on-hit `poisoned` — anti-hornet-swarm | find@meadow (hornet-nest scroll) |

### Scorpion Rocks (T3)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `scorpion_pick` (war-pick) | T3 | forge | `damage_pct +20`, `crit_chance +6`, **on-hit `envenomed`**; doubles as a light digging tool | find@scorpion_rocks (recipe scroll) |
| `venom_oil` | T3 | cauldron | weapon **coating** — strong `envenomed` on-hit for a window (scorpion-tier) | auto (cauldron + zone access) |

### Centipede Cavern (T3→T4)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `centipede_fang_blade` (fast venom sword) | T3 | forge | **`attack_speed_pct +20`**, `damage_pct +14`, `crit_chance +6`, on-hit `envenomed` — the agile-venom blade | find@centipede_cavern (deep-den scroll) |
| `venom_lash` (whip, reach) | T3→T4 | forge | `damage_pct +22`, `knockback +1`, **long reach**, strong `envenomed` — apex venom weapon (needs `potent_centipede_venom`) | buy@hermit (recipe) |
| `venom_oil` (centipede) | T3 | cauldron | weapon **coating** — `envenomed` on-hit (centipede-venom tier) | auto (cauldron + zone access) |

### Shallow Swamp (T3)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `harpoon_spear` | T3 | anvil | long-reach `spear` vs water bugs; **doubles as fishing** | buy@swamp_vendor |

### Spider Vale West (T4)
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `fang_dagger` (light, fast) | T4 | forge | `damage_pct +18`, `attack_speed_pct +12`, `crit_chance +6`, **on-hit `envenomed`** — the dodge-build blade | find@spider_vale_west (recipe scroll) |
| `venom_glaive` (reach polearm) | T4 | forge | `damage_pct +24`, `knockback +1`, **long reach** (anti-rush), strong `envenomed` | buy@hunters_lodge (recipe) |
| `paralytic_coating` | T4 | cauldron | weapon **coating** — on-hit **slow/`webbed`-lite** (paralytic, control) for a window | craft |
| `venom_oil` ✅ (spider) | T4 | cauldron | weapon **coating** — strong `envenomed` on-hit (spider-venom tier) | auto (cauldron + zone access) |

### Spider Vale East (T5) — top surface venom tier
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `widowfang_blade` (marquee venom sword) | T5 | forge | `damage_pct +30`, `crit_chance +8`, `crit_mult +0.4`, **heavy stacking `envenomed`** (strongest on-hit venom in the game) | **find@spider_vale_east** (rare lair scroll — *not sold*) |
| `silk_repeater` (venom crossbow, ranged) | T5 | forge | `damage_pct +22`, `attack_speed_pct +15`, **ranged**, bolts carry `envenomed` — out-spaces web ambush | buy@scavenger_camp (recipe); a salvaged unit also sold pre-made |
| `venom_draught` | T5 | cauldron | weapon **coating** — heavy `envenomed` on-hit (widow-tier) for a window | craft (cauldron + zone access) |

### Locust Farmland (T4–T5) — anti-swarm
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `swarm_culler` (AoE swarm weapon) | T5 reach | forge | wide-arc AoE that scales `damage_pct` **vs swarm density**, `knockback +3` — the marquee swarm-clear (uses `mantis_scythe`) | craft (buy recipe) |
| `harvest_sickle` (swarm-harvest tool/weapon) | T4 | anvil | `bug_value_pct +15` & `catch_cap +20` **vs swarm bugs**; harvests scattered swarm fast (uses `beetle_mandible`) | craft |
| `culler_charge` | T4 | forge | **ammo** — recharges the `swarm_culler` AoE blast | craft |
| `locust_oil` | T4 | cauldron | weapon **coating** — `damage_pct` vs swarms (also food fat / fuel) | craft |

### Millipede Forest (T4→T5) — the stag-horn melee
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `stag_horn_maul` (heavy mace) | T4 | forge | **`damage_pct +24`**, **`knockback +3`**, slow heavy swing — the iconic horn weapon (gores & tosses beetles) | find@millipede_forest (deep-grove scroll) |
| `horned_glaive` (reach polearm) | T4 | forge | `damage_pct +20`, `crit_chance +6`, **long reach**, on-hit `poisoned` (fang-tipped) | buy@ranger_station (recipe) |
| `rhino_breaker` (apex maul) | T4→T5 | forge | `damage_pct +30`, `knockback +4`, **armor-break on charge** — the upgraded horn weapon (needs `rhino_horn` + `silver_bar`) | find (apex-area scroll) |
| `barbed_dagger` (off-hand) | T4 | anvil | `attack_speed_pct +15`, `crit_chance +5`, `thorns +2`, on-hit `poisoned` — the quick venom off-hand | craft |
| `steel_axe` (felling axe / weapon) | T4 | anvil | `chop_speed_pct +30`, `damage_pct +12` — premium axe that doubles as a weapon (uses `stag_horn` grip) | buy@ranger_station (recipe) / craft |
| `venom_coat` (forest) | T4 | cauldron | weapon **coating** — `poisoned` on-hit (fang-tipped) for a window | craft |

### Deep Swamp (T4) — disease/venom & anti-apex
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `nymph_glaive` (reach polearm) | T4 | forge | long-reach polearm vs water bugs: high `damage_pct` vs aquatic/arthropod, `knockback +2`, light `venom` (uses `nymph_jaw`) | find (apex-area drop recipe) |
| `toebiter_maul` (heavy anti-apex) | T4 | forge | slow, heavy `knockback +3`, big `damage_pct`, **stuns predators** — the anti-apex maul (uses `giant_waterbug_carapace`) | buy@hermit (gated: apex slain) |
| `venom_coating` | T4 | cauldron | weapon **coating** — strong `venom` DoT on-hit for a window (uses `waterbug_venom_gland`) | find |
| `fever_bomb` (thrown) | T4 | cauldron | **thrown** AoE `swamp_fever`/poison cloud vs bugs (disease-as-weapon) | find / buy@hermit |

### Underground River (T3–T4) — cave-fishing / anti-apex pincer
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `cave_harpoon` (spear-fishing / light weapon) | T3 | anvil | long-reach spear-fishing tool that **doubles as a light melee weapon**; `catch_radius +3` over water (uses `crayfish_claw`) | buy@fisher |

> (Underground River's `crab_claw` is a flagged **anti-apex weapon component** for the apex/`divers_carapace`
> line; the finished blade isn't named in the zone doc — listed as a hook, not a counted weapon.)

### Deadly Ants (T4–T5) — the fire / acid / venom endgame
| id | tier | station | key stat / effect | obtain |
|---|---|---|---|---|
| `firebrand_blade` (fire endgame sword) | T5 | forge | `damage_pct +34`, `crit_chance +8`, **on-hit `scorched`** (fierce burn DoT) + leaves a brief `ignited` floor on crit — the marquee fire weapon | **find@deadly_ants** (scorched cache — *not sold*) |
| `acid_lance` (acid pierce) | T4→T5 | forge | `damage_pct +28`, `crit_chance +10`, **long reach**, **on-hit `corroded`** (shreds enemy `defense`) — answers armored soldiers | buy@exterminators_base (recipe) |
| `mandible_maul` (swarm-breaker AoE) | T4→T5 | forge | `damage_pct +24`, **wide cleave AoE** + `knockback +2` — built to break the `army_ant` river (uses `army_ant_mandible`) | buy@exterminators_base (recipe) |
| `bullet_sting_dagger` (venom-crit sidearm) | T5 | forge | `damage_pct +20`, **`crit_chance +14`, `crit_mult +0.4`**, on-hit strong `envenomed` — high-crit endgame sidearm | **find@deadly_ants** (rare scroll) |
| `inferno_coating` | T4 | cauldron | weapon **coating** — strong `scorched` on-hit for a window; upgrades any blade to fire-tier | auto (cauldron + zone access) |

### Zones with NO weapons (peaceful / non-combat)
`bee_meadow`, `butterfly_fields`, `village` — pollination/farming/town hubs; no offense content (correct by design).

---

## Totals

| Layer | Count |
|---|---|
| **(A) Base tiered families** — 6 families × 8 tiers | **48** |
| **(B) Special / bug-themed weapons** (incl. coatings & throwables — the weapon *slot* content) | **34** |
| **TOTAL** | **82** |

### Special-weapon breakdown by category (the 34)
- **Pure melee/ranged weapons (24):** `venom_dagger`, `stinger_spear`, `hornet_lance`, `scorpion_pick`,
  `centipede_fang_blade`, `venom_lash`, `harpoon_spear`, `fang_dagger`, `venom_glaive`, `widowfang_blade`,
  `silk_repeater`, `swarm_culler`, `harvest_sickle`, `stag_horn_maul`, `horned_glaive`, `rhino_breaker`,
  `barbed_dagger`, `steel_axe`, `nymph_glaive`, `toebiter_maul`, `cave_harpoon`, `firebrand_blade`,
  `acid_lance`, `mandible_maul`, `bullet_sting_dagger` — *(25; the count above folds `steel_axe`/`harvest_sickle`
  as tool-weapons)*.
- **Weapon coatings (consumable buffs, 8):** `venom_coat` (thicket), `venom_oil` (scorpion / centipede /
  spider — one shared id refreshed per zone), `paralytic_coating`, `venom_draught`, `locust_oil`,
  `venom_coat` (forest), `venom_coating` (deep_swamp), `inferno_coating`.
- **Thrown / ammo (3):** `acid_flask`, `fever_bomb`, `culler_charge`.

> If coatings/throwables/ammo are scored as *consumables* rather than *weapons*, the pure-weapon special count
> is **~24** and the grand total **~72**. Counted generously here (the brief: "be exhaustive — prune later").

### Coverage notes for pruning later
- **`venom_oil`** appears in three zones (scorpion / centipede / spider) as **one shared coating id** refreshed
  to the local venom — counted once conceptually; the rows show where it's earned.
- **Effect coverage is complete:** venom/poison (wasp→spider→ant lines), fire (`firebrand_blade`/`inferno_coating`),
  acid/armor-shred (`acid_flask`/`acid_lance`/`mandible_maul`), AoE-vs-swarm (`swarm_culler`/`mandible_maul`),
  blunt/horn knockback (`stag_horn_maul`/`rhino_breaker`/`toebiter_maul`), ranged (`silk_repeater`/`bow_*`),
  control/paralytic (`paralytic_coating`).
- **Tier coverage:** T2 (thicket/ant) → T3 (meadow/scorpion/centipede/swamp/river) → T4 (vales/forest/deep_swamp/
  locust) → T5 (spider_vale_east/deadly_ants) — a clean special ladder layered over the base metal spine.
