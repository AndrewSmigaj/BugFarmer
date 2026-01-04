package world

// AddBugs adds caught bugs to the player's inventory.
// Finds the first existing stack of the same species, or uses the first empty slot.
// Returns the slot index that was modified, or -1 if inventory is full.
// Note: For catching, bugs auto-merge into first matching stack. Players can split later.
func (p *PlayerState) AddBugs(speciesID string, count int) int {
	if count <= 0 {
		return -1
	}

	// First, find existing stack of same species
	for i := range p.BugSlots {
		if p.BugSlots[i].ItemID == speciesID {
			p.BugSlots[i].Count += count
			return i
		}
	}

	// No existing stack, find first empty slot
	for i := range p.BugSlots {
		if p.BugSlots[i].ItemID == "" {
			p.BugSlots[i].ItemID = speciesID
			p.BugSlots[i].Count = count
			return i
		}
	}

	return -1 // Inventory full
}

// RemoveBugs removes bugs from a specific slot.
// Returns true if successful, false if invalid slot or insufficient count.
func (p *PlayerState) RemoveBugs(slotIndex int, count int) bool {
	if slotIndex < 0 || slotIndex >= len(p.BugSlots) {
		return false
	}

	slot := &p.BugSlots[slotIndex]
	if slot.ItemID == "" || slot.Count < count {
		return false
	}

	slot.Count -= count
	if slot.Count <= 0 {
		slot.ItemID = ""
		slot.Count = 0
	}
	return true
}

// FindItem finds the first slot containing the given item ID.
// Returns the slot index, or -1 if not found.
func (p *PlayerState) FindItem(itemID string) int {
	for i := range p.ItemSlots {
		if p.ItemSlots[i].ItemID == itemID && p.ItemSlots[i].Count > 0 {
			return i
		}
	}
	return -1
}

// AddItem adds a tool to the player's item inventory.
// Returns the slot index that was modified, or -1 if inventory is full.
func (p *PlayerState) AddItem(itemID string, count int) int {
	if count <= 0 {
		return -1
	}

	// First, find existing stack of same item
	for i := range p.ItemSlots {
		if p.ItemSlots[i].ItemID == itemID {
			p.ItemSlots[i].Count += count
			return i
		}
	}

	// No existing stack, find first empty slot
	for i := range p.ItemSlots {
		if p.ItemSlots[i].ItemID == "" {
			p.ItemSlots[i].ItemID = itemID
			p.ItemSlots[i].Count = count
			return i
		}
	}

	return -1 // Inventory full
}

// RemoveItem removes items from a specific slot.
// Returns true if successful, false if invalid slot or insufficient count.
func (p *PlayerState) RemoveItem(slotIndex int, count int) bool {
	if slotIndex < 0 || slotIndex >= len(p.ItemSlots) {
		return false
	}

	slot := &p.ItemSlots[slotIndex]
	if slot.ItemID == "" || slot.Count < count {
		return false
	}

	slot.Count -= count
	if slot.Count <= 0 {
		slot.ItemID = ""
		slot.Count = 0
	}
	return true
}

// MoveSlot moves items between slots. Handles same-type merge, different-type swap, and splitting.
// srcType/dstType: "bug" or "item"
// count: -1 = all, else specific amount
// Returns true if move was successful.
func (p *PlayerState) MoveSlot(srcType string, srcIdx int, dstType string, dstIdx int, count int) bool {
	// Get source and destination slots
	var src, dst *InventorySlot

	if srcType == "bug" {
		if srcIdx < 0 || srcIdx >= len(p.BugSlots) {
			return false
		}
		src = &p.BugSlots[srcIdx]
	} else if srcType == "item" {
		if srcIdx < 0 || srcIdx >= len(p.ItemSlots) {
			return false
		}
		src = &p.ItemSlots[srcIdx]
	} else {
		return false
	}

	if dstType == "bug" {
		if dstIdx < 0 || dstIdx >= len(p.BugSlots) {
			return false
		}
		dst = &p.BugSlots[dstIdx]
	} else if dstType == "item" {
		if dstIdx < 0 || dstIdx >= len(p.ItemSlots) {
			return false
		}
		dst = &p.ItemSlots[dstIdx]
	} else {
		return false
	}

	// Can't move from empty slot
	if src.ItemID == "" {
		return false
	}

	// Determine amount to move
	moveCount := count
	if moveCount < 0 || moveCount > src.Count {
		moveCount = src.Count
	}

	// Case 1: Destination is empty - just move
	if dst.ItemID == "" {
		dst.ItemID = src.ItemID
		dst.Count = moveCount
		src.Count -= moveCount
		if src.Count <= 0 {
			src.ItemID = ""
			src.Count = 0
		}
		return true
	}

	// Case 2: Same item type - merge
	if dst.ItemID == src.ItemID {
		dst.Count += moveCount
		src.Count -= moveCount
		if src.Count <= 0 {
			src.ItemID = ""
			src.Count = 0
		}
		return true
	}

	// Case 3: Different item type - swap (only if moving all)
	if moveCount == src.Count {
		src.ItemID, dst.ItemID = dst.ItemID, src.ItemID
		src.Count, dst.Count = dst.Count, src.Count
		return true
	}

	// Can't partial-move to slot with different item
	return false
}
