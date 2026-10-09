// The darkness overlay's maths as it was before Stage 1.5 (BugFarmerClient/.../DarknessOverlay.cs at 246c217a): one
// 256 x 256 field and texture, every cell looked up in the solid and roof sets, a 3x3 box blur done as nine reads per
// cell, and lamps stamped into the whole texture. Copied with only the texture and TilemapManager plumbing taken out;
// it is the reference the new DarknessField is checked against. Never edit it to match the new code.
using System.Collections.Generic;
using UnityEngine;

namespace DarknessCheck
{
    public sealed class OldOverlay
    {
        public const int N = 256;            // max zone side (8x8 chunks * 32); covers any zone
        private const int Falloff = 4;       // cells of soft edge from an open face into the rock
        private const float RevealScale = 1.9f;
        private const int BlurPasses = 5;

        public readonly Color32[] Pixels = new Color32[N * N];   // per-frame output (base + light stamps)
        private readonly float[] _baseLit = new float[N * N];
        private readonly bool[] _underground = new bool[N * N];
        private readonly Color32[] _basePixels = new Color32[N * N];

        public void Recompute(HashSet<Vector2Int> blocksBugs, HashSet<Vector2Int> roof)
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
                    bool s = blocksBugs.Contains(cell);   // tm.IsCellBlockedForBugs(cell)
                    solid[i] = s;
                    roofed[i] = roof.Contains(cell);      // tm.IsRoofCell(cell)
                    cur[i] = s ? 0f : 1f;
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
                        if (!solid[i]) continue;
                        float m = cur[i];
                        if (x > 0)     m = Mathf.Max(m, cur[i - 1] - step);
                        if (x < N - 1) m = Mathf.Max(m, cur[i + 1] - step);
                        if (y > 0)     m = Mathf.Max(m, cur[i - N] - step);
                        if (y < N - 1) m = Mathf.Max(m, cur[i + N] - step);
                        nxt[i] = m;
                    }
                var t = cur; cur = nxt; nxt = t;
            }

            for (int i = 0; i < n2; i++)
            {
                _baseLit[i] = roofed[i] ? 0f : Mathf.Clamp01(cur[i]);
                _underground[i] = roofed[i];
            }

            BlurBaseLit();

            for (int i = 0; i < n2; i++)
            {
                byte v = (byte)(_baseLit[i] * 255f);
                _basePixels[i] = new Color32(v, v, v, 255);
            }
        }

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

        /// <summary>StampLights' body: the base, then every lamp.</summary>
        public void Stamp(IList<(float x, float y, float radius, float strength)> lamps, float undergroundCap)
        {
            System.Array.Copy(_basePixels, Pixels, Pixels.Length);
            foreach (var l in lamps) StampOne(l.x, l.y, l.radius, l.strength, undergroundCap);
        }

        private void StampOne(float wx, float wy, float radius, float strength, float undergroundCap)
        {
            if (radius <= 0.01f || strength <= 0.01f) return;
            float revealR = radius * RevealScale;
            int cxc = Mathf.FloorToInt(wx);
            int cyc = Mathf.FloorToInt(wy);
            int r = Mathf.CeilToInt(revealR);
            for (int y = cyc - r; y <= cyc + r; y++)
            {
                if (y < 0 || y >= N) continue;
                for (int x = cxc - r; x <= cxc + r; x++)
                {
                    if (x < 0 || x >= N) continue;
                    float dx = (x + 0.5f) - wx;
                    float dy = (y + 0.5f) - wy;
                    float t = Mathf.Sqrt(dx * dx + dy * dy) / revealR;
                    if (t >= 1f) continue;
                    int i = y * N + x;
                    float open = Mathf.SmoothStep(1f, 0f, t) * strength;
                    if (_underground[i]) open = Mathf.Min(open, undergroundCap);
                    float lit = Mathf.Max(_baseLit[i], open);
                    byte v = (byte)(lit * 255f);
                    if (v > Pixels[i].r) Pixels[i] = new Color32(v, v, v, 255);
                }
            }
        }

        public float UndergroundDarknessAt(Vector2Int c)
        {
            if (c.x < 0 || c.x >= N || c.y < 0 || c.y >= N) return 0f;
            return Mathf.Clamp01(1f - _baseLit[c.y * N + c.x]);
        }
    }
}
