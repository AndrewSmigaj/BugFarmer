using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;
using Unity.Profiling;

namespace BugFarmer.Util
{
    // TEST-ONLY measuring and checking probes (docs/plans/village-slice.md, Stage 1.0b). Every probe is OFF unless the
    // headless test runner turns it on from a command-line flag; when off, each hook in the game code costs one static
    // bool read. None of them changes the simulation: they read state, count, and write files.

    /// <summary>
    /// Cost recorder: the whole tick (a stopwatch around <c>AdvanceOneTick</c>, outside the per-part timers), the bug
    /// drawing per frame, frame times, the snapshot build, and allocations. Arrays are made once, so recording allocates
    /// nothing. Per-window p50/p99/max (CSV rows) and a whole-run histogram (a JSON summary).
    /// </summary>
    public static class CostProbe
    {
        public static bool Enabled;

        const int WindowCap = 1 << 16;                 // samples kept per window (ticks or frames); extra ones are counted, not sorted
        static readonly double TicksToMs = 1000.0 / Stopwatch.Frequency;

        // ---- whole run: log-spaced histograms, 0.001 ms .. ~1000 ms, 40 bins per decade (~6% wide)
        const int BinsPerDecade = 40, Decades = 6, Bins = BinsPerDecade * Decades + 2;
        static readonly long[] _tickHist = new long[Bins], _frameHist = new long[Bins], _renderHist = new long[Bins];
        static long _ticksTotal, _framesTotal, _framesOver16, _framesOver33, _ticksOver4;
        static double _tickMaxRun, _frameMaxRun, _renderMaxRun, _tickSumRun;

        // ---- current window
        static readonly float[] _wTick = new float[WindowCap], _wFrame = new float[WindowCap], _wRender = new float[WindowCap];
        static int _wTickN, _wFrameN, _wRenderN, _wFramesOver16;
        static long _wTickDropped, _wFrameDropped;
        static double _wAllocWithTickSum, _wAllocNoTickSum, _wAllocTickSum; static long _wAllocWithTickN, _wAllocNoTickN, _wAllocTickN;
        static long _wSnapN, _wSnapBytesMax; static double _wSnapMsMax;

        // ---- per tick / per frame scratch
        static long _tickStart, _allocStart, _renderStart, _renderAcc;
        static int _ticksThisFrame, _ticksPrevFrame;

        // ---- allocations: per-thread bytes if the runtime counts them (Mono's Boehm GC likely doesn't), else the
        // Unity profiler counter "GC Allocated In Frame" (Development builds only).
        public static bool ThreadAllocSupported { get; private set; }
        public static bool FrameAllocSupported => _gcFrame.Valid;
        static ProfilerRecorder _gcFrame;

        public static void Start()
        {
            Enabled = true;
            long a0 = GC.GetAllocatedBytesForCurrentThread();
            var probe = new byte[4096];
            long a1 = GC.GetAllocatedBytesForCurrentThread();
            ThreadAllocSupported = a1 - a0 >= probe.Length;
            try { _gcFrame = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame"); }
            catch (Exception) { /* not available in this build */ }
        }

        public static void Stop()
        {
            Enabled = false;
            if (_gcFrame.Valid) _gcFrame.Dispose();
        }

        // -------- hooks (called from the game code only when Enabled)
        public static void TickBegin()
        {
            if (ThreadAllocSupported) _allocStart = GC.GetAllocatedBytesForCurrentThread();
            _tickStart = Stopwatch.GetTimestamp();
        }

        public static void TickEnd()
        {
            double ms = (Stopwatch.GetTimestamp() - _tickStart) * TicksToMs;
            if (ThreadAllocSupported)
            {
                _wAllocTickSum += GC.GetAllocatedBytesForCurrentThread() - _allocStart;
                _wAllocTickN++;
            }
            _ticksThisFrame++;
            _ticksTotal++;
            _tickSumRun += ms;
            if (ms > _tickMaxRun) _tickMaxRun = ms;
            if (ms > 4.0) _ticksOver4++;
            _tickHist[Bin(ms)]++;
            if (_wTickN < WindowCap) _wTick[_wTickN++] = (float)ms; else _wTickDropped++;
        }

        /// <summary>Around a piece of bug drawing (smoothing, trails); summed per frame.</summary>
        public static void RenderBegin() => _renderStart = Stopwatch.GetTimestamp();
        public static void RenderEnd() => _renderAcc += Stopwatch.GetTimestamp() - _renderStart;

        public static void SnapshotBuilt(double ms, long bytes)
        {
            _wSnapN++;
            if (ms > _wSnapMsMax) _wSnapMsMax = ms;
            if (bytes > _wSnapBytesMax) _wSnapBytesMax = bytes;
        }

        /// <summary>Once per frame, late (CostProbeFrame): the frame time, this frame's bug drawing, ticks run.</summary>
        public static void FrameEnd(float frameSeconds)
        {
            double frameMs = frameSeconds * 1000.0, renderMs = _renderAcc * TicksToMs;
            _renderAcc = 0;
            _framesTotal++;
            if (frameMs > 16.7) { _framesOver16++; _wFramesOver16++; }
            if (frameMs > 33.4) _framesOver33++;
            if (frameMs > _frameMaxRun) _frameMaxRun = frameMs;
            if (renderMs > _renderMaxRun) _renderMaxRun = renderMs;
            _frameHist[Bin(frameMs)]++;
            _renderHist[Bin(renderMs)]++;
            if (_wFrameN < WindowCap) _wFrame[_wFrameN++] = (float)frameMs; else _wFrameDropped++;
            if (_wRenderN < WindowCap) _wRender[_wRenderN++] = (float)renderMs;

            // The profiler counter reports the PREVIOUS frame's allocations: pair it with that frame's tick count.
            if (_gcFrame.Valid)
            {
                long bytes = _gcFrame.LastValue;
                if (_ticksPrevFrame > 0) { _wAllocWithTickSum += bytes / (double)_ticksPrevFrame; _wAllocWithTickN++; }
                else { _wAllocNoTickSum += bytes; _wAllocNoTickN++; }
            }
            _ticksPrevFrame = _ticksThisFrame;
            _ticksThisFrame = 0;
        }

        // -------- output
        public const string WindowHeader =
            "real_s,tick,swarms,bugs,ticks,tick_p50_ms,tick_p99_ms,tick_max_ms,frames,frame_p50_ms,frame_p99_ms,frame_max_ms," +
            "frames_over_16_7,draw_p50_ms,draw_p99_ms,draw_max_ms,alloc_per_tick_b,alloc_frame_tick_b,alloc_frame_idle_b," +
            "snapshots,snapshot_max_ms,snapshot_max_bytes,dropped";

        /// <summary>One CSV row for the window just ended; resets the window.</summary>
        public static string WindowRow(double realS, long tick, int swarms, int bugs)
        {
            string row = string.Join(",",
                F(realS, 1), tick.ToString(CultureInfo.InvariantCulture), swarms.ToString(CultureInfo.InvariantCulture),
                bugs.ToString(CultureInfo.InvariantCulture),
                _wTickN.ToString(CultureInfo.InvariantCulture), F(Pct(_wTick, _wTickN, 0.50)), F(Pct(_wTick, _wTickN, 0.99)), F(Pct(_wTick, _wTickN, 1.0)),
                _wFrameN.ToString(CultureInfo.InvariantCulture), F(Pct(_wFrame, _wFrameN, 0.50)), F(Pct(_wFrame, _wFrameN, 0.99)), F(Pct(_wFrame, _wFrameN, 1.0)),
                _wFramesOver16.ToString(CultureInfo.InvariantCulture),
                F(Pct(_wRender, _wRenderN, 0.50)), F(Pct(_wRender, _wRenderN, 0.99)), F(Pct(_wRender, _wRenderN, 1.0)),
                _wAllocTickN > 0 ? F(_wAllocTickSum / _wAllocTickN, 0) : "",
                _wAllocWithTickN > 0 ? F(_wAllocWithTickSum / _wAllocWithTickN, 0) : "",
                _wAllocNoTickN > 0 ? F(_wAllocNoTickSum / _wAllocNoTickN, 0) : "",
                _wSnapN.ToString(CultureInfo.InvariantCulture), F(_wSnapMsMax), _wSnapBytesMax.ToString(CultureInfo.InvariantCulture),
                (_wTickDropped + _wFrameDropped).ToString(CultureInfo.InvariantCulture));
            _wTickN = _wFrameN = _wRenderN = _wFramesOver16 = 0;
            _wTickDropped = _wFrameDropped = 0;
            _wAllocWithTickSum = _wAllocNoTickSum = _wAllocTickSum = 0; _wAllocWithTickN = _wAllocNoTickN = _wAllocTickN = 0;
            _wSnapN = _wSnapBytesMax = 0; _wSnapMsMax = 0;
            return row;
        }

        /// <summary>The whole run, from the histograms (percentiles are bin edges, ~6% resolution).</summary>
        public static string SummaryJson(string mode)
        {
            var sb = new StringBuilder("{\n");
            void Kv(string k, string v, bool last = false) => sb.Append("  \"").Append(k).Append("\": ").Append(v).Append(last ? "\n" : ",\n");
            Kv("perfmode", "\"" + mode + "\"");
            Kv("ticks", _ticksTotal.ToString(CultureInfo.InvariantCulture));
            Kv("tick_mean_ms", F(_ticksTotal > 0 ? _tickSumRun / _ticksTotal : 0));
            Kv("tick_p50_ms", F(HistPct(_tickHist, _ticksTotal, 0.50)));
            Kv("tick_p99_ms", F(HistPct(_tickHist, _ticksTotal, 0.99)));
            Kv("tick_max_ms", F(_tickMaxRun));
            Kv("ticks_over_4ms", _ticksOver4.ToString(CultureInfo.InvariantCulture));
            Kv("frames", _framesTotal.ToString(CultureInfo.InvariantCulture));
            Kv("frame_p50_ms", F(HistPct(_frameHist, _framesTotal, 0.50)));
            Kv("frame_p99_ms", F(HistPct(_frameHist, _framesTotal, 0.99)));
            Kv("frame_max_ms", F(_frameMaxRun));
            Kv("frames_over_16_7ms", _framesOver16.ToString(CultureInfo.InvariantCulture));
            Kv("frames_over_33_4ms", _framesOver33.ToString(CultureInfo.InvariantCulture));
            Kv("draw_p50_ms", F(HistPct(_renderHist, _framesTotal, 0.50)));
            Kv("draw_p99_ms", F(HistPct(_renderHist, _framesTotal, 0.99)));
            Kv("draw_max_ms", F(_renderMaxRun));
            Kv("thread_alloc_supported", ThreadAllocSupported ? "true" : "false");
            Kv("frame_alloc_supported", FrameAllocSupported ? "true" : "false", last: true);
            return sb.Append("}\n").ToString();
        }

        // -------- helpers
        static int Bin(double ms)
        {
            if (ms <= 0.001) return 0;
            int b = 1 + (int)(Math.Log10(ms / 0.001) * BinsPerDecade);
            return b >= Bins ? Bins - 1 : b;
        }

        static double BinUpper(int b) => b == 0 ? 0.001 : 0.001 * Math.Pow(10, b / (double)BinsPerDecade);

        static double HistPct(long[] hist, long n, double p)
        {
            if (n <= 0) return 0;
            long want = (long)Math.Ceiling(p * n), seen = 0;
            for (int b = 0; b < hist.Length; b++) { seen += hist[b]; if (seen >= want) return BinUpper(b); }
            return BinUpper(hist.Length - 1);
        }

        /// <summary>Sorts the window in place (no allocation) and reads the p-th sample.</summary>
        static double Pct(float[] a, int n, double p)
        {
            if (n <= 0) return 0;
            Array.Sort(a, 0, n);
            return a[Math.Min(n - 1, (int)(p * (n - 1) + 0.5))];
        }

        static string F(double v, int decimals = 3) => v.ToString("F" + decimals, CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// The fingerprint log for the equivalence check: every tick, the game's own state check, a test-only check over
    /// each bug's full record, the bug count and whether the tick ran live. Resyncs and replays are marked, so the
    /// checker can treat a run that needed one as inconclusive.
    /// </summary>
    public static class HashLog
    {
        public static bool Enabled;
        static StreamWriter _w;

        public static void Open(string path)
        {
            _w = new StreamWriter(path, false, new UTF8Encoding(false), 1 << 16);
            _w.WriteLine("tick,hash,full,bugs,live");
            Enabled = true;
        }

        public static void Record(long tick, long hash, long fullHash, int bugs, bool live)
        {
            if (_w == null) return;
            _w.Write(tick.ToString(CultureInfo.InvariantCulture)); _w.Write(',');
            _w.Write(hash.ToString("X16", CultureInfo.InvariantCulture)); _w.Write(',');
            _w.Write(fullHash.ToString("X16", CultureInfo.InvariantCulture)); _w.Write(',');
            _w.Write(bugs.ToString(CultureInfo.InvariantCulture)); _w.Write(',');
            _w.WriteLine(live ? '1' : '0');
        }

        /// <summary>A line the checker reads as an event (resync, replay start/end, timeouts).</summary>
        public static void Marker(string kind, long tick)
        {
            if (_w == null) return;
            _w.WriteLine("#" + kind + "," + tick.ToString(CultureInfo.InvariantCulture));
        }

        public static void Close()
        {
            Enabled = false;
            _w?.Flush();
            _w?.Dispose();
            _w = null;
        }
    }

    /// <summary>
    /// The strike and corpse reports, logged on every computer: the one in charge logs what it sends; one that isn't
    /// (with <see cref="Shadow"/>) runs the same passes in log-only mode and logs what it WOULD send. Comparing the
    /// two logs shows whether two builds make the same decisions.
    /// </summary>
    public static class ReportLog
    {
        /// <summary>Run the report passes on a computer that isn't in charge, log-only (never sent).</summary>
        public static bool Shadow;
        /// <summary>Reports are counted (per species, for the behaviour tally) and, if a file is open, logged.</summary>
        public static bool Active;
        static StreamWriter _w;

        /// <summary>Per species: [predation strikes, prey bugs claimed, corpses consumed], since the last <see cref="TakeCounts"/>.</summary>
        static readonly Dictionary<string, long[]> _counts = new Dictionary<string, long[]>();

        public static void Open(string path)
        {
            _w = new StreamWriter(path, false, new UTF8Encoding(false), 1 << 16);
            _w.WriteLine("tick,kind,a,b,ids,sent");
            Active = true;
        }

        static long[] CountsFor(string species)
        {
            species ??= "?";
            if (!_counts.TryGetValue(species, out var c)) _counts[species] = c = new long[3];
            return c;
        }

        /// <summary>What a predator COULD strike this tick (before the local throttle) — the same on every computer.</summary>
        public static void Detect(long tick, string predator, string prey, List<int> victimIds)
        {
            if (_w == null) return;
            _w.WriteLine(tick.ToString(CultureInfo.InvariantCulture) + ",detect," + predator + "," + prey + "," +
                         string.Join(";", victimIds) + ",0");
        }

        public static void Strike(long tick, string predator, string prey, string predatorSpecies, int[] victimIds, bool sent)
        {
            var c = CountsFor(predatorSpecies);
            c[0]++;
            c[1] += victimIds.Length;
            if (_w == null) return;
            _w.WriteLine(tick.ToString(CultureInfo.InvariantCulture) + ",strike," + predator + "," + prey + "," +
                         string.Join(";", victimIds) + "," + (sent ? "1" : "0"));
        }

        public static void Corpse(long tick, string eaterSpecies, string foodId, bool sent)
        {
            CountsFor(eaterSpecies)[2]++;
            if (_w == null) return;
            _w.WriteLine(tick.ToString(CultureInfo.InvariantCulture) + ",corpse," + foodId + ",,," + (sent ? "1" : "0"));
        }

        /// <summary>The per-species counts since the last call (then cleared).</summary>
        public static Dictionary<string, long[]> TakeCounts()
        {
            var copy = new Dictionary<string, long[]>(_counts);
            _counts.Clear();
            return copy;
        }

        /// <summary>A line marking an event the checker must know about (first live tick, resync, replay).</summary>
        public static void Marker(string kind, long tick)
        {
            _w?.WriteLine("#" + kind + "," + tick.ToString(CultureInfo.InvariantCulture));
        }

        public static void Close()
        {
            _w?.Flush();
            _w?.Dispose();
            _w = null;
        }
    }
}
