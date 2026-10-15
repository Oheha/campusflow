"""Engineering Understanding Check (Engineer B).

Scoring is a pure function (score_answers); the question text lives in question_bank.py.
Explanations are saved for mentor discussion and are never auto-graded.
"""
import os
from datetime import datetime

from .question_bank import QUESTIONS

VALID_CHOICES = ("A", "B", "C", "D")
EXPLAIN_QUESTIONS = (0, 4)       # zero-based: Q1 and Q5 ask for a short explanation
MIN_EXPLANATION_LENGTH = 10


def parse_choice(raw):
    choice = raw.strip().upper() if isinstance(raw, str) else ""
    if choice not in VALID_CHOICES:
        raise ValueError("Please answer A, B, C or D.")
    return choice


def score_answers(questions, answers):
    """One point per answer equal to the question's correct option."""
    return sum(1 for q, a in zip(questions, answers) if a == q["answer"])


def _save_note(path, name, score, total, answers, explanations):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {name}: score {score}/{total}, "
                 f"answers {''.join(answers)}\n")
        for number, text in explanations.items():
            fh.write(f"  Q{number} explanation: {text}\n")


def run_check(input_fn=input, output_fn=print, notes_path=None, questions=QUESTIONS):
    name = ""
    while not name:
        name = input_fn("Your name: ").strip()
        if not name:
            output_fn("Please enter your name.")
    answers, explanations = [], {}
    for index, q in enumerate(questions):
        output_fn(f"\nQ{index + 1}. {q['prompt']}")
        for letter in VALID_CHOICES:
            output_fn(f"  {letter}. {q['options'][letter]}")
        while True:
            try:
                choice = parse_choice(input_fn("Your answer (A/B/C/D): "))
                break
            except ValueError as exc:
                output_fn(f"Error: {exc}")
        answers.append(choice)                       # first valid submission is final
        if choice == q["answer"]:
            output_fn("Correct.")
        else:
            output_fn(f"Not quite. Best answer: {q['answer']}. {q['options'][q['answer']]}")
        if index in EXPLAIN_QUESTIONS:
            while True:
                text = input_fn("Explain your answer in one or two sentences: ").strip()
                if len(text) >= MIN_EXPLANATION_LENGTH:
                    explanations[index + 1] = text
                    break
                output_fn(f"Error: please write at least {MIN_EXPLANATION_LENGTH} characters.")
    score = score_answers(questions, answers)
    output_fn(f"\nScore: {score}/{len(questions)}")
    output_fn("Your explanations are saved for mentor discussion; they are not auto-graded.")
    if notes_path:
        _save_note(notes_path, name, score, len(questions), answers, explanations)
    return {"name": name, "score": score, "total": len(questions),
            "answers": answers, "explanations": explanations}
