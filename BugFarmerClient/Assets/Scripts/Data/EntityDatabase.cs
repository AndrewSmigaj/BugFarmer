using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;

namespace BugFarmer.Data
{
    /// <summary>
    /// Unified database for all game entities (items, occupants, placeables).
    ///
    /// Design:
    /// - Pure static class, auto-initializes on first access
    /// - Loads entity definitions from Resources/Data/entities/*.json
    /// - Same JSON format as server nakama/data/entities/
    /// - Sprites load by convention from Resources/Sprites/
    /// - No Unity assets or scene objects required
    ///
    /// Usage:
    ///   var sprite = EntityDatabase.GetItemSprite("wood");
    ///   bool canPlace = EntityDatabase.IsPlaceable("dirt_block");
    ///   var footprint = EntityDatabase.GetFootprint("workbench");
    /// </summary>
    public static class EntityDatabase
    {
        #region Data Classes (mirror server JSON structure)

        public class DropEntry
        {
            public string ItemId;
            public int Count = 1;
            public float Chance = 1f;
        }

        public class BreakableData
        {
            public int HP = 1;
            public string RequiredToolType;
            public int RequiredToolTier;
            public DropEntry[] Drops;
        }

        public class WorldData
        {
            public int[] Footprint = new int[] { 1, 1 };
            public string Pivot = "bc";
            public bool BlocksPlayers;
            public bool BlocksBugs;
            public bool Rotatable;
            public int Directions = 4;
            public bool Interactable;
            public string InteractionType;
            public BreakableData Breakable;
        }

        public class EntityDef
        {
            public string Id;
            public string Name;
            public string Category;
            public string EntityType; // "item", "occupant", or "placeable"

            // Inventory properties
            public bool Stackable;
            public int MaxStack = 99;
            public int SellPrice;
            public int BuyPrice;

            // Tool properties
            public string ToolType;
            public int ToolTier;
            public float Reach;
            public float MiningSpeed;
            public int Durability;
            public float CatchRadius;

            // Consumable
            public string Effect;

            // World presence (null for inventory-only items)
            public WorldData World;
        }

        #endregion

        private static Dictionary<string, EntityDef> _entities;
        private static Dictionary<string, Sprite> _spriteCache;
        private static Sprite[] _breakStageSprites;
        private static bool _initialized;

        #region Initialization

        private static void EnsureInitialized()
        {
            if (_initialized) return;

            _entities = new Dictionary<string, EntityDef>();
            _spriteCache = new Dictionary<string, Sprite>();

            int itemCount = LoadEntityFile("Data/entities/items", "item");
            int occupantCount = LoadEntityFile("Data/entities/occupants", "occupant");
            int placeableCount = LoadEntityFile("Data/entities/placeables", "placeable");

            // Load break stage sprites
            _breakStageSprites = new Sprite[4];
            for (int i = 0; i < 4; i++)
            {
                _breakStageSprites[i] = Resources.Load<Sprite>($"Effects/break_stage_{i + 1}");
            }

            _initialized = true;
            Debug.Log($"[EntityDatabase] Loaded {itemCount} items, {occupantCount} occupants, {placeableCount} placeables");
        }

        private static int LoadEntityFile(string resourcePath, string entityType)
        {
            var textAsset = Resources.Load<TextAsset>(resourcePath);
            if (textAsset == null)
            {
                Debug.LogWarning($"[EntityDatabase] {resourcePath}.json not found in Resources");
                return 0;
            }

            int count = 0;
            try
            {
                var root = JObject.Parse(textAsset.text);
                foreach (var prop in root.Properties())
                {
                    string id = prop.Name;
                    if (id.StartsWith("_")) continue; // Skip comments

                    var entity = ParseEntity(id, prop.Value as JObject, entityType);
                    if (entity != null)
                    {
                        _entities[id] = entity;
                        count++;
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[EntityDatabase] Failed to parse {resourcePath}: {e.Message}");
            }

            return count;
        }

        private static EntityDef ParseEntity(string id, JObject data, string entityType)
        {
            if (data == null) return null;

            var entity = new EntityDef
            {
                Id = id,
                EntityType = entityType,
                Name = data["name"]?.Value<string>() ?? id,
                Category = data["category"]?.Value<string>() ?? "",
                Stackable = data["stackable"]?.Value<bool>() ?? false,
                MaxStack = data["max_stack"]?.Value<int>() ?? 99,
                SellPrice = data["sell_price"]?.Value<int>() ?? 0,
                BuyPrice = data["buy_price"]?.Value<int>() ?? 0,
                ToolType = data["tool_type"]?.Value<string>(),
                ToolTier = data["tool_tier"]?.Value<int>() ?? 0,
                Reach = data["reach"]?.Value<float>() ?? 0f,
                MiningSpeed = data["mining_speed"]?.Value<float>() ?? 1f,
                Durability = data["durability"]?.Value<int>() ?? 0,
                CatchRadius = data["catch_radius"]?.Value<float>() ?? 0f,
                Effect = data["effect"]?.Value<string>()
            };

            // Parse world data if present
            var worldData = data["world"] as JObject;
            if (worldData != null)
            {
                entity.World = ParseWorldData(worldData);
            }

            return entity;
        }

        private static WorldData ParseWorldData(JObject data)
        {
            var world = new WorldData
            {
                Pivot = data["pivot"]?.Value<string>() ?? "bc",
                BlocksPlayers = data["blocks_players"]?.Value<bool>() ?? false,
                BlocksBugs = data["blocks_bugs"]?.Value<bool>() ?? false,
                Rotatable = data["rotatable"]?.Value<bool>() ?? false,
                Directions = data["directions"]?.Value<int>() ?? 4,
                Interactable = data["interactable"]?.Value<bool>() ?? false,
                InteractionType = data["interaction_type"]?.Value<string>()
            };

            // Parse footprint array
            var footprintArray = data["footprint"] as JArray;
            if (footprintArray != null && footprintArray.Count >= 2)
            {
                world.Footprint = new int[]
                {
                    footprintArray[0].Value<int>(),
                    footprintArray[1].Value<int>()
                };
            }

            // Parse breakable data
            var breakableData = data["breakable"] as JObject;
            if (breakableData != null)
            {
                world.Breakable = ParseBreakableData(breakableData);
            }

            return world;
        }

        private static BreakableData ParseBreakableData(JObject data)
        {
            var breakable = new BreakableData
            {
                HP = data["hp"]?.Value<int>() ?? 1,
                RequiredToolType = data["required_tool_type"]?.Value<string>(),
                RequiredToolTier = data["required_tool_tier"]?.Value<int>() ?? 0
            };

            // Parse drops array
            var dropsArray = data["drops"] as JArray;
            if (dropsArray != null)
            {
                var drops = new List<DropEntry>();
                foreach (var dropToken in dropsArray)
                {
                    var dropObj = dropToken as JObject;
                    if (dropObj != null)
                    {
                        drops.Add(new DropEntry
                        {
                            ItemId = dropObj["item_id"]?.Value<string>(),
                            Count = dropObj["count"]?.Value<int>() ?? 1,
                            Chance = dropObj["chance"]?.Value<float>() ?? 1f
                        });
                    }
                }
                breakable.Drops = drops.ToArray();
            }

            return breakable;
        }

        #endregion

        #region Entity Lookup

        /// <summary>
        /// Get the full entity definition by ID. Returns null if not found.
        /// </summary>
        public static EntityDef Get(string id)
        {
            EnsureInitialized();
            if (string.IsNullOrEmpty(id)) return null;
            return _entities.TryGetValue(id, out var def) ? def : null;
        }

        /// <summary>
        /// Check if an entity exists.
        /// </summary>
        public static bool Exists(string id) => Get(id) != null;

        /// <summary>
        /// Check if an entity can be placed in the world by players.
        /// </summary>
        public static bool IsPlaceable(string id)
        {
            var def = Get(id);
            return def != null && def.EntityType == "placeable";
        }

        /// <summary>
        /// Check if an entity has world presence (occupant or placeable).
        /// </summary>
        public static bool HasWorldPresence(string id)
        {
            var def = Get(id);
            return def != null && def.World != null;
        }

        /// <summary>
        /// Check if an entity is breakable.
        /// </summary>
        public static bool IsBreakable(string id)
        {
            var def = Get(id);
            return def?.World?.Breakable != null;
        }

        /// <summary>
        /// Get the footprint size for placement/collision (in grid cells).
        /// Returns (1,1) if entity not found or has no world data.
        /// Direction: 0=down, 1=left, 2=right, 3=up
        /// </summary>
        public static Vector2Int GetFootprint(string id, int direction = 0)
        {
            var def = Get(id);
            if (def?.World?.Footprint == null || def.World.Footprint.Length < 2)
                return Vector2Int.one;

            int w = def.World.Footprint[0];
            int h = def.World.Footprint[1];
            if (w == 0) w = 1;
            if (h == 0) h = 1;

            // Swap for left/right facing (directions 1 and 2)
            if (direction == 1 || direction == 2)
                return new Vector2Int(h, w);

            return new Vector2Int(w, h);
        }

        /// <summary>
        /// Get the pivot point for world rendering.
        /// Returns Vector2 where (0.5, 0) = bottom-center, (0.5, 0.5) = center.
        /// </summary>
        public static Vector2 GetPivot(string id)
        {
            var def = Get(id);
            string pivot = def?.World?.Pivot ?? "bc";

            return pivot switch
            {
                "c" => new Vector2(0.5f, 0.5f),
                "bc" => new Vector2(0.5f, 0f),
                "bl" => new Vector2(0f, 0f),
                "br" => new Vector2(1f, 0f),
                "tc" => new Vector2(0.5f, 1f),
                "tl" => new Vector2(0f, 1f),
                "tr" => new Vector2(1f, 1f),
                _ => new Vector2(0.5f, 0f)
            };
        }

        #endregion

        #region Sprite Loading

        /// <summary>
        /// Get the inventory icon sprite for an item.
        /// Convention: Resources/Items/{id}
        /// For placeables (e.g., dirt_block), loads Items/{base}_icon (e.g., dirt_icon)
        /// </summary>
        public static Sprite GetItemSprite(string id)
        {
            EnsureInitialized();
            if (string.IsNullOrEmpty(id)) return null;

            string cacheKey = $"item:{id}";
            if (_spriteCache.TryGetValue(cacheKey, out var cached))
                return cached;

            // Determine sprite path based on entity type
            string spritePath = id;
            var def = Get(id);
            if (def != null && def.EntityType == "placeable" && id.EndsWith("_block"))
            {
                // Placeables use {base}_icon for inventory sprites
                string baseName = id.Substring(0, id.Length - 6); // Remove "_block"
                spritePath = baseName + "_icon";
            }

            var sprite = Resources.Load<Sprite>($"Items/{spritePath}");
            if (sprite != null)
                _spriteCache[cacheKey] = sprite;

            return sprite;
        }

        /// <summary>
        /// Get the world sprite for an entity (occupant or placed item).
        /// Convention: Resources/Objects/{id}
        /// </summary>
        public static Sprite GetWorldSprite(string id)
        {
            EnsureInitialized();
            if (string.IsNullOrEmpty(id)) return null;

            string cacheKey = $"world:{id}";
            if (_spriteCache.TryGetValue(cacheKey, out var cached))
                return cached;

            var sprite = Resources.Load<Sprite>($"Objects/{id}");
            if (sprite != null)
                _spriteCache[cacheKey] = sprite;

            return sprite;
        }

        /// <summary>
        /// Get break stage overlay sprites (crack effects during mining).
        /// </summary>
        public static Sprite[] GetBreakStageSprites()
        {
            EnsureInitialized();
            return _breakStageSprites;
        }

        #endregion
    }
}
