using UnityEngine;
using BugFarmer.Networking;

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
    /// Stage 1.5 (docs/plans/village-slice.md): the darkness FIELD (DarknessField: the maths) covers the whole zone at the
    /// zone's own size, but only a WINDOW around the camera is sent to the graphics card — the view plus a margin,
    /// re-centred (one fresh upload) when the view nears its edge. A moving torch re-sends the window, not the zone, so
    /// its cost doesn't grow with the zone (before, the whole 256 x 256 texture went up on every lamp move). Same
    /// per-cell values, same look (tools/darkness-check compares it with the overlay as it was).
    ///
    /// Self-bootstrapping (no scene setup). Press <b>L</b> in Play mode to toggle it on/off.
    /// </summary>
    public class DarknessOverlay : MonoBehaviour
    {
        private const int SortingOrder = 30000;
        private const float NightFloor = 0.2f;  // matches DayNightController.nightIntensity (global brightness floor)
        // Step 2: an underground torch pool is capped to this VISIBLE brightness (compensating for the surface
        // sun), so a cave reads as a warm DIM pool — never brighter than the daytime surface, ~time-independent.
        private const float UndergroundRevealTarget = 0.4f;
        // The window: the camera's view plus this many cells on every side, rounded up to whole chunks. Walking moves
        // the view inside it; it is re-centred only when the view would reach its edge.
        private const int WindowMargin = 16;
        private const int WindowStep = 32;

        /// <summary>Set once built; LampLight reads the smooth local darkness from here.</summary>
        public static DarknessOverlay Instance { get; private set; }

        private static bool _spawned;

        private SpriteRenderer _sr;

        private DarknessField _field;   // the whole zone's darkness; null until the first recompute

        // The window sent to the graphics card: its texture and pixels (base + light stamps), its size, and the zone
        // cell at its bottom-left corner.
        private Texture2D _tex;
        private Color32[] _pixels;
        private int _winW, _winH, _winX, _winY;
        private bool _windowMoved;      // created, resized or re-centred → refill + upload

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

            PlaceWindow();   // after a recompute, so the window always lies inside the current field
            StampLights();   // M3: open the mask where carried/placed lights reach (skips when nothing moved)
        }

        /// <summary>
        /// Size the window to the camera's view and keep the view inside it. The window stays inside the field (the
        /// zone, before the first recompute); outside the zone nothing is drawn, as before.
        /// </summary>
        private void PlaceWindow()
        {
            var zone = WorldManager.ZoneSize;
            int bw = _field != null ? _field.Width : zone.x;
            int bh = _field != null ? _field.Height : zone.y;

            var cam = Camera.main;
            float halfH = cam != null ? cam.orthographicSize : 10f;
            float halfW = cam != null ? halfH * cam.aspect : 18f;
            Vector2 c = cam != null ? (Vector2)cam.transform.position : new Vector2(bw * 0.5f, bh * 0.5f);

            // Grows with a zoom-out, never shrinks except to fit a smaller field.
            int w = Mathf.Min(bw, Mathf.Max(_winW, RoundUp(Mathf.CeilToInt(2f * halfW) + 2 + 2 * WindowMargin)));
            int h = Mathf.Min(bh, Mathf.Max(_winH, RoundUp(Mathf.CeilToInt(2f * halfH) + 2 + 2 * WindowMargin)));
            if (_tex == null || w != _winW || h != _winH) CreateWindow(w, h);

            // The view's cells within the field, plus one on each side for the smoothing between texels.
            int vx0 = Mathf.Max(0, Mathf.FloorToInt(c.x - halfW) - 1), vx1 = Mathf.Min(bw, Mathf.CeilToInt(c.x + halfW) + 1);
            int vy0 = Mathf.Max(0, Mathf.FloorToInt(c.y - halfH) - 1), vy1 = Mathf.Min(bh, Mathf.CeilToInt(c.y + halfH) + 1);
            bool outsideField = _winX + _winW > bw || _winY + _winH > bh;
            if (_windowMoved || outsideField || vx0 < _winX || vx1 > _winX + _winW || vy0 < _winY || vy1 > _winY + _winH)
            {
                int x = Mathf.Clamp(Mathf.RoundToInt(c.x - _winW * 0.5f), 0, bw - _winW);
                int y = Mathf.Clamp(Mathf.RoundToInt(c.y - _winH * 0.5f), 0, bh - _winH);
                if (_windowMoved || x != _winX || y != _winY)
                {
                    _winX = x;
                    _winY = y;
                    _windowMoved = true;
                    transform.position = new Vector3(x, y, 0f);
                }
            }
        }

        private static int RoundUp(int n) => (n + WindowStep - 1) / WindowStep * WindowStep;

        private void CreateWindow(int w, int h)
        {
            if (_tex != null)
            {
                Destroy(_sr.sprite);
                Destroy(_tex);
            }
            _tex = new Texture2D(w, h, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Bilinear,   // smooth the per-cell field
                wrapMode = TextureWrapMode.Clamp,
            };
            _pixels = new Color32[w * h];
            _winW = w;
            _winH = h;
            _windowMoved = true;
            // 1 texel per cell; pivot bottom-left, placed at the window's bottom-left cell, so texel (x,y) covers
            // zone cell (_winX + x, _winY + y) (cellSize = 1).
            _sr.sprite = Sprite.Create(_tex, new Rect(0, 0, w, h), new Vector2(0f, 0f), pixelsPerUnit: 1f);
            Debug.Log($"[DarknessOverlay] window {w} x {h} cells");
        }

        /// <summary>
        /// M3: start from the static darkness and "open" it (toward lit) wherever an active lamp reaches, so a torch
        /// pool isn't multiplied back to black. Only refills and re-uploads the window when a lamp moved / turned
        /// on-off, the base changed or the window moved — free when everything's static.
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
            if (!_baseDirty && !_windowMoved && emitting == _lastEmitting && Mathf.Abs(sig - _lastSig) < 1e-4f) return;
            _lastSig = sig;
            _lastEmitting = emitting;
            _baseDirty = false;
            _windowMoved = false;

            if (_field == null)
            {
                var lit = new Color32(255, 255, 255, 255);   // all lit until data arrives
                for (int i = 0; i < _pixels.Length; i++) _pixels[i] = lit;
            }
            else
            {
                _field.FillWindow(_pixels, _winX, _winY, _winW, _winH);
                for (int k = 0; k < lamps.Count; k++)
                {
                    var l = lamps[k];
                    if (l == null || !l.IsEmitting) continue;
                    var p = l.transform.position;
                    _field.StampLamp(_pixels, _winX, _winY, _winW, _winH, p.x, p.y, l.OuterRadius, l.Strength01, undergroundCap);
                }
            }
            _tex.SetPixels32(_pixels);
            _tex.Apply(false);
        }

        /// <summary>Smooth "underground darkness" at a cell (0 = surface/lit, 1 = deep underground), blurred at
        /// the cave mouth. LampLight fades a torch in with this — so a torch fades in at a cave entrance the
        /// same smooth way it fades in at dusk. Returns 0 before the field is built.</summary>
        public float UndergroundDarknessAt(Vector2Int c) => _field != null ? _field.UndergroundDarknessAt(c.x, c.y) : 0f;

        private bool Build()
        {
            var shader = GameShaders.Find("BugFarmer/DarknessMultiply");
            if (shader == null)
            {
                enabled = false;
                return false;
            }

            Instance = this;
            _sr = gameObject.AddComponent<SpriteRenderer>();
            _sr.sharedMaterial = new Material(shader);
            _sr.sortingLayerName = "Player";   // above world content; UI is a separate overlay canvas
            _sr.sortingOrder = SortingOrder;
            _sr.enabled = _enabledOverlay;
            Debug.Log("[DarknessOverlay] built (world-anchored, camera window). L toggles.");
            return true;
        }

        /// <summary>Work the whole zone's darkness out again (on join, resync and zone switch): at the zone's size, from
        /// its solid and roofed cells (DarknessField.Build).</summary>
        private void Recompute(TilemapManager tm)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var zone = WorldManager.ZoneSize;
            if (_field == null || _field.Width != zone.x || _field.Height != zone.y)
                _field = new DarknessField(zone.x, zone.y);
            _field.Build(tm.ZoneBlocksBugsCells, tm.ZoneRoofCells);
            _baseDirty = true;   // StampLights (this same frame) refills the window + light stamps + uploads
            Debug.Log($"[DarknessOverlay] darkness field recomputed for {zone.x} x {zone.y} in {sw.ElapsedMilliseconds} ms " +
                      "(M2 base: buried blocks + authored roof + blur).");
        }
    }
}
