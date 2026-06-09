using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.World;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles player pickup of ground items, Terraria-style:
    ///   - WALK-OVER AUTO-PICKUP: ordinary drops (wood, flowers, fresh fruit, produce) are
    ///     collected automatically when the player comes within the magnet radius.
    ///   - BUG FOOD IS THE EXCEPTION: rotten fruit is the flies' food — never auto-collected,
    ///     only with the deliberate E key. Keeps you from stripping your own fly farm by
    ///     walking through it.
    ///   - E key still picks up the closest item of ANY type (the deliberate case).
    /// </summary>
    public class PickupController : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private float pickupRange = 2f;
        [SerializeField] private float highlightRange = 3f;
        [SerializeField] private float autoPickupRange = 1.25f;
        [SerializeField] private float autoPickupInterval = 0.25f;

        private GroundItemVisual _highlightedItem;

        // Auto-pickup guards: don't spam the server while a request is in flight, and back
        // off items that keep failing (inventory full / contested pickup).
        private float _nextAutoPickup;
        private readonly Dictionary<string, (int attempts, float nextTry)> _requested = new();

        private void Update()
        {
            UpdateHighlight();

            if (Input.GetKeyDown(KeyCode.E))
            {
                TryPickup();
            }

            TryAutoPickup();
        }

        /// <summary>
        /// Walk-over magnet: request the closest NON-bug-food item in range, rate-limited,
        /// with per-item backoff (3 quick attempts, then a 10s cooldown for that item).
        /// </summary>
        private void TryAutoPickup()
        {
            if (Time.time < _nextAutoPickup) return;
            _nextAutoPickup = Time.time + autoPickupInterval;

            if (GroundItemManager.Instance == null) return;

            var item = GroundItemManager.Instance.GetClosestItem(transform.position, autoPickupRange, includeBugFood: false);
            if (item == null) return;

            if (_requested.TryGetValue(item.ItemId, out var r))
            {
                if (Time.time < r.nextTry) return;
                float delay = r.attempts >= 3 ? 10f : autoPickupInterval * 2f;
                _requested[item.ItemId] = (r.attempts + 1, Time.time + delay);
            }
            else
            {
                _requested[item.ItemId] = (1, Time.time + autoPickupInterval * 2f);
            }
            if (_requested.Count > 64) _requested.Clear(); // bound the guard map

            SendPickupRequest(item.ItemId);
        }

        private void UpdateHighlight()
        {
            if (GroundItemManager.Instance == null)
                return;

            var closest = GroundItemManager.Instance.GetItemAtPosition(transform.position, highlightRange);

            if (closest != _highlightedItem)
            {
                // Clear old highlight (check if still valid)
                if (_highlightedItem != null && _highlightedItem.gameObject.activeInHierarchy)
                {
                    _highlightedItem.SetHighlight(false);
                }

                _highlightedItem = closest;

                if (_highlightedItem != null)
                {
                    _highlightedItem.SetHighlight(true);
                }
            }
        }

        private void TryPickup()
        {
            if (GroundItemManager.Instance == null)
                return;

            var item = GroundItemManager.Instance.GetItemAtPosition(transform.position, pickupRange);
            if (item == null)
                return;

            SendPickupRequest(item.ItemId);
        }

        private void SendPickupRequest(string itemId)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || match == null)
                return;

            var msg = new PickupItemMessage { id = itemId };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.PickupItem, json);
        }
    }
}
