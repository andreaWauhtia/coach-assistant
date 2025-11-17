from pathlib import Path
import json


def test_docs_event_types_match_json():
    repo_root = Path(__file__).resolve().parents[1]
    data_file = repo_root / 'data' / 'event_types.json'
    docs_file = repo_root / 'docs' / 'event_types.md'

    assert data_file.exists(), 'data/event_types.json missing'
    assert docs_file.exists(), 'docs/event_types.md missing'

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    json_types = {e['type'] for e in data}

    docs_text = docs_file.read_text(encoding='utf-8')
    for t in json_types:
        assert t in docs_text, f'{t} not present in docs/event_types.md'
