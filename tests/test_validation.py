import unittest

from campusflow.validation import (ValidationError, normalize_author, normalize_note_message,
                                   normalize_staff_label, normalize_title, parse_affected_users)


class ValidationHelperTests(unittest.TestCase):
    def test_bool_is_an_int_in_python_but_rejected_here(self):
        self.assertTrue(isinstance(True, int))           # the trap
        for bad in (True, False, 0, -1, 2.0, 3.5, "3.5", "x", "", None, [5]):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                parse_affected_users(bad)

    def test_control_characters_rejected_inside_text(self):
        for fn, text in ((normalize_title, "Wi-Fi\x1b[31m down"),
                         (normalize_staff_label, "Ada\x07"),
                         (normalize_author, "Mentor\x00A")):
            with self.subTest(fn=fn.__name__), self.assertRaises(ValidationError):
                fn(text)

    def test_outer_whitespace_is_trimmed_not_rejected(self):
        self.assertEqual(normalize_title("  Wi-Fi down \n"), "Wi-Fi down")
        self.assertEqual(normalize_note_message("  router rebooted  "), "router rebooted")


if __name__ == "__main__":
    unittest.main()
