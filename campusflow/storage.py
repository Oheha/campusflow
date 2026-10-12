"""JSON persistence. Never silently discards data."""
import json
import os

from .tickets import (CATEGORIES, PRIORITIES, STATUSES, URGENCY_LEVELS,
                      id_number, ValidationError)

_FIELDS = {"id", "title", "category", "urgency", "affected_users",
           "priority", "status", "assigned_to"}


class StorageError(Exception):
    """Raised when the data file cannot be read safely."""


def _check_record(record, index):
    where = f"ticket #{index + 1}"
    if not isinstance(record, dict):
        raise StorageError(f"{where} is not an object.")
    if set(record) != _FIELDS:
        raise StorageError(f"{where} has missing or unexpected fields.")
    try:
        id_number(record["id"])
    except ValidationError:
        raise StorageError(f"{where} has an invalid id.")
    if not isinstance(record["title"], str) or not record["title"].strip():
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
    if record["status"] not in STATUSES:
        raise StorageError(f"{where} has an invalid status.")
    assigned = record["assigned_to"]
    if assigned is not None and (not isinstance(assigned, str) or not assigned.strip()):
        raise StorageError(f"{where} has an invalid assigned_to.")


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
    if not isinstance(data, list):
        raise StorageError(f"{path} must contain a list of tickets.")
    seen = set()
    for i, record in enumerate(data):
        _check_record(record, i)
        if record["id"] in seen:
            raise StorageError(f"Duplicate ticket id {record['id']} in {path}.")
        seen.add(record["id"])
    return data


def save_tickets(path, tickets):
    """Write to a temp file, then replace, so a crash can't leave a half-written file."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(tickets, fh, indent=2)
    os.replace(tmp_path, path)
