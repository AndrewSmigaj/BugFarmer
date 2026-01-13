using UnityEngine;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Fixed-point number for deterministic cross-platform math.
    /// Uses int32 with 3 decimal places (Value / 1000.0f = actual value).
    /// Range: approximately -2,147,483 to +2,147,483 in actual units.
    /// </summary>
    public struct FixedPoint
    {
        public int Value; // Actual = Value / 1000f

        public const int Scale = 1000;

        public static readonly FixedPoint Zero = new FixedPoint { Value = 0 };
        public static readonly FixedPoint One = new FixedPoint { Value = Scale };

        public static FixedPoint FromFloat(float f)
        {
            return new FixedPoint { Value = (int)(f * Scale) };
        }

        public static FixedPoint FromInt(int i)
        {
            return new FixedPoint { Value = i * Scale };
        }

        public float ToFloat()
        {
            return Value / (float)Scale;
        }

        public static FixedPoint operator +(FixedPoint a, FixedPoint b)
        {
            return new FixedPoint { Value = a.Value + b.Value };
        }

        public static FixedPoint operator -(FixedPoint a, FixedPoint b)
        {
            return new FixedPoint { Value = a.Value - b.Value };
        }

        public static FixedPoint operator *(FixedPoint a, FixedPoint b)
        {
            // Use long to prevent overflow: (a * b) / Scale
            return new FixedPoint { Value = (int)((long)a.Value * b.Value / Scale) };
        }

        public static FixedPoint operator *(FixedPoint a, int b)
        {
            return new FixedPoint { Value = a.Value * b };
        }

        public static FixedPoint operator /(FixedPoint a, FixedPoint b)
        {
            // Use long to prevent overflow: (a * Scale) / b
            return new FixedPoint { Value = (int)((long)a.Value * Scale / b.Value) };
        }

        public static FixedPoint operator /(FixedPoint a, int b)
        {
            return new FixedPoint { Value = a.Value / b };
        }

        public static FixedPoint operator -(FixedPoint a)
        {
            return new FixedPoint { Value = -a.Value };
        }

        public static bool operator ==(FixedPoint a, FixedPoint b) => a.Value == b.Value;
        public static bool operator !=(FixedPoint a, FixedPoint b) => a.Value != b.Value;
        public static bool operator <(FixedPoint a, FixedPoint b) => a.Value < b.Value;
        public static bool operator >(FixedPoint a, FixedPoint b) => a.Value > b.Value;
        public static bool operator <=(FixedPoint a, FixedPoint b) => a.Value <= b.Value;
        public static bool operator >=(FixedPoint a, FixedPoint b) => a.Value >= b.Value;

        public override bool Equals(object obj) => obj is FixedPoint other && Value == other.Value;
        public override int GetHashCode() => Value;
        public override string ToString() => $"{ToFloat():F3}";

        public FixedPoint Abs() => new FixedPoint { Value = Value < 0 ? -Value : Value };
    }

    /// <summary>
    /// 2D vector using fixed-point math for deterministic simulation.
    /// </summary>
    public struct FixedPoint2
    {
        public FixedPoint X;
        public FixedPoint Y;

        public static readonly FixedPoint2 Zero = new FixedPoint2 { X = FixedPoint.Zero, Y = FixedPoint.Zero };

        public FixedPoint2(FixedPoint x, FixedPoint y)
        {
            X = x;
            Y = y;
        }

        public static FixedPoint2 FromVector2(Vector2 v)
        {
            return new FixedPoint2
            {
                X = FixedPoint.FromFloat(v.x),
                Y = FixedPoint.FromFloat(v.y)
            };
        }

        public Vector2 ToVector2()
        {
            return new Vector2(X.ToFloat(), Y.ToFloat());
        }

        public static FixedPoint2 operator +(FixedPoint2 a, FixedPoint2 b)
        {
            return new FixedPoint2 { X = a.X + b.X, Y = a.Y + b.Y };
        }

        public static FixedPoint2 operator -(FixedPoint2 a, FixedPoint2 b)
        {
            return new FixedPoint2 { X = a.X - b.X, Y = a.Y - b.Y };
        }

        public static FixedPoint2 operator *(FixedPoint2 a, FixedPoint scalar)
        {
            return new FixedPoint2 { X = a.X * scalar, Y = a.Y * scalar };
        }

        public static FixedPoint2 operator /(FixedPoint2 a, FixedPoint scalar)
        {
            return new FixedPoint2 { X = a.X / scalar, Y = a.Y / scalar };
        }

        public static bool operator ==(FixedPoint2 a, FixedPoint2 b) => a.X == b.X && a.Y == b.Y;
        public static bool operator !=(FixedPoint2 a, FixedPoint2 b) => a.X != b.X || a.Y != b.Y;

        public override bool Equals(object obj) => obj is FixedPoint2 other && X == other.X && Y == other.Y;
        public override int GetHashCode() => X.GetHashCode() ^ (Y.GetHashCode() << 16);
        public override string ToString() => $"({X}, {Y})";

        /// <summary>
        /// Squared magnitude (avoids square root for distance comparisons)
        /// </summary>
        public FixedPoint SqrMagnitude()
        {
            return X * X + Y * Y;
        }

        /// <summary>
        /// Squared distance to another point
        /// </summary>
        public FixedPoint SqrDistanceTo(FixedPoint2 other)
        {
            var dx = X - other.X;
            var dy = Y - other.Y;
            return dx * dx + dy * dy;
        }

        /// <summary>
        /// Quantize to nearest integer cell coordinates.
        /// Used for deterministic player position comparison across clients.
        /// </summary>
        public FixedPoint2 Quantize()
        {
            // Round to nearest integer by dividing by Scale, rounding, then multiplying back
            int qx = ((X.Value + FixedPoint.Scale / 2) / FixedPoint.Scale) * FixedPoint.Scale;
            int qy = ((Y.Value + FixedPoint.Scale / 2) / FixedPoint.Scale) * FixedPoint.Scale;
            // Handle negative values correctly
            if (X.Value < 0) qx = ((X.Value - FixedPoint.Scale / 2) / FixedPoint.Scale) * FixedPoint.Scale;
            if (Y.Value < 0) qy = ((Y.Value - FixedPoint.Scale / 2) / FixedPoint.Scale) * FixedPoint.Scale;
            return new FixedPoint2
            {
                X = new FixedPoint { Value = qx },
                Y = new FixedPoint { Value = qy }
            };
        }
    }
}
