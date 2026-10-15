"""Centralised validation helpers (Engineer A).

Every function here is a pure check: it either returns the cleaned value or raises
ValidationError. None of them touch ticket data, so callers can validate first and
mutate afterwards ("validate-before-mutate").
"""

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCY_LEVELS = ("low", "medium", "high")
PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300


class ValidationError(ValueError):
    """Raised when user input or a requested action is invalid."""


def _reject_control_characters(text, what):
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        raise ValidationError(f"{what} must not contain control characters.")


def normalize_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title must not be blank.")
    cleaned = title.strip()
    _reject_control_characters(cleaned, "Title")
    return cleaned


def normalize_category(category):
    if isinstance(category, str):
        lookup = {c.casefold(): c for c in CATEGORIES}
        key = category.strip().casefold()
        if key in lookup:
            return lookup[key]
    raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")


def normalize_urgency(urgency):
    if isinstance(urgency, str):
        key = urgency.strip().casefold()
        if key in URGENCY_LEVELS:
            return key
    raise ValidationError(f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}.")


def parse_affected_users(value):
    """Return a strictly positive int.

    isinstance(True, int) is True in Python (bool is a subclass of int), so bools
    are rejected explicitly before the int check. Floats (even 3.0) and text that is
    not plain ASCII digits are rejected too.
    """
    msg = "Affected users must be a positive whole number (1 or more)."
    if isinstance(value, bool):
        raise ValidationError(msg)
    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        text = value.strip()
        if not text or not all("0" <= ch <= "9" for ch in text):
            raise ValidationError(msg)
        number = int(text)
    else:
        raise ValidationError(msg)
    if number < 1:
        raise ValidationError(msg)
    return number


def normalize_staff_label(label, what="Staff member name"):
    """Non-empty label (assignee or note author), trimmed."""
    if not isinstance(label, str) or not label.strip():
        raise ValidationError(f"{what} must not be blank.")
    cleaned = label.strip()
    _reject_control_characters(cleaned, what)
    return cleaned


def normalize_author(author):
    return normalize_staff_label(author, what="Author name")


def normalize_note_message(message):
    """Trim, then require NOTE_MIN_LENGTH..NOTE_MAX_LENGTH characters."""
    if not isinstance(message, str):
        raise ValidationError("Note message must be text.")
    cleaned = message.strip()
    if not NOTE_MIN_LENGTH <= len(cleaned) <= NOTE_MAX_LENGTH:
        raise ValidationError(
            f"Note message must be {NOTE_MIN_LENGTH}-{NOTE_MAX_LENGTH} characters "
            f"after trimming (got {len(cleaned)}).")
    _reject_control_characters(cleaned, "Note message")
    return cleaned
