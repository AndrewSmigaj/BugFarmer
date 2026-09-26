using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Scatters small grass-tuft sprites over grass cells — the detail layer that makes a lawn read as
    /// grass rather than as a flat green floor (every polished top-down farming game does this: a quiet
    /// base tile plus scattered tufts).
    ///
    /// These are PURELY VISUAL: no collider, no blob shadow, no click target, and they are NOT occupants.
    /// The occupant path is for things you interact with and is far heavier per instance; a dense carpet
    /// of those would be thousands of GameObjects with colliders. Tufts are plain SpriteRenderers created
    /// per loaded chunk and destroyed with it, and they use the shared LitWind material so they sway with
    /// the rest of the foliage for free.
    ///
    /// Placement is a deterministic hash of the cell coordinate, so every client and every reload sees the
    /// same field with nothing to store or sync.
    /// </summary>
    public class GrassTuftRenderer : MonoBehaviour
    {
        public static GrassTuftRenderer Instance { get; private set; }

        [Tooltip("Fraction of grass cells that get a tuft (0 = none, 1 = every cell).")]
        [Range(0f, 1f)] [SerializeField] private float density = 0.25f;

        [Tooltip("Sprites are drawn just above the ground tilemap but below entities.")]
        [SerializeField] private int sortingOrder = -1;

        private const int TuftCount = 4;                 // Resources/Objects/grass_tuft_1..4
        private const float PPU = 16f;                   // one cell = 16 px, as everywhere else

        private Sprite[] _sprites;
        private readonly Dictionary<Vector2Int, GameObject> _chunkRoots = new();

        /// <summary>
        /// Self-bootstrapping: the other world managers are components placed in the scene by hand, but a
        /// new one would silently do nothing until someone opens the Editor and adds it. Creating itself on
        /// load means the tuft layer works from a fresh checkout with no scene edit.
        /// </summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (Instance != null)
                return;
            var go = new GameObject("GrassTuftRenderer");
            go.AddComponent<GrassTuftRenderer>();
            DontDestroyOnLoad(go);
        }

        private void Awake()
        {
            Instance = this;
            _sprites = new Sprite[TuftCount];
            for (int i = 0; i < TuftCount; i++)
            {
                var tex = Resources.Load<Texture2D>($"Objects/grass_tuft_{i + 1}");
                if (tex == null)
                    continue;
                _sprites[i] = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height),
                                            new Vector2(0.5f, 0f), PPU);   // bottom-centred: sits ON the cell
            }
        }

        /// <summary>Deterministic per-cell hash — same cell, same tuft, on every client and reload.</summary>
        private static uint CellHash(int x, int y, int salt)
        {
            unchecked
            {
                uint h = (uint)(x * 73856093 ^ y * 19349663 ^ salt * 83492791);
                h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
                return h;
            }
        }

        /// <summary>Build the tuft layer for one loaded chunk. Call again to rebuild after edits.</summary>
        public void BuildChunk(int chunkX, int chunkY, int chunkSize, System.Func<int, int, string> groundAt)
        {
            if (_sprites == null)
                return;
            ClearChunk(chunkX, chunkY);

            var root = new GameObject($"Tufts_{chunkX}_{chunkY}");
            root.transform.SetParent(transform, false);
            _chunkRoots[new Vector2Int(chunkX, chunkY)] = root;

            for (int ly = 0; ly < chunkSize; ly++)
            {
                for (int lx = 0; lx < chunkSize; lx++)
                {
                    int wx = chunkX * chunkSize + lx, wy = chunkY * chunkSize + ly;
                    string ground = groundAt?.Invoke(wx, wy);
                    if (string.IsNullOrEmpty(ground) || !ground.StartsWith("grass"))
                        continue;                                   // tufts only grow on grass

                    uint h = CellHash(wx, wy, 1);
                    if ((h % 1000u) / 1000f > density)
                        continue;

                    var sprite = _sprites[(int)((h >> 10) % TuftCount)];
                    if (sprite == null)
                        continue;

                    var go = new GameObject("tuft");
                    go.transform.SetParent(root.transform, false);
                    // jitter inside the cell so tufts do not line up on the grid
                    float jx = ((h >> 14) % 100) / 100f - 0.5f;
                    float jy = ((h >> 21) % 100) / 100f * 0.4f;
                    go.transform.position = new Vector3(wx + 0.5f + jx * 0.6f, wy + jy, 0f);

                    var sr = go.AddComponent<SpriteRenderer>();
                    sr.sprite = sprite;
                    sr.sortingOrder = sortingOrder;
                    if (((h >> 28) & 1) == 1)
                        sr.flipX = true;                            // free extra variety
                    LitMaterials.Apply(sr, foliage: true);          // sways with the other foliage
                }
            }
        }

        public void ClearChunk(int chunkX, int chunkY)
        {
            var key = new Vector2Int(chunkX, chunkY);
            if (_chunkRoots.TryGetValue(key, out var go) && go != null)
                Destroy(go);
            _chunkRoots.Remove(key);
        }

        public void ClearAll()
        {
            foreach (var kv in _chunkRoots)
                if (kv.Value != null)
                    Destroy(kv.Value);
            _chunkRoots.Clear();
        }
    }
}
