using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>
/// Builds the standalone player used by the headless cross-client SYNC TEST (tools/run_sync_test.sh).
/// A built player does NOT take the Unity project lock, so several instances run alongside an open Editor.
///
/// From the Editor:  menu  BugFarmer ▸ Build Sync-Test Player
/// Headless (needs the project lock free, i.e. Editor closed):
///   "Unity.exe" -batchmode -quit -projectPath &lt;BugFarmerClient&gt; -executeMethod SyncTestBuild.Build -logFile -
/// Output: BugFarmerClient/Build/SyncTest/BugFarmerClient.exe  (Development build → console logging on).
/// </summary>
public static class SyncTestBuild
{
    private const string OutPath = "Build/SyncTest/BugFarmerClient.exe";

    [MenuItem("BugFarmer/Build Sync-Test Player")]
    public static void Build()
    {
        var opts = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/SampleScene.unity" },
            locationPathName = OutPath,
            target = BuildTarget.StandaloneWindows64,
            // Development build keeps Debug.Log output + a Player.log we can read; no script debugging server.
            options = BuildOptions.Development,
        };

        BuildReport report = BuildPipeline.BuildPlayer(opts);
        bool ok = report.summary.result == BuildResult.Succeeded;
        if (ok)
            Debug.Log($"[SyncTestBuild] OK -> {OutPath} ({report.summary.totalSize} bytes)");
        else
            Debug.LogError($"[SyncTestBuild] FAILED: {report.summary.result} ({report.summary.totalErrors} errors)");

        if (Application.isBatchMode)
            EditorApplication.Exit(ok ? 0 : 1);
    }
}
