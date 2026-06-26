#!/usr/bin/env python3
"""Unit test for tools/netcode/sync_diff.py — the cross-client determinism DIFF is load-bearing, so it gets a test.

Proves the leg-row/bug-id collision (Workstream-0 Defect #1) is actually closed, not just moved:
constructs traces where bug 0 and bug 1 of a swarm DIVERGE behind a colliding leg row (hasLeg digit ==
the bug id), and asserts the canonical loader returns the REAL bug state (catches the divergence) while the
OLD buggy loader shadowed it with leg data. Plus identical (no false-fail) and hash-only (set-diff) cases.

Run: python3 tools/netcode/test_sync_diff.py   (exit 0 = all pass, 1 = a test failed)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_diff  # noqa: E402


def bugrow(tick, swarm, bug, x, y, vx, vy):
    # 15 cols: tick,swarm,bug,x,y,vx,vy,behavior,a,rng,b,legX,legY,c,source
    return f"{tick},{swarm},{bug},{x},{y},{vx},{vy},wander,3,12345,6,0,0,0,test"


def legrow(tick, swarm, has_leg, ox, oy, tx, ty):
    # 14 cols: tick,swarm,hasLeg,originX,originY,targetX,targetY,speed,startTick,centerX,centerY,fbX,fbY,food
    return f"{tick},{swarm},{has_leg},{ox},{oy},{tx},{ty},200,1,{ox},{oy},0,0,0"


def write_trace(path, hashes, bugrows, legrows):
    lines = ["# State hashes per tick (for quick divergence check)"]
    for t, h in hashes:
        lines.append(f"# TICK {t} HASH {h} PLAYERS 2")
    lines.append("")
    lines.append("tick,swarmId,bugId,x,y,vx,vy,behavior,alert,rng,landticks,legx,legy,spawntick,source")
    lines.extend(bugrows)
    lines.append("")
    lines.append("# SWARMLEGS")
    lines.append("tick,swarmId,hasLeg,originX,originY,targetX,targetY,speed,startTick,centerX,centerY,fallbackX,fallbackY,foodNear")
    lines.extend(legrows)
    open(path, "w").write("\n".join(lines) + "\n")


# The OLD buggy loader, reproduced verbatim, to prove the fix changed real behavior.
def old_buggy_load(path):
    d = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        if not line[:1].isdigit():
            continue
        f = line.rstrip("\n").split(",")
        if len(f) < 7:
            continue
        try:
            t = int(f[0])
        except ValueError:
            continue
        d.setdefault(t, {})[(f[1], f[2])] = (f[3], f[4], f[5], f[6])
    return d


FAILED = []


def check(cond, msg):
    print(("  PASS: " if cond else "  FAIL: ") + msg)
    if not cond:
        FAILED.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="syncdiff_test_")
    A = os.path.join(tmp, "trace_A.csv")
    B = os.path.join(tmp, "trace_B.csv")

    # ---- Case 1: bug 0 and bug 1 diverge, behind colliding leg rows -------------------------------
    # s0 hasLeg=1 (leg key (s0,"1") collides with bug 1); s1 hasLeg=0 (collides with bug 0).
    print("Case 1: divergent bug 0 & bug 1 behind colliding leg rows")
    a_bugs = [bugrow(10, "s0", 0, 100, 100, 1, 1), bugrow(10, "s0", 1, 200, 200, 2, 2),
              bugrow(10, "s0", 2, 300, 300, 3, 3),
              bugrow(10, "s1", 0, 400, 400, 4, 4), bugrow(10, "s1", 1, 500, 500, 5, 5)]
    b_bugs = [bugrow(10, "s0", 0, 100, 100, 1, 1), bugrow(10, "s0", 1, 299, 299, 2, 2),  # bug1 y differs
              bugrow(10, "s0", 2, 300, 300, 3, 3),
              bugrow(10, "s1", 0, 499, 499, 4, 4), bugrow(10, "s1", 1, 500, 500, 5, 5)]  # bug0 x differs
    legs = [legrow(10, "s0", 1, 900, 900, 950, 950), legrow(10, "s1", 0, 800, 800, 850, 850)]
    write_trace(A, [(10, "HASH_A")], a_bugs, legs)
    write_trace(B, [(10, "HASH_B")], b_bugs, legs)

    # The canonical loader returns the REAL bug rows, not the leg (no collision).
    la = sync_diff.load_bugs(A)
    check(la[10][("s0", "1")] == ("200", "200", "2", "2"),
          "canonical load_bugs gives bug (s0,1) its real (x,y,vx,vy), not the leg origin/target")
    check(("s0", "1") in la[10] and la[10][("s0", "1")] != ("900", "900", "950", "950"),
          "bug (s0,1) is NOT shadowed by the hasLeg=1 leg row")

    # The OLD loader shadowed it with the leg's origin/target — proving the bug was real.
    oa = old_buggy_load(A)
    check(oa[10][("s0", "1")] == ("900", "900", "950", "950"),
          "OLD loader DID shadow bug (s0,1) with leg data (confirms the defect existed)")

    code, lines = sync_diff.compare(A, B)
    report = "\n".join(lines)
    check(code == 1, "compare() reports DIVERGED (code 1)")
    check("('s0', '1')" in report, "divergence report names bug (s0,1) — caught, not masked")
    check("('s1', '0')" in report, "divergence report names bug (s1,0) — caught, not masked")

    # ---- Case 2: identical traces -> no false-fail ------------------------------------------------
    print("Case 2: identical traces")
    write_trace(B, [(10, "HASH_A")], a_bugs, legs)  # B == A now
    code2, lines2 = sync_diff.compare(A, B)
    check(code2 == 0, "compare() reports IDENTICAL (code 0) for identical traces")

    # ---- Case 3: per-bug clean but hashes differ (e.g. a set difference) --------------------------
    print("Case 3: hash-only divergence (per-bug intersection clean)")
    write_trace(A, [(10, "HASH_X")], a_bugs, legs)
    write_trace(B, [(10, "HASH_Y")], a_bugs, legs)  # same bugs, different whole-state hash
    code3, lines3 = sync_diff.compare(A, B)
    check(code3 == 1, "compare() reports DIVERGED (code 1) when only the whole-state hash differs")
    check("DIVERGED (hash)" in "\n".join(lines3), "hash-only divergence is reported via the hash branch")

    print()
    if FAILED:
        print(f"RESULT: {len(FAILED)} CHECK(S) FAILED")
        return 1
    print("RESULT: ALL CHECKS PASSED — sync_diff is sound (leg/bug-id collision closed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
