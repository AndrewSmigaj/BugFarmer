using UnityEditor;
using UnityEngine;
using UnityEngine.Tilemaps;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using BugFarmer.World;

/// <summary>
/// Editor tool to auto-populate TileDatabase from JSON config files.
/// Reads occupants.json and tiles.json, creates Tile assets, and populates TileDatabase.
/// </summary>
public class TileDatabaseBuilder : EditorWindow
{
    private const string OccupantsJsonPath = "nakama/data/occupants.json";
    private const string TilesJsonPath = "nakama/data/tiles.json";
    private const string TileDatabasePath = "Assets/Resources/TileDatabase.asset";
    private const string GeneratedTilesFolder = "Assets/Resources/Tiles";

    [MenuItem("BugFarmer/Build TileDatabase")]
    public static void Build()
    {
        Debug.Log("[TileDatabaseBuilder] Starting build...");

        // Find repo root (parent of BugFarmerClient folder)
        // Application.dataPath = .../BugFarmer/BugFarmerClient/Assets
        // We need .../BugFarmer/ (two levels up)
        string unityProjectRoot = Path.GetDirectoryName(Application.dataPath);
        string repoRoot = Path.GetDirectoryName(unityProjectRoot);

        // Load JSON files
        string occupantsPath = Path.Combine(repoRoot, OccupantsJsonPath);
        string tilesPath = Path.Combine(repoRoot, TilesJsonPath);

        if (!File.Exists(occupantsPath))
        {
            Debug.LogError($"[TileDatabaseBuilder] occupants.json not found at: {occupantsPath}");
            return;
        }
        if (!File.Exists(tilesPath))
        {
            Debug.LogError($"[TileDatabaseBuilder] tiles.json not found at: {tilesPath}");
            return;
        }

        var occupantsJson = File.ReadAllText(occupantsPath);
        var tilesJson = File.ReadAllText(tilesPath);

        JObject occupants = JObject.Parse(occupantsJson);
        JObject tiles = JObject.Parse(tilesJson);

        // Get or create TileDatabase
        TileDatabase db = GetOrCreateTileDatabase();
        if (db == null)
        {
            Debug.LogError("[TileDatabaseBuilder] Failed to get or create TileDatabase");
            return;
        }

        // Ensure generated tiles folder exists
        EnsureFolder(GeneratedTilesFolder);

        // Build ground tiles
        var groundEntries = new List<TileDatabase.GroundTileEntry>();
        int groundCount = 0;
        int groundSkipped = 0;

        foreach (var prop in tiles.Properties())
        {
            string tileId = prop.Name;
            JObject data = prop.Value as JObject;
            string spritePath = data?["sprite_path"]?.ToString();

            if (string.IsNullOrEmpty(spritePath))
            {
                Debug.LogWarning($"[TileDatabaseBuilder] Tile '{tileId}' missing sprite_path, skipping");
                groundSkipped++;
                continue;
            }

            string fullSpritePath = $"Assets/{spritePath}";
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(fullSpritePath);

            if (sprite == null)
            {
                Debug.LogWarning($"[TileDatabaseBuilder] Sprite not found for tile '{tileId}' at {fullSpritePath}");
                groundSkipped++;
                continue;
            }

            Tile tile = CreateOrUpdateTile(tileId, sprite);
            if (tile != null)
            {
                var entry = new TileDatabase.GroundTileEntry
                {
                    tileId = tileId,
                    tile = tile
                };
                groundEntries.Add(entry);
                groundCount++;
            }
        }

        // Build occupant entries
        var occupantEntries = new List<TileDatabase.OccupantEntry>();
        int occupantCount = 0;
        int occupantSkipped = 0;

        foreach (var prop in occupants.Properties())
        {
            string occupantId = prop.Name;
            JObject data = prop.Value as JObject;
            string spritePath = data?["sprite_path"]?.ToString();

            if (string.IsNullOrEmpty(spritePath))
            {
                Debug.LogWarning($"[TileDatabaseBuilder] Occupant '{occupantId}' missing sprite_path, skipping");
                occupantSkipped++;
                continue;
            }

            string fullSpritePath = $"Assets/{spritePath}";
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(fullSpritePath);

            if (sprite == null)
            {
                Debug.LogWarning($"[TileDatabaseBuilder] Sprite not found for occupant '{occupantId}' at {fullSpritePath}");
                occupantSkipped++;
                continue;
            }

            // Parse footprint and visual data
            int footprintW = data?["footprint_w"]?.ToObject<int>() ?? 1;
            int footprintH = data?["footprint_h"]?.ToObject<int>() ?? 1;
            string pivotStr = data?["pivot"]?.ToString() ?? "bc";
            bool isBreakable = data?["is_breakable"]?.ToObject<bool>() ?? false;

            // Convert pivot string to Vector2
            Vector2 pivot;
            if (pivotStr == "c")
            {
                pivot = new Vector2(0.5f, 0.5f); // center
            }
            else
            {
                pivot = new Vector2(0.5f, 0f); // bottom-center (default)
            }

            var entry = new TileDatabase.OccupantEntry
            {
                occupantId = occupantId,
                sprite = sprite,
                footprintWidth = footprintW,
                footprintHeight = footprintH,
                pivot = pivot,
                isBreakable = isBreakable
            };
            occupantEntries.Add(entry);
            occupantCount++;
        }

        // Apply to database using reflection (arrays are private/serialized)
        SetPrivateField(db, "groundTiles", groundEntries.ToArray());
        SetPrivateField(db, "occupants", occupantEntries.ToArray());

        // Mark dirty and save
        EditorUtility.SetDirty(db);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        Debug.Log($"[TileDatabaseBuilder] Build complete!");
        Debug.Log($"  Ground tiles: {groundCount} created, {groundSkipped} skipped");
        Debug.Log($"  Occupants: {occupantCount} created, {occupantSkipped} skipped");
    }

    private static TileDatabase GetOrCreateTileDatabase()
    {
        // Ensure Resources folder exists
        EnsureFolder("Assets/Resources");

        // Try to load existing
        TileDatabase db = AssetDatabase.LoadAssetAtPath<TileDatabase>(TileDatabasePath);

        if (db == null)
        {
            // Create new
            db = ScriptableObject.CreateInstance<TileDatabase>();
            AssetDatabase.CreateAsset(db, TileDatabasePath);
            Debug.Log($"[TileDatabaseBuilder] Created new TileDatabase at {TileDatabasePath}");
        }
        else
        {
            Debug.Log($"[TileDatabaseBuilder] Using existing TileDatabase at {TileDatabasePath}");
        }

        return db;
    }

    private static Tile CreateOrUpdateTile(string tileId, Sprite sprite)
    {
        string tilePath = $"{GeneratedTilesFolder}/{tileId}.asset";

        Tile tile = AssetDatabase.LoadAssetAtPath<Tile>(tilePath);

        if (tile == null)
        {
            tile = ScriptableObject.CreateInstance<Tile>();
            AssetDatabase.CreateAsset(tile, tilePath);
        }

        tile.sprite = sprite;
        tile.color = Color.white;
        tile.colliderType = Tile.ColliderType.None;

        EditorUtility.SetDirty(tile);
        return tile;
    }

    private static void EnsureFolder(string path)
    {
        if (!AssetDatabase.IsValidFolder(path))
        {
            string parent = Path.GetDirectoryName(path);
            string folderName = Path.GetFileName(path);

            if (!AssetDatabase.IsValidFolder(parent))
            {
                EnsureFolder(parent);
            }

            AssetDatabase.CreateFolder(parent, folderName);
            Debug.Log($"[TileDatabaseBuilder] Created folder: {path}");
        }
    }

    private static void SetPrivateField(object obj, string fieldName, object value)
    {
        var field = obj.GetType().GetField(fieldName, BindingFlags.NonPublic | BindingFlags.Instance);
        if (field != null)
        {
            field.SetValue(obj, value);
        }
        else
        {
            Debug.LogError($"[TileDatabaseBuilder] Field '{fieldName}' not found on {obj.GetType().Name}");
        }
    }
}
