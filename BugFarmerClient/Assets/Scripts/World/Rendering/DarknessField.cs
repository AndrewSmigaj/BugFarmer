using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// The darkness overlay's maths, apart from Unity's textures and camera (DarknessOverlay does the plumbing), so it can
    /// be checked headless against the overlay as it was before Stage 1.5 (tools/darkness-check).
    ///
    /// The FIELD is one value per zone cell (index y * Width + x): buried-from-solids darkness (open cells lit, solid
    /// cells darkening from the exposed face inward over <see cref="Falloff"/> cells), fully dark where the zone is
    /// authored as roofed (underground), then softened by a 3x3 box blur. A WINDOW of it — a rectangle of zone cells —
    /// is copied into the pixels the graphics card gets, and each lamp opens the darkness back up where it reaches.
    /// </summary>
    public sealed class DarknessField
    {
        public const int Falloff = 4;           // cells of soft edge from an open face into the rock
        public const int BlurPasses = 5;        // 3x3 box-blur passes → a wider soft cave mouth (a torch fades in over more distance)
        public const float RevealScale = 1.9f;  // a torch's reveal reaches this * its light radius (bright core, dim ring)

        public readonly int Width, Height;
        private readonly float[] _baseLit;       // lit value per cell (0 = dark, 1 = lit), blurred
        private readonly bool[] _underground;    // roofed (no sun) per cell — caps a torch's reveal underground
        private readonly Color32[] _basePixels;  // _baseLit as pixels (no lights)

        public DarknessField(int width, int height)
        {
            Width = width;
            Height = height;
            int n = width * height;
            _baseLit = new float[n];
            _underground = new bool[n];
            _basePixels = new Color32[n];
        }

        /// <summary>Work the field out from the zone's solid (blocks bugs) and roofed cells; cells outside the zone are
        /// ignored. The sets are sparse, so they are walked once rather than asked about every cell.</summary>
        public void Build(IEnumerable<Vector2Int> solidCells, IEnumerable<Vector2Int> roofCells)
        {
            int W = Width, H = Height, n2 = W * H;
            var solid = new bool[n2];
            var roofed = new bool[n2];
            foreach (var c in solidCells)
                if (c.x >= 0 && c.x < W && c.y >= 0 && c.y < H) solid[c.y * W + c.x] = true;
            foreach (var c in roofCells)
                if (c.x >= 0 && c.x < W && c.y >= 0 && c.y < H) roofed[c.y * W + c.x] = true;
            var cur = new float[n2];
            for (int i = 0; i < n2; i++) cur[i] = solid[i] ? 0f : 1f;   // solid starts dark, open lit

            // A "light flood" growing inward from open cells; deep rock it can't reach stays black.
            float step = 1f / Falloff;
            var nxt = new float[n2];
            for (int pass = 0; pass < Falloff; pass++)
            {
                System.Array.Copy(cur, nxt, n2);
                for (int y = 0; y < H; y++)
                    for (int x = 0; x < W; x++)
                    {
                        int i = y * W + x;
                        if (!solid[i]) continue;                 // open cells stay fully lit
                        float m = cur[i];
                        if (x > 0)     m = Mathf.Max(m, cur[i - 1] - step);
                        if (x < W - 1) m = Mathf.Max(m, cur[i + 1] - step);
                        if (y > 0)     m = Mathf.Max(m, cur[i - W] - step);
                        if (y < H - 1) m = Mathf.Max(m, cur[i + W] - step);
                        nxt[i] = m;
                    }
                var t = cur; cur = nxt; nxt = t;
            }

            // Combined darkness = max(buried, roofed). A roofed cell (underground) is fully dark — tunnels AND block
            // faces — until a carried light opens it back up. Surface block masses keep their buried soft edge.
            for (int i = 0; i < n2; i++)
            {
                _baseLit[i] = roofed[i] ? 0f : Mathf.Clamp01(cur[i]);
                _underground[i] = roofed[i];
            }

            Blur();   // soften the cave-mouth boundary + edges so the dark→lit transition isn't abrupt

            for (int i = 0; i < n2; i++)
            {
                byte v = (byte)(_baseLit[i] * 255f);
                _basePixels[i] = new Color32(v, v, v, 255);
            }
        }

        /// <summary>3x3 box blur, <see cref="BlurPasses"/> times: each cell becomes the mean of the cells of its 3x3 block
        /// that lie inside the zone. Done as a row pass then a column pass — the same means, a third of the work.</summary>
        private void Blur()
        {
            int W = Width, H = Height;
            var row = new float[W * H];   // each cell: the mean of itself and its in-zone left/right neighbours
            for (int pass = 0; pass < BlurPasses; pass++)
            {
                for (int y = 0; y < H; y++)
                {
                    int o = y * W;
                    for (int x = 0; x < W; x++)
                    {
                        float s = _baseLit[o + x];
                        int c = 1;
                        if (x > 0) { s += _baseLit[o + x - 1]; c++; }
                        if (x < W - 1) { s += _baseLit[o + x + 1]; c++; }
                        row[o + x] = s / c;
                    }
                }
                for (int y = 0; y < H; y++)
                {
                    int o = y * W;
                    for (int x = 0; x < W; x++)
                    {
                        int i = o + x;
                        float s = row[i];
                        int c = 1;
                        if (y > 0) { s += row[i - W]; c++; }
                        if (y < H - 1) { s += row[i + W]; c++; }
                        _baseLit[i] = s / c;
                    }
                }
            }
        }

        /// <summary>Smooth "underground darkness" at a cell (0 = surface/lit, 1 = deep underground); 0 outside the zone.</summary>
        public float UndergroundDarknessAt(int x, int y)
        {
            if (x < 0 || x >= Width || y < 0 || y >= Height) return 0f;
            return Mathf.Clamp01(1f - _baseLit[y * Width + x]);
        }

        /// <summary>Copy the window of zone cells [winX, winX+winW) x [winY, winY+winH) — which must lie inside the zone —
        /// into `pixels` (row-major, winW wide).</summary>
        public void FillWindow(Color32[] pixels, int winX, int winY, int winW, int winH)
        {
            for (int y = 0; y < winH; y++)
                System.Array.Copy(_basePixels, (winY + y) * Width + winX, pixels, y * winW, winW);
        }

        /// <summary>
        /// Open the darkness in the window where a lamp at world position (wx, wy) reaches: gradual (bright core → dim
        /// ring), faded in by the lamp's own on-ness (no snap), and capped underground so a pool stays a warm dim, never
        /// brighter than noon. Only the cells inside the window are drawn.
        /// </summary>
        public void StampLamp(Color32[] pixels, int winX, int winY, int winW, int winH,
                              float wx, float wy, float radius, float strength, float undergroundCap)
        {
            if (radius <= 0.01f || strength <= 0.01f) return;
            float revealR = radius * RevealScale;   // open the darkness over a WIDER area than the bright light
            int cxc = Mathf.FloorToInt(wx);          // cellSize = 1
            int cyc = Mathf.FloorToInt(wy);
            int r = Mathf.CeilToInt(revealR);
            int x0 = Mathf.Max(cxc - r, winX), x1 = Mathf.Min(cxc + r, winX + winW - 1);
            int y0 = Mathf.Max(cyc - r, winY), y1 = Mathf.Min(cyc + r, winY + winH - 1);
            for (int y = y0; y <= y1; y++)
            {
                for (int x = x0; x <= x1; x++)
                {
                    float dx = (x + 0.5f) - wx;
                    float dy = (y + 0.5f) - wy;
                    float t = Mathf.Sqrt(dx * dx + dy * dy) / revealR;
                    if (t >= 1f) continue;
                    int i = y * Width + x;                       // the field
                    int wi = (y - winY) * winW + (x - winX);     // the window
                    float open = Mathf.SmoothStep(1f, 0f, t) * strength;
                    if (_underground[i]) open = Mathf.Min(open, undergroundCap);
                    float lit = Mathf.Max(_baseLit[i], open);
                    byte v = (byte)(lit * 255f);
                    if (v > pixels[wi].r) pixels[wi] = new Color32(v, v, v, 255);
                }
            }
        }
    }
}
