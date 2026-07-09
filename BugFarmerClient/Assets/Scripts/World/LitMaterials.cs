using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Shared URP 2D lit material(s) for world sprites. Uses the custom "BugFarmer/SpriteLitWorld" shader
    /// (a copy of URP's Sprite-Lit-Default + vertex wind + a fragment hit-flash), so world sprites both
    /// RECEIVE 2D lights (day/night global + lamps) AND can sway / flash. Two shared instances keep batching
    /// intact: <see cref="Lit"/> (no wind) for everything, <see cref="LitWind"/> (wind on) for foliage. The
    /// hit-flash is per-renderer via a MaterialPropertyBlock (`_FlashAmount`), so it never breaks batching.
    /// Falls back to the stock Sprite-Lit-Default (no wind/flash) if the custom shader is missing.
    /// </summary>
    public static class LitMaterials
    {
        private const string WorldShader = "BugFarmer/SpriteLitWorld";
        private const string FallbackShader = "Universal Render Pipeline/2D/Sprite-Lit-Default";
        // Default sway amplitude (world units at the sprite tip) + speed; tuned in-engine.
        public const float WindStrength = 0.12f;
        public const float WindSpeed = 1.5f;

        private static Shader _shader;
        private static bool _searched;
        private static Material _lit;
        private static Material _litWind;

        private static Shader FindShader()
        {
            if (_searched) return _shader;
            _searched = true;
            _shader = Shader.Find(WorldShader);
            if (_shader == null)
            {
                _shader = Shader.Find(FallbackShader);
                Debug.LogWarning($"[LitMaterials] '{WorldShader}' not found — using {FallbackShader} (no wind/flash).");
            }
            return _shader;
        }

        /// <summary>Shared lit material, no wind (everything except foliage).</summary>
        public static Material Lit
        {
            get
            {
                if (_lit == null) { var s = FindShader(); if (s != null) _lit = new Material(s); }
                return _lit;
            }
        }

        /// <summary>Shared lit material with wind sway on (foliage).</summary>
        public static Material LitWind
        {
            get
            {
                if (_litWind == null)
                {
                    var s = FindShader();
                    if (s != null)
                    {
                        _litWind = new Material(s);
                        _litWind.SetFloat("_WindStrength", WindStrength);
                        _litWind.SetFloat("_WindSpeed", WindSpeed);
                    }
                }
                return _litWind;
            }
        }

        /// <summary>Make this renderer receive 2D lights. foliage=true → the wind-swaying variant.</summary>
        public static void Apply(SpriteRenderer sr, bool foliage = false)
        {
            if (sr == null) return;
            var m = foliage ? LitWind : Lit;
            if (m != null) sr.sharedMaterial = m;
        }

        /// <summary>Make a tilemap/other renderer receive 2D lights (no wind).</summary>
        public static void Apply(Renderer r)
        {
            if (r != null && Lit != null) r.sharedMaterial = Lit;
        }
    }
}
