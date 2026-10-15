"""Read-only ticket search (Engineer B). Never modifies the ticket collection."""
import copy

from .tickets import PRIORITIES, ValidationError, id_number, normalize_category
from .workflow import normalize_status


def _blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def parse_category_filter(value):
    return None if _blank(value) else normalize_category(value)


def parse_status_filter(value):
    return None if _blank(value) else normalize_status(value)


def parse_priority_filter(value):
    if _blank(value):
        return None
    if isinstance(value, str) and value.strip().casefold() in PRIORITIES:
        return value.strip().casefold()
    raise ValidationError(f"Priority must be one of: {', '.join(PRIORITIES)}.")


def search_tickets(tickets, title_query="", category=None, status=None, priority=None):
    """Return COPIES of tickets matching ALL supplied filters (logical AND).

    title_query: case-insensitive substring (casefold). Empty filters mean "any".
    Invalid category/status/priority raise ValidationError.
    """
    if title_query is not None and not isinstance(title_query, str):
        raise ValidationError("Title search must be text.")
    query = (title_query or "").strip().casefold()
    category = parse_category_filter(category)
    status = parse_status_filter(status)
    priority = parse_priority_filter(priority)
    results = []
    for t in tickets:
        if query and query not in t["title"].casefold():
            continue
        if category and t["category"] != category:
            continue
        if status and t["status"] != status:
            continue
        if priority and t["priority"] != priority:
            continue
        results.append(copy.deepcopy(t))
    return results


def sort_by_priority(tickets):
    """Separate optional view: priority (critical first) then numeric ticket ID.
    Unlike work_queue() it does NOT filter by status."""
    rank = {p: i for i, p in enumerate(PRIORITIES)}
    return sorted(tickets, key=lambda t: (rank[t["priority"]], id_number(t["id"])))
