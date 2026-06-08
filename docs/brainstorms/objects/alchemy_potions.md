# Alchemy Stations & Potions — Brainstorm

Brewing/extraction stations and the potions, elixirs, extracts, and dyes made from plants, fungus,
and BUG PARTS. The bug parts are the signature crossover that makes "farm bugs" feed the alchemy
loop. Design only.

Read alongside:
- `docs/product/game_design.md` §11.3 (extractors/processing stations), §15 (small meaningful
  bonuses, no loot treadmill), §16 (soft modifiers).
- Existing ids: `cauldron`, `cooking_pot`, `mortar`-adjacent, `keg`, `still`-adjacent, `furnace`,
  `compost_bin`, `honey_extractor` (bug extraction precedent).
- Bug-part inputs from `bug_farming.md` (§4 breeding/growing) and `cooking_food.md` intermediates
  (royal_jelly, beeswax, honeydew, silk via silkworms).

## Rules this file follows
- Buffs/effects are **small, meaningful, temporary** (§15) — alchemy is a prep/utility layer, not a
  power curve. Many overlap the cooking buff palette (`cooking_food.md` §4) but lean utility/combat.
- **Bug parts are first-class ingredients** (formic acid, venom, royal jelly, silk, chitin, glow) —
  the whole point of the crossover.
- Stations tier poor→fancy; "quality" is value/material tier. Some are fuel-fed/electric (§11.6).

---

## 1. ALCHEMY STATIONS

| id | one-line | tier | role |
|----|----------|------|------|
| `mortar_pestle` | a stone mortar and pestle | starter | grind herbs/fungus/chitin into powders/pastes |
| `herb_grinder` | a cranked herb grinder | poor | faster bulk grinding |
| `cauldron` *(exists)* | a hanging brewing cauldron | common | brew potions/elixirs (fuel) |
| `brewing_stand` | a small multi-flask brewing rack | mid | brew several small batches |
| `still_copper` | a copper pot still | mid | distill extracts/spirits/essences (fuel) |
| `alembic` | a glass alembic distillation set | mid | fine extracts, essential oils |
| `extractor` (cf. `honey_extractor`) | a press/centrifuge for bug parts | mid | extract venom/acid/jelly cleanly |
| `dye_vat` | a big vat for dyeing | common | brew dyes (fuel/heat) |
| `alchemy_lab` | a full lab bench with glassware | high | top-tier brewing; many recipes (electric-capable) |
| `alchemy_lab_grand` | an ornate arcane laboratory | fancy | showpiece + best yields/rare recipes |
| `drying_rack` (shared w/ farming) | dries herbs/fungus for potency | poor | ingredient prep |
| `fermenter` (cf. `keg`) | a sealed fermenting vessel | mid | tinctures, fermented extracts |

---

## 2. INGREDIENTS — bug parts (the crossover) + plants/fungus

### 2.1 Bug-derived ingredients (from penned/bred/harvested bugs)
| id | one-line | source |
|----|----------|--------|
| `formic_acid` | sharp ant-derived acid | farmed ants (`ant_formicarium`) |
| `bee_venom` | potent bee venom | farmed bees |
| `wasp_venom` | aggressive wasp venom | farmed wasps |
| `spider_venom` | spider venom | farmed spiders |
| `scorpion_venom` | scorpion venom | farmed scorpions |
| `royal_jelly` | rich queen-bee jelly | queen-rearing hives |
| `raw_honey` / `honeydew` | sugars | hives / aphid ranch |
| `beeswax` | wax | honeycomb |
| `silk_thread` | strong spider/silkworm silk | spiders / `silkworm_tray` |
| `chitin_powder` | ground beetle/arthropod shell | farmed beetles (via `mortar_pestle`) |
| `glow_extract` | luminous fluid from glow-bugs | farmed glow-bugs |
| `moth_dust` | scale dust from moth wings | farmed moths |
| `butterfly_essence` | delicate winged essence | farmed butterflies |
| `centipede_oil` | pungent myriapod oil | farmed centipedes |
| `ant_egg_paste` | protein-rich egg paste | ant farm |

### 2.2 Plant / fungus ingredients (extend existing flora)
Existing crop/forage ids include `chamomile`, `lavender`, `yarrow`, `wild_berries`,
`red_mushroom`, `glowing_mushroom`, `brown_mushroom`, `chanterelle`, `puffball`, `sunflower_seed`,
`flower`, `fiber`. Alchemy-specific intermediates:
| id | one-line | role |
|----|----------|------|
| `herb_essence` | distilled herb extract | base for calming/heal potions |
| `mushroom_extract` | concentrated fungus extract | toxins, antidotes, glow |
| `glow_spores` | spores from glowing mushrooms | light/glow potions (+ glow-bug crossover) |
| `root_tincture` | a bitter root tincture | bittering/stabilizing agent |
| `flower_petal_dye` | crushed-petal pigment | dyes |
| `berry_juice` | crushed berry juice | dyes + sweet bases |
| `tree_resin` | sticky tree resin | binder/varnish, salves |

---

## 3. POTIONS & ELIXIRS + effects

Soft, temporary, utility-leaning. Tiers follow ingredient value.
| id | one-line | key ingredient | effect |
|----|----------|----------------|--------|
| `heal_potion` | a red healing draught | herbs + honey | instant heal (tiered minor→strong) |
| `regen_elixir` | a slow-healing elixir | royal_jelly + herbs | HP over time |
| `antidote` | a venom/toxin antidote | yarrow + mushroom_extract | cures poison/bug-sting effects |
| `calm_draught` | a soothing brew | chamomile + lavender | YOU agitate swarms far less (bug-farm synergy) |
| `vigor_tonic` | an energizing tonic | royal_jelly_tonic base | faster actions / less fatigue (brief) |
| `venom_vial` | a coating of bug venom | bee/wasp/spider venom | weapon coat: bonus damage vs bugs (combat, §14) |
| `acid_flask` | a thrown formic-acid flask | formic_acid | thrown: damage + weakens fences/shells (utility) |
| `glow_potion` | a luminous draught | glow_extract / glow_spores | night-glow, see in the dark (brief) |
| `swiftness_brew` | a quickening brew | moth_dust + herb_essence | move-speed (brief) |
| `ironhide_tonic` | a toughening tonic | chitin_powder | brief soft defense (§15-scale) |
| `lure_oil` | a smeared attractant oil | butterfly_essence/pheromone | makes a placed trap/lure stronger (bug-farm) |
| `repellent_balm` | a bug-repelling balm | centipede_oil + herbs | nearby hostile bugs keep their distance (brief) |
| `clarity_elixir` | a perception brew | mushroom_extract + essence | sharper ecology/inspect reading (§17) |
| `silk_salve` | a binding salve | silk_thread + resin | patches/repairs gear or fences (utility) |
| `panacea` | a grand cure-all | many rare parts | broad strong cure + buff; rare showpiece brew |

---

## 4. EXTRACTS, OILS, DYES & misc products

| id | one-line | from | use |
|----|----------|------|-----|
| `venom_extract` | refined concentrated venom | bug venoms | high-value sell + pot/coating base |
| `royal_jelly_extract` | concentrated jelly | hives | premium tonic/sell ingredient |
| `essential_oil` | a distilled plant oil | herbs (alembic) | ambiance, cosmetics, mild buffs |
| `glow_ink` | luminous ink | glow_extract | glowing signs/markings (decor crossover) |
| `dye_red` / `dye_blue` / `dye_yellow` | basic dyes | petals/berries/minerals | dye gear, furniture, fabric |
| `dye_purple_royal` | a rich royal-purple dye | rare bug/plant mix | prestige dye (high value) |
| `dye_iridescent` | a shifting iridescent dye | moth_dust/butterfly_essence | fancy cosmetic dye (bug crossover) |
| `wax_polish` | a beeswax polish | beeswax | shines/preserves wood furniture |
| `varnish` | a resin varnish | tree_resin | protect/finish crafted items |
| `pigment_powder` | ground mineral/petal pigment | minerals + petals | art/paint (cf. `easel`) |

---

## 5. EFFECT CATEGORIES (keep it a soft palette, §15)

- **Heal / Regen / Antidote** — survival staples.
- **Calm** (you spook swarms less) and **Lure-boost** / **Repellent** — direct bug-farming synergy.
- **Combat coatings** (venom/acid) — small, prep-based, vs bugs (no power curve).
- **Utility** (glow, swiftness, clarity, silk_salve repair) — situational tools.
- **Defense nudge** (ironhide) — brief, soft.
- **Cosmetic / craft** (dyes, polish, varnish, glow_ink) — non-combat value + decoration.

---

## Open questions / follow-ups
- Effect magnitudes/durations + recipe quantities go in the economy/ecology proposal, not here.
- Some bug parts assume bugs that may not exist yet — reconcile with the bugs brainstorm as it grows.
- `venom_vial`/`acid_flask` touch combat (§14) — confirm the "no loot treadmill" line holds (these
  are consumable prep, not permanent power).
- `alchemy_lab` electric tier + extractor automation get the §11.6 power flag *when that ships*.
