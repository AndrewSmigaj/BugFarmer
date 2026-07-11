# Shaped-ground builder (the shovel)

How players sculpt non-square ground — diagonal roads, patterns, checkerboards — with the shovel. Built
M0–M4 (2026-07-09/10), then reworked for **legibility** in S1 (2026-07-10) after playtest: dig and place
were indistinguishable and refusals were invisible. Ground look is cosmetic; ground MECHANICS
(swamp-slow/ice) are still deferred (see BACKLOG "Ground material MECHANICS").

## The composite-id grammar (the key idea)
Ground is a **string id per cell** and is **opaque** through storage/network/save. A shaped cell encodes its
look in that id — no structural data-model change anywhere:
- Plain paint → the existing id, no tilde: `dirt`.
- Shaped → **`matA~matB~shape`**, e.g. `grass~dirt~diagNE`. Material A fills the shape mask's 1-region,
  material B the 0-region.

Because the id stays an opaque string, the **server, save (`world_save.go` `GlobalCellEdit.Ground`), and
broadcast (`WorldUpdateMessage.Ground`) carry it unchanged** — only the client composites it, and only the
gameplay-derivation sites resolve it (below).

## Rendering — runtime GPU mask-composite (client)
`TileDatabase.GetGroundTile(id)`: if `id` contains `~`, `TileCompositor` blends `Resources/Tiles/{matA}.png`
+ `{matB}.png` through a procedural shape mask into one 32×32 tile via `Graphics.Blit` through
`Hidden/BugFarmer/TileComposite.shader` (`lerp(matB, matA, mask.r)`) → `RenderTexture` → `ReadPixels` →
`Texture2D`. GPU path because the base tiles import `isReadable:0` (no CPU `GetPixels`); project is Gamma
color space so no sRGB reconcile. Result cached by the full id (`_tileCache`) → each combo builds once.
- **Shapes** (`TileCompositor.Shapes`, generated procedurally, no PNG assets): `full` · 4 diagonal halves ·
  4 straight halves · 4 quadrant squares. Checkerboards = alternating SOLID tiles (no shape).
- **Build note:** add the shader to Always-Included Shaders before a player build (`Shader.Find` is
  Editor-only otherwise).

## The one rule — "primary material governs" (`PrimaryMaterial`)
For ALL gameplay a composite behaves as its **primary material (matA)**. A tiny split-helper is applied at
every derivation site so a composite never falls through a `TileDefs[...]` lookup or a hardcoded-tile check:
- Server `PrimaryMaterial(id)` (`tiles.go`): hoe `TileDefs` lookup, watering-can water refill, bug-block
  `TileDefs`, and the **player water/lava collision switch** (`state.go`).
- Client `TilemapManager.PrimaryMaterial` mirror: `IsWaterTile` (feeds collision + water overlay + minimap)
  and the player-collision check.
- **Lockstep:** the server (`state.go`) and client (`TilemapManager.IsCellBlockedForPlayers`) water/lava
  checks must change together or players desync at water edges. (Neutralized in practice: the palette is
  decorative-only, so no composite is ever water-primary.)
- Forward-compatible: ground MECHANICS later replace `PrimaryMaterial` with a `Properties(id)` that BLENDS
  matA+matB — same call sites.

## The terraform loop — dig = a BREAK, place = a CRAFT (S1)
The shovel is a terraform tool (`handleShovel`, routed from `handleToolUse` on tool_type `shovel`;
`ToolUseMessage` carries `ground_id` + `dig`). S1 made the two verbs read differently on purpose:

**Controls (client — `PlayerInputRouter`):** **LMB = place**, **Shift+LMB = dig** (hold to keep digging — a
dig-hold latch mirrors the block-break latch). RMB is intentionally *not* dig (it stays free for the context
actions: stations/hives/beds). The mouse **wheel cycles SHAPE only** (the old Shift/Ctrl-wheel material
scheme was the confusing part and is gone; material choice moves to a "Set Materials" panel in S2 — until
then temporary dev keys M/N cycle material A/B).

- **PLACE = a recipe-craft.** `ValidateShovelGround` still guards the player-supplied id (8 decorative
  materials × known shapes + length cap). The cost is then the **ground recipe**
  (`nakama/data/entities/ground_recipes.json`, id → `[]RecipeIO`): a solid tile costs its one material's
  recipe; a **composite costs the UNION of BOTH materials' recipes**, duplicates summed — it's made of both
  (owner: "a sandwich needs bread AND filling"). `groundRecipeIngredients(id)` merges via `CompositeMaterials`;
  `groundShortfall` builds a "Need 2 stone, 1 plank" message; consume goes through the crafting item path
  (`playerCount`/`playerConsume`). Missing ingredients → the world-error toast, not silence.
- **DIG = a progressive break.** Each Shift+LMB hit accumulates in a **`DiggingState`** map (separate from the
  occupant `BreakingState`, same key form) and broadcasts `BreakProgress` (OpCode 45) — the client crack
  pipeline is cell-keyed, so the 4-stage spiderweb renders on a bare ground cell with no client change.
  `digHitsFor` = 3 for stone-family, 2 for soft ground. After the last hit the cell becomes the recessed
  **`dug_soil`** tile and the tile's material(s) **drop to the ground** like felling a tree (`spawnHarvestDrops`,
  both materials of a composite). A dig left idle > 3s heals: `processDiggingReset` (a tick sweep) clears the
  crack and drops the `DiggingState` entry. `dug_soil` is a normal walkable/buildable-over tile
  (`tiles.json`); it has no recipe, so it isn't placeable or re-diggable.
- **The material loop** is now: dig ground → its material(s) drop as ground items → pick them up → place them
  (as a recipe) elsewhere. Coin-free. Neither verb touches water/lava (future sandbag system).
- **World-error toast (foundational, game-wide):** `WorldToast` (client HUD) surfaces every OpCode-40
  refusal ("Need 2 stone", "Can't shovel water", "Nothing to dig here"). Previously only `ShopPanel` read
  OpCode 40 (and only while open), so refusals outside a shop were invisible — the root cause of the shovel
  "does nothing, no feedback" bug. Fixed once, for all systems.
- Feedback: dust poof (`HitBurst.Kind.Dust`) + the shovel scoop swing per hit/place.

## Palette scope (decorative only) & excluded systems
Placeable: `grass, dirt, sand, mud, stone_floor, stone_path, wood_floor, cave_floor`. Excluded (own systems):
water/lava (collision — future sandbag fill), garden_plot (hoe/farming), bridges (placed structures over
water), rugs (future grid-square rug-pattern builder).

## Files
- Client: `World/Rendering/TileComposite.shader`, `World/Rendering/TileCompositor.cs`, `World/TileDatabase.cs`
  (`~` branch; plain `dug_soil` loads `Tiles/dug_soil.png`), `World/ShovelSelection.cs`,
  `World/ShapedGroundSpike.cs` (wheel=shape + temp M/N material keys + dev HUD — replaced by the S2 panel),
  `World/TilemapManager.cs` (`PrimaryMaterial`/`IsWaterTile`; the cell-keyed crack overlay `ShowBreakingProgress`
  is reused for dig), `Player/ToolUseController.cs` (place/`TryDig`), `Player/PlayerInputRouter.cs` (LMB place /
  Shift+LMB dig-hold latch), `UI/WorldToast.cs` (OpCode-40 toast) + `UI/UIBootstrap.cs` (registers it),
  `World/HitBurst.cs` (`Kind.Dust`).
- Server: `world/tiles.go` (`PrimaryMaterial`, `ValidateShovelGround`, `CompositeMaterials`; `GroundMaterialItem`
  is now legacy — only referenced by tests), `world/entities.go` (`LoadGroundRecipes`, `groundRecipeIngredients`,
  `groundShortfall`), `world/handlers_farming.go` (`handleShovel` place=recipe / dig=progressive, `digHitsFor`,
  `processDiggingReset`), `world/state.go` (`GroundRecipes`, `DiggingState`), `world/match.go` (recipe load + the
  dig-reset sweep), `world/persist_classes.go` (both new fields classified), `world/messages.go` (`ToolUseMessage`,
  `BreakProgressMessage`). Data: `nakama/data/entities/ground_recipes.json`, `nakama/data/tiles.json` (`dug_soil`),
  `Resources/Tiles/dug_soil.png`. Tests: `world/shaped_ground_test.go` (`CompositeMaterials`,
  `groundRecipeIngredients`, `groundShortfall`, `digHitsFor`).

## Milestones & deferred
- **Done + verified:** M0–M4; **S1** legibility rework (dig=progressive break→`dug_soil`+drops, place=recipe,
  LMB/Shift+LMB, wheel=shape, world-error toast) — Go tests + plugin build pass.
- **Built, in-engine verify owed (blind — no Unity in the build env):**
  - **S2 "Set Materials" panel** (`UI/ShovelBuilderPanel.cs`, open with `B`): composited-tile swatches +
    material B row + live have/need (`Data/GroundRecipeDatabase.cs` JObject-loads the published
    `ground_recipes.json`), unaffordable dimmed. Two layouts were rendered from the real composites
    (`tools/sprites/shovel_panel_mockup.py`) — layout A built; owner picks the final. The dev HUD + temp M/N
    keys stay as an additive fallback.
  - **S3 preview tooling** (`tools/sprites/composite_tiles.py`, `tool_swing_gif.py`) — CPU tile compositor
    (mirrors the GPU shader) + a faithful port of the animator's motion model to GIFs; verified by rendering.
  - **S4 animation fixes** — watering-can Pour rewritten (was applying the −45° diagonal tilt to an upright
    3/4 sprite, then freezing → lay on its side); hoe till strengthened. Designed in the GIF port, ported 1:1.
- **Later / owner passes:** material item icons (art = API spend); ground MECHANICS (swamp-slow/ice; diagonal
  AVERAGES the two); sandbag water-fill; rug grid-pattern builder; `dug_soil` art polish (current tile is a
  cropped placeholder); the broader tool-animation technique pass (reach-extension etc. — taste, owner-in-loop).
- **Verification owed:** in-engine S1 legibility playtest + client compile check (new toast/panel C# is unrun);
  a 2-client break-drop sync check (new drop-count + dig RNG fires only on player breaks, so the autonomous
  determinism harness is unaffected — confirm client parity once).
