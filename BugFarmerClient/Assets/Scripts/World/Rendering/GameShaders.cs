using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// The game's own shaders, held by reference so every built copy of the game contains them.
    ///
    /// A build keeps only the shaders something in it references; Shader.Find by name finds nothing else. The Editor
    /// finds every shader in the project, so a shader that was never referenced looked right in the Editor and was
    /// missing from every built copy (found 2026-10-08: no darkness, no sprite sway or hit-flash, still water). This
    /// asset (Resources/GameShaders.asset) is the reference, and <see cref="Find"/> looks only here, so the Editor
    /// behaves like a build. A shader in the project's scripts that isn't listed stops the build
    /// (Editor/GameShadersBuildCheck.cs).
    /// </summary>
    [CreateAssetMenu(fileName = "GameShaders", menuName = "BugFarmer/GameShaders")]
    public sealed class GameShaders : ScriptableObject
    {
        public const string ResourcePath = "GameShaders";

        [SerializeField] private Shader[] shaders = new Shader[0];

        private static GameShaders _instance;
        private static bool _loaded;

        /// <summary>The listed shaders (the build check reads them).</summary>
        public Shader[] Shaders => shaders;

        /// <summary>The listed shader with this name ("BugFarmer/DarknessMultiply"), or null with an error naming what's
        /// missing.</summary>
        public static Shader Find(string name)
        {
            if (!_loaded)
            {
                _loaded = true;
                _instance = Resources.Load<GameShaders>(ResourcePath);
                if (_instance == null)
                    Debug.LogError($"[GameShaders] Resources/{ResourcePath}.asset is missing — the game's own shaders can't be found.");
            }
            if (_instance != null)
                foreach (var s in _instance.shaders)
                    if (s != null && s.name == name) return s;
            Debug.LogError($"[GameShaders] '{name}' is not listed in Resources/{ResourcePath}.asset, so a built copy of the game wouldn't have it.");
            return null;
        }
    }
}
