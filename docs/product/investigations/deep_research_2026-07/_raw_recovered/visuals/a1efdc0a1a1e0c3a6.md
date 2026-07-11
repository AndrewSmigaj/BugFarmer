Now the meta import settings, camera zoom scroll usage, and the data files.

---

Now confirm CameraFollow has no scroll-zoom, and check items.json for matching ground-material item ids.

---

Let me enumerate all item ids to map ground materials to inventory items.

---

All facts verified. Here are the findings.

## 1. The render hook — `GetGroundTile`

`/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Scripts/World/TileDatabase.cs:45-73`

```csharp
public TileBase GetGroundTile(string tileId)
{
    if (string.IsNullOrEmpty(tileId))
        return GetFallbackTile();

    if (_tileCache == null)
        _tileCache = new Dictionary<string, TileBase>();

    if (_tileCache.TryGetValue(tileId, out var cached))
        return cached;

    var tex = Resources.Load<Texture2D>($"Tiles/{tileId}");
    if (tex != null)
    {
        // Create sprite with PPU = texture width so any size PNG fits exactly one cell
        var sprite = Sprite.Create(tex,
            new Rect(0, 0, tex.width, tex.height),
            new Vector2(0.5f, 0.5f),
            tex.width);
        var tile = ScriptableObject.CreateInstance<Tile>();
        tile.sprite = sprite;
        tile.color = Color.white;
        _tileCache[tileId] = tile;
        return tile;
    }

    Debug.LogWarning($"[TileDatabase] No sprite found for tile '{tileId}' in Resources/Tiles/");
    return GetFallbackTile();
}
```

- **PPU:** `tex.width` (so a 32×32 PNG → PPU 32 → exactly one 1-unit cell). Note this is the runtime PPU used for rendering; it overrides the `.meta`'s `spritePixelsToUnits: 16` because the sprite is rebuilt from the raw texture via `Sprite.Create`, not loaded as the imported sprite asset.
- **Pivot:** `(0.5, 0.5)` — centered.
- **filterMode:** Not set here — inherited from the loaded `Texture2D`'s import setting (see #2; it is mixed per-tile).
- **Cache:** Yes — `_tileCache` is a `Dictionary<string, TileBase>` keyed by the raw `tileId` string. So your composite key (e.g. `"grass~dirt~circle"`) would naturally cache as one entry.
- **Your `~` branch** slots cleanly in right after the `_tileCache.TryGetValue` check (line 53-54) and before/instead of the `Resources.Load` at line 56: if `tileId.Contains('~')`, build the composite texture, wrap it in `Sprite.Create(..., compositeTex.width)`, cache under the full id, return. The cache lookup already handles dedup.

## 2. Tile texture facts (load-bearing for compositing)

**Dimensions:** all sampled ground PNGs are **32×32** (`grass, dirt, sand, water_shallow, stone_floor, dirt_path_d_ne, stone_path_d_ne` all `(32, 32)`). Uniform 32×32. (The `.meta` even carves a legacy `16×16` sub-sprite rect in the spriteSheet block, but the actual PNG is 32×32 and `GetGroundTile` uses the full `tex.width/height`.)

**Import settings** (from `.meta`, e.g. `grass.png.meta`):
- **`isReadable: 0`** for ALL tiles (confirmed across every `*.png.meta` in the folder). This is the critical blocker: **CPU `GetPixels`/`SetPixels` will throw** on these textures as imported. For a CPU composite path you must either flip Read/Write Enabled on (import change), or `Resources.Load` + copy via a readable `RenderTexture`/`Graphics.Blit` + `ReadPixels`, i.e. a **GPU blit path is the safer route** given they're all non-readable.
- **`textureType: 8`** = Sprite (Sprite2D). All ground tiles are Sprite type, not Default.
- **`filterMode` is MIXED:**
  - `filterMode: 0` (Point) — grass, dirt, sand, stone_floor, stone_path, mud, water_shallow/deep, cave_floor, bridge_*, rug_*, garden_plot*, wood_floor.
  - `filterMode: 1` (Bilinear) — the diagonal path variants (`dirt_path_d_*`, `stone_path_d_*`) AND `grass_v2`, `grass_v3`.
- Other: `alphaIsTransparency: 1`, `sRGBTexture: 1`, `mipMapEnabled: 0`, `maxTextureSize: 2048`, wrap = Repeat.

Implication: base ground tiles are Point-filtered; if you composite onto a new `Texture2D` you should set `filterMode = FilterMode.Point` on the output to match the crisp pixel-art look of the base tiles.

## 3. Mousewheel binding

Scroll wheel is bound in **exactly one place**: `/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Scripts/UI/HotbarUI.cs:110-125` → **hotbar slot cycling**.

```csharp
private void HandleScrollWheel()
{
    // Disable scroll when inventory panel is open
    if (InventoryPanel.IsOpen)
        return;

    float scroll = Input.GetAxis("Mouse ScrollWheel");
    if (scroll > 0.01f)      SelectSlot((_selectedSlot - 1 + 10) % 10);
    else if (scroll < -0.01f) SelectSlot((_selectedSlot + 1) % 10);
}
```

- Uses the legacy `Input.GetAxis("Mouse ScrollWheel")`. No use of `Input.mouseScrollDelta` anywhere.
- **Camera zoom does NOT use scroll.** `CameraFollow.cs` has no scroll/zoom/orthographicSize code (grep returned "NO scroll/zoom/ortho"). Other `scroll` hits (TilemapManager water `_ScrollDir`, Rain/Dust "zoom" comments) are unrelated shader/particle scroll, not input.
- **Conflict:** only the hotbar. It already self-suppresses when `InventoryPanel.IsOpen`. Your builder should mirror that pattern — HotbarUI has no other guard, so either add a `Builder.IsActive` check to the `HandleScrollWheel` early-return, or gate your builder's scroll capture so only one consumes the wheel per frame.

## 4. Material palette + cost source

**Two `tiles.json` files exist:**
- `/mnt/c/Users/emily/BugFarmer/nakama/data/tiles.json` (the live/server data — full content read above)
- `/mnt/c/Users/emily/BugFarmer/tools/art/catalog/tiles.json` (art catalog)

**Ground materials enumerated** in `nakama/data/tiles.json` (keys = tile ids), with `sprite_path`, `movement_mult`, `accepts_furniture/structure/plant`, `blocks_players/bugs`, and `tool_actions`:

`grass, dirt, stone_path, wood_floor, stone_floor, cave_floor, garden_plot, garden_plot_wet, mud, sand, water_shallow, water_deep, bridge_wood, bridge_stone, rug_small, rug_large` + the 8 diagonal variants (`stone_path_d_{ne,nw,se,sw}`, `dirt_path_d_{ne,nw,se,sw}`).

For a placeable palette, the natural base-material subset is: grass, dirt, sand, mud, stone_path, stone_floor, wood_floor, cave_floor (water/bridge/rug/garden_plot are special-cased by flags).

**Material-cost / inventory mapping** (checked against all ~200 top-level ids in `/mnt/c/Users/emily/BugFarmer/nakama/data/entities/items.json`):

| Ground material | Matching item id? |
|---|---|
| **sand** | ✅ `sand` (exact) |
| grass | ❌ none |
| dirt | ❌ none |
| stone_floor / stone_path | ❌ no `stone` item at all |
| mud | ❌ none |
| cave_floor | ❌ none |
| wood_floor | ⚠️ `wood` exists as a raw material, but not `wood_floor` (would need a mapping/recipe, not a 1:1 id) |

Only **`sand`** has a direct 1:1 inventory item. There is **no** `dirt`, `grass`, `stone`, `mud`, `clay`, `gravel`, or `cobble` item. Related building-material items that DO exist (for a costed recipe): `wood`, `plank`, `brick`, `glass`, `charcoal`, `coal`, `fiber`, `cloth`. So a "consume material to place" system would work out-of-the-box only for sand; everything else needs new item entries or a material→item cost map.

## 5. Existing diagonal tiles (the precedent)

Confirmed — all 8 exist as real PNGs under `/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Tiles/`:

```
dirt_path_d_ne.png   dirt_path_d_nw.png   dirt_path_d_se.png   dirt_path_d_sw.png
stone_path_d_ne.png  stone_path_d_nw.png  stone_path_d_se.png  stone_path_d_sw.png
```

- **Pre-baked full 32×32 sprites** (verified `dirt_path_d_ne.png` = `(32,32)`, `stone_path_d_ne.png` = `(32,32)`) — full-cell tiles, not masks/overlays. File sizes ~2.1-2.4 KB.
- They differ from the base tiles in one import setting: **`filterMode: 1` (Bilinear)** vs the base tiles' Point — and `isReadable: 0` like everything else.
- They are registered in `tiles.json` (`nakama/data/tiles.json:105-152`) each inheriting the parent material's `movement_mult` (0.9 for dirt, 1.1 for stone) and `accepts_furniture/structure`.

This is exactly the pattern you're generalizing: today a diagonal blend of material-over-material is a hand-baked full-cell PNG per direction; your feature replaces that with a runtime composite of `{materialA}~{materialB}~{shape}` through a mask, keyed/cached in `_tileCache`.

One design note surfaced by the facts: because every source tile is `isReadable: 0`, the compositing implementation should assume a **GPU/RenderTexture blit + `ReadPixels`** path (or a shader-driven `Tile` material), rather than direct `Texture2D.GetPixels/SetPixels`, unless you also flip Read/Write Enabled in the importers.