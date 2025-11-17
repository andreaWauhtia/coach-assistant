import json
from tools.parse_timeline import load_definitions


def test_load_definitions_defaults():
    defs = load_definitions()
    assert 'But' in defs['event_keywords']
    assert defs['classification_map'].get('But') == 'goal'
    # inference map contains both us and opponent keys for Arrêt
    assert defs['inference_map'].get(('us', 'Arrêt')) == 'frappe_subite'
    assert defs['inference_map'].get(('opponent', 'Arrêt')) == 'frappe_crée'
