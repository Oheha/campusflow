"""Text menu for CampusFlow."""
from .reports import build_report, format_report
from .storage import StorageError, load_tickets, save_tickets
from .tickets import (ValidationError, create_ticket, find_ticket, normalize_category,
                      normalize_title, normalize_urgency, parse_affected_users)
from .workflow import assign_ticket, change_status, reopen_ticket, work_queue

MENU = """
=== CampusFlow ===
1. Create ticket
2. List all tickets
3. View ticket
4. Assign ticket
5. Change status
6. Reopen resolved ticket
7. Work queue
8. Report
0. Exit"""


def _row(t):
    who = t["assigned_to"] or "-"
    return (f"{t['id']:<6}{t['priority']:<10}{t['status']:<13}"
            f"{t['category']:<10}{who:<14}{t['title']}")


def _detail(t):
    return "\n".join(f"  {k:<15}{t[k]}" for k in
                     ("id", "title", "category", "urgency", "affected_users",
                      "priority", "status", "assigned_to"))


def _ask(prompt, parser, input_fn, output_fn):
    while True:
        try:
            return parser(input_fn(prompt))
        except ValidationError as exc:
            output_fn(f"Error: {exc}")


def run(data_path, input_fn=input, output_fn=print):
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

    actions = {"1": do_create, "2": do_list, "3": do_view, "4": do_assign,
               "5": do_status, "6": do_reopen, "7": do_queue, "8": do_report}

    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Choose an option: ").strip()
        except EOFError:
            choice = "0"
        if choice == "0":
            output_fn("Goodbye.")
            return 0
        action = actions.get(choice)
        if action is None:
            output_fn("Invalid option. Choose a number from the menu.")
            continue
        try:
            action()
        except ValidationError as exc:
            output_fn(f"Error: {exc}")
