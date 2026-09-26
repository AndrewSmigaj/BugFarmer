# Compost-bin panel — design synthesis (PROPOSED, under review)

Merges the three research threads (`research-apico-apiary.md`, `research-stardew-compost.md`,
`research-automation-layout.md`). Status: **PROPOSED** — pending one cold-critic pass + owner taste calls.
Graduate the kept conclusion into `architecture_nursery_stations.md` once built + verified.

## What the three threads agreed on (the load-bearing conclusion)
1. **Layout = a vertical Input→Process→Output column of three clearly-labeled blocks** — because our panel is a
   narrow (~320px) column and a horizontal furnace-row can't fit it. (Automation thread's scored PICK = "Vertical
   Sectioned IPO"; Apico thread's "pipeline on top" and Stardew thread's "cozy vessel" are the same spine.)
   - **Block A — MATERIAL** (non-living): deposit grid → hopper fill bar → compost fill bar.
   - **Block B — LIVING** (the flies): egg/larva/pupa stage slots + counts + ONE maturation bar + resident adults.
   - **Block C — OUTPUT**: finished compost to take (+ any byproduct) + a "Get all". *(Gated on the output decision.)*
2. **A progress bar hugs the thing it describes; one determinate bar per process; distinct hues; always paired
   with a number.** (Forestry's lifespan thermometer beside the queen; Material-3 progress rules.)
   → **Fixes a real bug found in the code:** the compost fill bar (`0.45,0.8,0.3`) and the brood maturation bar
   (`0.55,0.85,0.4`) are both green and confusable. Re-hue the maturation bar (warm gold/teal) + keep the number.
3. **The living-creatures area is visually SEPARATED from the materials area** ("vivarium band" — a tint/rule/
   framed viewport), because a compost bin is genuinely two things (a processor + a home) and they must not blur.
   Apico/Forestry don't model life-stages at all, so the stage lanes are grafted from **ARK** (per-stage slots +
   a maturation bar + named stages) and **Empires of the Undergrowth** (`adults N/cap` count pair, food-gated growth).
4. **The panel is a READ-ONLY VIEW of sim state** — never mutates brood. Living adult flies are rendered in the
   WORLD; the panel shows counts/stages. (This is also the determinism-safe choice — respects the client-authority
   bug-sim law; the brood counts already arrive via the server's BroodUpdate broadcast.)
5. **Description on open = a header plaque + ONE italic flavor line** (cozy-UI-kit convention; Sun Haven's mold:
   *what it IS + what it DOES*, present tense). Diagnostic status ("too dry / brood at capacity") goes to a small
   status line or (i), not smeared across the panel (Forestry ledgers).

## Corrections I made to the research (self-verified against our code)
- **Our compost is CONTINUOUS, not a "Start batch".** Stardew/Portia layouts show a "Start composting" button;
  our server model deposits into an `InputCount` hopper that converts continuously to `Fill` (no discrete start).
  So **drop the "Start" button and the Portia commit-dialog** — keep the calm continuous "toss it in, it rots"
  model (which the research also calls the truest reading of a compost heap). Verified: `entities/station.go`
  StationState (InputCount→Fill), `handlers_farming.go` deposit path.
- **Compost residents aren't produced server-side yet** (residents exist only for nests today — per
  `architecture_nursery_stations.md` "Not built"). So the "adults inside" readout will be empty for compost until
  that server bit is added. Design the slot; don't promise data that isn't emitted.
- **Output block is pending the owner's output decision** — "remove the compost" is unbuilt (fertilizer = "later"
  in `station.go`). Reserve the space; populate it only when we build the take-out path.

## The ≥4 scored candidate layouts (from the automation thread, axes: Apico-feel · readability · narrow-fit · dev-cost · reuse)
- **A — Vertical Sectioned IPO** (3 labeled blocks stacked) — 4·5·5·4·5 → **PICK**. Cleanest top→bottom read, three
  ideas unmistakably separate, smallest delta from working code, subsets trivially for nursery/beehive/chest.
- **E — Collapsible accordion cards** — 5·4·5·3·5 → **runner-up / build-pattern**. Hides live state (bad default),
  but its "each block is a self-contained section object" IS how we build A with uGUI; adopt its structure + use
  collapse only for overflow.
- **B — Horizontal furnace IPO** — 3·4·1·3·2 → reject (can't fit 320px; we have 3 meters not 1 arrow).
- **D — Two-column split** — 3·3·2·3·3 → reject (cramped at 320px; breaks the vertical read).
- **C — Tabbed sections** — 3·2·5·3·4 → reject (hides the simultaneous "filling AND maturing" that makes it feel alive).

**Merged recommendation:** Build **A** using **E's section-object structure**, with the **Apico "vivarium band"**
styling for Block B and the **Stardew flavor header**. Bars stay OUT of any uGUI layout group (they set width
per-frame via `SetBar` — a layout group would fight them; verified `CraftingPanel.cs:553`). Migrate incrementally
— don't rewrite the working ~700-line absolute-positioned panel wholesale.

## The satisfaction lever (Stardew) — and its cost
The single biggest "feels good" lever is **making the transformation visible**: the compost visibly changes across
~3–4 frames (fresh green scraps → browning → dark crumbly humus) as it matures, as the hero visual, with the slim
bar underneath + a soft "ready" bob/chime. **This costs new art** (gpt-image-1 frames). Without it we still ship a
clean, correct panel; with it the bin feels alive. → an owner scope call (build the art now vs. clean bar first).

## Owner-taste decisions to surface (not research-answerable)
- **Output scope** (already asked): fertilizer-effect now / plain resource now / defer.
- **Maturing-pile art**: generate the 3–4 frame maturing-compost visual now (the satisfaction lever), or ship the
  clean bar version first and add the animated pile later?
- **Grub byproduct**: composting also yielding a few grubs/maggots (free bug food/bait) is a genre delight
  (Graveyard Keeper/Sun Haven) — but there's a balance flag (don't turn it into a farm-dead-bugs-for-compost loop).
  Include the byproduct or keep compost the only output?

## Cold-critic pass — resolutions (see COLD-CRITIC.md; each finding re-verified against real code)
- **F1 (was flagged "blocking"): the fly compost brood pupates (`brood.go` `broodPupates` = `PupaSpriteID!=""`,
  applied to compost broods; `fly_common` has one) while `architecture_nursery_stations.md` said "flies: NO pupa."**
  Resolved the way the owner already endorsed ("finally flies to have pupae, i saw that") + real biology (a
  housefly IS egg→maggot→pupa→adult): **keep the pupa, fix the stale doc** (done). The critic's framing ("drop
  fly pupa = a determinism change") had the direction backwards — the fix is doc→code, no sim change.
- **F2 (valid, fold into redesign): the world-object "ready/working" indicator was dropped.** Add a subtle
  world-sprite signal (compost "cooking" / a ready glow when output is full) so the panel is for managing, not
  monitoring — the most-reused, no-art, genre-standard cue (Apico mini-bar / Stardew ready-bubble).
- **F3 (valid, separate backlog — NOT compost scope): chests get no quick-stack / deposit-all / sort.** The
  reuse-across-5-stations axis shouldn't imply chests are polished; track a chest-affordances item separately.
- **F4 (valid, build detail): the pick's "narrow-fit=5" was width-only; vertical overflow is unmeasured.** Build
  A with E's section-object structure AND a ScrollRect (or collapse) for height. A≈E, not decisive — E's structure IS how we build A.
- **F5 (validates the sequencing): defer the maturing-pile ART.** Ship the no-art cheap wins first (accepts + bar
  hue/number + the world-ready signal); the animated pile is the owner's Q2 call, not a prerequisite.
- **Precision fixes:** the panel is a read-only view of the **server-broadcast** brood (OpCode 104) — NOT the
  client-authoritative swarm; rendering the living adult flies is the *swarm's* job in the world; the panel
  mutates neither (that's the accurate framing — my earlier "determinism-safe / client-authority" wording
  conflated the two). The maturation bar still needs a **% number** (honor "always pair a bar with a number").
  The panel is **966 lines**, not ~700.

## Decided by me (law-aligned / research-answerable — NOT questions)
- Living flies render in the WORLD; the panel is a read-only count/stage view (determinism-safe, cheaper, more alive).
- Per-species stage names from real entomology (fly=maggot, wasp=grub, butterfly=caterpillar+chrysalis, beetle=grub,
  bee=larva); "brood" only for true nests/hives.
- Continuous deposit (no Start button / no commit dialog).
- Deposit stays click-to-deposit for speed (the game has drag, but click is fine here; trivially changeable later).
