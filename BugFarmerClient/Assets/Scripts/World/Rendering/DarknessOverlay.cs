using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Underground darkness overlay. A world-anchored MULTIPLY-blend sprite (shader
    /// "BugFarmer/DarknessMultiply", Blend DstColor Zero) covering the zone, sorted above all world
    /// content and below the ScreenSpaceOverlay UI. Its texture is a per-cell darkness field
    /// (1 = lit / 0 = dark); multiplying it over the already-lit frame darkens buried/roofed cells to
    /// black — even at noon — while the lit surface, the player's own lights, and the UI are untouched.
    ///
    /// M0 (done): proved the multiply renders in URP 2D with a test pattern.
    /// M1 (this): BURIED-BLOCK darkness from the zone-wide solid map — a block-mass interior goes dark,
    ///   the exposed face stays lit (a soft "the deeper into the rock, the darker" falloff). Open tunnels
    ///   stay lit until M2 adds the authored roof mask; M3 lets carried lights open the mask back up.
    ///
    /// Self-bootstrapping (no scene setup). Press <b>L</b> in Play mode to toggle it on/off.
    /// </summary>
    public class DarknessOverlay : MonoBehaviour
    {
        private const int N = 256;            // max zone side (8x8 chunks * 32); covers any zone
        private const int Falloff = 4;        // cells of soft edge from an open face into the rock
        private const int SortingOrder = 30000;

        private static bool _spawned;

        private SpriteRenderer _sr;
        private Texture2D _tex;
        private Color32[] _pixels;
        private bool _enabledOverlay = true;
        private bool _computedForReady;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (_spawned) return;
            _spawned = true;
            var go = new GameObject("DarknessOverlay");
            DontDestroyOnLoad(go);
            go.AddComponent<DarknessOverlay>();
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.L))
            {
                _enabledOverlay = !_enabledOverlay;
                if (_sr != null) _sr.enabled = _enabledOverlay;
                Debug.Log($"[DarknessOverlay] {(_enabledOverlay ? "ON" : "OFF")} (L toggles)");
            }

            var tm = TilemapManager.Instance;
            if (tm == null) return;
            if (_sr == null && !Build()) return;

            // Recompute once each time a zone's collision map becomes ready (join / zone switch).
            if (tm.CollisionMapReady)
            {
                if (!_computedForReady)
                {
                    Recompute(tm);
                    _computedForReady = true;
                }
            }
            else
            {
                _computedForReady = false; // a new zone is loading; recompute when it's ready
            }
        }

        private bool Build()
        {
            var shader = Shader.Find("BugFarmer/DarknessMultiply");
            if (shader == null)
            {
                Debug.LogError("[DarknessOverlay] shader 'BugFarmer/DarknessMultiply' not found.");
                enabled = false;
                return false;
            }

            _tex = new Texture2D(N, N, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Bilinear,   // smooth the per-cell field
                wrapMode = TextureWrapMode.Clamp,
            };
            _pixels = new Color32[N * N];
            for (int i = 0; i < _pixels.Length; i++) _pixels[i] = new Color32(255, 255, 255, 255); // all lit
            _tex.SetPixels32(_pixels);
            _tex.Apply();

            // 1 texel per cell; pivot bottom-left at world origin so texel (x,y) covers cell (x,y)'s
            // world area (cellSize = 1). The camera views whatever part of the zone it's over.
            var sprite = Sprite.Create(_tex, new Rect(0, 0, N, N), new Vector2(0f, 0f), pixelsPerUnit: 1f);

            _sr = gameObject.AddComponent<SpriteRenderer>();
            _sr.sprite = sprite;
            _sr.sharedMaterial = new Material(shader);
            _sr.sortingLayerName = "Player";   // above world content; UI is a separate overlay canvas
            _sr.sortingOrder = SortingOrder;
            _sr.enabled = _enabledOverlay;
            transform.position = new Vector3(0f, 0f, 0f);
            Debug.Log("[DarknessOverlay] built (world-anchored). L toggles.");
            return true;
        }

        /// <summary>
        /// Buried-from-solids darkness: open cells = lit (1); solid cells go dark, ramping from the
        /// exposed face (lit) into the interior (black) over <see cref="Falloff"/> cells. A "light flood"
        /// that grows inward from open cells — deep rock the flood can't reach stays black.
        /// </summary>
        private void Recompute(TilemapManager tm)
        {
            int n2 = N * N;
            var solid = new bool[n2];
            var cur = new float[n2];
            for (int y = 0; y < N; y++)
                for (int x = 0; x < N; x++)
                {
                    int i = y * N + x;
                    bool s = tm.IsCellBlockedForBugs(new Vector2Int(x, y));
                    solid[i] = s;
                    cur[i] = s ? 0f : 1f;   // solid starts dark, open lit
                }

            float step = 1f / Falloff;
            var nxt = new float[n2];
            for (int pass = 0; pass < Falloff; pass++)
            {
                System.Array.Copy(cur, nxt, n2);
                for (int y = 0; y < N; y++)
                    for (int x = 0; x < N; x++)
                    {
                        int i = y * N + x;
                        if (!solid[i]) continue;                 // open cells stay fully lit
                        float m = cur[i];
                        if (x > 0)     m = Mathf.Max(m, cur[i - 1] - step);
                        if (x < N - 1) m = Mathf.Max(m, cur[i + 1] - step);
                        if (y > 0)     m = Mathf.Max(m, cur[i - N] - step);
                        if (y < N - 1) m = Mathf.Max(m, cur[i + N] - step);
                        nxt[i] = m;
                    }
                var t = cur; cur = nxt; nxt = t;
            }

            for (int i = 0; i < n2; i++)
            {
                byte v = (byte)(Mathf.Clamp01(cur[i]) * 255f);
                _pixels[i] = new Color32(v, v, v, 255);
            }
            _tex.SetPixels32(_pixels);
            _tex.Apply();
            Debug.Log("[DarknessOverlay] darkness field recomputed from the solid map (M1 buried-block darkness).");
        }
    }
}
