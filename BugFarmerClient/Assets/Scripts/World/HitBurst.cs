using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// One-shot particle bursts for hit feedback — a little poof of leaves (chopping a tree) or wood
    /// chips (hitting a structure) at the strike point. A single shared World-space ParticleSystem that
    /// we Emit into (moved to the hit position first; a Circle shape gives an outward in-plane spray),
    /// so there's no GameObject churn per hit. Cosmetic, client-local, zero sim/determinism surface.
    /// </summary>
    public class HitBurst : MonoBehaviour
    {
        public enum Kind { Leaf, Chip, Generic }

        private static HitBurst _inst;
        private ParticleSystem _ps;

        private static HitBurst Instance()
        {
            if (_inst != null) return _inst;
            var go = new GameObject("HitBurst");
            _inst = go.AddComponent<HitBurst>();
            _inst.Build();
            return _inst;
        }

        private void Build()
        {
            _ps = gameObject.AddComponent<ParticleSystem>();

            var main = _ps.main;
            main.loop = false;
            main.playOnAwake = false;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.4f, 0.8f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(1.4f, 3.4f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.06f, 0.14f);
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, 6.28f);
            main.gravityModifier = 1.3f;             // chips/leaves fall after the pop
            main.maxParticles = 400;
            main.simulationSpace = ParticleSystemSimulationSpace.World;

            var emission = _ps.emission;
            emission.enabled = false;                // manual Emit only

            var shape = _ps.shape;                   // outward in-plane spray
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.1f;
            shape.arc = 360f;

            var col = _ps.colorOverLifetime;         // hold then fade
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[]
                {
                    new GradientAlphaKey(1f, 0f),
                    new GradientAlphaKey(1f, 0.6f),
                    new GradientAlphaKey(0f, 1f),
                });
            col.color = new ParticleSystem.MinMaxGradient(grad);

            var rot = _ps.rotationOverLifetime;      // tumble
            rot.enabled = true;
            rot.z = new ParticleSystem.MinMaxCurve(-3f, 3f);

            var r = _ps.GetComponent<ParticleSystemRenderer>();
            r.renderMode = ParticleSystemRenderMode.Billboard;
            r.material = new Material(Shader.Find("Sprites/Default")); // unlit
            r.sortingLayerName = "Occupants";
            r.sortingOrder = 800;                    // in front of occupant sprites
        }

        /// <summary>Emit a burst of <paramref name="count"/> particles at a world position.</summary>
        public static void Play(Vector3 worldPos, Kind kind, int count = 8)
        {
            var inst = Instance();
            inst.transform.position = worldPos;      // World sim space: particles live independently after emit

            var main = inst._ps.main;
            main.startColor = kind switch
            {
                Kind.Leaf => new Color(0.36f, 0.60f, 0.22f), // leaf green
                Kind.Chip => new Color(0.55f, 0.40f, 0.24f), // wood brown
                _ => new Color(0.72f, 0.72f, 0.72f),         // neutral
            };
            inst._ps.Emit(count);
        }
    }
}
