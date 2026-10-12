"""Summary reporting."""
from .tickets import PRIORITIES, STATUSES


def build_report(tickets):
    by_status = {s: 0 for s in STATUSES}
    by_priority = {p: 0 for p in PRIORITIES}
    for t in tickets:
        by_status[t["status"]] += 1
        by_priority[t["priority"]] += 1
    return {"total": len(tickets), "by_status": by_status, "by_priority": by_priority}


def format_report(report):
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    lines += [f"  {k:<12}{v}" for k, v in report["by_status"].items()]
    lines += ["", "By priority:"]
    lines += [f"  {k:<12}{v}" for k, v in report["by_priority"].items()]
    return "\n".join(lines)
