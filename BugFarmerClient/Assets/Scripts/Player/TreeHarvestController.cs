using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;

namespace BugFarmer.Player
{
    /// <summary>
    /// Left-click GRAB verb for fruit trees while hands (or nothing) are equipped: picks
    /// ONE fruit (OpCode 92) from the tree under the cursor. Context-detected the
    /// StationController way (OverlapPoint → OccupantClickTarget → interaction_type
    /// "fruit_tree"). CONSUMES the click whenever a fruit tree is under the cursor — even
    /// out of range — so a hands-click on a tree never falls through to bare-hand chopping.
    /// No optimism: the fruit appears via the slot echo, the canopy updates via OpCode 93,
    /// and server errors ("No fruit on the tree", "Too far away") are the feedback.
    /// </summary>
    public class TreeHarvestController : MonoBehaviour
    {
        [SerializeField] private float maxPickDistance = 2.5f; // server re-validates at 3.0

        private Camera _mainCamera;

        /// <summary>Routed left-click while the grab verb is active (hands / empty slot).</summary>
        public bool TryHandleClick()
        {
            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return false;
            }

            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;

            // Front-most interactable occupant (shared resolver; not a bare OverlapPoint that an
            // overlapping occupant could steal).
            var target = InteractionResolver.TopmostInteractable(mouseWorld);
            if (target == null) return false;

            var def = EntityDatabase.Get(target.OccupantId);
            if (def?.World == null || def.World.InteractionType != "fruit_tree")
                return false;

            // In range? Out-of-range still consumes (see class comment).
            var d = (Vector2)transform.position -
                    new Vector2(target.AnchorCell.x + 0.5f, target.AnchorCell.y + 0.5f);
            if (d.sqrMagnitude > maxPickDistance * maxPickDistance)
                return true;

            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
                return true;

            var msg = new TreeHarvestMessage { gx = target.AnchorCell.x, gy = target.AnchorCell.y };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.TreeHarvest,
                                           JsonUtility.ToJson(msg));
            return true;
        }
    }
}
