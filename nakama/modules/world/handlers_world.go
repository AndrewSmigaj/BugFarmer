package world

import (
	"encoding/json"
	"fmt"

	"bugfarmer/entities"

	"github.com/heroiclabs/nakama-common/runtime"
)

// handleChunkSubscribe loads a chunk and sends it to the subscribing player
func (m *Match) handleChunkSubscribe(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	cx, cy int,
) {
	chunkKey := ChunkKey(cx, cy)

	// Load chunk if not in memory
	if _, exists := state.Chunks[chunkKey]; !exists {
		zonePath := "data/zones/" + state.CurrentZone.ZoneID
		chunk, err := LoadChunk(zonePath, cx, cy)
		if err != nil {
			// Create empty chunk if file doesn't exist
			chunk = NewEmptyChunk(cx, cy, "grass")
			logger.Debug("Created empty chunk %d,%d (no file)", cx, cy)
		}
		state.Chunks[chunkKey] = chunk

		// ZONE PERSISTENCE note: every EDITED chunk was eager-loaded (edits applied + scanned) at
		// MatchInit by restoreWorldSave/importLegacySave — a chunk reaching this lazy path is
		// UNTOUCHED authored content, so the init scans below start it from scratch.

		// Initialize fruit tree states for any fruit trees in this chunk
		m.initFruitTreesInChunk(state, chunk, cx, cy, logger)
		m.initNestsInChunk(state, chunk, cx, cy, logger)
		m.initHostPlantsInChunk(state, chunk, cx, cy, logger)  // milkweed breeding capacity
		m.initForagePoolsInChunk(state, chunk, cx, cy, logger) // flower nectar (depletable feeding)
		// Initialize stations (compost bins etc. — entities with world.station)
		m.initStationsInChunk(state, chunk, cx, cy, logger)
	}

	// NOTE: bug state for late joiners is delivered zone-wide via LateJoinSnapshot (OpCode 72)
	// on MatchJoin, not per-chunk. The old chunk-level peer snapshot request was removed.

	// Add player to chunk subscribers
	if state.ChunkSubs[chunkKey] == nil {
		state.ChunkSubs[chunkKey] = make(map[string]bool)
	}
	state.ChunkSubs[chunkKey][userID] = true

	// Send chunk data to player
	chunk := state.Chunks[chunkKey]
	msg := ChunkDataMessage{
		ChunkX:    cx,
		ChunkY:    cy,
		Ground:    chunk.Ground,
		Occupants: chunk.Occupants,
	}
	data, _ := json.Marshal(msg)

	presence, ok := state.Presences[userID]
	if ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeChunkData, data, []runtime.Presence{presence}, nil, true)

		// Send ground items in this chunk
		cs := state.Config.ChunkSize
		for _, item := range state.GroundItems {
			if item.Position.ChunkX == cx && item.Position.ChunkY == cy {
				spawnMsg := GroundItemSpawnMessage{
					ID:       item.ID,
					ItemType: item.ItemType,
					Count:    item.Count,
					X:        float32(cx*cs) + item.Position.LocalX,
					Y:        float32(cy*cs) + item.Position.LocalY,
				}
				spawnData, _ := json.Marshal(spawnMsg)
				dispatcher.BroadcastMessage(OpCodeGroundItemSpawn, spawnData, []runtime.Presence{presence}, nil, true)
			}
		}

		// Send EVERY tracked tree's water + fruit display state in this chunk: the
		// client's default is "no droplet, no fruit", so subscribers need both messages
		// to render existing trees correctly (the snapshot carries neither).
		for _, tree := range state.FruitTreeStates {
			if tree.GridX/cs != cx || tree.GridY/cs != cy {
				continue
			}
			wMsg := TreeWaterUpdateMessage{
				GridX: tree.GridX, GridY: tree.GridY,
				WaterLevel:    tree.WaterLevel,
				PendingGrowth: tree.PendingGrowth,
				LastWaterDay:  tree.LastWaterDay,
			}
			wData, _ := json.Marshal(wMsg)
			dispatcher.BroadcastMessage(OpCodeTreeWaterUpdate, wData, []runtime.Presence{presence}, nil, true)

			if tree.FruitCount > 0 {
				fruitType := ""
				if def := state.Entities[tree.EntityID]; def != nil && def.World != nil {
					fruitType = def.World.FruitType
				}
				fMsg := TreeFruitUpdateMessage{
					GridX: tree.GridX, GridY: tree.GridY,
					FruitCount: tree.FruitCount, FruitType: fruitType,
				}
				fData, _ := json.Marshal(fMsg)
				dispatcher.BroadcastMessage(OpCodeTreeFruitUpdate, fData, []runtime.Presence{presence}, nil, true)
			}
		}

		// Send this chunk's visible nurseries (compost/milkweed/pile eggs+maggots) so a player
		// walking up to a breeding source sees its current brood (the snapshot carries none).
		for _, b := range state.BroodStates {
			if b.GridX/cs != cx || b.GridY/cs != cy {
				continue
			}
			bMsg := BroodUpdateMessage{
				GX: b.GridX, GY: b.GridY, Species: b.SpeciesID,
				Eggs: b.Eggs, Maggots: b.Maggots, Pupae: b.Pupae, Kind: b.SourceKind,
			}
			bData, _ := json.Marshal(bMsg)
			dispatcher.BroadcastMessage(OpCodeBroodUpdate, bData, []runtime.Presence{presence}, nil, true)
		}

		// Send crop states in this chunk (stage visuals for joiners — without this a grown
		// crop renders as the base sprite until its next stage change)
		for _, crop := range state.CropStates {
			if crop.GridX/cs == cx && crop.GridY/cs == cy {
				cMsg := CropUpdateMessage{
					GridX: crop.GridX, GridY: crop.GridY,
					Stage: crop.Stage, HP: crop.HP, Water: crop.Water, Flags: int(crop.Flags),
				}
				cData, _ := json.Marshal(cMsg)
				dispatcher.BroadcastMessage(OpCodeCropUpdate, cData, []runtime.Presence{presence}, nil, true)
			}
		}
	}
}

// handleChunkUnsub removes a player from chunk subscribers
func (m *Match) handleChunkUnsub(
	state *WorldState,
	userID string,
	cx, cy int,
) {
	chunkKey := ChunkKey(cx, cy)
	if subs, exists := state.ChunkSubs[chunkKey]; exists {
		delete(subs, userID)
	}
}

// handleTilePlace places an occupant at the specified location
func (m *Match) handleTilePlace(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg TilePlaceMessage,
) {
	logger.Info("TilePlace received from %s: occupant=%s at (%d,%d)", userID, msg.OccupantID, msg.GridX, msg.GridY)

	// Get entity definition
	def, exists := state.Entities[msg.OccupantID]
	if !exists {
		logger.Warn("TilePlace: Unknown entity %s", msg.OccupantID)
		m.sendWorldError(dispatcher, state, userID, "Unknown item type")
		return
	}
	logger.Info("TilePlace: Found entity def, PlacesCrop=%s", def.PlacesCrop)

	// Validate player has item in inventory. Cursor-place names its slot explicitly
	// (the drag cursor's source — resolved HERE, before the seed branch, so seed
	// cursor-place consumes the cursor's slot too); otherwise FindItem's first match.
	player := state.Players[userID]
	if player == nil {
		return
	}
	slotIndex := -1
	if msg.SourceSlot != nil {
		// Bounds-check before indexing: a hostile value would panic the match loop.
		// No FindItem fallback on mismatch — a stale client gets a visible failure.
		s := *msg.SourceSlot
		if s >= 0 && s < len(player.ItemSlots) &&
			player.ItemSlots[s].ItemID == msg.OccupantID && player.ItemSlots[s].Count > 0 {
			slotIndex = s
		}
	} else {
		slotIndex = player.FindItem(msg.OccupantID)
	}
	if slotIndex < 0 {
		m.sendWorldError(dispatcher, state, userID, "You don't have this item")
		return
	}

	// Check if this is a seed (has PlacesCrop)
	if def.PlacesCrop != "" {
		m.handleSeedPlanting(logger, dispatcher, state, userID, player, slotIndex, msg.GridX, msg.GridY, def)
		return
	}

	// Check entity can be placed in world
	if !def.IsPlaceable() {
		m.sendWorldError(dispatcher, state, userID, "Cannot place this item")
		return
	}

	// Check placement is valid
	if !m.canPlace(state, msg.GridX, msg.GridY, def, msg.Direction) {
		m.sendWorldError(dispatcher, state, userID, "Cannot place here")
		return
	}

	// Place occupant in chunk data
	cx, cy, lx, ly := GlobalToChunk(msg.GridX, msg.GridY)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		m.sendWorldError(dispatcher, state, userID, "Chunk not loaded")
		return
	}

	occ := &PlacedOccupant{ID: msg.OccupantID, Dir: msg.Direction}
	chunk.SetOccupant(lx, ly, occ)

	// Set footprint cells for multi-cell occupants
	w, h := def.GetFootprint(msg.Direction)
	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			if dx == 0 && dy == 0 {
				continue // Skip anchor
			}
			bx, by := msg.GridX+dx, msg.GridY+dy
			bcx, bcy, blx, bly := GlobalToChunk(bx, by)
			bChunk := state.Chunks[ChunkKey(bcx, bcy)]
			if bChunk != nil {
				bChunk.SetFootprintCell(blx, bly, msg.OccupantID, msg.Direction)
			}
		}
	}

	// Runtime-placed HIVE BOX: register a DORMANT nest (no free colony — a daughter-founding
	// or recovering colony must claim it; mirrors initNestsInChunk for the loaded-chunk case).
	if speciesID, hiveSpecies, isBox := m.speciesForNestOccupant(state, msg.OccupantID); hiveSpecies != nil {
		m.registerNestAt(state, msg.GridX, msg.GridY, msg.OccupantID, speciesID, hiveSpecies, isBox, logger)
	}

	// Consume item from inventory
	player.RemoveItem(slotIndex, 1)

	// Send inventory update to player
	slotMsg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    player.ItemSlots[slotIndex].ItemID,
		Count:     player.ItemSlots[slotIndex].Count,
	}
	slotData, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
	}

	logger.Debug("Player %s placed %s at %d,%d", userID, msg.OccupantID, msg.GridX, msg.GridY)

	// Broadcast update to chunk subscribers
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, msg.GridX, msg.GridY, "", occ, false)
}

// handleSeedPlanting plants a seed on a garden_plot tile
func (m *Match) handleSeedPlanting(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	player *PlayerState,
	slotIndex int,
	gx, gy int,
	seedDef *EntityDef,
) {
	logger.Info("DEBUG handleSeedPlanting: START user=%s, grid=(%d,%d), seedDef=%s", userID, gx, gy, seedDef.ID)

	cropType := seedDef.PlacesCrop
	logger.Info("DEBUG handleSeedPlanting: cropType=%s", cropType)

	// Get crop definition
	logger.Info("DEBUG handleSeedPlanting: Looking up CropDefs[%s], CropDefs has %d entries", cropType, len(state.CropDefs))
	cropDef := state.CropDefs[cropType]
	if cropDef == nil {
		logger.Warn("DEBUG handleSeedPlanting: cropDef is nil for %s", cropType)
		m.sendWorldError(dispatcher, state, userID, "Unknown crop type")
		return
	}
	logger.Info("DEBUG handleSeedPlanting: Got cropDef, MaxHarvests=%d", cropDef.MaxHarvests)

	// Get chunk and local coords
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunkKey := ChunkKey(cx, cy)
	logger.Info("DEBUG handleSeedPlanting: chunk=(%d,%d), local=(%d,%d), key=%s", cx, cy, lx, ly, chunkKey)

	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		logger.Warn("DEBUG handleSeedPlanting: chunk is nil for key %s", chunkKey)
		m.sendWorldError(dispatcher, state, userID, "Chunk not loaded")
		return
	}
	logger.Info("DEBUG handleSeedPlanting: Got chunk")

	// Check tile is garden_plot (accepts_plant)
	tile := chunk.GetGroundTile(lx, ly)
	logger.Info("DEBUG handleSeedPlanting: tile=%s", tile)
	tileDef := state.TileDefs[tile]
	if tileDef == nil || !tileDef.AcceptsPlant {
		logger.Warn("DEBUG handleSeedPlanting: tileDef nil or not AcceptsPlant")
		m.sendWorldError(dispatcher, state, userID, "Can only plant on tilled soil")
		return
	}
	logger.Info("DEBUG handleSeedPlanting: tile accepts plant")

	// Check cell is empty (no occupant)
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if !cell.IsEmpty {
		logger.Warn("DEBUG handleSeedPlanting: cell not empty")
		m.sendWorldError(dispatcher, state, userID, "Cell is occupied")
		return
	}
	logger.Info("DEBUG handleSeedPlanting: cell is empty")

	// Check no existing crop at this location
	cropKey := fmt.Sprintf("%d,%d", gx, gy)
	if state.CropStates[cropKey] != nil {
		logger.Warn("DEBUG handleSeedPlanting: crop already exists at %s", cropKey)
		m.sendWorldError(dispatcher, state, userID, "Crop already planted here")
		return
	}
	logger.Info("DEBUG handleSeedPlanting: no existing crop, creating CropState")

	// Create crop state
	plantID := fmt.Sprintf("plant_%d_%d_%d", gx, gy, state.TickCount)
	crop := &entities.CropState{
		PlantID:           plantID,
		PlantType:         cropType,
		GridX:             gx,
		GridY:             gy,
		Stage:             0, // Seed stage
		HP:                100,
		Water:             0,
		WateringsToday:    0,
		HarvestsRemaining: cropDef.MaxHarvests,
		PlantedTick:       state.TickCount,
	}
	state.CropStates[cropKey] = crop
	logger.Info("DEBUG handleSeedPlanting: Created CropState, plantID=%s", plantID)

	// Place plant occupant
	plantOccID := "plant_" + cropType
	occ := &PlacedOccupant{ID: plantOccID, Dir: 0}
	chunk.SetOccupant(lx, ly, occ)
	logger.Info("DEBUG handleSeedPlanting: Set occupant %s", plantOccID)

	// Consume seed from inventory
	player.RemoveItem(slotIndex, 1)
	logger.Info("DEBUG handleSeedPlanting: Removed seed from inventory slot %d", slotIndex)

	// Send inventory update
	logger.Info("DEBUG handleSeedPlanting: Creating SlotUpdateMessage")
	slotMsg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    player.ItemSlots[slotIndex].ItemID,
		Count:     player.ItemSlots[slotIndex].Count,
	}
	slotData, err := json.Marshal(slotMsg)
	if err != nil {
		logger.Error("DEBUG handleSeedPlanting: FAILED to marshal SlotUpdateMessage: %v", err)
	} else {
		logger.Info("DEBUG handleSeedPlanting: Marshaled SlotUpdateMessage")
	}

	presence, presenceOk := state.Presences[userID]
	logger.Info("DEBUG handleSeedPlanting: Presences lookup for %s: found=%v, nil=%v", userID, presenceOk, presence == nil)
	if presenceOk && presence != nil {
		logger.Info("DEBUG handleSeedPlanting: Broadcasting OpCodeItemSlotUpdate")
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
		logger.Info("DEBUG handleSeedPlanting: OpCodeItemSlotUpdate sent")
	}

	// Broadcast occupant placement
	logger.Info("DEBUG handleSeedPlanting: Calling broadcastWorldUpdate")
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, gx, gy, "", occ, false)
	logger.Info("DEBUG handleSeedPlanting: broadcastWorldUpdate done")

	// Broadcast initial crop state
	logger.Info("DEBUG handleSeedPlanting: Calling broadcastCropUpdate")
	m.broadcastCropUpdate(dispatcher, state, gx, gy, crop)
	logger.Info("DEBUG handleSeedPlanting: broadcastCropUpdate done")

	logger.Info("DEBUG handleSeedPlanting: END - Player %s planted %s at %d,%d", userID, cropType, gx, gy)
}

// handleTileBreak attempts to break/mine an occupant
func (m *Match) handleTileBreak(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg TileBreakMessage,
	tick int64,
) {
	cx, cy, lx, ly := GlobalToChunk(msg.GridX, msg.GridY)
	chunkKey := ChunkKey(cx, cy)
	chunk := state.Chunks[chunkKey]
	if chunk == nil {
		return // Chunk not loaded
	}

	// Get what's at this cell
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty {
		return // Nothing to break
	}
	if cell.Occupant != nil && !cell.Occupant.Anchor {
		// This is a footprint cell, not the anchor - ignore
		// TODO: Find anchor cell and break that instead
		return
	}

	occ := cell.Occupant
	def, exists := state.Entities[occ.ID]
	if !exists || !def.IsBreakable() {
		return
	}

	// Get player's equipped tool
	player := state.Players[userID]
	if player == nil {
		return
	}
	toolType, toolTier := m.getToolStats(state, player.EquippedTool)

	// Check tool requirements
	if !def.CanBreakWith(toolType, toolTier) {
		m.sendWorldError(dispatcher, state, userID, "Need better tool")
		return
	}

	// Get or create breaking progress
	breakKey := fmt.Sprintf("%d,%d", msg.GridX, msg.GridY)
	hp := def.GetHP()
	progress, exists := state.BreakingState[breakKey]
	if !exists || progress.PlayerID != userID {
		progress = &BreakingProgress{
			GridX:     msg.GridX,
			GridY:     msg.GridY,
			PlayerID:  userID,
			CurrentHP: hp,
			MaxHP:     hp,
			LastTick:  tick,
		}
		state.BreakingState[breakKey] = progress
	}

	// Apply damage
	progress.CurrentHP--
	progress.LastTick = tick

	// AGGRO-ON-DAMAGE: hitting a wasp nest recalls its resident onto the attacker
	// regardless of distance — axing while the patrol hunts is a head start, not
	// immunity (the loiter window LOOKS safe; the sign warns it isn't).
	m.recallNestDefenders(state, msg.GridX, msg.GridY, userID)

	// Tool hits KNOCK fruit off a fruit tree — one per registered hit, straight to the
	// ground via the normal drop path (the evening window doesn't apply: a hit is a hit).
	// Picking by hand (OpCode 92) is how fruit enters the inventory; tools shake it loose.
	if tree := state.FruitTreeStates[breakKey]; tree != nil && tree.FruitCount > 0 &&
		def.World != nil && def.World.FruitType != "" {
		tree.FruitCount--
		m.dropFruitFromTree(dispatcher, state, tree, def.World.FruitType, logger)
		m.broadcastTreeFruitUpdate(dispatcher, state, tree, def.World.FruitType)
	}

	// Broadcast progress
	progressMsg := BreakProgressMessage{
		GridX:     msg.GridX,
		GridY:     msg.GridY,
		CurrentHP: progress.CurrentHP,
		MaxHP:     progress.MaxHP,
		PlayerID:  userID,
	}
	logger.Debug("Broadcasting BreakProgress: %d,%d HP=%d/%d", msg.GridX, msg.GridY, progress.CurrentHP, progress.MaxHP)
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeBreakProgress, progressMsg)

	// Check if broken
	if progress.CurrentHP <= 0 {
		m.breakOccupantAt(logger, dispatcher, state, msg.GridX, msg.GridY, true)
		logger.Debug("Player %s broke %s at %d,%d", userID, occ.ID, msg.GridX, msg.GridY)
	}
}

// breakOccupantAt is THE shared occupant-removal completion path (player breaks +
// centipede gnaw + any future server-side destruction): clears the footprint cells,
// optionally rolls the def's drops (gnawed fences are CONSUMED — withDrops=false),
// clears breaking state, runs the nest-destruction hook, and broadcasts the removal.
func (m *Match) breakOccupantAt(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	gx, gy int,
	withDrops bool,
) {
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil {
		return
	}
	occ := cell.Occupant
	def := state.Entities[occ.ID]
	if def == nil {
		return
	}

	// Remove occupant + clear the full footprint
	chunk.ClearOccupant(lx, ly)
	w, h := def.GetFootprint(occ.Dir)
	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			bx, by := gx+dx, gy+dy
			bcx, bcy, blx, bly := GlobalToChunk(bx, by)
			bChunk := state.Chunks[ChunkKey(bcx, bcy)]
			if bChunk != nil {
				bChunk.ClearOccupant(blx, bly)
			}
		}
	}

	// Phase 1b: a REMOVED blocks_bugs occupant (player break OR centipede gnaw — this is the shared path)
	// unblocks its cells for per-bug collision zone-wide. Ride the tick-ordered ledger so every client
	// (incl. far ones) clears these cells at the SAME tick. w,h are the removed occupant's footprint.
	if def.World != nil && def.World.BlocksBugs && state.CurrentZone != nil {
		for dy := 0; dy < h; dy++ {
			for dx := 0; dx < w; dx++ {
				state.AddOccupantBlocksBugsEvent(state.CurrentZone.ZoneID, gx+dx, gy+dy, false)
			}
		}
	}

	// Drop items to ground (with chance-based multi-drop)
	if withDrops {
		drops := def.GetDrops()
		cs := float32(state.Config.ChunkSize)
		for _, drop := range drops {
			if state.Rng.Float32() > drop.Chance {
				continue
			}
			// Roll the drop count in [CountMin, CountMax] (server-authoritative; broadcast so clients agree).
			dropCount := drop.CountMin
			if drop.CountMax > drop.CountMin {
				dropCount += state.Rng.Intn(drop.CountMax - drop.CountMin + 1)
			}
			itemID := state.nextItemID(fmt.Sprintf("item_%d_%d", gx, gy))
			worldX := float32(gx) + 0.5 + (state.Rng.Float32()-0.5)*0.3
			worldY := float32(gy) + 0.5 + (state.Rng.Float32()-0.5)*0.3
			localX := worldX - float32(cx)*cs
			localY := worldY - float32(cy)*cs

			groundItem := &entities.GroundItem{
				ID:       itemID,
				ItemType: drop.ItemID,
				Count:    dropCount,
				Position: entities.EntityPosition{
					ChunkX: cx, ChunkY: cy, LocalX: localX, LocalY: localY,
				},
				Lifetime: 60.0,
			}
			state.putGroundItem(groundItem)

			spawnMsg := GroundItemSpawnMessage{
				ID: itemID, ItemType: drop.ItemID, Count: dropCount, X: worldX, Y: worldY,
			}
			m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeGroundItemSpawn, spawnMsg)
			logger.Debug("Spawned ground item %s x%d at %.1f,%.1f", drop.ItemID, drop.Count, worldX, worldY)
		}
	}

	// Clear breaking state for this cell
	delete(state.BreakingState, fmt.Sprintf("%d,%d", gx, gy))

	// Nest destruction: clear the state + ORPHAN the resident (it never breeds again,
	// tethers to its last home, still hunts/stings — a decaying patrol).
	m.onNestOccupantRemoved(state, dispatcher, gx, gy, logger)

	// A broken compost bin / milkweed loses its in-progress nursery (its eggs/maggots vanish).
	m.onBroodSourceRemoved(state, dispatcher, gx, gy)

	// Broadcast removal (clear occupant)
	m.broadcastWorldUpdate(dispatcher, state, cx, cy, gx, gy, "", nil, true)
}

// canPlace checks if an occupant can be placed at the given location
func (m *Match) canPlace(state *WorldState, gx, gy int, def *EntityDef, dir int) bool {
	w, h := def.GetFootprint(dir)

	for dy := 0; dy < h; dy++ {
		for dx := 0; dx < w; dx++ {
			cx, cy, lx, ly := GlobalToChunk(gx+dx, gy+dy)
			chunkKey := ChunkKey(cx, cy)
			chunk, exists := state.Chunks[chunkKey]
			if !exists {
				return false
			}

			cell, _ := chunk.GetOccupantCell(lx, ly)
			if !cell.IsEmpty {
				return false
			}
		}
	}
	return true
}

// broadcastToChunk sends a message to all players subscribed to a chunk
func (m *Match) broadcastToChunk(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	cx, cy int,
	opCode int64,
	msg interface{},
) {
	chunkKey := ChunkKey(cx, cy)
	subs := state.ChunkSubs[chunkKey]
	if len(subs) == 0 {
		return
	}

	var presences []runtime.Presence
	for userID := range subs {
		if p, exists := state.Presences[userID]; exists && p != nil {
			presences = append(presences, p)
		}
	}

	if len(presences) == 0 {
		return
	}

	data, _ := json.Marshal(msg)
	dispatcher.BroadcastMessage(opCode, data, presences, nil, true)
}

// broadcastWorldUpdate sends a world cell update to chunk subscribers
// clearOccupant: true = explicitly remove occupant, false = no change to occupant
func (m *Match) broadcastWorldUpdate(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	cx, cy, gx, gy int,
	ground string,
	occupant *PlacedOccupant,
	clearOccupant bool,
) {
	msg := WorldUpdateMessage{
		GridX:  gx,
		GridY:  gy,
		Ground: ground,
	}
	// Only include occupant field when explicitly setting or clearing
	// nil pointer assigned to interface{} is NOT nil interface, so omitempty won't work
	if occupant != nil {
		msg.Occupant = occupant
	} else if clearOccupant {
		// Assign typed nil to get "occupant": null in JSON (signals removal)
		msg.Occupant = (*PlacedOccupant)(nil)
	}
	// If neither: msg.Occupant stays as true nil interface, field is omitted (no change)
	m.broadcastToChunk(dispatcher, state, cx, cy, OpCodeWorldUpdate, msg)

	// Phase 1b: a PLACED blocks_bugs occupant changes per-bug COLLISION zone-wide. The WorldUpdate above is
	// chunk-scoped (can't reach far clients), so ALSO ride the tick-ordered ledger here — central to EVERY
	// placement path (player place, seed, runtime nest spawn). One event per footprint cell (anchor incl.).
	// Removal is emitted by breakOccupantAt (which has the removed occupant's def/footprint; here occ is nil).
	if occupant != nil && !clearOccupant && state.CurrentZone != nil {
		if def := state.Entities[occupant.ID]; def != nil && def.World != nil && def.World.BlocksBugs {
			w, h := def.GetFootprint(occupant.Dir)
			for dy := 0; dy < h; dy++ {
				for dx := 0; dx < w; dx++ {
					state.AddOccupantBlocksBugsEvent(state.CurrentZone.ZoneID, gx+dx, gy+dy, true)
				}
			}
		}
	}
}

// getToolStats returns the tool type and tier for a given tool ID
func (m *Match) getToolStats(state *WorldState, toolID string) (toolType string, tier int) {
	if toolID == "" {
		return "", 0 // Bare hands
	}

	// Look up tool from entity definitions. Weapons (sword/spear) carry a tool_type
	// too — a wielded weapon must resolve its type/tier, not read as bare hands.
	if def, exists := state.Entities[toolID]; exists && (def.Category == "tool" || def.Category == "weapon") {
		return def.ToolType, def.ToolTier
	}

	return "", 0
}

// sendWorldError sends an error message to a specific player
func (m *Match) sendWorldError(
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	message string,
) {
	msg := ErrorMessage{Error: message}
	data, _ := json.Marshal(msg)
	if presence, exists := state.Presences[userID]; exists && presence != nil {
		dispatcher.BroadcastMessage(OpCodeErrorMessage, data, []runtime.Presence{presence}, nil, true)
	}
}

// handlePickupItem processes a player's request to pick up a ground item
func (m *Match) handlePickupItem(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg PickupItemMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	item, exists := state.GroundItems[msg.ID]
	if !exists {
		// Item already picked up by another player - silently ignore
		return
	}

	// Distance check (server allows 3.0 vs client 2.0 to account for latency)
	cs := state.Config.ChunkSize
	playerX := player.WorldX(cs)
	playerY := player.WorldY(cs)
	itemX := float32(item.Position.ChunkX*cs) + item.Position.LocalX
	itemY := float32(item.Position.ChunkY*cs) + item.Position.LocalY

	dx := playerX - itemX
	dy := playerY - itemY
	if dx*dx+dy*dy > 9.0 { // 3.0 squared
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	slotIndex := player.AddItem(item.ItemType, item.Count)
	if slotIndex < 0 {
		m.sendWorldError(dispatcher, state, userID, "Inventory full")
		return
	}

	// Remove from ground
	state.deleteGroundItem(msg.ID)

	// If this was registered BUG FOOD (rotten fruit), tell the deterministic food registry
	// it's gone — bug AI must forget it at a tick boundary, not just visually.
	if item.FoodValue > 0 && state.CurrentZone != nil {
		wcx := item.Position.ChunkX*cs + int(item.Position.LocalX)
		wcy := item.Position.ChunkY*cs + int(item.Position.LocalY)
		state.AddFoodEvent(state.CurrentZone.ZoneID, InfluenceFoodConsumed, msg.ID, wcx, wcy, 0)
	}

	// Send inventory update to player
	slotMsg := SlotUpdateMessage{
		SlotIndex: slotIndex,
		ItemID:    player.ItemSlots[slotIndex].ItemID,
		Count:     player.ItemSlots[slotIndex].Count,
	}
	slotData, _ := json.Marshal(slotMsg)
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, slotData, []runtime.Presence{presence}, nil, true)
	}

	// Broadcast removal to chunk subscribers
	removeMsg := GroundItemRemoveMessage{ID: msg.ID}
	m.broadcastToChunk(dispatcher, state, item.Position.ChunkX, item.Position.ChunkY, OpCodeGroundItemRemove, removeMsg)

	logger.Debug("Player %s picked up %s x%d", userID, item.ItemType, item.Count)
}

// handleEquipArmor (OpCode 96): equip/unequip/swap worn armor. The message is
// {equip_slot, inv_slot} — no item search, duplicate-safe:
//   - equip:  ItemSlots[inv_slot] must be category "armor" with the matching
//     armor_slot; the piece moves INTO Equipment[equip_slot]; if that slot was
//     occupied, the old piece goes into inv_slot (just vacated) — a swap can
//     never hit "inventory full".
//   - unequip: inv_slot == -1 → AddItem back (the only rejectable case).
//
// Echoes the authoritative truth (EquipmentUpdate + ItemSlotUpdate) so the
// client always converges; the per-tick EntityData.eqa shows it to everyone.
func (m *Match) handleEquipArmor(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg EquipArmorMessage,
) {
	player := state.Players[userID]
	if player == nil || msg.EquipSlot < 0 || msg.EquipSlot >= len(player.Equipment) {
		return
	}

	slotNames := [8]string{"head", "body", "arms", "legs", "feet", "accessory", "accessory", "backpack"}
	echoInv := -1
	isBackpack := msg.EquipSlot == backpackSlotIndex

	// Backpack capacity safety: if this action would SHRINK usable item slots, the
	// to-be-locked slots must be empty (else worn items would strand). Check BEFORE mutating.
	if isBackpack {
		newBackpack := ""
		if msg.InvSlot != -1 && msg.InvSlot >= 0 && msg.InvSlot < len(player.ItemSlots) {
			newBackpack = player.ItemSlots[msg.InvSlot].ItemID
		}
		newCap := baseUnlockedItemSlots
		if newBackpack != "" {
			if d := state.Entities[newBackpack]; d != nil && d.SlotBonus > 0 {
				newCap += d.SlotBonus
			}
		}
		if newCap > len(player.ItemSlots) {
			newCap = len(player.ItemSlots)
		}
		for i := newCap; i < player.ItemSlotsUnlocked && i < len(player.ItemSlots); i++ {
			if player.ItemSlots[i].ItemID != "" {
				m.sendWorldError(dispatcher, state, userID, "Empty your backpack's extra slots first")
				return
			}
		}
	}

	if msg.InvSlot == -1 {
		// UNEQUIP -> inventory
		worn := player.Equipment[msg.EquipSlot]
		if worn == "" {
			return
		}
		slotIndex := player.AddItem(worn, 1)
		if slotIndex < 0 {
			m.sendWorldError(dispatcher, state, userID, "Inventory full")
			return
		}
		player.Equipment[msg.EquipSlot] = ""
		echoInv = slotIndex
	} else {
		// EQUIP from inv_slot (swap-safe)
		if msg.InvSlot < 0 || msg.InvSlot >= len(player.ItemSlots) {
			return
		}
		item := player.ItemSlots[msg.InvSlot]
		if item.ItemID == "" {
			return
		}
		def := state.Entities[item.ItemID]
		wantCat := "armor"
		if isBackpack {
			wantCat = "backpack"
		}
		if def == nil || def.Category != wantCat || def.ArmorSlot != slotNames[msg.EquipSlot] {
			m.sendWorldError(dispatcher, state, userID, "That doesn't go there")
			return
		}
		old := player.Equipment[msg.EquipSlot]
		player.Equipment[msg.EquipSlot] = item.ItemID
		// the equipped piece leaves the inventory; an old piece takes its slot
		player.ItemSlots[msg.InvSlot] = InventorySlot{}
		if old != "" {
			player.ItemSlots[msg.InvSlot] = InventorySlot{ItemID: old, Count: 1}
		}
		echoInv = msg.InvSlot
	}

	// A backpack change alters usable capacity — recompute it.
	if isBackpack {
		state.recomputeItemCapacity(player)
	}

	// ---- echoes: equipment truth + the touched inventory slot
	if presence, ok := state.Presences[userID]; ok && presence != nil {
		eqMsg := EquipmentUpdateMessage{Equipment: player.Equipment[:]}
		if data, err := json.Marshal(eqMsg); err == nil {
			dispatcher.BroadcastMessage(OpCodeEquipmentUpdate, data, []runtime.Presence{presence}, nil, true)
		}
		if isBackpack {
			// capacity (ItemSlotsUnlocked) + possibly several slots changed → full re-sync
			_ = m.sendInventorySync(logger, dispatcher, player, presence)
		} else if echoInv >= 0 {
			slotMsg := SlotUpdateMessage{
				SlotIndex: echoInv,
				ItemID:    player.ItemSlots[echoInv].ItemID,
				Count:     player.ItemSlots[echoInv].Count,
			}
			if data, err := json.Marshal(slotMsg); err == nil {
				dispatcher.BroadcastMessage(OpCodeItemSlotUpdate, data, []runtime.Presence{presence}, nil, true)
			}
		}
	}
	logger.Debug("Player %s equipment: %v", userID, player.Equipment)
}
