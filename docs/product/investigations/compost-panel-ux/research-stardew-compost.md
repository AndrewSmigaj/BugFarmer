# Research: Stardew & cozy-farming compost / processing-machine panel UX

Cluster: Stardew Valley and cozy-farming peers — how single-machine "put an item in → it
converts over time → collect the output" is presented, and how COMPOST / decomposition /
fertilizer specifically is handled and shown.

Target feature: a Unity uGUI "station panel" for a COMPOST BIN with (1) INPUT area, (2)
PROCESS/progress indicator, (3) OUTPUT the player takes, (4) flavor DESCRIPTION on open.

STATUS: COMPLETE. Raw research log below, then the SYNTHESIS / DELIVERABLES section
(source table, adoptable patterns, compost-satisfaction levers, ASCII layout candidates, skeptic list).

---

## Raw research log (appended as I go)

### Batch 1 — Stardew processing machines (keg/preserves jar), worm bin, fertilizer, GK compost

KEY STRUCTURAL FINDING: **Stardew's processing machines have NO panel UI at all.** They are
objects placed in the world. Interaction model:
- INPUT: player holds an item, clicks the machine once → the item is consumed, machine begins
  processing. There is no slot grid, no "load" screen.
- PROCESS: the machine's world SPRITE changes to an animated "working" frame (e.g. keg bubbles,
  preserves jar shakes) for the whole duration. That animated sprite IS the progress indicator —
  there is no numeric bar. Time is measured in in-game minutes/days.
- DONE: a **floating icon bubble** pops up above the machine showing the finished product's icon
  (the "ready bubble"). This is the single most reused readable signal in the genre.
- OUTPUT: player clicks the machine once more → collects the product, machine returns to idle.
So Stardew's "UX" for single-item processing is: click-in, sprite-animates, bubble-when-ready,
click-out. No progress bar, no timer text in vanilla (mods like "Detailed Machine Statuses" ADD
countdown text — meaning the community WANTED explicit timing the base game hides).

Preserves Jar mechanics: unlocks Farming lv4; fruit/veg/roe → jam/pickles. Quality of input is
ignored; output value = 2×base+50. Processing ~4000 in-game minutes (~2-3 days).
Keg: lv8; fruit→wine (7 days), veg→juice (4 days), etc. Recipe: 30 wood, 1 copper bar, 1 iron
bar, 1 oak resin. Value: fruit ×3, veg ×2.25.

Worm Bin / Deluxe Worm Bin: a **no-input** passive generator — auto-produces 4-5 bait each
morning; you just collect. Processing ~1 in-game day per batch. (Relevant as the "output only"
degenerate case — a compost bin that slowly makes compost from ambient input.)

Fertilizer trio (the compost/soil theme):
- Basic Fertilizer: "improves soil quality"; buy 100g at Pierre's from Spring 15; affects only
  base harvest quality. Placed on tilled soil before sprouting.
- Quality Fertilizer: "improves the chance to grow a quality crop"; craft / Bone Mill / 150g yr2.
- Deluxe Fertilizer: chance at IRIDIUM quality; craftable lv9 from 1 Super Cucumber + 1 Mayonnaise
  + 1 Truffle Oil; can be applied before OR during growth. Tiering = Basic→Quality→Deluxe is the
  clean "good/better/best" ladder we can mirror for compost outputs.
NOTE: the wiki pages are mechanics-only; they do NOT carry the verbatim in-game flavor text, so I
still need the actual description strings (pulled below from other sources / game data).

GRAVEYARD KEEPER Compost heap (the closest analogue to OUR bin):
- Built in the kitchen garden; requires studying the "Decay" technology first.
- INPUT→OUTPUT: **8 units of crop waste → 6 peat + 2 maggots** (a byproduct). Batch conversion,
  not 1:1. Peat = a "starter" fertilizer (copper quality/copper boost) AND an ingredient for
  higher-tier fertilizers, plus needed for landscaping (berry bushes, apple trees, flower beds).
  Maggots feed fishing/alchemy. → good model: compost feeds BOTH a direct use and higher recipes,
  and yields a flavorful byproduct (for us: maggots/grubs the bugs would love).

CONSEQUENCE FOR US: because we want an actual PANEL (input area / progress / output / description),
Stardew is the wrong structural template (it has no panel). Stardew gives us the *feel signals*
(ready-bubble, working animation, tiered outputs, terse flavor text). For the PANEL LAYOUT itself
we lean on the station-panel games: My Time at Portia/Sandrock, Graveyard Keeper's workstation
windows, Coral Island / Fields of Mistria. Pulling those next.


### Batch 2 — the PANEL-based station games (our real layout template) + Stardew code study

CORAL ISLAND — **Compost Bin (our near-exact twin)**:
- Crafted at Farming Mastery lv2 (20 wood, 5 trash, 5 sap). You place it on the farm/shed and
  INTERACT to open it.
- INPUT: 2 Trash → 1 Compost; OR an ORGANIC item (scavengeables, insects, crops) → **5 compost
  each**. So organics are the "premium" input. This is exactly our "fruit/crops/trimmings/dead
  bugs" loadout.
- Compost is then combined (2 Compost + 1 Sap) into FERTILIZER via the crafting menu.
- Coral Island's processing equipment generally (furnace/kiln/dehydrator): you interact → a panel
  with INPUT slots, a per-order DURATION, and OUTPUT slots; a **FIFO queue** (furnace holds up to
  5 orders; each 6h copper → 36h osmium). Dehydrator/fish pond/insect house process ALL inputs
  simultaneously (batch) rather than FIFO — relevant: a compost bin reads more naturally as BATCH
  (throw a pile in, it all rots together) than as a strict one-at-a-time queue.

MY TIME AT PORTIA — **Recycle Machine (clean panel template)**: interacting opens a window that
shows (a) the item to process, (b) a PREVIEW of the returned materials + quantities, (c) the TIME
needed, and (d) a quantity selector + Start / Cancel. Recycling is cancellable; if you cancel
after ≥1 in-game minute the item is lost. → Takeaways for us: show the OUTPUT PREVIEW before you
commit, show the TIME up front, and offer Start/Cancel. This is the "commit dialog" pattern.

MY TIME AT SANDROCK — **Worktable queue**: station has a "Working Queue" (how many orders can be
scheduled, set by station LEVEL) and "Queue Capacity" (max items per order, set by station
QUALITY). This is the scaling model if compost bins get upgrade tiers (bigger/faster).

GRAVEYARD KEEPER — **Compost heap**: batch 8 crop-waste → 6 peat + 2 maggots; requires the "Decay"
tech; world object with a progress bar shown on the heap; peat = starter fertilizer + higher-tier
ingredient; maggots = flavorful byproduct feeding other systems. Confirms: batch conversion +
byproduct + tiered fertilizer chain.

--- OPEN-SOURCE CODE STUDY #1 (authoritative): decompiled Stardew Valley `Object.cs` ---
(veywrn/StardewValley, StardewValley/Object.cs, 6658 lines — read the real methods)

The genre-defining "input → convert over time → collect" machine is ~4 net fields + a draw hook:
- `NetBool readyForHarvest`, `NetIntDelta minutesUntilReady`, `Object heldObject` (the OUTPUT that
  sits inside the machine), `NetBool showNextIndex` (draw sprite index+1 = the "working" frame).
- START (performObjectDropInAction, line 1987; Furnace case ~2741): validate input (Furnace needs
  coal present + ore stack ≥5), then set `heldObject = <output object>`, set `minutesUntilReady`
  to a PER-RECIPE duration (copper 30 min, iron 120, gold 300, iridium 480), consume inputs, set
  `showNextIndex=true`, play a sound, emit smoke particles. NOTE: **the output identity is decided
  at load time and stored immediately** — the machine already "knows" what it's making.
- TICK: each in-game clock step decrements `minutesUntilReady`; when ≤0 → `readyForHarvest=true`.
- READY-BUBBLE DRAW (line ~5260): if readyForHarvest, draw a small speech-bubble sprite
  (mouseCursors rect 141,465,20,24) ABOVE the machine at 0.75 alpha with a gentle vertical bob
  `yOffset = 4 * sin(totalMs / 250)`, and draw the OUTPUT icon (16×16) inside the bubble. That
  bob + product-icon is the entire "it's done, come get it" signal.
- COLLECT (checkForAction ~4000): click when ready → move `heldObject` to inventory, play "coin",
  reset `readyForHarvest=false`, `heldObject=null`, sprite back to idle.
KEY LESSON: vanilla shows NO numeric progress — only (idle sprite) → (animated working sprite) →
(bobbing ready bubble). The most-installed mods ("Detailed Machine Statuses", harvest bubbles)
ADD countdowns/ready-bubbles-for-everything, i.e. players DO want a legible time estimate. Since
we have a real PANEL (not a world click), we can give the explicit progress the world-sprite
version can't — a bar/estimate — while keeping the bobbing ready-icon as the "come collect" cue.

--- OPEN-SOURCE CODE STUDY #2: Unity uGUI slot pattern (wkoziel/2D-Farming-Game) ---
`ItemPanel : MonoBehaviour` holds `ItemContainer inventory` + `List<InventoryButton> buttons`.
`Show()` walks the container's slots and calls `buttons[i].Set(slot)` or `.Clean()` to rebind each
button to its slot's item; `OnClick(id)` is overridden per-panel (InventoryPanel routes clicks to a
drag-drop controller). This is the standard, dead-simple uGUI station-panel skeleton we'd reuse: a
fixed row of slot Buttons/Images, a Show()/Refresh() that re-binds from data, click handlers that
move items. Our compost panel = one such panel with an INPUT container (few slots), a PROGRESS
widget, and an OUTPUT container (1-2 slots).

### Batch 3 — cozy-UI design principles + verbatim flavor-text tone

COZY-UI FEEDBACK PRINCIPLES (from cozy-game UI writeups + a progress-bar design article):
- Cozy feedback is CALM and NON-INTRUSIVE — soft fades, gentle transitions, no rushed/jarring FX.
  Players "don't want to feel rushed," so completion should feel like a warm arrival, not an alarm.
- Tactility: thick borders, deep soft shadows, rounded corners make each element read as a
  physical object you could touch (matches a wooden compost bin).
- Progress-bar rules that map onto a station: (1) ANIMATE the fill, don't snap; (2) show REMAINING
  time/what's-needed; (3) show the REWARD up front (preview the output before you commit);
  (4) a small color/particle FLOURISH + a soft SOUND on completion; (5) keep durations
  PROPORTIONAL (too-long = abandonment); (6) if multiple outputs, show them all clearly.

VERBATIM FLAVOR-TEXT TONE (Sun Haven fertilizer strings, confirmed verbatim):
- "A farming essential, composters turn resources into compost and fertilizer." (the composter)
- "Fertilizer rich with the magic of earth, increasing your crop's harvest."
- "Fertilizer rich with the magic of water, increasing your crop's chance to stay watered over night."
- "Fertilizer rich with the magic of fire, increasing the speed your crops grow."
- Advanced variants reuse the sentence with "significantly" inserted → a tidy tier-scaling trick.
PATTERN: one short sentence = [what it IS, flavored] + [what it DOES], present tense. That's the
whole tooltip. (Stardew is even terser, e.g. Basic Fertilizer ≈ "improves soil quality a little,
increasing your chance to grow quality crops. Mix into tilled soil." — search-sourced, treat as
approximate, not verbatim-verified.) For OUR bin's open-description we want ~1-2 sentences of
warm flavor ("Toss in scraps, spoiled fruit, and the odd dead beetle; give it time and the pile
turns dark and crumbly — the bugs love what grows in it.") + a plain line of what to load.

---
---

## SYNTHESIS / DELIVERABLES

### (a) SOURCE TABLE

| Source (read) | Concrete technique it demonstrates | Fits our constraints? (Unity uGUI panel; organic in → compost over time; flavor on open) |
|---|---|---|
| **Stardew `Object.cs`** (decompiled, read in full) | Machine = `heldObject`(output) + `minutesUntilReady` + `readyForHarvest` + `showNextIndex`(working sprite). Idle→working-sprite→bobbing ready-bubble(product icon)→click-collect. Output identity chosen AT LOAD. | PARTIAL. It's world-object, no panel — but the STATE MODEL (decide output on load, tick a timer, flip to "ready", collect) ports 1:1 to our panel. Adopt the state machine; replace the world-bubble with an in-panel progress + a ready glow. |
| **Stardew ready-bubble draw** | Speech-bubble sprite + 16px product icon, bobbing `4*sin(t/250)`, 0.75 alpha, above machine. | YES as a MICRO-PATTERN: put a gently-bobbing product icon in the OUTPUT slot when ready (+ a soft "collect" chime). Cozy, non-intrusive. |
| **Coral Island Compost Bin** | Trash 2→1 compost; ORGANICS (crops/insects/scavenge) → 5 compost each; compost+sap→fertilizer. Interact-to-open panel. | YES — near-exact twin. Adopt: organics are the premium input; compost is an intermediate that feeds a fertilizer recipe; a real interact panel. |
| **Coral Island furnace/kiln/dehydrator** | Panel = input slots + per-order duration + output slots; FIFO queue for most, but dehydrator/insect-house process ALL inputs SIMULTANEOUSLY (batch). | YES. Compost reads as BATCH (a pile rots together), so model it like the dehydrator, not a 1-at-a-time keg. |
| **My Time at Portia Recycle Machine** | Interact → window shows item + PREVIEW of returned outputs + quantities + TIME needed + quantity selector + Start/Cancel; cancellable (with a cost). | YES — the "commit dialog" pattern: preview output + show time before you press Start; allow cancel. |
| **My Time at Sandrock Worktable** | Station has Working-Queue (count, by level) + Queue-Capacity (per-order size, by quality). | YES if compost bins TIER UP (bigger batch / faster) — clean upgrade axes. |
| **Graveyard Keeper Compost heap** | Batch 8 waste → 6 peat + 2 maggots (byproduct); "Decay" tech gate; progress bar on the heap; peat = starter fert + higher-tier ingredient. | YES — batch conversion + a flavorful BYPRODUCT (for us: grubs/maggots) + tiered fertilizer chain. |
| **Sun Haven Composter** | Workbench with a RECIPE LIST: organics(+mana)→compost; compost+elemental crystal→Earth/Water/Fire fertilizer (extra-harvest / stays-watered / faster-growth); also fishing baits. | YES — themeable OUTPUT LADDER (3 functional flavors) + a secondary output line (baits). |
| **Stardew Worm Bin** | Zero-input passive generator: makes 4-5 bait/morning; just collect. | PARTIAL — the "ambient trickle" degenerate case; useful if a bin also slowly self-composts. |
| **uGUI clone (wkoziel/2D-Farming-Game)** | `ItemPanel`: `List<InventoryButton>` bound to an `ItemContainer`; `Show()` re-binds each slot; `OnClick(id)` routes to a drag/drop controller. | YES — literal uGUI skeleton: our panel = INPUT ItemPanel + PROGRESS widget + OUTPUT ItemPanel; Refresh() re-binds from the station's server/sim state. |
| **Cozy-UI + progress-bar design writeups** | Calm/non-intrusive feedback; tactile (thick borders, soft shadows, rounded); animate fills; preview reward; proportional pacing; soft completion sound. | YES — the polish bar. Directly sets our styling + feedback rules. |

### (b) ADOPTABLE LAYOUT + STYLING PATTERNS

INPUT vs PROGRESS vs OUTPUT arrangement — two dominant idioms in the genre:
1. **Left→right conversion flow** (Minecraft furnace / Stardew mental model): INPUT on the left,
   a PROGRESS arrow/bar in the middle, OUTPUT on the right. Reads instantly as "this becomes that."
   Best when the conversion is the star and the panel is compact.
2. **Top→down "vessel" / journal** (cozy games): a header (bin art + flavor description), an INPUT
   tray, a central PROCESS visual (the pile maturing), an OUTPUT tray with a Collect button.
   Warmer, more diegetic, more room for flavor. Better fits our "open shows a description" ask.

How to visualize PROGRESS-OVER-TIME (ranked for our case):
- **BEST: a maturing-material sprite + a slim bar + a soft time estimate.** Show the compost
  visibly change state (fresh green scraps → browning → dark crumbly humus) across ~3-4 art
  frames tied to % complete; underlay a thin fill bar; label it "~2 days" / "ready at dawn," not a
  ticking second-counter (cozy = don't stopwatch the player). The changing PILE is the emotional
  progress; the bar is the precise one. This beats Stardew's single working-sprite because the
  panel gives us room, and beats a bare bar because it's diegetic and satisfying.
- Animate the bar FILL (lerp, don't snap) and, on completion, a small dust/steam puff + the
  output icon gently bobbing (Stardew's `4*sin(t/250)` bob) + a soft chime.
- Do NOT expose raw in-game minutes as the primary readout — show a friendly relative estimate;
  optionally a precise tooltip on hover (this is exactly what the "Detailed Machine Statuses" mod
  proved players want as an OPTION, not the default shout).

How the DESCRIPTION/flavor is shown on open:
- A short 1-2 sentence blurb in the panel HEADER (next to the bin's portrait/art), styled as warm
  body text. One sentence of flavor + one plain line of "what to load." Keep it terse (Sun Haven /
  Stardew are one sentence). Optionally fade it in softly (cozy transition).
- Per-ITEM tooltips (on hovering an input/output slot) follow the genre tooltip: name + one-line
  description + (for outputs) what it's good for. Reuse our existing item tooltip component.

Styling (from cozy-UI principles): wooden/earthy frame, thick rounded border, soft drop shadow so
the panel feels like a physical bin; generous slot padding; muted natural palette (browns/greens);
completion FX warm and small. No harsh reds/alarms.

### (c) MAKING COMPOST / FERTILIZER SPECIFICALLY SATISFYING

- **Batch, not queue.** A pile rots as a whole (Coral dehydrator / GK heap). Let the player toss a
  mixed handful of scraps in, then it all matures together. One progress track, one payoff — reads
  truer than a 1-in-1-out keg and is less fiddly.
- **Premium organics.** Mirror Coral Island: junk/trimmings give a little, but real organics
  (fruit, crops, DEAD BUGS) give more/better compost. This makes the bin a natural sink for the
  bug game's surplus and losses — dead bugs becoming rich compost is thematically perfect.
- **A visible transformation.** The single biggest "satisfying" lever: show the material CHANGE
  (green scraps → dark humus) as it composts, plus a tiny thermometer/steam wisp ("it's cooking").
  Decomposition that you can SEE maturing is the payoff Graveyard Keeper/Coral lean on.
- **A flavorful byproduct.** GK gives maggots; Sun Haven gives baits. For us: composting yields a
  few **grubs/maggots** as a byproduct — free bug food / bait / a treat that draws bugs. Turns one
  action into two little rewards (the "and also..." delight).
- **A tiered / themed output ladder.** Compost (base) → Fertilizer (compost + a binder). Offer a
  good/better/best ladder (Stardew Basic→Quality→Deluxe) or Sun Haven's flavor split
  (harvest / growth-speed / water-retention). Gives the bin long-tail purpose.
- **Warm completion.** Soft chime + dust puff + the output icon bobbing in its slot + maybe the
  bin art shows a full, dark, crumbly pile. Calm, not celebratory-loud.
- **Terse warm flavor text on open** in the Sun Haven mold: one sentence that says what it IS +
  what it DOES, present tense.

### (d) CANDIDATE LAYOUT SKETCHES (for OUR compost bin panel)

--- LAYOUT A: "Conversion flow" (horizontal, furnace idiom) ---
```
+--------------------------------------------------------------+
|  [bin art]  COMPOST BIN                                  (X)  |
|             "Toss in scraps and the odd dead beetle; give     |
|              it time and it turns to dark, rich earth."       |
+--------------------------------------------------------------+
|                                                              |
|   LOAD              COMPOSTING…              COLLECT          |
|  +----+----+       ############----   ~2d   +------+         |
|  | 🍎 | 🐛 |  ==>   [ pile: browning ]  ==>  | 🟤x3 |         |
|  +----+----+       (maturing sprite)         +------+        |
|  | 🌿 | +  |                                  | 🐛x1 |(grub)  |
|  +----+----+                                  +------+        |
|                                                              |
|          [ Start composting ]        [ Collect all ]         |
+--------------------------------------------------------------+
```
PROS: instantly legible as input→process→output; compact; matches genre mental model; the arrow
axis teaches the mechanic with zero text. CONS: less cozy/diegetic; horizontal space gets tight on
narrow layouts; the "process" cell is small so the maturing-pile art can't be a hero.

--- LAYOUT B: "Cozy vessel / journal" (vertical stack) ---
```
+---------------------------------------------+
|  COMPOST BIN                            (X)  |
|  [big bin cross-section art: the pile,       |
|   fresh green on top → dark humus at base;   |
|   fills & darkens as it matures]             |
|                                              |
|      ####################------  ~1 day      |
|                                              |
|  "Scraps, spoiled fruit, even fallen bugs —  |
|   time turns it into dark, crumbly earth."   |
+---------------------------------------------+
|  ADD ORGANICS         | READY TO TAKE        |
|  +--+--+--+--+         | +------+  +------+   |
|  |🍎|🌿|🐛|+ |         | 🟤 x3  |  | 🐛 x1 |   |
|  +--+--+--+--+         | compost|  | grubs |   |
|  [ Start ]            |        [ Collect ]    |
+---------------------------------------------+
```
PROS: the maturing pile is the HERO visual (max satisfaction); natural home for the on-open flavor
blurb; tactile/diegetic; scales to a tall panel; output byproduct sits comfortably. CONS: taller
footprint; input↔output relationship is implied by position, not an explicit arrow (slightly less
instantly obvious than A).

--- LAYOUT C (bonus): "Commit dialog" overlay (Portia idiom), if we want an explicit preview ---
```
+-----------------------------------------+
| Compost this batch?                     |
|  In:  🍎 x2  🌿 x3  🐛 x1                |
|  Out: 🟤 compost x4   🐛 grubs x1        |
|  Time: ~2 days                           |
|        [ Cancel ]     [ Start ]          |
+-----------------------------------------+
```
Use as a confirm step layered on A or B when the player presses Start — previews outputs + time
(Portia). PRO: sets expectations, prevents mis-loads. CON: an extra click; may feel heavy for a
cozy toss-it-in action — probably skip unless inputs are costly/ambiguous.

RECOMMENDATION: **Layout B** (cozy vessel) as the primary — it makes decomposition visible (the
satisfaction lever), gives the on-open description a natural home, and fits a wooden tactile style.
Borrow A's explicit input→output reading only if playtests show the relationship is unclear; skip
C's confirm dialog unless inputs are expensive.

### (e) WHAT A SKEPTIC WOULD SAY WE MISSED

- "Stardew isn't even a panel game — you leaned on the wrong template." Answered: we take Stardew's
  STATE MODEL + ready-bubble micro-pattern, and the PANEL layout from Coral/Portia/Sun Haven. But a
  skeptic is right that we should verify our engine already interacts-to-open a panel (we do — this
  is a 'station panel' by the task) rather than a world click.
- Determinism/sim ownership: BugFarmer's bugs are client-authoritative but the WORLD/economy is
  server-authoritative. A compost bin's timer + inventory is game state that must live where our
  other stations live and survive save/reload; the panel is just a VIEW. This research covered UX,
  not where the bin's state is stored/ticked — that's an architecture question to resolve before
  building (does it tick on the server clock? persist in the zone save?).
- Real-time vs in-game-days: Stardew/Coral measure in in-game time. BugFarmer's clock model (does
  it even have day-length in-game minutes?) determines whether "~2 days" or a real-time bar is
  right. Unverified here — check the game clock before writing the estimate text.
- Multiplayer: if two players open the same bin, the panel must reflect shared state live (someone
  else loading/collecting). None of the single-player sources address this; it's a real design
  question for us.
- Overflow/failure states: what if the output slot is full, or you load a non-organic item? Portia
  shows a red message; Stardew refuses the drop-in. We should specify reject feedback (a soft "that
  won't compost" nudge), not just the happy path.
- Accessibility/readability: relative time ("~2 days") is friendlier but vaguer; some players want
  the exact number (the Detailed-Machine-Statuses lesson). Offer precise time on hover.
- Input economy risk: if dead bugs → great compost, does that create a perverse incentive to kill
  bugs? Given MEMORY says bugs are the heart of the game, tune ratios so composting is a sink for
  NATURAL surplus/losses, not a farming-for-corpses loop. (Design/taste — flag to owner.)
- Art cost: the "maturing pile across 3-4 frames" is the satisfaction lever but it's real sprite
  work (pipeline A / gpt-image-1). If we only ship a bar, we lose most of the payoff — budget the
  frames or the feature underdelivers.

STATUS: COMPLETE.
