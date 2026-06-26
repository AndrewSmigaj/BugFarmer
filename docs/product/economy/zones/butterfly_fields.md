# Zone Content Sheet — Butterfly Fields (1,1 · `butterfly_fields_11`)

**Tier:** T2–T3 (copper/bronze → iron) · **Biome:** flower garden / wildflower meadow · **Difficulty:** MEDIUM.

The **aesthetic, light & silk** zone — the game's first turn toward *beauty as economy*. Where the village
taught the catch/cook/decorate loops on harmless bugs, Butterfly Fields is about **gorgeous specimen
collecting**: butterflies and moths you catch *for their scales and silk*, fireflies you harvest *for living
light*, and a **Collector's cabin** that upgrades your net and sells specimen jars. The signature verbs are
**rare-bug luck** (the most beautiful catches are the rarest), **night/glow content** (a whole second economy
that only opens after dark), and **silk/nectar refinement** (soft-goods that bridge cloth → real gear). It's a
generous mid-game pantry: T2–T3 gated, with the first **light gear**, the first **luck/rare-catch tooling**,
and the first **bonus set built around catching rather than fighting**.

> Design contracts this obeys: cost model + stations from [`../crafting.md`](../crafting.md); stat vocab +
> `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T2–T3 mid-game scope); shop seam from [`../merchants.md`](../merchants.md)
> (Collector's Cabin = *"Mothwing's"*). Zone fiction from [`../../zones/butterfly_meadow_11.md`](../../zones/butterfly_meadow_11.md).

---

## Species & drops

Butterfly Fields is the **lepidoptera + glow showcase**. Day belongs to butterflies and cicadas; **night**
flips the field — moths and fireflies come out, the rare catches get rarer, and the glow economy opens. Every
species is catch-focused (no real combat threat — the danger is *missing the rare one*), each has a behavior
gloss, a habitat, and at least one **new drop id** feeding crafting. Generous on purpose; prune later.

| Species (id) | Behavior gloss | Where / when | Drop(s) — new ids | Drop use |
|---|---|---|---|---|
| **common_butterfly** (`butterfly`, exists) | Lazy, looping flight from bloom to bloom; pauses to sip nectar, drifts off when you swing, settles again nearby. The bread-and-butter beautiful catch. | Flower beds, meadow · **day** | `dead_butterfly` (exists), **`butterfly_scale`** (the iridescent wing-dust), **`nectar`** (exists, gathered as it sips) | `butterfly_scale` → shimmer dye, scale-glaze décor, rare-luck charm; `nectar` → cooking sweetener + silk-soak |
| **monarch_butterfly** (`monarch`) | Bigger, bolder, milkweed-bound; glides in long arcs, less skittish but *high value*. The "trophy" day catch — a specimen-jar centerpiece. | Milkweed patches, field center · **day** | **`monarch_scale`** (premium amber-orange scale), `butterfly_scale` | `monarch_scale` → the best shimmer dye + the rare-luck **jeweled** charm tier; specimen-jar value bump |
| **glasswing_butterfly** (`glasswing`) | Rare, transparent-winged drifter; hard to see, hovers at shaded bloom clusters; flees fast. The **luck catch** — the field's "lucky day" sighting. | Shaded groves, dawn/dusk edges | **`glass_scale`** (clear prism scale) | `glass_scale` → clarity/`gem_luck` charm + a prism lens for light gear + glasswork accent |
| **luna_moth** (`luna_moth`) | Big, pale-green, **night** flier; slow, ethereal, drawn to your lantern. The flagship moth — its cocoon is the **silk** source. Calm but easily startled by sudden light. | Tree edges, glow-bloom groves · **night** | **`moth_silk`** (raw cocoon thread), **`luna_dust`** (pale-green wing powder) | `moth_silk` → spun into `silk` (exists) → moth-silk cloth & the collector outfit; `luna_dust` → glow-dye + night-vision tonic |
| **emperor_moth** (`emperor_moth`) | Large eyespotted moth; flutters hard, "plays dead," then bursts away — a *patience* catch at night. Heavier silk yield. | Hedgerows, lantern light · **night** | **`emperor_silk`** (thick premium thread), **`eyespot_scale`** (the false-eye patch) | `emperor_silk` → premium silk cloth (T3 gear); `eyespot_scale` → an intimidation/`dodge` trinket + décor |
| **firefly** (`firefly`) | Drifts in low blinking swarms over damp grass after dusk; the blink is a real signal you chase. Catching them stores **living light**. Calm, never flees hard — but only out **at night**. | Damp meadow, pond margins · **night** | **`firefly_lumen`** (a captured glow-gland), **`firefly_dust`** (spent glow powder) | `firefly_lumen` → the whole **light-gear** line (lanterns, glow-armor, night-vision); `firefly_dust` → glow paint/dye + a soft décor light |
| **cicada** (`cicada`) | Loud, clingy day bug on tree trunks; sings, sits still, then makes one explosive jump when grabbed — a *timing* catch. Leaves its molted shell behind on bark. | Tree trunks, grove · **day** | **`cicada_shell`** (the empty exoskeleton), **`cicada_wing`** (the lacy wing) | `cicada_shell` → a light, springy armor plating (`dodge`/`fall_resist`) + a percussive décor chime; `cicada_wing` → a translucent décor inlay + a glide trinket |
| **hawk_moth** (`hawk_moth`) | *(bonus species — the "hummingbird" moth)* Fast, hovering dusk nectar-feeder with a long tongue; darts between blooms like a hover-bird. A **skill** catch — fastest in the zone; best `bug_value`. | Bloom clusters · **dusk** | **`hawkmoth_silk`** (fine fast-spun thread), `nectar` | `hawkmoth_silk` → lightest silk for the speed trinket; high `bug_value` sale; dusk-window catch teach |

**Day / night split (the zone's core hook):** day = butterflies + cicadas + the dusk hawk_moth window;
**night = moths + fireflies**, the glow economy, and the rarest sightings (glasswing at the dawn/dusk seam).
This is the first zone where **time of day changes what you can catch** — and where carrying **light** is
suddenly worth it (lanterns draw moths *to you*).

**Calm/catch teaching:** butterflies teach the *beautiful drift* (the core specimen catch), monarch the
*trophy*, glasswing the *lucky rare*, the moths teach *night + patience + light-luring*, fireflies teach
*the chase-the-blink*, cicadas teach *timing the jump*, hawk_moth teaches *raw speed*. Together they graduate
the player from "catch a hundred flies" to "catch the *one* perfect specimen."

---

## New ingredients & materials

Zone-signature gatherables + refined intermediates. Source = `forage` (pick), `drop` (from a bug), `craft`
(refined at a station). The refined goods are the bridge from raw drops to T2–T3 gear.

| Id | Source | Where found / made | Use |
|---|---|---|---|
| **`glow_bloom`** | forage | night-blooming flowers in shaded groves (open only after dusk) | glow-dye base, night-vision tonic, the firefly-bloom décor; a moth lure ingredient |
| **`milkweed_silk`** | forage | milkweed seed-pods (`milkweed` exists as flora; this is the floss) | a *plant* silk that stretches the silk supply; soft cloth filler + a stuffing for cushions/décor |
| **`spider_silk`** | forage/drop | dew-strung webs along hedgerows at dawn | strongest natural thread; the **net mesh** upgrade + a tough silk blend |
| **`luminous_resin`** | forage | sap weeping from glow-touched grove trees at night | a binder that *holds* light — sealant for glow-armor + a self-lighting varnish for décor |
| **`prism_dust`** | craft (jeweler) | `glass_scale` + `quartz` ground at the jeweler | refractive grit → the prism lens (light gear) + `gem_luck` charm core + shimmer glaze |
| **`spun_silk`** | craft (loom) | `moth_silk`/`emperor_silk`/`milkweed_silk` spun into `silk` (exists) at the loom | the gateway: raw cocoon thread → usable `silk`; everything cloth-tier flows through here |
| **`luminescent_thread`** | craft (loom) | `silk` + `firefly_lumen` woven at the loom | glowing thread → glow-cloth, light-trim on gear, the firefly lantern wick |
| **`butterfly_press`** | craft (workbench) | `butterfly_scale`/`monarch_scale`/`glass_scale` pressed under glass | the mounted-specimen tile for cabinet/cabin décor (feeds the specimen-jar line) |

*(`butterfly_scale`, `monarch_scale`, `glass_scale`, `moth_silk`, `emperor_silk`, `luna_dust`, `firefly_lumen`,
`firefly_dust`, `cicada_shell`, `cicada_wing`, `eyespot_scale`, `hawkmoth_silk`, `nectar` from the species
table are also crafting ingredients; listed there to avoid duplication.)*

---

## Recipes debuting here

T2–T3 gear/consumables/food/décor built from this zone's materials, gated up the metal ladder per
`progression.md`. Station per row (one output → one station, per `crafting.md §3`). `unlock`: **craft** (have
station + recipe) / **buy@cabin** / **find**. Costs use the tier-point model (Σ inputs).

### Light gear (the firefly line — the zone's signature tooling)

| Output | Station | Inputs (counts) | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| **firefly_lantern** (held light) | workbench | copper_bar 1 + glass 2 + firefly_lumen 2 | craft / buy@cabin | `light_radius +3`, `night_vision +1`; **draws moths** (lures night catches) | T2 |
| **lumen_jar** (belt light, hands-free) | workbench | glass 2 + firefly_lumen 1 + luminous_resin 1 | craft | `light_radius +2`, `night_vision +1` | T2 |
| **prism_goggles** (head, night-sight) | jeweler | bronze_bar 1 + prism_dust 1 + glass_scale 1 | craft | `night_vision +2`, `gem_luck +1` | T3 |
| **glowweave_cloak** (body, soft light armor) | loom | luminescent_thread 3 + silk 2 + iron_bar 1 | craft | `defense +3`, `night_vision +1`, `light_radius +1` | T3 |
| **resin_torch ×3** (placed light) | workbench | wood 2 + luminous_resin 1 + firefly_dust 2 | craft | placed `light_radius` source (no fuel; self-lit) | T2 |

### Silk & cloth (the moth line — soft-goods bridge to T3)

| Output | Station | Inputs (counts) | Unlock | Stat / use | Tier |
|---|---|---|---|---|---|
| **moth_silk_cloth** (`silk_cloth`) | loom | spun_silk 3 + thread 2 | craft | the zone's premium cloth bolt → all silk gear/décor below | T2 |
| **emperor_silk_cloth** | loom | emperor_silk 3 + spun_silk 2 | craft | premium T3 cloth (sturdier; gates the cloak/robe) | T3 |
| **silk_sash** (waist) | loom | moth_silk_cloth 1 + nectar 1 | craft / buy@cabin | `move_speed_pct +3`, `catch_radius +1` | T2 |
| **collectors_satchel** (carry) | loom | moth_silk_cloth 2 + spider_silk 2 | craft | `catch_cap +10`, `pickup_radius +1` | T2 |
| **silk_gloves** (hands) | loom | moth_silk_cloth 1 + thread 2 | craft | `catch_arc +12°`, `calm_radius +1` | T2 |

### Net upgrades & luck tooling (the rare-bug line — debuts the catch economy's depth)

| Output | Station | Inputs (counts) | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| **silk_net** (T2 net) | workbench | copper_bar 1 + spider_silk 3 + moth_silk_cloth 1 | craft / buy@cabin | `catch_radius +2`, `catch_arc +15°`, `catch_cap +5` | T2 |
| **collectors_net** (T3 net) | workbench | iron_bar 2 + spider_silk 4 + silk 2 | craft / buy@cabin | `catch_radius +3`, `catch_arc +20°`, `rare_bug_luck +1` | T3 |
| **luck_charm** (trinket) | jeweler | butterfly_scale 4 + silver_ore 1 + thread 1 | craft | `luck +1`, `rare_bug_luck +1` | T3 |
| **monarch_brooch** (trinket, rare-luck) | jeweler | monarch_scale 2 + gold_ore 1 + prism_dust 1 | craft | `rare_bug_luck +2`, `bug_value_pct +5` | T3 |
| **glasswing_lens** (held, sighting aid) | jeweler | glass_scale 2 + prism_dust 1 + glass 2 | craft | `rare_bug_luck +1`, `catch_radius +1` (spots rare spawns) | T3 |
| **calm_chime** (held) | workbench | cicada_shell 3 + bronze_bar 1 + thread 1 | craft | `calm_radius +2` (still-bug aura for clean specimen catches) | T2 |

### Consumables, bait & tonics (cauldron / cooking_pot)

| Output | Station | Inputs (counts) | Unlock | Effect | Tier |
|---|---|---|---|---|---|
| **nectar_lure** (butterfly bait) | workbench | nectar 2 + glow_bloom 1 | craft / buy@cabin | lures butterflies/moths to a spot (specimen-farm) | T2 |
| **glow_lure** (firefly/moth bait) | workbench | firefly_dust 2 + luminous_resin 1 | craft | a placed light that draws fireflies & night moths | T2 |
| **nightsight_tonic** (drink) | cauldron | luna_dust 1 + glow_bloom 2 + mint 1 | craft / buy@cabin | timed `night_vision +2` self-buff | T2 |
| **luck_draught** (drink) | cauldron | butterfly_scale 2 + nectar 1 + chamomile 1 | craft | short `rare_bug_luck +1`, `luck +1` ("lucky sighting" buff) | T2 |
| **calm_incense** (placed) | cauldron | lavender 2 + luna_dust 1 + sage 1 | craft | area `calm_radius` (bugs hold still — clean catches) | T2 |
| **steady_hand_tea** (drink) | cooking_pot | thyme 1 + nectar 1 + spun_silk 0 *(garnish: mint 1)* | craft | short `catch_arc` + `catch_radius` buff (the skill-catch aid) | T2 |

### Food (cooking_pot — timed buffs)

| Output | Station | Inputs (counts) | Unlock | Buff | Tier |
|---|---|---|---|---|---|
| **nectar_cake** | cooking_pot | wheat 2 + nectar 1 + honey 1 | craft | `luck +1` (short, "sweet luck") | T2 |
| **wildflower_honey_toast** | cooking_pot | wheat 1 + honey 1 + nectar 1 | craft / buy@cabin | `hp_regen` (short) | T2 |
| **glowberry_tart** | cooking_pot | berries 2 + glow_bloom 1 + wheat 1 | craft | `night_vision +1` (short) | T2 |
| **monarch_feast** | cooking_pot | corn 1 + pumpkin 1 + nectar 2 + sage 1 | craft | `rare_bug_luck +1`, `bug_value_pct +3` (short, the "trophy meal") | T3 |
| **silk_tea_biscuit** | cooking_pot | wheat 2 + nectar 1 + lavender 1 | craft | `calm_radius +1` (short) | T2 |

### Dye & glaze (dye_vat — the shimmer colors)

| Output | Station | Inputs | Unlock | Color / use |
|---|---|---|---|---|
| **shimmer_dye** | dye_vat | butterfly_scale 3 | craft | iridescent shift-color (the zone's signature finish) |
| **amber_dye** | dye_vat | monarch_scale 1 + dandelion 1 | craft | deep amber-orange |
| **glow_dye** | dye_vat | firefly_dust 2 + glow_bloom 1 | craft | softly luminous paint (faint light tag) |
| **luna_glaze** | dye_vat | luna_dust 1 + glow_bloom 1 | craft | pale-green pearlescent glaze (décor accent) |
| **prism_glaze** | dye_vat | prism_dust 1 + glass 1 | craft | rainbow-refractive coat for specimen frames |

### Décor & specimen line (workbench / sawmill / jeweler)

| Output | Station | Inputs (counts) | Unlock | Tag | Tier |
|---|---|---|---|---|---|
| **specimen_jar** | workbench | glass 3 + copper_bar 1 + cork 0 *(seal: luminous_resin 1)* | craft / buy@cabin | display décor (mounts one caught specimen; value scales with rarity) | T2 |
| **butterfly_display_case** | workbench | wood 4 + glass 3 + butterfly_press 3 | craft | premium wall décor (a row of pressed specimens; comfort aura) | T2 |
| **firefly_jar_lamp** | workbench | glass 2 + firefly_lumen 1 + wood 1 | craft / buy@cabin | living-light décor (`light_radius` aura, soft blink) | T2 |
| **glow_bloom_planter** | sawmill | plank 2 + glow_bloom 2 + luminous_resin 1 | craft | self-lighting planter décor (night glow) | T2 |
| **cicada_chime** | workbench | cicada_shell 3 + plank 1 + thread 1 | craft | ambient sound décor (a gentle chime aura) | T2 |
| **prism_window** | jeweler | glass_scale 2 + glass 4 + bronze_bar 1 | craft | stained-glass décor (casts colored light) | T3 |
| **scale_mosaic_tile ×4** | jeweler | butterfly_scale 2 + monarch_scale 1 + glass 2 | craft | shimmering floor/wall tile décor | T3 |
| **specimen_cabinet** *(station-décor)* | workbench | plank 6 + glass 3 + iron_bar 1 | craft / buy@cabin | the collector's storage+display unit (holds the specimen collection) | T3 |

---

## Signature gear — the **Entomologist's Regalia** (the collector bonus set)

The zone's flagship **set bonus** and the first set built around **catching** rather than fighting or farming.
It is a *collector's field outfit* — themed to the night specimen hunt — so its signature stats are
**`rare_bug_luck` + `catch_radius` + `night_vision`**, carried on a frame of real **`defense`** (this is a
T3 set; it should feel like a step up from village cloth). Built from the zone's prize materials:
**`moth_silk_cloth`/`emperor_silk_cloth`, `firefly_lumen`, `spider_silk`, `monarch_scale`, `prism_dust`**.
Four pieces; wearing all four grants the set bonus.

`bonuses{}` schema per `../stats_and_bonuses.md §1` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs (counts) | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| **entomologists_hat** | head | loom | moth_silk_cloth 2 + prism_dust 1 + firefly_lumen 1 | `defense:2, night_vision:1, rare_bug_luck:1` | `entomologist` |
| **entomologists_coat** | body | loom | emperor_silk_cloth 2 + spider_silk 3 + iron_bar 1 | `defense:4, catch_radius:1, rare_bug_luck:1` | `entomologist` |
| **collectors_gloves** | hands | loom | moth_silk_cloth 1 + spider_silk 2 + monarch_scale 1 | `defense:1, catch_arc:12, calm_radius:1` | `entomologist` |
| **lumen_boots** | feet | loom | moth_silk_cloth 1 + firefly_lumen 1 + luminous_resin 1 | `defense:2, move_speed_pct:3, night_vision:1` | `entomologist` |

**Set bonus (4/4 `entomologist`):**
> *"Out after dark, net in hand — the rare ones come to you."* — additional `rare_bug_luck:+2`,
> `catch_radius:+1`, `night_vision:+1`, `bug_value_pct:+5`.
> Signature: at **night** the coat's silk *glows softly* (a personal `light_radius` that **lures moths and
> fireflies toward you**), and rare specimens (glasswing, luna, emperor, hawk_moth) spawn-spot more reliably
> while worn — turning the night field into a generous, sparkling specimen hunt.

**Why this set, this stat:** the Fields are about *the beautiful rare catch under the stars*. A
`rare_bug_luck` + `night_vision` + `catch_radius` set is the perfect mechanical expression of that fantasy —
it rewards going out at night, makes the rarest sightings feel reachable, and is a clean contrast to the
village's *gathering* Forager's Kit and the *combat* armor sets of later zones. The real `defense` frame
(T3 silk + iron) means it's also the player's first genuinely *good* armor — survivability arrives wrapped in
the prettiest outfit in the game. Pairs naturally with `collectors_net`, `monarch_brooch`, and a
`firefly_lantern` for a full rare-hunt build.

*Optional 5th piece (stretch):* **glasswing_pendant** (trinket · jeweler · glass_scale 2 + prism_dust 1 +
silver_ore 1) → `rare_bug_luck:1, gem_luck:1` — pushes the set to a 5-piece deep bonus; prune if the
4-piece reads cleaner.

---

## Shop stock — **Collector's Cabin ("Mothwing's")**

The zone vendor: an old lepidopterist's cabin at the field's edge. Its hook is **net upgrades, specimen jars,
and the buy-only recipes** that open the silk/light/luck economy — plus it **buys specimens at a rarity
multiplier**, making the field your first serious coin engine (the rarer the bug, the more it pays). Stock
**grows as you turn in specimens** (a "completion" reward loop). Below is the mid-game shelf.

### Sells — goods
| Item | Why it's bought, not crafted |
|---|---|
| **silk_net** (T2 net) | guaranteed net upgrade on arrival (the first real catch boost) |
| **collectors_net** (T3 net, unlocks after specimen turn-ins) | the field's reward net |
| **specimen_jar** ×3 / **specimen_cabinet** | the display/storage core; reason to keep the cabin in mind |
| **firefly_lantern** / **firefly_jar_lamp** | light, on hand for the night loop |
| **nectar_lure** / **glow_lure** | the specimen-farm baits, bought cheap |
| **nightsight_tonic** | the night-vision consumable for early night runs |
| **silk_sash** / **wildflower_honey_toast** | a finished soft-good + a buff snack |

### Sells — recipes (buy → then craft)
| Recipe | Unlocks crafting |
|---|---|
| **moth_silk_cloth** | the whole silk → cloth bridge |
| **firefly_lantern** | the light-gear line |
| **luck_charm** | the rare-bug-luck tooling |
| **butterfly_display_case** | the specimen-décor loop |
| **nightsight_tonic** / **luck_draught** | the night + luck consumables |

### Buys — specimens (rarity multiplier; the coin engine)
caught bugs at a **rarity ladder** — `butterfly` < `cicada` < `monarch` < `hawk_moth` < `luna_moth` /
`emperor_moth` < `glasswing` (rarest pays most) · plus raw drops (`butterfly_scale`, `moth_silk`,
`firefly_lumen`, `cicada_shell`, `nectar`) and foraged goods (`glow_bloom`, `milkweed_silk`, `spider_silk`).
Raw sells cheap; **mounted specimens (in a jar) and crafted silk/light goods sell far more** — the
artisan-multiplier lesson, scaled up from the village.

---

## "New toys" hook

Butterfly Fields hands the player a **second clock**: the field is one world by day (butterflies, cicadas, a
dusk hawk-moth dash) and a completely different, glowing one by **night** (luna and emperor moths drawn to your
lantern, firefly swarms blinking over wet grass, the glasswing flickering at the dawn/dusk seam). The toy is
that **time of day changes the hunt** — and suddenly carrying *light* matters, because your `firefly_lantern`
*pulls the rare moths toward you*. Drops aren't dead-ends: butterfly scales become **shimmer dye** and your
first **luck charm**, moth cocoons spin into **silk → real T3 gear**, fireflies become **living-light armor**
that glows in the dark and lures the very bugs you're hunting, and cicada shells become a springy plate and a
wind-chime for your cabin. The **Collector's Cabin** closes the loop: catch the rare one, mount it in a
**specimen jar**, turn it in for a rarity-scaled payout, and watch the shelf unlock better nets — so chasing
"the one perfect glasswing" is both the prettiest moment in the game *and* your best paycheck. And the
**Entomologist's Regalia** makes it self-reinforcing: the better you dress for the night hunt, the more the
rare ones come to you.
