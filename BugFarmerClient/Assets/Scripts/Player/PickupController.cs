using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.World;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles player pickup of ground items.
    /// E key to pick up nearby items.
    /// Highlights closest item within range.
    /// </summary>
    public class PickupController : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private float pickupRange = 2f;
        [SerializeField] private float highlightRange = 3f;

        private GroundItemVisual _highlightedItem;

        private void Update()
        {
            UpdateHighlight();

            if (Input.GetKeyDown(KeyCode.E))
            {
                TryPickup();
            }
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
