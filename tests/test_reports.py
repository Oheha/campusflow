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


# ---------------- CampusFlow Next additions (Engineer B) ----------------
from campusflow.workflow import reopen_ticket   # noqa: E402


def _fixture():
    t = []
    create_ticket(t, "a", "Network", "high", 20)      # T001 critical
    create_ticket(t, "b", "Hardware", "low", 1)       # T002 low
    create_ticket(t, "c", "Network", "medium", 1)     # T003 medium
    create_ticket(t, "d", "Other", "low", 3)          # T004 medium
    return t


class NextReportTests(unittest.TestCase):
    def test_empty_report_has_zero_percent_and_no_crash(self):
        r = build_report([])
        self.assertEqual((r["total"], r["unresolved"], r["resolved"]), (0, 0, 0))
        self.assertEqual(r["resolution_percent"], 0.0)
        self.assertIn("Resolution rate: 0.0%", format_report(r))
        self.assertEqual(sum(r["by_category"].values()), 0)

    def test_counts_follow_current_status_after_resolve_and_reopen(self):
        t = _fixture()
        for i in (0, 1):
            assign_ticket(t[i], "Ada"); change_status(t[i], "in_progress"); change_status(t[i], "resolved")
        assign_ticket(t[2], "Bob"); change_status(t[2], "in_progress")
        r = build_report(t)
        self.assertEqual(r["by_status"], {"open": 1, "in_progress": 1, "resolved": 2})
        self.assertEqual((r["unresolved"], r["resolved"], r["resolution_percent"]), (2, 2, 50.0))
        reopen_ticket(t[0])                                  # counted by CURRENT status
        r = build_report(t)
        self.assertEqual(r["by_status"], {"open": 2, "in_progress": 1, "resolved": 1})
        self.assertEqual(r["resolution_percent"], 25.0)

    def test_category_priority_and_status_counts_each_sum_to_total(self):
        r = build_report(_fixture())
        self.assertEqual(r["by_category"], {"Network": 2, "Hardware": 1, "Software": 0, "Other": 1})
        for key in ("by_status", "by_priority", "by_category"):
            with self.subTest(key=key):
                self.assertEqual(sum(r[key].values()), r["total"])        # nothing double-counted
        self.assertEqual(r["unresolved"] + r["resolved"], r["total"])

    def test_resolution_percent_is_rounded_to_one_decimal(self):
        t = _fixture()[:3]
        assign_ticket(t[0], "Ada"); change_status(t[0], "in_progress"); change_status(t[0], "resolved")
        self.assertEqual(build_report(t)["resolution_percent"], 33.3)


if __name__ == "__main__":
    unittest.main()
