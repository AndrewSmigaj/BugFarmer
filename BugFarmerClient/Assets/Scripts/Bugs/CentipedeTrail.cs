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
    ///
    /// Stage 1.2 (docs/plans/village-slice.md): the path is a fixed ring with each point's distance travelled, so placing
    /// the parts is one pass and trimming is constant time, with no memory per frame; the trail only runs while its group
    /// is in view (the group's object is switched off out of view), and <see cref="Rebuild"/> lays a straight body behind
    /// the head when it comes back.
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
        public static float PartScaleFor(string speciesId)
        {
            var info = BugFarmer.Data.EntityDatabase.GetSpecies(speciesId);
            float scale = (info != null && info.RenderScale > 0f) ? info.RenderScale : 1f;
            bool milli = speciesId != null && speciesId.Contains("millipede");
            return (milli ? MilliScale : CentScale) * scale;
        }

        /// <summary>Arc length between body parts for this species (spacing scales with size; millipede 2x).</summary>
        private static float SpacingFor(string speciesId)
        {
            var info = BugFarmer.Data.EntityDatabase.GetSpecies(speciesId);
            float renderScale = (info != null && info.RenderScale > 0f) ? info.RenderScale : 1f;
            bool milli = speciesId != null && speciesId.Contains("millipede");
            return (milli ? CentSpacing * 2f : CentSpacing) * renderScale;
        }

        /// <summary>How far the recorded path — so the body — can reach behind the head, for this species. SwarmVisual
        /// grows its group's in-view box by this so a body still on screen is drawn while its head is off it.</summary>
        public static float HistoryLengthFor(string speciesId) => (BodySegments + 2) * SpacingFor(speciesId) + 2f;

        // The segment sprites are 32px = 2.0 world units raw; CentScale (0.35) reads each part as
        // ~0.7 units — a long bug, not a parade of plates. MilliScale doubles it for millipedes.

        // The sprites are drawn FACING UP (head/segment top = forward); the tangent
        // math yields right-facing angles, so offset by -90°. If a re-bake changes the
        // art's base facing, this is the only knob.
        private const float ArtAngleOffset = -90f;

        private Transform _head;
        // The head's recorded path: a ring, newest at _newest, each point with the distance the head had travelled when
        // it was recorded (only grows, so double). Arc length between points = a subtraction.
        private Vector3[] _ring;
        private double[] _odo;
        private int _newest = -1;
        private int _count;
        private double _travelled;
        private Transform[] _segments;                  // [0..BodySegments-1] body, last = tail
        private SpriteRenderer[] _renderers;

        /// <summary>Build the segment chain (sprites from Resources/Bugs, two variants).</summary>
        public void Initialize(Transform head, string speciesId)
        {
            _head = head;
            // Pick the sprite family + size from the species (millipede has its own body/tail art
            // and renders 2x bigger; everything else uses the centipede segments).
            bool milli = speciesId != null && speciesId.Contains("millipede");
            // Segment art family: an explicit per-species sprite_family (a tier's OWN head/body/tail set),
            // falling back to the legacy millipede/centipede split. render_scale lets a giant tier be bigger.
            var info = BugFarmer.Data.EntityDatabase.GetSpecies(speciesId);
            string fam = !string.IsNullOrEmpty(info?.SpriteFamily) ? info.SpriteFamily
                         : (milli ? "millipede" : "centipede");
            float renderScale = (info != null && info.RenderScale > 0f) ? info.RenderScale : 1f;
            _partScale = (milli ? MilliScale : CentScale) * renderScale;
            _spacing = SpacingFor(speciesId);
            _maxHistory = HistoryLengthFor(speciesId);
            // Points are recorded at least MinSample apart and trimmed past _maxHistory (one kept beyond), so this holds
            // the longest history; a full ring would drop its oldest point.
            int capacity = Mathf.CeilToInt(_maxHistory / MinSample) + 4;
            _ring = new Vector3[capacity];
            _odo = new double[capacity];
            _count = 0;
            _newest = -1;
            _travelled = 0;
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
                Push(head.position);
        }

        /// <summary>Lay a straight body behind the head, along <paramref name="motion"/> (the head's last movement; any
        /// length; zero = hanging below it): the group was out of view, so the recorded path is stale.</summary>
        public void Rebuild(Vector2 motion)
        {
            if (_head == null || _ring == null) return;
            Vector3 hp = _head.position;
            Vector3 back = motion.sqrMagnitude > 1e-8f ? -(Vector3)motion.normalized : Vector3.down;
            _count = 0;
            _newest = -1;
            _travelled = 0;
            Push(hp + back * (_maxHistory + _spacing));   // the far end, past the whole body
            Push(hp);
        }

        // The k-th newest recorded point (k = 0 is the newest) and its distance travelled.
        private int Slot(int k) => (_newest - k + _ring.Length) % _ring.Length;

        private void Push(Vector3 p)
        {
            if (_count > 0) _travelled += Vector3.Distance(_ring[_newest], p);
            _newest = (_newest + 1) % _ring.Length;
            _ring[_newest] = p;
            _odo[_newest] = _travelled;
            if (_count < _ring.Length) _count++;
            // Trim: drop the oldest point while the second-oldest is already past _maxHistory behind the newest, so
            // exactly one point beyond _maxHistory stays (as the list version kept).
            while (_count >= 2 && _odo[_newest] - _odo[Slot(_count - 2)] > _maxHistory)
                _count--;
        }

        private void LateUpdate()
        {
            // TEST ONLY: summed into the frame's bug-drawing time when the cost probe is on.
            if (!BugFarmer.Util.CostProbe.Enabled) { DrawTrail(); return; }
            BugFarmer.Util.CostProbe.RenderBegin();
            try { DrawTrail(); } finally { BugFarmer.Util.CostProbe.RenderEnd(); }
        }

        private void DrawTrail()
        {
            using var _perf = PerfProfiler.Sample("Render.Trail");
            if (_head == null || _segments == null) return;

            // Record the head's rendered path
            Vector3 hp = _head.position;
            if (_count == 0 || (hp - _ring[_newest]).sqrMagnitude > MinSample * MinSample)
                Push(hp);

            // Orient the head along its own recent motion (same art offset).
            if (_count >= 2)
            {
                Vector3 headDir = (_ring[_newest] - _ring[Slot(1)]).normalized;
                float headAngle = Mathf.Atan2(headDir.y, headDir.x) * Mathf.Rad2Deg;
                _head.rotation = Quaternion.Euler(0f, 0f, headAngle + ArtAngleOffset);
            }

            // Place each segment at its arc-length offset along the history, in one walk from the newest point: the
            // targets grow, so the walk only moves back.
            double headOdo = _odo[_newest];
            int k = 0;   // the stretch between the k-th and (k+1)-th newest points
            for (int i = 0; i < _segments.Length; i++)
            {
                double target = _spacing * (i + 1);
                while (k < _count - 1 && headOdo - _odo[Slot(k + 1)] < target) k++;
                Vector3 pos, tangent;
                if (k >= _count - 1)
                {
                    // Not enough history yet: stack behind the head
                    pos = hp;
                    tangent = Vector3.right;
                }
                else
                {
                    Vector3 a = _ring[Slot(k)], b = _ring[Slot(k + 1)];
                    double seg = _odo[Slot(k)] - _odo[Slot(k + 1)];
                    float f = seg > 0.0001 ? (float)((target - (headOdo - _odo[Slot(k)])) / seg) : 0f;
                    pos = Vector3.Lerp(a, b, f);
                    tangent = (a - b).normalized; // facing direction of travel
                }
                _segments[i].position = pos;
                float angle = Mathf.Atan2(tangent.y, tangent.x) * Mathf.Rad2Deg;
                _segments[i].rotation = Quaternion.Euler(0f, 0f, angle + ArtAngleOffset);
                // Y-sort just behind the head's order so the head reads on top
                _renderers[i].sortingOrder = -Mathf.FloorToInt(pos.y) + 1 - 1;
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
