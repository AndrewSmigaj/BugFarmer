# Shaped-ground builder (the shovel)

How players sculpt non-square ground — diagonal roads, patterns, checkerboards — with the shovel. Built
M0–M4 (2026-07-09/10). Cosmetic; mechanics deferred (see BACKLOG "Ground material MECHANICS").

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

## The terraform loop (coin-free — "move ground around")
The shovel is a terraform tool (`handleShovel`, routed from `handleToolUse` on tool_type `shovel`;
`ToolUseMessage` carries `ground_id` + `dig`):
- **PLACE (LMB)** — validates the chosen id (`ValidateShovelGround`: 8 decorative materials × known shapes +
  length cap — the SOLE guard on the player-supplied string), consumes 1 **material block**
  (`FindItemSlot`+`RemoveItem`) or errors `Need <block>`, sets the ground, broadcasts.
- **DIG (RMB)** — reverts the cell to `dirt`, grants 1 block (`AddItem`; granted FIRST so a full bag cancels
  the dig, never destroying the block). Dirt is the abundant base (digging dirt yields dirt).
- Material↔block map: `GroundMaterialItem` — grass→`grass_turf`, dirt/sand/mud→self, stone family→`stone`,
  wood_floor→`wood`. Neither verb touches water/lava (that's the future sandbag system).
- Cosmetic feedback: dust poof (`HitBurst.Kind.Dust`) + the shovel swing on place/dig.

## Palette scope (decorative only) & excluded systems
Placeable: `grass, dirt, sand, mud, stone_floor, stone_path, wood_floor, cave_floor`. Excluded (own systems):
water/lava (collision — future sandbag fill), garden_plot (hoe/farming), bridges (placed structures over
water), rugs (future grid-square rug-pattern builder).

## Files
- Client: `World/Rendering/TileComposite.shader`, `World/Rendering/TileCompositor.cs`, `World/TileDatabase.cs`
  (`~` branch), `World/ShovelSelection.cs`, `World/ShapedGroundSpike.cs` (builder input + dev-grade HUD —
  replaced by the real UI at the polish pass), `World/TilemapManager.cs` (`PrimaryMaterial`/`IsWaterTile`),
  `Player/ToolUseController.cs` (place/`TryDig`), `Player/PlayerInputRouter.cs` (shovel routing),
  `UI/HotbarUI.cs` (yields the wheel), `World/HitBurst.cs` (`Kind.Dust`).
- Server: `world/tiles.go` (`PrimaryMaterial`, `ValidateShovelGround`, `GroundMaterialItem`),
  `world/handlers_farming.go` (`handleShovel`), `world/state.go` + others (derivation sites),
  `world/inventory.go` (`FindItemSlot`), `world/messages.go` (`ToolUseMessage` +`GroundID`/`Dig`).
  Tests: `world/shaped_ground_test.go`.

## Deferred (owner passes / later)
Builder UI polish (real panel — taste checkpoint); material item icons (art = API spend); ground MECHANICS
(swamp-slow/ice; diagonal AVERAGES the two); full conservation (place currently consumes only matA);
sandbag water-fill; rug grid-pattern builder.
