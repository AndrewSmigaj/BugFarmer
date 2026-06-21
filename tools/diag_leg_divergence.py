#!/usr/bin/env python3
"""
Leg/center late-join divergence diagnostic (Part 1 D2).

Reads the per-swarm leg section ("# SWARMLEGS") of two sync-test trace CSVs (HeadlessSyncTest.cs ->
TickTraceBuffer, D1 instrumentation) and pins WHY a swarm's center diverges across clients. Because the
center is closed-form center(leg, tick) with a frontier-synced tick, two clients agree iff they hold the
same LEG. So at each common tick we compare each swarm's leg (origin/target/speed/startTick), its hasLeg
flag, the center bug AI used, and the metadata fallback center.

Outputs, per divergent swarm: the FIRST common tick it diverges, WHICH field, and hasLeg on each side —
distinguishing the two candidates:
  * leg-CONTENT divergence  -> hasLeg true both sides but a leg field differs (origin/target/speed/start)
  * no-leg FALLBACK mismatch -> hasLeg differs, or both false and fallback/center differ

Leg row columns (13):
  0 tick 1 swarmId 2 hasLeg 3 originX 4 originY 5 targetX 6 targetY 7 speed 8 startTick
  9 centerX 10 centerY 11 fallbackX 12 fallbackY

Usage: diag_leg_divergence.py <traceA.csv> <traceB.csv> [material_fixedpoint_threshold]
       (threshold default 500 = 0.5 cell; positions are cell*1000 fixed-point)
"""
import sys

MATERIAL = int(sys.argv[3]) if len(sys.argv) > 3 else 500  # 0.5 cell

FIELDS = ["hasLeg", "originX", "originY", "targetX", "targetY", "speed", "startTick",
          "centerX", "centerY", "fallbackX", "fallbackY", "foodNear"]


def load(path):
    """(swarmId, tick) -> dict of leg fields, read ONLY from the # SWARMLEGS section."""
    out = {}
    in_legs = False
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.rstrip("\n")
        if s.startswith("# SWARMLEGS"):
            in_legs = True
            continue
        if not in_legs:
            continue
        if not s[:1].isdigit():
            continue  # header line ("tick,swarmId,...") or stray
        f = s.split(",")
        if len(f) < 13:
            continue
        try:
            tick = int(f[0])
        except ValueError:
            continue
        swarm = f[1]
        out[(swarm, tick)] = {
            "hasLeg": f[2], "originX": int(f[3]), "originY": int(f[4]),
            "targetX": int(f[5]), "targetY": int(f[6]), "speed": int(f[7]),
            "startTick": int(f[8]), "centerX": int(f[9]), "centerY": int(f[10]),
            "fallbackX": int(f[11]), "fallbackY": int(f[12]),
            "foodNear": f[13] if len(f) > 13 else "0",
        }
    return out


def center_gap(a, b):
    dx = a["centerX"] - b["centerX"]
    dy = a["centerY"] - b["centerY"]
    return (dx * dx + dy * dy) ** 0.5


def diff_fields(a, b):
    return [k for k in FIELDS if a[k] != b[k]]


def main():
    A = load(sys.argv[1])
    B = load(sys.argv[2])
    if not A or not B:
        print(f"INCONCLUSIVE: no SWARMLEGS section (A={len(A)} rows, B={len(B)} rows). "
              f"Rebuild the sync-test player with the D1 leg instrumentation.")
        return

    ticks_a = {t for (_, t) in A}
    ticks_b = {t for (_, t) in B}
    common = sorted(ticks_a & ticks_b)
    swarms = sorted({s for (s, _) in A} & {s for (s, _) in B})
    print(f"common ticks {common[0]}..{common[-1]} ({len(common)}); shared swarms {len(swarms)}; "
          f"material center gap {MATERIAL} fp (~{MATERIAL/1000:.2f} cell)")

    # For each shared swarm, find the first common tick where the leg (or fallback/center) diverges.
    diverged = []  # (swarm, first_tick, fields, hasLegA, hasLegB, gap_at_first, gap_max)
    clean = 0
    for s in swarms:
        first = None
        gap_max = 0.0
        for t in common:
            a = A.get((s, t))
            b = B.get((s, t))
            if a is None or b is None:
                continue
            gap = center_gap(a, b)
            gap_max = max(gap_max, gap)
            fields = diff_fields(a, b)
            if first is None and (fields or gap >= MATERIAL):
                first = (t, fields, a["hasLeg"], b["hasLeg"], gap)
        if first is None:
            clean += 1
        else:
            t, fields, ha, hb, gap = first
            diverged.append((s, t, fields, ha, hb, gap, gap_max))

    print(f"\nswarms clean (leg+center identical all common ticks): {clean}/{len(swarms)}")
    print(f"swarms diverged: {len(diverged)}/{len(swarms)}")

    if not diverged:
        print("\nVERDICT: legs identical across clients at every common tick -> NOT a leg/center issue.")
        return

    diverged.sort(key=lambda r: r[1])  # by onset tick
    print("\n--- divergent swarms (earliest first) ---")
    for s, t, fields, ha, hb, gap, gap_max in diverged:
        kind = ("LEG-CONTENT" if ("hasLeg" not in fields and ha == "1" and hb == "1" and fields)
                else "NO-LEG/FALLBACK" if (ha != hb or (ha == "0" and hb == "0"))
                else "MIXED")
        print(f"  {s}: first@tick {t}  kind={kind}  hasLeg A={ha} B={hb}  "
              f"fields={fields or '[center-only]'}  gap@first={gap:.0f}  gap_max={gap_max:.0f}")

    # Aggregate which field most often leads the divergence.
    from collections import Counter
    lead = Counter()
    kinds = Counter()
    for s, t, fields, ha, hb, gap, gap_max in diverged:
        for k in (fields or ["<center-only>"]):
            lead[k] += 1
        kinds[("hasLeg-diff" if ha != hb else "both-noleg" if ha == "0" else "content")] += 1
    print("\nfield divergence frequency:", dict(lead))
    print("kind frequency:", dict(kinds))

    # Show the single earliest divergent swarm's leg side-by-side at onset (the smoking gun).
    s, t, fields, ha, hb, gap, gap_max = diverged[0]
    a = A[(s, t)]; b = B[(s, t)]
    print(f"\n--- earliest: {s} @ tick {t} (A vs B) ---")
    for k in FIELDS:
        mark = "  <-- DIFFERS" if a[k] != b[k] else ""
        print(f"  {k:10s}  A={a[k]:>12}  B={b[k]:>12}{mark}")


if __name__ == "__main__":
    main()
