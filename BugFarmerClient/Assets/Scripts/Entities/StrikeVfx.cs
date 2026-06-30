using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.Entities
{
    /// <summary>
    /// #20 display-only strike VFX: the CONSUMED corpse the predator feeds on. A transient dead_&lt;prey&gt;
    /// sprite POPS in at the victim, holds for the feeding dwell (feed_pause_secs), then fades — vanishing
    /// as the predator finishes. It is NOT a real ground item (no pickup, no food registry, ecology-neutral)
    /// and never touches the deterministic sim or the state hash. Rendered like a dropped dead bug (Occupants
    /// layer + the GroundItemVisual fit-box scale + day/night lighting) so it reads as the real thing.
    /// Self-creating singleton + a small pool to avoid GC churn.
    /// </summary>
    public class StrikeVfx : MonoBehaviour
    {
        private static StrikeVfx _instance;

        private static StrikeVfx Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("StrikeVfx");
                    _instance = go.AddComponent<StrikeVfx>();
                }
                return _instance;
            }
        }

        private const float HoldFloorSecs = 0.4f; // even a 0s feed shows the corpse briefly
        private const float FadeSecs = 0.45f;
        private const float PopSecs = 0.1f;

        private class Corpse
        {
            public GameObject Go;
            public Transform T;
            public SpriteRenderer R;
            public float Born;
            public float Hold;  // seconds at full alpha before the fade
            public float Scale; // the fit-box scale for this sprite
        }

        private readonly List<Corpse> _active = new List<Corpse>();
        private readonly Queue<Corpse> _pool = new Queue<Corpse>();

        /// <summary>Spawn a consumed-corpse visual at a victim. holdSecs = the feeding dwell, then it fades.</summary>
        public static void SpawnCorpse(Sprite sprite, Vector2 pos, float holdSecs)
        {
            if (sprite == null) return;
            Instance.Spawn(sprite, pos, holdSecs);
        }

        private void Spawn(Sprite sprite, Vector2 pos, float holdSecs)
        {
            Corpse c = _pool.Count > 0 ? _pool.Dequeue() : NewCorpse();
            c.R.sprite = sprite;
            c.R.color = Color.white;
            c.R.sortingOrder = -Mathf.RoundToInt(pos.y); // sit on the ground like a real drop
            c.T.position = new Vector3(pos.x, pos.y, 0f);
            c.T.localScale = Vector3.zero; // pop-in from nothing
            c.Scale = FitScale(sprite);
            c.Born = Time.time;
            c.Hold = Mathf.Max(HoldFloorSecs, holdSecs);
            c.Go.SetActive(true);
            _active.Add(c);
        }

        private Corpse NewCorpse()
        {
            var go = new GameObject("Corpse");
            go.transform.SetParent(transform);
            var r = go.AddComponent<SpriteRenderer>();
            r.sortingLayerName = "Occupants";
            BugFarmer.World.LitMaterials.Apply(r); // receive day/night lighting like a real drop
            go.SetActive(false);
            return new Corpse { Go = go, T = go.transform, R = r };
        }

        private void Update()
        {
            for (int i = _active.Count - 1; i >= 0; i--)
            {
                Corpse c = _active[i];
                float age = Time.time - c.Born;
                if (age >= c.Hold + FadeSecs)
                {
                    c.Go.SetActive(false);
                    _active.RemoveAt(i);
                    _pool.Enqueue(c);
                    continue;
                }
                // Pop-in (ease-out-back overshoot) then settle at the fit scale.
                float pop = age < PopSecs ? EaseOutBack(age / PopSecs) : 1f;
                c.T.localScale = Vector3.one * (c.Scale * pop);
                // Hold at full alpha, then fade.
                float a = age <= c.Hold ? 1f : 1f - (age - c.Hold) / FadeSecs;
                Color col = c.R.color;
                col.a = a;
                c.R.color = col;
            }
        }

        // Mirror GroundItemVisual's fit-box: fit within 0.9 cell, floor at 0.6 cell, preserve aspect.
        private static float FitScale(Sprite sprite)
        {
            const float maxCells = 0.9f, minCells = 0.6f;
            if (sprite == null) return 1f;
            float w = sprite.rect.width / sprite.pixelsPerUnit;
            float h = sprite.rect.height / sprite.pixelsPerUnit;
            float big = Mathf.Max(w, h);
            return big > maxCells ? maxCells / big : big < minCells ? minCells / big : 1f;
        }

        private static float EaseOutBack(float x)
        {
            const float c1 = 1.70158f, c3 = c1 + 1f;
            x = Mathf.Clamp01(x);
            return 1f + c3 * Mathf.Pow(x - 1f, 3f) + c1 * Mathf.Pow(x - 1f, 2f);
        }
    }
}
