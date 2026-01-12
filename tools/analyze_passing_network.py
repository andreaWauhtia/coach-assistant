#!/usr/bin/env python3
"""
Script to analyze passing network from match events JSON.

Usage: python tools/analyze_passing_network.py input.json
"""

import argparse
import json

def analyze_passing_network(json_file):
    """
    Analyze passing stats and network from JSON data.
    """
    # Charger les données
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Analyser les passes
    passes = {}
    key_passes = {}
    assists = {}
    pass_network = {}
    key_pass_network = {}
    assist_network = {}
    global_network = {}

    for event in data['events']:
        player = event.get('player_name')
        if not player:
            continue
        
        event_type = event.get('action_type', '')
        if event_type in ['Pass', 'Assist', 'Key pass']:
            passes[player] = passes.get(player, 0) + 1
            if event_type == 'Key pass':
                key_passes[player] = key_passes.get(player, 0) + 1
            
            # Réseau selon le type
            note = event.get('note', '')
            if note.startswith('Vers: '):
                receiver = note[6:].strip()
                if event_type == 'Pass':
                    if player not in pass_network:
                        pass_network[player] = {}
                    pass_network[player][receiver] = pass_network[player].get(receiver, 0) + 1
                elif event_type == 'Key pass':
                    if player not in key_pass_network:
                        key_pass_network[player] = {}
                    key_pass_network[player][receiver] = key_pass_network[player].get(receiver, 0) + 1
                elif event_type == 'Assist':
                    if player not in assist_network:
                        assist_network[player] = {}
                    assist_network[player][receiver] = assist_network[player].get(receiver, 0) + 1
                
                # Réseau global de distribution
                if player not in global_network:
                    global_network[player] = {}
                global_network[player][receiver] = global_network[player].get(receiver, 0) + 1

    # Afficher les stats
    print('Stats de passes par joueur:')
    for player in sorted(set(passes.keys()) | set(key_passes.keys())):
        total = passes.get(player, 0)
        key = key_passes.get(player, 0)
        print(f'{player}: {total} passes total, {key} passes clés')

    print('\nRéseau de passes:')
    for passer in sorted(pass_network.keys()):
        print(f'{passer}:')
        for receiver in sorted(pass_network[passer].keys()):
            count = pass_network[passer][receiver]
            print(f'  -> {receiver} ({count} passe(s))')

    print('\nRéseau de passes clés:')
    for passer in sorted(key_pass_network.keys()):
        print(f'{passer}:')
        for receiver in sorted(key_pass_network[passer].keys()):
            count = key_pass_network[passer][receiver]
            print(f'  -> {receiver} ({count} passe(s) clé(s))')

    print('\nRéseau d\'assists:')
    for passer in sorted(assist_network.keys()):
        print(f'{passer}:')
        for receiver in sorted(assist_network[passer].keys()):
            count = assist_network[passer][receiver]
            print(f'  -> {receiver} ({count} assist(s))')

    print('\nRéseau de distribution globale:')
    for passer in sorted(global_network.keys()):
        print(f'{passer}:')
        for receiver in sorted(global_network[passer].keys()):
            count = global_network[passer][receiver]
            print(f'  -> {receiver} ({count} passe(s) totale(s))')

def main():
    parser = argparse.ArgumentParser(description="Analyze passing network from JSON")
    parser.add_argument('json_file', help='JSON file with match events')
    
    args = parser.parse_args()
    analyze_passing_network(args.json_file)

if __name__ == "__main__":
    main()