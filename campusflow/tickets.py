"""Ticket creation, validation and priority calculation (pure business logic)."""
import re

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCY_LEVELS = ("low", "medium", "high")
PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")

_ID_RE = re.compile(r"^T(\d+)$")
_DIGITS_RE = re.compile(r"^[0-9]+$")


class ValidationError(ValueError):
    """Raised when user input or a requested action is invalid."""


def normalize_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title must not be blank.")
    return title.strip()


def normalize_category(category):
    if isinstance(category, str):
        lookup = {c.lower(): c for c in CATEGORIES}
        key = category.strip().lower()
        if key in lookup:
            return lookup[key]
    raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")


def normalize_urgency(urgency):
    if isinstance(urgency, str):
        key = urgency.strip().lower()
        if key in URGENCY_LEVELS:
            return key
    raise ValidationError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}.")


def parse_affected_users(value):
    """Return a positive int. Rejects zero, negatives, decimals, text and bools."""
    msg = "Affected users must be a positive whole number (1 or more)."
    if isinstance(value, bool):
        raise ValidationError(msg)
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and _DIGITS_RE.match(value.strip()):
        number = int(value.strip())
    else:
        raise ValidationError(msg)
    if number < 1:
        raise ValidationError(msg)
    return number


def calculate_priority(urgency, affected_users):
    """Apply the four rules in order; the first match wins."""
    urgency = normalize_urgency(urgency)
    affected_users = parse_affected_users(affected_users)
    is_high = urgency == "high"
    is_many = affected_users >= 10
    if is_high and is_many:        
        return "critical"
    if is_high or is_many:         
        return "high"
    if urgency == "medium" or affected_users >= 3:  
        return "medium"
    return "low"                   


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
    }
    tickets.append(ticket)
    return ticket
