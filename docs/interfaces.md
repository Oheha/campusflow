# Interface contract between Engineer A and Engineer B

Agree on this BEFORE coding. Convention for the whole project: **business-layer functions raise
`ValidationError` (bad input / illegal action) or `StorageError` (bad file); they never print and
never read input. On any error nothing is changed.** The CLI catches both and prints `Error: ...`.

| Function | Owner | Contract |
|---|---|---|
| `validation.normalize_*`, `parse_affected_users` | A | return the cleaned value or raise `ValidationError`; no side effects |
| `tickets.create_ticket(tickets, title, category, urgency, affected_users)` | A | validates all fields, then appends a ticket with `notes: []`; returns it |
| `workflow.assign_ticket(ticket, name)` / `change_status(ticket, new)` / `reopen_ticket(ticket)` | A | validate, then mutate; resolved tickets locked until reopened; unassigned cannot start |
| `notes.add_note(tickets, ticket_id, author, message)` | A | ticket must be open/in_progress; author non-blank; message 5-300 chars after trim; returns the new note; a rejected call consumes no note ID |
| `notes.ensure_accepts_notes(ticket)` | A | raises if the ticket is resolved; lets the CLI refuse BEFORE asking for text |
| `notes.get_notes(tickets, ticket_id)` | A | copies of notes in note-ID order (works for resolved tickets) |
| `storage.load_tickets(path)` | A | `[]` if missing; validates the WHOLE file; raises `StorageError`; never writes |
| `storage.replace_from_file(tickets, path)` | A | replaces the list only after full validation succeeds |
| `storage.save_tickets(path, tickets)` | A | temp file + `os.replace`; keeps `<file>.v1.bak` when migrating a v1 file |
| `search.search_tickets(tickets, title, category, status, priority)` | B | AND of all supplied filters; blank/None = no filter; returns COPIES; never modifies |
| `search.sort_by_priority(tickets)` | B | priority then numeric ID; separate from the original queue |
| `reports.build_report(tickets)` | B | totals, by status/priority/category, unresolved, resolved, resolution %; `0.0` when empty |
| `understanding_check.run_check(input_fn, output_fn, notes_path)` | B | six questions, retry on invalid letter, returns score dict |
| `workflow.work_queue(tickets)` | original | UNCHANGED: open tickets only |
