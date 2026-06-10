using UnityEngine;
using System.Collections.Generic;
using System.Linq;
using Nakama;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.Entities;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles catching bugs. Two modes, routed by PlayerInputRouter:
    /// - Hand catch (no tool): precision grab — a small circle at the click (catch 1-ish).
    /// - Net sweep (net equipped): a physical SWING at the player — one full-sector query
    ///   (arc_degrees × reach from the net's data) at swing start; the PlayerToolAnimator
    ///   sweep + trail traces the exact queried arc, so the visual IS the honest catch area.
    /// A swing that hits multiple swarms sends its messages back-to-back; the server's
    /// per-swing rate limit treats the same-tick burst as one swing.
    /// </summary>
    public class CatchingController : MonoBehaviour
    {
        [Header("Catch Settings")]
        [SerializeField] private float catchCooldown = 0.2f;
        [SerializeField] private float handReach = 2.0f;
        [SerializeField] private float handCatchRadius = 0.5f;

        private float _lastCatchTime;
        private Camera _mainCamera;
        private PlayerToolAnimator _animator;

        private void Start()
        {
            _mainCamera = Camera.main;
            _animator = GetComponent<PlayerToolAnimator>();
        }

        /// <summary>
        /// Handle a routed left-click. netMode is resolved by PlayerInputRouter from the
        /// equipped tool's type. Returns true if any bugs were caught — the router uses
        /// this for the bare-hand fallthrough (no bug under cursor → the click breaks).
        /// </summary>
        public bool TryHandleClick(bool netMode)
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null)
            {
                Debug.Log("[Catch] No match - connect to world first");
                return false;
            }

            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected)
            {
                Debug.Log("[Catch] Socket not connected");
                return false;
            }

            // Cooldown mirrors the server's per-swing gate (net cooldown_ticks ≈ 3 = 0.3s;
            // hand keeps the legacy 0.2s).
            string toolId = netMode ? UI.InventoryManager.Instance?.GetEquippedToolId() : null;
            var net = netMode ? EntityDatabase.Get(toolId) : null;
            float cooldown = (net != null && net.CooldownTicks > 0)
                ? net.CooldownTicks / 10f : catchCooldown;
            if (Time.time - _lastCatchTime < cooldown)
                return false;

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return false;
            }

            Vector2 origin = transform.position;
            Vector2 clickPos = _mainCamera.ScreenToWorldPoint(Input.mousePosition);

            List<CatchResult> catches;
            Vector2 reportPos; // position sent for server reach validation + echo anims

            if (netMode)
            {
                // Physical sweep: arc/reach are the NET'S DATA (small 80°/2.5, large
                // 120°/3.5) — the old click-anywhere circle is gone.
                float reach = (net != null && net.Reach > 0) ? net.Reach : 2.5f;
                float arc = (net != null && net.ArcDegrees > 0) ? net.ArcDegrees : 80f;
                int cap = (net != null && net.CatchCap > 0) ? net.CatchCap : 10;

                Vector2 aim = clickPos - origin;
                if (aim.sqrMagnitude < 0.0001f) aim = Vector2.right;
                float aimDeg = Mathf.Atan2(aim.y, aim.x) * Mathf.Rad2Deg;

                catches = SwarmManager.Instance?.GetBugsInSector(origin, aimDeg, arc, reach);
                reportPos = origin + aim.normalized * Mathf.Min(aim.magnitude, reach);

                // Cap the SWING total client-side in deterministic order (the server caps
                // per message; an honest client respects the swing cap across swarms).
                if (catches != null && catches.Count > 0)
                {
                    var capped = new List<CatchResult>();
                    int taken = 0;
                    foreach (var c in catches.OrderBy(c => c.swarmId))
                    {
                        if (taken >= cap) break;
                        var ids = c.bugIds.OrderBy(id => id).Take(cap - taken).ToArray();
                        taken += ids.Length;
                        capped.Add(new CatchResult { swarmId = c.swarmId, bugIds = ids });
                    }
                    catches = capped;
                }

                // The sweep + trail plays even on a miss; the trail IS the catch area.
                _animator?.Play("net", EntityDatabase.GetItemSprite(toolId), aim,
                                arc, net != null ? net.SwingTime : 0f);
            }
            else
            {
                // Hand: precision grab, unchanged (small circle at the click, short reach).
                if ((clickPos - origin).magnitude > handReach)
                    return false;
                catches = SwarmManager.Instance?.GetBugsAtPosition(clickPos, handCatchRadius);
                reportPos = clickPos;
            }

            // Optimistic removal - remove bugs immediately for instant feedback
            bool caughtAny = false;
            if (catches != null)
            {
                foreach (var result in catches)
                {
                    var swarm = SwarmManager.Instance.GetSwarm(result.swarmId);
                    swarm?.RemoveBugsById(result.bugIds);
                }

                // Send bug IDs to server for validation (one message per swarm — the
                // server's same-tick burst rule treats them as one swing)
                foreach (var result in catches)
                {
                    caughtAny = true;
                    var msg = new CatchBugMessage
                    {
                        click_x = reportPos.x,
                        click_y = reportPos.y,
                        swarm_id = result.swarmId,
                        bug_ids = result.bugIds
                    };
                    var json = JsonUtility.ToJson(msg);
                    _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.CatchBug, json);
                }
            }

            _lastCatchTime = Time.time;
            return caughtAny;
        }
    }
}
