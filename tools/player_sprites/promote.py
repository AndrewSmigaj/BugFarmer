"""promote.py — make something the current version of an outfit. FREE, no API.

  python3 tools/player_sprites/promote.py bronze scratchpad/2-frames/2026-08-02-1344-first-cut \
      "ok lets use this one moving forward"

  python3 tools/player_sprites/promote.py bronze scratchpad/3-gauntlets/2026-08-02-1120-plated \
      "these are good" --dry-run

PROMOTING **IS** RECORDING — that is the entire point
-----------------------------------------------------
One atomic action: copy into `current/`, move whatever it replaced into `archive/`, append the row to
`CURRENT.md` with the owner's words VERBATIM, re-render the animations, refresh the gallery.

There is deliberately NO way to promote something without recording it, because every time recording was a
separate step it got skipped — and a decision nobody wrote down is a decision that gets lost. This is not a
reminder; it is the only path. The pre-commit hook (`check_sprite_ledger.py`) fails the commit if
`CURRENT.md` and `current/` ever disagree, which catches a hand-copy that bypassed this script.

WHAT GOES WHERE
---------------
The stage is inferred from the path, so you don't pass it:

  scratchpad/1-candidates/<batch>/  -> current/            the chosen sheet
  scratchpad/2-frames/<batch>/      -> current/            front_*/side_*/back_*
  scratchpad/3-gauntlets/<batch>/   -> current/gauntlet/

`anim/` IS ledgered. The MOTION is the decision and the gif is the record of it.

NOTHING IS EVER DELETED. What `current/` held before moves to `archive/<when>-superseded/`.
"""
import argparse
import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_animations as R                            # noqa: E402

PLAYER = R.PLAYER
LEDGER = "CURRENT.md"
# `anim/` USED to be excluded as derived output, regenerated from the frames. That is no longer true:
# the MOTION is the thing being chosen, and the gif is the record of that choice. An agreed animation
# that is not ledgered is exactly what went missing on 2026-08-04.
DERIVED = ()          # regenerated, never ledgered
IMG = (".png", ".gif")

STAGE_DEST = {"1-candidates": "", "2-frames": "", "3-gauntlets": "gauntlet"}

HEADER = """# {outfit} — current

Everything in `current/` and where it came from. **Written by `promote.py`; do not hand-edit.**
The pre-commit hook fails the commit if this table and the folder disagree.

`anim/` is listed too — an agreed motion is a decision, not derived output.

| file | agreed | from | your words |
|---|---|---|---|
"""

FOOTER_KEY = "## Deployed to the game"


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M")


def infer_stage(relpath):
    parts = relpath.replace("\\", "/").split("/")
    for p in parts:
        if p in STAGE_DEST:
            return p
    return None


def read_rows(path):
    """Existing ledger rows as {file: (agreed, source, words)}."""
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| ") or line.startswith("| file ") or set(line.strip()) <= set("|- "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4:
                rows[cells[0].strip("`")] = (cells[1], cells[2], cells[3])
    return rows


def deployed_note(path):
    if os.path.exists(path):
        body = open(path, encoding="utf-8").read()
        if FOOTER_KEY in body:
            return body.split(FOOTER_KEY, 1)[1].strip()
    return "Not yet deployed."


def write_ledger(path, outfit, rows, deployed):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEADER.format(outfit=outfit))
        for f in sorted(rows):
            agreed, source, words = rows[f]
            fh.write(f"| `{f}` | {agreed} | `{source}` | {words} |\n")
        fh.write(f"\n{FOOTER_KEY}\n{deployed}\n")


def current_files(cur):
    """Every ledgerable file under current/, relative to it. Excludes derived + the ledger itself."""
    out = []
    for root, dirs, files in os.walk(cur):
        dirs[:] = [d for d in dirs if d not in DERIVED]
        for f in files:
            if f == LEDGER:
                continue
            if os.path.splitext(f)[1].lower() in IMG:
                out.append(os.path.relpath(os.path.join(root, f), cur).replace(os.sep, "/"))
    return sorted(out)


def promote(outfit, src, words, dry=False, rerender=True):
    d = R.outfit_dir(outfit)
    if not os.path.isdir(d):
        raise SystemExit(f"no such outfit: {outfit}")
    if not words or not words.strip():
        raise SystemExit("refusing to promote with no reason recorded — pass the owner's words verbatim")

    abs_src = src if os.path.isabs(src) else os.path.join(d, src)
    if not os.path.exists(abs_src):
        raise SystemExit(f"not found: {abs_src}")

    rel_src = os.path.relpath(abs_src, d).replace(os.sep, "/")
    stage = infer_stage(rel_src)
    if stage is None:
        raise SystemExit(f"cannot tell which stage this is from the path: {rel_src}\n"
                         f"expected one of {list(STAGE_DEST)} in it")
    sub = STAGE_DEST[stage]

    cur = os.path.join(d, "current")
    dest_dir = os.path.join(cur, sub) if sub else cur

    files = ([f for f in sorted(os.listdir(abs_src)) if os.path.splitext(f)[1].lower() in IMG]
             if os.path.isdir(abs_src) else [os.path.basename(abs_src)])
    if not files:
        raise SystemExit(f"nothing to promote — no images in {abs_src}")
    src_dir = abs_src if os.path.isdir(abs_src) else os.path.dirname(abs_src)

    # what it replaces
    replaced = [f for f in files if os.path.exists(os.path.join(dest_dir, f))]
    arch = os.path.join(d, "archive", f"{stamp()}-superseded")

    print(f"  outfit   {outfit}")
    print(f"  stage    {stage}  ->  current/{sub or ''}")
    print(f"  from     {rel_src}")
    print(f"  promote  {len(files)} file(s): {', '.join(files[:6])}{' …' if len(files) > 6 else ''}")
    print(f"  replaces {len(replaced)} -> archive/{os.path.basename(arch)}" if replaced else "  replaces nothing")
    print(f"  words    {words!r}")
    if dry:
        print("\n  --dry-run, nothing written")
        return None

    if replaced:
        os.makedirs(arch, exist_ok=True)
        for f in replaced:
            shutil.move(os.path.join(dest_dir, f), os.path.join(arch, f))
    os.makedirs(dest_dir, exist_ok=True)
    for f in files:
        shutil.copy2(os.path.join(src_dir, f), os.path.join(dest_dir, f))

    ledger = os.path.join(cur, LEDGER)
    rows = read_rows(ledger)
    deployed = deployed_note(ledger)
    when = now()
    for f in files:
        key = f"{sub}/{f}" if sub else f
        rows[key] = (when, os.path.dirname(rel_src) if not os.path.isdir(abs_src) else rel_src,
                     words.replace("|", "\\|"))
    # drop rows whose file no longer exists, so the ledger can't drift from the folder
    have = set(current_files(cur))
    rows = {k: v for k, v in rows.items() if k in have}
    write_ledger(ledger, outfit, rows, deployed)
    print(f"\n  ledger   {len(rows)} row(s) -> {os.path.relpath(ledger, PLAYER)}")

    if rerender:
        made, gaps, prov = R.build(outfit, verbose=False)
        print(f"  animate  {len(made)} animation(s), hands = {prov}")
        for g in gaps:
            print(f"    GAP  {g}")
        import gallery
        gallery.build()
    return ledger


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Make something the current version of an outfit.")
    ap.add_argument("outfit")
    ap.add_argument("path", help="path under the outfit folder, e.g. scratchpad/2-frames/<batch>")
    ap.add_argument("words", help="the owner's words, verbatim — this goes in the ledger")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-rerender", action="store_true")
    a = ap.parse_args()
    promote(a.outfit, a.path, a.words, dry=a.dry_run, rerender=not a.no_rerender)
