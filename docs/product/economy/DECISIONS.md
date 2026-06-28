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
harder east columns. *Why:* shrink initial authoring scope; re-add depth later. → `../architecture_world.md`.

### D3 — Underground col-0: Centipede → Ants
Underground **col 0** (was Centipede Cavern easy+medium) becomes **Ants** — easy ants (row 3) + medium ants
(row 4), and the **medium ant zone gets a Queen** (mini-boss, relocated from the dropped row-5 chamber). The
**Centipede Cavern** moves to the **medium-passages slot (4,1)**. The deep/deadly ants shift **up a row** and
keep **surface access to the col-3 Swamp** for foraging. *Why:* user direction. → `../architecture_world.md`.

### D4 — Balance = pacing, not minimalism
Every gating/pricing choice is reasoned against named Schell lenses (Flow/Curve, Pacing/Reward, Economy,
Meaningful Choices/Triangularity, Need/Toy). Each content category has a **target FLOOR** (a minimum count) —
floors, not ceilings; tuning adjusts numbers, never deletes content. → `progression.md`, `crafting.md`.

### D5 — Fishing deferred; décor bonus values deferred
Fishing is **out for v1** (design the rod + fisherman's vest only). Décor passive-bonus **VALUES** are not
authored yet (the §11.5 field is unbuilt) — we only **tag the bonus TYPE** per décor item. → `crafting.md`.

### D6 — Single coin currency
One coin type (matches the existing `sell_price`/`buy_price` on items), not barter. *Why:* simplest, already
priced. → `merchants.md`.

### D7 — Surface terrain is fixed (no surface-floor digging)
Resolves O1. Surface **floor** tiles are never dug/removed (engine rule: "ground always filled, no holes").
Players gather via diggable **block nodes** + mining-cliff tiles; "terraforming" = *placing* a floor tile on
top. **Water care:** two water tiles exist — `water_shallow` (wade; blocks insects) and `water_deep` (blocks
both) — any water placement/feature must respect both. → `../architecture_world.md`.

### D8 — Sand is a diggable BLOCK in sandy/beach clumps
Resolves O2. Sand is a **block** you dig through like stone/clay (break → drops `sand` → reveals floor),
placed as **small clumps in sandy/beach areas** — NOT harvested from the sand *floor* tile (which stays
decorative). Uses the existing `sand_block` concept. → `../architecture_world.md` (resource map),
`crafting.md` (sand → glass).

### D9 — Keep both ant colonies
Resolves O3. **Col 0** = a gentle intro ant colony (easy/medium + the Queen); **col 3** = the deadly endgame
ant colony (hard/extra-hard) that forages out to the surface swamp. Ants are a deliberate recurring theme
across difficulty. → `../architecture_world.md`.

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
A signature set represents a *concept* (beekeeping, ranger, mining, diving, bug-catching, chitin armour), and
may span multiple zones — NOT one set per zone. "Thorough" = a balanced amount per category, **not excessive,
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
Base metal sets = **leather · padded(cloth) · copper · bronze · iron · steel · silver · gold · platinum**
(9). **Straw cut** (too hard to integrate). **Platinum is the top — no diamond armour** (doesn't make sense).
- **Leather** comes from the **Bug Extractor** (dead bugs → leather, D18; no skinning mechanic).
- **Cloth** comes from multiple sources: **silk + cotton** (cotton is a LATER crop, not Zone 1 — D15/D19).
- Per-zone armour DEFENSE values get tuned against each zone's enemy damage → **backlog** (armour-balance).

### D12 — Tools: trim to "metal tiers + a few meaningful specials"
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
exploratory ramp — being "up and running" takes time, which is fine (exploratory > rushed).

### D14 — Dredge (mechanic proposal, see backlog)
Direction: place a **dredge on water** → at its station press **"dredge"** → the player appears with a **hose
from the dredge** and **clicks the water to dredge it like a tool**. Tiers (weaker→stronger) + condition
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
Right now we are creating **just two zones**: the **Starting Village** (`zones/village.md`) and the **first
underground "Mining Camp"** = **Underground Passages** (3,1, `zones/underground_passages.md`, the Miner's
outpost hub). Everything else (the other 15 zone sheets + the full catalogs) stays as **catalog reference,
unpolished**, until we reach it. These two zones get finalized to a buildable spec; pull only what they need
from the catalogs.

### D18 — Bug drops = `dead_<bug>` only; the **Bug Extractor** processes them
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

**Status: DESIGN ONLY — not built.** Missing: the open-station brood UI, take/move-larvae, and the host-rule
(mature / relocate / die). The brood *source* layer exists in `brood.go` (milkweed host-plant) / `nests.go`
(wasp nest `NestState`); this is the player-facing harvest/teardown layer on top. Data changes for later:
`wasp_nest` drop `paper_nest`+`wasp_larvae` → **none** (pick-up-and-move); `milkweed` drop `milkweed` → `fiber` + a *chance* `milkweed_seed` (per the D24 harvest rule), and milkweed is a **large plant** (several hits to fell, D24).

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
today). "We'll see how it works out" — the seed-drop chance is the main balance knob.

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
- **Ecologist** (building exists, "we forgot him") — has recipes for his house items: telescope,
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
