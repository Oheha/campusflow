# Data file format (`data/tickets.json`)

A JSON **list** of ticket objects.

**v2 (current)** - original 8 fields plus `notes`:
```json
{
  "id": "T001", "title": "Campus Wi-Fi is down", "category": "Network", "urgency": "high",
  "affected_users": 15, "priority": "critical", "status": "in_progress", "assigned_to": "Ada",
  "notes": [{"note_id": "N001", "author": "Mentor A", "message": "Wi-Fi router reboot attempted"}]
}
```
**v1 (legacy)** - the same without `notes`. It still loads; each ticket gets `notes: []`. Loading never
rewrites the file. Before the first v2 save a copy is kept as `tickets.json.v1.bak`.

## Everything checked on load (the whole file, before anything is used)
- file is a list; every record has exactly the v1 or v2 keys
- ticket id is `T` + digits in canonical form (`T001`, not `T1`); ids unique by NUMBER
- title not blank; category / urgency / status legal; `affected_users` a positive int (not bool)
- `priority` equals what the priority rules give for urgency + affected users
- `in_progress` / `resolved` tickets have an assignee
- `notes` is a list; each note has exactly `note_id`, `author`, `message`; note ids canonical (`N001`) and
  unique inside the ticket; author non-blank; message 5-300 chars after trim

Any failure raises `StorageError` and the app keeps whatever is already in memory.
Next ticket id = highest ticket number + 1; next note id = highest note number in that ticket + 1.
