using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using BugFarmer.Data;
using BugFarmer.Networking;

namespace BugFarmer.UI
{
    public enum SlotType { Bug, Item }

    /// <summary>
    /// Reusable inventory slot UI component.
    /// Displays item icon and count, handles click events.
    /// </summary>
    public class InventorySlotUI : MonoBehaviour, IPointerClickHandler
    {
        [SerializeField] private Image iconImage;
        [SerializeField] private TMP_Text countText;
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image background;

        public SlotType SlotType { get; private set; }
        public int SlotIndex { get; private set; }
        public string CurrentItemId { get; private set; } = "";
        public int CurrentCount { get; private set; }

        public event Action<InventorySlotUI, PointerEventData> OnSlotClicked;

        public void Initialize(SlotType type, int index)
        {
            SlotType = type;
            SlotIndex = index;
            Clear();
        }

        public void SetSlot(InventorySlot slot)
        {
            if (slot == null || slot.IsEmpty)
            {
                Clear();
                return;
            }

            CurrentItemId = slot.item_id;
            CurrentCount = slot.count;

            if (iconImage != null)
            {
                var sprite = EntityDatabase.GetItemSprite(slot.item_id);
                iconImage.sprite = sprite;
                iconImage.enabled = sprite != null;
            }

            if (countText != null)
            {
                if (slot.count > 1)
                {
                    countText.text = slot.count.ToString();
                    countText.enabled = true;
                }
                else
                {
                    countText.enabled = false;
                }
            }
        }

        public void SetSelected(bool selected)
        {
            if (selectionHighlight != null)
            {
                selectionHighlight.enabled = selected;
                if (selected)
                    Debug.Log($"[SlotUI] Slot {SlotIndex} selected, highlight enabled");
            }
            else if (selected)
            {
                Debug.LogWarning($"[SlotUI] Slot {SlotIndex} selected but selectionHighlight is NULL!");
            }
        }

        public void Clear()
        {
            CurrentItemId = "";
            CurrentCount = 0;

            if (iconImage != null)
            {
                iconImage.sprite = null;
                iconImage.enabled = false;
            }

            if (countText != null)
            {
                countText.enabled = false;
            }
        }

        public void OnPointerClick(PointerEventData eventData)
        {
            OnSlotClicked?.Invoke(this, eventData);
        }
    }
}
