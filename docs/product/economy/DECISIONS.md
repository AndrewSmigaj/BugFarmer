# Economy / World — Decisions log

The single place design decisions live, so they're never scattered across docs. Each entry: the decision,
the why, and a pointer to where it's elaborated. **Open** items are unresolved forks — don't assume them.

---

## Resolved (2026-06-25)

### D1 — Stations are crafted OR bought (not "built")
Basic/intermediate stations (workbench, furnace, anvil, stonecutter, loom, sawmill, cauldron, cooking_pot…)
are **crafted** from materials. Complex/advanced stations a player would never realistically build — e.g. the
**electronics bench**, high-tech machinery — are **BOUGHT from a merchant** (a coin sink). A rare one may be
**found**. There is no separate "build" mechanic; a station is just a placeable obtained by recipe or purchase.
*Why:* matches the decoration rule (most craftable, some bought/found) and keeps the engine simple (no new
system). → `crafting.md` (recipes), `merchants.md` (which are sold).

### D2 — Drop row 5 from the world (re-add later)
The world becomes **rows 0–4**. The deepest underground row (Centipede Depths / Deep Passages / Deep River /
Ant Queen Chamber) is removed for now; its rare ores (silver→diamond) compress up into **row 4**, gated by the
harder east columns. *Why:* shrink initial authoring scope; re-add depth later. → `../architecture/architecture_world.md`.

### D3 — Underground col-0: Centipede → Ants
Underground **col 0** (was Centipede Cavern easy+medium) becomes **Ants** — easy ants (row 3) + medium ants
(row 4), and the **medium ant zone gets a Queen** (mini-boss, relocated from the dropped row-5 chamber). The
**Centipede Cavern** moves to the **medium-passages slot (4,1)**. The deep/deadly ants shift **up a row** and
keep **surface access to the col-3 Swamp** for foraging. *Why:* user direction. → `../architecture/architecture_world.md`.

### D4 — Balance = pacing, not minimalism
*Replaced 2026-09-28 (D55): content can be cut — every item gets a pass that may cut it.*
Every gating/pricing choice is reasoned against named Schell lenses (Flow/Curve, Pacing/Reward, Economy,
Meaningful Choices/Triangularity, Need/Toy). Each content category has a **target FLOOR** (a minimum count) —
floors, not ceilings; tuning adjusts numbers, never deletes content. → `progression.md`, `crafting.md`.

### D5 — Fishing deferred; décor bonus values deferred
*Replaced in part 2026-09-27 (D51): fishing starts in the village from the start.*
Fishing is **out for v1** (design the rod + fisherman's vest only). Décor passive-bonus **VALUES** are not
authored yet (the §11.5 field is unbuilt) — we only **tag the bonus TYPE** per décor item. → `crafting.md`.

### D6 — Single coin currency
*Replaced in part 2026-09-27 (D52): one coin, and barter too, as in Baldur's Gate.*
One coin type (matches the existing `sell_price`/`buy_price` on items), not barter. *Why:* simplest, already
priced. → `merchants.md`.

### D7 — Surface terrain is fixed (no surface-floor digging)
Resolves O1. Surface **floor** tiles are never dug/removed (engine rule: "ground always filled, no holes").
Players gather via diggable **block nodes** + mining-cliff tiles; "terraforming" = *placing* a floor tile on
top. **Water care:** two water tiles exist — `water_shallow` (wade; blocks insects) and `water_deep` (blocks
both) — any water placement/feature must respect both. → `../architecture/architecture_world.md`.

### D8 — Sand is a diggable BLOCK in sandy/beach clumps
Resolves O2. Sand is a **block** you dig through like stone/clay (break → drops `sand` → reveals floor),
placed as **small clumps in sandy/beach areas** — NOT harvested from the sand *floor* tile (which stays
decorative). Uses the existing `sand_block` concept. → `../architecture/architecture_world.md` (resource map),
`crafting.md` (sand → glass).

### D9 — Keep both ant colonies
Resolves O3. **Col 0** = a gentle intro ant colony (easy/medium + the Queen); **col 3** = the deadly endgame
ant colony (hard/extra-hard) that forages out to the surface swamp. Ants are a deliberate recurring theme
across difficulty. → `../architecture/architecture_world.md`.

---

## Open (unresolved)

*(none currently open — all forks resolved as of 2026-06-25; new ones get logged here)*

---

## Synthesis / prune notes (content pass, 2026-06-25)

The per-zone + catalog content was generated GENEROUS by design (over-produce → prune). Known cleanups for
the pruning pass:
- **Spider Vale East vs West silk/venom ladders** — East generated before West landed, so it used a parallel
  lineage; reconcile the two silk ladders.
- **`paper_wasp` double-listed** (Wasp Thicket threat + Meadow pest-control ally) = the single existing `wasp`.
- **Material aliases to fold** (flagged in `catalogs/materials.md`): `moth_silk_cloth`→`silk_cloth`,
  `glowshroom`→`mushroom_glow`, `tanned_leather`→`tanned_hide`; overlapping glow/venom reagents.
- **Optional 4th/5th set "band" accessories** (`colonist_band`, `prospector_band`, `spelunker_band`,
  `delver_band`, `warden_band`, `widow_locket`) are prune candidates that may fold into their marquee charm.
- New hazard/effect verbs introduced by zones (`scorched`/`ignited` fire, `corroded` acid, `envenomed`) should
  be reconciled into the canonical vocab in `stats_and_bonuses.md` if they survive pruning.
- Counts in `README.md`'s coverage table are the **design-stage maxima**; pruning toward a shippable set is the
  intended next step.

---

## Finalize pass — content rulings (2026-06-25, from review)

### D10 — Set philosophy: sets are CONCEPTUAL, not one-per-zone
*Replaced in part: no diving, so no diving set (August 2026); waders become a wading outfit for shallow water (D51).*
A signature set represents a *concept* (beekeeping, ranger, mining, diving, bug-catching, chitin armour), and
may span multiple zones — NOT one set per zone. A thorough roster = a balanced amount per category, **not excessive,
not lacking**. Consolidated bonus-set roster (replaces the 17 per-zone sets):
- **Ranger** — Wasp Thicket (east of village, half-woods, ranger station). The early exploration/woodland set
  (replaces the old *Forager* and *Thornweave* — "thornweave" cut, weaving thorns doesn't read).
- **Beekeeper** — a multi-tier line across the bee zones (folds *Hive-Keeper* + *Apiarist*); ties to the
  beekeeping system (see backlog).
- **Entomologist** — the bug-CATCHING set: boosts calm-spray, nets, `catch_*` (from Butterfly Fields, used
  broadly). Keep.
- **Miner / Spelunker** — one mining line (folds *Prospector* + *Spelunker* + *Deep-Delver*): light, mining
  speed, carry, vein_sense, hazard.
- **Diver / Waders** — aquatic line (folds *Marshwalker* + *Bog-Hunter* + *Cave-Diver*). **Waders are
  functional gating** (needed to enter certain water/swamp areas), not just a stat set.
- **Chitin / Carapace** — a bug-derived heavy-armour line (folds *Carapace Warden* + *Colonist*).
- **Silk** (late, pending) — light/agility spider-silk set; the *Widow* endgame variant folds in here.
- **CUT:** Forager, Thornweave, Swarm-Warden (locust = an interesting *area*, no set), Fire-Warden (no
  firewarden).
- Swamp: not designed yet → it gets a swamp **vendor** + waders; a swamp set is optional/pending.
- Far/late zones: **design but mark PENDING** until we reach them.

### D11 — Base armour: leather→platinum, no straw, no diamond
*Replaced 2026-09-28 (D61): armour follows the tool metals up to cobalt steel; platinum goes into a fancy armour that also needs steel.*
Base metal sets = **leather · padded(cloth) · copper · bronze · iron · steel · silver · gold · platinum**
(9). **Straw cut** (too hard to integrate). **Platinum is the top — no diamond armour** (doesn't make sense).
- **Leather** comes from the **Bug Extractor** (dead bugs → leather, D18; no skinning mechanic).
- **Cloth** comes from multiple sources: **silk + cotton** (cotton is a LATER crop, not Zone 1 — D15/D19).
- Per-zone armour DEFENSE values get tuned against each zone's enemy damage → **backlog** (armour-balance).

### D12 — Tools: trim to "metal tiers + a few meaningful specials"
*Partly replaced 2026-09-29 (D69): axes are stone, iron and steel; an axe can fell a big tree, slowly, and the saw is much faster; the cast net is settled.*
- **Picks:** metal tiers only — NO special pick variants. **Cut** `deepcut_pick`, `fortune_drill`,
  `fortune_pick`, `scorpion_pick`(as tool). (effective-tool-tier is a property of higher picks, not a separate
  tool.)
- **Watering cans:** **small + large ONLY** (cut steel/gold/platinum). Farming is **early-unlocked**, not
  gated behind fancy metals — delayed only by material affordability.
- **Nets:** small + large hand nets now (large = just bigger). **Bug-size matching** (a small net can't hold a
  big bug) and **cast/thrown nets** + better nets → **backlog** (alongside bows — neither mechanic exists yet).
  Cut `silk_net`/`gossamer_net` metal framing for now.
- **Saw:** ADD — a wood tool a tier ABOVE the current axes, for larger/tougher trees in forest zones; better
  axes arrive later above it (so axes don't go useless). Larger/tougher trees needed in those zones.
- **Harvest sickle:** AoE plant-harvest (cuts MORE plants per swing than normal harvesting); larger wheat
  fields exist. (Drop the swarm-specific framing.)
- **Bee smokers:** ≥3 tiers (faster/stronger bees; some bees hostile) — part of the beekeeping system (backlog).
- **Fishing:** rod **tiers** (not cave-vs-normal); **NO harpoons** (cut `cave_harpoon`, `harpoon_gun`). A
  fishing **mini-game** (backlog). **Fish traps** = passive over-time catchers, capacity-capped like all
  stations, with faster/better-effectiveness tiers.
- **Light:** keep a FEW that make sense — `firefly_lantern` (catch fireflies, **first area**), a **headlamp**
  (hands-free), `glowworm_lantern` (green), **torches** (many cosmetic). **Cut** `catcher_lantern`,
  `ranger_lantern`, oil lanterns/`bog_lantern_oil` (bugs are the light source). **Light décor** only where it
  makes sense; décor bonuses are a **separate home-plot system** (backlog).
- **Catching:** keep `bug_vacuum` (hand vacuum) + `autonet` (auto-collector, sprite exists). **Cut `shears`** —
  cut webbing for silk with a sword/blade instead.
- **Cut:** `dowsing_rod`, `watering_wand`. **Keep `magnifying_glass`** (essential, given **from the start** —
  inspect bugs). **Keep `grappling_hook`** (later-ish; cross deep-water gaps).
- **Sprinklers:** small + large (Stardew-style) — farming automation.
- **Loupe:** keep as an accessory (confirmed).

### D13 — Mining processing chain (NEW — mining is a priority loop)
**Rock crusher** crushes rock + ore → **`paydirt`** *(working name — needs a final name)* → fed into a
**sluice** that separates out ore/gems. A real gather→process→refine loop. Mining is deliberately a slow,
exploratory ramp — getting a mining operation going takes time, which is fine (exploratory > rushed).

### D14 — Dredge (mechanic proposal, see backlog)
Direction: place a **dredge on water** → at its station press **"dredge"** → the player appears with a **hose
from the dredge** and **works the water with the hose like a tool**. Tiers (weaker→stronger) + condition
variants (e.g. a **swamp dredge** that works better in bog) — all function, some give bonuses. Mechanic →
**backlog** (get it right). (Consolidates the old `bed_dredge`/`silt_dredge`/`dredge_shovel`.)

### D15 — Materials: add cotton; fibers from plants
Add **cotton** as a cloth source alongside silk — but a **LATER farming crop, NOT in the village** (no
wheat/cotton in Zone 1, D19). Fiber comes from plants (grass/reeds/bushes/clover) — fold
the `reed_fiber` alias into plain `fiber`. **Sand:** small amounts in Wasp Thicket, more to the north; sand
can fill swamp water to reduce mosquito breeding area.

### D16 — Venom/poison ARE mechanics; equipment should alter a VARIETY
**Venom and poison are assumed real combat mechanics** — keep them on gear. The point was only that interesting
equipment (weapons/armour/accessories) should alter a *variety* of things, not over-index on venom — so spread
bonuses across knockback, attack-speed, etc. too. **What's backlogged is POTIONS & ALCHEMY** (the
potion-crafting system), not the venom/poison effect. **Don't over-prune** uncertain items now — drop the ones
we're unsure about in a later finalize pass; leaving a few is fine.

### D17 — Active build scope: Village + Mining Camp only
*Replaced 2026-09-26 (the approved roadmap): all twenty zones, ring by ring.*
Right now we are creating **just two zones**: the **Starting Village** (`zones/village.md`) and the **first
underground "Mining Camp"** = **Underground Passages** (3,1, `zones/underground_passages.md`, the Miner's
outpost hub). Everything else (the other 15 zone sheets + the full catalogs) stays as **catalog reference,
unpolished**, until we reach it. These two zones get finalized to a buildable spec; pull only what they need
from the catalogs.

### D18 — Bug drops = `dead_<bug>` only; the **Bug Extractor** processes them
*Refined 2026-07-07: ants give formic acid — through the bug extractor.*
Killing any bug drops **only `dead_<bug>`** (`dead_fly`, `dead_butterfly`, `dead_wasp`, `dead_centipede`,
`dead_ant`, …) — **no messy per-bug ground drops** (no `ladybug_shell`/`pill_chitin`/`formic_dab`/etc.).
A **Bug Extractor** — a clean in-town building/station with crates + equipment — **processes dead bugs into
materials** (chitin, silk, venom, leather, etc.) **and is used in cooking** (bug-based food). This solves "how
do bugs drop things neatly": they don't — you extract.
- **Supersedes** the per-bug specific drops across all zone sheets, AND the separate "bug-leather station"
  (D11) — leather is one extraction output.
- Ants **lay** eggs (a mechanic), they don't drop them. **No formic items.**
- → backlog: build the Bug Extractor station + the extraction recipes (which dead bug → which material).

### D19 — Zone 1 (Village) finalized roster — grounded in real `village_21_B` data
**Zone 1 = `village_21_B`** (the tuned **6-species** ecology with the millipede→50 charts), NOT the plain
`village_21` demo.
- **Species (actual spawns, 6):** `fly`, `butterfly` (on `milkweed`), `wasp`, `centipede`, **`millipede`**,
  **`carrion beetle`** (`beetle_carrion`). (No pill bugs / ants / snails / aphids — later/forested zones, so no
  `honeydew`/`formic_*`.) Each drops only `dead_<bug>` → the Bug Extractor (D18).
- **Flowers (actual):** `flower_red`/`flower_blue`/`flower_yellow`/`flower_wild`, `poppy`, `lavender` — use
  these; each drops its own flower ingredient (`flower` for the colored ones, `poppy`/`lavender` for the named
  herbs). **No `wildflower_petals`** (that was a bad invented material — cut below).
- **Crops:** a nice collection of **garden vegetables** — `tomato`, `corn`, carrot, cabbage, eggplant, pumpkin.
  **Wheat is PULLED from the village** — you **buy it up north** (fast-growing, good money — a travel gate);
  *zone-authoring TODO: remove `plant_wheat` from `village_21_B`*. **No cotton yet.** New crops debut in new zones.
- **Centipede + millipede both stay** in the start village (decided).
- **Cut village materials:** `wildflower_petals`, `river_pebble`, `pond_clay` (→ plain `clay`), `compost_rich`
  (→ plain compost, one type), `beeswax_dab` (→ the **west/bee zone**). `reeds` stay (already in zone).
- **Stations already placed in `village_21`:** workbench, furnace, anvil, cauldron, forge, sawmill
  (the **wood-saw / woodcutting** station — sprite exists), keg. **Add:** the **Bug Extractor** + a
  **compost bin** (basic → bigger = more capacity).
- **Fishing:** basic fishing is here (water + boats + poles in the zone) — see the Fisherman NPC (D20).
- **No roofs** (overhead view) — walls, fences, doors only. (Drop `thatch_roof`.)
- **Storage:** start with a **small sack** → upgrade to a **large basket** → a **backpack** (storage slot).
- **Net:** start with one in inventory; also sold.
- **Décor/furniture:** everything currently in the zone (it's richly decorated). **Most are buildable**;
  **fancy ones that need dyes/advanced mats are NOT buildable yet** (e.g. `bed_fancy`, `sofa_fancy`,
  `dresser_fancy`) — buy or unlock later.
- **Consumables:** keep `calm_spray`. **Cut** `rot_bait`, `sweet_bait`, `petal_tincture`, `bug_balm`,
  `village_soap` (no game reason). **Health potions wait** for the alchemy pass (backlog).
- **Food:** offer **`forager_stew`** only; the player cooks the rest. **Food recipes = a separate system →
  backlog.**
- **Sprinklers:** basic + advanced, **cost-gated** (you can't get the good ones until you've played a while).
- **No Forager's Kit** (the early bonus set lands in a later zone).

### D20 — Village NPC roster (5)
1. **Merchant** (General Store) — general goods, seeds, supplies, decorations, recipes, basic equipment (the
   net); **randomized/rotating inventory** with a few **rare/expensive teases** (a peek at how awesome
   out-of-reach gear gets, right from the start).
2. **Fisherman / boatperson** — sells **fishing poles** + a **boat** (expensive); the fishing NPC.
3. **Blacksmith** — sells **some metal**; the real **mining equipment is at the Mining Camp**, not here.
4. **Carpenter** — furniture / wood / building recipes.
5. **Mayor** — sells nothing except **land deeds** (a separate system → backlog).

*(Recall: all **basic recipes auto-unlock** at their station; the store sells convenience + the rare teases.)*

### D21 — Underground critters & sprites (cols 0–1)
- **No critter rehash of `village_21_B`** — the underground gets its own, tougher species.
- **Ants spawn in the col-0 Ant Colony and CROSS OVER** into the Mining Camp via the dirt tunnels (cross-zone
  foraging) — they are **not** spawned in the Mining Camp itself. **Scout ants** = top of the western ant zone
  (3,0, range far/forage out); **warrior ants** = lower-left (4,0). (Ant species still need building.)
- **Centipede/millipede sprite plan:**
  - **Garden centipede** (village) → **NEW sprite**.
  - **Cave centipede** (underground) → **reuses the current centipede sprite**.
  - **Cave millipede** → **NEW** — faster, stronger, more aggressive than the garden millipede.
  - **Deeper south (Centipede Caverns):** **venomous centipede + venomous millipede** + other tougher things.
- **Terrain ecology:** dirt zones (col 0 + the Mining Camp's dirt top) hold detritivores + ants; rock zones
  (Mining Camp rock, Centipede Cavern) hold centipede/spider hunters.
- **Confirmed critter roster (first build, lean):** Mining Camp (3,1) = **cave centipede** (reuse sprite) +
  **cave beetle** (new) + **glowworm** (new) + **ants crossing in** from col 0.
  - **Light:** **glowworms + glowing mushrooms (`mushroom_glow`)** are the light sources — in some areas the
    **only** light. **Catch a glowworm → a firefly-style lantern** (lightning-bug source).
  - **Spiders:** only a **few small, webbed spiders** (new sprite), and only in the **lower/harder underground**
    (Centipede Cavern + deeper) — *not* the first Mining Camp.
  - **Deferred (later):** cave woodlouse, cave cricket, grub, stag/rove beetle; the venomous deep
    centipede/millipede + a mini-boss.
  - **New sprites needed:** garden centipede, cave millipede, cave beetle, glowworm, small cave spider.
    (Reuse: current centipede → cave centipede; `beetle` → recolor where useful; `mushroom_glow` exists.)

---

### D22 — Recurring rules logged so they stop getting re-litigated (2026-06-26)
These were decided (some repeatedly) but kept getting dropped. Recorded here as the canonical reference:
- **No rocks / boulders / stalagmites — only `stone_block` + mineral blocks.** Decided 3×. Depth shows via the
  **floor tile + ore richness**, NOT harder block tiers (`hard_stone_block` was deleted). The lone `boulder`
  placeable + rock décor are flagged in [`catalogs/materials.md`](catalogs/materials.md)/[`decoration.md`](catalogs/decoration.md)
  for your keep/cut call — not auto-removed.
- **D18 is APPLIED in `species.json`** (2026-06-26): every species' `kill_drops` is now `[]`; a killed bug drops
  **only `dead_<species>`** (the carcass). The **Bug Extractor** (a normal station, still to build) turns dead
  bugs → materials (chitin/silk/venom/leather). `wasp_stinger`/`centipede_parts` removed as direct drops.
- **Plants/forage drop their own ingredient** (2026-06-26): flowers → `flower`; named herbs → themselves
  (`mint`/`sage`/`thyme`/`fennel`/`aloe`/`agave` got real `resource` items); berries → `berries`; generic
  greenery (grass/vines/debris) → `fiber`. See [`catalogs/plants.md`](catalogs/plants.md).
- **Placeables & blocks drop THEMSELVES** (Terraria-style): break a `well` → get `well`; mine `stone_block` →
  `stone_block`. Drops must be explicit in the entity def (no self-fallback in code).
- **Unified entity registry:** the server merges `items.json` ∪ `occupants.json` ∪ `placeables.json` into ONE
  `state.Entities` map. A valid carryable/drop/recipe id exists if it's in **any** of the three — never read one
  file and conclude an id is missing. (`crops.json`/`recipes.json` are separate config layers, not entities.)

---

### D23 — Breeding stations (host + brood): the canonical model (2026-06-27)
> **⚠ SUPERSEDED (2026-07) — the canonical model is now [`architecture_nursery_stations.md`](../architecture/architecture_nursery_stations.md).** A nursery is a **modified station**: the brood **IS** the station (not a separate host that "holds" it), and its egg/larva/pupa counts are collectable **output units** you take like any station transfer — **no random yield, nothing perishes on take**. The "portable host carries its brood" special case is **dropped** (breaking any nursery perishes the brood + spills the resident adults). The text below is kept for history; where it conflicts, the nursery spec wins.

A **breeding station = a HOST that holds a BROOD** (eggs/larvae developing). The brood is a living thing
separate from the host's material — larvae are **never loot/drops**.

**Universal brood rule — a brood needs a host to develop:**
- **Leave it** → larvae mature on the host → become adult bugs → **released into the world** (the default lifecycle).
- **Open it → take & move the larvae** → relocate the brood to another host/nursery (the breeding-management
  action, and the only way to keep them off a host you're about to remove).
- **Destroy a ROOTED host while it's occupied** → the larvae have no host → they **DIE**. No free bugs, no magic
  survival — destroying the habitat costs you the brood.
- **Move a PORTABLE host** → the brood travels with it and survives.

**Two host types:**
- **Portable structure** (e.g. `wasp_nest`): NOT a resource plant. "Chop" = **pick it up and move it** (brood
  goes with it). It does **NOT drop material** — no paper, no fiber, no larvae. Open → harvest/move the brood.
- **Rooted host plant** (e.g. `milkweed`): an ordinary plant. Chop = **fiber + seed** (plant material).
  Open → harvest/move the brood. Tearing it down while occupied **kills** the brood.

**Status: BUILDING (2026-07).** BUILT: the brood engine + universal pupa stage; the open-station **panel**
(wasp nest / milkweed); **take** (a stage's units → the bag, larva → the `wasp_larvae` material); and **teardown**
(breaking a nursery **perishes the brood** + spills the resident adults). The `wasp_nest`
`paper_nest`+`wasp_larvae` break-drop is **removed** (now Wasp-Thicket boss loot only). PENDING: place-back onto
a compatible nursery, the compost bin's deposit+brood unified into the one panel, the wild fly-brood object, and
compost residents. `milkweed` drop `milkweed` → `fiber` + a *chance* `milkweed_seed` (D24) stays as designed.

---

### D24 — Plant harvest & seed model: ONE rule for every plant (2026-06-27)
After a long search for something non-clunky, the model is a single uniform rule (easy to learn; like Stardew):

> **Harvest a plant → its resource (always) + its seed (a CHANCE, every now and then). Plant the seed to grow it back.**

- **The seed is OCCASIONAL, not every harvest** — a tunable drop chance. Guaranteed seeds every time would flood
  the world and break balance (cf. Stardew wheat → wheat always, seed/hay only sometimes). Start low, tune by feel.
- Same rule for everything — no per-plant categories, no "pick-up-and-place vs seed vs extractor" to remember:
  - flower → `dead_flower` (dye/craft) + *chance* `flower_seed`
  - bush → `fiber` + *chance* seed · tree → `wood` + *chance* sapling/seed · wheat → `wheat` + *chance* seed
  - milkweed → `fiber` + *chance* `milkweed_seed` (a big plant **and** a breeding station, grown from seed — see D23)
- **Harvest effort scales with plant size (`breakable.hp`):** small flora (flowers, grass, small bushes) come up
  in **one hit**; **large plants — milkweed, trees — take several hits** to fell (not instantly harvestable),
  like trees already do (`hp: 5`). Raise `hp` on the big ones.
- **Crops are not one-and-done:** many are **multi-harvest** (Stardew-style) — the plant **regrows and yields
  repeatedly** before it's spent, not consumed on the first harvest. This already exists in `crops.json`
  (`multi_harvest` / `max_harvests` / `regrow_ticks`, e.g. tomato); single-harvest crops are consumed.
- **Living vs cut flower (free gameplay):** a flower **standing** in the world feeds pollinators (nectar/AoE);
  **cutting** it gives `dead_flower` + a chance seed. Leave them for the bugs or cut them for dye — a real choice.
- **No extractors required** — seeds drop directly. A **Seed Maker** is an OPTIONAL convenience (produce → extra
  seeds), never a gate. Seeds are also **buyable** (NPC) for reliability and the first batch of a crop.
- Supersedes the explored-and-dropped alternatives: per-resource extractors (clunky), Apico-style pick-up-and-place
  flowers + transplanting (charming but created edge cases), and "every plant always drops a seed" (imbalanced).

**Status: DESIGN ONLY — not built.** Implementation later: most flora gain a chance-based seed drop; the flower
resource becomes `dead_flower`; large plants get higher `hp`; seed items get created (only crop `seed_*` exist
today). It will be judged in play — the seed-drop chance is the main balance knob.

---

### D25 — Commerce spine v1 BUILT (2026-06-27)
The buy/sell/NPC/currency foundation is implemented and unit-tested. As built:
- **Currency live:** `PlayerState.Coins` is now mutated (earn on sell, spend on buy), persisted via
  `CharacterSave`, synced to the HUD via the existing `sendInventorySync` echo. Players start at **0 coins** —
  selling a caught bug is the first coin source (D24/onboarding).
- **NPC = a `shop` occupant** (`occupants.json`, `interaction_type:"shop"`, `world.shop{kind,sells,buys}`),
  resolved at its anchor cell. Server `handlers_shop.go` on **`OpCodeAction(2)`** (no new opcode); client
  `ShopController` (OnGUI), routed via `PlayerInputRouter`. Stock is unlimited → no shared state, no races.
- **Two vendors in the village:** **General Store** (`general_store_merchant`, kind items — sells seeds/tools,
  buys material/food-tagged crops & forage) and **Bug Dealer** (`bug_dealer`, kind bugs — buys live bugs at
  `species.sell_price` (1–25) + dead-bug items; sells a couple back at a markup). Placed at the storefront.
- **Anti-exploit:** a load-time invariant rejects any shop selling a good cheaper than it buys it back
  (`validateShopArbitrage`); fixed the `small_net` 0-buy/25-sell data bug.
- **Server logic unit-tested** (`shop_test.go`, 11 cases). Deferred (still design): recipe-selling, the other
  village NPCs, the Mining-Outpost, NPC dialogue/wandering, rotating/exotic stock, the bug-market building+scene,
  and **distinct NPC art** (v1 reuses the player-model `merchant`/`scholar` sprites as placeholders).

### D26 — Village economy buildout: full vendor roster + recipe system (2026-06-27)
*Replaced in part 2026-06-28: ore is crushed, washed, then smelted — not straight from the sluice to a bar.*
Andrew's calls from the `zones/_village_vendors.prune.md` review. **These are decided — do not re-litigate.**

**Recipe acquisition rule (the one that keeps getting inverted):** **basic recipes AUTO-unlock at their
station — ALL metal tool/weapon/armor tiers included.** Tools are NEVER gated. The **bought/found** layer is
**décor / furniture / advanced / "rare teases"** (crafting.md §7). Recipe gating uses the recipe `unlock`
seam (`default` vs `shop:<npc>`/`find`).

**Recipe collections / "recipe books" (NEW mechanism):** recipes carry an optional `collection`; a vendor
sells a **book ENTRY** (e.g. "Basic Furniture Vol. I") that grants **every recipe in that collection** into
`KnownRecipes` at once (collection-grant, NOT a physical item). Individual recipes still sell one-off.
Collections: `basic_furniture`, `advanced_furniture`, + stone/woven/etc. as lists settle.

**Vendor roster (village) — buildings mayor/market/smith/carpenter/ecologist already placed:**
- **General Store / Merchant** — wood tools, seeds, calm_spray (costs a bit), torch + lantern (buy; lantern
  pricier), **candle recipe**, **fence (finished good)**, **magnifying_glass** (new starter tool),
  **gardener_gloves** (decent price; harvest-bonus mechanic → backlog), some decorations + recipes/teases
  (specific lists in `_village_assignments.md`), **rotating random higher-level items**. **NO metal
  tools/weapons** (those are the Blacksmith's).
- **Blacksmith** — iron+copper **bars**, iron/copper tools, **weapons beyond wood**, armor, **wood stove**
  (`stove_wood` — it's metal), **candelabra recipe** (iron). **Buys metal BARS, not ore.** Remove
  bee_charm/lucky_clover. **Accessories → BACKLOG** (revisit list; assign each to vendor/found/recipe).
- **Carpenter** — **basic_furniture recipe book** (chair_wood, table_wood, stool_wood, bench, log_seat,
  bookshelf, dresser, desk, cabinet, cupboard, wardrobe, nightstand, side_table, coffee_table, bed_basic,
  rocking_chair, + the rest of basic). Individual: **keg** (basic; also sell kegs), grandfather_clock,
  bed_canopy. **advanced_furniture set** (loveseat/sofa/sofa_modern/armchair/chaise_lounge/ottoman/
  chair_cushioned/kitchen_island/map_table_big; sell the loveseat finished). **wall_wood** (default-unlock,
  wood station) + **fence recipe**. (Name collections better.)
- **Ecologist** (building exists; he had been overlooked) — has recipes for his house items: telescope,
  specimen_shelf, bug_terrarium(_big), specimen_case.
- **Mayor** — land deeds → DEFERRED. Add a **chest in his house** holding the **throne recipe** (found-only).
- **Fisherman** (NEW NPC) — poles + boat (**fishing mechanic deferred**), **reed_hat recipe** (workbench).
  straw_hat → a later zone.
- **Weaver** (NEW NPC + NEW shop scene) — woven goods (rugs/cloth/laundry_line) + **dyes** (dye station;
  basic colors default-unlocked; special colors = recipes spread across zones).
- **Stonemason** (NEW NPC + NEW building scene) — stone things: birdbath, fountain, statues, stone furniture,
  brick/stone walls & paths.
- **Modern Wares** (NEW NPC + NEW building scene; glass blocks/modern floors/shelves) — fridge, range_stove,
  floor lamps (need **electricity → backlog**), modern furniture.

**Mining mental model (corrected):** ore → `rock_crusher` → `paydirt` → `ore_sluice` → **bars**. So **raw ore
sells at the mining areas (Miner's Outpost); the village Blacksmith buys BARS.**

**Placeable taxonomy (adopted):** `category` = what it IS (art/org); behaviour = `interaction_type` +
blocks (`container`/`shop`/recipes). **"decoration" = placeable with NO behaviour.** Reclassify: buckets/
ore-bins/terraria → **containers**; fishing rod/net → **tools** (placeable form); `lily_pad` → **flora**;
campfire → **cook-station**; `cow_skull`/`tumbleweed` → **find-only**; `dead_bush` → **cut**. (Container &
tool conversions that need the fill-display / fishing mechanic ride with those backlog items.)

**Sneak-peek / find principles:** anything already placed in a zone **stays** (players glimpse décor whose
recipe lives elsewhere); part of furniture/décor is **find-only** (ties to **player plots / décor-on-farm →
backlog**, in the design).

**Build philosophy:** recipe creation is **mine to author, Andrew reviews** (too tedious by hand). The metal
bar ladder and base mats (plank/cloth/glass/leather via Bug Extractor) **just get built** — not a blocker.
Electronics = buy-only (no player recipe).

**Backlog (so nothing is lost):** fill-state placeable containers (ore bins/buckets/carts) · player plots /
décor-on-farm · finish lighting · electricity · fishing mechanic · land deeds · water-tile placement (one
`dock_plank` for docks+bridges) · gardener-glove bonus · accessories revisit+assign · fancy furniture → a
later zone (track bed_fancy/sofa_fancy/dresser_fancy/…) · wine_rack + bigger kegs → bee zone · garden_arch
recipe → another town · special dye colors across zones · straw_hat later · tumbleweed (drier zones) · the
stat `bonuses{}` engine.

### D27 — Covered containers + the Weaver/Stonemason/Modern build-out (2026-06-27)
The **container visual conundrum** (open baskets/piles look bad empty; we don't want a sprite-per-content or
an empty/full state-swap) is resolved by **COVERED containers**: a `basket` gets a **lid**, a `produce_crate`
gets a **tarp** — closed always reads fine, so **no client rendering work, no fill mechanic**. Functionality
lives in the data (`world.container` + `filter`). Locked:
- **Baskets** = standard **unfiltered** containers (we place cloth in them by hand in the Weaver). No multi-tag
  filter. **Crates** = `filter:food`, **1 slot** (bulk fruit/veg). `cloth_pile` **removed** (a "pile" implies
  put-anything, which fights the container model).
- **Mannequins** = hand-authored Pipeline-B white "blob-form" (faces hidden): `mannequin_white/_cream` +
  `mannequin_dress_red/_teal`. Replace `dress_form` in the Weaver display.
- **NEW rug family** (gpt-image-1): `rug_sm_sq/_sm_rect/_md_sq/_md_rect/_lg_rect/_runner` — square+rectangular,
  2×2→3×5, distinct colors/styles; convention is `footprint:[W,H]` + `sprite:[W·16,H·16]` (flat, pivot `c`).
- **`clothing_rack`** (2-wide garment rail) is a **display fixture only** — gated to "the other town" (see
  BACKLOG, with the windmill). `coat_rack` stays the house piece.
- The **three new shop scenes** are built: Weaver (`scene_weaver`), Stonemason (`scene_stonemason`, workshop +
  sculpture yard), Modern Wares (`scene_modern_wares`, marble showroom, glass-block windows). New entities:
  `chisel_bench, brick_pile, statue_unfinished, sign_mason, metal_shelf, electric_heater, glass_block`.
- gen_sprites had **no `glass` palette** (glass defaulted to wood/brown) → added a cool-blue glass palette to
  `style.json`.

### D28 — UI polish run: panels onto the Canvas/UIFactory system + signs/mannequins (2026-06-28)
The in-game UI is consolidated onto the ONE polished Canvas/UIFactory stack (the OnGUI ShopController is
removed — a debt reduction), in an Apico-style theme (rounded warm panels, **item-icon SQUARES** with
counts, gold selection ring, coin pill, per-purpose accent colours). PIL mockups (`tools/ui_mock.py`) are
the design surface we iterate on (the Unity C# can't compile here).
- **Stations** (`CraftingPanel`): inputs are now item SQUARES (icon + have/need, red when short) → an arrow
  → the output preview; the progress bar shows **time remaining** (matters for furnace/forge 15–26s).
- **Shop** (`ShopPanel`, Canvas, replaces OnGUI): dialogue (portrait + greeting + Trade/Goodbye) → trade
  board (Buy / Learn / Books / Sell as squares; known recipes greyed). Buys reuse the existing
  ShopActionMessage; refresh via `OnInventoryChanged`. No server change.
- **Signs** (`SignController`): store signs → 2-wide; the directional `signpost` → a thin 2-tall
  **crossroads** post; ALL signs `blocks_bugs:false` (bugs pass through — Andrew). Per-placement TEXT via
  `PlacedOccupant.Text` (authored, raw-JSON auto-flow; read-only). Right-click reads the carved board.
- **Mannequins** (`MannequinController`): `blocks_bugs:true` (solid — carried by the EXISTING generic
  frontier collision system; no new determinism code; re-run the cross-client gate). A clothing-filtered
  container + an equip-slot panel reusing the container move/sync protocol. The worn-outfit paper-doll
  render is the documented follow-up (BACKLOG).

**Determinism note:** the ONLY frontier-relevant change is occupant `blocks_bugs` — generic over the flag
(`state.go:702 BlocksBugsCells` static map + `handlers_world.go:674/538` dynamic `OCCUPANT_BLOCKS_BUGS`
ledger). Everything else (UI, dialogue, sign text, outfit storage) is pure display off the hash.

### D29 — Barter sell: staged basket + atomic `sell_batch` (2026-07-02, playtest #5 fix)
Selling is no longer a per-click loop on a cloned read-only list — it's the **Apico barter model** on the
player's REAL inventory (the design recorded in `crafting_buildout.md` "Barter sell UI" + BACKLOG):
- **Client:** the shop opens the InventoryPanel with it; right-/double-click (or drag via the cursor) stages
  a stack into the ShopPanel **basket**; one "**Sell for Xc**" sells everything. Staging is a **render
  OVERLAY** (`ShopPanel.StagedQty`/`ForRender`, consulted by the 4 inventory-backed render sites in
  InventoryPanel + HotbarUI) — inventory DATA is never mutated, so the FullInventorySync repaint (a buy
  mid-shop) cannot resurrect staged slots. A "**Buys: …**" header + client filter mirror `shopBuysItem`
  (ids OR tags; bug dealer = live bugs + `dead_*`); refusals/skips/payout land in a shop **status line**
  that also finally surfaces **OpCode-40 server errors** (previously defined but consumed by NOTHING —
  the root cause of playtest #5, where clicking appeared to do nothing).
- **Server:** `op:"sell_batch"` with `lines[]` on the same `ShopActionMessage` (OpCode 2, additive).
  `sellLine` is the extracted single source of sell validation (`shopSell` wraps it); the batch validates +
  removes per line sequentially (duplicate-slot lines re-validate the live count), sums, **credits once**,
  aggregates skips into one error, echoes one FullInventorySync. **Per-line `qty<=0` is rejected** — the
  handler's top-level clamp doesn't see lines, and a negative qty passes `RemoveItem`'s `Count < count`
  guard and would GROW the stack (a real duplication exploit, caught in plan review; regression-tested).
- **Scope decisions:** the four no-buy vendors (stonemason/modern_wares/fisherman/ecologist) stay buy-nothing
  (one-sided vendors are deliberate, merchants.md); "barter" = the staging-UI metaphor ONLY — the currency
  model is unchanged (one coin type, no item-for-item). *(Replaced 2026-09-27 by D52: goods can be traded for goods,
  as in Baldur's Gate.)* Bug-release is consumed (not fired) while a shop is
  open so a missed basket drag can't free the bugs being sold.
- **Gates:** 4 falsifiable Go tests (mixed batch / duplicate-slot / negative-qty exploit / bug-dealer batch)
  + suite green; Unity batchmode compile clean (fresh DLL symbol-verified); in-Editor visual pass pending.

### D30 — Per-station craft-slots (Procs lanes) + the crafting sprite pass (2026-07-03)
The last crafting-buildout mechanic (buildout §6, user-approved) + the user-scoped art pass (missing sprites +
placeholders):
- **Mechanic:** `CraftStationState` = a SHARED output grid + `Procs []CraftProcessor` lanes
  (`{Recipe,Queue,Progress}` each); lane count = `world.craft_slots` (default 1). Slots reward SLOW
  processors: furnace/forge/sawmill/ore_sluice/dye_vat/bug_extractor = 2; manual benches 1. Ops carry a
  `proc` index (`craft`/`set_recipe`; collect is station-level); the echo carries `procs[]`. A full output
  stalls ONLY its lane. **Legacy saves migrate** via `UnmarshalJSON` (flat fields → `Procs[0]`) — both
  shapes load forever. Client: one CraftingPanel row per lane; DoCraft targets same-recipe → idle → refuses.
- **Finding recorded:** campfire/stove/cooking_pot/cauldron/keg have ZERO recipes → not craft stations at
  all (recognition = RecipesByStation membership, NOT interaction_type). The "campfire 1 < stoves more"
  flavor stays inert until cooking recipes (D16/D19 backlog) ship.
- **Sprites:** 15 truly-missing generated (incl. the only 2 blank crafting outputs laundry_line +
  specimen_case; plum/cherry/rotten fruit icons with new catalog rows; a real backpack icon — its
  `icon_from:"ore_sack"` borrow REMOVED because fallback step 1 shadows dedicated icons). ~82 placeholder
  regens: metal intermediates, gems raw+cut, weapon tiers (regened WITH explicit per-metal look rows after
  the first pass lost the metal), saw/sickle, rock_crusher/gem_cutter, gem ore blocks, and the 30 tool-tier
  icons (per-metal catalog rows derived from the `_wood` bases — replacing palette-tint recolors).
- **Gates:** 5 falsifiable Go tests + suite green; previews rebuilt; in-Editor parallel-smelt + art eyeball
  pending; live-save migration check deferred (a player was CONNECTED — never swap the plugin mid-session).

### D31 — The beekeeping milestone: persistence + calming as FOUNDATIONS, then bees (2026-07-05)
The full milestone (plan: harmonic-weaving-dolphin) shipped in phases A0→E, each gated. Economy/design
decisions of record:
- **Persistence is a first-class system, not a bee feature** (owner directive: the entire game
  persists, as in Terraria). ONE WorldSave document per zone; the CLOCK persists; full-fidelity swarms;
  a reflection-enforced classification table so "forgot to persist X" fails a test BY NAME. Old
  multi-record saves import once, then delete. See architecture_persistence.md.
- **Calming is GENERAL** (owner correction: most bugs can be calmed): the dead
  condition stub (`condition_tools`/`ConditionValue`) is now the live §C system — one threshold (40)
  for behavior AND catching; every species carries an explicit `condition_tools.calm` fill (bee 95,
  centipede 90, wasp 85, harmless 80; no key = immune). calm_spray finally works; smoker + consumables
  share the ToolUse verb (no new OpCode). See architecture_beekeeping.md.
- **Honeycomb is the allocation currency:** recipes are single-output, so the extractor offers
  honeycomb→honey ×2 OR honeycomb→beeswax ×1 — the player allocates each comb (a deliberate economy
  choice, not a schema workaround to fix later).
- **Candle RE-THEMED:** beeswax ×1 + fiber ×1 @ workbench (was fiber ×2 — pre-bee placeholder).
- **Smoker id is `smoker`** (display "Bee Smoker") — reconciling the catalog's `bee_smoker` naming;
  craft iron_bar + wood ×2 + wasp_stinger @ workbench; tiers later via `effect_power` (data only).
- **Placed hive boxes are DORMANT** (no free bees — colonies must claim them); bees are nest-founded
  ONLY and the Director may never reseed them (min_population 0) — colony survival is real, unmasked.
- **Defaults taken on the unanswered playtest questions** (60s timeout; frogs explicitly REJECTED,
  crab cut): critters = fireflies (+ dragonflies as the wasp counterweight), bee suit = ONE body piece
  with full sting immunity (suit stops stings, NOT bites, and never the anger), hive harvest = hand
  right-click, no panel.
- **Maren the Beekeeper** (bee_meadow_20) is the bee-economy anchor: sells beehive_basic 60 / smoker
  120 / bee_suit 250 / calm_spray 20; buys honey / honeycomb / beeswax by id.
- **Gates:** every phase committed on green — Go suite (24 new tests across §P/§C/bees), the persist
  harness + a seeded legacy-migration run, sim-determinism, FRESH 2-client latejoin BOTH halves SYNC
  IDENTICAL, the bug_lab bee-arena chart gate (self-maintained colony, b_reseed 0, honey at cap — after
  fixing a REAL phase-handoff sim bug run 1 exposed), zone lint 0 + text-verified edge contracts +
  headless crosszone BOTH directions. In-Editor feel pass = Andrew's.

---

## Resolved (2026-09-27) — the owner's review of the game overview, parts 0–3
Restated in my words; the overview (`docs/gdd/overview.md`) carries the detail and the proposals built on these.

### D32 — What survives: bugs, fish and people
Birds, amphibians and reptiles died out along with the mammals; only bugs, fish and people survive. The mammal
things that slipped into the idea lists (cave bats and bat guano, milk and cheese, horseshoes, livestock and manure,
a rabbit's-foot charm, a pack mule) are dropped, and so is the December 2025 idea of a meteor-borne infection.
The prototype's own items that don't fit the premise — a cow skull, a cat statue, a hay bale, a birdbath, bones and
bone piles — can be removed too; the prototype isn't finished. *(Added 2026-09-28: the same review answered this, but
it was left out of this entry at first.)*

### D33 — The prototype is not the design
Nothing in the game is finished. Every value in the data — prices, timings, counts, capacities — is a placeholder
until it is designed and tuned, and every bug, including the ones already worked on, needs more passes for
behaviour, combat and ecology. Documents must not present prototype numbers as decisions.

### D34 — Catching: hand nets by size, placed catchers, the autonet
A small and a large hand net, each good only up to a certain size of bug; larger bugs are taken by catchers placed
on the ground. Early placed nets that bugs fly into hold only a few; the autonet draws in bugs from the area just
ahead of it and holds more; both take bugs out of the world. How they work is proposed in the overview (P3, P4).

### D35 — Calming is set species by species
One calming system, but what calms a species — and whether anything does — is set per species: many bugs can't be
calmed, and what calms one (smoke calms bees) may irritate another. This replaces "most bugs can be calmed" in D31.

### D36 — Pens hold every bug; fences are overhauled
No bug flies over a fence or wall (the 2026-06-18 correction for wasps, now for all bugs). Each species has up to
three tiers, stronger and often bigger, and a fence material holds only the bugs it is strong enough for; some bugs
can't damage some fence types at all. Stone is not a general answer. Fencing is rebuilt as posts that connect, as in
other games, instead of one repeated fence block.

### D37 — Compost, bug prices, and getting hold of things
Compost is sold and is also a fertiliser source. Carrion beetles do not make compost (a prototype rule that goes).
A live bug and a dead one are worth the same; processing a carcass may pay more or less; coins also come from other
things. Anything the game has but can't be obtained — the bug extractor, the large net and the rest — gets a way to
obtain it at the right point in the game.

### D38 — Butterflies grow up out in the world
The nursery holds the eggs and the young caterpillars; caterpillars go out into the world, grow, form a chrysalis
and emerge as butterflies. This settles the 2026-07-16 disagreement between the backlog (every stage on the
milkweed) and the nursery design (the caterpillar wanders off).

### D39 — Species: real ones, tiers per species, two kinds of ant
Real species with real behaviour — the game teaches a little ecology and biology — so invented names are replaced.
Tiers belong to a species, not a rule: some have one form, some two, none more than three (aphids have one). Two ant
species only, black ants and fire ants, in different zones; the other ant species in the zone designs go.
Mini-bosses are set off by conditions or simply placed. Real centipedes hunt alone; the game groups them only to
keep network traffic down, so they should spread out.

### D40 — The Ecologist, the Ecology tab and research
The Ecologist lives in a house east of the village. The Ecology tab's button stays greyed out until the player meets
him; his first quest asks the player to set up a bug monitoring station, which turns on that zone's information. His quests —
rebalancing, placing stations and more — are the tab's tasks: one system. Rewards are money, and sometimes gear or
recipes for big tasks such as taming a new area. The magnifying glass works like research in Apico: looking at
enough of a species unlocks facts about it (what helps it breed, what it dislikes, what it eats…), shown on the bug's
information page rather than in the tab. The ecology is balanced with many levers, not only food, predators and age;
fallen fruit is too plentiful, so it comes down and another lever goes up when the ecology is retuned. No
seasons.

### D41 — Village property
Players can't damage or take the townspeople's things; trying shows a short message. Bugs can damage village
fences, and the villagers repair them. Whether NPC workers exist more widely is left to the assistant's judgment
(the overview's P6).

## Resolved (2026-09-27) — the owner's review of the game overview, parts 4–9

### D42 — Farming: wheat from the Locust Farmland; harvest or cut down; fertiliser means yield
Wheat seeds are bought in the Locust Farmland or harvested from its fields; that zone has a small village with shops
and people of its own, which needs more townspeople. The one harvest rule stands (D24), and plants can also be cut
down and their parts processed at stations — simply, one step per station: it is a game, not a simulation of
real processing (no soaking or threshing steps). Fertiliser increases yield.

### D43 — Mining and the underground
Each underground zone is made of what fits it: the ant zones are dirt (ants don't dig through rock), the mining zones
rock. The underground's darkness belongs in every real underground zone, not a test zone. There is a limit on how much
a player can carry back from a trip. No mining dangers (no gas, no cave-ins). Prospecting uses a pan.

### D44 — Where stations come from; owned things; dyes
A station is found abandoned in the world, bought from someone, or crafted from a recipe — all still to be finished,
along with the missing stations and everything else in crafting that doesn't work yet. Stations that belong to someone
(as in a mining camp) can't be taken, and trying gives a short refusal. Dyes recolour cloth outfits through a
recolouring method built for it.

### D45 — Building and homes
*2026-09-29 (D69): diagonal ground is being reconsidered — the assistant designs how laying ground works, diagonals included; whole squares stand until then.*
Players build houses (walls, floors, doors), and can live in the village by building their own house there; they may
sleep only in abandoned beds, never in one that belongs to someone. Doors turn to fit the wall they are placed in,
which needs a second, side-facing door sprite. Ground is laid in whole grid squares — the diagonal shapes go. The
shovel both digs and lays ground, with a clearly shown switch between the two; how it switches is the assistant's
call.
Furniture doesn't rotate. Tents are three squares wide. Mannequins are overhauled to show whole outfits on a plain
white-faced figure. Decorative outfits are not on hold; they simply haven't been made yet.

### D46 — Combat
Danger rises outward from the village, not by compass direction. Swarms attack all at once, in sync, as they used to —
this replaces the "at most two attackers" pool recorded on 2026-07-11. Only lunging species wind up before striking
(millipedes, perhaps scorpions), decided bug by bug. Axe swings are attacks as well as tree-cutting. Players fight to
sell carcasses or to catch bugs to farm; large bugs, once subdued and still, are dragged. Dying costs little, mostly
the walk back. Stamina is allowed (replacing the January 2026 "no stamina"). Bosses are fully grown adults, harder and
usually bigger, never added at random, perhaps one at a time; only species where a fight is fun get one (no aphid
boss). *(Corrected 2026-09-28: this entry first said a locust swarm is a boss — a misreading; locusts get no boss and
their swarms aren't bosses, D63.)* Aphids live on plants and are seen in the plant's own view, like the milkweed nursery.
Enemies are built zone by zone, every one eventually, with test zones where the real zone isn't built yet.

### D47 — Gear
One outfit is worn at a time, whole, and changed any time from the inventory — no pieces. Non-combat outfits raise a
yield or make a job easier, and their description says how. Player characters come in several skin colours (the same
base, recoloured). The wizard's robe is dropped; an alchemist's robe comes with a potion station. Accessories need new
ideas. The tiers are still to be resolved.

### D48 — Nothing is locked
"LOCKED" in the December 2025 requirements only meant "don't change this without asking the owner"; nothing in older
documents is binding. Only dated decisions of the owner's are decisions.

## Resolved (2026-09-27) — the owner's review of the game overview, parts 10–14

### D49 — Tools and light
Light comes from several sources: bug lanterns (firefly and glowworm), torches, a headlamp and electric lights; oil
lamps stay out (D12). Tools never wear out — the game avoids that kind of upkeep — so the unused durability value goes.
No diamond or gold tools: neither makes sense as a tool. The tool motions are worked out; the pickaxe swings like the
axe.

### D50 — Food, potions and healing
No hunger. Meals heal and give boosts; which meal does what is settled with the recipe list. Potions heal and boost
too, but differently — stronger healing, and effects where food doesn't make sense; a better potion system is welcome
(the overview's P16). To heal someone else, a player equips a bandage or a potion and uses it on them. Items can be
given to other players, as in Terraria or Stardew Valley, in whatever way the assistant designs (P17).

### D51 — Fishing and water
Fishing starts in the starting village, at its lake and the fisherman's house — replacing D5 (fishing left out of the
first release) and the roadmap's "fishing with the Underground River". Water divides the map: natural barriers keep
areas from mixing too much, without having to follow zone borders exactly. There is no waders item: a wading outfit
lets its wearer wade slowly through shallow water (replacing D10's waders); deep water always takes a boat. There are no separate
sea zones: the coastline comes into the western and eastern zones, with at least one inlet, and off the west coast at
least one island shaped like a bug, with little inlets making its legs.

### D52 — Towns, trade and quests
Coins come from many sources, designed by the assistant. Bartering is allowed, as in Baldur's Gate: goods can be
offered instead of coins to a townsperson who accepts that kind of goods (replacing D6's "not barter"). The
western-style town has strings of lights and other electric things. The starting village is mostly unpowered: its
windmill (a kind of turbine) lights only part of it, such as the Mayor's house, as a glimpse of what power will bring,
and players can't take it — this refines the 2026-06-27 ruling, which had the windmill powering the village's houses.
Several townspeople give quests, not only the Ecologist — not designed yet; the myrmecologist has quests and a board
of retrieval jobs, some out of reach at first. No bounties. Townspeople keep their town — mending fences, gathering
fruit, dealing with bugs, and whatever else is good for the game — and sleep in their houses at night.

### D53 — The world
Bugs cross from zone to zone but spawn only in their species' own spawn areas. Every zone built so far will be
redesigned: zones can be designed much better now, and some houses don't meet the roads properly. The underground
fortress with the Queens' set is one example of a secret, not the only one. The prototype has four zones; the old
version of the village doesn't count. Where documents disagree, the owner and the assistant settle it together.

### D54 — Food, potions, giving, townspeople and trading: the overview's P16–P19 accepted (2026-09-27)
The owner accepted P16–P19 with two changes. A night-sight potion stays in the starting set — it is worth doing
properly, and simple to build. At night players simply walk into a townsperson's house and trade there, with no
knocking: simple play matters more than realism. So: a meal heals over a while and gives one fullness boost at a time; a healing
potion heals at once, then the person healed waits a short while before another works on them; other potions
(antivenom, a salve for sprays and acid, venom resistance, night sight) have no wait; stronger bugs make stronger
potions; the cauldron is the potion station; food doesn't spoil in bags or chests. Right-click a player to offer an
item, bugs or coins; left-click a bandage or potion on a friend to heal them at once; a new action drops things on the
ground. Shopkeepers keep their counters by day and chores fall early and late or to townspeople without a shop. One
trade screen: goods count at what that townsperson pays, and coins make up the difference either way. The art
approach is decided, so proposals don't offer cheaper art routes in its place.

## Resolved (2026-09-28) — the owner's review of the game overview, parts 15–20

### D55 — Progression, stations and the item pass
An open world with no ending, as in Terraria: no game over and no finale; the legendary sets are powerful and come
from the hardest zones, and some quest lines lead there to fight bosses, but players play however they like. The
basic stations — the anvil, the forge and the rest — stand in the village at the blacksmith's and the other shops;
players use them once they have the materials and can't take them, since they belong to the townspeople. Other
stations turn up in other places, mostly the first few zones, and powered versions come once the player reaches
where generators can be bought or built. The metal ladder is the assistant's to recommend, and the claim that each
new tool roughly halves the effort has to be justified against Terraria and other games. Every item in the game gets
a thorough pass for taste — the old lists, the accessories above all, will probably lose a lot — delivered as a
table of recommended additions, changes and cuts; this ends D4's "tuning never deletes content".

### D56 — Power and automation
No hired workers anywhere: automation comes from stations and tools as the player reaches them, and the early ones
are more manual. Small sprinklers are sold in the village but cost enough that the player saves up; larger ones come
from other places, such as the western town; the rest of the automation design is the assistant's. Modern Wares
sells powered things before the player can power them — a player can set up just outside the Mayor's house and run
them on his power. The Mayor's house has powered things a player may use, such as a fridge; everyone else in the
village lives by torches and bug lanterns.

### D57 — Time, weather and tuning
One clock for the whole world — no zone shows a different time of day. No skipping the night: sleeping doesn't move
time on, and the world stops only when no player is online. Empty zones stay frozen (2026-09-26), but random border
events still bring a few bugs from a frozen zone into a neighbouring zone that has players. Droughts and rain are
part of the game and need tuning. Balance must not lean on the weather: the prototype's balancing system, which
called a drought or extra rain whenever a species ran too high or too low, kept firing and made for poor play;
balance comes from many levers, and if it leans on weather too much the other levers are rethought. Retuning is part
of the bug overhaul, after bug behaviour has been polished and updated, and everything is retuned since fallen fruit
is being cut.

### D58 — Playing together
Everything in the shared world runs the same for every player; nothing goes faster for one player than another. No
limit on characters per account. Player-versus-player is allowed only when a server switches it on; the game is about
players against the world. Private plots are invite-only, follow the January 2026 plot design (decoration bonuses with
diminishing returns and a cap) and need a panel for their happiness level
and bonuses. What still runs on the server gets a thorough review: the game moved from the server running everything
to every player's computer running the same simulation in step, so each remaining server-side piece has to justify
its place — one of the most fragile parts of the game.

### D59 — Interface, tutorials and controls
Every system, the interface included, gets a polishing pass with the assistant's suggestions from taste and good game
design. Tutorials are the assistant's to design: some come from townspeople as the first quests, some unlock on
joining, some when the player reaches a new area, and many end with a task that leads into the next, often back at a
townsperson who sends the player on to another. Controls and settings are the assistant's to design.

### D60 — Art and sound
Most art is made with gpt-image-2. The interface and the blocks are drawn by the assistant in code, improved over
several rounds with the owner, since gpt-image-2 draws blocks poorly; characters stay with gpt-image-2 — this narrows
the 2026-09-26 rejection of code-drawn art to characters. Townspeople are drawn by gpt-image-2, each with walking
frames, floating hands like the player's and a matching face portrait for conversations; their looks are left to
gpt-image-2, and they are people of many ethnicities. The look gets a polishing pass: lighting (it falls short of
Necesse; Unity's screen effects may help), clearer signs of hitting and being hit, and wind sway done well and only on
plants — solid things such as standing stones sway today. The assistant makes the sound library and the music by
whatever method works best, without paid services; the owner has music packs, and each zone can have its own music.

### D61 — The overview's P20–P26 answered (2026-09-28)
*Renamed 2026-09-29 (D69): the top rung is tungsten steel, not tungsten carbide, and the top pickaxe has no gold-coloured finish.*
P20 accepted with eight rungs and without manganese steel — the assistant put cobalt steel on that rung instead: wood,
stone, copper, bronze, iron, steel, cobalt steel, tungsten carbide; no gold, silver or platinum tools. Armour follows
the tool metals, and platinum goes into fancy armour that also needs steel, sells well as money, and appears in
recipes where it fits. P21 accepted, with powered tools counted among the tiers. P23 (lessons), P24 (controls and
settings), P25 (border events) and P26 (the plot's happiness panel) accepted. Crops need one watering a day. For
sprinklers the owner suggested a hand pump — a well of sorts — followed by a powered pump, and asked for the
assistant's view — P22 revised with it; sprinklers water whatever is in reach, fruit trees included.

### D62 — Players may tip the ecosystem
Changing the ecosystem, balancing or unbalancing it, is the point of the game: a player who sets sprinklers on an
orchard and gets a fly explosion is free to, up to the cap. Fewer fruit on the ground (D40) was asked for because
hundreds of fruit lying around look ugly, not to control the bugs; the flies are retuned to live on the smaller
supply, which is the natural fix. Crops feed bugs too — locusts eat wheat.

### D63 — The overview's P3–P15 and P22 answered (2026-09-28)
All accepted, with these changes. Catching (P3): subduing a big bug and dragging it is one of the ways to take it, and
a larger cast net is welcome if it helps with big bugs (the assistant recommends one that tangles a bug so it can be
dragged). Traps (P4): a net placed in the world counts as a trap. Village property (P6): it stops annoying players
griefing. Research (P8): it can be as simple as examining a species a set number of times to open the next fact;
plants do more than steer bugs — some boost breeding, as in Apico. Tuning (P10): the hard caps stay, because a player
who dumps huge amounts of fruit could otherwise breed enough flies to crash players' games; a species that dies out is
reseeded; weather is one lever among many and a last resort — a drought means less pollen and slower plants, while
rain makes both flourish and does the watering — not the main way to keep numbers in their bands, as it was when it
rained all the time; behaviour is polished first, since a better-hunting wasp moves the bands; before retuning, the
assistant learns exactly how the existing tuning and polish work, then suggests what's new. The shovel (P12): the
interface keeps the dig/lay option visible, not only a first-time notice. Bosses (P13): locusts get no boss, and their
swarms aren't bosses either — a locust swarm eats wheat and other plants locusts eat; bosses are placed or grow out of
conditions, and not every species needs one. Stamina (P14): running drains it too. Pumps (P22): they work like power —
placing one shows its reach; working a hand pump's lever sets off every sprinkler within reach; a powered pump does it
by itself every day; no tanks (they would have to be tall and huge) and no hoses.

### D64 — The overview describes the game; what counts as a bug (2026-09-28)
The overview describes the game — light on detail in places, but not wrong — so the design document's sections are
rebuilt from it. A bug is an insect or another arthropod, since those are bug-like: spiders, scorpions, centipedes,
millipedes, pill bugs, crayfish and crabs. Fish are separate, because the owner enjoys fishing. No worms and no leeches
(snails, not being arthropods, go by the same rule — the assistant's reading).

### D65 — Later decisions stand; no magic; weather as weather (2026-09-28)
P1 accepted: where a later decision of the owner's replaced an older text, the later one stands, and the older
documents now carry a note saying so. P2 accepted: no magic — the world runs on 2126 science, and enchanting, arcane
tools and books, magic bait, dwarven ruins and fantasy metals are dropped. As a balancing lever, weather comes last;
rain and drought themselves stay an ordinary part of the game.

### D66 — §00 answers: a bug farmer, remains, the misfits, voices (2026-09-28)
The game is about being a bug farmer: bugs are raised like any other livestock, beside the gardening — plants and
compost — that feeds them; "catch, breed and fight" alone reads like a monster-collecting game, which it isn't.
Further from the village the bugs grow more dangerous, not necessarily bigger. Old mammal bones and other remains are
fine — only living mammals are out — so the bones, the bone piles and the cow skull stay, and so does the cat statue.
The hay bale becomes a straw bale; the scarecrow goes, since bug control comes from other mechanics; the birdbath
becomes a butterfly water dish (the assistant's name — "puddling" would lose most players). Realism is never required:
the game passes on a little real biology and ecology, but it plays as a game — mosquitoes and other blood-feeders feed
on people and on big bugs such as caterpillars, and the mosquito zone stays. Each townsperson has a voice of their
own. The pillars use plain names.

### D67 — A sandbox, not a path; what a private plot protects (2026-09-28)
It's a sandbox, and no one way of playing is required: a player can ranch ants, roam the wilds as a hunter, or do
anything else; most will start a fly farm and grow from there. Most players grow their bugs' food, but it can also be
bought — gardening is a choice, not a step. A private plot's protection is from other players: nobody can add
or change anything on it without the owner's permission. It is not protected from what the owner sets up there —
penned wasps can go wild while the owner is away. *(This corrects D58 and the overview, which had carried over the
January 2026 line that nothing on a plot is lost or damaged while its owner is away.)* The pillars (§00, P2) are
accepted.

### D68 — §00 settled: the pitch (2026-09-28)
The long pitch stands for now: a multiplayer sandbox set in 2126, where nearly every mammal is gone and people have
bred the bugs giant; players farm, mine, craft, build and explore however they like — most start a fly farm and grow
from there, while others ranch ants or roam the wilds as hunters — in a living ecosystem that answers everything they
do. It gets another look when the promotional material is made. With the pillars (D67), the misfits (D66) and the
voices (D66), §00 is final.

### D69 — The item pass, first batch: pickaxes, axes, shovels and the tool families (2026-09-29)
The owner marked the first 34 rows of the item pass; these are settled with his notes.
- **Pickaxes.** The eight rungs stay, copper and bronze both: each opens its own ore, and both outfits are already
  made. The top two rungs are called cobalt steel and tungsten steel — tungsten steel replaces tungsten carbide (D61),
  made at the forge from steel and tungsten the way cobalt steel is. The top pickaxe gets no gold-coloured finish, so it
  can't read as a gold pickaxe; the rock drill has tungsten-steel bits.
- **Axes.** A stone axe comes first, made from wood and stone at the village workbench, which an early task has the
  player do; then iron, then steel. The wooden and copper axes go. Trees come in two kinds of wood, ordinary and hard,
  each with big trees: the stone axe fells ordinary trees, hardwood needs iron, and steel is faster on both. An axe
  can fell a big tree, very slowly; the saw does it much faster (this replaces "only the saw fells a big tree", D12 and
  P21). The chainsaw tops the line, fast on every tree. A tree overview goes to the owner when the design reaches the
  world.
- **Shovels.** Wooden, copper and iron. Each takes one hit fewer per square at the same swing speed — three, two, one —
  on dirt blocks and ground alike. Digging is meant as an early-game skill that tops out a few sessions in, and tool
  lines may finish at different speeds, some early, some climbing all game. The shovel keeps all three jobs — digging
  dirt blocks, digging up ground and laying ground — on the square the player points at, within reach. Past the iron
  shovel, the faster step is a powered spade that chews through dirt when held against it, so the player tunnels
  faster: the power tool for dirt, beside the rock drill and the chainsaw.
- **Hoe and scythe.** Wooden, copper and iron, covering one square, then up to two by two, then up to three by three;
  R picks the size and the cursor outlines the squares first. Playtesting confirms the sizes.
- **Nets.** The small and large hand nets as the owner described them: the small net takes a few small bugs; the
  large one takes more flies per swing and bigger bugs such as wasps; which nets can hold a bug is set per species,
  and examining a bug tells at once which nets can't, while its other facts (bait, breeding needs) open with more
  examining. The cast net is thrown and never stays in the world; the placed trap is the net that stays put (D63).
- **Crafting.** Nothing is made by hand: every recipe needs a station, torches included — a separate system for a few
  items isn't worth it. An early task points new players to the village workbench, where they make their first stone
  axe. A player's own workbench can be picked up and carried; a player heading into the dark brings torches or a
  workbench, as in Terraria, where a player who runs out of light is left in the dark. How a stranded player gets
  home is open: a device that sends a player home would be used as a free warp, and what players like best is unknown.
- **Laying ground.** The owner would prefer diagonal ground too — roads look better with it — but worried players
  might find it confusing; the assistant designs how laying ground works, diagonals included, with the controls and
  screens that make it easy, and brings suggestions. Until then, whole squares (D45, P12) stand.
- **The first zones come first.** Before new zones are built, the owner and the assistant redo the first zones —
  every scene, the buildings included — starting from where they stand, to see how it goes and get the groundwork
  right for the rest (the roadmap's phase 2).
- **Testing grows with the game** as ongoing work, not a backlog item: test zones (a gardening one, for example) and
  more of what the assistant can run itself, such as Unity's command-line tools and screenshots, as each remaining
  system is built.

### D70 — Laying ground: shapes placed by hand (2026-09-29)
Building freedom comes first, so ground shapes are placed by hand rather than drawn automatically (the automatic
proposal of the same day is set aside). Players must be able to build checkerboards and other patterns; full squares
and the four diagonals are required, for roads, and straight halves and quarters are welcome only if the controls stay
simple on small screens. A shape is laid on top of whatever ground is already in the square, so one material is chosen.
Digging peels layers away down to a shared base that can't be dug, so a square is never empty. There is always a
preview. How the controls work is the assistant's to design (D45); the design and its open questions are in
`docs/product/investigations/research-2026-09-29/laying-ground-manual.md`.

### D71 — Laying ground: garden plots, what's covered, the base (2026-09-30)
No shaped piece can be laid on a garden plot, which the hoe makes; partial garden plots are not wanted. The assistant
is to suggest how garden plots are removed. On laying over something, the owner leans toward getting it back as its
materials, as if dug up (a tile under grass comes back as the tile), rather than losing it; the assistant is to think
it through and recommend. The base under all ground is left to the assistant. The recommendations are in
`docs/product/investigations/research-2026-09-29/laying-ground-manual.md`.

### D72 — The hoe; decorations and human places in later areas (2026-09-30)
- **The hoe (option A; adjustable later).** Any square made only of soft ground — grass, dirt, sand or mud, whole or
  mixed — is tilled where it lies in one swing, and nothing comes back. A square with a hard part (stone path, stone
  floor, wooden floor) needs that part dug first, and the preview says so. There are no partial beds. Every option had
  pros and cons; this one fits best.
- **Later areas.** Fresh decorations and other goods turn up in pockets through the game, a handful in some places,
  not in every area, with hidden and rare ones scattered in other places. The western town, for one, has recipes in a western style,
  and Spider Vale might have things of its own.
- **Human places.** Two or more are wanted. One is the Wasp Thicket's ranger outpost, which settles where the ranger
  station is (the documents disagreed; §01). Perhaps a castle or something similar in Spider Vale, or
  elsewhere.
- Items are added as the zones are built; most zones still need designing.

### D73 — Saving characters with the world, and backups (2026-09-30)
- **Build all of it now (the owner's decision).** Characters are saved together with their zone every minute and
  when the server stops; the faults that could still duplicate or lose items are fixed as part of it (zone
  crossings, reconnects, two copies of one zone); rolling backups and a restore command are added. Everything is
  to be tested end to end before it counts as done.
- **Recommendations the owner accepted.** Backups go to `C:/Users/emily/BugFarmer_backups/world`, outside the repo.
  A restore brings back every zone and every character together, after taking a safety copy — the recommended
  option, accepted as the one that serves players best. The numbers: a save every minute, a backup every 30
  minutes while anything changes, keeping the newest 10, one a day for a week and one a week for a month. The owner
  took these on trust in the research behind them, so they are recommendations to revisit if playtesting argues
  otherwise, not the owner's own design.
- How it works: `docs/product/architecture/architecture_persistence.md`; the proposal it builds is §19 P5.

### D74 — The item pass: the potion batch, foods from scratch, and a use for everything (2026-10-01)
The owner marked the fourteen rows of the new potion set and, the same day, set four directions for the item pass.
- **Potions.** The rules row, the calm spray, the bandages, the healing potion, the antivenom, the burn salve, strong
  coffee and the bug bomb stand as proposed. The venom coating goes, since a whole mechanic for coating a weapon isn't
  wanted, and so do the muscle rub, the stimulant shot and the sage tonic, which he marked down. The list should be
  fuller and designed effect first, ingredient second: stamina, speed, strength, healing at once and a health boost,
  armour, venom, stealth (how close a bug has to be to notice you), the private plot's happiness beside its
  decorations, sting resistance, and others. This replaces P16's "a small set to start". He asked how coffee would be
  made; an answer is proposed in its row. What "venom" means, and what to change in the night-sight drops, wait for
  his answers; night sight itself stays (D54).
- **Several things can boost the same thing.** An outfit's bonus doesn't stop a meal, a potion or an accessory from
  giving it too.
- **Everything in the world needs a use** — a food, a potion or a dye (dyes have recipes, and dye and dyed cloth
  sell) — or whether it belongs is questioned; some plants simply give different amounts of fibre. Items that clearly
  have no use are cut before his review.
- **Foods start again from scratch**: real dishes cooked from what players grow, fish and farm, and nothing goofy. The
  old list of 46 goes.
- **Cotton can stay**, his leaning after first saying cloth from thread was enough (D15 had already decided cotton):
  cotton thread and cotton cloth make finer clothes, beside roughspun clothes made from plant fibre.

### D75 — The item pass: the accessory marks, bugs as livestock in the kitchen, armour, and weapons so far (2026-10-01)
The owner's marks on the new accessory set were made just before his potion marks but were missed in D74; they are
recorded here, with his answers of the same day, the outcome of batch 3 (armour) and batch 2's answers so far.
- **Accessories.** He kept the work and harvest accessories (the garden gloves, seed tin, hive tool, oven mitts, tape
  measure, thimble, ore sieve and dyer's gloves), both headlamps, the first-aid kit (a kit sold in the village rather
  than a pouch from a far outpost) and, on trial, the telescopic net pole. A station accessory gives a 30% chance of
  an extra, his figure; the ore sieve helps the pan as well as the sluice. He cut the rest of the set: the accessories
  for stamina, defence and resistances, the hori-hori, the infrared thermometer, the measuring cylinder, the work
  apron, the night-vision goggles, the UV torch, the barometer, the thermos, the jar belt, the fuel pouch and the
  three kits; the dissecting kit because the bug extractor is a machine, and the mosquito head net because the
  mosquitoes are giant. In place of the running insoles he asked for something else: a Drag Harness is proposed, a
  smaller help with dragging than the Bug Wrangler's Leathers. My calls: the dyer's gloves rise to 30% to match the
  other station accessories, and the garden gloves stay at 15%, since crops are the bulk of a farm's harvest. With
  these marks, help in a fight comes from outfits, potions and food, and accessories are the work tools and lights.
- **Bugs in the kitchen are livestock (his direction).** Giant bugs give steaks, and a fly roasts like a small bird.
  The shape is my proposal, which he accepted: a small bug such as the fly is cooked whole; a big bug is butchered at
  the bug extractor into one cut per job (D31) — beetle steak, locust legs, scorpion tail, spider meat, or bug meat
  from flies, centipedes and dragonflies; giant ant eggs are the eggs; grub fat stands in for lard. Some bugs aren't
  food, for their real reasons: fireflies, millipedes, milkweed caterpillars, carrion beetles and ladybirds. The teas
  go. Drinks are juice, cider and mead in glass bottles, which are bought or made. After review I made these calls:
  drinks give no boost, so they never compete with a potion; centipedes give bug meat, since large centipedes really
  are eaten; and a dish's length follows the effort that went into it.
- **Potions.** The night-sight drops become the Night Vision Potion, made from carrot and glowing mushroom, with no
  moth eyes. Venom in his list meant resisting it: the Venom Resistance Potion, with spider venom among its sources as
  he said; wasp venom makes the first strength so it can be made early, as D54 has it, and stronger bugs' venom makes
  stronger ones (my call after review). One timed potion works at a time, drinks and balms alike, while cures and
  healing don't count against it (my proposal, accepted).
- **Venom on weapons.** There are no coatings: venom comes only on weapons made from a venomous part. The Venom
  Dagger kept in batch 2 is dropped (my recommendation, accepted).
- **Lights.** The Firefly Lantern pulses yellow-green, its fireflies blinking out of step with their glows overlapping,
  and the Glowworm Lantern glows a steady blue-green (his picture; both colours are true to life). Each is a glass
  bottle holding the live bugs.
- **Bee suits.** The bee suit stops every sting but is weak armour, worn for the bees; the ranger outfit is the quicker,
  better-armoured answer to wasps and hornets; the Padded Bee Suit comes later, with real armour (his calls). The
  ventilated suit goes. Fire ants and scorpions still hurt a player in a bee suit through their bites and claws, so
  their own armours keep a job (my proposal, accepted).
- **A private plot's happiness.** Outfits shown on a mannequin raise it, and so does armour made for show, such as
  Fancy Armor; jewelry on a stand raises it too (his direction). Counting them on display rather than worn, and making
  jewelry the happiness accessory, were my recommendations, accepted: five pieces made at the gem cutter from silver,
  gold or platinum and a cut gem, which give those metals and the gems a job.
- **Armour (batch 3).** The metal sets are armour, named Copper, Bronze, Iron, Steel and Cobalt-Steel Armor in the game.
  A new character starts in the Farmer's Outfit, and Bug-Leather Armor is an early craft once you have been out for
  bugs. Gilded steel is cut. Fancy Armor, made with gold and the high metals and not the strongest, replaces the
  platinum plate and uses the picked "fancy" design. Cobalt-Steel Armor's look was left to me, asked only to be
  striking and late-game: its own design, with the art asked for first. The picked "platinum" and "gilded-steel"
  designs are left without an armour for now.
- **Obsidian.** Everything mined comes as blocks, so obsidian is black blocks in Spider Vale West; the steel pickaxe
  opens them (my call).
- **Weapons and tools (batch 2), answered so far.** The weapon rule stands: each kind of weapon comes in the few metals
  that suit it, so each new metal upgrades some weapons, not all; swords are the exception, in every metal up to the
  two top steels; each kind mixes in two or three special weapons, mostly made the old-fashioned way. This changes
  P20, where weapons stopped at steel and bug parts took over. Daggers and maces come in copper and iron only.
  The specials are the Winged Spear, the Stiletto, the Obsidian Dagger, the War Hammer and the Beetle-Horn Maul, plus
  an Obsidian Sword, quick and nearly the strongest, and a katana sold in the western town (the Venom Dagger is dropped
  above). Three weapons are made of bug parts, his choice: the Beetle-Horn Maul, the Scorpion-Sting Spear, which
  carries venom, and the Spider-Fang Dagger. Two answers are still open, the harvest sickle and the tools that bring a
  bug in alive; batch 2's rows are updated once they are in.

### D76 — The item system's backbone, food and the stove, and no limit on art (2026-10-02)
The owner asked for the item system to be thought through as a whole rather than row by row, and answered the
proposal that followed.
- **A character sheet, to start (my proposal, accepted as a starting point).** Six meters shown as dots — Health,
  Stamina, Armor, Strength, Speed and Stealth (how close a bug gets before it notices you) — three protections (Sting,
  Venom, Acid) and a list of standalone perks (night vision, +30% planks, faster dragging). Each kind of item has a
  job: the one outfit sets armour and protections, shifts a meter or two and gives one to three perks; the two
  accessories give perks only; the one meal raises Health and Stamina; the one timed potion makes a strong, short
  change; tools take their power from their metal; weapons have damage, speed, reach and one trait. These are
  guidelines, not laws: an item may break the pattern when that makes sense.
- **Small mechanics are perks, not items.** Dragging is minor, so faster dragging is a second perk on the Bug
  Wrangler's Leathers; the Drag Harness goes, and the running insoles get no replacement. An outfit can carry several
  bonuses.
- **Food.** A meal raises Health and Stamina while it lasts, better food more, and many dishes add one of the eight
  boosts, depending on the food; the eight boost families stay. Coffee is made and sold with food but works like a
  potion.
- **Bugs go straight to the stove.** The bug extractor makes materials, and dishes take the bugs themselves, so
  players don't prepare cuts: the four cuts and bug meat go, and D18's line that the extractor is used in cooking no
  longer holds. How cooking plays — preparing ingredients first, as in Palia, straight from recipe to dish, as in
  Stardew Valley, or another way — is to be designed, with options for him.
- **No art budget.** The game gets as many outfits and as much art as a rich and varied game needs; the spending limit
  applied only to the test runs. Every paid image is still asked for first.
- **Left open:** a quality mark for well-raised bugs (prime materials), raised with the sheet; it comes back with the
  ranching design.

### D77 — How cooking plays: recipes from books, no experimenting (2026-10-02)
The owner answered §11's main question.
- **Cooking from recipes (the "cook from the book" route).** Dishes are cooked from recipes you know: there's no
  experimenting with ingredients and no Palia-style chains of preparing steps (single steps at other stations, such as
  milling flour, stay as they are). Recipes come singly and in recipe books, and both are found in the world and
  bought.
- **Everyday and rare dishes.** The food list needs a good spread of rare dishes beside the everyday ones.
- **Each recipe names its station.** Some need the cooking range; others need only the spit, whose own recipe takes a
  campfire (the owner's leaning).
- The follow-up questions that only mattered for the hands-on routes (how well you cook, experimenting, the spit's
  timing, mastering a dish, a mix that matches nothing) fall away. Feasts (§11 P4) and what a feast gives are still
  open.
- **Proposed, not decided:** the details are in §11 P9–P11 and Q2 for the owner's review. Bought recipes and books
  use the shop system the carpenter's books already run on (`shopBuyBook`); found ones are read where they lie, so
  nobody takes one from the others; the spit is made from a campfire and wood, and the plain campfire stops cooking.
  Which stations can cook which dishes is asked as Q2 (recommended: the range also cooks the wood stove's dishes, and
  only the spit cooks the fire dishes).

### D78 — Cooking stations by how they cook; rare dishes can give more (2026-10-02)
The owner described the cooking stations and asked for help designing the rest, aiming for what is most fun.
- **Stations.** Cooking takes time, so a larger stove cooks more dishes at once. A stove has a top with burners and
  can have an oven, and bread and other baking needs the oven. The wood stove has a top only; a larger range has more
  burners. The spit only roasts.
- **Fires.** Someone on the road carries a spit, a pot and firewood and makes a fire where they stop. A fire is made
  and placed where it's wanted, never carried: it stays where it is until it's dug out.
- **The owner's ideas to explore, not rulings:** adding a pot to a fire, and building up from a fire to a fire with a
  spit, then a pot as well. The design is left to the assistant. This replaces D77's leaning that the spit's recipe
  takes a campfire.
- **Rare dishes** may do more than raise Health and Stamina, and may raise those two by different amounts.
- **One review at the end.** Open review items are held until the whole set is ready, then reviewed together.
- **Paused the same day** for a check of the bugs: the owner asked to review the bug list first, since brainstorm
  passes make tentative lists, not additions to the game.

### D79 — The bug list marked: what stays, what goes, and fresh suggestions (2026-10-02)
The owner went through all 116 bugs on the items page and asked for the assistant's own suggestions in place of the
old lists, which earlier models wrote without taste, starting from the bugs kept.
- **Kept:** the fifteen in the game; black and fire ants, each with workers, warriors and a queen (fire ants far more
  dangerous); the locust; the mosquito; the glowworm, the cave beetle and the small cave spider; the cave fly; the
  killer bee; the black widow; the scorpion; the rhinoceros beetle. Saved from my cuts: the horse fly, woodland
  butterflies such as the purple emperor, the medium and deadly dragonflies, and more kinds of centipede.
- **Cut:** the aphid and the ladybird (the owner doubts aphids add play without muddling it), cockroaches, the
  gall wasp, leeches and snails, the extra ant species, the invented creatures, and the picture-only extras I proposed
  cutting. The thirty old zone-plan picks the owner disagreed with are off the list; any can return only as a fresh,
  reasoned suggestion.
- **Still candidates, for their zones:** the bumblebee, the carpenter bee, the paper wasp, the yellowjacket, a second
  hornet, the luna, emperor and hawk moths, the monarch, the water strider (its name), the daddy longlegs (its
  name, not "harvestman"), the cricket, the crop beetle, the mantis, the stag beetle, the wolf and jumping spiders,
  the tarantula, the giant huntsman, the crayfish and the crab.
- **How many of each:** two kinds of dragonfly at least, a beginner one found first west of the village and others
  in later areas; three millipedes, one more dangerous, perhaps poisonous, and fast, dangerous ones among them; three
  centipedes, chosen for real danger; at least two scorpions, some in the Wasp Thicket; two wasps and two hornets (the
  giant hornet and the hornet are separate species with hives). The owner asks whether wasps have soldiers at all.
- **What a zone holds:** zone bugs should be recognizable, or variants of known ones, with now and then a unique bug
  that has no variants; nothing that would puzzle players.
- **Ecosystems, not events:** centipedes near the ants live there as part of the ecosystem; there are no random raid
  events, and "raid centipede" isn't a species. Mosquitoes need something in the marsh to feed on; they are a
  later-stage danger that lunges and swarms, held back by sand laid on the marsh and other means. The desert zone is
  pictured as a drier, rocky place rather than sand.
- **A new mechanic:** the non-lethal bug stick can steer ants off their trail and herd them by tapping them.

### D80 — The bug lineups answered: bees as a progression, two cuts, real names (2026-10-02)
The owner answered the assistant's bug lineups in conversation.
- **Bees climb in danger.** The honeybee stays, with a more dangerous step up after it, the killer bee, and possibly
  a third beyond that. Beekeeping matters as much as the rest of bug farming, and both need progression.
- **Cut:** termites, which would not fit the game's mechanics, and the stick insect.
- **Mantis egg cases** come from the game's own mantises.
- **The farm cricket** is a maybe.
- **The rest of the lineups stand,** on one condition: every bug carries its real name.

### D81 — Bees for the hives (2026-10-02)
The owner added to D80 in conversation.
- **Hive bees.** The bees of the beekeeping ladder should, ideally, be bees a player can keep in hives.
- **The bumblebee is accepted.**
- My wild giant honey bee, hunted rather than kept, missed this. The revised lineup keeps it on rafters, as people
  in southern Vietnam really keep it, and offers the Asian honey bee, which lives in boxes, as the alternative. The
  third step is not yet decided.
