# Inventory & Shop System Architecture

## Overview

Terraria-inspired system: hotbar for tools, separate bug collection, simple buy/sell shop.

---

## Visual Layout

```
GAMEPLAY:
+-------------------------------------------------------------------+
|                         GAME WORLD                                 |
|                                                                    |
|                              +5 flies <- catch popup               |
|                                                                    |
+--------------------------------------------------------------------+
|  [N1][N1][SP][ ][ ][ ][ ][ ][ ][ ]         $ 1,234                 |
|   ^net selected                              Coins                 |
|              HOTBAR (tools only)                                   |
+--------------------------------------------------------------------+

INVENTORY (I key):
+--------------------------------------------------------------------+
|  +--- TOOLS (2x5 grid) --+  +--- BUGS (4x5 grid) ----------+      |
|  | [N1][N1][SP][ ][ ]    |  | [F99][F50][A89][B12][ ]      |      |
|  | [  ][  ][  ][  ][  ]  |  | [   ][   ][   ][   ][   ]    |      |
|  |                       |  | [   ][   ][   ][   ][   ]    |      |
|  |                       |  | [   ][   ][   ][   ][   ]    |      |
|  +-----------------------+  +------------------------------+      |
|                                                                    |
|  [N1][N1][SP][ ][ ][ ][ ][ ][ ][ ]         $ 1,234                 |
|   1   2   3  4  5  6  7  8  9  0           ^coins                  |
+--------------------------------------------------------------------+
  Right-click = split stack | Drag outside = release bugs

SHOP (at NPC):
+--------------------------------------------------------------------+
|  +--- SHOP (Buy) ------+  +--- YOUR BUGS (Sell) -------------+    |
|  | [Net      50$]      |  | [F99][F50][A89][B12][ ]          |    |
|  | [Spray    10$]      |  | [   ][   ][   ][   ][   ]        |    |
|  |                     |  |     Click slot to sell           |    |
|  +---------------------+  +----------------------------------+    |
|                                                                    |
|  [N1][N1][SP][ ][ ][ ][ ][ ][ ][ ]         $ 1,234                 |
+--------------------------------------------------------------------+
  Click bug slot -> Sell dialog (1 / Half / All / Cancel)
```

---

## Core Rules

1. **Hotbar = Tools Only** - Nets, sprays, etc. Never bugs.
2. **Bugs Auto-Collect** - Caught bugs go directly to bug inventory
3. **Catch Popup** - "+5 flies" floats up when catching
4. **Simple Shop** - Click slot to open quantity dialog
5. **Stack Splitting** - All items (bugs and tools) support Terraria-style splitting
6. **Infinite Stacks** - No stack size limits. A single slot can hold millions.

---

## Stack Splitting (Terraria-Style)

All inventory items support splitting:

### Interactions

**Left-click (entire stacks):**
- Click item while cursor empty -> Pick up entire stack
- Click empty slot while holding -> Drop entire stack
- Click same-item slot while holding -> Merge stacks (no limit, all merge)
- Click different-item slot while holding -> Swap cursor and slot

**Right-click (half stacks):**
- Click item while cursor empty -> Pick up half (rounded up)
- Click empty slot while holding -> Drop half into slot
- Click same-item slot while holding -> Add half to slot
- Click different-item slot while holding -> Do nothing

**Shift+click** -> Quick-stack to first matching/empty slot in other panel

### Multiple Stacks
- Same item type can occupy multiple slots
- Example: 3 stacks of flies (100, 50, 23) in bug inventory
- Caught bugs add to first available stack or create new slot

### Release Bugs
- Drag bug stack outside inventory window -> Release dialog
- Or right-click bug stack -> Context menu with "Release" option
- Quantity selector: Release 1 / Release Half / Release All / Cancel
- **Released bugs form swarms automatically:**
  - Server creates swarm(s) at player position
  - If count > max_swarm_size, creates multiple swarms
  - Existing merge mechanics handle combining nearby swarms naturally

### Visual
```
BUG INVENTORY (grid slots, not list):
+----+----+----+----+----+
| F  | F  | A  | B  |    |
|x100|x50 |x89 |x12 |    |
+----+----+----+----+----+
|    |    |    |    |    |
|    |    |    |    |    |
+----+----+----+----+----+
       ^ same species, different stacks
```

---

## Data Model

### Slot-Based Inventory

Instead of `map[species]count`, use slots that can each hold an item stack:

### Server (Go)

```go
// InventorySlot holds one stack of items
type InventorySlot struct {
    ItemID string `json:"item_id"` // species_id for bugs, item_id for tools
    Count  int    `json:"count"`
}

type PlayerState struct {
    // Existing
    Position      EntityPosition
    Facing        Direction
    EquippedTool  string
    LastCatchTime int64

    // New - Slot-based inventory
    Coins     int64              // Currency
    BugSlots  [20]InventorySlot  // Bug inventory (20 slots, fixed size)
    ItemSlots [10]InventorySlot  // Tool/hotbar inventory (10 slots = hotbar)
    // NOTE: No separate Hotbar binding - ItemSlots[0..9] ARE the hotbar
}

// AddBugs finds existing stack or empty slot, returns slot index modified (-1 if full)
func (p *PlayerState) AddBugs(speciesID string, count int) int

// RemoveBugs removes from specific slot, returns true if successful
func (p *PlayerState) RemoveBugs(slotIndex int, count int) bool

// MoveSlot moves/swaps between slots, handles splitting
func (p *PlayerState) MoveSlot(srcType string, srcIdx int, dstType string, dstIdx int, count int) bool
```

### Client (C#)

```csharp
[Serializable]
public class InventorySlot
{
    public string itemId;  // species_id or item_id, "" = empty
    public int count;
}

public class InventoryManager : MonoBehaviour
{
    // Slot-based inventories (synced from server)
    public InventorySlot[] BugSlots { get; private set; } = new InventorySlot[20];
    public InventorySlot[] ItemSlots { get; private set; } = new InventorySlot[10];
    // NOTE: ItemSlots[0..9] ARE the hotbar - no separate binding

    // Currency
    public long Coins { get; private set; }

    // Currently selected hotbar slot (0-9)
    public int SelectedSlot { get; private set; }

    // Cursor item (for drag/split operations, client-side only)
    public InventorySlot CursorItem { get; private set; }

    // Events
    public event Action<int> OnBugSlotChanged;   // slot index
    public event Action<int> OnItemSlotChanged;  // slot index
    public event Action OnCoinsChanged;
}
```

---

## Hotbar Behavior

**Key insight:** ItemSlots[0..9] ARE the hotbar. No separate binding needed.
- Hotbar slot 1 = ItemSlots[0]
- Hotbar slot 2 = ItemSlots[1]
- ...
- Hotbar slot 0 = ItemSlots[9]

### Selection (1-9, 0 keys or scroll)
1. Select slot index (keys 1-9 = index 0-8, key 0 = index 9)
2. If ItemSlots[index] has tool -> Send `EquipTool` message with item_id
3. If ItemSlots[index] empty -> Send `EquipTool` with empty string (unequip)

### Rearranging
- Drag tool between hotbar slots = swap ItemSlots positions
- Same as rearranging in inventory panel (they show the same data)

### Tool Stats (from items.json - must create this file)
```json
{
  "small_net": {
    "name": "Small Net",
    "reach": 4.5,
    "catch_radius": 1.5,
    "buy_price": 0,
    "sell_price": 25
  },
  "large_net": {
    "name": "Large Net",
    "reach": 5.5,
    "catch_radius": 2.5,
    "buy_price": 100,
    "sell_price": 50
  },
  "calm_spray": {
    "name": "Calm Spray",
    "reach": 3.0,
    "effect": "calm",
    "buy_price": 20,
    "sell_price": 10
  }
}
```

---

## Catch Feedback

When player catches bugs:

1. Server sends `BugSlotUpdate` (OpCode 26)
2. Client shows floating popup: "+5 flies"
3. Popup fades out after 1-2 seconds
4. Position: Above player's head or near catch location

```csharp
public class CatchPopup : MonoBehaviour
{
    public void Show(string speciesName, int count)
    {
        text.text = $"+{count} {speciesName}";
        StartCoroutine(FadeAndRise());
    }
}
```

---

## Shop System

### Opening Shop
1. Player near NPC (< 3 blocks), presses E
2. Client sends `OpenShop` (OpCode 30)
3. Server validates proximity
4. Server sends `ShopOpened` with buy prices + sell prices

### Shop Layout
- **Left Panel: Shop Inventory (Buy)**
  - Items NPC sells (nets, sprays)
  - Price shown, click to buy

- **Right Panel: Your Bugs (Sell)**
  - Your bug slots (same grid as inventory)
  - Click slot -> quantity dialog -> sell

### Selling Flow
1. Player clicks bug slot in shop
2. Quantity dialog: 1 / Half / All / Cancel
3. Client sends `SellItems` with slot_index, quantity
4. Server validates, processes
5. Server sends `SellResult` + `BugSlotUpdate`
6. "+523$" popup, coins HUD updates

### Buying Flow
1. Player clicks "Buy" on Large Net
2. Client sends `BuyItem` (OpCode 36)
3. Server checks coins, adds item to first empty ItemSlot
4. Server sends `ItemSlotUpdate` + `CurrencyUpdate`

---

## Network Messages

### OpCodes

| OpCode | Direction | Name | Description |
|--------|-----------|------|-------------|
| 26 | S->C | BugSlotUpdate | Single bug slot changed |
| 27 | C->S | EquipTool | Equip tool (existing) |
| 28 | C->S | MoveSlot | Move/swap items between slots |
| 29 | C->S | ReleaseBugs | Release bugs from slot |
| 30 | C->S | OpenShop | Request shop |
| 31 | S->C | ShopOpened | Shop data + prices |
| 32 | C->S | SellItems | Sell bugs from slot |
| 33 | S->C | SellResult | Transaction result |
| 34 | S->C | CurrencyUpdate | Coins changed |
| 35 | S->C | NPCUpdate | NPC positions |
| 36 | C->S | BuyItem | Buy from shop |
| 37 | S->C | ItemSlotUpdate | Single item slot changed |
| 38 | S->C | FullInventorySync | Complete state on join |
| 40 | S->C | ErrorMessage | Operation failed (insufficient funds, etc.) |

### Message Structs

```csharp
// === Slot Operations ===

// Move/swap items between slots (OpCode 28)
[Serializable] public class MoveSlotMessage
{
    public string source_type;  // "bug" or "item"
    public int source_index;
    public string dest_type;    // "bug" or "item"
    public int dest_index;
    public int count;           // -1 = all, else specific amount
}

// Release bugs (OpCode 29)
[Serializable] public class ReleaseBugsMessage
{
    public int slot_index;
    public int count;  // -1 = all
}

// Slot update from server (OpCode 26 for bugs, 37 for items)
[Serializable] public class SlotUpdateMessage
{
    public int slot_index;
    public string item_id;  // "" = empty slot
    public int count;
}

// === Shop ===

[Serializable] public class OpenShopMessage { public string npc_id; }

[Serializable] public class ShopOpenedMessage
{
    public string npc_id;
    public string npc_name;
    public ShopItem[] for_sale;    // Items to buy
    public PriceInfo[] sell_prices; // Bug sell prices
}

[Serializable] public class ShopItem
{
    public string item_id;
    public string name;
    public int price;
    public int stock; // -1 = unlimited
}

[Serializable] public class PriceInfo
{
    public string species_id;
    public string name;
    public int sell_price;
}

// Transactions
[Serializable] public class SellItemsMessage
{
    public string npc_id;
    public int slot_index;  // Which bug slot to sell from
    public int quantity;    // -1 = all
}

[Serializable] public class BuyItemMessage
{
    public string npc_id;
    public string item_id;
    public int quantity;
}

[Serializable] public class SellResultMessage
{
    public bool success;
    public int quantity_sold;
    public long coins_earned;
    public long new_balance;
    public string error;
}

// Full inventory sync on join (OpCode 38)
[Serializable] public class FullInventorySyncMessage
{
    public InventorySlot[] bug_slots;   // All 20 bug slots
    public InventorySlot[] item_slots;  // All 10 item slots (= hotbar)
    public long coins;
}

// Error message (OpCode 40)
[Serializable] public class ErrorMessage
{
    public int related_opcode;  // Which operation failed
    public string error_code;   // "INSUFFICIENT_FUNDS", "INVALID_SLOT", "SHOP_CLOSED"
    public string message;      // Human-readable error
}
```

---

## Implementation Phases

### Phase 3a: Core Inventory System
1. Create `nakama/data/items.json` with tool definitions
2. Server: Add `InventorySlot`, slot arrays to `PlayerState`
3. Server: Add helper methods (AddBugs, RemoveBugs, MoveSlot)
4. Server: Give new players 1x Small Net in ItemSlots[0]
5. Server: Send `FullInventorySync` on player join
6. Client: Create `InventorySlot` class
7. Client: Update `InventoryManager` with slot arrays
8. Client: Handle `FullInventorySync` message

### Phase 3b: Hotbar UI
1. Create `HotbarUI.cs` - 10 slots at bottom of screen
2. Create `InventorySlotUI.cs` - reusable slot component
3. 1-9, 0 key selection + scroll wheel
4. Connect to existing `EquipTool` message
5. Save selected slot index locally (PlayerPrefs)

### Phase 3c: Inventory Panel + Slot Operations
1. Create `InventoryPanel.cs` - toggle with I key
2. Tools grid (2x5) + Bugs grid (4x5)
3. Implement drag & drop between slots
4. Right-click to split (pick up half)
5. Send `MoveSlot` to server, handle slot updates

### Phase 3d: Bug Catching Integration
1. Update server catch handler to use AddBugs()
2. Send `BugSlotUpdate` after catch
3. Create `CatchPopup.cs` - floating "+5 flies" text
4. Track slot changes to calculate delta for popup

### Phase 3e: Release Bugs
1. Drag bug slot outside inventory -> release dialog
2. Create `QuantityDialog.cs` - 1 / Half / All / Cancel
3. Send `ReleaseBugs` message
4. Server removes from slot, sends update

### Phase 3f: Currency System
1. Add `Coins` to `PlayerState` (server)
2. Send coins in `FullInventorySync`
3. Add OpCode 34 `CurrencyUpdate`
4. Create `CoinsHUD.cs` at top-right

### Phase 3g: NPC System
1. Add `NPCState` to server
2. Spawn shop NPC at fixed location
3. Create `NPCController.cs` - E to interact
4. Proximity prompt "Press E to Shop"

### Phase 3h: Shop Panel
1. Create `ShopPanel.cs` - two-panel layout
2. Buy panel: List items, click to buy
3. Sell panel: Show bug slots, click to sell
4. Implement buy/sell message handlers
5. Use `QuantityDialog` for sell amounts

---

## Files Summary

### New Client Files (11)

| Path | Purpose |
|------|---------|
| `Scripts/UI/HotbarUI.cs` | Hotbar controller |
| `Scripts/UI/InventorySlotUI.cs` | Reusable slot component |
| `Scripts/UI/InventoryPanel.cs` | Full inventory panel |
| `Scripts/UI/ShopPanel.cs` | Buy/sell UI |
| `Scripts/UI/CatchPopup.cs` | "+5 flies" floating text |
| `Scripts/UI/CoinsHUD.cs` | Currency display |
| `Scripts/UI/QuantityDialog.cs` | 1/Half/All selector |
| `Scripts/Entities/NPCManager.cs` | NPC spawning |
| `Scripts/Entities/NPCController.cs` | NPC interaction |
| `Scripts/Networking/ShopMessages.cs` | Shop OpCodes & messages |
| `Scripts/Networking/InventoryMessages.cs` | Slot operation messages |

### New Server Files (2)

| Path | Purpose |
|------|---------|
| `nakama/modules/world/inventory.go` | Slot helpers, sync logic |
| `nakama/modules/world/shop.go` | Transaction logic |

### Modified Files (5)

| Path | Changes |
|------|---------|
| `nakama/modules/world/state.go` | Add InventorySlot, slot arrays, Coins |
| `nakama/modules/world/messages.go` | Add OpCodes 28-38, slot messages |
| `nakama/modules/world/match.go` | Handle inventory/shop messages |
| `Scripts/UI/InventoryManager.cs` | Slot arrays, cursor item, events |
| `Scripts/Networking/BugMessages.cs` | Update to slot-based messages |

### Data Files

- `nakama/data/items.json` - **NEW** - Tool definitions (reach, radius, price)
- `nakama/data/species.json` - Already has `sell_price`

---

## Starting State

New player:
- 1x Small Net in ItemSlots[0] (hotbar slot 1)
- 0 coins
- Empty BugSlots
- Selected slot = 0 (auto-equips small net)

---

## Future: Persistence (Phase 4)

Not in scope for Phase 3, but needed eventually:
- Save inventory to Nakama storage on disconnect
- Load inventory on MatchJoin
- Periodic auto-save (every 60 seconds)
- Currently: inventory resets each session
