import unittest

from campusflow.reports import build_report, format_report
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status


class ReportTests(unittest.TestCase):
    def test_zero_tickets(self):
        r = build_report([])
        self.assertEqual(r["total"], 0)
        self.assertTrue(all(v == 0 for v in r["by_status"].values()))
        self.assertTrue(all(v == 0 for v in r["by_priority"].values()))
        self.assertIn("Total tickets: 0", format_report(r))

    def test_counts(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "high", 20)
        create_ticket(tickets, "b", "Other", "low", 1)
        create_ticket(tickets, "c", "Other", "low", 1)
        assign_ticket(tickets[1], "Ada")
        change_status(tickets[1], "in_progress")
        r = build_report(tickets)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["by_status"], {"open": 2, "in_progress": 1, "resolved": 0})
        self.assertEqual(r["by_priority"]["critical"], 1)
        self.assertEqual(r["by_priority"]["low"], 2)


if __name__ == "__main__":
    unittest.main()
