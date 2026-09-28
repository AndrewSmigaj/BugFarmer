# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

> **2026-09-26:** finished sections moved to [`CHANGELOG.md`](CHANGELOG.md); the ordered plan is
> [`ROADMAP.md`](ROADMAP.md). This file is the capture queue for open items.

## Now — ALL ART ON gpt-image-2 + pixelsnap (owner decisions 2026-09-26)

The owner's decisions (2026-09-26):
- **All art uses gpt-image-2 and pixelsnap**, including whole outfits (a tentative choice, made when the code-drawn
  pieces were rejected). The outfits are the only art made the right way so far; all world and item art is to be
  regenerated on the same pipeline, because the older route didn't convert its pixels properly.
- **The outfit procedure:** three design variants per outfit; the owner picks one; then all the animation frames are
  made. Most outfits and other art are made after the GDD is signed off, starting with test batches that check the
  work is done right.
- **Every design marked as chosen has been picked;** the others are worked through together. The copper test batch
  was approved to run.

Art drawn by Claude in code was tried the same day and rejected — kept only as a record:
`tools/sprites/drawn/`, `tools/_generated/player/reviews/2026-09-26-art-demo/` and `…/2026-09-26-base-pass/`.
The decision log with every pick is `tools/_generated/player/APPROVED/DECISIONS.md`.

**The procedure** (proven on fire-ant, black-ant and bronze, approved 2026-08-15): three designs in one image → the owner picks one (`explore/<run>/CHOSEN_<name>.png`) → the pick
turned into a real-pixel reference at the base's size → a front/side/back turnaround (1 image) → one walk per
direction (3 images) → the five hands (1 image) → a review sheet → only on his yes: `outfits/<name>/`,
`official.py`, `build.py`, `gallery.py`, `DECISIONS.md`. The step-by-step how-to is the `player-sprites` skill.
Every paid image call is asked for first.

**Outfits:**
- **Done on the procedure** (in `official.py`): bronze, fire-ant, black-ant (approved 2026-08-18) and **copper**
  (2026-09-26, the first made end to end by `procedure.py`; approved, with hand-position polish left for later).
- **Picked, still to build** (turnaround → walks → hands → review), each batch asked for first: iron (`iron-r2`),
  platinum (`platinum-r5`), steel (`steel-r5`), leather (`leather-r2`), beetle-shell (`beetle-shell-r3`),
  gilded-steel, fancy (`fancy-r2`). Gilded-steel and fancy have no words in `outfits.OUTFITS` yet — his, before
  their batches.
- **To work through with the owner, from the three-designs step:** explored but not picked (wood, ranger,
  scorpion, the wasp/hornet/killer-bee sets, glowworm, fisherman, swamp-gear) and never explored on this procedure
  (silver, gold, padded, beekeeper, farmer, entomologist, moth-wool, wizard-robe, …; their folders hold July art —
  full-size renders, never snapped). Two catalog concepts have no art at all: Miner / Spelunker, Diver / Waders.
- **After the GDD sign-off:** the remaining outfits, then the 11 NPCs (merchant, bug dealer, blacksmith,
  carpenter, weaver, stonemason, modern wares, fisherman, ecologist, mayor, beekeeper — all still the old 16×32
  size) on the same procedure.

**World + item art — regenerate everything, after the GDD sign-off, test batches first.** 775 images (Objects 431,
Items 185, Bugs 106, Tiles 29, UI 20, Effects 4) were made on the old route (a gpt render shrunk by
`pixelclean.py`, which averages pixels instead of recovering them). Only content the GDD keeps gets redone.
- **Density: 32 art pixels per grid square**, reached by snapping and padding, never by resizing. For a placed
  object that means an image exactly 2 × (`sprite_w`, `sprite_h`) — the game scales objects to their data size
  (`TilemapManager.cs:65, 1101-1103`).
- **The July grass is 16 pixels per square** (the 5 grass tiles are 16×16; the other 24 tiles are 32×32) — redo
  at 32.
- **Write one sizing rule first.** Items have no size in the data (0 of 209), and held tools, ground drops, strike
  effects, grass tufts and bugs size themselves from the image's pixel count or a code constant
  (`PlayerToolAnimator.cs:245-247`, `GroundItemVisual.cs:97-98`, `StrikeVfx.cs:110-111`, `GrassTuftRenderer.cs:31`,
  `SwarmVisual.cs:343-344`), so a sharper image would change their size on screen unless those change with it.
- **The route:** the outfit procedure pointed at world art — `gen.py` needs a `--root` option (it writes into the
  player folder today); magenta background (gpt-image-2 refuses the transparent one `gen_sprites.py` asks for);
  the per-family prompts reused unchanged, with the needed changes (magenta, the density line) shown to the owner
  as one diff; ~157 things with no written brief get one, shown before any call; keying checked for leftover
  magenta (fence holes, pink subjects); the 8 pre-made diagonal path tiles included. Overwrite each PNG in place
  so its `.meta` survives.
- `docs/product/art_needed.md` (the old missing-sprite queue) is superseded by this item.

**Built outfits into the game — its own plan, with the owner's decisions in it** (GDD §08). None of the new art is
in the game: the client still draws the old 16×32 farmer from layers (`CharacterComposer.cs`, `RemoteEntity.cs`),
and `PlayerToolAnimator.cs` still runs the old swing curves.
- Owner decisions needed: the **published size** — the art is 36×71 while the game's character is 16×32 at 16
  pixels per unit; decide against a rendered scene, not in the abstract; the **equip model** (the server checks 8 armour slots piece by
  piece, `handlers_world.go:812,867`; no item exists for bronze/fire-ant/black-ant — see *Armour economy overhaul*
  below); a **starter outfit**; what becomes of **class, hair and skin** choices (`CharacterSelectPanel.cs:28-30`);
  **tool motions** — 9 tools animate in the game, only the sword is approved in all three facings (axe, net, hoe
  and shovel side-only; pickaxe, scythe, spear and watering can none — `official.py` `NOT_AGREED`).
- Engineering: hands and tools drawn at their own pixel size (no runtime rescaling); the spring swing
  (designed, `docs/product/investigations/swing-design/`, `tools/player_sprites/swing_lab.py` approach 6) plus the 3
  defects it found (no exit blend, the tool draws through the body, the hand vanishes against its own armour);
  the nameplate assumes a 2-unit-tall player (`RemoteEntity.cs:212`). First piece (no decision needed): draw a
  whole-outfit frame behind a debug outfit id, to make the rendered scene the size decision asks for.

**Polish later** — several outfits are nearly done and need a polish pass later (owner, 2026-09-26). Known: the
camera-facing walks lift the knees too high — fine for a run, too much for a walk (owner, 2026-08-18; `check_lift`
flags 5 of the 6 front/back walks of the first three, and copper's front at 18%); copper's hand positions (owner,
2026-09-26); copper's back walk is 71 px tall against its front's 66 (a fresh roll of
that one direction is the fix). Also *Running improvements* and *Sprite pipeline cleanup* below.

## Next — RUNNING IMPROVEMENTS (owner 2026-08-14: backlogged, not for now)

Two motions are **picked but not built**. Both are lab renders only; nothing in the game or in `build.py`
does either of them.

- **`run_front` has no pose of its own.** `official.GAITS["FRONT_RUN"]` is byte-identical to `FRONT` apart
  from `ms` — the camera-facing run is the camera-facing *walk* played faster, which is the failure the side
  run already fixed. The owner judged the walk-sped-up version not to read as running. Picked
  `W3_widest_lowest`; numbers and the two rejected attempts are in
  `_generated/player/reviews/2026-08-14-run-front-pump/DECISION.md`.
  Building it needs a **`pulse`** term in `gait.walk_front_into` (fists grow/shrink with depth — it has no
  per-hand scale today), the numbers into `official.GAITS`, and a re-render.
  ⚠ **`run_back` shares `FRONT_RUN`**, so both change together. Whether the depth pulse should invert for
  the away-facing view is still open — rendered both ways, not decided.
- **Swing while running.** Picked half pump — the off arm keeps running at half the approved amplitude while
  the weapon arm takes the swing arc. `reviews/2026-08-14-swing-while-running/DECISION.md`. Needs a new
  animation kind: today a gait and a swing are separate rows in `official.ANIMATIONS` that never overlap.

## Later — SPRITE PIPELINE CLEANUP + IMPROVEMENTS (owner 2026-08-14: after the sprites are done, based on what worked)

Do this **after** the outfit run finishes, so it is built from what actually worked rather than guessed.
Known material, all learned the hard way today:

- **A brief is the MATERIAL.** Make it structural, not a habit: one shared `UNDIRECTED` constant for the
  three option slots, one shared face/head phrase, so writing a directed brief means overriding a named
  default. See `APPROVED/DECISIONS.md`, 2026-08-14.
- **Guard against duplicate keys in `EXPLORATIONS`.** A repeated key silently discarded the undirected
  entry and rolled a directed one instead — one wasted call, and it looked like the model's fault.
- **The pixel-density anchor line works and is not applied everywhere.** *"Match the PIXEL DENSITY of the
  attached reference"* fixed copper; the gauntlet prompt never got it and both gauntlets came back smooth
  and outline-less. The owner requires the gauntlets to match the outfits' pixel density.
- **Tier separation is measurable, so measure it.** Mean luma + shadow hue over the worn material, skin
  excluded. It found that steel had drifted into silver's slot and that platinum's blue shadows were the
  real discriminator; the fix moved shadow hue +20 → +84. Worth a committed script rather than ad-hoc.
- **Two gauntlet paths exist** — the old 4-hand `GAUNTLET` and the 5-role `OFFICIAL_GAUNTLET`. The renderer
  needs five. fireant took three paid gauntlet calls because of this.
- **`render_animations.py` is stale**: its `frames_dir()` still looks at the outfit root, which predates the
  2026-08-06 move into `<outfit>/frames/`, so its loaders silently find nothing. `build.py` is the live one.

## Underground fortress — a secret, and the Queens' set (owner 2026-08-06)

The owner wants secrets in the world; this one is backlogged. A small built structure somewhere underground holding a **chest with a legendary armour recipe**. The set
needs parts from **BOTH colony queens** — the col-0 intro colony and the col-3 deadly one — plus rare
metals. Requiring both is the good part: it forces a traverse of the whole underground, east and west,
rather than grinding one place.

One of **two or three** most-powerful sets; a second is built on **spider plate** and is gated behind
Spider Vale by geography. Design notes: [`design/brainstorm_armor.md`](design/brainstorm_armor.md) §5.

Needs: a fortress structure (zonegen scene), a lockable/lootable chest with recipe contents, and the
queen-part drop items. None of those exist.

## Base village improvements (owner 2026-08-06 — placeholder, owner to fill)

The owner has things to add and improve in the village; this is the bucket for them. Known members so far:

- **Bug processing station.** A station that turns bugs into materials (owner, 2026-08-06).
  The `bug_extractor` placeable and its 8 recipes (carcasses → `chitin` / `leather` / `formic_acid`) already
  exist; what is open is its role in the village and in the armour ladder, since it is the source of the
  whole bug→material economy and gates the bottom two rungs (leather, then wood).

## Thorns — spiked armour hurts what runs into you (owner 2026-08-06)

The owner asked for the hornet thorn outfit to be redone so that enemies that run into you take damage. The
signature bonus of the **Chitin/Carapace** line. `stats_and_bonuses.md` already lists `thorns` under
that concept with status 🔴 **not built**, and there is nothing to hang it on yet: the entire armour system
in the sim is `sting_immune` (a bool) and `slot_bonus` (an int) — `entities.go:56-68`. No defense field, no
bonuses map, no `PlayerStats`.

- **Server-authoritative.** Player HP is server-only and sim-inert (`combat-enemy` skill), so reflecting
  damage back onto a bug is a server change. It kills bugs, so the kill must ride the ledger like any other
  (`BUG_REMOVED`, detect-don't-remove) or clients disagree about which bugs are alive.
- **Needs the `bonuses{}` block first** — this is the second armour stat ever, so it is really "build the
  armour-stat system, with thorns as its first customer".
- Reads naturally on: hornet (spined chitin), scorpion, centipede plate, pill-bug.

## Glowsticks and glow lanterns — a crafted light material (owner 2026-08-06)

The owner is considering a glowworm-outfit variant made from glowsticks, with glowsticks and glow lanterns both made
at the workbench. Workbench recipes for a **glowstick** and a **glow lantern**, which then become the material story for the
glowstick variant of the glowworm outfit — a *crafted* light set as an alternative to the *harvested*
glowworm one. Glowworms live in **Centipede Cavern (4,1)**; `light_radius` is 🔴 not built, so this pairs
with the lighting/mining bonus work.

## Armour economy overhaul — WHOLE OUTFITS, not per-slot pieces (owner 2026-08-05)

The player art moved to **whole-outfit sprite sheets** — one image per outfit, generated in a single
render. The owner moved to whole outfits because masking every individual piece wasn't workable.
The economy still assumes the old **per-piece** model, so it no longer matches the art.

**What has to change:**
- **Recipes.** Today there are separate recipes for individual pieces of equipment — helm, chest, legs,
  boots. Those become **one recipe per OUTFIT**. `nakama/data/entities/items.json` (`armor_slot`) and
  `recipes.json` both encode the per-slot model.
- **Costs.** A whole outfit is one purchase/craft, so the price ladder has to be rebuilt rather than
  summed from four pieces.
- **Armour slots.** If an outfit is one item, the multi-slot equip model may collapse to a single slot —
  that is a design decision, not a mechanical one, and it touches the server's equip handling.
- **Drops and vendors.** Same knock-on: what drops, what a shop stocks.

**Per-zone special outfits.** The owner expects one or two special outfits in each zone, including ones made from
natural materials. So the roster is partly **zone-gated content** — ant-carapace,
beetle-shell, moth-wool, glowworm and the rest are made from things a specific zone provides, and should
be obtainable there. That is a content-design pass over `docs/product/economy/zones/` as well as a
mechanical one.

**Not started.** Raised while building the fire-ant and black-ant outfits, which are the first two
material-sourced sets to go through the new whole-outfit flow.

## Stealth / reduced aggro — the spidersilk bonus (owner 2026-07-29, not built)
The spidersilk set's signature bonus: it makes you stealthier — roughly, bugs notice you less (the owner's
tentative description; backlogged). Nothing in the sim reads
a stealth stat today, so this is a real mechanic to design — bug aggro is CLIENT-authority per
`architecture_swarm_sync.md`, so anything that changes which bugs notice the player is a determinism-touching
change and goes through the `frontier-sync` recipe, not a cosmetic tweak.

> **STEALTH AND SPIDERS ARE ONE SPRINT (owner 2026-08-06).** Spiders give silk, silk is what stealth gear is
> made from, and stealth is a way through harder zones without fighting — so stealth and spiders are one sprint.
> They are the same feature: stealth needs a
> material, the material is silk, and **`silk` is currently an orphan item** — `items.json:1631` exists with
> no recipe and no bug that drops it. Spiders are the source. See *Later — creatures: ants & spiders*.
> Sequence: cave spider + webs → silk drops → the silk/`shadowsilk` set → the stealth stat.

> The rest of this item — the July "Player sprite + wearable creation system" record (22 outfits "built",
> a publishing to-do) — was folded into *Now — all art on gpt-image-2 + pixelsnap* at the top on 2026-09-26:
> those 22 were July renders, never pixel-snapped; three outfits are done on the approved procedure. Still
> open from it: the deferred `_generated/` root tidy (`scratch/` · `variants/` · category previews).
> `docs/plans/player-arm-and-wearables.md` (split arms) and `docs/plans/player-sprite-and-wearable-creation.md`
> are both superseded — kept for their findings.

## CLAUDE.md & scaffolding improvements (owner wants a pass here; captured 2026-07-09)
Umbrella for tightening how the assistant is steered. Add items here as they come up.
- **SCRIPTS AS REMINDERS — a cheaper hook (owner's idea, 2026-08-06).** Tools print reminders of the conventions
  they apply, as a lightweight kind of hook — provided their output is read. A tool that prints the convention it just applied fires exactly when it is relevant, cannot be
  routed around, and costs one `print()` — no manifest row, no session-start snapshot, no fail-open logic.
  **First instance is live:** `tools/player_sprites/review.py` `save()` prints the `C:/` path, that labels
  are 22pt (~2× PIL's default, because he has twice had to zoom in to read a comparison sheet), and warns
  when a review folder has no `README.md`. Worth spreading to the other generators — `gen_sprites.py`
  (which model is about to be paid for), `publish_entities.py`, the zone builders (re-save + re-render
  north-up before claiming a zone is fixed).
- **A skill for AUTHORING skills (owner, 2026-08-06).** `scaffolding-review` already covers *reviewing* a
  scaffolding change — levers, dimensions, gates, gotchas. What is missing is the authoring side: when a
  reminder should be a skill vs a hook vs a printed line in the tool vs a comment where the mistake is
  made, and how to tell whether it will actually change behaviour. Fold in the "scripts as reminders"
  pattern above and the 2026-08-06 lesson that **four rounds of better *records* did nothing because no
  code read them** — the fix was making the loader read the record, not writing a fifth record.
- **DONE 2026-07-15 — enforcement scaffolding landed (P0-P5; plan: `docs/plans/repo-health-enforcement.md`).**
  Built the manifest-driven hook system this section called for: `.claude/manifest.json` (one source) +
  `.claude/hooks/` (skill-read gates, doc-drift Stop hook + git pre-commit backstop, determinism Stop gate,
  plan-exit gate, prompt routing) + `nakama/modules/world/CLAUDE.md` + committed `docs/plans/`. System map:
  `.claude/hooks/README.md`. **Hooks go live at the NEXT session start** (Claude Code snapshots hooks at startup).
  STILL OPEN in this umbrella (deferred to owner review): the **server-data-reload reminder hook** (below) is now
  a ~1-row add to the framework (a PostToolUse Edit nudge on `nakama/data/**` + `tools/zonegen/**`); the
  **teach-as-we-go** and **token-optimization** items; and the owner's **scaffolding audit** (effort-pinning,
  trim CLAUDE.md to a router, skill scar-vs-guess review) + doc-hygiene (bugs_new.md dup, entity_sync stale).
- **Reminder HOOK: don't say "go test" after a server-DATA edit without reloading.** Recurring failure
  (many times): the assistant edits zone/server DATA, re-saves the file, then tells the owner to Play-test —
  but the running Nakama still serves the old in-memory match, so the owner hunts for things that aren't there.
  The knowledge IS documented (run-backend "restart on data changes"; bug-spawning "Gotcha #2 stale save"), but
  the assistant reliably **won't** read a skill/memory just because CLAUDE.md points to it — memory/CLAUDE.md
  reminders get buried in a large context and don't fire. So: a **reminder-style hook** (e.g. PostToolUse on
  Write/Edit under `nakama/data/**` or `tools/zonegen/**`) that injects a fresh nudge AT THE EDIT: *"server-data
  change — restart Nakama (and reset the persisted save for bug/edit cases) and verify BEFORE telling anyone to
  test."* **Reminder that nudges the assistant, NOT an auto-run script or hard block** — the owner needs the
  assistant's judgment in the loop (sometimes it needs to look at a specific thing), not a rigid runner. Will
  test whether it's a strong enough reminder in a fresh session.
- **The actual reload is simpler than the assistant made it (verified 2026-07-09):** authored occupants/ground
  come from the FILE (`LoadChunk` reads `nakama/data/zones/<zone>/chunk_*.json`; the save only layers player
  `CellEdits` on top — `world_save.go`). So for authored zone changes, **`docker compose restart nakama`** alone
  is enough (drops the cached match → re-reads the file). The DB wipe is only needed when the persisted SAVE
  masks the change: **bug population** (persists swarms → bug-spawning Gotcha #2) or a **player cell-edit** on a
  re-authored cell. The reminder hook should point at the simple restart first.
- **Make all sessions learning experiences (owner 2026-07-10).** A skill/scaffold — ideally triggered by a
  push (or other) hook — where the assistant ELI5s / teaches what it's doing as we go (concepts, why this
  approach, the trade-offs), so the owner actively learns software dev instead of being hand-waved through.
  The owner is building toward an AI-engineer role and wants to not let that part of the brain atrophy.
- **Audit our scaffolding — is it helping or caging? (owner 2026-07-10).** Review the skills / memories /
  CLAUDE.md / plan discipline and ask, per piece: what specific failure does it prevent (can we name it)?
  does it TRANSFER INFO the model can't have, or merely DICTATE METHOD / restate general competence? is it
  still true? Lens: **scar-born** scaffolding (from a real "burned us 3×" failure) = usually keep; **guess-born**
  (proactive theories of how an agent "should" work) = scrutinize hardest. Explicitly include the ASSISTANT's
  own habit of inventing rigid rules and over-constraining itself — that's a big source of caging, not just the
  docs. Prune noise/stale/method-dictation; keep info/corrections/taste.
- **Token-optimization review (owner 2026-07-10).** Owner has a guide (drafted in chat) on cutting token cost —
  both to run more projects and as a core modern-AI-engineer skill. Turn it into real practice/scaffolding:
  **compact early** (after a task completes, at direction pivots — don't just let context fill), prompt-**cache**
  awareness, and **richer up-front instructions to agents** so they don't waste turns re-discovering context
  (clear, streamlined briefs). Capture the guide into a doc/skill + habits.

## Shaped-ground builder — BUILT M0–M4 + S1 legibility rework (2026-07-09/10)
The shovel is a terraform builder: it places `matA~matB~shape` **composite ground ids** (two materials
blended through a runtime GPU mask-composite into one tile — see `architecture_shaped_ground.md`). A composite
is governed by its **primary material** (`PrimaryMaterial`) for gameplay. **S1 (2026-07-10)** made dig/place
legible after playtest: **LMB places** as a **recipe-craft** (`ground_recipes.json`; a composite costs BOTH
materials), **Shift+LMB digs** as a **progressive break** (2–3 hits, crack overlay, ~3s idle-reset) → the
recessed **`dug_soil`** tile + **drops the material(s) to the ground** like felling a tree; the mouse wheel
cycles **shape only**; and a game-wide **world-error toast** (`WorldToast`, OpCode 40) surfaces every refusal
("Need 2 stone"). Server-tested (`shaped_ground_test.go`). **Remaining (S2–S4 + owner passes):**
- **S2 — "Set Materials" panel — BUILT, verify + pick layout:** `UI/ShovelBuilderPanel.cs` (open with `B`) —
  composited-tile swatches + material-B row + live have/need (`Data/GroundRecipeDatabase.cs`), unaffordable
  dimmed; additive over the dev HUD + temp M/N keys. Two layouts rendered (`tools/sprites/shovel_panel_mockup.py`,
  option A built). Owner: pick A vs B; confirm it compiles + reads in-engine (blind-built, no Unity here).
- **S3 — preview/GIF tooling — BUILT:** `tools/sprites/composite_tiles.py` + `tool_swing_gif.py` (verified by render).
- **S4 — animation fixes — BUILT, eyeball in-engine:** watering-can Pour (was sideways+static) + hoe till.
  Broader technique pass (reach-extension etc.) is taste — do with owner watching.
- **`dug_soil` art polish** — the current tile is a cropped placeholder; re-prompt (gpt-image-1.5/medium) or
  hand-draw a cleanly-blended recessed edge so it doesn't read as a bordered box.
- **Material item icons** — `grass_turf, dirt, mud, stone, sand, plank, wood` used by recipes have placeholder
  icons; generate real icons via the pipeline (API spend → owner approval) in one batch.
- **Verification owed:** the in-engine S1 playtest is the legibility gate; also confirm 2-client parity of the
  new player-break drop RNG once (autonomous determinism harness is unaffected — it issues no player breaks).
- **Build note:** add `Hidden/BugFarmer/TileComposite` to Always-Included Shaders before a player BUILD
  (Shader.Find works in-Editor; a stripped build would miss it).

## Ground material MECHANICS (deferred from the shaped-ground builder; owner 2026-07-09)
The builder ships **COSMETIC** (above). Later: some ground materials carry mechanics — e.g. **swamp** =
slowed movement, **ice** (mountains, if we do them) = slippery. **Rule for a split (diagonal) cell: AVERAGE
the two materials' mechanical values.** Mechanism: replace `PrimaryMaterial(id)` (the cosmetic resolver used
at every gameplay derivation site — hoe/water/collision/bug-block) with a `Properties(id)` that blends
`matA`+`matB` — SAME call sites, no rework. Movement speed isn't ground-derived today (`TileDefinition.
MovementMult` has zero consumers), so swamp-slow also needs wiring movement to the tile def first.

## Rug system redo — grid-square pattern builder (owner 2026-07-09)
Replacing the current single-sprite rugs (`rug_small`/`rug_large`). Owner wants a **grid-square-based rug
system**: build rugs out of square/tile patterns the player composes, cell by cell (like laying carpet).
A cousin of the shaped-ground builder — likely reuses the same mask/composite + square-pattern tech. Because
of this redo, **rugs are EXCLUDED from the shovel palette** (they are not shovel-placed ground). Design when
we reach it.

## Sandbag water-fill system (owner 2026-07-09)
A separate mechanic (NOT the shovel builder): fill in **shallow water** (and later **swamp**) with sandbags,
which converts those cells into **normal walkable ground**. This is why water/bridges are out of the shovel
scope — crossing/filling water is its own system. Design + build later.

## Sound / audio pass (deferred 2026-07-09 — owner on a bad speaker, can't tune audio now)
The `AudioFx` synth system exists (bug hit/kill, sting, faint, thunder, hiss, crunch, and the new axe-chop).
Deferred until the owner has proper audio: broaden SFX coverage (footsteps, UI clicks, water, crafting,
pickups, ambience), tune the volume mix + distance falloff, positional-audio polish, and music. Revisit then.

## Tutorials & instructions review (owner, 2026-07-09)
Polish pass on player onboarding — show users the different systems instead of leaving them to guess.
Includes tool-role instruction via tooltips/first-use hints, e.g. the **shovel** reshapes the ground under the
player's feet and the **pick** breaks blocks and items at the player's level (tooltip wording TBD), and surfacing the other mechanics
(farming, catching, crafting, ground-editing) as they're encountered. Ties into the shovel ground-editing UX
being designed now.

## Late-join / determinism (found 2026-06-29 via the 2-client sync gate)
- **DONE 2026-06-29 — late-joiner gets 0 bugs in dense zones (real multiplayer bug + why the determinism gate "couldn't run").** Root cause: the Nakama client's default `MaxMessageReadSize` is **256KB**; village_21_B's `LateJoinSnapshot` is ~230KB raw → **~305KB base64 on the wire** (Nakama frames match-state data as base64) → the client silently truncates the frame, the websocket framing **desyncs**, and the late joiner receives **nothing** after it (snapshot + handoff + tick broadcasts) → **0 swarms**. Any 2nd player into a populated zone saw no bugs; regressed when #113 tripled swarm counts ("worked the other day"). Fix (shipped, `NetworkManager.Awake`): build the socket with `WebSocketStdlibAdapter(maxMessageReadSize: 8MB)` to match the server's `max_message_size_bytes`. **Verified:** co-located late-join `SYNC: IDENTICAL` (128332 bug-states + 236 tick-hashes, no drift). Proven by A/B zone size: bug_lab (20KB snapshot) ingested fine; village_21_B (230KB) dropped everything.
- **DONE 2026-06-29 — spawn-apart (disjoint-chunk) late-join divergence (the determinism gate's 2nd half).** Root cause (proven by a per-tick `_food` digest probe): the client deterministic food registry (`InfluenceManager._food`, which bug LANDING visuals read — `BugAgent.TryFeedAtFood` sets bug position) was hydrated **per-chunk** — `GroundItemManager.HandleItemSpawn` called `HydrateFood` for each `GroundItemSpawn`, and those are sent **per-chunk-subscribe** — so a client only knew food in its loaded chunks (authority held ~85 entries, a disjoint late-joiner ~265) → bugs forage/land differently → ~11-15% per-bug divergence. Fix (shipped, `GroundItemManager.cs`, 1 file): `GroundItemSpawn` is **COSMETIC-ONLY**; food enters `_food` only via the zone-wide `ITEM_ROTTED`/`FOOD_CONSUMED` ledger + the authority's `ZoneSnapshot.Food`. **Verified:** BOTH gate halves `SYNC: IDENTICAL` (co-located 166k + spawn-apart 161k shared-bug states, no drift). NOT an ecology change — `_food` is landing-visuals only; the server ecology uses its own `ForagePools`/`HostPlantStates`/`FindNearbyFood(worldState)`. With the collision map (#133) already zone-wide, food was the last view-scoped sim input → the deterministic bug sim is now fully zone-wide. (Optional polish, backlogged: a `ZoneFoodMap` would let bugs land on the FULL zone food set for richer feeding visuals, vs only the ledgered/un-consumed food they land on now.)
- **Snapshot size scalability (follow-up).** The `LateJoinSnapshot` grows unbounded with zone density (8MB client cap = ~30× today's headroom, not infinite). Consider gzip-compressing or chunking the snapshot, or bounding it.
- **DONE 2026-07-14 — S1/S2 predation client-state not surviving late-join (each client's wasps re-picked different prey → permanent desync).** Root: the server relayed the per-bug snapshot through a hand-declared Go `BugSampleData` struct missing `hunt_target`/`feed_until`/`feed_corpse_id` (silently dropped), and `_swarmStrikes` was never snapshot-hydrated. Fix: (A) `SwarmSnapshotData.Bugs` → `json.RawMessage` (server relays per-bug state VERBATIM — no field can drop); (B) snapshot `_swarmStrikes` by mirroring the food registry. Verified `SYNC: IDENTICAL` co-located + spawn-apart, non-vacuous (wasps hunting), 0 ht+pc mismatch. Contract in `architecture_swarm_sync.md §0`; check baked into test-changes/frontier-sync/certainty-assessment.
- **DONE 2026-07-19 — late-join swarm-LIFECYCLE divergence (merged-away/window-born swarms) + the drift net
  un-blinded (THE one-time-base fix).** Root (proven by a 17/17 one-class census of a failing disjoint run): the
  late-join package mixed two time bases — per-bug data at snapshot_tick but swarm METADATA from CURRENT
  state at end_tick (+ player_cells end-tick) — so a swarm that MERGED AWAY inside the ~4s window shipped
  bugs-without-metadata → the joiner orphaned them → the replayed merge deficit-filled same-id-DIFFERENT-bugs
  while the authority moved real ones → permanent ~2% divergence. Fix (structural, not a patch): the authority
  embeds per-swarm identity + player_cells in its snapshot; the server builds metadata FROM the snapshot
  entries; the joiner prunes-to-snapshot; resync reconciles per-swarm BUG-ID SETS. Adjacent races fixed:
  on-receipt SwarmUpdate removal racing the merge event (now replay-gated + a deferred tick-aligned
  empty-husk sweep), and the drift net (per-chunk rounds + tie-skip = structurally blind at ≤2 players) → ONE
  zone-scoped round + AUTHORITY tie-referee, proven by a new self-test (`DESYNC_B=<n>` deliberately perturbs
  one bug → detected in 1 round, resynced, CONVERGED). Harness hardened: FRESH=1 now REBUILDS the plugin
  (FRESH≠deploy — a stale baked plugin silently drops new fields and once invalidated a fix verification) +
  FAIL-loud reconstruction tripwires (exit 6 on `moved 0/N`/orphan lines). Verified: 3× non-vacuous
  (in-window merges, all `moved N/N`) + 6/6 runs SYNC IDENTICAL across disjoint + co-located topologies.
  Docs: `architecture_swarm_sync.md §0` "Update 2026-07-19".
- **STRESS / SCALE TEST the bug sim (owner ask 2026-07-14).** Spawn LARGE bug populations (many swarms, dense predation/breeding) and confirm it all still holds: (1) DETERMINISM — the 2-client late-join gate stays `SYNC: IDENTICAL` under high swarm/bug counts (the snapshot + per-tick hash cost scale; watch the 8MB snapshot cap above); (2) PERF — client FPS + server tick time under load (tie in the `perf-tuning` skill + the ground-item pile bound below); (3) STABILITY — no crashes/OOM, no unbounded growth (ground items, brood, food registry). Add a stress test-zone (mass `initial` spawns) or a debug "spawn N swarms" and run the determinism + perf gates against it. Likely surfaces snapshot-size + O(n) hot spots first.

## Playtest 2026-06-28 — backlog items + fix queue
Full investigation campaign: **`docs/product/investigations/playtest_2026-06-28_index.md`** (root-caused 17 of
the 22 issues; one findings doc each). Backlogged-by-the-user items (not investigated):
- **Net dynamics (catch by net size).** You shouldn't be able to catch a centipede with a small net but
  currently can — flesh out the net-size / `catch_condition` / catch-difficulty matching (which net catches
  which species). Pairs with the catching-gear backlog (auto-catcher + fly nets) below.
- **Sleep.** A sleep/skip-to-morning mechanic (right-click bed → sleep), beyond the bed-as-respawn-home that
  exists. Design the day-skip + any restore/cost.
- **MOSTLY DONE 2026-07-05 — night critters + fireflies.** Fireflies SHIPPED (species + existing sprite +
  the per-bug amber LampLight glow that self-ramps at night; spawns all day, glow reads at dusk) with the
  bee milestone, plus dragonflies (the wasp-hunting chassis proof). STILL BACKLOGGED: the day/night SPAWN
  gate (fireflies visible-glow-only at night is display; a real nocturnal spawn window is sim).
- **DONE 2026-07-02 — the last two playtest fixes: #2 ghost offset + #7 rain.** **#2**: `TilemapManager.OccupantWorldPos` = the ONE shared position helper (footprint-X + bottom-pivot Y baseline); `RenderOccupant` + the placement ghost both use it → preview == placement by construction (ghost positions with the seed→plant id it renders). **#7**: rain streak lifetime was a fixed spec (~9-10 units of fall) shorter than a screen crossing; now computed per-layer from the live camera so the SLOWEST drop crosses the bottom edge (+ band/splash boxes sized from the view, rebuilt on zoom). Both display-only, no sim surface; editor-compile + eyeball gates.
- **DONE 2026-07-01 — three quick playtest fixes: #14 containers · #15 water empty bed · #10 moved compost.**
  **#14** (data): `basket`/`chest`/`trunk`/`yarn_basket` had a `world.container` block but no
  `interaction_type` → the client open gate (`CraftingPanel` needs `storage`) never fired. Added
  `interaction_type:"storage"` (exhaustive audit: exactly these 4 of 30) + published. **#15** (server): bare
  tilled `garden_plot` now waters → `garden_plot_wet` + consumes a use (was "No crop here"); ground-tile
  CellEdit only, no sim surface. **#10** (server, sim-feeding station): moved/runtime-placed compost had no
  `StationState` (chunk-load scan only) → deposits rejected; new `resolveStation` lazily find-or-creates
  (mirrors `resolveCraftStation`). Determinism-safe (empty station inert; food rides the frontier-gated
  `processStations`→ledger). Gated: `go test ./world/` green incl. 2 new falsifiable tests + FRESH 2-client
  sync IDENTICAL. In-game visuals = the Editor pass.
- **DONE 2026-07-01 — shared front-most-interactable click resolver (#18 + the overlap-steal defect class).**
  Occupant `BoxCollider2D`s are sized to the full sprite, so tall/large sprites overlap neighbouring cells; every
  click used a single `Physics2D.OverlapPoint` (one ARBITRARY overlapping collider) → an occupant that merely
  overlaps could steal the click. New `InteractionResolver.TopmostInteractable` (`OverlapPointAll` → front-most
  INTERACTABLE occupant, front-most = lowest `AnchorCell.y` = highest render sortingOrder) routes all 8 click
  handlers (`Breaking/Sleep/TreeHarvest/Station/Shop/Crafting/Mannequin/Sign`). Client-only target selection, no
  sim/determinism surface; Unity batchmode build compile-clean. **Fixes #18** (break behind a tree) + the
  flakiness class; **de-risks but does NOT fix** #5 (live-confirmed *sell-flow*, not the open), #14 (data tag),
  #10 (station-state keying), #4 (render never built), bed-2 (respawn/optimistic-message) — each keeps its own
  fix. In-Editor click-feel pass pending.
- **DONE 2026-06-29 — village doors (#1/#9) + modern-store windows (#2) + village neighbor (#3-edge).**
  `door_square` (the only placed door — all village doors) is now 1×2 tall + `blocks_bugs:true`, so flies stop
  at doors; players still pass (`blocks_players` left unset, by design — doors don't open, they just block
  bugs). Pure entity-def change: `blocks_bugs` is derived at zone-load and synced via the existing
  `OCCUPANT_BLOCKS_BUGS` path, so **no zone re-save and no determinism gate** (data on a proven mechanism — the
  earlier "needs re-save/sim-determinism" note was wrong). Modern store's frosted `glass_block` "windows" →
  real `window_4pane` (also bumped to 2-tall to match the walls + door); village_21_B rebuilt and its dropped
  `south→underground_passages_31` neighbor restored. Art regenerated for door_square + window_4pane (gpt-image-1).
- **Doors/windows — general polish (deferred):** a slow per-item pass — review EVERY door/window placement in
  every zone for look, and conform the unused `door_wood`/`door_iron` defs to 1×2.
- **Object/bug blocking-consistency audit (deferred):** bugs pass through some fences/objects but not others
  (confusing in playtest) — one systematic pass over every occupant's `blocks_bugs`/`blocks_players` for
  correctness + consistency.
- **Zone-neighbors builder hardening (deferred — the general #3 fix):** `ZoneBuilder.save()` writes no
  `neighbors`, so every rebuild drops zone links (we patched village_21_B locally in its scene's post-save
  block). Add a first-class `ZoneBuilder.neighbors` field written by `save()`, retire the underground
  post-save hack, and audit all built zones for dropped links.
- **DONE 2026-06-29 — dead bugs + fruit are placed GRID objects; sword-kills drop the bug (#22).** Carcasses
  (player kill → the strike cell; old-age/starvation → scattered across the swarm by a DETERMINISTIC per-bug
  hash, never `state.Rng`) and fallen fruit snap to a cell centre and render STATIC + per-item-nudged (multiple
  per cell, no bob); excluded from the walk-over magnet (bug food + `no_auto_pickup`), grabbed with E on
  mouse-hover. Server: `spawnCarcass` snap + blocked-fallback, melee carcass, `killBugsNaturally` scatter, fruit
  snap. Client: `IsAutoPickupExcluded += FoodValue>0`, `GroundItemVisual` static+nudge, `PickupController`
  E-on-hover. Go tests + sim-determinism green; ecology band check + Unity render/pickup are the in-game gates.
- **★ ARCHITECTURE INITIATIVE — move the bug ECOLOGY onto the authority client (server → thin relay + snapshot
  cache; lockstep).** Movement is already client-authoritative, but the ecology (breeding/death/hunger/food/the
  Director) runs server-side — which is why a corpse has no individual position (the server thinks in swarm
  *centres*). Viable because zones **freeze when empty** (no always-on requirement; the frozen-zone catch-up is
  its own backlogged heuristic). Big project (the full ecology must become deterministic-on-clients, with
  authority handoff) — it dissolves the corpse-position problem and scales. The natural-death scatter above is
  the throwaway interim until this lands.
  - **PILOT SHIPPED — individual predation S1+S2 (2026-07):** the first slice of this initiative — per-bug
    DECISIONS on the authority client, deterministic, ~no new traffic. **S1** = one wasp PURSUES a specific fly
    (`BugAgent` HUNT branch, staggered commit; per-bug strike broad-phase). **S2** = the kill drops a REAL edible
    corpse and the wasp PAUSES to eat it, with a ~1/4 chance it leaves it (`BugAgent` FEED branch; the corpse rides
    the ITEM_ROTTED food ledger; consume via the new authority-only `CorpseConsume` opcode 112 → FOOD_CONSUMED).
    Gated: `sim-determinism --predation-test` (non-vacuous, byte-identical) + Go tests green; committed `c39289b`
    (S1 `0b7dd3c`). See `architecture_swarm_sync.md` §14.6. **Next — S3:** dial back the swarm-centre steamroll
    (`predationThink`, scoped to swarm predators) + an `ecology-tuning` re-balance; then arena feel-watch (owner).
    Breeding/death/hunger/food/Director still server-side — the FULL ecology port is the remaining big project.
    **→ Next slice mapped (2026-07, station-unify assessment):** the BREEDING STATIONS (compost/brood/nest/
    milkweed) belong to this port. Seam — move client-side (authority owns → hashed + snapshotted): per-swarm
    `Satiation`/`ReproductionMeter` + the feed/hunger loop (`match.go:1379-1474`) + `BroodStates` maturation +
    the authoritative food LEVELS (`Fill`/`FoodValue`/`Capacity`/`Nectar`) — **requires `float32`→fixed-point**;
    new `BREED_LAID`/`BROOD_HATCHED` events (→ existing `SWARM_REPRODUCED`); the food registry becomes
    authoritative. Stays server: the Director (population-count-driven, decoupled) + the nest/predator economies.
    NOT a now-simplification (the fixed-point conversion is the real cost) → deferred. **The player-facing UI is
    ALREADY unified** — compost/nursery/beehive + craft/storage open ONE `CraftingPanel` (dispatched by
    `interaction_type`; IMGUI `StationController` + `NurseryPanel` + `BeehiveController` deleted). The server-code
    merge was deliberately NOT done: crafting = inventory, breeding = ecology (different domains); merging the
    server tick loops would be thrown away by this ecology port.
- **Dead-bugs/fruit follow-ups:** ~~predator kills leave a corpse + the hornet feeding-pause (#20)~~ **DONE
  2026-06-30** — feed-pause (`feed_pause_ticks`, server) + client-side LOS (`BugCollision.LineBlocked`, fixes the
  through-bin phantom) + consumed-corpse/lunge VFX (`StrikeVfx`); see `investigations/wasp-attack-indicators-phantom.md`.
  Still deferred: drop/place ANY non-occupant item from inventory, one at a time (reuse the torch "placer"); smarter
  placement (true across-a-fence reachability, nicer spread); the frozen-zone catch-up heuristic; tree refinement + testing.

## Opening intro + title screen — built 2026-06-28 (follow-ups)
The game now opens with a text intro ("It is the year 2126…", line-by-line) → crossfade → a **BugFarmer** title
screen (composed farm scene + logo + Start) → reveals char-select. `UI/OpeningSequence.cs` (self-bootstrapping
canvas, order 30, skippable, fail-safe). Art: `tools/sprites/title_art.py` → `Resources/UI/title_{bg,logo}.png`.
- ~~Replace the placeholder intro script~~ — DONE: `IntroLines[]` in `OpeningSequence.cs` holds the owner's
  text ("It is the year 2126. A plague swept the Earth. Nearly every mammal — gone. … So we made the bugs
  bigger. … As a bug farmer."). The premise every design must fit (see `docs/product/ROADMAP.md`).
- **Animate the title scene** — currently a static PNG; layer it for parallax/drift (floating bugs, swaying
  crops, clouds) — re-author `title_art.py` to emit layers + a small animator, OR a particle/Tween pass.
- **Custom display font for the logo** (optional polish) — the wordmark uses DejaVuSerif-Bold + styling (only
  standard fonts were available); a bespoke pixel/display .ttf would lift it. Re-render via `title_art.py --font`.
- **Remember-intro-seen** (optional) — auto-skip the cinematic on later launches (PlayerPrefs), still show title.

## Testing backlog (deferred test coverage — not blocking)
- **Crafting chain — verify in-game (the buildout from 2026-06-28).** The data/sprites/test-zone are built +
  the validators (`recipe_graph.py`, `catalog_coverage.py`) + Go tests are green, but the chain was NOT
  exercised in a running client. Steps: rebuild/run the backend (`run-backend`, force-recreate so the Go
  plugin picks up the new F8 "crafting" give-loadout); enter the **`crafting_test`** zone; **F8 → give
  "crafting"**; then right-click through `rock_crusher` (ore→paydirt) → `ore_sluice` (paydirt→refined) →
  `furnace` (refined+coal→bar) → `anvil`/`forge` (bar→tool/weapon) → `gem_cutter` (raw→cut gem) →
  `bug_extractor` (dead bug→chitin/leather). Confirm each opens, crafts, and produces; check tool-tier icons.
- **Cross-zone determinism check**: a player leaves a zone and re-enters; assert the bug-sim STATE HASH
  is identical across the leave/join (same bug positions/phase) — i.e. the swap didn't perturb the
  deterministic tick. Extend the sync-harness `crosszone` scenario to capture + compare zone hashes
  before/after. (The crossing is *designed* to be determinism-inert; this proves it.)

## Crafting buildout — remaining pieces (data/sprites/test-zone DONE 2026-06-28; these were specified, not built)
Plan + designs: `docs/product/economy/crafting_buildout.md` + the saved plan. All three are fully designed.
- **DONE 2026-07-03 — Per-station craft-slot mechanic.** `Procs []CraftProcessor` lanes (world.`craft_slots`,
  default 1; furnace/forge/sawmill/ore_sluice/dye_vat/bug_extractor = 2) sharing ONE output grid; legacy
  saves migrate via `UnmarshalJSON`→`Procs[0]`; `proc` on ContainerActionMessage + `procs[]` on the echo;
  CraftingPanel renders one row per lane with lane-targeting DoCraft. 5 falsifiable Go tests (migration
  round-trip, parallel lanes, stall isolation, proc targeting, seeding/top-up) + suite green. NOTE from the
  build: campfire/stove/cooking_pot/cauldron/keg have ZERO recipes — not functional stations; their
  craft_slots are moot until cooking recipes ship (cooking = D16/D19 backlog). In-Editor parallel-smelt
  check pending. Sprite pass shipped alongside: 15 missing sprites + ~82 placeholder regens (metal/gem/
  weapon/tool tiers now real per-metal art; catalog rows authored). Editor eyeball flags: `specimen_case`
  reads empty; bronze-vs-gold sword tone is close.
- **Station panel LAYOUT session (user-requested backlog)** — a joint pass positioning panel elements
  ("right now they are ok but could be positioned a little better") + the themed per-station dressing
  (Apico fuel/heat treatment) that was deferred with it.
- **DONE 2026-07-02 — Barter sell UI** (Apico/BG3; also the playtest **#5** fix). Your REAL inventory opens
  with the shop; stage stacks into a basket (right-/double-click = whole stack; drag via the cursor;
  right-click a basket cell = one-at-a-time partial) → one atomic **`sell_batch`** server op (each line
  validated by the shared `sellLine` core vs the vendor `Buys` filter, sum, pay ONCE, one FullInventorySync
  echo) — NOT a client loop of single sells. Staging = a render OVERLAY (`ShopPanel.StagedQty`/`ForRender`,
  consulted by InventoryPanel + HotbarUI) so the mid-shop FullInventorySync repaint can't resurrect staged
  slots. Also shipped: "Buys: …" header + client stage filter mirroring `shopBuysItem`, OpCode-40 server
  errors surfaced in a shop status line (were silently dropped — the #5 feedback gap), per-line `qty<=0`
  rejection (closed a real negative-qty duplication exploit), bug-release guarded while a shop is open.
  Gated: 4 new falsifiable Go tests + suite green + Unity batchmode compile clean + in-Editor CONFIRMED (Andrew, 2026-07-02; incl. the layout fix — wide short trade dock clearing the inventory).
- **Station mockups** (PIL) — extend `tools/ui_mock.py` to render every craft station + the breeding/food
  stations (compost/beehive/milkweed/wasp-nest) with the Apico I/O-square treatment, for visual review.
- Also: armor + weapon-tier *sprite polish* (placeholders shipped); the InitialContainers authored-stock seed
  (the good-design alternative to the F8-give); fruit/crop + breeding-station info panels (separate backlog).
- **Compost → fertilizer (backlogged 2026-07, owner decision):** the compost bin now yields a sellable
  `compost` item (take-all harvest, `OpCodeCompostHarvest` 115). Its FERTILIZER use — apply compost to tilled
  soil/crops for a growth or yield boost — is DEFERRED (owner decision). Design when
  picked up: what the boost is (faster growth vs. better yield vs. water-retention — cf. Sun Haven's elemental
  split), how it's applied (a use-item on soil, mirroring `garden_plot` watering), and whether it tiers
  (basic/quality/deluxe). Compost also needs an icon sprite (`Items/compost_icon.png`, gpt-image-1).

## Now — Bug ecology / farming (livestock loop on a living-ecosystem engine)
Design of record: [bug_ecology_plan.md](../brainstorms/ecology/bug_ecology_plan.md). Phased build P0–P11
(P1 Bug Lab DONE). **Verify every sim-touching phase with the `test-changes` skill** (Go tests +
sync-harness + the determinism / "all players in sync" checks — the testing methodology is now captured as a
skill so it stops getting lost between sessions).
The **SERVER ecology is built + verified** (Go tests + 6× headless lab + per-species charts in
`tools/_generated/ecology_charts/`). The living system = **depletable food → boom-bust → the Director →
(future) the Ecologist restores → progression**. Done:
- **Breeding-unify — ONE visible brood model (2026-07-14, SERVER DONE + deployed):** ALL non-instant
  breeding lays eggs into a visible `BroodState` that develops over GAME-HOURS (`BroodEggMatureTicks=350`
  ≈ 1 game-hour/egg, was ~10s, which is why nests always looked empty) and hatches — flies/butterflies (compost /
  rotten-fruit pile / milkweed), detritivores, AND **wasp NESTS** (nest brood routed off the old invisible
  instant-pop counter onto the `BroodState`; recovery/founding read it via `nestBroodCount`; the homing
  resident ENTERS the nest a beat to tend). Go-tested; A1 ecology-validated (ground species self-sustain via
  `+brood`). `entities/brood.go`, `world/{brood,nests,predation}.go`.
  **→ NURSERY-STATION model built (2026-07-16) — see `architecture/architecture_nursery_stations.md`:** a brood
  IS a modified STATION. Right-click a **wasp nest** or **milkweed** → the `NurseryPanel` (egg/larva/pupa slots +
  stage sprites + resident adults + a maturing bar), fed by OpCode 104 (now carrying conversion progress +
  resident count). **Take** a stage's units into the bag like any station transfer — no random yield, nothing
  perishes on take (larva → the designed `wasp_larvae` material, else the stackable stage sprite;
  `OpCodeNurseryTake` 113). **Teardown** now **perishes the brood** and spills the resident adults (aggressive) —
  the `wasp_nest` `paper_nest`+`wasp_larvae` break-drop removed per D23 (now Wasp-Thicket boss loot only). The
  **pupa stage is universal** — nests pupate too (wasp `wasp_pupa`); millipede/centipede stay egg→larva→adult;
  `BroodEggMatureTicks` split across stages so total dev time is unchanged. Stage art: 11 existing +
  `fly_pupa`/`beetle_pupa`/`butterfly_caterpillar`/`butterfly_chrysalis`/`wasp_pupa`. The earlier wrong-model
  (on-world `BroodManager` sprite renderer + the "emergence beat") was a MIS-BUILD → **removed**. Go-tested green;
  determinism-safe by construction (broods are server-soft/unhashed); D23 + docs reconciled. **Place-back**
  (OpCode 114) built too — deposit a compatible brood item into a nursery (species-validated; tops up or seeds
  an empty nest). Client headless-compile CLEAN (Assembly-CSharp.dll built). **STILL OPEN:**
  the **compost bin** deposit+brood unified into the panel; the wild
  fly-brood object; compost residents; the owner's in-engine panel eyeball + a non-vacuous 2-client
  sync re-run. **Bug Zoo built** (`zone_bug_zoo.py` — a peaceful 3×3-pen observation zone, replaces the scattered
  labs) to watch the loop; `zone_arena`/`zone_crawler_lab` flagged superseded. Then Phase-3 re-tune to the new
  bands (fly 200 · butterfly 100 · rest 30) on the predation-inclusive Unity rig. Dead `egg_count_min/max`
  species fields to delete (unused).
- **Natural death + carcass recycle** (per-bug `DeathTick`, `dead_<species>`, millipede→compost).
- **Hard `max_population` crash-guard** (per species per zone; the only guaranteed bound — food is
  player-controlled, so it can't be the guard).
- **Depletable food** — flower `ForagePoolState` nectar + milkweed `HostPlantState` (deplete + regrow).
- **Starvation death** (`StarveTimer`/`processStarvation`) — the bust.
- **The Ecology Director** (`world/ecology_director.go`) — per-species bands: re-seed below `min_population`,
  cull above `cull_at` (release `cull_with` predator else overcrowding cull). The oscillation engine + the
  universal "add a layer when out of range" lever.
- **Test sim-speed control** (`SimRate`/`call_rate`, 6×, balance-neutral) + **per-species population graphs**.
- Design of record: see architecture_farming.md "Living ecology — population dynamics" + the roadmap plan.

### Phase W2 — Cost profiler + perf-first rebalance (DONE 2026-06-19)
Built the full-stack bug **cost profiler** (measure before optimizing) + rebalanced village_21_B to fix the
~1000-bug lag. All committed-ready (see ecology_tuning_log.md 2026-06-19 + the plan doc).
- **Profiler:** server `PERFSTATS`/`PERFSYS` (per-species CPU by sub-phase + leg counts + global passes +
  broadcast bytes; gated by zone `profile` flag; soft/never-hashed — `world/profiler.go`), `tools/ecology/plot_perf.py`,
  `run_config.py` wiring, and a client **F7 overlay + Unity-Profiler markers** (`Util/PerfProfiler.cs`,
  `DebugOverlay`). **Finding:** `FindNearbyFood` dominates server CPU (butterfly 11.7s/day); the predicted
  O(S²) merge is negligible (5ms/day).
- **Rebalance (baked):** fly/butterfly 3× swarm size; millipede+beetle category→swarm + brood-gate on
  `EggSpriteID` (detritivores instant-grow+merge); tuned to ballpark bands. **Win: legs 5.9→1.1 MB/day,
  butterfly cpu_food 11.7s→~0.5s, swarms 68→20 — lag gone.**
- **Follow-ups surfaced (NOT done — structural, not tunable):**
  - **[PERF, high] FindNearbyFood spatial index** — bucket `GroundItems`/`Stations` by chunk; route the
    food query + `nearestPredator/PreySwarm` + merge through it (O(S·I)→O(S·k)). The profiler-proven #1.
  - **[PERF] Chunk-scoped broadcasts = per-chunk-frontier redesign** — NOT safe routing (the client gate
    `HasAllEventsUpTo` needs a contiguous global seq stream; dropping a chunk's legs stalls it). Per-chunk
    seq+watermark+gating+handoff. Gate behind the profiler showing the global stream is still the bottleneck.
  - **[ECO] beetle carrion supply** — beetle stuck ~3 (carrion-starved); needs distributed carrion sources
    (zone change), not a breeding param.
  - **[ECO] wasp prey base** — stable ~16; reaches 30-50 only if fly settles higher.
  - **[ECO/Go] centipede kills→breeding conversion** — pinned ~4 across two breeding-lever runs; needs a Go
    fix (it can't convert kills to offspring), not tuning.

### Phase 4c — TUNING RIG (built + committed) + the sweep (in progress)
The ecology is structurally complete but UNTUNED; targets are the CENTERS of an oscillation (boom-bust
for ecologist gameplay), NOT flat lines: **fly 100, butterfly 100, wasp/centipede/beetle/millipede 30**.
Two acceptance criteria/species — **oscillates** (visible amplitude/period) + **self-maintained** (troughs
above the re-seed floor → `b_reseed` births ≈ 0). The RIG (all committed, see `ecology_parameters.md`):
- **Tick batching** (`sim_batch`) → 48× runs; **tunable consts** → `data/ecology_tuning.json` (`Tuning`,
  byte-identical defaults); **interaction-log telemetry** (`ECOSTATS`/`PREDLOG` → `plot_interactions.py`,
  births-by-source / deaths-by-cause / predation matrix); **config system** (`tools/bug_lab_configs/` +
  `run_config.py` snapshot→apply→run→chart→restore + `compare_configs.py` scoring).
- **40-run sweep (3 batches, configs in `tools/bug_lab_configs/`, charts in `_generated/ecology_charts/`):**
  - **Harness reliability fix (infra):** the sweeps exposed a real bug — Nakama's `socket.outgoing_queue_size`
    (1024) overflowed on the whole-zone chunk-subscribe burst → server closed the socket → runs froze (no
    CSV). Raised to **8192** (`nakama/data/local.yml`). Also hardened `run_config.py` (retry + per-run log
    isolation so `plot_interactions` can't read a prior run's ECOSTATS).
  - **SOLVED ✅ fly → 100:** `C3` lever = faster fly breeding (`reproduce_cooldown` 30→18, `breed_amount`
    10→16). Oscillating, 0% re-seed.
  - **SOLVED ✅ butterfly → ~90:** robust across nearly every config (host/nectar-limited, self-maintained).
  - **SOLVED ✅ centipede → 30** (the breakthrough): the predator FLOOR was **structural, not behavioral** —
    proven because NO predator/prey/food parameter (vision, speed, strike, feed, breed-bar, lifespan, decay)
    moved it across 30 runs (at fly=100 GLOBAL the predation log showed `centipede→fly = 0 kills` — its pen
    had no prey; a predator eats its small fly seed to extinction in ~3 days then starves = small-system
    predator-prey collapse). **Fix = prey immigration** (`fly_common` `spawn_interval` 999999→20s; since
    `spawnSwarmForSpecies` picks a random spawn area, fresh flies trickle into every predator pen). With
    sustained prey the centipede hunts→breeds→reaches 30, **0% re-seed, oscillating** (configs `G4`-`G7`).
  - **PARTIAL ◐ beetle ~12, millipede ~18:** both now self-maintained (0% re-seed) but below the 30 target —
    need higher caps + more food (beetle: corpse supply / cap 20→40; millipede: more `leaf_litter`).
  - **SOLVED ✅ wasp (2026-06-18, the living-zone redesign):** the frozen-wasp holdout was STRUCTURAL —
    nestless free-spawned/reseeded wasps (sterile, can't deposit brood) + dead colonies going permanently
    dormant. Fix = **wasps nest-only** (skip nest species in every free-spawn path → zero nestless wasps)
    + **prey-gated nest recovery** (a brood-exhausted colony re-founds a fresh patrol when live prey is
    within home range, else WAITS) + **6 nests spread to woods/corners each near a fly source**. Verified:
    wasp pop sustained ENTIRELY by `b_nest` (hatches + recoveries), `b_reseed=0 b_spawn=0`, colonies
    re-found as flies boom (run v21b_nocaps, seed 1337). Remaining = oscillation-band tuning, not structure.
  - **Open balance items:** immigration overshoots fly to ~390 — dial `spawn_interval`/cap so fly sits at
    100 while still feeding predators; then re-add the Director culls as far guardrails (`G10` showed culls
    reshape via re-seed, not self-maintenance — keep them last-resort).
  - **Best config so far: `G6_immig_breedbar` / `G4_immig_reach`** (centipede PASS + decomposers
    self-maintained); fly/wasp still need the two balance items above.
  - **→ Next (post living-zone redesign, 2026-06-18):** (1) longer runs (sim_batch>2) to watch a full fly
    boom→bust→wasp-dip→recovery oscillation and judge the bands; (2) dial fly initial/food (boomed to ~198);
    (3) beetle/centipede establishment (still reseed-reliant); (4) re-confirm same-seed reproducibility gate.

**Up next (the roadmap remainder, mostly client → needs the Unity Editor):**
### Ecology mechanic fixes (from the village_21_lab control campaign, 2026-06-18)
The 15-run controllability campaign (`docs/product/ecology/ecology_control_campaign.md`) proved two species are
STUCK for MECHANIC reasons, not tunable by any param:
- **Make `leaf_litter` DEPLETABLE** (a ForagePool like milkweed/nectar, deplete + regrow) — millipede's only
  food is non-depletable flora, so it's "food-limited" by infinite food → pins flat-high (~130) and never
  oscillates. Depletable litter makes it genuinely food-bounded → it'll sit in a real oscillating band.
- **Buff centipede kills→breeding CONVERSION** — centipede hunts fine (144 kills/run) but can't convert
  kills to population (stuck at the founding floor ~4 under every param). Likely `predator_breed_satiation`
  too high / `max_swarm_size` 3 too small to accumulate / well-fed-split too slow. A ground-predator
  breeding pass would let it climb. (Tuning vision/position/seed-count all FAILED — it's a breeding bottleneck.)
- **Brood CLIENT layer** — right-click a source → eggs/maggots panel + on-world maggot-pile/egg visuals + sprites.
- **Butterfly life stages ON the milkweed (owner decision 2026-07-16 — keep it simple):** caterpillar +
  chrysalis are STAGES that happen ON the milkweed host plant — eggs → caterpillar → chrysalis → adult — **NOT**
  a caterpillar that crawls off or a chrysalis that wanders to a tree/fence (that mobile-creature version is
  explicitly OUT of scope). Extends the existing `host_plant` `BroodState` (butterfly already breeds on milkweed,
  `brood.go`) with a chrysalis stage on top of egg→larva, plus caterpillar + chrysalis stage sprites (butterfly
  caterpillar sprite already backlogged above). Adult butterfly birth rides the deterministic ledger as today.
  Deferred: caterpillar/chrysalis are synchronized client-side bugs — needs the sync-gate work, not done today.
- **Plant repopulation** — player planting (seeds from destroying milkweed/flowers) + rare bounded natural spread.
- **Ecologist meta** — the Ecology TAB dashboard (per-species graph + band status + tasks, reusing the same
  per-species data), restorative TASKS (the Director's player-facing tier: a task + grace window before the
  auto-event fires), and progression (CharacterSave XP/unlocks).
- (Optional) natural predator-prey oscillator — the Director's predator pulse already covers the culling.

### Bugs at zone boundaries (owner has ideas incl. heuristics)
- **Problem:** bug swarms wander to / spawn near the zone edge (x|y → 0 or 256) — half a swarm's
  habitat falls off the map, predators chase prey that "leaks" past the boundary, and edge clusters
  read badly on the bug-map. The sim treats the 256×256 box as a hard wall with no edge behavior.
- **Direction (owner):** handle this with **heuristics** rather than a hard clamp — e.g. soft
  repulsion / reflect wander targets away from the border, weight spawn-area picks toward the interior,
  keep nest home-ranges off the edge, possibly hand swarms that cross to the neighbor zone (cross-zone
  movement already exists for players). Owner to detail the specific heuristics.
- **Why now:** the spatial multi-region seeding (below) puts clusters near the NE/NW corners, so edge
  behavior starts to matter; capture it before it bites the ecology tuning.

## Now — COMBAT FOUNDATION (M1 BUILT 2026-07-11 → `architecture_combat.md § Milestone 1 — as-built`)
Owner adopted the skeleton (**attack-token + FSM + steering**) + core bundle. **Decided dials:** bite-token
pool = **2**, **dodge-only**, danger **at night**, bug→player damage **per-individual** (authority-decided,
mirrors predation; swarm-of-1 dropped — player HP is SIM-INERT so it needs no hash/snapshot wiring), new sprites
**gpt-image-1.5/medium**.
- **✅ M1 DONE + gated** (commits `combat M1.1`…`M1.4`): arena + debug species-picker spawner · per-individual
  sting (fixes the wasp **phantom hit** — retired the `checkBugAttacks` swarm-centre sting; opcode 110) · player
  dodge + i-frames (Space; opcode 111 + `DodgeInvulnUntilTick`) · attack telegraph (two-beat wind-up = **12
  ticks**, `processPendingStings`). Gated: `bug_player_strike_test.go` + full world suite + `sim-determinism`
  PASS. **Left to run** (needs the rebuilt plugin deployed — do with the playtest): 2-client `run_sync_latejoin`
  regression + the **owner arena playtest**.
- **✅ M2 DONE + nocturnal + aggro:** **nocturnal** night-hunter mechanic + **player-aggro radius**
  (`aggroPlayerThink` — non-centipede attackers chase a nearby player) + 2 wasp tiers with fresh gpt-image-1.5
  sprites — `wasp_soldier` (med) / `hornet_giant` (hard, **diurnal** — real hornets are day-active).
  Gated: Go suite + sim-determinism PASS. Difficulty via existing knobs (dmg/cd/speed/vision/hp/swarm) + nocturnal.
- **🩹 M3 caterpillars STRIPPED (2026-07-12):** built as caterpillars off a literal misread; caterpillars are
  butterfly/moth larvae, not combat enemies. Removed all of it. Replaced by → **M3 centipede tiers** (below).
- **✅ M3 centipede tiers DONE:** 2 REAL centipede species, medium + hard, own segmented sprites, reusing the
  base centipede surge model — `centipede_tiger` (Scolopendra polymorpha) + `centipede_giant` (S. gigantea). One
  clean code change: de-hardcode `CentipedeTrail` segment family (add `sprite_family`).
- **✅ Enemy AI — individual attack movement + phantom/bumble fix (2026-07-12) → `architecture_combat.md §
  Individual attack AI`.** Owner report fixed: wasps bumbled about and centipedes hit from a distance; they should
  swoop in and attack, one or two divers at a time. ROOT CAUSE of the bumbling: wasps shipped
  `player_reaction:"ignore"` so each individual bug's AI wandered and never engaged (the swarm-centre chase +
  cosmetic-dart first pass didn't fix it). REAL fix: (A) **individual attack MOVEMENT** — `player_reaction:"attack"`
  + `BugAgent.AttackMove`: each bug HOVERS at `standoff` then SWOOPS in during its phase-offset slice
  (`dive_period_secs`/`dive_secs`) → ~1–2 divers at once, staggered, DETERMINISTIC (pure `tick`+`bugId` + player
  CELL); (B) `aggro_speed_mult` brings the cloud onto you; (C) sting detection vs the **RENDERED** sprite killed the
  phantom + the **server centipede bite was DELETED**; (D) `wasp_soldier render_scale 0.5` (was too big); (E) all
  feel in `attack{}` + a "Combat knobs" table. **Gated:** Go world+entities PASS; `sim-determinism` PASS (wander
  hash unchanged `BDE84AEF38467D57`) **+ a new `--attack-test`** that drives a moving player and proves the attack
  movement reproducible (A==B, `FB80CE8997CF9EC3`). **Left to run:** owner arena playtest + knob tuning; 2-client
  `run_sync_latejoin` confirmation (Unity build).
- **✅ CENTIPEDE PACKS + per-bug CLIENT brain DONE (2026-07-18):** centipedes now travel in PACKS of ~5, each acting
  INDEPENDENTLY (own serpentine wander, individual prey hunt+kill, telegraphed windup→surge→overshoot→recover LUNGE at
  the player), with that per-bug behavior on the CLIENT — the last species on the server combat brain, now migrated.
  The server ActionState combat machine + the `category:"individual"` swarm-of-1 hack were DELETED (`centipede.go`
  keeps only the gnaw; all knot special-cases gone from `predation.go`/`entities/swarm.go`/`match.go`); the client got
  `CentipedeMovement` (real chase steering) + the surge state machine on `BugAgent` (`CentipedeSurge`/`LaunchSurge`,
  hash+snapshot wired). Ecology (breeding/pop/food) + the GNAW stay server-side. **Gated:** Go world+entities PASS ·
  sim-determinism default + a NEW `--surge-test` (the lunge fires twice byte-identical, non-vacuous) · 2-client
  `run_sync_latejoin` co-located + disjoint SYNC IDENTICAL · Unity batchmode compile · owner playtest (the
  kills on flies seen in-game). Arch: `architecture_swarm_sync.md §14.3` (rewritten).
  **Deferred (owner feel calls):** per-MEMBER lunge-connect re-key (each surging member reports its own hit; i-frames
  cap burst — balance) · `village_21_B` `centipede_garden.swarm_size` density dial (currently 2, below pack min 3 →
  packs render sparse).
  **✅ SUBDUE-SYNC FIXED (2026-07-18):** subdue/smoke now suppresses the client lunge/dive. A per-swarm
  `SWARM_SUBDUED`/`SWARM_UNSUBDUED` toggle (emitted once per crossing from the lifecycle loop) + a `subdued`
  late-join snapshot section carry the calmed state to the client `_subdued` registry; `BugAgent`'s attack case
  suppresses a new lunge/dive and aborts an in-flight one. Was visual-only (damage was always server-gated). Gated
  by a new `sim-determinism --subdue-test` (control lunges, subdued does not, in-flight aborts; deterministic) + a
  server emit test. Docs: `architecture_swarm_sync.md §14.3` + `architecture_beekeeping.md`.
  NOTE: the `arena` zone is `peaceful:true` (observation) — the lunge only fires in a NON-peaceful zone (e.g.
  `village_21_B`); don't test centipede combat in the arena.
- **⏳ REMAINING:** the super-hard "boss" centipede (owner floated it). **Consolidation refactor** (future,
  tracked): bug→player DAMAGE now has ONE model (client-detect-vs-rendered → server-apply, both styles); the
  remaining overlap is the **3 aggro triggers** (surge-trigger / nest-defence / `aggroPlayerThink`) — collapse into
  one threat-table in a deliberate pass.

## Content — TRUE BUG MAPPINGS (make every bug a real bug) — owner direction 2026-07-11
Every creature in the game should be an **actual real bug species** — real name, real look, and behavior that
matches the real animal (so a player's real-world knowledge never jars, e.g. "hornets are diurnal, why is this one
nocturnal?"). The hint was already there: `nakama/data/bugs.json` is a roster of REAL species (honeybee, bumblebee,
luna/atlas moth, stag/rhino beetle, wolf/jumping spider, scorpions, cicadas…). Combat generated GENERIC invented
names (`wasp_soldier`, `hornet_giant`, `caterpillar_spiny/thornback`) that break this.
- **Task:** sweep ALL species (`species.json` combat + `bugs.json` art) and MAP each to a real species — rename ids,
  names, descriptions, sprites, AND align behavior to the real animal (diurnal/nocturnal, diet, aggression). e.g.
  the combat tiers → real day-active wasps/hornets (Vespa spp.) + real nocturnal caterpillars/moths; verify each
  flag against the real animal.
- **Discipline:** nocturnal ONLY where the real species is night-active (caterpillars/moths yes; wasps/hornets no).
  This is a rename+realism pass, not new mechanics — the combat/ecology machinery is unchanged.
**Backlog `zone barriers`:** gate danger by zone so starter zones stay cozy while wilds/caves/night are dangerous.
Earlier notes (still valid): Deferred — utility-AI attack selection, enemy-role/species expansion. Rejected: GOAP, flow fields.
All integer/fixed-point on the server → cheap on the wire (legs + events, not per-bug positions; see the doc's
network section). **Build order:** dodge+i-frames → one telegraphed enemy + token pool in `feel_test` (playtest)
→ aggro/leash → generalise FSM+steering → threat director. Open taste/scope Qs in the doc (how cozy vs hard;
dodge-only vs block/parry; is threat zoned; how many new enemy roles). Full evidence:
`investigations/deep_research_2026-07/combat/`.

## Next — HUD: bigger hearts + access-button bar (planned, not built)
Plan exists (`~/.claude/plans` / the torch+HUD plan). Bigger/nudged hearts; bottom rounded-square
access buttons (Inventory works; Ecologist/Mayor/Herbalist locked w/ toasts); Apico-style layout
(hotbar→top) OR keep bottom — DECISION pending. Needs `UIFactory.MakeButton` + `btn_square` art + a
reusable `ToastUI`. Also backlog: how players learn WHERE those NPCs are.

## Next — perf: bound the ground-item pile (decay pass grows O(items))
**Diagnosis (2026-06-22, investigate-only):** the `decay` system pass climbs monotonically over a run
(33k→435k µs/game-day on `village_21_B`, 8 days) because **ground-item count keeps growing** —
`processGroundItemDecay` ages EVERY item each tick (inherently O(total items); a spatial index does NOT
help it). The accumulator is **rotten fruit from fruit trees**: lifetime `rottenFruitDecaySeconds = 5040s
= 6 game-days` (`handlers_farming.go:29`), produced continuously by trees + windfall, faster than flies
eat or it expires, so it builds toward a high 6-day steady-state. Carcasses (`killDropLifetime = 60s`) are
negligible. Matches the documented old "immortal-rot → 40k+ items" history (`zone_persist.go:500`).
**Fix options (separate effort):** (a) **expiry-bucket the decay pass** — schedule each item's despawn
tick in a per-tick bucket so decay processes only items expiring this tick (O(expiring) not O(all)); and/or
(b) **bound the standing rotten-fruit count** — shorter rotten lifetime, a per-cell cap, or a lower tree
drop rate (a gameplay/ecology lever — run it through the 6× bug_lab chart loop). Verify: equivalence /
sim-determinism + re-profile that `decay` flattens. Note: the FindNearbyFood chunk index already removes
the *food-search* sensitivity to this pile (committed); this item is specifically the decay-pass cost +
the underlying unbounded accumulation.

## Later — UNDERGROUND LIGHTING + LOOK OVERHAUL (Plan 1 BUILT M0–M3 · Plan 2 look-&-feel BUILT 7/7 · 2026-07-09)
Design (scored candidates, spike-gated): `docs/product/architecture/architecture_lighting.md`. Evidence (each
through 2 adversarial critic rounds): `docs/product/investigations/research_lighting_dark_underground.md`,
`..._look.md`, `..._look_and_feel.md`.

**BUILT + in-engine (pending owner Play-test validation — client-only, no sim/determinism surface):**
- **Plan 1 lighting M0–M3** (owner-confirmed working): world-space darkness multiply overlay (`DarknessOverlay`
  + `DarknessMultiply.shader`) = max(buried-from-solids, roofed), opened by carried-light reach; roof data path
  zonegen→Go→client (`OpCodeZoneRoofMap` 109); torches fade in like dusk via one smooth "how-dark-here"
  (`LampLight` reads `UndergroundDarknessAt`). Test vehicle: `lighting_test` zone.
- **Plan 2 look-&-feel P2-1..P2-7 (ALL built)** on `feature/profiling-upgrade`, awaiting Play-test: wind sway +
  hit-flash lit shader (`SpriteLitWorld.shader`, world-space motion; grain crops sway, vegetables don't) +
  `LitMaterials` routing · ambient dust (`DustController`) · blob shadows (`BlobShadow`) · hit-flash + camera kick
  + leaf/chip burst on chops (`HitFlash`/`HitBurst`/`CameraFollow.AddShake`) · lily-pad bob + reed sway · emote
  bubble system (`Emote`, F6 test trigger) · **P2-6 animated water** (`WaterAnimated.shader` = copy of
  `SpriteLitWorld` + world-space seamless distortion/shimmer; a runtime second Tilemap under the Grid, sorted
  "Ground" order 10; centralized `IsWaterTile`; additive + graceful-degrade to static water; calm/flowing/sparkle
  are material dials). Test vehicle: `feel_test`. Tuning dials are owner Play-test work.

**STILL DEFERRED:**
- **Lighting M4:** roll the roof mask out to the REAL underground zones (`ant_tunnels_30`/mining), cross-zone
  seams, save migration, digging-updates the mask; run the M2 **2-client determinism gate** (roof is cosmetic →
  expected IDENTICAL, run when the owner's not connected).
- **Tree improvements** (owner 2026-07-09):
  - **Recreate the tree art**: regenerate `tree_oak` (+ other trees) via the sprite pipeline
    (`add-object`/`regenerate-sprite`). Art task. Blob-shadow read on trees improves once the trunk is redrawn.
  - **Cutting-down animation**: a proper felling animation when a tree is chopped (lean/fall + a stump left),
    beyond the current hit-flash + leaf burst. Owner wants it eventually; out of scope for now.
- **Water follow-ups (experimental):** shoreline **foam** = BUILT (world-space shore-mask swash) · specular
  **sparkle** default-on · reflections · **lava** animation (same overlay, different material).
- **Part II look phases** (flicker, post-processing bloom/grade, god-rays) + broader look-&-feel backlog below.
- **Owner-taste Qs** (mostly settled during the build; revisit if needed): scalar/binary roof (light shafts),
  palette mood, emission tooling, normal maps, player-light-underground.

**Original owner spec (still the requirement — the reference the build targets):** the outdoor top of the ant
zone and of the mining zone follow the normal day/night cycle; everything past that is dark. Inside any mass of
ore blocks, the inner blocks that are surrounded are dark, as in Terraria. (At the time, all lighting was
backlogged while the zones were built.)
- Surface strips of (3,0) + (3,1) get normal day/night; DARK below/past them.
- Terraria block rule: any block cell fully surrounded by blocks renders dark (applies to
  ore masses on the surface too — inner blocks of a mass are dark).
- Full-dark underground + flashlight (already designed, game_design.md ~720); glowworms +
  mushroom_glow are the natural sources (D21); zone docs place them to double as future
  light anchors so the lighting pass never rearranges rooms (R5).
- **CROSS-ZONE LIGHTING (owner 2026-07-07):** lighting must be continuous ACROSS zone
  seams, not per-zone-isolated. A lit surface zone bordering a dark underground zone (e.g.
  bee_meadow/ant_tunnels surface ↔ the underground below) must transition believably at the
  boundary — no hard light/dark wall at the seam, and a player straddling the edge sees one
  coherent light field. Design the lighting model to read the neighbor's light state (or a
  shared day/night + depth model) so crossing a zone line is seamless.

## Later — ANT mechanics riders (owner review 2026-07-07)
- Ants CARRY real items to chambers (fruit/rotten fruit/dead bugs -> granary caches) —
  the transport mechanic; v1 granaries are authored caches of real items.
- The ant BROOD system deep pass (the owner deferred all brood testing to here) — lifecycle,
  harvest response, defense tuning.
- Scouts are BASED in the lower colony and head UP AND OUT across zones — rides the
  real cross-zone transfer below.

## Later — UNDERGROUND BUG ROSTER (owner ruling 2026-07-07: all bugs backlogged while the zones are built)
Built AFTER the row-4 zone terrain. The zones PLAN the spawn locations; these are the sims.
- **Warrior ants** (soldier caste — BLACK ants): guard the Queen; turn aggressive near her; the
  general **defender response to STEALING/DAMAGING** (also the fix for players stealing boats/
  containers). This is the mechanic behind the (4,0) Queen "just chills, guarded by warriors."
- **Cave fly** — a NEW, REAL underground fly, faster + stronger than surface flies (a real
  cave-dwelling fly; owner: all bugs must be actual bugs, never invented).
- **Aggressive raid centipede** — GREEN variant, REUSE the existing garden-centipede sprite, tuned
  MORE aggressive than garden centipedes; dens at the (4,0)↔(4,1) raid seam and raids the colony.
- **Scout tuning** — scouts share the workers' home but wander much farther; must reliably FIND +
  return food, and IGNORE near-nest food (don't over-provision — ants forage). Tuning, not a spawn.
- **Glowworm** species (light keystone + catchable, firefly-style lantern) — the (4,1) grotto light.
- **Cave spider** species (webs slow prey via a speed-debuff; pounce hunter) + webs decor.
- **Aphids** (livestock/honeydew mutualism, disruptable).
- **Live cross-zone bug traffic** (real transfer; already sketched below).
- **Black mold hazard** — needs a POISON/hazard-cell mechanic (verified 2026-07-07: none exists);
  build the mechanic, THEN mold that poisons on contact can be placed. (Not decorative-only.)

## Later — POLISH ALL ZONES to the craft bar (owner 2026-07-07)
**2026-09-27: now a full redesign of every built zone (D53)** — see the parts 10–14 section above.
Bring the existing zones (village_21_B, bee_meadow_20, underground_passages_31, …) up to the
standard set building ant_tunnels_30: natural dirt/stone INTEGRATION (substrate model, not flat
fills), NOISE-FADED boundaries (never straight material lines), clean prominent entrances, wooded-
by-default with real carved clearings, neighbor edges that actually connect. Folds in the already-
listed bee-gradient removal + mushroom-realism sweep (ANT-ARC BUILD PREP below).
CRAFT RULES set this session (also in CORRECTIONS.md): **NO CEILINGS** (overhead view can't show
them — no ceiling glowworms/stalactites/star-fields; features are floor/wall based); **micro-stories
must be compatible with real game mechanics** (don't assume unbuilt mechanics).

## Now — ANT-ARC BUILD PREP (owner decisions 2026-07-06, do alongside the (3,0) build)
- **bee_meadow_20 — REMOVE the south dirtying/rocky GRADIENT** (zone_bee_meadow_20.py §1b:
  the `gradient_field` + rock_masses + torn-ground rubble + dead-tree/dry-flora band along
  the south edge) — the owner wants that space for meeting ants, and more spread-out forest. Its original job (blend into
  the ant zone below with no sudden dirt wall) is gone now that ant_tunnels_30 is
  half-outside and carries its own cliff transition. AFTER: restore meadow to the south
  edge with more spread-out forest. **Keep the Rocky Gorge (§1c, the stream's east exit) —
  a separate feature, untouched.** Re-save the zone + view_world.
- **Mushroom realism sweep — REPLACE the two generic ids** (`mushroom_cluster`,
  `mushroom_brown`) at all 17 placements with existing real species (morel, inkcap,
  chanterelle, puffball, bracket, red, glow…), then DEPRECATE the two generic entities.
  The owner wants real mushroom species, not generic clusters. Touches many
  zone_*.py + regen; no new art (real species already have sprites). Ant zone already uses
  inkcap/morel natively.

## Next — the village and the world map, as built (found 2026-09-26 while researching GDD §01)
- **One village.** The June review settled it: the starting village is `village_21_B`, not the old `village_21`
  demo (`economy/DECISIONS.md` D19). The game still starts new players in `village_21` ("Normal", first in the dev menu,
  `WorldMenu.cs`; also the server's fallback, `rpc/world.go`, `match.go`), a village with no vendors that nothing links
  back to — walk south from it and north again and you arrive in `village_21_B`. To do: start in `village_21_B`,
  drop the one-way link and its exception in `zone_links_test.go`, and move `village_21` to the test zones (the sync
  harness's `crosszone` scenario and its default zone still use it), and update the comment in `zone_links_test.go`
  that still calls this an open question. ⚠ `tools/zonegen/scenes/zone_village.py` saves `village_21` whenever it is
  run, without neighbour links — don't run it until this is done.
- **Doc errors found:** `architecture_world.md` says zones are 64×64 with 16×16 chunks (they are 256×256 with 32×32),
  that players wade shallow water (it blocks them), and that the player is 3×2 cells; `village_21_B.md` says "no
  transition system exists yet" (crossing works since 2026-06-16); `demo_slice.md` says a 24-zone world (20 now).
- **Crossing details:** `CrossZoneController` hard-codes a 256-cell zone (`ZoneMax = 255`); worlds created through
  `WorldJoin` get no neighbours, so they have no crossings; 88 crossing points land on a solid square (measured at the
  square under the player's feet, the one the game checks), 35 of them boxed in, worst on the Ant Tunnels ↔
  Underground Passages seam where the openings on the two sides don't line up — the "blocked zone entry" item on the
  roadmap.

## Next — the game against its design (found 2026-09-26 by the full design read; see `docs/gdd/overview.md`)
- **Processing stations missing from every playable zone.** The rock crusher, bug extractor and gem cutter stand only
  in the `crafting_test` zone; no recipe makes them and no shop sells them. So in normal play mined ore can't be
  refined (every bar recipe needs refined ore, which needs paydirt from the crusher), carcasses can't become chitin,
  leather or formic acid, and gems can't be cut. The blacksmith sells copper, iron, bronze and steel bars; silver,
  gold and platinum bars are neither sold nor makeable, so the top three metal tiers are out of reach. To do: place
  them where the design puts them (crusher and gem cutter at the mine beside the sluice; the bug extractor in town,
  D18) and settle how a player gets their own (D1). Data slip: `gem_cutter` drops a `rock_crusher` when broken.
- **Eleven of the fifteen stations can't be crafted or bought** (D1 says crafted or bought): the workbench, furnace,
  anvil, forge, sawmill, stonecutter, ore sluice, honey extractor and the three test-zone stations. Only the Weaver's
  four (loom, spinning wheel, sewing machine, dye vat — made at the workbench from recipes she sells), a campfire, a
  wood stove and a keg can be made. The only way to own one of the others is to break one where it stands and carry
  it off, which the decided protection of townspeople's property will forbid.
- **Unobtainable items.** `large_net` (no shop, no recipe) — so wasps, soldier wasps, giant hornets and dragonflies
  (all `net_size: medium`, large net only) can't be caught in normal play; `spear_wood`, `scythe_wood` and
  `shovel_wood` (starting kit only); `backpack` (no shop, recipe or placement — only the developer give-command;
  D19's storage ladder is small sack → large basket → backpack); no bronze tools although bronze weapons exist; the
  `floral_furniture` recipe book is sold by no one, so its 8 recipes can't be learned.
- **Magnifying glass.** D12 gives it from the start; the starting kit (`state.go`) doesn't include it (the general
  store sells it for 40), and it does nothing yet (see "Bug RESEARCH mechanic").
- **Floors don't stop bugs appearing** (the December 2025 requirements lock that rule): the spawn check honours only
  `blocks_bugs`, and no ground tile sets it.
- **Night danger is idle.** The night-hunter mechanism exists, but no species is night-active — by design, since
  real wasps and hornets hunt by day (the true-bug rule above); it waits for a real night hunter. `hornet_giant`'s
  description still calls it nocturnal.
- **Dormant hives.** `village_21_B`'s four beehives never wake: `bee_honey` isn't in that zone's roster.
- **The autonet catches nothing** — it is a storage placeable today (see "catching gear: auto-catcher").
- **Nest drops disagree.** Wasp nests drop nothing when broken, by design (D23 removed that drop); hornet nests
  still drop paper and larvae. Make them consistent.
- **Nursery gaps.** Milkweed and compost bins can't be seeded from empty, and nursery deposits and takes fail silently
  — every refusal in `handlers_nursery.go` returns without a message.
- **Hard population caps.** Each zone has a hard ceiling per species (`village_21_B`: flies 1,500, butterflies 800,
  wasps 120, centipedes 140, millipedes 200, beetles 140), while the owner's direction is that food, predators and
  age bound the numbers. Decide whether they stay as safety nets.
- **The Ecology tab doesn't exist** — only the F5 developer graph; noted beside the roadmap's brief.
- **An unused sound library.** 203 bug-sound and music files under `Audio/` (committed 2026-07-29) are neither in
  the Unity project nor used by the game; check their licence before use (roadmap Phase 4).

## Next — from the owner's review of the overview, parts 0–3 (2026-09-27; D32–D41)
The design lives in `docs/gdd/overview.md` and `economy/DECISIONS.md` D32–D41; this is the build work it creates.
Items marked (P#) wait for the owner's verdict on that proposal.
- **Prototype rules that go** (they change the shared simulation — frontier-sync gates apply): bees, dragonflies and
  fireflies stop flying over fences (`flies_over_fences`); the wood-is-gnawable / stone-is-immune rule gives way to
  fence strength against bug strength; carrion beetles stop making compost (`produces_compost`); centipedes spread
  out instead of moving as packs; calming values are set per species.
- **Fencing overhaul** — posts that connect, with materials of different strength (P5).
- **Catching** — bug size classes, hand-net limits, placed catchers, the autonet's drawing zone (P3); traps and bait
  (P4). Give the large net, the bug extractor and every other unobtainable item a way to be obtained (D37).
- **Butterflies in the world** — caterpillars leave the nursery, grow, pupate and emerge (D38; P7).
- **Research with the magnifying glass**, filling the bug's information page (D40; P8).
- **The Ecologist's quests, the monitoring station and the Ecology tab's unlock** (D40; P9).
- **Village property** — players can't damage or take it; bugs can damage village fences; villagers repair them
  (D41; P6).
- **Ecology retune** — fewer fruit on the ground with another lever raised; the other changes in P10.
- **Compost as fertiliser** — and the compost item's description should say so.
- **Species** — real names for all fifteen; the ant species cut to black and fire ants; birds, amphibians,
  reptiles and mammal-era things removed from the designs (D32, D39).
- **Lighting** — the whole lighting system is a prototype and needs its own improvement pass.
- **Opening text** — a placeholder; rewritten once the premise section is final.

## Next — from the owner's review of the overview, parts 4–9 (2026-09-27; D42–D48)
- **Rain shows nothing (diagnosed).** A shower waters crops and fruit trees, but the droplet over a tree means "not
  watered by you today" (`last_water_day`), which rain doesn't set, so it stays; and rain only turns a plot wet when a
  crop is in it (`rainWaterAll` loops over crop states). Fix: rain counts as the day's watering for trees and wets every
  tilled plot.
- **Underground darkness into the real zones** (today only `lighting_test` has the tunnel data); ant zones built of
  dirt, mining zones of rock (D43).
- **Ownership**: things that belong to townspeople or camps — stations, beds, fences, goods — refuse players, with a
  short message (D41, D44, D45); abandoned beds and stations are free to use or take.
- **Building**: doors that turn to fit their wall (+ a side-facing door sprite); ground laid in whole squares (the
  diagonal shapes go) and the shovel's dig/lay switch (P12); tents three squares wide; mannequins showing whole outfits
  on a white-faced figure.
- **Combat**: swarms attack together in sync (the two-attacker pool goes); wind-ups only for lunging species; the axe's
  swing attacks; stamina (P14); dragging big subdued bugs (P15); bosses (P13); aphids living on plants, shown in the
  plant's view.
- **Gear**: one outfit slot in place of the eight equipment slots; base characters in several skin colours by
  recolouring; the alchemist's robe and a potion station (the wizard's robe goes); new accessory ideas; the tiers.
- **Farming and mining**: wheat seeds from the Locust Farmland (the village stops selling them); plants cut down and
  processed (P11); a carrying limit; the prospecting pan.

## Next — from the owner's review of the overview, parts 10–14 (2026-09-27; D49–D53)
- **Tools**: the gold tier leaves the tools (pickaxe, axe, shovel, hoe, scythe) and the metal ladder is settled
  without gold or diamond (§09; gold swords and spears — the suggestion is that they go too); the unused `durability`
  field (43 items) and the durability bonuses in `economy/stats_and_bonuses.md` go; the pickaxe gets the axe's motion
  when the worked-out tool motions go in.
- **Food, potions, healing** (P16 and P17, accepted — D54): timed effects first (nothing in the game can give one
  yet), then venom and poison on stings, then the cures; meals that heal over a while with one fullness boost at a
  time (with the recipe list); healing potions with a short wait for the person healed; antivenom, salve, venom
  resistance, night sight; bandages; the cauldron's recipes; food that doesn't spoil in bags; right-click a player to
  offer items, bugs or coins; left-click to heal a friend; a new drop action with a per-zone limit.
- **Fishing in the village**: place the Fisherman — his spot at the boat store (`zone_village_21_B.py:222`) is blocked,
  so he was skipped when the village was saved (`investigations/missing-npcs-village21b.md`); then the fishing
  mini-game, rods, bug baits, fish traps and boats.
- **Water and the coast**: a wading outfit for shallow water (slow wading), boats for deep water (today every water
  tile stops players); the coastline into the western and eastern zones; the bug-shaped island in an inlet off the west coast;
  natural water barriers between areas.
- **Trade** (P19, accepted — D54): one trade screen — a "to take" box beside the "to sell" box, goods counted at the
  townsperson's buying price, coins making up the difference either way, one step that swaps everything at once
  (tested against duplication like the sell box); fish for the fisherman, stone for the stonemason; coins from many
  sources.
- **Shop screen bug (found 2026-09-27):** `ShopPanel.RowOfOffers` skips every offer after the sixth (`col >= 6`), so
  the general store's last 13 goods (small net, both watering cans, wooden hoe/pickaxe/axe, calm spray, magnifying
  glass, gardener's gloves, cot, torch, lantern, wooden fence), the blacksmith's last six (copper and iron axes,
  copper sword and spear, copper helmet, iron chest) and the carpenter's seventh recipe (picket gate) can't be
  bought. Data slips: the carpenter's `buys: furniture` matches nothing (79 placeables have the furniture category,
  none the tag, and `shopBuysItem` matches ids and tags only), and the blacksmith's `metal` tag covers ores as well as
  bars (D26 says bars only).
- **Townspeople** (P18, accepted — D54): shopkeepers at their counters by day; chores (mending fences, gathering
  fallen fruit, dealing with bugs that threaten people) early and late or by townspeople without a shop; sleeping at
  home at night, where players walk in and trade; townspeople become moving characters shown to every player, and
  their chores go through the same sync checks as a player's; quests from several townspeople; the myrmecologist's
  retrieval board.
- **Towns**: the western town's strings of lights and other electric things; the starting village mostly unpowered,
  its windmill lighting only part of it (the Mayor's house) as a glimpse of power to come, and not takeable.
- **World**: bugs spawn only in their own species' spawn areas and are free to cross zones (with "REAL cross-zone bug
  transfer" below); every built zone redesigned (`village_21_B`, `bee_meadow_20`, `underground_passages_31`,
  `ant_tunnels_30` — some village houses don't meet the roads; this replaces "POLISH ALL ZONES"); secrets everywhere,
  the underground fortress being one example; the document disagreements (the ranger station, Spider Vale East)
  settled with the owner.

## Next — from the owner's review of the overview, parts 15–20 (2026-09-28; D55–D60)
- **The item table** (D55): every item in the game — prototype data and the designed catalogues — with a recommended
  add, change or cut and a one-line reason each; the accessories first. The owner reviews it before anything changes.
- **Stations** (D55): the anvil, forge and other basic stations placed in the village at the blacksmith's and the
  other shops — usable, owned by the townspeople, never takeable; other stations in the first few zones; powered
  versions where generators are sold or built. (Pairs with "Eleven of the fifteen stations can't be crafted or bought"
  and the ownership item above.)
- **Metal ladder and tool tiers** (P20, P21 — accepted, D61): tools wood → stone → copper → bronze → iron → steel →
  cobalt steel → tungsten carbide; weapons to steel, then bug-part blades and spears; armour follows the metals, with
  platinum in a fancy armour that also needs steel; two new ores (cobalt, tungsten); gold, silver and platinum leave
  tools and weapons for money, power parts and jewelry; hits = tool strength − material toughness (the break handler's
  one-point-per-hit goes; the unused `mining_speed` becomes the strength); co-op digging adds up; power tools (a rock
  drill, a chainsaw) in the top tiers. Tier counts per tool come from the item table.
- **Automation** (D56, P22 revised): a hand pump (a well on the farm) filling a cistern that the sprinklers draw on,
  then a powered pump; sprinklers water everything in reach, trees included (D62); crops need one watering a day
  (D61 — `max_daily_waterings` 2 → 1 in `crops.json`, retuned); sprinklers — small ones in the village shop, priced to
  save up for; larger ones in the western town; powered appliances usable inside the Mayor's powered area; the Mayor's own appliances usable; other
  villagers' houses lit by torches and bug lanterns. No hired workers anywhere (the NPC workers of
  `design/game_design.md` §11.2 go).
- **Time** (D57): one world clock (the roadmap's per-zone `DayOffsetTicks` plan); no night skip; the world stops only
  when nobody is online; border events from frozen neighbours (P25).
- **Weather and tuning** (D57): remove the ecology director's weather steering (`ecology_director.go`: droughts when a
  species is high, extra rain when one is near collapse) as part of the bug overhaul; polish and update bug behaviour
  first, then retune everything with many levers (P10); droughts and rain keep a rhythm of their own.
- **Playing together** (D58): drop the eight-character cap (`nakama/modules/rpc/character.go`
  `maxCharactersPerAccount`); a server setting for player-versus-player; private plots invite-only with the January
  2026 plot design and a happiness panel (P26); **a thorough review of what still runs on the server**, each piece
  justified — bug behaviour stays on the players' computers.
- **Interface** (D59): tutorials (P23); controls and settings (P24); a polishing pass on every system with
  suggestions.
- **Art and sound** (D60): the interface and the blocks drawn in code and iterated with the owner; townspeople by
  gpt-image-2 — walking frames, floating hands, a face portrait, many ethnicities; lighting (compare Necesse; Unity
  screen effects), hit feedback, wind sway only on plants — swaying follows the `natural`/`flora` category today
  (`TilemapManager.cs`), so about 25 solid things sway, among them `standing_stone`, the crystals, `stump`, the logs,
  the nests and `shipwreck_hull`; a sound library and zone music made in code (research the method first), alongside
  the owner's music packs.

## Later — REAL cross-zone bug transfer (owner 2026-07-06: real transfer, not a pretend version)
Zones are isolated per-match sims today (Neighbors is player-only). The real feature:
a bug/swarm that walks off a connected edge LEAVES zone A's sim (a ledgered removal) and
ARRIVES in zone B's sim (a ledgered spawn at the matching edge) — two zone-local ledger
events, no shared sim state, each zone stays independently deterministic; transfer routing
via the existing Neighbors map. Until built: NO fake edge-spawn pretense; ant populations
stay zone-local (D21's "ants cross into the Mining Camp" waits for this).

## Later — MARBLE (owner 2026-07-06: an idea, backlogged)
The material exists (style.json marble palette; column_marble; wall_marble client-side).
Future: a quarry source in the deep zones (row 4), statues + fountains crafted at the
Stonemason (D27 sculpture yard), and the marble premium furniture tier (P2 of the
underground-arc plan adds table/bench/bust_marble as stone-set premium overrides).

## Now — ANT TRAIL FEEL-BAR (open; mechanism proven, rate-tuning remains)
The underground-arc P3 shipped the ant colony sim (species, nest gates, colony memory,
commitment, recruitment, reinforcement, coalescence — all gated: go suite, determinism,
latejoin x2 SYNC IDENTICAL, zero new ledger events). The visible nest→carrion FILE has
not yet formed in the open-field lab: 11 evidence-logged runs (ecology_tuning_log.md),
two named bottlenecks left — (1) recruit-eligibility filter (needs one instrumented
run), (2) scout coverage (patrol-bias lever). Owner decides at the review package
(docs/product/investigations/underground_arc_review_package.md): finish in the lab now,
or bar it on ant_tunnels_30's real tunnel geometry when built.

## Later — creatures: ants & spiders (DESIGNED, not built) — **PAIR WITH STEALTH**

> Owner 2026-08-06: run this **together with the stealth bonuses** (see *Player sprite + wearable creation
> system*). Spiders are the only source of silk, silk is what the stealth line is made of, and `silk`
> (`items.json:1631`) is an orphan id today — it exists with no recipe and nothing that drops it. Building
> spiders without stealth leaves a material with no purpose; building stealth without spiders leaves a set
> with no material.

Full approved design: **[design_ants_spiders.md](ecology/design_ants_spiders.md)**. Ants = a foraging colony
(hill/queen/eggs reuse Nest+Brood; workers forage carrion → carry home via the wasp provisioning loop;
scouts + server-only "colony memory" make trails emerge — no per-cell ACO grid). Spiders = a web-builder
ambusher (web tiles slow prey via a server speed-debuff; reuse occupant placement + `OCCUPANT_BLOCKS_BUGS`)
+ a jumping/stalk-pounce hunter (reuse the centipede `ActionState` lunge). Determinism-light (ant trails add
zero sync surface). Build spiders first (lower risk); ants are Med–High complexity. Includes Step 0 = the
rotten-fruit decay fix (bound the pile).
- **Spiders & webs in the underground (owner priority)** — finish adding the cave spider + its webs to the
  FIRST underground zone (Underground Passages / Mining Camp). Per the zone sheet it's the dark-warren ambush
  species (`cave_spider` drops from the ceiling on silk; web-choked side-passages; `cave_spider_silk` is the
  zone's soft-material spine) — designed, not yet placed/wired into the zone.

## Later — content layer (agriculture + crafting depth) + station minigames
- **Flesh out agriculture & crafting (finish the content layer):** the systems exist (crops, crafting
  stations, recipes, containers); this is the CONTENT pass — more crops/recipes/stations/products, the
  progression that ties them together, and the missing art. Needed eventually, not now.
- **Station minigames:** interactive minigames at craft stations (e.g. a timing/skill step when smelting,
  brewing, etc.) instead of a pure timer. Polish/engagement layer on top of the crafting system.

## Later — catching gear: auto-catcher + fly nets
The catch system already exists (net sweep + `net_size` small/large gate, `CatchingController`/
`BugReleaseController`); this is the gear layer on top of it.
- **Auto-catcher (placeable):** a passive bug-collection station — set near a swarm, it slowly catches
  bugs in range into a capped internal buffer the player empties; the bug-farm chore-relief device
  (cf. the `egg_collector` sketch in `docs/brainstorms/objects/storage_automation.md`). Must be
  **capacity-bounded** so it can't strip a farm, and respect the existing "what the bugs eat belongs to
  the bugs" rule. Likely a placeable with its own panel + a designed catch rate and species whitelist.
- **Fly nets (tool tiers):** dedicated nets for flies/butterflies — extend the small/large net ladder
  (e.g. small → large → specialized) with their craft recipes + diagonal tool icons (the same
  `net_size` enforcement already decides which species each net can take).

## Later — sprite review (manual, by hand)
Go through EVERY sprite by hand and fix/redo the ones that read wrong (Andrew edits on his end). Many
were auto-generated; quality varies. NB: a bare `pixelclean.py` re-cleans ALL sprites — regenerate +
clean ONE key at a time and revert incidental churn.

## Later — economy reconciliation follow-ups + item-model tech debt (from the 2026-06-26 catalog pass)
The catalog consolidation is **done**: 5 as-built pages (furniture/containers/decoration/structures/plants) +
materials blocks&deposits, `architecture_items.md §1–15` retired, `tools/data/catalog_coverage.py` no-orphan gate
green, the recurring rules logged as DECISIONS D22. Open follow-ups the user adjudicates:
- **The economy FEATURE itself** — buy/sell/NPC/dialogue/trading + recipe-acquisition (default/bought/found
  unlocks). The *data + catalogs* are ready; the *gameplay loop* (shops, dialogue, coin sink) is not built.
- **Per-item recipes & costs** — `recipes.json` only has ~10; the catalogs propose `source` (🔵) but not the
  ingredient lists. Author recipes per the crafting.md ~70/20/10 split.
- **Rock-decor / cave-scene rework** — "leave decor as-is for now"; `boulder` + `sandstone_formation`/`cave_moss`
  art/placement deferred. Decide keep/cut `boulder` + the `*_test`/look-alike entities the catalogs flag.
- **Tech debt — capability-based gating (8a):** stop overloading `category` as a behavior gate. Resolve
  tool/weapon/armor behavior from capability fields (`tool_type` present, `armor_slot` present) so recategorizing
  an item can't silently break `getToolStats` (handlers_world.go:693) or the armor-equip gate (:859). (This pass
  used the minimal `||"weapon"` fix deliberately; the clean refactor is here.)
- **Tech debt — data-schema lint (8b):** a committed validator for the entity JSON (category ∈ known enum, every
  drop/recipe id resolves in the unified registry, every drop has an item entry or is flagged). Extends
  `catalog_coverage.py`'s reports into a CI gate so the class of bug behind the 2026-06 doc-drift can't recur.
- **Icon polish (optional):** the 6 new herb items + the occupant-only drops (cacti, several mushrooms, `geode`,
  `reeds`) render via world-sprite fallback; dedicated `_icon.png`s via Pipeline A when art has time.

## Later additions from this slice
- route_road taper option (band narrows at zone edges, like path(taper_ends)).
- Chaikin smoothing pass on route_road centerlines (research; only if 45°
  quantization ever shows through smooth_paths' bevels).
- **The river-zone slice**: the stream + `terrain.bridge(b, start, end)` (engine-free —
  walkability is the tile-id switch; bridge tiles replacing water are walkable both
  sides). Recorded geometry from review: a gx≈40-50 stream needs TWO bridges
  (≈(44,130) + ≈(47,182)) or it walls off the west third.
- **Player-placed road AUTOTILE**: when tile placement lands, run the smooth_paths
  neighbor rule server-side on placement — no manual sprite flipping.
- Occupant-on-water support so lily pads can live in SAVED zones (today decor =
  render-only; the boat-store furniture un-reserves water as a special case).
- Side-door TEXT-GRID pieces (composer + place_room already do all sides).
- A leaf-litter/forest_floor ground tile (deep forest uses dirt=True meanwhile).
- ~~A frog ambient critter for the lake (intent doc wish).~~ — frogs rejected (2026-07-05, `economy/DECISIONS.md` D31).
- Subdue/drag/revive (smoke tool) — the centipede capture path (trap_only reserves it).
- Millipede: the peaceful detritivore on the same individual chassis (eats rot, makes
  compost). Dragonfly: prey:[wasp_common] — pure data + sprite (the chassis proof).
- Second wasp type (yellowjacket ground-nester); craftable hive box; roofed enclosures
  (blocks_flying); predator starvation (needed for finite-prey private plots);
  nocturnal centipede aggression; bee mass-sting damage scaling (per-swarm cooldown is
  the v1 cap); eat-fruit-to-heal (regen is the placeholder).
- Forest zone proper (docs/guides/authoring/forest.md collects the rules); village
  remake folds the test patches into real content.
- P8 curved legs (protocol bezier) — default-skipped; revisit only if the serpentine
  read disappoints; gate = sync-harness hash parity.
- spawnKillDrops directional scatter along the death trail (drops currently burst-jitter).

## Later additions from this slice
- Falling-fruit tween (canopy → ground arc) — falls currently just spawn the ground item.
- Underground full-dark zone ambient flag (flashlight required) — designed, not built.
- Weather ledger v2 (per-cell deterministic rain — designed in architecture_weather.md).
- Rain audio; sun/moon arc dial to replace the text clock.
- Tree-shake harvest animation + canopy rustle on knockdown.
- Shop entry for the flashlight (starter panel slot 15 has one for now).
- Hands as a permanent un-droppable slot-0 fixture (v1: a normal loseable item).

## Later additions from this slice
- ~~Zone swarm-count cap for releases~~ DONE (force-join nearest + max_population hard cap —
  see §13). Optional per-player release cooldown still open (validateCooldownTicks one-liner).
- Release-moment feedback polish (a "−N flies" popup like CatchPopup).

## Now — Scene 1: player house + fly farm
- House DONE (the ⊥ cottage, full real art). Fly farm FIRST PASS done
  (`scenes/scene1_player_farm.py`): netted fly pen (apple trees, fallen/rotting fruit, flies on
  ground + netting, autonet, compost bin, broken net, apple crate, the farmer), orchard, garden
  (fountain, benches, beds, lamps), paths, scattered decor + butterflies/bee. Pending:
  - **Generate the farm art** (placeholders now): fountain, compost_bin, autonet, fly_netting,
    fallen_fruit, rotten_fruit, rock_small, rock_mossy — `OBJECT_DESC` ready in `gen_sprites.py`.
  - Iterate the garden/pen layout; confirm the **decorative-rock** decision (vs the old
    "no standalone rocks, use stone_block" rule).
  - **Unity Play test** of the tall-sprite pivot fix + orientation (verify in-game vs preview).

## Now — Safe cleanup only (no refactoring, no splitting files)
Tidy what's clearly safe; leave anything risky alone.
- ~~Delete dead player-art spikes in `gen_sprites.py`~~ DONE (removed `recolor_skin`/`SKIN_*`/
  `PLAYER_STYLE`/`char_sample_prompt`/`body_prompt`/`walk_sheet_prompt`/`build_walk_set` + their CLI
  flags; kept `segment_sheet` + frame helpers per the multi-frame item).
- Remove scratch/clutter and any empty dirs left over from earlier reorgs.
- No structural refactors, no god-class splits — those are deferred until we have a way to verify
  them (there are currently no automated tests).

## Player art model — BALD BASE + hair-as-a-layer (owner decision 2026-07-20, REVERSED the earlier "baked-in")
> **Superseded (noted 2026-09-26):** this was the layered paper-doll model. Outfits became whole images on
> 2026-07-28, each drawn with its own hair, and today's base (`tools/_generated/player/bases/armless_front.png`)
> has hair. Whether players choose hair or skin under whole outfits is an open question in GDD §08.
The player BASE is now **BALD**; hair is a generated+masked **layer** like armor (owner decision: hair is handled
like the other parts). Locked bald front = `refart_spike/bald/base_down_bald_FINAL.png`
(`_REVIEW/LOCKED_bald_front.png`). `CharacterComposer` already draws `hair` as its own layer under `helmet`, so
this fits. Hair generation is proven (`refart_spike/hair/_hair.png` — `neat_short`+`tousled_mop`, face kept
pixel-identical via composite-in-post). TODO: build the hair-layer library on the bald base + a matching
running-sideways base (first frame done: `_REVIEW/11_bald_running_sideways.png`; a run CYCLE needs several).
- **Caps/hats now WORK with this model** (were blocked when hair was baked in): with hair as a layer you can use
  a **"hair-under-hat" flattened-hair variant** (Stardew-style) so a cap shows hair only below the brim. Crown-
  only head-gear mask (top ~16%, above the eyes) prevents the generator eating the head — fold into the pipeline.

## Next — client reconnect / self-heal (deferred from the 2026-06-13 freeze fix)
The logging fix removes the *cause* of the `session outgoing queue full` close, but the client still
has NO reconnect — `NetworkManager.Socket.Closed` only logs + invokes `OnDisconnected` (sole
subscriber: DebugPanel). Make a server-side close self-heal instead of freezing. Done correctly it
must: clear `WorldManager.CurrentMatch`, reset SwarmManager via the existing `RequestResync()`
(SwarmManager.cs ~580), re-check session expiry before reconnecting, and wait for
`ZoneAuthority`/`LateJoinSnapshot` before resuming ticks. Repro: kill/restart the server mid-session.

## Next — Tool ANIMATION improvement (Andrew, 2026-06-12)
The in-hand tool animations (PlayerToolAnimator swing/sweep/stab/pour) need a
quality pass — the profiles are functional but stiff. Candidates: anticipation
frames (wind-up before the arc), easing curves instead of linear sweeps, a
small body lean on swing (the walk-frame rig makes 1px shifts cheap via
pixkit), impact pause/flash on hit, tool-specific follow-through. Pairs well
with the existing walk-cycle rig since both are code-driven.

## Next — Bug RESEARCH mechanic (the magnifying glass) + food boosts
The bug info card ships with locked rows ("Breeding: ???", "Favorite foods:
???") — this fills them:
- magnifying_glass item; per-species research level on PlayerState (use it X
  times on a species to unlock tiers: breeding plants -> favorite foods)
- food-source boosts: flowers/foods grant swarm bonuses (data per species)
- BEES (later): produce honey; gain more from some flowers — the info card's
  foods tier is where players learn this in-game
- armor DEFENSE (cosmetic now): armor_class per piece, server damage reduction

## Next — Zone-design guides cleanup
- ~~Consolidate the scattered/contradictory guides into one coherent set~~ **DONE** — `docs/guides/`
  split into `art/` (look & pipeline) + `authoring/` (zone/scene building, indexed by
  `authoring/README.md`); the dead `generate_zone.py` system (+ its `ZONE_GENERATION_GUIDE`/
  `BUILDING_TEMPLATES` guides) archived; zonegen code consolidated (`houses/`+`builds/` folded into
  `features/`+`scenes/`; scene registry → `zonegen/registry.py`; `artlab/` is now purely the viewer).
- REMAINING (design, its own plan): make generation **natural & non-rigid** — no dead-straight roads,
  no uniform scatter; encode that into the authoring primitives + guides.

## Next — Zone graphics: 6 preview scenes
Fill missing entity data, generate/clean remaining sprites, render 3 surface + 3 mining preview
scenes. Depends on the two items above.

## Decided against
- **Sideways / rotated furniture (side + back facing variants + place-rotate)** — explored 2026-06-24
  (gpt-image-1.5 re-edited 8 pieces to `_side`/`_back`, separate placeable keys, server `resolveFacing`,
  a place-time R-rotate + a furnished showcase house). **Scrapped**: most JRPGs don't rotate furniture, and
  in this strictly-flat 3/4 projection the side/back views add art + placement complexity for little payoff.
  All variant sprites, the rotate code, and the showcase zone were removed. The reference-image re-angle
  TECHNIQUE survives for animation (see the fly/butterfly flap work) — only the furniture product use is dead.

## Now/Next — economy, gear & town NPCs (DESIGNED — see `economy/`)
Full design folder: [`docs/product/economy/`](economy/README.md) — **start at the README map.** Reorganized
2026-06-25, one-concern-per-file: `progression.md` (pacing/gating + village scope, lens-justified),
`crafting.md` (the master recipe/cost table — all categories incl. sprinklers, bug-derived + artisan goods,
target floors), `merchants.md` (the 3 shops + craft-vs-buy matrix), `production.md` (**build waves — start
W1**), `DECISIONS.md` (every decision, resolved + open). Geography for it is in
[`architecture_world.md`](architecture/architecture_world.md) (restructured 2026-06-25: **rows 0–4** with row 5 deferred,
underground col-0 centipede→ants + Queen, Centipede Cavern→(4,1), + a resource/material dispersion map §1b).
**Zone authoring of the new 0–4 layout is its own backlog effort.** The **content** is now designed in full:
`economy/zones/` (17 per-zone content sheets) + `economy/catalogs/` (28 armor sets, 82 weapons, 88
accessories, ~102 tools, 78 potions + 47 meals, ~315 materials) + `species_and_drops.md` (84 species) —
intentionally over-produced to **prune down**, then wire via `production.md`'s waves. The big build items:
- **Player bonus/stat layer** (the foundation) — add a `bonuses{}` block to the item schema + a derived
  `PlayerStats` recompute on equip; wire `defense` + `damage_pct` into combat first so armor/accessories
  finally DO something. Today the only working bonus is the backpack `slot_bonus`.
- **Currency + merchant economy** — `coins` on `CharacterSave`, buy/sell RPCs + merchant panel (reuse the
  crafting/container plumbing). `sell_price`/`buy_price` are already priced in data; no RPC/coins yet.
- **Town NPCs (merchant, blacksmith, carpenter)** — new `interaction_type:"npc"` occupant + a dialogue
  panel: intro line on first meet (track "met" in `CharacterSave`), random tip thereafter. Sprites exist
  (`merchant_down`/`miner_down`/`farmer_down`); persist them via `place_occupant` instead of preview-only
  `place_player`. Ecologist/Beekeeper reuse it later (GDD §13).
- **Material stations + ladders** — sawmill (planks), loom (cloth), forge (steel/alloys), cauldron
  (potions), stove (meals), jeweler (accessory gems), honey_extractor — data + recipes once art lands.
- **Recipe acquisition** — per-character known-recipes set + the auto/buy@npc/find content split.
- **Gear content** — armor tiers, utility outfits (bee suit, fisherman's vest, miner kit…), accessories,
  trade-off items (a bonus paired with a drawback), consumables.

## Later — mining depth (the loop is thin; flagged 2026-06-24)
Mining is currently "tool_tier gates ore → break block → get ore" with no risk, variety, or reason to go
deep — and several designed gear bonuses (`ore_fortune`, `gem_luck`, `light_radius`, `hazard_resist`,
`fall_resist`, miner's kit) have nothing to hook onto. To make it a real loop (details: `economy/suggestions.md §4`):
- **Depth + risk**: deeper layers = better ore + hazards (darkness, gas pockets, fall drops, cave-ins).
- **Yield variety**: `ore_fortune` (double drops), `gem_luck` (gems/geodes in plain stone), rare nodes.
- **Tools beyond the pick**: drill (fast/AoE, later electric §11.6), dynamite (already a concept), ore
  cart/rail haul, prospector/vein-sense tools.
- **Deep-only materials** (mithril/adamant) that gate the endgame gear in `economy/item_catalog.md`.
- **Light as a real stat** — `light_radius` (lanterns/headlamp/placed torches); the flashlight is cosmetic today.

## Later — mechanics flagged by the economy content pass (2026-06-25)
These came out of designing `economy/zones/` + `catalogs/`; each needs its own design before wiring. See
`economy/DECISIONS.md` D10–D16.
- **Electricity (a whole EXPANSION)** — drills/powered mining run on **batteries** (buy, or find in chests) for
  temporary power, until a **battery recharger** unlocks. Recharger is gated by **WEALTH, not zone**. Treat as
  a large standalone expansion.
- **Signposts** — fast-travel/landmark posts (per-zone hub, unlock-on-visit; `architecture_world.md` already
  sketches the road+signpost system).
- **Cart system** — rail carts go left/right/up/down (diagonal TBD); lots of payoffs to weigh. *Research how
  Minecraft minecarts work* (powered/detector/booster rails, momentum) before designing.
- **Dredge mechanic** — place-on-water → station "dredge" button → player drags a hose and clicks water to
  dredge like a tool; weaker/stronger + condition variants (swamp dredge). Get the feel right (D14).
- **Potions & alchemy system** — the cauldron potion-crafting + buff/cure layer. (Venom/poison combat
  *effects* are assumed real mechanics, D16; this backlog item is just the potion-making system.)
- **Fishing** — a fishing **mini-game** + rod tiers + passive capacity-capped fish traps (no harpoons). Bows
  + **cast/thrown nets** + **bug-size matching** (a small net can't hold a big bug) ride along here.
- **Beekeeping system** — multi-level beekeeping: faster/stronger bees, some **hostile**, smoker tiers (≥3),
  hive management. The bee zones' content hangs on this.
- **Armour balance** — tune per-set DEFENSE against each zone's enemy damage once combat numbers exist (D11).
- **Home-plot décor bonuses** — the capped idle/comfort aura system (GDD §11.5) that décor + light décor feed.
- **Mining processing** — rock crusher → `paydirt` (final name TBD) → sluice refine loop (D13).
- **Bug Extractor** (D18) — a clean in-town station that processes `dead_<bug>` → materials (chitin, silk,
  venom, leather…) AND feeds bug-based cooking. Replaces per-bug ground drops + the old bug-leather station.
  Needs: the station + the extraction recipe table (which dead bug → which material).
- **Food / cooking system** (D19) — cooking recipes are a separate system from crafting; the village ships one
  starter meal (`forager_stew`) and the player cooks freely. Design the cooking system + recipe set later.
- **Land deeds** (D20) — the Mayor's plot/land-ownership system (separate from the merchant economy).
- **Boats / vehicles** — the Fisherman sells a boat (water traversal); design the boat mechanic + cost.
- **Store inventory rotation** — randomized/rotating merchant stock with a few rare/expensive "teases" (a peek
  at high-end gear from the start).
- **Chests** (user request) — storage chest behaviour/UI pass.
- **Size-by-growth** — centipedes/millipedes grow ~0.5→×2 as they eat (new deterministic sim mechanic; static
  small/large variants ship in the meantime).
- **Projectile-spit** — a deep tough-area **cave beetle** that spits projectiles (new ranged-combat sim
  mechanic; frontier-sync + test-changes gates).
- **Station "crank-to-charge" mini-game** — most stations take an active crank input that charges them to run a
  while (the sluice hand-crank is the first); client mini-game + server charge state.
- **Cave species + sprites** — `cave_beetle`, `glowworm` (green, catchable light), small `cave_spider`, the
  **green garden centipede** (village) + **cave millipede** (millipede ×0.5); cave centipede reuses the current
  centipede sprite. Plus a **`rock_crusher`** + tube/pipe sprite for the mining camp (stand-in `coal_bin` bins
  used for now). Then wire the cave critters' real diets/breeding + the underground ecology tuning pass.

## Later — captured, not scoped yet
- **Tune bug animations, including speed and size** — the cosmetic flap/buzz frames + the per-species
  anim profile (FlapFps / GlideSecs / Bob, in BugVisual + SwarmVisual) and each animated species' frame
  pixel size (the downscale target) want a pass for feel: wing-beat speed, hover jitter, and on-screen
  scale per species (fly buzz + butterfly glide are the first two; more species as they get frames).
- **Grabbing / pushing / shoving** (Andrew has the design; to detail later). Replaces the old
  "hands" slot-0 grab verb, which was pulled from the starting kit 2026-06-14 pending this rework
  (empty slots still bare-hand grab in the meantime).
- **Weather system expansion** (rain light/heavy + lightning/thunder shipped 2026-06-13; the
  client preset is a seam for the below):
  - **Intentional droughts** — gameplay weather; Andrew has design ideas (his to scope).
  - **Fog** — layered scrolling noise + depth/parallax + 2D-light interaction (NOT a flat tint);
    own research pass. A SEPARATE self-activating component reading the weather state, not a
    branch in RainController.
  - **Dust storms** — horizontal driven sheet; same component pattern.
  - **Per-zone / server-driven weather + intensity** — when the multi-zone system lands, the
    server picks weather kind + intensity per zone (today `RainController.Intensity` is a client
    F8 toggle and "rain" is one state).
  - **Rain polish** — URP post-process color-grade while raining (desaturate/vignette), puddle
    accumulation; extract a shared `WeatherVisual` base once fog/dust make it rule-of-three.
- **Power & electrification + cooking progression** (design captured in `game_design.md §11.6/11.7`):
  windmill/hydro/generator → power unit with a coverage-radius aura (highlight covered cells at
  placement); a shared "linked placement" line tool (power lines AND rail/track — click start/end,
  reject if it clips); machines split into fuel-fed (wood stove) vs electric; stove cooking-capacity
  tiers. Add the power/fuel-requirement entity flag only when building this. Author a small
  **power/electronics demo scene** to tinker with it visually.
  - **Village windmill (Andrew, 2026-06-27; refined 2026-09-27, D52):** a **windmill in the starting town that powers
    part of it** — the village is mostly unpowered, and the windmill lights only a part such as the Mayor's house, as a
    glimpse of what power will bring; players can't take it. A windmill of their own the player **can only buy or build
    after reaching the wheat/locust area** (the `locust_farmland` zone, which holds a small western-style town). Gates
    electrification behind reaching that zone; the details are left for when the zone is built.
  - **`clothing_rack` unlock (D27):** the 2-wide garment rail is a **display fixture only** in the Weaver
    for now — **not craftable/buyable until "the other town"** (same later-zone gate as the windmill).
    Wire its recipe/shop-entry when that zone lands. (`coat_rack` stays the house clothing piece.)
  - **`electric_heater`** is a Modern-Wares showroom display; functional only with the electricity expansion.
- **Single-slot "bulk bin" containers (D26):** `produce_crate` is now `slots:1` (a covered crate = one bulk
  stack of fruit/veg) — the same model the **ore bins** want. For a slot holding MORE than the normal stack
  cap (a true silo), add a per-container `stack_cap` override; until then 1 slot = 1 normal stack.
- **Procedural container fill-display (deferred):** the "show real contents" idea (a `fill_rect` + the client
  drawing the top item icons into it) stays backlogged — covered containers (lid/tarp) sidestep it for now;
  it's the eventual upgrade for OPEN containers.
- **`modern_floor` TILE:** polished floor for the Modern Wares showroom (terrain pipeline); proxied by
  `stone_floor` for now.
- **Placeable wall/block visual tiling consistency** — make placeable walls/blocks (wood/brick/iron/
  glass/marble + wood/stone) tile together cleanly. Iterate-heavy, token-spend; its own pass.
- **General-store catalog scene** — a shop (next to the produce market) with a buy-catalog of
  furniture/decor/valuables (gold pieces, piano, fancy whatevers).
- **Building-materials + rug/valuables content** — wall_brick/iron/glass/marble, window_wood/metal/
  fancy, rug_bearskin/fancy-patterns/simple, piano & gilded valuables (data + art via the catalog).
- Bug behaviour / AI.
- Authoring brand-new zones.
- More weapons + loot tables: per-species `kill_drops` schema (v1 hardcodes `bug_parts`),
  higher weapon tiers via the recolor pipeline, rarity tiers per the weapons brainstorm.
- **Bug HP affecting BEHAVIOR is a determinism boundary**: today HP is display-only; if
  damaged bugs should flee/slow, HP must enter the deterministic sim + state hash
  (architecture_swarm_sync §12).
- Higher tool tiers (steel→diamond): items.json entries + `recolor_sprites.py --family ...`
  (ramps already inline; the legacy reference art was cleaned out of Items/).
- Tiles still import Bilinear (Objects/Items/Bugs are Point now) — flipping the ground's
  filtering is a deliberate style decision to make with eyes on it.
- Staggered per-bug catch/kill pops along the sweep arc (cosmetic, no protocol change).
- Client EditMode test infra (first candidates: icon resolution chain, sector math as a
  pure function, the cursor echo-interception rule).
- Weapon tiers as moves data (sword_stone+, spear_iron — items.json entries + recolored
  icons; the design-target table lives in [`economy/catalogs/weapons.md`](economy/catalogs/weapons.md)). Durability still unenforced.
- Whip weapon kind: one new AnimKind/profile + one client line/tip hit query — server-free
  (reach-only validation). First whip proves the moveset schema's extensibility claim.
- Idle-held display for torches/lights (v1 gates on ToolType; the held torch already glows).
- Facing-aware idle held pose (remote + local render at a fixed side regardless of facing).
- TilePlace server range check (none exists — you can place from any distance).
- "Cursor hold as server-visible state" if inventory grows sort/quick-stack/shift-click —
  each new server-side slot writer must re-prove the echo-interception invariant
  (architecture_inventory.md).
- An enemy.
- Active/inactive zones: simulate bugs in detail only in zones that have players; cheaply
  aggregate the rest; pause a zone entirely when it has no one. Finer-grained than today's
  per-match pause-when-empty (which only idles when the *whole* world is empty).
- Free long-idle matches + clean up accumulated world metadata (matches currently idle when
  empty but are never freed; harness `world_create` runs leave stale metadata).

## Later — commerce spine follow-ons (after the 2026-06-27 v1: currency + general store + bug dealer)
v1 (DECISIONS D25) shipped currency + two working village vendors. Open follow-ons:
- **Distinct NPC art** — v1 reuses player-model sprites (`merchant`/`scholar`) as placeholders; the user wants
  NPCs to look different from the player. Make proper NPC sprites (Pipeline B/A).
- **The other 3 village NPCs** (Fisherman, Blacksmith, Carpenter) + the **Mining-Outpost** vendor — pure data
  (new `shop` occupants) now that the spine works.
- **Bug-market building + scene** — a dedicated building w/ unique decor + sign for the bug dealer, plus 1–2
  pricier **exotic bugs from other zones** in its sell list to show the value ceiling (game-feel curation).
- **Recipe-selling (Phase 2)** — `KnownRecipes` on the character + craft-station unlock enforcement, so shops
  can sell recipes (today all recipes are `unlock:"default"`).
- **NPC dialogue / wandering**, rotating/rare stock (adds shared state → revisit concurrency), bug-slot UI polish.

## Later — furniture / container / skill mechanics (from the Weaver scene pass, 2026-06-27)
- **Placeable containers (world + char-slot):** a container item can be worn in the character's container
  slot AND **placed in the world and used like a chest** — for the ones that make sense (a `dresser` holds
  clothes; you shouldn't drop it as a generic world chest). Define which containers are placeable-as-storage.
- **Furniture container filters:** make sure **all** furniture/decoration containers are actually set up as
  containers and **filter correctly** (dresser → clothes/armor only, wardrobe → clothes, terrarium → bugs,
  ore bin → blocks, etc.). Audit the `world.container.filter` on every container.
- **Player skill system (passive, station-driven):** each station USE grants a little EXP toward a skill
  (weaving, smithing, masonry, cooking…) — a nice passive, player-driven progression. Skills unlock perks /
  speed / quality. Design + build later.
- **Furniture-on-rug:** placing furniture **on top of a rug** must work (rug is a flat floor decoration that
  doesn't block the cell; the furniture sits over it). Verify the flat-placeable + occupant stacking.
- **Multi-square rug art:** rugs should visibly span **multiple cells** (`rug` 2×2 / `rug_large` 2×3) — the
  current art reads as one tiny square; the sprite must fill its footprint. (Art fix, batched.)

## Later — functional clutter (Weaver pass follow-ups, 2026-06-27)
- **`fabric_bolt` → optional `fabric_pile` container:** dropping cloth on the ground could aggregate into a
  **fabric-pile container** (the drop-aggregation idea — same family as ore bins / placeable fill containers).
  For now `fabric_bolt` is shop décor; revisit when the placeable-container-with-fill mechanic lands.
- `yarn_basket` is now a real **container** (filter `textile`); its **fill-state visual** (showing yarn level)
  rides the same fill-display backlog.

## UI/shop follow-ups (2026-06-28 — the polish run)
- **Village shop placement cleanup** — the 3 new shops (Weaver/Stonemason/Modern Wares) are placed in a
  loose south commerce strip on open grass; give them proper access lanes/spurs + tidy the layout in a
  paired pass (positions are easy to nudge in `zone_village_21_B.py`).
- **Full verification pass** — Unity compile + in-game test of the new panels (dialogue/shop, station I/O
  squares, mannequin dress-up, sign read); go tests via the docker/run-backend path (local go toolchain
  can't parse `go 1.25`); re-run `sim-determinism` after the mannequin `blocks_bugs` change.
- **Mannequin render Increment-B** — sync each chunk's container states on subscribe (mirror tree-water in
  `handleChunkSubscribe`) so ALL viewers + rejoins see a dressed mannequin (Increment-A renders it for the
  dresser only). Keep ONE source of truth (the synced `ContainerState`); never store the outfit on the occupant.
- **Sign 2-wide retroactivity** — store signs widened to `[2,1]` render 2-wide in OTHER zones that already
  placed them (cosmetic, non-blocking); re-place signs there when those zones are next touched.
- **Richer NPC dialogue** — quests/lore/topics beyond Trade/Goodbye (the shell is extensible).

## UI polish run — remaining follow-ups (2026-06-28)
- **Mannequin LIVE outfit render** — the equip panel + storage + blocks_bugs ship now; the mannequin still
  shows its flat sprite. To render the WORN outfit as a paper-doll (Increment-A: compose locally from the
  ContainerUpdate when you open/dress it; Increment-B: sync each chunk's container states on subscribe so
  all viewers + rejoins see it), author `Player/layers/body/mannequin_{dir}{frame}.png` (Pipeline B) + a
  custom `Outfit{Body="mannequin", Shirt/Pants/Hair=null, +overlays}` → `CharacterComposer.Compose`, and
  inject at `TilemapManager.RenderOccupant`. Single source of truth = the synced ContainerState.
- **Store-sign 2-wide art** — the 11 store signs are now `[2,1]` in data; only the crossroads `signpost`
  was re-rendered. Regen the rest at the 32×24 aspect (gpt-image-1) so they don't stretch.
- **Re-run `sim-determinism`** — mannequins now `blocks_bugs:true` (in village_21_B's weaver), so the zone
  collision map changed (deterministically). Re-run the cross-client gate via the run-backend/docker path
  (local go toolchain can't build the plugin) — it should still PASS (every client gets the same new map).
