using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace BugFarmer.World
{
    /// <summary>
    /// ScriptableObject database mapping tile and occupant IDs to Unity assets.
    /// Ground tiles use TileBase for efficient tilemap rendering.
    /// Occupants use Sprites for individual GameObject rendering.
    /// Create via Assets > Create > BugFarmer > TileDatabase.
    /// Place the asset in a Resources folder for auto-loading.
    /// </summary>
    [CreateAssetMenu(fileName = "TileDatabase", menuName = "BugFarmer/TileDatabase")]
    public class TileDatabase : ScriptableObject
    {
        private static TileDatabase _instance;

        [System.Serializable]
        public class GroundTileEntry
        {
            public string tileId;       // Matches server tile ID (grass, dirt, etc.)
            public TileBase tile;       // Unity Tile asset for tilemap rendering
        }

        [System.Serializable]
        public class OccupantEntry
        {
            public string occupantId;   // Matches server occupant ID (tree_oak, rock_small, etc.)
            public Sprite sprite;       // Sprite for rendering
            public int footprintWidth = 1;  // Collision/placement width in cells
            public int footprintHeight = 1; // Collision/placement height in cells
            public Vector2 pivot = new Vector2(0.5f, 0f); // Pivot point (0.5,0 = bottom-center)
            public bool isBreakable;    // For client-side visual hints
        }

        [Header("Ground Tiles")]
        [Tooltip("Map tile IDs to Unity Tile assets for tilemap rendering")]
        [SerializeField] private GroundTileEntry[] groundTiles;

        [Header("Occupants (Objects)")]
        [Tooltip("Map occupant IDs to sprites for object rendering")]
        [SerializeField] private OccupantEntry[] occupants;

        [Header("Breaking Effects")]
        [Tooltip("Crack overlay sprites for breaking progress (stage 1-4, increasing damage)")]
        [SerializeField] private Sprite[] breakStageSprites;

        [Header("Fallbacks")]
        [SerializeField] private TileBase defaultGroundTile;
        [SerializeField] private Sprite defaultOccupantSprite;

        private Dictionary<string, GroundTileEntry> _groundLookup;
        private Dictionary<string, OccupantEntry> _occupantLookup;

        public static TileDatabase Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = Resources.Load<TileDatabase>("TileDatabase");
                    if (_instance == null)
                    {
                        Debug.LogWarning("[TileDatabase] Not found in Resources. Create via Assets > Create > BugFarmer > TileDatabase");
                    }
                    else
                    {
                        _instance.BuildLookups();
                    }
                }
                return _instance;
            }
        }

        private void BuildLookups()
        {
            // Build ground tile lookup
            _groundLookup = new Dictionary<string, GroundTileEntry>();
            if (groundTiles != null)
            {
                foreach (var entry in groundTiles)
                {
                    if (!string.IsNullOrEmpty(entry.tileId))
                    {
                        _groundLookup[entry.tileId] = entry;
                    }
                }
            }

            // Build occupant lookup
            _occupantLookup = new Dictionary<string, OccupantEntry>();
            if (occupants != null)
            {
                foreach (var entry in occupants)
                {
                    if (!string.IsNullOrEmpty(entry.occupantId))
                    {
                        _occupantLookup[entry.occupantId] = entry;
                    }
                }
            }
        }

        /// <summary>
        /// Get the Unity Tile for a ground tile ID.
        /// Returns defaultGroundTile if not found.
        /// </summary>
        public TileBase GetGroundTile(string tileId)
        {
            if (string.IsNullOrEmpty(tileId))
                return defaultGroundTile;

            if (_groundLookup == null)
                BuildLookups();

            if (_groundLookup.TryGetValue(tileId, out var entry) && entry.tile != null)
                return entry.tile;

            return defaultGroundTile;
        }

        /// <summary>
        /// Get the full occupant entry for an occupant ID.
        /// Returns null if not found.
        /// </summary>
        public OccupantEntry GetOccupant(string occupantId)
        {
            if (string.IsNullOrEmpty(occupantId))
                return null;

            if (_occupantLookup == null)
                BuildLookups();

            return _occupantLookup.TryGetValue(occupantId, out var entry) ? entry : null;
        }

        /// <summary>
        /// Get just the sprite for an occupant ID.
        /// Returns defaultOccupantSprite if not found.
        /// </summary>
        public Sprite GetOccupantSprite(string occupantId)
        {
            var entry = GetOccupant(occupantId);
            return entry?.sprite ?? defaultOccupantSprite;
        }

        /// <summary>
        /// Check if an occupant ID is placeable (exists in database).
        /// </summary>
        public bool IsPlaceable(string occupantId)
        {
            return GetOccupant(occupantId) != null;
        }

        /// <summary>
        /// Get the footprint size for an occupant (in grid cells).
        /// This is the collision/placement area, not sprite dimensions.
        /// </summary>
        public Vector2Int GetOccupantCellSize(string occupantId)
        {
            var entry = GetOccupant(occupantId);
            if (entry == null)
                return Vector2Int.one;

            return new Vector2Int(entry.footprintWidth, entry.footprintHeight);
        }

        /// <summary>
        /// Get the break stage sprites for visual feedback during breaking.
        /// Returns null if not configured.
        /// </summary>
        public Sprite[] GetBreakStageSprites()
        {
            return breakStageSprites;
        }
    }
}
