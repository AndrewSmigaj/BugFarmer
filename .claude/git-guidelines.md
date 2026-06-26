# Git workflow (the non-obvious conventions — not generic git)

These are the project's deliberate workflow choices that OVERRIDE an agent's defaults. Living doc — edit as
we learn.

## The model: feature branch is a sandbox, `main` is the gate
- **Branch per feature** off `main`: `feature/<name>`. **Never commit directly to `main`.**
- **Auto-commit + push the feature branch the moment a coherent unit passes its verification gate** — the
  agent does NOT wait to be asked. The branch is isolated + revertible, so frequent commits are safe; they
  give durable, gate-tied checkpoints, clean history, and protect autonomous work across context compaction
  / crashes. (This intentionally replaces the default "commit/push only when the user asks", which only made
  sense when working on a shared branch.)
- A commit = a **known-good checkpoint**: commit a unit only after its gates pass (the STAGE-4 / VERIFY cells
  in `complex-change-review.md`). Don't commit a half-finished or unverified unit.
- **Merge to `main` is the human gate.** When a feature is done + verified, the agent does a `--no-ff` merge
  into `main` and pushes — but ONLY on the user's explicit go-ahead. The agent prepares/recommends the merge;
  it never merges to `main` unsolicited.

## Commit messages
- One coherent, revertible unit per commit. Subject = what; body = why + how verified.
- End every commit with: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

## Notes
- `--no-ff` for merges to `main` leaves a visible integration commit (clearer history).
- Optional future hardening (not enforced yet): a git pre-push hook running the fast gates
  (`python3 tools/netcode/test_sync_diff.py` + `go test ./world/`).
