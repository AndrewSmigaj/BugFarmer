#!/usr/bin/env python3
"""The review app's builder refuses bad data (docs/plans/review-app.md, Test plan).

    python3 tools/gdd/tests/test_build_app.py

The real data must build cleanly; then each check gets a planted fault in a temporary copy and must refuse it with
its own message. Nothing in the repo is changed (copies live in a temporary folder).
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/gdd"))
import build_app as ba  # noqa: E402
import build_page as bp  # noqa: E402

REAL = {"REG": ba.REG, "GDD": ba.GDD, "APP": ba.APP, "OUT_DIR": ba.OUT_DIR, "STORED_GROUPS": list(ba.STORED_GROUPS)}


def read_jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]


def write_jsonl(p, rows):
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


class BuilderRefusesBadData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sections = [bp.parse_section(ba.GDD / n) for n in bp.review_order()]
        cls.zones = read_jsonl(ba.REG / "zones.jsonl")
        cls.bugs = read_jsonl(ba.REG / "bugs.jsonl")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="bf_build_app_"))

    def tearDown(self):
        for k, v in REAL.items():
            setattr(ba, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -------------------------------------------------------------- helpers
    def registry_errors(self, mutate):
        """Load the registry from a copy, after mutate(zones, bugs) edits it."""
        reg = self.tmp / "data"
        shutil.copytree(REAL["REG"], reg)
        zones, bugs = copy.deepcopy(self.zones), copy.deepcopy(self.bugs)
        mutate(zones, bugs)
        write_jsonl(reg / "zones.jsonl", zones)
        write_jsonl(reg / "bugs.jsonl", bugs)
        ba.REG = reg
        P = ba.Problems()
        ba.load_registry(P, self.sections)
        return P.errors

    def assertRefused(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), f"expected an error containing {needle!r}; got {errors[:6]}")

    def zone(self, zones, zid):
        return next(z for z in zones if z["id"] == zid)

    def bug(self, bugs, bid):
        return next(b for b in bugs if b["id"] == bid)

    def full_build(self, gdd=None, app=None):
        ba.OUT_DIR = self.tmp / "out"
        if gdd:
            ba.GDD = gdd
        if app:
            ba.APP = app
        return ba.build()

    # -------------------------------------------------------------- the real data is clean
    def test_real_registry_is_clean(self):
        self.assertEqual(self.registry_errors(lambda z, b: None), [])

    def test_real_build_is_clean(self):
        self.assertEqual(self.full_build(), 0)
        self.assertTrue((self.tmp / "out" / "review_app.html").exists())

    # -------------------------------------------------------------- zones
    def test_missing_zone(self):
        self.assertRefused(self.registry_errors(lambda z, b: z.pop()), "expected 20")

    def test_duplicate_zone(self):
        self.assertRefused(self.registry_errors(lambda z, b: z.append(copy.deepcopy(z[0]))), "duplicate zone ids")

    def test_zone_id_not_a_storage_key(self):
        def m(z, b):
            z[0]["id"] = "bad/zone"
        self.assertRefused(self.registry_errors(m), "can't be a storage key")

    def test_unknown_ring(self):
        def m(z, b):
            z[0]["ring"] = "outer"
        self.assertRefused(self.registry_errors(m), "ring 'outer'")

    def test_neighbour_not_next_door(self):
        def m(z, b):
            far = next(x for x in z if abs(x["row"] - self.zone(z, "village")["row"]) > 1)
            self.zone(z, "village")["neighbours"]["north"] = far["id"]
        self.assertRefused(self.registry_errors(m), "is not next door")

    def test_one_way_link(self):
        def m(z, b):
            v = self.zone(z, "village")
            d, n = next((d, n) for d, n in v["neighbours"].items() if n)
            other = self.zone(z, n)
            other["neighbours"] = {k: (None if x == "village" else x) for k, x in other["neighbours"].items()}
        self.assertRefused(self.registry_errors(m), "the link isn't returned")

    def test_shared_grid_square(self):
        def m(z, b):
            z[1]["row"], z[1]["col"] = z[0]["row"], z[0]["col"]
        self.assertRefused(self.registry_errors(m), "share grid square")

    def test_built_zone_in_the_wrong_square(self):
        def m(z, b):
            v = self.zone(z, "village")
            v["row"] += 1
        self.assertRefused(self.registry_errors(m), "registry says")

    # -------------------------------------------------------------- bugs
    def test_approval_stored_in_data(self):
        def m(z, b):
            b[0]["approved"] = True
        self.assertRefused(self.registry_errors(m), "approvals live in the app's storage")

    def test_unknown_family(self):
        def m(z, b):
            b[0]["family"] = "bats"
        self.assertRefused(self.registry_errors(m), "not in the family order")

    def test_unknown_species(self):
        def m(z, b):
            b[0]["species"] = b[0].get("species", []) + ["zz_not_a_species"]
        self.assertRefused(self.registry_errors(m), "not in species.json")

    def test_comes_in_from_a_non_neighbour(self):
        def m(z, b):
            bug = next(x for x in b if any(e["how"] == "comes_in" for e in x.get("zones", [])))
            e = next(e for e in bug["zones"] if e["how"] == "comes_in")
            zid = {x["id"]: x for x in z}
            nb = set(zid[e["zone"]]["neighbours"].values())
            e["from"] = [next(x["id"] for x in z if x["id"] not in nb and x["id"] != e["zone"])]
        self.assertRefused(self.registry_errors(m), "which isn't a neighbour")

    def test_spawns_nowhere(self):
        def m(z, b):
            bug = next(x for x in b if x.get("zones"))
            for e in bug["zones"]:
                e["how"] = "comes_in"
                e["from"] = [n for n in self.zone(z, e["zone"])["neighbours"].values() if n][:1]
        self.assertRefused(self.registry_errors(m), "it spawns nowhere")

    def test_bug_dropped_breaks_the_accounting(self):
        self.assertRefused(self.registry_errors(lambda z, b: b.pop(0)), "accounting: lineup row")

    def test_species_claimed_twice(self):
        def m(z, b):
            with_sp = [x for x in b if x.get("species")]
            with_sp[1]["species"] = with_sp[1]["species"] + [with_sp[0]["species"][0]]
        self.assertRefused(self.registry_errors(m), "belongs to 2 bugs")

    def test_bug_with_no_zone_and_no_note(self):
        def m(z, b):
            b[0]["zones"] = []
            b[0].pop("zones_note", None)
        self.assertRefused(self.registry_errors(m), "no zone, and no note")

    # -------------------------------------------------------------- explanation pages
    def test_diagram_with_a_script_is_refused(self):
        P = ba.Problems()
        ba.explain_body(["```svg", '<svg viewBox="0 0 1 1"><script>alert(1)</script></svg>', "```"], "x.md", P)
        self.assertRefused(P.errors, "may not hold scripts")

    def test_diagram_with_an_event_handler_is_refused(self):
        P = ba.Problems()
        ba.explain_body(["```svg", '<svg viewBox="0 0 1 1"><rect onclick="x()"/></svg>', "```"], "x.md", P)
        self.assertRefused(P.errors, "may not hold scripts")

    def test_diagram_must_be_one_svg(self):
        P = ba.Problems()
        ba.explain_body(["```svg", "<div>not a diagram</div>", "```"], "x.md", P)
        self.assertRefused(P.errors, "must hold one <svg>")

    # -------------------------------------------------------------- the whole build
    def test_lost_mark_group_is_refused(self):
        ba.STORED_GROUPS = REAL["STORED_GROUPS"] + ["zz_removed_group"]
        self.assertEqual(self.full_build(), 1)
        report = (self.tmp / "out" / "review_app_report.txt").read_text()
        self.assertIn("GROUPS lost 'zz_removed_group'", report)
        self.assertFalse((self.tmp / "out" / "review_app.html").exists(), "a refused build must not write the page")

    def test_duplicate_gdd_key_is_refused(self):
        gdd = self.tmp / "gdd"
        shutil.copytree(REAL["GDD"], gdd, ignore=shutil.ignore_patterns("_build"))
        f = gdd / "04_ecology.md"
        text = f.read_text(encoding="utf-8")
        keys = [l for l in text.split("\n") if l.startswith("<!-- key:")]
        self.assertGreaterEqual(len(keys), 2)
        f.write_text(text.replace(keys[1], keys[0], 1), encoding="utf-8")
        self.assertEqual(self.full_build(gdd=gdd), 1)
        self.assertIn("is used 2 times", (self.tmp / "out" / "review_app_report.txt").read_text())

    def test_shell_without_a_slot_is_refused(self):
        app = self.tmp / "app"
        shutil.copytree(REAL["APP"], app)
        (app / "shell.html").write_text((app / "shell.html").read_text().replace("/*__MAPS__*/", ""), encoding="utf-8")
        self.assertEqual(self.full_build(app=app), 1)
        self.assertIn("has no /*__MAPS__*/ slot", (self.tmp / "out" / "review_app_report.txt").read_text())

    def test_page_with_its_own_body_is_refused(self):
        app = self.tmp / "app"
        shutil.copytree(REAL["APP"], app)
        (app / "shell.html").write_text((app / "shell.html").read_text() + "\n<body></body>\n", encoding="utf-8")
        self.assertEqual(self.full_build(app=app), 1)
        self.assertIn("must not contain its own <body>", (self.tmp / "out" / "review_app_report.txt").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=1)
