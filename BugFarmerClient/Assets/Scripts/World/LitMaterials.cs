using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Shared URP 2D lit material for world sprites. Sprites render with the unlit default
    /// material unless told otherwise — they must use Sprite-Lit-Default to RECEIVE Light2D
    /// (the day/night global light + lamp point lights). One shared material instance keeps
    /// batching intact. Apply at every sprite-creation point.
    /// </summary>
    public static class LitMaterials
    {
        private static Material _lit;
        private static bool _searched;

        public static Material Lit
        {
            get
            {
                if (!_searched)
                {
                    _searched = true;
                    var shader = Shader.Find("Universal Render Pipeline/2D/Sprite-Lit-Default");
                    if (shader != null)
                        _lit = new Material(shader);
                    else
                        Debug.LogWarning("[LitMaterials] Sprite-Lit-Default shader not found - sprites stay unlit");
                }
                return _lit;
            }
        }

        /// <summary>Make this renderer receive 2D lights (no-op if the shader is missing).</summary>
        public static void Apply(SpriteRenderer sr)
        {
            if (sr != null && Lit != null)
                sr.sharedMaterial = Lit;
        }

        /// <summary>Make a tilemap renderer (ground tiles) receive 2D lights.</summary>
        public static void Apply(Renderer r)
        {
            if (r != null && Lit != null)
                r.sharedMaterial = Lit;
        }
    }
}
