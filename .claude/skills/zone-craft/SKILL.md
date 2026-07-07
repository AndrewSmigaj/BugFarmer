---
name: zone-craft
description: Use when a zone or scene needs to be INTERESTING — planning a new zone's content, running an improvement pass on a bland build, or judging whether a place feels alive. Covers the craft loop (the pre-build brief with brainstorm quotas, options-first sketches the owner picks from, the zone lens review, the corrections ledger, polish) and the hard rules that cost rebuilds. Does NOT cover builder mechanics, feature primitives, or the preview pipeline (that's author-zone).
---

# Craft a zone that feels alive

The enemy this skill exists to kill is the **technically-correct bland zone**: lint 0, contracts
honored, and nothing worth walking to. Two rules frame everything below:
- **Guides are GUIDELINES.** Context-appropriateness and variety beat rule-following —
  "sameness reads worse than any individual rule-break" (house.md, owner-corrected). Every zone
  names one deliberate rule-bend and why.
- **You are expected to be CREATIVE**, not to assemble the minimum the request named. The owner
  reviews taste; your job is to bring real options worth choosing between.

## ⛔ THE GATE — read this before you write ANY builder/scene code
This exists because the failure mode is real and repeated: skipping the loop and writing a
**monolithic `zone_*.py` that scatters props randomly** — no scene previews, haphazard "rooms with
stuff thrown in," boring, near-pure dirt. **That is a protocol VIOLATION, not a build.**

You may NOT write or edit a zone builder / scene until you have PRODUCED and POSTED to the owner:
1. **The BRIEF** (the fields below — promise, region jobs, ≥3 named landmarks, ground-variety, edges,
   rule-bend). Most zone docs already carry a `## Craft brief`; refine it, don't skip it.
2. **The LANDMARK-SCENE LIST** — every interesting place is a crafted **`place_<thing>(b, ox, oy)`
   scene piece** with a thin `build()` wrapper and its OWN preview in
   `tools/_generated/previews/zones/<zone>/scenes/` (author-zone). Name each scene + its preview path.
   Landmarks are authored DELIBERATELY (text-grids / arranged rows — the ROWS rule), never scatter.
3. **2-3 rendered OPTIONS per major feature** (layout band, showpiece landmark). "Never build the
   first idea for a major." Owner picks (AskUserQuestion; if it times out, state your pick + proceed).

No artifact → no build. If you catch yourself typing `fill_solid`/`carve_*` into a `zone_*.py`
before the scene list + options exist and are posted, STOP — you are violating the gate.

## The craft loop
0. **ORIENT** — read the zone doc (`docs/product/zones/<zone>.md`), the corrections ledger
   (`docs/guides/authoring/CORRECTIONS.md` — ALL of it, it's short), and the `research_*.md`
   packs relevant to this zone's biomes (`docs/guides/authoring/`).
1. **BRIEF** — fill the fields below BEFORE building; persist the filled brief into the zone
   doc as a `## Craft brief` section (single scenes: into the working plan, quotas halved).
2. **OPTIONS** — for each MAJOR feature (a settlement, a landmark, a terrain band), sketch
   **2-3 genuinely different arrangements**, render small crops of each, and present them —
   the OWNER picks (AskUserQuestion; if it times out, state your pick + why and proceed).
   Never build the first idea for a major.
3. **BUILD** — through the **author-zone** skill (the builder, primitives, lint, previews —
   mechanics live there, not here).
4. **LENS PASS** — run the **Zone & scene lenses** (`.claude/lenses.md` §"Zone & scene
   lenses"): one finding per lens, PASS/RISK/BROKEN, judged against RENDERED PIXELS with the
   crop in hand — never against the plan. All-PASS on a first build means the questions were
   soft: tighten and re-run.
5. **LEDGER CHECK** — walk CORRECTIONS.md; cite each applicable entry as HONORED or
   DELIBERATELY BENT (with the reason). Silence is not compliance.
6. **POLISH** — fix the lens/ledger findings, re-render, final full view + random game-zoom
   crops. New corrections learned → inline in the topical guide + one ledger line.

## The brief (fields; quotas are FLOORS, halve for a single scene)
- **The promise** — one sentence: what should a player FEEL here?
- **Region jobs** — every area of the map named with its job (working farm / wild meadow /
  transition band / quiet corner). A region with no job is where blandness lives.
- **Landmarks** — ≥3 NAMED places a sign could carry (bee_meadow_20 shipped 11; 3 is a floor).
- **Content brainstorm** — ≥25 candidate placements across ≥6 categories: activity/work,
  people & wear-and-tear, nature, ground/water, loot/extraction, whimsy. Then the trimmed pick.
- **Micro-stories** — ≥2 scenes narratable from placement alone (the wreck; the picnic).
- **Ground-variety plan** — ≥3 ground materials/blocks and where they transition (C9:
  blandness is fixed with GROUND first; objects only fix close-ups).
- **Edges** — what each of the 4 map edges connects to or foreshadows (and the exact contract
  rows shared with built neighbors).
- **One deliberate rule-bend** — the guideline being bent, and why this context wants it.
- **Owner questions** — ≥1 open question worth their time.

## HARD RULES (each learned by screwing it up — do not repeat)
1. **NEVER guess a footprint.** `python3 tools/data/footprints.py --id <entity>` (or read
   `tools/_generated/footprints.md`). A bed placed as 1×1 was 2×4 and cost a scene rebuild.
2. **Ore is ONLY veins per the caves.md doctrine** (runs 3-6, jittered seeding, commons
   shallow / rares few+deep, MEASURED with the density probe) — never hand-set coordinates or
   stepped lines, even for "special" rares. Applies to surface rock (`terrain.rock_mass`) too.
3. **Blandness = ground variety FIRST.** Before decorating a dead region, change what it's
   made of: materials, block masses, transitions. Ground reads at every zoom.
4. **"Dirt areas" are DIRT-BLOCK masses** (shovel shell, stone/ore core) — terrain that looks
   diggable must BE diggable. Painted dirt is only the apron between masses.
5. **Regeneration tools clobber newer committed art.** Before committing any bulk regen, diff
   the MODIFIED (not new) files against HEAD; run cleaners targeted. Exit 0 is not success.

## Verifying water, routes and claims — in TEXT, then pixels
Geography claims get PROVED, not eyeballed: water continuity = walk a water-only line in the
grid (the landlocked-harbor bug); edge contracts = read the edge cells; anchor placements =
count them (a silently-skipped wasp nest is an ecology hole). Then look at crops — both, always.

## Where everything lives
- **author-zone** — the mechanics: builder API, primitives, text-grid buildings, `b.lint()`,
  previews, save pipeline, in-game smoke. zone-craft decides WHAT; author-zone is HOW.
- **CORRECTIONS.md** (`docs/guides/authoring/`) — the owner-taste index (Steps 0 and 5).
- **Zone & scene lenses** — `.claude/lenses.md`, the section of that name (Step 4).
- **Research packs** — `docs/guides/authoring/research_{composition,mining_feel,settlements,
  coasts_geology}.md`: distilled, checkable rules per domain + one counterexample each.
- **gallery.md** (`docs/guides/authoring/`) — annotated before/after pairs; the fastest way to
  calibrate what "better" means here.
- **Footprints** — `python3 tools/data/footprints.py` (HARD RULE 1).
- **Ore doctrine** — `docs/guides/authoring/caves.md` §4 (+ the per-zone ore tables).
- **certainty-assessment** skill — to turn a lens pass into a scored, evidence-anchored table
  before claiming a zone "done".
