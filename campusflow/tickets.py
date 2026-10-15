"""Ticket creation, priority calculation and ID helpers (Engineer A)."""
import re

from .validation import (CATEGORIES, PRIORITIES, STATUSES, URGENCY_LEVELS,
                         ValidationError, normalize_category, normalize_title,
                         normalize_urgency, parse_affected_users)

__all__ = ["CATEGORIES", "PRIORITIES", "STATUSES", "URGENCY_LEVELS", "ValidationError",
           "normalize_category", "normalize_title", "normalize_urgency",
           "parse_affected_users", "calculate_priority", "format_ticket_id", "id_number",
           "next_ticket_id", "find_ticket", "create_ticket"]

_ID_RE = re.compile(r"^T(\d+)$")


def calculate_priority(urgency, affected_users):
    """Apply the four rules in order; the first match wins."""
    urgency = normalize_urgency(urgency)
    affected_users = parse_affected_users(affected_users)
    is_high = urgency == "high"
    is_many = affected_users >= 10
    if is_high and is_many:        # RULE 1
        return "critical"
    if is_high or is_many:         # RULE 2
        return "high"
    if urgency == "medium" or affected_users >= 3:  # RULE 3
        return "medium"
    return "low"                   # RULE 4


def format_ticket_id(number):
    return f"T{number:03d}"


def id_number(ticket_id):
    """'T012' -> 12. Raises ValidationError for malformed IDs."""
    match = _ID_RE.match(ticket_id) if isinstance(ticket_id, str) else None
    if not match:
        raise ValidationError(f"Invalid ticket ID: {ticket_id!r}.")
    return int(match.group(1))


def next_ticket_id(tickets):
    """Highest existing numeric ID + 1, so IDs stay unique after a reload."""
    highest = max((id_number(t["id"]) for t in tickets), default=0)
    return format_ticket_id(highest + 1)


def find_ticket(tickets, ticket_id):
    if not isinstance(ticket_id, str):
        raise ValidationError("Ticket ID must be text like T001.")
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket["id"] == wanted:
            return ticket
    raise ValidationError(f"No ticket found with ID {wanted or '(blank)'}.")


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate everything first; only then append, so bad input never changes data."""
    title = normalize_title(title)
    category = normalize_category(category)
    urgency = normalize_urgency(urgency)
    affected_users = parse_affected_users(affected_users)
    ticket = {
        "id": next_ticket_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    tickets.append(ticket)
    return ticket
