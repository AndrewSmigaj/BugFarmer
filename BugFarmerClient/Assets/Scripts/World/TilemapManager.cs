using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;
using Nakama;
using Newtonsoft.Json.Linq;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.World
{
    /// <summary>
    /// Manages chunk subscription, loading, and rendering for the tile-based world.
    /// Subscribes to chunks around the player and renders ground tiles + occupant objects.
    /// </summary>
    public class TilemapManager : MonoBehaviour
    {
        public static TilemapManager Instance { get; private set; }

        [Header("Tilemaps")]
        [SerializeField] private Tilemap groundTilemap;
        [SerializeField] private Transform occupantContainer;

        // Runtime-created animated water overlay (a second Tilemap under the same Grid, sorted just above the
        // ground water tiles). Null if the WaterAnimated shader is missing → water stays static (graceful).
        private Tilemap _waterTilemap;
        private Material _waterMat;   // the runtime WaterAnimated material (driven by the fields below)

        // Shore mask for foam: a 256² one-texel-per-cell texture (3-state: water=1, known-land=0.5,
        // unloaded=0) bound to the water material; the shader draws foam where water borders known land, in
        // WORLD space (no tile seams). Built from LOADED chunks (water is lazy per-chunk), rebuilt when dirty.
        private const int ShoreN = 256;
        private Texture2D _shoreMask;
        private Color32[] _shorePixels;
        private bool _shoreDirty;

        [Header("Water look — select THIS GameObject to tweak the pond live in Play mode")]
        [Tooltip("Sideways refraction of the water texture. Small; 0 = flat.")]
        [SerializeField] private float waterDistortion = 0.05f;
        [Tooltip("Ripple density (higher = finer, busier ripples).")]
        [SerializeField] private float waterFrequency = 4.19f;
        [Tooltip("Overall animation speed.")]
        [SerializeField] private float waterSpeed = 0.66f;
        [Tooltip("Directional drift. (0,0) = calm pond; set one axis for a flowing current.")]
        [SerializeField] private Vector2 waterScrollDir = new Vector2(0.24f, 0.45f);
        [Tooltip("Moving light ripple. 0 = off (default — it reads as a checkerboard grid on tiled water).")]
        [SerializeField, Range(0f, 0.5f)] private float waterShimmer = 0f;
        [Tooltip("Occasional bright sparkle glints. 0 = off (default — they march in stepped squares).")]
        [SerializeField, Range(0f, 1f)] private float waterSparkle = 0f;
        [Tooltip("Foam band width at the shore, in cells. 0 = no foam.")]
        [SerializeField, Range(0f, 2f)] private float waterFoamWidth = 0.7f;
        [Tooltip("Foam swash animation speed.")]
        [SerializeField] private float waterFoamSpeed = 1f;

        [Header("Settings")]
        [SerializeField] private int viewDistanceChunks = 2; // Subscribe to 5x5 grid of chunks
        [SerializeField] private float chunkCheckInterval = 0.5f;
        [SerializeField] private float cellSize = 1f; // World units per cell (matches PPU 16)

        // Constants matching server zone.go
        public const int ChunkSize = 32;

        // Chunk tracking
        private HashSet<Vector2Int> _subscribedChunks = new HashSet<Vector2Int>();
        private Dictionary<Vector2Int, ChunkRenderData> _loadedChunks = new Dictionary<Vector2Int, ChunkRenderData>();

        // Phase 1b: the ZONE-COMPLETE blocks_bugs collision set (every cell whose occupant blocks bugs,
        // across the WHOLE zone — not just loaded chunks). The bug sim reads THIS so a fly near a fence
        // collides identically on every client regardless of camera. Hydrated by OpCodeZoneCollisionMap on
        // join/resync, then kept in step by frontier-gated OCCUPANT_BLOCKS_BUGS events (SetBlocksBugs).
        // Rendering + player collision stay view-scoped (_loadedChunks) — only the bug sim went zone-wide.
        private readonly HashSet<Vector2Int> _blocksBugsZoneWide = new HashSet<Vector2Int>();
        private bool _collisionMapReady;
        /// <summary>True once the zone-wide blocks_bugs map has arrived — the bug sim gates on this.</summary>
        public bool CollisionMapReady => _collisionMapReady;

        // Authored "roof" (underground / no-sun) cell set, hydrated by OpCodeZoneRoofMap on join/resync.
        // COSMETIC — read only by the underground lighting overlay (DarknessOverlay); never a sim input.
        private readonly HashSet<Vector2Int> _roofZoneWide = new HashSet<Vector2Int>();
        /// <summary>True if the cell is authored underground/roofed (for the darkness overlay).</summary>
        public bool IsRoofCell(Vector2Int cell) => _roofZoneWide.Contains(cell);
        /// <summary>Bumps whenever the darkness inputs (collision map or roof map) change, so the
        /// DarknessOverlay knows to recompute. Cosmetic-only signal.</summary>
        public int DarknessDataVersion { get; private set; }
        private Vector2Int _lastPlayerChunk = new Vector2Int(int.MinValue, int.MinValue);
        private float _lastChunkCheck;

        // Occupant GameObjects by global cell position
        private Dictionary<Vector2Int, GameObject> _occupantObjects = new Dictionary<Vector2Int, GameObject>();

        // Breaking visuals by global cell position
        private Dictionary<Vector2Int, BreakingVisual> _breakingVisuals = new Dictionary<Vector2Int, BreakingVisual>();

        // "Needs water" droplets over dry fruit trees (OpCode 51), by tree anchor cell
        private Dictionary<Vector2Int, WaterDroplet> _waterDroplets = new Dictionary<Vector2Int, WaterDroplet>();

        // Last-known tree water state per anchor cell (OpCode 51): droplet visibility is
        // recomputed from this + the current day, so rollovers refresh with no message.
        private Dictionary<Vector2Int, TreeWaterUpdateMessage> _treeWaterStates = new Dictionary<Vector2Int, TreeWaterUpdateMessage>();
        private long _lastDropletDay = -1;

        // Canopy fruit overlays (OpCode 93) — SEPARATE GameObjects keyed by anchor cell,
        // NEVER children of the occupant GO: occupant objects are POOLED (RenderOccupant/
        // UnloadChunk ReturnToPool) and child fruit would ride a pooled tree into its next
        // life. Same reasoning as the droplet.
        private Dictionary<Vector2Int, GameObject> _fruitOverlays = new Dictionary<Vector2Int, GameObject>();
        private Dictionary<Vector2Int, TreeFruitUpdateMessage> _treeFruitStates = new Dictionary<Vector2Int, TreeFruitUpdateMessage>();

        // Object pooling for occupants
        private Stack<GameObject> _occupantPool = new Stack<GameObject>();

        // Events
        public event System.Action<int, int> OnChunkLoaded;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Start()
        {
            // Ground tiles must receive Light2D (day/night + lamps) like everything else
            if (groundTilemap != null)
                LitMaterials.Apply(groundTilemap.GetComponent<Renderer>());

            SetupWaterTilemap();

            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData += HandleMatchData;
                Debug.Log("[TilemapManager] Subscribed to WorldManager.OnMatchData");
            }
            else
            {
                Debug.LogError("[TilemapManager] WorldManager.Instance is null!");
            }

            // Load break stage sprites for visual feedback
            var breakSprites = EntityDatabase.GetBreakStageSprites();
            if (breakSprites != null && breakSprites.Length > 0)
            {
                BreakingVisual.SetBreakStages(breakSprites);
                Debug.Log($"[TilemapManager] Loaded {breakSprites.Length} break stage sprites");
            }
            else
            {
                Debug.LogWarning("[TilemapManager] No break stage sprites found in Resources/Sprites/Effects/");
            }
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
            }
        }

        private void Update()
        {
            // Droplets are day-dependent ("waterable today"): when the apparent day
            // rolls over, re-evaluate every tracked tree with NO new message needed.
            long day = DayNightController.CurrentDayIndex;
            if (day != _lastDropletDay)
            {
                _lastDropletDay = day;
                RefreshAllDroplets();
            }

            if (_shoreDirty && _waterMat != null)
            {
                _shoreDirty = false;
                RebuildShoreMask();
            }

            if (Time.time - _lastChunkCheck < chunkCheckInterval)
                return;
            _lastChunkCheck = Time.time;

            UpdateChunkSubscriptions();
        }

        #region Chunk Subscription

        private void UpdateChunkSubscriptions()
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null)
                return;

            // Find local player
            var player = FindObjectOfType<Player.PlayerController>();
            if (player == null)
                return;

            Vector2Int playerChunk = WorldToChunk(player.transform.position);
            if (playerChunk == _lastPlayerChunk)
                return;

            _lastPlayerChunk = playerChunk;

            // Calculate desired chunks (5x5 grid centered on player)
            var desiredChunks = new HashSet<Vector2Int>();
            for (int dy = -viewDistanceChunks; dy <= viewDistanceChunks; dy++)
            {
                for (int dx = -viewDistanceChunks; dx <= viewDistanceChunks; dx++)
                {
                    desiredChunks.Add(new Vector2Int(playerChunk.x + dx, playerChunk.y + dy));
                }
            }

            // Subscribe to new chunks
            foreach (var chunk in desiredChunks)
            {
                if (!_subscribedChunks.Contains(chunk))
                {
                    SendChunkSubscribe(chunk.x, chunk.y);
                    _subscribedChunks.Add(chunk);
                }
            }

            // Unsubscribe from distant chunks
            var toRemove = new List<Vector2Int>();
            foreach (var chunk in _subscribedChunks)
            {
                if (!desiredChunks.Contains(chunk))
                {
                    SendChunkUnsub(chunk.x, chunk.y);
                    toRemove.Add(chunk);
                    UnloadChunk(chunk);
                }
            }
            foreach (var chunk in toRemove)
            {
                _subscribedChunks.Remove(chunk);
            }
        }

        private void SendChunkSubscribe(int cx, int cy)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || match == null)
                return;

            var msg = new ChunkSubscribeMessage { chunk_x = cx, chunk_y = cy };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.ChunkSubscribe, json);
            Debug.Log($"[TilemapManager] Subscribe chunk {cx},{cy}");
        }

        private void SendChunkUnsub(int cx, int cy)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || match == null)
                return;

            var msg = new ChunkSubscribeMessage { chunk_x = cx, chunk_y = cy };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.ChunkUnsub, json);
            Debug.Log($"[TilemapManager] Unsubscribe chunk {cx},{cy}");
        }

        #endregion

        #region Message Handling

        private void HandleMatchData(IMatchState state)
        {
            switch (state.OpCode)
            {
                case OpCodes.ChunkData:
                    HandleChunkData(state);
                    break;
                case OpCodes.WorldUpdate:
                    HandleWorldUpdate(state);
                    break;
                case OpCodes.BreakProgress:
                    HandleBreakProgress(state);
                    break;
                case OpCodes.CropUpdate:
                    HandleCropUpdate(state);
                    break;
                case OpCodes.TreeWaterUpdate:
                    HandleTreeWaterUpdate(state);
                    break;
                case OpCodes.TreeFruitUpdate:
                    HandleTreeFruitUpdate(state);
                    break;
            }
        }

        /// <summary>
        /// OpCode 51: a fruit tree's tank state changed. The droplet means "this tree can
        /// drink TODAY": water_level below the cap AND not already manually watered this
        /// apparent day. Visibility is re-derived at every day rollover (see Update) —
        /// last_water_day is a day index, so no extra server message is needed.
        /// </summary>
        private void HandleTreeWaterUpdate(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<TreeWaterUpdateMessage>(json);
            if (msg == null) return;

            var cell = new Vector2Int(msg.grid_x, msg.grid_y);
            _treeWaterStates[cell] = msg;
            RefreshDroplet(cell, msg);
        }

        /// <summary>Show/hide the droplet for one tree from its last-known water state.</summary>
        private void RefreshDroplet(Vector2Int cell, TreeWaterUpdateMessage msg)
        {
            bool waterableToday = msg.water_level < 3 &&
                                  msg.last_water_day != DayNightController.CurrentDayIndex;

            if (!waterableToday)
            {
                if (_waterDroplets.TryGetValue(cell, out var existing) && existing != null)
                    Destroy(existing.gameObject);
                _waterDroplets.Remove(cell);
                return;
            }

            if (_waterDroplets.ContainsKey(cell)) return;
            if (!_occupantObjects.TryGetValue(cell, out var occupantGo) || occupantGo == null) return;

            var sr = occupantGo.GetComponent<SpriteRenderer>();
            float topY = sr != null ? sr.bounds.max.y + 0.15f : cell.y + 2f;
            float midX = sr != null ? sr.bounds.center.x : cell.x + 0.5f;

            var go = new GameObject($"WaterDroplet_{cell.x}_{cell.y}");
            var droplet = go.AddComponent<WaterDroplet>();
            droplet.AttachAbove(new Vector3(midX, topY, 0f));
            _waterDroplets[cell] = droplet;
        }

        /// <summary>Re-evaluate every tracked tree's droplet (called at the day rollover).</summary>
        private void RefreshAllDroplets()
        {
            foreach (var kv in _treeWaterStates)
                RefreshDroplet(kv.Key, kv.Value);
        }

        /// <summary>
        /// OpCode 93: a tree's canopy fruit count changed (grew / fell / picked / knocked).
        /// Rebuild the fruit overlay for that tree.
        /// </summary>
        private void HandleTreeFruitUpdate(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<TreeFruitUpdateMessage>(json);
            if (msg == null) return;

            var cell = new Vector2Int(msg.grid_x, msg.grid_y);
            _treeFruitStates[cell] = msg;
            RefreshFruitOverlay(cell, msg);
        }

        /// <summary>
        /// (Re)build the canopy fruit overlay for one tree: a separate GameObject with one
        /// small fruit sprite per count, at DETERMINISTIC hash-jittered anchors over the
        /// upper 60% of the tree sprite's bounds — every client renders identical canopies,
        /// and a count change only ever adds/removes the highest-index fruit visually.
        /// </summary>
        private void RefreshFruitOverlay(Vector2Int cell, TreeFruitUpdateMessage msg)
        {
            if (_fruitOverlays.TryGetValue(cell, out var old) && old != null)
                Destroy(old);
            _fruitOverlays.Remove(cell);

            if (msg.fruit_count <= 0)
            {
                _treeFruitStates.Remove(cell);
                return;
            }

            if (!_occupantObjects.TryGetValue(cell, out var occupantGo) || occupantGo == null)
                return; // tree not rendered yet — the chunk re-send refreshes us on load

            var treeSr = occupantGo.GetComponent<SpriteRenderer>();
            if (treeSr == null) return;

            var fruitSprite = EntityDatabase.GetItemSprite(msg.fruit_type);
            if (fruitSprite == null) return;

            var bounds = treeSr.bounds;
            var overlay = new GameObject($"TreeFruit_{cell.x}_{cell.y}");
            overlay.transform.position = bounds.center;

            const float fruitSize = 0.35f; // world units
            float spriteWorld = Mathf.Max(fruitSprite.bounds.size.x, fruitSprite.bounds.size.y);
            float scale = spriteWorld > 0f ? fruitSize / spriteWorld : 1f;

            for (int i = 0; i < msg.fruit_count; i++)
            {
                // Deterministic per-(cell, index) jitter — stable across clients/frames
                float hx = Hash01(cell.x * 73856093 ^ cell.y * 19349663 ^ (i * 83492791));
                float hy = Hash01(cell.x * 19349663 ^ cell.y * 83492791 ^ (i * 73856093 + 1));
                float x = Mathf.Lerp(bounds.min.x + bounds.size.x * 0.18f,
                                     bounds.max.x - bounds.size.x * 0.18f, hx);
                float y = Mathf.Lerp(bounds.min.y + bounds.size.y * 0.42f,
                                     bounds.max.y - bounds.size.y * 0.08f, hy);

                var fruitGo = new GameObject($"fruit_{i}");
                fruitGo.transform.SetParent(overlay.transform, false);
                fruitGo.transform.position = new Vector3(x, y, -0.15f);
                fruitGo.transform.localScale = new Vector3(scale, scale, 1f);

                var sr = fruitGo.AddComponent<SpriteRenderer>();
                sr.sprite = fruitSprite;
                sr.sortingLayerName = "Occupants";
                sr.sortingOrder = -cell.y + 1; // just in front of the canopy
                LitMaterials.Apply(sr);
            }

            _fruitOverlays[cell] = overlay;
        }

        private static float Hash01(int n)
        {
            unchecked
            {
                uint x = (uint)n;
                x = (x ^ 61u) ^ (x >> 16);
                x *= 9u;
                x ^= x >> 4;
                x *= 0x27d4eb2du;
                x ^= x >> 15;
                return (x & 0xFFFFFF) / (float)0x1000000;
            }
        }

        /// <summary>Destroy the fruit overlay + droplet at a cell (occupant removed/unloaded).</summary>
        private void RemoveTreeVisuals(Vector2Int cell, bool forgetState)
        {
            if (_fruitOverlays.TryGetValue(cell, out var overlay) && overlay != null)
                Destroy(overlay);
            _fruitOverlays.Remove(cell);

            if (_waterDroplets.TryGetValue(cell, out var droplet) && droplet != null)
                Destroy(droplet.gameObject);
            _waterDroplets.Remove(cell);

            if (forgetState)
            {
                _treeFruitStates.Remove(cell);
                _treeWaterStates.Remove(cell);
            }
        }

        private void HandleChunkData(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var chunk = ParseChunkData(json);
            if (chunk == null)
            {
                Debug.LogError("[TilemapManager] Failed to parse ChunkData");
                return;
            }

            var chunkPos = new Vector2Int(chunk.ChunkX, chunk.ChunkY);
            _loadedChunks[chunkPos] = chunk;

            RenderChunk(chunk);
            OnChunkLoaded?.Invoke(chunk.ChunkX, chunk.ChunkY);
            Debug.Log($"[TilemapManager] Loaded chunk {chunk.ChunkX},{chunk.ChunkY}");
        }

        private void HandleWorldUpdate(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var root = JObject.Parse(json);

            int gx = root["grid_x"]?.Value<int>() ?? 0;
            int gy = root["grid_y"]?.Value<int>() ?? 0;
            var cellPos = new Vector2Int(gx, gy);

            // Update ground if provided
            string ground = root["ground"]?.Value<string>();
            if (!string.IsNullOrEmpty(ground))
            {
                SetGroundTile(cellPos, ground);
            }

            // Update occupant only if the field is present in the JSON
            // Missing field = no change, explicit null = removal, object = placement
            if (root.Property("occupant") != null)
            {
                var occupantToken = root["occupant"];
                if (occupantToken != null && occupantToken.Type != JTokenType.Null)
                {
                    // Placement - parse and compute footprint
                    string id = occupantToken["id"]?.Value<string>();
                    int dir = occupantToken["dir"]?.Value<int>() ?? 0;
                    bool anchor = occupantToken["anchor"]?.Value<bool>() ?? false;

                    if (anchor && !string.IsNullOrEmpty(id))
                    {
                        // This is an anchor cell - compute and fill all footprint cells
                        var footprint = EntityDatabase.GetFootprint(id, dir);
                        for (int dy = 0; dy < footprint.y; dy++)
                        {
                            for (int dx = 0; dx < footprint.x; dx++)
                            {
                                var fpCellPos = new Vector2Int(gx + dx, gy + dy);
                                bool isAnchor = (dx == 0 && dy == 0);
                                UpdateOccupantCellData(fpCellPos, id, dir, isAnchor);

                                // Only render at anchor cell
                                if (isAnchor)
                                {
                                    var occData = new OccupantCellData
                                    {
                                        Occupant = new PlacedOccupant { id = id, dir = dir, anchor = true }
                                    };
                                    RenderOccupant(fpCellPos, occData);
                                }
                            }
                        }
                    }
                }
                else
                {
                    // Explicit null = removal
                    ClearOccupantAndFootprint(gx, gy);
                }
            }
            // If "occupant" key is missing, don't touch occupant (ground-only update)
        }

        /// <summary>
        /// Update occupant cell data in loaded chunk (for real-time sync).
        /// </summary>
        private void UpdateOccupantCellData(Vector2Int cellPos, string id, int dir, bool anchor)
        {
            int cx = cellPos.x / ChunkSize;
            int cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (!_loadedChunks.TryGetValue(chunkPos, out var chunk))
                return;

            int lx = cellPos.x - cx * ChunkSize;
            int ly = cellPos.y - cy * ChunkSize;

            if (ly < 0 || ly >= ChunkSize || lx < 0 || lx >= ChunkSize)
                return;

            if (chunk.Occupants[ly] == null)
                chunk.Occupants[ly] = new OccupantCellData[ChunkSize];

            chunk.Occupants[ly][lx] = new OccupantCellData
            {
                Occupant = new PlacedOccupant { id = id, dir = dir, anchor = anchor }
            };
        }

        /// <summary>
        /// Clear an occupant and all its footprint cells from chunk data.
        /// </summary>
        private void ClearOccupantAndFootprint(int anchorX, int anchorY)
        {
            var anchorPos = new Vector2Int(anchorX, anchorY);

            // Get existing occupant data (including direction for footprint calculation)
            int cx = anchorX / ChunkSize;
            int cy = anchorY / ChunkSize;
            if (anchorX < 0 && anchorX % ChunkSize != 0) cx--;
            if (anchorY < 0 && anchorY % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (!_loadedChunks.TryGetValue(chunkPos, out var chunk))
            {
                // Chunk not loaded, just remove render object if exists
                if (_occupantObjects.TryGetValue(anchorPos, out var obj))
                {
                    ReturnToPool(obj);
                    _occupantObjects.Remove(anchorPos);
                }
                RemoveBreakingVisual(anchorPos);
                return;
            }

            int lx = anchorX - cx * ChunkSize;
            int ly = anchorY - cy * ChunkSize;

            var oldOcc = chunk.Occupants[ly]?[lx]?.Occupant;
            if (oldOcc == null || string.IsNullOrEmpty(oldOcc.id))
            {
                // No occupant data, just clear render
                if (_occupantObjects.TryGetValue(anchorPos, out var obj))
                {
                    ReturnToPool(obj);
                    _occupantObjects.Remove(anchorPos);
                }
                RemoveBreakingVisual(anchorPos);
                return;
            }

            // Look up footprint from entity database
            var footprint = EntityDatabase.GetFootprint(oldOcc.id, oldOcc.dir);

            // Clear all footprint cells
            for (int dy = 0; dy < footprint.y; dy++)
            {
                for (int dx = 0; dx < footprint.x; dx++)
                {
                    var fpCellPos = new Vector2Int(anchorX + dx, anchorY + dy);
                    ClearOccupantCellData(fpCellPos);
                }
            }

            // Remove render object at anchor
            if (_occupantObjects.TryGetValue(anchorPos, out var anchorObj))
            {
                ReturnToPool(anchorObj);
                _occupantObjects.Remove(anchorPos);
            }
            RemoveBreakingVisual(anchorPos);
        }

        /// <summary>
        /// Clear occupant cell data in loaded chunk.
        /// </summary>
        private void ClearOccupantCellData(Vector2Int cellPos)
        {
            int cx = cellPos.x / ChunkSize;
            int cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (!_loadedChunks.TryGetValue(chunkPos, out var chunk))
                return;

            int lx = cellPos.x - cx * ChunkSize;
            int ly = cellPos.y - cy * ChunkSize;

            if (ly < 0 || ly >= ChunkSize || lx < 0 || lx >= ChunkSize)
                return;

            if (chunk.Occupants[ly] != null)
            {
                chunk.Occupants[ly][lx] = new OccupantCellData { IsEmpty = true };
            }
        }

        private void HandleBreakProgress(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            Debug.Log($"[TilemapManager] BreakProgress received: {json}");

            var msg = JsonUtility.FromJson<BreakProgressMessage>(json);
            if (msg == null)
            {
                Debug.LogWarning("[TilemapManager] Failed to parse BreakProgressMessage");
                return;
            }

            var cellPos = new Vector2Int(msg.grid_x, msg.grid_y);
            Debug.Log($"[TilemapManager] BreakProgress at {cellPos}: {msg.current_hp}/{msg.max_hp}");

            if (msg.current_hp <= 0)
            {
                // Breaking complete - remove visual
                RemoveBreakingVisual(cellPos);
            }
            else
            {
                // Show/update breaking progress
                ShowBreakingProgress(cellPos, msg.current_hp, msg.max_hp);
            }
        }

        private void HandleCropUpdate(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<CropUpdateMessage>(json);
            if (msg == null)
            {
                Debug.LogWarning("[TilemapManager] Failed to parse CropUpdateMessage");
                return;
            }

            var cellPos = new Vector2Int(msg.grid_x, msg.grid_y);

            // Crop STAGE visualization: re-render the cell as the stage entity
            // (plant_tomato_stage{n} etc. — each stage has its own sprite + size, so a sprout
            // really is small and the ripe plant tall). Falls back to the base plant sprite
            // when stage art is missing.
            if (!_occupantObjects.TryGetValue(cellPos, out var go) || go == null)
                return;
            var clickTarget = go.GetComponent<OccupantClickTarget>();
            string curId = clickTarget != null ? clickTarget.OccupantId : null;
            if (string.IsNullOrEmpty(curId))
                return;

            // Base plant id: strip a previous "_stageN" suffix if present
            int stageIdx = curId.IndexOf("_stage");
            string baseId = stageIdx >= 0 ? curId.Substring(0, stageIdx) : curId;
            string stageId = $"{baseId}_stage{msg.stage}";
            string renderId = EntityDatabase.GetWorldSprite(stageId) != null ? stageId : baseId;
            if (renderId == curId)
                return; // already showing this stage

            RenderOccupant(cellPos, new OccupantCellData
            {
                IsEmpty = false,
                Occupant = new Networking.PlacedOccupant { id = renderId, anchor = true }
            });
        }

        #endregion

        #region Chunk Parsing

        private ChunkRenderData ParseChunkData(string json)
        {
            try
            {
                var root = JObject.Parse(json);
                var chunk = new ChunkRenderData
                {
                    ChunkX = root["chunk_x"]?.Value<int>() ?? 0,
                    ChunkY = root["chunk_y"]?.Value<int>() ?? 0,
                    Ground = new string[ChunkSize][],
                    Occupants = new OccupantCellData[ChunkSize][]
                };

                // Parse ground 2D array - server uses [y][x] ordering
                var groundArray = root["ground"] as JArray;
                for (int y = 0; y < ChunkSize && y < groundArray?.Count; y++)
                {
                    chunk.Ground[y] = new string[ChunkSize];
                    var row = groundArray[y] as JArray;
                    for (int x = 0; x < ChunkSize && x < row?.Count; x++)
                    {
                        chunk.Ground[y][x] = row[x]?.Value<string>() ?? "grass";
                    }
                }

                // Parse occupants 2D array - polymorphic (null, "@", or {id, dir})
                var occupantsArray = root["occupants"] as JArray;
                for (int y = 0; y < ChunkSize && y < occupantsArray?.Count; y++)
                {
                    chunk.Occupants[y] = new OccupantCellData[ChunkSize];
                    var row = occupantsArray[y] as JArray;
                    for (int x = 0; x < ChunkSize && x < row?.Count; x++)
                    {
                        chunk.Occupants[y][x] = ParseOccupantCell(row[x]);
                    }
                }

                return chunk;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[TilemapManager] ParseChunkData error: {e.Message}");
                return null;
            }
        }

        private OccupantCellData ParseOccupantCell(JToken token)
        {
            if (token == null || token.Type == JTokenType.Null)
            {
                return new OccupantCellData { IsEmpty = true };
            }

            if (token.Type == JTokenType.Object)
            {
                var obj = token as JObject;
                return new OccupantCellData
                {
                    Occupant = new PlacedOccupant
                    {
                        id = obj["id"]?.Value<string>(),
                        dir = obj["dir"]?.Value<int>() ?? 0,
                        anchor = obj["anchor"]?.Value<bool>() ?? false,
                        text = obj["text"]?.Value<string>()   // signs: authored per-placement text
                    }
                };
            }

            return new OccupantCellData { IsEmpty = true };
        }

        #endregion

        #region Rendering

        private void RenderChunk(ChunkRenderData chunk)
        {
            int baseX = chunk.ChunkX * ChunkSize;
            int baseY = chunk.ChunkY * ChunkSize;

            for (int ly = 0; ly < ChunkSize; ly++)
            {
                if (chunk.Ground[ly] == null) continue;
                if (chunk.Occupants[ly] == null) continue;

                for (int lx = 0; lx < ChunkSize; lx++)
                {
                    int gx = baseX + lx;
                    int gy = baseY + ly;
                    var cellPos = new Vector2Int(gx, gy);

                    // Ground tile
                    string groundId = chunk.Ground[ly][lx];
                    SetGroundTile(cellPos, groundId);

                    // Occupant
                    var occData = chunk.Occupants[ly][lx];
                    RenderOccupant(cellPos, occData);
                }
            }
        }

        /// <summary>Ground ids that render as water — the single source used by the animated overlay AND
        /// the player-collision check, so "water" is defined once. (`lava` blocks but isn't animated here.)</summary>
        public static bool IsWaterTile(string id) => id == "water_shallow" || id == "water_deep";

        /// <summary>
        /// Create the animated water overlay: a second Tilemap under the same Grid as groundTilemap, sorted
        /// just above the ground water tiles (below Occupants), with the WaterAnimated material. Guarded — if
        /// the shader is missing we leave `_waterTilemap` null and the static ground water still renders.
        /// </summary>
        private void SetupWaterTilemap()
        {
            if (groundTilemap == null) return;
            var shader = Shader.Find("BugFarmer/WaterAnimated");
            if (shader == null)
            {
                Debug.LogWarning("[TilemapManager] 'BugFarmer/WaterAnimated' not found — water stays static.");
                return;
            }
            // Wrapped so a water-overlay failure can NEVER break the rest of Start (e.g. the OnMatchData hookup).
            try
            {
                var grid = groundTilemap.transform.parent; // GroundTilemap is a child of the Grid
                var go = new GameObject("WaterTilemap");
                go.transform.SetParent(grid, false);
                var tm = go.AddComponent<Tilemap>();
                tm.tileAnchor = groundTilemap.tileAnchor; // align with the ground grid
                // AddComponent<Tilemap> does NOT auto-attach the renderer at runtime. Use Unity's == null check
                // (NOT ??) — GetComponent returns a fake-null that ?? treats as non-null.
                var wr = go.GetComponent<TilemapRenderer>();
                if (wr == null) wr = go.AddComponent<TilemapRenderer>();
                _waterMat = new Material(shader);
                wr.sharedMaterial = _waterMat;
                wr.sortingLayerName = "Ground";
                wr.sortingOrder = 10; // above ground tiles (order 0), below the Occupants layer
                _waterTilemap = tm;   // assign only on full success → graceful fallback to static water
                ApplyWaterSettings();
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[TilemapManager] water overlay setup failed ({e.Message}) — water stays static.");
                _waterTilemap = null;
            }
        }

        /// <summary>Push the Inspector water-look fields onto the runtime material. Called on setup and from
        /// OnValidate, so dragging the sliders updates the pond live during Play mode.</summary>
        private void ApplyWaterSettings()
        {
            if (_waterMat == null) return;
            _waterMat.SetFloat("_WaterAmp", waterDistortion);
            _waterMat.SetFloat("_WaterFreq", waterFrequency);
            _waterMat.SetFloat("_ScrollSpeed", waterSpeed);
            _waterMat.SetFloat("_ScrollDirX", waterScrollDir.x);
            _waterMat.SetFloat("_ScrollDirY", waterScrollDir.y);
            _waterMat.SetFloat("_Shimmer", waterShimmer);
            _waterMat.SetFloat("_SparkleStrength", waterSparkle);
            _waterMat.SetFloat("_FoamWidth", waterFoamWidth);
            _waterMat.SetFloat("_FoamSpeed", waterFoamSpeed);
            _waterMat.SetFloat("_ShoreN", ShoreN);
        }

        private void OnValidate()
        {
            // Live-apply Inspector tweaks during Play (no-op before the material is built).
            ApplyWaterSettings();
        }

        /// <summary>
        /// Rebuild the 3-state shore mask from LOADED chunks and bind it to the water material. Water=1,
        /// known-land=0.5, unloaded=0 (so foam borders known land only, not the loaded-area edge). Cheap:
        /// iterates loaded chunks (one lookup per chunk), direct array reads — not 65k GetGroundAt calls.
        /// </summary>
        private void RebuildShoreMask()
        {
            if (_waterMat == null) return;
            if (_shoreMask == null)
            {
                _shoreMask = new Texture2D(ShoreN, ShoreN, TextureFormat.RGBA32, false)
                { wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Point };
                _shorePixels = new Color32[ShoreN * ShoreN];
            }
            System.Array.Clear(_shorePixels, 0, _shorePixels.Length);   // unloaded = 0
            foreach (var kv in _loadedChunks)
            {
                int baseX = kv.Key.x * ChunkSize, baseY = kv.Key.y * ChunkSize;
                var ground = kv.Value.Ground;
                if (ground == null) continue;
                for (int ly = 0; ly < ChunkSize; ly++)
                {
                    if (ground[ly] == null) continue;
                    int gy = baseY + ly;
                    if (gy < 0 || gy >= ShoreN) continue;
                    for (int lx = 0; lx < ChunkSize; lx++)
                    {
                        int gx = baseX + lx;
                        if (gx < 0 || gx >= ShoreN) continue;
                        byte v = IsWaterTile(ground[ly][lx]) ? (byte)255 : (byte)128; // water : known-land
                        _shorePixels[gy * ShoreN + gx] = new Color32(v, v, v, 255);
                    }
                }
            }
            _shoreMask.SetPixels32(_shorePixels);
            _shoreMask.Apply(false);
            _waterMat.SetTexture("_ShoreMask", _shoreMask);
        }

        private void SetGroundTile(Vector2Int cellPos, string tileId)
        {
            if (groundTilemap == null)
                return;

            // Update visual tilemap
            var tile = TileDatabase.Instance?.GetGroundTile(tileId);
            var tilePos = new Vector3Int(cellPos.x, cellPos.y, 0);
            groundTilemap.SetTile(tilePos, tile);

            // Mirror water cells onto the animated overlay (same tile); clear it for any non-water id. The
            // base water tile stays in groundTilemap, so a missing overlay just falls back to static water.
            if (_waterTilemap != null)
            {
                _waterTilemap.SetTile(tilePos, IsWaterTile(tileId) ? tile : null);
                _shoreDirty = true;   // any ground change can add/remove a shore edge → rebuild the foam mask
            }

            // Also update chunk data so GetGroundAt() returns correct value
            int cx = cellPos.x / ChunkSize;
            int cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (_loadedChunks.TryGetValue(chunkPos, out var chunk))
            {
                int lx = cellPos.x - cx * ChunkSize;
                int ly = cellPos.y - cy * ChunkSize;
                if (ly >= 0 && ly < ChunkSize && lx >= 0 && lx < ChunkSize)
                {
                    if (chunk.Ground[ly] != null)
                        chunk.Ground[ly][lx] = tileId;
                }
            }
        }

        private void RenderOccupant(Vector2Int cellPos, OccupantCellData occData)
        {
            // Remove existing occupant at this cell — and its tree visuals (separate GOs;
            // a pooled occupant must never carry fruit/droplets into its next life).
            if (_occupantObjects.TryGetValue(cellPos, out var existing))
            {
                ReturnToPool(existing);
                _occupantObjects.Remove(cellPos);
                RemoveTreeVisuals(cellPos, forgetState: true);
            }

            // Skip if empty
            if (occData == null || occData.IsEmpty)
                return;

            // Skip if no occupant data
            if (occData.Occupant == null || string.IsNullOrEmpty(occData.Occupant.id))
                return;

            // Skip non-anchor cells (footprint cells have occupant data but anchor=false)
            // We only render the sprite at the anchor cell to avoid duplicate sprites
            if (!occData.Occupant.anchor)
                return;

            string occupantId = occData.Occupant.id;

            // Get sprite from EntityDatabase
            var sprite = EntityDatabase.GetWorldSprite(occupantId);
            if (sprite == null)
            {
                Debug.LogWarning($"[TilemapManager] No sprite for occupant: {occupantId}");
                return;
            }

            bool isBreakable = EntityDatabase.IsBreakable(occupantId);

            // Create or get pooled GameObject
            var go = GetFromPool();
            go.name = $"Occ_{occupantId}_{cellPos.x}_{cellPos.y}";
            go.transform.SetParent(occupantContainer);

            // Position via the ONE shared helper (footprint-X + pivot-Y baseline) so the
            // placement ghost can't drift from the real render (playtest #2).
            var targetSize = EntityDatabase.GetSpriteSize(occupantId); // also scales the sprite below
            Vector3 worldPos = OccupantWorldPos(cellPos, occupantId);
            worldPos.z = -0.1f; // Slightly in front of tilemap to guarantee render order
            go.transform.position = worldPos;

            // Configure sprite renderer
            var def = EntityDatabase.Get(occupantId);
            var sr = go.GetComponent<SpriteRenderer>();
            if (sr == null)
                sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = sprite;
            // receive day/night + lamp Light2D; foliage sways, water plants bob, grain crops sway
            // but vegetables DON'T (routed by id in ApplyOccupant). Natural = grass/trees/flowers.
            var cat = def?.Category;
            bool isFoliage = cat == "natural" || cat == "flora";
            LitMaterials.ApplyOccupant(sr, occupantId, isFoliage);

            // Scale sprite to match target size from database
            float scaleX = targetSize.x / sprite.rect.width;
            float scaleY = targetSize.y / sprite.rect.height;
            go.transform.localScale = new Vector3(scaleX, scaleY, 1f);

            sr.sortingLayerName = "Occupants"; // Must create this sorting layer in Unity
            // Y-sorting: lower Y = higher sorting order (appears in front)
            sr.sortingOrder = -cellPos.y;

            // Lamp/torch glow: data-driven world.light block -> a LampLight child whose
            // Light2D fades with daylight. Pooled objects may carry a stale light from a
            // previous occupant type — remove it first.
            var stale = go.transform.Find("LampLight");
            if (stale != null)
                Destroy(stale.gameObject);
            if (def?.World != null && def.World.LightRadius > 0f)
            {
                var lightGo = new GameObject("LampLight");
                lightGo.transform.SetParent(go.transform, false);
                // counter the occupant's sprite scale so the light radius stays in world units
                lightGo.transform.localScale = new Vector3(
                    scaleX != 0 ? 1f / scaleX : 1f, scaleY != 0 ? 1f / scaleY : 1f, 1f);
                var lamp = lightGo.AddComponent<LampLight>();
                lamp.Configure(def.World.LightRadius, def.World.LightColor, def.World.LightIntensity);
            }

            // Blob shadow under standing objects (trees, flora, crops, structures, furniture, …) so they don't
            // look pasted on. Skip terrain blocks/ore (they ARE the ground) and water plants (a shadow on
            // water looks wrong). Sized to the SPRITE, so a small plant gets a small shadow and a tree a big
            // one. Base-drop is pivot-agnostic (the sprite is centred on the GO either way). Pool-safe.
            bool terrainOrWater = cat == "block" || cat == "ore" || cat == "flora"
                                  || LitMaterials.IsWaterPlant(occupantId);
            if (cat != null && !terrainOrWater)
            {
                BlobShadow.Attach(go.transform, targetSize.x / 16f, targetSize.y / 16f,
                                  new Vector2(scaleX, scaleY), 0.6f);
            }
            else
            {
                BlobShadow.Remove(go.transform);
            }

            // Configure collider to match sprite bounds
            var collider = go.GetComponent<BoxCollider2D>();
            if (collider != null)
            {
                var bounds = sprite.bounds;
                collider.offset = bounds.center;
                collider.size = bounds.size;
                collider.enabled = true;
            }

            // Initialize click target with occupant metadata
            var clickTarget = go.GetComponent<OccupantClickTarget>();
            if (clickTarget != null)
            {
                clickTarget.Initialize(cellPos, occupantId, isBreakable);
            }

            go.SetActive(true);
            _occupantObjects[cellPos] = go;
        }

        /// <summary>
        /// Unload EVERY loaded/subscribed chunk immediately — for a cross-zone swap, so zone A's terrain +
        /// occupants don't linger at the same coords while zone B streams in. Resets the chunk-check anchor
        /// so the next UpdateChunkSubscriptions re-subscribes fresh around the new player position.
        /// </summary>
        public void UnloadAllChunks()
        {
            var all = new HashSet<Vector2Int>(_subscribedChunks);
            foreach (var c in _loadedChunks.Keys) all.Add(c);
            foreach (var c in all) UnloadChunk(c);
            _subscribedChunks.Clear();
            _loadedChunks.Clear();
            _lastPlayerChunk = new Vector2Int(int.MinValue, int.MinValue); // force a fresh resubscribe
            // Phase 1b: the new zone sends its own OpCodeZoneCollisionMap on (re)join — drop the old zone's
            // collision set and re-gate the bug sim until it arrives, so bugs don't collide against stale walls.
            _blocksBugsZoneWide.Clear();
            _collisionMapReady = false;
            _roofZoneWide.Clear();       // drop the old zone's roof; the new zone re-sends OpCodeZoneRoofMap
            DarknessDataVersion++;       // force the darkness overlay to recompute for the new zone
        }

        private void UnloadChunk(Vector2Int chunkPos)
        {
            int baseX = chunkPos.x * ChunkSize;
            int baseY = chunkPos.y * ChunkSize;

            for (int ly = 0; ly < ChunkSize; ly++)
            {
                for (int lx = 0; lx < ChunkSize; lx++)
                {
                    var cellPos = new Vector2Int(baseX + lx, baseY + ly);

                    // Clear ground
                    if (groundTilemap != null)
                    {
                        groundTilemap.SetTile(new Vector3Int(cellPos.x, cellPos.y, 0), null);
                    }
                    if (_waterTilemap != null)
                    {
                        _waterTilemap.SetTile(new Vector3Int(cellPos.x, cellPos.y, 0), null);
                    }

                    // Remove occupant
                    if (_occupantObjects.TryGetValue(cellPos, out var obj))
                    {
                        ReturnToPool(obj);
                        _occupantObjects.Remove(cellPos);
                    }

                    // Remove breaking visual + tree visuals (fruit overlay, droplet,
                    // retained 51/93 state — the chunk re-send repopulates on resubscribe;
                    // without this the droplet dict leaked on every chunk unload)
                    RemoveBreakingVisual(cellPos);
                    RemoveTreeVisuals(cellPos, forgetState: true);
                }
            }

            _loadedChunks.Remove(chunkPos);
            if (_waterTilemap != null) _shoreDirty = true;   // shore set changed → rebuild the foam mask
        }

        #endregion

        #region Breaking Visuals

        private void ShowBreakingProgress(Vector2Int cellPos, int currentHP, int maxHP)
        {
            if (!_breakingVisuals.TryGetValue(cellPos, out var visual))
            {
                var go = new GameObject($"Breaking_{cellPos.x}_{cellPos.y}");
                // CellToWorld already returns cell center
                Vector3 pos = CellToWorld(cellPos);
                go.transform.position = pos;
                go.transform.SetParent(occupantContainer);
                visual = go.AddComponent<BreakingVisual>();
                _breakingVisuals[cellPos] = visual;
                Debug.Log($"[TilemapManager] Created BreakingVisual at world pos {pos} for cell {cellPos}");
            }
            float progress = (float)currentHP / maxHP;
            visual.SetProgress(progress);
            Debug.Log($"[TilemapManager] BreakingVisual renderer enabled: {visual.GetComponent<SpriteRenderer>()?.enabled}, sprite: {visual.GetComponent<SpriteRenderer>()?.sprite?.name}");
        }

        private void RemoveBreakingVisual(Vector2Int cellPos)
        {
            if (_breakingVisuals.TryGetValue(cellPos, out var visual))
            {
                if (visual != null && visual.gameObject != null)
                {
                    Destroy(visual.gameObject);
                }
                _breakingVisuals.Remove(cellPos);
            }
        }

        #endregion

        #region Object Pooling

        private GameObject GetFromPool()
        {
            if (_occupantPool.Count > 0)
            {
                return _occupantPool.Pop();
            }

            var go = new GameObject("PooledOccupant");
            go.AddComponent<SpriteRenderer>();

            // Add collider for sprite-based click detection
            var collider = go.AddComponent<BoxCollider2D>();
            collider.isTrigger = true; // Raycast-only, no physics

            // Add click target component for metadata
            go.AddComponent<OccupantClickTarget>();

            return go;
        }

        private void ReturnToPool(GameObject go)
        {
            if (go == null)
                return;

            go.SetActive(false);
            go.transform.SetParent(null);

            // Disable collider to prevent stray raycast hits
            var collider = go.GetComponent<BoxCollider2D>();
            if (collider != null)
                collider.enabled = false;

            // Reset click target metadata
            var clickTarget = go.GetComponent<OccupantClickTarget>();
            if (clickTarget != null)
                clickTarget.Reset();

            _occupantPool.Push(go);
        }

        #endregion

        #region Coordinate Utilities

        /// <summary>
        /// Convert world position to chunk coordinates.
        /// Handles negative coordinates correctly (matches server GlobalToChunk).
        /// </summary>
        public Vector2Int WorldToChunk(Vector3 worldPos)
        {
            int gx = Mathf.FloorToInt(worldPos.x / cellSize);
            int gy = Mathf.FloorToInt(worldPos.y / cellSize);
            int cx = gx / ChunkSize;
            int cy = gy / ChunkSize;

            // Negative coordinate correction (matches server)
            if (gx < 0 && gx % ChunkSize != 0) cx--;
            if (gy < 0 && gy % ChunkSize != 0) cy--;

            return new Vector2Int(cx, cy);
        }

        /// <summary>
        /// Convert world position to global cell coordinates.
        /// </summary>
        public Vector2Int WorldToCell(Vector3 worldPos)
        {
            return new Vector2Int(
                Mathf.FloorToInt(worldPos.x / cellSize),
                Mathf.FloorToInt(worldPos.y / cellSize)
            );
        }

        /// <summary>
        /// Convert global cell coordinates to world position (center of cell).
        /// </summary>
        public Vector3 CellToWorld(Vector2Int cellPos)
        {
            return new Vector3(
                cellPos.x * cellSize + cellSize * 0.5f,
                cellPos.y * cellSize + cellSize * 0.5f,
                0
            );
        }

        /// <summary>
        /// The world position an occupant RENDERS at when anchored at cellPos (z left at 0):
        /// the anchor cell's center, shifted X to center a multi-cell footprint (odd widths
        /// straddle symmetrically; even widths shift half a cell), and — for bottom-pivot
        /// sprites (pivot.y == 0) — baselined so the sprite sits at the anchor cell's front
        /// edge and rises toward the back of its footprint. The ONE source of truth:
        /// RenderOccupant and the placement ghost both use it, so preview == placement by
        /// construction (playtest #2 was these two computing different Y baselines).
        /// </summary>
        public Vector3 OccupantWorldPos(Vector2Int cellPos, string occupantId)
        {
            Vector3 worldPos = CellToWorld(cellPos);
            var footprint = EntityDatabase.GetFootprint(occupantId);
            worldPos.x += (footprint.x - 1) * 0.5f * cellSize;
            var pivot = EntityDatabase.GetPivot(occupantId);
            if (Mathf.Approximately(pivot.y, 0f))
            {
                float spriteHeightCells = EntityDatabase.GetSpriteSize(occupantId).y / 16f;
                worldPos.y = cellPos.y * cellSize + 0.5f * spriteHeightCells * cellSize;
            }
            return worldPos;
        }

        /// <summary>
        /// Check if a cell is occupied by an occupant (anchor or footprint cell).
        /// </summary>
        public bool IsCellOccupied(Vector2Int cellPos)
        {
            string occ = GetOccupantAt(cellPos);
            return !string.IsNullOrEmpty(occ);
        }

        /// <summary>
        /// Get the occupant ID at a cell, or null if empty.
        /// Works for both anchor and footprint cells.
        /// </summary>
        public string GetOccupantAt(Vector2Int cellPos)
        {
            // Check loaded chunk data
            int cx = cellPos.x / ChunkSize;
            int cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (!_loadedChunks.TryGetValue(chunkPos, out var chunk))
                return null;

            int lx = cellPos.x - cx * ChunkSize;
            int ly = cellPos.y - cy * ChunkSize;

            if (ly < 0 || ly >= ChunkSize || lx < 0 || lx >= ChunkSize)
                return null;

            var occ = chunk.Occupants[ly]?[lx];
            return occ?.Occupant?.id;
        }

        /// <summary>Per-placement authored text of the occupant at a cell (signs), or null.</summary>
        public string GetOccupantText(Vector2Int cellPos)
        {
            int cx = cellPos.x / ChunkSize, cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;
            if (!_loadedChunks.TryGetValue(new Vector2Int(cx, cy), out var chunk)) return null;
            int lx = cellPos.x - cx * ChunkSize, ly = cellPos.y - cy * ChunkSize;
            if (ly < 0 || ly >= ChunkSize || lx < 0 || lx >= ChunkSize) return null;
            return chunk.Occupants[ly]?[lx]?.Occupant?.text;
        }

        /// <summary>
        /// Get the ground tile ID at a cell, or null if chunk not loaded.
        /// </summary>
        public string GetGroundAt(Vector2Int cellPos)
        {
            int cx = cellPos.x / ChunkSize;
            int cy = cellPos.y / ChunkSize;
            if (cellPos.x < 0 && cellPos.x % ChunkSize != 0) cx--;
            if (cellPos.y < 0 && cellPos.y % ChunkSize != 0) cy--;

            var chunkPos = new Vector2Int(cx, cy);
            if (!_loadedChunks.TryGetValue(chunkPos, out var chunk))
                return null;

            int lx = cellPos.x - cx * ChunkSize;
            int ly = cellPos.y - cy * ChunkSize;

            if (ly < 0 || ly >= ChunkSize || lx < 0 || lx >= ChunkSize)
                return null;

            return chunk.Ground[ly]?[lx];
        }

        /// <summary>
        /// True once every chunk this client has subscribed to (its view grid) has its data loaded.
        /// The late-join bug replay gates on this: bug collision reads occupant data from loaded chunks,
        /// so replaying before the view chunks arrive makes bugs near walls collide differently than the
        /// authority (a permanent per-bug divergence). Bugs OUTSIDE the view have no occupants on any client
        /// (consistently), so the view grid is the right readiness bound. Returns false until the player has
        /// spawned and subscribed (empty set). See architecture_swarm_sync.md.
        /// </summary>
        public bool ViewChunksReady
        {
            get
            {
                if (_subscribedChunks.Count == 0) return false;
                foreach (var c in _subscribedChunks)
                    if (!_loadedChunks.ContainsKey(c)) return false;
                return true;
            }
        }

        /// <summary>
        /// Check if a cell blocks bug movement.
        /// Returns true if occupied by a blocking occupant or blocking ground tile.
        /// </summary>
        public bool IsCellBlockedForBugs(Vector2Int cellPos, bool ignoreOccupants = false)
        {
            // Check occupant — skipped for flies_over_fences species (§14: the flag
            // applies identically at BOTH collision sites).
            // GROUND never blocks bugs (water stops PEOPLE only — bugs fly over it;
            // the old hardcoded water check pinned shoreline flies visibly). The
            // server's data-driven tiles.json blocks_bugs flags are false on water to
            // match — keep both sides in step if a tile ever needs to block bugs.
            // Phase 1b: read the ZONE-WIDE collision set (not view-scoped _loadedChunks). This is the whole
            // point — every client must see the same blocks_bugs cells regardless of camera, or grounded bugs
            // near a fence that only some clients loaded would diverge. Fliers (ignoreOccupants) still skip.
            if (!ignoreOccupants)
            {
                return _blocksBugsZoneWide.Contains(cellPos);
            }

            return false;
        }

        /// <summary>
        /// Phase 1b: set/clear one cell in the zone-wide blocks_bugs collision set. Driven by frontier-gated
        /// OCCUPANT_BLOCKS_BUGS events (InfluenceManager) so every client mutates the SAME cell at the SAME
        /// tick. Idempotent (HashSet add/remove), so a placement event that also rode the join-snapshot is safe.
        /// </summary>
        public void SetBlocksBugs(Vector2Int cell, bool blocked)
        {
            if (blocked) _blocksBugsZoneWide.Add(cell);
            else _blocksBugsZoneWide.Remove(cell);
        }

        /// <summary>
        /// Phase 1b: hydrate the complete zone-wide blocks_bugs set from the server (OpCodeZoneCollisionMap,
        /// sent on join + resync). Replaces the set wholesale (resync re-sends the authoritative current state),
        /// then marks the bug sim free to run. Dynamic changes after this ride OCCUPANT_BLOCKS_BUGS events.
        /// </summary>
        public void HandleZoneCollisionMap(int[] cx, int[] cy)
        {
            _blocksBugsZoneWide.Clear();
            int n = (cx != null && cy != null) ? System.Math.Min(cx.Length, cy.Length) : 0;
            for (int i = 0; i < n; i++)
                _blocksBugsZoneWide.Add(new Vector2Int(cx[i], cy[i]));
            _collisionMapReady = true;
            DarknessDataVersion++;   // buried-block darkness reads the solid map
            Debug.Log($"[TilemapManager] Zone collision map hydrated: {_blocksBugsZoneWide.Count} blocks_bugs cells");
        }

        /// <summary>
        /// Hydrate the zone's authored roof (underground / no-sun) cell set from the server
        /// (OpCodeZoneRoofMap, on join + resync). COSMETIC — read only by DarknessOverlay; never a sim
        /// input. Bumps DarknessDataVersion so the overlay recomputes.
        /// </summary>
        public void HandleZoneRoofMap(int[] cx, int[] cy)
        {
            _roofZoneWide.Clear();
            int n = (cx != null && cy != null) ? System.Math.Min(cx.Length, cy.Length) : 0;
            for (int i = 0; i < n; i++)
                _roofZoneWide.Add(new Vector2Int(cx[i], cy[i]));
            DarknessDataVersion++;
            Debug.Log($"[TilemapManager] Zone roof map hydrated: {_roofZoneWide.Count} roofed cells");
        }

        /// <summary>
        /// Check if a cell blocks PLAYER movement (occupant with blocks_players, or impassable ground).
        /// Mirrors IsCellBlockedForBugs but reads blocks_players. Used by PlayerController for collision.
        /// </summary>
        public bool IsCellBlockedForPlayers(Vector2Int cellPos)
        {
            string occupantId = GetOccupantAt(cellPos);
            if (!string.IsNullOrEmpty(occupantId))
            {
                var def = Data.EntityDatabase.Get(occupantId);
                if (def?.World != null && def.World.BlocksPlayers)
                    return true;
            }

            string groundId = GetGroundAt(cellPos);
            if (IsWaterTile(groundId) || groundId == "lava")
                return true;

            return false;
        }

        #endregion
    }

    /// <summary>
    /// Parsed chunk data for rendering.
    /// </summary>
    public class ChunkRenderData
    {
        public int ChunkX;
        public int ChunkY;
        public string[][] Ground;         // [y][x] tile IDs
        public OccupantCellData[][] Occupants; // [y][x] occupant data
    }

    /// <summary>
    /// Parsed occupant cell data.
    /// </summary>
    public class OccupantCellData
    {
        public bool IsEmpty;    // null in JSON
        public Networking.PlacedOccupant Occupant; // Occupant data (anchor=true for anchor cell)
    }
}
