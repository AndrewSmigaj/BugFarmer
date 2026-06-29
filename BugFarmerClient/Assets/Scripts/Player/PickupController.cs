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

        // Floating keycap-E badge above the grabbable item (one reusable
        // world-space sprite; honest-range rules in UpdatePrompt)
        private SpriteRenderer _ePrompt;

        // Auto-pickup guards: don't spam the server while a request is in flight, and back
        // off items that keep failing (inventory full / contested pickup).
        private float _nextAutoPickup;
        private readonly Dictionary<string, (int attempts, float nextTry)> _requested = new();

        // Magnet marks: ids WE requested, with timestamps. When the remove broadcast for a
        // marked id arrives, GroundItemManager plays the fly-to-player tween instead of the
        // plain fade. TTL ~2s: pickup REJECTIONS are generic errors with no item id, so a
        // mark can leak — without the TTL, another player winning the race later would
        // magnet the item toward the LOSER. (Within the TTL that residual race is an
        // accepted cosmetic.)
        private const float MarkTTL = 2f;
        private static readonly Dictionary<string, float> _magnetMarks = new();

        /// <summary>
        /// True (and consumes the mark) if this id was requested by US within the TTL.
        /// Called by GroundItemManager on every remove broadcast.
        /// </summary>
        public static bool ConsumeMark(string itemId)
        {
            if (!_magnetMarks.TryGetValue(itemId, out float at))
                return false;
            _magnetMarks.Remove(itemId);
            return Time.time - at <= MarkTTL;
        }

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

            var closest = MouseTarget(highlightRange);

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

            UpdatePrompt();
        }

        /// <summary>
        /// The KEYCAP-E badge above an item — HONEST: it only appears when E
        /// would actually work (within pickupRange, NOT highlightRange — the
        /// old [E] text showed at 3.0 while pickup works at 2.0, a lie), and
        /// only where the deliberate grab MATTERS:
        ///   - E-required items (bug food / no-auto-pickup fruit): always in reach
        ///   - ordinary drops: only when the walk-over magnet is failing for
        ///     that item (backoff after rejections — e.g. inventory full)
        /// Repositioned every frame (items bob).
        /// </summary>
        private void UpdatePrompt()
        {
            GroundItemVisual target = null;
            if (GroundItemManager.Instance != null)
            {
                var closest = MouseTarget(pickupRange);
                if (closest != null && closest.gameObject.activeInHierarchy)
                {
                    var def = BugFarmer.Data.EntityDatabase.Get(closest.ItemType);
                    bool eRequired = def != null && (def.FoodValue > 0 || def.NoAutoPickup);
                    bool magnetFailing = _requested.TryGetValue(closest.ItemId, out var r)
                                         && r.attempts >= 2;
                    if (eRequired || magnetFailing)
                        target = closest;
                }
            }

            if (_ePrompt == null)
            {
                if (target == null) return;
                var go = new GameObject("PickupPromptE");
                _ePrompt = go.AddComponent<SpriteRenderer>();
                _ePrompt.sprite = Resources.Load<Sprite>("UI/keycap_e");
                _ePrompt.sortingLayerName = "Occupants";
                _ePrompt.sortingOrder = 950; // above world objects
                // keycap art is 14px at PPU 100 (0.14 units) — scale to ~0.5 cell
                go.transform.localScale = Vector3.one * 3.5f;
            }

            _ePrompt.gameObject.SetActive(target != null);
            if (target != null)
            {
                var sr = target.GetComponentInChildren<SpriteRenderer>();
                float topY = sr != null ? sr.bounds.max.y : target.transform.position.y + 0.4f;
                float x = sr != null ? sr.bounds.center.x : target.transform.position.x;
                _ePrompt.transform.position = new Vector3(x, topY + 0.34f, -0.2f);
            }
        }

        /// <summary>
        /// The ground item under the MOUSE cursor that is within the player's reach. Drives the
        /// highlight + E badge + the E grab, so you pick up exactly what you point at (the rule for
        /// the no-magnet grounded items). Reach is gated by the PLAYER distance, not the cursor.
        /// </summary>
        private GroundItemVisual MouseTarget(float playerRange)
        {
            if (GroundItemManager.Instance == null) return null;
            var cam = Camera.main;
            if (cam == null) return null;
            Vector3 mw = cam.ScreenToWorldPoint(Input.mousePosition);
            mw.z = 0f;
            var item = GroundItemManager.Instance.GetItemAtPosition(mw, 0.6f); // under the cursor
            if (item == null) return null;
            if (Vector2.Distance(transform.position, item.transform.position) > playerRange) return null;
            return item;
        }

        private void TryPickup()
        {
            var item = MouseTarget(pickupRange);
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

            // Mark for the magnet tween + prune anything stale (rejections never NACK by id)
            _magnetMarks[itemId] = Time.time;
            if (_magnetMarks.Count > 32)
            {
                var stale = new List<string>();
                foreach (var kv in _magnetMarks)
                    if (Time.time - kv.Value > MarkTTL)
                        stale.Add(kv.Key);
                foreach (var k in stale)
                    _magnetMarks.Remove(k);
            }

            var msg = new PickupItemMessage { id = itemId };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.PickupItem, json);
        }
    }
}
