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
    private const string ReleaseOutPath = "Build/Release/BugFarmerClient.exe";

    [MenuItem("BugFarmer/Build Sync-Test Player")]
    public static void Build() =>
        // Development build keeps Debug.Log output + a Player.log we can read; no script debugging server.
        BuildTo(OutPath, BuildOptions.Development);

    /// <summary>
    /// The same player WITHOUT the Development flag (docs/plans/village-slice.md, Stage 1.0b): the Unity profiler
    /// markers are compiled out, so timings judged against the performance targets come from this build. Headless:
    /// -executeMethod SyncTestBuild.BuildRelease → Build/Release/BugFarmerClient.exe.
    /// </summary>
    [MenuItem("BugFarmer/Build Release Test Player")]
    public static void BuildRelease() => BuildTo(ReleaseOutPath, BuildOptions.None);

    private static void BuildTo(string outPath, BuildOptions options)
    {
        var opts = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/SampleScene.unity" },
            locationPathName = outPath,
            target = BuildTarget.StandaloneWindows64,
            options = options,
        };

        BuildReport report = BuildPipeline.BuildPlayer(opts);
        bool ok = report.summary.result == BuildResult.Succeeded;
        if (ok)
            Debug.Log($"[SyncTestBuild] OK -> {outPath} ({report.summary.totalSize} bytes)");
        else
            Debug.LogError($"[SyncTestBuild] FAILED: {report.summary.result} ({report.summary.totalErrors} errors)");

        if (Application.isBatchMode)
            EditorApplication.Exit(ok ? 0 : 1);
    }
}
