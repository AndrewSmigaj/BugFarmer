# Fishing Gear & Fish — Brainstorm

Rods, bait, lures, tackle, fish traps, nets, boat/dock gear, and a fish list with rewards. Ties to
the village boat/fishing store on the SW lake. Design only.

Read alongside:
- `docs/product/game_design.md` (world/zones, village).
- `docs/product/zones/village_21.md` (the village + SW lake / fishing store).
- Existing related ids: `bait_basket`, `dock`-adjacent village build, `aquarium` (display fish),
  `lily_pad`, `well`/`water_bucket` (water flavor).

## Rules this file follows
- Rods tier by **material/quality**; better = longer cast, faster bite, access to deeper/rarer fish.
  Older rods keep working (§7.3 spirit).
- Bait/lures are **bug-farming crossover** where it makes sense (worms, grubs from `grub_bed`,
  caught small bugs as live bait).
- Variety poor→fancy; "quality" is value/material tier.
- Fishing is a hands-on minigame layer; fish traps are the slow passive option (no instant free fish).

---

## 1. RODS (held — item icons, tiered)

| id | one-line | tier | bonus / role |
|----|----------|------|--------------|
| `rod_branch` | a bent stick with string and a bent-pin hook | starter | shore only, easy/common fish; what the store gives first |
| `rod_cane` | a simple cane pole | poor | reliable shallow-water fishing |
| `rod_wood` | a proper wooden rod with a basic reel | common | longer cast, can hold tackle |
| `rod_fiberglass` | a springy mid-grade rod | mid | faster bite, deeper water |
| `rod_iron_reel` | a sturdy rod with an iron reel | mid | fights bigger fish |
| `rod_steel` | a high-tension steel-guide rod | high | deep-lake & strong fish |
| `rod_master` | a finely balanced angler's rod | high | top bite speed + cast; rarest fish |
| `rod_gilded` | an ornate gold-fitting prestige rod | fancy | showpiece; best stats |

---

## 2. BAIT (consumable — raises bite rate; bug crossover)

| id | one-line | best for |
|----|----------|----------|
| `worm_bait` | a wriggling earthworm | common pond/lake fish |
| `grub_bait` | a fat grub (from `grub_bed`, bug crossover) | mid fish; better than worms |
| `cricket_bait` | a live cricket (farmed bug) | surface-feeding fish |
| `maggot_bait` | a pinch of maggots | small panfish, fast bites |
| `dough_bait` | a ball of bread dough | cheap, weak, common fish |
| `roe_bait` | fish-egg bait | predatory/larger fish |
| `shrimp_bait` | a small shrimp | bottom feeders |
| `glowbug_bait` | a luminous glow-bug (night, bug crossover) | night-active fish |
| `magic_bait` | a shimmering enchanted bait | any fish, raises rare odds; rare |

`bait_basket` *(exists)* holds/dispenses bait at a fishing spot.

---

## 3. LURES & TACKLE (reusable gear that modifies fishing)

| id | one-line | role |
|----|----------|------|
| `lure_spinner` | a spinning metal blade lure | attracts predatory fish, no bait needed |
| `lure_spoon` | a wobbling spoon lure | flashy; deep fish |
| `lure_fly` | a tied feather fly | surface fish; elegant |
| `lure_plug` | a fish-shaped diving plug | big predators |
| `bobber` | a float that signals bites | clearer bite timing |
| `bobber_lighted` | a glowing night bobber | night fishing |
| `sinker_weight` | a lead weight | fish deeper water |
| `tackle_box` | an organizer of hooks/lures | carry more tackle; small bite-quality bonus |
| `line_strong` | a high-strength line spool | reduces line breaks on big fish |
| `hook_barbed` | a set of barbed hooks | fewer escapes |
| `hook_treble` | triple hooks for lures | better hookups on predators |

---

## 4. FISH TRAPS & NETS (passive / area — the slow option)

| id | one-line | tier | role |
|----|----------|------|------|
| `fish_trap_wicker` | a woven willow fish trap (creel) | poor | passive small-fish catch over time; check to collect |
| `fish_trap_wire` | a wire mesh cage trap | mid | catches more/larger fish, slow |
| `crab_pot` | a baited pot for crustaceans | mid | crabs/crayfish; baited |
| `eel_trap` | a long funnel trap | mid | eels |
| `cast_net` | a thrown weighted circular net | common | scoop a cluster of small surface fish |
| `dip_net` | a hand landing net | common | land hooked fish reliably; reduces escapes |
| `seine_net` | a long dragged shore net | high | bulk shallow-water haul (two-spot setup) |
| `lobster_pot` | a baited slatted pot | high | premium crustaceans (if coastal added) |

---

## 5. BOAT & DOCK GEAR (the SW-lake fishing setup)

| id | one-line | role |
|----|----------|------|
| `rowboat` | a small wooden rowboat | reach deeper lake fishing spots |
| `fishing_skiff` | a sturdier flat skiff | carry more gear/catch; stable |
| `canoe` | a light canoe | fast, low-capacity, quiet (skittish fish) |
| `dock` | a wooden fishing dock/jetty | fish off the end; tie up the boat (village build) |
| `dock_post` | a mooring post/cleat | tie up boats |
| `boat_house` | a covered boat shelter | store/repair the boat (village/plot) |
| `oars` | a pair of rowing oars | propel the rowboat |
| `bait_bucket` | a bucket of live bait by the dock | keep bait fresh on the water |
| `fish_cooler` | an iced catch box | keep caught fish fresh longer |
| `tackle_station_dock` | a dock-side tackle bench | re-rig lures/line at the water |
| `buoy_marker` | a floating marker buoy | mark a good fishing spot / trap location |
| `fish_cleaning_table` | a slatted gutting table | process fish into fillets/value-add |
| `aquarium` *(exists)* | display tank | show off prized fish (decor + idle boost) |
| `aquarium_grand` | a tall display tank | showpiece (also in `bug_farming.md` §2.4) |

---

## 6. FISH LIST + REWARDS

Tiered by where/how they're caught and value. "Reward" = rough sell tier + any use.
| id | one-line | habitat / catch | reward tier | use |
|----|----------|-----------------|-------------|-----|
| `minnow` | a tiny silver baitfish | shore, any bait | poor | live bait, cheap sell |
| `sunfish` | a flat bright panfish | lake shallows | poor | cheap food fish |
| `perch` | a striped lake perch | lake, worm/grub | common | food, sell |
| `bluegill` | a small round panfish | pond/lake | poor | food |
| `carp` | a big bottom-feeding carp | lake bottom, dough | common | fertilizer or food |
| `catfish` | a whiskered bottom fish | deep/muddy, night | mid | good food, sells well |
| `bass` | a fighting predator | lake, lures | mid | prized sport fish |
| `pike` | a long toothy predator | deep lake, plug lure | mid | high sell, fights hard |
| `trout` | a speckled cold-water fish | clear/stream water, fly | mid | premium food |
| `eel` | a slippery long fish | reeds, eel_trap | mid | exotic food/alchemy |
| `crayfish` | a small freshwater crustacean | crab_pot, edges | common | cooking ingredient |
| `crab` | a freshwater crab | crab_pot | mid | cooking |
| `golden_carp` | a rare shimmering carp | deep lake, magic_bait | high | high sell; collector |
| `lake_sturgeon` | a huge ancient bottom fish | deepest lake, master rod | high | big sell; roe for `roe_bait`/caviar |
| `glow_fish` | a bioluminescent night fish | night, glowbug_bait | high | glows; alchemy/aquarium prize |
| `legendary_lunker` | a giant fabled lake fish | rare spot + top gear | top | trophy; huge one-time reward |
| `boot_old` | a waterlogged old boot | junk catch | junk | flavor; recycle for scrap |
| `seaweed_clump` | a tangle of pond weed | junk catch | junk | compost ingredient |

Catch byproducts feeding other systems: `roe_bait`/caviar → cooking, `fish_scrap` → fertilizer
(`farming_tools.md` §3), eel/glow_fish → `alchemy_potions.md` ingredients, prized fish → aquarium
display (idle boost, §11.5).

---

## Open questions / follow-ups
- Exact sell prices + rare-catch odds go in the economy proposal, not here.
- Whether fishing has stamina/durability is undecided (game has no stamina, §14 — likely just bite RNG).
- Confirm the SW-lake store stock vs what the player crafts; align with `village_21.md`.
