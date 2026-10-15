import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "data", "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_missing_file_is_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_round_trip(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
        save_tickets(self.path, tickets)
        self.assertEqual(load_tickets(self.path), tickets)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_malformed_json_raises_and_file_untouched(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fh:
            fh.write("{ not json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path) as fh:
            self.assertEqual(fh.read(), "{ not json")

    def test_wrong_structure_raises(self):
        os.makedirs(os.path.dirname(self.path))
        for payload in ({"a": 1}, [1, 2], [{"id": "T001"}]):
            with self.subTest(payload=payload):
                with open(self.path, "w") as fh:
                    json.dump(payload, fh)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_ids_rejected(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)
        save_tickets(self.path, tickets + [dict(tickets[0])])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_ids_stay_unique_after_reload(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)
        create_ticket(tickets, "b", "Other", "low", 1)
        save_tickets(self.path, tickets)
        reloaded = load_tickets(self.path)
        new = create_ticket(reloaded, "c", "Other", "low", 1)
        self.assertEqual(new["id"], "T003")
        self.assertEqual(len({t["id"] for t in reloaded}), 3)


if __name__ == "__main__":
    unittest.main()


# ---------------- CampusFlow Next additions (Engineer A) ----------------
from campusflow.notes import add_note, next_note_id          # noqa: E402
from campusflow.storage import replace_from_file             # noqa: E402


def _good(**over):
    rec = {"id": "T001", "title": "Wi-Fi down", "category": "Network", "urgency": "high",
           "affected_users": 15, "priority": "critical", "status": "open",
           "assigned_to": None, "notes": []}
    rec.update(over)
    return rec


class NextStorageTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "tickets.json")

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, payload):
        with open(self.path, "w") as fh:
            json.dump(payload, fh)

    @staticmethod
    def _read(path):
        with open(path) as fh:
            return fh.read()

    def test_notes_and_next_ids_survive_reload(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
        create_ticket(tickets, "Printer", "Hardware", "low", 1)
        add_note(tickets, "T001", "Mentor A", "router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "investigating switch ports")
        save_tickets(self.path, tickets)
        reloaded = load_tickets(self.path)
        self.assertEqual(reloaded, tickets)
        self.assertEqual(next_note_id(reloaded[0]), "N003")
        self.assertEqual(add_note(reloaded, "T001", "Ada", "third note here")["note_id"], "N003")
        self.assertEqual(create_ticket(reloaded, "New", "Other", "low", 1)["id"], "T003")

    def test_v1_file_is_migrated_and_backed_up_before_first_save(self):
        v1 = _good()
        del v1["notes"]
        self._write([v1])
        original = self._read(self.path)
        tickets = load_tickets(self.path)
        self.assertEqual(tickets[0]["notes"], [])
        self.assertEqual(self._read(self.path), original)          # load never rewrites
        save_tickets(self.path, tickets)
        self.assertEqual(self._read(self.path + ".v1.bak"), original)
        self.assertIn("notes", load_tickets(self.path)[0])

    def test_priority_that_contradicts_the_rules_is_rejected(self):
        self._write([_good(priority="low")])           # high urgency + 15 users is critical
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_started_or_resolved_ticket_without_assignee_is_rejected(self):
        for status in ("in_progress", "resolved"):
            with self.subTest(status=status):
                self._write([_good(status=status, assigned_to=None)])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_same_number_in_different_spelling_counts_as_duplicate(self):
        self._write([_good(id="T001"), _good(id="T1")])
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_bad_note_records_are_rejected(self):
        note = {"note_id": "N001", "author": "Ada", "message": "valid message"}
        bad_sets = [
            [note, dict(note)],                                   # duplicate note id
            [dict(note, message="hey")],                          # too short
            [dict(note, author="  ")],                            # blank author
            [dict(note, note_id="N1")],                           # non-canonical id
            [{"note_id": "N001", "author": "Ada"}],               # missing key
        ]
        for notes in bad_sets:
            with self.subTest(notes=notes):
                self._write([_good(notes=notes)])
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_failed_reload_keeps_memory_unchanged(self):
        tickets = []
        create_ticket(tickets, "In memory", "Other", "low", 1)
        before = [dict(t) for t in tickets]
        self._write([_good(id="T001"), _good(id="T001")])        # duplicate IDs
        with self.assertRaises(StorageError):
            replace_from_file(tickets, self.path)
        self.assertEqual(tickets, before)
        self._write([_good(id="T005")])
        self.assertEqual(replace_from_file(tickets, self.path), 1)
        self.assertEqual(tickets[0]["id"], "T005")


if __name__ == "__main__":
    unittest.main()
