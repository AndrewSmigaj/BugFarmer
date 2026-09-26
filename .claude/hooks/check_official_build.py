#!/usr/bin/env python3
"""check_official_build — the committed animations must match what official.py says they are.

Replaces `check_sprite_ledger.py` (retired 2026-08-06). That hook compared FILENAMES between a hand-written
`CURRENT.md` and the `current/` folder — it never opened an image, so every animation could be wrong and it
would still pass. It also only inspected outfits that HAD a `CURRENT.md`, which was 2 of 24.

This one re-renders from `official.py` and compares the actual GIF bytes. The render is deterministic (same
md5 across runs), so a mismatch means the committed art genuinely disagrees with the declared source —
someone edited a motion and did not rebuild, or hand-edited an output.

Runs ONLY when something that could change a render is staged, so ordinary commits stay fast (~4s/outfit).

FAIL-OPEN: any error in this script exits 0. A gate must never wall off the workflow it disciplines.
"""
import os
import subprocess
import sys

# Staged paths that can change a rendered animation. Anything else and this hook is a no-op.
TRIGGERS = (
    "tools/player_sprites/official.py",
    "tools/player_sprites/build.py",
    "tools/player_sprites/gait.py",
    "tools/player_sprites/render_animations.py",
    "tools/_generated/player/outfits/",
)


def main():
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            capture_output=True, text=True, check=True).stdout.split()
    if not any(s.startswith(t) or s == t for s in staged for t in TRIGGERS):
        return 0

    build = os.path.join(root, "tools", "player_sprites", "build.py")
    if not os.path.exists(build):
        return 0
    r = subprocess.run([sys.executable, build, "--check"], capture_output=True, text=True, cwd=root)
    if r.returncode == 0:
        return 0

    print("\n⛔ Official build (pre-commit) — the committed animations do not match official.py:\n")
    for line in (r.stdout + r.stderr).strip().splitlines():
        print("    " + line)
    print("\nRebuild so the art matches what is declared:")
    print("    python3 tools/player_sprites/build.py")
    print("Or override:  git commit --no-verify")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)          # fail-open, always
