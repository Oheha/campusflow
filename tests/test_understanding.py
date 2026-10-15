import os
import tempfile
import unittest

from campusflow.question_bank import QUESTIONS
from campusflow.understanding_check import parse_choice, run_check, score_answers


def feed(answers):
    it = iter(answers)
    return lambda prompt="": next(it)


class UnderstandingCheckTests(unittest.TestCase):
    def test_question_bank_is_well_formed(self):
        self.assertEqual(len(QUESTIONS), 6)
        for q in QUESTIONS:
            self.assertEqual(list(q["options"]), ["A", "B", "C", "D"])
            self.assertIn(q["answer"], q["options"])

    def test_scoring_is_a_pure_function(self):
        correct = [q["answer"] for q in QUESTIONS]
        self.assertEqual(score_answers(QUESTIONS, correct), 6)
        self.assertEqual(score_answers(QUESTIONS, ["A"] * 6), 0)
        self.assertEqual(score_answers(QUESTIONS, correct[:3] + ["A"] * 3), 3)

    def test_invalid_choice_is_rejected_and_retried_then_scored(self):
        out = []
        result = run_check(feed([
            "Ada", "x", "", "E", "b", "Validate before mutate so nothing half-changes",   # Q1 (+ explanation)
            "C", "B", "C", "c", "Reject load and keep the current memory unchanged",     # Q2-Q5 (+ explanation)
            "B"]), out.append)
        text = "\n".join(out)
        self.assertEqual(text.count("Please answer A, B, C or D."), 3)
        self.assertEqual(result["score"], 6)
        self.assertIn("Score: 6/6", text)

    def test_wrong_answers_score_zero_and_feedback_is_shown(self):
        out = []
        result = run_check(feed(["Bo", "A", "my explanation here", "A", "A", "A", "A",
                                 "another explanation", "A"]), out.append)
        self.assertEqual(result["score"], 0)
        self.assertIn("Not quite. Best answer: B.", "\n".join(out))

    def test_short_explanations_are_rejected_and_saved_for_mentors(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "notes.txt")
            out = []
            run_check(feed(["Ada", "B", "ok", "it rejects bad input safely", "C", "B", "C", "C",
                            "short", "duplicates make IDs ambiguous", "B"]), out.append, path)
            self.assertIn("at least 10 characters", "\n".join(out))
            with open(path) as fh:
                saved = fh.read()
            self.assertIn("it rejects bad input safely", saved)
            self.assertIn("duplicates make IDs ambiguous", saved)
            self.assertIn("score 6/6", saved)

    def test_parse_choice(self):
        self.assertEqual(parse_choice(" d "), "D")
        with self.assertRaises(ValueError):
            parse_choice("AB")


if __name__ == "__main__":
    unittest.main()
