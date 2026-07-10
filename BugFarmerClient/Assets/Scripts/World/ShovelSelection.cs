namespace BugFarmer.World
{
    /// <summary>
    /// The player's current shaped-ground selection for the shovel: material A, material B, and shape. The
    /// placed id is <c>matA~matB~shape</c> (or plain <c>matA</c> when the shape is "full"). M2 drives this
    /// with debug keys; M4's builder UI (material pickers + mousewheel shape cycle) replaces that. Read by
    /// <c>ToolUseController</c> when a shovel is equipped.
    /// </summary>
    public static class ShovelSelection
    {
        public static string MatA = "grass";
        public static string MatB = "dirt";
        public static int ShapeIndex = 1; // default "diagNE" (index 0 is "full")

        public static string Shape => TileCompositor.Shapes[Mod(ShapeIndex, TileCompositor.Shapes.Length)];

        /// <summary>The id the shovel places: solid A for "full", else the composite.</summary>
        public static string CurrentGroundId => Shape == "full" ? MatA : $"{MatA}~{MatB}~{Shape}";

        public static void CycleShape(int dir) => ShapeIndex = Mod(ShapeIndex + dir, TileCompositor.Shapes.Length);

        private static int Mod(int a, int n) => ((a % n) + n) % n;
    }
}
