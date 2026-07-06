#!/usr/bin/env python3
"""The FOOTPRINT TABLE — every world entity's true grid size, generated from canonical data.

NEVER guess a footprint (a bed_basic placed as 1x1 was actually 2x4 and cost a scene rebuild —
zone-craft HARD RULE 1). This script reads `nakama/data/entities/{occupants,placeables,crops}.json`
and emits one table: id · footprint WxH · sprite WxH · pivot · source file. Sorted so the BIG
pieces (the ones that bite) lead each section.

Usage:  python3 tools/data/footprints.py            # write tools/_generated/footprints.md + stdout summary
        python3 tools/data/footprints.py --check    # exit non-zero if the written table is stale
        python3 tools/data/footprints.py --id bed_basic   # print one entity's line (the quick lookup)
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "nakama", "data", "entities")
OUT = os.path.join(ROOT, "tools", "_generated", "footprints.md")
FILES = ["occupants.json", "placeables.json", "crops.json"]


def rows():
    out = []
    for fn in FILES:
        path = os.path.join(SRC, fn)
        if not os.path.exists(path):
            continue
        data = json.load(open(path))
        for eid, e in data.items():
            if not isinstance(e, dict):
                continue
            w = e.get("world") or {}
            fw, fh = (w.get("footprint") or [1, 1])[:2]
            out.append({
                "id": eid, "fw": fw, "fh": fh,
                "sw": e.get("sprite_w", "?"), "sh": e.get("sprite_h", "?"),
                "pivot": w.get("pivot", "-"), "src": fn.replace(".json", ""),
            })
    return out


def render(all_rows):
    lines = [
        "# Entity footprints (GENERATED — do not edit; run `python3 tools/data/footprints.py`)",
        "",
        "The grid cells an anchor placement OCCUPIES (`world.footprint` WxH; the anchor is the",
        "SW cell, the footprint extends +x/+y — i.e. RIGHT and UP/NORTH on the map, which in an",
        "authoring TEXT GRID means later columns and EARLIER lines). Guessing these costs",
        "rebuilds: check anything you haven't placed before, and everything bigger than 1x1.",
        "",
    ]
    multi = sorted([r for r in all_rows if (r["fw"], r["fh"]) != (1, 1)],
                   key=lambda r: (-(r["fw"] * r["fh"]), r["id"]))
    singles = sorted([r for r in all_rows if (r["fw"], r["fh"]) == (1, 1)], key=lambda r: r["id"])
    lines.append(f"## Multi-cell footprints ({len(multi)}) — the ones that bite")
    lines.append("")
    lines.append("| id | footprint | sprite px | pivot | source |")
    lines.append("|----|-----------|-----------|-------|--------|")
    for r in multi:
        lines.append(f"| {r['id']} | **{r['fw']}x{r['fh']}** | {r['sw']}x{r['sh']} | {r['pivot']} | {r['src']} |")
    lines.append("")
    lines.append(f"## Single-cell ({len(singles)}) — safe anywhere free")
    lines.append("")
    lines.append("| id | sprite px | pivot | source |")
    lines.append("|----|-----------|-------|--------|")
    for r in singles:
        lines.append(f"| {r['id']} | {r['sw']}x{r['sh']} | {r['pivot']} | {r['src']} |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit non-zero if the table is stale")
    ap.add_argument("--id", help="print one entity's footprint line and exit")
    args = ap.parse_args()

    all_rows = rows()
    if args.id:
        hits = [r for r in all_rows if r["id"] == args.id]
        if not hits:
            raise SystemExit(f"{args.id}: not found in {FILES}")
        r = hits[0]
        print(f"{r['id']}: footprint {r['fw']}x{r['fh']}, sprite {r['sw']}x{r['sh']}px, "
              f"pivot {r['pivot']} ({r['src']})")
        return

    text = render(all_rows)
    if args.check:
        current = open(OUT).read() if os.path.exists(OUT) else ""
        if current != text:
            raise SystemExit(f"STALE: {OUT} does not match the entity data — regenerate.")
        print(f"OK: {OUT} is current ({len(all_rows)} entities).")
        return

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(text)
    multi_n = sum(1 for r in all_rows if (r["fw"], r["fh"]) != (1, 1))
    print(f"wrote {OUT}  ({len(all_rows)} entities, {multi_n} multi-cell)")


if __name__ == "__main__":
    main()
