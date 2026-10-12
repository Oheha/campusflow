# CampusFlow

A command-line helpdesk ticket manager for Learn2Earn campus staff. Records problems, calculates priority,
assigns responsibility, tracks progress and saves everything to JSON. Standard library only (Python 3.8+).

## Run
```
python main.py
```
Tickets are stored in `data/tickets.json` (created automatically, excluded from Git).

## Test
```
python -m unittest discover -s tests -v
```

## Menu
| # | Feature |
|---|---------|
| 1 | Create ticket (validates input, calculates priority, generates ID) |
| 2 | List all tickets |
| 3 | View one ticket |
| 4 | Assign ticket |
| 5 | Change status (open -> in_progress -> resolved) |
| 6 | Reopen a resolved ticket |
| 7 | Work queue (open tickets, critical -> low, ties by earlier ID) |
| 8 | Report (totals by status and priority) |
| 0 | Exit |

## Priority rules (first match wins)
1. high urgency AND 10+ affected users -> critical
2. high urgency OR 10+ affected users -> high
3. medium urgency OR 3+ affected users -> medium
4. otherwise -> low

## Layout
- `campusflow/tickets.py` - validation, priority, ID generation, ticket creation
- `campusflow/workflow.py` - assign, status transitions, reopen, work queue
- `campusflow/reports.py` - report data and formatting
- `campusflow/storage.py` - safe JSON load/save
- `campusflow/cli.py` - the menu (input/output injectable, so it is testable)
- `tests/` - unittest suites
- `docs/` - design decisions and AI learning log
