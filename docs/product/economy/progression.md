# Progression & Pacing

How the economy is **gated and paced** — *where and when* things become available — so the game ramps fairly
(not insane, not too easy). Balance lives here as **pacing**, justified against *The Art of Game Design* lenses.

- **Geography** (zones, depths, what material is where) → `../architecture_world.md` (§1, §1b). Not copied here.
- **Recipes / costs** → `crafting.md`. **Shops / craft-vs-buy** → `merchants.md`. **Item purpose/bonuses** →
  `stats_and_bonuses.md`. **Decisions** → `DECISIONS.md`.

---

## 1. The gating chain (the one core mechanic)
Progress is a loop where each link unlocks the next:

```
better TOOL tier → break harder ORE → smelt higher BAR → craft better TOOL/GEAR →
survive a harder/deeper ZONE → reach new MATERIAL → (repeat)
```

So three ladders advance together — **tools**, **stations**, **zones** — each gating the next. Nothing is a
time-gate or an XP grind (GDD: power comes from items, not levels); it's all "do you have the gear + material."

## 2. The tier backbone (~5 meaningful tiers)
| Tier | Get it in | Tools/bars | Breaks | Stations unlocked |
|---|---|---|---|---|
| **T1 Wood/Stone** | Village (2,1) | wood → stone | dirt, clay, **sand**, stone, copper, coal | workbench, furnace, stonecutter |
| **T2 Copper/Bronze** | row-2 surface + row-3 entrance | copper/bronze bars | iron ore | loom, cooking_pot |
| **T3 Iron** | row 3–4 mining | iron bars | silver, gold ore | **anvil**, cauldron |
| **T4 Steel** | iron + coal @ forge | steel bars | granite, hard stone | **forge**, keg |
| **T5 Silver→Platinum/Diamond** | row 4 **east cols** | silver/gold/platinum | all (faster) | jeweler; *electronics bench = **bought*** |

*(Row 5's dedicated rare tier returns later — for now T5 is compressed into row-4 east, harder-gated by column.)*

## 3. The three phases (the pacing curve)
| Phase | Where | Tools/gear | Stations | Bug content | Economy |
|---|---|---|---|---|---|
| **Early** | Village + easy rows-2 zones | wood→stone→copper; basic furniture | workbench, furnace, stonecutter | flies, ladybugs, honeybees | first crops + first coins; **General Store** opens |
| **Mid** | medium rows-1 + row-3 mining | iron→steel; first armor sets + a utility outfit; mining begins | anvil, forge, loom, cauldron, keg | wasps, butterflies, intro Ants (col 0) | **Blacksmith & Carpenter** recipes drip in; artisan goods become the money engine |
| **Late** | hard rows-0 + row-4 deep (east) | silver→platinum; top + **bug-derived** gear (chitin, bug-bane); sprinklers/automation | jeweler, **electronics (bought)** | Ant **Queen** mini-boss, Deadly Ants, spiders | full town; deeds/automation as coin sinks |

Each phase is **shippable on its own** and roughly one "chapter" of play; you should always have a visible
next rung (a tool, a zone, a recipe) without everything being available at once.

## 4. Starting-village scope (the concrete hour-1 economy)
The Village (2,1) and its surrounds give **only basic resources** (per `architecture_world.md §1b`):
**wood, fiber, flowers, shallow stone & coal, copper.** So at the start the player can:

- **Craft:** wood/stone/copper tools; basic furniture (chair, table, fence, torch, chest, **bed**); the
  **workbench** (cheap/hand), **furnace** (stone), **stonecutter**; basic walls & stone paths; simple cooked
  food (cooking_pot); plant the first seeds.
- **Buy (General Store):** seeds, basic goods (torches, watering can, sacks/containers), a couple of starter
  recipes.
- **Gated OUT until they travel:** iron+ and anything at the anvil/forge; armor sets, utility outfits,
  accessories; artisan goods (keg/cauldron/loom); sprinklers & automation; the electronics bench; deep ores;
  bug-derived gear; the ant Queen and the hard/eastern zones.

This deliberately small surface is the **tutorial economy** — enough to feel productive and build a little
home, with every richer thing clearly "out there" to pull the player onward.

## 5. Why it's balanced — the lenses (not vibes)
Each pacing choice is reasoned against a named Schell lens:

- **Lens of Flow / the Curve** — each tier is a *small* step up; challenge tracks the player's growing gear,
  so there's no wall and no flat boredom stretch. The tier table is intentionally fine-grained for this.
- **Lens of Pacing & the Lens of Reward** — unlocks are *dripped* (a new zone, station, or recipe every
  session-ish); merchant stock **grows with progress** rather than dumping everything at once.
- **Lens of Economy** — coins **in** (sell crops/bugs/ore/artisan) are balanced against **sinks** (recipes,
  bought stations, deeds); **raw < processed** sell value so the artisan loop is the money engine, not grinding.
- **Lens of Meaningful Choices / Triangularity** — *craft vs buy* is a real trade (materials+time vs coins);
  *which gear path* (combat / farming / bug-catching outfit) is a real choice; going **deeper/east** trades
  higher risk for richer ore.
- **Lens of Need (Maslow) & the Lens of the Toy** — availability is ordered survival→home→comfort→esteem
  (tools & safety first, décor/collection later); and gathering + crafting must be **fun to *do*** moment to
  moment, before the goals even land.

## 6. Pacing targets ("not insane, not too easy")
Rough intent (tune in `crafting.md`'s cost model, not by cutting content):
- **Iron** by a few play-sessions in — a real milestone, not 20 minutes, not 20 hours.
- Each tier is a **noticeable grind but never a wall**; a new tool roughly halves the effort of the gather it
  unlocks.
- **Bosses & hard zones gate on GEAR, not time** — you beat the ant Queen because you prepared, not because
  you waited.
- The player should be able to name their **current goal and next two** at any moment (Lens of Goals).
