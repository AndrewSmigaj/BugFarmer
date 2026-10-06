#!/usr/bin/env python3
"""Tests for behaviour_check.py: identical runs pass, a planted behaviour change is flagged, a metric that appears or
vanishes is flagged, day 1 and duplicate log lines are handled, and too little data is refused.

    python3 tools/ecology/test_behaviour_check.py
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import behaviour_check as bc  # noqa: E402

HEADER = "real_s,tick,species,bug_ticks,hunting,landed,eating,flee,attack,curious,windup,lunge,strikes,prey_claimed,corpses"


def write_run(root, name, hunting=100, noise=0, strikes=5, feed=8400 * 10, kills=7, extra_day1=False, dup=False, lunge=0):
    d = os.path.join(root, name)
    os.makedirs(d)
    rows = [HEADER]
    for w in range(1, 13):  # 12 windows of 5 s; the first 6 are inside the 30 s warm-up
        rows.append(f"{w * 5}.0,{w * 50},wasp_common,10000,{hunting + noise},50,20,0,0,0,0,{lunge},{strikes},{strikes},1")
    with open(os.path.join(d, "client_behaviour_A.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    log = []
    days = [1, 2, 3] if extra_day1 else [2, 3]
    for day in days:
        mult = 100 if day == 1 else 1  # day 1 must be skipped: a huge value there would swamp everything
        log.append(f'x {{"msg":"ECOSTATS day={day} sp=wasp_common pop=10 b_brood=0 b_nest={2 * mult} b_reproduce=0 '
                   f'b_reseed=0 b_spawn=0 d_oldage=0 d_starve=1 d_predation=0 d_cull=0 d_kill=0 d_catch=0 avg_sat=50.0"}}')
        log.append(f'x {{"msg":"BEHAVSTATS day={day} sp=wasp_common feed={feed * mult} breed=0 eggs=3 trip_home=9 '
                   f'trip_abandon=0 nest_defend=0 merge=0 split=0 player_hit=0"}}')
        log.append(f'x {{"msg":"PREDLOG day={day} pred=wasp_common prey=fly_common kills={kills * mult}"}}')
    if dup:
        log.append(log[-1])  # the same day's line twice must count once
    with open(os.path.join(d, "nakama.log"), "w") as f:
        f.write("\n".join(log) + "\n")
    return d


class BehaviourCheck(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="behcheck_")

    def base(self, n=5):
        return [write_run(self.root, f"base{i}", noise=(i % 3) - 1) for i in range(n)]

    def check(self, base, new, *extra):
        return bc.main(["--base", *base, "--new", *new, *extra])

    def test_same_behaviour_passes(self):
        b = self.base()
        n = [write_run(self.root, "new0"), write_run(self.root, "new1", noise=1)]
        self.assertEqual(self.check(b, n), 0)

    def test_planted_change_is_flagged(self):
        b = self.base()
        n = [write_run(self.root, "new0", hunting=130)]  # 30% more hunting
        self.assertEqual(self.check(b, n), 1)

    def test_server_change_is_flagged(self):
        b = self.base()
        n = [write_run(self.root, "new0", kills=12)]
        self.assertEqual(self.check(b, n), 1)

    def test_metric_appearing_is_flagged(self):
        b = self.base()
        n = [write_run(self.root, "new0", lunge=3)]  # lunging where there was none
        self.assertEqual(self.check(b, n), 1)

    def test_day_one_and_duplicates_are_ignored(self):
        b = self.base()
        n = [write_run(self.root, "new0", extra_day1=True, dup=True)]
        self.assertEqual(self.check(b, n), 0)

    def test_noise_floor_mode(self):
        self.assertEqual(bc.main(["--base", *self.base()]), 0)

    def test_too_few_base_runs(self):
        self.assertEqual(self.check(self.base(1), [write_run(self.root, "new0")]), 2)

    def test_run_without_data_is_refused(self):
        empty = os.path.join(self.root, "empty")
        os.makedirs(empty)
        self.assertEqual(self.check(self.base(), [empty]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
