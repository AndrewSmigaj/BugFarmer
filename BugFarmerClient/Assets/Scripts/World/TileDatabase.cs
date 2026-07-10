using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace BugFarmer.World
{
    /// <summary>
    /// Loads ground tile sprites from Resources/Tiles/ and creates TileBase objects at runtime.
    /// Drop a PNG in Resources/Tiles/{tileId}.png and it just works — consistent with
    /// EntityDatabase loading objects from Resources/Objects/, items from Resources/Items/, etc.
    /// </summary>
    [CreateAssetMenu(fileName = "TileDatabase", menuName = "BugFarmer/TileDatabase")]
    public class TileDatabase : ScriptableObject
    {
        private static TileDatabase _instance;

        [Header("Breaking Effects")]
        [Tooltip("Crack overlay sprites for breaking progress (stage 1-4, increasing damage)")]
        [SerializeField] private Sprite[] breakStageSprites;

        [Header("Fallback")]
        [SerializeField] private Sprite fallbackTileSprite;

        private Dictionary<string, TileBase> _tileCache;
        private TileBase _fallbackTile;

        public static TileDatabase Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = Resources.Load<TileDatabase>("TileDatabase");
                    if (_instance == null)
                        Debug.LogWarning("[TileDatabase] Not found in Resources. Create via Assets > Create > BugFarmer > TileDatabase");
                }
                return _instance;
            }
        }

        /// <summary>
        /// Get the Unity Tile for a ground tile ID.
        /// Loads sprite from Resources/Tiles/{tileId}.png and creates a Tile at runtime.
        /// </summary>
        public TileBase GetGroundTile(string tileId)
        {
            if (string.IsNullOrEmpty(tileId))
                return GetFallbackTile();

            if (_tileCache == null)
                _tileCache = new Dictionary<string, TileBase>();

            if (_tileCache.TryGetValue(tileId, out var cached))
                return cached;

            // Shaped ground: a composite id "matA~matB~shape" blends two materials through a shape mask into
            // one tile (runtime GPU composite). Cached by the full id, so each combo builds once.
            if (tileId.IndexOf('~') >= 0 && TileCompositor.TryParse(tileId, out var mA, out var mB, out var shape))
            {
                var comp = TileCompositor.Build(mA, mB, shape);
                if (comp != null)
                {
                    var compSprite = Sprite.Create(comp,
                        new Rect(0, 0, comp.width, comp.height),
                        new Vector2(0.5f, 0.5f),
                        comp.width);
                    var compTile = ScriptableObject.CreateInstance<Tile>();
                    compTile.sprite = compSprite;
                    compTile.color = Color.white;
                    _tileCache[tileId] = compTile;
                    return compTile;
                }
                // compositing failed (missing material/shader) -> fall through to fallback below
            }

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

        private TileBase GetFallbackTile()
        {
            if (_fallbackTile != null)
                return _fallbackTile;

            if (fallbackTileSprite != null)
            {
                var tile = ScriptableObject.CreateInstance<Tile>();
                tile.sprite = fallbackTileSprite;
                tile.color = new Color(1f, 0f, 1f, 1f); // Magenta so missing tiles are obvious
                _fallbackTile = tile;
                return _fallbackTile;
            }

            return null;
        }

        /// <summary>
        /// Get the break stage sprites for visual feedback during breaking.
        /// </summary>
        public Sprite[] GetBreakStageSprites()
        {
            return breakStageSprites;
        }
    }
}
