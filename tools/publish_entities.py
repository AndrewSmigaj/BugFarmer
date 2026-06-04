#!/usr/bin/env python3
"""Publish the canonical entity data into the Unity client.

`nakama/data/entities/*.json` is the SINGLE canonical source a human edits; the
Go server and every Python tool read only from there. The Unity client needs its
own copy under `Resources/Data/entities/` (loaded at runtime by string path), so
this script does a one-way copy: canonical -> client. The client copy is published
output, never hand-edited. Run this after editing any entity JSON.

Usage:  python3 publish_entities.py [--check]
        --check : report drift and exit non-zero without writing (for CI / sanity).
"""
import argparse
import filecmp
import glob
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "nakama", "data", "entities")
DST = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Data", "entities")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit non-zero without writing")
    args = ap.parse_args()

    os.makedirs(DST, exist_ok=True)
    sources = sorted(glob.glob(os.path.join(SRC, "*.json")))
    if not sources:
        raise SystemExit(f"No entity JSON found in {SRC}")

    drift, copied = [], []
    for src in sources:
        name = os.path.basename(src)
        dst = os.path.join(DST, name)
        same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
        if same:
            continue
        drift.append(name)
        if not args.check:
            shutil.copy2(src, dst)  # copies .json only; Unity owns the .meta
            copied.append(name)

    rel = os.path.relpath(DST, ROOT)
    if args.check:
        if drift:
            print(f"OUT OF SYNC ({len(drift)}): {', '.join(drift)} -- run publish_entities.py")
            raise SystemExit(1)
        print("In sync: client entity data matches canonical source.")
        return
    if copied:
        print(f"Published {len(copied)} -> {rel}/: {', '.join(copied)}")
    else:
        print(f"Already up to date: {rel}/ matches canonical source.")


if __name__ == "__main__":
    main()
