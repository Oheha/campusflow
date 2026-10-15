"""Text menu for CampusFlow Next (Engineer B owns this file)."""
import os

from .notes import add_note, ensure_accepts_notes, get_notes
from .reports import build_report, format_report
from .search import (parse_category_filter, parse_priority_filter, parse_status_filter,
                     search_tickets, sort_by_priority)
from .storage import StorageError, load_tickets, replace_from_file, save_tickets
from .tickets import (ValidationError, create_ticket, find_ticket, normalize_category,
                      normalize_title, normalize_urgency, parse_affected_users)
from .understanding_check import run_check
from .validation import (NOTE_MAX_LENGTH, NOTE_MIN_LENGTH, normalize_author,
                         normalize_note_message)
from .workflow import assign_ticket, change_status, reopen_ticket, work_queue

MENU = """
=== CampusFlow Next ===
1. Create ticket
2. List all tickets
3. View ticket
4. Assign ticket
5. Change status
6. Reopen resolved ticket
7. Open work queue
8. Report
9. Add follow-up note
10. View ticket notes
11. Search tickets
12. Engineering understanding check
13. Reload data from file
0. Exit"""


def _row(t):
    who = t["assigned_to"] or "-"
    return (f"{t['id']:<6}{t['priority']:<10}{t['status']:<13}"
            f"{t['category']:<10}{who:<14}{t['title']}")


def _search_row(t):
    who = t["assigned_to"] or "-"
    return (f"{t['id']:<7}{t['category']:<10}{t['priority']:<10}"
            f"{t['status']:<13}{who:<14}{t['title']}")


def _detail(t):
    shown = dict(t, assigned_to=t["assigned_to"] or "-")     # same "-" as the list view
    return "\n".join(f"  {k:<15}{shown[k]}" for k in
                     ("id", "title", "category", "urgency", "affected_users",
                      "priority", "status", "assigned_to")) + \
        f"\n  {'notes':<15}{len(t.get('notes', []))}"


def _ask(prompt, parser, input_fn, output_fn):
    while True:
        try:
            return parser(input_fn(prompt))
        except ValidationError as exc:
            output_fn(f"Error: {exc}")


def run(data_path, input_fn=input, output_fn=print, notes_path=None):
    if notes_path is None:
        notes_path = os.path.join(os.path.dirname(os.path.abspath(data_path)),
                                  "learning-notes.txt")
    try:
        tickets = load_tickets(data_path)
    except StorageError as exc:
        output_fn(f"Error: {exc}")
        return 1

    def save():
        try:
            save_tickets(data_path, tickets)
        except OSError as exc:
            output_fn(f"Warning: could not save tickets: {exc}")

    def pick():
        return find_ticket(tickets, input_fn("Ticket ID: "))

    def do_create():
        title = _ask("Title: ", normalize_title, input_fn, output_fn)
        category = _ask("Category (Network/Hardware/Software/Other): ",
                        normalize_category, input_fn, output_fn)
        urgency = _ask("Urgency (low/medium/high): ", normalize_urgency, input_fn, output_fn)
        users = _ask("Affected users: ", parse_affected_users, input_fn, output_fn)
        t = create_ticket(tickets, title, category, urgency, users)
        save()
        output_fn(f"Created {t['id']} with priority {t['priority']}.")

    def do_list():
        if not tickets:
            output_fn("No tickets yet.")
            return
        output_fn(f"{'ID':<6}{'PRIORITY':<10}{'STATUS':<13}{'CATEGORY':<10}{'ASSIGNED':<14}TITLE")
        for t in tickets:
            output_fn(_row(t))

    def do_view():
        output_fn(_detail(pick()))

    def do_assign():
        t = pick()
        assign_ticket(t, input_fn("Staff member name: "))
        save()
        output_fn(f"{t['id']} assigned to {t['assigned_to']}.")

    def do_status():
        t = pick()
        change_status(t, input_fn("New status (open/in_progress/resolved): "))
        save()
        output_fn(f"{t['id']} is now {t['status']}.")

    def do_reopen():
        t = pick()
        reopen_ticket(t)
        save()
        output_fn(f"{t['id']} reopened.")

    def do_queue():
        queue = work_queue(tickets)
        if not queue:
            output_fn("The work queue is empty.")
            return
        for t in queue:
            output_fn(_row(t))

    def do_report():
        output_fn(format_report(build_report(tickets)))

    def do_add_note():
        t = pick()
        ensure_accepts_notes(t)          # fail before the user types a whole note
        author = _ask("Author: ", normalize_author, input_fn, output_fn)
        message = _ask(f"Note ({NOTE_MIN_LENGTH}-{NOTE_MAX_LENGTH} characters): ",
                       normalize_note_message, input_fn, output_fn)
        note = add_note(tickets, t["id"], author, message)
        save()
        output_fn(f"Added {note['note_id']} to {t['id']}.")

    def do_view_notes():
        t = pick()
        notes = get_notes(tickets, t["id"])
        if not notes:
            output_fn(f"No notes for {t['id']}.")
            return
        for n in notes:
            output_fn(f"{n['note_id']}  {n['author']}: {n['message']}")

    def do_search():
        title = input_fn("Title contains (blank = any): ")
        category = _ask("Category (blank = any): ", parse_category_filter, input_fn, output_fn)
        status = _ask("Status (blank = any): ", parse_status_filter, input_fn, output_fn)
        priority = _ask("Priority (blank = any): ", parse_priority_filter, input_fn, output_fn)
        results = search_tickets(tickets, title, category, status, priority)
        if not results:
            output_fn("No matching tickets.")
            return
            
        header = (f"{'ID':<7}{'CATEGORY':<10}{'PRIORITY':<10}{'STATUS':<13}"
                  f"{'ASSIGNED':<14}TITLE")
        output_fn(header)
        for t in results:
            output_fn(_search_row(t))
        if input_fn("Show results sorted by priority? (y/N): ").strip().casefold() == "y":
            output_fn("Sorted by priority, then ticket ID:")
            output_fn(header)
            for t in sort_by_priority(results):
                output_fn(_search_row(t))

    def do_check():
        run_check(input_fn, output_fn, notes_path)

    def do_reload():
        count = replace_from_file(tickets, data_path)
        output_fn(f"Reloaded {count} ticket(s) from {data_path}.")

    actions = {"1": do_create, "2": do_list, "3": do_view, "4": do_assign,
               "5": do_status, "6": do_reopen, "7": do_queue, "8": do_report,
               "9": do_add_note, "10": do_view_notes, "11": do_search,
               "12": do_check, "13": do_reload}

    try:
        while True:
            output_fn(MENU)
            choice = input_fn("Choose an option: ").strip()
            if choice == "0":
                output_fn("Goodbye.")
                return 0
            action = actions.get(choice)
            if action is None:
                output_fn("Invalid option. Choose a number from the menu.")
                continue
            try:
                action()
            except (ValidationError, StorageError) as exc:
                output_fn(f"Error: {exc}")
    except (EOFError, KeyboardInterrupt):
        output_fn("\nInput closed. Saved tickets are safe. Goodbye.")
        return 0
