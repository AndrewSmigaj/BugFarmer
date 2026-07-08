using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// M0 SPIKE for the underground darkness system — proves the render approach in-engine.
    ///
    /// A world-space MULTIPLY-blend sprite (shader "BugFarmer/DarknessMultiply", Blend DstColor Zero)
    /// stretched over the camera view, sorted above all world content and below the ScreenSpaceOverlay UI.
    /// It multiplies the already-lit frame by a per-cell darkness texture (1 = lit / 0 = dark), so dark
    /// regions go BLACK even at noon (it multiplies the final lit color rather than adding into the 2D
    /// light accumulation), while the lit surface and the UI are untouched.
    ///
    /// M0 fills the texture with a TEST pattern (bottom of screen dark, top lit, soft band between) to
    /// confirm: (a) the multiply darkens to black at any time of day, (b) the UI is unaffected. Later
    /// milestones replace the test texture with the real per-cell darkness field (M1 buried-from-solids,
    /// M2 roofed) and let carried lights open it back up (M3).
    ///
    /// Self-bootstrapping (no scene setup): a RuntimeInitialize hook spawns one persistent instance; it
    /// waits for a Camera before building. Press <b>L</b> in Play mode to toggle it on/off for comparison.
    /// </summary>
    public class DarknessOverlay : MonoBehaviour
    {
        private const int TexW = 64, TexH = 64;
        private const int SortingOrder = 30000; // above world sprites; UI is a separate overlay canvas

        private static bool _spawned;

        private SpriteRenderer _sr;
        private Camera _cam;
        private bool _enabledOverlay = true;

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
                Debug.Log($"[DarknessOverlay] {( _enabledOverlay ? "ON" : "OFF")} (press L to toggle)");
            }

            if (_sr == null)
            {
                _cam = Camera.main;
                if (_cam != null) Build();
            }
        }

        private void Build()
        {
            var shader = Shader.Find("BugFarmer/DarknessMultiply");
            if (shader == null)
            {
                Debug.LogError("[DarknessOverlay] shader 'BugFarmer/DarknessMultiply' not found — is DarknessMultiply.shader in the project?");
                enabled = false;
                return;
            }

            // TEST darkness texture: bottom of the screen dark (0=black), top lit (1=unchanged), soft band.
            var tex = new Texture2D(TexW, TexH, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Bilinear,   // soft gradient band when stretched
                wrapMode = TextureWrapMode.Clamp,
            };
            for (int y = 0; y < TexH; y++)
            {
                float v = Mathf.Clamp01(Mathf.InverseLerp(28f, 40f, y)); // 0 (dark) low, 1 (lit) high
                var c = new Color(v, v, v, 1f);
                for (int x = 0; x < TexW; x++) tex.SetPixel(x, y, c);
            }
            tex.Apply();

            var sprite = Sprite.Create(tex, new Rect(0, 0, TexW, TexH),
                                       new Vector2(0.5f, 0.5f), pixelsPerUnit: 1f);

            var go = new GameObject("DarknessQuad");
            go.transform.SetParent(_cam.transform, false);
            go.transform.localPosition = new Vector3(0f, 0f, 1f); // just in front of the camera
            _sr = go.AddComponent<SpriteRenderer>();
            _sr.sprite = sprite;
            _sr.sharedMaterial = new Material(shader);
            // Sorting LAYER dominates sorting ORDER. World content is on Ground/Occupants/Player;
            // the HUD is a separate ScreenSpaceOverlay canvas (renders after everything). Put the
            // overlay at the TOP of the "Player" layer so it darkens all world content (incl. the
            // player) but leaves the "UI" sorting layer + the overlay HUD untouched.
            _sr.sortingLayerName = "Player";
            _sr.sortingOrder = SortingOrder;
            _sr.enabled = _enabledOverlay;

            Debug.Log("[DarknessOverlay] M0 spike active — bottom of screen should be dark at any time of day. Press L to toggle.");
        }

        private void LateUpdate()
        {
            if (_sr == null || _cam == null) return;
            if (!_cam.orthographic) return;
            // Cover the ortho view exactly (handles zoom/pan; the sprite is a camera child).
            float h = _cam.orthographicSize * 2f;
            float w = h * _cam.aspect;
            _sr.transform.localScale = new Vector3(w / TexW, h / TexH, 1f);
        }
    }
}
