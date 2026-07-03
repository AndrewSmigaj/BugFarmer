package world

import (
	"encoding/json"
	"fmt"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// craftOutputSlots is the size of every craft station's output grid. Each processor's output is a
// single item type that merges into one stack (addOutput is per-item), so even a multi-proc station
// only holds a handful of live stacks — a small SHARED grid is plenty.
const craftOutputSlots = 8

// CraftProcessor is ONE parallel recipe lane of a craft station: its active recipe, the batches
// still queued (incl. the one in progress), and the ticks into the current batch. A station has
// world.craft_slots of these (default 1) — a furnace can smelt two different bars at once.
type CraftProcessor struct {
	Recipe   string `json:"recipe,omitempty"`
	Queue    int    `json:"queue,omitempty"`
	Progress int    `json:"progress,omitempty"`
}

// CraftStationState is the runtime state of a recipe station (furnace/anvil/workbench…). It is
// a Container (the SHARED Output grid) plus N parallel CraftProcessors. Lazily created the first
// time a player opens the station. Outputs are display/inventory state — NEVER in the sim hash.
type CraftStationState struct {
	Key      string // CraftStationKey(gx,gy)
	EntityID string // occupant entity id (recipe lookups)
	GridX    int    // anchor cell
	GridY    int    // anchor cell

	Output []InventorySlot  // the shared output grid (collect from here)
	Procs  []CraftProcessor // the parallel recipe lanes (len = world.craft_slots, min 1)
}

// UnmarshalJSON accepts BOTH persisted shapes: the current Procs array and the legacy
// pre-craft-slots flat Recipe/Queue/Progress (Go-default field names — the struct never had json
// tags), which folds into Procs[0]. Zone saves round-trip whole CraftStationState values, so
// shipped worlds carry the legacy shape until their next save.
func (s *CraftStationState) UnmarshalJSON(data []byte) error {
	type alias CraftStationState // method-free view — avoids UnmarshalJSON recursion
	aux := struct {
		*alias
		Recipe   string `json:"Recipe"`
		Queue    int    `json:"Queue"`
		Progress int    `json:"Progress"`
	}{alias: (*alias)(s)}
	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}
	if len(s.Procs) == 0 && (aux.Recipe != "" || aux.Queue > 0 || aux.Progress > 0) {
		s.Procs = []CraftProcessor{{Recipe: aux.Recipe, Queue: aux.Queue, Progress: aux.Progress}}
	}
	return nil
}

// craftSlotsFor returns the station's configured parallel-lane count (world.craft_slots, min 1).
func craftSlotsFor(state *WorldState, entityID string) int {
	if def := state.Entities[entityID]; def != nil && def.World != nil && def.World.CraftSlots > 1 {
		return def.World.CraftSlots
	}
	return 1
}

// ensureProcs tops a station's lanes up to its configured craft_slots — the normalize point for
// legacy restores (0 or 1 lanes) and def changes. Extra lanes beyond a SHRUNK def are kept until
// they drain: queued batches are never dropped.
func ensureProcs(state *WorldState, s *CraftStationState) {
	want := craftSlotsFor(state, s.EntityID)
	for len(s.Procs) < want {
		s.Procs = append(s.Procs, CraftProcessor{})
	}
}

// CraftStationKey builds the stable cell key for a craft station at a global grid cell.
func CraftStationKey(gx, gy int) string {
	return fmt.Sprintf("craft_%d_%d", gx, gy)
}

// craftStationEntityAt returns the occupant entity id anchored at (gx,gy) IF it is a craft station
// (i.e. it has recipes), else "". Footprint (non-anchor) cells return "" — the client targets the
// anchor.
func (m *Match) craftStationEntityAt(state *WorldState, gx, gy int) string {
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return ""
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
		return ""
	}
	id := cell.Occupant.ID
	if len(state.RecipesByStation[id]) == 0 {
		return ""
	}
	return id
}

// isCraftStationAt reports whether a craft station is anchored at (gx,gy).
func (m *Match) isCraftStationAt(state *WorldState, gx, gy int) bool {
	return m.craftStationEntityAt(state, gx, gy) != ""
}

// resolveCraftStation returns the craft station at (gx,gy), lazily creating its state the first
// time. Returns nil if no craft-station occupant is anchored there. Always normalizes the lane
// count (ensureProcs) so restored legacy saves and def changes converge on craft_slots.
func (m *Match) resolveCraftStation(state *WorldState, gx, gy int) *CraftStationState {
	key := CraftStationKey(gx, gy)
	if s := state.CraftStations[key]; s != nil {
		ensureProcs(state, s)
		return s
	}
	id := m.craftStationEntityAt(state, gx, gy)
	if id == "" {
		return nil
	}
	s := &CraftStationState{
		Key:      key,
		EntityID: id,
		GridX:    gx,
		GridY:    gy,
		Output:   make([]InventorySlot, craftOutputSlots),
	}
	ensureProcs(state, s)
	state.CraftStations[key] = s
	return s
}

// --- Player inventory aggregate helpers (counts can span multiple stacks) ---

// playerCount sums every stack of itemID in the player's item inventory.
func playerCount(player *PlayerState, itemID string) int {
	n := 0
	for i := range player.ItemSlots {
		if player.ItemSlots[i].ItemID == itemID {
			n += player.ItemSlots[i].Count
		}
	}
	return n
}

// playerConsume removes `count` of itemID across stacks. Caller must have checked availability
// (playerCount); returns false (and leaves inventory untouched-enough) only if it ran short.
func playerConsume(player *PlayerState, itemID string, count int) bool {
	if playerCount(player, itemID) < count {
		return false
	}
	remaining := count
	for i := range player.ItemSlots {
		if remaining == 0 {
			break
		}
		if player.ItemSlots[i].ItemID == itemID {
			take := player.ItemSlots[i].Count
			if take > remaining {
				take = remaining
			}
			player.RemoveItem(i, take)
			remaining -= take
		}
	}
	return remaining == 0
}

// recipeKnown reports whether the player may craft r. Recipes with unlock "" / "default" are always
// craftable (basic auto-unlock — all tool/weapon/armor tiers). Gated recipes (unlock "shop:<npc>" /
// "find") require an entry in the player's KnownRecipes (bought from a vendor or found).
func recipeKnown(player *PlayerState, id string, r *entities.RecipeDef) bool {
	if r.Unlock == "" || r.Unlock == "default" {
		return true
	}
	return player.KnownRecipes != nil && player.KnownRecipes[id]
}

// recipeAllInputs returns the recipe's inputs plus its catalyst (if any) — everything consumed
// per batch.
func recipeAllInputs(r *entities.RecipeDef) []entities.RecipeIO {
	if r.Catalyst == nil {
		return r.Inputs
	}
	out := make([]entities.RecipeIO, 0, len(r.Inputs)+1)
	out = append(out, r.Inputs...)
	out = append(out, *r.Catalyst)
	return out
}

// playerHasInputs reports whether the player can afford ONE batch of r.
func playerHasInputs(player *PlayerState, r *entities.RecipeDef) bool {
	for _, in := range recipeAllInputs(r) {
		if playerCount(player, in.Item) < in.Count {
			return false
		}
	}
	return true
}

// consumeInputs removes ONE batch of r from the player's inventory (caller checked affordability).
func consumeInputs(player *PlayerState, r *entities.RecipeDef) {
	for _, in := range recipeAllInputs(r) {
		playerConsume(player, in.Item, in.Count)
	}
}

// --- Output grid helpers ---

// outputHasRoom reports whether item can be added to the output grid (an existing stack of it, or
// any empty cell).
func outputHasRoom(s *CraftStationState, item string) bool {
	for i := range s.Output {
		if s.Output[i].ItemID == item || s.Output[i].ItemID == "" {
			return true
		}
	}
	return false
}

// addOutput merges count of item into the output grid (existing stack else first empty cell).
func addOutput(s *CraftStationState, item string, count int) {
	for i := range s.Output {
		if s.Output[i].ItemID == item {
			s.Output[i].Count += count
			return
		}
	}
	for i := range s.Output {
		if s.Output[i].ItemID == "" {
			s.Output[i] = InventorySlot{ItemID: item, Count: count}
			return
		}
	}
}

// craftCollectOne takes the WHOLE stack at output slot → player inventory (double-click). If the
// bag can't hold it, the overflow STAYS in the grid (returns false).
func craftCollectOne(player *PlayerState, s *CraftStationState, slot int) bool {
	if slot < 0 || slot >= len(s.Output) {
		return false
	}
	src := &s.Output[slot]
	if src.ItemID == "" {
		return false
	}
	if player.AddItem(src.ItemID, src.Count) < 0 {
		return false // bag full — overflow stays
	}
	*src = InventorySlot{}
	return true
}

// craftCollectAll sweeps the whole output grid into the player's inventory; whatever doesn't fit
// STAYS in the grid ("Get all").
func craftCollectAll(player *PlayerState, s *CraftStationState) bool {
	moved := false
	for i := range s.Output {
		if s.Output[i].ItemID == "" {
			continue
		}
		if player.AddItem(s.Output[i].ItemID, s.Output[i].Count) < 0 {
			continue // overflow stays
		}
		s.Output[i] = InventorySlot{}
		moved = true
	}
	return moved
}

// --- Action handling ---

// handleCraftStationAction processes one OpCode-98 action against a craft station: select a
// recipe, queue batches (pulling inputs from the player's bag up-front, Terraria-style), or
// collect output. Processing itself happens over time in processCraftStations.
func (m *Match) handleCraftStationAction(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	player *PlayerState,
	msg ContainerActionMessage,
) {
	s := m.resolveCraftStation(state, msg.GX, msg.GY)
	if s == nil {
		m.sendWorldError(dispatcher, state, userID, "No station there")
		return
	}

	// The targeted processor lane. Proc 0 always exists (ensureProcs), so a legacy message
	// without the field keeps working. collect/get_all are station-level (shared output grid)
	// and ignore it.
	proc := msg.Proc
	if proc < 0 || proc >= len(s.Procs) {
		m.sendWorldError(dispatcher, state, userID, "No such processor")
		return
	}

	invChanged := false
	switch msg.Op {
	case "open":
		// Echo current state below.

	case "set_recipe":
		if msg.Recipe != "" {
			r := state.Recipes[msg.Recipe]
			if r == nil || r.Station != s.EntityID {
				m.sendWorldError(dispatcher, state, userID, "That recipe isn't made here")
				return
			}
			if !recipeKnown(player, msg.Recipe, r) {
				m.sendWorldError(dispatcher, state, userID, "You haven't learned that recipe yet")
				return
			}
		}
		if s.Procs[proc].Queue > 0 && msg.Recipe != s.Procs[proc].Recipe {
			m.sendWorldError(dispatcher, state, userID, "That processor is busy")
			return
		}
		s.Procs[proc].Recipe = msg.Recipe

	case "craft":
		invChanged = m.craftQueue(dispatcher, state, userID, player, s, proc, msg.Recipe, msg.Qty)

	case "collect":
		invChanged = craftCollectOne(player, s, msg.Slot)

	case "get_all":
		invChanged = craftCollectAll(player, s)

	default:
		m.sendWorldError(dispatcher, state, userID, "Unknown station action")
		return
	}

	if invChanged {
		if presence, ok := state.Presences[userID]; ok && presence != nil {
			_ = m.sendInventorySync(logger, dispatcher, player, presence)
		}
	}
	m.broadcastCraftStationUpdate(dispatcher, state, s)
}

// craftQueue pulls inputs for up to `qty` batches from the player's inventory and queues them on
// the targeted processor lane. Inputs are consumed up-front; outputs appear over time. Queues as
// many as the player can afford. A lane running a DIFFERENT recipe refuses (the client picks a
// same-recipe or idle lane before sending).
func (m *Match) craftQueue(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	player *PlayerState,
	s *CraftStationState,
	proc int,
	recipeID string,
	qty int,
) bool {
	p := &s.Procs[proc] // caller validated the index
	if recipeID == "" {
		recipeID = p.Recipe
	}
	r := state.Recipes[recipeID]
	if r == nil || r.Station != s.EntityID {
		m.sendWorldError(dispatcher, state, userID, "That recipe isn't made here")
		return false
	}
	if !recipeKnown(player, recipeID, r) {
		m.sendWorldError(dispatcher, state, userID, "You haven't learned that recipe yet")
		return false
	}
	if p.Queue > 0 && p.Recipe != recipeID {
		m.sendWorldError(dispatcher, state, userID, "That processor is busy")
		return false
	}
	p.Recipe = recipeID

	if qty <= 0 {
		qty = 1
	}
	queued := 0
	for b := 0; b < qty; b++ {
		if !playerHasInputs(player, r) {
			break
		}
		consumeInputs(player, r)
		p.Queue++
		queued++
	}
	if queued == 0 {
		m.sendWorldError(dispatcher, state, userID, "Not enough materials")
		return false
	}
	return true
}

// processCraftStations advances every queued processor lane one tick: when a batch's ProcessTicks
// elapse and the SHARED output grid has room, produce one output. Inputs were already consumed at
// queue time, so a full output grid just STALLS that lane (holds at full progress) until the
// player collects — the OTHER lanes keep producing, and nothing is ever lost. Non-deterministic
// display state; never touches the food ledger.
func (m *Match) processCraftStations(state *WorldState, dispatcher runtime.MatchDispatcher) {
	for _, s := range state.CraftStations {
		produced := false
		echo := false
		for pi := range s.Procs {
			p := &s.Procs[pi]
			if p.Queue <= 0 {
				p.Progress = 0
				continue
			}
			r := state.Recipes[p.Recipe]
			if r == nil {
				p.Queue = 0
				p.Progress = 0
				continue
			}
			total := r.ProcessTicks
			if total < 1 {
				total = 1
			}

			if p.Progress < total {
				p.Progress++
			}
			if p.Progress < total {
				// Periodic progress echo so a mid-batch opener / the bar stays roughly synced
				// (the client interpolates between these for smoothness). One broadcast per
				// STATION covers every lane.
				if p.Progress%20 == 0 {
					echo = true
				}
				continue
			}

			// Batch complete — produce if there's room, else THIS lane holds (others continue).
			if !outputHasRoom(s, r.Output.Item) {
				continue // Progress stays at `total`; retry next tick
			}
			p.Progress = 0
			p.Queue--
			addOutput(s, r.Output.Item, r.Output.Count)
			produced = true
		}
		if produced || echo {
			m.broadcastCraftStationUpdate(dispatcher, state, s)
		}
	}
}

// broadcastCraftStationUpdate echoes a craft station's shared output grid + every processor
// lane's recipe/progress to its chunk.
func (m *Match) broadcastCraftStationUpdate(dispatcher runtime.MatchDispatcher, state *WorldState, s *CraftStationState) {
	cx, cy, _, _ := GlobalToChunk(s.GridX, s.GridY)
	procs := make([]CraftProcInfo, len(s.Procs))
	for i := range s.Procs {
		total := 0
		if r := state.Recipes[s.Procs[i].Recipe]; r != nil {
			total = r.ProcessTicks
			if total < 1 {
				total = 1
			}
		}
		procs[i] = CraftProcInfo{
			Recipe:   s.Procs[i].Recipe,
			Progress: s.Procs[i].Progress,
			Total:    total,
			Queue:    s.Procs[i].Queue,
		}
	}
	msg := ContainerUpdateMessage{
		GX:      s.GridX,
		GY:      s.GridY,
		Slots:   s.Output,
		IsCraft: true,
		Procs:   procs,
	}
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeContainerUpdate, msg)
}
