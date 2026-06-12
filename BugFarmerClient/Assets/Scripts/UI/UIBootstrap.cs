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
            // Match the existing UI: constant pixel size (the scene canvas uses it).
            canvasGO.GetComponent<CanvasScaler>().uiScaleMode =
                CanvasScaler.ScaleMode.ConstantPixelSize;

            // Build order = render order: panel docks, hotbar, drag cursor on top.
            var panelGO = new GameObject("InventoryPanel(Code)", typeof(RectTransform));
            panelGO.transform.SetParent(canvasGO.transform, false);
            panelGO.AddComponent<InventoryPanel>();

            var hotbarGO = new GameObject("Hotbar(Code)", typeof(RectTransform));
            hotbarGO.transform.SetParent(canvasGO.transform, false);
            hotbarGO.AddComponent<HotbarUI>();

            var dragGO = new GameObject("DragDrop(Code)", typeof(RectTransform));
            dragGO.transform.SetParent(canvasGO.transform, false);
            dragGO.AddComponent<DragDropController>();
            dragGO.AddComponent<EquipmentController>();

            Debug.Log("[UIBootstrap] code-built UI canvas constructed.");
        }
    }
}
