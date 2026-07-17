# Research: Apico / apiary-style station UI for the Compost Bin panel

**Task:** Polish a "station panel" (Unity uGUI Canvas) for a COMPOST BIN that must show, in one reusable panel:
1. INPUT area (load organic items)
2. PROCESS / progress indicator (input -> compost over time)
3. OUTPUT (player takes compost)
4. "Creatures using the station" — flies that feed + breed in the compost: egg / maggot / pupa stage slots with counts + a maturation bar + resident adults
5. A flavor DESCRIPTION shown when the panel opens

**Reference named by owner:** Apico (the beekeeping game) — a station that BOTH processes materials AND houses breeding insects. Our compost bin is the same shape: process organic matter AND house breeding flies.

**Cluster for this doc:** Apico's apiary/station UI + how beekeeping / creature-husbandry / apiary games present a station where creatures LIVE IN and USE a processing station.

---

## Notes log (incremental — written as I read)

### Apico apiary panel — the concrete slot layout (multiple community sources agree)

The Apico apiary/beehive menu is a **single panel** with spatially-zoned slot groups:
- **INPUT: two bee slots, upper-left.** Drop two bees in; they auto-merge into a Queen. (Same type -> pure queen; two different queens -> hybrid queen.)
- **PROCESS/CONTAINER: frame slots, middle.** You place wooden "frames" into the hive; the queen slowly fills them with honeycomb over her lifespan. Filling the frames IS the visible progress.
- **OUTPUT: 3 offspring slots, right-hand side.** When the queen's lifespan ends, her offspring (new bees) drop here. Separately, produce/honeycomb accumulates in its own slots.
- **STORAGE: 6 slots along the bottom.** A convenience buffer to park spare bees while you're breeding for a target.
- The wiki's own "menu help" groups it as ~five functional areas: Queen slot, Breeding slot, Honeycomb (produce) slots, Offspring slots, Extra storage.

**Progress / lifespan visualization:**
- Hovering the hive in the WORLD shows a **mini lifebar** so you can read "how long the queen has left" without opening the menu.
- Apiaries get a **special visual when frames are full**, so you don't have to open the menu to know it's ready to harvest.
- Detailed per-bee stats (incl. lifespan rating) appear on **hover + Shift** — layered disclosure, not always on screen.

**Design philosophy (GameDeveloper "Deep Dive" article):**
- Deliberately a **multi-window** system: any number of menus open at once, each a **draggable title-bar window** (Terraria/Minecraft's single-menu limit was the pain they fixed).
- Interaction inside menus is **drag-based crafting minigames** (drag to chop at the Sawbench, drag down to scrape propolis at the Uncapper) — the station menu is a tactile workspace, not just slots.
- **Left-side button placement** so controls stay reachable even if a window is dragged partly off-screen.
- Shift-click moves items between open menus; a menu can be flagged (orange button) as the shift-click target.
- Takeaway for us: Apico's station panel is INPUT (top-left) -> CONTAINER/PROCESS (middle) -> OUTPUT (right) -> STORAGE (bottom), with the slow living process (queen lifespan, frame fill) shown as bars/fills and pushed to hover/world-icon for at-a-glance status.

> Caveat for our case: Apico's apiary does NOT render the bees as living creatures inside the panel, and it has NO egg/larva/pupa stage slots. Breeding is abstracted to "queen lifespan bar -> offspring appear in output slots." Our compost bin needs an EXPLICIT life-stage display (egg/maggot/pupa + adults), which Apico alone does not model — so the life-stage UI must come from other husbandry games (below).

### Forestry (Minecraft mod) apiary GUI — OPEN-SOURCE CODE READ (the canonical apiary-station panel, Apico's ancestor)

Read the actual Java: `forestry/apiculture/gui/GuiBeeHousing.java`, `ContainerBeeHousing.java`, `ContainerBeeHelper.java` (ForestryMC/ForestryMC, branch mc-1.12). This is a real, shippable implementation of exactly our shape: a station that houses breeding insects AND produces output.

**Exact slot coordinates (panel is 176 x 190 px), from `ContainerBeeHelper.addSlots`:**
- **INPUT, left column, stacked vertically:** Princess/Queen slot at (29, 39); Drone slot directly below at (29, 65). Two inputs -> a queen.
- **LIFESPAN/PROGRESS bar, immediately LEFT of the input:** a **vertical 4px-wide bar** at (guiLeft+20, guiTop+37), height = `delegate.getHealthScaled(46)` (46px tall), color from `EnumTankLevel.rateTankLevel(...)` (green=full life -> red=nearly dead). Drawn bottom-up: `drawTexturedModalRect(x, y + 46 - height, ...)`. So the queen's remaining life is a thermometer-style vertical fill hugging her slot.
- **PROCESS MODIFIERS, middle column:** 3 Frame slots at (66, 23), (66, 52), (66, 81) — consumable frames that boost/alter production. (Optional; only if `hasFrames`.)
- **OUTPUT, right side, honeycomb cluster:** 7 product slots arranged in a hexagonal/diamond pattern around center ~(116, 52): (116,26),(95,39),(137,39),(116,52),(95,65),(137,65),(116,78). Deliberately laid out like a honeycomb, not a boring grid — the output area LOOKS like bee product.
- Selected output combs get a highlight sprite drawn 3px around the slot (`SELECTED_COMB_SLOT.draw(... slot.xPos-3, slot.yPos-3)`).

**Status & flavor via SIDE LEDGERS (fold-out tabs on the panel edge), from `GuiBeeHousing.addLedgers()`:**
- `addErrorLedger(delegate)` — why the bee isn't working (wrong climate, no flowers, no sky, night, too crowded). Expands on hover/click.
- `addClimateLedger(delegate)` — temperature/humidity the housing provides vs. what the bee wants.
- `addHintLedger` — rotating flavor/tip text.
- owner/ownership ledger.
- The main panel stays clean (slots + bars); all the descriptive/diagnostic text lives in collapsible edge tabs. **This is the pattern to steal for our flavor DESCRIPTION + "why aren't the flies breeding" status.**

Takeaway: Forestry independently arrives at the SAME spatial grammar as Apico — INPUT (left, vertical) + a life bar hugging it, PROCESS mods (middle), OUTPUT (right, themed cluster) — and adds fold-out ledgers for status/flavor so the working area stays uncluttered.

### The life-stage / maturation displays (the piece Apico + Forestry DON'T have)

**ARK: Survival — Egg Incubator + maturation (the cleanest multi-slot life-stage pattern):**
- An incubator holds up to 10 eggs **simultaneously, each in its own slot**, each with its OWN progress.
- An egg shows **two bars**: an "Incubation" progress bar (how close to hatching) and an "Egg Health" bar.
- After hatch, a baby runs a **maturation progress bar** through **named stages** (Baby -> Juvenile -> Adolescent -> Adult). The stage name + a % maturation are shown together.
- Directly adoptable: our fly brood = per-stage SLOTS, each stage showing a COUNT and the front-of-queue individual's **maturation bar**; stage names (egg -> maggot -> pupa -> adult) read as the pipeline.

**Empires of the Undergrowth — brood + food-gated growth + count pair:**
- Population shown as a **pair of numbers: active / max** (max derived from how many brood tiles/slots exist). Clean, glanceable capacity readout — good for "resident adult flies: N / cap."
- Eggs -> larvae -> pupae -> workers are **visibly different sprites** as they develop; growth **stalls without enough food** (a larva stops mid-growth if underfed). Ties the creature life-stage directly to the station's "fuel" (for us: the compost/organic input feeds the maggots — a great mechanic + a reason the creatures share the panel with the materials).

**Creatures / Docking Station — a station that HOUSES living creatures + tracks life stage:**
- Creatures live in the world/station; a **side management panel** tracks each creature's **life stage** and enforces a **breeding limit/count** (raise the cap to allow more eggs to hatch). Confirms the pattern: creatures rendered living in the space, a side/aux panel does the accounting (stage + counts + caps).

**Stardew fish pond — houses breeders, glanceable population + world-side output:**
- One species per pond, **capacity X/10**, population grows by completing requests; produce drops into a **chum bucket collected by clicking** the pond. Reinforces: keep the "creatures live here" readout to a **count + capacity**, render the creatures in the WORLD, and make OUTPUT a simple click-to-collect.

### How flavor/description is presented "on open"

- **Forestry:** a fold-out **hint ledger** (rotating tip/flavor text) + an analyzer info panel — descriptive text is a collapsible edge tab, never clutters the working slots.
- **Apico:** per-bee/per-item **descriptions surface on hover** (tooltip) and in a bee-pedia; the station menu itself stays functional.
- **Cozy farming UI kits (commercial asset packs)** standardize the pattern: a panel has a **header plaque** (name) at top and neutral body slots/bars/portrait-rings below — i.e., the accepted place for a station's identity + one flavor line is a **title header plaque at the top of the panel**.
- Synthesis for us: show the DESCRIPTION as a **header block at the top of the panel on open** — station name + a one-line italic flavor sentence — optionally collapsible to a small (i) after first read, so it greets the player once but doesn't eat space every time.

---

## (a) SOURCE TABLE

| Source | Concrete technique | Fits our constraints? (Unity uGUI, one reusable panel, processes AND houses breeders) |
|---|---|---|
| Apico apiary/beehive (wiki.gg Beehive; halfglassgaming apiary guide) | Single panel, spatially zoned: INPUT 2 slots top-left -> merge; FRAMES middle (container/process); OUTPUT 3 offspring slots right + produce slots; STORAGE 6 slots bottom. World hive shows a **mini lifebar** + a **"frames full" special sprite**. | YES — the master template for INPUT/PROCESS/OUTPUT/STORAGE zoning + glanceable world-icon status. Doesn't cover life-stages. |
| Apico UI philosophy (GameDeveloper "Deep Dive") | Draggable-window menus; **left-side controls** (survive off-screen); tactile drag minigames inside; shift-click transfer with a flagged target menu. | PARTIAL — the drag-window multi-menu system is bigger than we need; adopt the left-side-controls + tactile feel, not the whole window manager. |
| **Forestry apiary GUI — source code** (`GuiBeeHousing`/`ContainerBeeHelper`) | Exact 176x190 layout: INPUT left column (queen (29,39) over drone (29,65)); **vertical 4px lifespan thermometer** hugging input at x=20, color green->red; FRAME mods middle column x=66; **honeycomb-clustered OUTPUT** right (~116,52); **fold-out side LEDGERS** for error/climate/hint/owner. | YES — near-1:1 with our need; the vertical life-bar-beside-input, themed output cluster, and side ledgers for status/flavor all port cleanly to uGUI. Best single reference. |
| ARK incubator + maturation (ark.fandom / dododex) | Multi-egg slots, each with **incubation bar + health bar**; post-hatch **named maturation stages** (Baby/Juvenile/Adolescent/Adult) with a maturation %/bar. | YES — this IS our egg/maggot/pupa stage slots + per-stage maturation bar + counts. |
| Empires of the Undergrowth (fandom Basic Mechanics; wiki) | **active/max count pair**; visibly distinct egg->larva->pupa->adult sprites; **growth food-gated** (starving larva stalls). | YES — count-pair for residents/capacity; ties brood growth to the station's fuel (compost feeds maggots). |
| Creatures / Docking Station (creatures.wiki; DS manual) | Creatures live in the station; **side panel tracks life stage + breeding-limit count/cap**; raise cap to allow more hatching. | PARTIAL/YES — confirms "creatures live in the world, side panel does stage+count+cap accounting"; validates a breeding-cap knob. |
| Stardew fish pond (SDV wiki; gamerant/thegamer guides) | One species; **capacity X/10**; **click pond to collect** produce from a bucket; population grows via requests; world sprite shows the creatures + a quest "!". | YES (as a restraint) — keep the resident readout to count+capacity, render flies in the world, click-to-collect output. |
| Cozy Farming UI Kit (Nexa Visuals, itch) — commercial art reference | Panels standardize a **header plaque** + body of slots/bars/**portrait rings**; category kits for inventory/crafting/modal. | YES — where the flavor DESCRIPTION + station name live (header plaque); portrait-ring motif for resident-adult avatar. |

Deep-read in full (WebFetch / code): GameDeveloper Deep Dive; apico.wiki.gg Beehive; halfglassgaming apiary guide; Forestry `GuiBeeHousing.java`; Forestry `ContainerBeeHelper.java` (+ container dir listing). Searched ≥6 angles (by-game Apico x2, by-technique apiary/husbandry UI, by-problem creatures-in-a-station-panel, by-community reddit/itch/github, open-source code). Fish pond wiki (403) and forestryforminecraft.info (refused) failed to fetch — covered via secondary guides.

## (b) Adoptable LAYOUT patterns

**The load-bearing pattern (Apico AND Forestry independently agree):** a station panel reads left-to-right as a PIPELINE — **INPUT (left) -> PROCESS/CONTAINER (middle) -> OUTPUT (right)** — with the slow "living" progress shown as a **bar hugging the thing it describes**, and diagnostic/flavor text pushed to **collapsible side tabs or a top header** so the working slots stay clean.

Concrete rules to adopt:
1. **Left = INPUT.** Where the player loads organic items. One-or-few slots, top-left (both refs put input top-left). Controls on the left survive if the panel is ever partially off-screen (Apico rule).
2. **A progress bar HUGS the process, not floating elsewhere.** Forestry's lifespan thermometer sits 1px left of the queen slot; Apico fills the frames in place. For us: the compost **conversion progress** should be a bar/fill on the compost mass in the CENTER, reading input -> compost.
3. **Right = OUTPUT, and theme its shape.** Forestry clusters output as a honeycomb; Apico stacks offspring slots on the right. For us: a small OUTPUT area on the right (finished compost), themed (dark crumbly icon), click/drag to take. Keep it visually distinct (product, not ingredients).
4. **Separate "MATERIALS PROCESSING" from "CREATURES LIVING HERE" with a hard visual band.** This is the one thing neither Apico nor Forestry does in-panel, so we design it: put the input->process->output pipeline as the TOP band, and a **visually distinct lower band (different background tint / a separator rule / a "vivarium" framed window)** for the fly brood. The creatures area should read like a little terrarium window, not more inventory slots — a framed viewport with the brood inside, so the eye instantly separates "stuff I process" from "critters that live here."
5. **The creatures area = stage lanes + counts + one maturation bar + resident adults** (ARK + Empires): a left-to-right lane of **EGG -> MAGGOT -> PUPA** each showing a **count badge**, plus a single **maturation bar** for the brood as a whole (or the front individual advancing), and a **resident ADULTS** readout as a **count/cap pair** (Empires "active/max") with a small portrait-ring avatar (UI-kit motif). Optionally render 1-2 live adult fly sprites walking in the viewport for life.
6. **Glanceable status without opening** (Apico): the compost bin's WORLD sprite should show a **mini progress pip/lifebar** and a **"ready" glow when output is full** — so the panel is for management, not monitoring.
7. **Status/flavor in ledgers or a header, never inline clutter** (Forestry): "flies need more wet scraps," "too dry," "brood at capacity" belong in a small status line or an (i)/warning icon, not spammed across the panel.

## (c) Flavor / description on open

Recommended: a **header plaque at the top of the panel** (station name in a title bar) with a **one-line italic flavor sentence beneath it**, shown every open but visually lightweight (dim italic, smaller than body text). This matches the cozy-farming-UI-kit convention and reads instantly. Rationale over the alternatives:
- Forestry's fold-out **hint ledger** is great for rotating tips but hides the flavor behind a click — worse for a "shown when the panel opens" requirement.
- Apico's hover-tooltip description is discoverable-only — also fails "on open."
- So: header flavor line for the always-on identity; optionally ALSO a small (i)/hint tab for longer lore or the rotating "what the flies need" tips (Forestry-style), so the header stays to one sentence.
- Keep it in plain, in-world voice (per project memory: plain language, say what the thing IS), e.g. *"A warm heap of rotting scraps. Flies love it here — and so do the worms turning it to black gold."*

## (d) Candidate layout sketches for OUR compost bin

### Sketch A — "Pipeline on top, terrarium on the bottom" (RECOMMENDED)
```
+-----------------------------------------------------------+
|  COMPOST BIN                                        [X]    |  <- header plaque
|  "A warm heap of rotting scraps; the flies love it."      |  <- italic flavor (on open)
+-----------------------------------------------------------+
|  INPUT            PROCESS (the heap)          OUTPUT       |
|  +----+ +----+    [======= 63% =======]       +----+       |
|  |scr | |scr |     input --> compost           |comp|  <-- click to take
|  +----+ +----+     (fill bar over heap art)    +----+       |
|  load organic      (warmth/moisture pip)       finished     |
+----------------------- vivarium band ----------------------+  <- hard separator
|  ~ LIVING IN THE COMPOST ~                Adults: 4 / 6    |
|  +---------+   +---------+   +---------+     ( o )( o )     |  <- resident adult
|  |  EGGS   |-->| MAGGOTS |-->|  PUPAE  |     avatars/portr. |
|  |   x12   |   |   x7    |   |   x3    |                    |
|  +---------+   +---------+   +---------+                    |
|  next hatch: [####----] maturation                         |  <- one maturation bar
+-----------------------------------------------------------+
```
Pros: instantly separates "materials I process" (top) from "creatures that live here" (framed terrarium band, bottom); left->right pipeline matches Apico+Forestry; ARK-style stage lanes with counts + one maturation bar; Empires active/max adults; header flavor satisfies "on open." Reads in one glance.
Cons: two horizontal bands make the panel fairly TALL — need to budget vertical space in uGUI; the terrarium viewport is extra art to make it feel alive.

### Sketch B — "Apiary-faithful: vertical input + honeycomb output, creatures as a right-side column"
```
+-----------------------------------------------------------+
|  COMPOST BIN    "...the flies love it."            [X]     |
+-----------------------------------------------------------+
| |I|  INPUT     FRAMES/HEAP        OUTPUT     |  BROOD      |
| |I|  +----+    [ heap art ]       (o)(o)     |  egg  x12   |
| |I|  |scr |    [==58%=====]      (o)(o)(o)   |  mag  x7    |
| |I|  +----+     (conversion)      (o)(o)     |  pup  x3    |
| ^life+----+                       cluster    |  ---------  |
| bar  |scr |                                  | mat [###-]  |
|      +----+                                  | adults 4/6  |
+-----------------------------------------------------------+
```
(|I| = the vertical conversion/"heat" thermometer hugging the input, Forestry-style.)
Pros: closest to the named reference (Apico/Forestry) — vertical input + life-thermometer + honeycomb output cluster; compact, wide-but-short; brood as a tidy right column. Cons: the creatures area is just another column of slots — it does NOT read as "creatures living here," it reads as more inventory; weaker on the owner's "creatures using the station" feel; the honeycomb output motif is bee-specific, less apt for compost.

### Sketch C — "Terrarium-first: the bin IS a cross-section, slots docked around it"
```
+-----------------------------------------------------------+
|  COMPOST BIN     "black gold in the making"        [X]    |
+-----------------------------------------------------------+
|  INPUT  |          CUTAWAY OF THE HEAP           | OUTPUT |
|  +----+ |   .-~ flies ~-.      (o) adult          | +----+ |
|  |scr | |   egg* egg*  maggot~   pupa#            | |comp| |
|  +----+ |   [====== compost 63% ======]           | +----+ |
|  +----+ |   moisture [##--]  warmth [###-]        |        |
|  +----+ |   Adults 4/6   next hatch [####--]      |        |
+-----------------------------------------------------------+
|  egg x12   maggot x7   pupa x3   (counts under the scene)  |
+-----------------------------------------------------------+
```
Pros: most alive/diegetic — the brood is literally shown living in a cutaway of the heap (creatures and materials share one scene, which is the truth of a compost bin); strong "polished commercial" wow. Cons: hardest to build well (animated cutaway + readable overlaid counts is real art+layout work); risk of clutter — counts/bars overlapping the scene can get busy; least like a conventional slot panel, so drag-load/collect affordances need care.

## (e) What a skeptic would say we missed

1. **Apico's apiary doesn't actually show life-stages** — we're grafting ARK/Empires onto an Apico skeleton. Make sure the grafted "brood band" still feels like one coherent panel, not two games stapled together. (Sketch A's hard separator + shared visual language is the mitigation.)
2. **"Creatures living here" is usually shown in the WORLD, not in the menu** (fish pond, Empires brood tiles, Creatures). A skeptic asks: should the flies be a menu widget at all, or should the panel just show COUNTS while the actual flies buzz around the bin in-world? Given our sim already has client-authoritative bug behavior, maybe the panel shows counts + stages and the WORLD shows the living flies — cheaper and more alive. Decide this deliberately.
3. **Determinism/authority:** brood counts + maturation are sim state — the panel must be a READ-ONLY VIEW of server/sim state (like Forestry's `delegate.getHealthScaled`), not a place that mutates bug state. (Project law: bug behavior is client-authority/deterministic; the panel must not fork it.)
4. **Vertical budget (uGUI):** the recommended two-band layout is tall. On a fixed canvas this may crowd; verify against our other station panels' size, and consider a tab/collapse for the brood band if space is tight.
5. **Feature creep vs. Apico's restraint:** Apico keeps each menu to a few slots + bars and pushes detail to ledgers/tooltips. We risk cramming input+process+output+3 stage lanes+maturation+adults+flavor into one screen. A skeptic says: prove each element earns its place; consider hover/expand for the brood detail so the default view is calm.
6. **Input/output granularity unspecified:** how many input slots? a single "insert scraps" bucket vs. multiple ingredient slots changes the layout a lot. Apico uses few; recommend ONE input drop-zone (accepts any organic) unless recipes demand more.
7. **Empico/Empires food-gating implies a coupling we haven't designed:** if maggots need the compost as food, an empty/finished bin should stall brood growth — is that our intended mechanic? It's a great one, but it's a design decision, not just UI.
8. **No Unity-native open-source station panel was found** to copy wholesale — the code reference is Java (Forestry). The layout/logic ports fine, but there's no drop-in uGUI prefab; budget the RectTransform/anchoring work.
9. **Accessibility/colorblind:** Forestry's lifespan bar encodes state as green->red color only. Pair every bar with a number/label (maturation %, X/Y counts) so it isn't color-only.

## Recommendation

Adopt **Sketch A** as the direction: keep Apico/Forestry's proven **left-to-right INPUT -> PROCESS -> OUTPUT pipeline** as the TOP band with the **conversion bar drawn on the heap itself**, and add a **visually distinct lower "vivarium" band** for the flies — **egg/maggot/pupa stage lanes with count badges + one maturation bar + an Empires-style `adults N/cap` readout with small portrait avatars** (ARK + Empires). Present the **flavor DESCRIPTION as a header plaque + one italic line on open** (cozy-UI-kit convention), and push "why aren't they breeding / too dry" **status into a small line or (i) tab** (Forestry ledger idea). Show glanceable **progress + ready-glow on the WORLD sprite** so the panel is for managing, not monitoring, and render the **living adult flies in the world** (with the panel as a read-only count view) to get "alive" cheaply and keep the panel calm. Treat the whole panel as a **read-only view of deterministic sim state** — never a place that mutates brood.
