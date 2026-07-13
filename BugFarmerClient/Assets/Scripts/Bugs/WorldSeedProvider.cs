using System.Text;
using UnityEngine;
using Nakama;
using BugFarmer.Networking;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Singleton that handles OpCode 68 (WorldInit) to store world seed
    /// for deterministic bug simulation. Each SwarmVisual manages its own
    /// tick timing - this class only provides the seed.
    /// </summary>
    public class WorldSeedProvider : MonoBehaviour
    {
        public static WorldSeedProvider Instance { get; private set; }

        /// <summary>
        /// World seed for deterministic RNG. All clients receive same seed.
        /// Used by BugAgent to create per-bug seeded RNG.
        /// </summary>
        public long WorldSeed { get; private set; }

        /// <summary>
        /// Observation/arena zone flag from WorldInit: bugs suppress their cosmetic attack/flee reaction to
        /// the player (paired with the server peace gates) so the player can walk among them undisturbed.
        /// </summary>
        public bool Peaceful { get; private set; }

        /// <summary>
        /// True after WorldInit message received from server.
        /// SwarmVisual should not simulate until this is true.
        /// </summary>
        public bool IsInitialized { get; private set; }

        /// <summary>
        /// Current server tick. Updated from WorldInit and SwarmUpdate messages.
        /// Used for sync comparison in drift detection.
        /// </summary>
        public long CurrentTick { get; private set; }

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        private void Start()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData += HandleMatchData;
            }
            else
            {
                Debug.LogError("[WorldSeedProvider] WorldManager not found!");
            }
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.OnMatchData -= HandleMatchData;
            }

            if (Instance == this)
            {
                Instance = null;
            }
        }

        private void HandleMatchData(IMatchState state)
        {
            if (state.State == null || state.State.Length == 0) return;

            switch (state.OpCode)
            {
                case OpCodes.WorldInit:
                    var initMsg = JsonUtility.FromJson<WorldInitMessage>(Encoding.UTF8.GetString(state.State));
                    WorldSeed = initMsg.world_seed;
                    CurrentTick = initMsg.tick;
                    Peaceful = initMsg.peaceful;
                    IsInitialized = true;
                    Debug.Log($"[WorldSeedProvider] Initialized with seed: {WorldSeed}, tick: {CurrentTick}");
                    break;

                case OpCodes.SwarmUpdate:
                    // Keep tick updated from periodic swarm updates
                    var swarmMsg = JsonUtility.FromJson<SwarmUpdateMessage>(Encoding.UTF8.GetString(state.State));
                    if (swarmMsg != null)
                    {
                        CurrentTick = swarmMsg.tick;
                    }
                    break;
            }
        }

        /// <summary>
        /// Set tick manually during replay/late join.
        /// Used by SwarmManager when controlling ticks externally.
        /// </summary>
        public void SetTick(long tick)
        {
            CurrentTick = tick;
        }

        /// <summary>
        /// Initialize seed and tick directly (for late join, bypasses OpCode 68).
        /// Used when receiving LateJoinSnapshot with embedded world seed.
        /// </summary>
        public void Initialize(long seed, long tick)
        {
            WorldSeed = seed;
            CurrentTick = tick;
            IsInitialized = true;
            Debug.Log($"[WorldSeedProvider] Initialized directly with seed: {seed}, tick: {tick}");
        }

        /// <summary>
        /// Reset state manually if needed (e.g., when leaving match without scene reload).
        /// Note: New WorldInit automatically overwrites old seed on rejoin.
        /// </summary>
        public void Reset()
        {
            WorldSeed = 0;
            CurrentTick = 0;
            IsInitialized = false;
        }
    }
}
