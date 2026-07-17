# Research: Automation / Crafting / Inventory Panel LAYOUT & Visual Hierarchy

**Cluster:** Automation/crafting/inventory panel LAYOUT and VISUAL HIERARCHY craft — the
general UI-design principles + the strongest input→progress→output examples outside cozy-farming.

**Target we are designing for:** ONE reusable Unity uGUI station panel (~320px-wide column)
serving compost bin, wasp nest, beehive, craft stations, chests. The compost bin case shows:
INPUT deposit grid, input-hopper fill bar, compost fill bar, "young insects" area (egg/larva/pupa
stage slots + maturation bar + resident adults), and (soon) an OUTPUT to take.

Status: IN PROGRESS (written incrementally).

---

## 0. The panel we are actually designing for (grounding — read from the real code)
`BugFarmerClient/Assets/Scripts/UI/CraftingPanel.cs` (966 lines) IS the one reusable station panel.
Verified facts (so the candidates below are concrete, not abstract):
- It is built by ABSOLUTE positioning: `Place(rect, x, y, w, h)` with hand-tuned magic numbers into a
  single `_content` transform. It does **NOT** use uGUI Layout Groups today (line 485+, 573+).
- Modes on one panel: `_isCraft` (a WIDE `_dock` = 600×320, 3-column recipe/IO/output), and station
  modes that are a NARROW column (~320px wide): `BuildStationContent` (compost), `BuildNurseryContent`
  (wasp nest/milkweed), `BuildBeehiveContent`, chest/container grid.
- Compost stack today, top→bottom (`BuildStationContent`, l.485–517):
  1. header "COMPOST — click an item to deposit" (w=320)
  2. DEPOSIT grid, 6 cols × 2 rows (12 slots, 44px pitch) — click a slot to deposit
  3. "Input n/cap" label + fill bar (bg 184px, fill grows from x=2)  — fill color amber (0.8,0.65,0.3)
  4. "Compost n/cap" label + fill bar                               — fill color green (0.45,0.8,0.3)
  5. BROOD region (`BuildBroodRegion`, l.573): "BROOD" header + hint, 3 stage slots (egg/larva/pupa,
     52px pitch) + count labels, a maturation fill bar (green 0.55,0.85,0.4), "INSIDE" resident slot+label.
  6. **No OUTPUT section exists yet** (the thing to add).
- BAR REALITY: `SetBar` sets the fill Image's `sizeDelta.x = 180*frac` every refresh/frame (l.553).
  → bars are animated per-frame by width; they must stay OUT of any Layout Group (which rebuilds at
    frame-end and would fight a per-frame size write). This constrains the "use layout groups" option.
- **Found a real readability bug:** input bar amber, compost bar green, brood bar green — the compost
  and maturation bars are nearly the same hue → two stacked green bars read as the same meter. Hue-code them.

---

## 1. Source table

| Source | Concrete technique | Fits our constraints? (uGUI · one panel/many stations · ~320px column) |
|---|---|---|
| [Minecraft Smelting/furnace wiki](https://minecraft.wiki/w/Smelting) | Canonical IPO: input top-left, FUEL bottom-left, progress ARROW center, OUTPUT right; flame = depleting fuel gauge | Idiom fits, ORIENTATION does not — remap the horizontal input→arrow→output onto a **vertical** top→bottom axis for a narrow column |
| [Factorio FFF-426 (assembler GUI)](https://factorio.com/blog/post/fff-426) | Give the RECIPE its own labeled element; never overload a slot with two meanings; show a NAME not just an icon | Yes — each concept (deposit / hopper / compost / brood / output) gets its own labeled region |
| [Techtonica machine UI — R. Chadwick](https://www.ryanchadwickart.com/projects/DLLAv0) | ONE menu flexes across machine tiers (3-vs-4 inputs, fuel-vs-electric); start minimal, show only what THAT machine needs; simplified over time | Yes — direct analog to "one panel, many station types"; drive region show/hide per station |
| [Apico UI deep dive (devs)](https://www.gamedeveloper.com/design/deep-dive-multiple-menu-systems-ui-design-in-i-apico-i-) | One menu system for all machines; drag windows by title bar; **buttons on the LEFT** (always in view, near cursor); Nielsen heuristics; hover mini life-bar | Yes — this is our quality bar; adopt left-anchored controls, tooltips, hover status |
| Apico beehive mechanic (same wiki family) | bees→INPUT slots → bred into a Queen (progress) → offspring in OUTPUT slots | Direct structural analog to compost: feed → living transformation → collect |
| [Evil Martians — devtool layout rule](https://evilmartians.com/chronicles/devtool-layout-rule) | STEARC effect: TOP controls BOTTOM, LEFT controls RIGHT; source→result reads down/right; against-flow = "modify" not "select" | Yes — fixes reading order: deposit (top) → process → OUTPUT/collect (bottom); "take" at the result end |
| [Progress-indicator best practice (SIDP / Material 3)](https://smart-interface-design-patterns.com/articles/designing-better-loading-progress-ux/) | Determinate bars fill 0→100%, NEVER regress; ONE per process; percent/value text; label what it measures | Yes — compost/hopper/maturation are long determinate processes; one bar each, valued, hue-coded |
| [NN/G — Common Region](https://www.nngroup.com/articles/common-region/) | Enclosure (border/bg) groups strongly and can overpower proximity; but prefer WHITESPACE first; over-bordering = clutter/"false floors" | Yes — separate the 3 blocks with headers+whitespace; add a subtle tint/divider only where whitespace is insufficient |
| [NN/G — Proximity (Gestalt)](https://www.nngroup.com/articles/gestalt-proximity/) | Near = related; proximity overpowers color/shape; define inside-vs-outside spacing | Yes — tighter spacing WITHIN a block than BETWEEN blocks is the primary grouping tool |
| [Unity uGUI auto-layout](http://docs.unity3d.com/Packages/com.unity.ugui@latest/index.html?subfolder=/manual/UIAutoLayout.html) + [UhiyamaLab guide](https://uhiyama-lab.com/en/notes/unity/unity-ugui-layout-group/) | Vertical/Horizontal/Grid Layout Group + LayoutElement (min/pref/flex) + Content Size Fitter; nest ≤2 deep; driven RectTransform; **don't put per-frame-animated widgets under a layout group** | Partial/careful — great for static section stacks & grids; but our fill bars animate per frame → keep them outside layout control (LayoutElement.ignoreLayout or an absolutely-placed child) |
| [Collect (OSS Unity inventory)](https://github.com/adampassey/Collect) — read the repo | Container→Slot hierarchy; attach a **GridLayoutGroup to the container** to auto-align slots; `SlotWithType` = type-restricted slot | Yes — deposit/output/stage grids = GridLayoutGroup; deposit slots are type-filtered (StationAccepts) = SlotWithType pattern |
| [basic-inventory-system-unity (OSS)](https://github.com/dcroitoru/basic-inventory-system-unity) — read the repo | UI DECOUPLED from behavior; drag/tooltip/ghost are composable behaviors; crafting bench = material slots + one outcome slot | Yes — architecture: one dumb view, behaviors attached; matches reusing the panel across station types |
| [Terraria mobile crafting UI](https://medium.com/@watsonwelch/the-making-of-terraria-mobile-part-3-crafting-a-new-ui-4fb84708c767) | Persistent categorized list + PROGRESSIVE DISCLOSURE (recipes unlock as you gather) | Partial — reveal the OUTPUT block only when something is ready; empty/locked regions should read "not yet", not clutter |
| [IxDF visual hierarchy](https://ixdf.org/literature/topics/visual-hierarchy) / [Unity blog: effective UI](https://unity.com/blog/games/how-to-immerse-your-players-through-effective-ui-and-game-design) | Size/contrast/position/spacing set importance; whitespace lowers cognitive load; progressive disclosure | Yes — general hierarchy discipline for the column |

**Rigor check:** 6 search angles (by-game ×3, by-technique ×2, by-problem ×1, by-theory ×3); 9 sources
deep-read in full via WebFetch (Factorio, Minecraft, Terraria, Techtonica, Evil Martians, Unity uGUI
guide, Apico, Common Region, plus the Collect repo); 2 open-source implementations studied (Collect,
basic-inventory-system-unity) + the real BugFarmer panel read at source-line level.

---

## 2. Adoptable layout + hierarchy rules (concrete, for OUR panel)

**R1 — Reading order = vertical IPO.** A ~320px column reads TOP→BOTTOM, so remap the furnace's
horizontal input→process→output onto the vertical axis (STEARC still holds: top=source, bottom=result):
  **(A) what you PUT IN / act on → (B) the PROCESS state → (C) the RESULT you COLLECT.**
Put the "Take / Get all" control at the BOTTOM (result end); put the deposit affordance at the TOP.

**R2 — Three perceptual BLOCKS, grouped by proximity first, enclosure only if needed.** The compost
panel is not one list — it is three ideas that must not blur together:
  - **Block A — MATERIAL PROCESSING** (non-living): deposit grid + input-hopper bar + compost bar.
  - **Block B — LIVING CREATURES / BROOD** (the "young insects"): egg/larva/pupa stage slots +
    maturation bar + resident adults ("INSIDE").
  - **Block C — OUTPUT**: finished goods to take + a "Get all".
Group with **inside-vs-outside spacing** (tight within a block, a bigger gap between blocks) + a labeled
header per block (Factorio: label it). Add a subtle background tint or a 1px divider between blocks ONLY
where whitespace alone doesn't separate them (Common Region: don't over-border → clutter/false floors).

**R3 — Label every block; don't make players decode icons.** Each block gets a short ALL-CAPS header
("DEPOSIT", "COMPOSTING", "BROOD", "READY / OUTPUT"). Keep headers short — the current
"COMPOST — click an item to deposit" is too long for a 320px column (truncation/localization risk).
Move the how-to ("click to deposit") to a lighter sub-hint or a tooltip.

**R4 — One determinate bar per process, valued, hue-coded, never regressing.** Each fill bar: fills
left→right 0→100%, shows a value (`n/cap` or %), has a small ICON at its left saying WHAT it measures,
and a DISTINCT HUE per meaning. Fix the current clash: input=amber (keep), compost=green (keep),
**maturation must NOT also be green** — give the living/time bar its own hue (e.g. warm gold or teal).
Never rely on hue alone (color-blind): icon + label carry the meaning too.

**R5 — Alignment & rhythm.** All block headers, grid left edges and bar left edges align to ONE left
margin (the column's left rule). Standardize spacing/padding to a small set of values (e.g. 8px inside a
block, 16–20px between blocks; 44px slot pitch as today). Consistency reads as "polished".

**R6 — Slots.** Deposit + output + stage grids each = a GridLayoutGroup container (Collect pattern).
Deposit slots are TYPE-FILTERED to `StationAccepts` (SlotWithType pattern). Slots carry composable
behaviors — tooltip on hover, drag-with-ghost, click-to-take (dcroitoru pattern), consistent with the
game's existing `DragDropController`.

**R7 — Reuse via region show/hide, not per-station panels (Techtonica/Apico).** The SAME panel renders
a subset of blocks per station: compost = A+B+C; wasp nest / milkweed = B only; beehive = B(+C);
chest = a plain grid; craft = the wide 3-column recipe/IO/output. Keep the station column at ~320px;
only craft goes wide. A block that has nothing yet (e.g. output before first harvest) reads "— nothing
ready yet —", not an empty box (progressive disclosure, Terraria).

**R8 — Controls & feedback (Apico quality bar).** Primary controls anchored where they're always in
view and near the cursor; tooltips, cursor-state feedback, input validation, a constant status line.
Consider a hover mini-bar on the world object (Apico's queen-lifespan bar) so players read compost/brood
state without opening the panel.

**R9 — uGUI build discipline.** Prefer a VerticalLayoutGroup of section sub-panels (each block = one
child object with its own Grid/HorizontalLayoutGroup + a LayoutElement), + a Content Size Fitter so the
column auto-sizes and show/hide reflows cleanly. **Keep the animated fill bars OUT of layout control**
(they set width per frame; a layout group rebuilds at frame-end and would fight them) — place each bar as
an `ignoreLayout` child within its section, or keep bars absolutely placed. Nest layout groups ≤2 deep.
If the full stack (A+B+C) can exceed screen height, wrap `_content` in a ScrollRect.

---

## 3. Scored candidate layouts (score 1–5, 5 = best)

Axes: **Apico-feel** · **Readability** · **Narrow-column fit** · **Dev-cost** (5 = cheap) · **Reuse across station types**

### Candidate A — Vertical Sectioned IPO  ★ PICK
Three labeled Common-Region blocks stacked top→bottom; grouped by whitespace + header + subtle divider;
built as layout-group section objects with bars kept out of layout. (Evolves what's already there.)
```
┌ COMPOST BIN ───────────────────[x]┐
│ DEPOSIT                            │   ← Block A: MATERIAL
│  [▦][▦][▦][▦][▦][▦]                │     (deposit grid, type-filtered)
│  [▦][▦][▦][▦][▦][▦]                │
│  🌾 Hopper   ▉▉▉▉▉▉░░░░  6/10      │     (amber bar + icon + value)
│  🟫 Compost  ▉▉▉▉░░░░░░  4/10      │     (green bar)
│ ── — — — — — — — — — — — — — — — — │   ← divider (only because 2 blocks of bars can blur)
│ BROOD                             │   ← Block B: LIVING CREATURES
│  egg[▦]12  larva[▦]5  pupa[▦]2     │     (stage slots + counts)
│  ⏳ Maturing ▉▉▉▉▉▉▉░░  gold       │     (DISTINCT hue vs compost)
│  INSIDE [▦] 3 resident flies      │
│ ── — — — — — — — — — — — — — — — — │
│ READY                             │   ← Block C: OUTPUT (new)
│  [▦][▦]                 [ Get all ]│     ("take" control at the result end)
└───────────────────────────────────┘
```
Scores: Apico-feel **4** · Readability **5** · Narrow-fit **5** · Dev-cost **4** · Reuse **5**  →  **strongest overall**
Why it wins: reads as clean IPO top→bottom (R1); the three ideas are unmistakably separate (R2); every
process is one valued hue-coded bar (R4); output/take sits at the natural result end (STEARC); it's the
smallest delta from the working code (add an OUTPUT block + hue-fix + section grouping); and the same
block set trivially subsets for nursery/beehive/chest (R7).

### Candidate B — Horizontal furnace IPO (literal Minecraft)
Input grid LEFT · big progress arrow CENTER · output RIGHT, all in one band; brood as a second band.
```
┌ COMPOST ─────────────────────────────────────[x]┐
│ [▦][▦][▦]     ▉▉▉▉░░░ ➜     [▦][▦]               │
│ [▦][▦][▦]  hopper/compost   OUTPUT              │
│ BROOD: egg[▦] larva[▦] pupa[▦]  ⏳▉▉▉  INSIDE[▦] │
└─────────────────────────────────────────────────┘
```
Scores: Apico-feel **3** · Readability **4** · Narrow-fit **1** · Dev-cost **3** · Reuse **2**  →  **REJECT**
Loses: needs real horizontal room (input + arrow + output side-by-side) — impossible at 320px without
shrinking everything; and the compost's TWO stacked meters + living brood don't fit the single-arrow
furnace idiom (furnace has one process; we have hopper + compost + maturation).

### Candidate C — Tabbed sections (Deposit / Brood / Output tabs)
One block visible at a time behind tabs.
```
┌ COMPOST  [Deposit][Brood][Output]─[x]┐
│  (only the active tab's block shown)  │
└───────────────────────────────────────┘
```
Scores: Apico-feel **3** · Readability **2** · Narrow-fit **5** · Dev-cost **3** · Reuse **4**  →  **REJECT**
Loses: it HIDES simultaneous state — the whole point of a compost bin is watching the compost fill AND
the brood mature at once; tabbing forces clicks to see if anything's ready and kills the "alive" feel.
Good pattern for a station with MANY heavy sub-panels, not for this one.

### Candidate D — Two-column split (Material | Life+Output)
Left column = deposit + bars; right column = brood + output.
```
┌ COMPOST ───────────────────────[x]┐
│ DEPOSIT        │ BROOD             │
│ [▦][▦][▦]      │ egg[▦] larva[▦]   │
│ [▦][▦][▦]      │ pupa[▦]           │
│ 🌾▉▉▉░ 6/10    │ ⏳▉▉▉▉             │
│ 🟫▉▉░░ 4/10    │ INSIDE[▦]         │
│                │ READY [▦][▦] Get  │
└───────────────────────────────────┘
```
Scores: Apico-feel **3** · Readability **3** · Narrow-fit **2** · Dev-cost **3** · Reuse **3**  →  **REJECT**
Loses: 320px split into two ~150px columns makes 44px slot grids + labeled bars cramped; it also breaks
the clean top→bottom IPO reading order (output ends up mid-panel). Would work at ~480px, not 320px.

### Candidate E — Collapsible accordion cards  ★ strong runner-up
Each block is a card (Common-Region enclosure) with an always-visible header + a summary chip (mini
fill); expand to see details. Default: compost expands all; other stations collapse unused cards.
```
┌ COMPOST ──────────────────────[x]┐
│ ▾ DEPOSIT              (6 items)  │
│    [▦][▦][▦][▦][▦][▦] …           │
│ ▾ COMPOSTING     🌾6/10 🟫4/10    │  ← collapsed shows summary chips
│ ▾ BROOD          egg12 ⏳72%      │
│ ▸ READY                (empty)    │  ← collapsed until something's ready
└───────────────────────────────────┘
```
Scores: Apico-feel **5** · Readability **4** · Narrow-fit **5** · Dev-cost **3** · Reuse **5**  →  **runner-up**
Why not the pick (yet): collapsing HIDES live state that compost players want at a glance (same weakness
as C, milder because summary chips help). Its real value is the BUILD PATTERN — its "each block is a
self-contained section object with a header + summary" is exactly how to construct Candidate A with uGUI
layout groups, and its optional-collapse is the clean mechanism for stations that outgrow one screen.
**Adopt A's expanded layout as default; adopt E's section-object + optional-collapse as the reuse/overflow
mechanism.**

**PICK = A (built with E's section-object structure).** Rejects lose on: B & D can't fit 320px and break
the vertical IPO read; C hides the simultaneous "is it done yet" state that makes the bin feel alive.

---

## 4. What a skeptic would say we missed

1. **Don't rip out working absolute-positioned code for layout-group purity.** The 966-line panel already
   works with `Place(x,y,w,h)`. Refactoring wholesale to layout groups is real risk for little user-visible
   gain. Pragmatic path: build the NEW output block + section grouping as layout-group sections, and keep
   the animated fill bars on absolute placement (they write width per frame — R9). Migrate incrementally.
2. **Bars under layout groups will fight `SetBar`.** Verified in code: `SetBar` sets `sizeDelta.x` each
   refresh (l.553). A layout group would recompute at frame-end and override it. Any candidate MUST keep
   bars out of layout control — this is a correctness constraint, not a style choice.
3. **Vertical height / overflow is unmeasured.** We know the column is ~320px WIDE; we do NOT know it fits
   the screen once A+B+C stack (deposit 2 rows + 2 bars + 3 stage slots + maturation + residents + output).
   Plan for a ScrollRect or the accordion (E) before this bites.
4. **The BROOD block is itself three sub-ideas** (stage slots, maturation bar, resident adults) — it can
   internally blur exactly like the top-level blocks do. It needs its own inside-vs-outside spacing, or the
   "young insects" area competes with the material block for the eye.
5. **Click-to-deposit vs drag-and-drop consistency.** The panel uses click-to-deposit; the game ships a
   `DragDropController` and inventory drag. Apico/most stations use drag. A skeptic asks: should station
   deposit match the game's drag idiom for consistency, or is click deliberately faster here? (a genuine
   design/taste call for the owner — surface, don't silently pick.)
6. **Color-blind & localization.** Hue-coding the three bars is necessary but insufficient — carry meaning
   in icon+label too. And short ALL-CAPS headers must survive translation in a 320px column.
7. **One-panel-for-everything can bloat.** Chest (plain grid) and compost (rich A+B+C) sharing one script
   is good reuse but risks a tangle of `if station-type` branches (the panel is already 966 lines). Verify
   the show/hide keeps each mode visually clean and the code legible.
8. **Thin GDC-talk coverage.** Game UI Database is a browse/reference tool, not an article; we leaned on the
   Apico dev deep-dive + NN/G + Evil Martians for theory rather than a recorded GDC UI talk. Low-risk gap,
   but a named talk (e.g. Diablo/Dead Space UI post-mortems) could add more inventory-panel specifics.

---

## Raw research log (searches + fetches, appended live)

### Factorio FFF-426 — Assembler GUI redesign (DEEP READ)
Source: https://factorio.com/blog/post/fff-426
- OLD problem: recipe info was crammed onto the OUTPUT slots as tooltips, so the slot could not
  show the actual item's own info (e.g. spoilage). Overloading one element with two meanings = bad.
- FIX: a DEDICATED recipe display element (recipe icon + NAME) separate from the inventory slots.
  "We can clearly separate where we are concerned with the recipe and where we are concerned with
  a specific item." → Principle: give each distinct concept its OWN region; don't overload a slot.
- Added benefit: showing the recipe NAME (text label), not just an icon, reduces reliance on icon
  recognition for unfamiliar recipes. → Principle: label the thing, don't make players decode icons.

### Minecraft Smelting / furnace GUI (DEEP READ) — the canonical processing layout
Source: https://minecraft.wiki/w/Smelting
- Three slots: INPUT top-left, FUEL bottom-left (stacked on the left as the two "feeds"),
  a PROGRESS ARROW in the MIDDLE pointing right, OUTPUT slot on the RIGHT.
- FLAMES above the fuel slot = a depleting fuel gauge (burns down over time).
- Left-to-right reading order encodes the causal flow: feeds (left) -> transformation (arrow,
  center) -> result (right). This is THE recognizable "processing machine" idiom.
  → Principle: put inputs on the left, an explicit directional progress element in the middle,
    output on the right; a second "consumable/fuel" feed stacks under the primary input.

### Progress-indicator best practices (SEARCH digest)
Sources: Smart Interface Design Patterns, Material Design 3, Nielsen/NNg-derived UX articles
- Use DETERMINATE bars when progress can be measured; they fill 0->100% and must NEVER go backwards.
- Percent-done indicators are the most informative wait feedback; showing progress more than doubles
  user patience (median tolerated wait 22.6s vs 9s with no indicator).
- Show only ONE progress indicator per process (avoid clutter / competing bars).
- Perceived-speed trick: fill fast at the start, slow near the end.
  → For us: compost/maturation are long processes -> determinate fill bars are correct; keep each
    bar tied to exactly one process and never let a fill visibly regress.

### Terraria mobile — crafting UI redesign (DEEP READ)
Source: https://medium.com/@watsonwelch/the-making-of-terraria-mobile-part-3-crafting-a-new-ui
- Persistent, always-visible recipe list split into CATEGORIES (borrowed from Minecraft PE).
- PROGRESSIVE DISCLOSURE: recipes unlock as you gather ingredients, so the list grows over time and
  never dumps hundreds of dead options on the player. Playtesting showed players self-set goals.
  → Principle: don't show everything at once; reveal capability as it becomes relevant. For us,
    empty/locked sub-sections (e.g. output before anything is ready) should read as "not yet",
    not clutter.

### Techtonica — machine menu UI (DEEP READ) — ONE flexible menu, many machine tiers
Source: https://www.ryanchadwickart.com/projects/DLLAv0 (Ryan Chadwick, UI artist)
- SAME menu system had to flex across machines: an Assembler shows 3 OR 4 inputs depending on
  recipe; a Mining Drill runs on organic fuel OR electricity depending on tier; Thresher = 2 in /
  2 out. → directly parallels OUR "one panel, many station types" constraint.
- Complexity ladder they designed to: Mining Drill = 1 fuel-in / 1 out ("nothing fancy", must be
  OBVIOUS since it's the first machine placed); Smelter = 2 in / 1 out; Thresher = 2 in / 2 out.
- They SHOWED MORE info in early designs and SIMPLIFIED in the final (Sand Pump). → Principle:
  start minimal; a station panel that tries to show everything reads worse than one that shows
  only what that station needs. The reusable panel should expand/collapse regions per station.
- Mekanism convention (from same search): INPUT slots red, OUTPUT slots dark-blue = a color code
  to distinguish feed vs result at a glance.

### Evil Martians — "the fundamental devtool layout rule" (DEEP READ) — theory
Source: https://evilmartians.com/chronicles/devtool-layout-rule
- RULE: elements on TOP control elements BELOW; elements on the LEFT control elements to the RIGHT.
- Grounded in the STEARC effect (Spatial-Temporal Association of Response Codes): LTR readers map
  left/up = SOURCE/CONTROL and right/down = RESULT/CONTENT. Cause-effect reads down and rightward.
- Controls placed AGAINST the flow (bottom/right) are read as "transform/modify the current view"
  rather than "select/replace it" -> selection (primary flow) vs filtering (secondary flow).
  → Principle: our reading order should be INPUT (top/left, the thing you act on) -> PROCESS
    (progress, middle) -> OUTPUT (the result you collect, end of flow). A "take" button belongs at
    the RESULT end, an "add fuel" affordance at the FEED end.

### Techtonica / IPO model / Mekanism (SEARCH digest)
Sources: Techtonica portfolio, Adobe IPO model, Mekanism wiki
- The Input-Process-Output (IPO) diagram is the canonical mental model: inputs LEFT, process MIDDLE,
  outputs RIGHT — "makes it easy to follow the flow of data from Input through processing to Output."
  This is the same idiom as the Minecraft furnace; it is a broadly recognized convention.

