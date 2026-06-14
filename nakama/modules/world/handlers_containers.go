package world

import (
	"fmt"

	"github.com/heroiclabs/nakama-common/runtime"
)

// ContainerState is the runtime contents of an item store (chest, dresser, rack). It is keyed by
// its anchor cell and lazily created the first time a player opens it (so both pre-placed and
// runtime-placed containers work without a placement hook). Display/inventory state only — it
// NEVER enters the deterministic sim hash.
type ContainerState struct {
	Key      string          // ContainerKey(gx,gy)
	EntityID string          // occupant entity id (def lookups)
	GridX    int             // anchor cell
	GridY    int             // anchor cell
	Slots    []InventorySlot // N storage cells
	Filter   string          // tag a deposited item must carry ("" = accept anything)
}

// ContainerKey builds the stable cell key for a container at a global grid cell.
func ContainerKey(gx, gy int) string {
	return fmt.Sprintf("container_%d_%d", gx, gy)
}

// resolveContainer returns the container at the anchor cell (gx,gy), lazily creating it from the
// occupant's world.container block the first time. Returns nil if there is no storage occupant
// anchored at that cell.
func (m *Match) resolveContainer(state *WorldState, gx, gy int) *ContainerState {
	key := ContainerKey(gx, gy)
	if c := state.Containers[key]; c != nil {
		return c
	}

	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return nil
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
		return nil // client must target the anchor cell (footprint cells carry no back-ref)
	}
	def := state.Entities[cell.Occupant.ID]
	if def == nil || def.World == nil || def.World.Container == nil {
		return nil
	}

	slots := def.World.Container.Slots
	if slots <= 0 {
		slots = 12
	}
	c := &ContainerState{
		Key:      key,
		EntityID: cell.Occupant.ID,
		GridX:    gx,
		GridY:    gy,
		Slots:    make([]InventorySlot, slots),
		Filter:   def.World.Container.Filter,
	}
	state.Containers[key] = c
	return c
}

// containerAccepts reports whether the container's filter admits this item (nil-safe).
func (m *Match) containerAccepts(state *WorldState, c *ContainerState, itemID string) bool {
	if c.Filter == "" {
		return true
	}
	return state.Entities[itemID].HasTag(c.Filter)
}

// addToContainer drops the WHOLE of src into the container (merging into an existing stack of the
// same item, else the first empty cell). Empties src on success; returns false if the container
// is full. (Stack caps are ignored, matching PlayerState.AddItem's current behavior.)
func addToContainer(c *ContainerState, src *InventorySlot) bool {
	if src.ItemID == "" {
		return false
	}
	for i := range c.Slots {
		if c.Slots[i].ItemID == src.ItemID {
			c.Slots[i].Count += src.Count
			*src = InventorySlot{}
			return true
		}
	}
	for i := range c.Slots {
		if c.Slots[i].ItemID == "" {
			c.Slots[i] = InventorySlot{ItemID: src.ItemID, Count: src.Count, Metadata: src.Metadata}
			*src = InventorySlot{}
			return true
		}
	}
	return false
}

// slotRef returns a pointer to the slot in the named zone ("player" item slots or "container"),
// or nil if the index is out of range.
func slotRef(player *PlayerState, c *ContainerState, zone string, idx int) *InventorySlot {
	switch zone {
	case "player":
		if idx < 0 || idx >= len(player.ItemSlots) {
			return nil
		}
		return &player.ItemSlots[idx]
	case "container":
		if idx < 0 || idx >= len(c.Slots) {
			return nil
		}
		return &c.Slots[idx]
	}
	return nil
}

// containerQuickMove transfers the WHOLE stack at (zone, slot) to the opposite side — the
// double-/shift-click affordance (drag-drop is slow). Returns true if anything moved.
func (m *Match) containerQuickMove(state *WorldState, player *PlayerState, c *ContainerState, zone string, slot int) bool {
	if zone == "player" {
		if slot < 0 || slot >= len(player.ItemSlots) {
			return false
		}
		src := &player.ItemSlots[slot]
		if src.ItemID == "" || !m.containerAccepts(state, c, src.ItemID) {
			return false
		}
		return addToContainer(c, src)
	}
	// container -> player
	if slot < 0 || slot >= len(c.Slots) {
		return false
	}
	src := &c.Slots[slot]
	if src.ItemID == "" {
		return false
	}
	if player.AddItem(src.ItemID, src.Count) < 0 {
		return false // player inventory full
	}
	*src = InventorySlot{}
	return true
}

// containerMove is precise drag-drop placement: move `count` (-1 = all) from (zone,slot) to
// (toZone,toSlot), merging onto a same-item stack, filling an empty cell, or swapping two
// whole stacks. Filter is enforced on whatever ends up inside the container.
func (m *Match) containerMove(state *WorldState, player *PlayerState, c *ContainerState, zone string, slot int, toZone string, toSlot, count int) bool {
	src := slotRef(player, c, zone, slot)
	dst := slotRef(player, c, toZone, toSlot)
	if src == nil || dst == nil || src.ItemID == "" {
		return false
	}
	if toZone == "container" && !m.containerAccepts(state, c, src.ItemID) {
		return false
	}

	n := count
	if n < 0 || n > src.Count {
		n = src.Count
	}
	if n <= 0 {
		return false
	}

	switch {
	case dst.ItemID == "":
		dst.ItemID = src.ItemID
		dst.Count = n
		dst.Metadata = src.Metadata
		src.Count -= n
		if src.Count <= 0 {
			*src = InventorySlot{}
		}
		return true

	case dst.ItemID == src.ItemID:
		dst.Count += n
		src.Count -= n
		if src.Count <= 0 {
			*src = InventorySlot{}
		}
		return true

	default:
		// Different items: only a whole-stack swap is meaningful.
		if n != src.Count {
			return false
		}
		// A swap pushes dst's item into src's zone — if that zone is the container, dst must
		// pass the filter too.
		if zone == "container" && !m.containerAccepts(state, c, dst.ItemID) {
			return false
		}
		*src, *dst = *dst, *src
		return true
	}
}

// broadcastContainerUpdate echoes a chest's contents to everyone subscribed to its chunk (so
// concurrent viewers stay in sync). Craft stations send a richer update (see craft station code).
func (m *Match) broadcastContainerUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, c *ContainerState) {
	cx, cy, _, _ := GlobalToChunk(c.GridX, c.GridY)
	msg := ContainerUpdateMessage{
		GX:     c.GridX,
		GY:     c.GridY,
		Slots:  c.Slots,
		Filter: c.Filter,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeContainerUpdate, msg)
}

// handleContainerAction routes one OpCode-98 action. Craft stations are handled by their own
// branch (added with the craft-station processor); everything else is a storage container.
func (m *Match) handleContainerAction(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg ContainerActionMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Range check (same 3.0 allowance as pickup/deposit)
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	// Craft station? (recipe processor — its own branch)
	if m.isCraftStationAt(state, msg.GX, msg.GY) {
		m.handleCraftStationAction(logger, dispatcher, state, userID, player, msg)
		return
	}

	// Storage container (chest/dresser/rack)
	c := m.resolveContainer(state, msg.GX, msg.GY)
	if c == nil {
		m.sendWorldError(dispatcher, state, userID, "Nothing to open there")
		return
	}

	changed := false
	switch msg.Op {
	case "open":
		// Echo current contents below.
	case "quick":
		changed = m.containerQuickMove(state, player, c, msg.Zone, msg.Slot)
	case "move":
		changed = m.containerMove(state, player, c, msg.Zone, msg.Slot, msg.ToZone, msg.ToSlot, msg.Count)
	default:
		m.sendWorldError(dispatcher, state, userID, "Unknown container action")
		return
	}

	if changed {
		if presence, ok := state.Presences[userID]; ok && presence != nil {
			_ = m.sendInventorySync(logger, dispatcher, player, presence)
		}
	}
	m.broadcastContainerUpdate(dispatcher, state, c)
}
