"""Assignment, status workflow and the work queue."""
from .tickets import PRIORITIES, STATUSES, ValidationError, id_number

_ALLOWED_TRANSITIONS = {("open", "in_progress"), ("in_progress", "resolved")}


def normalize_status(status):
    if isinstance(status, str):
        key = status.strip().lower().replace(" ", "_").replace("-", "_")
        if key in STATUSES:
            return key
    raise ValidationError(f"Status must be one of: {', '.join(STATUSES)}.")


def assign_ticket(ticket, staff_name):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValidationError("Staff member name must not be blank.")
    if ticket["status"] == "resolved":
        raise ValidationError("Resolved tickets cannot be modified. Reopen the ticket first.")
    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(ticket, new_status):
    new_status = normalize_status(new_status)
    current = ticket["status"]
    if current == "resolved":
        raise ValidationError("Resolved tickets cannot be modified. Reopen the ticket first.")
    if new_status == current:
        raise ValidationError(f"Ticket is already {current}.")
    if (current, new_status) not in _ALLOWED_TRANSITIONS:
        raise ValidationError(f"Cannot move a ticket from {current} to {new_status}.")
    if new_status == "in_progress" and not ticket["assigned_to"]:
        raise ValidationError("Assign the ticket to someone before moving it to in_progress.")
    ticket["status"] = new_status
    return ticket


def reopen_ticket(ticket):
    if ticket["status"] != "resolved":
        raise ValidationError("Only resolved tickets can be reopened.")
    ticket["status"] = "open"
    return ticket


def work_queue(tickets):
    """Open tickets, critical -> low, ties broken by the earlier numeric ID."""
    rank = {p: i for i, p in enumerate(PRIORITIES)}
    open_tickets = [t for t in tickets if t["status"] == "open"]
    return sorted(open_tickets, key=lambda t: (rank[t["priority"]], id_number(t["id"])))
