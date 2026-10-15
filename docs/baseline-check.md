# Baseline check (run BEFORE changing any code)

- Audited commit SHA: `<git rev-parse HEAD on the tag baseline-audit>`
- Command: `python -m unittest discover -s tests -v`
- Result: `<paste the "Ran N tests ... OK/FAILED" lines you actually saw>`

## Three inputs I tested on the old app
| # | Input (menu path + values) | Expected | Actual |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## What the audit said needed improvement
| Audit observation | Reproduced by me? (steps) | Confirmed / not reproduced |
|---|---|---|
| (copy from your audit, e.g. "loading does not cross-check priority or assignee") | | |
| (e.g. "Ctrl+C / end of input shows a traceback") | | |
| (e.g. "no validation of control characters in free text") | | |

Do not mark an item "confirmed" until you reproduced it yourself.
