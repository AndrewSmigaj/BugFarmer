# AGENTS.md

This repo's agent onboarding lives in **[CLAUDE.md](CLAUDE.md)** — read it first (stack, repo map, hard
rules, and the "Entry points for an AI coder" section: how to run every test, understand the deterministic
world, review complex changes, and the git workflow). This file exists so non-Claude tools that look for
`AGENTS.md` find the same starting point.

Quick pointers:
- **Tests / verification:** the `.claude/skills/test-changes` skill (the single source of truth).
- **Deterministic bug-sim model + adding a mechanic:** `docs/product/architecture/architecture_swarm_sync.md` §0, then
  the `.claude/skills/frontier-sync` skill.
- **Complex/risky change review:** `.claude/complex-change-review.md` + `.claude/lenses.md`.
- **Git workflow:** `.claude/git-guidelines.md`.
- **What's next:** `docs/product/BACKLOG.md`.
