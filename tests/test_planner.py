"""Behavior and failure-mode tests; run with unittest discovery."""

from contextlib import redirect_stderr, redirect_stdout
from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest

from cli import main
from studyplanner.planner import make_plan, parse_date
from studyplanner.storage import load


def task(number, due, minutes, done=False):
    return {"id": number, "course": "CS101", "title": f"Task {number}",
            "due": due, "minutes": minutes, "done": done}


class PlannerTests(unittest.TestCase):
    def test_deadline_priority_split_capacity_and_no_mutation(self):
        tasks = [task(1, "2026-10-14", 100), task(2, "2026-10-12", 80)]
        original = json.dumps(tasks)
        sessions, missing = make_plan(tasks, date(2026, 10, 11), 3, 60)
        self.assertEqual([(s["id"], s["minutes"]) for s in sessions],
                         [(2, 60), (1, 60), (1, 40)])
        self.assertEqual(missing[0]["minutes"], 20)
        self.assertIn("insufficient capacity", missing[0]["reason"])
        for session in sessions:
            self.assertLess(session["date"], next(t["due"] for t in tasks if t["id"] == session["id"]))
        self.assertEqual(json.dumps(tasks), original)

    def test_today_deadline_and_completed_tasks(self):
        sessions, missing = make_plan([task(1, "2026-10-11", 30),
                                      task(2, "2026-10-13", 40, True)],
                                     date(2026, 10, 11), 2, 60)
        self.assertEqual(sessions, [])
        self.assertEqual([item["id"] for item in missing], [1])
        self.assertIn("deadline reached", missing[0]["reason"])

    def test_short_horizon_does_not_claim_deadline_is_impossible(self):
        _, missing = make_plan([task(1, "2026-11-01", 100)], date(2026, 10, 11), 1, 30)
        self.assertIn("extend the plan", missing[0]["reason"])

    def test_empty_and_equal_deadlines(self):
        self.assertEqual(make_plan([], date(2026, 10, 11), 1, 60), ([], []))
        sessions, _ = make_plan([task(2, "2026-10-13", 30), task(1, "2026-10-13", 30)],
                                date(2026, 10, 11), 1, 60)
        self.assertEqual([s["id"] for s in sessions], [1, 2])

    def test_invalid_dates_and_bounds(self):
        for value in ("2026-02-30", "20261011", "bad", None):
            with self.assertRaises(ValueError):
                parse_date(value)
        for days, minutes in ((0, 30), (367, 30), (1, 1441), (1, -1)):
            with self.assertRaises(ValueError):
                make_plan([], date(2026, 10, 11), days, minutes)
        with self.assertRaises(ValueError):
            make_plan([], date.max, 2, 60)


class CLITests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = Path(self.directory.name) / "tasks.json"

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main(["--data", str(self.database), *args])
        return status, out.getvalue(), err.getvalue()

    def add_task(self):
        return self.invoke("add", "--course", "CS101", "--title", "Project",
                           "--due", "2026-10-14", "--minutes", "90")

    def test_full_lifecycle_and_export(self):
        self.assertEqual(self.add_task()[0], 0)
        self.assertIn("#1", self.invoke("list")[1])
        report = Path(self.directory.name) / "plan.txt"
        status, output, _ = self.invoke("plan", "--start", "2026-10-11", "--output", str(report))
        self.assertEqual(status, 0)
        self.assertEqual(report.read_text(), output)
        self.assertEqual(self.invoke("done", "--id", "1")[0], 0)
        self.assertTrue(load(self.database)["tasks"][0]["done"])
        self.assertEqual(self.invoke("reopen", "--id", "1")[0], 0)
        self.assertFalse(load(self.database)["tasks"][0]["done"])
        self.assertEqual(self.invoke("done", "--id", "999")[0], 1)

    def test_corrupt_database_is_preserved(self):
        for contents in ("{broken", '{"version":1,"next_id":1,"tasks":[{}]}'):
            self.database.write_text(contents)
            self.assertEqual(self.add_task()[0], 1)
            self.assertEqual(self.database.read_text(), contents)

    def test_export_does_not_overwrite_files(self):
        self.add_task()
        original = self.database.read_bytes()
        self.assertEqual(self.invoke("plan", "--output", str(self.database))[0], 1)
        self.assertEqual(self.database.read_bytes(), original)
        report = Path(self.directory.name) / "existing.txt"
        report.write_text("Keep me")
        self.assertEqual(self.invoke("plan", "--output", str(report))[0], 1)
        self.assertEqual(report.read_text(), "Keep me")

    def test_bad_input_does_not_create_database(self):
        self.assertEqual(self.invoke("add", "--course", " ", "--title", "Task",
                                     "--due", "2026-10-14", "--minutes", "30")[0], 1)
        self.assertFalse(self.database.exists())
        with self.assertRaises(SystemExit) as caught:
            self.invoke("add", "--course", "CS", "--title", "Task",
                        "--due", "2026-10-14", "--minutes", "-1")
        self.assertEqual(caught.exception.code, 2)

    def test_schema_rejects_duplicate_ids_and_wrong_types(self):
        for tasks in ([task(1, "2026-10-14", 20)] * 2,
                      [task(1, "2026-10-14", True)],
                      [task(1, "2026-10-14", 20, "false")]):
            self.database.write_text(json.dumps({"version": 1, "next_id": 2, "tasks": tasks}))
            self.assertEqual(self.invoke("list")[0], 1)


if __name__ == "__main__":
    unittest.main()
