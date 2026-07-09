using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Shared URP 2D lit materials for world sprites, all instances of the custom "BugFarmer/SpriteLitWorld"
    /// shader (URP's Sprite-Lit-Default + vertex wind/bob + a fragment hit-flash). World sprites RECEIVE 2D
    /// lights (day/night + lamps) AND can sway / bob / flash. A small fixed set of shared instances keeps
    /// batching intact — motion differs only by the material's constant wind/bob dials:
    ///   Lit      — no motion (everything non-foliage; the universal replacement for Sprite-Lit-Default).
    ///   LitWind  — land foliage sway (trees, flowers, grass, crops).
    ///   LitReed  — upright water plants: slower, higher-amplitude sway + a hint of bob (reeds/cattail).
    ///   LitBob   — flat floating leaves: a gentle vertical bob, no base-anchored wind (lily pads).
    /// The hit-flash is a per-renderer MaterialPropertyBlock (see <see cref="HitFlash"/>) so it never breaks
    /// batching. Falls back to the stock Sprite-Lit-Default (no motion/flash) if the custom shader is missing.
    /// </summary>
    public static class LitMaterials
    {
        private const string WorldShader = "BugFarmer/SpriteLitWorld";
        private const string FallbackShader = "Universal Render Pipeline/2D/Sprite-Lit-Default";

        // Motion dials (world units / phase speed). Tuned in-engine; land foliage is the reference.
        public const float WindStrength = 0.12f;
        public const float WindSpeed = 1.5f;
        private const float ReedWind = 0.18f, ReedWindSpeed = 1.0f, ReedBob = 0.03f, ReedBobSpeed = 0.8f;
        private const float FloatBob = 0.06f, FloatBobSpeed = 0.9f;

        // Water plants get floatier motion than land foliage. Small, greppable id sets (entity data has no
        // motion tag); widen here if new water-plant ids are added.
        private static readonly HashSet<string> Floaters = new() { "lily_pad", "water_lily" };
        private static readonly HashSet<string> WaterUpright = new() { "reeds", "cattail", "marsh_plant" };

        private static Shader _shader;
        private static bool _searched;
        private static Material _lit, _litWind, _litReed, _litBob;

        private static Shader FindShader()
        {
            if (_searched) return _shader;
            _searched = true;
            _shader = Shader.Find(WorldShader);
            if (_shader == null)
            {
                _shader = Shader.Find(FallbackShader);
                Debug.LogWarning($"[LitMaterials] '{WorldShader}' not found — using {FallbackShader} (no motion/flash).");
            }
            return _shader;
        }

        private static Material Make(float wind, float windSpeed, float bob, float bobSpeed)
        {
            var s = FindShader();
            if (s == null) return null;
            var m = new Material(s);
            m.SetFloat("_WindStrength", wind);
            m.SetFloat("_WindSpeed", windSpeed);
            m.SetFloat("_BobStrength", bob);
            m.SetFloat("_BobSpeed", bobSpeed);
            return m;
        }

        /// <summary>Shared lit material, no motion (everything except foliage/water plants).</summary>
        public static Material Lit
        {
            get { if (_lit == null) _lit = Make(0f, WindSpeed, 0f, 1f); return _lit; }
        }

        /// <summary>Shared lit material with land-foliage wind sway.</summary>
        public static Material LitWind
        {
            get { if (_litWind == null) _litWind = Make(WindStrength, WindSpeed, 0f, 1f); return _litWind; }
        }

        private static Material LitReed
        {
            get { if (_litReed == null) _litReed = Make(ReedWind, ReedWindSpeed, ReedBob, ReedBobSpeed); return _litReed; }
        }

        private static Material LitBob
        {
            get { if (_litBob == null) _litBob = Make(0f, WindSpeed, FloatBob, FloatBobSpeed); return _litBob; }
        }

        /// <summary>Make this renderer receive 2D lights. foliage=true → the wind-swaying variant.</summary>
        public static void Apply(SpriteRenderer sr, bool foliage = false)
        {
            if (sr == null) return;
            var m = foliage ? LitWind : Lit;
            if (m != null) sr.sharedMaterial = m;
        }

        /// <summary>Make a tilemap/other renderer receive 2D lights (no motion).</summary>
        public static void Apply(Renderer r)
        {
            if (r != null && Lit != null) r.sharedMaterial = Lit;
        }

        /// <summary>
        /// Assign the right lit material for an occupant: water floaters bob, upright water plants get the
        /// slow reed sway, other foliage gets land wind, everything else is still (no motion).
        /// </summary>
        public static void ApplyOccupant(SpriteRenderer sr, string occupantId, bool foliage)
        {
            if (sr == null) return;
            Material m = Floaters.Contains(occupantId) ? LitBob
                       : WaterUpright.Contains(occupantId) ? LitReed
                       : foliage ? LitWind : Lit;
            if (m != null) sr.sharedMaterial = m;
        }
    }
}
