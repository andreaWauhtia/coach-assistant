# Quickstart (trimmed)

This short guide shows the minimal steps to run the parser.

## 1) Prepare the JSON

Create `timeline.json` with `match_header` and `events` (minute, type, player, side).

## 2) Run the parser

```
python tools/parse_timeline.py --input timeline.json --out-dir output
```

## 3) Files produced

- `output/analysis/{matchday}/parsed_by_side.csv`
- `output/analysis/{matchday}/{matchday}.json`
- `output/analysis/{matchday}/{matchday}.md`

## Notes

- Event types and inference rules are canonical and stored in `data/event_types.json` and `data/inference_rules.json`.
- For detailed usage and examples see `docs/guide_parse_timeline.md` and `docs/examples.md`.