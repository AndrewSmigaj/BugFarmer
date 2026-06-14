using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace BugFarmer.UI
{
    /// <summary>
    /// Builds the ENTIRE inventory UI in code at startup (2026-06): its own
    /// overlay canvas + HotbarUI + InventoryPanel + DragDropController — zero
    /// scene wiring. The old scene canvas keeps WorldMenu/DebugPanel.
    ///
    /// SAFETY: if the scene still contains the old hand-built UI (a HotbarUI
    /// already exists), we skip building so the two never fight — delete the
    /// old HotBar + InventoryPanel prefab instances from SampleScene to get
    /// the code-built UI.
    /// </summary>
    public static class UIBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Init()
        {
            // Info/Warning logs in the Editor otherwise force a synchronous
            // StackTraceUtility.ExtractStackTrace() per call — the dominant cost
            // behind the per-tick logging stall that froze the client. Keep
            // stacks for Error/Exception/Assert (left at their default).
            Application.SetStackTraceLogType(LogType.Log, StackTraceLogType.None);
            Application.SetStackTraceLogType(LogType.Warning, StackTraceLogType.None);

            if (Object.FindObjectOfType<HotbarUI>() != null)
            {
                Debug.Log("[UIBootstrap] scene still has the old hand-built UI — " +
                          "skipping code build (delete the old HotBar/InventoryPanel " +
                          "instances from the scene to switch).");
                return;
            }

            // EventSystem (the scene normally has one; guard anyway)
            if (Object.FindObjectOfType<EventSystem>() == null)
            {
                var es = new GameObject("EventSystem(Code)", typeof(EventSystem),
                                        typeof(StandaloneInputModule));
                Object.DontDestroyOnLoad(es);
            }

            var canvasGO = new GameObject("UICanvas(Code)", typeof(Canvas),
                                          typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = canvasGO.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 10; // above the old scene canvas (order 0)
            // Scale with the window (Andrew's screen is much larger than the
            // 800x600 reference — ConstantPixelSize left the docks tiny).
            var scaler = canvasGO.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(800, 600);
            scaler.matchWidthOrHeight = 0.5f;

            // Build order = render order: panel docks, hotbar, drag cursor on top.
            var panelGO = new GameObject("InventoryPanel(Code)", typeof(RectTransform));
            panelGO.transform.SetParent(canvasGO.transform, false);
            panelGO.AddComponent<InventoryPanel>();

            // Crafting / container panel (workbench/furnace/anvil/… + chests/dressers).
            var craftGO = new GameObject("CraftingPanel(Code)", typeof(RectTransform));
            craftGO.transform.SetParent(canvasGO.transform, false);
            craftGO.AddComponent<CraftingPanel>();

            var hotbarGO = new GameObject("Hotbar(Code)", typeof(RectTransform));
            hotbarGO.transform.SetParent(canvasGO.transform, false);
            hotbarGO.AddComponent<HotbarUI>();

            // Retire leftover hand-built drag pieces: the old CursorRoot +
            // DragDropController lived OUTSIDE the deleted prefab instances, so
            // the old controller wins the singleton race (the new one self-
            // destructs, taking EquipmentController/BugInfoCard with it) and its
            // cursor renders on the LOW scene canvas — BEHIND the new hotbar.
            // DestroyImmediate so the singleton slot is free before our Awake.
            foreach (var old in Object.FindObjectsOfType<DragDropController>())
                Object.DestroyImmediate(old);
            var oldCursor = GameObject.Find("CursorRoot");
            if (oldCursor != null)
                Object.DestroyImmediate(oldCursor);

            var dragGO = new GameObject("DragDrop(Code)", typeof(RectTransform));
            dragGO.transform.SetParent(canvasGO.transform, false);
            dragGO.AddComponent<DragDropController>();
            dragGO.AddComponent<EquipmentController>();
            dragGO.AddComponent<BugInfoCard>();

            Debug.Log("[UIBootstrap] code-built UI canvas constructed.");
        }
    }
}
