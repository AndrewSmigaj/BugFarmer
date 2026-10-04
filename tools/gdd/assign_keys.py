"""assign_keys.py — give every design proposal and question a stable key, once.

Each `### P<n>.` / `### Q<n>.` heading in the GDD sections gets a line under it:

    <!-- key: 08.one-outfit-at-a-time -->

Feedback in the review app is stored by this key, so it stays attached when proposals are renumbered or reordered.
§03's bug sheets (P9 onward) get `bug.<id>`, the bug's id in docs/gdd/data/bugs.jsonl. A key is made from the title
the first time and then never changes; headings that already have one are left alone, so the script can be re-run
after new proposals are added. `--check` reports headings without a key and exits 1 (the review app's builder runs
the same check).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDD = ROOT / "docs/gdd"
sys.path.insert(0, str(ROOT / "tools/gdd"))
from build_page import KEY, review_order  # noqa: E402

HEAD = re.compile(r"^### ([PQ]\d+)\.\s+(.+)$")
STOP = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "is", "it", "its", "be", "by", "as",
        "at", "from", "that", "this", "your", "you", "do", "does", "should", "what", "how", "which", "who", "when"}


def slug(title, used):
    words = re.findall(r"[a-z0-9]+", re.sub(r"[*`]", "", title).lower().replace("'", ""))
    words = [w for w in words if w not in STOP] or ["item"]
    base = "-".join(words[:5])[:60].strip("-")
    s, n = base, 2
    while s in used:
        s, n = f"{base}-{n}", n + 1
    return s


def sheet_keys():
    """§03 sheet number now -> bug id, from the bug registry."""
    out = {}
    for line in open(GDD / "data/bugs.jsonl", encoding="utf-8"):
        if line.strip():
            b = json.loads(line)
            if b.get("sheet_p_now"):
                out[b["sheet_p_now"]] = b["id"]
    return out


def process(path, sheets, check):
    text = path.read_text(encoding="utf-8")
    sid = re.search(r"<!--\s*gdd:.*?id=(\w+)", text).group(1).lower()
    lines = text.split("\n")
    used = {m.group(1).split(".", 1)[1] for l in lines if (m := KEY.match(l)) and "." in m.group(1)}
    out, missing, added, part = [], [], 0, None
    for i, line in enumerate(lines):
        out.append(line)
        if line.startswith("## "):
            part = line[3:].strip()
        m = HEAD.match(line)
        if not m or part not in ("Proposals", "Questions"):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if KEY.match(nxt):
            continue
        pid, title = m.group(1), m.group(2)
        if check:
            missing.append(f"{path.name} {pid}")
            continue
        if sid == "03" and pid in sheets:
            key = f"bug.{sheets[pid]}"
        else:
            s = slug(title, used)
            used.add(s)
            key = f"{sid}.{s}"
        out.append(f"<!-- key: {key} -->")
        added += 1
    if not check and added:
        path.write_text("\n".join(out), encoding="utf-8")
    return added, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sheets = sheet_keys()
    total, missing = 0, []
    for name in review_order():
        added, miss = process(GDD / name, sheets, a.check)
        total += added
        missing += miss
    if a.check:
        if missing:
            print("headings without a key:\n  " + "\n  ".join(missing))
            sys.exit(1)
        print("every proposal and question has a key")
    else:
        print(f"added {total} keys")


if __name__ == "__main__":
    main()
