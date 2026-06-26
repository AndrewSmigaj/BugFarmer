# Zone Content Sheet — Starting Village (`village_21`) — FINALIZED (zone-accurate)

**Tier:** T1 (wood / stone / copper) · grassland with a pond & docks · EASY · tutorial home hub.

Finalized against the **real `village_21_B` zone data** (the tuned **6-species** ecology you balanced) + the
review decisions (`../DECISIONS.md` D18–D20). The village is the richly-built home town: a meadow with an
orchard (apple/plum/cherry/orange), a pond/river with **docks & boats**, a **garden plot**, and a town core
full of shops, stations, and furniture.

> **Key model (D18):** bugs drop **only `dead_<bug>`** when killed. You take dead bugs to the **Bug Extractor**
> (a clean in-town building with crates + equipment) which **processes them into materials** (chitin, silk,
> leather…) and feeds **cooking**. No messy per-bug ground drops. (This replaces the old `ladybug_shell`/
> `pill_chitin`/`bug-leather station` ideas.)

---

## Species & drops (actual spawns — `village_21_B`, 6 species)
| Species (real id) | Role | Drop |
|---|---|---|
| `fly` (`fly_common`) ✅ | drifting clouds — the catch-a-hundred tutorial bug | `dead_fly` ✅ |
| `butterfly` (`butterfly_meadow`) ✅ | pretty fliers on the `milkweed` host plant | `dead_butterfly` ✅ |
| `wasp` (`wasp_common`) ✅ | mild threat, anchored to `wasp_nest` ✅ | `dead_wasp` ✅ |
| `centipede` (`centipede_garden`) ✅ | the first real (mild) combat bug | `dead_centipede` ✅ |
| `millipede` (`millipede`) ✅ | slow detritivore (the leaf-litter niche) | `dead_millipede` ✅ |
| `carrion beetle` (`beetle_carrion`) ✅ | decomposer — works the rot/compost | `dead_beetle` ✅ |

*(No pill bugs / ants / snails / aphids — they belong to later/forested zones. So `honeydew`, `formic_*`, etc.
are NOT village materials.) Every kill drops only `dead_<bug>`; take them to the **Bug Extractor** → chitin /
silk / leather / cooking inputs.*

## Materials available here (from the real `village_21_B`)
- **Flora (forage):** wood + **fruit** (`tree_oak`/`tree_pine` + `tree_apple`/`tree_plum`/`tree_cherry`/
  `tree_orange` → apple/plum/cherry/orange); fiber (`bush`/`tall_grass`/`reeds`/`fern`/`clover`);
  **`milkweed`** (the butterfly host plant); **berries** (`wild_berry_bush`); flowers (`flower_red`/
  `flower_blue`/`flower_yellow`/`flower_wild`/`flower_aster`); `poppy`; `lavender`; mushrooms
  (`mushroom_cluster`/`mushroom_puffball`).
- **Mineable (basic surface — copper/tin/coal + a little iron per progression):** stone, `clay`, `sand`,
  + small `crystal`/`geode`. *(Ore deposits are densely placed in the `village_21` build; confirm they're in
  the B build before relying on volume.)*
- **Crops (garden_plot):** a nice collection of **garden vegetables** — `tomato`, `corn`, carrot, cabbage,
  eggplant, pumpkin. **Wheat PULLED** (you buy it **up north** — fast-growing, good money, a travel gate;
  *zone-authoring TODO: remove `plant_wheat` from `village_21_B`*). **No cotton yet.**
- **Bug materials (via the Bug Extractor):** chitin / silk / leather / etc. from the 6 species' `dead_*` bugs.
- **Crafted intermediates:** `copper_bar` etc. (furnace), `thread`+`cloth` (loom), `leather` (Bug Extractor),
  `brick` (stonecutter), compost → `fertilizer` (compost bin).

## Stations (already placed in the zone, + the two we add)
**In `village_21` today:** `workbench` · `furnace` · `anvil` · `sawmill` (the **wood-saw / woodcutting**
station) · `cauldron` · `forge` · `keg`. *(Cauldron/forge/keg are placed but their advanced content —
potions, steel, artisan — unlocks later; potions wait for the alchemy pass.)*
**Add:** the **Bug Extractor** (dead bugs → materials + cooking) and a **compost bin** (basic → a bigger one
that holds more).

## Tools & gear
- **Net:** you **start with one** in your inventory; also **sold** at the store. (Bigger nets later.)
- **Base tools** (all basic recipes **auto-unlock**): pickaxe / axe / shovel / hoe / scythe (wood → stone →
  copper), `watering_can` (small), **`magnifying_glass`** (starter — inspect bugs).
- **`gardener_gloves`**, **`straw_hat`** (sun hat) — craftable + sold at the store.
- **Fishing poles** — from the Fisherman (basic fishing is here).
- Woodcutting uses the **sawmill** + saw (larger trees later need the proper saw).

## Storage
Start with a **small sack** → upgrade to a **large basket** → then a **backpack** (the storage slot).

## Armour
- **Base sets only:** **leather** (via the **Bug Extractor**) · **padded/cloth** (loom) · **copper** (anvil).
- **No Forager's Kit** — the first bonus set lands in a later zone.

## Weapons
Basic weapons (`sword_wood`→`sword_copper`, `spear_wood`→`spear_copper`) — recipes **auto-unlock**; also
**sold at the store**, alongside a few **rare/expensive teases** (a peek at high-end gear from the start).

## Consumables
- **`calm_spray`** ✅ — keep (made from `lavender`/flowers or bought). *(Bee-area calming/smoke is to the west.)*
- **Cut:** `rot_bait`, `sweet_bait`, `petal_tincture`, `bug_balm`, `village_soap` (no game reason).
- **Health potions:** wait for the **alchemy pass** (backlog) — not in the village yet.

## Food
- Offer **`forager_stew`** as the one starter meal; the player cooks the rest freely.
- **Cooking recipes are a separate system → backlog** (D19).

## Décor & furniture (everything already in the zone)
The village is richly furnished — `bed_basic`/`bed_fancy`, sofas, dressers, tables, chairs, benches,
bookshelves, `fountain`, `statue_founder`, `lamp_post`, `potted_plant`, `aquarium`, `specimen_shelf`,
`bug_terrarium`, rugs, `mirror_standing`, `grandfather_clock`, signs, etc.
- **Most are buildable.** **Fancy pieces that need dyes / advanced materials are NOT buildable yet**
  (`bed_fancy`, `sofa_fancy`, `dresser_fancy`, `counter_fancy`, `dining_table_fancy`…) — buy or unlock later.
- **Structure:** walls (`wall_wood`/`wall_stone`/`wall_marble`), fences (`fence_picket`/`fence_wood`/
  `fence_iron`), gates, `door_square`. **No roofs** (overhead view).
- (Décor home-plot **bonuses** are the separate idle system → backlog.)

## Dyes
`red_dye` · `yellow_dye` · `blue_dye` · `green_dye` (from local flowers/poppy) — sold by the appropriate vendor.

## Farming
- **Garden crops:** tomato, corn (+ carrot/cabbage/eggplant/pumpkin seeds). Garden-plot tiles already in zone.
- **Fertilizer** from the compost bin.
- **Sprinklers:** **basic + advanced** — the better ones **cost-gated** (out of reach until you've played a while).

## Fishing
Basic fishing lives here (the pond/river, `bridge_wood`, `mooring_post`, `fish_crate`, `fishing_net`,
`fishing_pole`, `boat`, docks). The **Fisherman / boatperson** sells poles + a boat.

## NPCs (5)
1. **Merchant** — General Store: general goods, seeds, supplies, decorations, recipes, basic equipment (the
   net); **randomized/rotating stock** + a few **rare/expensive teases**.
2. **Fisherman / boatperson** — sells **fishing poles** + a **boat** (expensive). The fishing NPC.
3. **Blacksmith** — sells **some metal**; the real **mining equipment is at the Mining Camp**, not here.
4. **Carpenter** — furniture / wood / building recipes.
5. **Mayor** — sells nothing but **land deeds** (a separate system → backlog).

## Hook
A safe, lived-in home town: chase fly clouds and butterflies, knock back the odd wasp or centipede, **take your
catch to the Bug Extractor** to turn dead bugs into chitin/silk/leather (and dinner), fish off the docks, work
a garden plot, mine a little surface copper/tin, and **build out your house and town** from a deep furniture
set — while the merchant's rare teases and the expensive boat hint at how big it all gets.
