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
    /// The local player's personal night light: a dim glow (radius ~2.5) so dark hours stay
    /// playable — and a bigger, warmer one (radius ~5) while a TORCH is the equipped hotbar
    /// item. Client-visual only.
    /// </summary>
    public class PlayerNightLight : MonoBehaviour
    {
        private LampLight _lamp;

        private void Start()
        {
            _lamp = gameObject.AddComponent<LampLight>();
            _lamp.Configure(2.5f, new Color(0.9f, 0.9f, 1f), 0.55f);
        }

        private void Update()
        {
            if (_lamp == null) return;
            bool torch = BugFarmer.UI.InventoryManager.Instance != null &&
                         BugFarmer.UI.InventoryManager.Instance.GetEquippedToolId() == "torch";
            if (torch)
                _lamp.Configure(5f, new Color(1f, 0.82f, 0.55f), 1.0f);
            else
                _lamp.Configure(2.5f, new Color(0.9f, 0.9f, 1f), 0.55f);
        }
    }
}
