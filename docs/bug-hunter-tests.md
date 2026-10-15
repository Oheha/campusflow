# Bug-hunter tests (one written by each engineer for the OTHER engineer's module)

## B's test against A's module - note length is measured after trimming
- Test: `tests/test_notes.py::NoteTests::test_note_length_is_measured_after_trimming`
- Initial state: ticket `T001` open, no notes.
- Input: `"    abcd    "`, `"abcde"`, 300 x `a`, 300 x `a` + 5 trailing spaces, 301 x `a`.
- Expected: 4 rejected, 5 accepted, 300 accepted, 300+spaces accepted, 301 rejected; IDs N001-N003 only.
- Actual (my run): matched expectations; rejected notes consumed no ID. Code change: none needed.
- Invariant made visible: the length rule applies to the trimmed text, and rejections never burn an ID.

## A's test against B's module - casefold and blank queries
- Test: `tests/test_search.py::SearchTests::test_casefold_matches_what_lower_would_miss_and_blank_query_means_any`
- Initial state: one ticket titled `Straße closed sign`.
- Input: queries `STRASSE`, `"   "`, `"  closed  "`.
- Expected: all three return `T001` (casefold handles `ß`; blank means "no filter"; queries are trimmed).
- Actual (my run): matched expectations. Code change: none needed (`str.lower()` would have failed the first).
- Invariant made visible: search normalises text the same way on both sides and treats blank as "any".

Each engineer: replace these with your OWN invented case if you prefer, and record what YOUR run printed.
