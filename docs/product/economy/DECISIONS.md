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
  these, **drop `wildflower_petals`**.
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
