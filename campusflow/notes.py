"""Structured follow-up notes (Engineer A: data layer; Engineer B: menu/display).

Contract for add_note(tickets, ticket_id, author, message):
  - tickets: the in-memory list of ticket dictionaries (same style as assign/create)
  - raises ValidationError for: unknown ticket, ticket not open/in_progress,
    blank author, message not 5-300 characters after trimming
  - on ANY error nothing is changed and no note ID is consumed
  - on success appends {"note_id", "author", "message"} and returns that dict
"""
import re

from .tickets import find_ticket
from .validation import ValidationError, normalize_author, normalize_note_message

NOTE_ALLOWED_STATUSES = ("open", "in_progress")
_NOTE_ID_RE = re.compile(r"^N(\d+)$")


def format_note_id(number):
    return f"N{number:03d}"


def note_id_number(note_id):
    match = _NOTE_ID_RE.match(note_id) if isinstance(note_id, str) else None
    if not match:
        raise ValidationError(f"Invalid note ID: {note_id!r}.")
    return int(match.group(1))


def next_note_id(ticket):
    """Per-ticket counter: highest existing note number + 1."""
    highest = max((note_id_number(n["note_id"]) for n in ticket.get("notes", [])), default=0)
    return format_note_id(highest + 1)


def ensure_accepts_notes(ticket):
    if ticket["status"] not in NOTE_ALLOWED_STATUSES:
        raise ValidationError(
            f"Notes can only be added to open or in_progress tickets; {ticket['id']} is "
            f"{ticket['status']}. Reopen it first.")


def add_note(tickets, ticket_id, author, message):
    ticket = find_ticket(tickets, ticket_id)
    ensure_accepts_notes(ticket)
    author = normalize_author(author)            # validate everything...
    message = normalize_note_message(message)
    note = {"note_id": next_note_id(ticket),     # ...then mutate
            "author": author, "message": message}
    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(tickets, ticket_id):
    """Copies of a ticket's notes in note-ID order (resolved tickets can be read)."""
    ticket = find_ticket(tickets, ticket_id)
    ordered = sorted(ticket.get("notes", []), key=lambda n: note_id_number(n["note_id"]))
    return [dict(n) for n in ordered]
