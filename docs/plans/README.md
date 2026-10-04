# docs/plans/ — committed plans

Approved implementation plans, copied here from the harness plan-mode file when work begins, so they
**survive compaction, are reviewable in PRs, and leave a durable record** of intent + acceptance + what was
deferred. The live harness plan (`~/.claude/plans/<slug>.md`) is the working copy during a task; the approved
version lands here as `docs/plans/<slug>.md`.

## Use
- Start from `TEMPLATE.md`. Fill every section — especially **acceptance criteria (testable)**,
  **deferred decisions**, and **out-of-scope** (the sections that prevent drift and scope-creep).
- A task is not "done" until each acceptance criterion has a **conformance-table** row:
  `criterion · evidence (file:line / command output) · test name`. Score it with the `certainty-assessment`
  skill (which includes a premortem) BEFORE claiming done / verified / safe.
- One concern per plan; link related plans. Keep the PROGRESS log at the top as the resume pointer.

## Index
- `finish-bugs-zones-items.md` — the umbrella plan for finishing the bugs, their behaviour and combat, the zones' bug
  lists, the zone-design process and the items (2026-10-04). Part 0 in progress; the village's bug life is the first
  finished slice.
- `review-app.md` — Part A of that plan: one review app replacing the GDD and items pages. Not started.
- `repo-health-enforcement.md` — the enforcement-based repo-health pass (hooks + manifest). P0–P6 done; the rest
  waits for the owner.
- `grass-overhaul.md` — the grass overhaul. Shipped 2026-07-26.
- `swing-design-and-outfits.md` — the swing design and outfit build-out (2026-07-29). Phases 0–5 done; phase 6 not
  started.
- `player-arm-and-wearables.md` — superseded 2026-07-28 (the armless character replaced it).
- `player-sprite-and-wearable-creation.md` — superseded (the July masked approach; noted 2026-09-26).
