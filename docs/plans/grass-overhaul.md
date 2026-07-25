# Grass overhaul — roadmap + plan (WORKING)

**Goal:** our grass reads worse than games like Necesse and Stardew Valley. Overhaul it to a polished,
professional 2D top-down look. **NOT fast, NOT a prototype, NO shortcuts — the best result for the game**
(owner, 2026-07-25). This doc is the durable record; it starts as the roadmap and grows into the plan +
certainty assessment.

## Standing rules
- Research best practices FIRST, then design (thorough-research skill; hit its countable quotas).
- **Pace agents: ≤2–3 in flight, each "do it yourself, no sub-agents, write to disk incrementally."** Wide
  fan-out has destroyed unattended runs before. Verify load-bearing claims myself.
- Checkpoint (commit) after every stage so nothing is lost.

## Stages
0. **Persist this roadmap** (done — this file) on branch `feature/grass-overhaul`.
1. **Exhaustive research** — how ≥5–10 top-down farming/crafting games render grass (autotiling, tufts/decals,
   wind sway, color variation, transitions) + general techniques. → `docs/product/investigations/grass-overhaul/`.
2. **Read + review** all research; study OUR grass (`Resources/Tiles/grass*`, `TileDatabase`, `TilemapManager`,
   the shaped-ground/composite system) and pin down why ours reads worse.
3. **Write the improvement plan** (polished; ≥4 scored options per hard choice) → this file.
4. **Certainty assessment** (adapted for a VISUAL feature): drop sync/determinism (N/A); add visual axes —
   fidelity-vs-reference, art-pipeline feasibility, performance, tiling/seams, style cohesion, integration,
   look-&-feel acceptance bar.
5. **Raise every certainty** as high as possible (read code, web-verify, study references) until only genuine
   spikes / owner-taste remain.
6. **Save + present** the final plan.

## Status
- [x] Stage 0 — roadmap persisted.
- [ ] Stage 1 — research (in progress).
- [ ] Stage 2 — review + our-grass study.
- [ ] Stage 3 — plan.
- [ ] Stage 4 — certainty assessment.
- [ ] Stage 5 — raise certainties.
- [ ] Stage 6 — present.

_(Research findings + synthesis live under `docs/product/investigations/grass-overhaul/`.)_
