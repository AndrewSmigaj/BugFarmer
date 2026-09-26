"""migrate.py — move the existing player art into the scratchpad/current/archive shape. FREE, no API.

  python3 tools/player_sprites/migrate.py                # DRY RUN. Prints the plan, moves nothing.
  python3 tools/player_sprites/migrate.py bronze         # DRY RUN for one outfit
  python3 tools/player_sprites/migrate.py --go           # actually do it

DRY RUN IS THE DEFAULT, ON PURPOSE. Every bulk move run against this folder so far has destroyed or
hidden something the owner was using — a bulk re-cut overwrote approved gauntlets, and 131 files were
archived out from under him mid-conversation. So: print the plan, let a human read it, and only then move.

NOTHING IS DELETED. Files move; duplicates are flagged but still moved rather than dropped, because
"it looked like a duplicate" is exactly the reasoning that loses work.

Everything is in git before this runs, so the whole thing is one `git checkout` away from undone.
"""
import argparse
import hashlib
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_animations as R                            # noqa: E402

PLAYER = R.PLAYER
OUTFITS = R.OUTFITS
APPROVED = os.path.join(PLAYER, "APPROVED")
ARCHIVED_GAUNTLETS = os.path.join(PLAYER, "archive", "2026-08-01_pre-redo", "gauntlets")

FRAME = re.compile(r"^(front|side|back)_\d+\.png$", re.I)

# Loose review sheets I generated at the player root. Not the owner's reference images — he objected to
# them being there. They move to archive/, they are not deleted.
ROOT_KEEP = {"README.md", "HOW_TO_ASEPRITE.md", "RUNS.txt", "gallery.html"}


def digest(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def approved_digests():
    if not os.path.isdir(APPROVED):
        return {}
    out = {}
    for root, _, files in os.walk(APPROVED):
        for f in files:
            if f.lower().endswith((".png", ".gif")):
                out[digest(os.path.join(root, f))] = os.path.relpath(os.path.join(root, f), PLAYER)
    return out


def record_stamp(d):
    """A batch name from the folder's RECORD.txt date, so the batch is named for WHEN it was made."""
    p = os.path.join(d, "RECORD.txt")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8", errors="replace"):
            if line.lower().startswith("when"):
                m = re.search(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})", line)
                if m:
                    return "{}-{}-{}-{}{}".format(*m.groups())
    return "undated"


def plan_outfit(outfit, appr):
    """[(src, dest, note)] for one outfit. Sources and dests are absolute."""
    d = R.outfit_dir(outfit)
    cur = os.path.join(d, "current")
    scr = os.path.join(d, "scratchpad")
    arc = os.path.join(d, "archive")
    moves = []

    sheet_batch = os.path.join(scr, "1-candidates", f"{record_stamp(d)}-original-sheet")

    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if f in ("current", "scratchpad", "archive", "animations", "hands"):
            continue
        if os.path.isdir(p):
            moves.append((p, os.path.join(scr, "2-frames", f"unsorted-{f}"), "unrecognised folder"))
        elif FRAME.match(f):
            moves.append((p, os.path.join(cur, f), ""))
        elif f in ("result.png",) or f.startswith("ref_") or f == "RECORD.txt":
            moves.append((p, os.path.join(sheet_batch, f), "the sheet this outfit was cut from"))
        elif f.lower().endswith(".gif"):
            dup = appr.get(digest(p))
            moves.append((p, os.path.join(arc, "preview-gifs", f),
                          f"identical to {dup}" if dup else "old preview"))
        else:
            moves.append((p, os.path.join(arc, "loose", f), "unclassified"))

    anim = os.path.join(d, "animations")
    if os.path.isdir(anim):
        for f in sorted(os.listdir(anim)):
            moves.append((os.path.join(anim, f), os.path.join(cur, "anim", f), ""))

    hands = os.path.join(d, "hands")
    if os.path.isdir(hands):
        for f in sorted(os.listdir(hands)):
            p = os.path.join(hands, f)
            if f == "candidates" and os.path.isdir(p):
                for b in sorted(os.listdir(p)):
                    bp = os.path.join(p, b)
                    if os.path.isdir(bp):
                        moves.append((bp, os.path.join(scr, "3-gauntlets", f"{record_stamp(bp)}-{b}"), ""))
                    else:
                        moves.append((bp, os.path.join(scr, "3-gauntlets", "loose", b), ""))
            elif f.startswith("grip_"):
                moves.append((p, os.path.join(cur, "gauntlet", f), "APPROVED tool grip"))
            else:
                moves.append((p, os.path.join(scr, "3-gauntlets", "loose", f), ""))

    # the outfit's own gauntlet, currently only in the gitignored 08-01 archive
    g = os.path.join(ARCHIVED_GAUNTLETS, outfit)
    if os.path.isdir(g):
        for f in sorted(os.listdir(g)):
            if os.path.splitext(f)[1].lower() == ".png" and f.split(".")[0] in ("front", "back", "side", "grip"):
                moves.append((os.path.join(g, f), os.path.join(cur, "gauntlet", f),
                              "COPY out of the gitignored archive"))
    return moves


def plan_root(appr):
    moves = []
    dest = os.path.join(PLAYER, "archive", "review-sheets")
    for f in sorted(os.listdir(PLAYER)):
        p = os.path.join(PLAYER, f)
        if os.path.isdir(p) or f in ROOT_KEEP:
            continue
        if os.path.splitext(f)[1].lower() in (".png", ".gif"):
            dup = appr.get(digest(p))
            moves.append((p, os.path.join(dest, f), f"identical to {dup}" if dup else "review sheet"))
    return moves


def show(title, moves):
    if not moves:
        return
    print(f"\n{title}")
    for src, dst, note in moves:
        s = os.path.relpath(src, PLAYER).replace(os.sep, "/")
        t = os.path.relpath(dst, PLAYER).replace(os.sep, "/")
        kind = "dir " if os.path.isdir(src) else "    "
        print(f"  {kind}{s}\n       -> {t}" + (f"   ({note})" if note else ""))


def apply(moves):
    copies = 0
    for src, dst, note in moves:
        if not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if note.startswith("COPY"):
            shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
            copies += 1
        else:
            if os.path.exists(dst):
                print(f"  SKIP (dest exists) {dst}")
                continue
            shutil.move(src, dst)
    return copies


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Migrate player art into scratchpad/current/archive.")
    ap.add_argument("outfits", nargs="*", help="default: all")
    ap.add_argument("--go", action="store_true", help="actually move (default is a dry run)")
    ap.add_argument("--root", action="store_true", help="also tidy the loose files at the player root")
    a = ap.parse_args()

    appr = approved_digests()
    targets = a.outfits or R.all_outfits()
    allmoves = []
    for o in targets:
        m = plan_outfit(o, appr)
        show(f"--- {o}  ({len(m)} items)", m)
        allmoves += m
    if a.root:
        m = plan_root(appr)
        show(f"--- player root  ({len(m)} items)", m)
        allmoves += m

    print(f"\n{len(allmoves)} item(s) across {len(targets)} outfit(s)")
    if not a.go:
        print("DRY RUN — nothing moved. Re-run with --go to apply.")
    else:
        c = apply(allmoves)
        print(f"applied. {c} copied (left in place at source), {len(allmoves) - c} moved.")
