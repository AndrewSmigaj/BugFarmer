using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Runtime blob shadows — a soft dark oval under grounded, standing occupants (trees, structures) so
    /// they read as planted rather than pasted on. The oval is a single runtime-generated radial-gradient
    /// Sprite (no art asset), shared by every shadow; each shadow is a child <see cref="SpriteRenderer"/>
    /// managed per-render like the LampLight child. It sits on the "Ground" sorting layer → always under
    /// occupants, above ground tiles, and dimmed underground by the darkness overlay. Cosmetic only,
    /// client-local, zero sim/determinism surface.
    /// </summary>
    public static class BlobShadow
    {
        private const string ChildName = "BlobShadow";
        private static Sprite _sprite;
        private static bool _logged;

        // One shared soft oval; a circular radial-gradient texture squashed to an ellipse via transform scale.
        private static Sprite OvalSprite()
        {
            if (_sprite != null) return _sprite;
            const int N = 64;
            var tex = new Texture2D(N, N, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[N * N];
            float c = (N - 1) * 0.5f;
            for (int y = 0; y < N; y++)
                for (int x = 0; x < N; x++)
                {
                    float dx = (x - c) / c, dy = (y - c) / c;
                    float d = Mathf.Sqrt(dx * dx + dy * dy);  // 0 center .. 1 edge
                    float a = Mathf.Clamp01(1f - d);
                    a *= a;                                    // soft, core-weighted falloff
                    px[y * N + x] = new Color32(0, 0, 0, (byte)(a * 255f));
                }
            tex.SetPixels32(px);
            tex.Apply();
            _sprite = Sprite.Create(tex, new Rect(0, 0, N, N), new Vector2(0.5f, 0.5f), N); // PPU=N → 1 world unit
            return _sprite;
        }

        /// <summary>
        /// Attach or refresh a blob shadow child under a grounded (bottom-center) occupant GO. The parent's
        /// position is the sprite CENTER, so the shadow is dropped ½·spriteHeightCells down to the ground base.
        /// </summary>
        /// <param name="parent">Occupant GameObject transform.</param>
        /// <param name="widthCells">Sprite visual width in cells (shadow is scaled from this).</param>
        /// <param name="spriteHeightCells">Sprite height in cells (drops the shadow to the base).</param>
        /// <param name="parentScale">The occupant's localScale (countered → world-unit sizing).</param>
        /// <param name="alpha">Peak opacity (0..1).</param>
        public static void Attach(Transform parent, float widthCells, float spriteHeightCells,
                                  Vector2 parentScale, float alpha)
        {
            var t = parent.Find(ChildName);
            SpriteRenderer sr;
            if (t == null)
            {
                var go = new GameObject(ChildName);
                go.transform.SetParent(parent, false);
                sr = go.AddComponent<SpriteRenderer>();
                sr.sprite = OvalSprite();
                sr.material = new Material(Shader.Find("Sprites/Default")); // explicit, like the codebase's other runtime SRs
                sr.sortingLayerName = "Ground";  // above ground tiles (Ground/0), below every occupant
                sr.sortingOrder = 100;
                if (!_logged) { _logged = true; Debug.Log("[BlobShadow] first shadow created (Ground layer, order 100)"); }
            }
            else sr = t.GetComponent<SpriteRenderer>();

            sr.color = new Color(0f, 0f, 0f, alpha);

            float w = Mathf.Max(0.35f, widthCells * 0.75f);  // world units (cellSize=1); ~ the sprite's base width
            float h = w * 0.42f;                             // flat ellipse
            float sx = parentScale.x != 0 ? parentScale.x : 1f;
            float sy = parentScale.y != 0 ? parentScale.y : 1f;
            sr.transform.localScale = new Vector3(w / sx, h / sy, 1f);
            // Parent scale multiplies localPosition, so counter sy. Drop to the base (-0.5*height) plus a small
            // nudge below so a bit of the oval shows in front of a tall trunk without detaching under a low plant.
            sr.transform.localPosition = new Vector3(0f, (-0.5f * spriteHeightCells - 0.1f) / sy, 0.01f);
        }

        /// <summary>Remove a blob shadow if a pooled occupant no longer wants one.</summary>
        public static void Remove(Transform parent)
        {
            var t = parent.Find(ChildName);
            if (t != null) Object.Destroy(t.gameObject);
        }
    }
}
