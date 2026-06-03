using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using BugFarmer.Bugs;

namespace BugFarmer.Tracing
{
    /// <summary>
    /// Ring buffer that keeps last N ticks of trace data.
    /// Dump to file only when requested.
    /// </summary>
    public class TickTraceBuffer
    {
        private const int BufferSize = 500;  // ~50 seconds at 10 ticks/sec
        private readonly Queue<TickSnapshot> _buffer = new();

        public struct TickSnapshot
        {
            public long Tick;
            public long StateHash;
            public List<BugTrace> Bugs;
            public List<PlayerTarget> Players;
        }

        public int Count => _buffer.Count;

        public void RecordTick(long tick, long hash, List<BugTrace> bugs, List<PlayerTarget> players)
        {
            if (_buffer.Count >= BufferSize)
                _buffer.Dequeue();  // Drop oldest

            _buffer.Enqueue(new TickSnapshot
            {
                Tick = tick,
                StateHash = hash,
                Bugs = new List<BugTrace>(bugs),
                Players = new List<PlayerTarget>(players)
            });
        }

        public void DumpToFile(string clientId)
        {
            var timestamp = DateTime.Now.ToString("HHmmss");
            var path = Path.Combine(Application.persistentDataPath, $"trace_{clientId}_{timestamp}.csv");

            var sb = new StringBuilder();
            sb.AppendLine($"# State hashes per tick (for quick divergence check)");
            foreach (var snap in _buffer)
            {
                sb.AppendLine($"# TICK {snap.Tick} HASH {snap.StateHash:X16} PLAYERS {snap.Players.Count}");
            }
            sb.AppendLine();
            sb.AppendLine(BugTrace.CsvHeader);

            foreach (var snap in _buffer)
            {
                foreach (var bug in snap.Bugs)
                    sb.AppendLine(bug.ToCsv());
            }

            File.WriteAllText(path, sb.ToString());
            UnityEngine.Debug.Log($"[Trace] Dumped {_buffer.Count} ticks to {path}");
        }

        public long? GetHashAtTick(long tick)
        {
            var snap = _buffer.FirstOrDefault(s => s.Tick == tick);
            return snap.Tick == tick ? snap.StateHash : null;
        }

        public void Clear() => _buffer.Clear();
    }
}
