using TMPro;
using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// A small world-space emote bubble over an entity — a pop-in glyph (alert "!", thinking "…", etc.)
    /// on a soft white bubble that holds, then fades and self-destroys while following a target transform.
    /// <see cref="Show"/> is the reusable primitive; the TRIGGER sources (which entity emotes, and when)
    /// are wired by callers as features need them. Built like RemoteEntity's nameplate (a world-space
    /// TextMeshPro on the Occupants layer) plus a runtime bubble sprite (no art asset). Cosmetic,
    /// client-local, zero sim/determinism surface.
    /// </summary>
    public class Emote : MonoBehaviour
    {
        // Handy glyphs — callers can pass any string.
        public const string Alert = "!";
        public const string Question = "?";
        public const string Thinking = "…";
        public const string Happy = "♥"; // ♥
        public const string Sleep = "z";

        private static Sprite _bubble;

        private Transform _target;
        private readonly Vector3 _offset = new Vector3(0f, 1.4f, 0f);
        private float _age, _life;
        private const float FadeIn = 0.15f, FadeOut = 0.3f;
        private SpriteRenderer _bubbleSr;
        private TextMeshPro _glyph;

        /// <summary>Show an emote over <paramref name="target"/> for <paramref name="duration"/> seconds.</summary>
        public static Emote Show(Transform target, string glyph, float duration = 1.8f, Color? bg = null)
        {
            if (target == null || string.IsNullOrEmpty(glyph)) return null;
            Debug.Log($"[Emote] Show '{glyph}' over {target.name} at {target.position}");
            var go = new GameObject("Emote");
            var e = go.AddComponent<Emote>();
            e.Init(target, glyph, duration, bg ?? Color.white);
            return e;
        }

        private void Init(Transform target, string glyph, float duration, Color bg)
        {
            _target = target;
            _life = Mathf.Max(FadeIn + FadeOut + 0.1f, duration);
            transform.position = target.position + _offset;

            var bgGo = new GameObject("Bubble");
            bgGo.transform.SetParent(transform, false);
            _bubbleSr = bgGo.AddComponent<SpriteRenderer>();
            _bubbleSr.sprite = BubbleSprite();
            _bubbleSr.material = new Material(Shader.Find("Sprites/Default")); // explicit, like the codebase's other runtime SRs
            _bubbleSr.color = bg;
            _bubbleSr.sortingLayerID = SortingLayer.NameToID("Occupants");
            _bubbleSr.sortingOrder = 961;                 // above world sprites + nameplates (960)
            bgGo.transform.localScale = Vector3.one * 0.7f;

            var tGo = new GameObject("Glyph");
            tGo.transform.SetParent(transform, false);
            tGo.transform.localPosition = new Vector3(0f, 0.02f, 0f);
            _glyph = tGo.AddComponent<TextMeshPro>();
            _glyph.text = glyph;
            _glyph.alignment = TextAlignmentOptions.Center;
            _glyph.enableAutoSizing = false;
            _glyph.enableWordWrapping = false;
            _glyph.fontSize = 8f;                          // TMP-3D fontSize→world mapping; tuned in-Editor
            _glyph.color = new Color(0.15f, 0.12f, 0.1f, 1f);
            _glyph.rectTransform.sizeDelta = new Vector2(4f, 2f);
            tGo.transform.localScale = Vector3.one * 0.12f;
            var gr = _glyph.renderer;
            if (gr != null)
            {
                gr.sortingLayerID = SortingLayer.NameToID("Occupants");
                gr.sortingOrder = 963;                     // above the bubble
            }
        }

        private void LateUpdate()
        {
            if (_target == null) { Destroy(gameObject); return; }
            transform.position = _target.position + _offset;

            _age += Time.deltaTime;
            if (_age >= _life) { Destroy(gameObject); return; }

            float scale = _age < FadeIn ? Overshoot(_age / FadeIn) : 1f;
            transform.localScale = Vector3.one * scale;

            float alpha = _age > _life - FadeOut ? Mathf.Clamp01((_life - _age) / FadeOut) : 1f;
            SetAlpha(alpha);
        }

        // ease-out-back: 0 → overshoot ~1.1 → settle at 1.
        private static float Overshoot(float t)
        {
            t = Mathf.Clamp01(t) - 1f;
            const float s = 1.70158f;
            return 1f + (t * t * ((s + 1f) * t + s));
        }

        private void SetAlpha(float a)
        {
            if (_bubbleSr != null) { var c = _bubbleSr.color; c.a = a; _bubbleSr.color = c; }
            if (_glyph != null) { var c = _glyph.color; c.a = a; _glyph.color = c; }
        }

        // Shared soft white bubble: opaque core out to ~0.8r, soft edge to the rim. PPU=N → 1 world unit.
        private static Sprite BubbleSprite()
        {
            if (_bubble != null) return _bubble;
            const int N = 64;
            var tex = new Texture2D(N, N, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[N * N];
            float c = (N - 1) * 0.5f;
            for (int y = 0; y < N; y++)
                for (int x = 0; x < N; x++)
                {
                    float dx = (x - c) / c, dy = (y - c) / c;
                    float d = Mathf.Sqrt(dx * dx + dy * dy);
                    float a = d < 0.8f ? 1f : Mathf.Clamp01(1f - (d - 0.8f) / 0.2f);
                    px[y * N + x] = new Color32(255, 255, 255, (byte)(a * 255f));
                }
            tex.SetPixels32(px);
            tex.Apply();
            _bubble = Sprite.Create(tex, new Rect(0, 0, N, N), new Vector2(0.5f, 0.5f), N);
            return _bubble;
        }
    }
}
