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
