using System.Collections.Generic;
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

        // Registry of active lamps, read by DarknessOverlay to "open" the underground darkness mask where a
        // light reaches (so a torch pool isn't re-multiplied to black). Cosmetic — client-local only.
        public static readonly List<LampLight> Active = new List<LampLight>();

        private float _onFactor;   // 0..1 "how dark is it here" (night on the surface, or underground)

        /// <summary>Outer reach in world units (= cells) for the darkness light-stamp.</summary>
        public float OuterRadius => _light != null ? _light.pointLightOuterRadius : 0f;
        /// <summary>0..1 fade — how much this lamp is "on" (dark enough to matter). The reveal scales by this,
        /// so a torch fades its pool in smoothly (no snap at a cave mouth).</summary>
        public float Strength01 => _onFactor;
        /// <summary>Emitting enough to bother stamping.</summary>
        public bool IsEmitting => _onFactor > 0.02f;

        private void Awake()
        {
            EnsureLight();
        }

        private void OnEnable() { Active.Add(this); }
        private void OnDisable() { Active.Remove(this); }

        private void Update()
        {
            if (_light == null) return;
            // A torch fades in wherever it's dark — ONE "how dark is it here": the day/night curve (so it
            // fades in at dusk and glows at night) OR being underground (a smooth, boundary-blurred value, so
            // it fades in at a cave mouth the SAME way it does at dusk — no hard cave gate, no snap).
            float night = 1f - DayNightController.Daylight;
            float underground = 0f;
            var ov = DarknessOverlay.Instance;
            var tm = TilemapManager.Instance;
            if (ov != null && tm != null)
                underground = ov.UndergroundDarknessAt(tm.WorldToCell(transform.position));
            _onFactor = Mathf.Max(night, underground);
            _light.intensity = _baseIntensity * _onFactor;
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
            // Off by default — the player only emits light when a torch/lamp item is the
            // selected hotbar slot (Update drives it). No free glow at night.
            _lamp.Configure(0f, Color.clear, 0f);

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
                // Held torch/lamp (e.g. "torch", radius 3.5): a radial glow around the player.
                _lamp.Configure(def.World.LightRadius, def.World.LightColor, def.World.LightIntensity);
            else
                // Not holding a light source -> no player glow (hard to see at night unless you
                // select a torch or stand by a placed one). Terraria-style.
                _lamp.Configure(0f, Color.clear, 0f);

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
