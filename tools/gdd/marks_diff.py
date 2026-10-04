#!/usr/bin/env python3
"""Compare exports of the review page's stored answers, field by field (docs/plans/review-app.md, publishing).

An export is a folder written by the ArtifactData tool's `list` with `out_dir`: <export>/<collection path>/<doc_id>.json,
one file per stored document (the document's own fields). Exports live OUTSIDE the public repo
(C:/Users/emily/BugFarmer_backups/<date>_review-app/), because they hold the owner's own words.

    python3 tools/gdd/marks_diff.py manifest <export>             # write <export>/MANIFEST.json (counts + sha256)
    python3 tools/gdd/marks_diff.py diff <before> <after>         # exit 1 on ANY difference
    python3 tools/gdd/marks_diff.py diff <before> <after> --allow-newer
                                                                  # after the owner has opened the page: a document
                                                                  # may only have changed to a NEWER `at`, or be new
    python3 tools/gdd/marks_diff.py orphans <export>              # marks on rows the item table no longer has —
                                                                  # the app's "Older notes" must list this many

Prints counts and document ids only, never the owner's text.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/gdd"))


def load(export):
    """{collection: {doc_id: body}} for every document file under an export folder."""
    export = Path(export)
    out = {}
    for f in sorted(export.rglob("*.json")):
        if f.name == "MANIFEST.json":
            continue
        rel = f.relative_to(export)
        coll, doc_id = "/".join(rel.parts[:-1]), rel.stem
        out.setdefault(coll, {})[doc_id] = json.loads(f.read_text(encoding="utf-8"))
    return out


def digest(docs):
    return hashlib.sha256(json.dumps(docs, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def manifest(export):
    data = load(export)
    m = {"documents": sum(len(d) for d in data.values()),
         "collections": {c: {"count": len(d), "sha256": digest(d)} for c, d in sorted(data.items())}}
    Path(export, "MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    print(f"{m['documents']} documents in {len(m['collections'])} collections -> {Path(export, 'MANIFEST.json')}")
    for c, v in m["collections"].items():
        print(f"  {c}: {v['count']}")
    return 0


def diff(a, b, allow_newer=False):
    A, B = load(a), load(b)
    bad, ok_newer = [], []
    for c in sorted(set(A) | set(B)):
        da, db = A.get(c, {}), B.get(c, {})
        for i in sorted(set(da) | set(db)):
            x, y = da.get(i), db.get(i)
            if x == y:
                continue
            where = f"{c}/{i}"
            if y is None:
                bad.append(f"MISSING after: {where}")
            elif x is None:
                (ok_newer if allow_newer else bad).append(f"new: {where}")
            else:
                fields = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
                newer = isinstance(x.get("at"), (int, float)) and isinstance(y.get("at"), (int, float)) and y["at"] > x["at"]
                (ok_newer if (allow_newer and newer) else bad).append(f"changed {where}: {', '.join(fields)}"
                                                                      + (" (newer)" if newer else ""))
    n = sum(len(d) for d in A.values())
    print(f"before: {n} documents; after: {sum(len(d) for d in B.values())}")
    for line in ok_newer:
        print("  allowed  " + line)
    for line in bad:
        print("  DIFF     " + line)
    print("IDENTICAL" if not bad and not ok_newer else ("only newer answers" if not bad else f"{len(bad)} difference(s)"))
    return 1 if bad else 0


def filled(b):
    return any(isinstance(b.get(k), str) and b[k].strip() for k in ("mark", "note", "choice", "other", "level"))


def orphans(export):
    import build_items_page as bi
    items, _ = bi.load()
    ids = {it["id"] for it in items}
    data = load(export)
    found = [f"{c}/{i}" for c, d in data.items() if c.startswith("marks/") for i, b in d.items()
             if i not in ids and filled(b)]
    print(f"{len(found)} stored marks on rows the item table no longer has (the app lists them as Older notes)")
    for f in found:
        print("  " + f)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest").add_argument("export")
    d = sub.add_parser("diff")
    d.add_argument("before")
    d.add_argument("after")
    d.add_argument("--allow-newer", action="store_true")
    sub.add_parser("orphans").add_argument("export")
    a = ap.parse_args()
    if a.cmd == "manifest":
        return manifest(a.export)
    if a.cmd == "diff":
        return diff(a.before, a.after, a.allow_newer)
    return orphans(a.export)


if __name__ == "__main__":
    sys.exit(main())
