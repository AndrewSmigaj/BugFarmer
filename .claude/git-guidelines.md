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
- **`main` on GitHub must always hold all our work — merge + push it at the END OF EVERY SESSION** (standing
  go-ahead from the owner, 2026-09-26: *"main I want it pushed to main, this is fucked I already sent my repo
  as part of an assessment and now you havent been pushing for months"*). At session end: commit the whole
  working tree on the feature branch → `git checkout main && git merge --no-ff feature/<name>` → `git push
  origin main` → check `git rev-parse main` equals `git rev-parse origin/main` → back to the feature branch.
  Unfinished work still goes to `main` (the repo is the owner's portfolio; months of unpushed work was the
  failure). Push the feature branch itself after every commit.
- **What goes in a commit:** the FULL working tree — older uncommitted changes are our work too, never someone
  else's WIP. Unity's `.png.meta` re-import churn goes in its own labelled commit after the feature commit.
- **When:** after the unit's check passes. For art and design the check is the OWNER'S EYES — build it, show
  it, commit after (a working tree waiting for his review is correct; `main` still gets it at session end).

## Commit messages
- One coherent, revertible unit per commit. Subject = what; body = why + how verified.
- End every commit with the co-author line of the model doing the work, e.g.
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Notes
- `--no-ff` for merges to `main` leaves a visible integration commit (clearer history).
- Never pipe a check through `| tail`/`| head` when you rely on its exit code — the pipe reports the last
  command's status, so a failing check looks like a pass. Save the output to a file, then read it.
- Optional future hardening (not enforced yet): a git pre-push hook running the fast gates
  (`python3 tools/netcode/test_sync_diff.py` + `bash tools/run_go_tests.sh`).
