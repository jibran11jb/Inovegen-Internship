import json, os, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import student_manager as sm


class Validation(unittest.TestCase):
    def test_id(self):
        self.assertEqual(sm.parse_id(" s001 "), "S001")
        for bad in ["", "ab", "has space", "way-too-long-id", "a/b"]:
            with self.assertRaises(ValueError): sm.parse_id(bad)

    def test_marks(self):
        self.assertEqual(sm.parse_marks("88.456"), 88.46)
        for bad in ["", "abc", "-1", "101", "nan", "inf"]:
            with self.assertRaises(ValueError): sm.parse_marks(bad)

    def test_name_course(self):
        self.assertEqual(sm.parse_name("  ali   raza "), "Ali Raza")
        for bad in ["", "123", "<script>"]:
            with self.assertRaises(ValueError): sm.parse_name(bad)
        with self.assertRaises(ValueError): sm.parse_course("   ")

    def test_menu(self):
        with self.assertRaises(ValueError): sm.parse_menu_choice("9", sm.MENU)
        self.assertEqual(sm.parse_menu_choice(" 3 ", sm.MENU), "3")

    def test_grade(self):
        self.assertEqual([sm.grade_for(m) for m in (100, 90, 89.99, 50, 49.9, 0)], list("AABEFF"))


class Storage(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(); self.path = os.path.join(self.dir, "s.json")

    def test_roundtrip(self):
        data = [{"id": "A001", "name": "Test User", "course": "CS", "marks": 80.0}]
        self.assertTrue(sm.save_students(data, self.path))
        self.assertEqual(sm.load_students(self.path), data)

    def test_missing_file(self):
        self.assertEqual(sm.load_students(self.path), [])

    def test_corrupt_file_backed_up(self):
        open(self.path, "w").write("{not json")
        self.assertEqual(sm.load_students(self.path), [])
        self.assertTrue(os.path.exists(self.path + ".corrupt"))

    def test_bad_and_duplicate_records_skipped(self):
        json.dump([{"id": "A001", "name": "Ok", "course": "CS", "marks": 50},
                   {"id": "A001", "name": "Dup", "course": "CS", "marks": 60},
                   {"id": "A002", "name": "Bad", "course": "CS", "marks": 500},
                   {"id": "A003"}, "junk"], open(self.path, "w"))
        self.assertEqual([s["id"] for s in sm.load_students(self.path)], ["A001"])

    def test_sample_file_is_valid(self):
        sample = os.path.join(os.path.dirname(__file__), "..", "students.json")
        self.assertEqual(len(sm.load_students(sample)), 8)


class Logic(unittest.TestCase):
    S = [{"id": "A001", "name": "Ann", "course": "CS", "marks": 90},
         {"id": "A002", "name": "Bob", "course": "Math", "marks": 60},
         {"id": "A003", "name": "Cy", "course": "CS", "marks": 90}]

    def test_summary(self):
        r = sm.compute_summary(self.S)
        self.assertEqual((r["count"], r["average"]), (3, 80.0))
        self.assertEqual(len(r["highest"]), 2); self.assertEqual(r["lowest"][0]["id"], "A002")
        self.assertIsNone(sm.compute_summary([]))

    def test_search(self):
        self.assertEqual(len(sm.search_students(self.S, "cs")), 2)
        self.assertEqual(sm.search_students(self.S, "a002")[0]["name"], "Bob")
        self.assertEqual(sm.search_students(self.S, "zzz"), [])


class CLI(unittest.TestCase):
    """Drive the real menu with scripted input; invalid entries must never crash it."""
    def run_cli(self, inputs):
        path = os.path.join(tempfile.mkdtemp(), "s.json")
        with mock.patch.object(sm, "DATA_FILE", path), mock.patch("builtins.input", side_effect=inputs):
            rc = sm.main()
        return rc, path

    def test_full_flow_with_bad_input(self):
        rc, path = self.run_cli([
            "x", "", "99",                                            # invalid menu choices
            "1", "s1", "S001", "Ann Lee", "CS", "abc", "150", "88",   # bad id, bad marks, then ok
            "1", "S001", "cancel",                                    # duplicate id -> cancel
            "1", "S002", "Bob", "Math", "60",
            "4", "S001", "", "", "95",                                # update marks only
            "3", "bob", "6",
            "5", "S002", "no", "5", "S002", "yes",                    # decline, then confirm delete
            "5", "NOPE1", "2", "0"])
        self.assertEqual(rc, 0)
        with open(path) as f:
            self.assertEqual(json.load(f), [{"id": "S001", "name": "Ann Lee", "course": "CS", "marks": 95.0}])

    def test_eof_and_ctrl_c_do_not_crash(self):
        for exc in (EOFError, KeyboardInterrupt):
            rc, _ = self.run_cli(exc)
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
