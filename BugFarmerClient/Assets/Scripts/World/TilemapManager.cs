using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;
using Nakama;
using Newtonsoft.Json.Linq;
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

            // Update occupant (can be null, "@", or {id, dir})
            var occupantToken = root["occupant"];
            UpdateOccupantFromToken(cellPos, occupantToken);
        }

        private void HandleBreakProgress(IMatchState state)
        {
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<BreakProgressMessage>(json);
            if (msg == null)
                return;

            var cellPos = new Vector2Int(msg.grid_x, msg.grid_y);

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

            if (token.Type == JTokenType.String)
            {
                string str = token.Value<string>();
                if (str == "@")
                {
                    return new OccupantCellData { IsBlocked = true };
                }
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
                        dir = obj["dir"]?.Value<int>() ?? 0
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

            // Skip if empty or blocked
            if (occData == null || occData.IsEmpty || occData.IsBlocked)
                return;

            // Skip if no occupant data
            if (occData.Occupant == null || string.IsNullOrEmpty(occData.Occupant.id))
                return;

            // Get occupant entry from database
            var entry = TileDatabase.Instance?.GetOccupant(occData.Occupant.id);
            if (entry == null || entry.sprite == null)
            {
                Debug.LogWarning($"[TilemapManager] Unknown occupant: {occData.Occupant.id}");
                return;
            }

            // Create or get pooled GameObject
            var go = GetFromPool();
            go.name = $"Occ_{occData.Occupant.id}_{cellPos.x}_{cellPos.y}";
            go.transform.SetParent(occupantContainer);

            // Position at cell with pivot adjustment
            Vector3 worldPos = CellToWorld(cellPos);
            // Adjust Y for pivot (entry.pivot.y gives bottom-center offset)
            // Use sprite's actual height for positioning
            float spriteHeightCells = entry.sprite.rect.height / 16f;
            worldPos.y += entry.pivot.y * spriteHeightCells * cellSize;
            go.transform.position = worldPos;

            // Configure sprite renderer
            var sr = go.GetComponent<SpriteRenderer>();
            if (sr == null)
                sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = entry.sprite;
            sr.sortingLayerName = "Occupants"; // Must create this sorting layer in Unity
            // Y-sorting: lower Y = higher sorting order (appears in front)
            sr.sortingOrder = -cellPos.y;

            go.SetActive(true);
            _occupantObjects[cellPos] = go;
        }

        private void UpdateOccupantFromToken(Vector2Int cellPos, JToken token)
        {
            var occData = ParseOccupantCell(token);
            RenderOccupant(cellPos, occData);
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
                go.transform.position = CellToWorld(cellPos);
                go.transform.SetParent(occupantContainer);
                visual = go.AddComponent<BreakingVisual>();
                _breakingVisuals[cellPos] = visual;
            }
            visual.SetProgress((float)currentHP / maxHP);
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
            return go;
        }

        private void ReturnToPool(GameObject go)
        {
            if (go == null)
                return;

            go.SetActive(false);
            go.transform.SetParent(null);
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
        /// Check if a cell is occupied by an occupant.
        /// </summary>
        public bool IsCellOccupied(Vector2Int cellPos)
        {
            return _occupantObjects.ContainsKey(cellPos);
        }

        /// <summary>
        /// Get the occupant ID at a cell, or null if empty.
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
        public bool IsBlocked;  // "@" marker
        public PlacedOccupant Occupant; // Anchor cell with {id, dir}
    }
}
