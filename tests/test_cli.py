import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.storage import load_tickets


def drive(path, answers):
    it = iter(answers)
    out = []
    code = run(path, input_fn=lambda prompt="": next(it), output_fn=out.append)
    return code, "\n".join(out)


class CliTests(unittest.TestCase):
    def test_end_to_end_with_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "tickets.json")
            code, out = drive(path, [
                "1", "Campus Wi-Fi is down", "network", "HIGH", "abc", "15",  # bad users, retry
                "5", "T001", "in_progress",                                    # rejected: unassigned
                "4", "T001", "Ada",
                "5", "T001", "in_progress",
                "0"])
            self.assertEqual(code, 0)
            self.assertIn("priority critical", out)
            self.assertIn("positive whole number", out)
            self.assertIn("Assign the ticket", out)
            tickets = load_tickets(path)
            self.assertEqual(tickets[0]["status"], "in_progress")
            self.assertEqual(tickets[0]["assigned_to"], "Ada")
            code, out = drive(path, ["2", "8", "0"])
            self.assertIn("T001", out)
            self.assertIn("Total tickets: 1", out)

    def test_malformed_file_blocks_startup_without_erasing(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "tickets.json")
            with open(path, "w") as fh:
                fh.write("oops")
            code, out = drive(path, [])
            self.assertEqual(code, 1)
            self.assertIn("malformed JSON", out)
            with open(path) as fh:
                self.assertEqual(fh.read(), "oops")

    def test_invalid_menu_option_keeps_running(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = drive(os.path.join(d, "t.json"), ["99", "7", "0"])
            self.assertEqual(code, 0)
            self.assertIn("Invalid option", out)
            self.assertIn("work queue is empty", out)


if __name__ == "__main__":
    unittest.main()


# ---------------- CampusFlow Next additions (Engineer B) ----------------
def drive_lines(path, answers):
    it = iter(answers)
    out = []
    code = run(path, input_fn=lambda prompt="": next(it), output_fn=out.append)
    return code, out


class NextCliTests(unittest.TestCase):
    def test_notes_flow_through_the_menu(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.json")
            code, out = drive_lines(path, [
                "1", "Campus Wi-Fi is down", "network", "high", "15",
                "9", "T001", "Mentor A", "Wi-Fi router reboot attempted",
                "9", "T001", "Mentor B", "Investigating switch ports",
                "4", "T001", "Ada", "5", "T001", "in_progress", "5", "T001", "resolved",
                "9", "T001",                                     # refused before any prompt
                "6", "T001",
                "9", "T001", "Mentor A", "Router replaced after test",
                "10", "T001", "0"])
            text = "\n".join(out)
            self.assertEqual(code, 0)
            for expected in ("Added N001", "Added N002", "Added N003",
                             "Notes can only be added to open or in_progress tickets"):
                self.assertIn(expected, text)
            rows = [l for l in out if l[:4] in ("N001", "N002", "N003") and ":" in l]
            self.assertEqual([r[:4] for r in rows], ["N001", "N002", "N003"])

    def test_search_menu_reprompts_on_invalid_filter_and_combines_filters(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.json")
            code, out = drive_lines(path, [
                "1", "Campus WiFi down", "network", "high", "15",
                "1", "WiFi in library", "hardware", "low", "1",
                "11", "WIFI", "printers", "network", "", "", "n", "0"])
            self.assertEqual(code, 0)
            self.assertIn("Error: Category must be one of", "\n".join(out))
            self.assertTrue(any(l.startswith("T001") for l in out))
            self.assertFalse(any(l.startswith("T002") for l in out))

    def test_end_of_input_ends_cleanly_without_traceback(self):
        def eof(prompt=""):
            raise EOFError
        with tempfile.TemporaryDirectory() as d:
            out = []
            self.assertEqual(run(os.path.join(d, "t.json"), input_fn=eof, output_fn=out.append), 0)
            self.assertIn("Goodbye", "\n".join(out))

    def test_menu_reload_rejects_a_bad_file_and_keeps_memory(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.json")
            steps = iter(["1", "Wi-Fi down", "network", "high", "15", "13", "2", "0"])
            out = []

            def inp(prompt=""):
                answer = next(steps)
                if answer == "13":
                    with open(path, "w") as fh:
                        fh.write("oops")
                return answer
            run(path, input_fn=inp, output_fn=out.append)
            text = "\n".join(out)
            self.assertIn("malformed JSON", text)
            self.assertTrue(any(l.startswith("T001") for l in out))      # still in memory
            with open(path) as fh:
                self.assertEqual(fh.read(), "oops")                       # never overwritten

    def test_understanding_check_runs_from_the_menu_and_saves_notes(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.json")
            code, out = drive_lines(path, [
                "12", "Ada", "B", "validation runs first so data stays intact", "C", "B", "C", "C",
                "a duplicate ID makes tickets ambiguous", "B", "0"])
            self.assertIn("Score: 6/6", "\n".join(out))
            self.assertTrue(os.path.exists(os.path.join(d, "learning-notes.txt")))
