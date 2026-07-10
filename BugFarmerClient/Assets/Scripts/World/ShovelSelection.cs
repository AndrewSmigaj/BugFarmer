namespace BugFarmer.World
{
    /// <summary>
    /// The player's current shaped-ground selection for the shovel: material A, material B, and shape. The
    /// placed id is <c>matA~matB~shape</c> (or plain <c>matA</c> when the shape is "full"). Driven by the
    /// builder input (mouse wheel + modifiers); read by <c>ToolUseController</c> when a shovel is equipped.
    /// The palette is the decorative-material set (mirrors the server's shovelMaterials allow-list).
    /// </summary>
    public static class ShovelSelection
    {
        /// <summary>Placeable decorative materials (mirrors server tiles.go shovelMaterials). Keep in sync.</summary>
        public static readonly string[] Materials =
        {
            "grass", "dirt", "sand", "mud", "stone_floor", "stone_path", "wood_floor", "cave_floor",
        };

        public static int MatAIndex = 0; // grass
        public static int MatBIndex = 1; // dirt
        public static int ShapeIndex = 1; // "diagNE" (index 0 is "full")

        public static string MatA => Materials[Mod(MatAIndex, Materials.Length)];
        public static string MatB => Materials[Mod(MatBIndex, Materials.Length)];
        public static string Shape => TileCompositor.Shapes[Mod(ShapeIndex, TileCompositor.Shapes.Length)];

        /// <summary>The id the shovel places: solid A for "full", else the composite.</summary>
        public static string CurrentGroundId => Shape == "full" ? MatA : $"{MatA}~{MatB}~{Shape}";

        public static void CycleShape(int dir) => ShapeIndex = Mod(ShapeIndex + dir, TileCompositor.Shapes.Length);
        public static void CycleMatA(int dir) => MatAIndex = Mod(MatAIndex + dir, Materials.Length);
        public static void CycleMatB(int dir) => MatBIndex = Mod(MatBIndex + dir, Materials.Length);

        /// <summary>The inventory block a given ground material costs to place / yields when dug (mirrors the
        /// server's GroundMaterialItem). Used by the builder HUD to show the held count.</summary>
        public static string MaterialItem(string material)
        {
            switch (material)
            {
                case "grass": return "grass_turf";
                case "dirt": return "dirt";
                case "sand": return "sand";
                case "mud": return "mud";
                case "stone_floor":
                case "stone_path":
                case "cave_floor": return "stone";
                case "wood_floor": return "wood";
            }
            return "";
        }

        private static int Mod(int a, int n) => ((a % n) + n) % n;
    }
}
