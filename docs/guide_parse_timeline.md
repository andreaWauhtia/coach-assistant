# Parse Timeline - Full Guide (canonical)

Refer to these canonical docs for configuration and behavior:
- `docs/event_types.md` — Event types and classifications (human readable)
- `docs/inference.md` — Inference rules (human readable)
- `data/event_types.json` — Machine-readable event types used by the parser
- `data/inference_rules.json` — Machine-readable inference rules used by the parser

## Input JSON format

Same as before: `match_header`, `events` array (minute, type, player, side).

## Running the script

```
python tools/parse_timeline.py --input timeline.json --out-dir output
```

Use `--interactive` to enter data manually. Use `--data-dir` to override the default data folder.

## Output files

- `parsed_by_side.csv` — All events classified with inferred actions
- `{matchday}.md` — Markdown report
- `{matchday}.json` — Parsed enriched JSON

## Classification & Inference

Classification and inference behaviors are externalized in `data/*.json` as above. For examples and details see `docs/event_types.md` and `docs/inference.md`.

## Interactive mode

The interactive mode uses the `data/event_types.json` file to show and validate known event types automatically.

## Examples

See `docs/examples.md` for sample JSON files and a step-by-step example.