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

            // Station block (material processors: compost bin etc.)
            public string[] StationAccepts;  // Item types depositable here (menu filter)
            public int StationCapacity = 10;

            // Craft stations: how many recipes run AT ONCE (parallel processor lanes; 0/absent = 1).
            public int CraftSlots;

            // Container block (item storage: chests/dressers/racks). ContainerSlots > 0 marks a
            // storage occupant; ContainerFilter (a tag) restricts what it accepts ("" = anything).
            public int ContainerSlots;
            public string ContainerFilter;

            // Shop block (NPC vendor; interaction_type "shop"). ShopKind "items"|"bugs"; ShopSells is
            // what the NPC offers (id+price). ShopBuys = the ids/tags this vendor purchases (the
            // client-side stage filter + "Buys:" header); pricing stays server-authoritative.
            public string ShopKind;            // null = not a shop
            public string[] ShopBuys;          // ids or tags; null/empty = buys nothing
            public ShopOffer[] ShopSells;
            public ShopOffer[] ShopRecipes;    // recipes the NPC teaches (id = recipe id)
            public ShopOffer[] ShopBooks;      // recipe-book collections (id = collection id)
            public string Greeting;            // NPC dialogue line (null = use a default)

            // Light block (lamps/torches glow at night; 0 radius = no light)
            public float LightRadius;
            public Color LightColor = new Color(1f, 0.82f, 0.55f);
            public float LightIntensity = 1f;
        }

        /// <summary>One good an NPC vendor sells: an item/species id and its coin price.</summary>
        public class ShopOffer
        {
            public string Id;
            public long Price;
        }

        /// <summary>Parse a shop offer array (sells/recipes/books) → ShopOffer[] (null/empty → null).</summary>
        private static ShopOffer[] ParseOffers(JArray arr)
        {
            if (arr == null || arr.Count == 0) return null;
            var offers = new ShopOffer[arr.Count];
            for (int i = 0; i < arr.Count; i++)
                offers[i] = new ShopOffer
                {
                    Id = arr[i]["id"]?.Value<string>(),
                    Price = arr[i]["price"]?.Value<long>() ?? 0,
                };
            return offers;
        }

        /// <summary>
        /// One weapon move (an input slot's attack). The kind maps to a PlayerToolAnimator
        /// profile + a hit geometry; the server validates only move-existence + reach.
        /// </summary>
        public class MoveDef
        {
            public string Kind;       // "swing" | "stab" | "sweep"
            public int Damage;
            public float ArcDegrees;
            public float Reach;
            public float SwingTime;
            public int MaxTargets;
            public int CooldownTicks;
        }

        public class EntityDef
        {
            public string Id;
            public string Name;
            public string Category;
            public string EntityType; // "item", "occupant", or "placeable"

            // Sprite dimensions (target size in pixels)
            public int SpriteW;
            public int SpriteH;

            // Inventory properties
            public bool Stackable;
            public int MaxStack = 99;
            public int SellPrice;
            public int BuyPrice;

            // Item tags (material/food/metal/…): what vendor Buys filters match against
            // (an entry in shop.buys matches the item id OR any tag — mirrors server shopBuysItem).
            public string[] Tags;

            // Walk-over magnet exclusion: deliberate-E-only pickups (fresh tree fruit)
            public bool NoAutoPickup;

            // Bug-food value when this item lies on the ground (carrion). Drives the
            // join-time food-registry hydration (the rotten_ prefix can't cover carrion).
            public int FoodValue;

            // Armor properties (category = "armor"): equipment slot + the
            // CharacterComposer overlay layer-set name ("" = invisible, e.g. accessories)
            public string ArmorSlot;
            public string Overlay;

            // Tool properties
            public string ToolType;
            public int ToolTier;
            public float Reach;
            public float MiningSpeed;
            public int Durability;

            // NET sweep properties (top-level — nets have one move; weapons use Moves).
            // The catch area is a swept sector (ArcDegrees x Reach); cap is per-swing.
            public float ArcDegrees;
            public float SwingTime;
            public int CatchCap;

            // WEAPON movesets keyed by input slot ("primary" = left, "secondary" = right).
            public Dictionary<string, MoveDef> Moves;

            /// <summary>Resolve a weapon move; null for non-weapons / unknown names.</summary>
            public MoveDef GetMove(string name)
            {
                if (Moves == null || string.IsNullOrEmpty(name)) return null;
                return Moves.TryGetValue(name, out var m) ? m : null;
            }

            // Consumable
            public string Effect;

            // Seed properties - places a crop when used on garden_plot
            public string PlacesCrop;

            // Optional: borrow another entity's Objects/ sprite as this item's display
            // sprite (icon/drop) when the ids mismatch. See GetItemSprite.
            public string IconFrom;

            // Tool-use cooldown in server ticks (10Hz); 0 = server default (3).
            public int CooldownTicks;

            // World presence (null for inventory-only items)
            public WorldData World;
        }

        #endregion

        private static Dictionary<string, EntityDef> _entities;
        private static Dictionary<string, Sprite> _spriteCache;
        private static Sprite[] _breakStageSprites;
        // Species id -> sprite_id (from the published Data/species.json): bug slots store
        // SPECIES ids, so inventory display needs this map to find Bugs/{sprite_id}.
        private static Dictionary<string, string> _speciesSprites;

        /// <summary>
        /// Per-species client config from the PUBLISHED species.json. HASH-BEARING:
        /// movement_style and flies_over_fences feed the deterministic per-bug sim —
        /// same-build clients parse the same published file (the established class;
        /// publish_entities.py is the drift tripwire). Replaces MovementFactory's
        /// hardcoding so a new species is one data row + a sprite ("dragonfly = pure
        /// data").
        /// </summary>
        public class SpeciesInfo
        {
            public string SpriteId;
            public string MovementStyle = "";       // brownian | gliding | darting | crawling
            public string PlayerReaction = "ignore";
            public float ReactionRadius;
            public bool FliesOverFences;
            public string NetSize = "small";

            // Display fields (the bug info card; freely known tier)
            public string Name = "";
            public string Description = "";
            public int SellPrice;

            // Combat: legacy top-level fields (kept for back-compat). Prefer Attack (the data-driven profile).
            public int AttackDamage;
            public float AttackCooldown;

            // The data-driven attack profile (mirrors the server's attack{} block). Null = this bug can't
            // hurt the player. The authority reads Range + TelegraphSecs for its per-species detect/wind-up.
            public AttackInfo Attack;

            // Segmented crawlers (centipede/millipede): which body/tail art set to string behind the head,
            // and a render-scale multiplier so a giant tier is visibly bigger. SpriteFamily null → the
            // legacy centipede/millipede fallback in CentipedeTrail.
            public string SpriteFamily;
            public float RenderScale = 1f;

            // Life-stage nursery sprites (the nursery panel resolves each stage's sprite by id). A non-empty
            // PupaSpriteId means the species PUPATES (egg->larva->pupa->adult); else egg->larva->adult.
            public string EggSpriteId;
            public string LarvaSpriteId;
            public string PupaSpriteId;

            // Plain, per-species stage LABELS for the nursery panel (display-only — read only by the UI,
            // never by the sim, so they do NOT enter the state hash). The larva "form" is species-specific
            // (fly=maggots, wasp/beetle=grubs, butterfly=caterpillars, centi/millipede=young); butterfly
            // pupa=chrysalises. BroodLabel is the section's umbrella word — "Brood" only where it fits a
            // true nest/hive. Null → the panel falls back to eggs / larvae / pupae.
            public string LarvaName;
            public string PupaName;
            public string BroodLabel;
        }

        /// <summary>Client mirror of the server AttackConfig (species.json "attack"). Only the fields the
        /// authority needs to run per-individual detection + the wind-up telegraph.</summary>
        public class AttackInfo
        {
            public string Style = "contact"; // "contact" | "lunge"
            public int Damage;
            public float Range = 1.5f;        // detection range
            public float TelegraphSecs;       // per-species wind-up before the strike (0 = instant)
            public float AggroEnter;
            public float AggroExit;
            // ATTACK-MOVEMENT knobs (the "solo divers within a bigger swarm" — BugAgent reads these to hover +
            // swoop). Hash-bearing sim data, like movement_style. 0 = a sensible default.
            public float Standoff;            // cells the hovering cloud keeps off the player
            public float DivePeriodSecs;      // each bug's dive cycle (staggered per bug → 1-2 diving at once)
            public float DiveSecs;            // how long a swoop lasts
            // STING knobs (SwarmManager reads these to pace the strike reports; the server ignores them).
            public int AttackTokens;          // max concurrent stings reported per swarm (1-2)
            public float DiveCooldownSecs;    // per-bug rest between its sting reports
        }
        private static Dictionary<string, SpeciesInfo> _species;
        private static bool _initialized;

        /// <summary>Published per-species config (null for unknown ids).</summary>
        public static SpeciesInfo GetSpecies(string speciesId)
        {
            EnsureInitialized();
            return _species != null && _species.TryGetValue(speciesId, out var info) ? info : null;
        }

        /// <summary>All known species ids, sorted (for the debug spawner picker). Empty if not loaded.</summary>
        public static List<string> AllSpeciesIds()
        {
            EnsureInitialized();
            var ids = new List<string>();
            if (_species != null) ids.AddRange(_species.Keys);
            ids.Sort();
            return ids;
        }

        #region Initialization

        private static void EnsureInitialized()
        {
            if (_initialized) return;

            _entities = new Dictionary<string, EntityDef>();
            _spriteCache = new Dictionary<string, Sprite>();

            int itemCount = LoadEntityFile("Data/entities/items", "item");
            int occupantCount = LoadEntityFile("Data/entities/occupants", "occupant");
            int placeableCount = LoadEntityFile("Data/entities/placeables", "placeable");
            LoadSpeciesSprites();

            // Load break stage sprites
            _breakStageSprites = new Sprite[4];
            for (int i = 0; i < 4; i++)
            {
                _breakStageSprites[i] = Resources.Load<Sprite>($"Effects/break_stage_{i + 1}");
            }

            _initialized = true;
            Debug.Log($"[EntityDatabase] Loaded {itemCount} items, {occupantCount} occupants, {placeableCount} placeables");
        }

        /// <summary>
        /// Load the species id -> sprite_id map from the published Data/species.json
        /// (e.g. butterfly_meadow -> butterfly_common). Missing file = empty map (the
        /// GetItemSprite fallback then tries Bugs/{species id} directly).
        /// </summary>
        private static void LoadSpeciesSprites()
        {
            _speciesSprites = new Dictionary<string, string>();
            _species = new Dictionary<string, SpeciesInfo>();
            var textAsset = Resources.Load<TextAsset>("Data/species");
            if (textAsset == null)
            {
                Debug.LogWarning("[EntityDatabase] Data/species.json not found — bug-slot icons fall back to Bugs/{species id}");
                return;
            }
            try
            {
                var root = JObject.Parse(textAsset.text);
                foreach (var prop in root.Properties())
                {
                    if (prop.Name.StartsWith("_")) continue;
                    var obj = prop.Value as JObject;
                    var spriteId = obj?["sprite_id"]?.Value<string>();
                    _speciesSprites[prop.Name] = string.IsNullOrEmpty(spriteId) ? prop.Name : spriteId;

                    _species[prop.Name] = new SpeciesInfo
                    {
                        SpriteId = _speciesSprites[prop.Name],
                        MovementStyle = obj?["movement_style"]?.Value<string>() ?? "",
                        PlayerReaction = obj?["player_reaction"]?.Value<string>() ?? "ignore",
                        ReactionRadius = obj?["reaction_radius"]?.Value<float>() ?? 0f,
                        FliesOverFences = obj?["flies_over_fences"]?.Value<bool>() ?? false,
                        Name = obj?["name"]?.Value<string>() ?? prop.Name,
                        Description = obj?["description"]?.Value<string>() ?? "",
                        SellPrice = obj?["sell_price"]?.Value<int>() ?? 0,
                        NetSize = obj?["net_size"]?.Value<string>() ?? "small",
                        AttackDamage = obj?["attack_damage"]?.Value<int>() ?? 0,
                        AttackCooldown = obj?["attack_cooldown"]?.Value<float>() ?? 0f,
                        SpriteFamily = obj?["sprite_family"]?.Value<string>(),
                        RenderScale = obj?["render_scale"]?.Value<float>() ?? 1f,
                        EggSpriteId = obj?["egg_sprite_id"]?.Value<string>(),
                        LarvaSpriteId = obj?["larva_sprite_id"]?.Value<string>(),
                        PupaSpriteId = obj?["pupa_sprite_id"]?.Value<string>(),
                        LarvaName = obj?["larva_name"]?.Value<string>(),
                        PupaName = obj?["pupa_name"]?.Value<string>(),
                        BroodLabel = obj?["brood_label"]?.Value<string>(),
                        Attack = ParseAttack(obj),
                    };
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[EntityDatabase] Failed to parse Data/species: {e.Message}");
            }
        }

        /// <summary>Parse the data-driven attack{} profile; fall back to synthesizing one from the legacy
        /// top-level attack_damage so un-migrated species still work. Null = can't hurt the player.</summary>
        private static AttackInfo ParseAttack(JObject obj)
        {
            if (obj?["attack"] is JObject a)
            {
                return new AttackInfo
                {
                    Style = a["style"]?.Value<string>() ?? "contact",
                    Damage = a["damage"]?.Value<int>() ?? 0,
                    Range = a["range"]?.Value<float>() ?? 1.5f,
                    TelegraphSecs = a["telegraph_secs"]?.Value<float>() ?? 0f,
                    AggroEnter = a["aggro_enter"]?.Value<float>() ?? 0f,
                    AggroExit = a["aggro_exit"]?.Value<float>() ?? 0f,
                    Standoff = a["standoff"]?.Value<float>() ?? 0f,
                    DivePeriodSecs = a["dive_period_secs"]?.Value<float>() ?? 0f,
                    DiveSecs = a["dive_secs"]?.Value<float>() ?? 0f,
                    AttackTokens = a["attack_tokens"]?.Value<int>() ?? 0,
                    DiveCooldownSecs = a["dive_cooldown_secs"]?.Value<float>() ?? 0f,
                };
            }
            int dmg = obj?["attack_damage"]?.Value<int>() ?? 0;
            if (dmg <= 0) return null;
            return new AttackInfo { Style = "contact", Damage = dmg, Range = 1.5f, TelegraphSecs = 0.8f, AggroEnter = 8f, AggroExit = 12f };
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
                Tags = (data["tags"] as JArray)?.ToObject<string[]>(),
                NoAutoPickup = data["no_auto_pickup"]?.Value<bool>() ?? false,
                FoodValue = data["food_value"]?.Value<int>() ?? 0,
                ToolType = data["tool_type"]?.Value<string>(),
                ToolTier = data["tool_tier"]?.Value<int>() ?? 0,
                Reach = data["reach"]?.Value<float>() ?? 0f,
                MiningSpeed = data["mining_speed"]?.Value<float>() ?? 1f,
                Durability = data["durability"]?.Value<int>() ?? 0,
                ArcDegrees = data["arc_degrees"]?.Value<float>() ?? 0f,
                SwingTime = data["swing_time"]?.Value<float>() ?? 0f,
                CatchCap = data["catch_cap"]?.Value<int>() ?? 0,
                Effect = data["effect"]?.Value<string>(),
                PlacesCrop = data["places_crop"]?.Value<string>(),
                ArmorSlot = data["armor_slot"]?.Value<string>(),
                Overlay = data["overlay"]?.Value<string>(),
                IconFrom = data["icon_from"]?.Value<string>(),
                CooldownTicks = data["cooldown_ticks"]?.Value<int>() ?? 0
            };

            // Parse sprite dimensions (required for occupants/placeables)
            var spriteW = data["sprite_w"]?.Value<int>();
            var spriteH = data["sprite_h"]?.Value<int>();
            if (spriteW.HasValue)
                entity.SpriteW = spriteW.Value;
            else if (entityType != "item")
                Debug.LogWarning($"[EntityDatabase] {id} missing sprite_w");
            if (spriteH.HasValue)
                entity.SpriteH = spriteH.Value;
            else if (entityType != "item")
                Debug.LogWarning($"[EntityDatabase] {id} missing sprite_h");

            // Parse weapon moves if present (per-move combat stats keyed by input slot)
            if (data["moves"] is JObject movesObj)
            {
                entity.Moves = new Dictionary<string, MoveDef>();
                foreach (var moveProp in movesObj.Properties())
                {
                    if (moveProp.Value is not JObject mv) continue;
                    entity.Moves[moveProp.Name] = new MoveDef
                    {
                        Kind = mv["kind"]?.Value<string>() ?? "swing",
                        Damage = mv["damage"]?.Value<int>() ?? 1,
                        ArcDegrees = mv["arc_degrees"]?.Value<float>() ?? 90f,
                        Reach = mv["reach"]?.Value<float>() ?? 2f,
                        SwingTime = mv["swing_time"]?.Value<float>() ?? 0.2f,
                        MaxTargets = mv["max_targets"]?.Value<int>() ?? 1,
                        CooldownTicks = mv["cooldown_ticks"]?.Value<int>() ?? 3
                    };
                }
            }

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
                InteractionType = data["interaction_type"]?.Value<string>(),
                CraftSlots = data["craft_slots"]?.Value<int>() ?? 0
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

            // Parse station block (material processors — menu filter + capacity display)
            var station = data["station"] as JObject;
            if (station != null)
            {
                var accepts = station["accepts"] as JArray;
                if (accepts != null)
                {
                    world.StationAccepts = new string[accepts.Count];
                    for (int i = 0; i < accepts.Count; i++)
                        world.StationAccepts[i] = accepts[i].Value<string>();
                }
                world.StationCapacity = station["capacity"]?.Value<int>() ?? 10;
            }

            // Parse container block (item storage: chests/dressers/racks)
            var container = data["container"] as JObject;
            if (container != null)
            {
                world.ContainerSlots = container["slots"]?.Value<int>() ?? 12;
                world.ContainerFilter = container["filter"]?.Value<string>() ?? "";
            }

            // Parse shop block (NPC vendor: kind + the goods it sells)
            var shop = data["shop"] as JObject;
            if (shop != null)
            {
                world.ShopKind = shop["kind"]?.Value<string>() ?? "items";
                world.ShopBuys = (shop["buys"] as JArray)?.ToObject<string[]>();
                world.ShopSells = ParseOffers(shop["sells"] as JArray);
                world.ShopRecipes = ParseOffers(shop["recipes"] as JArray);   // D26: learnable recipes
                world.ShopBooks = ParseOffers(shop["books"] as JArray);       // D26: recipe-book collections
            }

            // NPC dialogue greeting (sibling of shop)
            world.Greeting = data["greeting"]?.Value<string>();

            // Parse light block (lamps/torches glow at night)
            var light = data["light"] as JObject;
            if (light != null)
            {
                world.LightRadius = light["radius"]?.Value<float>() ?? 4f;
                world.LightIntensity = light["intensity"]?.Value<float>() ?? 1f;
                var hex = light["color"]?.Value<string>();
                if (!string.IsNullOrEmpty(hex) && ColorUtility.TryParseHtmlString(hex, out var c))
                    world.LightColor = c;
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
        /// Includes placeables and seeds (which place crops).
        /// </summary>
        public static bool IsPlaceable(string id)
        {
            var def = Get(id);
            if (def == null) return false;
            return def.EntityType == "placeable" || !string.IsNullOrEmpty(def.PlacesCrop);
        }

        /// <summary>
        /// Check if an item is a seed that places a crop.
        /// </summary>
        public static bool IsSeed(string id)
        {
            var def = Get(id);
            return def != null && !string.IsNullOrEmpty(def.PlacesCrop);
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
        /// Get target sprite size in pixels.
        /// </summary>
        public static Vector2Int GetSpriteSize(string id)
        {
            var def = Get(id);
            return new Vector2Int(def.SpriteW, def.SpriteH);
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
        /// Get the DISPLAY sprite for an item — used by inventory slots, the hotbar, the
        /// drag cursor, and floating ground drops. The item's visual IS its world sprite,
        /// scaled down by the consumer (architecture_items.md §0): resolution order is
        ///   1. Objects/{icon_from}   (explicit borrow for id mismatches, from items.json)
        ///   2. Objects/{id}          (placeables/blocks/cut flora — the original object art)
        ///   3. Items/{id}_icon       (authored icons: tools, seeds, raw resources)
        ///   4. Items/{id}            (legacy plain files)
        ///   5. Bugs/{species sprite} (BUG SLOTS store species ids — without this, caught
        ///                             flies render as invisible slots and catching looks
        ///                             broken; the species->sprite_id map comes from the
        ///                             published Data/species.json)
        /// </summary>
        public static Sprite GetItemSprite(string id)
        {
            EnsureInitialized();
            if (string.IsNullOrEmpty(id)) return null;

            string cacheKey = $"item:{id}";
            if (_spriteCache.TryGetValue(cacheKey, out var cached))
                return cached;

            Sprite sprite = null;
            if (_entities.TryGetValue(id, out var def) && !string.IsNullOrEmpty(def.IconFrom))
                sprite = Resources.Load<Sprite>($"Objects/{def.IconFrom}");
            if (sprite == null)
                sprite = Resources.Load<Sprite>($"Objects/{id}");
            if (sprite == null)
                sprite = Resources.Load<Sprite>($"Items/{id}_icon");
            if (sprite == null)
                sprite = Resources.Load<Sprite>($"Items/{id}");
            if (sprite == null)
            {
                string bugSprite = (_speciesSprites != null &&
                                    _speciesSprites.TryGetValue(id, out var mapped)) ? mapped : id;
                sprite = Resources.Load<Sprite>($"Bugs/{bugSprite}");
            }
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
