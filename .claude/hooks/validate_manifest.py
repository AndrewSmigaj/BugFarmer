#!/usr/bin/env python3
"""Validate .claude/manifest.json — run from anywhere: python3 .claude/hooks/validate_manifest.py

Asserts referential integrity so a manifest typo can't silently disable a gate (the hooks are
fail-open, so a bad manifest degrades to "allow" — this is the check that catches that):
  * every authoring_gates / doc_coverage `covers` glob matches >= 1 real repo path
  * every referenced skill (skill / also_skills / command skills / owner_skill) has a real SKILL.md
  * every command_gates regex compiles
  * every doc_coverage `doc` file exists
Exit 0 iff valid; else prints a numbered list of problems and exits 1.
This is a P1 keystone check — keep it green alongside selftest.py.
"""
import os
import re
import sys
import glob
import json

HOOKS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HOOKS, "..", ".."))
SKILLS = os.path.join(REPO, ".claude", "skills")
MANIFEST = os.path.join(HOOKS, "..", "manifest.json")


def skill_exists(slug):
    return bool(slug) and os.path.isfile(os.path.join(SKILLS, slug, "SKILL.md"))


def glob_hits(pattern):
    return glob.glob(os.path.join(REPO, pattern))


def main():
    errs = []
    try:
        with open(MANIFEST) as f:
            m = json.load(f)
    except Exception as e:
        print(f"MANIFEST UNREADABLE: {e}")
        return 1

    for row in m.get("authoring_gates", []):
        tag = f"authoring_gates[{row.get('skill', '?')}]"
        if not skill_exists(row.get("skill", "")):
            errs.append(f"{tag}: skill has no .claude/skills/<slug>/SKILL.md")
        for s in row.get("also_skills", []):
            if not skill_exists(s):
                errs.append(f"{tag}.also_skills: '{s}' has no SKILL.md")
        for g in row.get("covers", []):
            if not glob_hits(g):
                errs.append(f"{tag}.covers: glob '{g}' matches 0 real paths")

    for i, row in enumerate(m.get("command_gates", [])):
        tag = f"command_gates[{i}]"
        for s in row.get("skills", []):
            if not skill_exists(s):
                errs.append(f"{tag}.skills: '{s}' has no SKILL.md")
        for p in row.get("patterns", []):
            try:
                re.compile(p)
            except re.error as e:
                errs.append(f"{tag}.patterns: bad regex '{p}': {e}")

    for row in m.get("doc_coverage", []):
        tag = f"doc_coverage[{row.get('doc', '?')}]"
        doc = row.get("doc", "")
        if not doc or not os.path.isfile(os.path.join(REPO, doc)):
            errs.append(f"{tag}: doc file does not exist")
        owner = row.get("owner_skill", "")
        if owner and owner != "none" and not skill_exists(owner):
            errs.append(f"{tag}: owner_skill '{owner}' has no SKILL.md")
        for g in row.get("covers", []):
            if not glob_hits(g):
                errs.append(f"{tag}.covers: glob '{g}' matches 0 real paths")

    if errs:
        print(f"MANIFEST INVALID — {len(errs)} problem(s):")
        for e in errs:
            print("  -", e)
        return 1
    print("manifest.json OK: "
          f"{len(m.get('authoring_gates', []))} authoring_gates, "
          f"{len(m.get('command_gates', []))} command_gates, "
          f"{len(m.get('doc_coverage', []))} doc_coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
