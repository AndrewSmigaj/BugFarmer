#!/usr/bin/env python3
"""Plan putting stored answers back from an export (docs/plans/review-app.md, publishing: "if any step fails, roll back").

    python3 tools/gdd/marks_restore.py <backup> <current> [--versions versions.json] [--out plan.json]

<backup> and <current> are export folders (see marks_diff.py): the backup taken before the risky step, and a fresh
export of the page as it is now. For every document that is missing or different now, the plan holds one `set` write
that puts the backup's copy back, referencing the backup's own file (so the owner's text never passes through this
script). Writes are grouped into batches of at most 50 — one ArtifactData `batch` call each.

It never deletes: a document that exists now but not in the backup (written after the backup) is left alone and
listed. Overwriting a document that exists needs its current version (`if_version`); pass them as
{"<collection>/<doc_id>": version} in --versions (the versions an ArtifactData `list` shows), or the plan marks the
write "needs_version" and the batch must not be sent until it is filled in.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from marks_diff import load  # noqa: E402

BATCH = 50


def plan(backup, current, versions):
    B, C = load(backup), load(current)
    writes, kept_newer, needs = [], [], 0
    for coll in sorted(B):
        for doc_id, body in sorted(B[coll].items()):
            now = C.get(coll, {}).get(doc_id)
            if now == body:
                continue
            w = {"op": "set", "collection": coll, "doc_id": doc_id,
                 "file_path": str(Path(backup, *coll.split("/"), doc_id + ".json"))}
            if now is not None:
                v = versions.get(f"{coll}/{doc_id}")
                if v is None:
                    w["needs_version"] = True
                    needs += 1
                else:
                    w["if_version"] = v
            writes.append(w)
    for coll in sorted(C):
        for doc_id in sorted(C[coll]):
            if doc_id not in B.get(coll, {}):
                kept_newer.append(f"{coll}/{doc_id}")
    return {"batches": [writes[i:i + BATCH] for i in range(0, len(writes), BATCH)], "writes": len(writes),
            "needs_version": needs, "left_alone_newer": kept_newer}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backup")
    ap.add_argument("current")
    ap.add_argument("--versions", help="JSON {collection/doc_id: version} for documents that exist now")
    ap.add_argument("--out", help="write the plan here (JSON)")
    a = ap.parse_args()
    versions = json.loads(Path(a.versions).read_text()) if a.versions else {}
    p = plan(a.backup, a.current, versions)
    print(f"{p['writes']} document(s) to put back in {len(p['batches'])} batch(es); "
          f"{p['needs_version']} need their current version first; "
          f"{len(p['left_alone_newer'])} newer document(s) left alone")
    for b in p["batches"]:
        for w in b:
            print(f"  set {w['collection']}/{w['doc_id']}" + (" (needs version)" if w.get("needs_version") else ""))
    if a.out:
        Path(a.out).write_text(json.dumps(p, indent=2) + "\n", encoding="utf-8")
        print(f"plan -> {a.out}")
    return 1 if p["needs_version"] else 0


if __name__ == "__main__":
    sys.exit(main())
