# Brainstorm — Mining Caves decorations

Props and small decor that **dress** the **Mining Caves** zone: the mining-camp gear, the man-made
infrastructure, and the natural cave formations that aren't ore, flora, or full landmarks. These are the
**parts** that compose the landmarks (see landmarks doc) and the **scatter** that makes a tunnel feel lived-in.

Per `brainstorm_items.md`, **placed decorations grant passive farm bonuses** (diminishing returns + cap), so
many cave props double as **farm/base decor** with a rugged "mine/industrial" or "glowing grotto" theme.
Mining gear already exists in `brainstorm_items` (`mine_rail`✓, `mine_cart`✓, `mine_support`✓, `pickaxe`✓,
`lantern`✓, `tnt`✓, etc.) — reuse those ids; new cave-specific decor is proposed below.

Legend: **Light** = light source (evening/glow bonus) · **FarmDecor** = usable as base/farm decor · **Func** = functional/interactive.

---

## 1. Lighting (the cave's whole mood — most important decor family)
- `mine_torch` — pitch torch in a wall bracket, warm flicker; the baseline cave light. Light, FarmDecor. common.
- `miners_lantern` — hanging oil lantern on a hook/post (reuse `lantern`✓). Light, FarmDecor, Func(portable). common.
- `headlamp_helmet` — a miner's helmet with carbide lamp on a peg; small prop. FarmDecor. uncommon.
- `candle_stub` — a guttering candle on a rock ledge; tiny intimate light. Light. common.
- `brazier_cave` — an iron fire-basket on legs lighting a camp (cf. brazier in items). Light, FarmDecor. uncommon.
- `glowstone_lamp` — a lamp set with a glow-crystal instead of flame (safe near gas pockets). Light, FarmDecor. uncommon.
- `firefly_jar` / `glowworm_jar` — jarred glow bugs (bugs doc) as a soft cool light. Light, FarmDecor. uncommon.
- `crystal_lamp` — a polished glowing crystal mounted as a fixture; the "fancy" cave light. Light, FarmDecor. rare.
- `string_lights_cave` — a strung line of small lamps along a rail tunnel. Light, FarmDecor. uncommon.

## 2. Mining tools & equipment (the working gear — leaned, racked, scattered)
- `pickaxe_leaning` — a pickaxe propped against a wall/rock (reuse `pickaxe`✓ as decor pose). FarmDecor. common.
- `shovel_leaning` — a shovel stood in a rubble pile (reuse `shovel`✓). FarmDecor. common.
- `tool_rack_mining` — a wall rack of picks, hammers, chisels, drills. FarmDecor, Func(storage flavor). uncommon.
- `pick_and_chisel_set` — a pick + chisel + hammer laid on a rock as if mid-job. FarmDecor. common.
- `gold_pan_set` — a pan + sluice bits by a stream (cf. `sluice`✓). FarmDecor, Func(panning). uncommon.
- `wheelbarrow_ore` — a wheelbarrow heaped with rock/ore. FarmDecor. uncommon.
- `winch_drum` — a hand-cranked winch with rope, for shafts/buckets. Func. uncommon.
- `dynamite_crate` — a crate stenciled with a warning, sticks of `tnt`✓ inside. Func(hazard/blasting), FarmDecor(novelty). uncommon.
- `survey_tripod` — a surveyor's tripod + claim stakes; "this is being mapped." FarmDecor. rare.

## 3. Storage, sacks & containers (the haul)
- `ore_sack` — a bulging burlap sack of ore lumps. FarmDecor, common.
- `ore_sack_pile` — several sacks stacked/slumped together. FarmDecor, common.
- `ore_pile_loose` — a loose heap of mined rock/ore chunks on the floor. common.
- `crate_mining` — a sturdy wooden crate (supplies, stenciled). FarmDecor, Func(storage). common.
- `barrel_cave` — a wooden barrel (water/oil/blasting powder). FarmDecor. common.
- `ore_bin` — a slatted bin/hopper holding sorted ore by a rail. Func. uncommon.
- `gem_lockbox` — a small iron strongbox for the good finds. Func(storage), FarmDecor. uncommon.
- `supply_shelf` — a plank shelf of tins, jars, fuses, a lamp. FarmDecor. uncommon.

## 4. Structure & infrastructure (the man-made bones)
- `mine_support` ✓ *(existing)* — vertical timber + crossbeam holding up the roof; lines straight tunnels. common.
- `support_arch_double` — a heavier doubled timber arch for big halls. uncommon.
- `mine_rail` ✓ *(existing)* — narrow-gauge track down a tunnel center. common.
- `rail_switch` — a points/switch where rail splits. uncommon.
- `mine_cart` ✓ *(existing)* — ore cart on the rail (full/empty/tipped variants as decor). common.
- `cart_tipped` — a derailed/overturned cart spilling ore; abandoned-feel. FarmDecor. uncommon.
- `ladder_wood` — a rough wooden ladder up a shaft. Func. common.
- `plank_bridge_cave` — planks over a chasm/stream. Func. uncommon.
- `ore_chute` — a sloped wooden chute funneling rock down to a bin. Func. uncommon.
- `signpost_mine` — a hand-painted sign ("DEEP MINE →", "DANGER", depth markers). FarmDecor, Func(wayfinding). common.
- `claim_notice` — a paper claim/notice nailed to a timber. flavor. uncommon.

## 5. Camp & comfort (the human warmth in the dark)
The mining-camp dressing (matches the zone's Miner's Camp + abandoned-camp landmark).
- `campfire_cave` — a ring-of-stones fire, the camp's heart. Light, FarmDecor, Func(cook). common.
- `stew_pot` — a pot/kettle on a tripod over the fire, steaming. Func(cook), FarmDecor. uncommon.
- `bedroll` — a rolled or laid-out bedroll on stone. FarmDecor. common.
- `camp_stool` / `log_seat` — a stool or a sawn log to sit on by the fire. FarmDecor. common.
- `cup_and_plate` — a tin cup + plate left by the fire; lived-in detail. flavor. common.
- `lantern_post_camp` — a post-mounted lantern marking the camp edge. Light, FarmDecor. uncommon.
- `journal_open` — an open miner's journal on a crate; lore prop. flavor. rare.
- `washtub` — a tin washtub of grey water. FarmDecor. uncommon.

## 6. Natural cave formations (the geology dressing — non-ore)
Stalactites/stalagmites etc. — note: per `caves.md §2` the *big rocky columns* are done as
`stone_block` clumps, but these are the small **decor-scale** formations scattered as flavor.
- `stalagmite_small` — a stubby floor cone (single/cluster). common.
- `stalactite_small` — ceiling-hung drip-cone (single/cluster). common.
- `stalactite_curtain` — a wavy "drapery" flowstone sheet on a wall. uncommon.
- `flowstone_cascade` — a frozen-waterfall mineral sheet. uncommon.
- `cave_column` — a stalactite + stalagmite joined floor-to-ceiling. uncommon.
- `crystal_cluster_small` — a small faceted crystal clump (mineral family); decor-scale gem dressing. FarmDecor. common.
- `crystal_cluster_glow` — a small glowing crystal clump. Light, FarmDecor. uncommon.
- `geode_cracked` — a fist-sized geode split open showing crystal lining. FarmDecor. uncommon.
- `rubble_pile` — a heap of broken rock (post-mining or rockfall). common.
- `boulder_cave` — a large fallen boulder breaking up the floor. common.
- `dripstone_basin` — a small rimstone basin holding a puddle. uncommon.
- `cave_pearls` — a cluster of smooth cave-pearls in a basin; rare oddity. rare.

## 7. Bone, fossil & macabre (the deep-time flavor)
- `bone_pile_small` — scattered old bones / a skull on the floor (zone doc). FarmDecor(spooky). common.
- `skull_on_rock` — a single skull as a grim marker. FarmDecor. uncommon.
- `fossil_chunk` — an embedded fossil in a loose rock (ammonite/trilobite). FarmDecor, collectible. uncommon.
- `amber_chunk` — a glob of amber with a bug trapped inside (ties to the BUG theme!). FarmDecor, Func(collectible). rare.
- `cobweb_corner` — dusty webbing in a tunnel corner (spider sign, bugs doc). flavor. common.

---

## Notes
- **Farm-decor crossovers (the bonus mechanic):** glow lights (`crystal_lamp`, `glowstone_lamp`,
  `firefly_jar`, `crystal_cluster_glow`), the rugged industrial set (`mine_cart`, `ore_sack`,
  `mine_support`, `tool_rack_mining`), and oddities (`amber_chunk`, `geode_cracked`, `fossil_chunk`) let a
  player theme a base/home as a "miner's den" or "glowing grotto" with passive bonuses.
- **Composition:** lighting + supports + rail/cart + sacks/crates compose the `rail_tunnel` and camp
  landmarks; formations (stalactites, rubble, boulders, crystal clusters) are the scatter that fills the
  dark between veins so caverns aren't empty bowls (`caves.md §2`).
- **Light is the scarce resource** — most props are dark; the light family is what the player places to push
  back the dark, which makes those bonuses feel earned.
- **Bug-theme tie-in:** `amber_chunk` (trapped ancient bug), `cobweb_corner`, `firefly_jar`/`glowworm_jar`
  keep the cave anchored to the game's bug identity even underground.

## Open questions
- Which formations are single sprites vs. `stone_block`-clump assemblies (per the caves guide)?
- Do `mine_cart`/`ore_chute`/`winch` get a functional automation role (cf. `brainstorm_items` §11.6 power /
  conveyor route), or stay pure decor for now?
- Light radius/strength per source — does the game model lighting yet, or is glow purely cosmetic so far?
