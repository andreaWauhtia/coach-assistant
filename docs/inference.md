# Inference rules (canonical)

This document explains inference rules used by `tools/parse_timeline.py`. The rules are machine-readable in `data/inference_rules.json`.

## Logic

- If our team has `Arrêt` or `Tir arrêté` on our side, infer `frappe_subite` (opponent shot on our goal).
- If the opponent has `Arrêt` or `Tir arrêté`, infer `frappe_crée` (we had a shot that opponent saved).

## How to add rules

The inference file `data/inference_rules.json` uses the schema:

```
[
  {
    "trigger_event_types": ["Arrêt", "Tir arrêté"],
    "if_team": "us",
    "inferred_action": "frappe_subite",
    "description": "Our side shows a save -> opponent shot on us"
  }
]
```

Add entries to the JSON as needed, and then update docs to mention the new case.