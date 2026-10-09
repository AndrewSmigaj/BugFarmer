// The UnityEngine types DarknessField.cs uses, with Unity's own definitions (Mathf.SmoothStep is Unity's formula).
using System;

namespace UnityEngine
{
    public struct Color32
    {
        public byte r, g, b, a;
        public Color32(byte r, byte g, byte b, byte a) { this.r = r; this.g = g; this.b = b; this.a = a; }
    }

    public struct Vector2Int : IEquatable<Vector2Int>
    {
        public int x, y;
        public Vector2Int(int x, int y) { this.x = x; this.y = y; }
        public bool Equals(Vector2Int o) => x == o.x && y == o.y;
        public override bool Equals(object o) => o is Vector2Int v && Equals(v);
        public override int GetHashCode() => x * 73856093 ^ y * 19349663;
    }

    public static class Mathf
    {
        public static float Max(float a, float b) => a > b ? a : b;
        public static int Max(int a, int b) => a > b ? a : b;
        public static float Min(float a, float b) => a < b ? a : b;
        public static int Min(int a, int b) => a < b ? a : b;
        public static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);
        public static float Sqrt(float v) => (float)Math.Sqrt(v);
        public static int FloorToInt(float v) => (int)Math.Floor(v);
        public static int CeilToInt(float v) => (int)Math.Ceiling(v);
        public static float SmoothStep(float from, float to, float t)
        {
            t = Clamp01(t);
            t = -2.0F * t * t * t + 3.0F * t * t;
            return to * t + from * (1F - t);
        }
    }
}
