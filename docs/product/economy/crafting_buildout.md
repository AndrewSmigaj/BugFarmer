# Crafting buildout — PROPOSAL for sign-off (decision-grounded)

Status: **PROPOSAL** — Andrew reviews before authoring (per D26 "recipe creation is mine to author, Andrew
reviews"). Scope is bounded by **D17** (build only what the **Village** + **Mining Camp / Underground Passages**
need) and the decision log, NOT by my older `crafting.md` prose. Every line cites its decision.

## What's OUT of this pass (decision-backlogged — do NOT author)
- **Potions / alchemy** — D16 ("what's backlogged is POTIONS & ALCHEMY"). → cauldron gets no recipes now.
- **Cooked food** — D19 ("Food recipes = a separate system → backlog"; only `forager_stew` is *sold*). →
  cooking_pot / campfire get no food recipes now.
- **Armor tier expansion** — backlogged this session (each worn piece = ~12 hand-authored paper-doll PNGs;
  ~420 for the ladder). Existing leather/iron stay. (D11 also backlogs armor *defense* values.)
- **Accessories / jeweler** — D26 ("Accessories → BACKLOG") + this session. Gems are produced; jeweler+accessory
  recipes ride the accessories backlog.
- **Keg artisan goods (wine/mead)** — D26 (wine_rack + bigger kegs → bee zone). Keg stays a buildable station,
  no artisan recipes now.
- **Electronics** — D26 (buy-only, no player recipe). **Fishing, land deeds, sprinkler bonuses** — backlogged.

## What's IN (build now)

### 1. Mining refine chain — the centerpiece (D13, D19, D26)
D26's model: **`ore → rock_crusher → paydirt → ore_sluice → bars`** (raw ore sells at the Miner's Outpost; the
Blacksmith buys BARS). This session you picked the **per-mineral deterministic** shape with a refine tier +
smelt step. **⚠ CONFIRM #1 — which chain length:**
- **(A) Session model:** `raw {m}_ore → [crusher] → {m}_paydirt → [sluice] → refined_{m}_ore → [furnace +coal] → {m}_bar`
- **(B) D26 literal (simpler):** `raw {m}_ore → [crusher] → {m}_paydirt → [sluice +coal?] → {m}_bar` (sluice
  yields the bar; furnace only does glass/charcoal)
- Metals in scope (have ore blocks + bar recipes today): **copper, iron, tin, silver, gold, platinum**. Doing
  all six keeps the chain complete (no half-ladder). Coal is a consumed input at the smelt step (from coal
  blocks, D-confirmed). New items per metal: paydirt + (model A) refined ore. New: `rock_crusher` placeable,
  wire `ore_sluice`, `charcoal` (wood→furnace, coal substitute). Delete the dead self-droppers
  (`ore_pile`/`ore_sack`/`coal_bin`/`geode`).

### 2. Gems — crushable blocks (Minecraft/Terraria style, user-confirmed)
**Gem blocks** (diamond, sapphire, ruby, emerald, topaz, …) are mined, then **crushed at the rock_crusher →
the gem** (NO sluice, NO smelter, no intermediate). **⚠ CONFIRM #2 — the gem-block set**: which gems exist
(propose: diamond ✓existing, sapphire, ruby, emerald, + quartz ✓existing). Today `ore_diamond_block`/
`quartz_block`/`crystal_*` drop the gem DIRECT → change them to drop a block/raw form that the crusher turns
into the gem. Gems are **sellable** this pass (consumer = jeweler, backlogged).

### 3. Metal bars + the base-material ladder — "just get built" (D26)
- Bars: copper/iron (furnace), bronze (copper+tin, forge), steel (iron+coal, forge) + silver/gold/platinum
  (exist) — all fed by the refine chain (#1).
- Base mats (D26 names them explicitly): **plank** (sawmill ✓), **cloth** (loom ✓ thread→cloth), **glass**
  (furnace ✓), **leather** (Bug Extractor, #5). Complete the loom cloth line (thread→cloth→cloth goods).

### 4. Tools & weapons — metal tiers + the D12 specials (auto-unlock, D26)
- **Metal-tier ladders** for **pickaxe / axe / sword / spear** at the tiers the two zones reach (wood→stone→
  copper→bronze→iron→steel; silver a stretch). Icons = free `recolor_sprites.py` (verified ramps exist).
  Fix the real bug: `sword_copper`/`spear_copper` lack `tool_tier`.
- **D12 specials:** add a **saw** (wood tool above axes), a harvest **sickle**. Watering cans + nets stay
  **small + large only** (NOT tiered).
- **⚠ CONFIRM #3 — weapons:** this session you bundled "weapon tiers" into the armor backlog, but weapons are
  just ICONS (no paper-doll overlay) so they're cheap like tools, and D26 has the Blacksmith selling "weapons
  beyond wood." Build the metal-tier sword/spear now (cheap), or keep them backlogged with armor?

### 5. Bug Extractor — dead_<bug> → materials (D18)
Each `dead_<bug>` (the 6: fly/butterfly/wasp/centipede/millipede/beetle) → a material. D18: chitin, **leather**,
silk, etc. Propose: `dead_beetle → chitin` (✓exists), `dead_*` → **leather** (the base mat), spider/silk later
(no spider in the village 6). **⚠ CONFIRM #4 — the per-bug → material map** (which bug yields what).

### 6. Per-station craft-slot mechanic (user-approved) — ✅ BUILT 2026-07-03
`craft_slots` on stations (default 1); N parallel recipe lanes (`Procs`) sharing one output grid; legacy-save
migration; lane-targeted craft ops; CraftingPanel lane rows. See architecture_crafting.md + DECISIONS D30.
(The "stoves differ by capacity" flavor is pending cooking recipes — campfire/stove have none yet.)

## Systems also in this pass (not recipe content)
- **Barter sell UI** (atomic `sell_batch` op — good design, not a client loop).
- **Stocked test zone** (authored `InitialContainers` seed mirroring `InitialCarrion`) + mannequin.
- **Mockups** of every in-scope station (craft + breeding) + the architecture_crafting.md update.

## The four CONFIRMs — RESOLVED (user, this session)
1. **Mining chain = model A** (refine + smelt): `ore → crusher → paydirt → sluice → refined → furnace+coal → bar`,
   for **all 6 metals** (copper/iron/tin/silver/gold/platinum — no half-ladder). Sluice takes only paydirt (no
   water). tin → refined_tin_ore → bronze (no tin_bar). **Ignore D26's shorter `sluice→bars` — user disavows D26.**
2. **Gems = crushable blocks** (diamond ✓, sapphire/ruby/emerald NEW, quartz ✓) → crusher → **raw gem** → a NEW
   **`gem_cutter` station** → **cut gem**. (Not "metal+gem at a jeweler" — that's backlogged.)
3. **Weapons = all metal tiers, built now** (they're swung, not just icons; sprite *visual polish* backlogged,
   the items are not).
4. **Bug map:** `dead_beetle/centipede/millipede/wasp → chitin`; `dead_fly/butterfly → leather`; silk deferred.

> Note: this doc earlier cited **D26** and listed jeweler/preserves_jar as in-scope — both corrected above.
> Authority is the user's direct words, not any doc (incl. DECISIONS.md, which carries my misattributions).
