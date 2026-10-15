import copy
import unittest

from campusflow.search import search_tickets, sort_by_priority
from campusflow.tickets import ValidationError, create_ticket
from campusflow.workflow import assign_ticket, change_status, work_queue


def sample():
    t = []
    create_ticket(t, "Campus WiFi down", "Network", "high", 15)          # T001 critical open
    create_ticket(t, "Library WIFI slow", "Network", "low", 1)            # T002 low open
    create_ticket(t, "wifi dongle broken", "Hardware", "medium", 1)       # T003 medium open
    create_ticket(t, "Moodle login fails", "Software", "medium", 5)       # T004 medium open
    assign_ticket(t[1], "Ada"); change_status(t[1], "in_progress")        # T002 in_progress
    return t


def ids(tickets):
    return [t["id"] for t in tickets]


class SearchTests(unittest.TestCase):
    def test_title_search_ignores_case_and_matches_substring(self):
        self.assertEqual(ids(search_tickets(sample(), "wifi")), ["T001", "T002", "T003"])
        self.assertEqual(ids(search_tickets(sample(), "WIFI")), ["T001", "T002", "T003"])
        self.assertEqual(ids(search_tickets(sample(), "ibrary")), ["T002"])
        self.assertEqual(search_tickets(sample(), "wi-fi"), [])      # no fuzzy matching

    def test_combined_filters_use_and(self):
        t = sample()
        self.assertEqual(ids(search_tickets(t, "wifi", "network", "open")), ["T001"])
        self.assertEqual(ids(search_tickets(t, "wifi", "Network", "in progress")), ["T002"])
        self.assertEqual(ids(search_tickets(t, "wifi", "Network", "open", "low")), [])
        self.assertEqual(ids(search_tickets(t, "", "Network", "", "critical")), ["T001"])

    def test_empty_filters_mean_do_not_filter(self):
        t = sample()
        self.assertEqual(len(search_tickets(t)), 4)
        self.assertEqual(len(search_tickets(t, "", "", "", "")), 4)
        self.assertEqual(len(search_tickets(t, None, None, None, None)), 4)

    def test_invalid_filter_values_are_rejected(self):
        for kwargs in ({"category": "Printers"}, {"status": "closed"}, {"priority": "urgent"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                search_tickets(sample(), **kwargs)

    def test_search_never_modifies_tickets_and_returns_copies(self):
        t = sample()
        before = copy.deepcopy(t)
        results = search_tickets(t, "wifi")
        results[0]["title"] = "tampered"
        results[0]["notes"].append({"note_id": "N001"})
        self.assertEqual(t, before)

    def test_sort_by_priority_uses_numeric_id_for_ties(self):
        rows = [{"id": "T1000", "priority": "low"}, {"id": "T999", "priority": "low"},
                {"id": "T5", "priority": "critical"}]
        self.assertEqual(ids(sort_by_priority(rows)), ["T5", "T999", "T1000"])

    def test_original_work_queue_still_shows_only_open_tickets(self):
        t = sample()                                  # T002 is in_progress
        self.assertEqual(ids(work_queue(t)), ["T001", "T003", "T004"])   # both medium: earlier ID first
        self.assertEqual(ids(sort_by_priority(search_tickets(t, "wifi"))),
                         ["T001", "T003", "T002"])   # the separate view keeps in_progress

    # ---- bug-hunter test (written by Engineer A against Engineer B's module) ----
    def test_casefold_matches_what_lower_would_miss_and_blank_query_means_any(self):
        t = []
        create_ticket(t, "Straße closed sign", "Other", "low", 1)
        self.assertEqual(ids(search_tickets(t, "STRASSE")), ["T001"])   # lower() would miss this
        self.assertEqual(ids(search_tickets(t, "   ")), ["T001"])       # whitespace = no filter
        self.assertEqual(ids(search_tickets(t, "  closed  ")), ["T001"])


if __name__ == "__main__":
    unittest.main()
