using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Entities;
using BugFarmer.Networking;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Melee combat (sword/spear). Routed by PlayerInputRouter when a weapon is equipped.
    ///
    /// Flow (the catch trust model): ONE full-sector query at swing START against render
    /// positions (zero perceived latency; the animator's sweep + trail then traces the
    /// exact queried arc) → optimistic hit-FLASH only (no optimistic removal — per-bug HP
    /// makes kill prediction wrong) → ONE MeleeAttackMessage per swing (multi-swarm hits
    /// in one payload) → server validates and broadcasts MeleeResultMessage (the sole HP
    /// display channel); kills land via BUG_REMOVED ledger events ≤1 tick later.
    /// </summary>
    public class MeleeController : MonoBehaviour
    {
        private Camera _mainCamera;
        private PlayerToolAnimator _animator;
        private float _lastSwingTime;

        private void Start()
        {
            _mainCamera = Camera.main;
            _animator = GetComponent<PlayerToolAnimator>();
        }

        /// <summary>
        /// Handle a routed click with the named MOVE ("primary" = left, "secondary" = right).
        /// The gate mirrors the server's: the equipped item must HAVE the move.
        /// Returns true if the swing was performed.
        /// </summary>
        public bool TryHandleClick(string moveName = "primary")
        {
            var world = WorldManager.Instance;
            if (world?.CurrentMatch == null) return false;
            var socket = NetworkManager.Instance?.Socket;
            if (socket == null || !socket.IsConnected) return false;

            string toolId = InventoryManager.Instance?.GetEquippedToolId();
            var weapon = EntityDatabase.Get(toolId);
            var move = weapon?.GetMove(moveName);
            if (move == null)
                return false;

            // Client mirrors the server's per-move cooldown on one shared swing timer
            // (matching the server's shared LastToolTick: jab/swing throttle each other).
            float cooldown = move.CooldownTicks > 0 ? move.CooldownTicks / 10f : 0.3f;
            if (Time.time - _lastSwingTime < cooldown)
                return false;

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return false;
            }

            Vector2 origin = transform.position;
            Vector2 clickPos = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            Vector2 aim = clickPos - origin;
            if (aim.sqrMagnitude < 0.0001f) aim = Vector2.right;

            float reach = move.Reach > 0 ? move.Reach : 2f;
            float arc = move.ArcDegrees > 0 ? move.ArcDegrees : 90f;
            float aimDeg = Mathf.Atan2(aim.y, aim.x) * Mathf.Rad2Deg;

            // You swing toward the cursor regardless of its distance (Terraria-style);
            // clamp the reported click to reach so server reach validation always
            // reflects where the weapon actually strikes (also the kill-drop position).
            Vector2 strikePos = origin + aim.normalized * Mathf.Min(aim.magnitude, reach);

            // Single full-arc query at swing START (render positions — what the player sees).
            var hits = SwarmManager.Instance?.GetBugsInSector(origin, aimDeg, arc, reach);

            // Swing plays even on a complete miss; the MOVE picks the animation kind
            // (a sword jab plays Stab on a "sword" profile). The optimistic bug FLASH stays at swing-start
            // below (zero-latency trust cue); we ADD a directional camera shake at the CONTACT frame.
            Vector2 kick = aim.normalized * 0.06f;
            bool connected = hits != null && hits.Count > 0;
            _animator?.Play(weapon.ToolType, EntityDatabase.GetItemSprite(toolId), aim,
                            arc, move.SwingTime, move.Kind,
                            onContact: connected ? () => CameraFollow.AddShake(0.22f, kick) : (System.Action)null);
            _lastSwingTime = Time.time;

            if (hits == null || hits.Count == 0)
                return true;

            // Truncate to the per-SWING cap in the same deterministic order the server
            // applies (swarm id ascending, bug ids ascending) so client expectation and
            // server outcome agree.
            int cap = move.MaxTargets > 0 ? move.MaxTargets : 1;
            var entries = new List<MeleeSwarmHits>();
            int taken = 0;
            foreach (var hit in hits.OrderBy(h => h.swarmId))
            {
                if (taken >= cap) break;
                var ids = hit.bugIds.OrderBy(id => id).Take(cap - taken).ToArray();
                taken += ids.Length;
                entries.Add(new MeleeSwarmHits { swarm_id = hit.swarmId, bug_ids = ids });

                // Optimistic feedback: FLASH + THWACK (HP/kill truth arrives via OpCode
                // 89 + the BUG_REMOVED ledger; the echo's sounds are !ownEcho-gated so
                // the attacker never double-hears).
                var swarm = SwarmManager.Instance.GetSwarm(hit.swarmId);
                if (swarm != null)
                {
                    foreach (var id in ids)
                    {
                        swarm.FlashBug(id);
                        BugFarmer.Audio.AudioFx.BugHit();
                    }
                }
            }

            var msg = new MeleeAttackMessage
            {
                click_x = strikePos.x,
                click_y = strikePos.y,
                move = moveName,
                hits = entries.ToArray()
            };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.MeleeAttack,
                                           JsonUtility.ToJson(msg));
            return true;
        }
    }
}
