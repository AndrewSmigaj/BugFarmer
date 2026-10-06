#!/usr/bin/env python3
"""Tests for equiv_check.py — the old-build-against-new-build check (tests have tests: a checker that passes
everything would let a changed build through). Each case writes small logs to a temp folder.

    python3 tools/netcode/test_equiv_check.py
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import equiv_check as ec  # noqa: E402


def hashlog(rows, markers=(), live_from=0):
    """rows: list of (tick, hash, full, bugs); markers: list of (kind, tick) inserted before that tick's row."""
    out = ["tick,hash,full,bugs,live"]
    mk = {}
    for kind, tick in markers:
        mk.setdefault(tick, []).append(kind)
    for tick, h, f, n in rows:
        for kind in mk.get(tick, []):
            out.append(f"#{kind},{tick}")
        out.append(f"{tick},{h},{f},{n},{1 if tick >= live_from else 0}")
    return "\n".join(out) + "\n"


def steady(n=400, start=1000, differ_at=None, field=0):
    rows = []
    for t in range(start, start + n):
        h, f, c = f"H{t:08X}", f"F{t:08X}", "500"
        if differ_at is not None and t >= differ_at:
            if field == 0:
                h = "XX"
            elif field == 1:
                f = "YY"
            else:
                c = "499"
        rows.append((t, h, f, c))
    return rows


class EquivCheck(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="equiv_")

    def write(self, name, text):
        p = os.path.join(self.dir, name)
        with open(p, "w") as f:
            f.write(text)
        return p

    def run_check(self, a_text, b_text, extra=()):
        a, b = self.write("a.csv", a_text), self.write("b.csv", b_text)
        return ec.main([a, b, "--min-ticks", "300", *extra])

    def test_identical(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, a), 0)

    def test_state_check_difference_is_caught(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(differ_at=1200), markers=[("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, b), 1)

    def test_full_record_difference_is_caught(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(differ_at=1300, field=1), markers=[("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, b), 1)

    def test_bug_count_difference_is_caught(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(differ_at=1350, field=2), markers=[("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, b), 1)

    def test_resync_is_inconclusive(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(), markers=[("live", 1000), ("resync", 1200)], live_from=1000)
        self.assertEqual(self.run_check(a, b), 2)

    def test_timeout_is_inconclusive(self):
        a = hashlog(steady(), markers=[("timeout", 1000), ("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, a), 2)

    def test_replay_after_live_is_inconclusive(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(), markers=[("live", 1000), ("replay", 1250)], live_from=1000)
        self.assertEqual(self.run_check(a, b), 2)

    def test_join_replay_before_live_is_normal(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        b = hashlog(steady(), markers=[("replay", 1000), ("live", 1050)], live_from=1050)
        self.assertEqual(self.run_check(a, b), 0)

    def test_short_overlap_is_inconclusive(self):
        a = hashlog(steady(n=100), markers=[("live", 1000)], live_from=1000)
        self.assertEqual(self.run_check(a, a), 2)

    def test_first_value_per_tick_wins(self):
        # B re-runs ticks 1100..1149 (a replay) with DIFFERENT values; the first values (identical to A) must be kept,
        # so the result is identical on the hashes — and the replay marker makes it inconclusive overall.
        rows = steady()
        dup = [(t, "ZZ", "ZZ", "1") for t in range(1100, 1150)]
        b_text = hashlog(rows, markers=[("live", 1000)], live_from=1000) + "".join(f"{t},{h},{f},{n},1\n" for t, h, f, n in dup)
        log = ec.load_hashlog(self.write("b_dup.csv", b_text))
        self.assertEqual(log.rows[1120][0], "H00000460")

    def test_reports_identical_and_different(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        rep = "tick,kind,a,b,ids,sent\n#live,1000\n1200,detect,w1,f1,3;4,1\n1250,corpse,dead_fly_9,,,1\n"
        rep_b_same = rep.replace(",1\n", ",0\n")  # the other computer only logs: `sent` differs, nothing else
        rep_b_diff = rep.replace("3;4", "3;5")
        ra, rbs, rbd = self.write("ra.csv", rep), self.write("rbs.csv", rep_b_same), self.write("rbd.csv", rep_b_diff)
        self.assertEqual(self.run_check(a, a, ["--reports", ra, rbs, "--warmup", "100"]), 0)
        self.assertEqual(self.run_check(a, a, ["--reports", ra, rbd, "--warmup", "100"]), 1)

    def test_reports_in_warmup_are_ignored(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        ra = self.write("ra.csv", "tick,kind,a,b,ids,sent\n#live,1000\n1050,detect,w1,f1,3,1\n1200,detect,w1,f1,7,1\n")
        rb = self.write("rb.csv", "tick,kind,a,b,ids,sent\n#live,1000\n1200,detect,w1,f1,7,0\n")
        self.assertEqual(self.run_check(a, a, ["--reports", ra, rb, "--warmup", "100"]), 0)

    def test_quiet_reports_are_inconclusive(self):
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        r = self.write("r.csv", "tick,kind,a,b,ids,sent\n#live,1000\n")
        self.assertEqual(self.run_check(a, a, ["--reports", r, r]), 2)


    def test_strike_phase_is_ignored_by_default(self):
        # The same predator's sends, paced by each computer's own throttle, come out at shifted ticks (a late joiner's
        # throttle starts empty); detections match. Default: identical. Asking for strikes too: a difference.
        a = hashlog(steady(), markers=[("live", 1000)], live_from=1000)
        common = "1200,detect,w1,f1,5,0\n1240,detect,w1,f1,5,0\n"
        ra = self.write("ra.csv", "tick,kind,a,b,ids,sent\n#live,1000\n" + common + "1200,strike,w1,f1,5,1\n")
        rb = self.write("rb.csv", "tick,kind,a,b,ids,sent\n#live,1000\n" + common + "1240,strike,w1,f1,5,0\n")
        self.assertEqual(self.run_check(a, a, ["--reports", ra, rb, "--warmup", "100"]), 0)
        self.assertEqual(self.run_check(a, a, ["--reports", ra, rb, "--warmup", "100", "--kinds", "detect,strike"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
