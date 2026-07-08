#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit) hook — block AUTHORING a file until its governing skill was read
this session. The file-edit twin of gate_skill_commands.py (which only gates Bash commands).

Why this exists: prose reminders + the loaded skill *description* failed repeatedly to make me READ the
governing skill/guide before authoring — I'd build from priors and REINVENT things we already designed
(a human farm instead of an ant nest; an entity that already exists). The Bash gate can't catch this:
authoring is a Write/Edit, which has no command signature. This gate makes the read non-optional for the
file being edited.

FAIL-OPEN by construction: the whole body is wrapped in try/except and always exits 0. Per the hook
contract, exit 0 + empty stdout = allow; only an explicit matched-gate-without-marker prints a deny.
So any bug here degrades to "allow", never "block everything". Once the governing skill is read/invoked
this session (marker set by mark_skill_read.py), that path authors freely for the rest of the session.

Extending to another authoring surface later = add one row to PATHS.

stdin (official contract):  { "session_id": "...", "tool_input": { "file_path": "..." }, ... }
Deny output (official contract): {"hookSpecificOutput":{"hookEventName":"PreToolUse",
                                   "permissionDecision":"deny","permissionDecisionReason":"..."}}
"""
import sys
import os
import re
import json

# ---------------------------------------------------------------------------
# PATHS: (primary skill slug, [path regexes matched against the edited file],
#         extra note appended to the deny reason — the OTHER skills/guides this
#         file also implicates). Reading/invoking the PRIMARY skill clears the
#         gate for that path (we don't force reading 3 skills to touch one file;
#         the reason names the rest so they're on the radar).
# Gate CONTENT-authoring surfaces only — NOT engine files (tools/zonegen/features,
# zonebuilder.py, render.py) which are mechanics, not content.
# ---------------------------------------------------------------------------
PATHS = [
    ("zone-craft", [r"tools/zonegen/scenes/[^/]*\.py$"],
     "Also read author-zone (builder/lint/preview mechanics) AND the FEATURE GUIDE for what you're "
     "building: ant nest=docs/guides/authoring/ant-colony.md, cave/tunnel/ore=caves.md, coast/water="
     "water.md, mine/cliff/camp=camps.md, blocks=blocks.md, forest=forest.md, houses=house.md "
     "(index: biome-feature-map.md). Walk CORRECTIONS.md (owner taste)."),
    ("economy", [r"nakama/data/entities/[^/]*\.json$"],
     "Also read add-object (the art pipeline). CHECK the unified registry FIRST — an id is valid if it "
     "exists in ANY of items/occupants/placeables.json (never conclude 'missing' from one file); never "
     "invent. Home any NEW entity in docs/product/economy/catalogs/ (run tools/data/catalog_coverage.py)."),
    ("frontier-sync", [r"nakama/modules/world/[^/]*\.go$"],
     "Determinism-critical server code. Also: bug-spawning (spawn/persist files), perf-tuning (hot "
     "loops), and the relevant docs/product/architecture/architecture_*.md (index: ARCHITECTURE.md) — "
     "UPDATE that architecture doc if you change behavior."),
    ("ecology-tuning", [r"nakama/data/(species|ecology_tuning)\.json$", r"tools/bug_lab_configs/[^/]*\.json$"],
     "Balance change. Also read frontier-sync if you touch a hash-bearing behavior field "
     "(movement_style / flies_over_fences / predation geometry) — that's a determinism change."),
    ("regenerate-sprite", [r"tools/art/catalog/[^/]*\.json$"],
     "Also read add-object if this is a NEW asset (not a re-do of an existing one's art)."),
]

_PATHS = [(slug, [re.compile(p) for p in pats], note) for (slug, pats, note) in PATHS]


def matched_gate(file_path):
    """Return (slug, note) of the first gate whose path pattern matches, else None."""
    fp = (file_path or "").replace("\\", "/")
    for slug, regexes, note in _PATHS:
        if any(r.search(fp) for r in regexes):
            return slug, note
    return None


def _safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "")


def main():
    data = json.load(sys.stdin)
    file_path = (data.get("tool_input") or {}).get("file_path", "") or ""
    hit = matched_gate(file_path)
    if not hit:
        return  # not a gated authoring surface — allow (silent)
    slug, note = hit

    session_id = _safe(data.get("session_id", "nosession"))
    marker = os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"claude-skill-read-{_safe(slug)}-{session_id}",
    )
    if os.path.exists(marker):
        return  # governing skill already read/invoked this session — allow (silent)

    reason = (
        f"⛔ Authoring gate — the {slug} skill has not been read this session, and its loaded "
        f"*description* is only a pointer, not the procedure. Before editing this file, read the full "
        f"skill (this clears the gate for the session):\n"
        f"    .claude/skills/{slug}/SKILL.md\n"
        f"{note}\n"
        f"Then re-run this edit. (Reading/invoking the skill clears the gate.)"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: any error → no output → tool proceeds
    sys.exit(0)
