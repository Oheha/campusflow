"""Read-only ticket search and combined filtering."""

from .tickets import CATEGORIES, PRIORITIES, STATUSES


def search_tickets(
    tickets,
    title="",
    category="",
    status="",
    priority="",
):
    """Return tickets matching every supplied filter.

    Title matching is case-insensitive substring matching.
    Category, status and priority are optional exact filters.

    The original ticket collection is never modified.
    """
    if not isinstance(title, str):
        raise ValueError("Title search must be text.")

    title = title.strip().casefold()

    category = _normalize_filter(
        category, CATEGORIES, "category"
    )
    status = _normalize_filter(
        status, STATUSES, "status"
    )
    priority = _normalize_filter(
        priority, PRIORITIES, "priority"
    )

    results = []

    for ticket in tickets:
        if title and title not in ticket["title"].casefold():
            continue

        if category and ticket["category"] != category:
            continue

        if status and ticket["status"] != status:
            continue

        if priority and ticket["priority"] != priority:
            continue

        results.append(ticket)

    return results


def _normalize_filter(value, allowed, field):
    """Validate an optional filter and normalize its spelling."""
    if value is None:
        return ""

    if not isinstance(value, str):
        raise ValueError(f"Invalid {field} filter.")

    value = value.strip()

    if not value:
        return ""

    for option in allowed:
        if value.casefold() == option.casefold():
            return option

    raise ValueError(
        f"Invalid {field}. Choose from: {', '.join(allowed)}."
    )


def sort_search_results(tickets):
    """Sort results by priority, then numeric ticket ID."""
    from .tickets import id_number

    rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    return sorted(
        tickets,
        key=lambda ticket: (
            rank[ticket["priority"]],
            id_number(ticket["id"]),
        ),
    )
