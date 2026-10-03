#!/usr/bin/env python3
"""Build the item-pass review page from docs/gdd/item_table.jsonl (and the bug list, docs/gdd/bug_table.jsonl).

The item table (the owner's request of 2026-09-28, D55) gives every item in the game and in the old designs a
recommendation — keep, change, cut or add — with one plain line on why. This script embeds it into
tools/gdd/items_page.template.html and writes tools/gdd/_build/item_pass.html (git-ignored), which is published to
claude.ai (https://claude.ai/artifact/L9ftJfjRfcFD3yAB66qenD). The owner's marks are stored in the page's own database, one document per item at
marks/<kind>/items/<item id> holding {mark, note, at}; read them back with the ArtifactData tool (list each kind's
collection). The first version of the page (https://claude.ai/artifact/3Sxunf4HDezB1fgAKFRZG1) saved a whole kind as
one document and lost marks when an older copy overwrote a newer one; it is retired, and its storage is not used.

The bug list (the owner's request of 2026-10-02) rides on the same page as its own kind, "bugs": every bug in the game,
in the old zone plans, in the game's files with only a picture, or named in the item rows, with a call of keep, cut or
later. Its marks are stored the same way, at marks/bugs/items/<bug id>.

Usage: python3 tools/gdd/build_items_page.py
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "gdd", "item_table.jsonl")
BUGS = os.path.join(ROOT, "docs", "gdd", "bug_table.jsonl")
LINEUPS = os.path.join(ROOT, "docs", "gdd", "bug_lineups.jsonl")   # my bug lineups for the owner's marks (D79)
TEMPLATE = os.path.join(ROOT, "tools", "gdd", "items_page.template.html")
OUT = os.path.join(ROOT, "tools", "gdd", "_build", "item_pass.html")

# Display order and plain labels for the kinds of item.
GROUPS = [
    ("bugs", "Bugs"),
    ("bug_ideas", "Bug lineups (the roster)"),
    ("tools", "Tools"), ("weapons", "Weapons"), ("armour", "Armour and outfits"), ("accessories", "Accessories"),
    ("potions", "Potions and remedies"), ("meals", "Meals and food"), ("seeds_crops", "Seeds and crops"),
    ("plants", "Plants"), ("materials", "Materials"), ("ores", "Ores and gems"), ("stations", "Stations"),
    ("furniture", "Furniture"), ("decoration", "Decorations"), ("lighting", "Lights"), ("storage", "Storage"),
    ("structures", "Structures, fences and buildings"), ("blocks", "Blocks and ground"), ("beekeeping", "Beekeeping"),
    ("natural", "Things found in the world"), ("npcs", "Townspeople and shops"), ("other", "Other"),
]
ITEM_VERDICTS = {"keep", "change", "cut", "add"}
BUG_VERDICTS = {"keep", "cut", "later"}       # later = decide when the bug's zone is designed
VERDICTS = ITEM_VERDICTS | BUG_VERDICTS
WHERE = {"game", "designed", "both", "new"}
BUG_WHERE = {"game", "asked", "art", "artplan", "plan", "rows"}   # in the game · asked for · art only · art and a plan · plan · rows


def load():
    items, seen, problems = [], set(), []
    for src in (SRC, BUGS, LINEUPS):
        if os.path.exists(src):
            read(src, items, seen, problems)
    return items, problems


def read(src, items, seen, problems):
    name = os.path.basename(src)
    is_bugs = src == BUGS
    is_lineups = src == LINEUPS
    with open(src, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                it = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"{name} line {n}: not JSON ({e})")
                continue
            # Ids must be unique across the whole page: the page keys its own state by id alone.
            key = it.get("id")
            if key in seen:
                problems.append(f"{name} line {n}: duplicate id {key!r}")
                continue
            seen.add(key)
            want = "bugs" if is_bugs else "bug_ideas" if is_lineups else None
            if want and it.get("group") != want:
                problems.append(f"{name} line {n}: group {it.get('group')!r} (this file is all {want!r})")
            if not want and it.get("group") in ("bugs", "bug_ideas"):
                problems.append(f"{name} line {n}: an item row in the {it.get('group')!r} group")
            if it.get("verdict") not in (BUG_VERDICTS if is_bugs else ITEM_VERDICTS):
                problems.append(f"{name} line {n}: verdict {it.get('verdict')!r}")
            if it.get("where") not in (BUG_WHERE if is_bugs else WHERE):
                problems.append(f"{name} line {n}: where {it.get('where')!r}")
            if it.get("group") not in dict(GROUPS):
                it["group"] = "other"
            items.append({k: it.get(k, "") for k in ("id", "name", "group", "where", "verdict", "change", "reason", "decided")})


def main():
    items, problems = load()
    if problems:
        print("item table problems:\n  " + "\n  ".join(problems[:40]))
        return 1
    present = {it["group"] for it in items}
    data = {"version": date.today().isoformat(), "groups": [g for g in GROUPS if g[0] in present], "items": items}
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "/*__DATA__*/null" not in html:
        print("template has no data slot")
        return 1
    html = html.replace("/*__DATA__*/null", payload)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    counts = {v: sum(1 for it in items if it["verdict"] == v) for v in sorted(VERDICTS)}
    print(f"Item pass page built: {OUT} ({len(html) // 1024} KB) · {len(items)} items · {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
