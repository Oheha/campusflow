# CampusFlow Next

A command-line helpdesk ticket manager for Learn2Earn campus staff: tickets, priority, assignment,
workflow, follow-up notes, search, reports, safe JSON storage, and an understanding check.
Python standard library only (3.8+).

## Run and test (works from a fresh clone)
```
python main.py
python -m unittest discover -s tests -v
```
Data is saved to `data/tickets.json` (created automatically, ignored by Git).

## Menu
1 Create - 2 List - 3 View - 4 Assign - 5 Change status - 6 Reopen - 7 Open work queue (open only) -
8 Report - 9 Add follow-up note - 10 View ticket notes - 11 Search tickets - 12 Engineering understanding
check - 13 Reload data from file - 0 Exit

## Rules in one place
- Priority (first match wins): high AND >=10 users -> critical; high OR >=10 -> high; medium OR >=3 -> medium; else low.
- Workflow: open -> in_progress (needs an assignee) -> resolved; resolved -> open only by explicit Reopen.
- Notes: only on open / in_progress tickets; author required; message 5-300 characters after trimming.
- Search: title substring (case-insensitive) AND optional category / status / priority.
- Report: total, by status / priority / category, unresolved, resolved, resolution %.

## Layout
| Path | Owner | Purpose |
|---|---|---|
| `campusflow/validation.py`, `tickets.py`, `notes.py`, `workflow.py`, `storage.py` | Engineer A | validation, tickets, notes, lifecycle, JSON |
| `campusflow/search.py`, `reports.py`, `cli.py`, `understanding_check.py`, `question_bank.py` | Engineer B | search, analytics, menu, quiz |
| `tests/` | both | A: validation, notes, storage - B: search, reports, understanding, cli |
| `docs/` | both | interfaces, data format, baseline check, design decisions, AI log, bug hunters |

Data file format and migration: `docs/data-format.md`. Contracts between the two modules: `docs/interfaces.md`.
