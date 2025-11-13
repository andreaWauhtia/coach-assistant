# Extraction report — 2025-09-06

Sources read:
- `2025-09-06.json` (parsed timeline JSON)
- `parsed_by_side.csv` (CSV of events)
- `match_summary.md` (human notes)

Summary of findings:
- Match header: "USAO U8 16-3 Bouillon" (our team `USAO U8`, opponent `Bouillon`).
- JSON contains 31 events (all classified as either `goal` or `shoot`, with two `Arrêt` entries classified as `shoot` with inferred `frappe_subite`).
- CSV mirrors the JSON events and was present.
- `match_summary.md` lists presence and notes a bug: "on ne retrouve pas les 3 buts de Bouillon" — the provided parsed data contains only events for the `us` side and no events for the opponent.

Totals validation (from JSON events):
- Goals for USAO U8 (team `us`): count all events with classification `goal` = 16 (matches `score1`).
- Goals for Bouillon: 0 events found (but `score2` is 3 in header). 3 opponent goals are missing from parsed data.

Inferred issues and recommendations:
1. The timeline parsing appears to have captured only the `USAO U8` side (left). The opponent events are missing — likely OCR/screenshots didn't include the opponent side or the parser failed to detect 'right' side events.
2. Action: run `/extract-timeline` using the original screenshots in `.memory-bank/competitions/feed/` (if present) or re-run OCR with settings that capture both sides.
3. Short-term fix: if you have the opponent events available elsewhere (screenshots, notes), provide them and I will merge them into `parsed_by_side.csv` and regenerate the JSON.

Files created/checked:
- Verified: `2025-09-06.json`, `parsed_by_side.csv`, `match_summary.md`.
- Created: `extraction_report.md` (this file).

Next steps:
- If you want, I can try to re-run the timeline extraction from screenshots (use `/extract-timeline` and ensure images are in `.memory-bank/competitions/feed/`).
- Or you can provide the opponent events and I will merge them.

Validation status:
- Goals for our team: PASS (16/16)
- Goals for opponent: FAIL (0 found vs 3 expected) — missing data in parsed files.

End of report.
