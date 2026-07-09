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
        private const float RevealScale = 1.9f; // torch reveal reaches this * the light radius (bright core, dim ring)
        private const int BlurPasses = 5;       // 3x3 box-blur passes on the base field → wider soft cave-mouth (torch fades in over more distance)
        private const float NightFloor = 0.2f;  // matches DayNightController.nightIntensity (global brightness floor)
        // Step 2: an underground torch pool is capped to this VISIBLE brightness (compensating for the surface
        // sun), so a cave reads as a warm DIM pool — never brighter than the daytime surface, ~time-independent.
        private const float UndergroundRevealTarget = 0.4f;

        /// <summary>Set once built; LampLight reads the smooth local darkness from here.</summary>
        public static DarknessOverlay Instance { get; private set; }

        private static bool _spawned;

        private SpriteRenderer _sr;
        private Texture2D _tex;
        private Color32[] _pixels;      // per-frame output (base + light stamps)
        private float[] _baseLit;       // static buried+roofed lit value per cell (0=dark, 1=lit); blurred → smooth
        private bool[] _underground;    // roofed (no-sun) per cell — caps the torch reveal underground (Step 2)
        private Color32[] _basePixels;  // _baseLit as pixels (no lights) — copied each stamp
        private bool _baseDirty = true; // base changed → re-stamp next frame
        private float _lastSig;         // light-configuration signature (skip re-upload when unchanged)
        private int _lastEmitting = -1;
        private bool _enabledOverlay = true;
        private int _lastVersion = -1;

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

            // Recompute whenever the darkness inputs change (collision map + roof map arrive on join, in
            // either order; and on a zone switch). The version bumps on each, so this catches the roof map
            // landing a frame after the collision map.
            if (tm.CollisionMapReady && tm.DarknessDataVersion != _lastVersion)
            {
                Recompute(tm);
                _lastVersion = tm.DarknessDataVersion;
            }

            StampLights();   // M3: open the mask where carried/placed lights reach (skips when nothing moved)
        }

        /// <summary>
        /// M3: each frame, start from the static darkness and "open" it (toward lit) wherever an active lamp
        /// reaches, so a torch pool isn't multiplied back to black. Only re-uploads when a lamp moved / turned
        /// on-off or the base changed — free when everything's static.
        /// </summary>
        private void StampLights()
        {
            if (_pixels == null) return;
            var lamps = LampLight.Active;

            // Surface-sun brightness — used to cap the underground reveal so a cave pool is a fixed DIM
            // brightness regardless of the surface clock, never brighter than the daytime surface (Step 2).
            float g = Mathf.Lerp(NightFloor, 1f, Mathf.Clamp01(DayNightController.Daylight));
            float undergroundCap = Mathf.Clamp01(UndergroundRevealTarget / Mathf.Max(g, 0.01f));

            float sig = g * 137f;   // re-stamp as day/night shifts (the cap changes)
            int emitting = 0;
            for (int k = 0; k < lamps.Count; k++)
            {
                var l = lamps[k];
                if (l == null || !l.IsEmitting) continue;
                emitting++;
                var p = l.transform.position;
                sig += p.x * 3.1f + p.y * 7.7f + l.OuterRadius * 1.3f + l.Strength01 * 11.1f;
            }
            if (!_baseDirty && emitting == _lastEmitting && Mathf.Abs(sig - _lastSig) < 1e-4f) return;
            _lastSig = sig;
            _lastEmitting = emitting;
            _baseDirty = false;

            System.Array.Copy(_basePixels, _pixels, _pixels.Length);
            for (int k = 0; k < lamps.Count; k++)
            {
                var l = lamps[k];
                if (l == null || !l.IsEmitting) continue;
                StampOne(l.transform.position, l.OuterRadius, l.Strength01, undergroundCap);
            }
            _tex.SetPixels32(_pixels);
            _tex.Apply();
        }

        private void StampOne(Vector3 world, float radius, float strength, float undergroundCap)
        {
            if (radius <= 0.01f || strength <= 0.01f) return;
            float revealR = radius * RevealScale;   // open the darkness over a WIDER area than the bright light
            int cxc = Mathf.FloorToInt(world.x);     // cellSize = 1
            int cyc = Mathf.FloorToInt(world.y);
            int r = Mathf.CeilToInt(revealR);
            for (int y = cyc - r; y <= cyc + r; y++)
            {
                if (y < 0 || y >= N) continue;
                for (int x = cxc - r; x <= cxc + r; x++)
                {
                    if (x < 0 || x >= N) continue;
                    float dx = (x + 0.5f) - world.x;
                    float dy = (y + 0.5f) - world.y;
                    float t = Mathf.Sqrt(dx * dx + dy * dy) / revealR;
                    if (t >= 1f) continue;
                    int i = y * N + x;
                    // gradual (bright core → dim ring) AND faded in by the lamp's own on-ness (no snap);
                    // capped underground so the pool stays a warm dim, not brighter than noon.
                    float open = Mathf.SmoothStep(1f, 0f, t) * strength;
                    if (_underground[i]) open = Mathf.Min(open, undergroundCap);
                    float lit = Mathf.Max(_baseLit[i], open);
                    byte v = (byte)(lit * 255f);
                    if (v > _pixels[i].r) _pixels[i] = new Color32(v, v, v, 255);
                }
            }
        }

        /// <summary>Smooth "underground darkness" at a cell (0 = surface/lit, 1 = deep underground), blurred at
        /// the cave mouth. LampLight fades a torch in with this — so a torch fades in at a cave entrance the
        /// same smooth way it fades in at dusk. Returns 0 before the field is built.</summary>
        public float UndergroundDarknessAt(Vector2Int c)
        {
            if (_baseLit == null || c.x < 0 || c.x >= N || c.y < 0 || c.y >= N) return 0f;
            return Mathf.Clamp01(1f - _baseLit[c.y * N + c.x]);
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
            _basePixels = new Color32[N * N];
            _baseLit = new float[N * N];
            _underground = new bool[N * N];
            for (int i = 0; i < _pixels.Length; i++)
            {
                _pixels[i] = new Color32(255, 255, 255, 255);      // all lit until data arrives
                _basePixels[i] = _pixels[i];
                _baseLit[i] = 1f;
            }
            Instance = this;
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
            var roofed = new bool[n2];
            var cur = new float[n2];
            for (int y = 0; y < N; y++)
                for (int x = 0; x < N; x++)
                {
                    int i = y * N + x;
                    var cell = new Vector2Int(x, y);
                    bool s = tm.IsCellBlockedForBugs(cell);
                    solid[i] = s;
                    roofed[i] = tm.IsRoofCell(cell);   // M2: authored underground/no-sun
                    cur[i] = s ? 0f : 1f;              // solid starts dark, open lit
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

            // Combined darkness = max(buried, roofed). A roofed cell (underground) is fully dark — tunnels
            // AND block faces — until a carried light opens it back up (M3). Surface block masses (not roofed)
            // keep their buried soft-edge look (M1).
            for (int i = 0; i < n2; i++)
            {
                _baseLit[i] = roofed[i] ? 0f : Mathf.Clamp01(cur[i]);
                _underground[i] = roofed[i];   // Step 2: cap the torch reveal here so pools stay dim
            }

            BlurBaseLit();   // soften the cave-mouth boundary + edges so the dark→lit transition isn't abrupt

            for (int i = 0; i < n2; i++)
            {
                byte v = (byte)(_baseLit[i] * 255f);
                _basePixels[i] = new Color32(v, v, v, 255);
            }
            _baseDirty = true;   // StampLights (this same frame) re-copies base + light stamps + uploads
            Debug.Log("[DarknessOverlay] darkness field recomputed (M2 base: buried blocks + authored roof + blur).");
        }

        /// <summary>Separable-ish 3x3 box blur on _baseLit, BlurPasses times — softens the cave-mouth
        /// boundary and block/pool edges so the darkness reads as a gentle gradient, not hard cell steps.</summary>
        private void BlurBaseLit()
        {
            int n2 = N * N;
            var tmp = new float[n2];
            for (int pass = 0; pass < BlurPasses; pass++)
            {
                for (int y = 0; y < N; y++)
                    for (int x = 0; x < N; x++)
                    {
                        float s = 0f;
                        int c = 0;
                        for (int dy = -1; dy <= 1; dy++)
                        {
                            int yy = y + dy;
                            if (yy < 0 || yy >= N) continue;
                            for (int dx = -1; dx <= 1; dx++)
                            {
                                int xx = x + dx;
                                if (xx < 0 || xx >= N) continue;
                                s += _baseLit[yy * N + xx];
                                c++;
                            }
                        }
                        tmp[y * N + x] = s / c;
                    }
                System.Array.Copy(tmp, _baseLit, n2);
            }
        }
    }
}
