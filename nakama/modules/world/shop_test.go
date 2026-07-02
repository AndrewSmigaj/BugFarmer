package world

import "testing"

// shopTestState: a player at p1 with coins, plus item/species defs the shops reference.
func shopTestState() (*WorldState, *PlayerState) {
	state := newTestState(50)
	state.Players = map[string]*PlayerState{}
	state.Entities = map[string]*EntityDef{
		"seed_tomato": {Category: "seed", BuyPrice: 10, SellPrice: 2},
		"tomato":      {Category: "resource", SellPrice: 5, Tags: []string{"crop"}},
		"wood":        {Category: "resource", SellPrice: 2, Tags: []string{"material"}},
		"dead_fly":    {Category: "resource", SellPrice: 1},
	}
	state.Species["fly_common"].SellPrice = 7 // live fly is worth 7
	p := testPlayer(0, 0, "")
	state.Players["p1"] = p
	return state, p
}

func itemShop() *ShopData {
	return &ShopData{Kind: "items", Sells: []ShopEntry{{ID: "seed_tomato", Price: 10}}, Buys: []string{"crop", "material"}}
}
func bugShop() *ShopData {
	return &ShopData{Kind: "bugs", Sells: []ShopEntry{{ID: "fly_common", Price: 20}}}
}

func TestShopBuyItem(t *testing.T) {
	state, p := shopTestState()
	p.Coins = 25
	if !(&Match{}).shopBuy(nopDispatcher{}, state, "p1", p, itemShop(), "seed_tomato", 2) {
		t.Fatal("buy should succeed")
	}
	if p.Coins != 5 {
		t.Fatalf("coins: want 5, got %d", p.Coins)
	}
	if p.FindItem("seed_tomato") < 0 || p.ItemSlots[p.FindItem("seed_tomato")].Count != 2 {
		t.Fatalf("expected 2 seed_tomato in inventory")
	}
}

func TestShopBuyInsufficientCoins(t *testing.T) {
	state, p := shopTestState()
	p.Coins = 5 // price is 10
	if (&Match{}).shopBuy(nopDispatcher{}, state, "p1", p, itemShop(), "seed_tomato", 1) {
		t.Fatal("buy should fail (too poor)")
	}
	if p.Coins != 5 || p.FindItem("seed_tomato") >= 0 {
		t.Fatalf("nothing should change: coins=%d", p.Coins)
	}
}

func TestShopBuyInventoryFullNoDeduct(t *testing.T) {
	state, p := shopTestState()
	p.Coins = 100
	p.ItemSlotsUnlocked = 1
	p.ItemSlots[0] = InventorySlot{ItemID: "wood", Count: 1} // only slot, occupied by a different item
	if (&Match{}).shopBuy(nopDispatcher{}, state, "p1", p, itemShop(), "seed_tomato", 1) {
		t.Fatal("buy should fail (inventory full)")
	}
	if p.Coins != 100 {
		t.Fatalf("coins must NOT be deducted on a failed buy: got %d", p.Coins)
	}
}

func TestShopBuyNotForSale(t *testing.T) {
	state, p := shopTestState()
	p.Coins = 100
	if (&Match{}).shopBuy(nopDispatcher{}, state, "p1", p, itemShop(), "tomato", 1) {
		t.Fatal("buy should fail (not in sells list)")
	}
}

func TestShopSellItem(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[3] = InventorySlot{ItemID: "tomato", Count: 4}
	if !(&Match{}).shopSell(nopDispatcher{}, state, "p1", p, itemShop(), "tomato", 3, 3, "item") {
		t.Fatal("sell should succeed (crop tag bought)")
	}
	if p.Coins != 15 { // 3 × sell_price 5
		t.Fatalf("coins: want 15, got %d", p.Coins)
	}
	if p.ItemSlots[3].Count != 1 {
		t.Fatalf("expected 1 tomato left, got %d", p.ItemSlots[3].Count)
	}
}

func TestShopSellNotOwnedRejected(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[3] = InventorySlot{ItemID: "wood", Count: 1} // slot holds wood, client claims tomato
	if (&Match{}).shopSell(nopDispatcher{}, state, "p1", p, itemShop(), "tomato", 1, 3, "item") {
		t.Fatal("sell must reject a stale/mismatched slot")
	}
	if p.Coins != 0 {
		t.Fatalf("no payout on a rejected sell: got %d", p.Coins)
	}
}

func TestShopSellItemNotBought(t *testing.T) {
	state, p := shopTestState()
	// itemShop buys crop/material; seed_tomato has neither tag → refused
	p.ItemSlots[0] = InventorySlot{ItemID: "seed_tomato", Count: 1}
	if (&Match{}).shopSell(nopDispatcher{}, state, "p1", p, itemShop(), "seed_tomato", 1, 0, "item") {
		t.Fatal("sell should fail (shop doesn't buy seeds)")
	}
}

func TestShopSellLiveBug(t *testing.T) {
	state, p := shopTestState()
	p.BugSlots[2] = InventorySlot{ItemID: "fly_common", Count: 3}
	if !(&Match{}).shopSell(nopDispatcher{}, state, "p1", p, bugShop(), "fly_common", 2, 2, "bug") {
		t.Fatal("bug dealer should buy a live fly")
	}
	if p.Coins != 14 { // 2 × species sell_price 7
		t.Fatalf("coins: want 14, got %d", p.Coins)
	}
	if p.BugSlots[2].Count != 1 {
		t.Fatalf("expected 1 fly left, got %d", p.BugSlots[2].Count)
	}
}

func TestShopSellBugToItemShopRejected(t *testing.T) {
	state, p := shopTestState()
	p.BugSlots[0] = InventorySlot{ItemID: "fly_common", Count: 1}
	if (&Match{}).shopSell(nopDispatcher{}, state, "p1", p, itemShop(), "fly_common", 1, 0, "bug") {
		t.Fatal("an item shop must not buy live bugs")
	}
}

func TestShopSellDeadBugToDealer(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[0] = InventorySlot{ItemID: "dead_fly", Count: 1}
	if !(&Match{}).shopSell(nopDispatcher{}, state, "p1", p, bugShop(), "dead_fly", 1, 0, "item") {
		t.Fatal("bug dealer should buy dead_<bug> items")
	}
	if p.Coins != 1 {
		t.Fatalf("coins: want 1, got %d", p.Coins)
	}
}

func TestShopSellBatchMixed(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[3] = InventorySlot{ItemID: "tomato", Count: 4}
	p.ItemSlots[5] = InventorySlot{ItemID: "wood", Count: 2}
	p.ItemSlots[7] = InventorySlot{ItemID: "seed_tomato", Count: 1} // shop doesn't buy seeds
	lines := []ShopSellLine{
		{SlotType: "item", Slot: 3, ID: "tomato", Qty: 3},      // valid → 15
		{SlotType: "item", Slot: 5, ID: "wood", Qty: 2},        // valid → 4
		{SlotType: "item", Slot: 7, ID: "seed_tomato", Qty: 1}, // refused (not bought)
		{SlotType: "item", Slot: 9, ID: "tomato", Qty: 1},      // stale: slot 9 is empty
	}
	if !(&Match{}).shopSellBatch(nopDispatcher{}, state, "p1", p, itemShop(), lines) {
		t.Fatal("batch with valid lines should report a change")
	}
	if p.Coins != 19 { // 3×5 + 2×2
		t.Fatalf("coins: want 19, got %d", p.Coins)
	}
	if p.ItemSlots[3].Count != 1 {
		t.Fatalf("expected 1 tomato left, got %d", p.ItemSlots[3].Count)
	}
	if p.ItemSlots[5].ItemID != "" {
		t.Fatalf("wood slot should be empty, holds %q", p.ItemSlots[5].ItemID)
	}
	if p.ItemSlots[7].Count != 1 || p.ItemSlots[7].ItemID != "seed_tomato" {
		t.Fatal("refused line must leave the slot untouched")
	}
}

func TestShopSellBatchDuplicateSlotNoDoublePayout(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[3] = InventorySlot{ItemID: "tomato", Count: 4}
	lines := []ShopSellLine{
		{SlotType: "item", Slot: 3, ID: "tomato", Qty: 3}, // sells → 15, leaves 1
		{SlotType: "item", Slot: 3, ID: "tomato", Qty: 3}, // re-validates live count (1 < 3) → skipped
	}
	if !(&Match{}).shopSellBatch(nopDispatcher{}, state, "p1", p, itemShop(), lines) {
		t.Fatal("first line should sell")
	}
	if p.Coins != 15 {
		t.Fatalf("duplicate-slot line must not double-pay: want 15, got %d", p.Coins)
	}
	if p.ItemSlots[3].Count != 1 {
		t.Fatalf("expected 1 tomato left, got %d", p.ItemSlots[3].Count)
	}
}

func TestShopSellBatchNegativeQtyRejected(t *testing.T) {
	state, p := shopTestState()
	p.ItemSlots[0] = InventorySlot{ItemID: "wood", Count: 5}
	lines := []ShopSellLine{
		{SlotType: "item", Slot: 0, ID: "wood", Qty: -5}, // the duplication exploit: must NOT grow the stack
	}
	if (&Match{}).shopSellBatch(nopDispatcher{}, state, "p1", p, itemShop(), lines) {
		t.Fatal("a batch of only invalid lines must report no change")
	}
	if p.ItemSlots[0].Count != 5 {
		t.Fatalf("negative qty must not change the stack: want 5, got %d", p.ItemSlots[0].Count)
	}
	if p.Coins != 0 {
		t.Fatalf("no payout for a rejected line: got %d", p.Coins)
	}
}

func TestShopSellBatchBugDealer(t *testing.T) {
	state, p := shopTestState()
	p.BugSlots[2] = InventorySlot{ItemID: "fly_common", Count: 3}
	p.ItemSlots[0] = InventorySlot{ItemID: "dead_fly", Count: 1}
	p.ItemSlots[1] = InventorySlot{ItemID: "wood", Count: 1} // dealer only buys dead_*
	lines := []ShopSellLine{
		{SlotType: "bug", Slot: 2, ID: "fly_common", Qty: 2}, // live bugs → 14
		{SlotType: "item", Slot: 0, ID: "dead_fly", Qty: 1},  // carcass → 1
		{SlotType: "item", Slot: 1, ID: "wood", Qty: 1},      // refused
	}
	if !(&Match{}).shopSellBatch(nopDispatcher{}, state, "p1", p, bugShop(), lines) {
		t.Fatal("bug-dealer batch should sell the bug + carcass lines")
	}
	if p.Coins != 15 { // 2×7 + 1×1
		t.Fatalf("coins: want 15, got %d", p.Coins)
	}
	if p.BugSlots[2].Count != 1 {
		t.Fatalf("expected 1 fly left, got %d", p.BugSlots[2].Count)
	}
	if p.ItemSlots[0].ItemID != "" {
		t.Fatal("dead_fly should be sold")
	}
	if p.ItemSlots[1].Count != 1 {
		t.Fatal("refused wood line must leave the slot untouched")
	}
}

func TestShopArbitrageInvariant(t *testing.T) {
	state, _ := shopTestState()
	// Clean: dealer sells fly at 20, buys back at 7 → fine.
	state.Entities["bug_dealer"] = &EntityDef{World: &WorldData{Shop: bugShop()}}
	if bad := validateShopArbitrage(state); len(bad) != 0 {
		t.Fatalf("clean shops flagged: %v", bad)
	}
	// Broken: a shop that SELLS tomato for 1 but BUYS crops at sell_price 5 → infinite money.
	state.Entities["bad_shop"] = &EntityDef{World: &WorldData{Shop: &ShopData{
		Kind: "items", Sells: []ShopEntry{{ID: "tomato", Price: 1}}, Buys: []string{"crop"},
	}}}
	bad := validateShopArbitrage(state)
	if len(bad) != 1 || bad[0] != "bad_shop:tomato" {
		t.Fatalf("arbitrage not caught: %v", bad)
	}
}
