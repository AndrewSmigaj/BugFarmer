using System;

namespace BugFarmer.Networking
{
    /// <summary>
    /// OpCodes for match state messages.
    /// Must match server nakama/modules/world/messages.go
    /// </summary>
    public static class OpCodes
    {
        // Client -> Server
        public const int Movement = 1;
        public const int Action = 2;
        public const int ChunkSubscribe = 3;
        public const int ChunkUnsub = 4;
        public const int TilePlace = 5;
        public const int TileBreak = 6;
        public const int ToolUse = 7;

        // Server -> Client
        public const int StateUpdate = 10;
        public const int EntityUpdate = 11;
        public const int Chat = 12;
    }

    /// <summary>
    /// Direction enum matching server entities.Direction.
    /// Down=0, Left=1, Right=2, Up=3
    /// </summary>
    public enum Direction
    {
        Down = 0,
        Left = 1,
        Right = 2,
        Up = 3
    }

    // === Client -> Server Messages ===

    /// <summary>
    /// Movement message sent to server (OpCode 1).
    /// Contains world coordinates and facing direction.
    /// </summary>
    [Serializable]
    public class MovementMessage
    {
        public float x;
        public float y;
        public int facing;
    }

    // === Server -> Client Messages ===

    /// <summary>
    /// Single entity data within EntityUpdateMessage.
    /// </summary>
    [Serializable]
    public class EntityData
    {
        public string id;
        public string type;
        public float x;
        public float y;
        public int facing;
    }

    /// <summary>
    /// Entity update message from server (OpCode 11).
    /// Contains all entity positions for the tick.
    /// </summary>
    [Serializable]
    public class EntityUpdateMessage
    {
        public EntityData[] entities;
    }
}
