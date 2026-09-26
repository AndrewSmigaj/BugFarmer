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
- `repo-health-enforcement.md` — the enforcement-based repo-health pass (hooks + manifest; P0-P7). First entry.
