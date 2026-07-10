using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Shaped-ground compositor (M0 render spike). A composite ground id is <c>matA~matB~shape</c> (e.g.
    /// <c>grass~dirt~diagNE</c>): material A fills the shape mask's 1-region, material B the 0-region. We blend
    /// on the GPU via <see cref="Graphics.Blit(Texture, RenderTexture, Material)"/> because the base tile PNGs
    /// import as <c>isReadable:0</c> (a CPU GetPixels would throw). The shape mask is generated procedurally
    /// (no PNG assets) and cached; the composited texture is cached by <see cref="TileDatabase"/> under the
    /// full id, so each (matA,matB,shape) combo builds exactly once.
    /// </summary>
    public static class TileCompositor
    {
        private static Material _mat;
        private static readonly Dictionary<string, Texture2D> _maskCache = new Dictionary<string, Texture2D>();

        /// <summary>Parse <c>matA~matB~shape</c>. Returns false for a plain (non-composite) id.</summary>
        public static bool TryParse(string id, out string matA, out string matB, out string shape)
        {
            matA = matB = shape = null;
            if (string.IsNullOrEmpty(id) || id.IndexOf('~') < 0)
                return false;
            var parts = id.Split('~');
            if (parts.Length != 3)
                return false;
            matA = parts[0]; matB = parts[1]; shape = parts[2];
            return !string.IsNullOrEmpty(matA) && !string.IsNullOrEmpty(matB) && !string.IsNullOrEmpty(shape);
        }

        /// <summary>
        /// Build the composited texture for a composite id, or null if a material texture / the shader is
        /// missing (caller then falls back). The output is Point-filtered to match the crisp base tiles.
        /// </summary>
        public static Texture2D Build(string matA, string matB, string shape)
        {
            var texA = Resources.Load<Texture2D>($"Tiles/{matA}");
            var texB = Resources.Load<Texture2D>($"Tiles/{matB}");
            if (texA == null || texB == null)
            {
                Debug.LogWarning($"[TileCompositor] missing material texture ('{matA}' or '{matB}')");
                return null;
            }

            int n = texA.width; // ground tiles are uniform 32x32
            var mask = GetMask(shape, n);

            if (_mat == null)
            {
                var sh = Shader.Find("Hidden/BugFarmer/TileComposite");
                if (sh == null)
                {
                    Debug.LogWarning("[TileCompositor] Hidden/BugFarmer/TileComposite shader not found");
                    return null;
                }
                _mat = new Material(sh) { hideFlags = HideFlags.HideAndDontSave };
            }
            _mat.SetTexture("_MatA", texA);
            _mat.SetTexture("_MatB", texB);
            _mat.SetTexture("_Mask", mask);

            var rt = RenderTexture.GetTemporary(n, n, 0, RenderTextureFormat.ARGB32);
            var prevActive = RenderTexture.active;
            Graphics.Blit(texA, rt, _mat); // source arg unused by the shader; explicit _MatA/_MatB/_Mask used
            RenderTexture.active = rt;
            var outTex = new Texture2D(n, n, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp,
            };
            outTex.ReadPixels(new Rect(0, 0, n, n), 0, 0);
            outTex.Apply(false);
            RenderTexture.active = prevActive;
            RenderTexture.ReleaseTemporary(rt);
            return outTex;
        }

        /// <summary>Procedural black/white shape mask (hard-edged for crisp pixel art), cached per shape+size.</summary>
        private static Texture2D GetMask(string shape, int n)
        {
            string key = $"{shape}~{n}";
            if (_maskCache.TryGetValue(key, out var cached))
                return cached;

            var tex = new Texture2D(n, n, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp,
            };
            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
            {
                for (int x = 0; x < n; x++)
                {
                    byte v = (byte)(MaskAt(shape, x, y, n) ? 255 : 0);
                    px[y * n + x] = new Color32(v, v, v, 255);
                }
            }
            tex.SetPixels32(px);
            tex.Apply(false);
            _maskCache[key] = tex;
            return tex;
        }

        /// <summary>
        /// True where material A shows. Pixel (0,0) is bottom-left, y up. The four diagonal halves use the two
        /// cell diagonals; "full" is solid A (plain paint). M1 adds straight halves + corner triangles here.
        /// </summary>
        private static bool MaskAt(string shape, int x, int y, int n)
        {
            int t = n - 1;
            switch (shape)
            {
                case "full":   return true;
                case "diagNE": return (x + y) >= t; // anti-diagonal, upper-right triangle
                case "diagSW": return (x + y) <= t; // lower-left triangle
                case "diagNW": return y >= x;       // main diagonal, upper-left triangle
                case "diagSE": return y <= x;       // lower-right triangle
                default:       return true;         // unknown -> solid A (visible, not magenta)
            }
        }
    }
}
