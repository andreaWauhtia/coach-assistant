# Examples (canonical)

Use the `example_complex.json` and `match_usao_clean.json` files as canonical examples. This doc explains how to run them and validate outputs.

## Example 1: Complex

```
python tools/parse_timeline.py --input example_complex.json --out-dir output_complex
```

Check `output_complex/analysis/{matchday}/parsed_by_side.csv` and `{matchday}.md` for results.

## Example 2: USAO match (real data)

```
python tools/parse_timeline.py --input match_usao_clean.json --out-dir output_usao --matchday usao_2025_11_01 --our-team "USAO U8"
```

Use `--data-dir` if you store `data/` elsewhere.