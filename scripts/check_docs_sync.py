#!/usr/bin/env python3
"""Simple script that validates that docs/event_types.md and data/event_types.json are in sync.
It prints mismatches and returns non-zero if mismatches found.
"""
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]

data_file = repo_root / 'data' / 'event_types.json'
docs_file = repo_root / 'docs' / 'event_types.md'

if not data_file.exists():
    print(f"ERROR: data file not found: {data_file}")
    raise SystemExit(2)

if not docs_file.exists():
    print(f"ERROR: docs file not found: {docs_file}")
    raise SystemExit(3)

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(docs_file, 'r', encoding='utf-8') as f:
    docs_text = f.read()

json_types = {e['type'] for e in data}
missing = [t for t in json_types if t not in docs_text]
extra = []

if missing:
    print("MISSING from docs/event_types.md:")
    for m in missing:
        print(" - ", m)

# Simple reverse check for doc header items: read the '## Canonical types' list

doc_lines = docs_text.splitlines()
canon_start = None
for i, line in enumerate(doc_lines):
    if line.strip().startswith('## Canonical types'):
        canon_start = i
        break

if canon_start is not None:
    canon_entries = []
    for line in doc_lines[canon_start+1:canon_start+15]:
        # simple list parsing
        if line.strip().startswith('-'):
            name = line.split('→')[0].replace('-', '').strip()
            canon_entries.append(name)
    extra = [c for c in canon_entries if c not in json_types]

if extra:
    print("Entries listed in docs but not in JSON:")
    for e in extra:
        print(" - ", e)

if missing or extra:
    print("\nPlease update docs/event_types.md or data/event_types.json to sync them.")
    raise SystemExit(1)

print('OK: docs and data event types are in sync')
raise SystemExit(0)
