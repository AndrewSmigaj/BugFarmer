using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Util;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// PURE DISPLAY: one centipede's segmented body. Knots are 1-3 centipedes per swarm
    /// (§14.3): each member bug gets its OWN trail component (on a child GO of the
    /// swarm visual) that records its head's RENDERED path (already tick-interpolated,
    /// which smooths the per-leg re-anchor snap) and places body segments + a tail at
    /// fixed arc-length offsets along the history, each oriented along its local
    /// tangent — corners read as curves for free, which is what sells the serpentine
    /// motion without protocol bezier. The head transform is rotated along its own
    /// motion here too (display-only; bug visuals are otherwise never rotated, and the
    /// rotation is reset on destroy so pooled sprites return clean). Segment positions
    /// feed the melee sector query (a segment hit maps to THIS trail's bug id);
    /// nothing here is hash state.
    /// </summary>
    public class CentipedeTrail : MonoBehaviour
    {
        private const int BodySegments = 6;
        private const float MinSample = 0.04f;    // head must move this far to record

        // Per-species size: millipedes render ~2x the centipede (bigger, chunkier body). Set in
        // Initialize from the species id; the segment SPRITES are also chosen per species there.
        private const float CentScale = 0.35f, MilliScale = 0.70f;
        private const float CentSpacing = 0.5f;   // arc-length between centipede segments (millipede 2x)
        private float _partScale = CentScale;
        private float _spacing = CentSpacing;
        private float _maxHistory = (BodySegments + 2) * CentSpacing + 2f;

        /// <summary>The crawler head's display scale for this species — SwarmVisual sets the head
        /// transform to this so the head matches its trail segments (millipede = 2x centipede).</summary>
        public static float PartScaleFor(string speciesId) =>
            (speciesId != null && speciesId.Contains("millipede")) ? MilliScale : CentScale;

        // The segment sprites are 32px = 2.0 world units raw; CentScale (0.35) reads each part as
        // ~0.7 units — a long bug, not a parade of plates. MilliScale doubles it for millipedes.

        // The sprites are drawn FACING UP (head/segment top = forward); the tangent
        // math yields right-facing angles, so offset by -90°. If a re-bake changes the
        // art's base facing, this is the only knob.
        private const float ArtAngleOffset = -90f;

        private Transform _head;
        private readonly List<Vector3> _points = new(); // newest at index 0
        private Transform[] _segments;                  // [0..BodySegments-1] body, last = tail
        private SpriteRenderer[] _renderers;

        /// <summary>Build the segment chain (sprites from Resources/Bugs, two variants).</summary>
        public void Initialize(Transform head, string speciesId)
        {
            _head = head;
            // Pick the sprite family + size from the species (millipede has its own body/tail art
            // and renders 2x bigger; everything else uses the centipede segments).
            bool milli = speciesId != null && speciesId.Contains("millipede");
            string fam = milli ? "millipede" : "centipede";
            _partScale = milli ? MilliScale : CentScale;
            _spacing = milli ? CentSpacing * 2f : CentSpacing;   // spacing scales with size
            _maxHistory = (BodySegments + 2) * _spacing + 2f;
            // ONE body design per creature: body_a/body_b are ALTERNATIVE looks, not strung together.
            // Chosen look: centipede = the "b" set, millipede = the "a" set. (Head is the species sprite_id.)
            string v = milli ? "a" : "b";
            var body = Resources.Load<Sprite>($"Bugs/{fam}_body_{v}");
            var tail = Resources.Load<Sprite>($"Bugs/{fam}_tail_{v}");

            int total = BodySegments + 1;
            _segments = new Transform[total];
            _renderers = new SpriteRenderer[total];
            for (int i = 0; i < total; i++)
            {
                var go = new GameObject(i < BodySegments ? $"seg_{i}" : "tail");
                go.transform.SetParent(transform, false);
                go.transform.localScale = new Vector3(_partScale, _partScale, 1f);
                var sr = go.AddComponent<SpriteRenderer>();
                sr.sprite = i >= BodySegments ? tail : body;
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
            using var _perf = PerfProfiler.Sample("Render.Trail");
            if (_head == null || _segments == null) return;

            // Record the head's rendered path
            Vector3 hp = _head.position;
            if (_points.Count == 0 || (hp - _points[0]).sqrMagnitude > MinSample * MinSample)
            {
                _points.Insert(0, hp);
                TrimHistory();
            }

            // Orient the head along its own recent motion (same art offset).
            if (_points.Count >= 2)
            {
                Vector3 headDir = (_points[0] - _points[1]).normalized;
                float headAngle = Mathf.Atan2(headDir.y, headDir.x) * Mathf.Rad2Deg;
                _head.rotation = Quaternion.Euler(0f, 0f, headAngle + ArtAngleOffset);
            }

            // Place each segment at its arc-length offset along the history
            for (int i = 0; i < _segments.Length; i++)
            {
                float target = _spacing * (i + 1);
                if (!SampleAt(target, out var pos, out var tangent))
                {
                    // Not enough history yet: stack behind the head
                    pos = hp;
                    tangent = Vector3.right;
                }
                _segments[i].position = pos;
                float angle = Mathf.Atan2(tangent.y, tangent.x) * Mathf.Rad2Deg;
                _segments[i].rotation = Quaternion.Euler(0f, 0f, angle + ArtAngleOffset);
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
                if (walked > _maxHistory)
                {
                    _points.RemoveRange(i + 1, _points.Count - i - 1);
                    return;
                }
            }
        }

        /// <summary>Segment positions for the melee sector query (a hit → this trail's bug).</summary>
        public IEnumerable<Vector2> SegmentPositions()
        {
            if (_segments == null) yield break;
            foreach (var s in _segments)
                yield return s.position;
        }

        private void OnDestroy()
        {
            // The head transform is a POOLED bug sprite — hand it back clean (the
            // segments are children of this GO and die with it).
            if (_head != null)
                _head.rotation = Quaternion.identity;
        }
    }
}
