# tools/viewer/ — pages that show the game's content

## Bug Farmer Sprites
Every sprite and animation the game uses, on one page. The owner asked for it on 2026-09-30.

**The page:** https://claude.ai/artifact/USSdDBRhcSQJugFdA7a8qE (private to the owner).

**What's on it:** the sprites are found the way the game itself finds them, so the page shows what a player sees.
- **Items:** the inventory icon each one shows.
- **Objects:** everything placed in the world, at its in-game size. The townspeople are here too.
- **Crops:** each one's growth stages.
- **Bugs:** each species flapping at the game's rate, with its eggs and young, and a centipede's segments.
- **Ground:** every tile type, the grass variants and the grass tufts.
- **Player:** the layered parts, which the page stacks the way the game does, the baked class sprites, and every
  layer piece.
- **Approved outfits:** the whole outfits and their animations. These are **not in the game yet**.
- **Effects and interface:** the breaking overlay and the interface sprites.

**Rebuild and republish** whenever art or entity data changes:
```bash
python3 tools/viewer/build_sprites_page.py
```
It writes into the git-ignored `tools/_generated/viewer/sprites/`:
- `index.html` — the page that gets published;
- `outfits/<outfit>/<animation>.gif` — the approved animations, published alongside the page;
- `preview.html` — the same page, to open on this PC.

It exits with an error if any sprite it names is missing.

To republish, use the Artifact tool:
- `file_path`: `tools/_generated/viewer/sprites/index.html`;
- `url`: the page above (from another conversation, always pass it; without it, a separate page is created);
- `files`: map every `outfits/<outfit>/<animation>.gif` to its copy in the same folder.

**The rules it copies from the game,** each with its source:

| Rule | Source |
|---|---|
| The icon lookup order | `EntityDatabase.GetItemSprite`, `EntityDatabase.cs:775-787` |
| Crop stages | `TilemapManager.cs:714-717` |
| Bug frames | `SwarmVisual.cs:121-130` |
| Flap speeds | `BugVisual.FlapFps` = 11; flies 20 (`SwarmVisual.cs:288`) |
| Centipede segments | `CentipedeTrail.cs:66-76` |
| Layer order and walk cycle | `CharacterComposer.cs:74-142` |
| Walk speed | `PlayerController.WalkFps` = 7 |

If one of those changes in the game, change it in `build_sprites_page.py` too.

**Not dead code.** The page is generated and never edited by hand. Its HTML lives in `sprites_page.template.html`.
