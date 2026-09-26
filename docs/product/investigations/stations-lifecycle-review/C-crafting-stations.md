# C — Crafting Stations & Containers: audit (ASSESSMENT ONLY, no code changed)

Scope: the recipe/craft-station engine (`craft_stations.go`), the storage-container engine
(`handlers_containers.go`), the recipe data (`recipes.json` + `entities/recipe.go`), the ONE unified
client panel (`CraftingPanel.cs`, ~1000 lines), and the integrity gates (`recipe_graph.py`,
`catalog_coverage.py`). Every claim below is anchored at file:line and verified against the real
code/data. Date: 2026-07-18.

Verdict legend: COMPLETE / HALF-WORKING / MISSING / NEEDS-REFACTOR.

---

## 0. The objective completeness gates — actual output

**`python3 tools/data/recipe_graph.py` → EXIT 0 (PASS).**
`recipes=185 items=209 placeables=286 occupants=159`. 9 warnings, all legitimate base resources
(carcasses `dead_centipede/millipede/wasp/fly/butterfly/beetle/ant`, `wasp_stinger`) that come from
mob drops, not recipes — not orphans. The three completeness matrices it asserts (6-metal
`ore→paydirt→refined` chain; tool ladder copper..platinum for pickaxe/axe/hoe/scythe/shovel; gem
`raw→cut` for diamond/quartz/ruby/sapphire/emerald) are all FULL.

**BUT the gate has real blind spots** (see §2): it does NOT check weapon ladders, bronze-tier tools,
the gem block→raw mining step, OR whether a `shop:<npc>`-gated recipe is actually *sold* anywhere.
Several genuine half-ladders and dead recipes pass it.

**`python3 tools/data/catalog_coverage.py` → EXIT 1 (FAIL).**
GATE 1 = **48 orphans** (an entity documented in no `docs/product/economy/catalogs/*` page). Most are
bee-zone / beach-zone / floral-furniture content added after the catalogs were last swept. Crucially,
**all 8 `*_floral` furniture items are orphans AND also unreachable recipes** (§3) — doubly flagged.
This gate is currently RED.

---

## 1. Findings table

| Area | Status | Evidence | Severity |
|---|---|---|---|
| Recipe reachability (recipe_graph) | COMPLETE | `recipe_graph.py` exit 0; 9 warnings are real base drops | — |
| Catalog coverage (catalog_coverage) | HALF-WORKING | exit 1; 48 orphans incl. all 8 floral items | MED |
| `floral_furniture` collection (8 recipes) | MISSING (unreachable) | gated `shop:carpenter` but carpenter sells NO floral book → can never be learned; `handlers_shop.go:165` `shopBuyBook` needs a `books` entry, carpenter has only basic+advanced (occupants.json:3089/3150) | **HIGH** |
| Metal refine chain (6 metals) | COMPLETE | crusher+sluice+bar recipes present per metal; tin→bronze by design (`recipes.json`) | — |
| Bronze TOOL tier | MISSING | no `{pickaxe,axe,hoe,scythe,shovel}_bronze` item OR recipe; gate only checks copper..platinum so it passes; bronze *weapons* exist → inconsistent | MED |
| Weapon ladder (sword/spear) | HALF-WORKING | `spear_wood` item exists but **no recipe, no shop → unobtainable**; `sword_stone`/`spear_stone` absent (ladder jumps wood→copper); gate checks weapons not at all | MED |
| Dead starter items | HALF-WORKING | `spear_wood`, `scythe_wood`, `shovel_wood`, `large_net` exist as items with **zero obtain path** (not crafted, not sold) | MED |
| Empty craft stations | HALF-WORKING | 7 placeables are `interaction_type:craft` with 0 recipes → open an empty panel: cauldron, cooking_pot, campfire, campfire_spit, stove, sink, keg (intentional per D16/D19/D26 backlog) | LOW-MED |
| Filtered containers that reject everything | HALF-WORKING | `bookshelf`/`bookshelf_fancy` filter=`book`, `wine_rack` filter=`drink`; **0 items carry those tags** → every deposit silently refused (`handlers_containers.go:67`) | MED |
| `catalyst` recipe field | NEEDS-REFACTOR (dead) | `RecipeDef.Catalyst` fully wired (`recipe.go:23`, `craft_stations.go:181`, client `EnumInputs`) but **0 recipes use it**; coal is a plain input, not a catalyst; doc implies fuel-catalyst | LOW |
| Dead-dropper cleanup | MISSING | crafting_buildout said "delete ore_pile/ore_sack/coal_bin/geode" — all 4 still present | LOW |
| Multi-lane processors (`craft_slots`) | COMPLETE | 6 stations ship craft_slots=2 (bug_extractor/dye_vat/forge/furnace/ore_sluice/sawmill); lane rows + PickLane + stall logic all wired; 5 Go tests | — |
| Legacy-save migration (UnmarshalJSON) | COMPLETE | `craft_stations.go:43` accepts both shapes; `TestCraftLegacySaveMigratesToProcs` green | — |
| Station→recipe contract (generic station) | COMPLETE | all 15 recipe stations exist as placeables with `interaction_type:craft` — no unreachable station | — |
| `move` op (precise drag-drop) | HALF-WORKING + doc-stale | doc says "client drag deferred"; client DOES send `op=move` for inventory→container deposit (`CraftingPanel.cs:468`) but container→player is quick-only, no in-grid reorder, no partial-count picker | LOW-MED |
| Quick-stack / sort on chests | MISSING | storage ops are only open/quick/move; no deposit-all-matching, no sort | LOW |
| Unified panel dispatch | NEEDS-REFACTOR | clean 5-way `BuildContent()` switch, NOT a scattered if-tangle — but one 1003-line MonoBehaviour holds all 5 modes' widgets (craft+compost+nursery+beehive+storage); server keeps crafting/breeding separate, client fused them | MED |
| Dead client code | NEEDS-REFACTOR (dead) | `CraftingPanel.CanAfford` (line 950) never called; `set_recipe` server op has no client sender | LOW |
| Server factoring (craft_stations/containers) | COMPLETE | clean helpers, lazy-init, per-item output merge, correctly OUT of the sim hash | — |
| Published client mirror | COMPLETE | `recipes.json` canonical == published (diff clean) | — |

---

## 2. The recipe_graph gate's blind spots (why "PASS" is not "complete")

`recipe_graph.py` (read in full) asserts three matrices, but its coverage is narrower than the
buildout's intent:

- **Weapons are not checked at all.** `spear_wood` is a valid item with tier 1 but has **no recipe and
  is in no shop** — completely unobtainable. `sword_wood` IS craftable (workbench). The gate never
  looks at sword/spear, so this asymmetry is invisible.
- **Tool ladder tier list is `copper,iron,steel,silver,gold,platinum`** (`recipe_graph.py:87`) — it
  skips **bronze** and the wood/stone base tiers. Result: bronze *weapons* exist
  (`sword_bronze`/`spear_bronze`, forge) but bronze *tools* do not exist at all (no item, no recipe)
  and the gate is happy. The buildout's stated ladder is "wood→stone→copper→bronze→iron→steel", so
  bronze tools are a real hole.
- **Gem chain checks `raw→cut` only** (`recipe_graph.py:96`), not the mining `block→raw` step. That
  step happens to be fine (blocks drop the raw gem — verified: `ore_diamond/ruby/sapphire/emerald_block`
  drop the gem; `quartz_block` drops `quartz`), but the gate would not catch a gem whose block was
  missing.
- **Shop-grant reachability is unchecked.** A recipe with `unlock:"shop:carpenter"` is only learnable
  if the carpenter sells its recipe (by id) OR sells the `books` entry for its `collection`
  (`shopBuyBook`, `handlers_shop.go:165`). The gate never cross-references shop stock, so the 8 dead
  floral recipes below pass it.

Recommendation (not applied): extend `recipe_graph.py` with a 4th gate — every `shop:*`-gated recipe
must be granted by some shop's `recipes[]` or `books[]` — and add bronze/weapon rows to the matrices.

---

## 3. Dead / unreachable content (concrete list)

**8 unreachable recipes — the entire `floral_furniture` collection.** All gated `unlock:"shop:carpenter"`
with `collection:"floral_furniture"`, but the carpenter's shop block sells only the `basic_furniture`
and `advanced_furniture` books (occupants.json:3089/3150) — there is **no `floral_furniture` book on
any vendor**, and `shopBuyBook` learns a collection only if a matching `books` entry exists. So these
can never enter `KnownRecipes`, and `CraftingPanel.BuildCraftContent` (line 330) filters out any recipe
the player hasn't learned → they are invisible/uncraftable forever:
`bed_floral, chair_floral, table_floral, dresser_floral, lamp_floral, vase_floral, bookshelf_floral,
rug_floral`. (All 8 are also catalog orphans.) One-line data fix would be a `books` entry, but this is
assessment-only — flagging.

**4 dead items (exist in data, zero obtain path):** `spear_wood`, `scythe_wood`, `shovel_wood`,
`large_net`. Not produced by any recipe and not in any shop's `sells`. Contrast the working starter
tools `pickaxe_wood/axe_wood/hoe_wood` + `watering_can_basic/large` + `small_net`, which the
general store sells. The wood-tool starter set is inconsistent — half sold, half stranded.

**7 empty craft stations** (`interaction_type:craft`, 0 recipes): cauldron, cooking_pot, campfire,
campfire_spit, stove, sink, keg. Right-clicking any of these opens the craft panel with an empty
recipe grid. This is *intentional scope* (potions/cooking/wine are decision-backlogged per
D16/D19/D26) but is currently a dead-end UI, not a "coming soon" affordance.

**3 non-functional filtered containers:** `bookshelf`, `bookshelf_fancy` (filter `book`) and
`wine_rack` (filter `drink`). No item in `items.json` carries the `book` or `drink` tag, so
`containerAccepts` (`handlers_containers.go:67`) refuses **every** deposit — silently. These read as
storage but store nothing. (`HasTag` is nil-safe — `entities.go:277` guards a nil receiver — so this
rejects rather than crashes.) `textile` is thin too (3 items) but functional.

**Dead-dropper cleanup never done:** the buildout instructed deleting `ore_pile/ore_sack/coal_bin/geode`;
all four still exist (`ore_pile`/`ore_sack`/`coal_bin` in placeables, `geode` an occupant).

---

## 4. The unified panel (`CraftingPanel.cs`, 1003 lines)

**Dispatch is clean, not a tangle.** `_mode` is set once from `world.interaction_type`
(`TryHandleRightClick:199`) and there is exactly ONE dispatch point — `BuildContent()` (line 291-295)
routes to `BuildCraftContent / BuildStationContent / BuildNurseryContent / BuildBeehiveContent /
BuildStorageContent`. The two echo/refresh paths (`OnMatchState`, `OnInventoryChanged`) branch by the
same mode flags. No scattered `if (interaction_type==...)` sprinkled through logic. Given it hosts five
modes this is orderly.

**But it is a "god panel" and that's the real smell.** This single MonoBehaviour owns widget fields and
build+refresh code for all five modes at once: craft engine (recipe grid, input squares, qty stepper,
lane rows, output grid), compost station (deposit grid, fill meters), the shared brood region (nursery),
the beehive harvest control, AND storage. ~40 instance fields, most mode-specific; `BuildContent()`
unconditionally clears every one of them each open (lines 269-289). The *server* deliberately keeps
crafting (this container/recipe engine) and breeding (compost/brood/nursery — a different domain, the
bug ecology) **separate** (architecture_crafting.md is explicit), yet the *client* fused all five into
one class. The station/nursery/beehive modes are the recent breeding fold-in (per the git log). This
works and is not buggy, but it is the maintainability liability here — a candidate for extracting
per-mode view components sharing a small base. Severity MED (structure, not correctness).

**Dead client code:**
- `CanAfford` (line 950-955) is defined `private static` and **never called** — `RefreshSelected`
  computes affordability inline (lines 759-778). Leftover.
- `set_recipe` op: the server handles it (`craft_stations.go:304-320`) but **no client code sends it**
  (only the doc comment in `ContainerMessages.cs:25` mentions it) — `craft` carries the recipe id.
  A deliberate seam, but currently a dead path both ends can't exercise together.

**`move` is now half-wired and the doc is stale.** architecture_crafting.md:50-51 and the
`ContainerMessages.cs` comment both say precise `move` is "server-supported; client drag deferred — see
backlog". In fact `OnContainerSlotClicked` (line 463-479) DOES send `op=move` (zone player→container,
respecting `count`) when you hold a cursor stack and click a container cell. What's still missing:
container→player precise move (only whole-stack `quick`), in-grid reordering, and a partial-count
picker (the client always passes the full `CursorCount`). So "move" is partially delivered; the
"deferred" note should be updated.

**Correct, well-built parts:** multi-lane rendering (one row per `craft_slots`, interpolated bars,
`PickLane` targeting a same-recipe or idle lane, "(all lanes busy)" disable), local-only recipe
selection (browsing never pokes the server), server-truth lane-count override rebuild (line 887),
and the shared brood region reused by compost+nursery+beehive.

---

## 5. Server factoring (`craft_stations.go`, `handlers_containers.go`) — mostly good

- **craft_stations.go** is tidy: small single-purpose helpers (`playerCount/Consume`,
  `outputHasRoom/addOutput`, `craftCollectOne/All`), lazy `resolveCraftStation` with `ensureProcs`
  normalizing lane count on both restore and def-change, and correct stall semantics (a full output
  grid holds one lane at full progress while siblings keep producing; inputs already consumed → nothing
  lost). The legacy `UnmarshalJSON` migration (line 43-58) folds the old flat `Recipe/Queue/Progress`
  into `Procs[0]` and is unit-tested. Well-factored — no notable smell.
- **handlers_containers.go**: `containerMove/QuickMove/addToContainer/slotRef` are clean and the
  filter check is nil-safe. One behavioral note (by design, not a bug): `addToContainer` and
  `PlayerState.AddItem` **ignore stack caps** (comment at line 76) — stacks grow unbounded.
- **Determinism**: both engines live in the deterministic `world` package but correctly stay OUT of
  `ComputeStateHash` — they are per-container/per-player display state, persisted per-chunk, never
  hashed. This matches the package-CLAUDE.md invariant and the architecture_crafting.md "never hashed"
  claim; verified the state structs feed no sim math.
- **Test coverage**: craft-station processors (5 tests), shop recipe/book grant (6 tests incl.
  `TestShopBuyBookGrantsCollection`), shop buy/sell (many). No *dedicated* unit test for
  `containerMove/quick` (exercised only indirectly) — minor gap.

---

## 6. Prose gap list (most severe first)

1. **HIGH — 8 dead floral recipes.** `floral_furniture` collection is gated to a carpenter book that
   no vendor sells → permanently unlearnable and uncraftable; also catalog orphans. Needs a `books`
   entry (or a re-decision to drop the set).
2. **MED — catalog_coverage GATE 1 is RED (48 orphans).** Bee/beach/floral zone content isn't
   documented in `catalogs/`; the coverage gate the project treats as objective is currently failing.
3. **MED — bronze tool tier missing** while bronze weapons exist; ladder is inconsistent and the
   integrity gate is blind to it.
4. **MED — dead items** `spear_wood`, `scythe_wood`, `shovel_wood`, `large_net` (exist, no obtain
   path). The starter tool/weapon set is half-stranded.
5. **MED — 3 filtered containers accept nothing** (bookshelf/bookshelf_fancy=`book`, wine_rack=`drink`;
   no item carries those tags). They look like storage but silently reject every deposit.
6. **MED — the panel is a 1003-line five-mode god class.** Not buggy, but the client fused domains the
   server keeps separate; extract per-mode components.
7. **LOW-MED — 7 empty craft stations** open a blank recipe panel (intentional backlog, poor
   affordance).
8. **LOW-MED — `move` op half-wired + doc stale** (deposit works; container→player precise, in-grid
   reorder, partial-count picker missing).
9. **LOW — dead code / dead paths:** client `CanAfford`, server `set_recipe` (no client sender),
   unused `catalyst` mechanism, uncleaned dead-droppers.
10. **LOW — no quick-stack/sort on chests** (genre-standard convenience, unbuilt).
11. **Tooling — recipe_graph.py under-covers:** add a shop-grant-reachability gate + bronze/weapon rows
    so the "no half-ladder" promise actually holds.
