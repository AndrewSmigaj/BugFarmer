using System.Collections.Generic;
using System.Linq;
using BugFarmer.World;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>
/// Stops a player build when one of the game's own shaders (any .shader under Assets/Scripts) isn't listed in
/// Resources/GameShaders.asset: an unlisted shader is left out of the build and the effect silently disappears from
/// every built copy (what happened to the darkness, sprite sway and water until 2026-10-10; see GameShaders.cs).
/// </summary>
public sealed class GameShadersBuildCheck : IPreprocessBuildWithReport
{
    public int callbackOrder => 0;

    public void OnPreprocessBuild(BuildReport report)
    {
        var problems = Problems();
        if (problems.Count > 0)
            throw new BuildFailedException("[GameShadersBuildCheck] " + string.Join(" ", problems));
        Debug.Log("[GameShadersBuildCheck] every shader under Assets/Scripts is listed in Resources/GameShaders.asset");
    }

    public static List<string> Problems()
    {
        var problems = new List<string>();
        var list = Resources.Load<GameShaders>(GameShaders.ResourcePath);
        if (list == null)
        {
            problems.Add($"Resources/{GameShaders.ResourcePath}.asset is missing.");
            return problems;
        }
        var listed = new HashSet<Shader>(list.Shaders.Where(s => s != null));
        if (listed.Count != list.Shaders.Length)
            problems.Add("Resources/GameShaders.asset has an empty or broken entry.");
        foreach (var guid in AssetDatabase.FindAssets("t:Shader", new[] { "Assets/Scripts" }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
            if (shader != null && !listed.Contains(shader))
                problems.Add($"'{shader.name}' ({path}) is not listed in Resources/GameShaders.asset, so the build would leave it out.");
        }
        return problems;
    }
}
