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
