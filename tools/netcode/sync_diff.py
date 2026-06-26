#!/usr/bin/env python3
"""Canonical cross-client sync diff for the headless 2-client determinism harness.

SINGLE SOURCE OF TRUTH shared by tools/run_sync_test.sh + tools/run_sync_latejoin.sh, and unit-tested by
tools/netcode/test_sync_diff.py — because the test harness is load-bearing and "tests have no tests".

Input: two TickTraceBuffer CSV dumps (BugFarmerClient .../Debug/TickTraceBuffer.cs). Each file is:
    # State hashes per tick ...
    # TICK <n> HASH <hex> PLAYERS <p>     <- per-tick whole-_swarms FNV hash (collision-free), section 1
    <blank>
    tick,swarmId,bugId,x,y,vx,vy,...      <- BUG rows (15 cols); the header line is non-digit
    ... (one per bug per tick)
    <blank>
    # SWARMLEGS                            <- DIAGNOSTIC leg section. Everything after = NOT bug rows.
    tick,swarmId,hasLeg,originX,...        <- leg rows (14 cols); f[2]=hasLeg serializes 0/1

Two independent signals:
  PRIMARY  = the per-tick HASH stream over common ticks (whole client state; identical => bit-identical).
             Also catches a divergent SWARM SET (different bugs present), which the per-bug diff cannot.
  LOCALIZER= per-bug (swarmId,bugId)->(x,y,vx,vy) on the INTERSECTION, to pinpoint WHICH bug drifted.

WHY the explicit `break` at "# SWARMLEGS" + the `len==15` guard (the bug this file fixes): the old inline
diff ingested EVERY digit-led >=7-col line, so a 14-col leg row's key (swarm, hasLeg="0"/"1") COLLIDED with
bug-id 0/1's key and (being written later) OVERWROTE it -> bug 0/1 of every swarm was silently shadowed by
leg data (a real divergence there could be MASKED). Stop at the marker AND only accept exact bug rows.

Exit codes: 0 = identical, 1 = diverged, 2 = inconclusive.
"""
import sys
import re

BUG_COLS = 15  # tick,swarmId,bugId,x,y,vx,vy,behavior,?,rng,?,legX,legY,?,source


def load_bugs(path):
    """tick -> {(swarmId,bugId): (x,y,vx,vy)} from the BUG section only (stops at # SWARMLEGS)."""
    d = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("# SWARMLEGS"):
            break  # leg diagnostics follow; their f[2]=hasLeg(0/1) would collide with bug-id 0/1 keys
        if not line[:1].isdigit():
            continue  # comments (# ...), blank lines, and the "tick,swarmId,..." header
        f = line.rstrip("\n").split(",")
        if len(f) != BUG_COLS:
            continue  # belt-and-suspenders: only the exact bug-row shape is ever a bug
        try:
            t = int(f[0])
        except ValueError:
            continue
        d.setdefault(t, {})[(f[1], f[2])] = (f[3], f[4], f[5], f[6])
    return d


def load_hashes(path):
    """tick -> hash hex, from the '# TICK <n> HASH <hex>' lines (section 1)."""
    h = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"# TICK (\d+) HASH (\S+)", line)
        if m:
            h[int(m.group(1))] = m.group(2)
    return h


def compare(ta, tb):
    """Returns (exit_code, lines[]) — pure, so test_sync_diff.py can assert on it."""
    out = []
    A, B = load_bugs(ta), load_bugs(tb)
    HA, HB = load_hashes(ta), load_hashes(tb)
    common = sorted(set(A) & set(B))
    if not common:
        out.append("INCONCLUSIVE: no overlapping ticks (clients never co-simulated).")
        return 2, out

    hcommon = sorted(set(HA) & set(HB))
    hmis = [t for t in hcommon if HA[t] != HB[t]]

    shared = mismatch = 0
    first = None
    divbugs = {}
    for t in common:
        a, b = A[t], B[t]
        for k in (a.keys() & b.keys()):
            shared += 1
            if a[k] != b[k]:
                mismatch += 1
                divbugs[k] = divbugs.get(k, 0) + 1
                if first is None:
                    first = (t, k, a[k], b[k])

    out.append(f"common ticks={len(common)} ({common[0]}..{common[-1]}); "
               f"shared-bug comparisons={shared}; hash-common ticks={len(hcommon)}")
    if shared == 0:
        out.append("INCONCLUSIVE: clients shared NO bugs (disjoint chunk subscriptions).")
        return 2, out
    if not hcommon:
        out.append("WARNING: no common hash ticks — per-bug localizer only (hash gate unavailable).")

    # PASS only if BOTH the whole-state hash AND every shared per-bug state match.
    if mismatch == 0 and not hmis:
        out.append(f"SYNC: IDENTICAL — all {shared} shared-bug states match AND all "
                   f"{len(hcommon)} common-tick hashes match.")
        return 0, out

    # Per-bug clean but whole-state hash differs => divergence the per-bug intersection can't see
    # (a bug present on only one client, i.e. a SET difference, or a non-(x,y,vx,vy) hashed field).
    if mismatch == 0 and hmis:
        out.append(f"SYNC: DIVERGED (hash) — {len(hmis)}/{len(hcommon)} common-tick hashes differ "
                   f"though all shared (x,y,vx,vy) match. First hash-mismatch tick {hmis[0]}. "
                   f"(Divergence is outside the shared-bug intersection — likely a swarm-SET difference.)")
        return 1, out

    pct = 100.0 * mismatch / shared
    t, k, va, vb = first
    topbugs = sorted(divbugs.items(), key=lambda kv: -kv[1])[:5]
    out.append(f"SYNC: DIVERGED — {mismatch}/{shared} shared-bug states differ ({pct:.1f}%); "
               f"hash-mismatch {len(hmis)}/{len(hcommon)} ticks. First: tick {t} bug {k} A={va} B={vb}")
    out.append(f"  top divergent bugs (swarm,bug -> ticks): {topbugs}")
    return 1, out


def main(argv):
    if len(argv) != 3:
        print("usage: sync_diff.py <trace_A.csv> <trace_B.csv>")
        return 2
    code, lines = compare(argv[1], argv[2])
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
