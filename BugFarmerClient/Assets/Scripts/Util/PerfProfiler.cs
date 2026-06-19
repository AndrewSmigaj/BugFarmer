using System.Collections.Generic;
using System.Diagnostics;

namespace BugFarmer.Util
{
    /// <summary>
    /// Lightweight CLIENT cost profiler for the bug system. Two outputs from one set of markers:
    ///   1. UnityEngine.Profiling.Profiler markers — ALWAYS emitted, so the Unity Profiler window
    ///      (Window ▸ Analysis ▸ Profiler) shows full CPU/GC/call-count detail when you record. This is
    ///      the deep tool; use it in the editor to find what's actually hot.
    ///   2. A cheap Stopwatch accumulator — gated by <see cref="Enabled"/> (default OFF) — feeding the live
    ///      DebugOverlay F7 panel, so you can watch per-subsystem ms + FPS in a player BUILD without the editor.
    ///
    /// Pure observation: it only TIMES existing work, never touches the deterministic (hashed) bug sim, so a
    /// profiled client still matches its peers. When Enabled is false the Stopwatch path is a single bool
    /// check — near-zero cost — so it is safe to leave the markers compiled in.
    ///
    /// Usage (whole method, early-return safe via the C# `using` declaration — no re-indent):
    ///     private void LateUpdate() { using var _p = PerfProfiler.Sample("Render.Trail"); ... }
    /// Frame-scoped: <see cref="EndFrame"/> snapshots + clears the accumulators each frame (called once per
    /// frame from SwarmManager.Update), so the panel shows the most recent full frame's cost.
    /// </summary>
    public static class PerfProfiler
    {
        /// <summary>Flip on (DebugOverlay F7) to feed the in-build panel. Off = the Stopwatch path no-ops.</summary>
        public static bool Enabled;

        public struct Stat { public double ms; public int calls; }

        static readonly Dictionary<string, (long ticks, int calls)> _cur = new();
        static readonly Dictionary<string, Stat> _display = new();
        static readonly double _ticksToMs = 1000.0 / Stopwatch.Frequency;

        /// <summary>Time a hot path: <c>using var _p = PerfProfiler.Sample("Render.Interpolate");</c></summary>
        public static Scope Sample(string scope) => new Scope(scope);

        public readonly struct Scope : System.IDisposable
        {
            readonly string _scope;
            readonly long _start;
            readonly bool _timed;

            public Scope(string scope)
            {
                UnityEngine.Profiling.Profiler.BeginSample(scope); // always: Unity Profiler sees it
                _scope = scope;
                _timed = Enabled; // captured at Begin so a mid-scope toggle stays balanced
                _start = _timed ? Stopwatch.GetTimestamp() : 0L;
            }

            public void Dispose()
            {
                if (_timed)
                {
                    long dt = Stopwatch.GetTimestamp() - _start;
                    _cur.TryGetValue(_scope, out var e);
                    _cur[_scope] = (e.ticks + dt, e.calls + 1);
                }
                UnityEngine.Profiling.Profiler.EndSample();
            }
        }

        /// <summary>Snapshot this frame's accumulators into the display set and clear. Call once per frame.</summary>
        public static void EndFrame()
        {
            _display.Clear();
            if (Enabled)
            {
                foreach (var kv in _cur)
                    _display[kv.Key] = new Stat { ms = kv.Value.ticks * _ticksToMs, calls = kv.Value.calls };
            }
            if (_cur.Count > 0) _cur.Clear();
        }

        /// <summary>The most recent full frame's per-scope cost (ms + call count). Read by the overlay.</summary>
        public static IReadOnlyDictionary<string, Stat> Display => _display;
    }
}
