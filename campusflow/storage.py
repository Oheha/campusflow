"""Safe JSON persistence (Engineer A).

File format: a JSON list of ticket objects.
  v2 (current): the 8 original fields + "notes" (list of {note_id, author, message})
  v1 (legacy):  the 8 original fields only. Loaded as v2 with notes = [];
                a copy of the v1 file is kept as <file>.v1.bak before the first v2 save.
The whole collection is parsed and validated BEFORE it is returned, so a bad file can
never partly overwrite what is already in memory.
"""
import json
import os
import shutil

from .notes import format_note_id, note_id_number
from .tickets import calculate_priority, format_ticket_id, id_number
from .validation import (CATEGORIES, NOTE_MAX_LENGTH, NOTE_MIN_LENGTH, PRIORITIES, STATUSES,
                         URGENCY_LEVELS, ValidationError)

V1_FIELDS = {"id", "title", "category", "urgency", "affected_users",
             "priority", "status", "assigned_to"}
V2_FIELDS = V1_FIELDS | {"notes"}
NOTE_FIELDS = {"note_id", "author", "message"}


class StorageError(Exception):
    """Raised when the data file cannot be read safely."""


def _nonblank_text(value):
    return isinstance(value, str) and bool(value.strip())


def _check_note(note, where, seen_ids):
    if not isinstance(note, dict) or set(note) != NOTE_FIELDS:
        raise StorageError(f"{where} has a malformed note.")
    try:
        number = note_id_number(note["note_id"])
    except ValidationError:
        raise StorageError(f"{where} has an invalid note id.")
    if note["note_id"] != format_note_id(number):
        raise StorageError(f"{where} has a non-canonical note id {note['note_id']!r}.")
    if number in seen_ids:
        raise StorageError(f"{where} has a duplicate note id {note['note_id']}.")
    seen_ids.add(number)
    if not _nonblank_text(note["author"]):
        raise StorageError(f"{where} has a note with a blank author.")
    message = note["message"]
    if not isinstance(message, str) or not NOTE_MIN_LENGTH <= len(message.strip()) <= NOTE_MAX_LENGTH:
        raise StorageError(f"{where} has a note message outside {NOTE_MIN_LENGTH}-{NOTE_MAX_LENGTH} characters.")


def _check_record(record, index):
    """Validate one record; return a v2 copy (v1 records get notes = [])."""
    where = f"ticket #{index + 1}"
    if not isinstance(record, dict):
        raise StorageError(f"{where} is not an object.")
    keys = set(record)
    if keys == V1_FIELDS:
        record = dict(record, notes=[])
    elif keys != V2_FIELDS:
        raise StorageError(f"{where} has missing or unexpected fields.")
    try:
        number = id_number(record["id"])
    except ValidationError:
        raise StorageError(f"{where} has an invalid id.")
    if record["id"] != format_ticket_id(number):
        raise StorageError(f"{where} has a non-canonical id {record['id']!r}.")
    where = f"ticket {record['id']}"
    if not _nonblank_text(record["title"]):
        raise StorageError(f"{where} has a blank title.")
    if record["category"] not in CATEGORIES:
        raise StorageError(f"{where} has an invalid category.")
    if record["urgency"] not in URGENCY_LEVELS:
        raise StorageError(f"{where} has an invalid urgency.")
    users = record["affected_users"]
    if isinstance(users, bool) or not isinstance(users, int) or users < 1:
        raise StorageError(f"{where} has invalid affected_users.")
    if record["priority"] not in PRIORITIES:
        raise StorageError(f"{where} has an invalid priority.")
    if record["priority"] != calculate_priority(record["urgency"], users):
        raise StorageError(f"{where} has a priority that contradicts the priority rules.")
    if record["status"] not in STATUSES:
        raise StorageError(f"{where} has an invalid status.")
    assigned = record["assigned_to"]
    if assigned is not None and not _nonblank_text(assigned):
        raise StorageError(f"{where} has an invalid assigned_to.")
    if record["status"] in ("in_progress", "resolved") and assigned is None:
        raise StorageError(f"{where} is {record['status']} but has no assignee.")
    if not isinstance(record["notes"], list):
        raise StorageError(f"{where} has notes that are not a list.")
    seen_notes = set()
    for note in record["notes"]:
        _check_note(note, where, seen_notes)
    return record


def parse_tickets(data, source="data"):
    """Validate a decoded JSON value; return a NEW list or raise StorageError."""
    if not isinstance(data, list):
        raise StorageError(f"{source} must contain a list of tickets.")
    checked, seen = [], set()
    for i, record in enumerate(data):
        good = _check_record(record, i)
        number = id_number(good["id"])
        if number in seen:
            raise StorageError(f"Duplicate ticket id {good['id']} in {source}.")
        seen.add(number)
        checked.append(good)
    return checked


def load_tickets(path):
    """Missing file -> fresh start ([]). Bad content -> StorageError (file untouched)."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"{path} contains malformed JSON ({exc}). The file was NOT changed; "
            "fix or move it before restarting.")
    except OSError as exc:
        raise StorageError(f"Could not read {path}: {exc}")
    return parse_tickets(data, path)


def replace_from_file(tickets, path):
    """Reload into an existing list. The list is replaced only after full validation."""
    loaded = load_tickets(path)      # raises before we touch `tickets`
    tickets[:] = loaded
    return len(tickets)


def _backup_v1_file(path):
    backup = path + ".v1.bak"
    if os.path.exists(backup) or not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return
    if isinstance(data, list) and any(isinstance(r, dict) and "notes" not in r for r in data):
        shutil.copy2(path, backup)


def save_tickets(path, tickets):
    """Temp file + fsync + os.replace, so a crash cannot leave a half-written file."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    _backup_v1_file(path)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(tickets, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except OSError:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
