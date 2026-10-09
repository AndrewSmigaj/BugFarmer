// darkness-check — the darkness overlay's maths since Stage 1.5 (DarknessField, linked from the client) against the
// overlay as it was before (OldOverlay), on random 256 x 256 zones: block masses and scattered blocks, roofed caves,
// cells outside the zone in the sets, camera windows anywhere (corners and the whole zone included), lamps inside,
// outside and across a window's edges. PASS = every window pixel and every "underground darkness" value matches the old
// one, give or take one shade of 255 (the blur is now a row pass then a column pass: the same means, summed in another
// order). Then a 512 x 512 zone: a buried mass in its far corner, which the old 256 overlay never covered, must be dark.
//
//   dotnet run --project tools/darkness-check            exit 0 = the same picture
using System;
using System.Collections.Generic;
using UnityEngine;
using BugFarmer.World;

namespace DarknessCheck
{
    public static class Program
    {
        private const int Trials = 12, WindowsPerTrial = 25;

        public static int Main()
        {
            var rng = new Random(20261009);
            int failures = 0, shadeDiffs = 0;
            long pixelsCompared = 0;
            for (int trial = 0; trial < Trials; trial++)
            {
                var (solid, roof) = RandomZone(rng, OldOverlay.N);
                var old = new OldOverlay();
                old.Recompute(solid, roof);
                var field = new DarknessField(OldOverlay.N, OldOverlay.N);
                field.Build(solid, roof);

                // Underground darkness, every cell and a ring outside the zone.
                for (int y = -2; y < OldOverlay.N + 2; y++)
                    for (int x = -2; x < OldOverlay.N + 2; x++)
                    {
                        float a = old.UndergroundDarknessAt(new Vector2Int(x, y)), b = field.UndergroundDarknessAt(x, y);
                        if (Math.Abs(a - b) > 1e-4f)
                        {
                            if (failures++ < 10) Console.WriteLine($"trial {trial}: underground darkness at {x},{y}: old {a} new {b}");
                        }
                    }

                for (int w = 0; w < WindowsPerTrial; w++)
                {
                    int winW, winH, winX, winY;
                    if (w == 0) { winW = winH = OldOverlay.N; winX = winY = 0; }   // the whole zone, no lamps: the base itself
                    else
                    {
                        winW = Math.Min(OldOverlay.N, 32 * rng.Next(1, 6));
                        winH = Math.Min(OldOverlay.N, 32 * rng.Next(1, 5));
                        winX = w % 5 == 1 ? 0 : w % 5 == 2 ? OldOverlay.N - winW : rng.Next(0, OldOverlay.N - winW + 1);
                        winY = w % 5 == 1 ? 0 : w % 5 == 2 ? OldOverlay.N - winH : rng.Next(0, OldOverlay.N - winH + 1);
                    }
                    var lamps = new List<(float x, float y, float radius, float strength)>();
                    if (w > 0)
                    {
                        int n = rng.Next(0, 7);
                        for (int k = 0; k < n; k++)
                        {
                            // Near the window (inside, outside or across its edges) most of the time, anywhere otherwise.
                            float lx = k % 3 == 0 ? (float)(rng.NextDouble() * (OldOverlay.N + 40) - 20) : winX + (float)(rng.NextDouble() * (winW + 24) - 12);
                            float ly = k % 3 == 0 ? (float)(rng.NextDouble() * (OldOverlay.N + 40) - 20) : winY + (float)(rng.NextDouble() * (winH + 24) - 12);
                            float strength = k % 4 == 3 ? 0f : (float)rng.NextDouble();
                            lamps.Add((lx, ly, (float)(0.5 + rng.NextDouble() * 8), strength));
                        }
                    }
                    float cap = (float)(0.2 + rng.NextDouble() * 0.8);

                    old.Stamp(lamps, cap);
                    var pixels = new Color32[winW * winH];
                    field.FillWindow(pixels, winX, winY, winW, winH);
                    foreach (var l in lamps) field.StampLamp(pixels, winX, winY, winW, winH, l.x, l.y, l.radius, l.strength, cap);

                    for (int y = 0; y < winH; y++)
                        for (int x = 0; x < winW; x++)
                        {
                            var a = old.Pixels[(winY + y) * OldOverlay.N + winX + x];
                            var b = pixels[y * winW + x];
                            pixelsCompared++;
                            int d = Math.Abs(a.r - b.r);
                            if (d == 1) shadeDiffs++;
                            if (d > 1 || b.r != b.g || b.g != b.b || b.a != 255)
                            {
                                if (failures++ < 10)
                                    Console.WriteLine($"trial {trial} window {winX},{winY} {winW}x{winH}: cell {winX + x},{winY + y} old {a.r} new {b.r},{b.g},{b.b},{b.a}");
                            }
                        }
                }
            }
            Console.WriteLine($"256 x 256: {Trials} zones, {pixelsCompared:N0} window pixels compared; {shadeDiffs} differ by one shade, {failures} differ by more");

            // 512 x 512: a buried mass in the far corner, a roofed cave next to it, open ground elsewhere.
            var solid512 = new HashSet<Vector2Int>();
            for (int y = 450; y < 500; y++) for (int x = 430; x < 500; x++) solid512.Add(new Vector2Int(x, y));
            var roof512 = new HashSet<Vector2Int>();
            for (int y = 300; y < 330; y++) for (int x = 300; x < 340; x++) roof512.Add(new Vector2Int(x, y));
            var f512 = new DarknessField(512, 512);
            f512.Build(solid512, roof512);
            int ok512 = 0;
            void Expect(string what, bool cond) { if (cond) ok512++; else { failures++; Console.WriteLine($"512: {what}"); } }
            var corner = new Color32[96 * 64];
            f512.FillWindow(corner, 512 - 96, 512 - 64, 96, 64);
            Expect("the middle of the buried mass in the far corner is dark", corner[(475 - 448) * 96 + (465 - 416)].r == 0);
            Expect("open ground in the far corner is lit", corner[(455 - 448) * 96 + (420 - 416)].r == 255);
            Expect("the roofed cave is fully underground", f512.UndergroundDarknessAt(320, 315) > 0.99f);
            Expect("open ground is not underground", f512.UndergroundDarknessAt(100, 100) == 0f);
            Expect("outside the zone is not underground", f512.UndergroundDarknessAt(512, 10) == 0f);
            var cave = new Color32[64 * 64];
            f512.FillWindow(cave, 290, 290, 64, 64);
            byte before = cave[(315 - 290) * 64 + (320 - 290)].r;
            f512.StampLamp(cave, 290, 290, 64, 64, 320.5f, 315.5f, 4f, 1f, 0.4f);
            byte after = cave[(315 - 290) * 64 + (320 - 290)].r;
            Expect($"a torch in the cave opens it to the underground cap (0 → {after}, want {(byte)(0.4f * 255f)})", before == 0 && after == (byte)(0.4f * 255f));
            Console.WriteLine($"512 x 512: {ok512} of 6 checks");

            Console.WriteLine(failures == 0 ? "PASS — the darkness is the old picture, and covers a 512 zone" : $"FAIL ({failures})");
            return failures == 0 ? 0 : 1;
        }

        // Block masses (some with holes), scattered blocks, roofed caves partly over the masses, and a few cells outside
        // the zone (which neither version may use).
        private static (HashSet<Vector2Int> solid, HashSet<Vector2Int> roof) RandomZone(Random rng, int n)
        {
            var solid = new HashSet<Vector2Int>();
            var roof = new HashSet<Vector2Int>();
            for (int m = rng.Next(4, 12); m > 0; m--)
            {
                int w = rng.Next(3, 40), h = rng.Next(3, 40), x0 = rng.Next(-10, n), y0 = rng.Next(-10, n);
                for (int y = y0; y < y0 + h; y++)
                    for (int x = x0; x < x0 + w; x++)
                        if (rng.NextDouble() > 0.04) solid.Add(new Vector2Int(x, y));
            }
            for (int k = n * n / 50; k > 0; k--) solid.Add(new Vector2Int(rng.Next(0, n), rng.Next(0, n)));
            for (int c = rng.Next(1, 5); c > 0; c--)
            {
                int w = rng.Next(8, 50), h = rng.Next(8, 40), x0 = rng.Next(-10, n), y0 = rng.Next(-10, n);
                for (int y = y0; y < y0 + h; y++)
                    for (int x = x0; x < x0 + w; x++)
                        roof.Add(new Vector2Int(x, y));
            }
            solid.Add(new Vector2Int(-1, 5)); solid.Add(new Vector2Int(n, 5)); roof.Add(new Vector2Int(5, n));
            return (solid, roof);
        }
    }
}
