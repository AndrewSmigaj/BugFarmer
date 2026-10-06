#!/usr/bin/env python3
"""Tests for run_config.py's leftover guard: a run that never put the data back (a crash, a PC restart, --keep) makes
the next run refuse to start, a run still going is named as such, and --restore-leftover puts every file back byte
for byte and clears the guard. Uses a temporary folder; the real data is never touched.

    python3 tools/ecology/test_run_config_guard.py
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_config as rc  # noqa: E402

DEAD_PID = 2 ** 22 + 12345  # above Linux's default pid limit, so no process has it


def read(path):
    with open(path) as f:
        return f.read()


class LeftoverGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rcguard_")
        self.old_leftover = rc.LEFTOVER
        rc.LEFTOVER = os.path.join(self.tmp, "scratch", "run_config_unrestored.pickle")
        self.file = os.path.join(self.tmp, "species.json")
        self.zone = os.path.join(self.tmp, "zones", "bench_x")
        os.makedirs(self.zone)
        with open(self.file, "w") as f:
            f.write('{"fly": 1}')
        with open(os.path.join(self.zone, "zone.json"), "w") as f:
            f.write('{"seed": 0}')

    def tearDown(self):
        rc.LEFTOVER = self.old_leftover

    def start_run(self, pid=DEAD_PID):
        """What run_config does before changing anything: the before-copy, saved."""
        snap = rc.snapshot([self.file, self.zone])
        rc.record_leftover(snap, "s10_test", "bench_x")
        if pid is not None:  # pretend the run was another process
            import pickle
            with open(rc.LEFTOVER, "rb") as f:
                left = pickle.load(f)
            left["pid"] = pid
            with open(rc.LEFTOVER, "wb") as f:
                pickle.dump(left, f)
        # the run changes the data...
        with open(self.file, "w") as f:
            f.write('{"fly": 999}')
        with open(os.path.join(self.zone, "zone.json"), "w") as f:
            f.write('{"seed": 3, "hold_population": true}')

    def test_clean_state_lets_a_run_start(self):
        self.assertIsNone(rc.check_leftover())

    def test_interrupted_run_blocks_the_next(self):
        self.start_run()  # ...and is interrupted: no restore, no clear
        with self.assertRaises(SystemExit) as e:
            rc.check_leftover()
        self.assertIn("never put the data back", str(e.exception))
        self.assertIn("--restore-leftover", str(e.exception))

    def test_a_run_still_going_is_named(self):
        self.start_run(pid=os.getpid())  # this test's own command line contains "run_config"
        with self.assertRaises(SystemExit) as e:
            rc.check_leftover()
        self.assertIn("still running", str(e.exception))

    def test_restore_leftover_puts_every_file_back(self):
        self.start_run()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(rc.restore_leftover(), 0)
        self.assertEqual(read(self.file), '{"fly": 1}')
        self.assertEqual(read(os.path.join(self.zone, "zone.json")), '{"seed": 0}')
        self.assertFalse(os.path.exists(rc.LEFTOVER))
        self.assertIsNone(rc.check_leftover())

    def test_normal_finish_clears_the_guard(self):
        snap = rc.snapshot([self.file, self.zone])
        rc.record_leftover(snap, "s10_test", "bench_x")
        rc.restore(snap)
        rc.clear_leftover()  # what the finally does after restoring
        self.assertIsNone(rc.check_leftover())

    def test_restore_with_nothing_left_over(self):
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(rc.restore_leftover(), 0)
        self.assertIn("nothing to restore", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
