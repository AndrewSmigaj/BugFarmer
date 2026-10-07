#!/usr/bin/env python3
"""Tests for behaviour_check.py: identical runs pass, a clear and sizeable change is flagged, a small change or a rare
event is not, a frequent metric that appears is flagged, day 1 and duplicate log lines are handled, and too little data
is refused. Paired by seed: a change hidden by large seed-to-seed differences is caught, noise and a change that goes
different ways on different seeds are not; a state's starts (not its bug-ticks) decide whether it is too rare. The pace
gate: groups whose client kept a different pace are not compared.

    python3 tools/ecology/test_behaviour_check.py
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import behaviour_check as bc  # noqa: E402

HEADER = "real_s,tick,species,bug_ticks,hunting,landed,eating,flee,attack,curious,windup,lunge,strikes,prey_claimed,corpses"
STARTS = ",hunting_starts,landed_starts,eating_starts,flee_starts,attack_starts,curious_starts,windup_starts,lunge_starts"


def write_run(root, name, hunting=100, noise=0, strikes=5, feed=8400 * 10, kills=7, extra_day1=False, dup=False, lunge=0,
              eggs=3, attack=0, attack_starts=None, pace=None):
    """attack_starts given: the file has the *_starts columns (hunting/landed/eating start 30 times a window, the
    attacks start attack_starts times in all, in the last window)."""
    d = os.path.join(root, name)
    os.makedirs(d)
    rows = [HEADER + (STARTS if attack_starts is not None else "")]
    for w in range(1, 13):  # 12 windows of 5 s; the first 6 are inside the 30 s warm-up
        row = f"{w * 5}.0,{w * 50},wasp_common,10000,{hunting + noise},50,20,0,{attack},0,0,{lunge},{strikes},{strikes},1"
        if attack_starts is not None:
            row += f",30,30,30,0,{attack_starts if w == 12 else 0},0,0,0"
        rows.append(row)
    with open(os.path.join(d, "client_behaviour_A.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")
    if pace is not None:  # client_perf.csv: 5 s windows of `pace` ticks per second
        perf = ["real_s,tick,swarms,bugs,ticks,frames"]
        perf += [f"{w * 5}.0,{int(w * 5 * pace)},10,100,{int(5 * pace)},300" for w in range(1, 13)]
        with open(os.path.join(d, "client_perf.csv"), "w") as f:
            f.write("\n".join(perf) + "\n")
    log = []
    days = [1, 2, 3] if extra_day1 else [2, 3]
    for day in days:
        mult = 100 if day == 1 else 1  # day 1 must be skipped: a huge value there would swamp everything
        log.append(f'x {{"msg":"ECOSTATS day={day} sp=wasp_common pop=10 b_brood=0 b_nest={2 * mult} b_reproduce=0 '
                   f'b_reseed=0 b_spawn=0 d_oldage=0 d_starve=1 d_predation=0 d_cull=0 d_kill=0 d_catch=0 avg_sat=50.0"}}')
        log.append(f'x {{"msg":"BEHAVSTATS day={day} sp=wasp_common feed={feed * mult} breed=0 eggs={eggs} trip_home=9 '
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
        n = [write_run(self.root, "new0", lunge=10)]  # frequent lunging where there was none (60 bug-ticks counted)
        self.assertEqual(self.check(b, n), 1)

    def test_rare_appearance_is_not_flagged(self):
        b = self.base()
        n = [write_run(self.root, "new0", lunge=1)]  # 6 bug-ticks of lunging: too rare to judge
        self.assertEqual(self.check(b, n), 0)

    def test_small_change_is_not_flagged(self):
        b = [write_run(self.root, f"base{i}", hunting=100 + (i % 3) - 1) for i in range(5)]
        n = [write_run(self.root, "new0", hunting=105), write_run(self.root, "new1", hunting=106)]  # +5-6%: clear but small
        self.assertEqual(self.check(b, n), 0)

    def test_rare_events_are_not_judged(self):
        # eggs 0 or 1 a day: too few to judge in either direction
        b = [write_run(self.root, f"base{i}", eggs=i % 2) for i in range(5)]
        n = [write_run(self.root, "new0", eggs=0)]
        self.assertEqual(self.check(b, n), 0)

    def test_day_one_and_duplicates_are_ignored(self):
        b = self.base()
        n = [write_run(self.root, "new0", extra_day1=True, dup=True)]
        self.assertEqual(self.check(b, n), 0)

    def test_noise_floor_mode(self):
        self.assertEqual(bc.main(["--base", *self.base()]), 0)

    def test_too_few_base_runs(self):
        self.assertEqual(self.check(self.base(1), [write_run(self.root, "new0")]), 2)

    # --- paired by seed (folders named *_seed<N>, as scaling_study.py names them)
    def seeded(self, label, hunting_of_seed, seeds=(1, 2, 3, 4, 5)):
        return [write_run(self.root, f"{label}_seed{s}", hunting=hunting_of_seed(s)) for s in seeds]

    def test_seed_pairing(self):
        self.assertEqual(bc.pairing(["a_seed1", "a_seed2", "a_seed3"], ["b_seed1", "b_seed2", "b_seed3"]), [1, 2, 3])
        self.assertIsNone(bc.pairing(["a_seed1", "a_seed2", "a_seed3"], ["b_seed1", "b_seed4", "b_seed2"]))  # 4 not in base
        self.assertIsNone(bc.pairing(["a_seed1", "a_seed2"], ["b_seed1", "b_seed2"]))  # too few seeds
        self.assertIsNone(bc.pairing(["base0", "base1", "base2"], ["new0"]))  # no seeds

    def test_paired_catches_a_change_hidden_by_seed_spread(self):
        # seeds differ a lot (150..350); the new build adds ~60 (24%) on every seed
        b = self.seeded("base", lambda s: 100 + 50 * s)
        n = self.seeded("new", lambda s: 160 + 50 * s + 2 * (s % 2))
        self.assertEqual(self.check(b, n), 1)
        self.assertEqual(self.check(b, n, "--unpaired"), 0)  # group means miss it: the seeds' spread swamps it

    def test_paired_noise_passes(self):
        b = self.seeded("base", lambda s: 100 + 50 * s)
        n = self.seeded("new", lambda s: 100 + 50 * s + (3 if s % 2 else -3))
        self.assertEqual(self.check(b, n), 0)

    def test_paired_change_must_go_the_same_way_on_every_seed(self):
        b = self.seeded("base", lambda s: 100 + 50 * s)
        n = self.seeded("new", lambda s: 100 + 50 * s + (60 if s < 5 else -10))  # up on four seeds, down on one
        self.assertEqual(self.check(b, n), 0)

    def test_starts_decide_rarity(self):
        # many bug-ticks of attacking (500 a window) but only one attack STARTED per run: too rare to judge, so its
        # vanishing in the new runs is not flagged; counted in bug-ticks it would have been
        b = [write_run(self.root, f"base{i}", noise=(i % 3) - 1, attack=500, attack_starts=1) for i in range(5)]
        n = [write_run(self.root, "new0", attack=0, attack_starts=0)]
        self.assertEqual(self.check(b, n), 0)
        b2 = [write_run(self.root, f"old{i}", noise=(i % 3) - 1, attack=500) for i in range(5)]  # no starts columns
        n2 = [write_run(self.root, "oldnew0", attack=0)]
        self.assertEqual(self.check(b2, n2), 1)

    def test_pace_gate(self):
        self.assertAlmostEqual(bc.client_pace(write_run(self.root, "p", pace=59.8), 30), 59.8, places=1)
        b = [write_run(self.root, f"base_seed{s}", hunting=100 + 50 * s, pace=59.8) for s in range(1, 6)]
        slow = [write_run(self.root, f"slow_seed{s}", hunting=100 + 50 * s, pace=58.8) for s in range(1, 6)]  # 1.7%
        self.assertEqual(self.check(b, slow), 2)  # not comparable, even though the behaviour is identical
        same = [write_run(self.root, f"same_seed{s}", hunting=100 + 50 * s, pace=59.9) for s in range(1, 6)]
        self.assertEqual(self.check(b, same), 0)

    def test_run_without_data_is_refused(self):
        empty = os.path.join(self.root, "empty")
        os.makedirs(empty)
        self.assertEqual(self.check(self.base(), [empty]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
