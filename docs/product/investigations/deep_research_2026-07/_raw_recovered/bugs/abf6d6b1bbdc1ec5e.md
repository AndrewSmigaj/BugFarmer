I'll gather all the requested facts in parallel batches. Let me start with the directory listings and key file reads.

---

Now let me gather the rest in parallel: the second skill, lenses, review file, guide formats, research digest, decisions, and corrections grep.

---

Now the research digest header, a sample brainstorm, decisions log, corrections grep, and skill lengths.

---

Let me read the house.md corrections section for the "learned the hard way" format example.

---

I have everything needed. Here is the complete report.

---

# Facts, formats & paths for planning a new zone-authoring craft skill

## 1. Skill file format

**Frontmatter.** Every skill uses a minimal YAML header fenced by `---`, with exactly two fields: `name` and `description`. No other metadata. Raw examples:

`/mnt/c/Users/emily/BugFarmer/.claude/skills/author-zone/SKILL.md` (lines 1-4):
```
---
name: author-zone
description: Use when creating or editing a game zone, or building an example scene/vignette for the zone guides. Covers the zonegen builder-library (feature primitives that coordinate through a shared occupancy model), placeholder-first composition, and rendering preview PNGs to review. Does NOT cover sprite generation (that's add-object / object_pipeline.md).
---
```

`/mnt/c/Users/emily/BugFarmer/.claude/skills/ecology-tuning/SKILL.md` (lines 1-4):
```
---
name: ecology-tuning
description: Use when balancing the bug ecology — tuning the 6-species food web (fly, butterfly, wasp, centipede, millipede, beetle) so populations sit in good, alive (oscillating) bands instead of crashing, running away, or pinning the hard cap. Covers the run_config harness, the per-zone chart layout, how to read population/interaction/phase charts, the levers (species params, plant/food, spawn/Director), the determinism caveats, and the discipline (one sane lever at a time, measure, log). Read this before proposing ANY ecology balance change.
---
```

The `description` is one long single-line sentence following a consistent shape: `Use when <trigger>. Covers <what>. Does NOT cover <boundary> (that's <other skill>).`

**Length & section conventions.** SKILL bodies are 45-213 lines (`wc -l`): regenerate-sprite 45, perf-tuning 69, frontier-sync 72, economy 74, add-object 93, run-backend 96, bug-spawning 120, certainty-assessment 125, ecology-tuning 136, author-zone 157, deep-investigate 196, test-changes 213. Body starts with a single `#` H1 title, then `##` section headers. ecology-tuning uses numbered sections (`## 0. Discipline`, `## 1. Zones`, `## 2. Run a config` … `## 6. Current status`); author-zone uses prose-named sections (`## The loop`, `## Builder`, `## Feature guides`, etc.). Bold-lead bullets are the dominant body style. Both open with a bold imperative framing paragraph before the first section.

**Supporting files.** No skill has any file beside `SKILL.md`. `find .claude/skills/ -type f` returns exactly 13 files, one `SKILL.md` per directory — no references/, no scripts, no assets. Skills instead point OUT to repo docs/tools (e.g. author-zone links `docs/guides/authoring/*.md` and `tools/zonegen/`).

**All directories under `/mnt/c/Users/emily/BugFarmer/.claude/skills/`** (13):
`add-object`, `author-zone`, `bug-spawning`, `certainty-assessment`, `deep-investigate`, `ecology-tuning`, `economy`, `frontier-sync`, `perf-tuning`, `regenerate-sprite`, `run-backend`, `test-changes`.

---

## 2. The lenses pattern

`/mnt/c/Users/emily/BugFarmer/.claude/lenses.md` (117 lines). Structure: a framing intro defining "a lens is a single perspective for re-examining work, with the question it forces," then an agent-prompt template, then two bullet lists — `## The lenses` (code-review lenses) and `## Design lenses (for feature/creature DESIGN…)` — then `## Notes for automating this`.

Each lens is a single bullet: an optional `★` (marks lenses that "earned their keep"), the **bold lens name**, an em-dash, the question it forces (often ending in `?`), and a parenthetical concrete "earned"/caught example. Verbatim format examples (lines 15-18):
```
- ★ **Requirements** — Does this *observably* satisfy what the user actually asked, not just "technically
  work"? (e.g. "*see* hornets attack individual flies" needs the visual, not only the correct kill.)
- ★ **Data / Contract** — Units, scales, serialization round-trips, fixed-point vs float, enum/string
  matches across a boundary. (Caught a ×1000 fixed-point radius-scale bug: threshold must use FixedPoint
  multiply, not raw int².)
```
Design-lens example (lines 88-90):
```
- ★ **Unbounded-Growth / Accumulation** — Does this system create entities or state that grow without a
  matching removal at steady rate? What bounds the standing count? (Generalized from the rotten-fruit pile:
  6-day lifetime × tree production → a deep pile + an O(items) decay pass. …)
```
The prompt template it gives for looping a lens (lines 7-8): `"Re-examine <artifact> through the <lens> lens: <question>. Report PASS / RISK / BROKEN with evidence (file:line). If RISK/BROKEN, propose the minimal fix."` The closing note points to the `certainty-assessment` skill for turning a lens pass into a numeric table.

`/mnt/c/Users/emily/BugFarmer/.claude/complex-change-review.md` (145 lines). Header: `# Complex-change review — steering a coding agent through hard changes in BugFarmer`. Structure: intro naming it "a manager's prompt-loop playbook," a "Companions" pointer (to `lenses.md`, the `certainty-assessment` skill, the `test-changes` skill), then `## The 7 ways a coding agent breaks THIS codebase` (FM1-FM7 failure modes), `## How to RUN it`, `## THE MATRIX` (5 lifecycle STAGES × failure-mode prompt cells, each with an exit gate), a `## BugFarmer invariant checklist` (11 numbered invariants), `## DYNAMIC PROMPTS`, and `## The loop`.

---

## 3. Authoring-guide conventions

**Files in `/mnt/c/Users/emily/BugFarmer/docs/guides/authoring/`** (18):
`ORGANIZATION.md`, `README.md`, `ant-colony.md`, `biome-feature-map.md`, `blocks.md`, `building.md`, `camps.md`, `caves.md`, `forest.md`, `house.md`, `research_procgen.md`, `roads.md`, `trees-and-ponds.md`, `vegetation.md`, `village.md`, `water.md`, `yard.md`. (README.md is the index; house.md is the largest at 227 lines; trees-and-ponds.md is a stub superseded by water.md.)

**`ORGANIZATION.md` — the placement rule (read in full, 48 lines).** The governing rule (lines 5-10):
```
> ## Is it a REUSABLE technique, or a specific PLACE (a zone)?
> - **Reusable technique** (a kind of thing used across zones — a building, a river, a cave, a block) →
>   organized **by feature**, under an `examples/<feature>/` area.
> - **A specific place** (the starting village, the underground passages, the desert) → organized
>   **by zone**, under that zone's folder.
> - **Game content** (every object/sprite that exists) → organized **by category**, under `catalog/`.
```
"Do not invent new top-level buckets." The "three mirrors" table (lines 19-23) maps docs / previews / scenes-code across the reusable-vs-zone-vs-content axes:
- Docs: `docs/guides/authoring/<feature>.md` | `docs/product/zones/<zone>.md` | —
- Previews (under `tools/_generated/previews/`): `examples/<feature>/` | `zones/<zone>/` | `catalog/<category>/`
- Scenes declare `PREVIEW = "examples/<feature>"` or `"zones/<zone>/scenes"`.

Previews live in exactly four folders (lines 26-32): `catalog/`, `examples/`, `zones/`, `player/`. Doc-kinds live under `docs/product/` split into `architecture/`, `zones/`, `economy/`, `ecology/`, `design/`, `investigations/` (with `BACKLOG.md` + `art_needed.md` at the product root). Tools rule (lines 44-48): every script finds the repo root by walking up from `__file__` to the folder containing `.git`.

**Guide rule/correction formatting.** Guides open with `# Feature guide: <topic>`, a one-paragraph scope line naming the module (`tools/zonegen/features/terrain.py`) and a "Test card" scene, then `##` sections mixing rules, fenced `python` snippets, and a `## Checklist` of `- [ ]` items (see water.md lines 51-58). Rules are bold-lead bullets.

The **"learned corrections" style** is a recurring inline convention: a dated, quoted owner correction embedded in the rule it produced. Examples:
- water.md line 15-16: `(2026-06 correction: "I really don't like the shapes of all the lakes")`
- roads.md line 35-36: `(2026-06 correction: a meandering town segment walked through the hall's yard)`
- vegetation.md line 46: `reads as speckle, never as a forest wall (2026-06 correction).`
- Section headers also carry provenance: roads.md line 87 `## Junctions & building adjacency (learned building village_21_B)`.

house.md is the richest example: an explicit numbered corrections block titled (line 202) `### Conventions the lint enforces — don't relearn these (each cost a correction)` — 8 numbered rules, each a hard-won gotcha (doors 1 cell wide, NPC 2 cells back, tall decor off the south row, etc.). It also carries an inline dated owner correction (line 194): `(owner correction 2026-07-05: "not all houses have to have doors on the bottom — it is awkward")` and the phrase (line 98) `this exact mistake cost an [collision]`.

---

## 4. Where research digests / brainstorms live

**`/mnt/c/Users/emily/BugFarmer/docs/brainstorms/`** is organized by TOPIC subdir, each holding per-zone or per-theme `.md` files:
- `armor/armor_clothing.md`, `bug_farming/bug_farming.md`, `weapons/weapons.md`
- `bugs/`, `decorations/`, `flora/`, `landmarks/`, `trees/` — each contains `ant_colony.md`, `butterfly_meadow.md`, `mining_caves.md`, `village.md` (one file per zone theme)
- `ecology/` — `bug_ecology_plan.md`, `ecology_proposal.md`
- `farming/farming_tools.md`, `materials/ores_metals.md`
- `objects/` — `alchemy_potions.md`, `cooking_food.md`, `fishing_gear.md`, `lighting_ambiance.md`, `storage_automation.md`

**Sample brainstorm format** (`docs/brainstorms/flora/butterfly_meadow.md`, lines 1-17): title `# Brainstorm: Butterfly Meadow — Flora & Fungus`, a scope paragraph naming the zone id (`butterfly_meadow_11`) and its role, a `Theme:` line, a **tags legend** (`nectar`, `host`, `edible/gatherable`, `ecology`), and a note that existing ids are marked `**[exists]**` with an EXTEND-don't-duplicate rule pointing at `tools/art/catalog/flora.json`. Body is `##` groupings (Groundcover, Wildflowers…) of `` - `id` — description. **tag**. *Ecology: role.* `` bullets.

**Research-digest precedent.** `docs/guides/authoring/research_procgen.md` (128 lines) is the model for capturing external research. Header (lines 1-6):
```
# Research: how others procedurally build terrain, roads & buildings (2026-06)

Digest of a three-track web-research sweep, kept as the paper trail for which
techniques zonegen adopted and which it passed on. Full citations at the end of
each section.
```
Body is numbered sections (`## 1. Terrain — noise density fields` …) that cite named sources (Red Blob Games, RimWorld, Dwarf Fortress), give the calibrated recipe zonegen adopted, and end with a "Failure modes" note. roads.md cross-references it inline (line 30: `Least-cost-path roads (see research_procgen.md §2)`). A grep for `research` in docs/ finds this one authoring digest as the precedent; no other file is named `research_*` in the authoring area.

---

## 5. Corrections / decision-logging precedent

**`/mnt/c/Users/emily/BugFarmer/docs/product/economy/DECISIONS.md`** (first ~24 lines). Header + entry format:
```
# Economy / World — Decisions log

The single place design decisions live, so they're never scattered across docs. Each entry: the decision,
the why, and a pointer to where it's elaborated. **Open** items are unresolved forks — don't assume them.

---

## Resolved (2026-06-25)

### D1 — Stations are crafted OR bought (not "built")
Basic/intermediate stations (workbench, furnace, anvil, stonecutter, loom, sawmill, cauldron, cooking_pot…)
are **crafted** from materials. … There is no separate "build" mechanic; …
*Why:* matches the decoration rule … → `crafting.md` (recipes), `merchants.md` (which are sold).
```
Convention: entries are `### D<n> — <decision title>`, a prose body, an italic `*Why:*` line, and an arrow `→` pointer to the elaborating doc(s). Entries are grouped under a dated `## Resolved (YYYY-MM-DD)` header; unresolved forks are marked **Open**. (Note: the lenses.md "Authored-Decision Fidelity" lens explicitly warns that a `DECISIONS.md` D-entry is NOT proof the user decided it — authority = built data + asking.)

**Embedded "learned the hard way" / corrections sections in guides** (grep `correction|cost a|learned` over docs/guides/): the strongest precedent is house.md line 202 `### Conventions the lint enforces — don't relearn these (each cost a correction)` (8 numbered gotchas). Plus the inline dated-correction convention across water.md:16, roads.md:35, vegetation.md:46, house.md:98/194. The ecology-tuning SKILL.md itself carries the pattern at the skill level: `## 5. Caveats that bite (learned the hard way)` and a `### HARD RULES (each one was learned by screwing it up — do not repeat)` block (lines 18, 120).

---

## 6. The author-zone skill's current routing

`/mnt/c/Users/emily/BugFarmer/.claude/skills/author-zone/SKILL.md`. The skill routes to docs/guides and docs/product at these points:

- **Up front — "Where things go" (lines 13-18):** hard-links `docs/guides/authoring/ORGANIZATION.md` as "the rule" for placement, before any building.
- **"Where the world lives" orientation block (lines 20-29):** `docs/guides/authoring/README.md` (the system index, "Read it first"), `docs/product/architecture/architecture_world.md` (the 24-zone grid), `docs/product/zones/<zone_id>.md` (+ `_TEMPLATE.md`, scope `demo_slice.md`), `docs/guides/authoring/biome-feature-map.md` (which primitives per biome), and `docs/brainstorms/<topic>/` + `ecology_proposal.md` (content to mine).
- **New-content path (lines 40-42):** routes to the **add-object** skill for new entities.
- **The loop, Step 2 (line 58):** `For each feature, read its **feature guide** (below) + the cross-cutting style guide.` — this is the workflow hook where per-feature guides are consulted.
- **The loop, Step 5 (lines 67-68):** track new-art placeholders in `docs/product/art_needed.md`.
- **"## Feature guides" (lines 105-120)** is the explicit routing table, headed `Full index + one-liners: docs/guides/authoring/README.md.` It links, per feature:
  - `docs/guides/authoring/building.md` — rooms, walls, doors, shells
  - `docs/guides/authoring/house.md` — multi-room houses, facing rule, furniture collections, layout generators
  - `docs/guides/authoring/yard.md` — fenced yards/pens
  - `docs/guides/authoring/roads.md` — organic roads
  - `docs/guides/authoring/vegetation.md` — scatter/clumping
  - `docs/guides/authoring/village.md` — composing a town
  - `docs/guides/authoring/water.md` — lakes, shores, docks ("Supersedes trees-and-ponds.md")
  - `docs/guides/authoring/{caves,blocks,ant-colony,forest,biome-feature-map}.md` — "the rest"
  - Cross-cutting: `docs/guides/art/MASTER_STYLE_GUIDE.md`
- **Pipeline / testing sections (lines 122-139):** route to `tools/world/view_world.py`, the `run-backend` skill, `tools/sync-harness`, and `tools/world/make_test_zone.py`.

Where a new craft guide + lenses step would hook: a new per-feature guide would be added to the `## Feature guides` list (lines 105-120) and consulted at **loop Step 2** (line 58, "read its feature guide"); a lenses/review step would slot into the go-slow / "check before you call it done" discipline at **loop Step 4** (lines 47-54, 62-63, the `b.lint()` → read-a-crop gate), which is the skill's existing self-review checkpoint (and which the lenses.md + certainty-assessment skill are designed to formalize).