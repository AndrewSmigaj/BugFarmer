# Zone Content Sheet — Centipede Cavern

> **Grid (4,1)** · a deep underground stalactite hall — glowworm-lit galleries, dripstone columns,
> crystal-veined walls far below the surface · **difficulty HARD** · **tier T3→T4 (iron era, reaching
> toward steel)**
>
> The **deep-cavern + bioluminescent-light + potent-centipede-venom** zone. Below the rock zones the world
> drops into a true cave: lightless stalactite halls where the only glow is the **glowworms** strung across
> the ceiling, fast **giant centipedes** flanking out of the dark, **cave beetles** trundling the floor, and
> **camel crickets** springing off the walls. This is where **GLOWWORM LIGHT** debuts as the **best natural
> light source in the game**, where **centipede venom** anchors a fast/agile venom-weapon tier, where **crystal
> formations** pay off into accessories, and where the **Hermit researcher** — a lantern-bearded recluse who
> studies the deep — trades **rare specimens and recipes**. Everything is gated **T3** (a few pieces reach a
> `steel_bar`/gem as a stretch toward T4) so it lands once the player has iron tools and is reaching for steel.
>
> **Design intent (pacing, per `../README.md` + `../progression.md` §"Mid"):** this zone teaches *seeing in
> the deep dark and out-fighting fast venom*. You don't brute-force the cavern blind — you harvest **glowworm
> lumen** for the best light in the game, brew the deep-cavern potions that give `night_vision` + `hazard_resist`
> (the cave-damp/spore answer), forge a fast **centipede venom** weapon to trade blows with the skittering
> hunters, and cut the wall crystals into a `light`/`crit` accessory. Then the lightless hall becomes a generous
> glow-crystal-and-venom farm. Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat vocab +
> `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T3 "Mid" / iron reaching steel); shop seam from
> [`../merchants.md`](../merchants.md) (realized here as the **Hermit researcher** — a rare-specimen/recipe
> vendor in the deep). World-guide species: giant centipedes, cave beetles, glowworms, camel crickets.

---

## Species & drops

Five concrete species span the difficulty curve — the lit-ceiling light source, a wall-springing harasser, a
passive floor tank, the fast venom threat, and a den apex. Behaviors slot into the existing arthropod ecology
vocabulary (anchor-and-patrol, flank, flee, swarm, curl/armor) without new sim primitives. The signature theme
is **bioluminescent light** (glowworm `glowworm_lumen` — the best natural light material) paired with **potent,
fast centipede venom**.

| Species (id) | Tier feel | Behavior | Primary drop | Secondary drop(s) |
|---|---|---|---|---|
| `giant_centipede` | **signature threat / fast venom** | The zone's signature bug. A long, fast, aggressive ground hunter that **flanks out of the dark, bites with venom forcipules** (applies a strong `envenomed` DoT — hotter than the surface centipede's `poisoned`), then **retreats and re-flanks**. Hits, skitters, circles — the "don't get surrounded in the dark" pressure. Fast, low-armor, telegraphed lunge. | `centipede_venom_gland` ✅(new) | `centipede_parts` ✅, `chitin` ✅, `dead_centipede` ✅ |
| `glowworm` | **light source / passive** | Strung in colonies across the cavern **ceiling**, glowworms are the cavern's light: their hanging silk lines glow blue-green, and harvesting a colony yields **`glowworm_lumen`** — the **best natural light material in the game**. Harmless, doesn't flee far (a *reach-up gather*, not a fight); the colony **dims and re-lights** as you harvest. The reason the deep is navigable at all. | `glowworm_lumen` ✅(new) | `glow_silk` (the luminous hanging thread), `dead_glowworm` (new `dead_*`) |
| `cave_beetle` | core / passive-tank | A blind, glossy **floor beetle** that trundles the dripstone in slow trains grazing cave moss & fungus. **Curls under its thick wing-case when struck** (heavy `defense`, little offense); a *patience/armor* catch. The deep's chitin/carapace source — the plate the delver set is built from. | `cave_beetle_carapace` ✅(new) | `chitin` ✅, `dead_beetle` ✅ |
| `camel_cricket` | swarm / harasser | Pale, long-legged **spider-crickets** that cling to the walls and **spring in erratic leaps** toward (or away from) you — a jittery chip-harasser that's hard to pin, not a heavy hitter. A *cluster* catch off a disturbed wall. Fragile individually, but the source of the spring-leg cordage and a light ecology pressure on the cave flora. | `camel_cricket_leg` ✅(new) | `chitin` ✅, `dead_cricket` (new `dead_*`) |
| `centipede_matron` *(apex)* | **mini-boss** (centipede brood) | The zone's apex — a bloated, segment-armored **brood-mother centipede** anchored to the **great crevice den** at the cavern's heart. Stationary-ish; **continuously spawns `giant_centipede` adds** from the den until it's destroyed, then descends to fight directly with a heavy `envenomed` bite + a skittering charge through the dark. The real fight — the keystone potent-venom source. | `potent_centipede_venom` (guaranteed, 1–2 — the apex venom) | `matron_forcipule` (rare — heavy fang trophy), `centipede_parts` ✅ (×2–4), `dead_centipede` ✅ |

**Drop notes**
- `centipede_venom_gland`, `cave_beetle_carapace`, `glowworm_lumen`, `camel_cricket_leg` are the **four
  brief-required new drops** — each species-signature.
- **Two-tier venom supply** (mirrors the scorpion zone's `scorpion_venom`→`potent_venom`): `centipede_venom_gland`
  (common-ish, off `giant_centipede`) → `potent_centipede_venom` (the **apex venom**, gated behind the
  `centipede_matron` mini-boss). `potent_centipede_venom` is the keystone weapon input and the forward hook into T4.
- `centipede_parts` ✅, `chitin` ✅, `dead_centipede` ✅, `dead_beetle` ✅ are **existing ids** — reused (the
  cavern is where the existing `centipede_parts`/`chitin` finally pay off into real gear). `dead_glowworm` /
  `dead_cricket` are new carcasses in the existing `dead_*` family.
- `glow_silk` (luminous thread), `matron_forcipule` (apex fang trophy) round out the tables — the glow-textile
  line and the boss flex.

**Drop → use at a glance**
- `glowworm_lumen` → the **best natural light** gear/items (lantern, lamp, set inlay) — the zone's headline.
- `glow_silk` → a luminous thread/textile (loom): glow-trim cloth, the light-décor line, a soft set underweave.
- `centipede_venom_gland` → the fast venom weapons + a venom coating (this zone's offense).
- `potent_centipede_venom` → the marquee apex venom weapon + the forward hook into the next tier.
- `cave_beetle_carapace` → the **Deep Delver** armor plating (the cavern's bug-derived set).
- `camel_cricket_leg` → springy cordage → the delver's harness/boots (`fall_resist`, leap/`move_speed`).
- `centipede_parts` ✅ / `chitin` ✅ → the set underweave, the venom dagger, segmented flex-plate.
- `matron_forcipule` → a heavier venom-weapon variant + a wall trophy.

---

## New ingredients & materials

Glow-, crystal-, and cave-themed gatherables you **mine, forage, or strip from the deep environment** (not bug
drops). They carry the bioluminescent-cavern identity and feed the recipe list. Source = `mine` (break a
node/vein), `forage` (pick), `strip` (lichen/moss off rock). Cost-points per the model (raw stone/crystal/fiber
class = 1–2 unless noted).

| Id | Source (find@centipede_cavern) | Cost-pt | Use |
|---|---|---|---|
| `glow_crystal` | mine — luminous blue-green crystal clusters studding the deep walls (a glowing cousin of `crystal`/`quartz`). Uncommon. | 2 | The signature **light crystal**: cut at the **jeweler** into `cut_glow_crystal` for the glow accessory & lamp inlays; pairs with `glowworm_lumen` for the best sustained light. The cavern's `light`/`crit` payoff node. |
| `cut_glow_crystal` | craft (jeweler: `glow_crystal` ×2 + an etch agent) | 3 | The **gem-cut** intermediate — a polished, faceted light-crystal for the glow accessory, the lantern lens, and set inlays. |
| `cave_crystal_geode` | mine — cracked-open nodules in the deep veins (yields raw `crystal`/`quartz`/`glow_crystal` inside). Uncommon. | 2 | Cracked at the **stonecutter/jeweler** for `crystal`/`quartz`/`glow_crystal`; the zone's `gem_luck` node — the "bring a fortune pick down here" tease. |
| `dripstone` | mine — the stalactite/stalagmite dripstone columns & flowstone (a fine, banded cave limestone). Common. | 1 | The signature **building stone**: stonecutter blocks/paths/columns, the cavern-shelter décor, and a lime/flux. Cuts at the **stonecutter**. |
| `cave_moss` ✅ | strip/forage — the soft luminescent-tinged moss matting the damp rock (reuse existing `cave_moss`). Common. | 1 | Reuse — a cheap green/glow dye & binder, a poultice base for the **damp-rot answer** salve, a décor moss, and a `light`-softening trim. |
| `mushroom_glow` ✅ | forage — clustered bioluminescent cave mushrooms on the flowstone & deadfall (reuse existing `mushroom_glow`). Common. | 1 | Reuse — the **glow-fungus alchemy** workhorse: the deep-cavern potion's `night_vision`/glow reagent, a cooking ingredient, and a soft `light` food garnish. |
| `cave_nitre` | mine — pale evaporite/saltpetre crust in the dry upper galleries. Common. | 1 | **Preservation** (cures bug-meat/jerky for long buffs), an etch/desiccant agent (the gem-cut etch), and a `hazard_resist` base for the cave-damp potion. |
| `bat_guano` | forage — rich deposits under the bat-roost ceilings (the cave's fertilizer node). Common. | 1 | Premium **compost/fertilizer** base (potent — the deep's payoff for the farm), a mushroom-growing substrate, and a saltpetre/nitre note. |

> **Why these:** `glow_crystal` → `cut_glow_crystal` carry the **bioluminescent light + crystal** identity and
> the whole accessory/lamp line; `cave_crystal_geode` is the dedicated `gem_luck` node so the fortune pick has
> something to mine for down here; `dripstone` carries the **deep-building** identity (columns/blocks/flux);
> `cave_moss`/`mushroom_glow` (reused) anchor the **glow-fungus alchemy** food/potion line; `cave_nitre` powers
> preservation + the etch + the `hazard_resist` answer; `bat_guano` is the deep's fertilizer payoff. The
> common gatherables (`cave_moss`, `mushroom_glow`, `cave_nitre`) keep the **survival** answers (the cave-damp
> potion, the salve, the antivenom) cheap and always craftable so a careful player is never locked out of staying
> alive — only of the spicy venom weapons and the glow set.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; everything is **gated T3** (several reach a `steel_bar`/
`silver_bar`/gem as a stretch toward T4). `unlock`: **craft** (have station + recipe) / **buy@hermit** /
**find@centipede_cavern**.

### Natural light — the glowworm line (the zone's headline — best light in the game)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `glowworm_lantern` (head/held light) | workbench | `iron_bar` ×1, `glass` ×2, `glowworm_lumen` ×2, `cut_glow_crystal` ×1 *(lens)* | buy@hermit (recipe) / craft | **`light_radius +5`**, **`night_vision +2`**, `move_speed_pct +2` — the **best natural light source in the game**; the deep dark is finally readable | T3 |
| `lumen_torch` ×3 (placed light) | workbench | `glowworm_lumen` ×1, `glow_silk` ×1, `dripstone` ×1 | craft | a cold bioluminescent **placed torch** — lights a cavern room without fire/heat; `light_radius` aura, never burns out | T3 |

### Weapons — fast centipede venom (the agile-venom tier)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `centipede_fang_blade` (fast venom sword) | forge | `iron_bar` ×2, `centipede_venom_gland` ×2, `chitin` ✅ ×2 | find@centipede_cavern (recipe scroll, deep den) | **`attack_speed_pct +20`**, `damage_pct +14`, `crit_chance +6`, **on-hit `envenomed`** (strong DoT) — the fast, skittering-bug-matching venom blade | T3 |
| `venom_lash` (whip, reach) | forge | `iron_bar` ×2, `camel_cricket_leg` ×3, `potent_centipede_venom` ×1 | buy@hermit (recipe) | `damage_pct +22`, `knockback +1`, **long reach** (keeps the fast flankers spaced), strong `envenomed` on-hit — the apex venom weapon | T3→T4 (needs `potent_centipede_venom`) |
| `venom_oil` (weapon coating, consumable) | cauldron | `centipede_venom_gland` ×1, `resin_glob` ✅ ×1, `cave_moss` ✅ ×1 | auto (once cauldron + zone access) | **coats your current weapon** — adds strong `envenomed` on-hit for a duration; upgrades any blade to centipede-venom tier | T3 |

### Crystal accessory & jeweler line (the glow-crystal payoff)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `glowstone_amulet` (accessory) | jeweler | `cut_glow_crystal` ×1, `silver_bar` ✅ ×1, `glowworm_lumen` ×1 | buy@hermit (recipe) / craft | **`light_radius +2`**, `night_vision +1`, `crit_chance +6`, `gem_luck +1` — a **worn light**: glow follows you even with no lantern out; a T3→T5 bridge accessory (needs `silver_bar`) | T3→T5 |
| `cut_glow_crystal` | jeweler | `glow_crystal` ×2 + `cave_nitre` ×1 *(etch)* | craft | **gem-cut** intermediate — the polished light-crystal for the amulet, lantern lens & set inlays (the `cave_nitre` is the gem-cutting etch) | T3 |

### Alchemy — deep-cavern potions (the survival answers)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `deep_delver_brew` *(deep-cavern potion)* | cauldron | `mushroom_glow` ✅ ×2, `glowworm_lumen` ×1, `cave_moss` ✅ ×1, `cave_nitre` ×1 | buy@hermit (recipe) / craft | the **signature cavern brew** — sustained **`night_vision +2`** + **`hazard_resist +2`** (cave-damp/spore) + `hp_regen +1` + a faint personal `light_radius +1`; the deep-explorer's tonic | T3 |
| `cave_antivenom` *(consumable)* | cauldron | `cave_moss` ✅ ×2, `cave_nitre` ×1, `centipede_venom_gland` ×1 | craft / buy@hermit | **cures `envenomed`** + short `hazard_resist` — the answer to the centipedes' strong venom | T3 |
| `damp_salve` *(consumable)* | cauldron | `cave_moss` ✅ ×2, `mushroom_glow` ✅ ×1, `bat_guano` ×1 *(saltpetre note)* | craft | short `defense +2` + heals chip damage + a `hazard_resist` (cave-rot/spore) tick — the cheap, always-craftable chip answer | T3 |

### Deep-stone structure, décor & food (stonecutter / workbench / cooking_pot — the cavern payoff)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `dripstone_block` ×4 | stonecutter | `dripstone` ×4 | craft | structure / cavern wall & path material | T3 |
| `dripstone_column` ×2 | stonecutter | `dripstone` ×4 + `cave_nitre` ×1 *(set)* | craft | the **flowstone column** building piece — the cavern-hall flex | T3 |
| `glowshroom_lamp` *(light décor)* | workbench | `dripstone` ×1 + `glass` ×1 + `mushroom_glow` ✅ ×1 + `glow_silk` ×1 | craft | light décor — a softly glowing fungus-and-silk lamp (`light_radius` aura), the deep-home flex piece | T3 |
| `crystal_terrarium` *(display décor)* | workbench | `dripstone` ×2 + `glass` ×2 + `glow_crystal` ×1 | craft / find | display décor — a lit crystal vivarium (shows a caught cave bug; idle-aura tag) | T3 |
| `chitin_buckler` *(off-hand shield)* | anvil | `iron_bar` ×1 + `chitin` ✅ ×3 + `cave_beetle_carapace` ×1 | craft | `defense +3`, `knockback +1`, `block` — the cave-chitin off-hand (pairs the venom blade) | T3 |
| `cave_jerky` *(food)* | cooking_pot | `dead_beetle` ✅ ×1 *(or any `dead_*` bug-meat)* + `cave_nitre` ×1 + `mushroom_glow` ✅ ×1 | craft | nitre-cured — long-duration `max_hp +5` / `hp_regen +1` buff (the preservation payoff) | T3 |

### Glow-textile & dye (loom / dye_vat — the luminous line)

| Output (id) | Station | Inputs | Unlock | Tag / color | Tier |
|---|---|---|---|---|---|
| `glow_thread` | loom | `glow_silk` ×2 + `thread` ✅ ×1 | craft | a **luminous thread** — the glow-trim textile base for the set underweave & glow décor | T3 |
| `cavern_dye` (set: glow-cyan / moss-green / nitre-pale) | dye_vat | `glow_crystal` / `cave_moss` ✅ / `cave_nitre` | auto | the **deep-cavern palette** for the delver outfit & cavern décor | T3 |

> **Supply logic:** `centipede_venom_gland` (the strong drop) is the bottleneck on offense; `cave_moss` /
> `mushroom_glow` / `cave_nitre` (common gatherables) keep the **survival** answers (deep-delver brew, antivenom,
> salve) cheap and always craftable. `glowworm_lumen` + `glow_crystal` gate the **light** line — the headline
> reward, and the thing that makes the whole zone playable. `potent_centipede_venom` (mini-boss) gates the spicy
> `venom_lash` and is held in reserve as the **forward hook** to the next tier's hotter venom.

---

## Signature BONUS gear — the **Deep Delver set** (T3→T4 glow/venom armor)

The zone's keystone reward and a **bug-derived deep-cavern armor set**: dark cave-beetle carapace plate over a
glow-thread underweave, glow-crystal inlays that light your own silhouette, centipede-segment flex greaves with
spring-leg cricket cordage. Theme = **the deep delver who carries her own light into the dark and out-fights the
venom**. This is the brief's signature set — a **`defense` + `light_radius`/`night_vision` + `crit_chance` +
venom (`envenomed` on-hit)** set: a true *deep-cavern explorer-fighter* set, the bug-and-glow gear the whole
cavern feeds into. Built at **anvil** (carapace plate) + **loom** (the glow-thread underweave) + a **jeweler**
inlay (the glow-crystal) — a mixed-station set that shows off the zone's chitin + glow + venom identity. Pure
T3→T4 (cave-beetle drops + iron, the body reaching steel/glow-crystal).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `delver_helm` | head | anvil | `iron_bar` ×2, `cave_beetle_carapace` ×1, `cut_glow_crystal` ×1 *(brow-lamp inlay)*, `glow_thread` ×1 | `defense:3, light_radius:3, night_vision:1, crit_chance:2` (built-in glow-lamp) | `deep_delver` |
| `delver_carapace` | body | anvil | `steel_bar` ✅ ×1, `cave_beetle_carapace` ×2, `glow_thread` ×2, `glowworm_lumen` ×1 *(glow inlay)*, `centipede_parts` ✅ ×1 | `defense:5, max_hp:6, light_radius:1, crit_chance:4` | `deep_delver` |
| `delver_greaves` | legs/feet | anvil | `iron_bar` ×1, `camel_cricket_leg` ×3 *(spring cordage)*, `centipede_venom_gland` ×1 *(venom-barb)*, `glow_thread` ×1 | `defense:3, move_speed_pct:4, fall_resist:1, crit_chance:2` | `deep_delver` |

**Set bonus (`set: deep_delver`, all 3 worn):**
> *"Carry your own light. Bite back in the dark."*
> - **+`light_radius +3`, +`night_vision +2`** (you never explore blind — the set *is* a worn lantern),
> - **+`crit_chance +6`, +`defense +3`** (the explorer-fighter payoff),
> - **Venom-barbed** — your hits gain a strong **`envenomed` on-hit** (the centipede-venom barbs in the greaves);
>   the more the fast flankers pile in, the more they bleed venom,
> - **Cave-sure footing** — the `hazard_resist` (cave-damp/spore) chip is shrugged and the `move_speed`/`fall_resist`
>   from the cricket-leg cordage lets you keep pace with the skittering centipedes in the dark.
> - **Fantasy realized:** fully kitted in dark cave-beetle plate lit by glow-crystal inlays, you walk into the
>   lightless centipede den as your own moving lantern, crit-and-envenom the fast flankers before they circle you,
>   and the cavern goes from a blind, venomous slog to a generous glow-crystal-and-venom farm. That power spike is
>   the reward for clearing the zone — and the `light` + `crit` + venom carry straight into the next, deeper zone.

**Unlock:** helm + greaves recipes **auto** at the anvil (you can grind those yourself from `cave_beetle`/
`giant_centipede`/`camel_cricket` drops); the **body (`delver_carapace`) is the keystone** — its recipe is
**bought from the Hermit** OR **dropped by the `centipede_matron`** mini-boss (it also wants the rarer
`glowworm_lumen` glow-inlay + `steel_bar`). So the marquee piece rewards either the merchant loop or the apex fight.

> Optional matching accessory: `delver_band` (jeweler — `cut_glow_crystal` ×1, `iron_bar` ×1, `glowworm_lumen` ×1):
> `light_radius +1`, `crit_chance +2`, `gem_luck +1`. A cheap 4th-slot stretch that deepens the glow identity; prune
> if the 3-piece reads cleaner. (Pairs naturally with `glowstone_amulet` + `centipede_fang_blade` + `glowworm_lantern`
> for a full light-and-venom build.)

---

## Shop / NPC stock — **the Hermit researcher** (`hermit`)

The recluse-researcher vendor camped in a **lamp-lit cave nook** off the main hall — a lantern-bearded hermit who
has spent years cataloguing the deep (this realizes the `merchants.md` rare-specimen/recipe seam, here as the
cavern **Hermit**). He **teaches the deep** (the cave-survival/light tips beat), sells the **glowworm light gear,
the deep-cavern brews, the crystal-cut & keystone recipes, and rare bug specimens** you can't easily catch, sells
**glow-crystal & the bridge-tier `silver_bar` at a markup** (so you can build the accessory before you've mined
enough), and **buys your venom, lumen & specimens high** (a reason to over-harvest the deep). Currency = coins
(existing). He is the gate that teaches "kit up with light before you push into the lightless den."

**Sells (buy@hermit):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: glowworm_lantern` | recipe | 200 | The best natural light — the headline unlock. |
| `recipe: deep_delver_brew` | recipe | 220 | The signature cavern brew (`night_vision`/`hazard_resist`). |
| `recipe: glowstone_amulet` | recipe | 240 | The worn-light crystal accessory. |
| `recipe: venom_lash` | recipe | 350 | Marquee apex venom weapon (needs `potent_centipede_venom` to build). |
| `recipe: delver_carapace` | recipe | 460 | **Keystone** set piece (alt path to the boss drop). |
| `deep_delver_brew` / `cave_antivenom` | consumable | 40 / 30 | Pre-made deep-survival on hand before you brew your own (daily cap). |
| `glowworm_lantern` | gear | 130 | Pre-made best-light so you can see the dark hall immediately. |
| `rare specimen: live glowworm / cave_beetle / centipede` | specimen | 60–140 | **Rare live specimens** — buy what you can't catch, for the terrarium/display, breeding-stock, or a guaranteed drop sample (the researcher's signature stock). |
| `glow_crystal` / `dripstone` | material | 30 / 12 | Convenience deep-stone restock (small daily cap, markup). |
| `iron_bar` / `coal` ✅ | material | 35 / 15 | Convenience restock of the T3 metal & fuel (small daily cap, markup). |
| `silver_bar` ✅ / `steel_bar` ✅ | material | 90 / 70 | The bridge-tier metals you may be short on — for the `glowstone_amulet` / `delver_carapace` stretch (capped). |
| `jeweler` / `stonecutter` (station) | station | 260 / 200 | Buy-the-station convenience for the gem-cut & deep-stone lines. |

**Buys (sell to vendor — the zone's coin sink + over-harvest incentive):** `glowworm_lumen`, `glow_silk`,
`glow_crystal`, `cut_glow_crystal`, `dripstone`, `centipede_venom_gland`, `centipede_parts` ✅, `chitin` ✅,
`cave_beetle_carapace`, `camel_cricket_leg`, `cave_nitre`, `bat_guano` — with a **`bug_value_pct` premium on venom
& lumen** and a **`gem_value_pct` premium on glow-crystal** (he pays well for both, reinforcing the
light-mine-and-fight loop). `potent_centipede_venom` and `matron_forcipule` sell highest (the apex flex).

---

## "New toys" hook

Centipede Cavern is where BugFarmer's **light becomes a craftable resource** and the venom gets *fast*. The new
toys are all about *seeing in the deep dark and out-skittering the venom*: the **`glowworm_lantern`** — the
**best natural light source in the game** — plus cold, never-burning **`lumen_torch`** placed lights that let you
finally read the lightless hall; the **`centipede_fang_blade`**, a fast `attack_speed`/`crit` venom sword that
trades blows with the skittering centipedes, with the apex **`venom_lash`** whip for reach. The crystal jeweler
line cuts wall `glow_crystal` into the **`glowstone_amulet`** — a *worn* light that follows you with `crit` on
top — and the glow-fungus cauldron gives the **`deep_delver_brew`** (the signature cavern tonic: `night_vision` +
`hazard_resist`) plus the survival answers — **`cave_antivenom`**, **`damp_salve`** — that take the blind,
venomous den from "this kills careless runs" to "this is my glow-crystal-and-venom farm." The capstone is the
**Deep Delver set**: dark cave-beetle plate lit by glow-crystal inlays, spring-leg cricket greaves, whose
`light_radius` + `night_vision` + `crit_chance` + venom-barb bonus lets you walk into the den as your own moving
lantern and crit-and-envenom the flankers before they circle you. And the **Hermit researcher** sells **rare live
specimens** of the deep's bugs — the thing you can't just catch — for your terrarium, breeding stock, or a sample
drop. Beat the `centipede_matron` and you walk out with **`potent_centipede_venom`** (the apex weapon seed) and
the `matron_forcipule` trophy for the wall.

---

## New id ledger

**materials:**
- `glow_crystal` — mine@centipede_cavern (luminous light crystal; jeweler cut line + lamp inlay; `gem_luck`/`light` node)
- `cut_glow_crystal` — craft (jeweler, `glow_crystal`×2 + etch) — the gem-cut polished light-crystal (amulet/lens/inlay)
- `cave_crystal_geode` — mine@centipede_cavern (cracks to crystal/quartz/glow_crystal; the `gem_luck` node)
- `dripstone` — mine@centipede_cavern (signature cavern building stone; stonecutter line + lime/flux)
- `cave_nitre` — mine@centipede_cavern (preservation/jerky, gem-cut etch, `hazard_resist` base)
- `bat_guano` — forage@centipede_cavern (premium cave fertilizer; mushroom substrate; nitre note)
- `glowworm_lumen` — drop, glowworm (the BEST natural light material; lantern/lamp/amulet/set inlay)
- `glow_silk` — drop, glowworm (luminous hanging thread; loom glow-textile + light décor)
- `centipede_venom_gland` — drop, giant_centipede (strong venom; fast venom weapons + coating)
- `potent_centipede_venom` — guaranteed drop, centipede_matron (APEX venom; marquee weapon + T4 hook)
- `cave_beetle_carapace` — drop, cave_beetle (the wing-case plate; delver armor input)
- `camel_cricket_leg` — drop, camel_cricket (spring cordage; delver greaves/boots — `fall_resist`/`move_speed`)
- `matron_forcipule` — rare drop, centipede_matron (heavy fang trophy; heavier venom weapon + décor)
- `glow_thread` — crafted intermediate (loom, `glow_silk`×2 + `thread`×1) — luminous thread, set underweave/décor

**species:** (id → primary drop)
- `giant_centipede` → `centipede_venom_gland` ✅(new) (also `centipede_parts` ✅, `chitin` ✅, `dead_centipede` ✅)
- `glowworm` → `glowworm_lumen` ✅(new) (also `glow_silk`, `dead_glowworm`)
- `cave_beetle` → `cave_beetle_carapace` ✅(new) (also `chitin` ✅, `dead_beetle` ✅)
- `camel_cricket` → `camel_cricket_leg` ✅(new) (also `chitin` ✅, `dead_cricket`)
- `centipede_matron` → `potent_centipede_venom` (mini-boss; also `matron_forcipule`, `centipede_parts` ✅, `dead_centipede` ✅)

*(The four brief-required new drops: `centipede_venom_gland`, `cave_beetle_carapace`, `glowworm_lumen`,
`camel_cricket_leg`. Reused: `centipede_parts`, `chitin`, `dead_centipede`, `dead_beetle`, `cave_moss`,
`mushroom_glow`. New `dead_*` carcasses: `dead_glowworm`, `dead_cricket`.)*

**items:**
- `glowworm_lantern` — light gear (head/held), workbench, T3 — light_radius(+5)/night_vision/move_speed_pct (BEST natural light)
- `lumen_torch` — placed light ×3, workbench, T3 — cold bioluminescent torch, light_radius aura, never burns out
- `centipede_fang_blade` — weapon (fast venom sword), forge, T3 — attack_speed_pct/damage_pct/crit_chance + on-hit envenomed
- `venom_lash` — weapon (whip, reach), forge, T3→T4 — damage_pct/knockback, long reach + strong envenomed (needs potent_centipede_venom)
- `venom_oil` — weapon coating consumable, cauldron, T3 — adds strong envenomed on-hit
- `glowstone_amulet` — accessory, jeweler, T3→T5 — light_radius/night_vision/crit_chance/gem_luck (worn light; needs silver_bar)
- `cut_glow_crystal` — gem-cut intermediate, jeweler, T3 — polished light-crystal (amulet/lens/inlay)
- `deep_delver_brew` — deep-cavern potion, cauldron, T3 — night_vision/hazard_resist/hp_regen + faint light (signature brew)
- `cave_antivenom` — consumable, cauldron, T3 — cures envenomed + hazard_resist
- `damp_salve` — consumable, cauldron, T3 — defense + heals chip + hazard_resist(cave-rot)
- `dripstone_block` — structure ×4, stonecutter, T3 — cavern wall/path
- `dripstone_column` — structure ×2, stonecutter, T3 — flowstone column building piece
- `glowshroom_lamp` — light décor, workbench, T3 — light_radius aura
- `crystal_terrarium` — display décor, workbench, T3 — lit crystal vivarium (shows a caught cave bug)
- `chitin_buckler` — off-hand shield, anvil, T3 — defense/knockback/block
- `cave_jerky` — food, cooking_pot, T3 — long max_hp/hp_regen buff (preservation)
- `glow_thread` — luminous textile, loom, T3 — glow-trim underweave/décor base
- `cavern_dye` — dye set (glow-cyan/moss-green/nitre-pale), dye_vat, T3 — deep-cavern palette
- `delver_helm` — armor (head), anvil, T3 — defense/light_radius/night_vision/crit_chance; set: deep_delver
- `delver_carapace` — armor (body), anvil, T3→T4 — defense/max_hp/light_radius/crit_chance; set: deep_delver (keystone; needs steel_bar)
- `delver_greaves` — armor (legs/feet), anvil, T3 — defense/move_speed_pct/fall_resist/crit_chance + venom-barb; set: deep_delver
- `delver_band` — accessory (optional 4th), jeweler, T3 — light_radius/crit_chance/gem_luck; set: deep_delver
- `hermit` — NPC ("the Hermit researcher") — rare-specimen + light/venom/recipe shop in a lamp-lit cave nook
