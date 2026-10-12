import unittest

from campusflow.tickets import (ValidationError, calculate_priority, create_ticket,
                                next_ticket_id, normalize_category, parse_affected_users)


class PriorityTests(unittest.TestCase):
    def test_rule_examples(self):
        cases = [
            ("high", 15, "critical"), ("high", 10, "critical"),
            ("high", 9, "high"), ("high", 1, "high"),
            ("low", 10, "high"), ("medium", 25, "high"),
            ("medium", 1, "medium"), ("low", 3, "medium"), ("low", 9, "medium"),
            ("low", 2, "low"), ("low", 1, "low"),
        ]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)


class ValidationTests(unittest.TestCase):
    def test_bad_affected_users_rejected(self):
        for bad in (0, -3, "0", "-2", "3.5", 3.0, "abc", "", None, True):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                parse_affected_users(bad)

    def test_good_affected_users_accepted(self):
        self.assertEqual(parse_affected_users(" 12 "), 12)
        self.assertEqual(parse_affected_users(4), 4)

    def test_case_variations_normalized(self):
        self.assertEqual(normalize_category("  nEtWoRk "), "Network")
        with self.assertRaises(ValidationError):
            normalize_category("Printers")


class CreateTests(unittest.TestCase):
    def test_ids_are_sequential_and_fields_set(self):
        tickets = []
        a = create_ticket(tickets, "Campus Wi-Fi is down", "network", "HIGH", "15")
        b = create_ticket(tickets, "Laptop screen cracked", "Hardware", "low", 1)
        self.assertEqual((a["id"], b["id"]), ("T001", "T002"))
        self.assertEqual(a["priority"], "critical")
        self.assertEqual(a["status"], "open")
        self.assertIsNone(a["assigned_to"])

    def test_invalid_input_does_not_change_tickets(self):
        tickets = []
        create_ticket(tickets, "Ok", "Other", "low", 1)
        before = [dict(t) for t in tickets]
        for args in (("  ", "Other", "low", 1), ("x", "Bad", "low", 1),
                     ("x", "Other", "urgent", 1), ("x", "Other", "low", 0)):
            with self.assertRaises(ValidationError):
                create_ticket(tickets, *args)
        self.assertEqual(tickets, before)

    def test_next_id_uses_highest_existing(self):
        tickets = [{"id": "T001"}, {"id": "T007"}]
        self.assertEqual(next_ticket_id(tickets), "T008")


if __name__ == "__main__":
    unittest.main()
