"""Summary reporting (Engineer B)."""
from .validation import CATEGORIES, PRIORITIES, STATUSES


def build_report(tickets):
    by_status = {s: 0 for s in STATUSES}
    by_priority = {p: 0 for p in PRIORITIES}
    by_category = {c: 0 for c in CATEGORIES}
    for t in tickets:                      # each ticket counted once per breakdown
        by_status[t["status"]] += 1
        by_priority[t["priority"]] += 1
        by_category[t["category"]] += 1
    total = len(tickets)
    resolved = by_status["resolved"]
    unresolved = by_status["open"] + by_status["in_progress"]
    percent = round(resolved / total * 100, 1) if total else 0.0   # no division by zero
    return {"total": total, "by_status": by_status, "by_priority": by_priority,
            "by_category": by_category, "unresolved": unresolved,
            "resolved": resolved, "resolution_percent": percent}


def format_report(report):
    lines = [f"Total tickets: {report['total']}",
             f"Unresolved (open + in_progress): {report['unresolved']}",
             f"Resolved: {report['resolved']}",
             f"Resolution rate: {report['resolution_percent']:.1f}%",
             "", "By status:"]
    lines += [f"  {k:<12}{v}" for k, v in report["by_status"].items()]
    lines += ["", "By priority:"]
    lines += [f"  {k:<12}{v}" for k, v in report["by_priority"].items()]
    lines += ["", "By category:"]
    lines += [f"  {k:<12}{v}" for k, v in report["by_category"].items()]
    return "\n".join(lines)
