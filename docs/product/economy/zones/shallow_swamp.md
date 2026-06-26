# Zone Content Sheet — Shallow Swamp

> **Status:** design only (content brainstorm). Generous-by-design — we prune later, never thin.
> Reuses existing ids where they exist; new ids are `snake_case`.

| | |
|---|---|
| **Zone** | Shallow Swamp |
| **Grid** | 2,3 — wetland east of the river |
| **Tier band** | T2–T3 (HARD-for-its-row, but reachable mid-game) |
| **Theme** | Water / wetland — reeds, mud, bog, standing water |
| **Identity** | The WATER zone: water-walking & water-breathing gear debut here, swamp alchemy
ingredients, fishing-adjacent gathering, leech/venom reagents |
| **Existing swamp flora** | reeds, cattail, duckweed, pondweed, water_lily, marsh_plant |
| **Hazards** | murky water (drown without `water_breath`), leech latch (DoT, `hazard_resist` mitigates),
sucking mud (move-slow without `water_walk`/`terrain_immunity`), swamp gas pockets |

The Shallow Swamp is the gate to **traversal power**: you come here for the ingredients and the
two new movement verbs (`water_walk`, `water_breath`) that this zone both *demands* and *sells the
tools for*. Everything keys off "wet": the bugs skim/dive/lurk, the gatherables are bog/reed/lily,
and the crafts let you finally cross the deep water that walls off later islands.

---

## 1. Species & drops

World-guide species for this zone: **damselflies, pond skaters, whirligig beetles, leeches**. Plus
two extra wetland species to round the food web and give more drops to craft with.

| Species (id) | Tier | Behavior | Catch / combat notes | Primary drop (id) | Secondary drop |
|---|---|---|---|---|---|
| `damselfly` | T2 | Skims low over reeds & open water; darts in short hops, perches on cattail tips. Skittish — flees fast, rewards `calm_radius` / a wide `catch_arc`. | Aerial catch; high `rare_bug_luck` payoff (an azure morph is the rare variant). Non-hostile. | `damselfly_wing` (iridescent membrane) | `dead_damselfly` |
| `pond_skater` | T2 | Glides on the **surface tension** of open water; rows in bursts, scatters from shadow. Only catchable if you can reach the water (net from a reed bank, or stand on it with `water_walk`). | Surface catch; teaches the water-walk loop. Non-hostile. | `skater_oil` (hydrophobic leg-wax) | `dead_skater` |
| `whirligig_beetle` | T2–T3 | Spins in tight clusters on the surface, dives when threatened (vanishes underwater for a beat). Comes in swarms — high `catch_cap` is rewarded. | Surface/dive catch; cluster = many per swing. Non-hostile but evasive. | `whirligig_shell` (split-eye carapace) | `dead_beetle` (reuses existing) |
| `leech` | T2–T3 | Lurks in murky shallows; **latches** onto the player on contact for a slow HP drain (DoT) until shaken/killed. The zone's "hazard bug." | Hostile-passive: damages on contact, not a chaser. `hazard_resist` + waders reduce latch. Kill or pry off. | `leech_extract` (anticoagulant ichor) | `dead_leech` |
| `marsh_mosquito` | T2 | Drifts in clouds at dusk near still water; weak individual sting, annoying in numbers. Drawn to the player (`lure` behavior). Extra species — a swarmy nuisance + reagent source. | Cloud catch (wide arc shines); minor sting damage. `sting_immunity` negates. | `mosquito_proboscis` | `dead_mosquito` |
| `bog_centipede` | T3 | A wetland centipede variant that hunts along reed roots & mud banks — the zone's apex arthropod, hits harder than its dryland cousin. Extra species — the T3 fight. | Hostile chaser; real combat. Rewards `defense` + `knockback`. | `centipede_parts` (reuses existing) | `dead_centipede` (reuses existing) |

**Drop → use at a glance**

- `leech_extract` → swamp alchemy: water-breath potion, anticoagulant salve (regen), the wader set
  treatment. The signature reagent.
- `damselfly_wing` → light, iridescent — gossamer cloth, the lily-glide trinket, decorative dye.
- `skater_oil` → **hydrophobic** coating: the water-walk boots' key reagent, waterproofing treatment.
- `whirligig_shell` → light carapace plating for the wader armor; split-eye lens → a night/clarity trinket.
- `mosquito_proboscis` → cheap venom-adjacent reagent for weak poison coatings / bait.
- `centipede_parts` (existing) → T3 weapon edge & the apex-bug bounty.

---

## 2. New ingredients / materials (swamp gatherables)

Gathered from the terrain & flora (no station), then fed into the crafts in §3. Generous list — prune later.

| Id | Source (find@shallow_swamp) | Use |
|---|---|---|
| `peat` | Cut from bog/mud tiles with a shovel (renews slowly). | Fuel (burns like coal-lite at furnace), soil amendment (`water_retention_pct`), brick-adjacent `peat_block` building mat. |
| `swamp_gas` | Captured from gas pockets (bubbling tiles) with a jar/bottle. | Volatile reagent: lantern fuel, a `light_radius` consumable, mild offensive gas bomb. |
| `bog_iron` | Reddish nodules dredged from shallow water/mud (a soft, swamp-native **iron source** — flavor route to `iron_bar` without a deep mine). | Smelt → `iron_bar` (existing) at furnace; ties the swamp into the T3 metal ladder. |
| `reed_stalk` | Harvested from existing `reeds` occupant. | Loom fiber substitute → `reed_fiber`; thatch building mat; the snorkel/breathing-tube craft. |
| `reed_fiber` | Process `reed_stalk` (workbench/loom). | Coarse cordage & matting — the wader/poncho weaves, baskets, fish-trap. |
| `cattail_fluff` | Gathered from `cattail` heads in season. | Buoyant stuffing → the **float/cork-substitute** for water-walk soles & a life-vest; soft padding. |
| `lily_pad` | Harvested from `water_lily`. | The water-walk **stepping** reagent (large buoyant pad); rendered into `lily_extract`. |
| `lily_extract` | Cauldron-process `lily_pad` + water_lily bloom. | Calming/clarity alchemy base (`calm_radius`, anti-leech salve); a soothing dye. |
| `duckweed_paste` | Cauldron-process `duckweed`. | Green dye + a `crop_growth_pct` fertilizer additive (the swamp's compost booster). |
| `marsh_clay` | Dug from riverbank mud (a wetter, finer `clay`). | Higher-grade clay for waterproof pottery/jars; smelts to a denser brick (`marsh_brick`). |
| `tannin` | Leached from peat + reed/oak bark (cauldron). | **Tanning agent** — turns hide/reed into water-resistant leather for the waders; brown dye. |
| `frog_spawn` | Skimmed from still water (seasonal, sparse). | Rare alchemy reagent (a `dodge_chance` / agility brew); bait. Flavor rarity drop. |

New raw building mats this introduces: `peat_block`, `marsh_brick`, `thatch` (from `reed_stalk`) — cheap
T2 structure pieces that read as "swamp shack."

---

## 3. Recipes debuting here

Each: output · station · inputs (+counts) · unlock · stat/bonus · tier. Costs sanity-checked against the
tier-point model (wood/fiber/stone/flower=1; plank/coal/brick=2; copper_bar/thread=3; bronze/cloth/beeswax/
chitin=4; iron_bar/silk/honey=6; venom/gem-minor=10).

### Traversal (the headline — water_walk & water_breath debut here)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `marsh_waders` (boots) | workbench | `reed_fiber` ×6, `skater_oil` ×3, `tannin` ×2, `cattail_fluff` ×4 | buy@swamp vendor | **`water_walk`** + `terrain_immunity` (no mud-slow) + tiny `defense` | T2 |
| `skater_boots` (boots, light variant) | loom/workbench | `skater_oil` ×4, `cloth` ×2, `cattail_fluff` ×3 | buy@swamp vendor | **`water_walk`** + `move_speed_pct +6` (skim faster) | T2–T3 |
| `reed_snorkel` (head accessory) | workbench | `reed_stalk` ×4, `reed_fiber` ×3, `swamp_gas` ×1 (sealed float) | auto (once you have reeds) | **`water_breath`** (short timer underwater) | T2 |
| `diving_bell_helm` (head) | anvil | `iron_bar` ×2 (from `bog_iron`), `glass` ×2, `whirligig_shell` ×3, `tannin` ×2 | buy@swamp vendor | **`water_breath`** (sustained) + `light_radius` + `defense` | T3 |
| `lily_glider` (accessory) | jeweler/workbench | `lily_pad` ×6, `damselfly_wing` ×4, `reed_fiber` ×3 | find (recipe scroll in swamp) | `water_walk` (brief) + `fall_resist` — pad-hop across gaps | T3 |

### Swamp alchemy (cauldron) — leech/herb potions

| Output (id) | Station | Inputs | Unlock | Effect (timed unless noted) | Tier |
|---|---|---|---|---|---|
| `water_breathing_potion` | cauldron | `leech_extract` ×2, `lily_extract` ×1, `pondweed` ×3 | buy@swamp vendor | timed `water_breath` (the consumable route, before you craft the helm) | T2 |
| `anticoagulant_salve` | cauldron | `leech_extract` ×3, `yarrow` ×2 (existing), `lily_extract` ×1 | auto | `hp_regen` + leech-latch immunity window | T2–T3 |
| `marsh_antidote` | cauldron | `lily_extract` ×2, `sage` ×2 (existing), `mint` ×1 (existing) | buy@swamp vendor | cures swamp poison / `hazard_resist` burst | T2 |
| `gas_bomb` | cauldron | `swamp_gas` ×2, `clay` ×1, `mosquito_proboscis` ×2 | find/buy | thrown AoE: bug `calm`/repel cloud (utility, not pure dmg) | T3 |
| `nimble_brew` | cauldron | `frog_spawn` ×1, `skater_oil` ×2, `mint` ×1 | find (rare) | timed `dodge_chance` + `move_speed_pct` | T3 |
| `bog_lantern_oil` | cauldron | `swamp_gas` ×3, `peat` ×2 | auto | refills a lantern — `light_radius` source (swamp is dim) | T2 |

### Reed / cloth & building crafts

| Output (id) | Station | Inputs | Unlock | Bonus / use | Tier |
|---|---|---|---|---|---|
| `reed_fiber` | loom/workbench | `reed_stalk` ×3 | auto | the swamp's fiber → cordage/matting (substitutes `fiber`/`thread` for coarse weaves) | T2 |
| `reed_mat` (décor/floor) | loom | `reed_fiber` ×4 | auto | walkable thatch floor; cheap swamp décor | T2 |
| `woven_basket` (storage) | loom | `reed_fiber` ×6, `cattail_fluff` ×2 | auto | a light container (storage slots) | T2 |
| `fish_trap` (placeable) | workbench | `reed_fiber` ×5, `reed_stalk` ×3 | buy@swamp vendor | **fishing-adjacent**: passive catch of fish/skaters when placed in water | T2–T3 |
| `thatch` (building mat) | sawmill/workbench | `reed_stalk` ×4 | auto | swamp-shack roofing/walls | T1–T2 |
| `peat_block` (building mat) | stonecutter | `peat` ×3 | auto | dark earthen block; cheap structure + fuel store | T2 |
| `marsh_brick` (building mat) | furnace | `marsh_clay` ×2, `peat` ×1 (fuel) | auto | denser waterproof brick (riverbank construction) | T2 |
| `tanned_hide` | dye_vat/cauldron | hide/`reed_fiber` ×3, `tannin` ×2 | auto | water-resistant leather — input to the wader set | T2 |
| `swamp_dye` (set: brown/green/azure) | dye_vat | `duckweed_paste` / `tannin` / `damselfly_wing` | auto | wetland color palette for outfits | T2 |

### Weapons / tools (T3 — ties combat to the apex bug)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `harpoon_spear` | anvil | `iron_bar` ×2 (bog_iron route), `wood` ×2, `reed_fiber` ×2 | buy@swamp vendor | long reach `spear` tuned vs water bugs; doubles as fishing | T3 |
| `centi_edge_dirk` | forge | `iron_bar` ×1, `centipede_parts` ×3, `leech_extract` ×1 | find (apex-bug drop recipe) | fast `attack_speed_pct` dagger, `damage_pct` vs arthropods, light `venom` | T3 |
| `dredge_shovel` | anvil | `iron_bar` ×1, `wood` ×2 | auto | digs `peat`/`bog_iron`/`marsh_clay` faster (mud-dig speed) | T2–T3 |

---

## 4. Signature BONUS gear — the **Wader / Marshwalker set** (T2→T3)

A swamp/wader-themed true outfit: the zone's identity piece. Low-to-moderate `defense`, with **traversal**
as the headline. Three core pieces (+ optional gloves), paper-doll overlay so it reads as "swamp rambler."

| Piece (id) | Slot | Made @ | Inputs | Per-piece bonuses | Tier |
|---|---|---|---|---|---|
| `marshwalker_hood` | head | workbench | `reed_fiber` ×4, `tanned_hide` ×2, `whirligig_shell` ×1 | `defense +1`, `hazard_resist +1` (gas/leech), small `light_radius` | T2 |
| `marshwalker_vest` | body | loom/workbench | `tanned_hide` ×4, `reed_fiber` ×4, `cattail_fluff` ×3 | `defense +2`, `water_retention_pct +10` (stay dry/warm), `hazard_resist +1` | T2 |
| `marshwalker_waders` | legs/feet | workbench | `tanned_hide` ×4, `skater_oil` ×3, `reed_fiber` ×3 | `defense +1`, **`water_walk`**, `terrain_immunity` (no mud-slow) | T2–T3 |
| `marshwalker_gloves` *(optional 4th)* | hands | loom | `reed_fiber` ×3, `leech_extract` ×1 | `defense +1`, leech-pry speed / minor `thorns` | T3 |

**Unlock:** waders & vest `buy@swamp vendor` (recipes); hood `auto`; the gloves `find` (rare swamp scroll).

### Set bonus — "Marshwalker" (3-piece, escalating)

- **2-piece:** `water_walk` is **sustained** (no timer flicker) + `terrain_immunity` everywhere.
- **3-piece (full):** add **`water_breath`** (the set becomes a full wetland traversal rig — cross deep
  water and stay under) + `hazard_resist +2` (leeches & swamp gas barely touch you) + `dodge_chance +5`.
- **4-piece (with gloves):** leeches **cannot latch** at all (sting/latch immunity) + `thorns` vs water bugs.

Design intent: the **set is the key that unwalls the rest of the map's water.** A player can buy a single
water-walk boot early, but the full Marshwalker set is the *clean, defensive* way to live in the swamp and
push into deep water / islands. Defense stays modest so it's a traversal outfit, not best-in-slot armor —
swap to iron plate for a real fight (GDD: one outfit at a time = the build choice).

### Signature accessories (jeweler / drops)

| Accessory (id) | Source | Bonus |
|---|---|---|
| `leech_charm` | jeweler (`leech_extract` + gem-minor) | `hp_regen` (slow leech-anticoagulant heal) |
| `whirligig_lens` | jeweler (`whirligig_shell` split-eye + glass) | `night_vision` + small `catch_arc` (clarity on water) |
| `damsel_pin` | find / jeweler (`damselfly_wing` ×4) | `rare_bug_luck` + tiny `move_speed_pct` |
| `frog_leg_charm` | drop/quest (`frog_spawn`-line) | `water_walk` (brief) + `fall_resist` — the cheap traversal trinket |

---

## 5. Shop / NPC — **"Old Mirk," the Bog Fisher / Herbalist**

A wetland vendor stationed on a reed dock at the swamp's edge (occupant w/ `interaction_type:"npc"`,
`npc{role:"swamp_vendor"}`). Half fisher (traversal & catch gear), half herbalist (swamp alchemy). Stock
**grows with progress** (Lens of Pacing): the deep-water gear only appears once you own the basic waders.

### Sells — goods

| Item | Rough cost | Notes |
|---|---|---|
| `fishing_rod` (existing concept) | low | gates the fishing-adjacent loop |
| `bait` (from `mosquito_proboscis`/`frog_spawn`) | low | for rod & `fish_trap` |
| `water_breathing_potion` | mid | the consumable traversal route (before the helm) |
| `marsh_antidote`, `bog_lantern_oil` | low–mid | swamp survival basics |
| `lily_extract`, `tannin` | mid | alchemy/leather reagents (skip the gather) |
| `reed_seedling` / swamp décor | low | reeds/cattail to plant; a buy-only lily-pond décor |

### Sells — recipes (the coin sink)

`marsh_waders` · `skater_boots` · `diving_bell_helm` · `marshwalker_vest` · `marshwalker_waders` ·
`water_breathing_potion` · `marsh_antidote` · `harpoon_spear` · `fish_trap` · `gas_bomb`. (Gated: deep-water
recipes — `diving_bell_helm`, `marshwalker_waders` — only stock once you own `marsh_waders`.)

### Buys — coin sources

Pays **high** for swamp drops & gatherables (a reason to over-harvest the wetland): `leech_extract`,
`damselfly_wing`, `whirligig_shell`, `skater_oil`, `frog_spawn`, `bog_iron`, `peat`, and caught fish.

### Flavor / tips

Intro hook: warns you the deep water drowns the unprepared, points you at the waders, mentions the apex
`bog_centipede` haunting the root-banks. Random tips seed the leech/gas hazards and the lily-pad glide trick.

---

## 6. "New toys" hook

The Shallow Swamp is where the game **hands you the water**: it's the first place you *can't* just walk
through, and the cure — `water_walk` boots, the `reed_snorkel`/`diving_bell_helm`, and the full **Marshwalker
wader set** — turns deep water from a wall into a highway, opening the river islands and later wet zones.
It debuts a whole **swamp-alchemy** branch (leech-extract potions, lily/duckweed reagents, the cauldron going
full bog-witch) plus a **fishing-adjacent** gathering loop (rod, `fish_trap`, harpoon) that finally rewards
standing on the water you just learned to cross. And it threads the swamp back into the metal ladder via
`bog_iron`, so even the T3 smithing has a wetland flavor.

---

## New-id summary

```
materials:
  peat, swamp_gas, bog_iron, reed_stalk, reed_fiber, cattail_fluff, lily_pad, lily_extract,
  duckweed_paste, marsh_clay, tannin, frog_spawn, peat_block, marsh_brick, thatch, tanned_hide,
  swamp_dye

species: (id -> primary drop)
  damselfly -> damselfly_wing
  pond_skater -> skater_oil
  whirligig_beetle -> whirligig_shell
  leech -> leech_extract
  marsh_mosquito -> mosquito_proboscis
  bog_centipede -> centipede_parts        # reuses existing drop id
  # secondary/carcass drops: dead_damselfly, dead_skater, dead_leech, dead_mosquito
  #   (dead_beetle, dead_centipede, centipede_parts reuse existing ids)

items:
  marsh_waders          # boots — water_walk + terrain_immunity (T2)
  skater_boots          # boots — water_walk + move_speed (T2-3)
  reed_snorkel          # head accessory — water_breath, short (T2)
  diving_bell_helm      # head — sustained water_breath + light_radius + defense (T3)
  lily_glider           # accessory — brief water_walk + fall_resist (T3)
  water_breathing_potion# cauldron — timed water_breath (T2)
  anticoagulant_salve   # cauldron — hp_regen + leech immunity (T2-3)
  marsh_antidote        # cauldron — hazard_resist / cure poison (T2)
  gas_bomb              # cauldron — AoE calm/repel cloud (T3)
  nimble_brew           # cauldron — timed dodge_chance + move_speed (T3)
  bog_lantern_oil       # cauldron — light_radius refill (T2)
  reed_mat              # loom — walkable décor floor (T2)
  woven_basket          # loom — light storage container (T2)
  fish_trap             # placeable — passive water catch (T2-3)
  dredge_shovel         # anvil — faster mud/bog digging (T2-3)
  harpoon_spear         # anvil — long-reach spear / fishing (T3)
  centi_edge_dirk       # forge — fast dagger, dmg vs arthropods, venom (T3)
  marshwalker_hood      # head armor — set "marshwalker" (T2)
  marshwalker_vest      # body armor — set "marshwalker" (T2)
  marshwalker_waders    # legs/feet armor — water_walk, set "marshwalker" (T2-3)
  marshwalker_gloves    # hands armor — set "marshwalker", latch immunity (T3)
  leech_charm           # accessory — hp_regen
  whirligig_lens        # accessory — night_vision + catch_arc
  damsel_pin            # accessory — rare_bug_luck + move_speed
  frog_leg_charm        # accessory — brief water_walk + fall_resist
  # set id: marshwalker (2/3/4-piece bonuses)
```
