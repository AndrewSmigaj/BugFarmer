# Cold-critic pass — compost-bin panel synthesis

Adversarial review of `SYNTHESIS.md` against the three research docs, the REAL code, and my own
web research. No cheerleading. Findings are ordered most-material first. Each cites evidence.

Status: IN PROGRESS (written incrementally so nothing is lost).

---

## What actually checks out (stated up front, briefly)
Verified against the real source so the critique below is fair:
- **"Compost is CONTINUOUS, no Start button"** — CORRECT. `handleStationDeposit` just increments
  `st.InputCount` (`handlers_farming.go:1354`); `processStations` (`:1406+`) converts one input → one
  compost every `process_ticks`. No discrete batch/commit. Dropping Stardew/Portia's "Start" is right.
- **"Compost residents aren't emitted server-side yet"** — CORRECT, and I verified it below the doc:
  residents come from `nest.ResidentSwarmID` only (`brood.go:417-421`); `messages.go:189` says
  `Residents … (nests today; 0 otherwise)`; `brood.go:401` "nests today; compost later". Compost is a
  `StationState`, not a `NestState`, so its resident count is always 0 today. The panel already
  auto-hides the resident slot when count==0 (`CraftingPanel.cs:640`).
- **The color-clash bug is real** — `_stCompostFill` = `(0.45,0.8,0.3)` (`:512`) and `_broodBar` =
  `(0.55,0.85,0.4)` (`:598`) are both green. (But see Finding 6 — the fix is over-sold.)
- **Bars must stay out of layout groups** — CORRECT. `SetBar` writes `sizeDelta.x` every frame
  (`:557`). A layout group would fight it. (Synthesis cited `:553`, the method decl; the write is `:557`.)

So the "corrections I made to the research" section is sound. The problems are elsewhere.

---

## Finding 1 — WRONG/UNVERIFIED: the fly brood has a PUPA stage in the code+data, which the canonical design doc forbids. The synthesis's 3-lane sketches sit on an unreconciled three-way contradiction. (MOST MATERIAL)

The synthesis, both research docs, and every hero sketch draw the compost/fly brood as **three lanes:
egg → maggot → PUPA** (SYNTHESIS Block B; apico Sketch A "EGGS→MAGGOTS→PUPAE"; automation Candidate A
"egg[▦]12 larva[▦]5 pupa[▦]2"). Nobody checked this against the decision doc or the data. All three
disagree:

- **Design doc (canonical):** `architecture_nursery_stations.md:73-75` — *"Stages in this scope — egg →
  larva → adult (NO pupa). The village nursery bugs (flies etc.) are egg → larva → adult. Do not add a
  pupa stage here — pupae are part of the deferred extended lifecycle."*
- **Data:** `nakama/data/species.json:62` — `fly_common` has `"pupa_sprite_id": "fly_pupa"`.
- **Server sim:** `brood.go:250-252` `broodPupates` = `sp.PupaSpriteID != ""` for **any brood, source OR
  nest** (comment: *"Holometabolous bugs (fly/butterfly/beetle …) pupate"*). So a fly's COMPOST/ground
  brood really does run egg→larva→**pupa**→adult and counts `b.Pupae`.
- **Client panel:** `CraftingPanel.cs:623-628` shows a stage slot whenever its sprite id is non-empty and
  binds `b.pupae`. → the compost bin **will render a populated pupa lane for flies today.**

So the as-built game shows 3 fly stages; the canonical decision says 2. The synthesis is silently building
on the side of this that the decision doc explicitly forbids — and never flags the conflict. This is the
exact "verify at the load-bearing altitude" scar: the stage-lane count is a core layout parameter (it sets
the vertical budget and the maturation-bar semantics) and it was asserted, not verified.

**Why it has teeth (not a free UI tweak):** you cannot reconcile it in the panel alone.
- Make the doc true (drop fly pupa) → blank `fly_common.pupa_sprite_id` → `broodPupates` flips to false →
  flies stop pupating → **that is a determinism change** to `brood.go`'s stage ladder/hatch timing
  (`world/CLAUDE.md`: editing this package is a determinism change; needs the `test-changes` gates).
- Hide the lane in the client only (leave the sprite) → server still counts `b.Pupae>0` while the UI drops
  it → the pupae silently vanish from the player's view (a worse bug).
- Make the code true (accept fly pupae) → just update the design doc — but then the "no pupa for flies"
  decision (and the extended-lifecycle plan that leans on it) is wrong.

**Fix:** the synthesis must carry this as a BLOCKING reconciliation (owner call: is the fly bin 2 lanes or
3?) before it commits its sketches to a lane count. Right now it launders a contradiction as settled.

---

## Finding 2 — MISSING TECHNIQUE: the synthesis dropped the single most-reused signal in the genre — the world-object "ready / working" status indicator.

Both research docs flagged it as load-bearing (apico pattern #6 "Glanceable status without opening" +
Apico's world hive mini-lifebar and "frames-full" special sprite; automation R8 "hover mini-bar on the
world object"; stardew research calls the ready-bubble *"the single most reused readable signal in the
genre"*). The SYNTHESIS's five load-bearing conclusions, its corrections, and its "decided by me" list
**never mention it once.** It survived only as the buried maturing-pile art idea.

My own web check confirms it is THE genre convention, not a nice-to-have:
- Stardew: *"When a machine … is done processing, it will have a little icon bubble above it … simply look
  for the bubble icon above your machines to know when processing is complete"* — the entire ecosystem of
  "Machine Status / Detailed Machine Statuses" mods exists only to EXTEND this on-world signal, proving
  players navigate by it. (Stardew Forums thread 1957; Nexus mods 44371, 11177.)

This is the "panel is for managing, not monitoring" principle the research explicitly endorsed and the
synthesis silently discarded. **Fix:** make a world-object status a first-class deliverable — a small
"compost ready / brood hatching" pip or soft glow on the bin sprite (reuses the existing bar-draw; cheap),
so the player reads state without opening the panel. This matters MORE for us than Stardew because our bin
runs continuously and the player will rarely have a reason to open it.

Sources: <https://forums.stardewvalley.net/threads/graphic-to-indicate-kegs-preserves-jars-and-casks-are-processing.1957/>,
<https://www.nexusmods.com/stardewvalley/mods/44371>

---

## Finding 3 — MISSING TECHNIQUE: the panel must serve CHESTS, but the synthesis gives chests nothing (no quick-stack / deposit-all / sort).

The whole justification for the design is "one reusable panel across compost / nest / beehive / chest /
craft." The synthesis dispatches chests in three words — *"chest = a plain grid"* — and never revisits
them. But a plain grid is below genre bar for a storage panel.

My web check: quick-stack / deposit-all / sort is standardized QoL across exactly the peer set:
- **Core Keeper** puts a quick-stack button *next to the chest inventory* that auto-merges duplicates.
- **Stardew / Terraria / Minecraft** all ship "quick stack to nearby chests" (Terraria's is the origin);
  it's described as *"common QoL across multiple cozy farming and crafting games."*

For a panel whose reason to exist is reuse, shipping the storage mode with none of the affordances every
peer has is a real gap — and it interacts with the output work: the synthesis only says "Get all" for
Block C, but the same convenience-button row (take-all / deposit-all / sort) is what the storage AND output
modes both want. **Fix:** design a small optional convenience-button row into the reusable panel
(sort / deposit-all / take-all), shown for storage + output modes. Cheap, and it's the difference between
"a grid" and "a storage panel."

Sources: <https://www.curseforge.com/minecraft/mc-mods/quick-stack-to-nearby-chests>,
<https://www.nexusmods.com/stardewvalley/mods/10384> (Convenient Inventory / quick-stack)

---

## Finding 4 — RANKING: the pick's "narrow-fit = 5" is unverified, and the rejected accordion (E) is the honest choice for the MULTI-STATION reuse the mandate cares about.

The scoring gives **A = 4·5·5·4·5** vs **E = 4·5·5·3·5** (Apico·read·fit·cost·reuse). Two problems:

1. **A's "narrow-fit = 5" is not evidence-backed — it's width-only.** Both research docs list vertical
   HEIGHT/overflow as UNMEASURED (automation skeptic #3: *"Vertical height / overflow is unmeasured … Plan
   for a ScrollRect"*; apico skeptic #4: *"the recommended two-band layout is tall"*). A ~320px column that
   overruns the screen HEIGHT fails to fit just as badly as one too wide. Compost stacks deposit(2 rows) +
   input bar + compost bar + BROOD header + 3 stage slots + count row + maturation bar + resident slot +
   (new) output — that is tall, and the synthesis's answer is "wrap `_content` in a ScrollRect," i.e. a
   scrolling cozy station panel, which is exactly the clunky outcome. Scoring fit = 5 puts a thumb on the
   scale for the incremental option.

2. **E (accordion) is the candidate that actually solves the unmeasured-overflow problem the pick punts on**
   — collapsing sections is the standard fix for "a reusable panel whose content varies wildly per station"
   (chest = plain grid; craft = wide 3-col; compost = A+B+C; nursery = B-only; beehive = B+C). The
   synthesis's SOLE objection to E is "it hides live state" — but E already carries **summary chips**
   (`🌾6/10 🟫4/10 · egg12 ⏳72%`) on collapsed headers, and you can **auto-expand the active station's
   sections** so compost still shows everything live while chest/craft collapse what they don't use. With
   that, E's one weakness evaporates and it strictly dominates A on the mandate's stated axis (reuse across
   5 very different station types) while being overflow-robust. The honest verdict is **A ≈ E**, and for
   "one panel that also serves chest/craft/nest/hive" E is at least co-equal, arguably the pick.

I'm not saying A is wrong — it's the lower-risk incremental path and that's legitimate. I'm saying the
ranking is presented as decisive when it rests on an unverified fit score and an objection to E that E
already answers. **Fix:** measure the stacked height against the real canvas FIRST; if A+B+C overflows,
E's collapse isn't a "runner-up pattern," it's the requirement.

---

## Finding 5 — the pick over-claims novelty: the panel ALREADY IS "Vertical Sectioned IPO."

`BuildStationContent` (`CraftingPanel.cs:485-517`) already stacks, top→bottom: header → 6×2 deposit grid →
input(amber) bar → compost(green) bar → `BuildBroodRegion` (3 stage slots + maturation bar + resident
slot), all absolute-positioned. So "PICK = Vertical Sectioned IPO" is a description of the **status quo**,
not a selection among alternatives. The real deltas are three small things: add an output block, re-hue the
maturation bar, and group into sections. (Also: the synthesis calls it a *"~700-line"* panel; it's **966
lines** — `wc -l`.) This isn't fatal, but the ≥4-candidate exercise reads as post-hoc ratification, and the
scope/risk framing should say plainly "we keep what's built and add 3 deltas," not "we chose a layout."

---

## Finding 6 — the "readability bug" fix is over-sold, and the synthesis's OWN bar rule is already violated in a more concrete way.

- The two green bars (`compost 0.45,0.8,0.3` @512; `maturation 0.55,0.85,0.4` @598) are **not adjacent** —
  they're separated by the entire BROOD header + 3 stage slots + count row (~100px apart). The genuinely
  adjacent pair is input(amber)@505 vs compost(green)@512, 32px apart — and those are already distinct
  hues. So "two stacked green bars read as one meter" overstates it; re-hueing is a fine one-line change but
  it is independent of, and doesn't justify, any layout redesign.
- The more concrete, verifiable defect: the synthesis's rule is *"one determinate bar per process … always
  paired with a number."* The existing **maturation bar has NO numeric label at all** (`BuildBroodRegion`
  @596-599 creates `barBg` + `_broodBar` with no adjacent `TMP_Text`; the count labels @591-593 belong to
  the stage slots). So the synthesis states a rule it doesn't apply to the one bar it's redesigning. Fix
  both in one pass (hue + add the value), and note neither needs layout work.

---

## Finding 7 — CHEAPER APPROACH (80% for ~10%): invert the "satisfaction lever." Ship the world-ready signal + bar polish (no art) FIRST; the maturing-pile frames are a nice-to-have, not the load-bearing beat.

The synthesis names *"making the transformation visible … the compost visibly changes across ~3–4 frames"*
as *"the single biggest 'feels good' lever,"* costing new gpt-image-1 art. The genre evidence contradicts
the ranking: **Stardew ships NO maturing-material art** — its machines go idle-sprite → working-sprite →
bobbing ready-bubble, and that loop is the beloved genre benchmark for processing satisfaction. The
load-bearing beat is the **READY signal**, not the maturing animation.

So the cheap 80% path, all non-art one-liners on top of the working panel:
1. World-object "ready / hatching" pip or glow on the bin sprite (Finding 2) — Stardew proves one bobbing
   icon carries the whole "come collect" payload with zero maturing frames.
2. Hue-fix + number on the maturation bar (Finding 6).
3. An "accepts: fruit, crops, dead bugs…" hint so players know what composts (the panel filters to
   `StationAccepts` @524 but never surfaces it).

That's the bulk of the felt improvement for near-zero cost and no art spend. The 3–4-frame maturing pile is
a real polish upgrade, but it should be sequenced AFTER the ready-signal, not sold as the primary lever.
(This is a research-answerable correction to the synthesis's own priority, not an owner taste call.)

---

## Finding 8 — DESIGN FLAW that bites: the compost bin's headline "alive" feeling is entirely vaporware today, and the "determinism-safe" justification is a category error.

The synthesis presents as a DECIDED win: *"Living flies render in the WORLD; the panel is a read-only
count/stage view … determinism-safe … respects the client-authority bug-sim law; the brood counts already
arrive via the server's BroodUpdate broadcast."* Two problems:

1. **For the compost bin specifically, the "alive" story doesn't exist yet.** Residents are emitted only
   for nests (`brood.go:401`, `messages.go:189` — verified in Finding-prep), and compost is a `StationState`
   with no `ResidentSwarmID`, so the "adults inside" count is structurally 0 and there is **no
   resident swarm of flies the bin owns to render in the world.** So "living flies render in the world +
   panel shows the count" is, for compost, hollow until the unbuilt server bit lands. The synthesis
   half-admits residents are empty, then still lists the world-flies life as a decided feature. Honest
   statement: **today the compost panel is brood stage-lanes + bars only; the adults-inside + owned
   world-flies life is gated on unbuilt server work.** Don't sell it as shipped.

2. **The "determinism-safe / respects the client-authority bug law" reasoning is wrong.** The brood engine
   (`brood.go`/`processBroods`) is **server-side**; brood counts reach the panel via a **server broadcast**
   (`broodUpdateMessage`, OpCode 104) — that is NOT the client-authoritative deterministic swarm sim. The
   client-authority/determinism LAW is about the live swarm (the flies buzzing in the world), which the
   panel never reads or writes. So "the panel is read-only, therefore it respects the client-authority bug
   law" invokes a law the decision doesn't bear on. Harmless as stated, but it will mislead whoever builds
   "render the resident flies in the world": those world flies ARE the deterministic swarm, and making the
   panel's server-broadcast count agree with the deterministic world render is a genuine sync question the
   synthesis has hand-waved as already-safe. Name it as an open question, not a settled invariant.

---

## VERDICT

**Sound enough to build the SKELETON from, NOT sound enough to finalize the design — one item is blocking.**

- The synthesis's fact-checking of its own "corrections" is genuinely solid (continuous deposit, residents
  not emitted, bars-out-of-layout, the color clash) — I re-verified each against source and they hold.
  The vertical-sectioned direction is the correct low-risk incremental path.
- **Blocking before build: Finding 1** — the fly-brood stage count (2 vs 3 lanes) is contradicted across
  the design doc, the data, and the sim, and it is NOT a free UI decision (one resolution is a determinism
  change). The synthesis's hero sketches commit to 3 lanes on the side the canonical doc forbids, silently.
  Resolve this (owner call) before committing the layout, because it sets the lane count, the vertical
  budget (Finding 4), and the maturation-bar meaning.
- **Fold in before build (material, cheap):** the world-object ready signal (Finding 2, the genre's #1
  technique, dropped) and re-sequence the satisfaction lever (Finding 7) so the no-art ready-signal ships
  first. Add chest affordances (Finding 3) to honor the reuse mandate. Measure stacked height and treat E's
  collapse as a requirement if A+B+C overflows (Finding 4).
- **Correct the reasoning (non-blocking):** the determinism-law justification is a category error and the
  "alive compost" feature is vaporware today (Finding 8); the novelty is over-claimed (Finding 5); the
  color fix is over-sold while the bar-has-no-number rule is self-violated (Finding 6).

Net: the bones are fine and the corrections are trustworthy, but do not treat the sketches as ready to
build — reconcile the pupa/stage contradiction first, and put back the world-status signal the research
found and the synthesis dropped.
</content>
</invoke>
