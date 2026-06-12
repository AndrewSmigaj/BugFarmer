package world

// Unit tests for the cosmetic armor system (handleEquipArmor): equip from an
// inventory slot, slot-mismatch rejection, swap puts the old piece into the
// vacated slot, unequip to inventory, unequip-when-full rejection.
//
// Run inside the builder image:  go test ./modules/world/ -run 'TestEquip' -v

import (
	"testing"

	"github.com/heroiclabs/nakama-common/runtime"
)

func equipTestState() *WorldState {
	state := newTestState(50)
	state.Players = map[string]*PlayerState{}
	state.Presences = map[string]runtime.Presence{}
	state.Entities = map[string]*EntityDef{
		"leather_cap":   {Category: "armor", ArmorSlot: "head"},
		"iron_helmet":   {Category: "armor", ArmorSlot: "head"},
		"leather_chest": {Category: "armor", ArmorSlot: "body"},
		"bee_charm":     {Category: "armor", ArmorSlot: "accessory"},
		"sword_wood":    {Category: "tool", ToolType: "sword"},
	}
	return state
}

func TestEquipFromInventory(t *testing.T) {
	state := equipTestState()
	p := testPlayer(10, 10, "")
	p.ItemSlots[3] = InventorySlot{ItemID: "iron_helmet", Count: 1}
	state.Players["p1"] = p

	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 0, InvSlot: 3})

	if p.Equipment[0] != "iron_helmet" {
		t.Fatalf("head = %q, want iron_helmet", p.Equipment[0])
	}
	if p.ItemSlots[3].ItemID != "" {
		t.Fatalf("inv slot 3 still holds %q, want empty", p.ItemSlots[3].ItemID)
	}
}

func TestEquipSlotMismatchRejected(t *testing.T) {
	state := equipTestState()
	p := testPlayer(10, 10, "")
	p.ItemSlots[3] = InventorySlot{ItemID: "leather_chest", Count: 1}
	state.Players["p1"] = p

	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 0, InvSlot: 3}) // chest into HEAD

	if p.Equipment[0] != "" || p.ItemSlots[3].ItemID != "leather_chest" {
		t.Fatalf("mismatch equipped anyway: head=%q inv=%q", p.Equipment[0], p.ItemSlots[3].ItemID)
	}
}

func TestEquipNonArmorRejected(t *testing.T) {
	state := equipTestState()
	p := testPlayer(10, 10, "")
	p.ItemSlots[0] = InventorySlot{ItemID: "sword_wood", Count: 1}
	state.Players["p1"] = p

	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 0, InvSlot: 0})

	if p.Equipment[0] != "" {
		t.Fatalf("equipped a sword on the head: %q", p.Equipment[0])
	}
}

func TestEquipSwapUsesVacatedSlot(t *testing.T) {
	state := equipTestState()
	p := testPlayer(10, 10, "")
	p.Equipment[0] = "leather_cap"
	p.ItemSlots[5] = InventorySlot{ItemID: "iron_helmet", Count: 1}
	// fill EVERY other slot: the swap must not need a free one
	for i := range p.ItemSlots {
		if i != 5 && p.ItemSlots[i].ItemID == "" {
			p.ItemSlots[i] = InventorySlot{ItemID: "wood", Count: 1}
		}
	}
	state.Players["p1"] = p

	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 0, InvSlot: 5})

	if p.Equipment[0] != "iron_helmet" {
		t.Fatalf("head = %q, want iron_helmet", p.Equipment[0])
	}
	if p.ItemSlots[5].ItemID != "leather_cap" {
		t.Fatalf("vacated slot holds %q, want leather_cap (the swap target)", p.ItemSlots[5].ItemID)
	}
}

func TestUnequipToInventoryAndFullRejection(t *testing.T) {
	state := equipTestState()
	p := testPlayer(10, 10, "")
	p.Equipment[1] = "leather_chest"
	state.Players["p1"] = p

	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 1, InvSlot: -1})

	if p.Equipment[1] != "" {
		t.Fatalf("body still %q after unequip", p.Equipment[1])
	}
	found := false
	for _, s := range p.ItemSlots {
		if s.ItemID == "leather_chest" {
			found = true
		}
	}
	if !found {
		t.Fatal("unequipped piece not in inventory")
	}

	// now FULL: unequip must reject and keep the piece worn
	p.Equipment[0] = "leather_cap"
	for i := range p.ItemSlots {
		if p.ItemSlots[i].ItemID == "" {
			p.ItemSlots[i] = InventorySlot{ItemID: "wood", Count: 1}
		}
	}
	(&Match{}).handleEquipArmor(nopRuntimeLogger(), nopDispatcher{}, state, "p1",
		EquipArmorMessage{EquipSlot: 0, InvSlot: -1})
	if p.Equipment[0] != "leather_cap" {
		t.Fatalf("full-inventory unequip removed the piece: head=%q", p.Equipment[0])
	}
}
