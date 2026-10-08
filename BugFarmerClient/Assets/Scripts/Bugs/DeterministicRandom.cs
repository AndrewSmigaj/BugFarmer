using System.Text;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Purpose IDs for counter-based RNG.
    /// Each purpose gets a different random stream per bug per tick.
    /// </summary>
    public static class RngPurpose
    {
        public const int Alert = 1;
        public const int Cooldown = 2;
        public const int Direction = 3;
        public const int SpawnAngle = 4;
        public const int SpawnDistance = 5;
        public const int MovementChange = 6;
        public const int TargetOffset = 7;
        public const int Land = 8;        // feed-at-food: landing duration
        public const int Participate = 9; // feed-at-food: per-bug per-window join roll
        public const int Hunt = 10;       // individual predation: per-bug per-window "do I pursue prey now" roll
        public const int LeaveCorpse = 11; // individual predation (S2): eat-vs-leave the corpse roll
    }

    /// <summary>
    /// Counter-based RNG for deterministic simulation.
    /// STATELESS: Hash(worldSeed, swarmId, bugId, tick, purposeId) always produces same result.
    ///
    /// Use this instead of stateful DeterministicRandom to prevent desync from:
    /// - Conditional RNG consumption (if one client's bug is alerted, another isn't)
    /// - Different execution order across clients
    ///
    /// Example:
    ///   float alertRoll = CounterRng.Float(worldSeed, swarmId, bugId, tick, RngPurpose.Alert);
    ///   if (alertRoll < 0.3f) { /* alerted */ }
    /// </summary>
    public static class CounterRng
    {
        // FNV-1a constants for 64-bit hash
        private const ulong FNV_OFFSET = 14695981039346656037;
        private const ulong FNV_PRIME = 1099511628211;

        /// <summary>
        /// Generate deterministic hash from immutable inputs.
        /// Same inputs always produce same output.
        /// </summary>
        public static uint Hash(long worldSeed, string swarmId, int bugId, long tick, int purposeId)
        {
            ulong hash = FNV_OFFSET;

            // Hash worldSeed bytes
            for (int i = 0; i < 8; i++)
            {
                hash ^= (byte)(worldSeed >> (i * 8));
                hash *= FNV_PRIME;
            }

            // Hash swarmId string: its UTF-8 bytes, folded without making a byte array (Stage 1.1)
            if (!string.IsNullOrEmpty(swarmId))
                hash = FoldUtf8(hash, swarmId);

            // Hash bugId bytes
            for (int i = 0; i < 4; i++)
            {
                hash ^= (byte)(bugId >> (i * 8));
                hash *= FNV_PRIME;
            }

            // Hash tick bytes
            for (int i = 0; i < 8; i++)
            {
                hash ^= (byte)(tick >> (i * 8));
                hash *= FNV_PRIME;
            }

            // Hash purposeId bytes
            for (int i = 0; i < 4; i++)
            {
                hash ^= (byte)(purposeId >> (i * 8));
                hash *= FNV_PRIME;
            }

            // Mix and return as uint32
            return (uint)(hash ^ (hash >> 32));
        }

        /// <summary>
        /// Fold a string's UTF-8 bytes into an FNV-1a hash, byte for byte what Encoding.UTF8.GetBytes gives (a surrogate
        /// pair becomes its four bytes; a lone surrogate becomes U+FFFD, EF BF BD, as the default encoder does) — without
        /// making a new array. Stage 1.1 (docs/plans/village-slice.md): GetBytes allocated one on every roll, per bug per
        /// tick. Proven equal to the old hash by tools/sim-determinism --alloc-test.
        /// </summary>
        private static ulong FoldUtf8(ulong hash, string s)
        {
            for (int i = 0; i < s.Length; i++)
            {
                int c = s[i];
                if (c < 0x80)
                {
                    hash = (hash ^ (uint)c) * FNV_PRIME;
                    continue;
                }
                if (c < 0x800)
                {
                    hash = (hash ^ (uint)(0xC0 | (c >> 6))) * FNV_PRIME;
                    hash = (hash ^ (uint)(0x80 | (c & 0x3F))) * FNV_PRIME;
                    continue;
                }
                if (c >= 0xD800 && c <= 0xDBFF && i + 1 < s.Length && s[i + 1] >= 0xDC00 && s[i + 1] <= 0xDFFF)
                {
                    int cp = 0x10000 + ((c - 0xD800) << 10) + (s[i + 1] - 0xDC00);
                    i++;
                    hash = (hash ^ (uint)(0xF0 | (cp >> 18))) * FNV_PRIME;
                    hash = (hash ^ (uint)(0x80 | ((cp >> 12) & 0x3F))) * FNV_PRIME;
                    hash = (hash ^ (uint)(0x80 | ((cp >> 6) & 0x3F))) * FNV_PRIME;
                    hash = (hash ^ (uint)(0x80 | (cp & 0x3F))) * FNV_PRIME;
                    continue;
                }
                if (c >= 0xD800 && c <= 0xDFFF) c = 0xFFFD; // a lone surrogate
                hash = (hash ^ (uint)(0xE0 | (c >> 12))) * FNV_PRIME;
                hash = (hash ^ (uint)(0x80 | ((c >> 6) & 0x3F))) * FNV_PRIME;
                hash = (hash ^ (uint)(0x80 | (c & 0x3F))) * FNV_PRIME;
            }
            return hash;
        }

        /// <summary>
        /// Random float in [0, 1) from counter-based hash.
        /// </summary>
        public static float Float(long worldSeed, string swarmId, int bugId, long tick, int purposeId)
        {
            uint h = Hash(worldSeed, swarmId, bugId, tick, purposeId);
            return (h & 0x7FFFFFFF) / (float)0x7FFFFFFF;
        }

        /// <summary>
        /// Random int in [min, max) from counter-based hash.
        /// </summary>
        public static int RangeInt(long worldSeed, string swarmId, int bugId, long tick, int purposeId, int min, int max)
        {
            if (max <= min) return min;
            uint h = Hash(worldSeed, swarmId, bugId, tick, purposeId);
            return min + (int)(h % (uint)(max - min));
        }

        /// <summary>
        /// Random float in [min, max) from counter-based hash.
        /// </summary>
        public static float Range(long worldSeed, string swarmId, int bugId, long tick, int purposeId, float min, float max)
        {
            return min + Float(worldSeed, swarmId, bugId, tick, purposeId) * (max - min);
        }

        /// <summary>
        /// Integer-only probability test: returns true with probability numerator/denominator.
        /// Compares the raw hash modulo denominator to numerator - no float math, so the result
        /// is bit-identical across platforms (unlike Float(...) &lt; threshold). Use this for
        /// gameplay decisions in the deterministic sim hot path.
        /// </summary>
        public static bool Chance(long worldSeed, string swarmId, int bugId, long tick, int purposeId, int numerator, int denominator)
        {
            if (denominator <= 0) return false;
            uint h = Hash(worldSeed, swarmId, bugId, tick, purposeId);
            return (h % (uint)denominator) < (uint)numerator;
        }
    }

    /// <summary>
    /// Deterministic random number generator using xorshift32.
    /// Each bug gets its own instance seeded from (worldSeed, swarmId, bugId).
    /// All clients with the same seed produce the same sequence.
    ///
    /// WARNING: This stateful RNG can desync if conditional branches consume
    /// values differently across clients. Prefer CounterRng for simulation logic.
    /// Keep this for spawn-time initialization only.
    /// </summary>
    public class DeterministicRandom
    {
        private uint _state;

        /// <summary>
        /// Get/set internal state for sync purposes.
        /// </summary>
        public uint State
        {
            get => _state;
            set => _state = value == 0 ? 1u : value; // Never allow zero
        }

        public DeterministicRandom(long seed)
        {
            // Mix 64-bit seed into 32-bit state
            _state = (uint)(seed ^ (seed >> 32));
            if (_state == 0) _state = 1; // State must never be zero (would stay zero)
        }

        /// <summary>
        /// Create RNG for a specific bug. Same inputs = same sequence.
        /// </summary>
        public static DeterministicRandom ForBug(long worldSeed, string swarmId, int bugId)
        {
            long seed = ComputeBugSeed(worldSeed, swarmId, bugId);
            return new DeterministicRandom(seed);
        }

        /// <summary>
        /// Combine (worldSeed, swarmId, bugId) into unique seed using FNV-1a hash.
        /// </summary>
        public static long ComputeBugSeed(long worldSeed, string swarmId, int bugId)
        {
            // FNV-1a 64-bit - simple hash that XORs each byte and multiplies
            const ulong FNV_OFFSET = 14695981039346656037;
            const ulong FNV_PRIME = 1099511628211;

            ulong hash = FNV_OFFSET;

            // Hash worldSeed bytes
            for (int i = 0; i < 8; i++)
            {
                hash ^= (byte)(worldSeed >> (i * 8));
                hash *= FNV_PRIME;
            }

            // Hash swarmId string
            byte[] swarmBytes = Encoding.UTF8.GetBytes(swarmId);
            foreach (byte b in swarmBytes)
            {
                hash ^= b;
                hash *= FNV_PRIME;
            }

            // Hash bugId bytes
            for (int i = 0; i < 4; i++)
            {
                hash ^= (byte)(bugId >> (i * 8));
                hash *= FNV_PRIME;
            }

            return (long)hash;
        }

        /// <summary>
        /// xorshift32: three XOR-shift operations produce next random value.
        /// </summary>
        private uint NextUInt()
        {
            _state ^= _state << 13;
            _state ^= _state >> 17;
            _state ^= _state << 5;
            return _state;
        }

        /// <summary>
        /// Random float in [0, 1).
        /// </summary>
        public float NextFloat()
        {
            return (NextUInt() & 0x7FFFFFFF) / (float)0x7FFFFFFF;
        }

        /// <summary>
        /// Random float in [min, max).
        /// </summary>
        public float Range(float min, float max)
        {
            return min + NextFloat() * (max - min);
        }

        /// <summary>
        /// Random int in [min, max).
        /// </summary>
        public int RangeInt(int min, int max)
        {
            if (max <= min) return min;
            return min + (int)(NextUInt() % (uint)(max - min));
        }
    }
}
