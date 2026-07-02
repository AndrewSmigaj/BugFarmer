package world

import (
	"strings"

	"github.com/heroiclabs/nakama-common/runtime"
)

// NPC vendors. A buy/sell is a per-player coin + inventory transaction — it NEVER enters the
// deterministic sim hash (like containers). The server is authoritative for price and validation:
// the client message carries only what to trade, never a price. Stock is unlimited (no shared
// mutable shop state), so concurrent buys can't race. See ShopData / handleShopAction.

// resolveShop returns the shop block of the vendor occupant anchored at (gx,gy), or nil. Mirrors
// resolveContainer: the client must target the anchor cell (footprint cells carry no back-ref).
func (m *Match) resolveShop(state *WorldState, gx, gy int) *ShopData {
	cx, cy, lx, ly := GlobalToChunk(gx, gy)
	chunk := state.Chunks[ChunkKey(cx, cy)]
	if chunk == nil {
		return nil
	}
	cell, _ := chunk.GetOccupantCell(lx, ly)
	if cell.IsEmpty || cell.Occupant == nil || !cell.Occupant.Anchor {
		return nil
	}
	def := state.Entities[cell.Occupant.ID]
	if def == nil || def.World == nil {
		return nil
	}
	return def.World.Shop
}

// handleShopAction processes one buy/sell at the vendor at (gx,gy) (OpCodeAction). The response is the
// existing FullInventorySync echo (coins + item + bug slots) — no shop-specific S→C opcode.
func (m *Match) handleShopAction(
	logger runtime.Logger,
	dispatcher runtime.MatchDispatcher,
	state *WorldState,
	userID string,
	msg ShopActionMessage,
) {
	player := state.Players[userID]
	if player == nil {
		return
	}

	// Range check (same 3.0 allowance as container/station interactions).
	cs := state.Config.ChunkSize
	px, py := player.WorldX(cs), player.WorldY(cs)
	dx, dy := px-(float32(msg.GX)+0.5), py-(float32(msg.GY)+0.5)
	if dx*dx+dy*dy > 9.0 {
		m.sendWorldError(dispatcher, state, userID, "Too far away")
		return
	}

	shop := m.resolveShop(state, msg.GX, msg.GY)
	if shop == nil {
		m.sendWorldError(dispatcher, state, userID, "Nothing to trade there")
		return
	}

	qty := msg.Qty
	if qty <= 0 {
		qty = 1
	}
	if qty > 999 {
		qty = 999
	}

	var changed bool
	switch msg.Op {
	case "buy":
		switch msg.SlotType {
		case "recipe":
			changed = m.shopBuyRecipe(dispatcher, state, userID, player, shop, msg.ID)
		case "book":
			changed = m.shopBuyBook(dispatcher, state, userID, player, shop, msg.ID)
		default:
			changed = m.shopBuy(dispatcher, state, userID, player, shop, msg.ID, qty)
		}
	case "sell":
		changed = m.shopSell(dispatcher, state, userID, player, shop, msg.ID, qty, msg.Slot, msg.SlotType)
	case "sell_batch":
		changed = m.shopSellBatch(dispatcher, state, userID, player, shop, msg.Lines)
	default:
		m.sendWorldError(dispatcher, state, userID, "Unknown shop action")
		return
	}

	if changed {
		if presence, ok := state.Presences[userID]; ok && presence != nil {
			_ = m.sendInventorySync(logger, dispatcher, player, presence)
		}
	}
}

// shopBuy: the player buys `id` × qty from the shop's sells list. Price is the shop's asking Price.
// Adds to bug slots when the shop is a bug dealer and `id` is a live species; otherwise item slots.
// Inventory-full aborts WITHOUT charging coins.
func (m *Match) shopBuy(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, player *PlayerState, shop *ShopData, id string, qty int) bool {
	unit := int64(-1)
	for _, e := range shop.Sells {
		if e.ID == id {
			unit = e.Price
			break
		}
	}
	if unit < 0 {
		m.sendWorldError(dispatcher, state, userID, "Not for sale here")
		return false
	}
	cost := unit * int64(qty)
	if player.Coins < cost {
		m.sendWorldError(dispatcher, state, userID, "Not enough coins")
		return false
	}
	if shop.Kind == "bugs" && state.Species[id] != nil {
		if player.AddBugs(id, qty) < 0 {
			m.sendWorldError(dispatcher, state, userID, "Bug slots full")
			return false
		}
	} else {
		if player.AddItem(id, qty) < 0 {
			m.sendWorldError(dispatcher, state, userID, "Inventory full")
			return false
		}
	}
	player.Coins -= cost
	return true
}

// shopBuyRecipe: the player learns ONE gated recipe from the shop's `recipes` list. Price is the
// shop's asking Price. No-op (no charge) if already known or the recipe id doesn't exist.
func (m *Match) shopBuyRecipe(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, player *PlayerState, shop *ShopData, id string) bool {
	unit := int64(-1)
	for _, e := range shop.Recipes {
		if e.ID == id {
			unit = e.Price
			break
		}
	}
	if unit < 0 || state.Recipes[id] == nil {
		m.sendWorldError(dispatcher, state, userID, "No such recipe here")
		return false
	}
	if player.KnownRecipes == nil {
		player.KnownRecipes = make(map[string]bool)
	}
	if player.KnownRecipes[id] {
		m.sendWorldError(dispatcher, state, userID, "You already know that recipe")
		return false
	}
	if player.Coins < unit {
		m.sendWorldError(dispatcher, state, userID, "Not enough coins")
		return false
	}
	player.KnownRecipes[id] = true
	player.Coins -= unit
	return true
}

// shopBuyBook: the player buys a "recipe book" — a `books` entry whose ID is a recipe `collection`.
// Learns EVERY recipe sharing that collection at once. No-op (no charge) if the player already knows
// them all or the collection has no recipes.
func (m *Match) shopBuyBook(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, player *PlayerState, shop *ShopData, collection string) bool {
	unit := int64(-1)
	for _, e := range shop.Books {
		if e.ID == collection {
			unit = e.Price
			break
		}
	}
	if unit < 0 {
		m.sendWorldError(dispatcher, state, userID, "No such book here")
		return false
	}
	if player.KnownRecipes == nil {
		player.KnownRecipes = make(map[string]bool)
	}
	// Gather the collection's recipes (deterministic iteration not required — per-player, off-sim).
	learned := 0
	for rid, r := range state.Recipes {
		if r.Collection == collection && !player.KnownRecipes[rid] {
			learned++
		}
	}
	if learned == 0 {
		m.sendWorldError(dispatcher, state, userID, "You already know that book")
		return false
	}
	if player.Coins < unit {
		m.sendWorldError(dispatcher, state, userID, "Not enough coins")
		return false
	}
	for rid, r := range state.Recipes {
		if r.Collection == collection {
			player.KnownRecipes[rid] = true
		}
	}
	player.Coins -= unit
	return true
}

// shopSell: the player sells `id` × qty from their own slot. Payout = the entity's sell_price
// (species.sell_price for live bugs, item sell_price for items). The server verifies the slot
// actually holds `id` (guards a stale client slot) and that the shop buys it.
func (m *Match) shopSell(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, player *PlayerState, shop *ShopData, id string, qty, slot int, slotType string) bool {
	ok, payout, reason := sellLine(state, player, shop, id, qty, slot, slotType)
	if !ok {
		if reason != "" {
			m.sendWorldError(dispatcher, state, userID, reason)
		}
		return false
	}
	player.Coins += payout
	return true
}

// sellLine validates ONE sell line and removes the goods on success, returning the payout WITHOUT
// crediting it (callers credit — the batch sums first, pays once). The single source of truth for
// sell validation: slot must actually hold `id` with at least `qty` (guards a stale client slot),
// and the shop must buy it. qty <= 0 is rejected here — RemoveItem's `Count < count` guard passes
// for a negative count and would GROW the stack.
func sellLine(state *WorldState, player *PlayerState, shop *ShopData, id string, qty, slot int, slotType string) (bool, int64, string) {
	if qty <= 0 {
		return false, 0, "Invalid quantity"
	}

	if slotType == "bug" {
		if shop.Kind != "bugs" {
			return false, 0, "They don't buy bugs"
		}
		if slot < 0 || slot >= len(player.BugSlots) || player.BugSlots[slot].ItemID != id || player.BugSlots[slot].Count < qty {
			return false, 0, "You don't have that"
		}
		sp := state.Species[id]
		if sp == nil {
			return false, 0, "Unknown bug"
		}
		if !player.RemoveBugs(slot, qty) {
			return false, 0, "You don't have that"
		}
		return true, int64(sp.SellPrice) * int64(qty), ""
	}

	// item sell
	if slot < 0 || slot >= len(player.ItemSlots) || player.ItemSlots[slot].ItemID != id || player.ItemSlots[slot].Count < qty {
		return false, 0, "You don't have that"
	}
	def := state.Entities[id]
	if def == nil {
		return false, 0, "Can't sell that"
	}
	if !shopBuysItem(shop, id, def) {
		return false, 0, "They don't buy that"
	}
	if !player.RemoveItem(slot, qty) {
		return false, 0, "You don't have that"
	}
	return true, int64(def.SellPrice) * int64(qty), ""
}

// shopSellBatch: the barter basket — sell every staged line in one transaction (validate each with
// the exact single-sell rules, remove per line, sum, CREDIT ONCE, one FullInventorySync echo via the
// caller). Invalid lines are skipped and reported in one aggregated error; the valid ones still sell.
// Sequential per-line validate+remove makes duplicate-slot lines naturally safe (RemoveItem
// re-validates the live count each time). Idempotent under a double-send: the second pass finds the
// slots already emptied and skips everything.
func (m *Match) shopSellBatch(dispatcher runtime.MatchDispatcher, state *WorldState, userID string, player *PlayerState, shop *ShopData, lines []ShopSellLine) bool {
	const maxBatchLines = 100 // defensive bound; the client basket is far smaller
	if len(lines) == 0 {
		m.sendWorldError(dispatcher, state, userID, "Nothing staged to sell")
		return false
	}
	if len(lines) > maxBatchLines {
		lines = lines[:maxBatchLines]
	}

	var total int64
	sold := 0
	var skipped []string
	for _, ln := range lines {
		qty := ln.Qty
		if qty > 999 {
			qty = 999
		}
		ok, payout, reason := sellLine(state, player, shop, ln.ID, qty, ln.Slot, ln.SlotType)
		if !ok {
			skipped = append(skipped, ln.ID+" ("+strings.ToLower(reason)+")")
			continue
		}
		total += payout
		sold++
	}

	if total > 0 {
		player.Coins += total
	}
	if len(skipped) > 0 {
		m.sendWorldError(dispatcher, state, userID, "Didn't sell: "+strings.Join(skipped, ", "))
	}
	return sold > 0
}

// shopBuysItem reports whether this shop purchases the item: a bug dealer takes any dead_<bug>
// carcass; an item shop takes ids or tags listed in its Buys.
func shopBuysItem(shop *ShopData, id string, def *EntityDef) bool {
	if shop.Kind == "bugs" {
		return strings.HasPrefix(id, "dead_")
	}
	for _, b := range shop.Buys {
		if b == id {
			return true
		}
		for _, t := range def.Tags {
			if t == b {
				return true
			}
		}
	}
	return false
}

// validateShopArbitrage checks the load-time economy invariant: for any good a shop both SELLS and
// BUYS, the buy cost must exceed the sell payout — else the player has an infinite-money pump. Returns
// the offending "<npc>:<id>" strings (empty = clean).
func validateShopArbitrage(state *WorldState) []string {
	var bad []string
	for npcID, def := range state.Entities {
		if def == nil || def.World == nil || def.World.Shop == nil {
			continue
		}
		shop := def.World.Shop
		for _, e := range shop.Sells {
			payout := int64(-1)
			if shop.Kind == "bugs" {
				if sp := state.Species[e.ID]; sp != nil {
					payout = int64(sp.SellPrice) // a live bug it also buys back
				}
			} else if ed := state.Entities[e.ID]; ed != nil && shopBuysItem(shop, e.ID, ed) {
				payout = int64(ed.SellPrice)
			}
			if payout >= 0 && e.Price <= payout {
				bad = append(bad, npcID+":"+e.ID)
			}
		}
	}
	return bad
}
