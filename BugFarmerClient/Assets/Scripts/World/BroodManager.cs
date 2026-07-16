using System.Collections.Generic;
using Nakama;
using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.World
{
    /// <summary>
    /// Renders visible breeding nurseries (OpCode 104 BroodUpdate). DISPLAY-ONLY: the actual births ride the
    /// deterministic SWARM_REPRODUCED ledger (SwarmManager), so nothing here touches the sim or the state hash
    /// — a dropped/late BroodUpdate only delays the on-screen stage sprite, never bug positions. One small
    /// sprite per brood CELL showing the MOST-ADVANCED non-empty life stage (egg -> larva -> pupa) so the
    /// nursery visibly develops. Mirrors GroundItemManager (subscribe WorldManager.OnMatchData, pooled sprites),
    /// keyed by cell. Self-bootstraps (no scene edit); cleared on a zone swap by WorldManager.ResetForZoneSwap.
    /// </summary>
    public class BroodManager : MonoBehaviour
    {
        public static BroodManager Instance { get; private set; }
        private static bool _spawned;

        private readonly Dictionary<Vector2Int, GameObject> _broods = new();
        private readonly Queue<GameObject> _pool = new();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (_spawned) return;
            _spawned = true;
            var go = new GameObject("BroodManager");
            DontDestroyOnLoad(go);
            go.AddComponent<BroodManager>();
        }

        private void Awake() { Instance = this; }

        private void Start()
        {
            if (WorldManager.Instance != null)
                WorldManager.Instance.OnMatchData += HandleMatchData;
        }

        private void OnDestroy()
        {
            if (WorldManager.Instance != null)
                WorldManager.Instance.OnMatchData -= HandleMatchData;
        }

        private void HandleMatchData(IMatchState state)
        {
            if (state.OpCode != OpCodes.BroodUpdate) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<BroodUpdateMessage>(json);
            if (msg == null) return;

            var cell = new Vector2Int(msg.gx, msg.gy);
            if (msg.removed || (msg.eggs + msg.maggots + msg.pupae) <= 0)
            {
                Despawn(cell);
                return;
            }

            var spriteId = StageSpriteId(msg);
            var sprite = string.IsNullOrEmpty(spriteId) ? null : EntityDatabase.GetWorldSprite(spriteId);
            if (sprite == null) { Despawn(cell); return; } // no art for this stage yet -> render nothing (fallback)
            RenderBrood(cell, sprite);
        }

        // The most-advanced non-empty stage's sprite id, so the nursery visibly progresses egg -> larva -> pupa.
        private static string StageSpriteId(BroodUpdateMessage msg)
        {
            var sp = EntityDatabase.GetSpecies(msg.species);
            if (sp == null) return null;
            if (msg.pupae > 0) return sp.PupaSpriteId;
            if (msg.maggots > 0) return sp.LarvaSpriteId;
            return sp.EggSpriteId;
        }

        private void RenderBrood(Vector2Int cell, Sprite sprite)
        {
            if (!_broods.TryGetValue(cell, out var go))
            {
                go = GetFromPool();
                _broods[cell] = go;
            }
            Vector3 pos = TilemapManager.Instance != null
                ? TilemapManager.Instance.CellToWorld(cell)
                : new Vector3(cell.x + 0.5f, cell.y + 0.5f, 0f);
            go.transform.position = pos;
            go.transform.localScale = FitScale(sprite);
            var sr = go.GetComponent<SpriteRenderer>();
            sr.sprite = sprite;
            sr.sortingOrder = -Mathf.RoundToInt(pos.y);
            go.SetActive(true);
        }

        // Fit the stage sprite within ~0.9 cell (preserve aspect) so the nursery reads as a small clutch on
        // its cell and never rivals placed occupants. Mirrors GroundItemVisual's fit-box.
        private static Vector3 FitScale(Sprite sprite)
        {
            if (sprite == null) return Vector3.one;
            float w = sprite.rect.width / sprite.pixelsPerUnit;
            float h = sprite.rect.height / sprite.pixelsPerUnit;
            float big = Mathf.Max(w, h);
            const float maxCells = 0.9f;
            float s = big > maxCells ? maxCells / big : 1f;
            return new Vector3(s, s, 1f);
        }

        private void Despawn(Vector2Int cell)
        {
            if (_broods.TryGetValue(cell, out var go))
            {
                _broods.Remove(cell);
                go.SetActive(false);
                _pool.Enqueue(go);
            }
        }

        /// <summary>Clear every nursery visual — called by WorldManager.ResetForZoneSwap on a zone change so a
        /// previous zone's broods don't linger (this manager is DontDestroyOnLoad).</summary>
        public void ClearAll()
        {
            foreach (var go in _broods.Values)
            {
                go.SetActive(false);
                _pool.Enqueue(go);
            }
            _broods.Clear();
        }

        private GameObject GetFromPool()
        {
            if (_pool.Count > 0) return _pool.Dequeue();
            var go = new GameObject("Brood");
            go.transform.SetParent(transform);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sortingLayerName = "Occupants";
            LitMaterials.Apply(sr); // day/night lighting like other world sprites
            return go;
        }

        /// <summary>Nearest known brood cell within `radius` world-units of `worldPos`, or null — used by the
        /// emergence beat (T4) to originate a hatchling's visual from the nursery it emerged from.</summary>
        public Vector2Int? NearestBroodCell(Vector2 worldPos, float radius)
        {
            Vector2Int? best = null;
            float bestSqr = radius * radius;
            foreach (var kv in _broods)
            {
                Vector2 p = TilemapManager.Instance != null
                    ? (Vector2)TilemapManager.Instance.CellToWorld(kv.Key)
                    : new Vector2(kv.Key.x + 0.5f, kv.Key.y + 0.5f);
                float d = (p - worldPos).sqrMagnitude;
                if (d <= bestSqr) { bestSqr = d; best = kv.Key; }
            }
            return best;
        }
    }
}
