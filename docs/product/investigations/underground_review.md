# Underground scenes — review & "what else?" proposals

Quick review of the underground scenes + proposals for what to add next (you asked specifically about the
mining camp and the ant colony). Previews live in `tools/_generated/previews/` (flat `scene_<name>.png`).

## Mining camp (`scene_underground_mining_camp.png`) — additions to consider
Already has: rail track in, campfire+spit, second campfire, log seats, tents, mine cart, crates/barrels,
ore sacks, tool rack, ore sluice, powder keg, torches/lantern, miners, custom camp sign.
Proposed adds (mostly mining-flavored, since underground is utilitarian):
- **A bedroll/sleeping mat** by the tents; a **stew pot** on the cooking fire; a **wash basin / water
  barrel**; a **ledger/notice board** (claims); an **ore scale**; a **lantern post** trail back up the rail.
- **A foreman's tent** (bigger) vs worker tents (small) for hierarchy.
- **An ore-cart turntable / siding** where carts queue; **stacked timber** for supports.
- **Pack animal** (mule) someday, or a **hand-crank winch** over a shaft.
- A few **personal touches** (a guitar on a crate, laundry line, playing cards) make it lived-in.
- Equipment for the deeper loop: **smelter/furnace**, **grindstone**, **anvil**, **gold pan + sluice**✓.

## Ant colony (`scene_ant_colony.png`) — your questions, answered + more
- **Eggs in a room?** Done — added an **egg/brood chamber** with `ant_eggs` clutches.
- **A queen ant?** Done — the **`ant_queen`** sits in the deep queen chamber.
- **Other ants?** Worker files on the trails + chamber tenders. Proposed: a **soldier ant** tier (bigger,
  mandibles — already in the encyclopedia as `ant_soldier`/elite), **winged alates** (nuptial flight),
  **aphid "livestock"** the ants farm, **fungus garden** in a chamber (leafcutter vibe).
- **What else in this area?** The big tunnel → **mushroom cavern** is in (centipede + millipede crawl
  there). Proposed: **larvae/pupae** sprites for the brood room, **food stores** (seed/leaf piles),
  **a beetle or springtail** as cave fauna, **a predator** (the centipede already threatens), and
  **dripping water / a small pool** in the mushroom cavern.

## General underground polish
- **Lighting/darkness** (the Terraria-style "dark until lit") is a real-engine/Unity feature — the preview
  can't fake it; flagged for later (block-aura or Unity lights). Undiscovered rock blacked-out = future.
- **Block seams**: blocks are generated transparent+cropped (NOT opaque) and verified for tiling with
  `scene_block_tiling.py`; pick A/B per that sheet. If a block's seams read too loud, reroll its variant.
- **A/B picks**: comparison sheets in `previews/ab_review/`. Most defaults (A) are fine; segments use B.
