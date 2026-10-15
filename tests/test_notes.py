import copy
import unittest

from campusflow.notes import add_note, get_notes, next_note_id
from campusflow.tickets import ValidationError, create_ticket
from campusflow.workflow import assign_ticket, change_status, reopen_ticket


def fixture():
    tickets = []
    create_ticket(tickets, "Campus Wi-Fi is down", "Network", "high", 15)
    return tickets, tickets[0]


def resolve(ticket):
    assign_ticket(ticket, "Ada")
    change_status(ticket, "in_progress")
    change_status(ticket, "resolved")


class NoteTests(unittest.TestCase):
    def test_valid_notes_get_sequential_ids(self):
        tickets, t = fixture()
        a = add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        b = add_note(tickets, "t001", " Mentor B ", "  Investigating switch ports  ")
        self.assertEqual((a["note_id"], b["note_id"]), ("N001", "N002"))
        self.assertEqual(b["author"], "Mentor B")
        self.assertEqual(b["message"], "Investigating switch ports")
        self.assertEqual(next_note_id(t), "N003")

    def test_rejected_note_does_not_consume_an_id(self):
        tickets, t = fixture()
        for author, message in (("", "long enough message"), ("   ", "long enough message"),
                                ("Ada", "    "), ("Ada", "hey"), ("Ada", "x" * 301)):
            with self.subTest(author=author, message=message[:8]), self.assertRaises(ValidationError):
                add_note(tickets, "T001", author, message)
        self.assertEqual(t["notes"], [])
        self.assertEqual(add_note(tickets, "T001", "Ada", "now a valid note")["note_id"], "N001")

    def test_resolved_rejects_then_reopen_accepts_and_notes_are_kept(self):
        tickets, t = fixture()
        add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        resolve(t)
        with self.assertRaises(ValidationError):
            add_note(tickets, "T001", "Mentor A", "this must be refused")
        self.assertEqual([n["note_id"] for n in get_notes(tickets, "T001")], ["N001", "N002"])
        reopen_ticket(t)
        self.assertEqual(add_note(tickets, "T001", "Mentor A", "back in action")["note_id"], "N003")
        self.assertEqual(len(get_notes(tickets, "T001")), 3)

    def test_failed_note_leaves_whole_collection_unchanged(self):
        tickets, t = fixture()
        create_ticket(tickets, "Printer jam", "Hardware", "low", 1)
        add_note(tickets, "T001", "Ada", "first valid note")
        resolve(t)
        before = copy.deepcopy(tickets)
        for args in (("T999", "Ada", "valid message"), ("T001", "Ada", "valid message"),
                     ("T002", "", "valid message"), ("T002", "Ada", "tiny")):
            with self.subTest(args=args), self.assertRaises(ValidationError):
                add_note(tickets, *args)
        self.assertEqual(tickets, before)

    def test_in_progress_tickets_accept_notes(self):
        tickets, t = fixture()
        assign_ticket(t, "Ada")
        change_status(t, "in_progress")
        self.assertEqual(add_note(tickets, "T001", "Ada", "working on it")["note_id"], "N001")

    # ---- bug-hunter test (written by Engineer B against Engineer A's module) ----
    def test_note_length_is_measured_after_trimming(self):
        tickets, t = fixture()
        cases = [("    abcd    ", False),         # 4 chars after trim
                 ("abcde", True),                # exactly 5
                 ("a" * 300, True),              # exactly 300
                 ("a" * 300 + "     ", True),    # 300 + trailing spaces -> still 300
                 ("a" * 301, False)]
        for message, ok in cases:
            with self.subTest(length=len(message), ok=ok):
                if ok:
                    add_note(tickets, "T001", "Ada", message)
                else:
                    with self.assertRaises(ValidationError):
                        add_note(tickets, "T001", "Ada", message)
        self.assertEqual([n["note_id"] for n in t["notes"]], ["N001", "N002", "N003"])


if __name__ == "__main__":
    unittest.main()
