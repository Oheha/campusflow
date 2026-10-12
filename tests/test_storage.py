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
