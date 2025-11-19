# Event types (canonical)

This file is the canonical, human-readable summary of event types and their classification. The parser loads `data/event_types.json` for machine-readability.

## Canonical types

- But → goal
- Assist → assist (optional)
- Carton Jaune → card
- Carton Rouge → card
- Remplacement → substitution
- Arrêt → shoot
- Tir à côté → shoot
- Poteau → shoot
- Transversale → shoot
- Tir arrêté → shoot
- Blessé → injury

## Adding synonyms

Add synonyms in `data/event_types.json` under `synonyms` for each entry so the parser recognizes different strings (e.g. "Tir à coté").

## Link to machine-readable file

- `data/event_types.json` — should be kept in sync with this doc