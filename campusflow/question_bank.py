"""Question bank for the Engineering Understanding Check.
Kept separate from the scoring/menu logic in understanding_check.py."""

QUESTIONS = [
    {"prompt": "Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
     "options": {"A": "Accept", "B": "Reject and preserve all data",
                 "C": "Resolve it automatically", "D": "Remove ticket"},
     "answer": "B"},
    {"prompt": "The app has zero tickets. What should resolution percentage display?",
     "options": {"A": "Crash", "B": "100%", "C": "0%",
                 "D": "Divide by one without explanation"},
     "answer": "C"},
    {"prompt": "Filter title='wifi', category='Network', status='open'. Which records should match?",
     "options": {"A": "Any record matching one filter", "B": "Only records matching all supplied filters",
                 "C": "All network records", "D": "All open records"},
     "answer": "B"},
    {"prompt": "A resolved ticket receives 'Add note'. What should happen?",
     "options": {"A": "Append anyway", "B": "Delete old notes",
                 "C": "Reject until reopened", "D": "Change status silently"},
     "answer": "C"},
    {"prompt": "The JSON file includes two tickets with the same ID. What should load do?",
     "options": {"A": "Keep both", "B": "Replace memory with duplicates",
                 "C": "Reject the load without changing current memory", "D": "Rename IDs silently"},
     "answer": "C"},
    {"prompt": "A PR changes validation but has no negative-case tests. Best review action?",
     "options": {"A": "Approve because it runs", "B": "Request focused tests and reasoning",
                 "C": "Merge immediately", "D": "Ask AI to approve it"},
     "answer": "B"},
]
