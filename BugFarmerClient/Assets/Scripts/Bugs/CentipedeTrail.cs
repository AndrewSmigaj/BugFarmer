using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// PURE DISPLAY: the centipede's segmented body. The sim is a single bug (id 0,
    /// the head) riding the swarm center; this component records the head's RENDERED
    /// path (already tick-interpolated, which smooths the per-leg re-anchor snap) and
    /// places body segments + a tail at fixed arc-length offsets along the history,
    /// each oriented along its local tangent — corners read as curves for free, which
    /// is what sells the serpentine motion without protocol bezier. Segment positions
    /// feed the melee sector query (any segment hit maps to bug 0); nothing here is
    /// hash state.
    /// </summary>
    public class CentipedeTrail : MonoBehaviour
    {
        private const int BodySegments = 6;
        private const float Spacing = 0.45f;     // arc-length between segments
        private const float MinSample = 0.04f;   // head must move this far to record
        private const float MaxHistory = (BodySegments + 2) * Spacing + 2f;

        private Transform _head;
        private readonly List<Vector3> _points = new(); // newest at index 0
        private Transform[] _segments;                  // [0..BodySegments-1] body, last = tail
        private SpriteRenderer[] _renderers;

        /// <summary>Build the segment chain (sprites from Resources/Bugs, two variants).</summary>
        public void Initialize(Transform head, string speciesId)
        {
            _head = head;
            var bodyA = Resources.Load<Sprite>("Bugs/centipede_body_a");
            var bodyB = Resources.Load<Sprite>("Bugs/centipede_body_b");
            var tail = Resources.Load<Sprite>("Bugs/centipede_tail_a");

            int total = BodySegments + 1;
            _segments = new Transform[total];
            _renderers = new SpriteRenderer[total];
            for (int i = 0; i < total; i++)
            {
                var go = new GameObject(i < BodySegments ? $"seg_{i}" : "tail");
                go.transform.SetParent(transform, false);
                var sr = go.AddComponent<SpriteRenderer>();
                sr.sprite = i >= BodySegments ? tail : (i % 2 == 0 ? bodyA : bodyB);
                sr.sortingLayerName = "Occupants";
                World.LitMaterials.Apply(sr);
                _segments[i] = go.transform;
                _renderers[i] = sr;
                go.transform.position = head != null ? head.position : transform.position;
            }
            if (head != null)
                _points.Add(head.position);
        }

        private void LateUpdate()
        {
            if (_head == null || _segments == null) return;

            // Record the head's rendered path
            Vector3 hp = _head.position;
            if (_points.Count == 0 || (hp - _points[0]).sqrMagnitude > MinSample * MinSample)
            {
                _points.Insert(0, hp);
                TrimHistory();
            }

            // Place each segment at its arc-length offset along the history
            for (int i = 0; i < _segments.Length; i++)
            {
                float target = Spacing * (i + 1);
                if (!SampleAt(target, out var pos, out var tangent))
                {
                    // Not enough history yet: stack behind the head
                    pos = hp;
                    tangent = Vector3.right;
                }
                _segments[i].position = pos;
                float angle = Mathf.Atan2(tangent.y, tangent.x) * Mathf.Rad2Deg;
                _segments[i].rotation = Quaternion.Euler(0f, 0f, angle);
                // Y-sort just behind the head's order so the head reads on top
                _renderers[i].sortingOrder = -Mathf.FloorToInt(pos.y) + 1 - 1;
            }
        }

        /// <summary>Walk the history to the point arc-length `target` behind the head.</summary>
        private bool SampleAt(float target, out Vector3 pos, out Vector3 tangent)
        {
            float walked = 0f;
            for (int i = 0; i < _points.Count - 1; i++)
            {
                Vector3 a = _points[i];
                Vector3 b = _points[i + 1];
                float seg = Vector3.Distance(a, b);
                if (seg <= 0.0001f) continue;
                if (walked + seg >= target)
                {
                    float t = (target - walked) / seg;
                    pos = Vector3.Lerp(a, b, t);
                    tangent = (a - b).normalized; // facing direction of travel
                    return true;
                }
                walked += seg;
            }
            pos = default;
            tangent = default;
            return false;
        }

        private void TrimHistory()
        {
            float walked = 0f;
            for (int i = 0; i < _points.Count - 1; i++)
            {
                walked += Vector3.Distance(_points[i], _points[i + 1]);
                if (walked > MaxHistory)
                {
                    _points.RemoveRange(i + 1, _points.Count - i - 1);
                    return;
                }
            }
        }

        /// <summary>Segment positions for the melee sector query (any hit → bug 0).</summary>
        public IEnumerable<Vector2> SegmentPositions()
        {
            if (_segments == null) yield break;
            foreach (var s in _segments)
                yield return s.position;
        }
    }
}
