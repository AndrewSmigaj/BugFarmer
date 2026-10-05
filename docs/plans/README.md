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
- **One active plan at a time.** When a plan is replaced or finished it moves to `archive/` (with `git mv`, so its
  history stays), gets a dated line at its top saying what replaced it, and every link to it is updated.

## Index
### Active (one at a time)
- `village-slice.md` — **the one active plan** (2026-10-04): the foundation under the bugs (the waste cut on the
  players' computers, the whole zone running on the server, the bug state sent on join, zones of 512 × 512, tuning
  tools), the bug budget, then the village rebuilt at 512 with its bugs tuned, played and signed off. A one-screen
  summary sits at its top. Start here.

### Reference (in force, but not an order of work)
- `finish-bugs-zones-items.md` — the earlier plan (2026-10-03/04): the owner's requirements and the designs the active
  plan points into (Parts B–E, the behaviour model D0–D7, the combat groundwork C1–C12, how we work). Its order of work
  is replaced; each section is labelled done, replaced or reference.
- `review-app.md` — the review app (the earlier plan's Part A): built, tested and rehearsed; the publish waits for the
  owner's word (the active plan's Stage 0). Marked done once published.

### Paused (open phases, picked up when the roadmap reaches them)
- `grass-overhaul.md` — the grass overhaul: phase 1a and a simple tuft layer shipped 2026-07-26; 1b–1c and phases 2–5
  open.
- `swing-design-and-outfits.md` — the swing design and outfit build-out (2026-07-29). Phases 0–5 done; phase 6 not
  started.
- `repo-health-enforcement.md` — the enforcement-based repo-health pass (hooks + manifest). P0–P6 done; P7 waits for
  the owner.

### Archived (`archive/`: replaced or superseded, kept for the record)
- `archive/finishing-the-game.md` — the morning plan of 2026-10-04; replaced the same day by `village-slice.md`.
- `archive/player-arm-and-wearables.md` — superseded 2026-07-28 (the armless character replaced it).
- `archive/player-sprite-and-wearable-creation.md` — superseded (the July masked approach; noted 2026-09-26).
