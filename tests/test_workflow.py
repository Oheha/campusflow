import unittest

from campusflow.tickets import ValidationError, create_ticket, find_ticket
from campusflow.workflow import assign_ticket, change_status, reopen_ticket, work_queue


def make():
    tickets = []
    create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
    return tickets, tickets[0]


class WorkflowTests(unittest.TestCase):
    def test_unassigned_cannot_start(self):
        _, t = make()
        with self.assertRaises(ValidationError):
            change_status(t, "in_progress")
        self.assertEqual(t["status"], "open")

    def test_full_lifecycle(self):
        _, t = make()
        assign_ticket(t, "  Ada ")
        self.assertEqual(t["assigned_to"], "Ada")
        change_status(t, "in_progress")
        change_status(t, "RESOLVED")
        self.assertEqual(t["status"], "resolved")

    def test_invalid_transitions_rejected(self):
        _, t = make()
        for bad in ("resolved", "open", "closed"):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                change_status(t, bad)
        self.assertEqual(t["status"], "open")

    def test_resolved_is_locked_until_reopened(self):
        _, t = make()
        assign_ticket(t, "Ada")
        change_status(t, "in_progress")
        change_status(t, "resolved")
        with self.assertRaises(ValidationError):
            assign_ticket(t, "Bob")
        with self.assertRaises(ValidationError):
            change_status(t, "open")
        self.assertEqual(t["assigned_to"], "Ada")
        reopen_ticket(t)
        self.assertEqual(t["status"], "open")
        assign_ticket(t, "Bob")
        self.assertEqual(t["assigned_to"], "Bob")

    def test_reopen_only_for_resolved(self):
        _, t = make()
        with self.assertRaises(ValidationError):
            reopen_ticket(t)

    def test_blank_staff_name_and_unknown_id_rejected(self):
        tickets, t = make()
        with self.assertRaises(ValidationError):
            assign_ticket(t, "   ")
        self.assertIsNone(t["assigned_to"])
        with self.assertRaises(ValidationError):
            find_ticket(tickets, "T999")
        self.assertIs(find_ticket(tickets, " t001 "), t)


class QueueTests(unittest.TestCase):
    def test_order_priority_then_id(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)       # T001 low
        create_ticket(tickets, "b", "Other", "high", 20)     # T002 critical
        create_ticket(tickets, "c", "Other", "medium", 1)    # T003 medium
        create_ticket(tickets, "d", "Other", "high", 20)     # T004 critical
        create_ticket(tickets, "e", "Other", "high", 1)      # T005 high
        order = [t["id"] for t in work_queue(tickets)]
        self.assertEqual(order, ["T002", "T004", "T005", "T003", "T001"])

    def test_numeric_tie_break_past_999(self):
        tickets = [
            {"id": "T1000", "priority": "low", "status": "open"},
            {"id": "T999", "priority": "low", "status": "open"},
        ]
        self.assertEqual([t["id"] for t in work_queue(tickets)], ["T999", "T1000"])

    def test_queue_excludes_non_open(self):
        tickets, t = make()
        assign_ticket(t, "Ada")
        change_status(t, "in_progress")
        self.assertEqual(work_queue(tickets), [])


if __name__ == "__main__":
    unittest.main()
