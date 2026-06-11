using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace BugFarmer.World
{
    /// <summary>
    /// A point light that fades with daylight — full at night, off at noon. Used for lamp/
    /// torch occupants (data-driven from the entity's world.light block) and reused by the
    /// player's personal night light. Creates its own Light2D at runtime.
    /// </summary>
    public class LampLight : MonoBehaviour
    {
        private Light2D _light;
        private float _baseIntensity = 1f;

        /// <summary>Configure radius/color/base intensity (call right after AddComponent).</summary>
        public void Configure(float radius, Color color, float intensity)
        {
            EnsureLight();
            _light.pointLightOuterRadius = radius;
            _light.pointLightInnerRadius = radius * 0.25f;
            _light.color = color;
            _baseIntensity = intensity;
        }

        private void EnsureLight()
        {
            if (_light != null) return;
            _light = gameObject.AddComponent<Light2D>();
            _light.lightType = Light2D.LightType.Point;
            _light.intensity = 0f;
        }

        private void Awake()
        {
            EnsureLight();
        }

        private void Update()
        {
            // Inverse of daylight: invisible at noon, full glow at night, eased through dusk.
            if (_light != null)
                _light.intensity = _baseIntensity * (1f - DayNightController.Daylight);
        }
    }

    /// <summary>
    /// The local player's personal night light. Client-visual only. Three states by the
    /// EQUIPPED item, all data-driven (no hardcoded item ids):
    ///   - an item with a world.light block (torch, lamp...): its radius/color held-glow;
    ///   - tool_type "flashlight": the dim base glow PLUS a long Light2D CONE aimed at
    ///     the mouse — the deep-night exploration tool;
    ///   - anything else: a dim glow (radius ~2.5) so dark hours stay barely navigable.
    /// </summary>
    public class PlayerNightLight : MonoBehaviour
    {
        private LampLight _lamp;
        private Light2D _cone;
        private Transform _coneT;
        private Camera _cam;

        private void Start()
        {
            _lamp = gameObject.AddComponent<LampLight>();
            _lamp.Configure(2.5f, new Color(0.9f, 0.9f, 1f), 0.55f);

            // Flashlight cone: a child Light2D point light with a narrow angle (URP 17),
            // rotated toward the mouse while the flashlight is equipped.
            var go = new GameObject("FlashlightCone");
            go.transform.SetParent(transform, false);
            _coneT = go.transform;
            _cone = go.AddComponent<Light2D>();
            _cone.lightType = Light2D.LightType.Point;
            _cone.pointLightOuterRadius = 8f;
            _cone.pointLightInnerRadius = 0.5f;
            _cone.pointLightInnerAngle = 30f;
            _cone.pointLightOuterAngle = 70f;
            _cone.color = new Color(1f, 0.97f, 0.85f); // warm white
            _cone.intensity = 0f;
        }

        private void Update()
        {
            if (_lamp == null) return;

            string id = BugFarmer.UI.InventoryManager.Instance != null
                ? BugFarmer.UI.InventoryManager.Instance.GetEquippedToolId() : "";
            var def = BugFarmer.Data.EntityDatabase.Get(id);

            bool flashlight = def?.ToolType == "flashlight";
            if (def?.World != null && def.World.LightRadius > 0f)
                _lamp.Configure(def.World.LightRadius, def.World.LightColor, def.World.LightIntensity);
            else
                _lamp.Configure(2.5f, new Color(0.9f, 0.9f, 1f), 0.55f);

            if (_cone == null) return;
            float night = 1f - DayNightController.Daylight;
            _cone.intensity = flashlight ? 1.1f * Mathf.Max(night, 0.15f) : 0f;
            if (flashlight)
            {
                if (_cam == null) _cam = Camera.main;
                if (_cam != null)
                {
                    Vector2 mouse = _cam.ScreenToWorldPoint(Input.mousePosition);
                    Vector2 dir = mouse - (Vector2)transform.position;
                    if (dir.sqrMagnitude > 0.001f)
                    {
                        // A 2D cone light fans around the transform's UP axis
                        float angle = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg - 90f;
                        _coneT.rotation = Quaternion.Euler(0f, 0f, angle);
                    }
                }
            }
        }
    }
}
