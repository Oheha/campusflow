import unittest

from campusflow.search import search_tickets, sort_search_results
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status


class SearchTests(unittest.TestCase):

    def setUp(self):
        self.tickets = []

        create_ticket(
            self.tickets,
            "Wi-Fi connection failure",
            "Network",
            "high",
            15,
        )

        create_ticket(
            self.tickets,
            "Laptop screen broken",
            "Hardware",
            "low",
            1,
        )

        create_ticket(
            self.tickets,
            "Wi-Fi access point issue",
            "Network",
            "high",
            1,
        )

        create_ticket(
            self.tickets,
            "Software installation problem",
            "Software",
            "medium",
            3,
        )

        assign_ticket(self.tickets[2], "Mentor A")
        change_status(self.tickets[2], "in_progress")

    def test_title_search_ignores_case(self):
        results = search_tickets(self.tickets, title="WI-FI")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001", "T003"],
        )

    def test_title_search_matches_substrings(self):
        results = search_tickets(self.tickets, title="connection")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001"],
        )

    def test_combined_filters_use_and(self):
        results = search_tickets(
            self.tickets,
            title="wi-fi",
            category="network",
            status="open",
            priority="critical",
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001"],
        )

    def test_empty_filters_return_all_tickets(self):
        results = search_tickets(self.tickets)

        self.assertEqual(len(results), 4)

    def test_invalid_filter_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, category="Printers")

    def test_search_does_not_modify_tickets(self):
        before = [dict(ticket) for ticket in self.tickets]

        search_tickets(
            self.tickets,
            title="wifi",
            category="Network",
        )

        self.assertEqual(self.tickets, before)

    def test_search_sort_uses_priority_and_numeric_id(self):
        results = sort_search_results(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001", "T003", "T004", "T002"],
        )


if __name__ == "__main__":
    unittest.main()