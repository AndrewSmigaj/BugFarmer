namespace BugFarmer.Util
{
    /// <summary>
    /// Single switch for the high-frequency diagnostic logging (per-tick gate,
    /// per-message opcode dumps, the DebugFileLogger file sink). Default OFF:
    /// in the Editor those logs ran ~125 lines/tick and stalled the Unity main
    /// thread (the socket couldn't be drained → Nakama closed the session with
    /// "session outgoing queue full" → frozen client). Flip to true to bring the
    /// diagnostics back when investigating sync issues.
    /// See docs/product/investigations/crash_investigation.md.
    /// </summary>
    public static class DebugConfig
    {
        public static bool Verbose = false;
    }
}
