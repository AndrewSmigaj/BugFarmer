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

        [Header("Settings")]
        [SerializeField] private int viewDistanceChunks = 2; // Subscribe to 5x5 grid of chunks
        [SerializeField] private float chunkCheckInterval = 0.5f;
        [SerializeField] private float cellSize = 1f; // World units per cell (matches PPU 16)

        // Constants matching server zone.go
        public const int ChunkSize = 32;

        // Chunk tracking
        private HashSet<Vector2Int> _subscribedChunks = new HashSet<Vector2Int>();
        private Dictionary<Vector2Int, ChunkRenderData> _loadedChunks = new Dictionary<Vector2Int, ChunkRenderData>();
        private Vector2Int _lastPlayerChunk = new Vector2Int(int.MinValue, int.MinValue);
        private float _lastChunkCheck;

        // Occupant GameObjects by global cell position
        private Dictionary<Vector2Int, GameObject> _occupantObjects = new Dictionary<Vector2Int, GameObject>();

        // Breaking visuals by global cell position
        private Dictionary<Vector2Int, BreakingVisual> _breakingVisuals = new Dictionary<Vector2Int, BreakingVisual>();

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

            // Update occupant
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
                // Removal - look up old occupant to get footprint, then clear all cells
                ClearOccupantAndFootprint(gx, gy);
            }
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
                        anchor = obj["anchor"]?.Value<bool>() ?? false
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

        private void SetGroundTile(Vector2Int cellPos, string tileId)
        {
            if (groundTilemap == null)
                return;

            var tile = TileDatabase.Instance?.GetGroundTile(tileId);
            var tilePos = new Vector3Int(cellPos.x, cellPos.y, 0);
            groundTilemap.SetTile(tilePos, tile);
        }

        private void RenderOccupant(Vector2Int cellPos, OccupantCellData occData)
        {
            // Remove existing occupant at this cell
            if (_occupantObjects.TryGetValue(cellPos, out var existing))
            {
                ReturnToPool(existing);
                _occupantObjects.Remove(cellPos);
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

            // Get pivot from EntityDatabase
            var pivot = EntityDatabase.GetPivot(occupantId);
            bool isBreakable = EntityDatabase.IsBreakable(occupantId);

            // Create or get pooled GameObject
            var go = GetFromPool();
            go.name = $"Occ_{occupantId}_{cellPos.x}_{cellPos.y}";
            go.transform.SetParent(occupantContainer);

            // Position at cell with pivot adjustment
            Vector3 worldPos = CellToWorld(cellPos);
            // Adjust Y for pivot (pivot.y gives bottom-center offset)
            // Use target size from database for positioning
            var targetSize = EntityDatabase.GetSpriteSize(occupantId);
            float spriteHeightCells = targetSize.y / 16f;
            worldPos.y += pivot.y * spriteHeightCells * cellSize;
            go.transform.position = worldPos;

            // Configure sprite renderer
            var sr = go.GetComponent<SpriteRenderer>();
            if (sr == null)
                sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = sprite;

            // Scale sprite to match target size from database
            float scaleX = targetSize.x / sprite.rect.width;
            float scaleY = targetSize.y / sprite.rect.height;
            go.transform.localScale = new Vector3(scaleX, scaleY, 1f);

            sr.sortingLayerName = "Occupants"; // Must create this sorting layer in Unity
            // Y-sorting: lower Y = higher sorting order (appears in front)
            sr.sortingOrder = -cellPos.y;

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

                    // Remove occupant
                    if (_occupantObjects.TryGetValue(cellPos, out var obj))
                    {
                        ReturnToPool(obj);
                        _occupantObjects.Remove(cellPos);
                    }

                    // Remove breaking visual
                    RemoveBreakingVisual(cellPos);
                }
            }

            _loadedChunks.Remove(chunkPos);
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
        /// Check if a cell blocks bug movement.
        /// Returns true if occupied by a blocking occupant or blocking ground tile.
        /// </summary>
        public bool IsCellBlockedForBugs(Vector2Int cellPos)
        {
            // Check occupant
            string occupantId = GetOccupantAt(cellPos);
            if (!string.IsNullOrEmpty(occupantId))
            {
                var def = Data.EntityDatabase.Get(occupantId);
                if (def?.World != null && def.World.BlocksBugs)
                    return true;
            }

            // Check ground tile
            string groundId = GetGroundAt(cellPos);
            if (groundId == "water_shallow" || groundId == "water_deep" || groundId == "lava")
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
