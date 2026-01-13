namespace BugFarmer.Bugs
{
    /// <summary>
    /// Fixed-point math utilities with lookup tables for deterministic trig.
    /// All operations stay in integer domain - no float conversions.
    /// </summary>
    public static class FixedPointMath
    {
        // 256-entry lookup table for sin (covers 0 to 2*PI)
        // Values are in FixedPoint scale (multiply by 1000)
        private static readonly int[] SinTable = new int[256];
        private static readonly int[] CosTable = new int[256];

        public const int TableSize = 256;
        public const int TwoPiScaled = 6283; // 2 * PI * 1000

        static FixedPointMath()
        {
            // Precompute tables at startup (one-time cost)
            for (int i = 0; i < TableSize; i++)
            {
                double angle = i * 2.0 * System.Math.PI / TableSize;
                SinTable[i] = (int)(System.Math.Sin(angle) * FixedPoint.Scale);
                CosTable[i] = (int)(System.Math.Cos(angle) * FixedPoint.Scale);
            }
        }

        /// <summary>
        /// Get sin from lookup table. Angle is in fixed-point radians.
        /// </summary>
        public static FixedPoint Sin(FixedPoint angle)
        {
            int wrapped = ((angle.Value % TwoPiScaled) + TwoPiScaled) % TwoPiScaled;
            int index = wrapped * TableSize / TwoPiScaled;
            if (index >= TableSize) index = TableSize - 1;
            return new FixedPoint { Value = SinTable[index] };
        }

        /// <summary>
        /// Get cos from lookup table. Angle is in fixed-point radians.
        /// </summary>
        public static FixedPoint Cos(FixedPoint angle)
        {
            int wrapped = ((angle.Value % TwoPiScaled) + TwoPiScaled) % TwoPiScaled;
            int index = wrapped * TableSize / TwoPiScaled;
            if (index >= TableSize) index = TableSize - 1;
            return new FixedPoint { Value = CosTable[index] };
        }

        /// <summary>
        /// Integer-only square root using Newton-Raphson.
        /// </summary>
        public static FixedPoint Sqrt(FixedPoint value)
        {
            if (value.Value <= 0) return FixedPoint.Zero;

            // Scale up for precision: sqrt(x * Scale)
            long x = (long)value.Value * FixedPoint.Scale;
            long estimate = x;

            // Initial estimate
            if (x > 1000000) estimate = x / 1000;
            else if (x > 10000) estimate = x / 100;
            else if (x > 100) estimate = x / 10;

            // Newton-Raphson iterations
            for (int i = 0; i < 5; i++)
            {
                if (estimate == 0) break;
                estimate = (estimate + x / estimate) / 2;
            }

            return new FixedPoint { Value = (int)estimate };
        }

        /// <summary>
        /// Normalize a vector to unit length (deterministic).
        /// </summary>
        public static FixedPoint2 Normalize(FixedPoint2 v)
        {
            var sqrMag = v.SqrMagnitude();
            if (sqrMag.Value == 0) return FixedPoint2.Zero;

            var mag = Sqrt(sqrMag);
            if (mag.Value == 0) return FixedPoint2.Zero;

            return new FixedPoint2(v.X / mag, v.Y / mag);
        }

        /// <summary>
        /// Get a unit direction vector from table index (0-255).
        /// </summary>
        public static FixedPoint2 DirectionFromIndex(int index)
        {
            index = ((index % TableSize) + TableSize) % TableSize;
            return new FixedPoint2(
                new FixedPoint { Value = CosTable[index] },
                new FixedPoint { Value = SinTable[index] }
            );
        }
    }
}
