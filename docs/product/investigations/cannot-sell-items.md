# Investigation: #5 unable to sell items
_status: ✅ FIXED 2026-07-02 (barter sell) · was: LIVE-CONFIRMED — the sell flow, not the open · investigate-only doc_

> **FIX SHIPPED (2026-07-02):** the recommended fix below was built as the full **Apico barter sell** —
> stage stacks from your REAL inventory into a basket → one atomic "Sell for Xc" (`sell_batch` server op),
> a **"Buys: …"** header + client-side stage filter mirroring `shopBuysItem`, and a shop status line that
> surfaces OpCode-40 server errors (both feedback gaps below closed). See architecture_inventory.md STATUS
> + DECISIONS D29. Pending: the in-Editor confirm (incl. the bug-dealer live-bug sell).

## ★ Live confirm (Andrew, 2026-06-28)
The NPC dialogue + shop panel **open fine** → **NOT the OverlapPoint bug** (§3A falsified). Clicking sell
slots "doesn't do anything", with **no indicator of what the NPC would buy**; the **bug vendor can't sell bugs
by any click/drag**. So it's the **sell flow + a missing-feedback UX gap**, root-caused below (§3B confirmed).

## Real root cause (post-confirm)
The whole sell pipeline is correctly wired (slot click `InventorySlotUI.OnPointerClick → OnSlotClicked →
Send("sell",…) → OpCode 2 → `match.go:1025 handleShopAction` → `shopSell`; species have sell_price). The break
is **feedback + filtering**, two parts:
1. **No rejection is surfaced.** `shopSell` rejects with `sendWorldError` ("They don't buy that" / "You don't
   have that"), but the client has **no UI that shows server world-errors while the shop is open** (WorldManager
   only `Debug.LogError`s connection failures). So a rejected sell = visibly nothing happens.
2. **No "what it buys" indicator.** Each NPC only buys a filtered set — general store buys `material`/`food`
   **tags** (`shopBuysItem` tag match); the **bug dealer (kind "bugs") buys only live bugs (BugSlots) + items
   prefixed `dead_`** (`shopBuysItem` returns `HasPrefix("dead_")`). The Sell column shows ALL your sellable-priced
   items with no hint which the NPC accepts, so clicking a non-accepted item silently rejects (part 1).
- **Bug vendor specifically:** live-bug sell IS coded (`shopSell` "bug" branch sells at `species.SellPrice`,
  prices exist). If it truly does nothing, the fast check is the **Unity console on a bug-sell click**: a logged
  world-error ("…") ⇒ it's reaching the server (feedback bug); total silence ⇒ the click/slot isn't firing for
  bug slots (a slot-build/raycast issue to chase). **This one console check pins it.**

## Recommended fix (post-confirm)
1. **Surface shop results** — on a sell, show "Sold N for Xc" (success) or the server's reason (failure) in/over
   the ShopPanel. The server already sends the error + an inventory sync; the panel just needs to display it.
2. **Show each NPC's Buys** — a "Buys: material, food" header + **grey/disable un-accepted items** in the Sell
   column (so you only click sellable ones). For the bug dealer, label it "Buys: bugs & carcasses."
3. Confirm the bug-sell with the console check above; if the click isn't firing for bug slots, inspect the
   bug-slot build in `BuildSell` (kind=="bugs" branch).
- Determinism: none.

## Debrief (read me first — original pre-confirm analysis below)
- **TL;DR:** The sell system is **fully implemented** end-to-end (client Sell UI + server `shopSell`). The
  user-facing break is almost certainly **opening the shop**, not selling: every right-click interaction
  resolves its target with a single `Physics2D.OverlapPoint` that returns ONE arbitrary collider among
  overlapping occupants, with **no topmost-wins rule** — and NPCs stand in front of their storefronts (sprite
  bounds overlap the building), so the click can land on the building (not a "shop") and the dialogue never
  opens. "tried clicking in different ways" fits this exactly.
- **Shared root cause** with #18 (break-behind-tree) and likely #14/#10/#4/#12 — see the cross-cutting note.
- **Recommended fix:** replace the single `OverlapPoint` with `OverlapPointAll` + pick the **topmost
  interactable** occupant (highest sprite sorting order / nearest anchor / prefer the handler's own
  interaction_type) — one shared helper used by all right-click handlers + BreakingController. Fixes the cluster.
- **Certainty:** sell-system-works **95%** · open-shop-is-the-cause **70%** (vs. the secondary modes below) ·
  shared-with-#18 **90%**. **Needs your decision/confirm:** does the BG-style **dialogue actually open** when you
  right-click an NPC? (If yes → it's the sell step, see §4B; if no/intermittent → it's the OverlapPoint resolution.)
- **Status:** `BLOCKED ON: one live confirm` (then `READY` — the fix is clear either way).

## 1. Issue & evidence
> "unable to sell items (at least clicking in different ways) and haven't tried buying as I have no money as I can't sell yet"
- Acceptance: clicking sell on an item at a shop transfers it + grants coins.

## 2. The system is fully wired (verified)
- **Client:** right-click a `"shop"` occupant → `ShopPanel.TryHandleRightClick` (`ShopPanel.cs:92`) → BG-style
  dialogue → [Trade] → board with a **Sell** column (`BuildSell:253`). A Sell slot is built for every inventory
  item with `sell_price>0` (`:263`); clicking sends `Send("sell", id, slotType, slot)` (`:269`) →
  `ShopActionMessage{gx=_cell.x, gy=_cell.y, op:"sell", …}` via `OpCodes.Action` (`Send():` confirmed transmits).
- **Server:** `handleShopAction` (`handlers_shop.go:35`) → range 3.0 → `resolveShop(gx,gy)` → `shopSell` (`:82`):
  slot check → `shopBuysItem(shop, id, def)` (tag match) → `player.Coins += def.SellPrice*qty`.
- **Data:** 187/190 items have `sell_price>0`; NPCs buy real tags (general_store_merchant: `material`,`food`;
  blacksmith: `metal`; weaver: `textile`,`fiber`; bug_dealer kind `bugs` buys any species + `dead_*`). So the
  Sell column WILL populate and most items are sellable. (`ecologist` buys nothing — talk-only.)

## 3. Why it fails (ranked)
- **A — the shop dialogue never opens (most likely).** `TryHandleRightClick` does `Physics2D.OverlapPoint(mouseWorld)`
  (`ShopPanel.cs:94`) → ONE `OccupantClickTarget` collider. Every occupant has a `BoxCollider2D` sized to its
  **sprite bounds** (`TilemapManager.cs:906-913`), and `OverlapPoint` returns one collider with no
  topmost/sorting preference. NPCs sit at storefronts where their sprite bounds overlap the building/sign/
  counter → the click resolves to the wrong occupant → `def.InteractionType != "shop"` → falls through, nothing
  opens. The router (`PlayerInputRouter.cs:152-178`) chains many handlers, all using the same single hit, so a
  mis-resolved click fails for all of them and falls through to a melee jab = "clicking did nothing."
- **B — the shop opens but the sell is rejected (secondary).** If the user reached the board: selling an item
  the NPC's `buys` tags don't cover → `"They don't buy that"`; or a **slot-index mismatch** — `BuildSell` sends
  the client `ItemSlots[i]` index; if the client/server inventory slot layouts differ, `shopSell`'s
  `player.ItemSlots[slot].ItemID != id` check → `"You don't have that"`. (Worth a glance during the fix.)

## 4. Recommendation
1. **Primary (shared fix):** a single `ResolveClickedOccupant(mouseWorld)` helper using `OverlapPointAll` →
   choose the topmost interactable (highest `SpriteRenderer.sortingOrder`/lowest anchor, tie-break prefer an
   occupant whose `interaction_type` matches a live handler). Route ShopPanel/CraftingPanel/StationController/
   Mannequin/Sign/Bed/Breaking through it. Fixes #5-open, #18, and de-risks #14/#10/#4/#12.
2. **Confirm first (cheap):** right-click an NPC and watch for the dialogue. Opens reliably → it's §3B (chase the
   tag/slot path). Doesn't open / only from certain pixels → it's §3A (the OverlapPoint fix).
- Determinism: none — pure client interaction + a coins/inventory transfer already server-validated.

## 5. Cross-cutting note
See the index "shared OverlapPoint resolution" note. #18 is the same defect on the break path
(`BreakingController` `OverlapPoint`). #14/#10/#4 right-click-to-open route through the same chain — each is
investigated for its OWN distinct cause too (e.g. #10 is station-state keying, not click resolution).
