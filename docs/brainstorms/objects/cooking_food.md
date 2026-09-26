# Cooking Stations & Food — Brainstorm

Cooking stations across the capacity progression, plus the dishes/foods they make — including the
signature BUG foods — and the buffs they grant. Design only.

Read alongside:
- `docs/product/design/game_design.md` §11.7 (stove capacity progression) and §11.6 (fuel vs power).
- Existing ids: `campfire`, `campfire_spit`, `cooking_pot`, `stove_wood`, `stove`, `range_stove`,
  `fireplace`, `kitchen_island`, `counter`/`counter_fancy`, `fridge`, `sink`, `cupboard`, `keg`.
- Bug-food inputs come from `bug_farming.md` (honey, honeydew, royal jelly, grubs, cricket flour, silk-
  adjacent) and `farming_tools.md` processing (flour, oil, cider).

## Rules this file follows
- **Stove capacity = simultaneous dishes**, gated by tier + fuel/power (§11.7). Wood stove = 1 dish,
  manual fuel; ranges cook several; electric range = top capacity, needs power (§11.6).
- Buffs are **soft, meaningful, temporary** (cf. §15 "small bonuses", §16 "soft modifiers"). No stat
  trees; food is a prep/consumable layer.
- Variety across poor→fancy; bug foods are a first-class, distinctive branch.

---

## 1. COOKING STATIONS (capacity progression)

| id | one-line | tier | capacity / fuel | role |
|----|----------|------|-----------------|------|
| `campfire` *(exists)* | open log fire | starter | 1 dish, burns wood | first cooking, outdoors/camp |
| `campfire_spit` *(exists)* | fire with a roasting spit | starter | 1 dish (roasts), wood | roast meat/skewers |
| `cooking_pot` *(exists)* | a cauldron pot over heat | starter | 1 dish (soups/stews), wood | soups, stews, boils |
| `clay_oven` | a domed clay/cob oven | poor | 1 dish (bakes), wood | bread, baked dishes |
| `stove_wood` *(exists)* | cast-iron wood stove | common | 1 dish, manual wood fuel | the §11.7 starter stove |
| `stove` *(exists)* | 2-burner enamel stove | mid | 2 dishes, fuel | step up |
| `range_stove` *(exists)* | 4-burner range + oven | high | 4 dishes, fuel | the "4-burner range" of §11.7 |
| `range_electric` | sleek electric range | top | high capacity, needs POWER (§11.6) | top-tier, no fuel |
| `brick_oven` | a built-in brick baking oven | high | 2 dishes (bake), fuel | pizzas/pies/bread at scale |
| `kitchen_island` *(exists)* | prep island | — | prep surface (not heat) | speeds prep / extra counter |
| `prep_counter` (cf. `counter`) | a kitchen prep counter | — | prep surface | chopping/mixing station |
| `grill_outdoor` | an outdoor charcoal grill | mid | 2 dishes (grill), fuel | yard cooking, BBQ dishes |
| `tea_kettle_stand` | a small kettle on a stand | poor | drinks only, fuel | teas/tonics (bug tonics below) |

Support appliances (extend kitchen set): `fridge` *(exists, store perishables longer)*,
`sink` *(exists, prep/clean)*, `cupboard` *(exists, ingredient store)*, `ice_box` (poor fridge),
`spice_rack` (small buff to dish quality), `mixing_bowl_stand` (prep), `mortar_kitchen` (grind
spices — distinct from the alchemy mortar).

---

## 2. DISHES & FOODS (plant/crop based) + buffs

Buffs are short, soft, stackable-with-care. Tiers roughly follow ingredient value.
| id | one-line | tier | buff |
|----|----------|------|------|
| `bread` | a baked loaf from flour | poor | small, long stamina-of-effort... (energy regen) over time |
| `veggie_soup` | a simple vegetable soup | poor | minor heal + brief warmth (cold-weather soft mod) |
| `corn_roast` | a roasted corn cob | poor | small instant heal |
| `tomato_stew` | a hearty tomato stew | common | heal + brief defense nudge |
| `wheat_porridge` | warm grain porridge | poor | slow regen, cheap filler |
| `fruit_pie` | a baked fruit pie | common | heal + small move-speed for a while |
| `salad_fresh` | a crisp garden salad | common | minor heal + foraging/inspect clarity |
| `herb_tea` | brewed herb tea (chamomile/lavender) | poor | calm — reduces nearby swarm agitation you cause |
| `berry_jam` | preserved berry jam | common | small heal, shelf-stable, stackable |
| `pickled_veg` | crock-pickled vegetables | poor | minor heal, very shelf-stable |
| `roast_dinner` | a big roast plate | high | strong heal + defense for a long duration |
| `mushroom_skewer` | grilled foraged mushrooms | common | regen; glowing-mushroom variant = night-vision-ish glow |
| `feast_platter` | a grand multi-dish feast | fancy | broad multi-buff; party/showpiece dish |

---

## 3. BUG FOODS (the signature branch) + buffs

The crossover that makes "farm bugs" pay off at the table. Inputs come from penned/bred bugs
(`bug_farming.md` §4) and beekeeping (`beehive_*`, `honey_extractor`).
| id | one-line | input | buff |
|----|----------|-------|------|
| `honey` | raw golden honey | beehives + extractor | small sustained heal; sweetener ingredient |
| `honeycomb` | a chunk of wax comb + honey | hives | heal + yields beeswax (candles, see lighting) |
| `honeydew_syrup` | syrup boiled from aphid honeydew | `honeydew_tap`/aphid ranch | energy/regen; gentler than honey |
| `royal_jelly_tonic` | a potent royal-jelly drink | queen-rearing bees | strong temporary vitality/regen; rare |
| `candied_grubs` | sugar-glazed roasted grubs | bred grubs (`grub_bed`) | dense instant energy; portable snack |
| `cricket_flour` | ground roasted-cricket flour | farmed crickets + `grain_mill` | a protein flour ingredient (sub for flour, +buff) |
| `cricket_protein_bar` | a pressed cricket-flour bar | cricket_flour | sustained stamina-of-effort over a long duration |
| `grub_skewer` | grilled grubs on a stick | bred grubs | hearty heal; rustic |
| `ant_egg_caviar` | delicate ant-egg "caviar" (escamoles) | `ant_formicarium`/`ant_eggs` | refined buff: inspect/perception clarity; fancy |
| `bee_brood_fry` | pan-fried bee brood | hives | protein heal |
| `silkworm_pupae_snack` | boiled silkworm pupae | `silkworm_tray` | cheap protein snack + minor regen |
| `mantis_skewer` | grilled large-bug meat | farmed large bugs | strong heal; "exotic" high-value plate |
| `chitin_crisps` | crispy roasted beetle shells | farmed beetles | brief defense nudge (armor flavor) |
| `glowbug_jelly` | luminous jelly from glow-bugs | glow-bugs | brief night-glow (see yourself in the dark) |
| `nectar_cordial` | a sweet nectar drink | butterfly/bee nectar | calm + small regen |
| `royal_feast` | a grand all-bug banquet | many bug foods | top showpiece dish; broad strong buffs |

Bug-food intermediates (ingredients, not eaten raw): `beeswax`, `raw_honeydew`, `royal_jelly`,
`raw_grubs`, `bug_protein_meal`. (These also feed `alchemy_potions.md` and `lighting_ambiance.md`.)

---

## 4. BUFF CATEGORIES (for consistency when these get values)

Keep buffs to a small soft palette so cooking stays prep, not a stat tree:
- **Heal** (instant HP) — most savory dishes.
- **Regen** (HP over time) — soups, honey, tonics.
- **Energy/effort** (faster actions / less fatigue feel) — breads, bars, candied grubs.
- **Defense nudge** (brief soft armor) — roasts, chitin crisps.
- **Move speed** (brief) — pies, light fare.
- **Calm** (you agitate nearby swarms less — bug-farming synergy) — teas, nectar cordial.
- **Perception/inspect clarity** (easier reading of ecology/specimens, §17) — salads, ant-egg caviar.
- **Night glow** (see in the dark briefly) — glowbug jelly, glowing-mushroom skewer.

---

## Open questions / follow-ups
- Buff magnitudes/durations + whether they stack belong in the economy/ecology proposal, not here.
- Recipe inputs assume crops/bugs that may not all exist yet — reconcile with the crops/bugs
  brainstorms as those grow.
- `range_electric`/automation cooking need the §11.6 power flag *when that system ships*.
