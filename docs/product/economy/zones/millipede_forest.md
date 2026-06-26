# Zone Content Sheet — Millipede Forest

> **Grid (0,1)** · dense old-growth forest of giant trees, deep leaf-litter & bracket-fungus · **difficulty
> HARD** · **tier T4 (steel era, reaching toward T5)**
>
> The **deep-woods + premium-lumber + chitin-armor** zone. Past the mid-game zones the world closes over into
> towering canopy — shafts of green light, knee-deep litter, mossed deadfall, shelf fungus climbing the bark.
> This is the **logging/woodcraft** zone: it debuts **premium hardwoods & bark, big-beetle chitin/carapace
> armor, the iconic stag-beetle horn weapon, and bark/fungus alchemy**, fronted by the **Ranger station**
> (the woodsman vendor — lumber tools, forest gear, recipes). Everything is gated **T4** so it lands once the
> player has steel and is reaching for the first T5 (silver/gold/diamond) pieces.
>
> **Design intent (pacing, per `../README.md` + `../progression.md` §"Mid→Late"):** this is a hard zone that
> teaches *the woodcraft loop and the bug-derived armor tier*. You don't brute-force the old-growth — you fell
> premium timber for a real `sawmill` line, harvest **chitin from the big beetles** to build the **Carapace
> Warden** armor set, forge the **stag-horn** melee, and brew the bark/fungus answers to the forest's hazards.
> Then the woods become a generous lumber-and-chitin farm. Generous content below — **we prune later, never thin.**
>
> Status: **design only** — nothing here is wired in yet. Reuses existing ids where they exist; new ids are
> snake_case and called out in the trailing id ledger.

> Design contracts this obeys: cost model + station roster from [`../crafting.md`](../crafting.md); stat vocab +
> `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T4 "Mid→Late" / steel reaching T5); shop seam from
> [`../merchants.md`](../merchants.md) (the **Carpenter — builder-themed** vendor, realized here as the forest
> **Ranger station**). World-guide species: millipedes (many varieties), forest centipedes, bark beetles,
> stag beetles.

---

## Species & drops

Six concrete species span the difficulty curve — a passive litter detritivore, two ground threats, a wood-borer,
the iconic horned bruiser, and an apex armored beetle. Behaviors slot into the existing arthropod ecology
vocabulary (anchor-and-patrol, flank, flee, swarm, curl/armor) without new sim primitives. The signature theme
is **chitin/carapace armor** (big-beetle plates) plus the **stag-beetle horn** melee anchor and a poison/bite
ground hazard from the forest centipedes.

| Species (id) | Tier feel | Behavior | Primary drop | Secondary drop(s) |
|---|---|---|---|---|
| `giant_millipede` | core / passive-tank | The zone's signature bug. **Long, segmented, armored detritivore** that grazes the deep litter and climbs deadfall in slow trains. **Curls into a defensive coil when struck** (heavy `defense`, little offense); when cornered it **secretes a `cyanide`-class defensive toxin** (a `noxious` cloud — irritant, not a sting). Slow, tanky, a *patience/armor* catch. | `millipede_segment` ✅(new) | `defensive_toxin` (uncommon — the secretion), `dead_millipede` ✅ |
| `forest_centipede` | ground threat / venom | A bigger, faster cousin of the meadow centipede — **a fast, aggressive ground hunter** that flanks from the litter and **bites with venom forcipules** (applies `poisoned` DoT). Skitters between root-shadows; hits, retreats, re-flanks. The "don't get surrounded" pressure of the forest floor. | `forest_centipede_fang` ✅(new) | `chitin` ✅, `dead_centipede` ✅ |
| `bark_beetle` | swarm / borer | Small **wood-boring beetles** that swarm a single bored tree and **chew galleries under the bark**; disturb the tree and a cloud erupts to harass (a chip-damage swarm, not a heavy hitter). Fragile individually — a *cluster* catch — but they're the source of the bark/jaw alchemy line and they riddle the premium timber (a harvest mini-event). | `bark_beetle_jaw` ✅(new) | `bored_bark` (the galleried bark they shed), `dead_beetle` ✅ |
| `stag_beetle` | **signature bruiser** | The iconic fight. A heavy, glossy beetle with **huge mandible "antlers"** — it **anchors a clearing, charges, and tries to grapple-and-throw** with its horns (big `knockback`). Tanky, telegraphed charge, hits hard but slow. Beating it yields the **`stag_horn`** — the marquee melee material of the zone. | `stag_horn` ✅(new) | `beetle_carapace` (the thick wing-case plate), `dead_beetle` ✅ |
| `rhino_beetle` *(apex)* | **mini-boss** (forest apex) | The zone's apex armored beetle — an enormous horned bruiser anchored to the **great rotten log** at the heart of the old-growth. **Stationary-ish; periodically summons `bark_beetle` swarms** off the log, then **charges with a single forward horn** (heavy `knockback` + brief stun) and shrugs off chip damage with the thickest plate in the forest. The real fight of the zone — the keystone carapace source. | `prime_carapace` (guaranteed, 1–2 — the apex plate) | `rhino_horn` (rare — a heavier `stag_horn`), `beetle_carapace` (×2–4), `dead_beetle` ✅ |
| `forest_snail` *(bonus — flavor/forage)* | passive / forage | *(low-risk flavor species)* A big **timber snail** that grazes bracket fungus on the deadfall at dawn/after rain; leaves a slick trail, tucks into a banded shell when poked. A relaxing catch and a light décor/lime source — the forest's calm counterpoint to the beetles. | `timber_shell` (banded spiral shell) | `snail` ✅ (the body, food) |

**Drop notes**
- `millipede_segment`, `forest_centipede_fang`, `bark_beetle_jaw`, `stag_horn` are the **four brief-required new
  drops** — each species-signature.
- `chitin` ✅, `dead_centipede` ✅, `dead_millipede` ✅, `dead_beetle` ✅, `snail` ✅ are **existing ids** — reused
  (the forest is the place the existing `chitin` / big-bug carcasses pay off into real armor).
- **Two-tier carapace supply** (mirrors the scorpion zone's venom tiers): `beetle_carapace` (common-ish, off
  `stag_beetle`/`rhino_beetle`) → `prime_carapace` (the **apex plate**, gated behind the `rhino_beetle`
  mini-boss). `prime_carapace` is the keystone armor input and the forward hook into T5.
- `defensive_toxin` (millipede secretion), `bored_bark` (beetle-galleried bark), `rhino_horn` (heavier horn),
  `timber_shell` round out the tables — alchemy, building, and the apex melee flex.

**Drop → use at a glance**
- `stag_horn` → the **marquee horn melee** (the iconic stag-beetle weapon) + the warden set's pauldron spikes.
- `rhino_horn` → the **upgraded** horn weapon variant (apex) — a T4→T5 bridge weapon.
- `beetle_carapace` / `prime_carapace` → the **Carapace Warden** armor plating (the bug-derived T4 set).
- `chitin` ✅ → the warden's underweave/gauntlet plates and the chitin-buckler.
- `forest_centipede_fang` → a venom-coating + a barbed dagger/thorns reagent.
- `millipede_segment` → segmented flex-plating (light armor / greaves) + the thorns trinket.
- `bark_beetle_jaw` + `bored_bark` + `defensive_toxin` → the **bark/fungus alchemy** line (the forest potions).

---

## New ingredients & materials

Wood-, bark-, and fungus-themed gatherables you **fell, forage, or strip from the environment** (not bug drops).
They give the zone its lumber/woodcraft identity and feed the recipe list. Source = `chop` (fell a premium tree),
`forage` (pick), `strip` (bark off deadfall). Cost-points per the model (wood/fiber/stone=1; plank=2; the premium
woods sit one notch above their common cousins).

| Id | Source (find@millipede_forest) | Cost-pt | Use |
|---|---|---|---|
| `hardwood` | chop — the great old-growth trunks (oak/ironwood-class; far denser than common `wood`). The zone's headline timber. Common-but-slow (big trees). | 2 | The premium lumber: milled at the **sawmill** into `hardwood_plank` for T4 structures, weapon hafts, and the warden set's frame. Denser/stronger than `wood`/`plank`. |
| `hardwood_plank` | craft (sawmill: `hardwood` ×2) | 3 | The premium **plank** grade — T4 furniture & structures, the ranger lodge line, weapon hafts, the keg/loom upgrades. A clean step above common `plank`. |
| `bark_strip` | strip — peeled from standing premium trees & deadfall (clean, un-bored bark). Common. | 1 | Tannin source: the **tannic** dye/leather line, a bitter alchemy base (the forest potions), and a fiber-binder for the warden underweave. |
| `tree_resin` | forage — amber sap weeping from cut/bored trunks (reuse the `resin_glob` ✅ family, forest-grade). Uncommon. | 2 | A **binder/sealant**: weatherproofs the lumber line, glues horn to haft, seals preserves; an alchemy thickener and a torch/varnish base. |
| `mushroom_bracket` ✅ | forage — shelf fungus climbing the deadfall & living bark. Common. | 1 | Reuse — the forest's **fungus alchemy** workhorse: a cooking ingredient, a `hp_regen`/woodland-tonic reagent, and a leather-tanning note. |
| `mushroom_morel` ✅ | forage — prized morels in the rich leaf-litter after rain. Uncommon. | 2 | Reuse — the premium forest food/potion ingredient (a `crop_quality`/luck cooking note + the high-end woodland brew). |
| `forest_moss` | forage — thick moss on the north faces of the old trunks. Common. | 1 | A cheap green dye/binder, a `light`-softening décor moss, and a poultice base for the bark salve (the chip-damage answer). |
| `litter_mulch` | forage — the deep, rich leaf-litter floor (a forest-grade `leaf_litter` ✅). Common. | 1 | Premium **compost/fertilizer** base (better than meadow litter), a mushroom-growing substrate, and a stuffing for the warden underweave. |

> **Why these:** `hardwood` → `hardwood_plank` carry the **premium-lumber** identity and the whole T4 sawmill/
> furniture line; `bark_strip` + `tree_resin` power the **tannic leather + sealant** crafts (and bind horn to
> haft); `mushroom_bracket`/`mushroom_morel` (reused) anchor the **fungus alchemy** food/potion line; `forest_moss`
> + `litter_mulch` keep the **survival + farming** answers (bark salve, compost) cheap and always craftable so a
> careful player is never locked out of staying alive — only of the spicy horn weapons and the warden plate.

---

## Recipes debuting here

Nine recipes (well past the ≥4 floor — prune later). Each lists output · station · inputs(+counts) · unlock ·
stat/bonus · tier. Costs use the tier-point model; everything is **gated T4** (several reach a `silver_bar`/
`gold_bar`/gem as a stretch toward T5). `unlock`: **craft** (have station + recipe) / **buy@ranger_station** /
**find@millipede_forest**.

### Lumber tools & woodcraft (the zone's headline — the premium-wood line)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `steel_axe` | anvil | `steel_bar` ×3, `hardwood_plank` ×2, `stag_horn` ×1 *(grip)* | buy@ranger_station (recipe) / craft | `chop_speed_pct +30`, `damage_pct +12`; the **premium felling axe** — chops `hardwood` fast and doubles as a weapon | T4 |
| `lumberjack_saw` (tool) | anvil | `steel_bar` ×2, `hardwood_plank` ×1, `tree_resin` ×1 | craft / buy@ranger_station | `chop_speed_pct +15`, **`harvest_yield +2` on timber** (more planks per tree) — the lumber-fortune tool | T4 |
| `hardwood_plank` ×2 | sawmill | `hardwood` ×2 | auto (once sawmill + zone access) | the **premium plank** intermediate — feeds every T4 structure/haft below | T4 |
| `ranger_lantern` (head/held light) | workbench | `steel_bar` ×1, `glass` ×2, `tree_resin` ×1 | craft / buy@ranger_station | `light_radius +3`, `night_vision +1`, `move_speed_pct +2` — the canopy is dark; see & move | T4 |

### Weapons — the stag-horn melee (the marquee offense)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `stag_horn_maul` *(heavy mace)* | forge | `steel_bar` ×2, `stag_horn` ×2, `hardwood_plank` ×1 *(haft)*, `tree_resin` ×1 *(bind)* | find@millipede_forest (recipe scroll, deep grove) | **`damage_pct +24`**, **`knockback +3`**, slow heavy swing — the **iconic horn weapon**; horns gore & toss the beetles | T4 |
| `horned_glaive` *(reach polearm)* | forge | `steel_bar` ×2, `stag_horn` ×1, `forest_centipede_fang` ×3, `hardwood_plank` ×1 | buy@ranger_station (recipe) | `damage_pct +20`, `crit_chance +6`, long reach (anti-swarm spacing), **on-hit `poisoned`** (fang-tipped) | T4 |
| `rhino_breaker` *(apex maul)* | forge | `steel_bar` ×2, `rhino_horn` ×1, `silver_bar` ✅ ×1, `prime_carapace` ×1 | find (apex-area drop recipe) | the **upgraded horn weapon** — huge `damage_pct +30`, `knockback +4`, armor-break on charge; a T4→T5 bridge | T4→T5 |
| `barbed_dagger` *(off-hand)* | anvil | `steel_bar` ×1, `forest_centipede_fang` ×2, `chitin` ✅ ×2 | craft | fast `attack_speed_pct +15`, `crit_chance +5`, `thorns +2`, on-hit `poisoned` — the quick venom off-hand | T4 |
| `venom_coat` *(weapon coating, consumable)* | cauldron | `forest_centipede_fang` ×1, `tree_resin` ×1, `defensive_toxin` ×1 | craft | **coats your current weapon** — adds `poisoned` on-hit for a duration; turns any blade fang-tipped | T4 |

### Alchemy — bark & fungus (the forest potions / survival answers)

| Output (id) | Station | Inputs | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| `woodland_tonic` *(forest potion)* | cauldron | `mushroom_bracket` ×2, `mushroom_morel` ×1, `bark_strip` ×1 | buy@ranger_station (recipe) / craft | the **signature forest brew** — sustained `hp_regen +2` + `max_hp +6` + `night_vision +1` (the deep-woods explorer's tonic) | T4 |
| `bark_salve` *(consumable)* | cauldron | `bark_strip` ×2, `forest_moss` ×1, `mushroom_bracket` ×1 | craft | short `defense +2` + heals chip damage — the **answer to the swarm/centipede chip**; cheap, always craftable | T4 |
| `antitoxin` *(consumable)* | cauldron | `forest_moss` ×2, `defensive_toxin` ×1, `mushroom_bracket` ×1 | craft / buy@ranger_station | **cures `poisoned`/`noxious`** + short `hazard_resist` — the answer to the centipede venom & millipede cloud | T4 |
| `thorns_draught` *(buff)* | cauldron | `forest_centipede_fang` ×1, `defensive_toxin` ×1, `mushroom_morel` ×1 | find | timed `thorns +3` + `defense +1` — turn the beetles' charges against them (the "spiky" buff) | T4 |

### Premium-wood structure, furniture & décor (sawmill / stonecutter / workbench — the lumber payoff)

| Output (id) | Station | Inputs | Unlock | Tag / bonus | Tier |
|---|---|---|---|---|---|
| `hardwood_beam` ×4 | sawmill | `hardwood_plank` ×2 + `tree_resin` ×1 | craft | structure — the premium **building beam** (T4 walls/floors/frames; the ranger-lodge line) | T4 |
| `ranger_lodge_kit` *(structure set)* | sawmill | `hardwood_plank` ×6 + `hardwood_beam` ×2 + `bark_strip` ×4 | buy@ranger_station (recipe) | a **premium log-cabin** building kit (walls/roof/door) — the forest home flex | T4 |
| `carved_throne` *(furniture)* | sawmill | `hardwood_plank` ×4 + `stag_horn` ×2 *(antler-arms)* + `beetle_carapace` ×1 *(inlay)* | craft / find | the **premium-wood furniture** flex — a comfort/idle-aura décor piece (the warden's seat) | T4 |
| `bracket_lamp` *(light décor)* | workbench | `hardwood_plank` ×1 + `glass` ×1 + `mushroom_bracket` ×1 *(glow shelf)* | craft | light décor — a softly glowing bracket-fungus lamp (`light_radius` aura) | T4 |
| `chitin_buckler` *(off-hand shield)* | anvil | `steel_bar` ×1 + `chitin` ✅ ×3 + `beetle_carapace` ×1 | craft | `defense +3`, `knockback +1`, `block` — the chitin off-hand (pairs the horn maul) | T4 |
| `forest_jerky` *(food)* | cooking_pot | `dead_beetle` ✅ ×1 *(or any `dead_*` bug-meat)* + `mushroom_morel` ×1 + `sage` ✅ ×1 | craft | smoked — long-duration `max_hp +6` / `hp_regen +1` buff (the forest provision) | T4 |

### Dye & leather (dye_vat / loom — the tannic line)

| Output (id) | Station | Inputs | Unlock | Tag / color | Tier |
|---|---|---|---|---|---|
| `tanned_leather` | dye_vat | `bark_strip` ×3 + *(hide/`fiber` ✅ ×2)* | craft | **tannic-cured leather** — the warden underweave base & a furniture/armor strap material | T4 |
| `forest_dye` (set: bark-brown / moss-green / amber) | dye_vat | `bark_strip` / `forest_moss` / `tree_resin` | auto | the **woodland palette** for the warden outfit & lodge décor | T4 |

---

## Signature BONUS gear — the **Carapace Warden set** (T4 bug-derived armor)

The zone's keystone reward and a **key bug-derived armor set**: glossy beetle-carapace plate over a tannic-leather
underweave, stag-horn pauldron spikes, segmented millipede greaves. Theme = **the forest warden who stands like
a tree and punishes anything that bites him**. This is the brief's signature set — a **defense + `thorns` +
`damage_pct` + `hp_regen`** chitin set (a true *combat-tank* set, the bug-derived T4 armor the whole forest food
chain feeds into). Built at **anvil** (carapace plate) + **loom** (the tannic-leather underweave) + a touch of
**sawmill** (horn-spike mounts) — a mixed-station set that shows off the zone's chitin + lumber identity. Pure T4
(beetle drops + steel + premium wood).

`bonuses{}` schema per `../stats_and_bonuses.md` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| `warden_helm` | head | anvil | `steel_bar` ×1, `beetle_carapace` ×1, `stag_horn` ×1 *(horn crest)*, `tanned_leather` ×1 | `defense:4, max_hp:6, knockback:1, hp_regen:1` | `carapace_warden` |
| `warden_carapace` | body | anvil | `steel_bar` ×2, `prime_carapace` ×1, `beetle_carapace` ×2, `tanned_leather` ×2, `litter_mulch` ×1 *(padding)* | `defense:6, max_hp:8, thorns:2, hp_regen:1` | `carapace_warden` |
| `warden_pauldrons` | shoulders | anvil | `steel_bar` ×1, `stag_horn` ×2 *(spikes)*, `beetle_carapace` ×1, `hardwood_plank` ×1 *(mount)* | `defense:3, damage_pct:6, thorns:2, knockback:1` | `carapace_warden` |
| `warden_greaves` | legs/feet | anvil | `steel_bar` ×1, `millipede_segment` ×4 *(flex-plate)*, `beetle_carapace` ×1, `tanned_leather` ×2 | `defense:4, max_hp:4, thorns:1, move_speed_pct:3` | `carapace_warden` |

**Set bonus (`set: carapace_warden`, all 4 worn):**
> *"Stand like a tree. Bite back like the forest."*
> - **+`defense +4`, +`thorns +3`, +`damage_pct +8`, +`hp_regen +2`** (the tank-bruiser payoff),
> - **Reflect on hit** — chip/swarm damage (bark beetles, centipede flanks) is reflected back via `thorns`,
>   so the more they pile on, the more they die to your plate; the millipede's `noxious`/centipede `poisoned`
>   chip is shrugged (`hazard_resist` tick),
> - **Charge brace** — the `knockback` from the stag/rhino-beetle charge no longer staggers you; you hold the line.
> - **Fantasy realized:** fully kitted in beetle plate with horn-spiked shoulders, you wade into a stag-beetle
>   clearing, eat the charge without budging, and watch the swarm kill itself on your `thorns` while your
>   `hp_regen` keeps you topped. The forest goes from a lethal crush to a generous chitin-and-lumber farm. That
>   power spike is the reward for clearing the zone — and the `damage_pct`/`defense` carry straight into the next,
>   deeper zone.

**Unlock:** helm + pauldrons + greaves recipes **auto** at the anvil (you can grind those yourself from
`stag_beetle`/`giant_millipede` drops); the **body (`warden_carapace`) is the keystone** — its recipe is
**bought from the Ranger station** OR **dropped by the `rhino_beetle`** mini-boss (the only `prime_carapace`
source). So the marquee piece rewards either the merchant loop or the apex fight.

> Optional matching accessory: `warden_band` (jeweler — `beetle_carapace` ×1, `steel_bar` ×1, `forest_centipede_fang`
> ×1): `thorns +1`, `defense +1`, `hp_regen +1`. A cheap 5th-slot stretch that deepens the tank identity; prune if
> the 4-piece reads cleaner. (Pairs naturally with `stag_horn_maul` + `chitin_buckler` for a full horn-and-plate build.)

---

## Shop / NPC stock — **the Ranger station** (`ranger_station`)

The woodsman-themed vendor stationed at the **forest edge / trailhead** of the old-growth (this realizes the
`merchants.md` **Carpenter — builder-themed** seam, here as a forest **Ranger**). A weathered woodland ranger who
runs the lodge: she **teaches woodcraft** (the lumber tips/tutorial beat), sells the **premium-lumber tools,
forest gear, survival brews, the building kits, and the keystone recipes**, sells **premium wood/planks at a
markup** (so you can build before you've felled enough), and **buys your timber & chitin high** (a reason to
over-harvest). Currency = coins (existing). She is the gate that teaches "kit up before you push into the deep grove."

**Sells (buy@ranger_station):**

| Item | Type | Price (coins, placeholder) | Notes |
|---|---|---|---|
| `recipe: steel_axe` | recipe | 260 | The premium felling axe — the headline lumber unlock. |
| `recipe: stag_horn_maul` | recipe | 380 | Marquee horn weapon (also a deep-grove scroll find). |
| `recipe: horned_glaive` | recipe | 320 | Reach + venom horn polearm. |
| `recipe: woodland_tonic` | recipe | 220 | The signature forest brew. |
| `recipe: ranger_lodge_kit` | recipe | 300 | The premium log-cabin building set. |
| `recipe: warden_carapace` | recipe | 480 | **Keystone** set piece (alt path to the boss drop). |
| `woodland_tonic` / `bark_salve` | consumable | 40 / 25 | Pre-made survival on hand before you brew your own (daily cap). |
| `antitoxin` | consumable | 35 | Cures `poisoned`/`noxious` — the venom answer, stock-limited. |
| `ranger_lantern` | gear | 120 | Pre-made canopy light so you can see the dark grove immediately. |
| `hardwood_plank` / `hardwood_beam` | material | 18 / 40 | Convenience premium-lumber restock (small daily cap, markup). |
| `steel_bar` ✅ | material | 70 | The T4 metal you may be short on (capped) — for the warden/weapon line. |
| `silver_bar` ✅ | material | 95 | The bridge-tier metal you can't yet refine — for the `rhino_breaker` stretch (capped). |
| `sawmill` / `loom` (station) | station | 240 / 220 | Buy-the-station convenience for the lumber & underweave lines (the Carpenter's stations). |

**Buys (sell to vendor — the zone's coin sink + over-harvest incentive):** `hardwood`, `hardwood_plank`,
`bark_strip`, `tree_resin`, `mushroom_bracket`, `mushroom_morel`, `stag_horn`, `beetle_carapace`,
`millipede_segment`, `forest_centipede_fang`, `bark_beetle_jaw`, `chitin` ✅, `defensive_toxin` — with a
**`sell_pct` premium on premium timber** and a **`bug_value_pct` premium on chitin/horn** (she pays well for both,
reinforcing the chop-and-fight loop). `prime_carapace` and `rhino_horn` sell highest (the apex flex).

---

## "New toys" hook

Millipede Forest is where BugFarmer's **woodcraft loop turns on** and the **bug-derived armor tier** arrives. The
new toys are all about *felling the old-growth and wearing the bugs you beat*: your **first premium felling axe**
(`steel_axe`) and the **`lumberjack_saw`** that rip `hardwood` into the T4 `hardwood_plank` line — feeding a real
sawmill of beams, the **ranger lodge cabin kit**, a **carved antler throne**, and bracket-fungus lamps. The marquee
weapon is the **`stag_horn_maul`** — the iconic horn mace that gores and tosses the beetles — with a fang-tipped
**`horned_glaive`** for reach and the apex **`rhino_breaker`** for the T5 reach. The bark/fungus cauldron gives the
**`woodland_tonic`** (the signature deep-woods brew) plus the survival answers — **`bark_salve`**, **`antitoxin`**,
**`thorns_draught`** — that take the venomous, swarming grove from "this crushes careless runs" to "this is my
lumber-and-chitin farm." The capstone is the **Carapace Warden set**: glossy beetle plate, stag-horn pauldron
spikes, segmented millipede greaves, whose `defense` + `thorns` + `damage_pct` + `hp_regen` bonus lets you stand
unmoved in a stag-beetle charge while the swarm kills itself on your spines. Beat the `rhino_beetle` and you walk
out with **`prime_carapace`** (the keystone warden plate) + **`rhino_horn`** for the apex maul — the seed of the
next, deeper zone's gear.

---

## New id ledger

**materials:**
- `hardwood` — chop@millipede_forest (premium old-growth timber; sawmill line + hafts)
- `hardwood_plank` — craft (sawmill, `hardwood`×2) — the premium plank grade (T4 structures/hafts)
- `bark_strip` — strip@millipede_forest (tannin; tannic leather/dye + alchemy base + binder)
- `tree_resin` — forage@millipede_forest (binder/sealant; weatherproof, glue, alchemy thickener) *(resin_glob ✅ family, forest-grade)*
- `forest_moss` — forage@millipede_forest (green dye/binder; bark-salve poultice base; décor moss)
- `litter_mulch` — forage@millipede_forest (premium compost/fertilizer; mushroom substrate; armor padding)
- `defensive_toxin` — uncommon drop, giant_millipede (the noxious secretion; antitoxin/venom-coat input)
- `bored_bark` — drop, bark_beetle (galleried bark; bark alchemy + rustic décor)
- `beetle_carapace` — drop, stag_beetle/rhino_beetle (the wing-case plate; warden armor input)
- `prime_carapace` — guaranteed drop, rhino_beetle (the APEX plate; keystone warden input + T5 hook)
- `rhino_horn` — rare drop, rhino_beetle (heavier stag_horn; apex maul)
- `timber_shell` — drop, forest_snail (banded shell; décor + lime/grit)
- `tanned_leather` — crafted intermediate (dye_vat; tannic-cured leather, warden underweave)

**species:** (id → primary drop)
- `giant_millipede` → `millipede_segment` ✅(new) (also `defensive_toxin`, `dead_millipede` ✅)
- `forest_centipede` → `forest_centipede_fang` ✅(new) (also `chitin` ✅, `dead_centipede` ✅)
- `bark_beetle` → `bark_beetle_jaw` ✅(new) (also `bored_bark`, `dead_beetle` ✅)
- `stag_beetle` → `stag_horn` ✅(new) (also `beetle_carapace`, `dead_beetle` ✅)
- `rhino_beetle` → `prime_carapace` (mini-boss; also `rhino_horn`, `beetle_carapace`, `dead_beetle` ✅)
- `forest_snail` → `timber_shell` (bonus flavor; also `snail` ✅)

*(The four brief-required new drops: `millipede_segment`, `bark_beetle_jaw`, `stag_horn`, `forest_centipede_fang`.
Reused: `chitin`, `dead_centipede`, `dead_millipede`, `dead_beetle`, `snail`, `mushroom_bracket`, `mushroom_morel`.)*

**items:**
- `steel_axe` — lumber tool/weapon, anvil, T4 — chop_speed_pct/damage_pct (premium felling axe)
- `lumberjack_saw` — lumber tool, anvil, T4 — chop_speed_pct/harvest_yield(timber)
- `ranger_lantern` — light gear, workbench, T4 — light_radius/night_vision/move_speed_pct
- `stag_horn_maul` — weapon (heavy mace), forge, T4 — damage_pct/knockback (the iconic horn weapon)
- `horned_glaive` — weapon (reach polearm), forge, T4 — damage_pct/crit_chance + on-hit poisoned
- `rhino_breaker` — weapon (apex maul), forge, T4→T5 — damage_pct/knockback/armor-break (needs silver_bar)
- `barbed_dagger` — weapon (off-hand), anvil, T4 — attack_speed_pct/crit_chance/thorns + on-hit poisoned
- `venom_coat` — weapon coating consumable, cauldron, T4 — adds poisoned on-hit
- `woodland_tonic` — forest potion, cauldron, T4 — hp_regen/max_hp/night_vision (signature brew)
- `bark_salve` — consumable, cauldron, T4 — defense + heals chip damage
- `antitoxin` — consumable, cauldron, T4 — cures poisoned/noxious + hazard_resist
- `thorns_draught` — buff consumable, cauldron, T4 — thorns/defense
- `hardwood_beam` — structure ×4, sawmill, T4 — premium building beam
- `ranger_lodge_kit` — structure set, sawmill, T4 — premium log-cabin kit
- `carved_throne` — furniture, sawmill, T4 — premium-wood comfort/idle décor
- `bracket_lamp` — light décor, workbench, T4 — light_radius aura
- `chitin_buckler` — off-hand shield, anvil, T4 — defense/knockback/block
- `forest_jerky` — food, cooking_pot, T4 — long max_hp/hp_regen buff
- `forest_dye` — dye set (bark-brown/moss-green/amber), dye_vat, T4 — woodland palette
- `warden_helm` — armor (head), anvil, T4 — defense/max_hp/knockback/hp_regen; set: carapace_warden
- `warden_carapace` — armor (body), anvil, T4 — defense/max_hp/thorns/hp_regen; set: carapace_warden (keystone)
- `warden_pauldrons` — armor (shoulders), anvil, T4 — defense/damage_pct/thorns/knockback; set: carapace_warden
- `warden_greaves` — armor (legs/feet), anvil, T4 — defense/max_hp/thorns/move_speed_pct; set: carapace_warden
- `warden_band` — accessory (optional 5th), jeweler, T4 — thorns/defense/hp_regen; set: carapace_warden
- `ranger_station` — NPC ("the Ranger station", builder/Carpenter-themed) — forest woodcraft/lumber shop at the trailhead
