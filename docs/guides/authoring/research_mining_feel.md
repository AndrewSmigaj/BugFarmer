# Research: what makes mining/ore terrain feel good in 2D games (2026-07)

Digest of a web-research sweep on the FEEL layer of mining — the invitation, the
reward rhythm, the visual value ladder, the tier gates. Complements caves.md §4
(which fixes the distribution numbers); every rule below is checkable on a render.

## 1. The invitation — surface features that advertise digging

**Terraria seeds the itch above ground**: worldgen places large surface veins
"buried near the ground, with a few ore blocks above it" — the exposed blocks ARE
the ad for the buried body — plus cave mouths that visibly continue down. Nobody
mines in the abstract; a specific outcrop propositions them. `terrain.rock_mass`
builds the body (multi-blob fill, apron, spill, 3-5-cell veins); make veins SURFACE.

**Rules we adopt** (check on the zone render):
- Every rock_mass shows ≥1 ore cell on its visible outer ring — never 100%
  interior ore; a pure-grey mass means reroll the vein seed.
- Every mass keeps its rubble skirt (ragged dirt apron + spilled stray blocks);
  a crisp grass-to-stone edge reads placed, not geological.
- The first mass near spawn/road is a dirt_block-shell body: shovel-first invite.
- Masses nearest the underground-zone entrance get the richest visible salting —
  surface hints point AT the way down (honest advertising).

**Counterexample**: a hand-set lone gold block on grass — a color pop with no
body behind it breaks the outcrop grammar's promise (owner call, caves.md §4).

Sources: terraria.wiki.gg World_generation + Layers · carlsguides.com caverns guide.

## 2. Reward cadence — the strike-to-payoff rhythm and the near miss

**The lab numbers are real**: near-misses (a vein tip = two matching symbols)
motivate more than full misses; persistence peaks near a ~30% near-miss rate —
15% too stingy, 45% reads rigged (Candy Crush: "you only needed 2 more"). Mining
is a variable-ratio schedule where some strikes reveal the EDGE of something.
SteamWorld Dig banks payoff in beats (bag-fill → sell → upgrade → deeper); Dome
Keeper went 2-phase because raw mining needs an external return-pull — ours is
the economy. The MAP owns per-strike rhythm; caves.md §4 fixed it as numbers.

**Rules we adopt** (run the ore-distribution probe, then eyeball the render):
- Mean dist-to-nearest-ore 3-4 cells, ~75% of rock within 5, p90 ≤ 10 — a blind
  miner nicks SOMETHING every few strikes (caves.md §4; re-run after any change).
- Veins 3-6 cells so one find pays several swings; 1-cell specks are full misses
  with paint (probe the vein-size histogram — no pile of singletons).
- Engineer near-misses: vein tips breach mass edges showing ~1 cell of 3-6 —
  visible fraction near the productive ~30%; the rest stays "almost".
- Rares are spikes, not schedule: 0-2 precious cells per mass, clumped; most masses none.

**Counterexample**: checkerboard-even ore — perfectly fair, zero suspense; a schedule
the player can predict is one they stop feeling.

Sources: PMC7214505 near-miss review (30% optimum) · PMC5445157 Candy Crush ·
playcritically.com SteamWorld Dig · gamedeveloper/shacknews Dome Keeper interviews.

## 3. Telegraphing value — the visual ladder of worth

**Minecraft's 21w08 ore redesign is the canonical lesson**: one speckle pattern
recolored seven ways meant colorblind players couldn't tell diamond from gold —
the fix gave each ore a UNIQUE inclusion shape, so identity survives with color
removed (and caves gained variety free). SteamWorld Dig keeps ore/gems plainly
visible in walls: discovery is a read, not a dice roll. **Rarity is encoded in
the read itself** — commons parse calmly; rares interrupt (glint, saturation).

**Rules we adopt** (check the catalog preview strip + a zone render):
- Each ladder ore (coal→copper→iron→tin→silver→gold→platinum) reads at zone zoom
  by inclusion SHAPE, not color — grayscale the preview row; merging tiers → redo one.
- Luminance tracks value up-ladder (coal dull → precious bright); gems add jewel
  saturation + the mineral-family facet glint so one deep cell pops in a render.
- Ore blocks stay stone-matrix + colored inclusions, never a full recolor — the
  matrix says "rock, mineable", the inclusion says "worth it".
- dirt_block vs stone_block read at a glance (warm/crumbly vs cool/solid): the
  shovel-vs-pickaxe decision is made from the render, before the click.

**Counterexample**: pre-1.17 Minecraft — one texture, seven tints; the rarest find had the quietest read.

Sources: feedback.minecraft.net 21w08 threads · techraptor.net + screenrant.com
ore-redesign coverage · playcritically.com SteamWorld Dig.

## 4. Tool gating as geography — tier walls are return tickets

**Terraria's bootstrap**: each tier's ore crafts the pickaxe that breaks the next
tier — the gate is the MATERIAL itself, so progression is geography, not doors.
**Stardew makes the gate a landmark**: the Secret Woods log and the farm boulders
sit visibly on the map from day one, unbreakable until Steel Axe/Pickaxe — every
walk past renews the promise. SteamWorld Dig gates softly (harder soil just digs
SLOWER). Ours: shovel-dirt → pickaxe-stone → tiered ores, in one concentric mass.

**Rules we adopt** (check on the zone render):
- Every gate is visible before it is passable: whatever a tier wall protects
  (ore heart, passage, grove) shows in the render from the accessible side.
- Compose masses concentric — dirt shell → stone → ore core — so first strikes
  always succeed and the mass itself teaches the tool ladder.
- Plant ≥1 see-but-can't-mine tease per zone: a next-tier ore visible behind
  stone the starting kit can't clear — the return trip booked on visit one.
- The tier-0 path never strands: dirt + common ore reachable end-to-end with
  starting tools. Gates pace; they don't wall.

**Counterexample**: a gate hiding its reward is just a wall — Stardew's log
works because the Woods visibly CONTINUE behind it.

Sources: terraria.wiki.gg Pickaxe_power · terraria.guide ore-progression ·
stardewvalleywiki Secret_Woods + Axes · playcritically.com SteamWorld Dig.

## 5. Biome-flavored rock identity — one rock, many accents

**Terraria varies the world around the rock**: snow gets ice, jungle gets mud —
identity comes from the SURROUND. Ours matches: one mined rock (stone_block) by
design; depth/biome change floor tile, apron, ore mix, dressing (caves.md §4).
Flavor is a recipe over one block — skills transfer, yet zones smell different.

**Rules we adopt** (compare two zone renders side by side):
- Per-zone ore TABLE, read not guessed (caves.md §4): the ore MIX is the flavor
  knob — coal-heavy smoky hills vs copper-stained red gorge.
- Shift the surround, not the block: mass ground tile, apron material, dressing
  (crystals, geodes, bones, mushrooms) vary per biome; stone_block never does.
- Two zones' rock areas must be tellable apart in thumbnails with the ore cells
  covered — if flavor lives only in the ore, the biome isn't doing its job.

**Counterexample**: a per-biome "hard_stone" recolor — removed (caves.md §4): visual noise AND redundant.

Sources: terraria.wiki.gg Biomes + Layers · caves.md §4 (internal doctrine).
