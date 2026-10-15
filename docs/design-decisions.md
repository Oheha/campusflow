# Design decisions

1. **Business logic is separate from the CLI.** `tickets.py`, `workflow.py`, `reports.py` and `storage.py` never call `input()` or `print()`, so they can be unit-tested directly.
2. **Validate first, mutate last.** `create_ticket` checks every field before appending, so a bad request cannot leave a half-built ticket behind.
3. **Errors are `ValidationError`s** that the menu catches and prints; the program never crashes on bad user input.
4. **Case-insensitive input, canonical storage.** `" nEtWoRk "` is stored as `Network`; urgency and status are stored lowercase.
5. **affected_users** accepts digits only (`"15"` or `15`). Zero, negatives, decimals (even `3.0`), text and booleans are rejected.
6. **Work queue = tickets whose status is `open`.** The spec says "open, unresolved"; in_progress tickets are already being worked, so they are excluded. Easy to change in `work_queue` if the team decides otherwise.
7. **Allowed transitions:** open -> in_progress (needs an assignee) and in_progress -> resolved. Resolved -> open happens only through the explicit Reopen action. A resolved ticket cannot be assigned or have its status changed until reopened.
8. **Reopen keeps the assignee** so the work history is not lost.
9. **IDs** are `max existing number + 1`, formatted `T001`. Tickets are never deleted, so IDs are never reused, and they stay unique after reload. Queue ties compare the *numeric* part, so `T999` comes before `T1000`.
10. **Persistence:** a missing file means a fresh start. Malformed JSON, wrong structure, invalid fields or duplicate IDs raise `StorageError`; the app refuses to start and leaves the file untouched. Saves write a temp file and then `os.replace`, so a crash mid-save cannot corrupt the existing file.

## CampusFlow Next additions
11. **Notes live inside the ticket** (`notes` list). Per-ticket IDs `N001...` use highest-number + 1, so a rejected note never burns an ID and reload continues correctly.
12. **Validate everything, then mutate** is now centralised in `validation.py`; `tickets.py` re-exports the old names so v1 imports and tests keep working.
13. **Load validation is a full consistency check** (priority matches the rules, started/resolved tickets have an assignee, canonical unique IDs, note shapes). It fixes the audit finding that a hand-edited file loaded silently.
14. **v1 files still load.** Missing `notes` becomes `[]`; `<file>.v1.bak` is kept before the first v2 save.
15. **`replace_from_file`** swaps the in-memory list only after the entire file validated, so a failed reload changes nothing.
16. **Search returns deep copies** so a caller can never edit tickets through search results. Filters are ANDed; blank means "any".
17. **Original Open Work Queue is untouched** (open only). The priority-sorted search view is a separate function and menu path.
18. **Control characters** are rejected in titles, staff labels, authors and notes (terminal escape sequences).
19. **Ctrl+C / closed input** exits with a short message; data is already saved after each action.
20. **Quiz**: bank in `question_bank.py`, scoring in a pure function, explanations saved to `data/learning-notes.txt` and never auto-graded.
