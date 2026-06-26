# Zone Content Sheet — Wasp Thicket

> **Grid (2,2)** · dense brush east of the river · **difficulty MEDIUM** · **tier T2 (copper/bronze era)**
>
> The **combat intro zone**. The river behind you is the soft boundary between the safe starting village and
> the first place that *fights back*. The Thicket is a tangle of brambles, paper-wasp nests slung in the
> branches, and mud-dauber burrows in the clay banks — your first real encounters with **venom, stingers, and
> swarms**, and therefore the debut of **defensive/thorns gear, anti-sting protection, and venom-tipped
> weapons**. Everything here is gated to **T2** so it lands right after the player has copper/bronze tools but
> before iron — the "I can fight now, carefully" beat.
>
> **Design intent (pacing, per `../README.md`):** this zone teaches *preparation beats reflexes*. You don't
> out-twitch a wasp swarm; you show up with anti-sting gear, an antidote, and a venom-tipped weapon, and then
> it's manageable. Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

---

## Species & drops

Five concrete species span the difficulty curve of the zone — two trash-tier swarmers, two mid threats, and a
mini-boss nest. Behaviors are written to slot into the existing 6-species ecology vocabulary (the Thicket
leans on the **wasp** archetype already in the food web) without requiring new sim primitives.

| Species (id) | Tier feel | Behavior | Primary drop | Secondary drop(s) |
|---|---|---|---|---|
| `paper_wasp` | core threat | Nest-anchored. Patrols a radius around its `paper_nest`; **swarms (calls 2–4 nestmates)** when the player gets within sting range or strikes a nestmate. Fast, low HP, **stings inflict the `poisoned` debuff** (small DoT). | `wasp_stinger` ✅ | `venom_sac` (uncommon), `dead_wasp` ✅ |
| `mud_dauber` | solitary bruiser | Burrow-anchored in the clay banks. **Solitary, does NOT swarm** but hits harder and has more HP than a paper wasp; slower, telegraphs a lunging sting. Drops the clay it builds with. | `mud_dauber_clay` | `venom_sac` (uncommon), `dead_wasp` ✅ |
| `earwig` | ground harasser | Skitters along the brush floor, **flanks** (approaches from behind), pincer melee — **no venom**, but applies **knockback** and is annoyingly evasive (high dodge). Comes in small clusters. | `earwig_pincer` | `chitin` (common), `dead_centipede` ✅ (reuse — segmented ground bug) |
| `silverfish` | nuisance / forager | Fast, fragile, **flees** the player; nests in leaf-litter and **eats fallen flora/fiber** (light ecology pressure on the zone's gatherables). Worth chasing for its scales. | `silverfish_scale` | `fiber` ✅ (regurgitated), `dead_fly` ✅ (reuse — tiny skittering bug) |
| `thicket_matriarch` | **mini-boss** (nest queen) | The **signature fight**. A bloated paper-wasp queen anchored to the **great nest** at the zone's heart. Stationary-ish; **continuously spawns paper_wasp adds** from the nest until the nest is destroyed, then she descends and fights directly with a heavy venom sting + an AoE "sting cloud". | `royal_venom` (guaranteed, 1–2) | `paper_nest` ✅ (×3–5), `wasp_larvae` ✅ (×2–4), `matriarch_trophy` (rare décor) |

**Drop notes**
- `wasp_stinger`, `paper_nest`, `wasp_larvae`, `dead_wasp`/`dead_centipede`/`dead_fly`, `chitin`, `fiber` are
  **existing ids** — reused, not reinvented.
- `venom_sac` is the **mid-grade venom material** (uncommon off both wasp species); `royal_venom` is its
  **rare/upgraded** form, gated behind the mini-boss — this gives venom recipes a clean two-tier supply.
- `matriarch_trophy` is a rare décor/idle-aura piece (a mounted nest-queen trophy), the "I beat the zone" flex.

---

## New ingredients / gatherables

Venom-, nest-, and brush-themed gatherables you **harvest from the environment** (not bug drops). These give
the zone non-combat reasons to explore and feed the recipe list below.

| Id | Source (find@wasp_thicket) | Use |
|---|---|---|
| `bramble_vine` | Cut from the dense thornbushes that wall the Thicket (tool: any blade/scythe). Common. | Cordage + the **thorns** mechanic — core input to thicket armor & traps. |
| `wasp_paper` | Scraped off **abandoned** (empty) paper nests on the ground. Common. | A light papery fiber — bandages, the antidote filter, light armor padding. (Distinct from `paper_nest`, which is the looted full-nest drop.) |
| `nettle_leaf` | Picked from stinging-nettle clumps in the brush (stings you slightly if picked bare-handed — costs a sliver of HP, or 0 with gloves equipped). Common. | The poison/irritant flora — feeds both the **poison potion** and, when boiled, the **antidote** (counter-irritant). |
| `clay` ✅ | Dug from the **mud-dauber clay banks** along the river edge (reuse existing `clay`). | Reuse — bricks, the mud-dauber-themed gear, ties this zone into existing clay supply. |
| `resin_glob` | Tapped from wounded brush-trees / sap pockets in the thicket. Uncommon. | Sticky binder — venom-coating adhesive (makes venom *stick* to a blade), glue for traps, a waterproofing for armor. |

> **Why these three+ new ones:** `bramble_vine` powers the thorns theme, `nettle_leaf` powers the
> poison/antidote pair, `resin_glob` is the binder that lets venom become a *weapon coating* (and seeds later
> alchemy). `wasp_paper` rounds out a light-armor/bandage thread. All are T1–T2 cheap (cost-point 1) so they
> stay accessible.

---

## Recipes debuting here

Seven recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model from the brief; everything is **gated T2**.

### Weapons — venom-tipped

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `venom_dagger` | forge | `bronze_bar` ×2, `wood` ×1, `venom_sac` ×2, `resin_glob` ×1 | buy@thicket_vendor (recipe) | `damage_pct +12`, `attack_speed_pct +10`, **on-hit applies `poisoned` DoT** | T2 |
| `stinger_spear` | forge | `bronze_bar` ×2, `bramble_vine` ×3, `wasp_stinger` ×4 | find@wasp_thicket (recipe scroll, matriarch chamber) | `damage_pct +18`, `knockback +1`, longer reach (anti-swarm spacing) | T2 |
| `venom_coat` (consumable buff) | cauldron | `venom_sac` ×1, `resin_glob` ×1, `nettle_leaf` ×2 | auto (once cauldron + thicket access) | **Coats your current weapon** — adds `poisoned` on-hit for a duration. Lets ANY weapon go venom-tipped. | T2 |

### Anti-sting / defensive gear (the non-set utility pieces — the **signature set** is its own section)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `padded_gloves` | loom | `wasp_paper` ×3, `cloth` ×2, `fiber` ×4 | auto@loom | `sting_immunity +1` (partial), lets you pick `nettle_leaf` HP-free; small `defense +1` | T2 |
| `clay_buckler` (shield/accessory) | workbench | `clay` ×4, `bronze_bar` ×1, `bramble_vine` ×2 | buy@thicket_vendor | `defense +3`, `knockback resist`, `thorns +1` | T2 |

### Potions / consumables (the poison/antidote pair + a combat consumable)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `antidote` | cauldron | `nettle_leaf` ×2, `wasp_paper` ×1, `mushroom_brown` ×1 | buy@thicket_vendor (recipe) | **Cures `poisoned`** + grants short `hazard_resist` (resists new venom). The answer to the zone. | T2 |
| `poison_vial` (thrown consumable) | cauldron | `nettle_leaf` ×3, `venom_sac` ×1, `resin_glob` ×1 | find@wasp_thicket (recipe scroll) | **Throwable** — AoE `poisoned` cloud on enemies; great vs swarms/the matriarch adds. | T2 |
| `nettle_salve` (combat consumable) | cauldron | `nettle_leaf` ×2, `yarrow` ×1, `wasp_paper` ×1 | auto@cauldron | Short buff: `hp_regen +1` + `thorns +1` (skin irritant) — a cheap pre-fight prep item. | T2 |

> **Supply logic:** `venom_sac` (uncommon drop) is the bottleneck on offense; `nettle_leaf`/`wasp_paper`
> (common gatherables) keep the *defensive* answers (antidote, gloves) cheap and always craftable — so a
> careful player is never *locked out* of survival, only of the spicy venom weapons. `royal_venom` (mini-boss)
> is held in reserve for a T3 venom upgrade in the next zone, so the Thicket's drop has a forward hook.

---

## Signature gear — the **Thornweave Hunter** set (T2 bonus set)

A 3-piece thicket-hunter armor set: woven bramble + wasp-paper + bronze studs. Theme = **the hunter who turns
the brush's own defenses against the bugs**. Pure T2. Built at the **anvil** (studs) + **loom** (weave); a
clean mixed-station set that shows off the bramble/thorns identity.

| Piece (id) | Slot | Station | Inputs | Bonuses |
|---|---|---|---|---|
| `thornweave_hood` | head | loom | `wasp_paper` ×4, `cloth` ×2, `bramble_vine` ×2 | `defense +2`, `sting_immunity +1`, `night_vision` (brush is dark) |
| `thornweave_vest` | body | loom | `bramble_vine` ×4, `cloth` ×3, `bronze_bar` ×2, `chitin` ×2 | `defense +4`, `thorns +2`, `max_hp +5` |
| `thornweave_greaves` | legs | anvil | `bronze_bar` ×2, `bramble_vine` ×3, `clay` ×2 | `defense +3`, `thorns +1`, `move_speed_pct +4` (brush-runner) |

**Set bonus (`set: thornweave`, all 3 worn):**
- **+`thorns +3`** (stacks — total thorns becomes punishing for swarms),
- **full `sting_immunity`** (wasp/dauber stings can no longer apply `poisoned`),
- **+`damage_pct +8` vs bugs in brush/thicket tiles**.
- **Fantasy realized:** fully kitted, you can stand inside a paper-wasp swarm and let `thorns` shred them while
  immunity eats their stings — the zone's swarm goes from lethal to farmable. That power spike is the reward
  for clearing the content.

**Unlock:** hood + greaves recipes **auto** at their stations (you can grind the set yourself); the **vest**
recipe is **bought from the thicket vendor** OR **dropped by the `thicket_matriarch`** (mini-boss) — so the
keystone piece rewards either the merchant loop or the boss fight.

> Optional matching accessory: `stinger_pendant` (jeweler — `wasp_stinger` ×6, `silver_bar` ×1, `quartz` ×1):
> `crit_chance +5`, `rare_bug_luck +1`. A T2→T4 bridge accessory (needs a `silver_bar`, so it's a stretch
> goal that keeps the zone relevant a little longer).

---

## Shop / NPC stock — **the Thicket Trapper** (`thicket_vendor`)

A grizzled bug-hunter camped at the river-ford trailhead (the safe edge of the zone). She's the **combat-supply
NPC**: she buys your stingers/venom and sells the *preparation* you need to survive deeper in. Currency =
coins (existing). Acts as the gate that teaches "stock up before you push in."

**Sells (buy@thicket_vendor):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `antidote` | consumable | 25 | Cures `poisoned`. Stock-limited daily (forces gathering too). |
| `recipe: antidote` | recipe | 120 | So you can craft your own thereafter. |
| `recipe: venom_dagger` | recipe | 250 | The marquee weapon recipe. |
| `recipe: clay_buckler` | recipe | 150 | Defensive accessory. |
| `recipe: thornweave_vest` | recipe | 400 | The keystone set piece (alt path to the boss drop). |
| `padded_gloves` | gear | 90 | Pre-made, so you can pick nettles safely before crafting your own. |
| `smoke_pouch` | consumable | 40 | **New** thrown item — `calm_radius` AoE: briefly pacifies a wasp swarm (beekeeper trick). Buy-only here. |
| `bronze_bar` | material | 30 | Convenience restock of the era's metal (small daily cap). |

**Buys (sell to vendor — gives the zone a sink):** `wasp_stinger`, `venom_sac`, `mud_dauber_clay`,
`silverfish_scale`, `earwig_pincer`, `paper_nest`, `wasp_larvae` — with a **`bug_value_pct` premium** on venom
materials (she pays well for venom, reinforcing the combat loop).

---

## "New toys" hook

The Wasp Thicket is where BugFarmer stops being a peaceful farm sim for an afternoon and hands you your **first
real fight** — venom that actually hurts, swarms that gang up, and a nest-queen mini-boss at the heart of the
brush. The new toys are all about *answering* that threat: a **venom-tipped dagger** and a thrown **poison
vial** to turn the bugs' own poison against them, an **antidote** and **anti-sting gloves** so the stings stop
mattering, and the **Thornweave Hunter set** whose `thorns` + `sting_immunity` set bonus lets you eventually
stand inside a swarm and farm it. Beat the `thicket_matriarch` and you walk out with `royal_venom` — the seed
of the next zone's nastier weapons — plus a trophy for the wall.

---

## New id ledger

**materials:**
- `venom_sac` — uncommon drop, paper_wasp / mud_dauber (mid venom material)
- `royal_venom` — guaranteed drop, thicket_matriarch (rare/upgraded venom; forward hook to T3)
- `mud_dauber_clay` — drop, mud_dauber
- `silverfish_scale` — drop, silverfish
- `earwig_pincer` — drop, earwig
- `bramble_vine` — find@wasp_thicket (thornbush cordage; thorns theme)
- `wasp_paper` — find@wasp_thicket (light papery fiber; bandages/padding)
- `nettle_leaf` — find@wasp_thicket (irritant flora; poison + antidote)
- `resin_glob` — find@wasp_thicket (sticky binder; venom coating/glue)
- `matriarch_trophy` — rare décor drop, thicket_matriarch

**species:** (id → primary drop)
- `paper_wasp` → `wasp_stinger` ✅ (also `venom_sac`)
- `mud_dauber` → `mud_dauber_clay` (also `venom_sac`)
- `earwig` → `earwig_pincer`
- `silverfish` → `silverfish_scale`
- `thicket_matriarch` → `royal_venom` (mini-boss; also `paper_nest`/`wasp_larvae`/`matriarch_trophy`)

**items:**
- `venom_dagger` — weapon, forge, T2 — damage_pct/attack_speed + on-hit poisoned
- `stinger_spear` — weapon, forge, T2 — damage_pct/knockback, long reach (anti-swarm)
- `venom_coat` — consumable buff, cauldron, T2 — coats any weapon with on-hit poison
- `padded_gloves` — armor (hands), loom, T2 — partial sting_immunity, safe nettle-picking
- `clay_buckler` — shield/accessory, workbench, T2 — defense/knockback-resist/thorns
- `antidote` — consumable, cauldron, T2 — cures poisoned + hazard_resist
- `poison_vial` — thrown consumable, cauldron, T2 — AoE poisoned cloud
- `nettle_salve` — combat consumable, cauldron, T2 — hp_regen + thorns buff
- `thornweave_hood` — armor (head), loom, T2 — defense/sting_immunity/night_vision; set: thornweave
- `thornweave_vest` — armor (body), loom, T2 — defense/thorns/max_hp; set: thornweave (keystone)
- `thornweave_greaves` — armor (legs), anvil, T2 — defense/thorns/move_speed; set: thornweave
- `stinger_pendant` — accessory, jeweler, T2→T4 bridge — crit_chance/rare_bug_luck
- `smoke_pouch` — thrown consumable, buy@thicket_vendor, T2 — calm_radius AoE (pacify swarm)
- `thicket_vendor` — NPC ("the Thicket Trapper") — combat-supply shop at the river-ford
