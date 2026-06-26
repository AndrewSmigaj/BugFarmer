#!/usr/bin/env python3
"""
Determinism re-root diagnostic (Phase A / A2-A3).

Reads two per-bug trace CSVs (from the headless sync test, HeadlessSyncTest.cs -> TickTraceBuffer)
and, for every shared (swarmId,bugId), classifies divergence AND attributes it to the bug's spawn
provenance (spawnTick + spawnSource, the A1 instrumentation columns).

Goal: prove "material divergence <=> the two clients first simulated the bug at a DIFFERENT global
tick (re-root)", and quantify which acquisition vector dominates (metadataPrespawn vs liveSwarmUpdate
vs reproduce vs splitMerge), with snapshotApply expected to be the matched/clean set.

Trace row columns (15):
  0 tick 1 swarmId 2 bugId 3 x 4 y 5 vx 6 vy 7 behavior 8 alertCooldown 9 rngState
  10 ticksUntilChange 11 intentDirX 12 intentDirY 13 spawnTick 14 spawnSource

Usage: diag_determinism_provenance.py <traceA.csv> <traceB.csv> [material_fixedpoint_threshold]
       (threshold default 500 = 0.5 cell; positions are cell*1000 fixed-point)
"""
import sys, collections

MATERIAL = int(sys.argv[3]) if len(sys.argv) > 3 else 500  # 0.5 cell


def load(path):
    """tick -> {(swarm,bug): row}, plus per-bug provenance (constant per bug)."""
    per_tick = {}
    prov = {}  # (swarm,bug) -> (spawnTick, spawnSource)
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("# SWARMLEGS"):
            break  # leg section (digit-led rows w/ different schema) — see diag_leg_divergence.py
        if not line[:1].isdigit():
            continue
        f = line.rstrip("\n").split(",")
        if len(f) < 13:
            continue
        try:
            t = int(f[0])
        except ValueError:
            continue
        key = (f[1], f[2])
        per_tick.setdefault(t, {})[key] = f
        if len(f) >= 15 and key not in prov:
            try:
                prov[key] = (int(f[13]), f[14])
            except ValueError:
                prov[key] = (-1, f[14] if len(f) >= 15 else "?")
    return per_tick, prov


def main():
    A, provA = load(sys.argv[1])
    B, provB = load(sys.argv[2])
    common = sorted(set(A) & set(B))
    if not common:
        print("INCONCLUSIVE: no overlapping ticks")
        return
    print(f"common ticks {common[0]}..{common[-1]} ({len(common)}); material threshold "
          f"{MATERIAL} fixed-point (~{MATERIAL/1000:.2f} cell)")

    # classify each shared bug at its first co-observed tick
    allk = set()
    for t in common:
        allk |= (A[t].keys() & B[t].keys())

    rows = []  # (key, material?, rngDiff?, tucDiff?, spawnTickA, spawnTickB, srcA, srcB, maxDelta)
    for k in allk:
        ft = next(t for t in common if k in A[t] and k in B[t])
        a, b = A[ft][k], B[ft][k]
        # max position delta across the bug's shared lifetime
        md = 0
        for t in common:
            if k in A[t] and k in B[t]:
                md = max(md, abs(int(A[t][k][3]) - int(B[t][k][3])) +
                             abs(int(A[t][k][4]) - int(B[t][k][4])))
        rngDiff = a[9] != b[9]
        tucDiff = a[10] != b[10]
        material = md >= MATERIAL
        sa, sb = provA.get(k, (-1, "?")), provB.get(k, (-1, "?"))
        rows.append((k, material, rngDiff, tucDiff, sa[0], sb[0], sa[1], sb[1], md))

    total = len(rows)
    material = [r for r in rows if r[1]]
    print(f"\nshared bugs: {total}; material-divergent (>= {MATERIAL}): {len(material)} "
          f"({100*len(material)/total:.0f}%)")

    # CORE CLAIM: material divergence <=> different spawn tick across clients
    diff_spawn = sum(1 for r in material if r[4] != r[5])
    print(f"\n[A2] material-divergent bugs whose spawnTick differs A vs B: "
          f"{diff_spawn}/{len(material)} ({100*diff_spawn/max(1,len(material)):.0f}%)")
    same_spawn_material = [r for r in material if r[4] == r[5]]
    if same_spawn_material:
        print(f"  !! {len(same_spawn_material)} material bugs with SAME spawnTick — NOT explained by re-root; inspect:")
        for r in same_spawn_material[:6]:
            print(f"     {r[0]} spawnTick={r[4]} srcA={r[6]} srcB={r[7]} maxDelta={r[8]} rngDiff={r[2]} tucDiff={r[3]}")

    # control: matched bugs should mostly share spawn tick / be snapshotApply
    matched = [r for r in rows if not r[1]]
    msame = sum(1 for r in matched if r[4] == r[5])
    print(f"  (control) matched bugs with SAME spawnTick: {msame}/{len(matched)}")

    # [A3] vector split: source-pair for material-divergent bugs
    print("\n[A3] material-divergent bugs by (sourceA -> sourceB):")
    pair = collections.Counter((r[6], r[7]) for r in material)
    for (sa, sb), n in pair.most_common():
        print(f"  {sa:16s} | {sb:16s} : {n}")
    print("\n[A3] material-divergent bugs by source on the LATE-JOINER side (whichever differs from snapshotApply):")
    srccount = collections.Counter()
    for r in material:
        nonsnap = [s for s in (r[6], r[7]) if s != "snapshotApply"]
        srccount[nonsnap[0] if nonsnap else "snapshotApply"] += 1
    for s, n in srccount.most_common():
        print(f"  {s:16s}: {n}")

    # rng vs phase split among material (re-confirm the cycle-phase signature)
    rngm = sum(1 for r in material if r[2])
    tucm = sum(1 for r in material if r[3] and not r[2])
    print(f"\nmaterial signature: rngState-differ={rngm} (id-remap), "
          f"ticksUntilChange-differ-only={tucm} (re-root cycle phase)")


if __name__ == "__main__":
    main()
