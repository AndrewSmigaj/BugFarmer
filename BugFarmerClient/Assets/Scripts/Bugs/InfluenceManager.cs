using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.Entities;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Manages player cell positions from server-authored influence events.
    /// CRITICAL: Bug AI reads from this manager, NOT from player transforms.
    /// This ensures all clients process the same ordered event stream for deterministic behavior.
    ///
    /// Rules:
    /// - PLAYER_CELL_ENTER overwrites cell position
    /// - PLAYER_CELL_LEAVE does nothing (keeps last known position)
    /// - This guarantees single cell per player, no transient states
    /// </summary>
    public class InfluenceManager : MonoBehaviour
    {
        public static InfluenceManager Instance { get; private set; }

        // Player cell positions from server events only
        // Key: player_id, Value: (cellX, cellY)
        private readonly Dictionary<string, (int cellX, int cellY)> _playerCells = new();

        // Event type constants (must match server)
        public const string EventPlayerCellEnter = "PLAYER_CELL_ENTER";
        public const string EventPlayerCellLeave = "PLAYER_CELL_LEAVE";
        public const string EventSwarmCenterMove = "SWARM_CENTER_MOVE";
        public const string EventBugRemoved = "BUG_REMOVED";
        public const string EventBugSpawned = "BUG_SPAWNED";

        private void Awake()
        {
            Instance = this;
        }

        // NOTE: OpCode 71 (InfluenceBroadcast) is handled by SwarmManager,
        // which controls event buffering during REPLAY state and calls
        // ProcessInfluenceEvent() directly for deterministic event ordering.

        /// <summary>
        /// Process a single influence event.
        /// Called from match data handler or during late join replay.
        /// </summary>
        public void ProcessInfluenceEvent(InfluenceEvent evt)
        {
            switch (evt.type)
            {
                case EventPlayerCellEnter:
                    // Overwrite cell position - player is now in this cell
                    _playerCells[evt.player_id] = (evt.cell_x, evt.cell_y);
                    break;

                case EventPlayerCellLeave:
                    // DO NOTHING - keep last known position
                    // ENTER will overwrite when player enters new cell
                    // This guarantees single cell per player, no transient states
                    break;

                case EventSwarmCenterMove:
                    // Forward to SwarmManager (future: implement swarm center tracking)
                    // SwarmManager.Instance?.UpdateSwarmCenter(evt.swarm_id, evt.cell_x, evt.cell_y);
                    break;

                case EventBugRemoved:
                    // Remove bug from swarm (for late joiner replay)
                    SwarmManager.Instance?.GetSwarm(evt.swarm_id)?.RemoveBugsById(new[] { evt.bug_id });
                    break;

                case EventBugSpawned:
                    // Future: handle bug spawning for reproduction
                    break;

                default:
                    Debug.LogWarning($"[InfluenceManager] Unknown event type: {evt.type}");
                    break;
            }
        }

        /// <summary>
        /// Get all player cells for bug AI.
        /// Returns cell coordinates only - deterministic for all clients.
        /// </summary>
        public IEnumerable<(string playerId, int cellX, int cellY)> GetPlayerCells()
        {
            foreach (var kvp in _playerCells)
            {
                yield return (kvp.Key, kvp.Value.cellX, kvp.Value.cellY);
            }
        }

        /// <summary>
        /// Get player count for debugging/validation.
        /// </summary>
        public int PlayerCellCount => _playerCells.Count;

        /// <summary>
        /// Clear all player cells.
        /// Called when leaving match or during late join initialization.
        /// </summary>
        public void ClearPlayerCells()
        {
            _playerCells.Clear();
        }

        /// <summary>
        /// Remove a specific player's cell.
        /// Called when player leaves.
        /// </summary>
        public void RemovePlayerCell(string playerId)
        {
            _playerCells.Remove(playerId);
        }
    }
}
