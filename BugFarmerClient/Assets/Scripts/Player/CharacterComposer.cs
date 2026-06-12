using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.Player
{
    /// <summary>
    /// Runtime paper-doll compositor. Stacks layer PNGs from
    /// Resources/Player/layers/ (emitted by tools/generate_player_sprites.py)
    /// into composited per-(direction, frame) sprites:
    ///   layer order: body -> pants -> shirt -> chest -> hair -> helmet
    ///   frames per direction: [contact-L(_w1), idle(), contact-R(_w3), idle()]
    /// One composed Sprite per cell keeps a single SpriteRenderer (Y-sort and
    /// day/night lighting unchanged). Requires the layer textures to be
    /// CPU-readable (fix_sprite_ppu.py sets isReadable on Player/layers metas).
    /// Composition results are cached per outfit key.
    /// </summary>
    public static class CharacterComposer
    {
        /// <summary>An outfit: layer set names (null/empty = layer absent).</summary>
        public class Outfit
        {
            public string Body = "default";   // skin tone: default | tan | deep
            public string Hair = "brown";     // color, or "long_<color>" for the long style
            public string Shirt = "farmer";   // class outfit sets
            public string Pants = "farmer";
            public string Chest;              // leather_chest | iron_chest
            public string Helmet;             // straw_hat | copper_helmet | iron_helmet

            public string Key => $"{Body}|{Hair}|{Shirt}|{Pants}|{Chest}|{Helmet}";
        }

        // Full helms replace hair (mirrors wearables.HIDES_HAIR in the generator).
        private static readonly HashSet<string> HidesHair = new HashSet<string> { "iron_helmet" };

        // Direction enum order: Down=0, Left=1, Right=2, Up=3 (NetworkMessages).
        private static readonly string[] DirNames = { "down", "left", "right", "up" };
        private static readonly string[] FrameSuffix = { "_w1", "", "_w3", "" };

        private const int W = 16, H = 32, PPU = 16;
        private static readonly Dictionary<string, Sprite[][]> Cache =
            new Dictionary<string, Sprite[][]>();

        /// <summary>
        /// Compose [4 dirs][4 frames] sprites for the outfit, or null when the
        /// body layer is missing/unreadable (caller keeps its baked fallback).
        /// </summary>
        public static Sprite[][] Compose(Outfit outfit)
        {
            if (Cache.TryGetValue(outfit.Key, out var cached))
                return cached;

            var result = new Sprite[4][];
            for (int d = 0; d < 4; d++)
            {
                result[d] = new Sprite[4];
                for (int f = 0; f < 4; f++)
                {
                    if (f == 3 && result[d][1] != null) { result[d][3] = result[d][1]; continue; }

                    var px = new Color32[W * H]; // transparent
                    bool gotBody = false;
                    foreach (var layer in LayerPaths(outfit, DirNames[d], FrameSuffix[f]))
                    {
                        var ok = Blend(px, layer);
                        if (layer.StartsWith("Player/layers/body/")) gotBody = ok;
                    }
                    if (!gotBody) return null; // unreadable/missing — use baked fallback

                    var tex = new Texture2D(W, H, TextureFormat.RGBA32, false)
                    { filterMode = FilterMode.Point };
                    tex.SetPixels32(px);
                    tex.Apply(false, true);
                    result[d][f] = Sprite.Create(tex, new Rect(0, 0, W, H),
                                                 new Vector2(0.5f, 0.5f), PPU);
                }
            }
            Cache[outfit.Key] = result;
            return result;
        }

        private static IEnumerable<string> LayerPaths(Outfit o, string dir, string suffix)
        {
            yield return $"Player/layers/body/{o.Body}_{dir}{suffix}";
            if (!string.IsNullOrEmpty(o.Pants))
                yield return $"Player/layers/pants/{o.Pants}_{dir}{suffix}";
            if (!string.IsNullOrEmpty(o.Shirt))
                yield return $"Player/layers/shirt/{o.Shirt}_{dir}{suffix}";
            if (!string.IsNullOrEmpty(o.Chest))
                yield return $"Player/layers/chest/{o.Chest}_{dir}{suffix}";
            bool hideHair = o.Helmet != null && HidesHair.Contains(o.Helmet);
            if (!string.IsNullOrEmpty(o.Hair) && !hideHair)
                yield return $"Player/layers/hair/{o.Hair}_{dir}{suffix}";
            if (!string.IsNullOrEmpty(o.Helmet))
                yield return $"Player/layers/helmet/{o.Helmet}_{dir}{suffix}";
        }

        /// <summary>Alpha-over blend a layer sprite's pixels into px. False if missing/unreadable.</summary>
        private static bool Blend(Color32[] px, string resourcePath)
        {
            var sprite = Resources.Load<Sprite>(resourcePath);
            if (sprite == null) return false;
            Color32[] src;
            try { src = sprite.texture.GetPixels32(); }
            catch (UnityException)
            {
                Debug.LogWarning($"[CharacterComposer] {resourcePath} not CPU-readable — " +
                                 "run tools/fix_sprite_ppu.py and reimport.");
                return false;
            }
            if (src.Length != px.Length) return false;
            for (int i = 0; i < px.Length; i++)
            {
                var s = src[i];
                if (s.a == 0) continue;
                if (s.a == 255) { px[i] = s; continue; }
                float a = s.a / 255f, ia = 1f - a;
                px[i] = new Color32(
                    (byte)(s.r * a + px[i].r * ia), (byte)(s.g * a + px[i].g * ia),
                    (byte)(s.b * a + px[i].b * ia), (byte)Mathf.Max(s.a, px[i].a));
            }
            return true;
        }

        /// <summary>
        /// Load the BAKED class sprites as a [4 dirs][4 frames] set (the no-layers
        /// path: classes + walk frames straight from Resources/Player/).
        /// </summary>
        public static Sprite[][] LoadBaked(string cls)
        {
            var result = new Sprite[4][];
            for (int d = 0; d < 4; d++)
            {
                var idle = Resources.Load<Sprite>($"Player/{cls}_{DirNames[d]}");
                if (idle == null) return null;
                var w1 = Resources.Load<Sprite>($"Player/{cls}_{DirNames[d]}_w1");
                var w3 = Resources.Load<Sprite>($"Player/{cls}_{DirNames[d]}_w3");
                result[d] = new[] { w1 != null ? w1 : idle, idle,
                                    w3 != null ? w3 : idle, idle };
            }
            return result;
        }
    }
}
